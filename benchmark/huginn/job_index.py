from huginn_schema import *

# SELECT  `delayed_jobs`.* FROM `delayed_jobs` ORDER BY coalesce(failed_at,'1000-01-01'), run_at asc LIMIT 25 OFFSET 0
# SELECT  `agents`.* FROM `agents` WHERE `agents`.`id` = 8 LIMIT 1
# SELECT agents.id FROM `agents` WHERE `agents`.`type` IN ('Agents::HttpStatusAgent') AND (NOT disabled AND NOT deactivated AND schedule = 'every_1m')
# SELECT `agents`.* FROM `agents` WHERE `agents`.`type` IN ('Agents::TwitterStreamAgent') AND `agents`.`disabled` = FALSE AND `agents`.`deactivated` = FALSE ORDER BY `agents`.`id` ASC
# SELECT  `delayed_jobs`.* FROM `delayed_jobs` WHERE ((run_at <= '2019-04-21 04:11:11.230130' AND (locked_at IS NULL OR locked_at < '2019-04-21 04:09:11.230190') OR locked_by = 'host:dragon pid:12241') AND failed_at IS NULL) ORDER BY priority ASC, run_at ASC LIMIT 5[0m
# SELECT `agents`.`name`, `agents`.`id` FROM `agents` WHERE `agents`.`user_id` = 1 ORDER BY agents.created_at desc

q_ji_1 = get_all_records(delayed_job)
q_ji_1.orderby([f('failed_at'), f('run_at')])
q_ji_1.return_limit(25)
q_ji_1.project('*')
q_ji_1.complete()

q_ji_2 = get_all_records(agent)
q_ji_2.pfilter(BinOp(f('type'), EQ, Parameter('atype')))
q_ji_2.pfilter(BinOp(f('disabled'), EQ, AtomValue(False)))
q_ji_2.pfilter(BinOp(f('deactivated'), EQ, AtomValue(False)))
q_ji_2.pfilter(BinOp(f('schedule'), EQ, Parameter('schedule')))
q_ji_2.project([f('id')])
q_ji_2.complete()

q_ji_3 = get_all_records(agent)
q_ji_3.pfilter(BinOp(f('type'), EQ, Parameter('atype')))
q_ji_3.pfilter(BinOp(f('disabled'), EQ, AtomValue(False)))
q_ji_3.pfilter(BinOp(f('deactivated'), EQ, AtomValue(False)))
q_ji_3.orderby([f('id')])
q_ji_3.return_limit(25)
q_ji_3.project('*')
q_ji_3.complete()

q_ji_4 = get_all_records(delayed_job)
q_ji_4.pfilter(BinOp(f('run_at'), LT, Parameter('run_at')))
q_ji_4.pfilter(ConnectOp(ConnectOp(BinOp(f('locked_at'), EQ, AtomValue('0000-00-00 00:00:00')), OR, \
    BinOp(f('locked_at'), LT, Parameter('time2'))), OR,
    BinOp(f('locked_by'), EQ, Parameter('lockedby'))))
q_ji_4.orderby([f('priority'), f('run_at')])
q_ji_4.return_limit(5)
q_ji_4.project('*')
q_ji_4.complete()

