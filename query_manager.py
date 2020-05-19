from ds import *
from ds_manager import *
from query import *
from plan_search import *


# one query & one data layout  -- > one query plan
# one data layout--> one nesting + a set of indexes
class RQManager(object):
  def __init__(self, query, plans=[]):
    self.query = query
    self.frequency = 1
    self.plans = plans # list of PlansForOneNesting

class WQManager(object):
  def __init__(self, query):
    self.query = query
    self.frequency = 1
    self.ds = [] # TODO


# manager that merges all ds

# index/array; fields in object

# return last_ds_id and the set of delta index/array newly added to dsmeta

def collect_all_structures(dsmeta, dsmng, begin_ds_id=1):
  return data_structures_merge_helper(dsmeta.data_structures, dsmng.data_structures, begin_ds_id, dsmng.data_structures)

def data_structures_merge_helper(lst1, lst2, begin_ds_id, topds, upperds=None):
  cur_ds_id = begin_ds_id
  delta_structures = []
  temp_lst1 = [ds for ds in lst1]

  # copy id in lst1
  pairs = []
  for ds2 in lst2:
    exist = False
    for ds1 in temp_lst1:
      if ds1 == ds2:
        ds2.id = ds1.id
        pairs.append((ds1, ds2))
        exist = True
        break
    if not exist:
      tempds = ds2.fork_without_memobj()
      tempds.id = cur_ds_id
      ds2.id = cur_ds_id
      cur_ds_id = cur_ds_id + 1
      tempds.upper = upperds
      ds2.upper = upperds
      delta_structures.append(tempds)
      lst1.append(tempds)
      pairs.append((tempds, ds2))
  assert(len(pairs) == len(lst2)) 
  for ds1,ds2 in pairs:
    new_ds_id, new_delta = collect_structures_helper_index(ds1, ds2, cur_ds_id, topds, upperds)
    cur_ds_id = new_ds_id
    delta_structures += new_delta

  for i,ds2 in enumerate(lst2):
    if ds2.value.is_main_ptr():
      dependent_ds = ds2.value.value
      for ds1 in topds:
        if ds1.eq_without_memobj(dependent_ds):
          ds2.value.value = ds1
          pairs[i][0].value.value = ds1
      assert(ds2.value.value.id > 0)
    #if ds2.upper:
    #  pairs[i][0].upper = ds2.upper
  return cur_ds_id, delta_structures

def collect_structures_helper_memobj(obj, newobj, begin_ds_id, topds, upperds):
  obj.add_fields(newobj.fields)
  return data_structures_merge_helper(obj.nested_objects, newobj.nested_objects, begin_ds_id, topds, upperds)

def collect_structures_helper_index(ds, newds, begin_ds_id, topds, upperds):
  if ds.value.is_main_ptr() or ds.value.is_aggr():
    return begin_ds_id, []
  return collect_structures_helper_memobj(ds.value.get_object(), newds.value.get_object(), begin_ds_id, topds, ds)

compatible_ds_list = []
not_compatible_ds_list = []
# check ds1 can be replaced with ds2
# if yes, return (newop, newparams)
def compatible_ds_pairs(ds1, step, ds2, thread_ctx):
  global compatible_ds_list
  global not_compatible_ds_list
  if len(step.params) > 1:
    return None
  if isinstance(ds1, ObjBasicArray) or isinstance(ds2, ObjBasicArray):
    return None
  if not ds1.table == ds2.table:
    return None
  # if not ds1.value.eq_without_memobj(ds2.value):
  #   return None
  if not set_include(ds2.key_fields(), ds1.key_fields()):
    return None
  if ds1.condition.idx_pred_eq(ds2.condition):
    return None
  ds1_param = step.params[0]
  if len(ds2.key_fields()) > len(ds1.key_fields()):
    q2_params = [IndexParam(), IndexParam()]
    for k in ds2.key_fields():
      if k in step.params[0].fields:
        q2_params[0].add_param(k, ds1_param.find_param_by_field(k))
        q2_params[1].add_param(k, ds1_param.find_param_by_field(k))
      else:
        q2_params[0].add_param(k, AtomValue(k.get_query_field().field_class.get_min_value()))
        q2_params[1].add_param(k, AtomValue(k.get_query_field().field_class.get_max_value()))
    q2_op = IndexOp(RANGE)
  else:
    q2_params = [IndexParam()]
    for k in ds2.key_fields():
      q2_params[0].add_param(k, ds1_param.find_param_by_field(k))
    q2_op = step.op
  if '{}-{}'.format(ds1.id, ds2.id) in compatible_ds_list:
    r = True
  if '{}-{}'.format(ds1.id, ds2.id) in not_compatible_ds_list:
    return None
  else:
    symbolic_ds1 = SymbolicIndex(ds1, None, thread_ctx)
    symbolic_result1 = symbolic_ds1.get_symbolic_tuple_with_cond(step.op, step.params)[0]
    symbolic_ds2 = SymbolicIndex(ds2, None, thread_ctx)
    #print 'ds2 = {}, op = {}, param = {}'.format(ds2.__str__(short=True), q2_op, q2_params)
    symbolic_result2 = symbolic_ds2.get_symbolic_tuple_with_cond(q2_op, q2_params)[0]
    r = check_dsop_equiv(thread_ctx, ds1.table, symbolic_result1, symbolic_result2)
    if r:
      compatible_ds_list.append('{}-{}'.format(ds1.id, ds2.id))
    else:
      not_compatible_ds_list.append('{}-{}'.format(ds1.id, ds2.id))
  #print 'compare {} and {}'.format(ds1, ds2)
  if r:
    news = step.fork()
    news.idx = ds2
    news.op = q2_op
    news.params = q2_params
    #print 'find compatible!: ds1 = {}\nds2 = {}'.format(step, news)
    return news
  return None

