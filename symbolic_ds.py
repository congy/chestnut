from schema import *
from constants import *
from query import *
from nesting import *
from planIR import *
from symbolic_pred import *
from symbolic_helper import *
import z3
import itertools


class SymbolicIndexEntry(object):
  def __init__(self, ids, condition, keys, qfs):
    self.ids = ids
    self.keys = keys
    self.invalid_value = [get_invalid_z3v_by_type(get_query_field(qf).field_class) for qf in qfs]
    self.condition = z3.And(condition, self.keys_valid_cond())
  def keys_valid_cond(self):
    valid_conds = []
    for i,k in enumerate(self.keys):
      if self.invalid_value[i] is not None:
        valid_conds.append(k!=self.invalid_value[i])
    return and_exprs(valid_conds)


class SymbolicIndex(object):
  def __init__(self, idx, upper_cond_lambda=None, thread_ctx=None, init_tuples=True):
    self.idx = idx
    self.tables = [] #list of tables in denormalized
    self.keys = [] #list of key fields
    self.tuples = []
    self.upper_cond_lambda = upper_cond_lambda #lambda id, x: If (id==...) x False
    self.thread_ctx = thread_ctx
    if init_tuples:
      if isinstance(self.idx, ObjBasicArray):
        self.build_from_basic()
      else:
        self.build_from_idx()

  def build_from_basic(self):
    main_t = get_main_table(self.idx.table)
    if isinstance(main_t, DenormalizedTable):
      assert(self.upper_cond_lambda is None)
      self.tables = main_t
      for i,symbolic_tuple in enumerate(self.thread_ctx.get_symbs().symbolic_tables[main_t].symbols):
        self.tuples.append(SymbolicIndexEntry(get_ids_from_denormalized_symb(main_t, symbolic_tuple), \
              self.thread_ctx.get_symbs().symbolic_tables[main_t].exists[i], [], [])) 
    else:
      self.tables = [main_t]
      for i,symbolic_tuple in enumerate(self.thread_ctx.get_symbs().symbolic_tables[main_t].symbols):
        if self.upper_cond_lambda:
          cond = self.upper_cond_lambda(i+1)
        else:
          cond = True
        self.tuples.append(SymbolicIndexEntry([i+1], cond, [], [])) 

  def build_from_idx(self):
    pred = self.idx.condition
    self.keys = [k for k in self.idx.keys.keys]
    self.tables = get_denormalized_tables(pred)
    temp_keys = get_denormalized_keys(pred)
    assert(set_equal(self.keys, temp_keys))
    new_key_order = []
    for k in self.keys:
      pos = 0
      for j,k1 in enumerate(temp_keys):
        if k == k1:
          pos = j
      new_key_order.append(pos)
    all_table_ids = [range(1, self.thread_ctx.get_symbs().symbolic_tables[t].sz+1) for t in self.tables]
    main_t = get_main_table(self.idx.table)
    self.tables.insert(0, main_t)
    for i,symbolic_tuple in enumerate(self.thread_ctx.get_symbs().symbolic_tables[main_t].symbols):
      for table_ids in itertools.product(*all_table_ids):
        cnt, keys, cond = get_denormalizing_cond_helper(self.thread_ctx, symbolic_tuple, pred, 0, table_ids)
        assert(all([keys[i1][0]==temp_keys[i1] for i1 in range(0, len(temp_keys))]))
        if self.upper_cond_lambda:
          cond = self.upper_cond_lambda(i+1, cond)
        symbol_tuple = SymbolicIndexEntry([i+1]+list(table_ids), cond, \
              [keys[new_key_order[i1]][1] for i1 in range(0, len(self.keys))], \
              [keys[new_key_order[i1]][0] for i1 in range(0, len(self.keys))])
        self.tuples.append(symbol_tuple)

  def get_symbolic_tuple_with_cond(self, idx_op, params):
    main_symbol_t = self.thread_ctx.get_symbs().symbolic_tables[self.tables[0]]
    ret_idx = [[] for i in range(0, main_symbol_t.sz)]
    for tup in self.tuples:
      main_id = tup.ids[0]
      if len(params) > 0:
        if idx_op == RANGE:
          prev_eq_lft = True
          prev_eq_rgt = True
          cond_lft = False
          cond_rgt = False
          for i in range(0, len(tup.keys)):
            if isinstance(params[0].params[i], Parameter): 
              param0 = self.thread_ctx.get_symbs().param_symbol_map[params[0].params[i]]
            elif isinstance(params[0].params[i], QueryField):
              assert(False)
            elif value_is_basic_type(params[0].params[i]):
              param0 = params[0].params[i]
            else:
              assert(False)
            if isinstance(params[1].params[i], Parameter): 
              param1 = self.thread_ctx.get_symbs().param_symbol_map[params[1].params[i]]
            elif isinstance(params[1].params[i], QueryField):
              assert(False)
            elif value_is_basic_type(params[1].params[i]):
              param1 = params[1].params[i]
            else:
              assert(False)
            # special cases:
            if is_bool(get_query_field(self.keys[i]).field_class):
              tup_v = z3.If(tup.keys[i], 1, 0)
            else:
              tup_v = tup.keys[i]
            cond_lft = z3.Or(cond_lft, z3.And(prev_eq_lft, tup_v > param0))
            cond_rgt = z3.Or(cond_rgt, z3.And(prev_eq_rgt, tup_v < param1))
            prev_eq_lft = z3.And(prev_eq_lft, tup_v == param0)
            prev_eq_rgt = z3.And(prev_eq_rgt, tup_v == param1)
          cond_lft = z3.Or(cond_lft, prev_eq_lft)
          cond_rgt = z3.Or(cond_rgt, prev_eq_rgt)
          cond = z3.And(cond_lft, cond_rgt)
        elif idx_op == POINT:
          eqs = []
          for i in range(0, len(tup.keys)):
            if isinstance(params[0].params[i], Parameter): 
              param = self.thread_ctx.get_symbs().param_symbol_map[params[0].params[i]]
            elif isinstance(params[0].params[i], QueryField):
              assert(False)
            elif value_is_basic_type(params[0].params[i]):
              param = params[0].params[i]
            else:
              assert(False)
            eqs.append(param == tup.keys[i])
          cond = and_exprs(eqs)
        ret_idx[main_id-1].append(z3.And(cond, tup.condition))
      else:
        ret_idx[main_id-1].append(tup.condition)
    # TODO: currently does not check duplication
    r = []
    for i in range(0, len(ret_idx)):
      r.append(or_exprs(ret_idx[i], default=False))
    # r = [z3.Or(*ret_idx[i]) for i in range(0, len(ret_idx))]
    # return a 01 bitmask
    return r

  def set_keys_and_tables(self):
    if isinstance(self.idx, ObjBasicArray):
      self.tables = [get_main_table(self.idx.table)]
    else:
      pred = self.idx.condition
      self.keys = [k for k in self.idx.keys]
      self.tables = get_denormalized_tables(pred)
      temp_keys = get_denormalized_keys(pred)
      assert(set_equal(self.keys, temp_keys))
      main_t = get_main_table(self.idx.table)
      self.tables.insert(0, main_t)

