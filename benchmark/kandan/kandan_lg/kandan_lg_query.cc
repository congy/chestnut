#include "kandan_lg_query.h"
// prepare query 4 (len param = 0)
// Index range[] on [[17] treeindex : [table = Activity, keys = (activity:channel-channel:id,-activity:id), cond = (((activity:channel . channel:id) == Param (channel_id)) && (activity:id <= Param (oldest))), value = ptr to 5]] (params = [(Param (channel_id),Value (1)),(Param (channel_id),Param (oldest))]): 
//   if (None) result_activity = None
//   Scan [7] Basic array: Activity::UserInActivity(5), value = memobj(Activity::UserInActivity-id) : 
//     if (None) result_user = None
//     
//   
// 

void query_0_plan_7(oid_t param_channel_id_0, oid_t param_oldest_1, Query0Result& qresult) {
  char msg[] = "query 0 plan 7 run time ";
  get_time_start();
    ds_17_key_type v_ds_17_key0_4(param_channel_id_0,1);
    ds_17_key_type v_ds_17_key1_5(param_channel_id_0,param_oldest_1);
    TREEINDEX_RANGE_FOR_BEGIN(ds_17_3, &v_ds_17_key0_4, &v_ds_17_key1_5, ds_17, obj_activity_3)
      auto ptr_obj_activity_6 = (activity_5.get_ptr_by_pos(obj_activity_3.pos));
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
        if ((&qresult)->activity_size() > 40) break;
      }
       }
      auto& obj_user_8 = obj_activity_6.user;

        Query0Result::PActivity::PUserInActivity* ele_result_user_9 = nullptr;
        if (true) { if (ele_result_activity_7 != nullptr) {
          ele_result_user_9 = ele_result_activity_7->mutable_user();
          ele_result_user_9->set_id(obj_user_8.user_id);
          ele_result_user_9->set_username(obj_user_8.user_username.c_str());
        }
         }


    TREEINDEX_INDEX_FOR_END


    print_time_diff(msg);
    printf("sz = %u\n", qresult.activity.size());
    size_t cnt_activity = 0;
    for (auto i = qresult.activity.begin(); i != qresult.activity.end(); i++) {
    cnt_activity ++;
    if (cnt_activity > 20) break;
      printf("	id = %u, created_at = %u, updated_at = %u, action = %s, content = %s, channel_id = %u, user_id = %u\n", (*i).id(),(*i).created_at(),(*i).updated_at(),(*i).action().c_str(),(*i).content().c_str(),(*i).channel_id(),(*i).user_id());
      auto& element_user = (*i).user;
        printf("		id = %u, username = %s\n", element_user.id(),element_user.username().c_str());


    }

}


// prepare query 6 (len param = 0)
// Index range[] on [[10] treeindex : [table = Activity, keys = (activity:channel-channel:id,-activity:id), cond = (((activity:channel . channel:id) == Param (channel_id)) && ((activity:id >= Value (1)) && (activity:id <= Value (10000000)))), value = ptr to 5]] (params = [(Param (channel_id),Value (1)),(Param (channel_id),Value (10000000))]): 
//   if (None) result_activity = None
//   Scan [7] Basic array: Activity::UserInActivity(5), value = memobj(Activity::UserInActivity-id) : 
//     if (None) result_user = None
//     
//   
// 

