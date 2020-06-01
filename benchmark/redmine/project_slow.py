from .redmine_schema import *

"""
p = Project.where((pending_delete == False && namespace.owner_id == ? && namespace.type == NULL) ||
(pending_delete == False && namespace.owner_id == ? && namespace.type == 'GROUP' && exists(members, type == 'GroupMember' && source_type == 'Namespace' && user_id == ?)) ||
(pending_delete == False && exists(members, type == 'ProjectMember' && source_type == 'Project' && user_id == ?)) ||
(pending_delete == False && namespace.type == 'GROUP' && exists(members, type == 'GroupMember' && source_type == 'Namespace' && user_id == ?) && exist(namespace.project_links, True)) ||
)
"""


"""
FROM `issues` INNER JOIN `projects` ON `projects`.`id` = `issues`.`project_id` 
INNER JOIN `issue_statuses` ON `issue_statuses`.`id` = `issues`.`status_id` 
LEFT OUTER JOIN `users` ON `users`.`id` = `issues`.`assigned_to_id` 
LEFT OUTER JOIN `trackers` ON `trackers`.`id` = `issues`.`tracker_id` 
LEFT OUTER JOIN `enumerations` ON `enumerations`.`id` = `issues`.`priority_id` 
AND `enumerations`.`type` IN ('IssuePriority') 
LEFT OUTER JOIN `issue_categories` ON `issue_categories`.`id` = `issues`.`category_id` 
LEFT OUTER JOIN `versions` ON `versions`.`id` = `issues`.`fixed_version_id` 
WHERE (projects.status <> 9 AND projects.id IN (SELECT em.project_id FROM enabled_modules em WHERE em.name='issue_tracking')) 
AND ((issues.status_id IN (SELECT id FROM issue_statuses WHERE is_closed=0)) 
AND (issues.tracker_id IN ('39')) AND projects.id = 37623)  
ORDER BY issues.id DESC LIMIT 25 OFFSET 0
"""

q_pl = get_all_records(project)
q_pl.pfilter(BinOp(f('status'), NEQ, AtomValue(9)))
q_pl.pfilter(SetOp(f('enabled_modules'), EXIST, BinOp(f('name'), EQ, AtomValue('issue_tracking'))))
q_pl.finclude(f('issues'))
q_pl_1 = q_pl.get_include(f('issues'))
q_pl_1.finclude(f('user'))
q_pl_1.finclude(f('tracker'))
q_pl_1.finclude(f('version'))
#q_pl_1.pfilter(BinOp(f('project').f('status'), NEQ, AtomValue(9)))
#q_pl_1.pfilter(SetOp(f('project').f('enabled_modules'), EXIST, BinOp(f('name'), EQ, AtomValue('issue_tracking'))))
q_pl_1.pfilter(BinOp(f('tracker').f('id'), EQ, Parameter('trackerid')))
q_pl_1.pfilter(BinOp(f('enumeration').f('type'), EQ, AtomValue('IssuePriority')))
q_pl_1.pfilter(BinOp(f('status').f('is_closed'), EQ, AtomValue(False)))
q_pl_1.orderby([f('id')])
q_pl_1.return_limit(25)
q_pl.complete()

# NcnQ: 1
# NSQL: 2