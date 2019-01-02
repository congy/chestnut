from lobsters_schema import *
# SELECT `stories`.`id`, `stories`.`upvotes`, `stories`.`downvotes`, `stories`.`user_id` 
# FROM `stories`  WHERE `stories`.`merged_story_id` IS NULL AND `stories`.`is_expired` = 0 
# AND (`stories`.`id` NOT IN (SELECT `hidden_stories`.`story_id` FROM `hidden_stories`  
# WHERE `hidden_stories`.`user_id` = 1)) AND (`stories`.`id` NOT IN 
# (SELECT `taggings`.`story_id` FROM `taggings`  WHERE `taggings`.`tag_id` IN (?))) AND 
# (`stories`.`created_at` > '2016-10-23 22:34:39')  
# ORDER BY stories.id DESC, stories.created_at DESC

# SQL: SELECT  `stories`.* FROM `stories`  WHERE `stories`.`merged_story_id` IS NULL AND 
# `stories`.`is_expired` = 0 AND (`stories`.`id` NOT IN 
# (SELECT `hidden_stories`.`story_id` FROM `hidden_stories`  WHERE `hidden_stories`.`user_id` = 1)) AND 
# (`stories`.`id` NOT IN (SELECT `taggings`.`story_id` FROM `taggings`  WHERE 
# `taggings`.`tag_id` IN (?2)))  ORDER BY stories.id DESC, stories.created_at 
# DESC LIMIT 26 OFFSET 0

# SELECT `users`.* FROM `users`  WHERE `users`.`id` IN (stories.user)

#SELECT `taggings`.* FROM `taggings`  WHERE `taggings`.`story_id` IN (786423, 786422, 13594, 36812, 190806, 28097, 11657, 187258, 141210, 54044, 578, 4790, 786421, 88555, 69122, 661790, 723977, 720045, 660499, 383323, 723970, 723164, 660748, 660809, 661022, 660544)

# SELECT `tags`.* FROM `tags`  WHERE `tags`.`id` IN (stories.tags)

# SELECT `votes`.* FROM `votes`  WHERE `votes`.`user_id` = 1 AND `votes`.`story_id` IN 
# (stories.votes) AND `votes`.`comment_id` IS NULL
	
# SELECT `hidden_stories`.* FROM `hidden_stories`  WHERE `hidden_stories`.`user_id` = 1 AND `hidden_stories`.`story_id` IN (stories.hidden)

param_user_id = Parameter('user_id')
q_hr_1 = get_all_records(story)
q_hr_1.pfilter(BinOp(f('merged_story_id'), EQ, AtomValue('0')))
q_hr_1.pfilter(BinOp(f('is_expired'), EQ, AtomValue(False)))
q_hr_1.pfilter(UnaryOp(SetOp(f('hidden_users'), EXIST, BinOp(f('id'), EQ, param_user_id))))
q_hr_1.pfilter(UnaryOp(SetOp(f('tags'), EXIST, BinOp(f('id'), EQ, Parameter('tag_id')))))
q_hr_1.pfilter(BinOp(f('created_at'), GT, Parameter('some_date')))
q_hr_1.orderby([f('id'), f('created_at')], ascending=False)
q_hr_1.project([f('id'), f('upvotes'), f('downvotes'), f('user_id')])
#q_hr_1.finclude(f('user'))
q_hr_1.finclude(f('tags'), pfilter=BinOp(f('id'), EQ, Parameter('tag_id')), projection=[f('tag'),f('id')])
q_hr_1.finclude(f('votes'), pfilter=ConnectOp(BinOp(f('user').f('id'), EQ, param_user_id), AND, BinOp(f('comment').f('id'), EQ, AtomValue(0))), projection=[f('vote'),f('id')])
#q_hr_1.finclude(f('hidden_users'), pfilter=BinOp(f('id'), EQ, param_user_id))
q_hr_1.complete()

q_hr_2 = get_all_records(story)
q_hr_2.pfilter(BinOp(f('merged_story_id'), EQ, AtomValue('0')))
q_hr_2.pfilter(BinOp(f('is_expired'), EQ, AtomValue(False)))
q_hr_2.pfilter(UnaryOp(SetOp(f('hidden_users'), EXIST, BinOp(f('id'), EQ, param_user_id))))
q_hr_2.pfilter(UnaryOp(SetOp(f('tags'), EXIST, BinOp(f('id'), EQ, Parameter('tag_id')))))
q_hr_2.orderby([f('id'), f('created_at')], ascending=False)
q_hr_2.project('*')
q_hr_2.return_limit(26)
#q_hr_2.finclude(f('user'))
q_hr_2.finclude(f('tags'), pfilter=BinOp(f('id'), EQ, Parameter('tag_id')), projection=[f('tag'),f('id')])
q_hr_2.finclude(f('votes'), pfilter=ConnectOp(BinOp(f('user').f('id'), EQ, param_user_id), AND, BinOp(f('comment').f('id'), EQ, AtomValue(0))), projection=[f('vote'),f('id')])
#q_hr_2.finclude(f('hidden_users'), pfilter=BinOp(f('id'), EQ, param_user_id))
q_hr_2.complete()

q_hr_3 = get_all_records(vote)
q_hr_3.pfilter(ConnectOp(BinOp(f('user').f('id'), EQ, param_user_id), AND, \
ConnectOp(BinOp(f('comment').f('id'), EQ, AtomValue(0)), AND, \
BinOp(f('story').f('id'), EQ, Parameter('user_id')))))
q_hr_3.complete()



