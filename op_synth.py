from schema import *
from util import *
from constants import *
from pred import *
from query import *
from expr import *
from pred_helper import *
from pred_enum import *
from ds_manager import *
from ds_helper import *
from planIR import *
from symbolic_pred import *
from symbolic_ds import *
from symbolic_helper import *
import symbolic_context as symbctx
import itertools
import globalv

def get_ds_and_op_on_cond(thread_ctx, qtable, pred, ds_value, order=None, fk_pred=None, nonexternal={}):
  if pred is None:
    op = OpPredHelper(get_main_table(qtable))
    if order:
      op.add_order(order)
    (ds_t, ds_v) = get_ds_type_value_pair(qtable, op.keys, ds_value)
    return [[(op.to_ds_ops(ds_t, ds_v, qtable), None)]]

  cache = globalv.check_synth_cache(pred, order, fk_pred)
  if cache:
    states = cache
  else:
    states = enumerative_gen(qtable, thread_ctx, pred, order, fk_pred)
    globalv.add_to_synth_cache(pred, order, fk_pred, states)
  all_ops = []
  for state in states:
    for op in state.result:
      op.set_pred()
    if len(nonexternal) > 0:
      for op in state.result:
        op.replace_param_with_qf(nonexternal)
    
    op_and_rest = []
    for op in state.result:
      (ds_t, ds_v) = get_ds_type_value_pair(qtable, op.keys, ds_value)
      op_and_rest.append((op.to_ds_ops(ds_t, ds_v, qtable), op.rest_pred))
    all_ops.append(op_and_rest)

    if not isinstance(qtable, NestedTable):
      op_and_rest = []
      for op in state.result:
        if len(op.condition) > 0 or len(op.keys) > 0:
          (ds_t, ds_v) = get_ds_type_value_pair(qtable, op.keys, ds_value, True)
          op_and_rest.append((op.to_ds_ops(ds_t, ds_v, qtable), op.rest_pred))
          all_ops.append(op_and_rest)
  return all_ops
    
def get_ds_type_value_pair(table, keys, ds_value, ptr=False):
  if isinstance(table, NestedTable) and len(keys) > 0:
    return (get_ds_type_lambda('ObjSortedArray'), ds_value)
  elif isinstance(table, NestedTable):
    return (get_ds_type_lambda('ObjArray'), ds_value)
  elif len(keys) > 0:
    if ptr:
      return (get_ds_type_lambda('ObjTreeIndex'), IndexValue(MAINPTR))
    else:
      return (get_ds_type_lambda('ObjSortedArray'), ds_value)
  else:
    if ptr:
      return (get_ds_type_lambda('ObjArray'), IndexValue(MAINPTR))
    else:
      return (get_ds_type_lambda('ObjArray'), ds_value)

  
