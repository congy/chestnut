from .kandan_schema import *
# def create
#     @activity = Channel.find(params[:channel_id]).activities.build(params[:activity])
#     @activity.user_id = current_user.id if @activity.action == "message"
# end

q_ac_w1 = AddObject(activity, {f('action'): Parameter('new_action'), \
                              f('content'): Parameter('new_content'), \
                              f('created_at'): Parameter('new_created_at'), \
                              f('updated_at'): Parameter('new_updated_at')})

q_ac_w2 = ChangeAssociation(QueryField('activities',table=channel), INSERT, Parameter('channel_id'), Parameter('activity_id'))                             
q_ac_w3 = ChangeAssociation(QueryField('activities',table=user), INSERT, Parameter('user_id'), Parameter('activity_id'))                             