from .kandan_schema import *
# def find_channel_by_name
#     @channel = Channel.where("LOWER(name) = ?", params['id'].downcase).first
#   end

q_cs_1 = get_all_records(channel)
q_cs_1.pfilter(BinOp(f('name'), EQ, Parameter('name')))
q_cs_1.complete()