from .kandan_schema import *
# def index
#     # TODO can be divided into two actions

#     first_activity_id = 1
#     if params[:oldest]
#       activities = Channel.find(params[:channel_id]).
#         activities.
#         includes(:user).
#         order('id DESC').
#         where("id < ?", params[:oldest]).
#         limit(Kandan::Config.options[:per_page])
#     else
#       activities = Channel.find(params[:channel_id]).
#         activities.
#         includes(:user).
#         order('id DESC').
#         limit(Kandan::Config.options[:per_page])
#     end

#     first_activity = Activity.order('id').where(:channel_id => params[:channel_id]).first
#     first_activity_id = first_activity.id if not first_activity.nil?

#     # NOTE if the action is accessed then there's definitely activities, so skip check for #first to be nil
#     more_activities = first_activity_id < (activities.last.try(:id).presence || 1)

#     activities.each { |a| a.user ||= User.deleted_user }

#     respond_to do |format|
#       format.json { render :text => {:activities => activities.reverse, :more_activities => more_activities }.to_json(:include => :user) }
#     end
#   end

q_ai_1 = get_all_records(activity)
q_ai_1.pfilter(BinOp(f('channel').f('id'), EQ, Parameter('channel_id')))
q_ai_1.pfilter(BinOp(f('id'), LE, Parameter('oldest')))
q_ai_1.finclude(f('user'), projection=[f('id'),f('username')])
q_ai_1.orderby([f('id')], ascending=False)
q_ai_1.return_limit(40)
q_ai_1.complete()

q_ai_2 = get_all_records(activity)
q_ai_2.pfilter(BinOp(f('channel').f('id'), EQ, Parameter('channel_id')))
q_ai_2.finclude(f('user'), projection=[f('id'),f('username')])
q_ai_2.orderby([f('id')], ascending=False)
q_ai_2.return_limit(40)
q_ai_2.complete()

q_ai_3 = get_all_records(activity)
q_ai_3.pfilter(BinOp(f('channel').f('id'), EQ, Parameter('channel_id')))
q_ai_3.orderby([f('id')], ascending=True)
q_ai_3.return_limit(1)
q_ai_3.complete()


