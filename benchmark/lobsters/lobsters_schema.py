import sys
import os
sys.path.append("../../")
from schema import *
from query import *
from pred import *

from faker import Faker
fake = Faker()

#scale = 10000
scale = 10
story = Table('story', scale*100)
comment = Table('comment', scale*500)
message = Table('message', scale*100)
tag = Table('tag', 100)
vote = Table('vote', scale*2000)
user = Table('user', scale*10)

THREAD_NUM = 100

# create_table "stories", force: :cascade do |t|
#     t.datetime "created_at"
#     t.integer  "user_id",                limit: 4
#     t.string   "url",                    limit: 250,                                default: ""
#     t.string   "title",                  limit: 150,                                default: "",    null: false
#     t.text     "description",            limit: 16777215
#     t.string   "short_id",               limit: 6,                                  default: "",    null: false
#     t.boolean  "is_expired",                                                        default: false, null: false
#     t.integer  "upvotes",                limit: 4,                                  default: 0,     null: false
#     t.integer  "downvotes",              limit: 4,                                  default: 0,     null: false
#     t.boolean  "is_moderated",                                                      default: false, null: false
#     t.decimal  "hotness",                                 precision: 20, scale: 10, default: 0.0,   null: false
#     t.text     "markeddown_description", limit: 16777215
#     t.text     "story_cache",            limit: 16777215
#     t.integer  "comments_count",         limit: 4,                                  default: 0,     null: false
#     t.integer  "merged_story_id",        limit: 4
#     t.datetime "unavailable_at"
#     t.string   "twitter_id",             limit: 20
#     t.boolean  "user_is_author",                                                    default: false
#   end
created_at = Field('created_at', 'date')
url = Field('url', 'varchar(256)')
url.set_value_generator(lambda: fake.url()[:254])
title = Field('title', 'varchar(128)')
title.set_value_generator(lambda: fake.text(max_nb_chars=126).replace('\t', ' ').replace('\n', ' '))
short_id = Field('short_id', 'varchar(8)')
is_expired = Field('is_expired', 'bool')
upvotes = Field('upvotes', 'int')
downvotes = Field('downvotes', 'int')
is_moderated = Field('is_moderated', 'bool')
hotness = Field('hotness', 'float')
description = Field('description', 'string')
description.set_value_generator(lambda: fake.text(max_nb_chars=1024).replace('\t', ' ').replace('\n', ' '))
markeddown_description = Field('markeddown_description', 'string')
markeddown_description.set_value_generator(lambda: fake.text(max_nb_chars=1024).replace('\t', ' ').replace('\n', ' '))
story_cache = Field('story_cache', 'string')
story_cache.set_value_generator(lambda: fake.text(max_nb_chars=1024).replace('\t', ' ').replace('\n', ' '))
merged_story_id = Field('merged_story_id', 'uint')
merged_story_id.value_with_prob = [(0, 80), (1, 5), (2, 5), (3, 5), (4, 5)]
unavailable_at = Field('unavailable_at', 'date')
twitter_id = Field('twitter_id', 'varchar(16)')
user_is_author = Field('user_is_author', 'bool')

story.add_fields([created_at, url, title, short_id, is_expired, upvotes, downvotes, \
is_moderated, hotness, description, markeddown_description, story_cache, \
merged_story_id, unavailable_at, twitter_id, user_is_author])

storys_user = get_new_assoc("stories_user", "one_to_many", user, story, "stories", "user")
storys_tags = get_new_assoc("stories_tags", "many_to_many", story, tag, "tags", "stories", 2, 0)
storys_hidden = get_new_assoc('stories_hidden', 'many_to_many', story, user, "hidden_users", "hidden_stories", 10, 0)

# create_table "comments", force: :cascade do |t|
#     t.datetime "created_at",                                                                    null: false
#     t.datetime "updated_at"
#     t.string   "short_id",           limit: 10,                                 default: "",    null: false
#     t.integer  "story_id",           limit: 4,                                                  null: false
#     t.integer  "user_id",            limit: 4,                                                  null: false
#     t.integer  "parent_comment_id",  limit: 4
#     t.integer  "thread_id",          limit: 4
#     t.text     "comment",            limit: 16777215,                                           null: false
#     t.integer  "upvotes",            limit: 4,                                  default: 0,     null: false
#     t.integer  "downvotes",          limit: 4,                                  default: 0,     null: false
#     t.decimal  "confidence",                          precision: 20, scale: 19, default: 0.0,   null: false
#     t.text     "markeddown_comment", limit: 16777215
#     t.boolean  "is_deleted",                                                    default: false
#     t.boolean  "is_moderated",                                                  default: false
#     t.boolean  "is_from_email",                                                 default: false
#     t.integer  "hat_id",             limit: 4
#     t.boolean  "is_dragon",                                                     default: false
#   end