void query_1_plan_3(oid_t param_channel_id_0, Query1Result& qresult) {
  char msg[] = "query 1 plan 3 run time ";
  get_time_start();
    ds_10_key_type v_ds_10_key0_11(param_channel_id_0,1);
    ds_10_key_type v_ds_10_key1_12(param_channel_id_0,10000000);
    TREEINDEX_RANGE_FOR_BEGIN(ds_10_4, &v_ds_10_key0_11, &v_ds_10_key1_12, ds_10, obj_activity_10)
      auto ptr_obj_activity_13 = (activity_5.get_ptr_by_pos(obj_activity_10.pos));
      if (ptr_obj_activity_13 == nullptr) continue;
      auto& obj_activity_13 = *ptr_obj_activity_13;

      Query1Result::PActivity* ele_result_activity_14 = nullptr;
      if (true) { if ((&qresult) != nullptr) {
        ele_result_activity_14 = (&qresult)->add_activity();
        ele_result_activity_14->set_id(obj_activity_13.activity_id);
        ele_result_activity_14->set_created_at(obj_activity_13.activity_created_at);
        ele_result_activity_14->set_updated_at(obj_activity_13.activity_updated_at);
        ele_result_activity_14->set_action(obj_activity_13.activity_action.c_str());
        ele_result_activity_14->set_content(obj_activity_13.activity_content.c_str());
        ele_result_activity_14->set_channel_id(obj_activity_13.activity_channel_id);
        ele_result_activity_14->set_user_id(obj_activity_13.activity_user_id);
        if ((&qresult)->activity_size() > 40) break;
      }
       }
      auto& obj_user_15 = obj_activity_13.user;

        Query1Result::PActivity::PUserInActivity* ele_result_user_16 = nullptr;
        if (true) { if (ele_result_activity_14 != nullptr) {
          ele_result_user_16 = ele_result_activity_14->mutable_user();
          ele_result_user_16->set_id(obj_user_15.user_id);
          ele_result_user_16->set_username(obj_user_15.user_username.c_str());
        }
         }


    TREEINDEX_INDEX_FOR_END


    print_time_diff(msg);
    printf("sz = %u\n", qresult.activity.size());
    size_t cnt_activity = 0;
    for (auto i = qresult.activity.begin(); i != qresult.activity.end(); i++) {
    cnt_activity ++;
    if (cnt_activity > 20) break;
      printf("	id = %u, created_at = %u, updated_at = %u, action = %s, content = %s, channel_id = %u, user_id = %u\n", (*i).id(),(*i).created_at(),(*i).updated_at(),(*i).action().c_str(),(*i).content().c_str(),(*i).channel_id(),(*i).user_id());
      auto& element_user = (*i).user;
        printf("		id = %u, username = %s\n", element_user.id(),element_user.username().c_str());


    }

}


// prepare query 8 (len param = 0)
// Index range[] on [[10] treeindex : [table = Activity, keys = (activity:channel-channel:id,-activity:id), cond = (((activity:channel . channel:id) == Param (channel_id)) && ((activity:id >= Value (1)) && (activity:id <= Value (10000000)))), value = ptr to 5]] (params = [(Param (channel_id),Value (1)),(Param (channel_id),Value (10000000))]): 
//   if (None) result_activity = None
//   
// 

void query_2_plan_3(oid_t param_channel_id_0, Query2Result& qresult) {
  char msg[] = "query 2 plan 3 run time ";
  get_time_start();
    ds_10_key_type v_ds_10_key0_18(param_channel_id_0,1);
    ds_10_key_type v_ds_10_key1_19(param_channel_id_0,10000000);
    TREEINDEX_RANGE_FOR_BEGIN(ds_10_5, &v_ds_10_key0_18, &v_ds_10_key1_19, ds_10, obj_activity_17)
      auto ptr_obj_activity_20 = (activity_5.get_ptr_by_pos(obj_activity_17.pos));
      if (ptr_obj_activity_20 == nullptr) continue;
      auto& obj_activity_20 = *ptr_obj_activity_20;

      Query2Result::PActivity* ele_result_activity_21 = nullptr;
      if (true) { if ((&qresult) != nullptr) {
        ele_result_activity_21 = (&qresult)->add_activity();
        ele_result_activity_21->set_id(obj_activity_20.activity_id);
        ele_result_activity_21->set_created_at(obj_activity_20.activity_created_at);
        ele_result_activity_21->set_updated_at(obj_activity_20.activity_updated_at);
        ele_result_activity_21->set_action(obj_activity_20.activity_action.c_str());
        ele_result_activity_21->set_content(obj_activity_20.activity_content.c_str());
        ele_result_activity_21->set_channel_id(obj_activity_20.activity_channel_id);
        ele_result_activity_21->set_user_id(obj_activity_20.activity_user_id);
        if ((&qresult)->activity_size() > 1) break;
      }
       }

    TREEINDEX_INDEX_FOR_END


    print_time_diff(msg);
    printf("sz = %u\n", qresult.activity.size());
    size_t cnt_activity = 0;
    for (auto i = qresult.activity.begin(); i != qresult.activity.end(); i++) {
    cnt_activity ++;
    if (cnt_activity > 20) break;
      printf("	id = %u, created_at = %u, updated_at = %u, action = %s, content = %s, channel_id = %u, user_id = %u\n", (*i).id(),(*i).created_at(),(*i).updated_at(),(*i).action().c_str(),(*i).content().c_str(),(*i).channel_id(),(*i).user_id());

    }

}


