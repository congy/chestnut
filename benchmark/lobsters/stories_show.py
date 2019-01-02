from lobsters_schema import *
# SELECT  `stories`.* FROM `stories`  WHERE `stories`.`short_id` = 'cZPgmX'  
# ORDER BY `stories`.`id` ASC LIMIT 1
	
# SELECT `stories`.`id` FROM `stories`  WHERE `stories`.`merged_story_id` = 661922
	
# SELECT `comments`.* FROM `comments`  WHERE `comments`.`story_id` IN (661922)  
# ORDER BY confidence DESC

# SELECT  `votes`.* FROM `votes`  WHERE `votes`.`user_id` = 1 AND `votes`.`story_id` = 661922 AND 
# `votes`.`comment_id` IS NULL  ORDER BY `votes`.`id` ASC LIMIT 1
	
# SELECT  `hidden_stories`.* FROM `hidden_stories`  WHERE `hidden_stories`.`user_id` = 1 AND 
# `hidden_stories`.`story_id` = 661922  ORDER BY `hidden_stories`.`id` ASC LIMIT 1

# SELECT `votes`.* FROM `votes`  WHERE `votes`.`user_id` = 1 AND `votes`.`story_id` = 661922 AND 
# (comment_id IS NOT NULL)

# SELECT `taggings`.* FROM `taggings`  WHERE `taggings`.`story_id` = 661922

# SELECT  `tags`.* FROM `tags`  WHERE `tags`.`id` = 52 LIMIT 1

# SELECT  `users`.* FROM `users`  WHERE `users`.`id` = 368 LIMIT 1

q_ss_1 = get_all_records(story)
q_ss_1.pfilter(BinOp(f('id'), EQ, Parameter('story_id')))
q_ss_1.finclude(f('comments'))
q_ss_1.get_include(f('comments')).orderby([f('confidence')], ascending=False)
q_ss_1.finclude(f('votes'), projection=[f('vote'), f('id')])
q_ss_1.get_include(f('votes')).orderby([f('id')], ascending=False)
q_ss_1.finclude(f('tags'), projection=[f('tag')])
q_ss_1.finclude(f('user'), projection=[f('username')])
q_ss_1.complete()
