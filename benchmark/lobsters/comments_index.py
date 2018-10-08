from lobsters_schema import *
# SELECT  `comments`.* FROM `comments`  WHERE `comments`.`is_deleted` = 0 AND 
# `comments`.`is_moderated` = 0 AND (story_id NOT IN 
# (SELECT story_id FROM hidden_stories WHERE user_id = 1))  
# ORDER BY created_at DESC LIMIT 20 OFFSET 0

# SELECT `users`.* FROM `users`  WHERE `users`.`id` IN (?)

# SELECT `stories`.* FROM `stories`  WHERE `stories`.`id` IN (?)

# SELECT `votes`.* FROM `votes`  WHERE `votes`.`user_id` = 1 AND `votes`.`comment_id` IN (?)

param_user_id = Parameter('user_id')
q_ci_1 = get_all_records(comment)
q_ci_1.pfilter(BinOp(f('is_deleted'), EQ, AtomValue(False)))
q_ci_1.pfilter(BinOp(f('is_moderated'), EQ, AtomValue(False)))
q_ci_1.pfilter(BinOp(f('story').f('user').f('id'), NEQ, param_user_id))
q_ci_1.orderby([f('created_at')], ascending=False)
q_ci_1.return_limit(20)
q_ci_1.project('*')
#q_ci_1.finclude(f('user'))
#q_ci_1.finclude(f('story'))
q_ci_1.finclude(f('votes'), pfilter=BinOp(f('user').f('id'), EQ, param_user_id))
q_ci_1.complete()