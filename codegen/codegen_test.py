import sys
sys.path.append('../')
from schema import *
from ds import *
from query import *
from .codegen_sql import *
from .codegen_initialize import *
from .codegen_ir import *
from .codegen_template import *
from .protogen import *
from constants import *
#import mysql.connector
from ilp.ilp_manager import *

# ====== test initialize ds ======

def prepare_other_files(tables, associations):
  os.system('mkdir {}'.format(get_db_name()))
  generate_proto_files('./{}/'.format(get_db_name()), tables, associations)
  for f in copy_cpp_files:
    os.system('cp {}/cpp_utils/{} {}/'.format(get_cpp_file_path(), f, get_db_name()))


def test_initialize(tables, associations, read_queries, planid=0):
  rqmanagers, dsmeta_ = get_dsmeta(read_queries)
  # dsmeta = dsmeta_
  for idx,rqmng in enumerate(rqmanagers):
    cnt = 0
    #print sum([len(plan_for_one_nesting.plans) for plan_for_one_nesting in rqmng.plans])
    for i,plan_for_one_nesting in enumerate(rqmng.plans):
      if cnt + len(plan_for_one_nesting.plans) > planid:
        j = planid - cnt
        plan = plan_for_one_nesting.plans[j]
        dsmeta = plan_for_one_nesting.dsmanagers[j]
        plan.copy_ds_id(None, dsmeta)
        break
      cnt = cnt + len(plan_for_one_nesting.plans)
      
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

def test_query(tables, associations, query: ReadQuery, planid: int = 0):
  rqmanagers, dsmeta_ = get_dsmeta([query])
  for idx,rqmng in enumerate(rqmanagers):
    cnt = 0
    print('Nplans = {}'.format(sum([len(x.plans) for x in rqmng.plans])))
    for i,plan_for_one_nesting in enumerate(rqmng.plans):
      if cnt + len(plan_for_one_nesting.plans) > planid:
        j = planid - cnt
        plan = plan_for_one_nesting.plans[j]
        dsmeta = plan_for_one_nesting.dsmanagers[j]
        plan.copy_ds_id(None, dsmeta)
        break
      cnt = cnt + len(plan_for_one_nesting.plans)
      
  header, cpp = cgen_initialize_all(tables, associations, dsmeta)
  #prepare_other_files(tables, associations)

  fp = open('{}/{}.h'.format(get_db_name(), get_db_name()), 'w')
  fp.write(header)
  fp.close()

  fp = open('{}/{}.cc'.format(get_db_name(), get_db_name()), 'w')
  fp.write(cpp)
  fp.close()

  header, cpp = cgen_for_read_query(0, query, plan, dsmeta, planid)
  header = query_includes + '#include "{}.h"\n\n'.format(get_db_name()) + header 
  cpp = '#include "{}_query.h"'.format(get_db_name()) + '\n' + cpp

  fp = open('{}/{}_query.h'.format(get_db_name(), get_db_name()), 'w')
  fp.write(header)
  fp.close()

  fp = open('{}/{}_query.cc'.format(get_db_name(), get_db_name()), 'w')
  fp.write(cpp)
  fp.close()

  main_body = 'read_data();\n' + cgen_for_query_in_main([query], [planid])
  main = cgen_for_main_test(main_body, ds_def=True, include_query=True)
  fp = open('{}/main.cc'.format(get_db_name()), 'w')
  fp.write(main)
  fp.close()

