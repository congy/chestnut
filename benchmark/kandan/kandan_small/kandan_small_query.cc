#include "kandan_small_query.h"
#include "proto_kandan_small.pb.h"
// prepare query 9 (len param = 0)
// Index point on [[35] treeindex : [table = Activity, keys = (-activity:id), cond = ((activity:id >= Value (1)) && (activity:id <= Value (5000))), value = ptr to 1]] (params = [(Param (id))]): 
//   if (None) result_activity = None
//   
// 

void query_0_plan_4(oid_t param_id_0, kandan_small::PQuery0Result& qresult) {
  char msg[] = "query 0 plan 4 run time ";
  get_time_start();
    ds_35_key_type v_ds_35_key0_5(param_id_0);
    TREEINDEX_INDEX_FOR_BEGIN(ds_35_4, &v_ds_35_key0_5, ds_35, obj_activity_4)
      auto ptr_obj_activity_6 = (activity_1.get_ptr_by_pos(obj_activity_4.pos));
      if (ptr_obj_activity_6 == nullptr) continue;
      auto& obj_activity_6 = *ptr_obj_activity_6;

      kandan_small::PActivity* ele_result_activity_7 = nullptr;
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

}


// prepare query 10 (len param = 0)
// Scan [4] Basic array: User, value = memobj(User-id) : 
//   if ((user:id != Param (uid))) result_user = None
//   
// 

void query_1_plan_0(oid_t param_uid_0, kandan_small::PQuery1Result& qresult) {
  char msg[] = "query 1 plan 0 run time ";
  get_time_start();
    SMALLBASICARRAY_FOR_BEGIN(user_4_5, user_4, obj_user_8)

      kandan_small::PUser* ele_result_user_9 = nullptr;
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

}


// prepare query 16 (len param = 0)
// Index range[] on [[12] sorted-array : [table = Attachment, keys = (attachment:channel-channel:id,-attachment:created_at), cond = (((attachment:channel . channel:id) == Param (channel_id)) && ((attachment:created_at >= Value (0)) && (attachment:created_at <= Value (4294967295)))), value = memobj(Attachment-id)]] (params = [(Param (channel_id),Value (0)),(Param (channel_id),Value (4294967295))]): 
//   if (None) result_attachment = None
//   
// 

void query_2_plan_2(oid_t param_channel_id_0, kandan_small::PQuery2Result& qresult) {
  char msg[] = "query 2 plan 2 run time ";
  get_time_start();
    ds_12_key_type v_ds_12_key0_11(param_channel_id_0,0);
    ds_12_key_type v_ds_12_key1_12(param_channel_id_0,4294967295);
    SORTEDARRAY_RANGE_FOR_BEGIN(ds_12_6, &v_ds_12_key0_11, &v_ds_12_key1_12, ds_12, obj_attachment_10)

      kandan_small::PAttachment* ele_result_attachment_13 = nullptr;
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

}


// prepare query 19 (len param = 0)
// Index point on [[27] treeindex : [table = Channel, keys = (-channel:id), cond = (channel:id == Param (channel_id)), value = ptr to 16]] (params = [(Param (channel_id))]): 
//   if (None) result_channel = None
//   if (None) count = Value (0)
//   Index range[] on [[28] sorted-array : [table = Channel::ActivitiesInChannel(16), keys = (-activity:id), cond = ((activity:id >= Value (1)) && (activity:id <= Value (5000))), value = ptr to 1]] (params = [(Value (1)),(Value (5000))]): 
//     if (None) count = count()
//     if (None) result_activities = None
//     Scan [29] Basic array: Activity::UserInActivity(1), value = memobj(Activity::UserInActivity-id) : 
//       if (None) result_user = None
//       
//     
//   
// 

