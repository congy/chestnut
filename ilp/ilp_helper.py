import sys
sys.path.append('../')
from ds import *
from ds_manager import *
from plan_search import *
from plan_helper import *
import globalv

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

    
