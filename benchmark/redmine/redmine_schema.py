import sys
import os
sys.path.append("../../")
from schema import *
from query import *
from pred import *

from faker import Faker
fake = Faker()

#scale=4000
scale=40
issue = Table('issue', scale*2000)
user = Table('user', scale*200)
member = Table('member', scale*400)
project = Table('project', scale*80)
enabled_module = Table('enabled_module', project.sz*6)
enumeration = Table('enumeration', project.sz*4)
version = Table('version', project.sz*2)
news = Table('news', project.sz*8)
board = Table('board', project.sz*2)
message = Table('message', board.sz*2)

tracker = Table('tracker', 10)
role = Table('role', 20)
issue_status = Table('issue_status', 10)


  # create_table "issues", id: :integer, options: "ENGINE=InnoDB DEFAULT CHARSET=utf8", force: :cascade do |t|
  #   t.integer "tracker_id", null: false
  #   t.integer "project_id", null: false
  #   t.string "subject", default: "", null: false
  #   t.text "description", limit: 4294967295
  #   t.date "due_date"
  #   t.integer "category_id"
  #   t.integer "status_id", null: false
  #   t.integer "assigned_to_id"
  #   t.integer "priority_id", null: false
  #   t.integer "fixed_version_id"
  #   t.integer "author_id", null: false
  #   t.integer "lock_version", default: 0, null: false
  #   t.timestamp "created_on"
  #   t.timestamp "updated_on"
  #   t.date "start_date"
  #   t.integer "done_ratio", default: 0, null: false
  #   t.float "estimated_hours"
  #   t.integer "parent_id"
  #   t.integer "root_id"
  #   t.integer "lft"
  #   t.integer "rgt"
  #   t.boolean "is_private", default: false, null: false
  #   t.datetime "closed_on"
  # end

subject = Field('subject', 'varchar(128)')
subject.set_value_generator(lambda: ' '.join(fake.words(nb=2))[:127])
description = Field('description', 'string')
description.set_value_generator(lambda: fake.text(max_nb_chars=1024).replace('\t', ' ').replace('\n', ' '))
due_date = Field('due_date', 'date')
assigned_to_id = Field('assigned_to_id', 'oid')
assigned_to_id.range = [1, user.sz]
created_on = Field('created_on', 'date')
updated_on = Field('updated_on', 'date')
start_date = Field('start_date', 'date')
done_ratio = Field('done_ratio', 'smallint')
done_ratio.range = [0, 100]
estimated_hours = Field('estimated_hours', 'float')
parent_id = Field('parent_id', 'oid')
parent_id.range = [1, issue.sz]
root_id = Field('root_id', 'oid')
lft = Field('lft', 'oid')
rgt = Field('rgt', 'oid')
is_private = Field('is_private', 'bool')
closed_on = Field('closed_on', 'date')
author_id = Field('author_id', 'oid')
author_id.range = [1, user.sz]
priority_id = Field('priority_id', 'smallint')
priority_id.range = [1, 10]
issue.add_fields([subject, description, due_date, assigned_to_id, created_on, updated_on, start_date, \
done_ratio, estimated_hours, parent_id, root_id, lft, rgt, is_private, closed_on, author_id, priority_id])

project_issue = get_new_assoc("project_to_issue", "one_to_many", project, issue, "issues", "project")
issue_tracker = get_new_assoc("issue_to_tracker", "one_to_many", tracker, issue, 'issues', 'tracker')
issue_status_issue = get_new_assoc('issue_to_statuses', 'one_to_many', issue_status, issue, 'issues', 'status')
#issue_user = get_new_assoc('issue_user', 'one_to_many', user, issue, 'issues', 'user')

  # create_table "trackers", id: :integer, options: "ENGINE=InnoDB DEFAULT CHARSET=utf8", force: :cascade do |t|
  #   t.string "name", limit: 30, default: "", null: false
  #   t.boolean "is_in_chlog", default: false, null: false
  #   t.integer "position"
  #   t.boolean "is_in_roadmap", default: true, null: false
  #   t.integer "fields_bits", default: 0
  #   t.integer "default_status_id"
  # end

