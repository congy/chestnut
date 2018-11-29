import sys
sys.path.append('../')
from schema import *
from ds import *
from query import *
from codegen_template import *
from codegen_helper import *
from codegen_ds import *

def cgen_init_ds(data_file_dir, tables, associations, dsmeta):
  db_name = get_db_name()
  header = "#ifndef __{}_H_\n".format(db_name.upper())
  header += "#define __{}_H_\n".format(db_name.upper())
  header += includes
  header += "\n#define DATA_DIR \"{}\"\n\n".format(data_file_dir)
  cpp = "#include \"{}.h\"\n".format(db_name)
  header += "#include \"proto_{}.pb.h\"\n".format(db_name)
  header += '\n'.join(['// '+l for l in str(struct_pool).split('\n')])

  for t in tables:
    header += "struct {};\n".format(get_capitalized_name(t.name))

  for ds in dsmeta.data_structures:
    def_header, def_cpp = cgen_ds_def(ds, None, [])
    header += def_header 
    cpp += def_cpp
  
  t_header, t_cpp = cgen_read_data_general(tables, associations)
  header += t_header
  cpp += t_cpp

  t_header, t_cpp = codegen_read_data_tables(tables, associations, struct_pool)
  header += t_header
  cpp += t_cpp

  header += "#endif // __{}_H_\n".format(db_name.upper())
  return header, cpp

def cgen_read_data_general(tables, associations):
  header = "void read_tables(); \n"
  code = ""

  for a in get_assoc_tables(associations):
    code += "std::vector<std::vector<size_t>> temp_{}_{};\n".format(a.lft.name, a.lft_field_name)
    code += "std::vector<std::vector<size_t>> temp_{}_{};\n".format(a.rgt.name, a.rgt_field_name)
  for a in get_one_to_many_relations(associations):
    code += "std::vector<std::vector<size_t>> temp_{}_{};\n".format(a.lft.name, a.lft_field_name)

  code += "void read_tables() {\n"
  #code += "  init_random_gen();\n"
  code += "  //read tables\n"
  code += "  char msg[] = \"data structure loading time \";\n"
  code += "  get_time_start();\n"

  for i,t in enumerate(tables):
    if t.is_temp == False:
      code += "  read_{}_table();\n".format(t.name)
  for i,t in enumerate(tables):
    if t.is_temp:
      code += "fill_{}_table();\n".format(t.name)

  code += "  print_time_diff(msg);\n"
  code += "  std::this_thread::sleep_for(std::chrono::seconds(10));\n"
  code += "}\n"

  return header, code

def codegen_read_data_tables(tables, associations, dsmeta):
  header = ""
  cpp = ""

  # define macros
  for a in associations:
    qf_lft = QueryField(a.lft_field_name, a.lft)
    qf_rgt = QueryField(a.rgt_field_name, a.rgt)
    header += codegen_scanassoc_routine_macro(qf_lft, struct_pool)
    header += codegen_scanassoc_routine_macro(qf_rgt, struct_pool)
  
  # read tables
  for t in tables:
    id_idx = dsmeta.find_id_idx(create_new=True)
    assert(id_idx)
    objstruct = struct_pool.get_obj(t)
    basic_ary = 
    # two helper functions
    # get_{}_obj_ptr_by_id()
    # get_{}_obj_pos_by_id()
    helper1 = '{}* get_{}_obj_ptr_by_id(size_t id) {{\n'.format(get_capitalized_name(t.name), t.name)
    header += '{}* get_{}_obj_ptr_by_id(size_t id); \n'.format(get_capitalized_name(t.name), t.name)
    helper1 += "  ItemPointer* pos = {}.find_by_key(id);\n".format(id_idx.get_idx_name())
    helper1 += "  if (pos == nullptr) return nullptr;\n"
    helper1 += "  return {}.get_ptr_by_pos(pos->pos);\n".format(basic_ary.get_idx_name())
    helper1 += "}\n"
    helper2 = 'size_t get_{}_obj_pos_by_id(size_t id) {{\n'.format(t.name)
    header += 'size_t get_{}_obj_pos_by_id(size_t id); \n'.format(t.name)
    helper2 += "  ItemPointer* pos = {}.find_by_key(id);\n".format(id_idx.get_idx_name())
    helper2 += "  if (pos == nullptr) return INVALID_POS;\n"
    helper2 += "  return pos->pos;\n"
    helper2 += "}\n"
    
    if t.is_temp: 
      cpp += helper1
      cpp += helper2
      continue
    
    table_name = t.name
    table_cap = get_capitalized_name(table_name) 
    code = "void read_{}_table() {{\n".format(t.name)
    header +=  "void read_{}_table();\n".format(t.name)
    column_cnt = 0
    var_name = 'v_{}'.format(table_name)
    init_code = "{} {};  ".format(get_capitalized_name(t.name), var_name)
    readline_code = ''
    for i,c in enumerate([f.name for f in t.get_fields()]):
      if i == 0:
        readline_code += "      if"
        readline_code += " (i=={}) {{ // {}\n".format(i, c)
        readline_code += "        {}.{} = str_to_uint(content);\n".format(var_name, c)
        column_cnt += 1
      elif is_original_table_field(t, c):
        readline_code += "      }else if"
        readline_code += " (i=={}) {{ // {}\n".format(i, c)
        f = t.get_field_by_name(c)
        if is_date(f):
          readline_code += "        {}.{} = time_to_uint(content);\n".format(var_name, c)
        elif is_unsigned_int(f) or is_bool(f):
          readline_code += "        {}.{} = str_to_uint(content);\n".format(var_name, c)
        elif is_int(f):
          readline_code += "        {}.{} = str_to_int(content);\n".format(var_name, c)
        elif is_float(f):
          readline_code += "        {}.{} = str_to_float(content);\n".format(var_name, c)
        elif is_string(f):
          readline_code += "        {}.{} = content;\n".format(var_name, c)
        else:
          assert(False)
        column_cnt += 1
    readline_code += "      }\n"
    
    insert_code = "size_t pos = {}.insert({});\n".format(basic_ary.get_idx_name(), var_name)
    insert_code += "{}.insert_by_key({}({}.id), ItemPointer(pos));\n".format(id_idx.get_idx_name(), id_idx.get_key_type_name(), var_name)

    for a in get_one_to_many_relations(associations):
      if a.rgt == t and (a.lft.is_temp == False):
        # fill one_to_many assoc array
        insert_code += 'if ({}.{}_id < {}) temp_{}_{}[{}.{}_id].push_back({}.id);\n'.format(\
                var_name, a.rgt_field_name, a.lft.sz+1, a.lft.name, a.lft_field_name, var_name, a.rgt_field_name, var_name)
        # insert_code += 'for (size_t i0=0; i0<{}; i0++) {{\n'.format(a.lft_ratio)
        # ary_idx = 'temp_{}_{}[{}.{}_id][i0]'.format(a.lft.name, a.lft_field_name, var_name, a.rgt_field_name)
        # insert_code += '  if ({} == 0) {{\n'.format(ary_idx)
        # insert_code += '    {} = {}.id;\n'.format(ary_idx, var_name)
        # insert_code += '    break;\n'
        # insert_code += '  }\n'
        # insert_code += '}\n'

    code += fill_template_head(table_name, init_code, column_cnt)
    code += "\n"
    code += readline_code
    code += fill_template_end(column_cnt-1, insert_indent(insert_code, indent_level=2))
    cpp += code

    cpp += helper1
    cpp += helper2