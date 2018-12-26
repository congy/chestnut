import sys
sys.path.append('../')
from codegen_helper import *
from schema import *
from ds import *

def cgen_ds_def(ds, upper_table=None, prefix=[]):
  header = ''
  cpp = ''
  #value type def
  if ds.value.is_aggr():
    value_type_name = ds.get_value_type_name()
    structs = 'struct {} {{\n'.format(value_type_name)
    structs += ''.join(['  {} {}_{};\n'.format(get_cpp_type(x[0].get_type()), x[0].name, i) for i,x in enumerate(idx.value.value.aggrs)])
    structs += '  {}(): {} {{}}\n'.format(value_type_name, ','.join(['{}_{}(0)'.format(x[0].name, i) for i,x in enumerate(idx.value.value.aggrs)]))
    structs += '  inline bool operator==(const {}& other) const {{ return {}; }}\n'.format(value_type_name, \
          '&&'.join(['{}_{} == other.{}_{}'.format(x[0].name, i, x[0].name, i) for i,x in enumerate(idx.value.value.aggrs)]))
    # a false comparator, will never be used
    structs += '  inline bool operator<(const {}& other) const {{ return true; }}\n'.format(value_type_name)
    structs += '};\n'
    header += structs
  elif ds.value.is_main_ptr():
    pass
  else:
    nheader, ncpp = cgen_class_def(ds.value.get_object(), upper_table, prefix)
    header += nheader
    cpp += ncpp

  #key type def and ds declaration
  ds_name = ds.get_ds_name()
  if isinstance(ds, ObjBasicArray) or len(ds.key_fields()) == 0:
    if ds.value.is_aggr() or (isinstance(ds, ObjBasicArray) and ds.is_single_element()):
      ds_def = "{} {};\n".format(ds.get_value_type_name(), ds_name)
    else:
      ds_def = "{}<{}, {}> {};\n".format(cgen_ds_type(ds), \
                                            ds.get_value_type_name(), \
                                            int(to_real_value(ds.compute_single_size())), \
                                            ds_name)
  else:
    key_type_name = ds.get_key_type_name()
    key_fields = [key for key in ds.key_fields()]
    structs = "struct  {} {{\n".format(key_type_name)
    structs += ''.join(["  {} {};\n".format(cgen_scalar_ftype(key), cgen_fname(key)) for i,key in enumerate(key_fields)])
    #init function
    structs += "  {}({}): {} {{}}\n".format(key_type_name, \
                            ','.join(['{} {}_'.format(cgen_scalar_ftype(key), cgen_fname(key)) for i,key in enumerate(key_fields)]), \
                            ','.join(['{}({}_)'.format(cgen_fname(key), cgen_fname(key)) for i,key in enumerate(key_fields)]))
    structs += "  {}(): {} {{}}\n".format(key_type_name, \
                            ','.join(['{}(0)'.format(cgen_fname(key)) for i,key in enumerate(key_fields)]))
    #equality checker
    structs += "  inline bool operator==(const {}& other) const {{ return {}; }}\n".format(key_type_name,\
                                      '&&'.join(['({} == other.{})'.format(cgen_fname(key), cgen_fname(key)) for i,key in enumerate(key_fields)]))
    #comparator 
    cmp_str = "false"
    tmp = "true"
    for i,key in enumerate(key_fields):
      cmp_str += " || ({} && {} < other.{})".format(tmp, cgen_fname(key), cgen_fname(key))
      tmp = tmp + "&& {} == other.{}".format(cgen_fname(key), cgen_fname(key))
    structs += "  inline bool operator<(const {}& other) const {{ return {}; }}\n".format(key_type_name, cmp_str)
    shift_bits = int(32/len(ds.key_fields()))
    structs += "  inline size_t get_hash() const {{ return {}; }}\n".format(' + '.join(['{}'.format(\
                          "{}_{}.get_hash() << {}".format(cgen_fname(key), i, i*shift_bits) \
                          if is_string_type(key.get_query_field().field_class.tipe) else \
                          "(std::hash<{}>()({}) << {})".format(\
                          cgen_scalar_ftype(key), cgen_fname(key), i*shift_bits)) for i,key in enumerate(key_fields)]))                                        
    structs += "};\n"

    ds_def = "{}<{}, {}, {}> {};\n".format(cgen_ds_type(ds), \
                                              key_type_name, \
                                              ds.get_value_type_name(), \
                                              int(to_real_value(ds.compute_single_size())), \
                                              ds_name)   

    header += structs
  if not isinstance(ds.table, NestedTable):
    cpp += ds_def
    header += 'extern {}'.format(ds_def)
  else:
    header += ds_def

  if isinstance(ds.table, DenormalizedTable):
    tables = ds.table.tables
    entryt = ds.table.get_main_table()
    proto_toptype_prefixes = ['{}::P{}'.format(get_db_name(), get_capitalized_name(get_main_table(t1).name)) for t1 in tables] 
  else:
    tables = [ds.table]
    entryt = get_main_table(ds.table)
    proto_toptype_prefixes = ['{}::P{}'.format(get_db_name(), get_capitalized_name(get_main_table(entryt).name))]
  
  for ix in range(0, len(tables)):
    t = tables[ix]
    proto_toptype_prefix = proto_toptype_prefixes[ix]

    # insert by key
    if isinstance(ds, ObjBasicArray) or len(ds.key_fields()) == 0:
      insert_func = 'inline size_t insert_{}_by_key({}& v) {{\n'.format(ds_name, ds.get_value_type_name())
      if ds.value.is_aggr():
        assert(False)
      elif isinstance(ds, ObjBasicArray) and ds.is_single_element():
        insert_func += '  {} = v;\n'.format(ds_name)
        insert_func += '  size_t insertpos = 0;\n'
      else:
        insert_func += '  size_t insertpos = {}.insert(v);\n'.format(ds_name)
    else:
      insert_func = 'inline size_t insert_{}_by_key({}& key, {}& v) {{\n'.format(ds_name, ds.get_key_type_name(), ds.get_value_type_name())
      if ds.value.is_aggr():
        assert(False)
      else:
        insert_func += '  size_t insertpos = {}.insert_by_key(key, v);\n'.format(ds_name)
    if ds.is_refered:
      assert(ds.value.is_object())
      insert_func += '  if (!invalid_pos(insertpos)) {}.insert_by_key(v.{}, insertpos);\n'.format(cgen_getpointer_helperds(ds), cgen_fname(QueryField('id',entryt)))
    insert_func += '}\n'
    header += insert_func

    """
    # get keys func
    getkey_func = "inline void get_keys_for_{} (const {}& p, TempArray<{}>& keys) {{\n".format(ds_name, \
                                                            proto_toptype_prefix, ds.get_key_type_name())
    for i,key in enumerate(ds.key_fields()):
      getkey_func += "  TempArray<{}> key_{};\n".format(cgen_scalar_ftype(key), cgen_fname(key))
    getkey_func += insert_indent(codegen_getkeys_recursive(ds.condition, 'p', key_to_id_map, 1, ds.table, t))
    level = 1
    key_to_var_map = {}
    for i,key in enumerate(ds.key_fields()):
      indent = ''.join(['  ' for i in range(0, level)])
      getkey_func += "{}for(auto i{} = key_{}.begin(); i{} != key_{}.end(); i{}++) {{\n".format(indent, \
                                          level, cgen_fname(key), level, cgen_fname(key), level)
      key_to_var_map[key] = '(*i{})'.format(level)
      level += 1
    indent = ''.join(['  ' for i in range(0, level)])
    # check condition
    if isinstance(ds, ObjBasicArray):
      getkey_func += "{}keys.append(1);\n".format(indent)
    else:
      getkey_func += "{}//check key sat for each key combination\n".format(indent)
      getkey_func += "{}bool sat_condition=false;\n".format(indent)
      checksat_code = codegen_checksat_recursive(idx.condition, 'p', 'sat_condition', key_to_var_map, 1, ds.table, t)
      for x in range(0, level):
        checksat_code = insert_indent(checksat_code)
      getkey_func += checksat_code
      getkey_func += "{}if (sat_condition) {{\n".format(indent)
      if len(ds.key_fields()) > 0:
        getkey_func += "{}  {} temp_key({});\n".format(indent, ds.get_key_type_name(), ','.join(['(*i{})'.format(i) for i in range(1, len(ds.key_fields())+1)]))
      else:
        getkey_func += "{}  oid_t temp_key = 1;\n".format(indent)
      getkey_func += "{}  keys.append(temp_key);\n".format(indent)
      getkey_func += "{}}}\n".format(indent)
    while level > 1:
      level -= 1
      indent = ''.join(['  ' for i in range(0, level)])
      getkey_func += "{}}}\n".format(indent)
    getkey_func += "  return ;\n"
    getkey_func += "}\n"
    header += (getkey_func + '\n')

    # insert and delete
    insert_func = 'inline void insert_into_{}(const {}&p, const ItemPointer& pos) {{\n'.format(ds_name, proto_toptype_prefix)
    delete_func = 'inline void delete_from_{}(const {}&p, const ItemPointer& pos) {{\n'.format(ds_name, proto_toptype_prefix)
    func_body = "  TempArray<{}> keys;\n".format(ds.get_key_type_name())
    if ds.value.is_main_ptr():
      func_body += '  if (pos.is_valid() == false) return; \n'
    func_body += "  get_keys_for_{}(p, keys);\n".format(ds_name)
    if ds.value.is_aggr():
      # TODO
      for i,x in enumerate(idx.value.value.aggrs):
        v,aggr = x
        if len(idx.key_fields()) > 0:
          func_body += "  for (auto i = keys.begin(); i != keys.end(); i++) {\n"
          func_body += "    auto x = {}.find_by_key(*i);\n".format(ds_name)
          func_body += "    if (x!=nullptr) {{\n      PLACEHOLDER;\n    }}\n"
          init_v = '(*x).{}_{}'.format(v.name, i)
          func_body += "  }\n"
          helper_s, expr_s = cgen_expr_from_protov(aggr, init_v, 'p')
          insert_func += func_body.replace('PLACEHOLDER', helper_s+expr_s)
          helper_s, expr_s = cgen_expr_from_protov(idx.value.value.delta_exprs[i], init_v, 'p')
          delete_func += func_body.replace('PLACEHOLDER', (helper_s + '{} = {};\n'.format(init_v, expr_s)))
        else:
          init_v = '{}.{}_{}'.format(ds_name, v.name, i)
          helper_s, expr_s = cgen_expr_from_protov(aggr, init_v, 'p')
          insert_func += (helper_s + expr_s)
          helper_s, expr_s = cgen_expr_from_protov(idx.value.value.delta_exprs[i], init_v, 'p')
          delete_func += (helper_s + '{} = {};\n'.format(init_v, expr_s))
    else:
      if len(ds.key_fields()) > 0:
        func_body += "  for (auto i = keys.begin(); i != keys.end(); i++) {\n" 
        func_body += "    {}.PLACEHOLDER((*i), pos);\n".format(ds_name)
        func_body += "  }\n"
      else:
        func_body += "  if (keys.size() > 0) {\n"
        func_body += "      {}.PLACEHOLDER(pos);\n".format(ds_name)
        func_body += "  }\n"
      insert_func += (func_body.replace('PLACEHOLDER', 'insert'))
      delete_func += (func_body.replace('PLACEHOLDER', 'remove'))
    insert_func += '}\n'
    delete_func += '}\n'

    header += (insert_func + '\n')
    header += (delete_func + '\n')
    """

  if isinstance(ds.table, NestedTable):
    header = insert_indent(header)  
  return header,cpp

