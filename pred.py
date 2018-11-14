from util import *
from constants import *
from schema import *
import globalv
import z3

def f(field, table=None):
  return QueryField(field, table)

envvar_cnt = 0

class TempVariable(object):
  def __init__(self, name, tipe, is_temp=True):
    self.name = name
    self.tipe = tipe
    self.is_temp = is_temp
  def get_type(self):
    return self.tipe
  def complete_field(self):
    pass
  def query_pred_eq(self, other):
    return self == other
  def get_curlevel_fields(self):
    return []
  def get_all_fields(self):
    return []
  def __str__(self):
    return self.name

class EnvAtomicVariable(TempVariable):
  def __init__(self, name, tipe, is_temp=True, init_value=0):
    super(EnvAtomicVariable, self).__init__(name, tipe, is_temp)
    self.init_value = init_value
  def to_json(self, full_dump=False):
    return {"atom":True, "name":self.name, "type":self.tipe, "init":self.init_value} if full_dump else self.name

class EnvCollectionVariable(TempVariable):
  def __init__(self, name, tipe, is_temp=True, updateptr_type=False):
    super(EnvCollectionVariable, self).__init__(name, tipe, is_temp)
    self.order = None
    self.ascending = True
    self.limit = 0
    # instead of array of proto objs, use a quicker/smaller optimized objs (usually to improve sorting speed)
    self.updateptr_type = updateptr_type
    # for nested_proto_obj and update obj
    self.upper_var = None
    # in reflect to upper_var: self.upper_var.nested_type == self.tipe
    self.nested_type = None
    self.sz = 0
    self.fields = []
  def set_upper_var(self, upper_var):
    if upper_var:
      self.upper_var = upper_var
      upper_var.nested_type = self.tipe
  def get_sz(self):
    return self.sz
  def to_json(self, full_dump=False):
    return {"atom":False, "name":self.name, "type":self.tipe.name, "fields":[f.field_class.name for f in self.fields]} if full_dump else self.name
    
def get_envvar_name(v):
  global envvar_cnt
  envvar_cnt += 1
  return 'v{}'.format(envvar_cnt)

class Parameter(object):
  def __init__(self, symbol, tipe='oid', dependence=None):
    self.symbol = symbol
    self.tipe = tipe
    self.dependence = dependence
  def has_param(self):
    return True
  def complete_field(self, table):
    pass
  def __str__(self):
    return "Param ({})".format(self.symbol)
  def __hash__(self):
   return hash(str(self))
  def __eq__(self, other):
    return str(self) == str(other)
  def template_eq(self, other):
    return self.idx_pred_eq(other)
  def get_type(self):
    return self.tipe
  def to_var_or_value(self, replace={}):
    return self.symbol
  def get_all_params(self):
    return [self]
  def idx_pred_eq(self, other):
    return isinstance(other, Parameter)
  def query_pred_eq(self, other):
    return type(self)==type(other) and (not isinstance(other, MultiParam)) and self.symbol == other.symbol
  def get_curlevel_fields(self, include_assoc=False):
    return []
  def to_json(self):
    return 'param[{}]'.format(self.symbol)
  def get_all_fields(self):
    return []

class MultiParam(Parameter):
  def __init__(self, params=[]):
    self.params = params
  def __str__(self):
    return "({})".format(','.join([str(p) for p in self.params]))
  def __eq__(self, other):
    return str(self) == str(other)
  def get_type(self):
    return self.params[0].tipe
  def get_all_params(self):
    return filter(lambda p: isinstance(p, Parameter), self.params)
  def query_pred_eq(self, other):
    return type(self) == type(other) and len(self.params) == len(other.params) and \
      all([self.params[p]==other.params[p] for p in range(0, len(self.params))])
  def to_json(self):
    return '[{}]'.format(', '.join([x.to_json() for x in self.params]))

def DoubleParam(p1, p2):
  return MultiParam([p1, p2])
  
class AtomValue(object):
  def __init__(self, v, tipe='int'):
    self.v = v
    self.tipe = tipe
  def to_var_or_value(self, replace={}):
    return '"{}"'.format(self.v) if is_string_type(self.tipe) or type(self.v) is str else self.v
  def to_z3_value(self):
    if is_string_type(self.tipe) or type(self.v) is str:
      return hash(self.v) % MAXINT
    else:
      return self.v
  def get_type(self):
    return self.tipe
  def has_param(self):
    return False
  def complete_field(self, table):
    pass
  def __str__(self):
    return "Value ({})".format(self.v)
  def __eq__(self, other):
    return str(self) == str(other)
  def template_eq(self, other):
    return type(self) == type(other)
  def get_all_params(self):
    return []
  def get_all_fields(self):
    return []
  def idx_pred_eq(self,  other):
    return type(other) == type(self) and self.v == other.v
  def query_pred_eq(self, other):
    return type(other) == type(self) and self.v == other.v
  def get_curlevel_fields(self, include_assoc=False):
    return []
  def get_all_atom_values(self):
    return [self]
  def to_json(self):
    return "'{}'".format(self.v) if type(self.v) is str else str(self.v)

