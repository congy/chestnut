from .kandan_schema import *
# def toggle_admin
#       user_id = params[:user_id]

#       user = User.find(user_id)

#       user.is_admin = !user.is_admin?

#       user.save!

#       render :json => user, :status => 200
#     end

q_dt_1 = UpdateObject(user, Parameter('user_id'), \
    updated_fields={QueryField('is_admin', table=user):Parameter('new_is_admin')})
