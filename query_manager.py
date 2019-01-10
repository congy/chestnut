from ds import *
from ds_manager import *
from query import *
from plan_search import *


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

  # for ds2 in lst2:
  #   exist = False
  #   for ds1 in temp_lst1:
  #     if ds1 == ds2:
  #       ds2.id = ds1.id
  #       cur_ds_id, new_delta = collect_structures_helper_index(ds1, ds2, cur_ds_id, topds, upperds)
  #       delta_structures += new_delta
  #       exist = True
  #   if not exist:
  #     tempds = ds2.fork_without_memobj()
  #     cur_ds_id = cur_ds_id + 1
  #     tempds.id = cur_ds_id
  #     ds2.id = cur_ds_id
  #     tempds.upper = upperds
  #     ds2.upper = upperds
  #     delta_structures.append(tempds)
  #     lst1.append(tempds)
  #     new_ds_id, new_delta = collect_structures_helper_index(tempds, ds2, cur_ds_id, topds, upperds)
  #     cur_ds_id = new_ds_id
  #     delta_structures += new_delta

  for i,ds2 in enumerate(lst2):
    if ds2.value.is_main_ptr():
      dependent_ds = ds2.value.value
      for ds1 in topds:
        if ds1.eq_without_memobj(dependent_ds):
          ds2.value.value = ds1
          pairs[i][0].value.value = ds1
      assert(ds2.value.value.id > 0)
  return cur_ds_id, delta_structures

def collect_structures_helper_memobj(obj, newobj, begin_ds_id, topds, upperds):
  obj.add_fields(newobj.fields)
  return data_structures_merge_helper(obj.nested_objects, newobj.nested_objects, begin_ds_id, topds, upperds)

def collect_structures_helper_index(ds, newds, begin_ds_id, topds, upperds):
  if ds.value.is_main_ptr() or ds.value.is_aggr():
    return begin_ds_id, []
  return collect_structures_helper_memobj(ds.value.get_object(), newds.value.get_object(), begin_ds_id, topds, ds)

def get_dsmeta(read_queries):
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
        begin_ds_id, deltas = collect_all_structures(dsmeta, new_dsmnger, begin_ds_id)
        plan.copy_ds_id(None, new_dsmnger)
        rqmanagers[-1].plans[i].dsmanagers.append(new_dsmnger)

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
