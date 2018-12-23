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
import symbolic_context as symbctx
import itertools
import globalv

def get_ds_and_op_on_cond(thread_ctx, queried_table, idx_pred, rest_pred, ds_value, nonexternal={}):
  # get all fields and their compared value
  field_cmp_map = {}
  get_compare_map_by_field(idx_pred, field_cmp_map)
  state = SynthHelper(queried_table, thread_ctx, field_cmp_map, idx_pred, rest_pred)
  enumerative_gen(state)
  idx_ops = []
  if state.result is None:
    return []
  temp_op_combs = []
  for op in state.result:
    op.replace_param_with_qf(nonexternal)
    ds_type = lambda *arg: ObjSortedArray(args) if len(op.keys) > 0 else lambda *arg: ObjArray(args)
    idxop = op.to_ds_ops(queried_table, ds_type, ds_value)
    idx_ops.append(idxop)
  r = [idx_ops]
  if not isinstance(queried_table, NestedTable):
    idx_ops = []
    for op in state.result:
      ds_type = lambda *arg: ObjTreeIndex(args) if len(op.keys) > 0 else lambda *arg: ObjArray(args)
      idxop = op.to_ds_ops(queried_table, ds_type, IndexValue(MAINPTR))
      idx_ops.append(idxop)
    r.append(idx_ops)
  return r
  
class KeyPath(object):
  def __init__(self, key, path):
    self.path = path
    self.key = key
    self.hashstr = '-'.join([str(x) for x in self.path])+'-'+str(self.key)
  def __eq__(self, other):
    return len(self.path) == len(other.path) and all([self.path[i]==other.path[i] for i in range(0, len(self.path))]) and self.key == other.key
  def __str__(self):
    return self.hashstr
  def __hash__(self):
    return hash(self.hashstr)
  def is_hasone_assoc(self):
    return len(self.path) == 0
  
def get_compare_map_by_field(pred, mp, upper_path=[], reverse=False):
  if isinstance(pred, UnaryOp):
    get_compare_map_by_field(pred.operand, mp, upper_path, (not reverse))
  elif isinstance(pred, SetOp):
    next_upper = upper_path + [pred.lh]
    get_compare_map_by_field(pred.rh, mp, next_upper, reverse)
  elif isinstance(pred, ConnectOp):
    get_compare_map_by_field(pred.lh, mp, upper_path, reverse)
    get_compare_map_by_field(pred.rh, mp, upper_path, reverse)
  elif isinstance(pred, BinOp):
    if is_query_field(pred.lh):
      key = KeyPath(pred.lh, upper_path)
      if is_query_field(pred.rh):
        if reverse:
          pass
        else:
          add_to_list_map(key, (pred.op, pred.rh), mp)
      elif isinstance(pred.rh, MultiParam):
        if pred.op == BETWEEN:
          if reverse:
            add_to_list_map(key, (LE, pred.rh.params[0]), mp)
            add_to_list_map(key, (GE, pred.rh.params[1]), mp)
          else:
            add_to_list_map(key, (GT, pred.rh.params[0]), mp)
            add_to_list_map(key, (LT, pred.rh.params[1]), mp)
        elif pred.op == IN:
          if reverse:
            # TODO
            for param in pred.rh.params:
              add_to_list_map(key, (LT, param), mp)
              add_to_list_map(key, (GT, param), mp)
          else:
            for param in pred.rh.params:
              add_to_list_map(key, (EQ, param), mp)
      elif isinstance(pred.rh, Parameter):
        if pred.op == NEQ or (pred.op==EQ and reverse):
          add_to_list_map(key, (GT, pred.rh), mp)
          add_to_list_map(key, (LT, pred.rh), mp)
        else:
          if reverse:
            pass
          else:
            add_to_list_map(key, (pred.op, pred.rh), mp)
      elif isinstance(pred.rh, AtomValue):
        if reverse:
          pass
        else:
          add_to_list_map(key, (pred.op, pred.rh), mp)

