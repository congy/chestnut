from lobsters_schema import *
# SELECT  `stories`.* FROM `stories`  WHERE `stories`.`short_id` = 'cZPgmX'  ORDER BY `stories`.`id` ASC LIMIT 1
	
# SELECT `taggings`.* FROM `taggings`  WHERE `taggings`.`story_id` = 661922

# SELECT  `tags`.* FROM `tags`  WHERE `tags`.`id` = 52 LIMIT 1
	
# SELECT  `stories`.* FROM `stories`  WHERE `stories`.`id` = 661922 LIMIT 1

# SELECT  1 AS one FROM `messages`  WHERE `messages`.`short_id` = 'm2ak14' LIMIT 1

# SELECT  `users`.* FROM `users`  WHERE `users`.`id` = 368 LIMIT 1

# SELECT  `users`.* FROM `users`  WHERE `users`.`id` = 1 LIMIT 1

# INSERT INTO `messages` (`author_user_id`, `body`, `created_at`, `deleted_by_author`, `recipient_user_id`, `short_id`, `subject`) VALUES (1, 'Your story [XWexrbKbeT](https://whyamilearningruby.com/s/cZPgmX/xwexrbkbet) has been edited by a moderator with the following changes:\n\n> *deleted story*\n\nThe reason given:\n\n> *jhyt*\n\n*This is an automated message.*', '2016-10-26 21:31:25', 1, 368, 'm2ak14', 'Your story has been edited by a moderator')

# SELECT COUNT(*) FROM `messages`  WHERE `messages`.`recipient_user_id` = 368 AND 
# `messages`.`has_been_read` = 0 AND `messages`.`deleted_by_recipient` = 0

# UPDATE `stories` SET `is_expired` = 1, `is_moderated` = 1 WHERE `stories`.`id` = 661922

# q_mc_1
# q_mc_2
# q_mc_3
# q_mc_4
# q_mc_5
# q_mc_6
q_sd_1 = get_all_records(story)
q_sd_1.pfilter(BinOp(f('short_id'), EQ, Parameter('story_short_id')))
q_sd_1.finclude(f('tags'), projection=[f('tag'),f('id')])
q_sd_1.complete()

q_sd_2 = UpdateObject(story, Parameter('story_id'), {f('is_expired'):AtomValue(False), f('is_moderated'):AtomValue(True)})

