import sys
sys.path.append('../')
import random
from schema import *
from pred import *
from pred_helper import *
from nesting import *
from ds import *
from codegen_helper import *
from query_manager import *

# FIXME: currently we do not deal with NULL value:
# if key is (f1, f2), then (v1, NULL) will not be considered as a valid key 
#     i.e., any object with such key (v1, NULL), (NULL, v2), etc., will not be inserted into the data structure

def clean_sql_query(s):
  return s.replace('"', "'")
def get_path_prefix_helper(qf):
  if isinstance(qf, AssocOp):
    return [qf.lh] + get_path_prefix_helper(qf.rh)
  else:
    return [qf]
def get_path_prefix(path, name):
  fullpath = []
  for p in path:
    fullpath += get_path_prefix_helper(p)
  fullname = [x.table.name for x in fullpath]
  fullname.append(name)
  return '_'.join(fullname)
def get_field_with_prefix(f, connect='.'):
  path = [f1 for f1 in f.path]
  if isinstance(f.key, AssocOp):
    path += get_fields_from_assocop(f.key)[:-1]
  return get_path_prefix(path, get_query_field(f.key).table.name) + connect + get_query_field(f.key).field_name

def sql_for_ds_query(ds, select_by_id=False):
  table = ds.table
  join_strs = []
  if isinstance(table, NestedTable):
    upper_table = get_main_table(table.upper_table)
    upper_qf = get_reversed_assoc_qf(get_qf_from_nested_t(table))
    join_strs.append(get_join_condition([], upper_qf, 'INNER JOIN'))
    pred_strs = ['{}.id = %u'.format(get_path_prefix([upper_qf], upper_qf.field_class.name))]
    #pred_strs = ['{}.id = {}'.format(get_path_prefix([upper_qf], upper_qf.field_class.name), random.randint(1, upper_table.sz-2))]
  else:
    pred_strs = []
  entry_table = get_main_table(table).name
  if ds.value.is_object():
    fields = [KeyPath(f) for f in ds.value.get_object().fields] #[f for f in ds.value.get_object().fields]
  else:
    fields = []
  if not isinstance(ds, ObjBasicArray):
    for f in ds.key_fields():
      insert_no_duplicate(fields, f)
  if isinstance(table, DenormalizedTable):
    maint = table.get_main_table()
    entry_table = maint.name
    nesting = ObjNesting(maint)
    nesting_map = {maint:nesting} # key: table; value: nesting
    for qf in table.join_fields:
      insert_no_duplicate(join_strs, get_join_condition(qf, 'INNER JOIN'))
      if qf.field_class not in nesting_map:
        qfn = nesting_map[qf.table].get_or_add_assoc(qf)
        nesting_map[qf.field_class] = qfn
    for t in table.tables:
      insert_no_duplicate(fields, KeyPath(QueryField('id', t)))
    if select_by_id:
      pred_strs += ['{}.id = %u'.format(t.name) for t in table.tables]
  else:
    maint = get_main_table(table)
    nesting = ObjNesting(maint)
    insert_no_duplicate(fields, KeyPath(QueryField('id', maint)))
    if select_by_id:
      pred_strs.append('{}.id = %u'.format(maint.name))
  if isinstance(ds, ObjBasicArray):
    pred = None
  else:
    pred = ds.condition
  if pred:
    sql_for_ds_pred([], pred, fields, nesting, join_strs, pred_strs)
    #field_str = ','.join(['{}.{} as {}_{}'.format(f.table.name, f.field_name, f.table.name, f.field_name) for f in fields])
    renamed = []
    filtered_fields = []
    for f in fields:
      rename = get_field_with_prefix(f,'_')
      if rename not in renamed:
        renamed.append(rename)
        filtered_fields.append(f)
    field_str = ','.join(['{} as {}'.format(get_field_with_prefix(f), get_field_with_prefix(f,'_')) for f in filtered_fields])
    group_str = ','.join([get_field_with_prefix(f, '_') for f in filtered_fields])
    tableids = []
    for f in filtered_fields:
      if get_query_field(f.key).field_name == 'id':
        insert_no_duplicate(tableids, f)
    order_str = ','.join([get_field_with_prefix(f, '_') for f in tableids])
    s = 'select {} from {} as {} {} {} group by {} order by {}'.format(field_str, to_plural(entry_table), entry_table, ' '.join(join_strs), \
                    ' where '+' and '.join(pred_strs) if len(pred_strs) > 0 else '', group_str, order_str)
  else:
    #field_str = ','.join(['{}.{} as {}_{}'.format(f.table.name, f.field_name, f.table.name, f.field_name) for f in fields])
    field_str = ','.join([get_field_with_prefix(f) for f in fields])
    s = 'select {} from {} as {} {} {}'.format(field_str, to_plural(entry_table), entry_table, \
                    ' '.join(join_strs), ' where '+' and '.join(pred_strs) if len(pred_strs) > 0 else '')

  print "ds = {}, fields = {}".format(ds, ','.join(['{}({})'.format(str(f), f.__class__.__name__) for f in fields]))
  return clean_sql_query(s), nesting, fields

