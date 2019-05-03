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
    #self.condition = condition
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
    # if isinstance(main_t, DenormalizedTable):
    #   assert(self.upper_cond_lambda is None)
    #   self.tables = main_t
    #   for i,symbolic_tuple in enumerate(self.thread_ctx.get_symbs().symbolic_tables[main_t].symbols):
    #     self.tuples.append(SymbolicIndexEntry(get_ids_from_denormalized_symb(main_t, symbolic_tuple), \
    #           self.thread_ctx.get_symbs().symbolic_tables[main_t].exists[i], [], [])) 
    # else:
    if True:
      self.tables = [main_t]
      for i,symbolic_tuple in enumerate(self.thread_ctx.get_symbs().symbolic_tables[main_t].symbols):
        if self.upper_cond_lambda:
          cond = self.upper_cond_lambda(i+1)
        else:
          cond = True
        self.tuples.append(SymbolicIndexEntry([i+1], cond, [], [])) 

  def build_from_idx(self):
    pred = self.idx.condition
    main_t = get_main_table(self.idx.table)
    main_id_key = KeyPath(QueryField('id', main_t),[])
    self.keys = [k for k in self.idx.key_fields()]
    table_by_path = [main_id_key] + remove_duplicate(get_denormalized_tables(pred))
    self.tables = [t.get_query_field().table for t in table_by_path]
    all_table_ids = [range(1, self.thread_ctx.get_symbs().symbolic_tables[t].sz+1) for t in self.tables[1:]]
    for i,symbolic_tuple in enumerate(self.thread_ctx.get_symbs().symbolic_tables[main_t].symbols):
      for table_ids in itertools.product(*all_table_ids):
        table_id_map = {table_by_path[i]:table_ids[i-1] for i in range(1, len(table_by_path))}
        table_id_map[main_id_key] = i+1
        key_map = {k:None for k in self.keys}
        cond = get_denormalizing_cond_helper(self.thread_ctx, symbolic_tuple, [], pred, table_id_map, key_map)
        # if i == 0:
        #   print '  ^ pred = {}, ds cond = {}, keys = {}'.format(pred, cond, ','.join([str(v) for k,v in key_map.items()]))
        assert(all([v is not None for k,v in key_map.items()]))
        if self.upper_cond_lambda:
          cond = self.upper_cond_lambda(i+1, cond)
        symbol_tuple = SymbolicIndexEntry([i+1]+list(table_ids), cond, \
              [key_map[k] for k in self.keys], \
              [k.get_query_field() for k in self.keys])
        self.tuples.append(symbol_tuple)

  def get_symbolic_tuple_with_cond(self, idx_op, params):
    main_symbol_t = self.thread_ctx.get_symbs().symbolic_tables[self.tables[0]]
    ret_idx = [[] for i in range(0, main_symbol_t.sz)]
    for ki, tup in enumerate(self.tuples):
      main_id = tup.ids[0]
      if len(params) > 0:
        if idx_op.is_range():
          prev_eq_lft = True
          prev_eq_rgt = True
          cond_lft = False
          cond_rgt = False
          param_valid = True
          for i in range(0, len(tup.keys)):
            if isinstance(params[0].params[i], Parameter): 
              param0 = self.thread_ctx.get_symbs().param_symbol_map[params[0].params[i]]
            elif isinstance(params[0].params[i], QueryField):
              assert(False)
            elif isinstance(params[0].params[i], AtomValue): #and value_is_basic_type(params[0].params[i]):
              param0 = params[0].params[i].to_z3_value()
            else:
              assert(False)
            if isinstance(params[1].params[i], Parameter): 
              param1 = self.thread_ctx.get_symbs().param_symbol_map[params[1].params[i]]
            elif isinstance(params[1].params[i], QueryField):
              assert(False)
            elif isinstance(params[1].params[i], AtomValue): #value_is_basic_type(params[1].params[i]):
              param1 = params[1].params[i].to_z3_value()
            else:
              assert(False)
            # special case for bool:
            if is_bool(self.keys[i].get_query_field().field_class):
              tup_v = z3.If(tup.keys[i], 1, 0)
            else:
              tup_v = tup.keys[i]
            cond_lft = z3.Or(cond_lft, z3.And(prev_eq_lft, (tup_v > param0)))
            cond_rgt = z3.Or(cond_rgt, z3.And(prev_eq_rgt, (tup_v < param1)))
            prev_eq_lft = z3.And(prev_eq_lft, tup_v == param0)
            prev_eq_rgt = z3.And(prev_eq_rgt, tup_v == param1)
            param_valid = z3.And(param_valid, param0<=param1 if (idx_op.left==CLOSE and idx_op.right==CLOSE) else param0<param1)
            #print 'cond k {} iter {} cond = {} || {}'.format(ki, i, z3.simplify(cond_lft), z3.simplify(cond_rgt))
          cond = z3.And(cond_lft, cond_rgt)
          if idx_op.left==CLOSE:
            cond = z3.Or(cond, z3.And(param_valid, prev_eq_lft))
          if idx_op.right==CLOSE:
            cond = z3.Or(cond, z3.And(param_valid, prev_eq_rgt))
        else:
          eqs = []
          for i in range(0, len(tup.keys)):
            if isinstance(params[0].params[i], Parameter): 
              param = self.thread_ctx.get_symbs().param_symbol_map[params[0].params[i]]
            elif isinstance(params[0].params[i], QueryField):
              assert(False)
            elif isinstance(params[0].params[i], AtomValue): #value_is_basic_type(params[0].params[i]):
              param = params[0].params[i].v
            else:
              assert(False)
            eqs.append(param == tup.keys[i])
          cond = and_exprs(eqs)
        #debug_add_expr('cond={}, keys: {}'.format(self.idx.condition, ' - '.join(['{}({})'.format(self.tables[ik], tup.ids[ik]) for ik in range(0, len(tup.ids))])), cond)
        ret_idx[main_id-1].append(z3.And(cond, tup.condition))
      else:
        ret_idx[main_id-1].append(tup.condition)
    # TODO: currently does not check duplication
    r = []
    for i in range(0, len(ret_idx)):
      expr = or_exprs(ret_idx[i], default=False)
      r.append(expr)
    #debug_add_expr('{} -- TUPLE 0: '.format(self.idx), r[0])
    # r = [z3.Or(*ret_idx[i]) for i in range(0, len(ret_idx))]
    # return a 01 bitmask
    return r

import time

def is_idx_useful(thread_ctx, idx, table, pred, expected=None):

  start_time = time.time()
  
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

  #print 'time = {}'.format(time.time()-start_time)
  return r