class SynthHelper(object):
  def __init__(self, table, thread_ctx, pred_pool, idx_pred, rest_pred):
    self.constant_pred = []
    self.idx_pred = idx_pred
    if rest_pred:
      self.target_pred = ConnectOp(idx_pred, AND, rest_pred)
    else:
      self.target_pred = idx_pred
    self.pred_pool = {}
    self.cur_ops = []
    self.thread_ctx = thread_ctx
    self.rest_pred = rest_pred
    self.main_table = table
    self.result = None
    self.tried_ops = [] # a list of hash value array
    self.all_params = []
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
    for k,v in pred_pool.items():
      print 'pool k = {}, v = {}'.format(k, ','.join([str(v1[1]) for v1 in v]))
    if len(self.pred_pool) == 0: # no key
      self.cur_ops = [OpPredHelper()]
      self.cur_ops[-1].condition = self.constant_pred
      self.add_result()
    self.max_sz = 1 if len(self.pred_pool) == 0 else reduce(lambda x, y: x*y, [len(v) for k,v in self.pred_pool.items()])
  def str_ops(self):
    return '\n'.join([str(o) for o in self.cur_ops])
  def add_result(self):
    ds_str = [str(o) for o in self.cur_ops]
    print '\n  -- Find result: {}'.format('\n'.join(ds_str))
    self.result = [o.fork() for o in self.cur_ops]

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
    p = []
    for c in self.cur_ops:
      p1 = c.to_pred()
      #print ' -- dsop = {}'.format(c)
      if p1:
        p.append(p1)
    if self.rest_pred:
      p = [ConnectOp(p1, AND, self.rest_pred) for p1 in p]
    if len(p) == 0:
      return False
    cur_pred = p[0]
    for p1 in p[1:]:
      cur_pred = ConnectOp(cur_pred, OR, p1)
    r = check_pred_equiv(self.thread_ctx, self.main_table, cur_pred, self.target_pred)
    if r:
      print '\n ** check equiv: {} {} '.format(cur_pred, r)
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
  def __init__(self):
    self.keys = []
    self.params = {} # field: (op,value) / ((op,value),(op,value))
    self.point_keys = []
    self.range_keys = []
    self.condition = [] # [(k, (op,value))]
    self.is_subset = False
    self.is_superset = False
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
  def __str__(self):
    s1 = ', '.join(['{}'.format(k) for k in self.point_keys])
    s2 = ', '.join(['{}'.format(k) for k in self.range_keys])
    cond = self.to_pred()
    return 'ds: {} keys = [{} | {}] // cond = {}'.format(hash(self), s1, s2, cond)
  def __eq__(self, other):
    # return list_equal(self.keys, other.keys) and \
    #     map_equal(self.params, other.params, value_func=(lambda x,y: param_value_eq(x,y))) \
    #     and list_equal(self.point_keys, other.point_keys) and \
    #     map_equal(self.condition, other.condition, value_func=(lambda x, y: x.query_pred_eq(y)))
    p1 = key_map_to_pred(self.merge_keymap())
    p2 = key_map_to_pred(other.merge_keymap())
    return ( p1 is None and p2 is None ) or (p1 is not None and p2 is not None and p1.query_pred_eq(p2))
  def fork(self):
    newop = OpPredHelper()
    newop.keys = [k for k in self.keys]
    newop.params = {k:v for k,v in self.params.items()}
    newop.point_keys = [k for k in self.point_keys]
    newop.range_keys = [k for k in self.range_keys]
    newop.condition = [k for k in self.condition]
    return newop
  def next_key_values(self, pred_pool):
    for k,v in pred_pool.items():
      if k not in self.keys and k not in self.range_keys:
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
        return k, values
    return None
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
  def set_condition(self, cond):
    self.condition = cond
  def remove_key(self, k):
    if k not in self.keys:
      return
    #print '{}: keys = {}, k = {}'.format(hash(self), ','.join([str(k1) for k1 in self.keys]), k)
    self.keys.remove(k)
    del self.params[k]
    if k in self.point_keys:
      self.point_keys.remove(k)
    if k in self.range_keys:
      self.range_keys.remove(k)
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
  def to_pred(self):
    pred = key_map_to_pred(self.merge_keymap())
    #print '  ** curop = {}, pred = {}'.format(self, pred)
    return pred
  def to_ds_ops(self, ds_table, ds_type, ds_value):
    ds_pred = self.to_pred()
    if ds_pred is None:
      ds =  ObjBasicArray(ds_table, ds_value)
      return ExecScanStep(ds)
    table = ds_table
    op = POINT if len(self.range_keys) == 0 else RANGE
    keys = [k for k in self.point_keys] + [k for k in self.range_keys]
    if op == POINT:
      param = IndexParam()
      for k in keys:
        param.add_param(k, self.params[k][1])
      params = [param]
    else:
      params = [IndexParam(), IndexParam()]
      for k in keys:
        value = self.params[k]
        if type(value[0]) is tuple:
          params[0].add_param(k, value[0][1])
          params[1].add_param(k, value[1][1])
        else:
          params[0].add_param(k, value[1])
          params[1].add_param(k, value[1])
  if len(keys) > 0:
    ds = ds_type(table, keys, ds_pred, ds_value) # ObjSortedArray
  else:
    ds = ds_type(table, ds_pred, ds_value) # ObjArray
  return ExecIndexStep(ds, ds_pred, op, params)