def cgen_class_def(obj, upper_table=None, prefix=[]): 
  header = ""
  cpp = ""
  t = obj.table
  main_t = get_main_table(t)
  element = ''
  ele_name = obj.get_value_type_name()
  element += "struct {} {{\n".format(ele_name)
  element += "public:\n"
  fields = [f for f in obj.fields]
  for f in fields:
    element += "  {} {};\n".format(cgen_scalar_ftype(f), cgen_fname(f))

  for ds in obj.nested_objects:
    new_prefix = [p for p in prefix] + [ele_name]
    next_header, next_cpp = cgen_ds_def(ds, t, new_prefix)
    element += insert_indent(next_header)
    cpp += next_cpp

  db_name = get_db_name()
  prefix.append(ele_name)
  idx_type_prefix = '::'.join([p for p in prefix]) # ??

  element += "  {}(): {} {{}}\n".format(ele_name, ','.join(['{}(0)'.format(cgen_fname(f)) for f in fields]))
  element += "  {}({}): {} {{}}\n".format(ele_name, \
      ','.join(['{} v{}'.format(get_cpp_type(f.field_class.tipe), i) for i,f in enumerate(fields)]), \
      ','.join(['{}(v{})'.format(cgen_fname(f), i) for i,f in enumerate(fields)]))
  if isinstance(obj.table, DenormalizedTable):
    t1 = obj.table.get_main_table()
    proto_type_prefix = '{}::P{}'.format(db_name, get_capitalized_name(t1.name))
    element += cgen_init_from_proto(ele_name, t1, proto_type_prefix, fields)
  else:
    proto_type_prefix = db_name + ''.join(['::P{}'.format(p) for p in prefix])
    proto_toptype_prefix = '{}::P{}'.format(db_name, get_capitalized_name(main_t.name))
    element += cgen_init_from_proto(ele_name, main_t, proto_type_prefix, fields)
    if upper_table:
      element += cgen_init_from_proto(ele_name, main_t, proto_toptype_prefix, fields)
  
  id_fields = filter(lambda x: x.field_name=='id', fields)
  element += "  inline void clear() {{ {} }}\n".format(' '.join(['{} = 0;'.format(cgen_fname(idf)) for idf in id_fields]))
  element += "  inline bool operator==(const {}& other) const {{ return {}; }}\n".format(ele_name, '&&'.join(['{}==other.{}'.format(cgen_fname(idf),cgen_fname(idf)) for idf in id_fields]))
    #element += "  inline bool operator<(const {}& other) const {{ return id < other.id; }}\n".format(ele_name)

  print_func = "  void print() {\n"
  print_fields = [cgen_fprint(f) for f in fields]
  print_func += "    printf(\"[{}:{}]\\n\", {});\n".format(t.name, ', '.join([x[0] for x in print_fields]), ', '.join([x[1] for x in print_fields]))
  print_func += "  }\n"
  element += print_func

  element += "};\n"
  header += element

  return header, cpp