name = Field('name', 'varchar(16)')
name.set_value_generator(lambda: ' '.join(fake.words(nb=1)[:15]))
is_in_chlog = Field('is_in_chlog', 'bool')
position = Field('position', 'uint')
is_in_roadmap = Field('is_in_roadmap', 'bool')
field_bits = Field('field_bits','uint')
default_status_id = Field('default_status_id', 'int')
tracker.add_fields([name, is_in_chlog, position, is_in_roadmap, default_status_id])

  # create_table "member_roles", id: :integer, options: "ENGINE=InnoDB DEFAULT CHARSET=utf8", force: :cascade do |t|
  #   t.integer "member_id", null: false
  #   t.integer "role_id", null: false
  #   t.integer "inherited_from"
  #   t.index ["inherited_from"], name: "index_member_roles_on_inherited_from"
  #   t.index ["member_id"], name: "index_member_roles_on_member_id"
  #   t.index ["role_id"], name: "index_member_roles_on_role_id"
  # end

  # create_table "members", id: :integer, options: "ENGINE=InnoDB DEFAULT CHARSET=utf8", force: :cascade do |t|
  #   t.integer "user_id", default: 0, null: false
  #   t.integer "project_id", default: 0, null: false
  #   t.timestamp "created_on"
  #   t.boolean "mail_notification", default: false, null: false
  #   t.index ["project_id"], name: "index_members_on_project_id"
  #   t.index ["user_id", "project_id"], name: "index_members_on_user_id_and_project_id", unique: true
  #   t.index ["user_id"], name: "index_members_on_user_id"
  # end

created_on = Field('created_on', 'date')
mail_notification = Field('mail_notification', 'bool')
member.add_fields([created_on, mail_notification])

  # create_table "roles", id: :integer, options: "ENGINE=InnoDB DEFAULT CHARSET=utf8", force: :cascade do |t|
  #   t.string "name", limit: 30, default: "", null: false
  #   t.integer "position"
  #   t.boolean "assignable", default: true
  #   t.integer "builtin", default: 0, null: false
  #   t.text "permissions"
  #   t.string "issues_visibility", limit: 30, default: "default", null: false
  #   t.string "users_visibility", limit: 30, default: "all", null: false
  #   t.string "time_entries_visibility", limit: 30, default: "all", null: false
  #   t.boolean "all_roles_managed", default: true, null: false
  #   t.text "settings"
  # end

position = Field('position', 'smallint')
position.range = [1, 100]
builtin = Field('builtin', 'smallint')
builtin.value_with_prob = [(0, 33), (1, 33), (2, 33)]
assignable = Field('assignable', 'bool')
permissions = Field('permissions', 'varchar(32)')
permissions.value_with_prob = [('add_project', 20), ('edit_project',20), ('close_project', 20), ('select_project_modules', 20), ('manage_members',20)]
settings = Field('settings', 'string')
settings.set_value_generator(lambda: fake.text(max_nb_chars=1024).replace('\t', ' ').replace('\n', ' '))
role.add_fields([position, builtin, assignable, permissions, settings])

member_user = get_new_assoc('member_to_user', 'one_to_many', user, member, 'members', 'user')
project_member = get_new_assoc("project_to_member", "one_to_many", project, member, "members", "project")
member_roles = get_new_assoc("member_roles", 'many_to_many', member, role, 'roles', 'members', 3, 0, "member_id", "role_id")

  # create_table "projects", id: :integer, options: "ENGINE=InnoDB DEFAULT CHARSET=utf8", force: :cascade do |t|
  #   t.string "name", default: "", null: false
  #   t.text "description"
  #   t.string "homepage", default: ""
  #   t.boolean "is_public", default: true, null: false
  #   t.integer "parent_id"
  #   t.timestamp "created_on"
  #   t.timestamp "updated_on"
  #   t.string "identifier"
  #   t.integer "status", default: 1, null: false
  #   t.integer "lft"
  #   t.integer "rgt"
  #   t.boolean "inherit_members", default: false, null: false
  #   t.integer "default_version_id"
  #   t.integer "default_assigned_to_id"
  #   t.index ["lft"], name: "index_projects_on_lft"
  #   t.index ["rgt"], name: "index_projects_on_rgt"
  # end

