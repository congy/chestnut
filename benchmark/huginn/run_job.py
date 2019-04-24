

# SELECT  `delayed_jobs`.* FROM `delayed_jobs` WHERE ((run_at <= '2019-04-21 04:11:12.698662' AND (locked_at IS NULL OR locked_at < '2019-04-21 04:09:12.698709') OR locked_by = 'host:dragon pid:12241') AND failed_at IS NULL) ORDER BY priority ASC, run_at ASC LIMIT 5

# SELECT agents.id AS receiver_agent_id, sources.type AS source_agent_type, 
# agents.type AS receiver_agent_type, events.id AS event_id 
# FROM `agents` 
# JOIN links ON (links.receiver_id = agents.id) 
# JOIN agents AS sources ON (links.source_id = sources.id) 
# JOIN events ON (events.agent_id = sources.id AND events.id > links.event_id_at_creation) 
# WHERE (NOT agents.disabled AND NOT agents.deactivated AND 
# (agents.last_checked_event_id IS NULL OR events.id > agents.last_checked_event_id))

# SELECT `agents`.`type` FROM `agents` WHERE `agents`.`schedule` = 'every_1m' GROUP BY `agents`.`type`
# SELECT agents.id FROM `agents` WHERE `agents`.`type` IN ('Agents::HttpStatusAgent') AND (NOT disabled AND NOT deactivated AND schedule = 'every_1m')
# UPDATE `agents` SET `events_count` = COALESCE(`events_count`, 0) + 1 WHERE `agents`.`type` IN ('Agents::HttpStatusAgent') AND `agents`.`id` = 8

# INSERT INTO delayed_jobs
# DELETE FROM delayed_jobs WHERE id = ?

q_rj_1 = get_all_records(events)
q_rj_1.pfilter(BinOp(f('agent').f('disabled'), EQ, AtomValue(False)))
q_rj_1.pfilter(BinOp(f('agent').f('deactivated'), EQ, AtomValue(False)))
q_rj_1.pfilter(ConnectOp(BinOp(f('agent').f('last_checked_event_id'), EQ, AtomValue(0)), OR,
  BinOp(f('id'), LT, f('agent').f('last_checked_event_id'))))
q_rj_1.pfilter()