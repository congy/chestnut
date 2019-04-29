import sys
import os
sys.path.append("../../")
from schema import *
from query import *
from pred import *

from faker import Faker
fake = Faker()

scale = 10

agent = Table('agent', scale)
event = Table('event', scale*100)
delayed_job = Table('delayed_job', scale*2)
link = Table('link',scale)
user = Table('user',5)

def fake_text(length):
  return lambda: fake.text(max_nb_chars=length).replace('\n',' ').replace('\t',' ')


# create_table "agents", id: :integer, options: "ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci", force: :cascade do |t|
#     t.integer "user_id"
#     t.text "options", collation: "utf8mb4_bin"
#     t.string "type", collation: "utf8_bin"
#     t.string "name", collation: "utf8mb4_bin"
#     t.string "schedule", collation: "utf8_bin"
#     t.integer "events_count", default: 0, null: false
#     t.datetime "last_check_at"
#     t.datetime "last_receive_at"
#     t.integer "last_checked_event_id"
#     t.datetime "created_at"
#     t.datetime "updated_at"
#     t.text "memory", limit: 4294967295, collation: "utf8mb4_bin"
#     t.datetime "last_web_request_at"
#     t.integer "keep_events_for", default: 0, null: false
#     t.datetime "last_event_at"
#     t.datetime "last_error_log_at"
#     t.boolean "propagate_immediately", default: false, null: false
#     t.boolean "disabled", default: false, null: false
#     t.integer "service_id"
#     t.string "guid", null: false, collation: "utf8mb4_general_ci"
#     t.boolean "deactivated", default: false
#     t.index ["disabled", "deactivated"], name: "index_agents_on_disabled_and_deactivated"
#     t.index ["guid"], name: "index_agents_on_guid"
#     t.index ["schedule"], name: "index_agents_on_schedule"
#     t.index ["type"], name: "index_agents_on_type"
#     t.index ["user_id", "created_at"], name: "index_agents_on_user_id_and_created_at"
#   end

a_options = Field('options','string')
a_options.set_value_generator(fake_text(32))
a_type = Field('type','varchar(16)')
a_type.value_with_prob = [('Agents::EmailAgent',15),('Agents::EmailDigestAgent',15),('Agents::EventFormattingAgent',15),('Agents::HttpStatusAgent',15),('Agents::TriggerAgent',10),('Agents::WeatherAgent',10),('Agents::WebsiteAgent',10),('Agents:WeiboAgent',10)]
a_name = Field('name','varchar(16)')
a_name.set_value_generator(lambda: fake.name()[:16])
a_schedule = Field('schedule','varchar(16)')
a_schedule.value_with_prob = [('every_1m',10),('every_5m',10),('every_10m',10),('every_1h',10),('every_2h',10),('every_1d',10),('every_3d',10),('every_5d',10),('every_1week',10),('every_1month',10)]
a_events_count = Field('events_count','uint')
a_events_count.range = [1, event.sz/10]
a_last_check_at = Field('last_check_at', 'date')
a_last_check_event_id = Field('last_check_event_id', 'uint')
a_last_check_event_id.range = [1, event.sz]
a_receive_at = Field('receive_at','date')
a_created_at = Field('created_at', 'date')
a_updated_at = Field('updated_at', 'date')
a_memory = Field('memory','string')
a_memory.set_value_generator(fake_text(128))
a_last_web_request_at = Field('last_web_request_at','date')
a_keep_events_for = Field('keep_events_for','uint')
a_last_event_at = Field('last_event_at','date')
a_last_error_log_at = Field('last_error_log_at','date')
a_propagate_immediately = Field('propagate_immediately','bool')
a_disabled = Field('disabled','bool')
a_service_id = Field('service_id','uint')
a_guid = Field('guid', 'varchar(64)')
a_deactivated = Field('deactivated','bool')
agent.add_fields([a_options,a_type,a_name,a_schedule,a_events_count,a_last_check_at,a_last_check_event_id,a_receive_at,a_created_at,\
  a_updated_at,a_memory,a_last_web_request_at,a_keep_events_for,a_last_event_at,a_last_error_log_at,a_propagate_immediately,\
    a_disabled,a_service_id,a_guid,a_deactivated])

