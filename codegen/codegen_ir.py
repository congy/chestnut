import sys
sys.path.append('../')
from ds import *
from planIR import *
from codegen_helper import *
from codegen_state import *
from codegen_client import *
import globalv

def cgen_for_read_query(qid, query, plan, dsmnger, plan_id):
  state = CodegenState()
  state.topquery = query
  state.dsmnger = dsmnger
  params = query.get_all_params()
  param_var_map = {}
  param_str = []
  header = ""
  code = ""
  
  print '\nread plan:'
  print plan
  for i,p in enumerate(params):
    param_str.append("{} param_{}_{}".format(get_cpp_type(p.tipe), p.symbol, i))
    param_var_map[p] = "param_{}_{}".format(p.symbol, i)
  state.param_map = param_var_map

  param_str.append('{}& qresult'.format(cgen_query_result_type(query)))

  if not globalv.is_qr_type_proto():
    header += cgen_nonproto_query_result(query)

  code += ''.join(['// '+l+'\n' for l in str(plan).split('\n')])
  header += "\nvoid query_{}_plan_{}({});\n".format(qid, plan_id, ', '.join(param_str))
  code += "\nvoid query_{}_plan_{}({}) {{\n".format(qid, plan_id, ', '.join(param_str))
  code += "  char msg[] = \"query {} plan {} run time \";\n".format(qid, plan_id)
  code += "  get_time_start();\n"

  code_s, new_state = cgen_for_one_step(plan, state, print_result=True)
  code += insert_indent(code_s)
  
  code += "}\n\n"

  return header,code

def cgen_for_one_step(step, state, print_result=False):
  s = ''
  if isinstance(step, ExecQueryStep):
    state.qr_var = 'qresult'
    next_s, temp_state = cgen_for_one_step(step.step, state)
    s += insert_indent(next_s)
    for v,aggr in state.topquery.aggrs:
      irvar = state.find_ir_var(v)
      s += '  qresult.set_{}({});\n'.format(v.name, irvar)
    s += "  print_time_diff(msg);\n"
    if print_result:
      if not globalv.is_qr_type_proto():
        s += cgen_print_query_result(step.query)
    return s, state

  elif isinstance(step, ExecSetVarStep):
    # var = pred / aggr / append()
    expr_s = ''
    if isinstance(step.var, EnvAtomicVariable):
      if not state.exist_ir_var(step.var):
        ir_var = state.find_or_create_ir_var(step.var)
        s += '{} {};\n'.format(get_cpp_type(step.var.get_type()), ir_var)
      else:
        ir_var = state.find_ir_var(step.var)
      inits, expr_s = cgen_expr_with_placeholder(step.expr, state, ir_var) if step.expr else ('','')
      if step.expr and (not is_aggr_expr(step.expr)):
        expr_s = '{} = {};'.format(ir_var, expr_s)
      s += inits
    elif isinstance(step.var, EnvCollectionVariable):
      ele_name = cgen_cxxvar(step.var, True)
      state.qr_var = '(*{})'.format(ele_name)
      s += '{}* {};\n'.format(cgen_query_result_var_type(step.var.tipe, state.topquery), ele_name)
      expr_s = cgen_add_to_qresult(step.var, ele_name, step.projections, state)
    if step.cond:
      dummp,cond_s = cgen_expr_with_placeholder(step.cond, state)
    else:
      cond_s = 'true'
    s += 'if ({}) {{ {} }}\n'.format(cond_s, expr_s)
    return s, state

  elif isinstance(step, ExecStepSeq):
    next_state = state.fork()
    for nested_step in step.steps:
      inner_s, next_state = cgen_for_one_step(nested_step, next_state)
      state.merge(next_state)
      s += inner_s
    return s, state

  elif isinstance(step, ExecScanStep):
    new_state = state.add_nextscope_state(step)
    if step.idx.value.is_aggr():
      # TODO
      assert(False)
    ds_name = step.idx.get_ds_name()
    type_prefix = '{}::'.format(step.idx.table.upper_table.get_full_type()) if isinstance(step.idx.table, NestedTable) else ''
    idx_prefix = '{}.'.format(state.loop_var) if isinstance(step.idx.table, NestedTable) else ''
    ary_name = '{}{}'.format(idx_prefix, ds_name)
    ary_ele_name = cgen_cxxvar(step.idx.table)
    if (not isinstance(step, ExecIndexStep)) or len(step.idx.key_fields())==0:
      if step.idx.is_single_element():
        s += 'auto& {} = {};\n'.format(ary_ele_name, ary_name)
      else:
        s += get_loop_define(step.idx) + \
          '({}_{}, {}, {})\n'.format(ds_name, get_random_suffix(), ary_name, ary_ele_name)
    else:
      keys = []
      for i,p in enumerate(step.params):
        key_name, init_str = get_param_str(new_state, p, i)
        s += '{}{} {};\n'.format(type_prefix, step.idx.get_key_type_name(), init_str)
        keys.append(key_name)
      params_str = ', '.join(['&{}'.format(k) for k in keys])
      s += get_loop_define(step.idx, is_range=(step.op.is_range())) + \
            '({}_{}, {}, {}, {})\n'.format(ds_name, get_random_suffix(), params_str, ary_name, ary_ele_name)

    init_obj_str, cxxobj = get_obj_from_value_type(step.idx, ary_ele_name, state.dsmnger)
    new_state.loop_var = cxxobj
    s += insert_indent(init_obj_str)
    next_s, temp_state = cgen_for_one_step(step.ele_ops, new_state)
    s += insert_indent(next_s)
    if not step.idx.is_single_element():
      s += get_loop_define(step.idx, is_begin=False) + '\n'
    return s, state

  elif isinstance(step, ExecGetAssocStep):
    irvar = state.find_or_create_ir_var(step.var)
    if step.idx is None:
      assert(is_atomic_field(step.field))
      s += '{} {} = {}.{};\n'.format(get_cpp_type(step.field.get_type()), irvar, state.loop_var, cgen_fname(step.field))
      return s, state
    new_state = state.add_nextscope_state(step)
    if isinstance(step.idx, ObjTreeIndex):
      topds = state.dsmnger.find_primary_array(get_main_table(step.idx.table))
      tempv = cgen_cxxvar('ptrv')
      fk_id = cgen_fname(QueryField('id', get_main_table(state.ds.table)))
      s += 'auto {} = {}.find_by_key({}.{});\n'.format(tempv, step.idx.get_ds_name(), state.loop_var, fk_id)
      s += 'if ({} == nullptr) continue;\n'.format(tempv)
      s += 'auto ptr_{} = ({}.get_ptr_by_pos({}->pos));\n'.format(irvar, topds.get_ds_name(), tempv)
      s += 'if (ptr_{} == nullptr) continue;\n'.format(irvar)
      s += 'auto& {} = *ptr_{};\n'.format(irvar, irvar)
    else:
      curobj = '{}.{}'.format(state.loop_var, step.field.field_name)
      if step.idx.value.is_object():
        s += 'auto& {} = {};\n'.format(irvar, curobj)
      else:
        getobj_s, vname = get_obj_from_value_type(step.idx, curobj, state.dsmnger, irvar)
        s += getobj_s
    new_state.loop_var = irvar
    return s, new_state

  elif isinstance(step, ExecSortStep):
    if globalv.is_qr_type_proto():
      proto_type = cgen_proto_type(step.var.tipe)
      cmp_func = '[](const {}& a, const {}& b){{\n\treturn '.format(proto_type, proto_type)
      cmp_func += "(a.{}() < b.{}())".format(step.order[0].field_name, step.order[0].field_name)
      cmp_accu = "a.{}() == b.{}()".format(step.order[0].field_name, step.order[0].field_name)
      for f in step.order[1:]:
        cmp_func += " || ({} && a.{}() < b.{}())".format(cmp_accu, f.field_name, f.field_name)
        cmp_accu += " && a.{}() == b.{}()".format(f.field_name, f.field_name)
      cmp_func += '; }'
      s += "std::sort({}.mutable_{}()->begin(),\n".format(state.ir_var, step.var.tipe.name)
      s += "         {}.mutable_{}()->end(),\n".format(state.ir_var, step.var.tipe.name)
      s += "         {});\n".format(cmp_func)
    else:
      s += '{}.sort_{}();\n'.format(state.ir_var, step.var.tipe.name)
    return s, state

  elif isinstance(step, ExecUnionStep):
    assert(False)

