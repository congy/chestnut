import sys
sys.path.append('../')
from ds import *
from ds_manager import *
from plan_search import *
from plan_helper import *
import globalv


def compute_mem_bound(factor=2):
  sz = 0
  ele_cnt = 0
  for t in globalv.tables:
    field_sz = sum([f.get_sz() for f in t.get_fields()])
    sz += t.sz*field_sz
  for a in globalv.associations:
    if a.assoc_type == 'many_to_many':
      sz += a.lft.sz * a.lft_ratio * 3
  globalv.memory_bound = sz * factor
  return sz * factor

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

    
