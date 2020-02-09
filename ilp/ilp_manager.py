import sys
sys.path.append('../')
from query_manager import *
from util import *
from cost import *
from .ilp_helper import *
from constants import *
from query_manager import *
from .ilp_helper import *
from .prune_plans import *
from ds_manager import *
import multiprocessing
import pickle

# TODO: use gurobipy when you have a license.
from .ilp_fake import *
#from gurobipy import *

class PlanUseDSConstraints(object):
  def __init__(self, ds, memobj):
    self.ds = ds
    self.memobjs = memobj # key: ds id; value: a list of field
  def to_ilpv_lst(self, ds_map, memobj_map):
    lst = [ds_map[ds] for ds in self.ds]
    if len(self.memobjs) == 0:
      return lst
    for ds,fields in list(self.memobjs.items()):
      ref_pairs = memobj_map[ds]
      for f in fields:
        if f.field_name == 'id':
          continue
        exists_ref = None
        for f1,ilpv in ref_pairs:
          if f1 == f:
            lst.append(ilpv)
            exists_ref = f1
        if exists_ref is None:
          print('ds = {}, check ref f = {}'.format(ds, f))
        assert(exists_ref)
    return lst

# FOL constraint to ILP:
# a -> b => a <= b
# This class interfaces with gurobi ILP solver.
class ILPVariableManager(object):
  def __init__(self):
    self.model = Model('idxsearch')
    self.readqv = []
    self.readq_frequency = []
    self.readq_planv = [] # [plan_ilpv]
    self.readq_plancost = []
    self.readq_constraint = []
    self.writeqv = []
    self.writeq_frequency = []
    self.writeq_planv = [] # key: writeq id; value: {ds:[plan_ilpv]}
    self.writeq_plancost = []
    self.writeq_constraint = []
    self.dsv = {} # key: ds id; value: dsv
    self.ds_instance = {} # key: ds id; value: ds instance
    self.memobjv = {} # key: ds id; value: a list of (field, ilpv)
    self.dsv_dependency = [] # pair of (ptr_index, basic_ary)
    self.mem_bound = 0
  def add_constraints(self):
    # =========== constraints for data structures ============
    # CONSTR 1: data structure dependency for pointers
    for d1, d2 in self.dsv_dependency:
      self.model.addConstr(self.dsv[d1] <= self.dsv[d2])

    # CONSTR 2: memobj dependency
    # A contains B (nesting). Then if B exists A must exist.
    for ds, pairs in list(self.memobjv.items()):
      for pair in pairs:
        self.model.addConstr(pair[1] <= self.dsv[ds])

    # CONSTR 3: data structure conflict ??

    # =========== constraints for read query ============
    # CONSTR 4: each read query must have exactly one plan
    for i in range(0, len(self.readqv)):
      self.model.addConstr(self.readqv[i] == or_(self.readq_planv[i]))
      self.model.addConstr(self.readqv[i] == 1)

    # CONSTR 5: each plan use structures/memobjs
    for i in range(0, len(self.readqv)):
      Nplans = len(self.readq_planv[i])
      tempv = self.model.addVars(Nplans,  vtype=GRB.BINARY)
      for j in range(0, Nplans):
        self.model.addConstr(tempv[j] == and_(self.readq_constraint[i][j].to_ilpv_lst(self.dsv, self.memobjv)))
        self.model.addConstr(self.readq_planv[i][j] <= tempv[j])

    # =========== constraints for write query ============
    # CONSTR 6: each data structure is updated correctly

    # CONSTR 7: each write query for a data structure has one plan

    # CONSTR 8: each plan use structures/memobjs

    # =========== ===========
    # CONSTR 9: within memory bound
    # compute_mem_cost() computes memory cost of data structure.
    cost = sum([self.dsv[ds.id]*to_real_value(ds.compute_mem_cost()) for ds_id,ds in list(self.ds_instance.items())])
    cost = cost + sum([sum([ilpv*f.field_class.get_sz() for f,ilpv in pair]) \
          * to_real_value(self.ds_instance[dsid].element_count()) \
            for dsid, pair in list(self.memobjv.items())])
    self.model.addConstr(cost <= self.mem_bound)

    # ========= set objective =========
    # Objective is weighted sum of query times.
    runtime = sum([sum([self.readq_planv[i][j] * self.readq_plancost[i][j]\
       for j in range(0, len(self.readq_planv[i]))]) for i in range(0, len(self.readqv))])
    # TODO: write run time
    self.model.setObjective(runtime, GRB.MINIMIZE)

  def add_data_structures(self, dsmng):
    ds_lst, memobj_map = self.add_ds_list_helper(dsmng.data_structures)
    temp_vars = self.model.addVars(len(ds_lst), vtype=GRB.BINARY)
    self.dsv = {ds_lst[i].id:temp_vars[i] for i in range(0, len(ds_lst))}
    self.ds_instance = {ds.id:ds for ds in ds_lst}
    for dsid,fields in list(memobj_map.items()):
      newv = self.model.addVars(len(fields), vtype=GRB.BINARY)
      self.memobjv[dsid] = [(fields[i], newv[i]) for i in range(0, len(fields))]
    for ds in ds_lst:
      if ds.value.is_main_ptr():
        #dependent = dsmng.find_primary_array_exact_match(ds.table)
        dependent = ds.value.value
        if (not dependent and dependent.id > 0):
          print('ds fail! {}'.format(ds))
        assert(dependent and dependent.id > 0)
        self.dsv_dependency.append((ds.id, dependent.id))
        #print 'ds {} pointer depends on {}'.format(ds.id, dependent.id)
      if isinstance(ds.table, NestedTable):
        assert(ds.upper)
        self.dsv_dependency.append((ds.id, ds.upper.id))
        #print 'ds {} nested depends on {}'.format(ds.id, ds.upper.id)
  # return [ds_id], {ds_id:[field]}
  def add_ds_list_helper(self, lst):
    r_lst = []
    memobj_map = {}
    for ds in lst:
      r_lst.append(ds)
      if not (ds.value.is_main_ptr() or ds.value.is_aggr()):
        temp_lst, next_memobj_map = self.add_memobj_helper(ds)
        r_lst += temp_lst
        memobj_map = map_union(memobj_map, next_memobj_map, merge_func=(lambda x,y: x.merge(y)))
    return r_lst, memobj_map
  # return [(ds_id,ds_mem_cost)], {ds_id:[field]}
  def add_memobj_helper(self, ds):
    obj = ds.value.get_object()
    for f in obj.fields:
      assert(isinstance(f, QueryField) and f.table == get_main_table(obj.table))
    memobj_map = {ds.id:clean_lst([None if f.field_name == 'id' else f for f in obj.fields])}
    r_lst, next_memobj_map = self.add_ds_list_helper(obj.nested_objects)
    memobj_map = map_union(memobj_map, next_memobj_map, merge_func=(lambda x,y: x.merge(y)))
    return r_lst, memobj_map
  def add_read_queries(self, rqmanagers):
    self.readqv = self.model.addVars(len(rqmanagers), vtype=GRB.BINARY)
    self.readq_planv = [0 for i in range(0, len(rqmanagers))]
    for idx,rqmng in enumerate(rqmanagers):
      self.readq_frequency.append(rqmng.frequency)
      Nplans = sum([len(plan_for_one_nesting.plans) for plan_for_one_nesting in rqmng.plans])
      self.readq_planv[idx] = self.model.addVars(Nplans, vtype=GRB.BINARY)
      plan_cost = []
      plan_constraint = []
      cnt = 0
      for i,plan_for_one_nesting in enumerate(rqmng.plans):
        for j in range(0, len(plan_for_one_nesting.plans)):
          plan = plan_for_one_nesting.plans[j]
          dsmng = plan_for_one_nesting.dsmanagers[j]
          ds_lst, memobj_map = self.add_ds_list_helper(dsmng.data_structures)
          #print 'Query {} plan {}:'.format(idx, cnt)
          #print 'ds: {}'.format(','.join([str(ds.id) for ds in ds_lst]))
          #for k,v in memobj_map.items():
          #  print '  ds {} has fields {}'.format(k, ','.join([str(f) for f in v]))
          #cnt = cnt + 1
          plan_constraint.append(PlanUseDSConstraints([ds_.id for ds_ in ds_lst], memobj_map))
          plan_cost.append(to_real_value(plan.compute_cost())) # TODO
      self.readq_plancost.append(plan_cost)
      self.readq_constraint.append(plan_constraint)
  def add_write_queries(self, wqmanagers):
    # TODO
    pass

  def solve(self):
    self.model.optimize() # solves ILP (gurobi).
    status = self.model.getAttr(GRB.Attr.Status)
    # Failure cases.
    if status == GRB.INF_OR_UNBD or \
        status == GRB.UNBOUNDED:
      print("The model cannot be solved because it is unbounded")
      sys.exit(1)   
    if status == GRB.INFEASIBLE:
      print("The mode is not feasible")
      sys.exit(1)
    
    # Result of objective. Recall objective is weighted sum of (theoretical) query times.
    self.objective_value = self.model.getAttr(GRB.Attr.ObjVal)
    
  # Interprets the ILP results as the actual chosen datastructures and query plans.
  def interpret_result(self, dsmng, rqmanagers, wqmanagers=None):
    self.ret_dsmng = DSManager()
    self.ret_dsmng.data_structures = self.construct_result_dsmng_helper1(dsmng.data_structures)

    # find result plan for read queries:
    self.result_read_plans = []
    self.result_read_ds = []
    self.result_read_plan_id = []
    for i in range(0, len(rqmanagers)):
      rqmng = rqmanagers[i]
      cnt = 0
      plan = None
      planid = 0
      for plan_for_one_nesting in rqmng.plans:
        for j in range(0, len(plan_for_one_nesting.plans)):
          # For some reasone gurobi returns non-bool values.
          # > 0.5 means 1 (true).
          if (self.readq_planv[i][cnt].x > 0.5):
            plan = plan_for_one_nesting.plans[j]
            dsmanager = plan_for_one_nesting.dsmanagers[j]
            planid = cnt
          cnt = cnt + 1
      assert(plan)
      self.result_read_plans.append(plan)
      self.result_read_ds.append(dsmanager)
      self.result_read_plan_id.append(planid)

    # find result plan for write queries:
    # TODO

  def construct_result_dsmng_helper1(self, lst, upperds=None):
    ret_lst = []
    for ds in lst:
      if self.dsv[ds.id].x > 0.5:
        new_ds = ds.fork_without_memobj()
        new_ds.id = ds.id
        new_ds.upper = upperds
        if new_ds.value.is_object():
          self.construct_result_dsmng_helper2(new_ds, ds, new_ds)
        ret_lst.append(new_ds)
    return ret_lst

  def construct_result_dsmng_helper2(self, ret_ds, ds, upperds):
    ret_obj = ret_ds.value.get_object()
    obj = ds.value.get_object()
    for field,ilpv in self.memobjv[ds.id]:
      if ilpv.x > 0.5:
        ret_obj.add_field(field)
    ret_obj.nested_objects = self.construct_result_dsmng_helper1(obj.nested_objects, upperds)


