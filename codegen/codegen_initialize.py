import sys
sys.path.append('../')
from schema import *
from ds import *
from query import *
from .codegen_template import *
from .codegen_helper import *
from .codegen_ds import *
from .codegen_sql import *
from .codegen_main import *
import globalv

def cgen_initialize_all(tables, associations, dsmeta):
  db_name = get_db_name()
  header = "#ifndef __{}_H_\n".format(db_name.upper())
  header += "#define __{}_H_\n".format(db_name.upper())
  header += includes
  cpp = "#include \"{}.h\"\n".format(db_name)
  header += "#include \"proto_{}.pb.h\"\n".format(db_name)

  set_ds_is_refered(dsmeta.data_structures, dsmeta.data_structures)
  dsmeta_str = str(dsmeta)
  header += ''.join(['//'+l+'\n' for l in dsmeta_str.split('\n')])

  for ds in dsmeta.data_structures:
    if ds.is_refered:
      helperds_def = 'TreeIndex<oid_t, size_t, {}> {}'.format(to_real_value(ds.element_count()), cgen_getpointer_helperds(ds))
      header += 'extern {};\n'.format(helperds_def)
      cpp += '{};\n'.format(helperds_def)

  for ds in dsmeta.data_structures:
    def_header, def_cpp = cgen_ds_def(ds, None, [])
    header += def_header 
    cpp += def_cpp
  
  t_header, t_cpp = cgen_read_data_general(tables, associations, dsmeta)
  header += t_header
  cpp += t_cpp

  header += "#endif // __{}_H_\n".format(db_name.upper())
  return header, cpp

def cgen_read_data_general(tables, associations, dsmeta):
  header = "void read_data(); \n"
  code = "void read_data() {\n"
  code += "  char msg[] = \"data structure loading time \";\n"
  code += "  get_time_start();\n"

  code += """
  MYSQL *conn = mysql_init(NULL);
  if (conn == NULL){
    fprintf(stderr, "mysql_init() failed\\n");
    exit(1);
  }
"""
  if globalv.mysql_socket == "":
    code += '  if (mysql_real_connect(conn, "localhost", "root", "", "{}", 0, NULL, 0) == NULL){{\n'.format(get_db_name())
  else:
    code += '  if (mysql_real_connect(conn, "localhost", "root", "", "{}", 0, "{}", 0) == NULL){{\n'.format(get_db_name(), globalv.mysql_socket)
  code += """
    fprintf(stderr, "mysql connect failed\\n");
    exit(1);
  }
"""

  next_header, next_cpp = cgen_init_ds_lst(dsmeta.data_structures)
  header += next_header
  code += ('  size_t cnt;\n' + insert_indent(next_cpp))
  
  code += "  print_time_diff(msg);\n"
  for ds in dsmeta.data_structures:
    code += '  printf("ds {} sz = %d;\\n", {}.size());\n'.format(ds.id, ds.get_ds_name())
  code += "  std::this_thread::sleep_for(std::chrono::seconds(1));\n"
  code += "}\n"

  return header, code
  
def cgen_init_ds_lst(dslst, upper_type=None, upper_v=None):
  header = ''
  cpp = ''
  # s = 'inline void init_ds_from_sql(MYSQL* conn{}{}) {{\n'.format(param1, param2)
  for ds in dslst:
    print('ds = {}'.format(ds))
    select_by_id = (not isinstance(ds.table, NestedTable)) and to_real_value(ds.table.sz) > 100000
    query_str, nesting, fields = sql_for_ds_query(ds, select_by_id)
    header += '//ds {}: {}\n'.format(ds.id, ds.__str__(True))
    header += cgen_init_ds_from_sql(ds, nesting, fields, query_str, upper_type, select_by_id)
  
  s = ''
  if upper_type is None:
    # reorganize ds and generate code to get pointer
    pointed = {}
    for ds in dslst:
      ds_sz = ds.table.sz
      select_by_id = ds_sz > 100000
      if not ds.value.is_main_ptr():
        if select_by_id:
          s += 'for (size_t i=0; i<{}; i++)\n'.format(int(ds_sz))
        s += 'init_ds_{}_from_sql(conn{});\n'.format(ds.id, ', i' if select_by_id else '')
        s += 'printf("finish initialize ds {}\\n");\n'.format(ds.id)
    for ds in dslst:
      ds_sz = ds.table.sz
      select_by_id = ds_sz > 100000
      if ds.value.is_main_ptr():
        if select_by_id:
          s += 'for (size_t i=0; i<{}; i++)\n'.format(int(ds_sz))
        s += 'init_ds_{}_from_sql(conn{});\n'.format(ds.id, ', i' if select_by_id else '')
        s += 'printf("finish initialize ds {}\\n");\n'.format(ds.id)
    s += 'oid_t obj_pos = 0;\n'
  else:
    s += 'init_ds_{}_from_sql(conn, &{});\n'.format(ds.id, upper_v)

  for ds in dslst:
    if ds.value.is_object() and len(ds.value.get_object().nested_objects) > 0:
      array_ele = cgen_cxxvar(ds.table)
      s += 'cnt = 0;\n'
      s += get_loop_define(ds, is_begin=True, is_range=True)
      ds_prefix = '{}.'.format(upper_v) if upper_v else ''
      if isinstance(ds, ObjBasicArray) or len(ds.key_fields()) == 0:
        s += '({}_{}, {}{}, {})\n'.format(ds.get_ds_name(), get_random_suffix(), ds_prefix, ds.get_ds_name(), array_ele)
      else:
        s += '({}_{}, nullptr, nullptr, {}{}, {})\n'.format(ds.get_ds_name(), get_random_suffix(), ds_prefix, ds.get_ds_name(), array_ele)
      next_header, next_cpp = cgen_init_ds_lst(ds.value.get_object().nested_objects, ds.table, array_ele)
      header += next_header
      s += insert_indent(next_cpp)
      ds_sz = ds.table.sz/100
      if not isinstance(ds.table, NestedTable) and ds_sz>100000:
        s += '  cnt++;\n'
        s += '  if (cnt % {} == 0) printf("----ds {} inner finish %u\\n", cnt/{});\n'.format(int(ds_sz/100), ds.id, int(ds_sz)/100)
      s += get_loop_define(ds, is_begin=False, is_range=True)
      if not isinstance(ds.table, NestedTable):
        s += '  printf("finish initialize ds\'s object {}\\n");\n\n'.format(ds.id)
  cpp += s
  return header, cpp

def set_ds_is_refered(dslst, toplst):
  for ds in dslst:
    if ds.value.is_main_ptr():
      assert(ds.value.value)
      for dsl in toplst:
        if ds.value.value == dsl:
          dsl.is_refered=True
    if ds.value.is_object():
      set_ds_is_refered(ds.value.get_object().nested_objects, toplst)
