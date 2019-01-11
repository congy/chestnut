import sys
sys.path.append('../')
from constants import *
from schema import *
from pred import *
from expr import *
from ds import *

def cgen_fname(f):
  if isinstance(f, QueryField):
    return '{}_{}'.format(f.table.name, f.field_name)
  elif isinstance(f, AssocOp):
    lst = get_assoc_field_list(f)
    s = '_'.join([f1.field_name for f1 in lst])
    return s
  elif isinstance(f, KeyPath):
    return cgen_fname(f.key)
  elif isinstance(f, Field):
    return '{}_{}'.format(f.table.name, f.name)
  elif isinstance(f, EnvAtomicVariable):
    return f.name
  else:
    print f
    assert(False)

def cgen_scalar_ftype(f):
  if isinstance(f, QueryField):
    return get_cpp_type(f.field_class.tipe)
  elif isinstance(f, KeyPath):
    return cgen_scalar_ftype(get_query_field(f.key))
  elif isinstance(f, Field):
    return get_cpp_type(f.tipe)

def cgen_obj_fulltype(ds):
  if isinstance(ds.table, NestedTable):
    return cgen_obj_fulltype(ds.upper) + \
      '::{}'.format(ds.get_value_type_name())
  else:
    return '{}'.format(ds.get_value_type_name())

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
  elif isinstance(f, KeyPath):
    assert(False)

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

def get_ds_type_prefix(idx):
  if isinstance(idx.table, NestedTable):
    assert(idx.upper)
    return get_ds_type_prefix(idx.upper) + '{}::'.format(idx.upper.get_value_type_name())
  else:
    return ''
def cgen_ds_type(idx):
  sz = to_real_value(idx.compute_single_size())
  if isinstance(idx, ObjBasicArray):
    if idx.is_single_element():
      return ''
      #qf = get_qf_from_nested_t(idx.table)
      #return '{}In{}'.format(get_capitalized_name(qf.field_name), get_capitalized_name(qf.table.name))
    if sz < SMALL_DT_BOUND: 
      return 'SmallBasicArray'
    else:
      return 'BasicArray'
  elif isinstance(idx, IndexBase):
    prefix = ''
    if sz < SMALL_DT_BOUND:
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

def get_loop_define(idx, is_begin=True, is_range=False):
  range_for = 'RANGE_' if is_range else 'INDEX_'
  suffix = 'BEGIN' if is_begin else 'END\n'
  if isinstance(idx, ObjBasicArray):
    if isinstance(idx.table, NestedTable) and get_main_table(idx.table.upper_table).has_one_or_many_field(idx.table.name) == 1:
      return 'SINGLE_ELEMENT_FOR_{}'.format(suffix) 
    sz = to_real_value(idx.compute_single_size())
    if sz < SMALL_DT_BOUND:
      return 'SMALLBASICARRAY_FOR_{}'.format(suffix)
    else:
      return 'BASICARRAY_FOR_{}'.format(suffix)
  elif isinstance(idx, IndexBase):
    if to_real_value(idx.compute_single_size()) < SMALL_DT_BOUND:
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


def cgen_getpointer_helperds(ds):
  return 'idptr_ds_{}'.format(ds.id)

def cgen_query_result_type(qid):
  if globalv.is_qr_type_proto():
    return '{}::PQuery{}Result'.format(get_db_name(), qid)
  else:
    return 'Query{}Result'.format(qid)
def cgen_query_result_var_type(table, qid):
  if isinstance(table, NestedTable):
    return cgen_query_result_var_type(table.upper_table, qid)+\
      '::P{}In{}'.format(get_capitalized_name(table.name), get_capitalized_name(get_main_table(table.upper_table).name))
  else:
    return cgen_query_result_type(qid)+'::P{}'.format(get_capitalized_name(table.name))

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
def cgen_cxxvar(v, is_element=False):
  global cxxvar_cnt
  cxxvar_cnt += 1
  if isinstance(v, EnvAtomicVariable):
    return 'e_{}_{}'.format(v.name, cxxvar_cnt)
  elif isinstance(v, EnvCollectionVariable):
    if is_element:
      return 'ele_{}_{}'.format(v.name, cxxvar_cnt)
    else:
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
    return '', state.find_ir_var(expr)
  elif isinstance(expr, AssocOp):
    s, rh = cgen_expr_from_protov(expr.rh, init_var, '{}.{}()'.format(proto_var, expr.lh.field_name))
    return s, rh
  elif isinstance(expr, AtomValue):
    return '', str(int(expr.to_var_or_value()))
  elif isinstance(expr, InitialValuePlaceholder):
    return '', init_var
  else:
    assert(False)

def is_aggr_expr(expr):
  return isinstance(expr, UnaryExpr)

