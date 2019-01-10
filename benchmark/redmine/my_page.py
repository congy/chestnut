from redmine_schema import *
  # [1m[36mTracker Load (5933.9ms)[0m  [1m[34mSELECT DISTINCT `trackers`.* FROM `trackers` INNER JOIN `projects_trackers` ON `projects_trackers`.`tracker_id` = `trackers`.`id` INNER JOIN `projects` ON `projects`.`id` = `projects_trackers`.`project_id` WHERE (projects.status <> 9 AND EXISTS (SELECT 1 AS one FROM enabled_modules em WHERE em.project_id = projects.id AND em.name='issue_tracking')) ORDER BY `trackers`.`position` ASC[0m
  # [1m[35m (0.5ms)[0m  [1m[34mSELECT `users`.`id` FROM `users` INNER JOIN `groups_users` ON `users`.`id` = `groups_users`.`group_id` WHERE `users`.`type` IN ('Group', 'GroupBuiltin', 'GroupAnonymous', 'GroupNonMember') AND `groups_users`.`user_id` = 1[0m
  # [1m[35mSQL (0.8ms)[0m  [1m[34mSELECT  `issues`.`id` AS t0_r0, `issues`.`tracker_id` AS t0_r1, `issues`.`project_id` AS t0_r2, `issues`.`subject` AS t0_r3, `issues`.`description` AS t0_r4, `issues`.`due_date` AS t0_r5, `issues`.`category_id` AS t0_r6, `issues`.`status_id` AS t0_r7, `issues`.`assigned_to_id` AS t0_r8, `issues`.`priority_id` AS t0_r9, `issues`.`fixed_version_id` AS t0_r10, `issues`.`author_id` AS t0_r11, `issues`.`lock_version` AS t0_r12, `issues`.`created_on` AS t0_r13, `issues`.`updated_on` AS t0_r14, `issues`.`start_date` AS t0_r15, `issues`.`done_ratio` AS t0_r16, `issues`.`estimated_hours` AS t0_r17, `issues`.`parent_id` AS t0_r18, `issues`.`root_id` AS t0_r19, `issues`.`lft` AS t0_r20, `issues`.`rgt` AS t0_r21, `issues`.`is_private` AS t0_r22, `issues`.`closed_on` AS t0_r23, `issue_statuses`.`id` AS t1_r0, `issue_statuses`.`name` AS t1_r1, `issue_statuses`.`is_closed` AS t1_r2, `issue_statuses`.`position` AS t1_r3, `issue_statuses`.`default_done_ratio` AS t1_r4, `projects`.`id` AS t2_r0, `projects`.`name` AS t2_r1, `projects`.`description` AS t2_r2, `projects`.`homepage` AS t2_r3, `projects`.`is_public` AS t2_r4, `projects`.`parent_id` AS t2_r5, `projects`.`created_on` AS t2_r6, `projects`.`updated_on` AS t2_r7, `projects`.`identifier` AS t2_r8, `projects`.`status` AS t2_r9, `projects`.`lft` AS t2_r10, `projects`.`rgt` AS t2_r11, `projects`.`inherit_members` AS t2_r12, `projects`.`default_version_id` AS t2_r13, `projects`.`default_assigned_to_id` AS t2_r14 FROM `issues` INNER JOIN `projects` ON `projects`.`id` = `issues`.`project_id` INNER JOIN `issue_statuses` ON `issue_statuses`.`id` = `issues`.`status_id` 
  # LEFT OUTER JOIN enumerations ON enumerations.id = issues.priority_id WHERE (projects.status <> 9 AND EXISTS (SELECT 1 AS one FROM enabled_modules em WHERE em.project_id = projects.id AND em.name='issue_tracking')) AND ((issues.status_id IN (SELECT id FROM issue_statuses WHERE is_closed=FALSE)) AND (issues.assigned_to_id IN ('1'))) ORDER BY enumerations.position DESC, issues.updated_on DESC LIMIT 10[0m
  # [1m[35m (0.3ms)[0m  [1m[34mSELECT COUNT(*) FROM `issues` INNER JOIN `projects` ON `projects`.`id` = `issues`.`project_id` INNER JOIN `issue_statuses` ON `issue_statuses`.`id` = `issues`.`status_id` WHERE (projects.status <> 9 AND EXISTS (SELECT 1 AS one FROM enabled_modules em WHERE em.project_id = projects.id AND em.name='issue_tracking')) AND ((issues.status_id IN (SELECT id FROM issue_statuses WHERE is_closed=FALSE)) AND (issues.assigned_to_id IN ('1')))[0m
  # [1m[36mCACHE Tracker Load (5290ms)[0m  [1m[34mSELECT DISTINCT `trackers`.* FROM `trackers` INNER JOIN `projects_trackers` ON `projects_trackers`.`tracker_id` = `trackers`.`id` INNER JOIN `projects` ON `projects`.`id` = `projects_trackers`.`project_id` WHERE (projects.status <> 9 AND EXISTS (SELECT 1 AS one FROM enabled_modules em WHERE em.project_id = projects.id AND em.name='issue_tracking')) ORDER BY `trackers`.`position` ASC[0m
  # [1m[36mCACHE IssuePriority Load (0.0ms)[0m  [1m[34mSELECT `enumerations`.* FROM `enumerations` WHERE `enumerations`.`type` IN ('IssuePriority') ORDER BY `enumerations`.`position` ASC[0m
  # 1m[35mSQL (0.6ms)[0m  [1m[34mSELECT  `issues`.`id` AS t0_r0, `issues`.`tracker_id` AS t0_r1, `issues`.`project_id` AS t0_r2, `issues`.`subject` AS t0_r3, `issues`.`description` AS t0_r4, `issues`.`due_date` AS t0_r5, `issues`.`category_id` AS t0_r6, `issues`.`status_id` AS t0_r7, `issues`.`assigned_to_id` AS t0_r8, `issues`.`priority_id` AS t0_r9, `issues`.`fixed_version_id` AS t0_r10, `issues`.`author_id` AS t0_r11, `issues`.`lock_version` AS t0_r12, `issues`.`created_on` AS t0_r13, `issues`.`updated_on` AS t0_r14, `issues`.`start_date` AS t0_r15, `issues`.`done_ratio` AS t0_r16, `issues`.`estimated_hours` AS t0_r17, `issues`.`parent_id` AS t0_r18, `issues`.`root_id` AS t0_r19, `issues`.`lft` AS t0_r20, `issues`.`rgt` AS t0_r21, `issues`.`is_private` AS t0_r22, `issues`.`closed_on` AS t0_r23, `issue_statuses`.`id` AS t1_r0, `issue_statuses`.`name` AS t1_r1, `issue_statuses`.`is_closed` AS t1_r2, `issue_statuses`.`position` AS t1_r3, `issue_statuses`.`default_done_ratio` AS t1_r4, `projects`.`id` AS t2_r0, `projects`.`name` AS t2_r1, `projects`.`description` AS t2_r2, `projects`.`homepage` AS t2_r3, `projects`.`is_public` AS t2_r4, `projects`.`parent_id` AS t2_r5, `projects`.`created_on` AS t2_r6, `projects`.`updated_on` AS t2_r7, `projects`.`identifier` AS t2_r8, `projects`.`status` AS t2_r9, `projects`.`lft` AS t2_r10, `projects`.`rgt` AS t2_r11, `projects`.`inherit_members` AS t2_r12, `projects`.`default_version_id` AS t2_r13, `projects`.`default_assigned_to_id` AS t2_r14 FROM `issues` INNER JOIN `projects` ON `projects`.`id` = `issues`.`project_id` INNER JOIN `issue_statuses` ON `issue_statuses`.`id` = `issues`.`status_id` 
  # WHERE (projects.status <> 9 AND EXISTS (SELECT 1 AS one FROM enabled_modules em WHERE em.project_id = projects.id AND em.name='issue_tracking')) AND ((issues.status_id IN (SELECT id FROM issue_statuses WHERE is_closed=FALSE)) AND (issues.author_id IN ('1'))) ORDER BY issues.updated_on DESC LIMIT 10[0m
  # [1m[35m (0.3ms)[0m  [1m[34mSELECT COUNT(*) FROM `issues` INNER JOIN `projects` ON `projects`.`id` = `issues`.`project_id` INNER JOIN `issue_statuses` ON `issue_statuses`.`id` = `issues`.`status_id` WHERE (projects.status <> 9 AND EXISTS (SELECT 1 AS one FROM enabled_modules em WHERE em.project_id = projects.id AND em.name='issue_tracking')) AND ((issues.status_id IN (SELECT id FROM issue_statuses WHERE is_closed=FALSE)) AND (issues.author_id IN ('1')))[0m
  
