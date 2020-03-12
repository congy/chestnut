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
//ds[0]: [1] Basic array: Activity, value = memobj(Activity-id,created_at,updated_at,action,content,channel_id,user_id), nested = {
//  [29] Basic array: Activity::UserInActivity(1), value = memobj(Activity::UserInActivity-id,username)
//}
//
//ds[1]: [3] treeindex : [table = Activity, keys = (-activity:id), cond = (activity:id == Param (id)), value = ptr to 1]
//ds[2]: [4] Basic array: User, value = memobj(User-id,email,encrypted_password,reset_password_token,reset_password_sent_at,remember_created_at,first_name,last_name,signin_count,current_sign_in_at,current_sign_in_ip,last_sign_in_at,last_sign_in_ip,auth_token,locale,gravatar_hash,username,regstatus,active,is_admin,avatar_url,created_at,updated_at)
//ds[3]: [12] sorted-array : [table = Attachment, keys = (attachment:channel-channel:id,-attachment:created_at), cond = (((attachment:channel . channel:id) == Param (channel_id)) && ((attachment:created_at >= Value (0)) && (attachment:created_at <= Value (4294967295)))), value = memobj(Attachment-id,file_file_name,file_content_type,file_file_size,message_id,file_updated_at,created_at,updated_at,user_id,channel_id)]
//ds[4]: [16] Basic array: Channel, value = memobj(Channel-id,name,created_at,updated_at,user_id), nested = {
//  [30] Basic array: Channel::ActivitiesInChannel(16), value = ptr to 1
//}
//
//ds[5]: [22] sorted-array : [table = Channel, keys = (-channel:id), cond = (channel:id == Param (channel_id)), value = memobj(Channel-id,name,created_at,updated_at,user_id), nested = {
//  [31] sorted-array : [table = Channel::ActivitiesInChannel(22), keys = (-activity:id), cond = ((activity:id >= Value (1)) && (activity:id <= Value (250000))), value = ptr to 1]
//}
//]
//ds[6]: [43] treeindex : [table = Channel, keys = (-channel:name), cond = (channel:name == Param (name)), value = ptr to 16]
//
extern TreeIndex<oid_t, size_t, 250000> idptr_ds_1;
extern TreeIndex<oid_t, size_t, 500> idptr_ds_16;
struct Activity1 {
public:
  oid_t activity_id;
  date_t activity_created_at;
  date_t activity_updated_at;
  VarChar<16> activity_action;
  LongString activity_content;
  oid_t activity_channel_id;
  oid_t activity_user_id;
    struct UserInActivity29 {
    public:
      oid_t user_id;
      VarChar<32> user_username;
      UserInActivity29(): user_id(0),user_username(0) {}
      UserInActivity29(oid_t v0,VarChar<32> v1): user_id(v0),user_username(v1) {}
      UserInActivity29(const kandan_lg::PUser& p): user_id(p.id()),user_username(p.username()) {}
      inline void clear() { user_id = 0; }
      inline bool operator==(const UserInActivity29& other) const { return user_id==other.user_id; }
      void print() {
        printf("[user:id=%u, username=%s]\n", user_id, user_username.s);
      }
    };
    UserInActivity29 user;
    inline size_t insert_user_by_key(UserInActivity29& v) {
      user = v;
      size_t insertpos = 0;
    }