def print_ilp_result(read_queries, ilp):
  print('result data structures = {}'.format(ilp.ret_dsmng))
  print('mem cost = {}'.format(to_real_value(ilp.ret_dsmng.compute_mem_cost())))
  print('cost breakdown: ')
  ds_lst, memobj = collect_all_ds_helper1(ilp.ret_dsmng.data_structures)
  for ds in ds_lst:
    print('ds {} cost = {}'.format(ds.id, to_real_value(ds.compute_mem_cost())))
  for k,v in list(memobj.items()): 
    cnt = k.element_count()
    field_sz = sum([f.field_class.get_sz() for f in v.fields])
    print('memobj {} #ele = {}, field = {}, cost = {}'.format(k.__str__(True), to_real_value(cnt), field_sz, to_real_value(cost_mul(cnt, field_sz))))

  print('result query plan:')
  for i in range(0, len(read_queries)):
    print('QUERY {} plan {}:'.format(i, ilp.result_read_plan_id[i]))
    print(ilp.result_read_plans[i])
    print('time cost = {}'.format(to_real_value(ilp.result_read_plans[i].compute_cost())))
    print('actual_ds = {}'.format(ilp.result_read_ds[i]))
    print('---------\n')


import time
def test_ilp(read_queries, membound_factor=1):
  ilp_solve(read_queries, membound_factor=1)