class QueryField(object):
  def __init__(self, field, table=None):
    self.table = table
    self.field_name = field
    self.field_class = None
    if table is not None:
      self.complete_field(table)
  def field_eq(self, other):
    return type(self) == type(other) and self.field_name == other.field_name and get_main_table(self.table) == get_main_table(other.table)
  def __eq__(self, other):
    return self.field_eq(other)
  def get_type(self):
    if is_atomic_field(self):
      return self.field_class.tipe
    else:
      return self.field_class
  def is_atomic_field(self):
    return isinstance(self.field_class, Field)
  def f(self, field_name, table=None): #one to many relation
    new_qf = QueryField(field_name, table)
    q = AssocOp(self, new_qf)
    return q
  def complete_field(self, table):
    field = self.field_name
    self.table = table
    if table.has_field(field):
      self.field_class = table.get_field_by_name(field)
    elif table.has_assoc(field):
      assoc = table.get_assoc_by_name(field)
      if table.name == assoc.lft.name:
        self.field_class = assoc.rgt
      else:
        self.field_class = assoc.lft
    else:
      print "field {} in table {} unfound".format(field, table.name)
      assert (False)
  def to_var_or_value(self, replace={}):
    return "{}.{}".format(self.table.name, self.field_name)
  def __str__(self):
    return "{}:{}".format(self.table.name if self.table else None, self.field_name)
  def __hash__(self):
    return hash(str(self))
  def has_param(self):
    return False
  def get_all_params(self):
    return []
  def get_necessary_index_keys(self):
    return [self]
  def get_all_fields(self):
    return [self]
  def idx_pred_eq(self, other):
    return isinstance(other, QueryField) and self.table == other.table and self.field_name == other.field_name
  def query_pred_eq(self, other):
    return isinstance(other, QueryField) and self.table == other.table and self.field_name == other.field_name
  def template_eq(self, other):
    return self.idx_pred_eq(other)
  def get_curlevel_fields(self, include_assoc=False):
    return [self]
  def get_all_atom_values(self):
    return []
  def to_json(self):
    return self.field_name

# used in if condition...
class UpperQueryField(QueryField): 
  def __str__(self):
    return "Upper({}:{})".format(self.table.name, self.field_name)
  
class Pred(object):
  def has_param(self):
    pass
  def get_all_params(self):
    pass
  def get_necessary_index_keys(self):
    pass
  def get_all_fields(self, include_assoc=False):
    pass
  def get_necessary_index_params(self):
    pass
  def complete_field(self, table, upper_table=None, assoc_name=""):
    pass
  def __str__(self):
    pass
  def __hash__(self):
    return hash(str(self))
  def split(self):
    pass
  def get_reverse(self):
    pass
  def contain_exist_forall(self):
    pass
  def idx_pred_eq(self, other):
    pass
  def query_pred_eq(self, other):
    pass
  def get_cnf_literal(self):
    pass
  def get_dnf_literal(self):
    pass
  def get_curlevel_fields(self, include_assoc=False):
    pass

class UnaryOp(Pred):
  def __init__(self, operand):
    self.op = NOT
    self.operand = operand
  def has_param(self):
    return self.operand.has_param()
  def get_all_params(self):
    return self.operand.get_all_params()
  def get_necessary_index_keys(self):
    return self.operand.get_necessary_index_keys()
  def get_all_fields(self, include_assoc=False):
    return self.operand.get_all_fields()
  def get_necessary_index_params(self):
    return self.operand.get_necessary_index_params()
  def complete_field(self, table):
    self.operand.complete_field(table)
  def __str__(self):
    return '(!{})'.format(self.operand)
  def __eq__(self, other):
    return str(self) == str(other)
  def __hash__(self):
    return hash(str(self))
  def split(self):
    return [self]
  def get_reverse(self):
    return self.operand
  def contain_exist_forall(self):
    return self.operand.contain_exist_forall()
  def idx_pred_eq(self, other):
    return self.operand.idx_pred_eq(other.operand)
  def query_pred_eq(self, other):
    return type(self) == type(other) and self.operand.query_pred_eq(other.operand)
  def template_eq(self, other):
    return self.operand.template_eq(other)
  def get_cnf_literal(self):
    return [self]
  def get_dnf_literal(self):
    return [self]
  def get_curlevel_fields(self, include_assoc=False):
    return self.operand.get_curlevel_fields(include_assoc)
  