  Activity1(): activity_id(0),activity_created_at(0),activity_updated_at(0),activity_action(0),activity_content(0),activity_channel_id(0),activity_user_id(0) {}
  Activity1(oid_t v0,date_t v1,date_t v2,VarChar<16> v3,LongString v4,oid_t v5,oid_t v6): activity_id(v0),activity_created_at(v1),activity_updated_at(v2),activity_action(v3),activity_content(v4),activity_channel_id(v5),activity_user_id(v6) {}
  Activity1(const kandan_lg::PActivity& p): activity_id(p.id()),activity_created_at(p.created_at()),activity_updated_at(p.updated_at()),activity_action(p.action()),activity_content(p.content()),activity_channel_id(p.channel_id()),activity_user_id(p.user_id()) {}
  inline void clear() { activity_id = 0; }
  inline bool operator==(const Activity1& other) const { return activity_id==other.activity_id; }
  void print() {
    printf("[activity:id=%u, created_at=%u, updated_at=%u, action=%s, content=%s, channel_id=%u, user_id=%u]\n", activity_id, activity_created_at, activity_updated_at, activity_action.s, activity_content.s.c_str(), activity_channel_id, activity_user_id);
  }
};
extern SmallBasicArray<Activity1, 250000> activity_1;
inline size_t insert_activity_1_by_key(Activity1& v) {
  size_t insertpos = activity_1.insert(v);
  if (!invalid_pos(insertpos)) idptr_ds_1.insert_by_key(v.activity_id, insertpos);
}
struct  ds_3_key_type {
  oid_t activity_id;
  ds_3_key_type(oid_t activity_id_): activity_id(activity_id_) {}
  ds_3_key_type(): activity_id(0) {}
  inline bool operator==(const ds_3_key_type& other) const { return (activity_id == other.activity_id); }
  inline bool operator<(const ds_3_key_type& other) const { return false || (true && activity_id < other.activity_id); }
  inline size_t get_hash() const { return (std::hash<oid_t>()(activity_id) << 0); }
};
extern TreeIndex<ds_3_key_type, ItemPointer, 250000> ds_3;
inline size_t insert_ds_3_by_key(ds_3_key_type& key, ItemPointer& v) {
  size_t insertpos = ds_3.insert_by_key(key, v);
}
struct User4 {
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
  User4(): user_id(0),user_email(0),user_encrypted_password(0),user_reset_password_token(0),user_reset_password_sent_at(0),user_remember_created_at(0),user_first_name(0),user_last_name(0),user_signin_count(0),user_current_sign_in_at(0),user_current_sign_in_ip(0),user_last_sign_in_at(0),user_last_sign_in_ip(0),user_auth_token(0),user_locale(0),user_gravatar_hash(0),user_username(0),user_regstatus(0),user_active(0),user_is_admin(0),user_avatar_url(0),user_created_at(0),user_updated_at(0) {}
  User4(oid_t v0,VarChar<32> v1,VarChar<256> v2,VarChar<256> v3,date_t v4,date_t v5,VarChar<32> v6,VarChar<32> v7,uint32_t v8,date_t v9,VarChar<16> v10,date_t v11,VarChar<16> v12,VarChar<128> v13,VarChar<16> v14,VarChar<256> v15,VarChar<32> v16,VarChar<8> v17,bool v18,bool v19,LongString v20,date_t v21,date_t v22): user_id(v0),user_email(v1),user_encrypted_password(v2),user_reset_password_token(v3),user_reset_password_sent_at(v4),user_remember_created_at(v5),user_first_name(v6),user_last_name(v7),user_signin_count(v8),user_current_sign_in_at(v9),user_current_sign_in_ip(v10),user_last_sign_in_at(v11),user_last_sign_in_ip(v12),user_auth_token(v13),user_locale(v14),user_gravatar_hash(v15),user_username(v16),user_regstatus(v17),user_active(v18),user_is_admin(v19),user_avatar_url(v20),user_created_at(v21),user_updated_at(v22) {}
  User4(const kandan_lg::PUser& p): user_id(p.id()),user_email(p.email()),user_encrypted_password(p.encrypted_password()),user_reset_password_token(p.reset_password_token()),user_reset_password_sent_at(p.reset_password_sent_at()),user_remember_created_at(p.remember_created_at()),user_first_name(p.first_name()),user_last_name(p.last_name()),user_signin_count(p.signin_count()),user_current_sign_in_at(p.current_sign_in_at()),user_current_sign_in_ip(p.current_sign_in_ip()),user_last_sign_in_at(p.last_sign_in_at()),user_last_sign_in_ip(p.last_sign_in_ip()),user_auth_token(p.auth_token()),user_locale(p.locale()),user_gravatar_hash(p.gravatar_hash()),user_username(p.username()),user_regstatus(p.regstatus()),user_active(p.active()),user_is_admin(p.is_admin()),user_avatar_url(p.avatar_url()),user_created_at(p.created_at()),user_updated_at(p.updated_at()) {}
  inline void clear() { user_id = 0; }
  inline bool operator==(const User4& other) const { return user_id==other.user_id; }
  void print() {
    printf("[user:id=%u, email=%s, encrypted_password=%s, reset_password_token=%s, reset_password_sent_at=%u, remember_created_at=%u, first_name=%s, last_name=%s, signin_count=%u, current_sign_in_at=%u, current_sign_in_ip=%s, last_sign_in_at=%u, last_sign_in_ip=%s, auth_token=%s, locale=%s, gravatar_hash=%s, username=%s, regstatus=%s, active=%d, is_admin=%d, avatar_url=%s, created_at=%u, updated_at=%u]\n", user_id, user_email.s, user_encrypted_password.s, user_reset_password_token.s, user_reset_password_sent_at, user_remember_created_at, user_first_name.s, user_last_name.s, user_signin_count, user_current_sign_in_at, user_current_sign_in_ip.s, user_last_sign_in_at, user_last_sign_in_ip.s, user_auth_token.s, user_locale.s, user_gravatar_hash.s, user_username.s, user_regstatus.s, user_active, user_is_admin, user_avatar_url.s.c_str(), user_created_at, user_updated_at);
  }
};
extern SmallBasicArray<User4, 5000> user_4;
inline size_t insert_user_4_by_key(User4& v) {
  size_t insertpos = user_4.insert(v);
}
struct Attachment12 {
public:
  oid_t attachment_id;
  VarChar<128> attachment_file_file_name;
  VarChar<16> attachment_file_content_type;
  uint32_t attachment_file_file_size;
  uint32_t attachment_message_id;
  date_t attachment_file_updated_at;
  date_t attachment_created_at;
  date_t attachment_updated_at;
  oid_t attachment_user_id;
  oid_t attachment_channel_id;
  Attachment12(): attachment_id(0),attachment_file_file_name(0),attachment_file_content_type(0),attachment_file_file_size(0),attachment_message_id(0),attachment_file_updated_at(0),attachment_created_at(0),attachment_updated_at(0),attachment_user_id(0),attachment_channel_id(0) {}
  Attachment12(oid_t v0,VarChar<128> v1,VarChar<16> v2,uint32_t v3,uint32_t v4,date_t v5,date_t v6,date_t v7,oid_t v8,oid_t v9): attachment_id(v0),attachment_file_file_name(v1),attachment_file_content_type(v2),attachment_file_file_size(v3),attachment_message_id(v4),attachment_file_updated_at(v5),attachment_created_at(v6),attachment_updated_at(v7),attachment_user_id(v8),attachment_channel_id(v9) {}
  Attachment12(const kandan_lg::PAttachment& p): attachment_id(p.id()),attachment_file_file_name(p.file_file_name()),attachment_file_content_type(p.file_content_type()),attachment_file_file_size(p.file_file_size()),attachment_message_id(p.message_id()),attachment_file_updated_at(p.file_updated_at()),attachment_created_at(p.created_at()),attachment_updated_at(p.updated_at()),attachment_user_id(p.user_id()),attachment_channel_id(p.channel_id()) {}
  inline void clear() { attachment_id = 0; }
  inline bool operator==(const Attachment12& other) const { return attachment_id==other.attachment_id; }
  void print() {
    printf("[attachment:id=%u, file_file_name=%s, file_content_type=%s, file_file_size=%u, message_id=%u, file_updated_at=%u, created_at=%u, updated_at=%u, user_id=%u, channel_id=%u]\n", attachment_id, attachment_file_file_name.s, attachment_file_content_type.s, attachment_file_file_size, attachment_message_id, attachment_file_updated_at, attachment_created_at, attachment_updated_at, attachment_user_id, attachment_channel_id);
  }
};
struct  ds_12_key_type {
  oid_t channel_id;
  date_t attachment_created_at;
  ds_12_key_type(oid_t channel_id_,date_t attachment_created_at_): channel_id(channel_id_),attachment_created_at(attachment_created_at_) {}
  ds_12_key_type(): channel_id(0),attachment_created_at(0) {}
  inline bool operator==(const ds_12_key_type& other) const { return (channel_id == other.channel_id)&&(attachment_created_at == other.attachment_created_at); }
  inline bool operator<(const ds_12_key_type& other) const { return false || (true && channel_id < other.channel_id) || (true&& channel_id == other.channel_id && attachment_created_at < other.attachment_created_at); }
  inline size_t get_hash() const { return (std::hash<oid_t>()(channel_id) << 0) + (std::hash<date_t>()(attachment_created_at) << 16); }
};
extern SortedArray<ds_12_key_type, Attachment12, 1000> ds_12;
inline size_t insert_ds_12_by_key(ds_12_key_type& key, Attachment12& v) {
  size_t insertpos = ds_12.insert_by_key(key, v);
}
struct Channel16 {
public:
  oid_t channel_id;
  VarChar<64> channel_name;
  date_t channel_created_at;
  date_t channel_updated_at;
  oid_t channel_user_id;
    SmallBasicArray<ItemPointer, 500> activities_30;
    inline size_t insert_activities_30_by_key(ItemPointer& v) {
      size_t insertpos = activities_30.insert(v);
    }