def cgen_expr_with_placeholder(expr, state, init_var=None):
  if isinstance(expr, ConnectOp):
    dummy, lh_s = cgen_expr_with_placeholder(expr.lh, state, init_var)
    dummy, rh_s = cgen_expr_with_placeholder(expr.rh, state, init_var)
    return '','({} {} {})'.format(lh_s, get_pred_op_to_cpp_map(expr.op), rh_s)
  elif isinstance(expr, BinOp):
    dummy, lh_s = cgen_expr_with_placeholder(expr.lh, state, init_var)
    dummy, rh_s = cgen_expr_with_placeholder(expr.rh, state, init_var)
    if expr.op == BETWEEN:
      return '',"(({} > {}) && ({} < {}))".format(lh_s, rh_s[0], lh_s, rh_s[1])
    elif expr.op == IN:
      return '','({})'.format(' || '.join(['({} == {})'.format(lh_s, rh_s[i]) for i in range(0, len(rh_s))]))
    elif expr.op == SUBSTR:
      return '','({}.find({})!=std::string::npos)'.format(lh_s, rh_s)
    else:
      return '','({} {} {})'.format(lh_s, get_pred_op_to_cpp_map(expr.op), rh_s)
  elif isinstance(expr, UnaryOp):
    dummy,s = cgen_expr_with_placeholder(expr.operand, state, init_var)
    return '','!({})'.format(s)
  elif isinstance(expr, SetOp):
    assert(False)
  elif isinstance(expr, AssocOp):
    assert(False)
    #return state.find_cxx_var(expr)
  elif isinstance(expr, QueryField):
    return '',state.get_queryfield_var(expr)
  elif isinstance(expr, Parameter):
    if isinstance(expr, MultiParam):
      return '',[cgen_expr_with_placeholder(p, state)[1] for p in expr.params]
    else:
      return '',state.find_param_var(expr)
  elif isinstance(expr, EnvAtomicVariable):
    return '',state.find_ir_var(expr)
  elif isinstance(expr, AtomValue):
    if is_string_type(expr.get_type()):
      return '',expr.to_var_or_value()
    else:
      return '',str(int(expr.to_var_or_value()))
  elif isinstance(expr, BinaryExpr):
    s1, lh = cgen_expr_with_placeholder(expr.lh, state, init_var)
    s2, rh = cgen_expr_with_placeholder(expr.rh, state, init_var)
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
      s, opd = cgen_expr_with_placeholder(expr.operand, state, init_var)
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
    s1, cond = cgen_expr_with_placeholder(expr.cond, state, init_var)
    s2, expr1 = cgen_expr_with_placeholder(expr.expr1, state, init_var)
    s3, expr2 = cgen_expr_with_placeholder(expr.expr2, state, init_var)
    newv = get_cxxvar_name('temp')
    s = '{} {} = 0;\n'.format(get_cpp_type(expr.expr1.get_type()), newv)
    s += 'if ({}) {} = {};\nelse {} = {};\n'.format(cond, newv, expr1, newv, expr2)
    return s1+s2+s3+s, newv
  else:
    assert(False)

# deal with avg
def get_aggr_result(vpair, cxx_var, state):
  if not vpair[1].op == AVG:
    return cxx_var
  sum_v = None
  count_v = None
  for k,v in state.ir_map.items():
    if k == vpair[0].sum_var:
      sum_v = v
    if k == vpair[0].count_var:
      count_v = v
  assert(sum_v and count_v)
  return 'float({}) / float({})'.format(sum_v, count_v)

def cgen_print_query_result(query):
  fields = {}
  s = ''
  for v,f in query.aggrs:
    if v.is_temp == False:
      fields[v] = type_to_print_symbol[v.tipe]
  if len(fields) > 0:
    s += "  printf(\"aggrs: {}\\n\", {});\n".format(', '.join(['{} = {}'.format(k.name, v) for k,v in fields.items()]),\
                  ','.join(['qresult.{}()'.format(k.name) for k,v in fields.items()]))
  if query.return_var:
    return_cxx_var = 'qresult.{}'.format(query.table.name)
    s += "  printf(\"sz = %u\\n\", {}.size());\n".format(return_cxx_var)
    s += "  size_t cnt_{} = 0;\n".format(query.table.name)
    s += "  for (auto i = {}.begin(); i != {}.end(); i++) {{\n".format(return_cxx_var, return_cxx_var)
    s += '  cnt_{} ++;\n'.format(query.table.name)
    s += '  if (cnt_{} > 20) break;\n'.format(query.table.name)
    s += insert_indent(cgen_print_query_result_helper(query, '(*i)'))
    s += "  }\n"
  return s

def cgen_print_query_result_helper(query, element_var, level=1):
  s = ''
  fields = [f1.field_class for f1 in query.projections]
  for k,q in query.includes.items(): 
    for v,f in q.aggrs:
      if v.is_temp == False:
        fields.append(v)
  if len(fields) > 0:
    s += "  printf(\"{}{}\\n\", {});\n".format(''.join(['\t' for i in range(0, level)]), ', '.join(['{} = {}'.format(f.name, get_type_to_print_symbol(f.tipe)) for f in fields]),\
                        ','.join(['{}.{}().c_str()'.format(element_var, f.name) if is_string_type(f.tipe) \
                              else '{}.{}()'.format(element_var, f.name) for f in fields]))
  # FIXME
  for k,v in query.includes.items():
    if v.return_var:
      if k.table.has_one_or_many_field(k.field_name):
        next_element_var = 'element_{}'.format(k.field_name)
        s += '  auto& {} = {}.{};\n'.format(next_element_var, element_var, k.field_name)
        s += insert_indent(cgen_print_query_result_helper(v, next_element_var, level+1))
      else:
        s += '  printf("sz = %u\\n", {}.{}_size());\n'.format(element_var, k.field_name)
        next_counter = 'i_{}'.format(k.field_name)
        s += '  for (size_t {} = 0; {} != {}.{}_size(); {}++) {{\n'.format(next_counter,\
            next_counter, element_var, k.field_name, next_counter)
        next_element_var = 'element_{}'.format(k.field_name)
        s += '      auto& {} = {}.{}[{}];\n'.format(next_element_var, element_var, k.field_name, next_counter)
        s += insert_indent(cgen_print_query_result_helper(v, next_element_var, level+1))
        s += '  }\n'
  return s             

def get_param_str_for_main(param_values, params):
  param_str = []
  for p in params:
    if p.tipe == 'date':
      param_str.append('time_to_uint(std::string("{}"))'.format(param_values[p]))
    elif is_string_type(p.tipe):
      param_str.append('\"{}\"'.format(param_values[p]))
    else:
      param_str.append(str(param_values[p]))
  return ','.join(param_str)
