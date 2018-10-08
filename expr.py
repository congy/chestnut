from util import *
from constants import *
from pred import *

expr_delta_cache = {}

def get_expr_delta_cache(v):
  global expr_delta_cache
  if v not in expr_delta_cache:
    thread_ctx = symbctx.create_thread_ctx()
  return expr_delta_cache[v]

def set_expr_delta_cache(key, value):
  global expr_delta_cache
  expr_delta_cache[key] = value

def type_larger(l, r):
  if l == 'float' and (not r == 'float'):
    return True
  return False

class InitialValuePlaceholder(object):
  def __init__(self,tipe=None):
    self.tipe = tipe
  def get_type(self):
    return self.tipe
  def __str__(self):
    return 'orig_value'

class BinaryExpr(object):
  def __init__(self, lh, op, rh):
    self.lh = lh
    self.op = op
    self.rh = rh 
    # assert(is_query_field(self.lh) or \
    #   isinstance(self.lh, AtomValue) or \
    #   isinstance(self.lh, BinaryExpr) or\
    #   isinstance(self.lh, Parameter))
    # assert(is_query_field(self.rh) or \
    #   isinstance(self.rh, AtomValue) or \
    #   isinstance(self.rh, BinaryExpr) or\
    #   isinstance(self.rh, Parameter))  
    assert(not isinstance(self.lh, UnaryExpr))
    assert(not isinstance(self.rh, UnaryExpr))
  def __eq__(self, other):
    return type(self) == type(other) and self.lh == other.lh and self.op == other.op and self.rh == other.rh
  def to_var_or_value(self, replace={}):
    lh = replace[self.lh] if self.lh in replace else '{}'.format(self.lh.to_var_or_value(replace=replace))
    rh = replace[self.rh] if self.rh in replace else '{}'.format(self.rh.to_var_or_value(replace=replace))    
    if type_larger(self.lh.get_type(), self.rh.get_type()):
      rh = '({}){}'.format(get_cpp_types(self.lh.get_type()), rh)
    if type_larger(self.rh.get_type(), self.lh.get_type()):
      lh = '({}){}'.format(get_cpp_types(self.rh.get_type()), lh)
    return '({} {} {})'.format(lh, expr_op_to_cpp_map[self.op], rh)
  def __str__(self):
    lh = str(self.lh)
    op = expr_op_to_str_map[self.op]
    rh = str(self.rh)
    return '({} {} {})'.format(lh, op, rh)
  def complete_field(self, table):
    self.lh.complete_field(table)
    self.rh.complete_field(table)
    if isinstance(self.rh, AtomValue):
      self.rh.tipe = self.lh.get_type()
  def get_type(self):
    lh_type = self.lh.get_type()
    rh_type = self.rh.get_type()
    if lh_type == 'float' or rh_type == 'float':
      return 'float'
    if lh_type:
      return lh_type
    if rh_type:
      return rh_type
    assert(False)
    return None
  def get_all_fields(self):
    return self.lh.get_all_fields() + self.rh.get_all_fields()
  def get_curlevel_fields(self, include_assoc=False):
    return self.lh.get_curlevel_fields(include_assoc) + self.rh.get_curlevel_fields(include_assoc)
  def get_all_params(self):
    return self.lh.get_all_params() + self.rh.get_all_params()
  def query_pred_eq(self, other):
    return self.__eq__(other)
  def get_all_atom_values(self):
    return self.lh.get_all_atom_values() + self.rh.get_all_atom_values()
  def to_json(self):
    return '({}){}({})'.format(self.lh.to_json(), expr_op_to_str_map[self.op], self.rh.to_json())

class UnaryExpr(object):
  def __init__(self, op, operand=""):
    self.op = op
    self.operand = operand
    # assert(is_query_field(self.operand) or \
    #   isinstance(self.operand, BinaryExpr) or \
    #   isinstance(self.operand, AtomValue) or \
    #   isinstance(self.operand, IfThenElseExpr) or \
    #   self.operand == '')
    if self.op == AVG:
      self.sum_var = None
      self.count_var = None
  def __eq__(self, other):
    return type(self) == type(other) and self.op == other.op and self.operand == other.operand
  def to_var_or_value(self, init_var='', replace_var={}):
    if self.op == COUNT:
      opd = ''
    elif self.operand in replace_var:
      opd = replace_var[self.operand]
    else:
      opd = '{}'.format(self.operand.to_var_or_value(replace_var))
    if self.op == MAX:
      return 'if ({}<{}) {} = {};\n'.format(init_var, opd, init_var, opd)
    elif self.op == MIN:
      return 'if ({}>{}) {} = {};\n'.format(init_var, opd, init_var, opd)
    elif self.op == COUNT:
      return '{}++;\n'.format(init_var)
    elif self.op == SUM:
      return '{} = {} + {};\n'.format(init_var, init_var, opd)
    elif self.op == AVG:
      return ''
    else:
      assert(False)
  def __str__(self):
    op = expr_op_to_str_map[self.op]
    operand = str(self.operand)
    return '{}({})'.format(op, operand)
  def get_type(self):
    if self.op == COUNT:
      return 'uint'
    tipe = self.operand.get_type()
    if self.op == SUM:
      return get_sum_type(tipe)
    return tipe
    assert(False)
  def complete_field(self, table):
    if self.op != COUNT:
      self.operand.complete_field(table)
  def get_all_fields(self):
    if self.op == COUNT:
      return []
    return self.operand.get_all_fields()
  def get_curlevel_fields(self, include_assoc=False):
    if self.op == COUNT:
      return []
    return self.operand.get_curlevel_fields(include_assoc)
  def get_all_atom_values(self):
    if self.op == COUNT:
      return [AtomValue(1)]
    return self.operand.get_all_atom_values()
  def get_all_params(self):
    if self.op == COUNT:
      return []
    return self.operand.get_all_params()
  def query_pred_eq(self, other):
    return self.__eq__(other)
  def to_json(self):
    if self.op == COUNT:
      return 'count()'
    else:
      return '{}({})'.format(expr_op_to_str_map[self.op], self.operand.to_json())


