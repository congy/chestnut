from .redmine_schema import *
#   [1m[36mTracker Load (4091.7ms)[0m  [1m[34mSELECT DISTINCT `trackers`.* FROM `trackers` INNER JOIN `projects_trackers` ON `projects_trackers`.`tracker_id` = `trackers`.`id` INNER JOIN `projects` ON `projects`.`id` = `projects_trackers`.`project_id` WHERE (projects.status <> 9 AND EXISTS (SELECT 1 AS one FROM enabled_modules em WHERE em.project_id = projects.id AND em.name='issue_tracking')) ORDER BY `trackers`.`position` ASC[0m
#   [1m[36mIssuePriority Load (0.3ms)[0m  [1m[34mSELECT `enumerations`.* FROM `enumerations` WHERE `enumerations`.`type` IN ('IssuePriority') ORDER BY `enumerations`.`position` ASC[0m
#   [1m[35m (43087.8ms)[0m  [1m[34mSELECT COUNT(*) FROM `issues` INNER JOIN `projects` ON `projects`.`id` = `issues`.`project_id` INNER JOIN `issue_statuses` ON `issue_statuses`.`id` = `issues`.`status_id` WHERE (projects.status <> 9 AND EXISTS (SELECT 1 AS one FROM enabled_modules em WHERE em.project_id = projects.id AND em.name='issue_tracking')) AND ((issues.status_id IN (SELECT id FROM issue_statuses WHERE is_closed=TRUE)))[0m
#   [1m[35mSQL (55716.6ms)[0m  [1m[34mSELECT  `issues`.`id` AS t0_r0, `issues`.`tracker_id` AS t0_r1, `issues`.`project_id` AS t0_r2, `issues`.`subject` AS t0_r3, `issues`.`description` AS t0_r4, `issues`.`due_date` AS t0_r5, `issues`.`category_id` AS t0_r6, `issues`.`status_id` AS t0_r7, `issues`.`assigned_to_id` AS t0_r8, `issues`.`priority_id` AS t0_r9, `issues`.`fixed_version_id` AS t0_r10, `issues`.`author_id` AS t0_r11, `issues`.`lock_version` AS t0_r12, `issues`.`created_on` AS t0_r13, `issues`.`updated_on` AS t0_r14, `issues`.`start_date` AS t0_r15, `issues`.`done_ratio` AS t0_r16, `issues`.`estimated_hours` AS t0_r17, `issues`.`parent_id` AS t0_r18, `issues`.`root_id` AS t0_r19, `issues`.`lft` AS t0_r20, `issues`.`rgt` AS t0_r21, `issues`.`is_private` AS t0_r22, `issues`.`closed_on` AS t0_r23, `issue_statuses`.`id` AS t1_r0, `issue_statuses`.`name` AS t1_r1, `issue_statuses`.`is_closed` AS t1_r2, `issue_statuses`.`position` AS t1_r3, `issue_statuses`.`default_done_ratio` AS t1_r4, `projects`.`id` AS t2_r0, `projects`.`name` AS t2_r1, `projects`.`description` AS t2_r2, `projects`.`homepage` AS t2_r3, `projects`.`is_public` AS t2_r4, `projects`.`parent_id` AS t2_r5, `projects`.`created_on` AS t2_r6, `projects`.`updated_on` AS t2_r7, `projects`.`identifier` AS t2_r8, `projects`.`status` AS t2_r9, `projects`.`lft` AS t2_r10, `projects`.`rgt` AS t2_r11, `projects`.`inherit_members` AS t2_r12, `projects`.`default_version_id` AS t2_r13, `projects`.`default_assigned_to_id` AS t2_r14 FROM `issues` 
#   INNER JOIN `projects` ON `projects`.`id` = `issues`.`project_id` INNER JOIN `issue_statuses` ON `issue_statuses`.`id` = `issues`.`status_id` WHERE (projects.status <> 9 AND EXISTS (SELECT 1 AS one FROM enabled_modules em WHERE em.project_id = projects.id AND em.name='issue_tracking')) AND ((issues.status_id IN (SELECT id FROM issue_statuses WHERE is_closed=TRUE))) ORDER BY issues.id DESC LIMIT 25 OFFSET 0[0m
#   [1m[36mIssuePriority Load (0.3ms)[0m  [1m[34mSELECT `enumerations`.* FROM `enumerations` WHERE `enumerations`.`type` IN ('IssuePriority') AND `enumerations`.`id` = 0 ORDER BY `enumerations`.`position` ASC[0m
#   [1m[36mTracker Load (0.3ms)[0m  [1m[34mSELECT `trackers`.* FROM `trackers` WHERE `trackers`.`id` IN (9, 1, 3, 4, 2, 10, 7, 5, 8)[0m
#   Rendering issues/index.html.erb within layouts/base
#   [1m[36mIssueStatus Load (0.2ms)[0m  [1m[34mSELECT `issue_statuses`.* FROM `issue_statuses` ORDER BY `issue_statuses`.`position` ASC[0m
#   [1m[36mProject Load (0.3ms)[0m  [1m[34mSELECT `projects`.`id`, `projects`.`name`, `projects`.`identifier`, `projects`.`lft`, `projects`.`rgt` FROM `projects` INNER JOIN `members` ON `projects`.`id` = `members`.`project_id` WHERE `members`.`user_id` = 1 AND `projects`.`status` != 9 AND `projects`.`status` = 1[0m
# Completed 200 OK in 103113ms (Views: 53.0ms | ActiveRecord: 103039.5ms)


# q_ii_0 = get_all_records(enumeration)
# q_ii_0.pfilter(BinOp(f('id'), EQ, Parameter('euid')))
# q_ii_0.finclude(f('trackers'))
# q_ii_0.project('*')
# q_ii_0.complete()

q_ii_1 = get_all_records(issue)
q_ii_1.pfilter(BinOp(f('project').f('status'), NEQ, AtomValue(9)))
q_ii_1.pfilter(SetOp(f('project').f('enabled_modules'), EXIST, BinOp(f('name'), EQ, AtomValue('issue_tracking'))))
q_ii_1.pfilter(BinOp(f('status').f('is_closed'), EQ, AtomValue(True)))
q_ii_1.aggr(UnaryExpr(COUNT), 'count')
q_ii_1.orderby([f('id')])
q_ii_1.project('*')
q_ii_1.return_limit(25)
q_ii_1.complete()

# q_ii_1 = get_all_records(project)
# q_ii_1.pfilter(BinOp(f('status'), NEQ, AtomValue(9)))
# q_ii_1.pfilter(SetOp(f('enabled_modules'), EXIST, BinOp(f('name'), EQ, AtomValue('issue_tracking'))))
# q_ii_1.finclude(f('issues'), pfilter=BinOp(f('status').f('is_closed'), EQ, AtomValue(True)))
# q_ii_1.get_include(f('issues')).aggr(UnaryExpr(COUNT), 'count')
# q_ii_1.get_include(f('issues')).orderby([f('id')])
# q_ii_1.orderby([f('id')])
# q_ii_1.return_limit(25)
# q_ii_1.complete()

q_ii_2 = get_all_records(project)
q_ii_2.pfilter(BinOp(f('status'), EQ, AtomValue(1)))
q_ii_2.pfilter(BinOp(f('status'), NEQ, AtomValue(9)))
q_ii_2.pfilter(SetOp(f('members'), EXIST, BinOp(f('user').f('id'), EQ, Parameter('user_id'))))
q_ii_2.complete()


# NcnQ: 3
# NSQL: 5