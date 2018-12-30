from kandan_schema import *
# @channels.each do |channel|
#       activities = []
#       more_activities = (channel.activities.count > Kandan::Config.options[:per_page])
#       channel.activities.order('id DESC').includes(:user).page.each do |activity|
#         activities.push activity.attributes.merge({
#           :user => activity.user_or_deleted_user.as_json(:only => [:id, :email, :first_name, :last_name, :gravatar_hash, :active, :locale, :username, :avatar_url])
#         })
#       end
#     end

# SELECT COUNT(*) FROM `activities`  WHERE `activities`.`channel_id` = 1

# SELECT  `activities`.* FROM `activities`  WHERE `activities`.`channel_id` = 1 
# ORDER BY id DESC LIMIT 30 OFFSET 0

# SELECT `users`.* FROM `users`  WHERE `users`.`id` IN (?)

q_ci_1 = get_all_records(channel)
q_ci_1.pfilter(BinOp(f('id'), EQ, Parameter('channel_id')))
#q_ci_1.orderby([f('created_at')], ascending=False)
q_ci_1.finclude(f('activities'), projection=[f('content'), f('action'), f('created_at'), f('updated_at')])
q_ci_1.get_include(f('activities')).orderby([f('id')])
q_ci_1.get_include(f('activities')).aggr(UnaryExpr(COUNT), 'count')
q_ci_1.get_include(f('activities')).finclude(f('user'), projection=[f('id'),f('username')])
q_ci_1.complete()
