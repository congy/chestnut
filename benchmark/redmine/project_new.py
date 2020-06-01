from .redmine_schema import *


q_pn_1 = AddObject(project, {QueryField('name', table=project): Parameter('name')})
q_pn_2 = ChangeAssociation(QueryField('issues', table=project), INSERT, Parameter('project_id'), Parameter('issue_id'))
q_pn_3 = ChangeAssociation(QueryField('trackers', table=project), INSERT, Parameter('project_id'), Parameter('tracker_id'))
q_pn_4 = ChangeAssociation(QueryField('news', table=project), INSERT, Parameter('project_id'), Parameter('news_id'))
q_pn_5 = ChangeAssociation(QueryField('enabled_modules', table=project), INSERT, Parameter('project_id'), Parameter('enabled_module_id'))
q_pn_6 = ChangeAssociation(QueryField('roles', table=member), INSERT, Parameter('member_id'), Parameter('role_id'))
q_pn_7 = ChangeAssociation(QueryField('members', table=user), INSERT, Parameter('user_id'), Parameter('member_id'))
