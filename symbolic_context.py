import z3
from constants import *
debug_constraint = False
expr_pool = []
tempv_cnt = 0
class SymbolicManager(object):
  def __init__(self):
    self.param_symbol_map = {}
    self.symbolic_tables = {}
    self.symbolic_assocs = {}
    self.symbolic_struct = None
    self.cur_update_ptr_lst = None
    self.placeholder_list = None
    self.solver = z3.Solver()

    self.index_map = []

  def register_tables_and_assocs(self,_tables, _assocs):
    global tables
    global associations
    self.tables = [t for t in _tables]
    self.associations = [a for a in _assocs]

  def get_param_symbol_map(self, p):
    if p in self.param_symbol_map:
      return self.param_symbol_map[p]
    else:
      global tempv_cnt
      newv = get_symbol_by_field_type(p.get_type(), '{}_{}'.format(p.symbol, tempv_cnt))
      tempv_cnt += 1
      self.param_symbol_map[p] = newv
  def set_global_symbolic_struct(self, r):
    self.symbolic_struct = r
  def get_global_symbolic_struct(self):
    return self.symbolic_struct

  def set_cur_update_ptr_lst(self, r):
    self.cur_update_ptr_lst = r
  def get_cur_update_ptr_lst(self):
    return self.cur_update_ptr_lst

  def set_placeholder_list(self, r):
    self.placeholder_list = r
  def get_placeholder_list(self):
    return self.placeholder_list

  def clear_solver(self):
    self.solver = z3.Solver()

  def add_to_index_map(self, idx, symbolic_idx):
    self.idx_map.append((idx, symbolic_idx))
  
  def exist_symbolic_idx(self, idx):
    for k,v in self.idx_map:
      if k==idx:
        return v
    return None

class ThreadCtx(object):
  def __init__(self):
    self.symbolic_manager = SymbolicManager()
  def get_symbs(self):
    return self.symbolic_manager

def create_thread_ctx():
  return ThreadCtx()