void query_3_plan_16(oid_t param_channel_id_0, kandan_small::PQuery3Result& qresult) {
  char msg[] = "query 3 plan 16 run time ";
  get_time_start();
    ds_27_key_type v_ds_27_key0_15(param_channel_id_0);
    TREEINDEX_INDEX_FOR_BEGIN(ds_27_7, &v_ds_27_key0_15, ds_27, obj_channel_14)
      auto ptr_obj_channel_16 = (channel_16.get_ptr_by_pos(obj_channel_14.pos));
      if (ptr_obj_channel_16 == nullptr) continue;
      auto& obj_channel_16 = *ptr_obj_channel_16;

      kandan_small::PChannel* ele_result_channel_17 = nullptr;
      if (true) { if ((&qresult) != nullptr) {
        ele_result_channel_17 = (&qresult)->add_channel();
        ele_result_channel_17->set_id(obj_channel_16.channel_id);
        ele_result_channel_17->set_name(obj_channel_16.channel_name.c_str());
        ele_result_channel_17->set_created_at(obj_channel_16.channel_created_at);
        ele_result_channel_17->set_updated_at(obj_channel_16.channel_updated_at);
        ele_result_channel_17->set_user_id(obj_channel_16.channel_user_id);
      }
       }
      uint32_t e_count_18;
      if (true) { e_count_18 = 0; }
      Channel16::ds_28_key_type v_ds_28_key0_20(1);
      Channel16::ds_28_key_type v_ds_28_key1_21(5000);
      SORTEDARRAY_RANGE_FOR_BEGIN(ds_28_8, &v_ds_28_key0_20, &v_ds_28_key1_21, obj_channel_16.ds_28, obj_activities_19)
        auto ptr_obj_activities_22 = (activity_1.get_ptr_by_pos(obj_activities_19.pos));
        if (ptr_obj_activities_22 == nullptr) continue;
        auto& obj_activities_22 = *ptr_obj_activities_22;

        if (true) { e_count_18++;
         }
        kandan_small::PChannel::PActivitiesInChannel* ele_result_activities_23 = nullptr;
        if (true) { if (ele_result_channel_17 != nullptr) {
          ele_result_activities_23 = ele_result_channel_17->add_activities();
          ele_result_activities_23->set_content(obj_activities_22.activity_content.c_str());
          ele_result_activities_23->set_action(obj_activities_22.activity_action.c_str());
          ele_result_activities_23->set_created_at(obj_activities_22.activity_created_at);
          ele_result_activities_23->set_updated_at(obj_activities_22.activity_updated_at);
          ele_result_activities_23->set_id(obj_activities_22.activity_id);
        }
         }
        auto& obj_user_24 = obj_activities_22.user;

          kandan_small::PChannel::PActivitiesInChannel::PUserInActivity* ele_result_user_25 = nullptr;
          if (true) { if (ele_result_activities_23 != nullptr) {
            ele_result_user_25 = ele_result_activities_23->mutable_user();
            ele_result_user_25->set_id(obj_user_24.user_id);
            ele_result_user_25->set_username(obj_user_24.user_username.c_str());
          }
           }


      SORTEDARRAY_INDEX_FOR_END


    TREEINDEX_INDEX_FOR_END


    print_time_diff(msg);

}


// prepare query 22 (len param = 0)
// Index point on [[43] treeindex : [table = Channel, keys = (-channel:name), cond = (channel:name == Param (name)), value = ptr to 16]] (params = [(Param (name))]): 
//   if (None) result_channel = None
//   
// 

