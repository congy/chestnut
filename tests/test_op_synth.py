import sys
sys.path.append("../")
from schema import *
from query import *
from pred import *
from nesting import *
from ds_manager import *
from op_synth import *
import globalv

workload_name = "test2"
set_db_name(workload_name)
datafile_dir = '{}/data/{}/'.format(os.getcwd(), workload_name)
set_data_file_dir(datafile_dir)
set_cpp_file_path('{}/{}/'.format(os.getcwd(), workload_name))

scale=1
issue = Table('issue', scale*1000)
project = Table('project', scale*80)
enabled_module = Table('enabled_module', project.sz*6)
issue_status = Table('issue_status', 10)

assigned_to_id = Field('assigned_to_id', 'oid')
assigned_to_id.range = [1, 1000]
issue.add_field(assigned_to_id)

status = Field('status', 'smallint')
status.value_with_prob = [(1, 33), (5, 33), (9, 33)]
left = Field('lft', 'uint')
left.range = [1, project.sz]
right = Field('rgt', 'uint')
right.range = [1, project.sz]
project.add_fields([status, left, right])

name = Field('name', 'varchar(16)')
name.value_with_prob = [('issue_tracking', 20), ('wiki',20), ('repository',20), ('boards',20), ('news', 20)]
restricted = Field('restricted', 'uint')
restricted.range = [1, 100]
enabled_module.add_fields([name, restricted])

is_closed = Field('is_closed', 'bool')
issue_status.add_field(is_closed)

issue_status_issue = get_new_assoc('issue_to_status', 'one_to_many', issue_status, issue, 'issues', 'status')
project_issue = get_new_assoc("project_to_issue", "one_to_many", project, issue, "issues", "project")
project_enabled_module = get_new_assoc("project_to_enabled_module", "one_to_many", project, enabled_module, "enabled_modules", "project")

globalv.tables = [issue, project, enabled_module, issue_status]
globalv.associations = [issue_status_issue, project_issue, project_enabled_module]


pred0 = ConnectOp(BinOp(f('lft'), LT, Parameter('p1')), AND, BinOp(f('rgt'), GT, Parameter('p2')))
pred00 = BinOp(f('lft'), IN, MultiParam([Parameter('p1'), Parameter('p2')])) # order by id; a case that MySQL would not use combined index

pred1=ConnectOp(ConnectOp(\
      BinOp(f('project').f('status'), NEQ, AtomValue(9)), AND, \
        SetOp(f('project').f('enabled_modules'), EXIST, BinOp(f('name'), EQ, AtomValue('issue_tracking')))),
      AND,
      ConnectOp(BinOp(f('assigned_to_id'), EQ, Parameter('assigned_to')), AND, 
        SetOp(f('status'), EXIST, BinOp(f('is_closed'), EQ, AtomValue(False)))))

pred2 = ConnectOp(BinOp(f('lft'), NE, Parameter('p1')), AND, BinOp(f('status'), EQ, Parameter('p2')))

pred3 = ConnectOp(ConnectOp(\
  BinOp(f('project').f('id'), IN, MultiParam([Parameter('p1'), Parameter('p2')])), AND,\
  BinOp(f('project').f('lft'), NE, Parameter('p3'))), AND,
  SetOp(f('project').f('enabled_modules'), EXIST, \
    ConnectOp(BinOp(f('name'), EQ, AtomValue('issue_tracking')), AND, \
        BinOp(f('restricted'), LE, Parameter('p4')))))

pred4 = ConnectOp(ConnectOp(\
      BinOp(f('project').f('status'), EQ, Parameter('x1')), AND, \
        SetOp(f('project').f('enabled_modules'), EXIST, BinOp(f('name'), EQ, Parameter('x2')))),
      AND,
      ConnectOp(BinOp(f('assigned_to_id'), EQ, Parameter('assigned_to')), AND, 
        SetOp(f('status'), EXIST, BinOp(f('is_closed'), EQ, AtomValue(False)))))

pred5 = ConnectOp(BinOp(f('project').f('status'), EQ, Parameter('x1')), AND, \
        SetOp(f('project').f('enabled_modules'), EXIST, BinOp(f('name'), EQ, Parameter('x2'))))

#test_synth(project, pred0, order=[f('id',table=project)])
#test_synth(issue, pred1)
#test_synth(project, pred2)
test_synth(issue, pred3)