class AssocOp(Pred):
  def __init__(self, lh, rh):
    self.lh = lh
    self.rh = rh
    assert(isinstance(lh, QueryField))
    assert(is_query_field(self.rh))
  def has_param(self):
    return False
  def get_type(self):
    return self.rh.get_type()
  def f(self, field_name):
    last = self
    while isinstance(last.rh, AssocOp):
      last = last.rh
    assert(isinstance(last.rh, QueryField))
    newf = QueryField(field_name)
    q = AssocOp(last.rh, newf)
    last.rh = q
    return self
  def get_all_params(self):
    return []
  def get_necessary_index_keys(self):
    return get_necessary_index_keys(self.rh)
  def get_all_fields(self):
    return [self]
  def get_necessary_index_params(self):
    return []
  def complete_field(self, table):
    self.lh.complete_field(table)
    assoc = table.get_nested_table_by_name(self.lh.field_name)
    assert(assoc)
    next_table = assoc.related_table
    self.rh.complete_field(next_table)
  def __str__(self):
    return "({} . {})".format(self.lh, self.rh)
  def __hash__(self):
    return hash(str(self))
  def __eq__(self, other):
    return str(self) == str(other)
  def split(self):
    return [self]
  def get_reverse(self):
    return self
  def contain_exist_forall(self):
    return True
  def idx_pred_eq(self, other):
    return type(self) == type(other) and self.lh == other.lh and self.rh == other.rh
  def query_pred_eq(self, other):
    return self.idx_pred_eq(other)
  def template_eq(self, other):
    return self.idx_pred_eq(other)
  def get_cnf_literal(self):
    return [self]
  def get_dnf_literal(self):
    return [self]
  def get_curlevel_fields(self, include_assoc=False):
    return [self] if include_assoc else []
  def get_all_atom_values(self):
    return []
  def to_json(self):
    return '{}.{}'.format(self.lh.to_json(), self.rh.to_json())

class SetOp(Pred):
  def __init__(self, lh, op, rh):
    self.lh = lh
    self.rh = rh
    self.op = op
    assert(op in [EXIST, FORALL])
    assert(is_query_field(self.lh))
    assert(isinstance(self.rh, BinOp) or \
            isinstance(self.rh, ConnectOp) or \
            isinstance(self.rh, SetOp) or \
            is_query_field(self.rh))
  def has_param(self):
    r = self.rh.has_param() 
    return r
  def get_all_params(self):
    return self.lh.get_all_params() + self.rh.get_all_params()
  def get_necessary_index_keys(self):
    return self.rh.get_necessary_index_keys()
  def get_all_fields(self):
    return self.rh.get_all_fields()
  def get_necessary_index_params(self):
    return self.rh.get_necessary_index_params()
  def complete_field(self, table):
    self.lh.complete_field(table)
    lh = get_query_field(self.lh)
    assoc = lh.table.get_nested_table_by_name(lh.field_name)
    assert(assoc)
    next_table = assoc.related_table
    self.rh.complete_field(next_table)
  def __str__(self):
    return "({} {} {})".format(self.lh, pred_op_to_cpp_map[self.op], self.rh)
  def __hash__(self):
    return hash(str(self))
  def __eq__(self, other):
    return str(self) == str(other)
  def split(self):
    return [self]
  def split_into_dnf(self):
    return [self]
  def get_reverse(self):
    return SetOp(self.lh, reversed_op[self.op], self.rh.get_reverse())
  def contain_exist_forall(self):
    return True
  def idx_pred_eq(self, other):
    return type(self) == type(other) and self.op == other.op and self.lh.idx_pred_eq(other.lh) and self.rh.idx_pred_eq(other.rh)
  def query_pred_eq(self, other):
    return type(self) == type(other) and self.op == other.op and self.lh.query_pred_eq(other.lh) and self.rh.query_pred_eq(other.rh)
  def template_eq(self, other):
    return type(self) == type(other) and self.op == other.op and self.lh.template_eq(other.lh) and self.rh.template_eq(other.rh)
  def get_cnf_literal(self):
    return [self]
  def get_dnf_literal(self):
    return [self]
  def get_curlevel_fields(self, include_assoc=False):
    return []
  def to_json(self):
    return 'exists({}, {})'.format(self.lh.to_json(), self.rh.to_json())