def cgen_add_to_qresult(qr_array, ele_name, fields, state):
  s = ''
  upper_qrvar = state.upper.qr_var
  irvar = state.loop_var
  table = qr_array.tipe
  if isinstance(table, NestedTable) and get_main_table(table.upper_table).has_one_or_many_field(table.name) == 1:
    s += '{} = {}.mutable_{}();\n'.format(ele_name, upper_qrvar, table.name)
  else:
    s += '{} = {}.add_{}();\n'.format(ele_name, upper_qrvar, table.name) 
  for f in fields:
    if type(f) is not tuple:
      if is_string(f.field_class):
        s += '{}->set_{}({}.{}.c_str());\n'.format(ele_name, f.field_name, irvar, cgen_fname(f))
      else:
        s += '{}->set_{}({}.{});\n'.format(ele_name, f.field_name, irvar, cgen_fname(f))
    else:
      vpair = f
      cxx_var = state.find_ir_var(vpair[0])
      if not vpair[0].is_temp:
        s += '{}->set_{}({});\n'.format(ele_name, vpair[0].name, get_aggr_result(vpair, cxx_var, state))
  if qr_array.limit > 0 and state.order_maintained(qr_array):
    s += 'if ({}.{}_size() > {}) break;\n'.format(upper_irvar, qr_array.tipe.name, qr_array.limit)
  return s

def get_obj_from_value_type(idx, ary_ele_name, dsmnger, cxxobj=None):
  s = ''
  if idx.value.is_object():  
    return s, ary_ele_name
  if idx.value.is_main_ptr():
    topds = dsmnger.find_primary_array(get_main_table(idx.table))
    if cxxobj is None:
      cxxobj= cgen_cxxvar(idx.table)
    s += 'auto ptr_{} = ({}.get_ptr_by_pos({}.pos));\n'.format(cxxobj, topds.get_ds_name(), ary_ele_name)
    s += 'if (ptr_{} == nullptr) continue;\n'.format(cxxobj)
    s += 'auto& {} = *ptr_{};\n'.format(cxxobj, cxxobj)
    return s, cxxobj
  else:
    assert(False)

def get_param_str(state, param, paramid=0):
  ds = state.ds
  key_name = cgen_cxxvar('{}_key{}'.format(state.ds.get_ds_name(), paramid))
  pstrs = []
  for i in range(0, len(param.params)):
    p = param.params[i]
    if isinstance(p, Parameter):
      pstrs.append(state.param_map[p])
    elif isinstance(p, AtomValue):
      pstrs.append(str(p.to_var_or_value()))
    elif isinstance(p, QueryField):
      pstrs.append(state.upper.get_queryfield_var(p))
    else:
      assert(False)
  return key_name, '{}({})'.format(key_name, ','.join([s for s in pstrs]))