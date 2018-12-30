from kandan_schema import *
# def update_user
#       user_id = params[:user_id]
#       action = params[:action_taken].to_s

#       user = User.find(user_id)

#       case action
#       when "activate", "approve"
#         user.activate!
#       when "suspend"
#         user.suspend!
#       end

#       render :json => user, :status => 200
#     end

q_du_1 = UpdateObject(user, Parameter('user_id'), \
    updated_fields={QueryField('active', table=user):Parameter('new_active'),\
                    QueryField('regstatus', table=user):Parameter('suspend')})
