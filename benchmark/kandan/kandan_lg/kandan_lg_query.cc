#include "kandan_lg_query.h"
// prepare query 9 (len param = 0)
// Index point on [[35] treeindex : [table = Activity, keys = (-activity:id), cond = ((activity:id >= Value (1)) && (activity:id <= Value (10000000))), value = ptr to 1]] (params = [(Param (id))]): 
//   if (None) result_activity = None
//   
// 

void query_0_plan_6(oid_t param_id_0, Query0Result& qresult) {
  char msg[] = "query 0 plan 6 run time ";
  get_time_start();
    ds_35_key_type v_ds_35_key0_5(param_id_0);
    TREEINDEX_INDEX_FOR_BEGIN(ds_35_4, &v_ds_35_key0_5, ds_35, obj_activity_4)
      auto ptr_obj_activity_6 = (activity_1.get_ptr_by_pos(obj_activity_4.pos));
      if (ptr_obj_activity_6 == nullptr) continue;
      auto& obj_activity_6 = *ptr_obj_activity_6;

      Query0Result::PActivity* ele_result_activity_7 = nullptr;
      if (true) { if ((&qresult) != nullptr) {
        ele_result_activity_7 = (&qresult)->add_activity();
        ele_result_activity_7->set_id(obj_activity_6.activity_id);
        ele_result_activity_7->set_created_at(obj_activity_6.activity_created_at);
        ele_result_activity_7->set_updated_at(obj_activity_6.activity_updated_at);
        ele_result_activity_7->set_action(obj_activity_6.activity_action.c_str());
        ele_result_activity_7->set_content(obj_activity_6.activity_content.c_str());
        ele_result_activity_7->set_channel_id(obj_activity_6.activity_channel_id);
        ele_result_activity_7->set_user_id(obj_activity_6.activity_user_id);
      }
       }

    TREEINDEX_INDEX_FOR_END


    print_time_diff(msg);
    printf("sz = %u\n", qresult.activity.size());
    size_t cnt_activity = 0;
    for (auto i = qresult.activity.begin(); i != qresult.activity.end(); i++) {
    cnt_activity ++;
    if (cnt_activity > 20) break;
      printf("	id = %u, created_at = %u, updated_at = %u, action = %.20s, content = %.20s, channel_id = %u, user_id = %u\n", (*i).id(),(*i).created_at(),(*i).updated_at(),(*i).action().c_str(),(*i).content().c_str(),(*i).channel_id(),(*i).user_id());

    }

}


// prepare query 10 (len param = 0)
// Scan [4] Basic array: User, value = memobj(User-id) : 
//   if ((user:id != Param (uid))) result_user = None
//   
// 

