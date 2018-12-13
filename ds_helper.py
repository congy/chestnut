from pred import *
from ds import *

def contain_range_count(pred):
  if isinstance(pred, ConnectOp):
    return contain_range_count(pred.lh) + contain_range_count(pred.rh)
  elif isinstance(pred, BinOp):
    if pred.op in [LT, LE, GT, GE, BETWEEN] and pred.has_param():
      return 1
    elif pred.op == IN and any([isinstance(p, Parameter) for p in pred.rh.params]):
      return 2
    elif pred.op == SUBSTR: # and isinstance(pred.rh, Parameter):
      return 2
    else:
      return 0
  elif isinstance(pred, SetOp):
    return contain_range_count(pred.rh)
  else:
    return 0
  

def contain_negation(pred):
  if isinstance(pred, ConnectOp):
    return contain_negation(pred.lh) or contain_negation(pred.rh)
  elif isinstance(pred, UnaryOp):
    return len(pred.get_all_params())>0 
  elif isinstance(pred, BinOp) and pred.op == NEQ:
    return len(pred.get_all_params())>0
  else:
    return False

def contain_str_match(pred):
  if isinstance(pred, ConnectOp):
    return contain_str_match(pred.lh) or contain_str_match(pred.rh)
  elif isinstance(pred, UnaryOp):
    return contain_str_match(pred.operand)
  elif isinstance(pred, BinOp):
    if is_long_string(get_query_field(pred.lh).field_class):
      return True
  return False

# FIXME: Valid index pred?
def is_valid_idx_cond(pred, hash_idx=False):
  if contain_negation(pred):
    return False
  range_cnt = contain_range_count(pred)
  if hash_idx and range_cnt > 0:
    return False
  elif range_cnt > 1:
    return False
  elif contain_str_match(pred):
    return False
  else:
    return True

def is_mainptr_idx(idx):
  return (not isinstance(idx, ObjBasicArray)) and idx.value.is_main_ptr()

def is_basic_array(idx):
  return isinstance(idx, ObjBasicArray) and idx.value.is_object()

def is_id_idx(idx):
  qf = QueryField('id', table=get_main_table(idx.table))
  pred = BinOp(qf, EQ, Parameter('id'))
  #if not (type(idx.value) is int):
  #  return False
  if isinstance(idx, ObjBasicArray):
    return False
  if (not isinstance(idx.table, NestedTable)) and pred.idx_pred_eq(idx.condition):
    return True
  return False

#include basic arrays and id index on obj collection
def is_basic_idx(idx):
  if is_basic_array(idx) or is_id_idx(idx):
    return True
  return False

def is_aggr_idx(idx):
  return isinstance(idx.value, AggrResult)
 
def require_basic_ary(idx, relates):
  if isinstance(idx, ObjBasicArray):
    return False
  if idx.value.is_nested_ptr() and relates == False:
    return True
  if idx.value.is_main_ptr() and (not isinstance(idx.table, NestedTable)) and relates == False:
    return True
  return False

def get_loop_define(idx, is_begin=True, is_range=False):
  range_for = 'RANGE_' if is_range else 'INDEX_'
  suffix = 'BEGIN' if is_begin else 'END\n'
  if isinstance(idx, ObjBasicArray):
    if isinstance(idx.table, NestedTable) and get_main_table(idx.table.upper_table).has_one_or_many_field(idx.table.name) == 1:
      return 'SINGLE_ELEMENT_FOR_{}'.format(suffix) 
    sz = to_real_value(idx.compute_size())
    if sz < SMALL_DT_BOUND:
      return 'SMALLBASICARRAY_FOR_{}'.format(suffix)
    else:
      return 'BASICARRAY_FOR_{}'.format(suffix)
  elif isinstance(idx, IndexBase):
    if to_real_value(idx.compute_size()) < SMALL_DT_BOUND:
      prefix = 'SMALL'
    else:
      prefix = ''
    if isinstance(idx, ObjTreeIndex):
      typ = 'TREEINDEX'
    elif isinstance(idx, ObjSortedArray):
      typ = 'SORTEDARRAY'
    elif isinstance(idx, ObjHashIndex):
      typ = 'HASHINDEX'
    elif isinstance(idx, ObjArray):
      typ = 'BASICARRAY'
      range_for = ''
    return '{}{}_{}FOR_{}'.format(prefix, typ, range_for, suffix)
  else:
    print idx
    assert(False)

def get_idx_define(idx):
  if isinstance(idx, ObjBasicArray):
    if idx.single_element:
      qf = get_qf_from_nested_t(idx.table)
      return '{}In{}'.format(get_capitalized_name(qf.field_name), get_capitalized_name(qf.table.name))
    sz = to_real_value(idx.compute_size())
    if sz < SMALL_DT_BOUND: 
      return 'SmallBasicArray'
    else:
      return 'BasicArray'
  elif isinstance(idx, IndexBase):
    prefix = ''
    if to_real_value(idx.compute_size()) < SMALL_DT_BOUND:
      prefix='Small'
    if isinstance(idx, ObjTreeIndex):
      return '{}TreeIndex'.format(prefix)
    elif isinstance(idx, ObjSortedArray):
      return '{}SortedArray'.format(prefix)
    elif isinstance(idx, ObjHashIndex):
      return '{}HashIndex'.format(prefix)
    elif isinstance(idx, ObjArray):
      return '{}BasicArray'.format(prefix)
  assert(False)