// prepare query 9 (len param = 0)
// Index point on [[25] treeindex : [table = Activity, keys = (-activity:id), cond = (activity:id == Param (id)), value = ptr to 5]] (params = [(Param (id))]): 
//   if (None) result_activity = None
//   
// 

void query_3_plan_2(oid_t param_id_0, Query3Result& qresult) {
  char msg[] = "query 3 plan 2 run time ";
  get_time_start();
    ds_25_key_type v_ds_25_key0_23(param_id_0);
    TREEINDEX_INDEX_FOR_BEGIN(ds_25_6, &v_ds_25_key0_23, ds_25, obj_activity_22)
      auto ptr_obj_activity_24 = (activity_5.get_ptr_by_pos(obj_activity_22.pos));
      if (ptr_obj_activity_24 == nullptr) continue;
      auto& obj_activity_24 = *ptr_obj_activity_24;

      Query3Result::PActivity* ele_result_activity_25 = nullptr;
      if (true) { if ((&qresult) != nullptr) {
        ele_result_activity_25 = (&qresult)->add_activity();
        ele_result_activity_25->set_id(obj_activity_24.activity_id);
        ele_result_activity_25->set_created_at(obj_activity_24.activity_created_at);
        ele_result_activity_25->set_updated_at(obj_activity_24.activity_updated_at);
        ele_result_activity_25->set_action(obj_activity_24.activity_action.c_str());
        ele_result_activity_25->set_content(obj_activity_24.activity_content.c_str());
        ele_result_activity_25->set_channel_id(obj_activity_24.activity_channel_id);
        ele_result_activity_25->set_user_id(obj_activity_24.activity_user_id);
      }
       }

    TREEINDEX_INDEX_FOR_END


    print_time_diff(msg);
    printf("sz = %u\n", qresult.activity.size());
    size_t cnt_activity = 0;
    for (auto i = qresult.activity.begin(); i != qresult.activity.end(); i++) {
    cnt_activity ++;
    if (cnt_activity > 20) break;
      printf("	id = %u, created_at = %u, updated_at = %u, action = %s, content = %s, channel_id = %u, user_id = %u\n", (*i).id(),(*i).created_at(),(*i).updated_at(),(*i).action().c_str(),(*i).content().c_str(),(*i).channel_id(),(*i).user_id());

    }

}


// prepare query 16 (len param = 0)
// Index range[] on [[31] sorted-array : [table = Attachment, keys = (attachment:channel-channel:id,-attachment:created_at), cond = (((attachment:channel . channel:id) == Param (channel_id)) && ((attachment:created_at >= Value (0)) && (attachment:created_at <= Value (4294967295)))), value = memobj(Attachment-id)]] (params = [(Param (channel_id),Value (0)),(Param (channel_id),Value (4294967295))]): 
//   if (None) result_attachment = None
//   
// 

