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
from codegen.protogen import *
from codegen.codegen_test import *
import globalv


workload_name = "redmine"
set_db_name(workload_name)
datafile_dir = '{}/data/{}/'.format(os.getcwd(), workload_name)
set_data_file_dir(datafile_dir)

set_cpp_file_path('../../')

globalv.tables = [issue, user, member, project, enabled_module, version, news, board, message, tracker, role, issue_status, enumeration]
globalv.associations = [project_issue, issue_tracker, issue_status_issue, member_user, project_member, member_roles,\
project_tracker, project_news, project_enabled_module, project_version, project_board, message_board, project_enumeration]
#issue_version, issue_user, issue_enumeration]

tables = globalv.tables
associations = globalv.associations



#SELECT projects.* FROM projects WHERE projects.status!=9 AND (projects.lft >= 1 AND projects.rgt <= 77927) ORDER BY projects.lft ASC
# SELECT projects.* into table q_ai_1 FROM projects WHERE projects.status!=9 ORDER BY projects.lft;
# SELECT * FROM q_ai_1 as projects where (projects.lft >= 1 AND projects.rgt <= 77927);
q_ai_1 = get_all_records(project)
q_ai_1.pfilter(BinOp(f('status'), NEQ, AtomValue(9)))
q_ai_1.pfilter(ConnectOp(BinOp(f('lft'), GE, Parameter('pid2')), AND, BinOp(f('rgt'), LE, Parameter('pid3'))))
q_ai_1.orderby([f('lft')])
q_ai_1.complete()


#select projects.id, projects.lft, projects.rgt from projects where (projects.status = 1) ORDER BY projects.lft ASC;
# select projects.id, projects.lft, projects.rgt into table q_pi_0 from projects where (projects.status = 1) ORDER BY projects.lft ASC;
# select * from q_pi_0;
q_pi_0 = get_all_records(project)
q_pi_0.pfilter(BinOp(f('status'), EQ, AtomValue(1)))
q_pi_0.orderby([f('lft')])
q_pi_0.project([f('id'), f('name'), f('lft'), f('rgt')])
q_pi_0.complete()


#SELECT  news.* FROM news INNER JOIN projects ON projects.id = news.project_id WHERE 
# (projects.status <> 9 AND EXISTS (SELECT 1 AS one FROM enabled_modules em WHERE em.project_id = projects.id AND em.name='news')) 
# ORDER BY news.created_on DESC LIMIT 5
## SELECT  news.* FROM news INNER JOIN projects ON projects.id = news.project_id WHERE (projects.status <> 9 AND EXISTS (SELECT 1 AS one FROM enabled_modules em WHERE em.project_id = projects.id AND em.name='news')) ORDER BY news.created_on DESC LIMIT 5
## SELECT * FROM 
q_wi_4 = get_all_records(news)
q_wi_4.pfilter(BinOp(f('project').f('status'), NEQ, AtomValue(9)))
q_wi_4.pfilter(SetOp(f('project').f('enabled_modules'), EXIST, BinOp(f('name'), EQ, AtomValue('news'))))
q_wi_4.orderby([f('created_on')])
q_wi_4.return_limit(5)
q_wi_4.complete()


# select projects.*, news.id as newsid, news.title as newstitle, news.author_id as newsauthor from projects 
# inner join news ON projects.id = news.project_id WHERE 
# (projects.status <> 9 AND EXISTS 
# (SELECT 1 AS one FROM enabled_modules em WHERE em.project_id = projects.id AND em.name='news'));

# select projects.*, news.id as newsid, news.title as newstitle, news.author_id as newsauthor into table q_wi_2 from projects inner join news ON projects.id = news.project_id WHERE (projects.status <> 9 AND EXISTS (SELECT 1 AS one FROM enabled_modules em WHERE em.project_id = projects.id AND em.name='news'));
# SELECT * FROM q_wi_2;
q_wi_2 = get_all_records(project)
q_wi_2.pfilter(BinOp(f('status'), NEQ, AtomValue(9)))
q_wi_2.pfilter(SetOp(f('enabled_modules'), EXIST, BinOp(f('name'), EQ, AtomValue('news'))))
q_wi_2.finclude(f('news'), projection=[f('title'), f('author_id')])
#q_wi_2.project([f('id'), f('name'), f('lft'), f('rgt')])
q_wi_2.complete()

q_test = get_all_records(project)
q_test.pfilter(SetOp(f('issues'), EXISTS, BinOp(f('status_id'), EQ, AtomValue(4))))
q_test.pfilter(BinOp(f('created_on'), GE, Parameter('created')))
q_test.complete()

read_queries=[q_test]
ilp_solve(read_queries, write_queries=[], membound_factor=1.4, save_to_file=True, read_from_file=False, read_ilp=False, save_ilp=True)
test_read_overall(tables, associations, read_queries, memfactor=1.4, read_from_file=True, read_ilp=True)
