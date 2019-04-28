from huginn_schema import *

# SELECT  `agents`.* FROM `agents` WHERE `agents`.`user_id` = 1 ORDER BY `agents`.`created_at` DESC LIMIT 25 OFFSET 0
# SELECT `links`.`receiver_id`, count(receiver_id) as id FROM `links` WHERE `links`.`receiver_id` IN (8, 1, 2, 3, 4, 5, 6, 7) GROUP BY `links`.`receiver_id`
# SELECT `links`.`source_id`, count(source_id) as id FROM `links` WHERE `links`.`source_id` IN (8, 1, 2, 3, 4, 5, 6, 7) GROUP BY `links`.`source_id`
# SELECT `agents`.`name`, `agents`.`id` FROM `agents` WHERE `agents`.`user_id` = 1 ORDER BY agents.created_at desc

q_ai_1 = get_all_records(agent)
q_ai_1.pfilter(BinOp(f('user_id'), EQ, Parameter('user_id')))
q_ai_1.orderby([f('created_at')])
q_ai_1.project('*')
q_ai_1.finclude(f('receivers'))
q_ai_1.get_include(f('receivers')).aggr(UnaryExpr(COUNT), 'receiver_count')
q_ai_1.finclude(f('sources'))
q_ai_1.get_include(f('sources')).aggr(UnaryExpr(COUNT), 'source_count')
q_ai_1.orderby([f('created_at')])
q_ai_1.return_limit(25)
q_ai_1.complete()

q_ai_2 = get_all_records(agent)
q_ai_2.pfilter(BinOp(f('user_id'), EQ, Parameter('user_id')))
q_ai_2.project([f('id')])
q_ai_2.orderby([f('created_at')])
q_ai_2.complete()