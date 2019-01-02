from lobsters_schema import *
# SELECT  `users`.* FROM `users`  WHERE `users`.`username` = 'armando'  
# ORDER BY `users`.`id` ASC LIMIT 1
	
# SELECT  `users`.* FROM `users`  WHERE `users`.`id` = 1 LIMIT 1
	
# SELECT  `tags`.* FROM `tags` INNER JOIN `taggings` ON `taggings`.`tag_id` = `tags`.`id` 
# INNER JOIN `stories` ON `stories`.`id` = `taggings`.`story_id` WHERE `tags`.`inactive` = 0 AND 
# `stories`.`user_id` = 117 GROUP BY `tags`.`id`  ORDER BY COUNT(*) desc LIMIT 1

# SELECT  `votes`.* FROM `votes` INNER JOIN `stories` ON `stories`.`id` = `votes`.`story_id` 
# INNER JOIN `comments` ON `comments`.`id` = `votes`.`comment_id` WHERE `votes`.`user_id` = 117 AND 
# (comments.user_id <> votes.user_id AND stories.user_id <> votes.user_id)  ORDER BY id DESC LIMIT 10


q_us_1 = get_all_records(user)
q_us_1.pfilter(BinOp(f('username'), EQ, Parameter('user_name')))
q_us_1.complete()

param_user_id = Parameter('user_id')

q_us_2 = get_all_records(tag)
q_us_2.pfilter(BinOp(f('inactive'), EQ, AtomValue(False)))
q_us_2.finclude(f('stories'), pfilter=BinOp(f('user').f('id'), EQ, param_user_id))
q_us_2.get_include(f('stories')).aggr(UnaryExpr(COUNT), 'story_count')
q_us_2.orderby([f('story_count')])
q_us_2.return_limit(1)
q_us_2.complete()

q_us_3 = get_all_records(vote)
q_us_3.pfilter(BinOp(f('comment').f('user').f('id'), NEQ, f('user').f('id')))
q_us_3.pfilter(BinOp(f('story').f('user').f('id'), NEQ, f('user').f('id')))
q_us_3.pfilter(BinOp(f('user').f('id'), EQ, param_user_id))
q_us_3.orderby([f('id')])
q_us_3.return_limit(10)
q_us_3.complete()

