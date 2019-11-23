from redmine_schema import *
#  [1m[36mProject Load (0.3ms)[0m  [1m[34mSELECT  `projects`.* FROM `projects` WHERE `projects`.`id` = 118986 LIMIT 1[0m
#   [1m[35m (0.5ms)[0m  [1m[34mSELECT `enabled_modules`.`name` FROM `enabled_modules` WHERE `enabled_modules`.`project_id` = 118986[0m
#   [1m[36mMember Load (0.6ms)[0m  [1m[34mSELECT `members`.* FROM `members` INNER JOIN `users` ON `users`.`id` = `members`.`user_id` WHERE `members`.`project_id` = 118986 AND `users`.`type` = 'User' AND `users`.`status` = 1[0m
#   [1m[36mProject Load (66.0ms)[0m  [1m[34mSELECT `projects`.* FROM `projects` WHERE `projects`.`parent_id` = 118986 AND (projects.status <> 9) ORDER BY `projects`.`lft` ASC[0m
#   [1m[36mNews Load (0.7ms)[0m  [1m[34mSELECT  `news`.* FROM `news` WHERE `news`.`project_id` = 118986 ORDER BY news.created_on DESC LIMIT 5[0m
#   [1m[36mUser Load (0.8ms)[0m  [1m[34mSELECT `users`.* FROM `users` WHERE `users`.`type` IN ('User', 'AnonymousUser') AND `users`.`id` IN (552274, 230616, 450110, 431449, 496418)[0m
#   [1m[36mProject Load (0.2ms)[0m  [1m[34mSELECT `projects`.* FROM `projects` WHERE `projects`.`id` = 118986[0m
#   [1m[35m (19106.4ms)[0m  [1m[34mSELECT COUNT(*) AS count_all, `issues`.`tracker_id` AS issues_tracker_id FROM `issues` INNER JOIN `projects` ON `projects`.`id` = `issues`.`project_id` INNER JOIN `issue_statuses` ON `issue_statuses`.`id` = `issues`.`status_id` 
#   WHERE (projects.status <> 9 AND EXISTS (SELECT 1 AS one FROM enabled_modules em WHERE em.project_id = projects.id AND em.name='issue_tracking')) 
#   AND `issue_statuses`.`is_closed` = FALSE AND ((projects.id = 118986 OR (projects.lft > 1 AND projects.rgt < 77927))) 
#   GROUP BY `issues`.`tracker_id`[0m
#   [1m[36mTracker Load (0.4ms)[0m  [1m[34mSELECT `trackers`.* FROM `trackers` WHERE `trackers`.`id` IN (1, 2, 3, 4, 5, 6, 7, 8, 9, 10)[0m
#   [1m[35m (18440.2ms)[0m  [1m[34mSELECT COUNT(*) AS count_all, `issues`.`tracker_id` AS issues_tracker_id FROM `issues` INNER JOIN `projects` ON `projects`.`id` = `issues`.`project_id` 
#   WHERE (projects.status <> 9 AND EXISTS (SELECT 1 AS one FROM enabled_modules em WHERE em.project_id = projects.id AND em.name='issue_tracking')) 
#   AND ((projects.id = 118986 OR (projects.lft > 1 AND projects.rgt < 77927))) GROUP BY `issues`.`tracker_id`[0m
#   [1m[36mCACHE Tracker Load (0.0ms)[0m  [1m[34mSELECT `trackers`.* FROM `trackers` WHERE `trackers`.`id` IN (1, 2, 3, 4, 5, 6, 7, 8, 9, 10)[0m
#   [1m[36mProject Load (0.3ms)[0m  [1m[34mSELECT `projects`.`id`, `projects`.`name`, `projects`.`identifier`, `projects`.`lft`, `projects`.`rgt` FROM `projects` INNER JOIN `members` ON `projects`.`id` = `members`.`project_id` WHERE `members`.`user_id` = 1 AND `projects`.`status` != 9 AND `projects`.`status` = 1[0m
#   [1m[36mProject Load (0.4ms)[0m  [1m[34mSELECT `projects`.* FROM `projects` WHERE (projects.lft < 1 AND projects.rgt > 77927) AND (projects.status <> 9) ORDER BY `projects`.`lft` ASC[0m
#   [1m[36mBoard Exists (0.3ms)[0m  [1m[34mSELECT  1 AS one FROM `boards` WHERE `boards`.`project_id` = 118986 LIMIT 1[0m
# Completed 200 OK in 37687ms (Views: 33.5ms | ActiveRecord: 37625.1ms)

q_ps_1 = get_all_records(project)
q_ps_1.pfilter(BinOp(f('id'), EQ, Parameter('pid')))
q_ps_1.finclude(f('enabled_modules'), projection=[f('name')])
q_ps_1.finclude(f('members'), pfilter=BinOp(f('user').f('status'), EQ, AtomValue(1)))
q_ps_1.finclude(f('news'), projection=[f('title'), f('author_id')])
q_ps_1.get_include(f('news')).orderby([f('created_on')])
#q_ps_1.get_include(f('members')).finclude(f('user'))
q_ps_1.complete()


q_ps_2 = get_all_records(tracker)
p1 = BinOp(f('status'), NEQ, AtomValue(9))
p2_1 = BinOp(f('name'), EQ, AtomValue('issue_tracking')) # enabled_modules
p2 = SetOp(f('enabled_modules'), EXIST, p2_1)
p3 = BinOp(f('id'), EQ, Parameter('pid1')) #project
p4 = BinOp(f('lft'), GE, Parameter('pid2')) #project
p5 = BinOp(f('rgt'), LE, Parameter('pid3')) #project
# p1 && p2 && (p3 || (p4 && p5))
pred_id = ConnectOp(ConnectOp(p1, AND, p2), AND, p3)
pred_lft_rgt = ConnectOp(ConnectOp(p1, AND, p2), AND, ConnectOp(p4, AND, p5))
q_ps_2.finclude(f('projects'), pfilter=ConnectOp(pred_id, OR, pred_lft_rgt), projection=[])
q_ps_2.finclude(f('issues'), pfilter=BinOp(f('status').f('is_closed'), EQ, AtomValue(False)), projection=[])
q_ps_2.get_include(f('issues')).aggr(UnaryExpr(COUNT), 'counti')
q_ps_2.get_include(f('projects')).aggr(UnaryExpr(COUNT), 'countp')
q_ps_2.complete()

q_ps_3 = get_all_records(project)
q_ps_3.pfilter(BinOp(f('status'), NEQ, AtomValue(9)))
q_ps_3.pfilter(ConnectOp(BinOp(f('lft'), GE, Parameter('pid2')), AND, BinOp(f('rgt'), LE, Parameter('pid3'))))
q_ps_3.orderby([f('lft')])
q_ps_3.complete()

#q_ii_2

# NcnQ: 3
# NSQL: 6
