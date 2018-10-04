import sys
sys.path.append("../")
from schema import *
from query import *
from pred import *
from nesting import *

workload_name = "usergroup"
set_db_name(workload_name)

users1 = Table("user1", 10000)
users2 = Table("user2", 10000)
groups = Table("ugroup", 1000000)

user1_to_group = get_new_assoc("user1_to_group", "many_to_many", users1, groups, "belong1", "member1", 2000, 0)
user2_to_group = get_new_assoc("user2_to_group", "many_to_many", users2, groups, "belong2", "member2", 2000, 0)

user_name = Field("name", "oid")
user_name.range = [1, 10000]
group_vis = Field("visibility", "oid")
group_vis.value_with_prob = [(1, 40), (2, 60)]

users1.add_field(user_name)
users2.add_field(user_name)
groups.add_field(group_vis)
tables = [users1, users2, groups]
associations = [user1_to_group, user2_to_group]

q = get_all_records(users1)
q.pfilter(ConnectOp(BinOp(f('id'), EQ, Parameter('userA')), AND, \
  SetOp(f('belong1'), EXIST, \
  ConnectOp(BinOp(f('visibility'), EQ, AtomValue(2)), AND, \
  SetOp(f('member2'), EXIST, BinOp(f('id'), EQ, Parameter('userB')))))))
q.project([f('id'), f('name')])
q.complete()

dsmanagers = enumerate_nestings_for_query(q)
for i,ds in enumerate(dsmanagers):
  print "Nesting {}:\n".format(i)
  print ds
  print '--------'