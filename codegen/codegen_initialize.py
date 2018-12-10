import sys
sys.path.append('../')
from schema import *
from ds import *
from query import *
from codegen_template import *
from codegen_helper import *
from codegen_ds import *
from codegen_sql import *
from codegen_main import *

def cgen_initialize_all(tables, associations, dsmeta):
  db_name = get_db_name()
  header = "#ifndef __{}_H_\n".format(db_name.upper())
  header += "#define __{}_H_\n".format(db_name.upper())
  header += includes
  cpp = "#include \"{}.h\"\n".format(db_name)
  header += "#include \"proto_{}.pb.h\"\n".format(db_name)
  header += '\n'.join(['// '+l for l in str(struct_pool).split('\n')])

  for t in tables:
    header += "struct {};\n".format(get_capitalized_name(t.name))

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

  next_header, next_cpp = cgen_init_ds_lst(dsmeta.data_structures)
  header += next_header
  code += insert_indent(next_cpp)
  
  code += "  print_time_diff(msg);\n"
  code += "  std::this_thread::sleep_for(std::chrono::seconds(10));\n"
  code += "}\n"

  return header, code
  
def cgen_init_ds_lst(dslst, upper_type=None, upper_v=None):
  header = ''
  cpp = ''
  # s = 'inline void init_ds_from_sql(MYSQL* conn{}{}) {{\n'.format(param1, param2)
  for ds in dslst:
    query_str, nesting, fields = sql_for_ds_query(ds, ds.value.is_main_ptr())
    header += '//ds {}: {}\n'.format(ds.id, ds.__str__(True))
    header += cgen_init_ds_from_sql(ds, nesting, fields, query_str, upper_obj=cgen_obj_type(upper_type))
  
  s = ''
  if upper_type is None:
    # reorganize ds and generate code to get pointer
    pointed = {}
    for ds in dslst:
      if ds.value.is_main_ptr():
        dependent = ds.value.value
        if dependent not in pointed:
          pointed[dependent] = [ds]
        else:
          pointed[dependent].append(ds)
    for ds in dslst:
      if not ds.value.is_main_ptr():
        # code to get pointer
        s += 'init_ds_{}_from_sql(conn);\n'.format(ds.id)
    s += 'oid_t obj_pos = 0;\n'
    for k,lst in pointed:
      assert(k.value.is_object())
      cpp += get_loop_define(k, is_begin=True, is_range=True)
      array_ele = cgen_cxxvar(k.table)
      s += 'obj_pos = 0;\n'
      if isinstance(k, ObjBasicArray) or len(k.key_fields()) == 0:
        s += '({}_{}, {}, {})\n'.format(k.get_idx_name(), get_random_suffix(), k.get_idx_name(), array_ele)
      else:
        s += '({}_{}, nullptr, nullptr, {}, {})\n'.format(k.get_idx_name(), get_random_suffix(), k.get_idx_name(), array_ele))
      for ds in lst:
        s += '  init_ds_{}_from_sql(conn, {}.id, obj_pos);\n'.format(ds.id, array_ele)
      s += 'obj_pos ++;\n'
      s += get_loop_define(k, is_begin=False, is_range=True)
  else:
    s += 'init_ds_{}_from_sql(conn, &{});\n'.format(ds.id, upper_v)

  for ds in dslst:
    if ds.value.is_object() and len(ds.value.nested_objects) > 0:
      array_ele = cgen_cxxvar(ds.table)
      if isinstance(ds, ObjBasicArray) or len(ds.key_fields()) == 0:
        s += '({}_{}, {}, {})\n'.format(ds.get_idx_name(), get_random_suffix(), ds.get_idx_name(), array_ele)
      else:
        s += '({}_{}, nullptr, nullptr, {}, {})\n'.format(ds.get_idx_name(), get_random_suffix(), ds.get_idx_name(), array_ele))
      next_header, next_cpp = cgen_init_ds_lst(ds.value.nested_objects, ds.table, array_ele)
      header += next_header
      s += insert_indent(next_cpp)
      s += get_loop_define(k, is_begin=False, is_range=True)
  cpp += s
  return header, cpp

def test_initialize(tables, associations, read_queries, planid=0):
  rqmanagers, dsmeta_ = get_dsmeta(read_queries)
  # dsmeta = dsmeta_
  for idx,rqmng in enumerate(rqmanagers):
    cnt = 0
    for i,plan_for_one_nesting in enumerate(rqmng.plans):
      if cnt + len(plan_for_one_nesting.plans) > planid:
        j = planid - cnt
        plan = plan_for_one_nesting.plans[j]
        dsmeta = plan_for_one_nesting.dsmanagers[j]
      
  header, cpp = cgen_initialize_all(tables, associations, dsmeta)

  fp = open('{}/{}.h'.format(get_db_name(), get_db_name()), 'w')
  fp.write(header)
  fp.close()

  fp = open('{}/{}.cc'.format(get_db_name(), get_db_name()), 'w')
  fp.write(cpp)
  fp.close()

  main_body = 'read_data();\n'
  main = cgen_for_main_test(main_body, ds_def=True, include_query=False)
  fp = open('{}/main.cc'.format(get_db_name()), 'w')
  fp.write(main)
  fp.close()