void query_4_plan_13(oid_t param_channel_id_0, Query4Result& qresult) {
  char msg[] = "query 4 plan 13 run time ";
  get_time_start();
    ds_31_key_type v_ds_31_key0_27(param_channel_id_0,0);
    ds_31_key_type v_ds_31_key1_28(param_channel_id_0,4294967295);
    SORTEDARRAY_RANGE_FOR_BEGIN(ds_31_7, &v_ds_31_key0_27, &v_ds_31_key1_28, ds_31, obj_attachment_26)

      Query4Result::PAttachment* ele_result_attachment_29 = nullptr;
      if (true) { if ((&qresult) != nullptr) {
        ele_result_attachment_29 = (&qresult)->add_attachment();
        ele_result_attachment_29->set_id(obj_attachment_26.attachment_id);
        ele_result_attachment_29->set_file_file_name(obj_attachment_26.attachment_file_file_name.c_str());
        ele_result_attachment_29->set_file_content_type(obj_attachment_26.attachment_file_content_type.c_str());
        ele_result_attachment_29->set_file_file_size(obj_attachment_26.attachment_file_file_size);
        ele_result_attachment_29->set_message_id(obj_attachment_26.attachment_message_id);
        ele_result_attachment_29->set_file_updated_at(obj_attachment_26.attachment_file_updated_at);
        ele_result_attachment_29->set_created_at(obj_attachment_26.attachment_created_at);
        ele_result_attachment_29->set_updated_at(obj_attachment_26.attachment_updated_at);
        ele_result_attachment_29->set_user_id(obj_attachment_26.attachment_user_id);
        ele_result_attachment_29->set_channel_id(obj_attachment_26.attachment_channel_id);
      }
       }

    SORTEDARRAY_INDEX_FOR_END


    print_time_diff(msg);
    printf("sz = %u\n", qresult.attachment.size());
    size_t cnt_attachment = 0;
    for (auto i = qresult.attachment.begin(); i != qresult.attachment.end(); i++) {
    cnt_attachment ++;
    if (cnt_attachment > 20) break;
      printf("	id = %u, file_file_name = %s, file_content_type = %s, file_file_size = %u, message_id = %u, file_updated_at = %u, created_at = %u, updated_at = %u, user_id = %u, channel_id = %u\n", (*i).id(),(*i).file_file_name().c_str(),(*i).file_content_type().c_str(),(*i).file_file_size(),(*i).message_id(),(*i).file_updated_at(),(*i).created_at(),(*i).updated_at(),(*i).user_id(),(*i).channel_id());

    }

}


// prepare query 19 (len param = 0)
// Index point on [[40] sorted-array : [table = Channel, keys = (-channel:id), cond = (channel:id == Param (channel_id)), value = memobj(Channel-id)]] (params = [(Param (channel_id))]): 
//   if (None) result_channel = None
//   if (None) count = Value (0)
//   Index range[] on [[48] sorted-array : [table = Channel::ActivitiesInChannel(40), keys = (-activity:id), cond = ((activity:id >= Value (1)) && (activity:id <= Value (10000000))), value = ptr to 5]] (params = [(Value (1)),(Value (10000000))]): 
//     if (None) count = count()
//     if (None) result_activities = None
//     Scan [7] Basic array: Activity::UserInActivity(5), value = memobj(Activity::UserInActivity-id) : 
//       if (None) result_user = None
//       
//     
//   
// 

