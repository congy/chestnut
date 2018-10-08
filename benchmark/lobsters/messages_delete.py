from lobsters_schema import *
# SELECT  `messages`.* FROM `messages`  WHERE `messages`.`short_id` = 'vWnlSS'  ORDER BY `messages`.`id` ASC LIMIT 1

# SELECT  `users`.* FROM `users`  WHERE `users`.`id` = 1 LIMIT 1

# SELECT  `users`.* FROM `users`  WHERE `users`.`id` = 283 LIMIT 1

# UPDATE `messages` SET `deleted_by_recipient` = 1 WHERE `messages`.`id` = 6895

# SELECT COUNT(*) FROM `messages`  WHERE `messages`.`recipient_user_id` = 1 AND 
# `messages`.`has_been_read` = 0 AND `messages`.`deleted_by_recipient` = 0

q_md_1 = get_all_records(message)
q_md_1.pfilter(BinOp(f('short_id'), EQ, Parameter('msg_short_id')))
q_md_1.project('*')
q_md_1.finclude(f('author'))
q_md_1.finclude(f('recipient'))
q_md_1.complete()

q_md_2 = UpdateObject(message, Parameter('message_id'), {f('deleted_by_recipient'):AtomValue(True)})

#q_mc_6