agent_to_user = get_new_assoc('agents_user','one_to_many',user,agent,'agents','user',0,0)


# create_table "delayed_jobs", id: :integer, options: "ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci", force: :cascade do |t|
#     t.integer "priority", default: 0
#     t.integer "attempts", default: 0
#     t.text "handler", limit: 16777215, collation: "utf8mb4_bin"
#     t.text "last_error", collation: "utf8mb4_bin"
#     t.datetime "run_at"
#     t.datetime "locked_at"
#     t.datetime "failed_at"
#     t.string "locked_by"
#     t.string "queue"
#     t.datetime "created_at"
#     t.datetime "updated_at"
#     t.index ["priority", "run_at"], name: "delayed_jobs_priority"
#   end

import random
import datetime
def get_random_date():
  return str(datetime.datetime.now()-datetime.timedelta(days=random.randint(0, 365), hours=random.randint(0, 24), seconds=random.randint(0, 3600)))[0:-7]

d_priority = Field('priority','uint')
d_attempts = Field('attempts','uint')
d_handler = Field('handler','string')
d_handler.set_value_generator(fake_text(32))
d_last_error = Field('last_error','string')
d_last_error.set_value_generator(fake_text(128))
d_run_at = Field('run_at','date')
d_locked_at = Field('locked_at','date')
d_locked_at.set_value_generator(lambda: get_random_date() if random.randint(1, 10)<6 else '0000-00-00 00:00:00')
d_failed_at = Field('failed_at','date')
d_failed_at.value_with_prob = [('0000-00-00 00:00:00',80),('2019-01-01 00:00:00',20)]
d_locked_by = Field('locked_by','varchar(32)')
d_queue = Field('queue','varchar(16)')
d_created_at = Field('created_at','date')
d_updated_at = Field('updated_at','date')
delayed_job.add_fields([d_priority,d_attempts,d_handler,d_last_error,d_run_at,d_locked_at,d_failed_at,d_locked_by,d_queue,d_created_at,d_updated_at])

  # create_table "events", id: :integer, options: "ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci", force: :cascade do |t|
  #   t.integer "user_id"
  #   t.integer "agent_id"
  #   t.decimal "lat", precision: 15, scale: 10
  #   t.decimal "lng", precision: 15, scale: 10
  #   t.text "payload", limit: 16777215, collation: "utf8mb4_bin"
  #   t.datetime "created_at"
  #   t.datetime "updated_at"
  #   t.datetime "expires_at"
  #   t.index ["agent_id", "created_at"], name: "index_events_on_agent_id_and_created_at"
  #   t.index ["expires_at"], name: "index_events_on_expires_at"
  #   t.index ["user_id", "created_at"], name: "index_events_on_user_id_and_created_at"
  # end
e_lat = Field('lat','float')
e_lng = Field('lng','float')
e_payload = Field('payload','string')
e_payload.set_value_generator(fake_text(128))
e_created_at = Field('created_at','date')
e_updated_at = Field('updated_at','date')
e_expires_at = Field('expires_at','date')
event.add_fields([e_lat,e_lng,e_payload,e_created_at,e_updated_at,e_expires_at])

event_to_agent = get_new_assoc('events_agent','one_to_many',agent,event,'events','agent',0,0)
event_to_user = get_new_assoc('events_user','one_to_many',user,event,'events','user',0,0)

  # create_table "links", id: :integer, options: "ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci", force: :cascade do |t|
  #   t.integer "source_id"
  #   t.integer "receiver_id"
  #   t.datetime "created_at"
  #   t.datetime "updated_at"
  #   t.integer "event_id_at_creation", default: 0, null: false
  #   t.index ["receiver_id", "source_id"], name: "index_links_on_receiver_id_and_source_id"
  #   t.index ["source_id", "receiver_id"], name: "index_links_on_source_id_and_receiver_id"
  # end
