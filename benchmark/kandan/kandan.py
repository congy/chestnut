import sys
sys.path.append("../../")
from schema import *
from query import *
from pred import *
from plan_search import *
from ilp.ilp_manager import *
from ds_manager import *
from populate_database import *
from codegen.protogen import *
from codegen.codegen_test import *
import globalv

from activities_create import *
from activities_index import *
from activities_show import *
from admin_index import *
from admin_toggle_admin import *
from admin_update_user import *
from attachment_create import *
from attachment_index import *
from channels_create import *
from channels_index import *
from channels_show import *
from main_index import *
from main_search import *
#from ilp_solve import *

workload_name = "kandan"
set_db_name(workload_name)
datafile_dir = '{}/data/{}/'.format(os.getcwd(), workload_name)
set_data_file_dir(datafile_dir)

set_cpp_file_path('../../')

tables = [user, channel, activity, attachment]
associations = [channel_to_activitiy, channel_user, activity_user, attachment_user, attachment_channel]

globalv.tables = tables
globalv.associations = associations
#generate_db_data_files(datafile_dir, tables, associations)
#exit(0)

read_queries = [q_ai_1, q_ai_2, q_ai_3, \
q_as_1, \
q_di_1, \
q_ti_1, \
q_ci_1, \
q_cs_1, \
q_mi_1, \
q_ms_1]

write_queries = [q_ac_w1, q_ac_w2, q_ac_w3, \
q_du_1, \
q_dt_1, \
q_tc_w1, q_tc_w2, q_tc_w3, \
q_cc_w1, q_cc_w2]


#q_ai_1.assigned_param_values = {Parameter('channel_id'):'47', Parameter('oldest'):'183'}
#q_ai_2.assigned_param_values = {Parameter('channel_id'):'47'}

# q_ti_1.assigned_param_values = {Parameter('channel_id'):'3'}
# q_tc_w2.assigned_param_values = {Parameter('channel_id'):'3', Parameter('attachment_id'):'14'}
#[q_ti_1], [q_tc_w1, q_tc_w2]

#q_ci_1.assigned_param_values = {Parameter('channel_id'):'47'}

search_plans_for_one_query(read_queries[4])

# test_merge(q)
#test_ilp(read_queries)

data_dir=datafile_dir
#generate_proto_files(get_cpp_file_path(), tables, associations)
#generate_db_data_files(data_dir, tables, associations)
#populate_database(data_dir, tables, associations)
#test_query(tables, associations, q, 20)