class SynthHelper(object):
  def __init__(self, table, thread_ctx, pred_pool, target_pred, rest_preds):
    self.constant_pred = []
    self.pred_pool = {}
    self.cur_ops = []
    self.thread_ctx = thread_ctx
    self.main_table = get_main_table(table)
    self.rest_preds = rest_preds
    self.result = None
    self.tried_ops = [] # a list of hash value array
    self.all_params = []
    self.target_pred = target_pred
    for k,v in pred_pool.items():
      params = []
      for v1 in v:
        if isinstance(v1[1], Parameter):
          params.append(v1)
          self.all_params.append(v1[1])
        else:
          self.constant_pred.append((k,v1))
      if len(params) > 0:
        self.pred_pool[k] = params
    # print 'table = {}'.format(self.main_table)
    # for k,v in pred_pool.items():
    #   print 'pool k = {}, v = {}'.format(k, ','.join([str(v1[1]) for v1 in v]))
    self.max_sz = 1 if len(self.pred_pool) == 0 else reduce(lambda x, y: x*y, [len(v) for k,v in self.pred_pool.items()])
  def str_ops(self, print_restp=False):
    return '\n'.join([o.__str__(print_restp) for o in self.cur_ops])
  def add_result(self):
    ds_str = [str(o) for o in self.cur_ops]
    #print '\n  -- Find result: {}'.format('\n'.join(ds_str))
    self.result = [o.fork() for o in self.cur_ops]
  def rest_preds_state_clear(self):
    # FIXME
    self.rest_pred_combs = [[merge_into_cnf(self.rest_preds) for i in range(0, len(self.cur_ops))]]
    self.restp_cnt = 0
  def assign_rest_preds(self):
    if self.restp_cnt < len(self.rest_pred_combs) :
      self.restp_cnt += 1
      for i,o in enumerate(self.cur_ops):
        o.set_rest_pred(self.rest_pred_combs[self.restp_cnt-1][i])
      return True
    return None
  def check_size(self):
    return len(self.cur_ops) > self.max_sz
  def check_examed(self):
    if any([set_equal(tried, self.cur_ops) for tried in self.tried_ops]):
      #print '  $$ ds examed : {}'.format('\n'.join([str(o.to_pred()) for o in self.cur_ops]))
      return True
  def check_contain_all_params(self):
    for p in self.all_params:
      contained = False
      if any([o.contain_param(p) for o in self.cur_ops]):
        contained = True
      if not contained:
        return False
    return True
  def check_dup(self):
    if len(self.cur_ops) <= 1:
      return False
    for o in self.cur_ops[:-1]:
      if o.__eq__(self.cur_ops[-1]):
        return True
    return False
  def check_equiv(self):
    ds_exprs = [(c.symbolic_result[0], c.rest_pred) for c in self.cur_ops]
    r = check_dsop_pred_equiv(self.thread_ctx, self.main_table, ds_exprs, self.target_pred)
    # print '\n** ds: {}'.format(self.str_ops(True))
    # print '\n op = {}'.format('\n'.join([str(o.dsop) for o in self.cur_ops]))
    # print '\n ** check equiv: {} '.format(r)
    if not r:
      self.tried_ops.append([o.fork() for o in self.cur_ops])
    return r

def param_value_eq(v1, v2):
  if type(v1[0]) != type(v2[0]):
    return False
  if type(v1[0]) is tuple:
    return v1[0][0]==v2[0][0] and v1[0][1]==v2[0][1] and v1[1][0]==v2[1][0] and v1[1][1]==v2[1][1]
  else:
    return v1[0]==v2[0] and v1[1]==v2[1]
  
def keyvalue_to_pred(key, value):
  key = key.key
  if type(value[0]) is tuple:
    return ConnectOp(BinOp(key, value[0][0], value[0][1]), AND,\
        BinOp(key, value[1][0], value[1][1]))
  else:
    return BinOp(key, value[0], value[1])

def key_map_to_pred(keymap):
  others = {}
  preds = []
  for k,v in keymap.items():
    if len(k.path) == 0:
      preds += [keyvalue_to_pred(k, v1) for v1 in v]
    else:
      add_to_list_map(k.path[0], (k,v), others)
  for k,v in others.items():
    newmap = {}
    for k1,v1 in v: # v is a list of (k,v) from keymap
      newk = KeyPath(k1.key, k1.path[1:])
      if newk not in newmap:
        newmap[newk] = v1 #v1 is a list
      else:
        newmap[newk] += v1 
    nextpred = key_map_to_pred(newmap)
    setpred = SetOp(k, EXIST, nextpred)
    preds.append(setpred)
  return merge_into_cnf(preds)  