# ====== test generate SQL and deserialize ========
def test_print_nesting(nesting, upper_obj, qf=None, level=1):
  if level == 1:
    tname = nesting.table.name
  else:
    tname = qf.field_name
  s = ''
  if qf and qf.table.has_one_or_many_field(qf.field_name) == 1:
    s += '{\n'
    s += '  auto& i{}_{} = {}.{}();\n'.format(level, tname, upper_obj, tname)
    s += '  printf("{}{} %u\\n", i{}_{}.id());\n'.format('  '.join(['' for x in range(0, level)]), tname, level, tname)
  else:
    s += 'for(int i{}=0; i{}<{}.{}_size(); i{}++){{\n'.format(level, level, upper_obj, tname, level)
    s += '  auto& i{}_{} = {}.{}(i{});\n'.format(level, tname, upper_obj, tname, level)
    s += '  printf("{}{} %u\\n", i{}_{}.id());\n'.format('  '.join(['' for x in range(0, level)]), tname, level, tname)
  for k,v in list(nesting.assocs.items()):
    s += insert_indent(test_print_nesting(v, 'i{}_{}'.format(level, tname), k, level+1), level)
  s += '}\n'
  return s
  
def test_deserialize(read_queries):
  rqmanagers, dsmeta = get_dsmeta(read_queries)
  ds_lst = collect_all_ds_helper1(dsmeta.data_structures)[0]
  s = test_deserialize_helper(ds_lst)
  fp = open('{}/test_{}.cc'.format(get_db_name(), get_db_name()), 'w')
  fp.write(s)
  fp.close()

def test_deserialize_helper(ds_lst):
  s = '#include "proto_{}.pb.h"\n'.format(get_db_name())
  s += '#include "mysql.h"\n'
  s += '#include "util.h"\n'
  ds_nestings = []
  for ds in ds_lst:
    query_str, nesting, fields = sql_for_ds_query(ds)
    s += '//ds {}: {}\n'.format(ds.id, ds.__str__(True))
    s += codegen_deserialize(ds, nesting, fields, query_str)
    ds_nestings.append((ds, nesting))
  
  s += '\n\n'
  s += """
int main() {
  MYSQL *conn = mysql_init(NULL);
  if (conn == NULL){
    fprintf(stderr, "mysql_init() failed\\n");
    exit(1);
  }
"""
  s += 'if (mysql_real_connect(conn, "localhost", "root", "", "{}", 0, NULL, 0) == NULL){{\n'.format(get_db_name())
  s += """
    fprintf(stderr, "mysql connect failed\\n");
    exit(1);
  }
"""
  
  for ds,nesting in ds_nestings:
    tname = nesting.table.name
    s += '  printf("result fo ds {}\\n");\n'.format(ds.id)
    s += '  {}::P{}List ret_obj_{}_{};\n'.format(get_db_name(), get_capitalized_name(tname), tname, ds.id)
    s += '  query_data_for_ds{}(conn, &ret_obj_{}_{});\n'.format(ds.id, tname, ds.id)
    s += insert_indent(test_print_nesting(nesting, 'ret_obj_{}_{}'.format(tname, ds.id)))

  s += '  return 0;\n'
  s += '}\n'
  return s


def test_generate_sql(read_queries):
  rqmanagers, dsmeta = get_dsmeta(read_queries)
  mydb = mysql.connector.connect(host="localhost", user="root", passwd="", database=get_db_name())
  mycursor = mydb.cursor()
  for ds in dsmeta.data_structures:
    test_generate_sql_helper(ds, mycursor)

def test_generate_sql_helper(ds, mycursor):
  query_str, nesting, fields = sql_for_ds_query(ds)
  print('ds = {}, query = {}'.format(ds.__str__(short=True), query_str))
  print('')
  mycursor.execute(query_str+' limit 1')
  myresult = mycursor.fetchall()
  #print codegen_deserialize(ds, nesting, fields, query_str)
  #print '----\n'
  if ds.value.is_object():
    for nextds in ds.value.get_object().nested_objects:
      nextqf = get_qf_from_nested_t(nextds.table)
      test_generate_sql_helper(nextds, mycursor)

