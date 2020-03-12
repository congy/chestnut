#include "kandan_small_query.h"
#include "proto_kandan_small.pb.h"
// prepare query 0 (len param = 0)
// Scan [1] Basic array: User, value = memobj(User-id) : 
//   if ((user:id != Param (uid))) result_user = None
//   
// 

void query_0_plan_0(oid_t param_uid_0, kandan_small::PQuery0Result& qresult) {
  char msg[] = "query 0 plan 0 run time ";
  get_time_start();
    SMALLBASICARRAY_FOR_BEGIN(user_1_1, user_1, obj_user_1)

      kandan_small::PUser* ele_result_user_2 = nullptr;
      if ((obj_user_1.user_id != param_uid_0)) { if ((&qresult) != nullptr) {
        ele_result_user_2 = (&qresult)->add_user();
        ele_result_user_2->set_id(obj_user_1.user_id);
        ele_result_user_2->set_email(obj_user_1.user_email.c_str());
        ele_result_user_2->set_encrypted_password(obj_user_1.user_encrypted_password.c_str());
        ele_result_user_2->set_reset_password_token(obj_user_1.user_reset_password_token.c_str());
        ele_result_user_2->set_reset_password_sent_at(obj_user_1.user_reset_password_sent_at);
        ele_result_user_2->set_remember_created_at(obj_user_1.user_remember_created_at);
        ele_result_user_2->set_first_name(obj_user_1.user_first_name.c_str());
        ele_result_user_2->set_last_name(obj_user_1.user_last_name.c_str());
        ele_result_user_2->set_signin_count(obj_user_1.user_signin_count);
        ele_result_user_2->set_current_sign_in_at(obj_user_1.user_current_sign_in_at);
        ele_result_user_2->set_current_sign_in_ip(obj_user_1.user_current_sign_in_ip.c_str());
        ele_result_user_2->set_last_sign_in_at(obj_user_1.user_last_sign_in_at);
        ele_result_user_2->set_last_sign_in_ip(obj_user_1.user_last_sign_in_ip.c_str());
        ele_result_user_2->set_auth_token(obj_user_1.user_auth_token.c_str());
        ele_result_user_2->set_locale(obj_user_1.user_locale.c_str());
        ele_result_user_2->set_gravatar_hash(obj_user_1.user_gravatar_hash.c_str());
        ele_result_user_2->set_username(obj_user_1.user_username.c_str());
        ele_result_user_2->set_regstatus(obj_user_1.user_regstatus.c_str());
        ele_result_user_2->set_active(obj_user_1.user_active);
        ele_result_user_2->set_is_admin(obj_user_1.user_is_admin);
        ele_result_user_2->set_avatar_url(obj_user_1.user_avatar_url.c_str());
        ele_result_user_2->set_created_at(obj_user_1.user_created_at);
        ele_result_user_2->set_updated_at(obj_user_1.user_updated_at);
      }
       }

    SMALLBASICARRAY_FOR_END


    print_time_diff(msg);

}


