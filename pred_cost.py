import math
from pred import *
from util import *
from constants import *
from cost import *
import globalv

class IdxBaseUnit(Cost):
  def __init__(self, idx, single=False):
    self.idx = idx
    if isinstance(idx.table, NestedTable):
      assert(idx.upper)
      if single:
        self.base_sz = idx.table.sz
      else:
        self.base_sz = cost_mul(idx.upper.element_count(), idx.table.sz)
    else:
      self.base_sz = idx.table.sz 
    self.tup_cnt = self.base_sz
  def str_symbol(self):
    return to_symbol(self.tup_cnt)
  def to_real_value(self):
    return to_real_value(self.tup_cnt)

class IdxSizeUnit(IdxBaseUnit):
  def __init__(self, idx, single=False):
    self.idx = idx
    if isinstance(idx.table, NestedTable):
      assert(idx.upper)
      if single:
        self.base_sz = idx.table.sz
      else:
        self.base_sz = cost_mul(idx.upper.element_count(), idx.table.sz)
    else:
      self.base_sz = idx.table.sz 
    self.dup_ratio = get_dup_ratio_from_keys(idx.key_fields())
    self.div_ratio = get_div_ratio(idx.condition, idx.key_fields())
    self.tup_cnt = CostOp(CostOp(self.base_sz, COST_MUL, self.dup_ratio), COST_DIV, self.div_ratio)

def get_dup_ratio_from_keys(keys, path=[]):
  nextlevel = {}
  for k in keys:
    if len(k.path) > 0:
      add_to_list_map(k.path[0], k, nextlevel)
  factor = 1
  for k,v in list(nextlevel.items()):
    f = get_query_field(k)
    if f.table.has_one_or_many_field(f.field_name) != 1:
      factor = cost_mul(factor, f.table.get_nested_table_by_name(f.field_name).sz)
    newkeys = []
    for k1 in v:
      newk = KeyPath(k1.key, k1.path[1:])
      if newk not in newkeys:
        newkeys.append(newk)
    next_factor = get_dup_ratio_from_keys(newkeys)
    factor = cost_mul(factor, next_factor)
  return factor


def find_assigned_pred_selectivity(pred):
  for p,s in globalv.pred_selectivity:
    if p.query_pred_eq(pred):
      return s
  return None

def get_div_ratio(pred, keys):
  assigned = find_assigned_pred_selectivity(pred)
  if assigned:
    return 1.0/float(assigned)
  if isinstance(pred, ConnectOp):
    if pred.op == AND:
      return cost_mul(get_div_ratio(pred.lh, keys), get_div_ratio(pred.rh, keys))
    else:
      # FIXME : estimiation for OR
      return 2
  elif isinstance(pred, BinOp):
    if len(pred.get_all_params()) > 1:
      return 1
    if any([k.key == pred.lh for k in keys]):
      return 1
    if isinstance(pred.rh, QueryField) or isinstance(pred.rh, AssocOp):
      return 2
    if pred.op in [LT, GT, LE, GE, IN, BETWEEN]:
      return 2
    if isinstance(pred.rh, MultiParam):
      return 2
    assert(isinstance(pred.rh, AtomValue))
    v = pred.rh.v
    r = get_query_field(pred.lh).field_class.get_nv_for_cost(v=v, exclude=(pred.op==NEQ))
    return r
  elif isinstance(pred, SetOp):
    # newk = []
    # for k in keys:
    #   if len(k.path) > 0 and k.path[0] == pred.lh:
    #     newk.append(KeyPath(k.key, k.path[1:]))
    # return get_div_ratio(pred.rh, newk)
    return 1
  elif isinstance(pred, UnaryOp):
    return 1
  else:
    assert(False)

def get_keys_by_pred(pred, path=[]):
  if isinstance(pred, ConnectOp):
    return get_keys_by_pred(pred.lh)+get_keys_by_pred(pred.rh)
  elif isinstance(pred, BinOp):
    if isinstance(pred.rh, Parameter):
      return [KeyPath(pred.lh, path)]
    else:
      return []
  elif isinstance(pred, UnaryOp):
    return get_keys_by_pred(pred.operand)
  elif isinstance(pred, SetOp):
    nextpath = [p for p in path] + [pred.lh]
    return get_keys_by_pred(pred.rh, nextpath)
  else:
    assert(False)

def get_idx_op_cost_div(idxop, params):
  if len(params) == 0:
    return 1
  if idxop.is_point():
    factor = 1
    for i in range(0, len(params[0].fields)):
      p1 = params[0].params[i]
      f = get_query_field(params[0].fields[i].key)
      factor = cost_mul(factor, f.field_class.get_nv_for_cost())
    return factor
  else:
    factor = 1
    for i in range(0, len(params[0].fields)):
      p1 = params[0].params[i]
      p2 = params[1].params[i]
      f = get_query_field(params[0].fields[i].key)
      if p1 == p2:
        if isinstance(p1, AtomValue):
          factor = cost_mul(factor, f.field_class.get_nv_for_cost(p1.v))
        else:
          factor = cost_mul(factor, f.field_class.get_nv_for_cost())
      elif isinstance(p1, Parameter) or isinstance(p2, Parameter):
        factor = cost_mul(factor, 2)
    return factor

def get_query_result_sz(table, pred):
  base_sz = table.sz
  if pred is None:
    return base_sz
  keys = get_keys_by_pred(pred)
  pred_div = get_div_ratio(pred, keys)
  return cost_div(base_sz, pred_div)


def cost_computed(cost):
  return type(cost) is not int or cost > 0