l_created_at = Field('created_at','date')
l_updated_at = Field('updated_at','date')
l_event_id_at_creation = Field('event_id_at_creation','uint')
l_event_id_at_creation.range = [1, event.sz]
link.add_fields([l_created_at,l_updated_at,l_event_id_at_creation])

link_source = get_new_assoc('link_source','one_to_many',agent,link,'sources','source',0,0)
link_receive = get_new_assoc('link_receive','one_to_many',agent,link,'receivers','receiver',0,0)

  # create_table "users", id: :integer, options: "ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci", force: :cascade do |t|
  #   t.string "email", default: "", null: false, collation: "utf8_bin"
  #   t.string "encrypted_password", default: "", null: false, collation: "ascii_bin"
  #   t.string "reset_password_token", collation: "utf8_bin"
  #   t.datetime "reset_password_sent_at"
  #   t.datetime "remember_created_at"
  #   t.integer "sign_in_count", default: 0
  #   t.datetime "current_sign_in_at"
  #   t.datetime "last_sign_in_at"
  #   t.string "current_sign_in_ip"
  #   t.string "last_sign_in_ip"
  #   t.datetime "created_at"
  #   t.datetime "updated_at"
  #   t.boolean "admin", default: false, null: false
  #   t.integer "failed_attempts", default: 0
  #   t.string "unlock_token"
  #   t.datetime "locked_at"
  #   t.string "username", collation: "utf8mb4_unicode_ci"
  #   t.string "invitation_code"
  #   t.integer "scenario_count", default: 0, null: false
  #   t.string "confirmation_token"
  #   t.datetime "confirmed_at"
  #   t.datetime "confirmation_sent_at"
  #   t.string "unconfirmed_email"
  #   t.datetime "deactivated_at"
  # end
u_email = Field('email','varchar(16)')
u_encrypted_password = Field('encrypted_password', 'varchar(128)')
u_reset_password_token = Field('reset_password_token','varchar(128)')
u_reset_password_sent_at = Field('reset_password_sent_at','date')
u_remember_created_at = Field("remember_created_at",'date')
u_sign_in_count = Field('sign_in_count','uint')
u_current_sign_in_at = Field('current_sign_in_at','date')
u_last_sign_in_at = Field('last_sign_in_at','date')
u_current_sign_in_ip = Field('current_sign_in_ip','varchar(16')
u_last_sign_in_ip = Field('last_sign_in_ip','varchar(16)')
u_created_at = Field('created_at','date')
u_updated_at = Field('updated_at','date')
u_admin = Field('admin','bool')
u_failed_attempts = Field('failed_attempts','uint')
u_unlock_token = Field('unlock_token','varchar(128)')
u_locked_at = Field('locked_at','date')
u_username = Field('username','string')
u_username.set_value_generator(lambda: fake.name()[:16])
u_invitation_code = Field('invitation_code','string')
u_invitation_code.set_value_generator(fake_text(32))
u_scenario_count = Field('scenario_count','uint')
u_confirmation_token = Field('confirmation_token','string')
u_confirmation_token.set_value_generator(fake_text(32))
u_confirmed_at = Field('confirmed_at','date')
u_confirmation_sent_at = Field('confirmation_sent_at','date')
u_unconfirmed_email = Field('unconfirmed_email','string')
u_unconfirmed_email.set_value_generator(fake_text(32))
u_deactivated_at = Field('deactivated_at','date')
user.add_fields([u_email, u_encrypted_password,u_reset_password_sent_at,u_reset_password_token,u_remember_created_at,\
  u_sign_in_count,u_current_sign_in_at,u_current_sign_in_ip,u_last_sign_in_at,u_last_sign_in_ip,\
    u_created_at,u_updated_at,u_admin,u_failed_attempts,u_unlock_token,u_locked_at,u_username,u_invitation_code,u_scenario_count,\
      u_confirmation_sent_at,u_confirmed_at,u_unconfirmed_email,u_confirmation_token,u_deactivated_at])
