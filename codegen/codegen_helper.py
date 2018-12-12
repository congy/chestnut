import sys
sys.path.append('../')
from constants import *
from schema import *
from pred import *
from ds import *

def cgen_fname(f):
  if isinstance(f, QueryField):
    return '{}_{}'.format(f.table.name, f.field_name)
  elif isinstance(f, AssocOp):
    lst = get_assoc_field_list(f)
    s = '_'.join([f1.field_name for f1 in lst])
  elif isinstance(f, Field):
    return '{}_{}'.format(f.table.name, f.name)

def cgen_scalar_ftype(f):
  if isinstance(f, QueryField):
    return get_cpp_type(f.field_class.tipe)
  elif isinstance(f, Field):
    return get_cpp_type(f.tipe)
def cgen_obj_fulltype(table):
  if isinstance(table, NestedTable):
    return cgen_obj_fulltype(table.upper_table) + \
      '::{}In{}'.format(get_capitalized_name(table.name), get_capitalized_name(get_main_table(table.upper_table).name))
  else:
    return '{}'.format(get_capitalized_name(table.name))

def cgen_proto_type(t):
  if isinstance(t, NestedTable):
    r = ''
    while isinstance(t, NestedTable):
      r = '::P{}In{}'.format(get_capitalized_name(t.name),get_capitalized_name(get_main_table(t.upper_table).name)) + r
      t = t.upper_table
    r = '{}::P{}{}'.format(get_db_name(), get_capitalized_name(t.name), r)
    return r
  else:
    assert(not isinstance(t, DenormalizedTable))
    return '{}::P{}'.format(get_db_name(), get_capitalized_name(t.name))
def cgen_get_fproto(f):
  if isinstance(f, QueryField):
    return '{}()'.format(f.field_name)
  elif isinstance(f, AssocOp):
    lst = get_assoc_field_list(f)
    s = []
    for qf in lst:
      if qf.table.has_one_or_many_field(qf.field_name) == 1:
        s.append('{}()'.format(qf.field_name))
      else:
        s.append('{}(0)'.format(qf.field_name))
    return '.'.join([s1 for s1 in s])
  elif isinstance(f, Field):
    return '{}()'.format(f.name)

def cgen_fprint(f):
  if isinstance(f, QueryField):
    f.field_class.table = f.table
    f = f.field_class
  if is_int(f) or is_bool(f):
    return "{}=%d".format(f.name), cgen_fname(f)
  elif is_unsigned_int(f):
    return "{}=%u".format(f.name), cgen_fname(f)
  elif is_float(f):
    return "{}=%f".format(f.name), cgen_fname(f)
  elif is_string(f):
   return '{}=%s'.format(f.name), '{}.s'.format(cgen_fname(f)) if is_varchar(f) else '{}.s.c_str()'.format(cgen_fname(f))
  else:
    assert(False)

def cgen_ds_type(idx):
  if isinstance(idx, ObjBasicArray):
    if idx.is_single_element():
      qf = get_qf_from_nested_t(idx.table)
      return '{}In{}'.format(get_capitalized_name(qf.field_name), get_capitalized_name(qf.table.name))
    sz = to_real_value(idx.element_count())
    if sz < SMALL_DT_BOUND: 
      return 'SmallBasicArray'
    else:
      return 'BasicArray'
  elif isinstance(idx, IndexBase):
    prefix = ''
    if to_real_value(idx.element_count()) < SMALL_DT_BOUND:
      prefix='Small'
    if isinstance(idx, ObjTreeIndex):
      return '{}TreeIndex'.format(prefix)
    elif isinstance(idx, ObjSortedArray):
      return '{}SortedArray'.format(prefix)
    elif isinstance(idx, ObjHashIndex):
      return '{}HashIndex'.format(prefix)
    elif isinstance(idx, ObjArray):
      return '{}ObjArray'.format(prefix)
  assert(False)

def cgen_getpointer_helperds(ds):
  return 'idptr_ds_{}'.format(ds.id)

def merge_assoc_qf(assoc, qf):
  if isinstance(assoc, QueryField):
    return AssocOp(assoc, qf)
  elif isinstance(assoc, AssocOp):
    return AssocOp(assoc.lh, merge_assoc_qf(assoc.rh, qf))
  else:
    assert(False)

def merge_qf_assoc(qf, assoc):
  pass

var_suffix_cnt = 0
def get_random_suffix():
  global var_suffix_cnt
  var_suffix_cnt += 1
  return '{}'.format(var_suffix_cnt)

