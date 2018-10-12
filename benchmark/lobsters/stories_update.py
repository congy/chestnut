from lobsters_schema import *
# SELECT  `stories`.* FROM `stories`  WHERE `stories`.`short_id` = 'rcuLcy'  ORDER BY `stories`.`id` ASC LIMIT 1
	
# SELECT  `stories`.* FROM `stories`  WHERE `stories`.`short_id` = 190806  ORDER BY `stories`.`id` ASC LIMIT 1

# SELECT `taggings`.* FROM `taggings`  WHERE `taggings`.`story_id` = 190806

# SELECT  `tags`.* FROM `tags`  WHERE `tags`.`id` = 64 LIMIT 1

# SELECT  1 AS one FROM `tags` INNER JOIN `taggings` ON `tags`.`id` = `taggings`.`tag_id` WHERE 
# `taggings`.`story_id` = 190806 AND `tags`.`tag` = 'ruby' LIMIT 1

# SELECT  `stories`.* FROM `stories`  WHERE `stories`.`id` = 190806 LIMIT 1

# SELECT  1 AS one FROM `messages`  WHERE `messages`.`short_id` = 'u9ffbx' LIMIT 1

# SELECT  `users`.* FROM `users`  WHERE `users`.`id` = 453 LIMIT 1

# SELECT  `users`.* FROM `users`  WHERE `users`.`id` = 1 LIMIT 1

# INSERT INTO `messages` (`author_user_id`, `body`, `created_at`, `deleted_by_author`, `recipient_user_id`, `short_id`, `subject`) VALUES (?)

# SELECT COUNT(*) FROM `messages`  WHERE `messages`.`recipient_user_id` = 453 AND `messages`.`has_been_read` = 0 
# AND `messages`.`deleted_by_recipient` = 0

# UPDATE `stories` SET `description` = 'RnIntHzacohVmY\r\nlklkSMWHKa', `is_moderated` = 1, `markeddown_description` = '<p>RnIntHzacohVmY\nlklkSMWHKa</p>\n' WHERE `stories`.`id` = 190806

# q_sd_1
q_su_1 = get_all_records(tag)
q_su_1.pfilter(BinOp(f('tag'), EQ, Parameter('tag')))
q_su_1.pfilter(SetOp(f('stories'), EXIST, BinOp(f('id'), EQ, Parameter('story_id'))))
q_su_1.project('*')
q_su_1.complete()

# q_mc_1
# q_mc_2
# q_mc_3
# q_mc_4
# q_mc_5
# q_mc_6
q_su_2 = UpdateObject(story, Parameter('story_id'), {f('description'):Parameter('description'), f('is_moderated'):AtomValue(True)})

