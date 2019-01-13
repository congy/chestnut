from lobsters_schema import *
# SELECT  1 AS one FROM `messages`  WHERE `messages`.`short_id` = 'fmowuz' LIMIT 1

# SELECT  `users`.* FROM `users`  WHERE `users`.`id` = 208 LIMIT 1

# SELECT  `users`.* FROM `users`  WHERE `users`.`id` = 1 LIMIT 1

# INSERT INTO `messages` (`author_user_id`, `body`, `created_at`, `recipient_user_id`, `short_id`, `subject`) VALUES (1, 'uihguifdhbhabkdhviuahdf', '2016-10-26 21:26:28', 208, 'fmowuz', 'iufdva')

# SELECT COUNT(*) FROM `messages`  WHERE `messages`.`recipient_user_id` = 208 AND 
# `messages`.`has_been_read` = 0 AND `messages`.`deleted_by_recipient` = 0

q_mc_1 = get_all_records(message)
q_mc_1.pfilter(BinOp(f('short_id'), EQ, Parameter('msg_short_id')))
q_mc_1.project([f('id')])
q_mc_1.complete()

q_mc_2 = get_all_records(user)
q_mc_2.pfilter(BinOp(f('id'), EQ, Parameter('user_id')))
q_mc_2.project('*')
q_mc_2.complete()

q_mc_3 = AddObject(message, {QueryField('body', table=message):Parameter('new_body'), \
QueryField('created_at', table=message):Parameter('new_created_at'), \
QueryField('short_id', table=message):Parameter('new_short_id'), \
QueryField('subject', table=message):Parameter('new_subject'),})
q_mc_4 = ChangeAssociation(QueryField('author_user', table=message), INSERT, Parameter('message_id'), Parameter('user_id'))
q_mc_5 = ChangeAssociation(QueryField('recipient_user', table=message), INSERT, Parameter('message_id'), Parameter('user_id'))

q_mc_6 = get_all_records(message)
q_mc_6.pfilter(BinOp(f('recipient_user').f('id'), EQ, Parameter('recipient_id')))
q_mc_6.pfilter(BinOp(f('has_been_read'), EQ, AtomValue(False)))
q_mc_6.pfilter(BinOp(f('deleted_by_recipient'), EQ, AtomValue(False)))
q_mc_6.aggr(UnaryExpr(COUNT), 'count')
q_mc_6.complete()
