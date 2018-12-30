import sys
sys.path.append('../')
from plan_search import *
from nesting import *
from util import *
from query_manager import *
from ilp_helper import *
import math
from sets import Set
import globalv
# opt 0: reduce possible nestings
# set globalv.always_nested, always_fk_indexed and reversely_visited
def prune_nestings(queries):
  assoc_fields = []
  for query in queries:
    cur_obj = ObjNesting(query.table)
    get_obj_nesting_by_query(cur_obj, query)
    assoc_fields += prune_nesting_helper(cur_obj)

  for qf in assoc_fields:
    reversed_qf = get_reversed_assoc_qf(qf)
    reverse = False
    if any([qf_==reversed_qf for qf_ in assoc_fields]):
      globalv.reversely_visited.append(qf)
      globalv.reversely_visited.append(reversed_qf)
      reverse = True
    # if a field is only visited within one other object, then always nested
    if not reverse and all([qf==qf_ if qf.field_class==qf_.field_class else True for qf_ in assoc_fields]):
      globalv.always_nested.append(qf)
    # always fk indexed? TODO
  
  return assoc_fields

# return a list of assoc fields
def prune_nesting_helper(obj):
  assocs = [qf for qf,assoc in obj.assocs.items()]
  for qf,assoc in obj.assocs.items():
    assocs += prune_nesting_helper(assoc)
  return assocs
    
def prune_nesting_test(queries):
  prev_nestings = 0
  after_nestings = 0
  for query in queries:
    ns = enumerate_nestings_for_query(query)
    prev_nestings += len(ns)
  assoc_fields = prune_nestings(queries)
  for query in queries:
    ns = enumerate_nestings_for_query(query)
    after_nestings += len(ns)
  print 'assoc_fields = {}'.format(', '.join([str(f) for f in assoc_fields]))
  not_reversed = clean_lst([None if any([qf_==qf for qf_ in globalv.reversely_visited]) else qf for qf in assoc_fields])
  print '\nnot reversed: {}'.format(', '.join([str(f) for f in not_reversed]))
  print '\nalways_nested = {}'.format(', '.join([str(f) for f in globalv.always_nested]))
  print '\nbefore {}; after {};'.format(prev_nestings, after_nestings)

def encode_plan_list(lst):
  if len(lst) == 0:
    return 0
  lst.sort()
  return sum([lst[i]*math.pow(2, i) for i in range(0, len(lst))])

import time
def prune_read_plans(rqmanagers, dsmeta):
  Nqueries = len(rqmanagers)
  pruned_plans = [0 for i in range(0, Nqueries)]
  used_ds_lst = [Set([]) for i in range(0, Nqueries)]
  temp_plan_cost = [0 for i in range(0, Nqueries)]

  for qi,rqmng in enumerate(rqmanagers):
    start_time = time.time()
    temp_plan_cost[qi] = [0 for i in range(0, len(rqmng.plans))]
    pruned_plans[qi] = [[] for i in range(0, len(rqmng.plans))]
    for i,plan_for_one_nesting in enumerate(rqmng.plans):
      temp_plan_cost[qi][i] = [0 for j in range(0, len(plan_for_one_nesting.plans))]
      for j in range(0, len(plan_for_one_nesting.plans)):
        dsmnger = plan_for_one_nesting.dsmanagers[j]
        plan = plan_for_one_nesting.plans[j]
        mem_cost = to_real_value(dsmnger.compute_mem_cost())
        plan_cost = to_real_value(plan.compute_cost())
        ds_lst, memobj = collect_all_ds_helper1(dsmnger.data_structures)
        dsid_lst = [ds.id for ds in ds_lst]
        for dsid in dsid_lst:
          used_ds_lst[qi].add(dsid)
        temp_plan_cost[qi][i][j] = (dsid_lst, mem_cost, plan_cost)
        #if mem_cost > globalv.memory_bound:
        #  print 'query {} nesting {} plan {} is removed, mem_cost = {}'.format(qi, i, j, mem_cost)
        #  pruned_plans[qi][i].append(j)
    print 'pass 1 query {}: {}'.format(qi, time.time()-start_time)
  print 'finish pass 1'
  # opt 2.1: if planA's shared ds set (with any other query) is the same as planB's shared ds set, and planA is better than planB, just keep planA
  for qi,rqmng in enumerate(rqmanagers):
    start_time = time.time()
    map_by_shared_ds = {} # key: encoded shared lst; value: a set of plans
    for i,plan_for_one_nesting in enumerate(rqmng.plans):
      for j in range(0, len(plan_for_one_nesting.plans)):
        ds_lst = temp_plan_cost[qi][i][j][0]
        shared_lst = []
        for dsid in ds_lst:
          if any([False if qj == qi else (dsid in used_ds_lst[qj]) for qj in range(0, Nqueries)]):
            shared_lst.append(dsid) 
        shared_encoded = encode_plan_list(shared_lst)
        if shared_encoded not in map_by_shared_ds:
          map_by_shared_ds[shared_encoded] = []
        map_by_shared_ds[shared_encoded].append((i,j,temp_plan_cost[qi][i][j][1],temp_plan_cost[qi][i][j][2]))
   
    for xx,lst in map_by_shared_ds.items():
      best = []
      for x1,tup1 in enumerate(lst): 
        exist_equal = False
        exist_better = False
        for x2,tup2 in enumerate(lst):
          if x1 == x2:
            continue
          if tup1[2] == tup2[2] and tup1[3] == tup2[3]:
            exist_equal = True
          elif tup1[2] >= tup2[2] and tup1[3] >= tup2[3]:
            exist_better = True
        if exist_better:
          pruned_plans[qi][tup1[0]].append(tup1[1])
        elif exist_equal:
          lst[x1] = (tup1[0], tup1[1], tup1[2]-1, tup1[3])
    print 'pass 2 query {}: {}'.format(qi, time.time()-start_time)
    #print 'finish query {}'.format(qi)
        
  print 'finish pass 2'

  for qi,rqmng in enumerate(rqmanagers):
    for i,plan_for_one_nesting in enumerate(rqmng.plans):
      left = []
      for j in range(0, len(plan_for_one_nesting.plans)):
        if j in pruned_plans[qi][i]:
          continue
        left.append(j)
      rqmng.plans[i].dsmanagers = [plan_for_one_nesting.dsmanagers[j] for j in left] 
      rqmng.plans[i].plans = [plan_for_one_nesting.plans[j] for j in left]
  