created_at = Field('created_at', 'date')
updated_at = Field('updated_at', 'date')
short_id = Field('short_id', 'varchar(8)')
parent_comment_id = Field('parent_comment_id', 'oid')
parent_comment_id.value_range = [1, comment.sz]
thread_id = Field('thread_id', 'oid')
thread_id.range = [1, THREAD_NUM]
comment_comment = Field('comment', 'string')
comment_comment.set_value_generator(lambda: fake.text(max_nb_chars=1024).replace('\t', ' ').replace('\n', ' '))
upvotes = Field('upvotes', 'int')
downvotes = Field('downvotes', 'int')
confidence = Field('confidence', 'float')
markeddown_comment = Field('markeddown_comment', 'string')
markeddown_comment.set_value_generator(lambda: fake.text(max_nb_chars=1024).replace('\t', ' ').replace('\n', ' '))
is_delete = Field('is_deleted', 'bool')
is_moderated = Field('is_moderated', 'bool')
is_from_email = Field('is_from_email', 'bool')
hat_id = Field('hat_id', 'oid')
hat_id.range = [1, 100]
is_dragon = Field('is_dragon', 'bool')

comment.add_fields([created_at, updated_at, short_id, parent_comment_id, thread_id, comment_comment, \
upvotes, downvotes, confidence, markeddown_comment, is_delete, is_moderated, is_from_email, hat_id, is_dragon])

comments_user = get_new_assoc("comments_user", "one_to_many", user, comment, "comments", "user")
comments_story = get_new_assoc("comments_story", "one_to_many", story, comment, "comments", "story")

# create_table "messages", force: :cascade do |t|
#     t.datetime "created_at"
#     t.integer  "author_user_id",       limit: 4
#     t.integer  "recipient_user_id",    limit: 4
#     t.boolean  "has_been_read",                         default: false
#     t.string   "subject",              limit: 100
#     t.text     "body",                 limit: 16777215
#     t.string   "short_id",             limit: 30
#     t.boolean  "deleted_by_author",                     default: false
#     t.boolean  "deleted_by_recipient",                  default: false
#     t.integer  "hat_id",               limit: 4
#   end
created_at = Field('created_at', 'date')
has_been_read = Field('has_been_read', 'bool')
subject = Field('subject', 'varchar(128)')
subject.set_value_generator(lambda: ' '.join(fake.words(nb=3)))
body = Field('body', 'string')
body.set_value_generator(lambda: fake.text(max_nb_chars=1024).replace('\t', ' ').replace('\n', ' '))
short_id = Field('short_id', 'varchar(8)')
deleted_by_author = Field('deleted_by_author', 'bool')
deleted_by_recipient = Field('deleted_by_recipient', 'bool')
hat_id = Field('hat_id', 'oid')
hat_id.range = [1, 100]

message.add_fields([created_at, has_been_read, subject, body, short_id, \
deleted_by_author, deleted_by_recipient, hat_id])

message_author = get_new_assoc("messages_author", "one_to_many", user, message, "sent_msgs", "author")
message_recipient = get_new_assoc("messages_recipient", "one_to_many", user, message, "received_msgs", "recipient")


# create_table "tags", force: :cascade do |t|
#   t.string  "tag",         limit: 25,  default: "",    null: false
#   t.string  "description", limit: 100
#   t.boolean "privileged",              default: false
#   t.boolean "is_media",                default: false
#   t.boolean "inactive",                default: false
#   t.float   "hotness_mod", limit: 24,  default: 0.0
# end
tag_text = Field('tag', 'varchar(24)')
tag_text.set_value_generator(lambda: fake.words(nb=1)[0][:22])
description = Field('description', 'varchar(128)')
description.set_value_generator(lambda: fake.text(max_nb_chars=126).replace('\t', ' ').replace('\n', ' '))
privileged = Field('privileged', 'bool')
is_media = Field('is_media', 'bool')
inactive = Field('inactive', 'bool')
hotness_mod = Field('hotness_mod', 'float')

tag.add_fields([tag_text, description, privileged, is_media, inactive, hotness_mod])

