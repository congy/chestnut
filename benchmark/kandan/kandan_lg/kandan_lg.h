#ifndef __KANDAN_LG_H_
#define __KANDAN_LG_H_

#include <fstream>
#include <vector>
#include <map>
#include <thread>
#include <chrono> 
#include "mysql.h"
#include "util.h"
#include "data_struct.h"
#include "proto_kandan_lg.pb.h"
//ds[0]: [1] Basic array: User, value = memobj(User-id,email,encrypted_password,reset_password_token,reset_password_sent_at,remember_created_at,first_name,last_name,signin_count,current_sign_in_at,current_sign_in_ip,last_sign_in_at,last_sign_in_ip,auth_token,locale,gravatar_hash,username,regstatus,active,is_admin,avatar_url,created_at,updated_at)
//ds[1]: [4] Basic array: Channel, value = memobj(Channel-id,name,created_at,updated_at,user_id), nested = {
//  [5] Basic array: Channel::ActivitiesInChannel(4), value = memobj(Channel::ActivitiesInChannel-id,created_at,updated_at,action,content,channel_id,user_id)
//}
//
//ds[2]: [7] Basic array: Activity, value = memobj(Activity-id,created_at,updated_at,action,channel_id,user_id)
//
struct User1 {
public:
  oid_t user_id;
  VarChar<32> user_email;
  VarChar<256> user_encrypted_password;
  VarChar<256> user_reset_password_token;
  date_t user_reset_password_sent_at;
  date_t user_remember_created_at;
  VarChar<32> user_first_name;
  VarChar<32> user_last_name;
  uint32_t user_signin_count;
  date_t user_current_sign_in_at;
  VarChar<16> user_current_sign_in_ip;
  date_t user_last_sign_in_at;
  VarChar<16> user_last_sign_in_ip;
  VarChar<128> user_auth_token;
  VarChar<16> user_locale;
  VarChar<256> user_gravatar_hash;
  VarChar<32> user_username;
  VarChar<8> user_regstatus;
  bool user_active;
  bool user_is_admin;
  LongString user_avatar_url;
  date_t user_created_at;
  date_t user_updated_at;
  User1(): user_id(0),user_email(0),user_encrypted_password(0),user_reset_password_token(0),user_reset_password_sent_at(0),user_remember_created_at(0),user_first_name(0),user_last_name(0),user_signin_count(0),user_current_sign_in_at(0),user_current_sign_in_ip(0),user_last_sign_in_at(0),user_last_sign_in_ip(0),user_auth_token(0),user_locale(0),user_gravatar_hash(0),user_username(0),user_regstatus(0),user_active(0),user_is_admin(0),user_avatar_url(0),user_created_at(0),user_updated_at(0) {}
  User1(oid_t v0,VarChar<32> v1,VarChar<256> v2,VarChar<256> v3,date_t v4,date_t v5,VarChar<32> v6,VarChar<32> v7,uint32_t v8,date_t v9,VarChar<16> v10,date_t v11,VarChar<16> v12,VarChar<128> v13,VarChar<16> v14,VarChar<256> v15,VarChar<32> v16,VarChar<8> v17,bool v18,bool v19,LongString v20,date_t v21,date_t v22): user_id(v0),user_email(v1),user_encrypted_password(v2),user_reset_password_token(v3),user_reset_password_sent_at(v4),user_remember_created_at(v5),user_first_name(v6),user_last_name(v7),user_signin_count(v8),user_current_sign_in_at(v9),user_current_sign_in_ip(v10),user_last_sign_in_at(v11),user_last_sign_in_ip(v12),user_auth_token(v13),user_locale(v14),user_gravatar_hash(v15),user_username(v16),user_regstatus(v17),user_active(v18),user_is_admin(v19),user_avatar_url(v20),user_created_at(v21),user_updated_at(v22) {}
  User1(const kandan_lg::PUser& p): user_id(p.id()),user_email(p.email()),user_encrypted_password(p.encrypted_password()),user_reset_password_token(p.reset_password_token()),user_reset_password_sent_at(p.reset_password_sent_at()),user_remember_created_at(p.remember_created_at()),user_first_name(p.first_name()),user_last_name(p.last_name()),user_signin_count(p.signin_count()),user_current_sign_in_at(p.current_sign_in_at()),user_current_sign_in_ip(p.current_sign_in_ip()),user_last_sign_in_at(p.last_sign_in_at()),user_last_sign_in_ip(p.last_sign_in_ip()),user_auth_token(p.auth_token()),user_locale(p.locale()),user_gravatar_hash(p.gravatar_hash()),user_username(p.username()),user_regstatus(p.regstatus()),user_active(p.active()),user_is_admin(p.is_admin()),user_avatar_url(p.avatar_url()),user_created_at(p.created_at()),user_updated_at(p.updated_at()) {}
  inline void clear() { user_id = 0; }
  inline bool operator==(const User1& other) const { return user_id==other.user_id; }
  void print() {
    printf("[user:id=%u, email=%s, encrypted_password=%s, reset_password_token=%s, reset_password_sent_at=%u, remember_created_at=%u, first_name=%s, last_name=%s, signin_count=%u, current_sign_in_at=%u, current_sign_in_ip=%s, last_sign_in_at=%u, last_sign_in_ip=%s, auth_token=%s, locale=%s, gravatar_hash=%s, username=%s, regstatus=%s, active=%d, is_admin=%d, avatar_url=%s, created_at=%u, updated_at=%u]\n", user_id, user_email.s, user_encrypted_password.s, user_reset_password_token.s, user_reset_password_sent_at, user_remember_created_at, user_first_name.s, user_last_name.s, user_signin_count, user_current_sign_in_at, user_current_sign_in_ip.s, user_last_sign_in_at, user_last_sign_in_ip.s, user_auth_token.s, user_locale.s, user_gravatar_hash.s, user_username.s, user_regstatus.s, user_active, user_is_admin, user_avatar_url.s.c_str(), user_created_at, user_updated_at);
  }
};
extern SmallBasicArray<User1, 200000> user_1;
inline size_t insert_user_1_by_key(User1& v) {
  size_t insertpos = user_1.insert(v);
}
struct Channel4 {
public:
  oid_t channel_id;
  VarChar<64> channel_name;
  date_t channel_created_at;
  date_t channel_updated_at;
  oid_t channel_user_id;
    struct ActivitiesInChannel5 {
    public:
      oid_t activity_id;
      date_t activity_created_at;
      date_t activity_updated_at;
      VarChar<16> activity_action;
      LongString activity_content;
      oid_t activity_channel_id;
      oid_t activity_user_id;
      ActivitiesInChannel5(): activity_id(0),activity_created_at(0),activity_updated_at(0),activity_action(0),activity_content(0),activity_channel_id(0),activity_user_id(0) {}
      ActivitiesInChannel5(oid_t v0,date_t v1,date_t v2,VarChar<16> v3,LongString v4,oid_t v5,oid_t v6): activity_id(v0),activity_created_at(v1),activity_updated_at(v2),activity_action(v3),activity_content(v4),activity_channel_id(v5),activity_user_id(v6) {}
      ActivitiesInChannel5(const kandan_lg::PActivity& p): activity_id(p.id()),activity_created_at(p.created_at()),activity_updated_at(p.updated_at()),activity_action(p.action()),activity_content(p.content()),activity_channel_id(p.channel_id()),activity_user_id(p.user_id()) {}
      inline void clear() { activity_id = 0; }
      inline bool operator==(const ActivitiesInChannel5& other) const { return activity_id==other.activity_id; }
      void print() {
        printf("[activities:id=%u, created_at=%u, updated_at=%u, action=%s, content=%s, channel_id=%u, user_id=%u]\n", activity_id, activity_created_at, activity_updated_at, activity_action.s, activity_content.s.c_str(), activity_channel_id, activity_user_id);
      }
    };
    SmallBasicArray<ActivitiesInChannel5, 20000> activities_5;
    inline size_t insert_activities_5_by_key(ActivitiesInChannel5& v) {
      size_t insertpos = activities_5.insert(v);
    }


