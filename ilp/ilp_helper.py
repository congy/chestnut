import sys
sys.path.append('../')
from ds import *
from ds_manager import *
from plan_search import *
from plan_helper import *


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


def index_conflict(idx1, idx2):
  if not type(idx1) == type(idx2):
    return False
  if isinstance(idx1, ObjBasicArray) and isinstance(idx2, ObjBasicArray):
    if (not isinstance(idx1.table, NestedTable)) and (not isinstance(idx2.table, NestedTable)):
      if idx1.table.contain_table(idx2.table) or idx2.table.contain_table(idx1.table):
        return True
    elif not idx1.table == idx2.table:
      return False 
    elif not idx1.value == idx2.value:
      return True
  if idx1.condition.idx_pred_eq(idx2.condition) and not (idx1.value == idx2.value):
    return True
  return False

def test_merge(query):
  nesting_plans = search_plans_for_one_query(query)
  dsmeta = DSManager()
  begin_ds_id = 1
  for plan_for_one_nesting in nesting_plans:
    print 'nesting...{}'.format(len(plan_for_one_nesting.plans))
    dsmng = plan_for_one_nesting.nesting
    for plan in plan_for_one_nesting.plans:
      new_dsmnger = dsmng.copy_tables()
      plan.get_used_ds(None, new_dsmnger)
      begin_ds_id, deltas = collect_all_structures(dsmeta, new_dsmnger, begin_ds_id)
  print dsmeta

  print_ds_with_cost(dsmeta)

    