def find_nesting_until_match(nesting, table):
  if nesting.table == table:
    return nesting
  for qf,assoc in nesting.assocs.items():
    n = find_nesting_until_match(assoc, table)
    if n:
      return n
  return None
def find_nesting_by_qf(nesting, qf):
  if isinstance(qf, AssocOp):
    next_nesting = find_nesting_by_qf(nesting, qf.lh)
    return find_nesting_by_qf(next_nesting, qf.rh)
  else:
    if qf.table == nesting.table:
      if is_atomic_field(qf):
        return nesting
      else:
        return nesting.get_or_add_assoc(qf)
    else:
      return find_nesting_until_match(nesting, qf.table)
def sql_get_element_str(path, pred, fields, nesting, join_strs):
  if isinstance(pred, QueryField):
    if is_atomic_field(pred):
      insert_no_duplicate(fields, KeyPath(QueryField('id', pred.table), path))
      insert_no_duplicate(fields, KeyPath(pred, path))
      return get_path_prefix(path, pred.table.name) + '.' + pred.field_name
    else:
      insert_no_duplicate(join_strs, get_join_condition(path, pred, 'INNER JOIN'))
      return ''
  elif isinstance(pred, AssocOp):
    insert_no_duplicate(join_strs, get_join_condition(path, pred.lh, 'INNER JOIN'))
    #f = get_query_field(pred)
    next_nesting = find_nesting_by_qf(nesting, pred.lh)
    return sql_get_element_str(path+[pred.lh], pred.rh, fields, next_nesting, join_strs)
  elif isinstance(pred, MultiParam):
    return '({})'.format(','.join([sql_get_element_str(path, p, fields, nesting, join_strs) for p in pred.params]))
  elif isinstance(pred, AtomValue):
    return pred.to_var_or_value()
  else:
    assert(False)