void query_4_plan_2(VarChar<64> param_name_0, kandan_small::PQuery4Result& qresult) {
  char msg[] = "query 4 plan 2 run time ";
  get_time_start();
    ds_43_key_type v_ds_43_key0_27(param_name_0);
    TREEINDEX_INDEX_FOR_BEGIN(ds_43_9, &v_ds_43_key0_27, ds_43, obj_channel_26)
      auto ptr_obj_channel_28 = (channel_16.get_ptr_by_pos(obj_channel_26.pos));
      if (ptr_obj_channel_28 == nullptr) continue;
      auto& obj_channel_28 = *ptr_obj_channel_28;

      kandan_small::PChannel* ele_result_channel_29 = nullptr;
      if (true) { if ((&qresult) != nullptr) {
        ele_result_channel_29 = (&qresult)->add_channel();
        ele_result_channel_29->set_id(obj_channel_28.channel_id);
        ele_result_channel_29->set_name(obj_channel_28.channel_name.c_str());
        ele_result_channel_29->set_created_at(obj_channel_28.channel_created_at);
        ele_result_channel_29->set_updated_at(obj_channel_28.channel_updated_at);
        ele_result_channel_29->set_user_id(obj_channel_28.channel_user_id);
      }
       }

    TREEINDEX_INDEX_FOR_END


    print_time_diff(msg);

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

void query_5_plan_3(kandan_small::PQuery5Result& qresult) {
  char msg[] = "query 5 plan 3 run time ";
  get_time_start();
    SMALLBASICARRAY_FOR_BEGIN(channel_16_10, channel_16, obj_channel_30)

      kandan_small::PChannel* ele_result_channel_31 = nullptr;
      if (true) { if ((&qresult) != nullptr) {
        ele_result_channel_31 = (&qresult)->add_channel();
        ele_result_channel_31->set_id(obj_channel_30.channel_id);
        ele_result_channel_31->set_name(obj_channel_30.channel_name.c_str());
        ele_result_channel_31->set_created_at(obj_channel_30.channel_created_at);
        ele_result_channel_31->set_updated_at(obj_channel_30.channel_updated_at);
        ele_result_channel_31->set_user_id(obj_channel_30.channel_user_id);
      }
       }
      SMALLBASICARRAY_FOR_BEGIN(activities_30_11, obj_channel_30.activities_30, obj_activities_32)
        auto ptr_obj_activities_33 = (activity_1.get_ptr_by_pos(obj_activities_32.pos));
        if (ptr_obj_activities_33 == nullptr) continue;
        auto& obj_activities_33 = *ptr_obj_activities_33;

        kandan_small::PChannel::PActivitiesInChannel* ele_result_activities_34 = nullptr;
        if (true) { if (ele_result_channel_31 != nullptr) {
          ele_result_activities_34 = ele_result_channel_31->add_activities();
          ele_result_activities_34->set_id(obj_activities_33.activity_id);
          ele_result_activities_34->set_created_at(obj_activities_33.activity_created_at);
          ele_result_activities_34->set_updated_at(obj_activities_33.activity_updated_at);
          ele_result_activities_34->set_action(obj_activities_33.activity_action.c_str());
          ele_result_activities_34->set_content(obj_activities_33.activity_content.c_str());
          ele_result_activities_34->set_channel_id(obj_activities_33.activity_channel_id);
          ele_result_activities_34->set_user_id(obj_activities_33.activity_user_id);
        }
         }
        SMALLBASICARRAY_FOR_BEGIN(user_4_12, user_4, obj_user_35)

          kandan_small::PChannel::PActivitiesInChannel::PUserInActivity* ele_result_user_36 = nullptr;
          if (true) { if (ele_result_activities_34 != nullptr) {
            ele_result_user_36 = ele_result_activities_34->mutable_user();
            ele_result_user_36->set_id(obj_user_35.user_id);
            ele_result_user_36->set_email(obj_user_35.user_email.c_str());
            ele_result_user_36->set_encrypted_password(obj_user_35.user_encrypted_password.c_str());
            ele_result_user_36->set_reset_password_token(obj_user_35.user_reset_password_token.c_str());
            ele_result_user_36->set_reset_password_sent_at(obj_user_35.user_reset_password_sent_at);
            ele_result_user_36->set_remember_created_at(obj_user_35.user_remember_created_at);
            ele_result_user_36->set_first_name(obj_user_35.user_first_name.c_str());
            ele_result_user_36->set_last_name(obj_user_35.user_last_name.c_str());
            ele_result_user_36->set_signin_count(obj_user_35.user_signin_count);
            ele_result_user_36->set_current_sign_in_at(obj_user_35.user_current_sign_in_at);
            ele_result_user_36->set_current_sign_in_ip(obj_user_35.user_current_sign_in_ip.c_str());
            ele_result_user_36->set_last_sign_in_at(obj_user_35.user_last_sign_in_at);
            ele_result_user_36->set_last_sign_in_ip(obj_user_35.user_last_sign_in_ip.c_str());
            ele_result_user_36->set_auth_token(obj_user_35.user_auth_token.c_str());
            ele_result_user_36->set_locale(obj_user_35.user_locale.c_str());
            ele_result_user_36->set_gravatar_hash(obj_user_35.user_gravatar_hash.c_str());
            ele_result_user_36->set_username(obj_user_35.user_username.c_str());
            ele_result_user_36->set_regstatus(obj_user_35.user_regstatus.c_str());
            ele_result_user_36->set_active(obj_user_35.user_active);
            ele_result_user_36->set_is_admin(obj_user_35.user_is_admin);
            ele_result_user_36->set_avatar_url(obj_user_35.user_avatar_url.c_str());
            ele_result_user_36->set_created_at(obj_user_35.user_created_at);
            ele_result_user_36->set_updated_at(obj_user_35.user_updated_at);
          }
           }

        SMALLBASICARRAY_FOR_END


      SMALLBASICARRAY_FOR_END


    SMALLBASICARRAY_FOR_END


    print_time_diff(msg);

}


// prepare query 26 (len param = 0)
// Scan [1] Basic array: Activity, value = memobj(Activity-id) : 
//   if ((activity:content like Param (keyword))) result_activity = None
//   Scan [29] Basic array: Activity::UserInActivity(1), value = memobj(Activity::UserInActivity-id) : 
//     if (None) result_user = None
//     
//   
// 

void query_6_plan_0(LongString param_keyword_0, kandan_small::PQuery6Result& qresult) {
  char msg[] = "query 6 plan 0 run time ";
  get_time_start();
    SMALLBASICARRAY_FOR_BEGIN(activity_1_13, activity_1, obj_activity_37)

      kandan_small::PActivity* ele_result_activity_38 = nullptr;
      if ((obj_activity_37.activity_content.find(param_keyword_0)!=std::string::npos)) { if ((&qresult) != nullptr) {
        ele_result_activity_38 = (&qresult)->add_activity();
        ele_result_activity_38->set_id(obj_activity_37.activity_id);
        ele_result_activity_38->set_created_at(obj_activity_37.activity_created_at);
        ele_result_activity_38->set_updated_at(obj_activity_37.activity_updated_at);
        ele_result_activity_38->set_action(obj_activity_37.activity_action.c_str());
        ele_result_activity_38->set_content(obj_activity_37.activity_content.c_str());
        ele_result_activity_38->set_channel_id(obj_activity_37.activity_channel_id);
        ele_result_activity_38->set_user_id(obj_activity_37.activity_user_id);
        if ((&qresult)->activity_size() > 100) break;
      }
       }
      auto& obj_user_39 = obj_activity_37.user;

        kandan_small::PActivity::PUserInActivity* ele_result_user_40 = nullptr;
        if (true) { if (ele_result_activity_38 != nullptr) {
          ele_result_user_40 = ele_result_activity_38->mutable_user();
          ele_result_user_40->set_id(obj_user_39.user_id);
          ele_result_user_40->set_username(obj_user_39.user_username.c_str());
        }
         }


    SMALLBASICARRAY_FOR_END


    print_time_diff(msg);

}