class OpPredHelper(object):
  def __init__(self, table):
    self.keys = []
    self.params = {} # field: (op,value) / ((op,value),(op,value))
    self.point_keys = []
    self.range_keys = []
    self.condition = [] # [(k, (op,value))]
    self.rest_pred = None
    self.table = table
    self.dsop = None
    self.symbolic_result = None
    self.pred = None
  def create_symbolic_idx(self, thread_ctx):
    ds_type = get_ds_type_lambda('ObjTreeIndex') if len(self.keys) > 0 else get_ds_type_lambda('ObjArray')
    ds_value = IndexValue(MAINPTR)
    self.dsop = self.to_ds_ops(ds_type, ds_value)
    ds = self.dsop.idx
    symbolic_ds = SymbolicIndex(ds, None, thread_ctx)
    self.symbolic_result = symbolic_ds.get_symbolic_tuple_with_cond(self.dsop.op, self.dsop.params)
  def merge_keymap(self):
    m = {k:[v] for k,v in self.params.items()}
    for k,v in self.condition:
      add_to_list_map(k,v,m)
    return m
  def is_valid(self):
    # TODO
    return len(self.range_keys) <= 1 
  def contain_param(self, p):
    for k,v in self.params.items():
      if type(v[0]) is tuple:
        if v[0][1] == p or v[1][1] == p:
          return True
      else:
        if v[1] == p:
          return True
    return False
  def __str__(self, print_rest=False):
    s1 = ', '.join(['{}'.format(k) for k in self.point_keys])
    s2 = ', '.join(['{}'.format(k) for k in self.range_keys])
    cond = self.to_pred()
    return 'ds: {} keys = [{} | {}] // cond = {}{}'.format(hash(self), s1, s2, cond, ', rest={}'.format(self.rest_pred) if print_rest else '')
  def __eq__(self, other):
    # return list_equal(self.keys, other.keys) and \
    #     map_equal(self.params, other.params, value_func=(lambda x,y: param_value_eq(x,y))) \
    #     and list_equal(self.point_keys, other.point_keys) and \
    #     map_equal(self.condition, other.condition, value_func=(lambda x, y: x.query_pred_eq(y)))
    p1 = key_map_to_pred(self.merge_keymap())
    p2 = key_map_to_pred(other.merge_keymap())
    return ( p1 is None and p2 is None ) or (p1 is not None and p2 is not None and p1.query_pred_eq(p2))
  def fork(self):
    newop = OpPredHelper(self.table)
    newop.keys = [k for k in self.keys]
    newop.params = {k:v for k,v in self.params.items()}
    newop.point_keys = [k for k in self.point_keys]
    newop.range_keys = [k for k in self.range_keys]
    newop.condition = [k for k in self.condition]
    newop.rest_pred = self.rest_pred
    #newop.dsop = self.dsop
    #newop.symbolic_result = self.symbolic_result
    return newop
  def add_key_value(self, key, value):
    #print '{}: add {} {}'.format(hash(self), key, value)
    if value is None:
      return True
    if type(value[0]) is tuple:
      is_range = True
    else:
      is_range = value[0] in [LT, GT, LE, GE]
    if is_range:
      self.range_keys.append(key)
    else:
      self.point_keys.append(key)
    self.keys.append(key)
    self.params[key] = value
    return True
  def add_order(self, keys):
    if len(self.range_keys) > 0 and any([KeyPath(k, []) not in self.keys for k in keys]):
      return False
    for k in keys:
      newk = KeyPath(k, [])
      if newk not in self.keys:
        new_value = ((GE, AtomValue(k.field_class.get_min_value())),\
                     (LE, AtomValue(k.field_class.get_max_value())))
        self.add_key_value(newk, new_value)
    return True
  def set_condition(self, cond):
    self.condition = cond
  def set_rest_pred(self, rest_pred):
    self.rest_pred = rest_pred
  def set_pred(self):
    self.pred = self.to_pred()
  def to_pred(self):
    pred = key_map_to_pred(self.merge_keymap())
    #print '  ** curop = {}, pred = {}'.format(self, pred)
    return pred
  def replace_param_with_qf(self, nonexternal):
    for k,v in self.params.items():
      if any([k==qf for qf,v1 in nonexternal.items()]):
        to_be_replaced = nonexternal[k][1]
        qf = nonexternal[k][0]
        if type(self.params[k][0]) is tuple:
          if self.params[k][0][1] == to_be_replaced:
            self.params[k] = ((self.params[k][0][0], qf), self.params[k][1])
          if self.params[k][1][1] == to_be_replaced:
            self.params[k] = (self.params[k][1], (self.params[k][1][0], qf))
        else:
          if self.params[k][1] == to_be_replaced:
            self.params[k] = (self.params[k][0], qf)
  def to_ds_ops(self, ds_type, ds_value, qtable=None):
    ds_pred = self.to_pred()
    if self.pred is None:
      self.pred = ds_pred
    table = self.table if qtable is None else qtable
    if ds_pred is None:
      ds = ObjBasicArray(table, ds_value)
      return ExecScanStep(ds)
    op = IndexOp(POINT) if len(self.range_keys) == 0 else IndexOp(RANGE)
    keys = [k for k in self.point_keys] + [k for k in self.range_keys]
    pathkeys = self.point_keys+self.range_keys
    if op.is_point():
      param = IndexParam()
      for k in keys:
        param.add_param(k, self.params[k][1])
      params = [param]
    else:
      params = [IndexParam(), IndexParam()]
      for i,k in enumerate(keys):
        value = self.params[pathkeys[i]]
        if type(value[0]) is tuple:
          if value[0][0] in [GT, LT]:
            op.left = OPEN
          if value[1][0] in [GT, LT]:
            op.right= OPEN
          params[0].add_param(k, value[0][1])
          params[1].add_param(k, value[1][1])
        else:
          if value[0] in [GT, GE]:
            params[0].add_param(k, value[1])
            params[1].add_param(k, AtomValue(k.get_query_field().field_class.get_max_value()))
            if value[0] == GT:
              op.left = OPEN
          elif value[0] in [LT, LE]:
            params[0].add_param(k, AtomValue(k.get_query_field().field_class.get_min_value()))
            params[1].add_param(k, value[1])
            if value[0] == LT:
              op.right = OPEN
          elif value[0] == EQ:
            params[0].add_param(k, value[1])
            params[1].add_param(k, value[1])
          else:
            assert(False)
          
    if len(keys) > 0:
      #print 'keys = {}, ds_pred = {}'.format(','.join([str(k) for k in keys]), ds_pred)
      ds = ds_type(table, IndexKeys(keys, self.range_keys), self.pred, ds_value) # ObjSortedArray
    else:
      ds = ds_type(table, self.pred, ds_value) # ObjArray
    return ExecIndexStep(ds, ds_pred, op, params)