name = Field('name', 'varchar(64)')
name.set_value_generator(lambda: ' '.join(fake.words(nb=1)[:63]))
description = Field('description', 'string')
description.set_value_generator(lambda: fake.text(max_nb_chars=256).replace('\t', ' ').replace('\n', ' '))
homepage = Field('homepage', 'varchar(128)')
homepage.set_value_generator(lambda: fake.url()[:127])
is_public = Field('is_public','bool')
parent_id = Field('parent_id', 'oid')
parent_id.range = [1, project.sz]
created_on = Field('created_on', 'date')
updated_on = Field('updated_on', 'date')
status = Field('status', 'smallint')
status.value_with_prob = [(1, 33), (5, 33), (9, 33)]
lft = Field('lft', 'oid')
lft.range = [1, project.sz]
rgt = Field('rgt', 'oid')
rgt.range = [1, project.sz]
inherit_members = Field('inherit_members', 'bool')
default_version_id = Field('default_version_id', 'oid')
default_assigned_to_id = Field('default_assigned_to_id', 'oid')
project.add_fields([name, description, homepage, is_public, parent_id, created_on, updated_on, status, lft, rgt, inherit_members, default_version_id, default_assigned_to_id])

project_tracker = get_new_assoc("projects_trackers", "many_to_many", project, tracker, "trackers", "projects", 3, 0, "project_id", "tracker_id")

  # create_table "news", id: :integer, options: "ENGINE=InnoDB DEFAULT CHARSET=utf8", force: :cascade do |t|
  #   t.integer "project_id"
  #   t.string "title", limit: 60, default: "", null: false
  #   t.string "summary", default: ""
  #   t.text "description"
  #   t.integer "author_id", default: 0, null: false
  #   t.timestamp "created_on"
  #   t.integer "comments_count", default: 0, null: false
  #   t.index ["author_id"], name: "index_news_on_author_id"
  #   t.index ["created_on"], name: "index_news_on_created_on"
  #   t.index ["project_id"], name: "news_project_id"
  # end

title = Field('title', 'varchar(64)')
summary = Field('summary', 'varchar(128)')
description = Field('description', 'string')
description.set_value_generator(lambda: fake.text(max_nb_chars=127).replace('\t', ' ').replace('\n', ' '))
created_on = Field('created_on','date')
comments_count = Field('comments_count', 'uint')
author_id = Field('author_id', 'uint')
author_id.range = [1, user.sz]
news.add_fields([title, summary, description, created_on, comments_count, author_id])

project_news = get_new_assoc("project_news", "one_to_many", project, news, "news", "project")

  # create_table "users", id: :integer, options: "ENGINE=InnoDB DEFAULT CHARSET=utf8", force: :cascade do |t|
  #   t.string "login", default: "", null: false
  #   t.string "hashed_password", limit: 40, default: "", null: false
  #   t.string "firstname", limit: 30, default: "", null: false
  #   t.string "lastname", default: "", null: false
  #   t.boolean "admin", default: false, null: false
  #   t.integer "status", default: 1, null: false
  #   t.datetime "last_login_on"
  #   t.string "language", limit: 5, default: ""
  #   t.integer "auth_source_id"
  #   t.timestamp "created_on"
  #   t.timestamp "updated_on"
  #   t.string "type"
  #   t.string "identity_url"
  #   t.string "mail_notification", default: "", null: false
  #   t.string "salt", limit: 64
  #   t.boolean "must_change_passwd", default: false, null: false
  #   t.datetime "passwd_changed_on"
  #   t.index ["auth_source_id"], name: "index_users_on_auth_source_id"
  #   t.index ["id", "type"], name: "index_users_on_id_and_type"
  #   t.index ["type"], name: "index_users_on_type"
  # end