void query_1_plan_0(oid_t param_uid_0, Query1Result& qresult) {
  char msg[] = "query 1 plan 0 run time ";
  get_time_start();
    SMALLBASICARRAY_FOR_BEGIN(user_4_5, user_4, obj_user_8)

      Query1Result::PUser* ele_result_user_9 = nullptr;
      if ((obj_user_8.user_id != param_uid_0)) { if ((&qresult) != nullptr) {
        ele_result_user_9 = (&qresult)->add_user();
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


    print_time_diff(msg);
    printf("sz = %u\n", qresult.user.size());
    size_t cnt_user = 0;
    for (auto i = qresult.user.begin(); i != qresult.user.end(); i++) {
    cnt_user ++;
    if (cnt_user > 20) break;
      printf("	id = %u, email = %.20s, encrypted_password = %.20s, reset_password_token = %.20s, reset_password_sent_at = %u, remember_created_at = %u, first_name = %.20s, last_name = %.20s, signin_count = %u, current_sign_in_at = %u, current_sign_in_ip = %.20s, last_sign_in_at = %u, last_sign_in_ip = %.20s, auth_token = %.20s, locale = %.20s, gravatar_hash = %.20s, username = %.20s, regstatus = %.20s, active = %d, is_admin = %d, avatar_url = %.20s, created_at = %u, updated_at = %u\n", (*i).id(),(*i).email().c_str(),(*i).encrypted_password().c_str(),(*i).reset_password_token().c_str(),(*i).reset_password_sent_at(),(*i).remember_created_at(),(*i).first_name().c_str(),(*i).last_name().c_str(),(*i).signin_count(),(*i).current_sign_in_at(),(*i).current_sign_in_ip().c_str(),(*i).last_sign_in_at(),(*i).last_sign_in_ip().c_str(),(*i).auth_token().c_str(),(*i).locale().c_str(),(*i).gravatar_hash().c_str(),(*i).username().c_str(),(*i).regstatus().c_str(),(*i).active(),(*i).is_admin(),(*i).avatar_url().c_str(),(*i).created_at(),(*i).updated_at());

    }

}


// prepare query 16 (len param = 0)
// Index range[] on [[12] sorted-array : [table = Attachment, keys = (attachment:channel-channel:id,-attachment:created_at), cond = (((attachment:channel . channel:id) == Param (channel_id)) && ((attachment:created_at >= Value (0)) && (attachment:created_at <= Value (4294967295)))), value = memobj(Attachment-id)]] (params = [(Param (channel_id),Value (0)),(Param (channel_id),Value (4294967295))]): 
//   if (None) result_attachment = None
//   
// 

void query_2_plan_13(oid_t param_channel_id_0, Query2Result& qresult) {
  char msg[] = "query 2 plan 13 run time ";
  get_time_start();
    ds_12_key_type v_ds_12_key0_11(param_channel_id_0,0);
    ds_12_key_type v_ds_12_key1_12(param_channel_id_0,4294967295);
    SORTEDARRAY_RANGE_FOR_BEGIN(ds_12_6, &v_ds_12_key0_11, &v_ds_12_key1_12, ds_12, obj_attachment_10)

      Query2Result::PAttachment* ele_result_attachment_13 = nullptr;
      if (true) { if ((&qresult) != nullptr) {
        ele_result_attachment_13 = (&qresult)->add_attachment();
        ele_result_attachment_13->set_id(obj_attachment_10.attachment_id);
        ele_result_attachment_13->set_file_file_name(obj_attachment_10.attachment_file_file_name.c_str());
        ele_result_attachment_13->set_file_content_type(obj_attachment_10.attachment_file_content_type.c_str());
        ele_result_attachment_13->set_file_file_size(obj_attachment_10.attachment_file_file_size);
        ele_result_attachment_13->set_message_id(obj_attachment_10.attachment_message_id);
        ele_result_attachment_13->set_file_updated_at(obj_attachment_10.attachment_file_updated_at);
        ele_result_attachment_13->set_created_at(obj_attachment_10.attachment_created_at);
        ele_result_attachment_13->set_updated_at(obj_attachment_10.attachment_updated_at);
        ele_result_attachment_13->set_user_id(obj_attachment_10.attachment_user_id);
        ele_result_attachment_13->set_channel_id(obj_attachment_10.attachment_channel_id);
      }
       }

    SORTEDARRAY_INDEX_FOR_END


    print_time_diff(msg);
    printf("sz = %u\n", qresult.attachment.size());
    size_t cnt_attachment = 0;
    for (auto i = qresult.attachment.begin(); i != qresult.attachment.end(); i++) {
    cnt_attachment ++;
    if (cnt_attachment > 20) break;
      printf("	id = %u, file_file_name = %.20s, file_content_type = %.20s, file_file_size = %u, message_id = %u, file_updated_at = %u, created_at = %u, updated_at = %u, user_id = %u, channel_id = %u\n", (*i).id(),(*i).file_file_name().c_str(),(*i).file_content_type().c_str(),(*i).file_file_size(),(*i).message_id(),(*i).file_updated_at(),(*i).created_at(),(*i).updated_at(),(*i).user_id(),(*i).channel_id());

    }

}


// prepare query 19 (len param = 0)
// Index point on [[22] sorted-array : [table = Channel, keys = (-channel:id), cond = (channel:id == Param (channel_id)), value = memobj(Channel-id)]] (params = [(Param (channel_id))]): 
//   if (None) result_channel = None
//   if (None) count = Value (0)
//   Index range[] on [[31] sorted-array : [table = Channel::ActivitiesInChannel(22), keys = (-activity:id), cond = ((activity:id >= Value (1)) && (activity:id <= Value (10000000))), value = ptr to 1]] (params = [(Value (1)),(Value (10000000))]): 
//     if (None) count = count()
//     if (None) result_activities = None
//     Scan [29] Basic array: Activity::UserInActivity(1), value = memobj(Activity::UserInActivity-id) : 
//       if (None) result_user = None
//       
//     
//   
// 

void query_3_plan_14(oid_t param_channel_id_0, Query3Result& qresult) {
  char msg[] = "query 3 plan 14 run time ";
  get_time_start();
    ds_22_key_type v_ds_22_key0_15(param_channel_id_0);
    SORTEDARRAY_INDEX_FOR_BEGIN(ds_22_7, &v_ds_22_key0_15, ds_22, obj_channel_14)

      Query3Result::PChannel* ele_result_channel_16 = nullptr;
      if (true) { if ((&qresult) != nullptr) {
        ele_result_channel_16 = (&qresult)->add_channel();
        ele_result_channel_16->set_id(obj_channel_14.channel_id);
        ele_result_channel_16->set_name(obj_channel_14.channel_name.c_str());
        ele_result_channel_16->set_created_at(obj_channel_14.channel_created_at);
        ele_result_channel_16->set_updated_at(obj_channel_14.channel_updated_at);
        ele_result_channel_16->set_user_id(obj_channel_14.channel_user_id);
      }
       }
      uint32_t e_count_17;
      if (true) { e_count_17 = 0; }
      Channel22::ds_31_key_type v_ds_31_key0_19(1);
      Channel22::ds_31_key_type v_ds_31_key1_20(10000000);
      SORTEDARRAY_RANGE_FOR_BEGIN(ds_31_8, &v_ds_31_key0_19, &v_ds_31_key1_20, obj_channel_14.ds_31, obj_activities_18)
        auto ptr_obj_activities_21 = (activity_1.get_ptr_by_pos(obj_activities_18.pos));
        if (ptr_obj_activities_21 == nullptr) continue;
        auto& obj_activities_21 = *ptr_obj_activities_21;

        if (true) { e_count_17++;
         }
        Query3Result::PChannel::PActivitiesInChannel* ele_result_activities_22 = nullptr;
        if (true) { if (ele_result_channel_16 != nullptr) {
          ele_result_activities_22 = ele_result_channel_16->add_activities();
          ele_result_activities_22->set_content(obj_activities_21.activity_content.c_str());
          ele_result_activities_22->set_action(obj_activities_21.activity_action.c_str());
          ele_result_activities_22->set_created_at(obj_activities_21.activity_created_at);
          ele_result_activities_22->set_updated_at(obj_activities_21.activity_updated_at);
          ele_result_activities_22->set_id(obj_activities_21.activity_id);
        }
         }
        auto& obj_user_23 = obj_activities_21.user;

          Query3Result::PChannel::PActivitiesInChannel::PUserInActivity* ele_result_user_24 = nullptr;
          if (true) { if (ele_result_activities_22 != nullptr) {
            ele_result_user_24 = ele_result_activities_22->mutable_user();
            ele_result_user_24->set_id(obj_user_23.user_id);
            ele_result_user_24->set_username(obj_user_23.user_username.c_str());
          }
           }


      SORTEDARRAY_INDEX_FOR_END


    SORTEDARRAY_INDEX_FOR_END


    print_time_diff(msg);
    printf("sz = %u\n", qresult.channel.size());
    size_t cnt_channel = 0;
    for (auto i = qresult.channel.begin(); i != qresult.channel.end(); i++) {
    cnt_channel ++;
    if (cnt_channel > 20) break;
      printf("	id = %u, name = %.20s, created_at = %u, updated_at = %u, user_id = %u, count = %u\n", (*i).id(),(*i).name().c_str(),(*i).created_at(),(*i).updated_at(),(*i).user_id(),(*i).count());
      printf("sz = %u\n", (*i).activities_size());
      for (size_t i_activities = 0; i_activities != (*i).activities_size(); i_activities++) {
          auto& element_activities = (*i).activities[i_activities];
        printf("		content = %.20s, action = %.20s, created_at = %u, updated_at = %u\n", element_activities.content().c_str(),element_activities.action().c_str(),element_activities.created_at(),element_activities.updated_at());
        auto& element_user = element_activities.user;
          printf("			id = %u, username = %.20s\n", element_user.id(),element_user.username().c_str());


      }

    }

}


// prepare query 22 (len param = 0)
// Index point on [[43] treeindex : [table = Channel, keys = (-channel:name), cond = (channel:name == Param (name)), value = ptr to 16]] (params = [(Param (name))]): 
//   if (None) result_channel = None
//   
// 

void query_4_plan_2(VarChar<64> param_name_0, Query4Result& qresult) {
  char msg[] = "query 4 plan 2 run time ";
  get_time_start();
    ds_43_key_type v_ds_43_key0_26(param_name_0);
    TREEINDEX_INDEX_FOR_BEGIN(ds_43_9, &v_ds_43_key0_26, ds_43, obj_channel_25)
      auto ptr_obj_channel_27 = (channel_16.get_ptr_by_pos(obj_channel_25.pos));
      if (ptr_obj_channel_27 == nullptr) continue;
      auto& obj_channel_27 = *ptr_obj_channel_27;

      Query4Result::PChannel* ele_result_channel_28 = nullptr;
      if (true) { if ((&qresult) != nullptr) {
        ele_result_channel_28 = (&qresult)->add_channel();
        ele_result_channel_28->set_id(obj_channel_27.channel_id);
        ele_result_channel_28->set_name(obj_channel_27.channel_name.c_str());
        ele_result_channel_28->set_created_at(obj_channel_27.channel_created_at);
        ele_result_channel_28->set_updated_at(obj_channel_27.channel_updated_at);
        ele_result_channel_28->set_user_id(obj_channel_27.channel_user_id);
      }
       }

    TREEINDEX_INDEX_FOR_END


    print_time_diff(msg);
    printf("sz = %u\n", qresult.channel.size());
    size_t cnt_channel = 0;
    for (auto i = qresult.channel.begin(); i != qresult.channel.end(); i++) {
    cnt_channel ++;
    if (cnt_channel > 20) break;
      printf("	id = %u, name = %.20s, created_at = %u, updated_at = %u, user_id = %u\n", (*i).id(),(*i).name().c_str(),(*i).created_at(),(*i).updated_at(),(*i).user_id());

    }

}


// prepare query 23 (len param = 0)
// Scan [16] Basic array: Channel, value = memobj(Channel-id) : 
//   if (None) result_channel = None
//   Scan [30] Basic array: Channel::ActivitiesInChannel(16), value = ptr to 1 : 
//     if (None) result_activities = None
//     Scan [4] Basic array: User, value = memobj(User-id) : 
//       if (None) result_user = None
//       
//     
//   
// 

void query_5_plan_3(Query5Result& qresult) {
  char msg[] = "query 5 plan 3 run time ";
  get_time_start();
    SMALLBASICARRAY_FOR_BEGIN(channel_16_10, channel_16, obj_channel_29)

      Query5Result::PChannel* ele_result_channel_30 = nullptr;
      if (true) { if ((&qresult) != nullptr) {
        ele_result_channel_30 = (&qresult)->add_channel();
        ele_result_channel_30->set_id(obj_channel_29.channel_id);
        ele_result_channel_30->set_name(obj_channel_29.channel_name.c_str());
        ele_result_channel_30->set_created_at(obj_channel_29.channel_created_at);
        ele_result_channel_30->set_updated_at(obj_channel_29.channel_updated_at);
        ele_result_channel_30->set_user_id(obj_channel_29.channel_user_id);
      }
       }
      SMALLBASICARRAY_FOR_BEGIN(activities_30_11, obj_channel_29.activities_30, obj_activities_31)
        auto ptr_obj_activities_32 = (activity_1.get_ptr_by_pos(obj_activities_31.pos));
        if (ptr_obj_activities_32 == nullptr) continue;
        auto& obj_activities_32 = *ptr_obj_activities_32;

        Query5Result::PChannel::PActivitiesInChannel* ele_result_activities_33 = nullptr;
        if (true) { if (ele_result_channel_30 != nullptr) {
          ele_result_activities_33 = ele_result_channel_30->add_activities();
          ele_result_activities_33->set_id(obj_activities_32.activity_id);
          ele_result_activities_33->set_created_at(obj_activities_32.activity_created_at);
          ele_result_activities_33->set_updated_at(obj_activities_32.activity_updated_at);
          ele_result_activities_33->set_action(obj_activities_32.activity_action.c_str());
          ele_result_activities_33->set_content(obj_activities_32.activity_content.c_str());
          ele_result_activities_33->set_channel_id(obj_activities_32.activity_channel_id);
          ele_result_activities_33->set_user_id(obj_activities_32.activity_user_id);
        }
         }
        SMALLBASICARRAY_FOR_BEGIN(user_4_12, user_4, obj_user_34)

          Query5Result::PChannel::PActivitiesInChannel::PUserInActivity* ele_result_user_35 = nullptr;
          if (true) { if (ele_result_activities_33 != nullptr) {
            ele_result_user_35 = ele_result_activities_33->mutable_user();
            ele_result_user_35->set_id(obj_user_34.user_id);
            ele_result_user_35->set_email(obj_user_34.user_email.c_str());
            ele_result_user_35->set_encrypted_password(obj_user_34.user_encrypted_password.c_str());
            ele_result_user_35->set_reset_password_token(obj_user_34.user_reset_password_token.c_str());
            ele_result_user_35->set_reset_password_sent_at(obj_user_34.user_reset_password_sent_at);
            ele_result_user_35->set_remember_created_at(obj_user_34.user_remember_created_at);
            ele_result_user_35->set_first_name(obj_user_34.user_first_name.c_str());
            ele_result_user_35->set_last_name(obj_user_34.user_last_name.c_str());
            ele_result_user_35->set_signin_count(obj_user_34.user_signin_count);
            ele_result_user_35->set_current_sign_in_at(obj_user_34.user_current_sign_in_at);
            ele_result_user_35->set_current_sign_in_ip(obj_user_34.user_current_sign_in_ip.c_str());
            ele_result_user_35->set_last_sign_in_at(obj_user_34.user_last_sign_in_at);
            ele_result_user_35->set_last_sign_in_ip(obj_user_34.user_last_sign_in_ip.c_str());
            ele_result_user_35->set_auth_token(obj_user_34.user_auth_token.c_str());
            ele_result_user_35->set_locale(obj_user_34.user_locale.c_str());
            ele_result_user_35->set_gravatar_hash(obj_user_34.user_gravatar_hash.c_str());
            ele_result_user_35->set_username(obj_user_34.user_username.c_str());
            ele_result_user_35->set_regstatus(obj_user_34.user_regstatus.c_str());
            ele_result_user_35->set_active(obj_user_34.user_active);
            ele_result_user_35->set_is_admin(obj_user_34.user_is_admin);
            ele_result_user_35->set_avatar_url(obj_user_34.user_avatar_url.c_str());
            ele_result_user_35->set_created_at(obj_user_34.user_created_at);
            ele_result_user_35->set_updated_at(obj_user_34.user_updated_at);
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


// prepare query 26 (len param = 0)
// Scan [1] Basic array: Activity, value = memobj(Activity-id) : 
//   if ((activity:content like Param (keyword))) result_activity = None
//   Scan [29] Basic array: Activity::UserInActivity(1), value = memobj(Activity::UserInActivity-id) : 
//     if (None) result_user = None
//     
//   
// 

void query_6_plan_0(LongString param_keyword_0, Query6Result& qresult) {
  char msg[] = "query 6 plan 0 run time ";
  get_time_start();
    BASICARRAY_FOR_BEGIN(activity_1_13, activity_1, obj_activity_36)

      Query6Result::PActivity* ele_result_activity_37 = nullptr;
      if ((obj_activity_36.activity_content.find(param_keyword_0)!=std::string::npos)) { if ((&qresult) != nullptr) {
        ele_result_activity_37 = (&qresult)->add_activity();
        ele_result_activity_37->set_id(obj_activity_36.activity_id);
        ele_result_activity_37->set_created_at(obj_activity_36.activity_created_at);
        ele_result_activity_37->set_updated_at(obj_activity_36.activity_updated_at);
        ele_result_activity_37->set_action(obj_activity_36.activity_action.c_str());
        ele_result_activity_37->set_content(obj_activity_36.activity_content.c_str());
        ele_result_activity_37->set_channel_id(obj_activity_36.activity_channel_id);
        ele_result_activity_37->set_user_id(obj_activity_36.activity_user_id);
        if ((&qresult)->activity_size() > 100) break;
      }
       }
      auto& obj_user_38 = obj_activity_36.user;

        Query6Result::PActivity::PUserInActivity* ele_result_user_39 = nullptr;
        if (true) { if (ele_result_activity_37 != nullptr) {
          ele_result_user_39 = ele_result_activity_37->mutable_user();
          ele_result_user_39->set_id(obj_user_38.user_id);
          ele_result_user_39->set_username(obj_user_38.user_username.c_str());
        }
         }


    BASICARRAY_FOR_END


    print_time_diff(msg);
    printf("sz = %u\n", qresult.activity.size());
    size_t cnt_activity = 0;
    for (auto i = qresult.activity.begin(); i != qresult.activity.end(); i++) {
    cnt_activity ++;
    if (cnt_activity > 20) break;
      printf("	id = %u, created_at = %u, updated_at = %u, action = %.20s, content = %.20s, channel_id = %u, user_id = %u\n", (*i).id(),(*i).created_at(),(*i).updated_at(),(*i).action().c_str(),(*i).content().c_str(),(*i).channel_id(),(*i).user_id());
      auto& element_user = (*i).user;
        printf("		id = %u, username = %.20s\n", element_user.id(),element_user.username().c_str());


    }

}


