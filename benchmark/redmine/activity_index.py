from redmine_schema import *
  # [1m[36mUser Load (0.4ms)[0m  [1m[34mSELECT  `users`.* FROM `users` WHERE `users`.`type` IN ('User', 'AnonymousUser') AND `users`.`status` = 1 AND `users`.`id` = 1 LIMIT 1[0m
  # Current user: admin (id=1)
  # [1m[36mProject Load (0.3ms)[0m  [1m[34mSELECT  `projects`.* FROM `projects` WHERE `projects`.`id` = 118986 LIMIT 1[0m
  # [1m[35m (0.4ms)[0m  [1m[34mSELECT `enabled_modules`.`name` FROM `enabled_modules` WHERE `enabled_modules`.`project_id` = 118986[0m
  # [1m[36mProject Load (350.8ms)[0m  [1m[34mSELECT `projects`.* FROM `projects` WHERE (projects.lft >= 1 AND projects.rgt <= 77927) ORDER BY `projects`.`lft` ASC[0m
  # [1m[35mCACHE  (0.0ms)[0m  [1m[34mSELECT `enabled_modules`.`name` FROM `enabled_modules` WHERE `enabled_modules`.`project_id` = 118986[0m
  # [1m[35m (0.5ms)[0m  [1m[34mSELECT `enabled_modules`.`name` FROM `enabled_modules` WHERE `enabled_modules`.`project_id` = 181011[0m
  # [1m[35m (0.3ms)[0m  [1m[34mSELECT `enabled_modules`.`name` FROM `enabled_modules` WHERE `enabled_modules`.`project_id` = 132413[0m
  # 
q_ai_0 = get_all_records(project)
q_ai_0.pfilter(BinOp(f('id'), EQ, Parameter('pid')))
q_ai_0.finclude(f('enabled_modules'), projection=[f('name')])
q_ai_0.complete()

q_ai_1 = get_all_records(project)
q_ai_1.pfilter(BinOp(f('status'), NEQ, AtomValue(9)))
q_ai_1.pfilter(ConnectOp(BinOp(f('lft'), GE, Parameter('pid2')), AND, BinOp(f('rgt'), LE, Parameter('pid3'))))
q_ai_1.finclude(f('enabled_modules'), projection=[f('name')])
q_ai_1.orderby([f('lft')])
q_ai_1.complete()

# NcnQ: 2
# NSQL: 5