# if has parameter --- select that field
# if no parameter --- just predicate
def sql_for_ds_pred(path, pred, fields, nesting, join_strs, pred_strs):
  if isinstance(pred, ConnectOp):
    sql_for_ds_pred(path, pred.lh, fields, nesting, join_strs, pred_strs)
    sql_for_ds_pred(path, pred.rh, fields, nesting, join_strs, pred_strs)
  elif isinstance(pred, BinOp):
    if len(pred.get_all_params()) == 0:
      fork_nesting = nesting.fork()
      lft_str = sql_get_element_str(path, pred.lh, [], fork_nesting, join_strs)
      rgt_str = sql_get_element_str(path, pred.rh, [], fork_nesting, join_strs)
      if pred.op == SUBSTR:
        rgt_str = '%{}'.format(rgt_str[1:-1])
      else:
        pred_strs.append('{} {} {}'.format(lft_str, pred_op_to_sql_map[pred.op], rgt_str))
    else:
      assert(isinstance(pred.rh, Parameter))
      sql_get_element_str(path, pred.lh, fields, nesting, join_strs)
  elif isinstance(pred, SetOp):
    if len(pred.get_all_params()) == 0:
      new_pred_strs = []
      new_join_strs = []
      newpath = path
      if pred.op == EXIST:
        if isinstance(pred.lh, QueryField):
          new_pred = pred.rh
        else:
          lqf = reconstruct_assocop_from_lst(get_fields_from_assocop(pred.lh)[:-1])
          newpath = path + [lqf]
          sql_get_element_str(path, lqf, fields, nesting, join_strs)
          new_pred = pred.rh #SetOp(pred.lh.rh, pred.op, pred.rh)
        joinp = 'INNER JOIN'
      else:
        if isinstance(pred.lh, QueryField):
          new_pred = UnaryOp(pred.rh)
        else: # FIXME
          new_pred = SetOp(pred.lh.rh, pred.op, UnaryOp(pred.rh))
        joinp = 'LEFT OUTER JOIN'
      outer_pred = get_exists_condition_helper(newpath, get_query_field(pred.lh), 'INNER JOIN', new_join_strs)
      inner_table = get_query_field(pred.lh).field_class.name
      subq_prefix = 'select 1 from {} as {}'.format(to_plural(inner_table), inner_table)
      new_pred_strs.append(outer_pred)
      fork_nesting = nesting.fork()
      next_nesting = find_nesting_by_qf(fork_nesting, pred.lh) #find_nesting_by_qf(fork_nesting, lqf)
      sql_for_ds_pred([], new_pred, [], next_nesting, new_join_strs, new_pred_strs)
      if pred.op == EXIST:
        pred_strs.append('exists ({} {} where {})'.format(subq_prefix, ' '.join(new_join_strs), ' and '.join(new_pred_strs)))
      else:
        pred_strs.append('not exists ({} {} where {})'.format(subq_prefix, ' '.join(new_join_strs), ' and '.join(new_pred_strs)))
    else:
      next_nesting = find_nesting_by_qf(nesting, pred.lh)
      insert_no_duplicate(join_strs, get_join_condition(path, pred.lh, 'INNER JOIN'))
      newpath = [p for p in path] + [pred.lh]
      sql_for_ds_pred(newpath, pred.rh, fields, next_nesting, join_strs, pred_strs)
  elif isinstance(pred, UnaryOp):
    if len(pred.operand.get_all_params()) == 0:
      return 'not ({})'.format(sql_for_ds_pred(path, pred.operand, fields, nesting, join_strs, pred_strs))
    else:
      return sql_for_ds_pred(path, pred.operand, fields, nesting, join_strs, pred_strs)

# TODO:
#def sql_for_ds_expr(pred, fields, nesting, join_strs, pred_strs):

def get_join_condition(path, qf, joinq):
  if isinstance(qf, AssocOp):
    return get_join_condition_helper(path, qf.lh, joinq) + get_join_condition(path+[qf.lh], qf.rh, joinq)
  else:
    if is_atomic_field(qf):
      return ''
    return get_join_condition_helper(path, qf, joinq)
  
# return a pair: table_name, join_pred
# used for:
#   -> exists (select 1 from table_name .... where ... and outer_pred)
#   -> inner join table_name on join_pred
def get_join_condition_helper(path, qf, joinq):
  assoc_renamed = get_path_prefix(path+[qf], qf.field_class.name)
  if qf.table.has_one_or_many_field(qf.field_name) == 1:
    return '{} {} as {} ON {}.{}_id = {}.id '.format(\
                  joinq, to_plural(qf.field_class.name), assoc_renamed, \
                  get_path_prefix(path, qf.table.name), qf.field_name, assoc_renamed)
  elif qf.field_class.has_one_or_many_field(get_reversed_assoc_qf(qf).field_name) == 1:
    return '{} {} as {} ON {}.id = {}.{}_id '.format(\
                  joinq, to_plural(qf.field_class.name), assoc_renamed, \
                  get_path_prefix(path, qf.table.name), assoc_renamed, get_reversed_assoc_qf(qf).field_name)
  else:
    assoc = qf.table.get_assoc_by_name(qf.field_name)
    connect_table_name = assoc.name
    connect_table_renamed = get_path_prefix(path+[qf], connect_table_name)
    lft_field = assoc.assoc_f1 if assoc.lft == qf.table else assoc.assoc_f2
    rgt_field = assoc.assoc_f2 if assoc.lft == qf.table else assoc.assoc_f1
    return '{} {} as {} ON {}.id = {}.{} {} {} as {} ON {}.id = {}.{} '.format(\
                  joinq, connect_table_name, connect_table_renamed, \
                  get_path_prefix(path, qf.table.name), connect_table_renamed, lft_field, \
                  joinq, to_plural(qf.field_class.name), get_path_prefix(path+[qf], qf.field_class.name),
                  get_path_prefix(path+[qf], qf.field_class.name), connect_table_renamed, rgt_field)  

