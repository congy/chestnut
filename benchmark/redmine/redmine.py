import sys
import os
sys.path.append("../../")
from schema import *
from constants import *
from populate_database import *
from redmine_schema import *
from nesting import *
from plan_search import *
from ds_manager import *
from populate_database import *
from ilp.ilp_manager import *
import globalv


workload_name = "redmine"
set_db_name(workload_name)
datafile_dir = '{}/data/{}/'.format(os.getcwd(), workload_name)
set_data_file_dir(datafile_dir)

set_cpp_file_path('{}/{}/'.format(os.getcwd(), workload_name))

globalv.tables = [issue, user, member, project, enabled_module, version, news, board, message, tracker, role, issue_status, enumeration]
globalv.associations = [project_issue, issue_tracker, issue_status_issue, member_user, project_member, member_roles,\
project_tracker, project_news, project_enabled_module, project_version, project_board, message_board, project_enumeration]
#issue_version, issue_user, issue_enumeration]

from activity_index import *
from issue_index import *
from my_page import *
from project_index import *
from project_show import *
from welcome_index import *
from project_new import *
#from project_slow import *


#generate_proto_files(get_cpp_file_path(), tables, associations)
generate_db_data_files(datafile_dir, globalv.tables, globalv.associations)
#populate_database(data_dir, tables, associations)
exit(0)

read_queries = [q_ai_0, q_ai_1, \
q_ii_1, q_ii_2, \
q_mp_1, q_mp_2, q_mp_3, \
q_pi_0, q_pi_1, q_pi_2, \
q_ps_1, q_ps_2, q_ps_3, \
q_wi_0, q_wi_1, q_wi_2, q_wi_3, q_wi_4]
#q_pl, 

write_queries = [q_pn_1, q_pn_2, q_pn_3, q_pn_4, q_pn_5, q_pn_6, q_pn_7]


# globalv.set_use_template()
# globalv.set_always_nested([QueryField('enabled_modules', table=project), QueryField('status', table=issue), \
# QueryField('tracker', table=issue), QueryField('enumeration', table=issue), QueryField('version', table=issue)])

# globalv.add_pred_scope([ConnectOp(BinOp(f('status', table=project), NEQ, AtomValue(9)), AND, \
# SetOp(f('enabled_modules', table=project), EXIST, BinOp(f('name', table=enabled_module), EQ, AtomValue('issue_tracking')))), 
# ConnectOp(BinOp(f('tracker', table=issue).f('id', table=tracker), EQ, Parameter('trackerid')), AND, \
# BinOp(f('enumeration', table=issue).f('type', table=enumeration), EQ, AtomValue('IssuePriority')))\
# ])

#test_merge(q_us_2)
#prune_nesting_test(read_queries)

test_ilp(read_queries)
#test_prune_read_plan(read_queries)
#search_plans_for_one_query(q_ai_1)