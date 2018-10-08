from lobsters_schema import *
# SELECT  `stories`.* FROM `stories`  WHERE `stories`.`short_id` = 'JVHuGQ'  ORDER BY `stories`.`id` ASC LIMIT 1

# SELECT  `votes`.* FROM `votes`  WHERE `votes`.`user_id` = 1 AND `votes`.`story_id` = 661022 AND `votes`.`comment_id` IS NULL  ORDER BY `votes`.`id` ASC LIMIT 1
	
# INSERT INTO `votes` (`story_id`, `user_id`, `vote`) VALUES (661022, 1, 1)
	
# SELECT  `stories`.* FROM `stories`  WHERE `stories`.`id` = 661022 LIMIT 1

# UPDATE `users` SET `karma` = COALESCE(`karma`, 0) + 1 WHERE `users`.`id` = 436

# SELECT `tags`.* FROM `tags` INNER JOIN `taggings` ON `tags`.`id` = `taggings`.`tag_id` WHERE `taggings`.`story_id` = 661022

# SELECT `comments`.`upvotes`, `comments`.`downvotes` FROM `comments`  WHERE `comments`.`story_id` = 661022 AND (user_id <> 436)

# UPDATE stories SET upvotes = COALESCE(upvotes, 0) + 1, downvotes = COALESCE(downvotes, 0) + 0, hotness = '-17064.8927694' WHERE id = 661022

q_sv_1 = get_all_records(story)
q_sv_1.pfilter(BinOp(f('short_id'), EQ, Parameter('story_short_id')))
q_sv_1.project('*')
q_sv_1.finclude(f('votes'), pfilter=ConnectOp(BinOp(f('user').f('id'), EQ, Parameter('user_id')), AND, BinOp(f('comment_id'), EQ, AtomValue(0))))
q_sv_1.finclude(f('tags'))
q_sv_1.complete()

q_sv_2 = AddObject(vote, {QueryField('vote', table=vote):Parameter('new_vote')})
q_sv_3 = ChangeAssociation(QueryField('story', table=vote), INSERT, Parameter('vote_id'), Parameter('story_id'))
q_sv_4 = ChangeAssociation(QueryField('user', table=vote), INSERT, Parameter('vote_id'), Parameter('user_id'))

q_sv_5 = UpdateObject(user, Parameter('user_id'), {f('karma'):Parameter('karma')})

#q_cc_10
q_sv_6 = UpdateObject(story, Parameter('story_id'), {f('upvotes'):Parameter('new_upvotes'), f('hotness'):Parameter('new_hotness')})