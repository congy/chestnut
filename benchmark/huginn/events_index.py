from huginn_schema import *

# SELECT  `users`.* FROM `users` WHERE `users`.`id` = 1 ORDER BY `users`.`id` ASC LIMIT 1
# SELECT  `events`.* FROM `events` WHERE `events`.`user_id` = 1 ORDER BY events.created_at desc LIMIT 25 OFFSET 0
# SELECT `agents`.* FROM `agents` WHERE `agents`.`id` IN (8, 7, 2)
# SELECT `agents`.`name`, `agents`.`id` FROM `agents` WHERE `agents`.`user_id` = 1 ORDER BY agents.created_at desc

q_ei_1 = get_all_records(user)
q_ei_1.pfilter(BinOp(f('id'), EQ, Parameter('uid')))
q_ei_1.complete()


q_ei_2 = get_all_records(event)
q_ei_2.pfilter(BinOp(f('user_id'), EQ, Parameter('uid')))
q_ei_2.project('*')
q_ei_2.orderby([f('created_at')])
q_ei_2.return_limit(25)
q_ei_2.complete()

q_ei_3 = get_all_records(agent)
q_ei_3.pfilter(BinOp(f('user_id'), EQ, Parameter('user_id')))
q_ei_3.orderby([f('created_at')])
q_ei_3.return_limit(25)
q_ei_3.project('*')