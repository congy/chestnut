import sys
sys.path.append('../')
from plan_search import *
from nesting import *
from util import *
from query_manager import *
from ilp_helper import *
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


def prune_read_plans(rqmanagers, dsmeta):
  pruned_plans = []

  temp_plan_cost = []
  plan_ds = []
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
        temp_plan_cost1[i].append(([ds.id for ds in ds_lst], mem_cost, plan_cost))
        plan_ds1 += [ds.id for ds in ds_lst]
    plan_ds1 = list_remove_duplicate(plan_ds1)
    plan_ds.append(plan_ds1)
    pruned_plans.append(plan_to_be_removed)
    temp_plan_cost.append(temp_plan_cost1)

  print '\n------\n'
  # opt 2: if plan's every ds is not shared with other query, collect all such plans and only keep the best ones
  plan_may_be_removed = []
  for qi,rqmng in enumerate(rqmanagers):
    temp_plan_cost1 = temp_plan_cost[qi]
    plan_may_be_removed1 = [[] for i in range(0, len(rqmng.plans))]
    for i,plan_for_one_nesting in enumerate(rqmng.plans):
      for j in range(0, len(plan_for_one_nesting.plans)):
        ds_used_by_others = False
        for dsid in temp_plan_cost1[i][j][0]:
          for qj in range(0, len(rqmanagers)):
            if qi != qj and any([dsid_==dsid for dsid_ in plan_ds[qj]]):
              ds_used_by_others = True
        if not ds_used_by_others:
          print 'query {} nesting {} plan {} ds not used by others'.format(qi, i, j)
          plan_may_be_removed1[i].append((j, temp_plan_cost1[i][j][1], temp_plan_cost1[i][j][2]))
    plan_may_be_removed.append(plan_may_be_removed1)

  print '\n------\n'
  for qi,rqmng in enumerate(rqmanagers):
    plan_may_be_removed1 = plan_may_be_removed[qi]
    equal_plans = []
    for i,plan_for_one_nesting in enumerate(rqmng.plans):
      for triple in plan_may_be_removed1[i]:
        exist_better_plan = False
        exist_equal_plan = False
        for i1,triple_lst in enumerate(plan_may_be_removed1):
          for triple_ in triple_lst:
            if i1==i and triple_[0]==triple[0]:
              continue
            if (triple[1] == triple_[1] and triple[2] == triple_[2]):
              exist_equal_plan = True
            elif (triple[1] >= triple_[1] and triple[2] >= triple_[2]):
              #print 'nesting {} plan {} ({} {}) is worse than nesting {} plan {} ({} {})'.format(i, triple[0], triple[1], triple[2], i1, triple_[0], triple_[1], triple_[2])
              exist_better_plan = True
        
        if (not exist_better_plan) and exist_equal_plan:
          for pair in equal_plans:
            if triple[1] == pair[0] and triple[2] == pair[1]:
              exist_better_plan = True
          if not exist_better_plan:
            equal_plans.append((triple[1], triple[2]))
        if exist_better_plan:
          pruned_plans[qi][i].append(triple[0])
        else:
          print 'query {} nesting {} plan {} not shared and is the best plan, mem_cost = {}, time = {}'.format(qi, i, triple[0], triple[1], triple[2])
          
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

def test_prune_read_plan(read_queries, membound_factor=2):
  prune_nestings(read_queries)

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

  #print dsmeta
  mem_bound = compute_mem_bound(membound_factor)
  print 'mem_bound = {}'.format(mem_bound)
  prune_read_plans(rqmanagers, dsmeta)

  new_plan_cnt = 0
  for qi,rqmng in enumerate(rqmanagers):
    for i,plan_for_one_nesting in enumerate(rqmng.plans):
      new_plan_cnt += len(plan_for_one_nesting.plans)

  print 'old plan cnt = {}, new plan cnt = {}'.format(old_plan_cnt, new_plan_cnt)