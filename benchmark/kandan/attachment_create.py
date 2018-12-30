from kandan_schema import *

q_tc_w1 = AddObject(attachment, {f('created_at'): Parameter('new_created_at'), \
                              f('updated_at'): Parameter('new_updated_at')})

q_tc_w2 = ChangeAssociation(QueryField('attachments',table=channel), INSERT, Parameter('channel_id'), Parameter('attachment_id'))                             
q_tc_w3 = ChangeAssociation(QueryField('attachments',table=user), INSERT, Parameter('user_id'), Parameter('attachment_id'))                             