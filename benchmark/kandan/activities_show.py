from .kandan_schema import *

# def show
#     @activity = Activity.find params[:id]
#     respond_to do |format|
#       format.html do
#         render :inline => "<pre><%= @activity.content %></pre>", :content_type => 'text/html'
#       end
#       format.json { render :json => @activity }
#     end
#   end


q_as_1 = get_all_records(activity)
q_as_1.pfilter(BinOp(f('id'), EQ, Parameter('id')))
q_as_1.complete()