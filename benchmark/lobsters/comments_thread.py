from lobsters_schema import *
# SELECT  `comments`.`thread_id` FROM `comments`  WHERE `comments`.`user_id` = 117 
# GROUP BY `comments`.`thread_id`  ORDER BY MAX(created_at) DESC LIMIT 20
	
# SELECT `comments`.* FROM `comments`  WHERE `comments`.`thread_id` IN (?)  
# ORDER BY confidence DESC
	
# SELECT `users`.* FROM `users`  WHERE `users`.`id` IN (?)

# SELECT `stories`.* FROM `stories`  WHERE `stories`.`id` IN (?)

q_ct_1_comment = get_all_records(comment)
q_ct_1 = q_ct_1_comment.groupby([f('thread_id')], THREAD_NUM)
q_ct_1.pfilter(SetOp(f('comments'), EXIST, BinOp(f('user').f('id'), EQ, Parameter('user_id'))))
q_ct_1.get_include(f('comments')).aggr(UnaryExpr(MAX, f('created_at')), 'max_created')
q_ct_1.orderby([f('max_created')])
q_ct_1.return_limit(20)
q_ct_1.project([f('thread_id')])
q_ct_1.complete()

threads = [Parameter('thread_id_{}'.format(i)) for i in range(0, 5)]
q_ct_2 = get_all_records(comment)
q_ct_2.pfilter(BinOp(f('thread_id'), IN, MultiParam(threads)))
q_ct_2.orderby([f('confidence')])
q_ct_2.finclude(f('user'))
q_ct_2.finclude(f('story'))
q_ct_2.project('*')
q_ct_2.complete()