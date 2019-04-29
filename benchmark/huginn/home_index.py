from huginn_schema import *

# SELECT  `users`.* FROM `users` WHERE `users`.`id` = 1 ORDER BY `users`.`id` ASC LIMIT 1
# SELECT  `agents`.* FROM `agents` WHERE `agents`.`user_id` = 1 AND (type like 'Agents::Twitter%') ORDER BY agents.created_at desc LIMIT 1
# SELECT  `agents`.* FROM `agents` WHERE `agents`.`user_id` = 1 AND `agents`.`type` = 'Agents::BasecampAgent' ORDER BY agents.created_at desc LIMIT 1
# SELECT COUNT(*) FROM `agents` WHERE `agents`.`user_id` = 1
# SELECT COUNT(*) FROM `events` WHERE `events`.`user_id` = 1 AND (events.created_at > '2019-04-20 16:26:35.270740')
# SELECT COUNT(*) FROM `events` WHERE `events`.`user_id` = 1
# SELECT `agents`.`name`, `agents`.`id` FROM `agents` WHERE `agents`.`user_id` = 1 ORDER BY agents.created_at desc

q_hi_1 = get_all_records(agent)
q_hi_1.pfilter(BinOp(f('user_id'), EQ, Parameter('user_id')))
q_hi_1.pfilter(BinOp(f('type'), EQ, Parameter('type')))
q_hi_1.orderby([f('created_at')])
q_hi_1.return_limit(1)
q_hi_1.project('*')
q_hi_1.complete()

q_hi_2 = get_all_records(agent)
q_hi_2.pfilter(BinOp(f('user_id'), EQ, Parameter('user_id')))
q_hi_2.aggr(UnaryExpr(COUNT), 'agent_count')
q_hi_2.complete()

q_hi_3 = get_all_records(event)
q_hi_3.pfilter(BinOp(f('user_id'), EQ, Parameter('user_id')))
q_hi_3.pfilter(BinOp(f('created_at'), LT, Parameter('last_create')))
q_hi_3.aggr(UnaryExpr(COUNT), 'events_count')
q_hi_3.complete()