cxxvar_cnt = 0
def cgen_cxxvar(v):
  global cxxvar_cnt
  cxxvar_cnt += 1
  if isinstance(v, EnvAtomicVariable):
    return 'e_{}_{}'.format(v.name, cxxvar_cnt)
  elif isinstance(v, EnvCollectionVariable):
    return 'lst_{}_{}'.format(v.name, cxxvar_cnt)
  elif isinstance(v, Table):
    return 'obj_{}_{}'.format(v.name, cxxvar_cnt)
  elif is_query_field(v):
    return 'qf_{}_{}'.format(get_query_field(v).field_name, cxxvar_cnt)
  else:
    if type(v) is str:
      return 'v_{}_{}'.format(v, cxxvar_cnt)
    else:
      return 'v_{}'.format(cxxvar_cnt)

def cgen_init_from_proto(typename, table, proto, fields):
  if isinstance(table, DenormalizedTable):
    s = []
    maint = table.get_main_table()
    vs = {maint:'p'}
    for t in table.tables:
      var = vs[t]
      fs = filter(lambda x: x.table == t, fields)
      s.append(','.join(['{}({}.{}())'.format(cgen_fname(f), var, f.name) for f in fields]))
      for k,v in t.nested_tables.items():
        if t.has_one_or_many_field(k) == 1:
          vs[get_main_table(v)] = '{}.{}()'.format(var, k)
        else:
          vs[get_main_table(v)] = '{}.{}(0)'.format(var, k)
    return "  {}(const {}& p): {} {{}}\n".format(typename, proto, ','.join(s))
  else:
    return "  {}(const {}& p): {} {{}}\n".format(typename, proto, \
                                ','.join(['{}(p.{}())'.format(cgen_fname(f), f.field_name) for f in fields]))


def cgen_expr_from_protov(expr, init_var, proto_var):
  if isinstance(expr, BinaryExpr):
    s1, lh = cgen_expr_from_protov(expr.lh, init_var, proto_var)
    s2, rh = cgen_expr_from_protov(expr.rh, init_var, proto_var)
    if type_larger(expr.lh.get_type(), expr.rh.get_type()):
      rh = '({}){}'.format(get_cpp_type(expr.lh.get_type()), rh)
    if type_larger(expr.rh.get_type(), expr.lh.get_type()):
      lh = '({}){}'.format(get_cpp_type(expr.rh.get_type()), lh)
    return s1+s2, '({} {} {})'.format(lh, expr_op_to_cpp_map[expr.op], rh)
  elif isinstance(expr, UnaryExpr):
    if expr.op == COUNT:
      opd = ''
      s = ''
    else:
      s, opd = cgen_expr_from_protov(expr.operand, init_var, proto_var)
    if expr.op == MAX:
      return s, 'if ({}<{}) {} = {};\n'.format(init_var, opd, init_var, opd)
    elif expr.op == MIN:
      return s, 'if ({}>{}) {} = {};\n'.format(init_var, opd, init_var, opd)
    elif expr.op == COUNT:
      return s, '{}++;\n'.format(init_var)
    elif expr.op == SUM:
      return s, '{} = {} + {};\n'.format(init_var, init_var, opd)
    elif expr.op == AVG:
      return s, ''
    else:
      assert(False)
  elif isinstance(expr, IfThenElseExpr):
    s1, cond = cgen_expr_from_protov(expr.cond, init_var, proto_var)
    s2, expr1 = cgen_expr_from_protov(expr.expr1, init_var, proto_var)
    s3, expr2 = cgen_expr_from_protov(expr.expr2, init_var, proto_var)
    newv = 'tempv_{}'.format(hash(expr)%10)
    s = '{} {} = 0;\n'.format(get_cpp_type(expr.expr1.get_type()), newv)
    s += 'if ({}) {} = {};\nelse {} = {};\n'.format(cond, newv, expr1, newv, expr2)
    return s1+s2+s3+s, newv
  elif isinstance(expr, QueryField):
    return '', '{}.{}()'.format(proto_var, expr.field_name)
  elif isinstance(expr, Parameter) or isinstance(expr, EnvAtomicVariable):
    assert(False)
    return '', ''
  elif isinstance(expr, EnvAtomicVariable):
    return '', state.find_cxx_var(expr)
  elif isinstance(expr, AssocOp):
    s, rh = cgen_expr_from_protov(expr.rh, init_var, '{}.{}()'.format(proto_var, expr.lh.field_name))
    return s, rh
  elif isinstance(expr, AtomValue):
    return '', str(int(expr.to_var_or_value()))
  elif isinstance(expr, InitialValuePlaceholder):
    return '', init_var
  else:
    assert(False)

