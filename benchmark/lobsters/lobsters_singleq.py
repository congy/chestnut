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
from lobsters_schema import *
import globalv

#from test_ilp import *

workload_name = "lobsters"
set_db_name(workload_name)
datafile_dir = '{}/data/{}/'.format(os.getcwd(), workload_name)
set_data_file_dir(datafile_dir)

set_cpp_file_path('../../')

tables = [story, comment, message, tag, vote, user]
associations = [storys_user, storys_tags, storys_hidden, comments_user, comments_story, message_author, message_recipient, \
votes_comment, votes_story, votes_user]

globalv.tables = tables
globalv.associations = associations


# SELECT  comments.* FROM comments  WHERE comments.is_deleted = 0 AND comments.is_moderated = 0 AND (story_id NOT IN (SELECT story_id FROM hidden_stories WHERE user_id = 1))  ORDER BY created_at DESC LIMIT 20 OFFSET 0
# SELECT comments.*, hidden_stories.user_id as hu_user_id into table q_ci_1 FROM comments INNER JOIN hidden_stories on hidden_stories.story_id = comments.story_id ORDER BY hu_user_id;
# SELECT * FROM q_ci_1 WHERE hu_user_id = 1 ORDER BY created_at DESC LIMIT 20 OFFSET 0
param_user_id = Parameter('user_id')
q_ci_1 = get_all_records(comment)
q_ci_1.pfilter(BinOp(f('is_deleted'), EQ, AtomValue(False)))
q_ci_1.pfilter(BinOp(f('is_moderated'), EQ, AtomValue(False)))
q_ci_1.pfilter(BinOp(f('story').f('user').f('id'), NEQ, param_user_id))
q_ci_1.orderby([f('created_at')], ascending=False)
q_ci_1.return_limit(20)
q_ci_1.project('*')
#q_ci_1.finclude(f('votes'), pfilter=BinOp(f('user').f('id'), EQ, param_user_id), projection=[f('vote'),f('id')])
q_ci_1.complete()

#SELECT  comments.thread_id FROM comments WHERE comments.user_id = 1 GROUP BY comments.thread_id  ORDER BY MAX(created_at) DESC LIMIT 20
q_ct_1_comment = get_all_records(comment)
q_ct_1 = q_ct_1_comment.groupby([f('thread_id')], THREAD_NUM)
q_ct_1.finclude(f('comments'), pfilter=BinOp(f('user').f('id'), EQ, Parameter('user_id')))
q_ct_1.get_include(f('comments')).aggr(UnaryExpr(MAX, f('created_at')), 'max_created')
q_ct_1.orderby([f('max_created')])
q_ct_1.return_limit(20)
q_ct_1.project([f('thread_id')])
q_ct_1.complete()

#SELECT comments.* , users.username, story.title, story.short_id FROM comments 
# inner join stories on comments.story_id = stories.id inner join users on comments.user_id = user.id
# WHERE comments.thread_id IN (6, 99, 77, 49, 37, 75, 7, 85, 14, 88, 48, 93, 44, 47, 46, 26, 89, 60, 22, 81)  ORDER BY confidence DESC
threads = [Parameter('thread_id_{}'.format(i)) for i in range(0, 20)]
q_ct_2 = get_all_records(comment)
q_ct_2.pfilter(BinOp(f('thread_id'), IN, MultiParam(threads)))
q_ct_2.orderby([f('confidence')])
q_ct_2.finclude(f('user'), projection=[f('username')])
q_ct_2.finclude(f('story'),projection=[f('title'),f('short_id')])
q_ct_2.complete()


#SELECT stories.id, stories.upvotes, stories.downvotes, stories.user_id FROM stories  WHERE stories.merged_story_id = 0 AND stories.is_expired = 0  AND (stories.id NOT IN (SELECT hidden_stories.story_id FROM hidden_stories WHERE hidden_stories.user_id = 1)) AND (stories.id NOT IN (SELECT taggings.story_id FROM taggings  WHERE taggings.tag_id IN (23))) AND (stories.created_at > '2016-10-23 22:34:39')  ORDER BY stories.id DESC, stories.created_at DESC;
# SELECT stories.id, stories.upvotes, stories.downvotes, stories.user_id, stories.created_at, hidden_stories.user_id as hu_user_id, taggings.tag_id as tag_id into table q_hr_1 FROM stories inner join hidden_stories on hidden_stories.story_id = stories.id inner join taggings on taggings.story_id = stories.id WHERE stories.merged_story_id = 0 AND stories.is_expired = 0 order by stories.id;
# SELECT id, upvotes, downvotes, user_id from q_hr_1 where hu_user_id != 32 and tag_id != 3 and created_at > '2016-10-23 22:34:39' group by id, upvotes, downvotes, user_id order by id;
param_user_id = Parameter('user_id')
q_hr_1 = get_all_records(story)
q_hr_1.pfilter(BinOp(f('merged_story_id'), EQ, AtomValue(0)))
q_hr_1.pfilter(BinOp(f('is_expired'), EQ, AtomValue(False)))
q_hr_1.pfilter(UnaryOp(SetOp(f('hidden_users'), EXIST, BinOp(f('id'), EQ, param_user_id))))
q_hr_1.pfilter(UnaryOp(SetOp(f('tags'), EXIST, BinOp(f('id'), EQ, Parameter('tag_id')))))
q_hr_1.pfilter(BinOp(f('created_at'), GT, Parameter('some_date')))
q_hr_1.orderby([f('id'), f('created_at')], ascending=False)
q_hr_1.project([f('id'), f('upvotes'), f('downvotes'), f('user_id')])
#q_hr_1.finclude(f('tags'), pfilter=BinOp(f('id'), EQ, Parameter('tag_id')), projection=[f('tag'),f('id')])
#q_hr_1.finclude(f('votes'), pfilter=ConnectOp(BinOp(f('user').f('id'), EQ, param_user_id), AND, BinOp(f('comment').f('id'), EQ, AtomValue(0))), projection=[f('vote'),f('id')])
q_hr_1.complete()

read_queries = [q_ci_1]
ilp_solve(read_queries, write_queries=[], membound_factor=1.1, save_to_file=True, read_from_file=False, read_ilp=False, save_ilp=True)
test_read_overall(tables, associations, read_queries, memfactor=1.1, read_from_file=True, read_ilp=True)