def get_exists_condition_helper(outer_path, qf, joinq, join_strs):
  outerid = get_path_prefix(outer_path, qf.table.name)+'.id'
  if qf.field_class.has_one_or_many_field(get_reversed_assoc_qf(qf).field_name) == 1:
    return '{} = {}.{}_id'.format(outerid, qf.field_class.name, get_reversed_assoc_qf(qf).field_name)
  else:
    assoc = qf.table.get_assoc_by_name(qf.field_name)
    connect_table_name = assoc.name
    lft_field = assoc.assoc_f1 if assoc.lft == qf.table else assoc.assoc_f2
    rgt_field = assoc.assoc_f2 if assoc.lft == qf.table else assoc.assoc_f1
    join_str = '{} {} ON {}.id = {}.{} '.format(joinq, connect_table_name, qf.field_class.name, connect_table_name, rgt_field)
    join_strs.append(join_str)
    return '{} = {}.{}'.format(outerid, connect_table_name, lft_field)

def cgen_init_ds_from_sql(ds, nesting, fields, query_str, upper_type=None, select_by_id=False):
  if ds.upper:
    param1 = ', {}* upper_obj'.format(cgen_obj_fulltype(ds.upper)) 
  elif select_by_id:
    param1 = ', size_t oid'
  else:
    param1 = ''
  s = 'inline void init_ds_{}_from_sql(MYSQL* conn{}) {{\n'.format(ds.id, param1)
  ds_name = ds.get_ds_name()
  maint = ds.table.get_main_table() if isinstance(ds.table, DenormalizedTable) else get_main_table(ds.table)
  if isinstance(ds, ObjBasicArray) or len(ds.key_fields()) == 0:
    pass
  else:
    for i,key in enumerate(ds.key_fields()):
      s += '  {} key_{} = 0;\n'.format(get_cpp_type(key.get_query_field().field_class.tipe), i)
  # TODO: replace %d with id using sprintf
  if upper_type:
    s += '  char qs[2000];\n'
    s += '  sprintf(qs, \"{}\", upper_obj->{});\n'.format(query_str, cgen_fname(QueryField('id', get_main_table(upper_type))))
    s += '  std::string query_str(qs);\n'
  elif select_by_id:
    s += '  char qs[2000];\n'
    s += '  sprintf(qs, \"{}\", oid);\n'.format(query_str)
    s += '  std::string query_str(qs);\n'
  else:
    s += '  std::string query_str("{}");\n'.format(query_str)

  s += """
  if (mysql_query(conn, query_str.c_str())) {
    fprintf(stderr, "mysql query failed: %s\\n", query_str.c_str());
    exit(1);
  }
  MYSQL_RES *result = mysql_store_result(conn);
  if (result == NULL) exit(0);
  MYSQL_ROW row;
  row = mysql_fetch_row(result);
  size_t insertpos = 0;
  while (row != NULL) {
"""
  
  ds_name = ds.get_ds_name()
  if ds.value.is_main_ptr():
    dependent_ds = ds.value.value
    id_pos = helper_field_pos_in_row(fields, QueryField('id', get_main_table(ds.table)))
    s += '    size_t* pos = {}.find_by_key(str_to_uint(row[{}]));\n'.format(cgen_getpointer_helperds(dependent_ds), id_pos)
    s += '    ItemPointer ipos(INVALID_POS);\n'
    s += '    if (pos != nullptr) ipos.pos = *pos;\n'
    value_str = 'ipos'
  elif ds.value.is_object():
    obj_fields = ['{}(row[{}])'.format(helper_get_row_type_transform(f), helper_field_pos_in_row(fields, f)) for f in ds.value.get_object().fields]
    s += '    {} value({});\n'.format(cgen_obj_fulltype(ds), ','.join(obj_fields))
    value_str = 'value'
  else:
    assert(False)
  
  if isinstance(ds, ObjBasicArray) or len(ds.key_fields()) == 0:
    key_str = ''
  else:
    for i,key in enumerate(ds.key_fields()):
      rpos = helper_field_pos_in_row(fields, key)
      s += '    key_{} = {}(row[{}]);\n'.format(i, helper_get_row_type_transform(key.get_query_field()), rpos)
    s +='    {}{} key({});\n'.format(cgen_obj_fulltype(ds.upper)+'::' if isinstance(ds.table, NestedTable) else '', ds.get_key_type_name(), \
        ','.join(['key_{}'.format(j) for j in range(0, len(ds.key_fields()))]))
    key_str = 'key,'
  insert_code = '    {}{}insert_{}_by_key({}{});\n'.format('if (pos != nullptr) ' if ds.value.is_main_ptr() else '',\
                  'upper_obj->' if upper_type else '', ds_name, key_str, value_str)
  s += insert_code
  s += '    row = mysql_fetch_row(result);\n'
  s += '  }\n'
  s += '  mysql_free_result(result);\n'
  if upper_type is None and select_by_id:
    ds_sz_100 = int(ds.table.sz / 100)
    s += '  if(oid%{}==0) printf("----ds {} finish %u\\n", oid/{});\n'.format(ds_sz_100, ds.id, ds_sz_100)
  s += '}\n'
  return s