def codegen_getkeys_recursive(pred, proto_vname, level, maint=None, curt=None):
  s = ""
  if is_type_or_subtype(pred, ConnectOp):
    s += codegen_getkeys_recursive(pred.lh, proto_vname, level+1, maint, curt)
    s += codegen_getkeys_recursive(pred.rh, proto_vname, level+1, maint, curt)
  elif is_type_or_subtype(pred, SetOp):
    proto_lh = proto_vname+'.'+cgen_get_fproto(pred.lh)
    s += "for (int j{} = 0; j{} < {}_size(); j{}++) {{\n".format(level, level, proto_lh[:-2], level)
    t = get_query_field(pred.lh).table
    new_proto_vname = '({}(j{}))'.format(get_pred_lh_str, level)
    inner_s = codegen_getkeys_recursive(pred.rh, new_proto_vname, level+1)
    s += insert_indent(inner_s)
    s += "}\n"
  elif isinstance(pred.rh, Parameter) and (not isinstance(pred.rh, MultiParam)):
    keyname = cgen_fname(pred)
    if curt and not get_table_from_pred(pred.lh).name == curt.name:
      qf = maint.get_qf_by_tables(curt, get_table_from_pred(pred.lh))
      pred = merge_assoc_qf(qf, pred.lh)
    s += "key_{}.append({});\n".format(keyname, proto_vname+'.'+cgen_get_fproto(pred.lh))  
  return s

