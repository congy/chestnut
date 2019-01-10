from redmine_schema import *

  # [1m[36mRole Load (0.3ms)[0m  [1m[34mSELECT  `roles`.* FROM `roles` WHERE `roles`.`builtin` = 2 ORDER BY `roles`.`id` ASC LIMIT 1[0m
  # [1m[35m (0.2ms)[0m  [1m[34mSELECT `users`.`id` FROM `users` WHERE `users`.`type` IN ('GroupAnonymous')[0m
  # [1m[35m (0.4ms)[0m  [1m[34mSELECT `members`.`user_id`, `role_id`, `members`.`project_id` FROM `members` INNER JOIN `projects` ON `projects`.`id` = `members`.`project_id` INNER JOIN `member_roles` ON `member_roles`.`member_id` = `members`.`id` 
  # WHERE (projects.status <> 9) AND (members.user_id = 4 OR (projects.is_public = TRUE AND members.user_id = 2))[0m
  # [1m[36mProject Load (0.3ms)[0m  [1m[34mSELECT `projects`.`id`, `projects`.`name`, `projects`.`identifier`, `projects`.`lft`, `projects`.`rgt` FROM `projects` INNER JOIN `members` ON `projects`.`id` = `members`.`project_id` WHERE `members`.`user_id` = 5 AND `projects`.`status` != 9 AND `projects`.`status` = 1[0m

  # [1m[36mUser Load (0.3ms)[0m  [1m[34mSELECT  `users`.* FROM `users` WHERE `users`.`type` IN ('User', 'AnonymousUser') AND `users`.`status` = 1 AND `users`.`id` = 1 LIMIT 1[0m
  # [1m[36mNews Load (56183.2ms)[0m  [1m[34mSELECT  `news`.* FROM `news` INNER JOIN `projects` ON `projects`.`id` = `news`.`project_id` WHERE (projects.status <> 9 AND EXISTS (SELECT 1 AS one FROM enabled_modules em WHERE em.project_id = projects.id AND em.name='news')) ORDER BY news.created_on DESC LIMIT 5[0m

q_wi_0 = get_all_records(user)
q_wi_0.pfilter(BinOp(f('type'), EQ, Parameter('GroupAnonymous')))
q_wi_0.project([f('id')])
q_wi_0.complete()


q_wi_1 = get_all_records(user)
q_wi_1.pfilter(BinOp(f('id'), EQ, Parameter('user_id')))
q_wi_1.pfilter(BinOp(f('status'), EQ, AtomValue(1)))
q_wi_1.complete()

q_wi_4 = get_all_records(news)
q_wi_4.pfilter(BinOp(f('project').f('status'), NEQ, AtomValue(9)))
q_wi_4.pfilter(SetOp(f('project').f('enabled_modules'), EXIST, BinOp(f('name'), EQ, AtomValue('news'))))
q_wi_4.orderby([f('created_on')])
q_wi_4.return_limit(5)
q_wi_4.complete()

q_wi_2 = get_all_records(project)
q_wi_2.pfilter(BinOp(f('status'), NEQ, AtomValue(9)))
q_wi_2.pfilter(SetOp(f('enabled_modules'), EXIST, BinOp(f('name'), EQ, AtomValue('news'))))
q_wi_2.finclude(f('news'), projection=[f('title'), f('author_id')])
q_wi_2.project([f('id'), f('name'), f('lft'), f('rgt')])
q_wi_2.complete()

q_wi_3 = get_all_records(member)
p1 = BinOp(f('project').f('status'), NEQ, AtomValue(9))
p2 = BinOp(f('project').f('is_public'), EQ, AtomValue(True))
p3 = BinOp(f('user_id'), EQ, Parameter('puid1'))
p4 = BinOp(f('user_id'), EQ, Parameter('puid2'))
pred = ConnectOp(ConnectOp(p1, AND, p3), OR,\
ConnectOp(ConnectOp(p1, AND, p2), AND, p4))
q_wi_3.project([f('user_id'), f('project_id')])
q_wi_3.pfilter(pred)
q_wi_3.complete()

# NcnQ: 3
# NSQL: 4