login = Field('login', 'varchar(64)')
hashed_password = Field('hashed_password', 'varchar(40)')
firstname = Field('firstname', 'varchar(30)')
firstname.set_value_generator(lambda: fake.name()[:29])
lastname = Field('lastname', 'varchar(30)')
lastname.set_value_generator(lambda: fake.name()[:29])
admin = Field('admin', 'bool')
status = Field('status', 'smallint')
status.range = [1, 10]
last_login_on = Field('last_login_on', 'date')
language = Field('language', 'varchar(5)')
auth_source_id = Field('auth_source_id', 'oid')
created_on = Field('created_on', 'date')
utype = Field('type', 'varchar(16)')
utype.value_with_prob = [('GroupAnonymous',20), ('User',20), ('AnonymousUser',20), ('Other',20), ('Other2',20)]
identity_url = Field('identity_url', 'varchar(64)')
identity_url.set_value_generator(lambda: fake.url()[:63])
mail_notification = Field('mail_notification', 'string')
mail_notification.set_value_generator(lambda: fake.text(max_nb_chars=128).replace('\t', ' ').replace('\n', ' '))
salt = Field('salt', 'varchar(64)')
must_change_passwd = Field('must_change_passwd', 'bool')
passwd_changed_on = Field('passwd_changed_on', 'date')
user.add_fields([login, hashed_password, firstname, lastname, admin, status, last_login_on, language, auth_source_id,\
created_on, utype, identity_url, mail_notification, salt, must_change_passwd, passwd_changed_on])

  # create_table "issue_statuses", id: :integer, options: "ENGINE=InnoDB DEFAULT CHARSET=utf8", force: :cascade do |t|
  #   t.string "name", limit: 30, default: "", null: false
  #   t.boolean "is_closed", default: false, null: false
  #   t.integer "position"
  #   t.integer "default_done_ratio"
  #   t.index ["is_closed"], name: "index_issue_statuses_on_is_closed"
  #   t.index ["position"], name: "index_issue_statuses_on_position"
  # end

name = Field('name', 'varchar(24)')
is_closed = Field('is_closed', 'bool')
position = Field('position', 'int')
default_done_ratio = Field('default_done_ratio', 'smallint')
default_done_ratio.range = [1, 100]
issue_status.add_fields([name, is_closed, position, default_done_ratio])

  # create_table "enabled_modules", id: :integer, options: "ENGINE=InnoDB DEFAULT CHARSET=utf8", force: :cascade do |t|
  #   t.integer "project_id"
  #   t.string "name", null: false
  #   t.index ["project_id"], name: "enabled_modules_project_id"
  # end

name = Field('name', 'varchar(16)')
name.value_with_prob = [('issue_tracking', 20), ('wiki',20), ('repository',20), ('boards',20), ('news', 20)]
enabled_module.add_fields([name])

project_enabled_module = get_new_assoc("project_to_enabled_module", "one_to_many", project, enabled_module, "enabled_modules", "project")

  # create_table "enumerations", id: :integer, options: "ENGINE=InnoDB DEFAULT CHARSET=utf8", force: :cascade do |t|
  #   t.string "name", limit: 30, default: "", null: false
  #   t.integer "position"
  #   t.boolean "is_default", default: false, null: false
  #   t.string "type"
  #   t.boolean "active", default: true, null: false
  #   t.integer "project_id"
  #   t.integer "parent_id"
  #   t.string "position_name", limit: 30
  #   t.index ["id", "type"], name: "index_enumerations_on_id_and_type"
  #   t.index ["project_id"], name: "index_enumerations_on_project_id"
  # end

name = Field('name', 'varchar(16)')
name.set_value_generator(lambda: fake.name()[:15])
etype = Field('type', 'varchar(16)')
etype.value_with_prob = [('IssuePriority', 25), ('Enumeration', 25), ('DocumentCategory', 25), ('IssuePriority', 25)]
is_default = Field('is_default', 'bool')
active = Field('active', 'bool')
parent_id = Field('parent_id', 'oid')
parent_id.range = [1, enumeration.sz]
position_name = Field('position_name', 'varchar(30)')
enumeration.add_fields([name, etype, is_default, active, parent_id, position_name])

project_enumeration = get_new_assoc("project_to_enumeration", "one_to_many", project, enumeration, "enumerations", "project")
#issue_enumeration = get_new_assoc("issue_to_enumeration", 'one_to_many', enumeration, issue, 'issues', 'enumeration')

  # create_table "versions", id: :integer, options: "ENGINE=InnoDB DEFAULT CHARSET=utf8", force: :cascade do |t|
  #   t.integer "project_id", default: 0, null: false
  #   t.string "name", default: "", null: false
  #   t.string "description", default: ""
  #   t.date "effective_date"
  #   t.timestamp "created_on"
  #   t.timestamp "updated_on"
  #   t.string "wiki_page_title"
  #   t.string "status", default: "open"
  #   t.string "sharing", default: "none", null: false
  #   t.index ["project_id"], name: "versions_project_id"
  #   t.index ["sharing"], name: "index_versions_on_sharing"
  # end

