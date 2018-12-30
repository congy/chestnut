import math
from pred import *
from util import *
from constants import *
from cost import *
import globalv

#duplication, as table size estimation
#also computes for partition
class IdxSizeUnit(Cost):
  def __init__(self, idx):
    self.idx = idx
    self.pred = idx.condition
    self.table_sz = CostTableUnit(idx.table)
    self.dup_ratio = get_denormalized_table_factor(self.pred)
    self.div_ratio = SelectivityConstUnit(self.pred)
    self.record_cnt = CostOp(CostOp(self.table_sz, COST_MUL, self.dup_ratio), COST_DIV, self.div_ratio)
  def str_symbol(self):
    return to_symbol(self.record_cnt)
  def to_real_value(self):
    return to_real_value(self.record_cnt)
    
#divider, as selectivity estimation, pred without considering next level
class SelectivityConstUnit(Cost):
  def __init__(self, pred):
    self.pred = pred
    v = find_assigned_pred_selectivity(pred)
    if v is not None:
      self.div_ratio = int(1.0/v)
    if isinstance(pred, ConnectOp):
      if pred.op == AND:
        self.div_ratio = CostOp(SelectivityConstUnit(pred.lh), COST_MUL, SelectivityConstUnit(pred.rh))
      else:
        # FIXME
        self.div_ratio = CostOp(SelectivityConstUnit(pred.lh), COST_DIV, 2)
    else:
      if isinstance(pred, SetOp):
        if len(pred.get_all_params()) > 0:
          self.div_ratio = 1
        else:
          self.div_ratio = 2
      elif isinstance(pred, UnaryOp):
        self.div_ratio = 1
      elif isinstance(pred, BinOp):
        if pred.op in [LT, GT, LE, GE, IN, BETWEEN]:
          self.div_ratio = 2
        else:
          v = None
          if isinstance(pred.rh, AtomValue):
            v = pred.rh.v
            r = get_query_field(pred.lh).field_class.get_nv_for_cost(v=v, exclude=(pred.op==NEQ)) 
            self.div_ratio = r
          else:
            self.div_ratio = 1
      else:
        self.div_ratio = 1
  def str_symbol(self):
    return to_symbol(self.div_ratio)
  def to_real_value(self):
    return to_real_value(self.div_ratio)
  
#divider, as selectivity estimation
class SelectivityUnit(Cost):
  def __init__(self, pred):
    self.pred = pred
    v = find_assigned_pred_selectivity(pred)
    if v is not None:
      self.div_ratio = int(1.0/v)
    if isinstance(pred, ConnectOp):
      if pred.op == AND:
        self.div_ratio = CostOp(SelectivityUnit(pred.lh), COST_MUL, SelectivityUnit(pred.rh))
      else:
        # FIXME : estimiation for OR
        self.div_ratio = CostOp(SelectivityUnit(pred.lh), COST_DIV, 2)
    else:
      assigned_ratio = None
      if assigned_ratio:
        self.div_ratio = assigned_ratio
      else:
        if isinstance(pred, SetOp):
          if pred.rh.has_param():
            self.div_ratio = SelectivityUnit(pred.rh) 
          else:
            self.div_ratio = 1
        elif isinstance(pred, UnaryOp):
          self.div_ratio = 1
        elif pred.op in [LT, GT, LE, GE, IN, BETWEEN]:
          self.div_ratio = 2
        else:
          v = None
          if isinstance(pred.rh, AtomValue):
            v = pred.rh.v
          r = get_query_field(pred.lh).field_class.get_nv_for_cost(v=v, exclude=(pred.op==NEQ))
          self.div_ratio = r
  def str_symbol(self):
    return to_symbol(self.div_ratio)
  def to_real_value(self):
    return to_real_value(self.div_ratio)
  
def get_denormalized_table_factor(idx_pred):
  if isinstance(idx_pred, SetOp):
    if idx_pred.rh.has_param():
      pred_factor = get_denormalized_table_factor(idx_pred.rh)
      assoc = get_query_field(idx_pred.lh).table.get_assoc_by_name(get_query_field(idx_pred.lh).field_name)
      assoc_factor = CostAssocUnit(uppert=get_query_field(idx_pred.lh).table, assoc=assoc)
      if type(pred_factor) is int:
        return assoc_factor
      else:
        return CostOp(assoc_factor, COST_MUL, pred_factor)
    else:
      return 1
  elif isinstance(idx_pred, ConnectOp):
    lft_factor = get_denormalized_table_factor(idx_pred.lh)
    rgt_factor = get_denormalized_table_factor(idx_pred.rh)
    if type(lft_factor) is int and lft_factor == 1:
      return rgt_factor
    if type(rgt_factor) is int and rgt_factor == 1:
      return lft_factor
    return CostOp(lft_factor, COST_ADD, rgt_factor)
  else:
    return 1


def get_div_ratio_by_pred(pred):
  qs = [pred]
  rs = []
  while len(qs) > 0:
    q = qs.pop()
    v = find_assigned_pred_selectivity(pred)
    if v is not None:
      rs.append(1.0/v)
      continue
    if isinstance(q, ConnectOp):
      if q.op == AND:
        qs.append(q.lh)
        qs.append(q.rh)
      if q.op == OR:
        assert(False)
    elif isinstance(q, SetOp):
      qs.append(q.rh)
    elif isinstance(q.rh, Parameter) or isinstance(q.rh, AtomValue):
      if q.op == EQ:
        rs.append(SelectivityUnit(q))
      elif q.op == NEQ:
        rs.append(1)
      else:
        rs.append(2)
  if len(rs) == 0:
    return 1
  r = rs[0]
  for i in range(1, len(rs)):
    r = CostOp(r, COST_MUL, rs[i])
  return r

def get_div_ratio_for_idx_size(pred):
  qs = [pred]
  rs = []
  while len(qs) > 0:
    q = qs.pop()
    v = find_assigned_pred_selectivity(pred)
    if v is not None:
      rs.append(1.0/v)
      continue
    if isinstance(q, ConnectOp):
      if q.op == AND:
        qs.append(q.lh)
        qs.append(q.rh)
      if q.op == OR:
        assert(False)
    elif isinstance(q, SetOp):
      qs.append(q.rh)
    elif isinstance(q.rh, AtomValue):
      if q.op == EQ:
        rs.append(SelectivityUnit(q))
      elif q.op == NEQ:
        rs.append(1)
      else:
        rs.append(2)
  if len(rs) == 0:
    return 1
  r = rs[0]
  for i in range(1, len(rs)):
    r = CostOp(r, COST_MUL, rs[i])
  return r

def get_query_result_sz(table, pred):
  base_sz = CostTableUnit(table)
  if pred is None:
    return base_sz
  pred_div = SelectivityUnit(pred)
  return cost_div(base_sz, pred_div)

def find_assigned_pred_selectivity(pred):
  for p,s in globalv.pred_selectivity:
    if p.query_pred_eq(pred):
      return s
  return None

def cost_computed(cost):
  return type(cost) is not int or cost > 0
