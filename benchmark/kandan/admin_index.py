from kandan_schema import *
# def index
#       @settings = Setting.my_settings
#       @all_users = User.find(:all, :conditions => ["id != ?", current_user.id])

#       @waiting_for_approval_users = []
#       @approved_users = []

#       # Iterate over the array to get approved and non-approved users
#       @all_users.each{|user| user.registration_status.waiting_approval? ? @waiting_for_approval_users.push(user) : @approved_users.push(user) }
#     end

q_di_1 = get_all_records(user)
q_di_1.pfilter(BinOp(f('id'), NEQ, Parameter('uid')))
q_di_1.project([f('id'),f('username')])
q_di_1.complete()