def index_conflict(idx1, idx2):
  if not type(idx1) == type(idx2):
    return False
  if not idx1.table == idx2.table:
    return False
  if not isinstance(idx1.table, NestedTable):
    return False
  if isinstance(idx1, ObjBasicArray) and isinstance(idx2, ObjBasicArray):
    if (not idx1.value == idx2.value):
      return True
    else:
      return False
  if idx1.condition.idx_pred_eq(idx2.condition) and not (idx1.value == idx2.value):
    return True
  return False


def get_idxop_and_params_by_pred(pred, keys, nonexternal={}):
  if isinstance(keys, IndexKeys):
    keys = keys.keys
  qs = [pred]
  params = {}
  op = POINT
  while len(qs) > 0:
    q = qs.pop()
    if isinstance(q, ConnectOp):
      qs.append(q.lh)
      qs.append(q.rh)
    elif isinstance(q, SetOp):
      qs.append(q.rh)
    elif isinstance(q, UnaryOp):
      qs.append(q.operand)
    elif isinstance(q.rh, Parameter):
      if q.op in [LT, LE]:
        params[q.lh] = ([q.lh.field_class.get_min_value(), q.rh])
        op = RANGE
      elif q.op in [GT, GE]:
        params[q.lh] = ([q.rh, q.lh.field_class.get_max_value()])
        op = RANGE
      elif q.op == EQ:
        if any([q.lh==qf for qf,v in nonexternal.items()]):
          params[q.lh] = ([nonexternal[q.lh]])
        else:
          params[q.lh] = ([q.rh])
      elif q.op == BETWEEN:
        params[q.lh] = ([q.rh.params[0], q.rh.params[1]])
        op = RANGE
      elif q.op == IN:
        params[q.lh] = ([q.rh.params[0]])
        # FIXME: Convert into union!!
      else:
        assert(False)
  if op == RANGE:
    r_params = [IndexParam(), IndexParam()]
  else:
    if len(params) > 0:
      r_params = [IndexParam()]
    else:
      r_params = []
  for k in keys:
    v = params[k]
    if len(v) == 1:
      r_params[0].add_param(k, v[0])
      if op == RANGE:
        r_params[1].add_param(k, v[0])
    else:
      r_params[0].add_param(k, v[0])
      r_params[1].add_param(k, v[1])
  
  return op, r_params

def get_order_param(order):
  r_param_1 = IndexParam()
  r_param_2 = IndexParam()
  for o in order:
    r_param_1.add_param(o, o.field_class.get_min_value())
    r_param_2.add_param(o, o.field_class.get_max_value())
  return [r_param_1, r_param_2]

#return new_idx, op, param
def merge_order_pred(idx, order):
  keys = [k for k in idx.keys]
  cond = idx.condition
  r_param_1 = IndexParam()
  r_param_2 = IndexParam()
  for o in order:
    if not any([o==k for k in keys]):
      keys.append(o)
      cond = ConnectOp(BinOp(o, EQ, Parameter('order_{}'.format(o.field_name))), AND, cond)
      r_param_1.add_param(o, o.field_class.get_min_value())
      r_param_2.add_param(o, o.field_class.get_max_value())

  # FIXME: only tree index
  new_idx = ObjTreeIndex(idx.table, keys, cond, idx.value)
  return new_idx, RANGE, [r_param_1, r_param_2]

def replace_subpred_with_var(pred, placeholder):
  if isinstance(pred, ConnectOp):
    return ConnectOp(replace_subpred_with_var(pred.lh, placeholder), pred.op, replace_subpred_with_var(pred.rh, placeholder))
  elif isinstance(pred, SetOp):
    assert(pred in placeholder)
    return placeholder[pred]
  elif isinstance(pred, UnaryOp):
    return UnaryOp(replace_subpred_with_var(pred.operand, placeholder))
  elif isinstance(pred, AssocOp):
    assert(pred in placeholder)
    return placeholder[pred]
  elif isinstance(pred, BinOp):
    return BinOp(replace_subpred_with_var(pred.lh, placeholder), pred.op, replace_subpred_with_var(pred.rh, placeholder))
  else:
    return pred

def find_objstruct_by_idx(pool, idx):
  for k,v in pool.pools.items():
    r = find_objstruct_by_idx_helper(v, idx)
    if r is not None:
      return r
  return None

def find_objstruct_by_idx_helper(objstruct, idx):
  for _idx in objstruct.idxes:
    if idx == _idx:
      return objstruct
  for k,v in objstruct.next_level.items():
    r = find_objstruct_by_idx_helper(v, idx)
    if r is not None:
      return r
  return None

def is_primary_index(idx):
  # id index or top level basic array
  if isinstance(idx.table, NestedTable):
    return False
  return is_id_idx(idx) or is_basic_array(idx)

def order_maintained(scan_order, target_order):
  if target_order is None:
    return True
  if scan_order is None:
    return False
  # FIXME
  return all([any([o1==o2 for o2 in scan_order]) for o1 in target_order])