"""
def prune_read_plans(rqmanagers, dsmeta):
  pruned_plans = []

  temp_plan_cost = []
  plan_ds = []
  ds_map = {}
  for qi,rqmng in enumerate(rqmanagers):
    plan_to_be_removed = [[] for i in range(0, len(rqmng.plans))]
    temp_plan_cost1 = [[] for i in range(0, len(rqmng.plans))] 
    plan_ds1 = []
    for i,plan_for_one_nesting in enumerate(rqmng.plans):
      for j in range(0, len(plan_for_one_nesting.plans)):
        # opt 1: if plan mem cost > mem bound, do not consider
        dsmnger = plan_for_one_nesting.dsmanagers[j]
        plan = plan_for_one_nesting.plans[j]
        mem_cost = to_real_value(dsmnger.compute_mem_cost())
        plan_cost = to_real_value(plan.compute_cost())
        if mem_cost > globalv.memory_bound:
          print 'query {} nesting {} plan {} is removed, mem_cost = {}'.format(qi, i, j, mem_cost)
          plan_to_be_removed[i].append(j)
        ds_lst, memobj = collect_all_ds_helper1(dsmnger.data_structures)
        for ds in ds_lst:
          ds_map[ds.id] = ds
        temp_plan_cost1[i].append(([ds.id for ds in ds_lst], mem_cost, plan_cost))
        plan_ds1 += [ds.id for ds in ds_lst]
    plan_ds1 = list_remove_duplicate(plan_ds1)
    plan_ds.append(plan_ds1)
    pruned_plans.append(plan_to_be_removed)
    temp_plan_cost.append(temp_plan_cost1)

  print '\n------\n'
  # opt 2: if plan's every ds is not shared with other query, collect all such plans and only keep the best ones
  # opt 2.1: if planA's shared ds set (with any other query) is the same as planB's shared ds set, and planA is better than planB, just keep planA
  #plan_may_be_removed = []
  plan_ds_shared = [0 for i in range(0, len(rqmanagers))]
  for qi,rqmng in enumerate(rqmanagers):
    temp_plan_cost1 = temp_plan_cost[qi]
    #plan_may_be_removed1 = [[] for i in range(0, len(rqmng.plans))]
    plan_ds_shared[qi] = [0 for i in range(0, len(rqmng.plans))]
    for i,plan_for_one_nesting in enumerate(rqmng.plans):
      plan_ds_shared[qi][i] = [[] for j in range(0, len(plan_for_one_nesting.plans))]
      for j in range(0, len(plan_for_one_nesting.plans)):
        #ds_used_by_others = False
        for dsid in temp_plan_cost1[i][j][0]:
          for qj in range(0, len(rqmanagers)):
            if qi != qj and any([dsid_==dsid for dsid_ in plan_ds[qj]]):
              #ds_used_by_others = True
              plan_ds_shared[qi][i][j].append(dsid)
              break
        #if not ds_used_by_others:
        #  print 'query {} nesting {} plan {} ds not used by others'.format(qi, i, j)
        #  plan_may_be_removed1[i].append((j, temp_plan_cost1[i][j][1], temp_plan_cost1[i][j][2]))
    #plan_may_be_removed.append(plan_may_be_removed1)

  print '\n------\n'
  for qi,rqmng in enumerate(rqmanagers):
    #plan_may_be_removed1 = plan_may_be_removed[qi]
    equal_plans = []
      
    for i1,plan_for_one_nesting in enumerate(rqmng.plans):
      for j1 in range(0, len(plan_for_one_nesting.plans)):
        #if (plan_ds_shared[qi][i1][j1] == 0):  # used for opt 1
        #  continue
        exist_better_plan = False
        exist_equal_plan = False
        for i2,plan_for_one_nesting2 in enumerate(rqmng.plans):
          for j2 in range(0, len(plan_for_one_nesting2.plans)):
            if i1 == i2 and j1 == j2:
              continue
            if set_equal(plan_ds_shared[qi][i1][j1], plan_ds_shared[qi][i2][j2]):
              if temp_plan_cost[qi][i1][j1][1] == temp_plan_cost[qi][i2][j2][1] and temp_plan_cost[qi][i1][j1][2] == temp_plan_cost[qi][i2][j2][2]:
                exist_equal_plan = True
              elif temp_plan_cost[qi][i1][j1][1] >= temp_plan_cost[qi][i2][j2][1] and temp_plan_cost[qi][i1][j1][2] >= temp_plan_cost[qi][i2][j2][2]:
                #if not exist_better_plan:
                #  print 'len = {}, j1={}, j2={}'.format(len(plan_for_one_nesting.plans), j1, j2)
                #  print 'plan {} ({}, {}, ds = {} {}) is better than {} ({}, {}, ds = {} {})'.format(plan_for_one_nesting2.plans[j2], \
                #    temp_plan_cost[qi][i2][j2][1], temp_plan_cost[qi][i2][j2][2], ','.join([str(x) for x in plan_ds_shared[qi][i2][j2]]), plan_for_one_nesting2.dsmanagers[j2], \
                #    plan_for_one_nesting.plans[j1], \
                #    temp_plan_cost[qi][i1][j1][1], temp_plan_cost[qi][i1][j1][2], ','.join([str(x) for x in plan_ds_shared[qi][i2][j2]]), plan_for_one_nesting.dsmanagers[j1])
                #  print '--------'
                exist_better_plan = True
        if exist_better_plan:
          pruned_plans[qi][i1].append(j1)
          #print 'query {} nesting {} plan {} is minor in index'.format(qi, i1, j1)
        elif exist_equal_plan:
          temp_plan_cost[qi][i1][j1] = (temp_plan_cost[qi][i1][j1][0], temp_plan_cost[qi][i1][j1][1]-1, temp_plan_cost[qi][i1][j1][2])
 
  for qi,rqmng in enumerate(rqmanagers):
    for i,plan_for_one_nesting in enumerate(rqmng.plans):
      new_dsmngers = []
      new_plans = []
      for j in range(0, len(plan_for_one_nesting.plans)):
        if j in pruned_plans[qi][i]:
          continue
        dsmnger = plan_for_one_nesting.dsmanagers[j]
        plan = plan_for_one_nesting.plans[j]
        new_dsmngers.append(dsmnger)
        new_plans.append(plan)
      rqmng.plans[i].dsmanagers = new_dsmngers
      rqmng.plans[i].plans = new_plans

# opt 3: if plan time is too long (how long?), do not consider
"""


