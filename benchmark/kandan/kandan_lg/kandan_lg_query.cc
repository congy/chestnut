#include "kandan_lg_query.h"
// prepare query 8 (len param = 0)
// Index range[] on [[6] sorted-array : [table = Activity, keys = (activity:channel-channel:id,-activity:id), cond = (((activity:channel . channel:id) == Param (channel_id)) && ((activity:id >= Value (1)) && (activity:id <= Value (20)))), value = memobj(Activity-id)]] (params = [(Param (channel_id),Value (1)),(Param (channel_id),Value (20))]): 
//   if (None) result_activity = None
//   
// 

void query_0_plan_13(oid_t param_channel_id_0, Query0Result& qresult) {
  char msg[] = "query 0 plan 13 run time ";
  get_time_start();
    ds_6_key_type v_ds_6_key0_2(param_channel_id_0,1);
    ds_6_key_type v_ds_6_key1_3(param_channel_id_0,20);
    SORTEDARRAY_RANGE_FOR_BEGIN(ds_6_1, &v_ds_6_key0_2, &v_ds_6_key1_3, ds_6, obj_activity_1)

      Query8Result::PActivity* ele_result_activity_4 = nullptr;
      if (true) { if ((&qresult) != nullptr) {
        ele_result_activity_4 = (&qresult)->add_activity();
        ele_result_activity_4->set_id(obj_activity_1.activity_id);
        ele_result_activity_4->set_created_at(obj_activity_1.activity_created_at);
        ele_result_activity_4->set_updated_at(obj_activity_1.activity_updated_at);
        ele_result_activity_4->set_action(obj_activity_1.activity_action.c_str());
        ele_result_activity_4->set_content(obj_activity_1.activity_content.c_str());
        ele_result_activity_4->set_channel_id(obj_activity_1.activity_channel_id);
        ele_result_activity_4->set_user_id(obj_activity_1.activity_user_id);
        if ((&qresult)->activity_size() > 1) break;
      }
       }

    SORTEDARRAY_INDEX_FOR_END


    print_time_diff(msg);
    printf("sz = %u\n", qresult.activity.size());
    size_t cnt_activity = 0;
    for (auto i = qresult.activity.begin(); i != qresult.activity.end(); i++) {
    cnt_activity ++;
    if (cnt_activity > 20) break;
      printf("	id = %u, created_at = %u, updated_at = %u, action = %s, content = %s, channel_id = %u, user_id = %u\n", (*i).id(),(*i).created_at(),(*i).updated_at(),(*i).action().c_str(),(*i).content().c_str(),(*i).channel_id(),(*i).user_id());

    }

}