  Channel4(): channel_id(0),channel_name(0),channel_created_at(0),channel_updated_at(0),channel_user_id(0) {}
  Channel4(oid_t v0,VarChar<64> v1,date_t v2,date_t v3,oid_t v4): channel_id(v0),channel_name(v1),channel_created_at(v2),channel_updated_at(v3),channel_user_id(v4) {}
  Channel4(const kandan_lg::PChannel& p): channel_id(p.id()),channel_name(p.name()),channel_created_at(p.created_at()),channel_updated_at(p.updated_at()),channel_user_id(p.user_id()) {}
  inline void clear() { channel_id = 0; }
  inline bool operator==(const Channel4& other) const { return channel_id==other.channel_id; }
  void print() {
    printf("[channel:id=%u, name=%s, created_at=%u, updated_at=%u, user_id=%u]\n", channel_id, channel_name.s, channel_created_at, channel_updated_at, channel_user_id);
  }
};
extern SmallBasicArray<Channel4, 500> channel_4;
inline size_t insert_channel_4_by_key(Channel4& v) {
  size_t insertpos = channel_4.insert(v);
}
struct Activity7 {
public:
  oid_t activity_id;
  date_t activity_created_at;
  date_t activity_updated_at;
  VarChar<16> activity_action;
  oid_t activity_channel_id;
  oid_t activity_user_id;
  Activity7(): activity_id(0),activity_created_at(0),activity_updated_at(0),activity_action(0),activity_channel_id(0),activity_user_id(0) {}
  Activity7(oid_t v0,date_t v1,date_t v2,VarChar<16> v3,oid_t v4,oid_t v5): activity_id(v0),activity_created_at(v1),activity_updated_at(v2),activity_action(v3),activity_channel_id(v4),activity_user_id(v5) {}
  Activity7(const kandan_lg::PActivity& p): activity_id(p.id()),activity_created_at(p.created_at()),activity_updated_at(p.updated_at()),activity_action(p.action()),activity_channel_id(p.channel_id()),activity_user_id(p.user_id()) {}
  inline void clear() { activity_id = 0; }
  inline bool operator==(const Activity7& other) const { return activity_id==other.activity_id; }
  void print() {
    printf("[activity:id=%u, created_at=%u, updated_at=%u, action=%s, channel_id=%u, user_id=%u]\n", activity_id, activity_created_at, activity_updated_at, activity_action.s, activity_channel_id, activity_user_id);
  }
};
extern BasicArray<Activity7, 10000000> activity_7;
inline size_t insert_activity_7_by_key(Activity7& v) {
  size_t insertpos = activity_7.insert(v);
}
void read_data(); 
//ds 1: [1] Basic array: User, value = memobj(User-id,email,encrypted_password,reset_password_token,reset_password_sent_at,remember_created_at,first_name,last_name,signin_count,current_sign_in_at,current_sign_in_ip,last_sign_in_at,last_sign_in_ip,auth_token,locale,gravatar_hash,username,regstatus,active,is_admin,avatar_url,created_at,updated_at)
inline void init_ds_1_from_sql(MYSQL* conn, size_t oid) {
  char qs[2000];
  sprintf(qs, "select user.id,user.email,user.encrypted_password,user.reset_password_token,user.reset_password_sent_at,user.remember_created_at,user.first_name,user.last_name,user.signin_count,user.current_sign_in_at,user.current_sign_in_ip,user.last_sign_in_at,user.last_sign_in_ip,user.auth_token,user.locale,user.gravatar_hash,user.username,user.regstatus,user.active,user.is_admin,user.avatar_url,user.created_at,user.updated_at from users as user   where user.id = %u", oid);
  std::string query_str(qs);

  if (mysql_query(conn, query_str.c_str())) {
    fprintf(stderr, "mysql query failed: %s\n", query_str.c_str());
    exit(1);
  }
  MYSQL_RES *result = mysql_store_result(conn);
  if (result == NULL) exit(0);
  MYSQL_ROW row;
  row = mysql_fetch_row(result);
  size_t insertpos = 0;
  while (row != NULL) {
    User1 value(str_to_uint(row[0]),(row[1]),(row[2]),(row[3]),time_to_uint(row[4]),time_to_uint(row[5]),(row[6]),(row[7]),str_to_uint(row[8]),time_to_uint(row[9]),(row[10]),time_to_uint(row[11]),(row[12]),(row[13]),(row[14]),(row[15]),(row[16]),(row[17]),str_to_uint(row[18]),str_to_uint(row[19]),(row[20]),time_to_uint(row[21]),time_to_uint(row[22]));
    insert_user_1_by_key(value);
    row = mysql_fetch_row(result);
  }
  mysql_free_result(result);
  if(oid%2000==0) printf("----ds 1 finish %u\n", oid/2000);
}
//ds 4: [4] Basic array: Channel, value = memobj(Channel-id,name,created_at,updated_at,user_id)
inline void init_ds_4_from_sql(MYSQL* conn) {
  std::string query_str("select channel.id,channel.name,channel.created_at,channel.updated_at,channel.user_id from channels as channel  ");

  if (mysql_query(conn, query_str.c_str())) {
    fprintf(stderr, "mysql query failed: %s\n", query_str.c_str());
    exit(1);
  }
  MYSQL_RES *result = mysql_store_result(conn);
  if (result == NULL) exit(0);
  MYSQL_ROW row;
  row = mysql_fetch_row(result);
  size_t insertpos = 0;
  while (row != NULL) {
    Channel4 value(str_to_uint(row[0]),(row[1]),time_to_uint(row[2]),time_to_uint(row[3]),str_to_uint(row[4]));
    insert_channel_4_by_key(value);
    row = mysql_fetch_row(result);
  }
  mysql_free_result(result);
}
//ds 7: [7] Basic array: Activity, value = memobj(Activity-id,created_at,updated_at,action,channel_id,user_id)
inline void init_ds_7_from_sql(MYSQL* conn, size_t oid) {
  char qs[2000];
  sprintf(qs, "select activity.id,activity.created_at,activity.updated_at,activity.action,activity.channel_id,activity.user_id from activities as activity   where activity.id = %u", oid);
  std::string query_str(qs);

  if (mysql_query(conn, query_str.c_str())) {
    fprintf(stderr, "mysql query failed: %s\n", query_str.c_str());
    exit(1);
  }
  MYSQL_RES *result = mysql_store_result(conn);
  if (result == NULL) exit(0);
  MYSQL_ROW row;
  row = mysql_fetch_row(result);
  size_t insertpos = 0;
  while (row != NULL) {
    Activity7 value(str_to_uint(row[0]),time_to_uint(row[1]),time_to_uint(row[2]),(row[3]),str_to_uint(row[4]),str_to_uint(row[5]));
    insert_activity_7_by_key(value);
    row = mysql_fetch_row(result);
  }
  mysql_free_result(result);
  if(oid%100000==0) printf("----ds 7 finish %u\n", oid/100000);
}
//ds 5: [5] Basic array: Channel::ActivitiesInChannel(4), value = memobj(Channel::ActivitiesInChannel-id,created_at,updated_at,action,content,channel_id,user_id)
inline void init_ds_5_from_sql(MYSQL* conn, Channel4* upper_obj) {
  char qs[2000];
  sprintf(qs, "select activity.id,activity.created_at,activity.updated_at,activity.action,activity.content,activity.channel_id,activity.user_id from activities as activity INNER JOIN channels as activity_channel ON activity.channel_id = activity_channel.id   where activity_channel.id = %u", upper_obj->channel_id);
  std::string query_str(qs);

  if (mysql_query(conn, query_str.c_str())) {
    fprintf(stderr, "mysql query failed: %s\n", query_str.c_str());
    exit(1);
  }
  MYSQL_RES *result = mysql_store_result(conn);
  if (result == NULL) exit(0);
  MYSQL_ROW row;
  row = mysql_fetch_row(result);
  size_t insertpos = 0;
  while (row != NULL) {
    Channel4::ActivitiesInChannel5 value(str_to_uint(row[0]),time_to_uint(row[1]),time_to_uint(row[2]),(row[3]),(row[4]),str_to_uint(row[5]),str_to_uint(row[6]));
    upper_obj->insert_activities_5_by_key(value);
    row = mysql_fetch_row(result);
  }
  mysql_free_result(result);
}
#endif // __KANDAN_LG_H_
