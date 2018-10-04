import math
from util import *
from constants import *

def is_basic_type(v):
  return type(v) is int or type(v) is float

class Cost(object):
  def to_real_value(self):
    return None
  def to_range_value(self, take_min=True):
    return None

class IndexSearchUnit(Cost):
  def __init__(self, tree_sz):
    self.tree_sz = tree_sz
  def str_symbol(self):
    tree_sz_symbol = self.tree_sz.str_symbol()
    return 'log({})'.format(tree_sz_symbol)
  def to_real_value(self):
    v = to_real_value(self.tree_sz)
    return math.log(v, 2)

class CostTableUnit(Cost):
  def __init__(self, table):
    self.table = table
  def str_symbol(self):
    return self.table.cost_str_symbol()
  def to_real_value(self):
    return self.table.cost_real_size() 

class CostAssocUnit(Cost):
  def __init__(self, uppert=0, assoc=None):
    self.assoc = assoc
    self.reverse_direction = (uppert == assoc.rgt)
  def str_symbol(self):
    if self.reverse_direction:
      return '{}_per_{}'.format(self.assoc.rgt_field_name, self.assoc.rgt.name)
    else:
      return '{}_per_{}'.format(self.assoc.lft_field_name, self.assoc.lft.name)
  def to_real_value(self):
    if self.reverse_direction:
      return self.assoc.rgt_ratio
    else:
      return self.assoc.lft_ratio 

class CostOp(Cost):
  def __init__(self, lh, op, rh):
    self.lh = lh
    self.op = op
    self.rh = rh
  def str_symbol(self):
    lh_symbol = to_symbol(self.lh)
    rh_symbol = to_symbol(self.rh)
    return "({} {} {})".format(lh_symbol, get_cost_op_to_str(self.op), rh_symbol)
  def to_real_value(self):
    lh_v = to_real_value(self.lh)
    rh_v = to_real_value(self.rh)
    if self.op == COST_DIV:
      assert(rh_v > 0)
      r = float(lh_v) / float(rh_v)
      return math.ceil(r) 
    if self.op == COST_ADD:
      return lh_v + rh_v
    if self.op == COST_MUL:
      return lh_v * rh_v
    if self.op == COST_MINUS:
      if lh_v - rh_v <= 1:
        return 1
      return lh_v - rh_v
    assert(False)

class CostLogOp(Cost):
  def __init__(self, operand):
    self.operand = operand
  def str_symbol(self):
    return "log({})".format(self.operand.str_symbol())
  def to_real_value(self):
    v = to_real_value(self.operand)
    if v == 0:
      return 0
    r = math.log(v, 2)
    return math.ceil(r)
  def to_range_value(self, take_min=True):
    v = to_range_value(self.operand, take_min)
    if v == 0:
      return 0
    r = math.log(v, 2)
    return math.ceil(r)
  def to_range_symbol(self, take_min=True):
    return 'log({})'.format(self.operand.to_range_symbol(take_min))

def to_symbol(v):
  return v.str_symbol() if not is_basic_type(v) else v

def to_real_value(v):
  return v.to_real_value() if not is_basic_type(v) else v

def cost_add(x, y):
  if type(x) is int and type(y) is int:
    return x+y
  else:
    return CostOp(x, COST_ADD, y)

def cost_minus(x, y):
  if type(x) is int and type(y) is int:
    return x-y if x>y else 1
  else:
    return CostOp(x, COST_MINUS, y)

def cost_mul(x, y):
  if type(x) is int and type(y) is int:
    return x*y
  else:
    return CostOp(x, COST_MUL, y)

def cost_div(x, y):
  if type(x) is int and type(y) is int:
    return math.ceil(float(x)/float(y))
  else:
    return CostOp(x, COST_DIV, y)