  Channel16(): channel_id(0),channel_name(0),channel_created_at(0),channel_updated_at(0),channel_user_id(0) {}
  Channel16(oid_t v0,VarChar<64> v1,date_t v2,date_t v3,oid_t v4): channel_id(v0),channel_name(v1),channel_created_at(v2),channel_updated_at(v3),channel_user_id(v4) {}
  Channel16(const kandan_lg::PChannel& p): channel_id(p.id()),channel_name(p.name()),channel_created_at(p.created_at()),channel_updated_at(p.updated_at()),channel_user_id(p.user_id()) {}
  inline void clear() { channel_id = 0; }
  inline bool operator==(const Channel16& other) const { return channel_id==other.channel_id; }
  void print() {
    printf("[channel:id=%u, name=%s, created_at=%u, updated_at=%u, user_id=%u]\n", channel_id, channel_name.s, channel_created_at, channel_updated_at, channel_user_id);
  }
};
extern SmallBasicArray<Channel16, 500> channel_16;
inline size_t insert_channel_16_by_key(Channel16& v) {
  size_t insertpos = channel_16.insert(v);
  if (!invalid_pos(insertpos)) idptr_ds_16.insert_by_key(v.channel_id, insertpos);
}
struct Channel22 {
public:
  oid_t channel_id;
  VarChar<64> channel_name;
  date_t channel_created_at;
  date_t channel_updated_at;
  oid_t channel_user_id;
    struct  ds_31_key_type {
      oid_t activity_id;
      ds_31_key_type(oid_t activity_id_): activity_id(activity_id_) {}
      ds_31_key_type(): activity_id(0) {}
      inline bool operator==(const ds_31_key_type& other) const { return (activity_id == other.activity_id); }
      inline bool operator<(const ds_31_key_type& other) const { return false || (true && activity_id < other.activity_id); }
      inline size_t get_hash() const { return (std::hash<oid_t>()(activity_id) << 0); }
    };
    SortedArray<ds_31_key_type, ItemPointer, 500> ds_31;
    inline size_t insert_ds_31_by_key(ds_31_key_type& key, ItemPointer& v) {
      size_t insertpos = ds_31.insert_by_key(key, v);
    }