class IfThenElseExpr(object):
  def __init__(self, cond, expr1, expr2):
    self.cond = cond
    self.expr1 = expr1
    self.expr2 = expr2
    self.op = IFTHENELSE
    # assert(isinstance(self.cond, BinaryExpr))
    # assert(is_query_field(self.expr1) or isinstance(self.expr1, AtomValue) or isinstance(self.expr1, BinaryExpr))
    # assert(is_query_field(self.expr2) or isinstance(self.expr2, AtomValue) or isinstance(self.expr2, BinaryExpr))
    assert(not isinstance(self.expr1, UnaryExpr))
    assert(not isinstance(self.expr2, UnaryExpr))
  def __eq__(self, other):
    return type(self) == type(other) and self.cond == other.cond and self.expr1 == other.expr1 and self.expr2 == other.expr2
  def to_var_or_value(self, init_var='', replace_var={}):
    cond = self.cond.to_var_or_value(replace_var)
    if isinstance(self.expr1, UnaryExpr):
      expr1 = '{}'.format(self.expr1.to_var_or_value(init_var, replace_var))
    else:
      expr1 = '{} = {};\n'.format(init_var, self.expr1.to_var_or_value(replace_var))
    if isinstance(self.expr2, UnaryExpr):
      expr2 = '{}'.format(self.expr2.to_var_or_value(init_var, replace_var))
    else:
      expr2 = '{} = {};\n'.format(init_var, self.expr2.to_var_or_value(replace_var))
    return 'if ({}) {}else {}'.format(cond, expr1, expr2)
  def __str__(self):
    return 'if ({}) then ({}) else ({})'.format(self.cond, self.expr1, self.expr2)
  def get_type(self):
    tipe = self.expr1.get_type()
    return tipe
  def complete_field(self, table):
    self.cond.complete_field(table)
    self.expr1.complete_field(table)
    self.expr2.complete_field(table)
  def get_all_fields(self):
    return self.cond.get_all_fields() + self.expr1.get_all_fields() + self.expr2.get_all_fields()
  def get_curlevel_fields(self, include_assoc=False):
    return self.cond.get_curlevel_fields(include_assoc) + \
          self.expr1.get_curlevel_fields(include_assoc) + \
          self.expr2.get_curlevel_fields(include_assoc)
  def get_all_params(self):
    return self.cond.get_all_params() + self.expr1.get_all_params() + self.expr2.get_all_params()
  def get_all_atom_values(self):
    return self.cond.get_all_atom_values() + self.expr1.get_all_atom_values() + self.expr2.get_all_atom_values()
  def query_pred_eq(self, other):
    return self.__eq__(other)
  def to_json(self):
    return 'ite({}, {}, {})'.format(self.cond.to_json(), self.expr1.to_json(), self.expr2.to_json())


def replace_subexpr_with_var(expr, placeholder):
  if isinstance(expr, BinaryExpr):
    return BinaryExpr(replace_subexpr_with_var(expr.lh, placeholder), expr.op, replace_subexpr_with_var(expr.rh, placeholder))
  elif isinstance(expr, UnaryExpr):
    return UnaryExpr(expr.op, replace_subexpr_with_var(expr.operand, placeholder))
  elif isinstance(expr, IfThenElseExpr):
    return IfThenElseExpr(replace_subexpr_with_var(expr.cond, placeholder), \
                          replace_subexpr_with_var(expr.expr1, placeholder), \
                          replace_subexpr_with_var(expr.expr2, placeholder))
  elif isinstance(expr, AssocOp):
    assert(expr in placeholder)
    return placeholder[expr]
  elif isinstance(expr, BinOp):
    return BinOp(replace_subexpr_with_var(expr.lh, placeholder), expr.op, replace_subexpr_with_var(expr.rh, placeholder))
  else:
    return expr

def get_curlevel_fields(expr):
  if isinstance(expr, QueryField):
    if isinstance(expr, UpperQueryField):
      return []
    return [expr]
  elif isinstance(expr, BinOp):
    return get_curlevel_fields(expr.lh) + get_curlevel_fields(expr.rh)
  elif isinstance(expr, SetOp):
    return []
  elif isinstance(expr, ConnectOp):
    return get_curlevel_fields(expr.lh) + get_curlevel_fields(expr.rh)
  elif isinstance(expr, AssocOp):
    return []
  elif isinstance(expr, UnaryOp):
    return get_curlevel_fields(expr.operand)
  elif isinstance(expr, IfThenElseExpr):
    return get_curlevel_fields(expr.cond) + get_curlevel_fields(expr.expr1) + get_curlevel_fields(expr.expr2)
  elif isinstance(expr, BinaryExpr):
    return get_curlevel_fields(expr.lh) + get_curlevel_fields(expr.rh)
  elif isinstance(expr, UnaryExpr):
    return get_curlevel_fields(expr.operand)
  else:
    return []
