from .redmine_schema import *
# [1m[36mUser Load (4.4ms)[0m  [1m[34mSELECT  `users`.* FROM `users` WHERE `users`.`type` IN ('User', 'AnonymousUser') AND `users`.`status` = 1 AND `users`.`id` = 1 LIMIT 1[0m
#   Current user: admin (id=1)
#   [1m[36mProject Load (728.2ms)[0m  [1m[34mSELECT `projects`.* FROM `projects` WHERE (projects.status <> 9) ORDER BY `projects`.`lft` ASC[0m
#   Rendering projects/index.html.erb within layouts/base
#   [1m[35m (0.4ms)[0m  [1m[34mSELECT `projects`.`id` FROM `projects` INNER JOIN `members` ON `projects`.`id` = `members`.`project_id` WHERE `members`.`user_id` = 1 AND `projects`.`status` != 9[0m
#   Rendered projects/index.html.erb within layouts/base (63452.0ms)
#   [1m[36mProject Load (1.2ms)[0m  [1m[34mSELECT `projects`.`id`, `projects`.`name`, `projects`.`identifier`, `projects`.`lft`, `projects`.`rgt` FROM `projects` INNER JOIN `members` ON `projects`.`id` = `members`.`project_id` WHERE `members`.`user_id` = 1 AND `projects`.`status` != 9 AND `projects`.`status` = 1[0m
# Completed 200 OK in 69490ms (Views: 63630.2ms | ActiveRecord: 741.8ms)

q_pi_0 = get_all_records(project)
q_pi_0.pfilter(BinOp(f('status'), EQ, AtomValue(1)))
q_pi_0.orderby([f('lft')])
q_pi_0.project([f('id'), f('name'), f('lft'), f('rgt')])
q_pi_0.complete()

q_pi_1 = get_all_records(user)
q_pi_1.pfilter(BinOp(f('id'), EQ, Parameter('uid')))
q_pi_1.pfilter(BinOp(f('status'), EQ, AtomValue(1)))
q_pi_1.complete()

q_pi_2 = get_all_records(project)
q_pi_2.pfilter(BinOp(f('status'), NEQ, AtomValue(9)))
q_pi_2.orderby([f('lft')])
q_pi_2.project([f('id')])
q_pi_2.complete()

#q_ii_2

# NcnQ: 2
# NSQL: 2