def enumerate_all_ops(state, order=None):
  ops = []
  all_keys = []
  all_values = []
  for k,v in state.pred_pool.items():
    lt = []
    gt = []
    for v1 in v:
      if v1[0] in [LT, LE]:
        lt.append(v1)
      elif v1[0] in [GT, GE]:
        gt.append(v1)
      else:
        assert(v1[0] in [EQ, SUBSTR])
    values = [v1 for v1 in v]
    if len(lt)>0 and len(gt)>0:
      for x in itertools.product(lt, gt):
        values.append((x[0],x[1]))
    values.append(None)
    all_keys.append(k)
    all_values.append(values)
  for xx in itertools.product(*all_values):
    for i in reversed(range(0, len(state.constant_pred)+1)):
      for consts in itertools.combinations(state.constant_pred, i):
        op = OpPredHelper(state.main_table)
        for j,value in enumerate(xx):
          op.add_key_value(all_keys[j], value)
          op.set_condition(list(consts))
        if order:
          if op.add_order(order) == False:
            continue
        if (not any([op1==op for op1 in ops])):
          op.create_symbolic_idx(state.thread_ctx)
          ops.append(op)
  # print 'ALL ops:'
  # for op in ops:
  #   print op 
  return ops

def enumerative_gen(queried_table, thread_ctx, pred, order, fk_pred):
  states = []
  new_pred = dispatch_not(pred)
  Nors = count_ors(new_pred)
  elements = []
  break_pred_into_compares(new_pred, elements)
  fk_elements = [fk_pred] if fk_pred else []
  if fk_pred:
    target_pred = ConnectOp(pred, AND, fk_pred)
  else:
    target_pred = pred
  for length in range(0, len(elements) + 1):
    for x in itertools.combinations(elements, length):
      field_cmp_map = {}
      for literal in list(x)+fk_elements:
        get_compare_map_by_field(literal, field_cmp_map)
      #print '\nidx pred = {}'.format('; '.join([str(x1) for x1 in list(x)+fk_elements]))
      rest_pred_pool = set_minus(elements, list(x), eq_func=(lambda x,y: x.query_pred_eq(y)))
      if Nors == 0:
        rest_preds = [merge_into_cnf(rest_pred_pool)]
      else:
        rest_preds = enumerate_rest_pred(rest_pred_pool)
      #print 'rest_pred = {}'.format('&&'.join([str(rp) for rp in rest_preds]))
      state = SynthHelper(queried_table, thread_ctx, field_cmp_map, target_pred, rest_preds)
      if len(state.pred_pool) == 0: # no key
        state.cur_ops = [OpPredHelper(state.main_table)]
        state.cur_ops[-1].condition = state.constant_pred
        state.cur_ops[-1].rest_pred = merge_into_cnf(rest_preds)
        if order:
          state.cur_ops[-1].add_order(order)
        state.add_result()
        states.append(state)
        continue
      ops = enumerate_all_ops(state, order)
      #print '  max sz = {}'.format(state.max_sz)
      for i in range(1, state.max_sz+1):
        #print 'search size {}'.format(i)
        enumerative_gen_by_depth(ops, state, i)
        if state.result is not None:
          break
      if state.result:
        states.append(state)
  return states