  Channel22(): channel_id(0),channel_name(0),channel_created_at(0),channel_updated_at(0),channel_user_id(0) {}
  Channel22(oid_t v0,VarChar<64> v1,date_t v2,date_t v3,oid_t v4): channel_id(v0),channel_name(v1),channel_created_at(v2),channel_updated_at(v3),channel_user_id(v4) {}
  Channel22(const kandan_lg::PChannel& p): channel_id(p.id()),channel_name(p.name()),channel_created_at(p.created_at()),channel_updated_at(p.updated_at()),channel_user_id(p.user_id()) {}
  inline void clear() { channel_id = 0; }
  inline bool operator==(const Channel22& other) const { return channel_id==other.channel_id; }
  void print() {
    printf("[channel:id=%u, name=%s, created_at=%u, updated_at=%u, user_id=%u]\n", channel_id, channel_name.s, channel_created_at, channel_updated_at, channel_user_id);
  }
};
struct  ds_22_key_type {
  oid_t channel_id;
  ds_22_key_type(oid_t channel_id_): channel_id(channel_id_) {}
  ds_22_key_type(): channel_id(0) {}
  inline bool operator==(const ds_22_key_type& other) const { return (channel_id == other.channel_id); }
  inline bool operator<(const ds_22_key_type& other) const { return false || (true && channel_id < other.channel_id); }
  inline size_t get_hash() const { return (std::hash<oid_t>()(channel_id) << 0); }
};
extern SortedArray<ds_22_key_type, Channel22, 500> ds_22;
inline size_t insert_ds_22_by_key(ds_22_key_type& key, Channel22& v) {
  size_t insertpos = ds_22.insert_by_key(key, v);
}
struct  ds_43_key_type {
  VarChar<64> channel_name;
  ds_43_key_type(VarChar<64> channel_name_): channel_name(channel_name_) {}
  ds_43_key_type(): channel_name(0) {}
  inline bool operator==(const ds_43_key_type& other) const { return (channel_name == other.channel_name); }
  inline bool operator<(const ds_43_key_type& other) const { return false || (true && channel_name < other.channel_name); }
  inline size_t get_hash() const { return channel_name.get_hash() << 0; }
};
extern TreeIndex<ds_43_key_type, ItemPointer, 500> ds_43;
inline size_t insert_ds_43_by_key(ds_43_key_type& key, ItemPointer& v) {
  size_t insertpos = ds_43.insert_by_key(key, v);
}
void read_data(); 
//ds 1: [1] Basic array: Activity, value = memobj(Activity-id,created_at,updated_at,action,content,channel_id,user_id)
inline void init_ds_1_from_sql(MYSQL* conn, size_t oid) {
  char qs[2000];
  sprintf(qs, "select activity.id,activity.created_at,activity.updated_at,activity.action,activity.content,activity.channel_id,activity.user_id from activities as activity   where activity.id = %u", oid);
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
    Activity1 value(str_to_uint(row[0]),time_to_uint(row[1]),time_to_uint(row[2]),(row[3]),(row[4]),str_to_uint(row[5]),str_to_uint(row[6]));
    insert_activity_1_by_key(value);
    row = mysql_fetch_row(result);
  }
  mysql_free_result(result);
  if(oid%2500==0) printf("----ds 1 finish %u\n", oid/2500);
}
//ds 3: [3] treeindex : [table = Activity, keys = (-activity:id), cond = (activity:id == Param (id)), value = ptr to 1]
inline void init_ds_3_from_sql(MYSQL* conn, size_t oid) {
  oid_t key_0 = 0;
  char qs[2000];
  sprintf(qs, "select activity.id as activity_id from activities as activity   where activity.id = %u group by activity_id order by activity_id", oid);
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
    size_t* pos = idptr_ds_1.find_by_key(str_to_uint(row[0]));
    ItemPointer ipos(INVALID_POS);
    if (pos != nullptr) ipos.pos = *pos;
    key_0 = str_to_uint(row[0]);
    ds_3_key_type key(key_0);
    if (pos != nullptr) insert_ds_3_by_key(key,ipos);
    row = mysql_fetch_row(result);
  }
  mysql_free_result(result);
  if(oid%2500==0) printf("----ds 3 finish %u\n", oid/2500);
}
//ds 4: [4] Basic array: User, value = memobj(User-id,email,encrypted_password,reset_password_token,reset_password_sent_at,remember_created_at,first_name,last_name,signin_count,current_sign_in_at,current_sign_in_ip,last_sign_in_at,last_sign_in_ip,auth_token,locale,gravatar_hash,username,regstatus,active,is_admin,avatar_url,created_at,updated_at)
inline void init_ds_4_from_sql(MYSQL* conn) {
  std::string query_str("select user.id,user.email,user.encrypted_password,user.reset_password_token,user.reset_password_sent_at,user.remember_created_at,user.first_name,user.last_name,user.signin_count,user.current_sign_in_at,user.current_sign_in_ip,user.last_sign_in_at,user.last_sign_in_ip,user.auth_token,user.locale,user.gravatar_hash,user.username,user.regstatus,user.active,user.is_admin,user.avatar_url,user.created_at,user.updated_at from users as user  ");

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
    User4 value(str_to_uint(row[0]),(row[1]),(row[2]),(row[3]),time_to_uint(row[4]),time_to_uint(row[5]),(row[6]),(row[7]),str_to_uint(row[8]),time_to_uint(row[9]),(row[10]),time_to_uint(row[11]),(row[12]),(row[13]),(row[14]),(row[15]),(row[16]),(row[17]),str_to_uint(row[18]),str_to_uint(row[19]),(row[20]),time_to_uint(row[21]),time_to_uint(row[22]));
    insert_user_4_by_key(value);
    row = mysql_fetch_row(result);
  }
  mysql_free_result(result);
}
//ds 12: [12] sorted-array : [table = Attachment, keys = (attachment:channel-channel:id,-attachment:created_at), cond = (((attachment:channel . channel:id) == Param (channel_id)) && ((attachment:created_at >= Value (0)) && (attachment:created_at <= Value (4294967295)))), value = memobj(Attachment-id,file_file_name,file_content_type,file_file_size,message_id,file_updated_at,created_at,updated_at,user_id,channel_id)]
inline void init_ds_12_from_sql(MYSQL* conn) {
  oid_t key_0 = 0;
  date_t key_1 = 0;
  std::string query_str("select attachment.id as attachment_id,attachment.file_file_name as attachment_file_file_name,attachment.file_content_type as attachment_file_content_type,attachment.file_file_size as attachment_file_file_size,attachment.message_id as attachment_message_id,attachment.file_updated_at as attachment_file_updated_at,attachment.created_at as attachment_created_at,attachment.updated_at as attachment_updated_at,attachment.user_id as attachment_user_id,attachment.channel_id as attachment_channel_id from attachments as attachment INNER JOIN channels as attachment_channel ON attachment.channel_id = attachment_channel.id   where attachment.created_at >= 0 and attachment.created_at <= 4294967295 group by attachment_id,attachment_file_file_name,attachment_file_content_type,attachment_file_file_size,attachment_message_id,attachment_file_updated_at,attachment_created_at,attachment_updated_at,attachment_user_id,attachment_channel_id order by attachment_id");

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
    Attachment12 value(str_to_uint(row[0]),(row[1]),(row[2]),str_to_uint(row[3]),str_to_uint(row[4]),time_to_uint(row[5]),time_to_uint(row[6]),time_to_uint(row[7]),str_to_uint(row[8]),str_to_uint(row[9]));
    key_0 = str_to_uint(row[10]);
    key_1 = time_to_uint(row[6]);
    ds_12_key_type key(key_0,key_1);
    insert_ds_12_by_key(key,value);
    row = mysql_fetch_row(result);
  }
  mysql_free_result(result);
}
//ds 16: [16] Basic array: Channel, value = memobj(Channel-id,name,created_at,updated_at,user_id)
inline void init_ds_16_from_sql(MYSQL* conn) {
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
    Channel16 value(str_to_uint(row[0]),(row[1]),time_to_uint(row[2]),time_to_uint(row[3]),str_to_uint(row[4]));
    insert_channel_16_by_key(value);
    row = mysql_fetch_row(result);
  }
  mysql_free_result(result);
}
//ds 22: [22] sorted-array : [table = Channel, keys = (-channel:id), cond = (channel:id == Param (channel_id)), value = memobj(Channel-id,name,created_at,updated_at,user_id)]
inline void init_ds_22_from_sql(MYSQL* conn) {
  oid_t key_0 = 0;
  std::string query_str("select channel.id as channel_id,channel.name as channel_name,channel.created_at as channel_created_at,channel.updated_at as channel_updated_at,channel.user_id as channel_user_id from channels as channel   group by channel_id,channel_name,channel_created_at,channel_updated_at,channel_user_id order by channel_id");

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
    Channel22 value(str_to_uint(row[0]),(row[1]),time_to_uint(row[2]),time_to_uint(row[3]),str_to_uint(row[4]));
    key_0 = str_to_uint(row[0]);
    ds_22_key_type key(key_0);
    insert_ds_22_by_key(key,value);
    row = mysql_fetch_row(result);
  }
  mysql_free_result(result);
}
//ds 43: [43] treeindex : [table = Channel, keys = (-channel:name), cond = (channel:name == Param (name)), value = ptr to 16]
inline void init_ds_43_from_sql(MYSQL* conn) {
  VarChar<64> key_0 = 0;
  std::string query_str("select channel.name as channel_name,channel.id as channel_id from channels as channel   group by channel_name,channel_id order by channel_id");

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
    size_t* pos = idptr_ds_16.find_by_key(str_to_uint(row[1]));
    ItemPointer ipos(INVALID_POS);
    if (pos != nullptr) ipos.pos = *pos;
    key_0 = (row[0]);
    ds_43_key_type key(key_0);
    if (pos != nullptr) insert_ds_43_by_key(key,ipos);
    row = mysql_fetch_row(result);
  }
  mysql_free_result(result);
}
//ds 29: [29] Basic array: Activity::UserInActivity(1), value = memobj(Activity::UserInActivity-id,username)
inline void init_ds_29_from_sql(MYSQL* conn, Activity1* upper_obj) {
  char qs[2000];
  sprintf(qs, "select user.id,user.username from users as user INNER JOIN activities as user_activity ON user.id = user_activity.user_id   where user_activity.id = %u", upper_obj->activity_id);
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
    Activity1::UserInActivity29 value(str_to_uint(row[0]),(row[1]));
    upper_obj->insert_user_by_key(value);
    row = mysql_fetch_row(result);
  }
  mysql_free_result(result);
}
//ds 30: [30] Basic array: Channel::ActivitiesInChannel(16), value = ptr to 1
inline void init_ds_30_from_sql(MYSQL* conn, Channel16* upper_obj) {
  char qs[2000];
  sprintf(qs, "select activity.id from activities as activity INNER JOIN channels as activity_channel ON activity.channel_id = activity_channel.id   where activity_channel.id = %u", upper_obj->channel_id);
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
    size_t* pos = idptr_ds_1.find_by_key(str_to_uint(row[0]));
    ItemPointer ipos(INVALID_POS);
    if (pos != nullptr) ipos.pos = *pos;
    if (pos != nullptr) upper_obj->insert_activities_30_by_key(ipos);
    row = mysql_fetch_row(result);
  }
  mysql_free_result(result);
}
//ds 31: [31] sorted-array : [table = Channel::ActivitiesInChannel(22), keys = (-activity:id), cond = ((activity:id >= Value (1)) && (activity:id <= Value (250000))), value = ptr to 1]
inline void init_ds_31_from_sql(MYSQL* conn, Channel22* upper_obj) {
  oid_t key_0 = 0;
  char qs[2000];
  sprintf(qs, "select activity.id as activity_id from activities as activity INNER JOIN channels as activity_channel ON activity.channel_id = activity_channel.id   where activity_channel.id = %u and activity.id >= 1 and activity.id <= 250000 group by activity_id order by activity_id", upper_obj->channel_id);
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
    size_t* pos = idptr_ds_1.find_by_key(str_to_uint(row[0]));
    ItemPointer ipos(INVALID_POS);
    if (pos != nullptr) ipos.pos = *pos;
    key_0 = str_to_uint(row[0]);
    Channel22::ds_31_key_type key(key_0);
    if (pos != nullptr) upper_obj->insert_ds_31_by_key(key,ipos);
    row = mysql_fetch_row(result);
  }
  mysql_free_result(result);
}
#endif // __KANDAN_LG_H_
