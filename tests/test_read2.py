import sys
sys.path.append("../")
from schema import *
from query import *
from pred import *
from nesting import *
from plan_search import *
from ilp.ilp_manager import *
from ds_manager import *
import globalv

workload_name = "test2"
set_db_name(workload_name)

scale=50
issue = Table('issue', scale*2000)
project = Table('project', scale*80)
enabled_module = Table('enabled_module', project.sz*6)
issue_status = Table('issue_status', 10)

assigned_to_id = Field('assigned_to_id', 'oid')
assigned_to_id.range = [1, 1000]
issue.add_field(assigned_to_id)

status = Field('status', 'smallint')
status.value_with_prob = [(1, 33), (5, 33), (9, 33)]
project.add_field(status)

name = Field('name', 'varchar(16)')
name.value_with_prob = [('issue_tracking', 20), ('wiki',20), ('repository',20), ('boards',20), ('news', 20)]
enabled_module.add_fields([name])

is_closed = Field('is_closed', 'bool')
issue_status.add_field(is_closed)

issue_status_issue = get_new_assoc('issue_to_status', 'one_to_many', issue_status, issue, 'issues', 'status')
project_issue = get_new_assoc("project_to_issue", "one_to_many", project, issue, "issues", "project")
project_enabled_module = get_new_assoc("project_to_enabled_module", "one_to_many", project, enabled_module, "enabled_modules", "project")

globalv.tables = [issue, project, enabled_module, issue_status]
globalv.associations = [issue_status_issue, project_issue, project_enabled_module]

q_mp_2 = get_all_records(issue)
q_mp_2.pfilter(BinOp(f('project').f('status'), NEQ, AtomValue(9)))
q_mp_2.pfilter(SetOp(f('project').f('enabled_modules'), EXIST, BinOp(f('name'), EQ, AtomValue('issue_tracking'))))
q_mp_2.pfilter(ConnectOp(BinOp(f('assigned_to_id'), EQ, Parameter('assigned_to')), AND, 
SetOp(f('status'), EXIST, BinOp(f('is_closed'), EQ, AtomValue(False)))))
q_mp_2.aggr(UnaryExpr(COUNT), 'count_issue')
q_mp_2.complete()

q = q_mp_2

# test enumerate nesting
# dsmanagers = enumerate_nestings_for_query(q)
# for i,ds in enumerate(dsmanagers):
#   print "Nesting {}:\n".format(i)
#   print ds
#   print '--------'

# test search plan
# search_plans_for_one_query(q)

# test_merge(q)
test_ilp([q])