q_mp_1 = get_all_records(tracker)
q_mp_1.pfilter(SetOp(f('projects'), EXIST, ConnectOp(BinOp(f('status'), NEQ, AtomValue(9)), AND, \
    SetOp(f('enabled_modules'), EXIST, BinOp(f('name'), EQ, AtomValue('issue_tracking'))))))
q_mp_1.orderby([f('position')])
q_mp_1.complete()

q_mp_2 = get_all_records(issue)
q_mp_2.pfilter(BinOp(f('project').f('status'), NEQ, AtomValue(9)))
q_mp_2.pfilter(SetOp(f('project').f('enabled_modules'), EXIST, BinOp(f('name'), EQ, AtomValue('issue_tracking'))))
q_mp_2.pfilter(ConnectOp(BinOp(f('assigned_to_id'), EQ, Parameter('assigned_to')), AND, 
SetOp(f('status'), EXIST, BinOp(f('is_closed'), EQ, AtomValue(False)))))
q_mp_2.aggr(UnaryExpr(COUNT), 'count_issue')
q_mp_2.project('*')
q_mp_2.complete()

q_mp_3 = get_all_records(issue)
q_mp_3.pfilter(BinOp(f('project').f('status'), NEQ, AtomValue(9)))
q_mp_3.pfilter(SetOp(f('project').f('enabled_modules'), EXIST, BinOp(f('name'), EQ, AtomValue('issue_tracking'))))
q_mp_3.pfilter(ConnectOp(BinOp(f('author_id'), EQ, Parameter('author_id')), AND, 
SetOp(f('status'), EXIST, BinOp(f('is_closed'), EQ, AtomValue(False)))))
q_mp_3.aggr(UnaryExpr(COUNT), 'count')

