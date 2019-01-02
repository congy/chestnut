from lobsters_schema import *
# SELECT COUNT(*) FROM `messages`  WHERE `messages`.`recipient_user_id` = 1 AND 
# `messages`.`deleted_by_recipient` = 0

# SELECT `messages`.* FROM `messages`  WHERE `messages`.`recipient_user_id` = 1 AND 
# `messages`.`deleted_by_recipient` = 0

# SELECT `users`.* FROM `users`  WHERE `users`.`id` IN (?)

q_mi_1 = get_all_records(message)
q_mi_1.pfilter(BinOp(f('recipient').f('id'), EQ, Parameter('user_id')))
q_mi_1.pfilter(BinOp(f('deleted_by_recipient'), EQ, AtomValue(False)))
q_mi_1.aggr(UnaryExpr(COUNT), 'msg_count')
q_mi_1.finclude(f('author'), projection=[f('username')])
q_mi_1.complete()
