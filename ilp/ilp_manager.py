import sys
sys.path.append('../')
from query_manager import *
from util import *
from cost import *
from ilp_helper import *
from query_manager import *
from ilp_helper import *
from gurobipy import *
#from ilp_fake import *

class PlanUseDSConstraints(object):
  def __init__(self, ds, memobj):
    self.ds = ds
    self.memobjs = memobj # key: ds id; value: a list of field
  def to_ilpv_lst(self, ds_map, memobj_map):
    lst = [ds_map[ds] for ds in self.ds]
    if len(self.memobjs) == 0:
      return lst
    for ds,fields in self.memobjs.items():
      ref_pairs = memobj_map[ds]
      for f in fields:
        if f.field_name == 'id':
          continue
        for f1,ilpv in ref_pairs:
          if f1 == f:
            lst.append(ilpv)
      return lst

# FOL constraint to ILP:
# a -> b => a <= b
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
    for d1,d2 in self.dsv_dependency:
      self.model.addConstr(self.dsv[d1] <= self.dsv[d2])

    # CONSTR 2: memobj dependency
    for ds,pairs in self.memobjv.items():
      for pair in pairs:
        self.model.addConstr(pair[1] <= self.dsv[ds])

    # CONSTR 3: data structure conflict ??

    # =========== constraints for read query ============
    # CONSTR 4: each read query has one plan
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

    # CONSTR 9: within memory bound
    cost = sum([self.dsv[ds.id]*to_real_value(ds.compute_mem_cost()) for ds_id,ds in self.ds_instance.items()])
    cost = cost + sum([sum([ilpv*f.field_class.get_sz() for f,ilpv in pair]) \
          * to_real_value(self.ds_instance[dsid].element_count()) \
            for dsid, pair in self.memobjv.items()])
    self.model.addConstr(cost <= self.mem_bound)

    # ========= set objective =========
    runtime = sum([sum([self.readq_planv[i][j] * self.readq_plancost[i][j]\
       for j in range(0, len(self.readq_planv[i]))]) for i in range(0, len(self.readqv))])
    # TODO: write run time
    self.model.setObjective(runtime, GRB.MINIMIZE)

  def add_data_structures(self, dsmng):
    ds_lst, memobj_map = self.add_ds_list_helper(dsmng.data_structures)
    temp_vars = self.model.addVars(len(ds_lst), vtype=GRB.BINARY)
    self.dsv = {ds_lst[i].id:temp_vars[i] for i in range(0, len(ds_lst))}
    self.ds_instance = {ds.id:ds for ds in ds_lst}
    for dsid,fields in memobj_map.items():
      newv = self.model.addVars(len(fields), vtype=GRB.BINARY)
      self.memobjv[dsid] = [(fields[i], newv[i]) for i in range(0, len(fields))]
    for ds in dsmng.data_structures:
      if ds.value.is_main_ptr():
        dependent = dsmng.find_primary_array_exact_match(ds.table)
        assert(dependent)
        self.dsv_dependency.append((ds.id, dependent.id))
  # return [ds_id], {ds_id:[field]}
  def add_ds_list_helper(self, lst):
    r_lst = []
    memobj_map = {}
    for ds in lst:
      r_lst.append(ds)
      if not (ds.value.is_main_ptr() or ds.value.is_aggr()):
        temp_lst, next_memobj_map = self.add_memobj_helper(ds)
        r_lst += temp_lst
        memobj_map = map_union(memobj_map, next_memobj_map)
    return r_lst, memobj_map
  # return [(ds_id,ds_mem_cost)], {ds_id:[field]}
  def add_memobj_helper(self, ds):
    obj = ds.value.get_object()
    memobj_map = {ds.id:clean_lst([None if f.field_name == 'id' else f for f in obj.fields])}
    r_lst, next_memobj_map = self.add_ds_list_helper(obj.nested_objects)
    memobj_map = map_union(memobj_map, next_memobj_map)
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
      for i,plan_for_one_nesting in enumerate(rqmng.plans):
        for j in range(0, len(plan_for_one_nesting.plans)):
          plan = plan_for_one_nesting.plans[j]
          dsmng = plan_for_one_nesting.dsmanagers[j]
          ds_lst, memobj_map = self.add_ds_list_helper(dsmng.data_structures)
          plan_constraint.append(PlanUseDSConstraints([ds_.id for ds_ in ds_lst], memobj_map))
          plan_cost.append(to_real_value(plan.compute_cost())) # TODO
      self.readq_plancost.append(plan_cost)
      self.readq_constraint.append(plan_constraint)
  def add_write_queries(self, wqmanagers):
    # TODO
    pass

  def solve(self):
    self.model.optimize()
    status = self.model.getAttr(GRB.Attr.Status)
    if status == GRB.INF_OR_UNBD or \
        status == GRB.UNBOUNDED:
      print("The model cannot be solved because it is unbounded")
      sys.exit(1)   
    if status == GRB.INFEASIBLE:
      print("The mode is not feasible")
      sys.exit(1)
    
    self.objective_value = self.model.getAttr(GRB.Attr.ObjVal)
    
  def interpret_result(self, dsmng, rqmanagers, wqmanagers=None):
    self.ret_dsmng = DSManager()
    self.ret_dsmng.data_structures = self.construct_result_dsmng_helper1(dsmng.data_structures)

    # find result plan for read queries:
    self.result_read_plans = []
    self.result_read_ds = []
    for i in range(0, len(rqmanagers)):
      rqmng = rqmanagers[i]
      cnt = 0
      plan = None
      for plan_for_one_nesting in rqmng.plans:
        for j in range(0, len(plan_for_one_nesting.plans)):
          if (self.readq_planv[i][cnt].x > 0.5):
            plan = plan_for_one_nesting.plans[j]
            dsmanager = plan_for_one_nesting.dsmanagers[j]
          cnt = cnt + 1
      assert(plan)
      self.result_read_plans.append(plan)
      self.result_read_ds.append(dsmanager)

    
    # find result plan for write queries:
    # TODO

  def construct_result_dsmng_helper1(self, lst):
    ret_lst = []
    for ds in lst:
      if self.dsv[ds.id].x > 0.5:
        new_ds = ds.fork_without_memobj()
        new_ds.id = ds.id
        if new_ds.value.is_object():
          self.construct_result_dsmng_helper2(new_ds, ds)
        ret_lst.append(new_ds)
    return ret_lst

  def construct_result_dsmng_helper2(self, ret_ds, ds):
    ret_obj = ret_ds.value.get_object()
    obj = ds.value.get_object()
    for field,ilpv in self.memobjv[ds.id]:
      if ilpv.x > 0.5:
        ret_obj.add_field(field)
    ret_obj.nested_objects = self.construct_result_dsmng_helper1(obj.nested_objects)


def test_ilp(read_queries, write_queries=[], membound_factor=2):
  rqmanagers = []
  dsmeta = DSManager()
  begin_ds_id = 1
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

  print dsmeta

  ilp = ILPVariableManager()
  ilp.mem_bound = compute_mem_bound(membound_factor)
  ilp.add_data_structures(dsmeta)
  ilp.add_read_queries(rqmanagers)

  ilp.add_constraints()
  #ilp.model.print_stat()

  ilp.solve()
  ilp.interpret_result(dsmeta, rqmanagers)

  print 'result data structures = {}'.format(ilp.ret_dsmng)
  print 'mem cost = {}'.format(to_real_value(ilp.ret_dsmng.compute_mem_cost()))
  print 'result query plan:'
  for i in range(0, len(read_queries)):
    print 'QUERY {}:'.format(i)
    print ilp.result_read_plans[i]
    print 'time cost = {}'.format(to_real_value(ilp.result_read_plans[i].compute_cost()))
    print 'actual_ds = {}'.format(ilp.result_read_ds[i])
    print '---------\n'