void query_5_plan_14(oid_t param_channel_id_0, Query5Result& qresult) {
  char msg[] = "query 5 plan 14 run time ";
  get_time_start();
    ds_40_key_type v_ds_40_key0_31(param_channel_id_0);
    SORTEDARRAY_INDEX_FOR_BEGIN(ds_40_8, &v_ds_40_key0_31, ds_40, obj_channel_30)

      Query5Result::PChannel* ele_result_channel_32 = nullptr;
      if (true) { if ((&qresult) != nullptr) {
        ele_result_channel_32 = (&qresult)->add_channel();
        ele_result_channel_32->set_id(obj_channel_30.channel_id);
        ele_result_channel_32->set_name(obj_channel_30.channel_name.c_str());
        ele_result_channel_32->set_created_at(obj_channel_30.channel_created_at);
        ele_result_channel_32->set_updated_at(obj_channel_30.channel_updated_at);
        ele_result_channel_32->set_user_id(obj_channel_30.channel_user_id);
      }
       }
      uint32_t e_count_33;
      if (true) { e_count_33 = 0; }
      Channel40::ds_48_key_type v_ds_48_key0_35(1);
      Channel40::ds_48_key_type v_ds_48_key1_36(10000000);
      SORTEDARRAY_RANGE_FOR_BEGIN(ds_48_9, &v_ds_48_key0_35, &v_ds_48_key1_36, obj_channel_30.ds_48, obj_activities_34)
        auto ptr_obj_activities_37 = (activity_5.get_ptr_by_pos(obj_activities_34.pos));
        if (ptr_obj_activities_37 == nullptr) continue;
        auto& obj_activities_37 = *ptr_obj_activities_37;

        if (true) { e_count_33++;
         }
        Query5Result::PChannel::PActivitiesInChannel* ele_result_activities_38 = nullptr;
        if (true) { if (ele_result_channel_32 != nullptr) {
          ele_result_activities_38 = ele_result_channel_32->add_activities();
          ele_result_activities_38->set_content(obj_activities_37.activity_content.c_str());
          ele_result_activities_38->set_action(obj_activities_37.activity_action.c_str());
          ele_result_activities_38->set_created_at(obj_activities_37.activity_created_at);
          ele_result_activities_38->set_updated_at(obj_activities_37.activity_updated_at);
          ele_result_activities_38->set_id(obj_activities_37.activity_id);
        }
         }
        auto& obj_user_39 = obj_activities_37.user;

          Query5Result::PChannel::PActivitiesInChannel::PUserInActivity* ele_result_user_40 = nullptr;
          if (true) { if (ele_result_activities_38 != nullptr) {
            ele_result_user_40 = ele_result_activities_38->mutable_user();
            ele_result_user_40->set_id(obj_user_39.user_id);
            ele_result_user_40->set_username(obj_user_39.user_username.c_str());
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
      printf("	id = %u, name = %s, created_at = %u, updated_at = %u, user_id = %u, count = %u\n", (*i).id(),(*i).name().c_str(),(*i).created_at(),(*i).updated_at(),(*i).user_id(),(*i).count());
      printf("sz = %u\n", (*i).activities_size());
      for (size_t i_activities = 0; i_activities != (*i).activities_size(); i_activities++) {
          auto& element_activities = (*i).activities[i_activities];
        printf("		content = %s, action = %s, created_at = %u, updated_at = %u\n", element_activities.content().c_str(),element_activities.action().c_str(),element_activities.created_at(),element_activities.updated_at());
        auto& element_user = element_activities.user;
          printf("			id = %u, username = %s\n", element_user.id(),element_user.username().c_str());


      }

    }

}


// prepare query 22 (len param = 0)
// Index point on [[56] sorted-array : [table = Channel, keys = (-channel:name), cond = (channel:name == Param (name)), value = memobj(Channel-id)]] (params = [(Param (name))]): 
//   if (None) result_channel = None
//   
// 

void query_6_plan_1(VarChar<64> param_name_0, Query6Result& qresult) {
  char msg[] = "query 6 plan 1 run time ";
  get_time_start();
    ds_56_key_type v_ds_56_key0_42(param_name_0);
    SORTEDARRAY_INDEX_FOR_BEGIN(ds_56_10, &v_ds_56_key0_42, ds_56, obj_channel_41)

      Query6Result::PChannel* ele_result_channel_43 = nullptr;
      if (true) { if ((&qresult) != nullptr) {
        ele_result_channel_43 = (&qresult)->add_channel();
        ele_result_channel_43->set_id(obj_channel_41.channel_id);
        ele_result_channel_43->set_name(obj_channel_41.channel_name.c_str());
        ele_result_channel_43->set_created_at(obj_channel_41.channel_created_at);
        ele_result_channel_43->set_updated_at(obj_channel_41.channel_updated_at);
        ele_result_channel_43->set_user_id(obj_channel_41.channel_user_id);
      }
       }

    SORTEDARRAY_INDEX_FOR_END


    print_time_diff(msg);
    printf("sz = %u\n", qresult.channel.size());
    size_t cnt_channel = 0;
    for (auto i = qresult.channel.begin(); i != qresult.channel.end(); i++) {
    cnt_channel ++;
    if (cnt_channel > 20) break;
      printf("	id = %u, name = %s, created_at = %u, updated_at = %u, user_id = %u\n", (*i).id(),(*i).name().c_str(),(*i).created_at(),(*i).updated_at(),(*i).user_id());

    }

}


// prepare query 26 (len param = 0)
// Scan [5] Basic array: Activity, value = memobj(Activity-id) : 
//   if ((activity:content like Param (keyword))) result_activity = None
//   Scan [7] Basic array: Activity::UserInActivity(5), value = memobj(Activity::UserInActivity-id) : 
//     if (None) result_user = None
//     
//   
// 

void query_7_plan_0(LongString param_keyword_0, Query7Result& qresult) {
  char msg[] = "query 7 plan 0 run time ";
  get_time_start();
    BASICARRAY_FOR_BEGIN(activity_5_11, activity_5, obj_activity_44)

      Query7Result::PActivity* ele_result_activity_45 = nullptr;
      if ((obj_activity_44.activity_content.find(param_keyword_0)!=std::string::npos)) { if ((&qresult) != nullptr) {
        ele_result_activity_45 = (&qresult)->add_activity();
        ele_result_activity_45->set_id(obj_activity_44.activity_id);
        ele_result_activity_45->set_created_at(obj_activity_44.activity_created_at);
        ele_result_activity_45->set_updated_at(obj_activity_44.activity_updated_at);
        ele_result_activity_45->set_action(obj_activity_44.activity_action.c_str());
        ele_result_activity_45->set_content(obj_activity_44.activity_content.c_str());
        ele_result_activity_45->set_channel_id(obj_activity_44.activity_channel_id);
        ele_result_activity_45->set_user_id(obj_activity_44.activity_user_id);
        if ((&qresult)->activity_size() > 100) break;
      }
       }
      auto& obj_user_46 = obj_activity_44.user;

        Query7Result::PActivity::PUserInActivity* ele_result_user_47 = nullptr;
        if (true) { if (ele_result_activity_45 != nullptr) {
          ele_result_user_47 = ele_result_activity_45->mutable_user();
          ele_result_user_47->set_id(obj_user_46.user_id);
          ele_result_user_47->set_username(obj_user_46.user_username.c_str());
        }
         }


    BASICARRAY_FOR_END


    print_time_diff(msg);
    printf("sz = %u\n", qresult.activity.size());
    size_t cnt_activity = 0;
    for (auto i = qresult.activity.begin(); i != qresult.activity.end(); i++) {
    cnt_activity ++;
    if (cnt_activity > 20) break;
      printf("	id = %u, created_at = %u, updated_at = %u, action = %s, content = %s, channel_id = %u, user_id = %u\n", (*i).id(),(*i).created_at(),(*i).updated_at(),(*i).action().c_str(),(*i).content().c_str(),(*i).channel_id(),(*i).user_id());
      auto& element_user = (*i).user;
        printf("		id = %u, username = %s\n", element_user.id(),element_user.username().c_str());


    }

}


