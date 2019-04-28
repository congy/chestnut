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

tables = [user, agent, event, delayed_job, link]
associations = [agent_to_user, event_to_agent, event_to_user, link_source, link_receive]

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
test_query(tables, associations, read_queries[0], 13)