# create_table "votes", force: :cascade do |t|
#   t.integer "user_id",    limit: 4, null: false
#   t.integer "story_id",   limit: 4, null: false
#   t.integer "comment_id", limit: 4
#   t.integer "vote",       limit: 1, null: false
#   t.string  "reason",     limit: 1
# end
vote_vote = Field('vote', 'int')
vote_vote.value_with_prob = [(2, 25), (1, 25), (-1, 25), (-2, 25)]
reason = Field('reason', 'varchar(64)')
reason.set_value_generator(lambda: fake.text(max_nb_chars=62).replace('\t', ' ').replace('\n', ' '))

vote.add_fields([vote_vote, reason])

votes_user = get_new_assoc("votess_user", "one_to_many", user, vote, "votes", "user")
votes_story = get_new_assoc("votes_story", "one_to_many", story, vote, "votes", "story")
votes_comment = get_new_assoc("votes_comment", "one_to_many", comment, vote, "votes", "comment")

# create_table "users", force: :cascade do |t|
#   t.string   "username",                   limit: 50
#   t.string   "email",                      limit: 100
#   t.string   "password_digest",            limit: 75
#   t.datetime "created_at"
#   t.boolean  "is_admin",                                    default: false
#   t.string   "password_reset_token",       limit: 75
#   t.string   "session_token",              limit: 75,       default: "",    null: false
#   t.text     "about",                      limit: 16777215
#   t.integer  "invited_by_user_id",         limit: 4
#   t.boolean  "is_moderator",                                default: false
#   t.boolean  "pushover_mentions",                           default: false
#   t.string   "rss_token",                  limit: 75
#   t.string   "mailing_list_token",         limit: 75
#   t.integer  "mailing_list_mode",          limit: 4,        default: 0
#   t.integer  "karma",                      limit: 4,        default: 0,     null: false
#   t.datetime "banned_at"
#   t.integer  "banned_by_user_id",          limit: 4
#   t.string   "banned_reason",              limit: 200
#   t.datetime "deleted_at"
#   t.datetime "disabled_invite_at"
#   t.integer  "disabled_invite_by_user_id", limit: 4
#   t.string   "disabled_invite_reason",     limit: 200
#   t.text     "settings",                   limit: 65535
# end
username = Field('username', 'varchar(32)')
username.set_value_generator(lambda: fake.user_name()[:31])
email = Field('email', 'varchar(128)')
password_digest = Field('password_digest', 'varchar(64)')
created_at = Field('created_at', 'date')
is_admin = Field('is_admin', 'bool')
password_reset_token = Field('password_reset_token', 'varchar(64)')
session_token = Field('session_token', 'varchar(64)')
about = Field('about', 'string')
invited_by_user_id = Field('invited_by_user_id', 'oid')
invited_by_user_id.range = [1, user.sz]
is_moderator = Field('is_moderator', 'bool')
pushover_mentions = Field('pushover_mentions', 'bool')
rss_token = Field('rss_token', 'varchar(64)')
mailing_list_token = Field('mailing_list_token', 'varchar(64)')
mailing_list_mode = Field('mailing_list_mode', 'varchar(4)')
karma = Field('karma', 'varchar(4)')
banned_at = Field('banned_at', 'date')
banned_by_user_id = Field('banned_by_user_id', 'uint')
banned_by_user_id.range = [1, user.sz]
banned_reason = Field('banned_reason', 'varchar(256)')
banned_reason.set_value_generator(lambda: fake.text(max_nb_chars=255).replace('\t', ' ').replace('\n', ' '))
deleted_at = Field('deleted_at', 'date')
disabled_invite_at = Field('disabled_invite_at', 'date')
disabled_invite_by_user_id = Field('disabled_invite_by_user_id', 'oid')
settings = Field('settings', 'string')
settings.set_value_generator(lambda: fake.text(max_nb_chars=1024).replace('\t', ' ').replace('\n', ' '))

user.add_fields([username, email, password_digest, created_at, is_admin, password_reset_token, \
session_token, about, invited_by_user_id, is_moderator, pushover_mentions, rss_token, \
mailing_list_token, mailing_list_mode, karma, banned_at, banned_reason, banned_by_user_id, deleted_at, \
disabled_invite_at, disabled_invite_by_user_id, settings])


vote.get_field_by_name('comment_id').set_value_generator(lambda: 0 if (random.randint(0, 100) < 40) else random.randint(1, comment.sz))
vote.get_field_by_name('story_id').set_value_generator(lambda: 0 if (random.randint(0, 100) < 40) else random.randint(1, story.sz))

