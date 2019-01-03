from lobsters_schema import *
# SELECT  `stories`.* FROM `stories`  WHERE `stories`.`short_id` = 'sdCYqs'  ORDER BY `stories`.`id` ASC LIMIT 1

# SELECT  `comments`.* FROM `comments`  WHERE `comments`.`story_id` = 36812 AND `comments`.`short_id` = 'OKbybe'  ORDER BY `comments`.`id` ASC LIMIT 1

# SELECT  `comments`.* FROM `comments`  WHERE `comments`.`story_id` = 36812 AND `comments`.`user_id` = 1 AND 
# `comments`.`parent_comment_id` = 6029056  ORDER BY `comments`.`id` ASC LIMIT 1

# SELECT  1 AS one FROM `comments`  WHERE `comments`.`short_id` = 'w1ijom' LIMIT 1
	
# SELECT  1 AS one FROM `comments`  WHERE `comments`.`short_id` = 'a1bdvx' LIMIT 1

# INSERT INTO `comments` (`comment`, `confidence`, `created_at`, `markeddown_comment`, `parent_comment_id`, `short_id`, `story_id`, `thread_id`, `updated_at`, `upvotes`, `user_id`) VALUES ('kklkuuu', 0.182884783413889, '2016-10-26 21:50:32', '<p>kklkuuu</p>\n', 6029056, 'a1bdvx', 36812, 146, '2016-10-26 21:50:32', 1, 1)

# SELECT  `votes`.* FROM `votes`  WHERE `votes`.`user_id` = 1 AND `votes`.`story_id` = 36812 AND 
# `votes`.`comment_id` = 6094772  ORDER BY `votes`.`id` ASC LIMIT 1
	
# INSERT INTO `votes` (`comment_id`, `story_id`, `user_id`, `vote`) VALUES (6094772, 36812, 1, 1)

# SELECT `stories`.`id` FROM `stories`  WHERE `stories`.`merged_story_id` = 36812

# SELECT `comments`.* FROM `comments`  WHERE `comments`.`story_id` IN (36812)  ORDER BY confidence DESC

# UPDATE `stories` SET `stories`.`comments_count` = 0 WHERE `stories`.`id` = 36812

# SELECT `tags`.* FROM `tags` INNER JOIN `taggings` ON `tags`.`id` = `taggings`.`tag_id` WHERE `taggings`.`story_id` = 36812

# SELECT `comments`.`upvotes`, `comments`.`downvotes` FROM `comments`  WHERE `comments`.`story_id` = 36812 AND (user_id <> 384)

# UPDATE `stories` SET `stories`.`hotness` = -17065.6717654 WHERE `stories`.`id` = 36812

q_cc_1 = get_all_records(story)
q_cc_1.pfilter(BinOp(f('short_id'), EQ, Parameter('story_short_id')))
q_cc_1.project('*')
q_cc_1.finclude(f('comments'), pfilter=BinOp(f('short_id'), EQ, Parameter('comment_short_id')), projection=[f('short_id'), f('id'), f('parent_comment_id')])
q_cc_1.complete()

q_cc_2 = get_all_records(comment)
q_cc_2.pfilter(BinOp(f('parent_comment_id'), EQ, Parameter('parent_comment_id')))
q_cc_2.pfilter(BinOp(f('user').f('id'), EQ, Parameter('comment_author_id')))
q_cc_2.pfilter(BinOp(f('story').f('id'), EQ, Parameter('story_id')))
q_cc_2.orderby([f('id')])
q_cc_2.project([f('upvotes'), f('downvotes')])
q_cc_2.return_limit(1)
q_cc_2.complete()

q_cc_3 = AddObject(comment, {QueryField('comment', table=comment):Parameter('new_comment'), \
QueryField('confidence', table=comment):Parameter('new_confidence'), \
QueryField('created_at', table=comment):Parameter('new_created_at'), \
QueryField('parent_comment_id', table=comment):Parameter('new_parent_comment_id'), \
QueryField('short_id', table=comment):Parameter('new_short_id'), \
QueryField('thread_id', table=comment):Parameter('new_thread_id'), \
QueryField('updated_at', table=comment):Parameter('new_updated_at'), \
QueryField('upvotes', table=comment):Parameter('new_upvotes')})
q_cc_4 = ChangeAssociation(QueryField('comments', table=story), INSERT, Parameter('story_id'), Parameter('comment_id'))
q_cc_5 = ChangeAssociation(QueryField('user', table=comment), INSERT, Parameter('comment_id'), Parameter('user_id'))

q_cc_6 = AddObject(vote, {QueryField('vote', table=vote):Parameter('new_vote')})
q_cc_7 = ChangeAssociation(QueryField('votes', table=story), INSERT, Parameter('story_id'), Parameter('vote_id'))
q_cc_8 = ChangeAssociation(QueryField('votes', table=comment), INSERT, Parameter('comment_id'), Parameter('vote_id'))
q_cc_9 = ChangeAssociation(QueryField('votes', table=user), INSERT, Parameter('user_id'), Parameter('vote_id'))

q_cc_10 = get_all_records(story)
q_cc_10.pfilter(BinOp(f('merged_story_id'), EQ, Parameter('story_id')))
q_cc_10.project([f('id')])
q_cc_10.finclude(f('comments'), pfilter=BinOp(f('user').f('id'), NEQ, Parameter('user_id')), projection=[f('short_id'), f('id'), f('parent_comment_id')])
q_cc_10.finclude(f('tags'), projection=[f('tag'),f('id')])
q_cc_10.complete()


q_cc_12 = UpdateObject(story, Parameter('story_id'), {f('hotness'): Parameter('new_hotness')})