def codegen_deserialize(ds, nesting, fields, query_str):
  table = ds.table
  dsid = ds.id
  if isinstance(table, DenormalizedTable):
    maint = table.get_main_table()
  else:
    maint = get_main_table(table)
  s = 'inline void query_data_for_ds{}(MYSQL* conn, {}::P{}List* ret_objs) {{\n'.format(dsid, get_db_name(), get_capitalized_name(maint.name))
  s += '  std::string query_str("{}");\n'.format(query_str)
  s += """
  if (mysql_query(conn, query_str.c_str())) {
    fprintf(stderr, "mysql query failed\\n");
    exit(1);
  }
  MYSQL_RES *result = mysql_store_result(conn);
  if (result == NULL) exit(0);
  MYSQL_ROW row;
  row = mysql_fetch_row(result);
  while (row != NULL) {
"""
  # int num_fields = mysql_num_fields(result);
  s += insert_indent(codegen_deserialize_helper(get_main_table(table), nesting, fields, 'ret_objs'), 2)
  s += '    row = mysql_fetch_row(result);\n'
  s += '  }\n'
  s += '}\n'
  return s

def codegen_deserialize_helper(table, nesting, fields, upper_var, level=1):
  s = ''
  """
  xx_obj_ptr = nullptr;
  last_xx_id = 0;
  while (true) {{
    if (str_to_uint(row[x]) != last_xx_id || str_to_uint(row[y]) != last_yy_id || ...) {{
      xx_obj_ptr = ??.add_{}();
      xx_obj_ptr->set_**();
      last_xx_id = 
      last_yy_id = 
    }}
    {} // next level
    row = mysql_fetch_row(result);
    if (row == NULL) break;
  }}
  """
  if isinstance(table, DenormalizedTable):
    maint = table.get_main_table()
    nesting_map = {maint:nesting} # key: table; value: nesting
    table_map = {maint:maint}
    for qf in table.join_fields:
      if qf.field_class not in nesting_map:
        qfn = nesting_map[qf.table].get_assoc(qf)
        nesting_map[qf.field_class] = qfn
        table_map[qf.field_class] = table_map[qf.table].get_nested_table_by_name(qf.field_name)
  else:
    table_map = {get_main_table(table):table}
  for k,v in table_map.items():
    s += '{}* {}_obj_ptr_{} = nullptr;\n'.format(cgen_proto_type(v), k.name, level)
    s += 'uint32_t last_{}_id_{} = 0;\n'.format(k.name, level)
  s += 'if ({}) {{\n'.format('||'.join([\
      'str_to_uint(row[{}]) != last_{}_id_{}'.format(helper_field_pos_in_row(fields,QueryField('id',k)), k.name, level) \
        for k,v in table_map.items()]))
  if isinstance(table, DenormalizedTable):
    maint = table.get_main_table()
    s += '  {}_obj_ptr_{} = {}->add_{}();\n'.format(maint.name, level, upper_var, maint.name)
    for qf in table.join_fields:
      if qf.table.has_one_or_many_field(qf.field_name) == 1:
        s += '  {}_obj_ptr_{} = {}_obj_ptr_{}->mutable_{}();\n'.format(qf.field_class.name, level, qf.table.name, level, qf.field_name)
      else: 
        s += '  {}_obj_ptr_{} = {}_obj_ptr_{}->add_{}();\n'.format(qf.field_class.name, level, qf.table.name, level, qf.field_name)
  elif isinstance(table, NestedTable):
    if get_main_table(table.upper_table).has_one_or_many_field(table.name) == 1:
      s += '  {}_obj_ptr_{} = {}->mutable_{}();\n'.format(get_main_table(table).name, level, upper_var, table.name)
    else:
      s += '  {}_obj_ptr_{} = {}->add_{}();\n'.format(get_main_table(table).name, level, upper_var, table.name)
  else:
    s += '  {}_obj_ptr_{} = {}->add_{}();\n'.format(table.name, level, upper_var, table.name)
  for k,v in table_map.items():
    for f,pos in helper_get_table_fields_in_row(fields, k):
      s += '  {}_obj_ptr_{}->set_{}({}(row[{}]));\n'.format(f.table.name, level, f.field_name, helper_get_row_type_transform(f), pos)
  for k,v in table_map.items():
    s += '  last_{}_id_{} = str_to_uint(row[{}]);\n'.format(k.name, level, helper_field_pos_in_row(fields,QueryField('id',k)))
  s += '}\n'

  if isinstance(table, DenormalizedTable):
    maint = table.get_main_table()
    for t in [qf.table for qf in table.join_fields]:
      n = nesting_map[t]
      for next_qf,assoc in n.assocs.items():
        if next_qf.field_class not in nesting_map:
          next_table = next_qf.table.get_nested_table_by_name(next_qf.field_name)
          s += codegen_deserialize_helper(next_table, assoc, fields, upper_var='{}_obj_ptr_{}'.format(next_qf.table.name, level), level=level+1)
  else:
    for qf,assoc in nesting.assocs.items():
      next_table = table.get_nested_table_by_name(qf.field_name)
      s += codegen_deserialize_helper(next_table, assoc, fields, upper_var='{}_obj_ptr_{}'.format(get_main_table(table).name, level), level=level+1)
  
  return s


def helper_field_pos_in_row(fields, field):
  if isinstance(field, QueryField):
    field = KeyPath(field)
  for i,f in enumerate(fields):
    if f == field:
      return i
  assert(False)
def helper_get_table_fields_in_row(fields, table):
  r = []
  for i,f in enumerate(fields):
    if f.key.table == table:
      r.append((f, i))
  return r
def helper_get_row_type_transform(f):
  if isinstance(f, QueryField):
    f = f.field_class
  else:
    f = f.key.field_class
  if is_varchar(f) or is_long_string(f):
    return ''
  elif is_date(f):
    return 'time_to_uint'
  elif is_float(f):
    return 'str_to_float'
  elif is_int(f):
    return 'str_to_int'
  else:
    return 'str_to_uint'

