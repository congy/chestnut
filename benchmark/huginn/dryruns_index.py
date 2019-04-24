from huginn_schema import *

# SELECT  `events`.* FROM `events` INNER JOIN `agents` ON `events`.`agent_id` = `agents`.`id` INNER JOIN `links` ON `agents`.`id` = `links`.`source_id` WHERE `links`.`receiver_id` = 2 ORDER BY events.id desc LIMIT 5

q_di_1 = get_all_records(event)
q_di_1.pfilter(SetOp(f('agent').f('sources'), EXIST, BinOp(f('receiver_id'), EQ, Parameter('receiver_id'))))
q_di_1.orderby([f('id')])
q_di_1.return_limit(25)
q_di_1.project('*')
q_di_1.complete()

