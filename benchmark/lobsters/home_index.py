from lobsters_schema import *
# SELECT  `stories`.* FROM `stories`  WHERE `stories`.`merged_story_id` IS NULL AND 
# `stories`.`is_expired` = 0 AND ((CAST(upvotes AS signed) - CAST(downvotes AS signed)) >= -1) AND 
# (`stories`.`id` NOT IN (SELECT `hidden_stories`.`story_id` FROM `hidden_stories`  WHERE `hidden_stories`.`user_id` = 1)) \
# AND (`stories`.`id` NOT IN (SELECT `taggings`.`story_id` FROM `taggings`  WHERE `taggings`.`tag_id` IN (2, 2, 2, 2, 2, 2, 2)))  \
# ORDER BY hotness LIMIT 26 OFFSET 0

#SELECT `users`.* FROM `users`  WHERE `users`.`id` IN (stories.author)
	
#SELECT `taggings`.* FROM `taggings`  WHERE `taggings`.`story_id` IN (stories.id)
	
#SELECT `tags`.* FROM `tags`  WHERE `tags`.`id` IN (?)
	
#SELECT `votes`.* FROM `votes`  WHERE `votes`.`user_id` = 1 AND `votes`.`story_id` IN (>) 
#AND `votes`.`comment_id` IS NULL
	
#SELECT `hidden_stories`.* FROM `hidden_stories`  WHERE `hidden_stories`.`user_id` = 1 AND 
#`hidden_stories`.`story_id` IN (?)

param_tag = Parameter('tag_id')
param_user_id = Parameter('user_id')
q_hi_1 = get_all_records(story)
q_hi_1.pfilter(BinOp(f('merged_story_id'), EQ, AtomValue('0')))
q_hi_1.pfilter(BinOp(f('is_expired'), EQ, AtomValue(False)))
q_hi_1.pfilter(BinOp(f('upvotes'), GE, AtomValue(-1))) #TODO
q_hi_1.pfilter(UnaryOp(SetOp(f('hidden_users'), EXIST, BinOp(f('id'), EQ, param_user_id))))
q_hi_1.pfilter(UnaryOp(SetOp(f('tags'), EXIST, BinOp(f('id'), EQ, Parameter('tag_id2')))))
q_hi_1.orderby([f('hotness')], ascending=False)
q_hi_1.project('*')
q_hi_1.return_limit(26)
#q_hi_1.finclude(f('user'))
q_hi_1.finclude(f('tags'), pfilter=BinOp(f('id'), EQ, param_tag))
q_hi_1.finclude(f('votes'), pfilter=ConnectOp(BinOp(f('user').f('id'), EQ, param_user_id), AND, BinOp(f('comment_id'), EQ, AtomValue(0))))
#q_hi_1.finclude(f('hidden_users'), pfilter=BinOp(f('id'), EQ, param_user_id))
q_hi_1.complete()