def test_prune_read_plan(read_queries, membound_factor=2):
  prune_nestings(read_queries)
  #print dsmeta
  mem_bound = compute_mem_bound(membound_factor)

  rqmanagers = []
  dsmeta = DSManager()
  begin_ds_id = 1
  old_plan_cnt = 0
  for query in read_queries:
    nesting_plans = search_plans_for_one_query(query, print_plan=False)
    rqmanagers.append(RQManager(query, nesting_plans))
    for i,plan_for_one_nesting in enumerate(nesting_plans):
      #print 'nesting...{}'.format(len(plan_for_one_nesting.plans))
      dsmng = plan_for_one_nesting.nesting
      for j,plan in enumerate(plan_for_one_nesting.plans):
        new_dsmnger = dsmng.copy_tables()
        plan.get_used_ds(None, new_dsmnger)
        rqmanagers[-1].plans[i].dsmanagers.append(new_dsmnger)
        begin_ds_id, deltas = collect_all_structures(dsmeta, new_dsmnger, begin_ds_id)
        old_plan_cnt += 1

  
  print 'mem_bound = {}'.format(mem_bound)
  prune_read_plans(rqmanagers, dsmeta)

  new_plan_cnt = 0
  for qi,rqmng in enumerate(rqmanagers):
    for i,plan_for_one_nesting in enumerate(rqmng.plans):
      new_plan_cnt += len(plan_for_one_nesting.plans)

  print 'old plan cnt = {}, new plan cnt = {}'.format(old_plan_cnt, new_plan_cnt)
