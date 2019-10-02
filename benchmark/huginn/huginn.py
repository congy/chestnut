import sys
sys.path.append("../../")
from schema import *
from query import *
from pred import *
from plan_search import *
from ilp.ilp_manager import *
from ds_manager import *
from query_manager import *
from populate_database import *
from codegen.protogen import *
from codegen.codegen_test import *
from codegen.codegen_client import *
import globalv

from huginn_schema import *
from agents_index import *
from agents_show import *
from events_index import *
from dryruns_index import *
from home_index import *
from job_index import *

workload_name = "huginn"
set_db_name(workload_name)
datafile_dir = '{}/data/{}/'.format(os.getcwd(), workload_name)
set_data_file_dir(datafile_dir)

set_cpp_file_path('../../')

tables = [delayed_job]
associations = []
#tables = [agent, event, delayed_job, link]
#associations = [agent_to_user, event_to_agent, event_to_user, link_source, link_receive]

#globalv.always_fk_indexed = [QueryField('sources',agent)]#[QueryField('agent',event)] 
globalv.tables = tables
globalv.associations = associations

read_queries = [q_ai_1, q_ai_2,\
  q_as_1,\
  q_di_1,\
  q_ei_1,q_ei_2,q_ei_3,\
  q_hi_1,q_hi_2,q_hi_3,\
  q_ji_1,q_ji_2,q_ji_3,q_ji_4]

write_queries = []


data_dir=datafile_dir
#generate_proto_files(get_cpp_file_path(), tables, associations)
#generate_db_data_files(data_dir, tables, associations)
#populate_database(data_dir, tables, associations, True)
#test_query(tables, associations, read_queries[0], 13)
#search_plans_for_one_query(q_di_1)

#cgen_ruby_client(read_queries, './{}/ruby/'.format(workload_name))

# test_merge(q)
#test_ilp(read_queries, membound_factor=1)
ilp_solve(read_queries, write_queries=[], membound_factor=20, save_to_file=True, read_from_file=False, read_ilp=False, save_ilp=True)
exit(0)
#test_read_overall(tables, associations, read_queries, memfactor=1.5, read_from_file=True, read_ilp=True)

#exit(0)
indexes = {user:[],\
delayed_job:[['priority','run_at']],\
event:[['id'], ['agent_id', 'created_at'], ['user_id','created_at'],['user_id'],['created_at']],\
agent:[['id'],['disabled','deactivated'],['type'],['user_id','created_at'],['type']],\
link:[['receiver_id','source_id'],['id'],['source_id','receiver_id'],['receiver_id'],['source_id']]}
s = create_psql_tables_script(data_dir, tables, associations, indexes)
f = open('load_postgres_tables.sql', 'w')
f.write(s)
f.close()