# q_mp_2 = get_all_records(project)
# q_mp_2.pfilter(BinOp(f('status'), NEQ, AtomValue(9)))
# q_mp_2.pfilter(SetOp(f('enabled_modules'), EXIST, BinOp(f('name'), EQ, AtomValue('issue_tracking'))))
# q_mp_2.finclude(f('issues'), pfilter=ConnectOp(BinOp(f('assigned_to_id'), EQ, Parameter('assigned_to')), AND, \
#      BinOp(f('status').f('is_closed'), EQ, AtomValue(False))))
# q_mp_2.get_include(f('issues')).aggr(UnaryExpr(COUNT), 'count')
# q_mp_2.complete()

# q_mp_3 = get_all_records(project)
# q_mp_3.pfilter(BinOp(f('status'), NEQ, AtomValue(9)))
# q_mp_3.pfilter(SetOp(f('enabled_modules'), EXIST, BinOp(f('name'), EQ, AtomValue('issue_tracking'))))
# q_mp_3.finclude(f('issues'), pfilter=ConnectOp(BinOp(f('author_id'), EQ, Parameter('author')), AND, \
#      BinOp(f('status').f('is_closed'), EQ, AtomValue(False))))
# q_mp_3.get_include(f('issues')).aggr(UnaryExpr(COUNT), 'count_issue')
# q_mp_3.complete()

# NcnQ: 3
# NSQL: 5