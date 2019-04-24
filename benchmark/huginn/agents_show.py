from huginn_schema import *

# SELECT `agents`.`name`, `agents`.`id` FROM `agents` WHERE `agents`.`user_id` = 1 ORDER BY agents.created_at desc
# SELECT `agents`.* FROM `agents` INNER JOIN `links` ON `agents`.`id` = `links`.`source_id` WHERE `links`.`receiver_id` = 9

q_as_1 = get_all_records(agents)
q_as_1.pfilter(SetOp(f('sources'), EXIST, BinOp(f('receiver_id'), EQ, Parameter('receiver_id'))))
q_as_1.complete()