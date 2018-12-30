from kandan_schema import *
# def create
#     @channel = Channel.new(params[:channel])
#     @channel.user_id = current_user.id
# end

q_cc_w1 = AddObject(channel, {f('name'): Parameter('new_name'), \
                              f('created_at'): Parameter('new_created_at'), \
                              f('updated_at'): Parameter('new_updated_at')})

q_cc_w2 = ChangeAssociation(QueryField('user',table=channel), INSERT, Parameter('channel_id'), Parameter('user_id'))                             