def test_codegen_one_query(tables, associations, query, planid=-1):
  rqmanagers, dsmeta = get_dsmeta([query]) 
  rqmng = rqmanagers[0]
  chosen_plan = None # tup: ()
  plan_id = 0
  query.id = 0
  for i,plan_for_one_nesting in enumerate(rqmng.plans):
    for j in range(0, len(plan_for_one_nesting.plans)):
      plan = plan_for_one_nesting.plans[j]
      dsmng = plan_for_one_nesting.dsmanagers[j]
      cost = to_real_value(plan.compute_cost())
      if (planid==-1 and (chosen_plan is None or chosen_plan[0]>cost)) or (planid == plan_id):
        chosen_plan = (cost, plan, dsmng, plan_id)  
      plan_id = plan_id + 1

  prepare_other_files(tables, associations)
  header, cpp = cgen_initialize_all(tables, associations, dsmeta)
  fp = open('{}/{}.h'.format(get_db_name(), get_db_name()), 'w')
  fp.write(header)
  fp.close()

  fp = open('{}/{}.cc'.format(get_db_name(), get_db_name()), 'w')
  fp.write(cpp)
  fp.close()

  chosen_plan[1].copy_ds_id(None, dsmeta)
  header_, cpp_ = cgen_for_read_query(0, query, chosen_plan[1], chosen_plan[2], chosen_plan[3])
  header = (header_ + '\n')
  cpp = (cpp_ + '\n')
  
  header = query_includes + '#include "{}.h"\n\n'.format(get_db_name()) + header 
  cpp = '#include "{}_query.h"'.format(get_db_name()) + '\n' + cpp

  fp = open('{}/{}_query.h'.format(get_db_name(), get_db_name()), 'w')
  fp.write(header)
  fp.close()

  fp = open('{}/{}_query.cc'.format(get_db_name(), get_db_name()), 'w')
  fp.write(cpp)
  fp.close()

  main_body = 'read_data();\n' + cgen_for_query_in_main([query], [chosen_plan[3]])
  main = cgen_for_main_test(main_body, ds_def=True, include_query=True)
  fp = open('{}/main.cc'.format(get_db_name()), 'w')
  fp.write(main)
  fp.close()

def test_read_overall(tables, associations, queries: [ReadQuery], memfactor=1, read_from_file=False, read_ilp=False):

  (dsmeta, plans, plan_ds, plan_ids) = ilp_solve(queries, membound_factor=memfactor, read_from_file=read_from_file, read_ilp=read_ilp)

  prepare_other_files(tables, associations)

  header, cpp = cgen_initialize_all(tables, associations, dsmeta)

  fp = open('{}/{}.h'.format(get_db_name(), get_db_name()), 'w')
  fp.write(header)
  fp.close()

  fp = open('{}/{}.cc'.format(get_db_name(), get_db_name()), 'w')
  fp.write(cpp)
  fp.close()

  header = ''
  cpp = ''
  for i in range(0, len(plans)):
    print('generate file for query {} plan {}'.format(i, plan_ids[i]))
    queries[i].id = i
    print(plans[i])
    plans[i].copy_ds_id(None, dsmeta)
    header_, cpp_ = cgen_for_read_query(i, queries[i], plans[i], plan_ds[i], plan_ids[i])
    header += (header_ + '\n')
    cpp += (cpp_ + '\n')
  
  header = query_includes + '#include "{}.h"\n\n'.format(get_db_name()) + header 
  cpp = '#include "{}_query.h"'.format(get_db_name()) + '\n' + cpp

  fp = open('{}/{}_query.h'.format(get_db_name(), get_db_name()), 'w')
  fp.write(header)
  fp.close()

  fp = open('{}/{}_query.cc'.format(get_db_name(), get_db_name()), 'w')
  fp.write(cpp)
  fp.close()

  main_body = 'read_data();\n' + cgen_for_query_in_main(queries, plan_ids)
  main = cgen_for_main_test(main_body, ds_def=True, include_query=True)
  fp = open('{}/main.cc'.format(get_db_name()), 'w')
  fp.write(main)
  fp.close()
