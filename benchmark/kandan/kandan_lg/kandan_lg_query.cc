#include "kandan_lg_query.h"
// prepare query 10 (len param = 0)
// Scan [1] Basic array: User, value = memobj(User-id) : 
//   if ((user:id != Param (uid))) result_user = None
//   
// 

void query_0_plan_0(oid_t param_uid_0, Query0Result& qresult) {
  char msg[] = "query 0 plan 0 run time ";
  get_time_start();
    SMALLBASICARRAY_FOR_BEGIN(user_1_2, user_1, obj_user_2)

      Query0Result::PUser* ele_result_user_3 = nullptr;
      if ((obj_user_2.user_id != param_uid_0)) { if ((&qresult) != nullptr) {
        ele_result_user_3 = (&qresult)->add_user();
        ele_result_user_3->set_id(obj_user_2.user_id);
        ele_result_user_3->set_email(obj_user_2.user_email.c_str());
        ele_result_user_3->set_encrypted_password(obj_user_2.user_encrypted_password.c_str());
        ele_result_user_3->set_reset_password_token(obj_user_2.user_reset_password_token.c_str());
        ele_result_user_3->set_reset_password_sent_at(obj_user_2.user_reset_password_sent_at);
        ele_result_user_3->set_remember_created_at(obj_user_2.user_remember_created_at);
        ele_result_user_3->set_first_name(obj_user_2.user_first_name.c_str());
        ele_result_user_3->set_last_name(obj_user_2.user_last_name.c_str());
        ele_result_user_3->set_signin_count(obj_user_2.user_signin_count);
        ele_result_user_3->set_current_sign_in_at(obj_user_2.user_current_sign_in_at);
        ele_result_user_3->set_current_sign_in_ip(obj_user_2.user_current_sign_in_ip.c_str());
        ele_result_user_3->set_last_sign_in_at(obj_user_2.user_last_sign_in_at);
        ele_result_user_3->set_last_sign_in_ip(obj_user_2.user_last_sign_in_ip.c_str());
        ele_result_user_3->set_auth_token(obj_user_2.user_auth_token.c_str());
        ele_result_user_3->set_locale(obj_user_2.user_locale.c_str());
        ele_result_user_3->set_gravatar_hash(obj_user_2.user_gravatar_hash.c_str());
        ele_result_user_3->set_username(obj_user_2.user_username.c_str());
        ele_result_user_3->set_regstatus(obj_user_2.user_regstatus.c_str());
        ele_result_user_3->set_active(obj_user_2.user_active);
        ele_result_user_3->set_is_admin(obj_user_2.user_is_admin);
        ele_result_user_3->set_avatar_url(obj_user_2.user_avatar_url.c_str());
        ele_result_user_3->set_created_at(obj_user_2.user_created_at);
        ele_result_user_3->set_updated_at(obj_user_2.user_updated_at);
      }
       }

    SMALLBASICARRAY_FOR_END


    print_time_diff(msg);
    printf("sz = %u\n", qresult.user.size());
    size_t cnt_user = 0;
    for (auto i = qresult.user.begin(); i != qresult.user.end(); i++) {
    cnt_user ++;
    if (cnt_user > 20) break;
      printf("	id = %u, email = %.20s, encrypted_password = %.20s, reset_password_token = %.20s, reset_password_sent_at = %u, remember_created_at = %u, first_name = %.20s, last_name = %.20s, signin_count = %u, current_sign_in_at = %u, current_sign_in_ip = %.20s, last_sign_in_at = %u, last_sign_in_ip = %.20s, auth_token = %.20s, locale = %.20s, gravatar_hash = %.20s, username = %.20s, regstatus = %.20s, active = %d, is_admin = %d, avatar_url = %.20s, created_at = %u, updated_at = %u\n", (*i).id(),(*i).email().c_str(),(*i).encrypted_password().c_str(),(*i).reset_password_token().c_str(),(*i).reset_password_sent_at(),(*i).remember_created_at(),(*i).first_name().c_str(),(*i).last_name().c_str(),(*i).signin_count(),(*i).current_sign_in_at(),(*i).current_sign_in_ip().c_str(),(*i).last_sign_in_at(),(*i).last_sign_in_ip().c_str(),(*i).auth_token().c_str(),(*i).locale().c_str(),(*i).gravatar_hash().c_str(),(*i).username().c_str(),(*i).regstatus().c_str(),(*i).active(),(*i).is_admin(),(*i).avatar_url().c_str(),(*i).created_at(),(*i).updated_at());

    }

}