class BinOp(Pred):
  def __init__(self, lh, op, rh):
    self.lh = lh
    self.rh = rh
    self.op = op 
  def has_param(self):
    return self.lh.has_param() or self.rh.has_param()
  def get_all_params(self):
    return self.lh.get_all_params() + self.rh.get_all_params()
  def get_necessary_index_keys(self):
    if (is_query_field(self.lh) and is_query_field(self.rh)):
      return []
    if self.op in [EQ, NEQ, LT, LE, GT, GE, BETWEEN]:
      if isinstance(self.rh, Parameter):
        return [self.lh]
    elif self.op in [IN, SUBSTR]:
      return []
    else:
      assert(False) 
    return []
  def get_all_fields(self):
    return self.lh.get_all_fields() + self.rh.get_all_fields()
  def get_all_assocs(self):
    if is_next_level_op(self.op):
      assoc = self.lh.table.get_assoc_by_name(self.lh.field_name)
      assert(assoc)
      return [assoc] + self.rh.get_all_assocs()
    return []
  def get_necessary_index_params(self):
    index_params = []
    if isinstance(self.rh, Parameter):
      if self.op == EQ:
        index_params.append(self.rh)
      elif self.op in [LT, LE]:
        index_params.append((type_min_value(get_query_field(self.rh).get_type()), self.rh))
      elif self.op in [GT, GE]:
        index_params.append((self.rh, type_max_value(get_query_field(self.rh).get_type())))
    elif isinstance(self.rh, MultiParam):
      assert(len(self.rh.params)==2)
      index_params.append((self.rh.params[0], self.rh.params[1]))
    return index_params
  def complete_field(self, table):
    self.lh.complete_field(table)
    self.rh.complete_field(table)
    if isinstance(self.rh, MultiParam):
      for x in self.rh.params:
        x.tipe = self.lh.get_type()
    elif isinstance(self.rh, Parameter):
      self.rh.tipe = self.lh.get_type()
  def __str__(self):
    return "({} {} {})".format(self.lh, pred_op_to_cpp_map[self.op], self.rh)
  def __hash__(self):
    return hash(str(self))
  def __eq__(self, other):
    return str(self) == str(other)
  def split(self):
    return [self]
  def split_into_dnf(self):
    return [self]
  def get_reverse(self):
    if isinstance(self.lh, MultiParam):
      return ConnectOp(BinOp(self.lh, LE, self.rh.params[0]), OR, BinOp(self.lh, GE, self.rh.params[1]))
    else:
      return BinOp(self.lh, reversed_op[self.op], self.rh)
  def contain_exist_forall(self):
    if isinstance(self.lh, AssocOp):
      return True
    elif isinstance(self.rh, AssocOp):
      return True
    return False
  def idx_pred_eq(self, other):
    return type(self) == type(other) and self.lh.idx_pred_eq(other.lh) and self.rh.idx_pred_eq(other.rh)
  def query_pred_eq(self, other):
    return type(self) == type(other) and self.op == other.op and self.lh.query_pred_eq(other.lh) and self.rh.query_pred_eq(other.rh)
  def template_eq(self, other):
    basic_eq = type(self) == type(other) and self.lh.template_eq(other.lh) and self.rh.template_eq(other.rh)
    op_eq = (self.op in [LE, LT, GE, GT, BETWEEN] and other.op in [LE, LT, GE, GT, BETWEEN]) or \
        (self.op in [EQ, NEQ, IN] and other.op in [EQ, NEQ, IN]) or (self.op == SUBSTR and other.op == SUBSTR)
    return basic_eq and op_eq
  def get_cnf_literal(self):
    return [self]
  def get_dnf_literal(self):
    return [self]
  def get_curlevel_fields(self, include_assoc=False):
    if isinstance(self.lh, AssocOp) or isinstance(self.lh, QueryField):
      lh = self.lh.get_curlevel_fields(include_assoc)
    else:
      lh = []
    if isinstance(self.rh, AssocOp) or isinstance(self.rh, QueryField):
      rh = self.rh.get_curlevel_fields(include_assoc)
    else:
      rh = []
    return lh + rh
  def to_json(self):
    return '{} {} {}'.format(self.lh.to_json(), pred_op_to_cpp_map[self.op], self.rh.to_json())
  
