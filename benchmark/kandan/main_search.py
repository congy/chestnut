from .kandan_schema import *
# def search
#     minimum_query_length = 3

#     if params[:query] and params[:query].length >= minimum_query_length
#       @activities = Activity.includes(:user).where("LOWER(content) LIKE ?", "%#{params[:query]}%").limit(params[:limit] || 100).all
#     end

#     respond_to do |format|
#       format.html
#       format.json { render :json => @activities.to_json(:include => :user) }
#     end
#   end

q_ms_1 = get_all_records(activity)
q_ms_1.finclude(f('user'), projection=[f('id'),f('username')])
q_ms_1.pfilter(BinOp(f('content'), SUBSTR, Parameter('keyword')))
q_ms_1.return_limit(100)
q_ms_1.complete()
