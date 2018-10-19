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

workload_name = "usergroup"
set_db_name(workload_name)

users1 = Table("user1", 10000)
users2 = Table("user2", 10000)
groups = Table("ugroup", 100)

user1_to_group = get_new_assoc("user1_to_group", "many_to_many", users1, groups, "belong1", "member1", 2, 0)
user2_to_group = get_new_assoc("user2_to_group", "many_to_many", users2, groups, "belong2", "member2", 2, 0)

user_name = Field("name", "oid")
user_name.range = [1, 10000]
group_vis = Field("visibility", "oid")
group_vis.value_with_prob = [(1, 40), (2, 60)]

users1.add_field(user_name)
users2.add_field(user_name)
groups.add_field(group_vis)
globalv.tables = [users1, users2, groups]
globalv.associations = [user1_to_group, user2_to_group]

q = get_all_records(users1)
q.pfilter(ConnectOp(BinOp(f('id'), EQ, Parameter('userA')), AND, \
  SetOp(f('belong1'), EXIST, \
  ConnectOp(BinOp(f('visibility'), EQ, AtomValue(2)), AND, \
  SetOp(f('member2'), EXIST, BinOp(f('id'), EQ, Parameter('userB')))))))
q.project([f('id'), f('name')])
q.complete()

q1 = get_all_records(users1)
q1.pfilter(ConnectOp(BinOp(f('id'), EQ, Parameter('i1')), AND, BinOp(f('name'), GE, Parameter('i2'))))
q1.complete()

# test enumerate nesting
# dsmanagers = enumerate_nestings_for_query(q)
# for i,ds in enumerate(dsmanagers):
#   print "Nesting {}:\n".format(i)
#   print ds
#   print '--------'

# test search plan
search_plans_for_one_query(q)

#test_merge(q)
#test_ilp([q])
#test_prune_read_plan([q])