def ilp_solve(read_queries, write_queries=[], membound_factor=1, save_to_file=False, read_from_file=False, read_ilp=False, save_ilp=False):
  
  #prune_nestings(read_queries)
  mem_bound = compute_mem_bound(membound_factor)

  start_time = time.time()
  
  if read_ilp == False:
    if read_from_file:
      manager = multiprocessing.Manager()
      temp_rqmanagers = manager.dict() #[None for i in range(0, len(read_queries))]
      processing_jobs = []
      def read_pickle_file(ix, rqmanagers):
        f = open('q{}_plan.pickle'.format(ix), 'r')
        rqmanagers[ix] = pickle.load(f)
        assert(rqmanagers[ix])
        print('read file {}'.format(ix))
        f.close()

      for i in range(0, len(read_queries)):
        p = multiprocessing.Process(target=read_pickle_file, args=(i, temp_rqmanagers))
        processing_jobs.append(p)
        p.start()
      for p in processing_jobs:
        p.join()

      f = open('dsmeta.pickle', 'r')
      dsmeta = pickle.load(f)
      f.close()
      assert(len(temp_rqmanagers) == len(read_queries))
      rqmanagers = [None for i in range(0, len(read_queries))]
      for i in range(0, len(read_queries)):
        if i not in temp_rqmanagers:
          print('manager {} is None!'.format(i))
        else:
          rqmanagers[i] = temp_rqmanagers[i]
      for i in range(0, len(read_queries)):
        assert(rqmanagers[i])
    else:
      rqmanagers, dsmeta = get_dsmeta(read_queries) # Does data structure/query plan search.
      # TODO why is this disabled
      #prune_read_plans(rqmanagers, dsmeta)
      if save_to_file:
        for i in range(0, len(rqmanagers)):
          f = open('q{}_plan.pickle'.format(i), 'w')
          pickle.dump(rqmanagers[i], f)
          f.close()
        f = open('dsmeta.pickle', 'w')
        pickle.dump(dsmeta, f)
        f.close()
    
    print('load time = {}'.format(time.time()-start_time))
    print(dsmeta)

    total_Nplans = 0
    # rqmanagers: ReadQueryManagers has a list of list.
    # list of PlansPerNesting, each contains multiple plans (data layouts/queries).
    for qi,rqmng in enumerate(rqmanagers):
      Nqplans = sum([len(xxx.plans) for xxx in rqmng.plans])
      print("query {} has {} plans ({}) nestings".format(qi, Nqplans, len(rqmng.plans)))
      total_Nplans += Nqplans
    print("total: {}".format(total_Nplans))

  if read_ilp:
    f = open('mem{}_ilp.pickle'.format(membound_factor), 'r')
    ilp = pickle.load(f)
    f.close()
  else:
    # Configur ILPVariableManager which interfaces with gurobi.
    ilp = ILPVariableManager()
    ilp.mem_bound = mem_bound 
    ilp.add_data_structures(dsmeta)
    ilp.add_read_queries(rqmanagers)

    ilp.add_constraints()
    
    # ilp.model.print_stat()
    # exit(0)
    ilp.solve()
    ilp.interpret_result(dsmeta, rqmanagers)
    if save_ilp:
      f = open('mem{}_ilp.pickle'.format(membound_factor), 'w')
      new_ilp = ILPVariableManager()
      new_ilp.model = None
      new_ilp.ret_dsmng = ilp.ret_dsmng
      new_ilp.result_read_plans = ilp.result_read_plans 
      new_ilp.result_read_ds = ilp.result_read_ds
      new_ilp.result_read_plan_id = ilp.result_read_plan_id
      new_ilp.mem_bound = ilp.mem_bound
      pickle.dump(new_ilp, f)
      f.close()

  print('MEMORY BOUND = {}'.format(ilp.mem_bound))
  print_ilp_result(read_queries, ilp)

  dsmeta = ilp.ret_dsmng
  plans = ilp.result_read_plans
  plan_ds = ilp.result_read_ds
  plan_id = ilp.result_read_plan_id

  # Return the final processed results of the ILP plan.
  return (dsmeta, plans, plan_ds, plan_id)