def codegen_checksat_recursive(pred, proto_vname, condition_var, key_to_var_map, level, maint=None, curt=None):
  s = ""
  if isinstance(pred, ConnectOp):
    if condition_var:
      lh_var_name = get_predvar_name("b_lh")
      rh_var_name = get_predvar_name("b_rh")
      s += "bool {} = false;\n".format(lh_var_name)
      s += "bool {} = false;\n".format(rh_var_name)
      s += codegen_checksat_recursive(pred.lh, proto_vname, lh_var_name, key_to_var_map, level, maint, curt)
      s += codegen_checksat_recursive(pred.rh, proto_vname, rh_var_name, key_to_var_map, level, maint, curt)
      s += "{} = {} {} {};\n".format(condition_var, lh_var_name, get_pred_op_to_cpp_map(pred.op), rh_var_name)

  elif isinstance(pred, SetOp):
    proto_lh = proto_vname+'.'+cgen_get_fproto(pred.lh)
    s += "for (int j{} = 0; j{} < {}_size(); j{}++) {{\n".format(level, level, proto_lh[:-2], level)
    new_cond_var = "temp_b_{}".format(level)
    inner_s = ''
    if pred.op == EXIST:
      inner_s += "bool {} = false;\n".format(new_cond_var)
    elif pred.op == FORALL:
      inner_s += "bool {} = true;\n".format(new_cond_var)
    new_proto_vname = 'p{}'.format(get_query_field(pred.lh).field_name)
    inner_s += "const auto& {} = {}(j{});\n".format(new_proto_vname, get_pred_lh_str, level)
    inner_s += codegen_checksat_recursive(pred.rh, new_proto_vname, new_cond_var, key_to_var_map, level+1)
    if pred.op == EXIST:
      inner_s += "if ({}) {} = true;\n".format(new_cond_var, condition_var)
    elif pred.op == FORALL:
      inner_s += "if (!{}) {} = false;\n".format(new_cond_var, condition_var)
    s += insert_indent(inner_s)
    s += '}\n'
 
  elif isinstance(pred, BinOp):
    if isinstance(pred.rh, Parameter) and (not isinstance(pred.rh, MultiParam)): # pred.lh is key
      pred_rh = key_to_var_map[pred.lh]
      s += "{} = ({} {} {});\n".format(condition_var, key_to_var_map[pred.lh], get_pred_op_to_cpp_map(pred.op), pred_rh)
    else:
      if curt and not get_table_from_pred(pred.lh) == curt:
        qf = maint.get_qf_by_tables(curt, get_table_from_pred(pred.lh))
        pred_lh = proto_vname+'.'+cgen_get_fproto(merge_assoc_qf(qf, pred.lh))
      else:
        pred_lh = proto_vname+'.'+cgen_get_fproto(pred.lh)
      if is_query_field(pred.rh):
        if curt and is_query_field(pred.rh) and not get_table_from_pred(pred.rh) == curt:
          qf = maint.get_qf_by_tables(curt, get_table_from_pred(pred.rh))
          pred_rh = proto_vname+'.'+cgen_get_fproto(merge_assoc_qf(qf, pred.rh))
        else:
          pred_rh = proto_vname+'.'+cgen_get_fproto(pred.rh)
      elif isinstance(pred.rh, MultiParam):
        pred_rh = [key_to_var_map[pred.lh] if isinstance(p, Parameter) else p.to_var_or_value() for p in pred.rh.params]
      else: # pred.rh is constant
        pred_rh = '\"{}\"'.format(pred.rh.to_var_or_value()) if is_string_type(pred.lh.get_type())  else pred.rh.to_var_or_value()
      if pred.op == SUBSTR:
        s += "{} = ({}.find_first_of({}.c_str())!=std::string::npos);\n".format(condition_var, pred_lh, pred_rh)
      elif pred.op == IN or pred.op == BETWEEN:
        s += '{} = {};\n'.format(condition_var, '||'.join(['({} == {})'.format(pred_lh, x)  for x in pred_rh]))
      else:
        s += "{} = ({} {} {});\n".format(condition_var, pred_lh, get_pred_op_to_cpp_map(pred.op), pred_rh)

  return s