from lobsters_schema import *
# SELECT  `stories`.* FROM `stories`  WHERE `stories`.`merged_story_id` IS NULL AND 
# `stories`.`is_expired` = 0 AND ((CAST(upvotes AS signed) - CAST(downvotes AS signed)) >= -1) AND 
# `stories`.`id` IN (SELECT `taggings`.`story_id` FROM `taggings`  WHERE `taggings`.`tag_id` = 7)  
# ORDER BY stories.created_at DESC LIMIT 26 OFFSET 0

# SELECT `users`.* FROM `users`  WHERE `users`.`id` IN (stories.author)

# SELECT `tags`.* FROM `tags`  WHERE `tags`.`id` IN (7)

# SELECT `votes`.* FROM `votes`  WHERE `votes`.`user_id` = 1 AND `votes`.`story_id` IN 
# (stories.votes) AND `votes`.`comment_id` IS NULL

# SELECT `hidden_stories`.* FROM `hidden_stories`  WHERE `hidden_stories`.`user_id` = 1 AND 
# `hidden_stories`.`story_id` IN (stories.hidden)

param_tag = Parameter('tag_id')
param_user_id = Parameter('user_id')
q_ht_1 = get_all_records(story)
q_ht_1.pfilter(BinOp(f('merged_story_id'), EQ, AtomValue('0')))
q_ht_1.pfilter(BinOp(f('is_expired'), EQ, AtomValue(False)))
q_ht_1.pfilter(BinOp(f('upvotes'), GE, AtomValue(-1))) #TODO
q_ht_1.pfilter(SetOp(f('tags'), EXIST, BinOp(f('id'), EQ, param_tag)))
q_ht_1.orderby([f('created_at')], ascending=False)
q_ht_1.project('*')
q_ht_1.finclude(f('user'))
q_ht_1.finclude(f('tags'), pfilter=BinOp(f('id'), EQ, param_tag))
q_ht_1.finclude(f('votes'), pfilter=ConnectOp(BinOp(f('user').f('id'), EQ, param_user_id), AND, BinOp(f('comment_id'), EQ, AtomValue(0))))
#q_ht_1.finclude(f('hidden_users'), pfilter=BinOp(f('id'), EQ, param_user_id))
q_ht_1.complete()