// prepare query 23 (len param = 0)
// Scan [4] Basic array: Channel, value = memobj(Channel-id) : 
//   if (None) result_channel = None
//   Scan [5] Basic array: Channel::ActivitiesInChannel(4), value = memobj(Channel::ActivitiesInChannel-id) : 
//     if (None) result_activities = None
//     Scan [1] Basic array: User, value = memobj(User-id) : 
//       if (None) result_user = None
//       
//     
//   
// 

void query_1_plan_1(Query1Result& qresult) {
  char msg[] = "query 1 plan 1 run time ";
  get_time_start();
    SMALLBASICARRAY_FOR_BEGIN(channel_4_3, channel_4, obj_channel_4)

      Query1Result::PChannel* ele_result_channel_5 = nullptr;
      if (true) { if ((&qresult) != nullptr) {
        ele_result_channel_5 = (&qresult)->add_channel();
        ele_result_channel_5->set_id(obj_channel_4.channel_id);
        ele_result_channel_5->set_name(obj_channel_4.channel_name.c_str());
        ele_result_channel_5->set_created_at(obj_channel_4.channel_created_at);
        ele_result_channel_5->set_updated_at(obj_channel_4.channel_updated_at);
        ele_result_channel_5->set_user_id(obj_channel_4.channel_user_id);
      }
       }
      SMALLBASICARRAY_FOR_BEGIN(activities_5_4, obj_channel_4.activities_5, obj_activities_6)

        Query1Result::PChannel::PActivitiesInChannel* ele_result_activities_7 = nullptr;
        if (true) { if (ele_result_channel_5 != nullptr) {
          ele_result_activities_7 = ele_result_channel_5->add_activities();
          ele_result_activities_7->set_id(obj_activities_6.activity_id);
          ele_result_activities_7->set_created_at(obj_activities_6.activity_created_at);
          ele_result_activities_7->set_updated_at(obj_activities_6.activity_updated_at);
          ele_result_activities_7->set_action(obj_activities_6.activity_action.c_str());
          ele_result_activities_7->set_content(obj_activities_6.activity_content.c_str());
          ele_result_activities_7->set_channel_id(obj_activities_6.activity_channel_id);
          ele_result_activities_7->set_user_id(obj_activities_6.activity_user_id);
        }
         }
        SMALLBASICARRAY_FOR_BEGIN(user_1_5, user_1, obj_user_8)

          Query1Result::PChannel::PActivitiesInChannel::PUserInActivity* ele_result_user_9 = nullptr;
          if (true) { if (ele_result_activities_7 != nullptr) {
            ele_result_user_9 = ele_result_activities_7->mutable_user();
            ele_result_user_9->set_id(obj_user_8.user_id);
            ele_result_user_9->set_email(obj_user_8.user_email.c_str());
            ele_result_user_9->set_encrypted_password(obj_user_8.user_encrypted_password.c_str());
            ele_result_user_9->set_reset_password_token(obj_user_8.user_reset_password_token.c_str());
            ele_result_user_9->set_reset_password_sent_at(obj_user_8.user_reset_password_sent_at);
            ele_result_user_9->set_remember_created_at(obj_user_8.user_remember_created_at);
            ele_result_user_9->set_first_name(obj_user_8.user_first_name.c_str());
            ele_result_user_9->set_last_name(obj_user_8.user_last_name.c_str());
            ele_result_user_9->set_signin_count(obj_user_8.user_signin_count);
            ele_result_user_9->set_current_sign_in_at(obj_user_8.user_current_sign_in_at);
            ele_result_user_9->set_current_sign_in_ip(obj_user_8.user_current_sign_in_ip.c_str());
            ele_result_user_9->set_last_sign_in_at(obj_user_8.user_last_sign_in_at);
            ele_result_user_9->set_last_sign_in_ip(obj_user_8.user_last_sign_in_ip.c_str());
            ele_result_user_9->set_auth_token(obj_user_8.user_auth_token.c_str());
            ele_result_user_9->set_locale(obj_user_8.user_locale.c_str());
            ele_result_user_9->set_gravatar_hash(obj_user_8.user_gravatar_hash.c_str());
            ele_result_user_9->set_username(obj_user_8.user_username.c_str());
            ele_result_user_9->set_regstatus(obj_user_8.user_regstatus.c_str());
            ele_result_user_9->set_active(obj_user_8.user_active);
            ele_result_user_9->set_is_admin(obj_user_8.user_is_admin);
            ele_result_user_9->set_avatar_url(obj_user_8.user_avatar_url.c_str());
            ele_result_user_9->set_created_at(obj_user_8.user_created_at);
            ele_result_user_9->set_updated_at(obj_user_8.user_updated_at);
          }
           }

        SMALLBASICARRAY_FOR_END


      SMALLBASICARRAY_FOR_END


    SMALLBASICARRAY_FOR_END


    print_time_diff(msg);
    printf("sz = %u\n", qresult.channel.size());
    size_t cnt_channel = 0;
    for (auto i = qresult.channel.begin(); i != qresult.channel.end(); i++) {
    cnt_channel ++;
    if (cnt_channel > 20) break;
      printf("	id = %u, name = %.20s, created_at = %u, updated_at = %u, user_id = %u\n", (*i).id(),(*i).name().c_str(),(*i).created_at(),(*i).updated_at(),(*i).user_id());
      printf("sz = %u\n", (*i).activities_size());
      for (size_t i_activities = 0; i_activities != (*i).activities_size(); i_activities++) {
          auto& element_activities = (*i).activities[i_activities];
        printf("		id = %u, created_at = %u, updated_at = %u, action = %.20s, content = %.20s, channel_id = %u, user_id = %u\n", element_activities.id(),element_activities.created_at(),element_activities.updated_at(),element_activities.action().c_str(),element_activities.content().c_str(),element_activities.channel_id(),element_activities.user_id());
        auto& element_user = element_activities.user;
          printf("			id = %u, email = %.20s, encrypted_password = %.20s, reset_password_token = %.20s, reset_password_sent_at = %u, remember_created_at = %u, first_name = %.20s, last_name = %.20s, signin_count = %u, current_sign_in_at = %u, current_sign_in_ip = %.20s, last_sign_in_at = %u, last_sign_in_ip = %.20s, auth_token = %.20s, locale = %.20s, gravatar_hash = %.20s, username = %.20s, regstatus = %.20s, active = %d, is_admin = %d, avatar_url = %.20s, created_at = %u, updated_at = %u\n", element_user.id(),element_user.email().c_str(),element_user.encrypted_password().c_str(),element_user.reset_password_token().c_str(),element_user.reset_password_sent_at(),element_user.remember_created_at(),element_user.first_name().c_str(),element_user.last_name().c_str(),element_user.signin_count(),element_user.current_sign_in_at(),element_user.current_sign_in_ip().c_str(),element_user.last_sign_in_at(),element_user.last_sign_in_ip().c_str(),element_user.auth_token().c_str(),element_user.locale().c_str(),element_user.gravatar_hash().c_str(),element_user.username().c_str(),element_user.regstatus().c_str(),element_user.active(),element_user.is_admin(),element_user.avatar_url().c_str(),element_user.created_at(),element_user.updated_at());


      }

    }

}