class ConnectOp(BinOp):
  def __init__(self, lh, op, rh):
    #lh/rh: BinOp
    self.lh = lh
    self.rh = rh
    self.op = op #op can only be AND, OR
  def get_necessary_index_keys(self):
    return self.lh.get_necessary_index_keys() + self.rh.get_necessary_index_keys()
  def complete_field(self, table):
    self.lh.complete_field(table)
    self.rh.complete_field(table)
  def get_necessary_index_params(self):
    return self.lh.get_necessary_index_params() + self.rh.get_necessary_index_params()
  def has_param(self):
    return self.lh.has_param() or self.rh.has_param()
  def get_all_params(self):
    return self.lh.get_all_params() + self.rh.get_all_params()
  def get_all_assocs(self):
    return self.lh.get_all_assocs() + self.rh.get_all_assocs()
  def contain_exist_forall(self):
    return self.lh.contain_exist_forall() or self.rh.contain_exist_forall()
  def __str__(self):
    return "({} {} {})".format(self.lh, pred_op_to_cpp_map[self.op], self.rh)
  def __hash__(self):
    return hash(str(self))
  def __eq__(self, other):
    return str(self) == str(other)
  def split(self):
    if self.op == AND:
      if any([self.query_pred_eq(pred) for pred in globalv.pred_scope]):
        return [self]
      return self.lh.split() + self.rh.split()
    else:
      return [self]
  def split_into_dnf(self):
    if self.op == AND:
      return [self]
    else:
      return self.lh.split_into_dnf() + self.rh.split_into_dnf()
  def get_reverse(self):
    return ConnectOp(self.lh.get_reverse(), reversed_op[self.op], self.rh.get_reverse())
  def get_cnf_literal(self):
    if self.op == AND:
      return self.lh.get_cnf_literal() + self.rh.get_cnf_literal()
    else:
      return [self]
  def get_dnf_literal(self):
    if self.op == OR:
      return self.lh.get_dnf_literal() + self.rh.get_dnf_literal()
    else:
      return [self]
  def get_curlevel_fields(self, include_assoc=False):
    if isinstance(self.lh, BinOp):
      lh = self.lh.get_curlevel_fields(include_assoc)
    else:
      lh = []
    if isinstance(self.rh, BinOp):
      rh = self.rh.get_curlevel_fields(include_assoc)
    else:
      rh = []
    return lh + rh
  def idx_pred_eq(self, other):
    return type(self) == type(other) and self.some_pred_eq(other, idx=True)
  def query_pred_eq(self, other):
    return type(self) == type(other) and self.some_pred_eq(other, idx=False)
  def template_eq(self, other):
    return type(self) == type(other) and self.op == other.op and \
          self.lh.template_eq(other.lh) and self.rh.template_eq(other.rh)
  def some_pred_eq(self, other, idx=False):
    cmp_func = lambda x, y: x.idx_pred_eq(y)
    if idx == False:
      cmp_func = lambda x, y: x.query_pred_eq(y)
    if self.op != other.op:
      return False
    if self.op == AND:
      cnf_literals = self.get_cnf_literal()
      cnf_literals_other = other.get_cnf_literal()
      r = True
      for c in cnf_literals:
        exist = any([cmp_func(c, co) for co in cnf_literals_other])
        if exist == False:
          r = False
      for co in cnf_literals_other:
        exist = any([cmp_func(c, co) for c in cnf_literals])
        if exist == False:
          r = False
      return r
    else: 
      dnf_literals = self.get_dnf_literal()
      dnf_literals_other = other.get_dnf_literal()
      for d in dnf_literals:
        exist = any([cmp_func(d, do) for do in dnf_literals_other])
        if exist == False:
          return False
      for do in dnf_literals_other:
        exist = any([cmp_func(d, do) for d in dnf_literals])
        if exist == False:
          return False
    return True
  def to_json(self):
    return '({}) {} ({})'.format(self.lh.to_json(), pred_op_to_cpp_map[self.op], self.rh.to_json())


def is_query_field(f, include_assoc=True):
  if isinstance(f, QueryField):
    return True
  if include_assoc and is_assoc_field(f):
    return True
  return False
def is_assoc_field(pred):
  return isinstance(pred, AssocOp)
def is_atomic_field(f):
  if isinstance(f, QueryField):
    if isinstance(f.field_class, Field):
      return True
    else:
      return False
  elif isinstance(f, AssocOp):
    return is_atomic_field(f.rh)
def is_singlelevel_atomic_field(f):
  if isinstance(f, QueryField):
    if isinstance(f.field_class, Field):
      return True
    else:
      return False
  elif isinstance(f, AssocOp):
    return False
def get_query_field(f):
  if isinstance(f, QueryField):
    return f
  elif isinstance(f, AssocOp):
    return get_query_field(f.rh)
def get_query_table(f):
  if isinstance(f, QueryField):
    return f.table
  elif isinstance(f, AssocOp):
    return get_query_table(f.lh)