import time
def is_idx_useful(thread_ctx, idx, table, pred, expected=None):

  start_time = time.time()
  # TODO:
  if isinstance(idx.table, DenormalizedTable):
    return True

  #if not any([k==idx.table for k,v in thread_ctx.symbolic_tables.items()]):
  #  create_symbolic_denormalized_table(thread_ctx, table)
  op, params = get_idxop_and_params_by_pred(pred, idx.key_fields())  
  symbolic_idx = SymbolicIndex(idx, None, thread_ctx)

  query_obj = []
  table = get_main_table(table)
  symbolic_table = thread_ctx.get_symbs().symbolic_tables[table]
  for i,symbolic_tuple in enumerate(symbolic_table.symbols):
    cond_expr = generate_condition_for_pred(thread_ctx, symbolic_tuple, pred)
    query_obj.append(cond_expr)

  table_idx = -1
  idx_obj = [[] for i in range(0, symbolic_table.sz)]
  for i,t in enumerate(symbolic_idx.tables):
    if t == table:
      table_idx = i
  assert(table_idx >= 0)

  idx_obj = symbolic_idx.get_symbolic_tuple_with_cond(op, params)
  assert(len(idx_obj) == symbolic_table.sz)

  eq_cond = []
  for i in range(0, symbolic_table.sz):
    eq_cond.append(query_obj[i] == idx_obj[i])
    #print 'lft = {} |||||| rgt = {}'.format(z3.simplify(query_obj[i]), z3.simplify(idx_obj[i]))
    #check_eq_debug(thread_ctx, 'msg', query_obj[i] == idx_obj[i])
    
  thread_ctx.get_symbs().solver.push()
  thread_ctx.get_symbs().solver.add(z3.Not(and_exprs(eq_cond)))
  r = True
  if expected is not None:
    if expected:
      #print 'idx = {}, pred = {}'.format(idx, pred)
      assert(thread_ctx.get_symbs().solver.check() == z3.unsat)
    else:
      assert(thread_ctx.get_symbs().solver.check() != z3.unsat)
  else:
    r = thread_ctx.get_symbs().solver.check() == z3.unsat
  thread_ctx.get_symbs().solver.pop()

  print 'time = {}'.format(time.time()-start_time)
  return r
