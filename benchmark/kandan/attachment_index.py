from .kandan_schema import *

q_ti_1 = get_all_records(attachment)
q_ti_1.pfilter(BinOp(f('channel').f('id'), EQ, Parameter('channel_id')))
q_ti_1.orderby([f('created_at')], ascending=False)
q_ti_1.complete()