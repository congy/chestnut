#ifndef __KANDAN_SMALL_H_
#define __KANDAN_SMALL_H_

#include <fstream>
#include <vector>
#include <map>
#include <thread>
#include <chrono> 
#include "mysql.h"
#include "util.h"
#include "data_struct.h"
#include "proto_kandan_small.pb.h"
//ds[0]: [1] Basic array: User, value = memobj(User-id,email,encrypted_password,reset_password_token,reset_password_sent_at,remember_created_at,first_name,last_name,signin_count,current_sign_in_at,current_sign_in_ip,last_sign_in_at,last_sign_in_ip,auth_token,locale,gravatar_hash,username,regstatus,active,is_admin,avatar_url,created_at,updated_at)
//ds[1]: [2] sorted-array : [table = User, keys = (-user:id), cond = (user:id < Param (uid)), value = memobj(User-id,email,encrypted_password,reset_password_token,reset_password_sent_at,remember_created_at,first_name,last_name,signin_count,current_sign_in_at,current_sign_in_ip,last_sign_in_at,last_sign_in_ip,auth_token,locale,gravatar_hash,username,regstatus,active,is_admin,avatar_url,created_at,updated_at)]
//ds[2]: [3] treeindex : [table = User, keys = (-user:id), cond = (user:id < Param (uid)), value = ptr to 1]
//
extern TreeIndex<oid_t, size_t, 100> idptr_ds_1;
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
  User1(const kandan_small::PUser& p): user_id(p.id()),user_email(p.email()),user_encrypted_password(p.encrypted_password()),user_reset_password_token(p.reset_password_token()),user_reset_password_sent_at(p.reset_password_sent_at()),user_remember_created_at(p.remember_created_at()),user_first_name(p.first_name()),user_last_name(p.last_name()),user_signin_count(p.signin_count()),user_current_sign_in_at(p.current_sign_in_at()),user_current_sign_in_ip(p.current_sign_in_ip()),user_last_sign_in_at(p.last_sign_in_at()),user_last_sign_in_ip(p.last_sign_in_ip()),user_auth_token(p.auth_token()),user_locale(p.locale()),user_gravatar_hash(p.gravatar_hash()),user_username(p.username()),user_regstatus(p.regstatus()),user_active(p.active()),user_is_admin(p.is_admin()),user_avatar_url(p.avatar_url()),user_created_at(p.created_at()),user_updated_at(p.updated_at()) {}
  inline void clear() { user_id = 0; }
  inline bool operator==(const User1& other) const { return user_id==other.user_id; }
  void print() {
    printf("[user:id=%u, email=%s, encrypted_password=%s, reset_password_token=%s, reset_password_sent_at=%u, remember_created_at=%u, first_name=%s, last_name=%s, signin_count=%u, current_sign_in_at=%u, current_sign_in_ip=%s, last_sign_in_at=%u, last_sign_in_ip=%s, auth_token=%s, locale=%s, gravatar_hash=%s, username=%s, regstatus=%s, active=%d, is_admin=%d, avatar_url=%s, created_at=%u, updated_at=%u]\n", user_id, user_email.s, user_encrypted_password.s, user_reset_password_token.s, user_reset_password_sent_at, user_remember_created_at, user_first_name.s, user_last_name.s, user_signin_count, user_current_sign_in_at, user_current_sign_in_ip.s, user_last_sign_in_at, user_last_sign_in_ip.s, user_auth_token.s, user_locale.s, user_gravatar_hash.s, user_username.s, user_regstatus.s, user_active, user_is_admin, user_avatar_url.s.c_str(), user_created_at, user_updated_at);
  }
};
extern SmallBasicArray<User1, 100> user_1;
inline size_t insert_user_1_by_key(User1& v) {
  size_t insertpos = user_1.insert(v);
  if (!invalid_pos(insertpos)) idptr_ds_1.insert_by_key(v.user_id, insertpos);
}
struct User2 {
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
  User2(): user_id(0),user_email(0),user_encrypted_password(0),user_reset_password_token(0),user_reset_password_sent_at(0),user_remember_created_at(0),user_first_name(0),user_last_name(0),user_signin_count(0),user_current_sign_in_at(0),user_current_sign_in_ip(0),user_last_sign_in_at(0),user_last_sign_in_ip(0),user_auth_token(0),user_locale(0),user_gravatar_hash(0),user_username(0),user_regstatus(0),user_active(0),user_is_admin(0),user_avatar_url(0),user_created_at(0),user_updated_at(0) {}
  User2(oid_t v0,VarChar<32> v1,VarChar<256> v2,VarChar<256> v3,date_t v4,date_t v5,VarChar<32> v6,VarChar<32> v7,uint32_t v8,date_t v9,VarChar<16> v10,date_t v11,VarChar<16> v12,VarChar<128> v13,VarChar<16> v14,VarChar<256> v15,VarChar<32> v16,VarChar<8> v17,bool v18,bool v19,LongString v20,date_t v21,date_t v22): user_id(v0),user_email(v1),user_encrypted_password(v2),user_reset_password_token(v3),user_reset_password_sent_at(v4),user_remember_created_at(v5),user_first_name(v6),user_last_name(v7),user_signin_count(v8),user_current_sign_in_at(v9),user_current_sign_in_ip(v10),user_last_sign_in_at(v11),user_last_sign_in_ip(v12),user_auth_token(v13),user_locale(v14),user_gravatar_hash(v15),user_username(v16),user_regstatus(v17),user_active(v18),user_is_admin(v19),user_avatar_url(v20),user_created_at(v21),user_updated_at(v22) {}
  User2(const kandan_small::PUser& p): user_id(p.id()),user_email(p.email()),user_encrypted_password(p.encrypted_password()),user_reset_password_token(p.reset_password_token()),user_reset_password_sent_at(p.reset_password_sent_at()),user_remember_created_at(p.remember_created_at()),user_first_name(p.first_name()),user_last_name(p.last_name()),user_signin_count(p.signin_count()),user_current_sign_in_at(p.current_sign_in_at()),user_current_sign_in_ip(p.current_sign_in_ip()),user_last_sign_in_at(p.last_sign_in_at()),user_last_sign_in_ip(p.last_sign_in_ip()),user_auth_token(p.auth_token()),user_locale(p.locale()),user_gravatar_hash(p.gravatar_hash()),user_username(p.username()),user_regstatus(p.regstatus()),user_active(p.active()),user_is_admin(p.is_admin()),user_avatar_url(p.avatar_url()),user_created_at(p.created_at()),user_updated_at(p.updated_at()) {}
  inline void clear() { user_id = 0; }
  inline bool operator==(const User2& other) const { return user_id==other.user_id; }
  void print() {
    printf("[user:id=%u, email=%s, encrypted_password=%s, reset_password_token=%s, reset_password_sent_at=%u, remember_created_at=%u, first_name=%s, last_name=%s, signin_count=%u, current_sign_in_at=%u, current_sign_in_ip=%s, last_sign_in_at=%u, last_sign_in_ip=%s, auth_token=%s, locale=%s, gravatar_hash=%s, username=%s, regstatus=%s, active=%d, is_admin=%d, avatar_url=%s, created_at=%u, updated_at=%u]\n", user_id, user_email.s, user_encrypted_password.s, user_reset_password_token.s, user_reset_password_sent_at, user_remember_created_at, user_first_name.s, user_last_name.s, user_signin_count, user_current_sign_in_at, user_current_sign_in_ip.s, user_last_sign_in_at, user_last_sign_in_ip.s, user_auth_token.s, user_locale.s, user_gravatar_hash.s, user_username.s, user_regstatus.s, user_active, user_is_admin, user_avatar_url.s.c_str(), user_created_at, user_updated_at);
  }
};
struct  ds_2_key_type {
  oid_t user_id;
  ds_2_key_type(oid_t user_id_): user_id(user_id_) {}
  ds_2_key_type(): user_id(0) {}
  inline bool operator==(const ds_2_key_type& other) const { return (user_id == other.user_id); }
  inline bool operator<(const ds_2_key_type& other) const { return false || (true && user_id < other.user_id); }
  inline size_t get_hash() const { return (std::hash<oid_t>()(user_id) << 0); }
};
extern SortedArray<ds_2_key_type, User2, 100> ds_2;
inline size_t insert_ds_2_by_key(ds_2_key_type& key, User2& v) {
  size_t insertpos = ds_2.insert_by_key(key, v);
}
struct  ds_3_key_type {
  oid_t user_id;
  ds_3_key_type(oid_t user_id_): user_id(user_id_) {}
  ds_3_key_type(): user_id(0) {}
  inline bool operator==(const ds_3_key_type& other) const { return (user_id == other.user_id); }
  inline bool operator<(const ds_3_key_type& other) const { return false || (true && user_id < other.user_id); }
  inline size_t get_hash() const { return (std::hash<oid_t>()(user_id) << 0); }
};
extern TreeIndex<ds_3_key_type, ItemPointer, 100> ds_3;
inline size_t insert_ds_3_by_key(ds_3_key_type& key, ItemPointer& v) {
  size_t insertpos = ds_3.insert_by_key(key, v);
}
void read_data(); 
//ds 1: [1] Basic array: User, value = memobj(User-id,email,encrypted_password,reset_password_token,reset_password_sent_at,remember_created_at,first_name,last_name,signin_count,current_sign_in_at,current_sign_in_ip,last_sign_in_at,last_sign_in_ip,auth_token,locale,gravatar_hash,username,regstatus,active,is_admin,avatar_url,created_at,updated_at)
inline void init_ds_1_from_sql(MYSQL* conn) {
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
    User1 value(str_to_uint(row[0]),(row[1]),(row[2]),(row[3]),time_to_uint(row[4]),time_to_uint(row[5]),(row[6]),(row[7]),str_to_uint(row[8]),time_to_uint(row[9]),(row[10]),time_to_uint(row[11]),(row[12]),(row[13]),(row[14]),(row[15]),(row[16]),(row[17]),str_to_uint(row[18]),str_to_uint(row[19]),(row[20]),time_to_uint(row[21]),time_to_uint(row[22]));
    insert_user_1_by_key(value);
    row = mysql_fetch_row(result);
  }
  mysql_free_result(result);
}
//ds 2: [2] sorted-array : [table = User, keys = (-user:id), cond = (user:id < Param (uid)), value = memobj(User-id,email,encrypted_password,reset_password_token,reset_password_sent_at,remember_created_at,first_name,last_name,signin_count,current_sign_in_at,current_sign_in_ip,last_sign_in_at,last_sign_in_ip,auth_token,locale,gravatar_hash,username,regstatus,active,is_admin,avatar_url,created_at,updated_at)]
inline void init_ds_2_from_sql(MYSQL* conn) {
  oid_t key_0 = 0;
  std::string query_str("select user.id as user_id,user.email as user_email,user.encrypted_password as user_encrypted_password,user.reset_password_token as user_reset_password_token,user.reset_password_sent_at as user_reset_password_sent_at,user.remember_created_at as user_remember_created_at,user.first_name as user_first_name,user.last_name as user_last_name,user.signin_count as user_signin_count,user.current_sign_in_at as user_current_sign_in_at,user.current_sign_in_ip as user_current_sign_in_ip,user.last_sign_in_at as user_last_sign_in_at,user.last_sign_in_ip as user_last_sign_in_ip,user.auth_token as user_auth_token,user.locale as user_locale,user.gravatar_hash as user_gravatar_hash,user.username as user_username,user.regstatus as user_regstatus,user.active as user_active,user.is_admin as user_is_admin,user.avatar_url as user_avatar_url,user.created_at as user_created_at,user.updated_at as user_updated_at from users as user   group by user_id,user_email,user_encrypted_password,user_reset_password_token,user_reset_password_sent_at,user_remember_created_at,user_first_name,user_last_name,user_signin_count,user_current_sign_in_at,user_current_sign_in_ip,user_last_sign_in_at,user_last_sign_in_ip,user_auth_token,user_locale,user_gravatar_hash,user_username,user_regstatus,user_active,user_is_admin,user_avatar_url,user_created_at,user_updated_at order by user_id");

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
    User2 value(str_to_uint(row[0]),(row[1]),(row[2]),(row[3]),time_to_uint(row[4]),time_to_uint(row[5]),(row[6]),(row[7]),str_to_uint(row[8]),time_to_uint(row[9]),(row[10]),time_to_uint(row[11]),(row[12]),(row[13]),(row[14]),(row[15]),(row[16]),(row[17]),str_to_uint(row[18]),str_to_uint(row[19]),(row[20]),time_to_uint(row[21]),time_to_uint(row[22]));
    key_0 = str_to_uint(row[0]);
    ds_2_key_type key(key_0);
    insert_ds_2_by_key(key,value);
    row = mysql_fetch_row(result);
  }
  mysql_free_result(result);
}
//ds 3: [3] treeindex : [table = User, keys = (-user:id), cond = (user:id < Param (uid)), value = ptr to 1]
inline void init_ds_3_from_sql(MYSQL* conn) {
  oid_t key_0 = 0;
  std::string query_str("select user.id as user_id from users as user   group by user_id order by user_id");

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
}
#endif // __KANDAN_SMALL_H_
