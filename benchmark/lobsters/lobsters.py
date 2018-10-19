import sys
import os
sys.path.append("../../")
from schema import *
from constants import *
from populate_database import *
from lobsters_schema import *

from nesting import *
from plan_search import *
from ds_manager import *
from ilp.ilp_manager import *
import globalv

#from test_ilp import *

workload_name = "lobsters"
set_db_name(workload_name)
datafile_dir = '{}/data/{}/'.format(os.getcwd(), workload_name)
set_data_file_dir(datafile_dir)

set_cpp_files_path('../../')

globalv.tables = [story, comment, message, tag, vote, user]
globalv.associations = [storys_user, storys_tags, storys_hidden, comments_user, comments_story, message_author, message_recipient, \
votes_comment, votes_story, votes_user]

from comments_create import *
from comments_index import *
from comments_thread import *
from home_index import *
from home_recent import *
from home_tagged import *
from messages_create import *
from messages_delete import *
from messages_index import *
from stories_destroy import *
from stories_show import *
from stories_update import *
from stories_upvote import *
from user_show import *
#generate_db_data_files(datafile_dir, tables, associations)

read_queries = [q_cc_1, q_cc_2, q_cc_10, \
q_ci_1, \
q_ct_1, q_ct_2, \
q_hi_1,
q_hr_1, q_hr_2, q_hr_3, \
q_ht_1,
q_mc_1, q_mc_2, q_mc_6, \
q_md_1, \
q_mi_1, \
q_sd_1, \
q_ss_1, \
q_su_1, \
q_sv_1, \
q_us_1, q_us_2, q_us_3]


write_queries = [q_cc_3, q_cc_4, q_cc_5, q_cc_6, q_cc_7, q_cc_8, q_cc_9, \
q_mc_3, q_mc_4, q_mc_5, \
q_md_2, \
q_sd_2, \
q_su_2, \
q_sv_2, q_sv_3, q_sv_4, q_sv_5, q_sv_6]


# globalv.set_use_template()
# globalv.set_always_nested([QueryField('hidden_users', table=story), QueryField('user', table=vote)])
# globalv.set_always_fk_indexed([QueryField('tags', table=story)])
# globalv.add_pred_scope([ConnectOp(BinOp(f('merged_story_id',table=story), EQ, AtomValue('0')), AND, \
# ConnectOp(BinOp(f('is_expired',table=story), EQ, AtomValue(False)), AND, \
# BinOp(f('upvotes',table=story), GE, AtomValue(-1)))), \
# ConnectOp(BinOp(f('merged_story_id',table=story), EQ, AtomValue('0')), AND, \
# BinOp(f('is_expired',table=story), EQ, AtomValue(False))) \
# ])

#dump_read_plans([q_hr_2])
#exit(0)

globalv.set_qr_type('fastv')
#generate_plans_for_all_queries(tables, associations, [q_us_3], [q_cc_7])
#globalv.pred_selectivity.append((BinOp(f('merged_story_id', table=story), EQ, Parameter('story_id')), 0.001))
#generate_plans_for_all_queries(tables, associations, [q_ct_2], [])
#exit(0)

#test_merge(q_us_2)
#prune_nesting_test(read_queries)
test_ilp(read_queries)
#test_prune_read_plan(read_queries)

# dsmanagers = enumerate_nestings_for_query(q_hr_1)
# for i,ds in enumerate(dsmanagers):
#   print "Nesting {}:\n".format(i)
#   print ds
#   print '--------'