def enumerative_gen_by_depth(ops, state, depth, i=0):
  if state.result is not None:
    return
  if len(state.cur_ops) >= depth:
    # evaluate
    #print 'evaluate: {}'.format(state.str_ops())
    if state.check_contain_all_params() == False:
      return 
    if (not state.check_examed()):
      state.rest_preds_state_clear()
      while state.assign_rest_preds():
        if state.check_equiv():
          state.add_result()
        if state.result is not None:
          break
    return
  for op in ops[i:]:
    if state.result is not None:
      break
    state.cur_ops.append(op)
    # if state.check_dup():
    #   state.cur_ops.pop(-1)
    #   continue
    enumerative_gen_by_depth(ops, state, depth, i+1)
    state.cur_ops.pop(-1)

def test_synth(table, pred, order=None):
  pred.complete_field(table)
  thread_ctx = symbctx.create_thread_ctx()
  create_symbolic_obj_graph(thread_ctx, globalv.tables, globalv.associations)
  query = get_all_records(table)
  query.pfilter(pred)
  create_param_map_for_query(thread_ctx, query)
  get_ds_and_op_on_cond(thread_ctx, table, pred, IndexValue(MAINPTR), order)


# # pred_pool: key -> field; value -> [(op, rh),]
# # cur_ops: [OpPredHelper]
# def enumerative_gen(state):
#   if state.result is not None:
#     return
#   if state.check_size() or state.check_examed():
#     return
    
#   print '\none enumerate'
#   print '\n'.join(['    {}'.format(ds) for ds in state.cur_ops])

#   if state.check_equiv(): # check equivalence
#     state.add_result()
#     return

#   last_op = state.cur_ops[-1]
#   nextkv = last_op.next_key_values(state.pred_pool)
#   if nextkv is None:
#     state.cur_ops.append(OpPredHelper())
#     last_op = state.cur_ops[-1]
#     nextkv = state.cur_ops[-1].next_key_values(state.pred_pool)
#     assert(nextkv)
#   next_key, next_values = nextkv
#   next_values.append(None)
#   for nv in next_values:
#     last_op.add_key_value(next_key, nv)
#     for i in reversed(range(0, len(state.constant_pred)+1)):
#       for consts in itertools.combinations(state.constant_pred, i):
#         if state.result:
#           return
#         last_op.set_condition(list(consts))
#         # first simple validation
#         if state.check_dup():
#           continue
#         enumerative_gen(state)
#     last_op.remove_key(next_key)