def enumerate_all_ops(state):
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
        op = OpPredHelper()
        for j,value in enumerate(xx):
          op.add_key_value(all_keys[j], value)
          op.set_condition(list(consts))
        if op.is_valid() and (not any([op1==op for op1 in ops])):
          op.is_subset = check_pred_subset(state.thread_ctx, state.main_table, op.to_pred(), state.idx_pred) # pred1 -> pred2
          op.is_superset = check_pred_subset(state.thread_ctx, state.main_table, state.idx_pred, op.to_pred())
          ops.append(op)
          if op.is_subset and op.is_superset:
            state.cur_ops = [op]
            state.add_result()
  print 'ALL ops:'
  for op in ops:
    print op 
    print '  subset = {}, superset = {}'.format(op.is_subset, op.is_superset)
  return ops

def enumerative_gen(state):
  ops = enumerate_all_ops(state)
  print 'max sz = {}'.format(state.max_sz)
  for i in range(1, state.max_sz+1):
    #print 'search size {}'.format(i)
    enumerative_gen_helper(ops, state, i)
    if state.result is not None:
      break

def enumerative_gen_helper(ops, state, depth):
  if state.result is not None:
    return
  if len(state.cur_ops) >= depth:
    # evaluate
    #print 'evaluate: {}'.format(state.str_ops())
    if (not state.check_examed()) and state.check_equiv():
      state.add_result()
    return
  for op in ops:
    if state.result is not None:
      break
    if op.is_subset == False:
      continue
    state.cur_ops.append(op)
    if state.check_dup():
      state.cur_ops.pop(-1)
      continue
    enumerative_gen_helper(ops, state, depth)
    state.cur_ops.pop(-1)

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

def test_synth(table, pred):
  pred.complete_field(table)
  thread_ctx = symbctx.create_thread_ctx()
  create_symbolic_obj_graph(thread_ctx, globalv.tables, globalv.associations)
  query = get_all_records(table)
  query.pfilter(pred)
  create_param_map_for_query(thread_ctx, query)
  for union_set in enumerate_pred_combinations(pred):
    for j,cnf in enumerate(union_set):
      clauses = cnf.split()
      for length in range(1, len(clauses)+1):
        for idx_combination in itertools.combinations(clauses, length):
          rest_preds = set_minus(clauses, idx_combination, eq_func=(lambda x,y: x.query_pred_eq(y)))
          idx_pred = merge_into_cnf(idx_combination)
          rest_pred = merge_into_cnf(rest_preds)
          print '\n\nidx pred = {}'.format(idx_pred)
          print 'rest pred = {}'.format(rest_pred)
          get_ds_and_op_on_cond(thread_ctx, table, idx_pred, rest_pred, IndexValue(MAINPTR))