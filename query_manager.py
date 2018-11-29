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
  return data_structures_merge_helper(dsmeta.data_structures, dsmng.data_structures, begin_ds_id)

def data_structures_merge_helper(lst1, lst2, begin_ds_id):
  cur_ds_id = begin_ds_id
  delta_structures = []
  temp_lst1 = [ds for ds in lst1]
  for ds2 in lst2:
    exist = False
    for ds1 in temp_lst1:
      if ds1 == ds2:
        ds2.id = ds1.id
        cur_ds_id, new_delta = collect_structures_helper_index(ds1, ds2, cur_ds_id)
        delta_structures += new_delta
        exist = True
    if not exist:
      tempds = ds2.fork_without_memobj()
      cur_ds_id = cur_ds_id + 1
      tempds.id = cur_ds_id
      ds2.id = cur_ds_id
      delta_structures.append(tempds)
      lst1.append(tempds)
      new_ds_id, new_delta = collect_structures_helper_index(tempds, ds2, cur_ds_id)
      cur_ds_id = new_ds_id
      delta_structures += new_delta
  return cur_ds_id, delta_structures

def collect_structures_helper_memobj(obj, newobj, begin_ds_id):
  obj.add_fields(newobj.fields)
  return data_structures_merge_helper(obj.nested_objects, newobj.nested_objects, begin_ds_id)

def collect_structures_helper_index(ds, newds, begin_ds_id):
  if ds.value.is_main_ptr() or ds.value.is_aggr():
    return begin_ds_id, []
  return collect_structures_helper_memobj(ds.value.get_object(), newds.value.get_object(), begin_ds_id)

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
        rqmanagers[-1].plans[i].dsmanagers.append(new_dsmnger)
        begin_ds_id, deltas = collect_all_structures(dsmeta, new_dsmnger, begin_ds_id)
  return rqmanagers, dsmeta

def test_merge(query):
  rqmanagers, dsmeta = get_dsmeta([query])
  print dsmeta
  print_ds_with_cost(dsmeta)