# FIXME
# now it only replace top ds
def replace_compatible_ds(step, cur_obj, dsmeta, thread_ctx):
  if isinstance(step, ExecQueryStep):
    news = replace_compatible_ds(step.step, cur_obj, dsmeta, thread_ctx)
    if len(news) > 0:
      r = []
      for s in news:
        e = ExecQueryStep(step.query, step.new_params)
        e.variables = [v for v in step.variables]
        e.step = s
        r.append(e)
      return r
    return []
  elif isinstance(step, ExecStepSeq):
    for i,s in enumerate(step.steps):
      news = replace_compatible_ds(s, cur_obj, dsmeta, thread_ctx)
      if len(news) > 0:
        r = []
        for s1 in news:
          e = step.fork()
          e.steps[i] = s1
          r.append(e)
        return r
    return []
  elif isinstance(step, ExecScanStep):
    ds1 = step.idx
    new_steps = []
    for ds2 in dsmeta.data_structures:
      r1 = compatible_ds_pairs(ds1, step, ds2, thread_ctx)
      if r1:
        new_steps.append(r1)
    return new_steps
  else:
    return []
  # if isinstance(step, ExecStepSeq):
  # if isinstance(step, ExecSortStep):
  # if isinstance(step, ExecUnionStep):
  # if isinstance(step, ExecGetAssocStep):
  # if isinstance(step, ExecScanStep):

def get_dsmeta(read_queries):
  rqmanagers = []
  dsmeta = DSManager()
  begin_ds_id = 1
  for query in read_queries:
    print("query {}".format(query))
    nesting_plans = search_plans_for_one_query(query, print_plan=False)
    rqmanagers.append(RQManager(query, nesting_plans))
    for i,plan_for_one_nesting in enumerate(nesting_plans):
      #print 'nesting...{}'.format(len(plan_for_one_nesting.plans))
      dsmng = plan_for_one_nesting.nesting
      for j,plan in enumerate(plan_for_one_nesting.plans):
        new_dsmnger = dsmng.copy_tables()
        plan.get_used_ds(None, new_dsmnger)
        begin_ds_id, deltas = collect_all_structures(dsmeta, new_dsmnger, begin_ds_id)
        plan.copy_ds_id(None, new_dsmnger)
        rqmanagers[-1].plans[i].dsmanagers.append(new_dsmnger)


  thread_ctx = symbctx.create_thread_ctx()
  create_symbolic_obj_graph(thread_ctx, globalv.tables, globalv.associations)
  for qi, query in enumerate(read_queries):
    create_param_map_for_query(thread_ctx, query)
    nesting_plans = rqmanagers[qi].plans
    total_new_plans = 0
    for i,plan_for_one_nesting in enumerate(nesting_plans):
      dsmng = plan_for_one_nesting.nesting
      add_plans = []
      add_dsmngers = []
      for j,plan in enumerate(plan_for_one_nesting.plans):
        newplans = replace_compatible_ds(plan, None, dsmeta, thread_ctx)
        for newplan in newplans:
          new_dsmnger = dsmng.copy_tables()
          newplan.get_used_ds(None, new_dsmnger)
          begin_ds_id, deltas = collect_all_structures(dsmeta, new_dsmnger, begin_ds_id)
          add_plans.append(newplan)
          add_dsmngers.append(new_dsmnger)
      total_new_plans += len(add_plans)
      rqmanagers[qi].plans[i].plans += add_plans
      rqmanagers[qi].plans[i].dsmanagers += add_dsmngers
    print "finish find compatible ds for query {}, total new plan len = {}".format(qi, total_new_plans)

  return rqmanagers, dsmeta

def test_merge(query):
  rqmanagers, dsmeta = get_dsmeta([query])
  print dsmeta
  print_ds_with_cost(dsmeta)

def test_cost(queries):
  rqmanagers, dsmeta = get_dsmeta(queries)
  ds_lst, memobj = collect_all_ds_helper1(dsmeta.data_structures)
  for ds in ds_lst:
    print 'ds {} cost = {}'.format(ds.__str__(True), to_real_value(ds.compute_mem_cost()))
    print ''
  for k,v in memobj.items(): 
    cnt = k.element_count()
    print 'memobj {} #element = {}'.format(k.__str__(True), to_real_value(cnt))
    print ''
