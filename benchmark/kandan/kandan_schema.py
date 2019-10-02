import sys
import os
sys.path.append("../../")
from schema import *
from query import *
from pred import *

from faker import Faker
fake = Faker()

#scale = 10000
scale = 20000 #1000
#scale = 10
channel = Table('channel', 500)
activity = Table('activity', 500*scale)
user = Table('user', 10*scale)
attachment = Table('attachment', 2*scale)

# create_table "activities", :force => true do |t|
#     t.text     "content"
#     t.integer  "channel_id"
#     t.integer  "user_id"
#     t.string   "action"
#     t.datetime "created_at", :null => false
#     t.datetime "updated_at", :null => false
#   end

a_created_at = Field('created_at', 'date')
a_updated_at = Field('updated_at', 'date')
a_action = Field('action', 'varchar(16)')
a_action.value_with_prob = [('connect', 20), ('disconnect', 20), ('upload', 10), ('message', 50)]
a_content = Field('content', 'string')
a_content.set_value_generator(lambda: fake.text(max_nb_chars=1024).replace('\n',' ').replace('\t',' '))
activity.add_fields([a_created_at, a_updated_at, a_action, a_content])

# create_table "channels", :force => true do |t|
#     t.text     "name"
#     t.datetime "created_at", :null => false
#     t.datetime "updated_at", :null => false
#     t.integer  "user_id"
#   end

c_name = Field('name', 'varchar(64)')
c_name.set_value_generator(lambda: fake.name())
c_created_at = Field('created_at', 'date')
c_updated_at = Field('updated_at', 'date')
channel.add_fields([c_name, c_created_at, c_updated_at])

# class Channel < ActiveRecord::Base
#   has_many :activities, :dependent => :destroy
#   has_many :attachments, :dependent => :destroy
#   belongs_to :user

# class Activity < ActiveRecord::Base
#   belongs_to :user
#   belongs_to :channel

# create_table "attachments", :force => true do |t|
#     t.integer  "user_id"
#     t.integer  "channel_id"
#     t.integer  "message_id"
#     t.string   "file_file_name"
#     t.string   "file_content_type"
#     t.integer  "file_file_size"
#     t.datetime "file_updated_at"
#     t.datetime "created_at",        :null => false
#     t.datetime "updated_at",        :null => false
#   end

t_filename = Field('file_file_name', 'varchar(128)')
t_filename.set_value_generator(lambda: fake.name())
t_contenttype = Field('file_content_type', 'varchar(16)')
t_contenttype.value_with_prob = [('message', 25), ('paragraph', 25), ('test', 25), ('long-article', 25)]
t_filesz = Field('file_file_size', 'uint')
t_messageid = Field('message_id', 'uint')
t_fileupdated = Field('file_updated_at', 'date')
t_created_at = Field('created_at', 'date')
t_updated_at = Field('updated_at', 'date')
attachment.add_fields([t_filename, t_contenttype, t_filesz, t_messageid, t_fileupdated, t_created_at, t_updated_at])


# create_table "users", :force => true do |t|
#     t.string   "email",                  :default => "",       :null => false
#     t.string   "encrypted_password",     :default => "",       :null => false
#     t.string   "reset_password_token"
#     t.datetime "reset_password_sent_at"
#     t.datetime "remember_created_at"
#     t.integer  "sign_in_count",          :default => 0
#     t.datetime "current_sign_in_at"
#     t.datetime "last_sign_in_at"
#     t.string   "current_sign_in_ip"
#     t.string   "last_sign_in_ip"
#     t.string   "authentication_token"
#     t.text     "first_name"
#     t.text     "last_name"
#     t.string   "locale"
#     t.datetime "created_at",                                   :null => false
#     t.datetime "updated_at",                                   :null => false
#     t.text     "gravatar_hash"
#     t.boolean  "active",                 :default => true
#     t.string   "username"
#     t.boolean  "is_admin"
#     t.string   "registration_status",    :default => "active"
#     t.string   "avatar_url"
#   end

u_email = Field('email', 'varchar(32)')
u_email.set_value_generator(lambda: fake.email())

u_encrypted_password = Field('encrypted_password', 'varchar(256)')
#u_encrypted_password.value_generator = lambda: fake.password(length=256, digits=True, upper_case=True, lower_case=True)

u_reset_password_token = Field('reset_password_token', 'varchar(256)')
#u_reset_password_token.value_generator = value_generator = lambda: fake.password(length=32, digits=True, upper_case=True, lower_case=True)

u_reset_password_sent_at = Field('reset_password_sent_at', 'date')

u_remember_created_at = Field('remember_created_at', 'date')

u_first_name = Field('first_name', 'varchar(32)')
u_first_name.set_value_generator(lambda: fake.first_name()[:31])

u_last_name = Field('last_name', 'varchar(32)')
u_last_name.set_value_generator(lambda: fake.last_name()[:31])

u_signin_count = Field('signin_count', 'uint')

u_current_signin = Field('current_sign_in_at', 'date')

u_current_signin_ip = Field('current_sign_in_ip', 'varchar(16)')
u_current_signin_ip.set_value_generator(lambda: fake.ipv4())

u_last_signin = Field('last_sign_in_at', 'date')

u_last_signin_ip = Field('last_sign_in_ip', 'varchar(16)')
u_last_signin_ip.set_value_generator(lambda: fake.ipv4())

u_auth_token = Field('auth_token', 'varchar(128)')

u_locale = Field('locale', 'varchar(16)')
u_locale.set_value_generator(lambda: fake.locale()[:15])

u_gravatar_hash = Field('gravatar_hash', 'varchar(256)')

u_username = Field('username', 'varchar(32)')
u_username.set_value_generator(lambda: fake.user_name()[:31])

u_regstatus = Field('regstatus', 'varchar(8)')
u_regstatus.value_with_prob = [('active', 70), ('inactive', 30)]

u_active = Field('active', 'bool')

u_is_admin = Field('is_admin', 'bool')

u_avatar_url = Field('avatar_url', 'string')
u_avatar_url.set_value_generator(lambda: fake.url())

u_created_at = Field('created_at', 'date')
u_updated_at = Field('updated_at', 'date')

user.add_fields([u_email,\
u_encrypted_password, \
u_reset_password_token, \
u_reset_password_sent_at, \
u_remember_created_at, \
u_first_name, \
u_last_name, \
u_signin_count, \
u_current_signin, \
u_current_signin_ip, \
u_last_signin, \
u_last_signin_ip, \
u_auth_token, \
u_locale, \
u_gravatar_hash, \
u_username, \
u_regstatus, \
u_active, \
u_is_admin, \
u_avatar_url, \
u_created_at, \
u_updated_at])

# types = ["int", "oid", "uint", "smallint", "float", "bool", "date"]

channel_to_activitiy = get_new_assoc("channel_activity", "one_to_many", channel, activity, "activities", "channel", 0, 0)
channel_user = get_new_assoc("channel_user", 'one_to_many', user, channel, 'channels', 'user', 0, 0)
activity_user = get_new_assoc("activity_user", 'one_to_many', user, activity, 'activities', 'user', 0, 0)
attachment_user = get_new_assoc('attachment_user', 'one_to_many', user, attachment, 'attachments', 'user')
attachment_channel = get_new_assoc('attachment_channel', 'one_to_many', channel, attachment, 'attachments', 'channel')