name = Field('name', 'varchar(32)')
description = Field('description', 'varchar(128)')
description.set_value_generator(lambda: fake.text(max_nb_chars=127).replace('\t', ' ').replace('\n', ' '))
effective_date = Field('effective_date', 'date')
created_on = Field('created_on', 'date')
updated_on = Field('updated_on', 'date')
wiki_page_title = Field('wiki_page_title', 'varchar(64)')
wiki_page_title.set_value_generator(lambda: fake.text(max_nb_chars=63).replace('\t', ' ').replace('\n', ' '))
status = Field('status', 'varchar(16)')
status.value_with_prob = [('open', 33), ('locked', 33), ('closed', 33)]
sharing = Field('sharing', 'varchar(16)')
sharing.value_with_prob = [('none',20), ('descendants',20), ('hierarchy',20), ('tree',20), ('system',20)]
version.add_fields([name, description, effective_date, created_on, updated_on, wiki_page_title, status, sharing])

project_version = get_new_assoc("project_version", "one_to_many", project, version, "versions", "project")
#issue_version = get_new_assoc('issue_version', 'one_to_many', version, issue, 'issues', 'version')

  # create_table "boards", id: :integer, options: "ENGINE=InnoDB DEFAULT CHARSET=utf8", force: :cascade do |t|
  #   t.integer "project_id", null: false
  #   t.string "name", default: "", null: false
  #   t.string "description"
  #   t.integer "position"
  #   t.integer "topics_count", default: 0, null: false
  #   t.integer "messages_count", default: 0, null: false
  #   t.integer "last_message_id"
  #   t.integer "parent_id"
  #   t.index ["last_message_id"], name: "index_boards_on_last_message_id"
  #   t.index ["project_id"], name: "boards_project_id"
  # end

name = Field('name', 'varchar(32)')
name.set_value_generator(lambda: fake.name()[:30])
description = Field('description', 'string')
description.set_value_generator(lambda: fake.text(max_nb_chars=256).replace('\t', ' ').replace('\n', ' '))
position = Field('position', 'uint')
topics_count = Field('topics_count', 'uint')
last_message_id = Field('last_message_id', 'uint')
last_message_id.range = [1, message.sz]
parent_id = Field('parent_id', 'oid')
parent_id.range = [1, board.sz]
board.add_fields([name, description, position, topics_count, last_message_id, parent_id])

project_board = get_new_assoc("project_board", "one_to_many", project, board, "boards", "project")

  # create_table "messages", id: :integer, options: "ENGINE=InnoDB DEFAULT CHARSET=utf8", force: :cascade do |t|
  #   t.integer "board_id", null: false
  #   t.integer "parent_id"
  #   t.string "subject", default: "", null: false
  #   t.text "content"
  #   t.integer "author_id"
  #   t.integer "replies_count", default: 0, null: false
  #   t.integer "last_reply_id"
  #   t.datetime "created_on", null: false
  #   t.datetime "updated_on", null: false
  #   t.boolean "locked", default: false
  #   t.integer "sticky", default: 0
  #   t.index ["author_id"], name: "index_messages_on_author_id"
  #   t.index ["board_id"], name: "messages_board_id"
  #   t.index ["created_on"], name: "index_messages_on_created_on"
  #   t.index ["last_reply_id"], name: "index_messages_on_last_reply_id"
  #   t.index ["parent_id"], name: "messages_parent_id"
  # end

parent_id = Field('parent_id', 'uint')
parent_id.range = [1, message.sz]
subject = Field('subject', 'varchar(64)')
content = Field('content', 'string')
content.set_value_generator(lambda: fake.text(max_nb_chars=128).replace('\t', ' ').replace('\n', ' '))
created_on = Field('created_on', 'date')
updated_on = Field('updated_on', 'date')
replies_count = Field('replies_count', 'uint')
author_id = Field('author_id', 'uint')
author_id.range = [1, user.sz]
last_reply_id = Field('last_reply_id', 'uint')
locked = Field('locked','bool')
sticky = Field('sticky', 'smallint')
sticky.range = [1, 10]
message.add_fields([parent_id, subject, content, created_on, updated_on, replies_count, author_id, last_reply_id])

message_board = get_new_assoc("board_message", "one_to_many", board, message, "messages", "board")
