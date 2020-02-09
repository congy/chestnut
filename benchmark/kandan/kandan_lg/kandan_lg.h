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
//ds[0]: [5] Basic array: Activity, value = memobj(Activity-id,created_at,updated_at,action,content,channel_id,user_id), nested = {
//  [7] Basic array: Activity::UserInActivity(5), value = memobj(Activity::UserInActivity-id,username)
//}
//
//ds[1]: [10] treeindex : [table = Activity, keys = (activity:channel-channel:id,-activity:id), cond = (((activity:channel . channel:id) == Param (channel_id)) && ((activity:id >= Value (1)) && (activity:id <= Value (10000000)))), value = ptr to 5]
//ds[2]: [17] treeindex : [table = Activity, keys = (activity:channel-channel:id,-activity:id), cond = (((activity:channel . channel:id) == Param (channel_id)) && (activity:id <= Param (oldest))), value = ptr to 5]
//ds[3]: [25] treeindex : [table = Activity, keys = (-activity:id), cond = (activity:id == Param (id)), value = ptr to 5]
//ds[4]: [31] sorted-array : [table = Attachment, keys = (attachment:channel-channel:id,-attachment:created_at), cond = (((attachment:channel . channel:id) == Param (channel_id)) && ((attachment:created_at >= Value (0)) && (attachment:created_at <= Value (4294967295)))), value = memobj(Attachment-id,file_file_name,file_content_type,file_file_size,message_id,file_updated_at,created_at,updated_at,user_id,channel_id)]
//ds[5]: [40] sorted-array : [table = Channel, keys = (-channel:id), cond = (channel:id == Param (channel_id)), value = memobj(Channel-id,name,created_at,updated_at,user_id), nested = {
//  [48] sorted-array : [table = Channel::ActivitiesInChannel(40), keys = (-activity:id), cond = ((activity:id >= Value (1)) && (activity:id <= Value (10000000))), value = ptr to 5]
//}
//]
//ds[6]: [56] sorted-array : [table = Channel, keys = (-channel:name), cond = (channel:name == Param (name)), value = memobj(Channel-id,name,created_at,updated_at,user_id)]
//
extern TreeIndex<oid_t, size_t, 10000000> idptr_ds_5;
struct Activity5 {
public:
  oid_t activity_id;
  date_t activity_created_at;
  date_t activity_updated_at;
  VarChar<16> activity_action;
  LongString activity_content;
  oid_t activity_channel_id;
  oid_t activity_user_id;
    struct UserInActivity7 {
    public:
      oid_t user_id;
      VarChar<32> user_username;
      UserInActivity7(): user_id(0),user_username(0) {}
      UserInActivity7(oid_t v0,VarChar<32> v1): user_id(v0),user_username(v1) {}
      UserInActivity7(const kandan_lg::PUser& p): user_id(p.id()),user_username(p.username()) {}
      inline void clear() { user_id = 0; }
      inline bool operator==(const UserInActivity7& other) const { return user_id==other.user_id; }
      void print() {
        printf("[user:id=%u, username=%s]\n", user_id, user_username.s);
      }
    };
    UserInActivity7 user;
    inline size_t insert_user_by_key(UserInActivity7& v) {
      user = v;
      size_t insertpos = 0;
    }


  Activity5(): activity_id(0),activity_created_at(0),activity_updated_at(0),activity_action(0),activity_content(0),activity_channel_id(0),activity_user_id(0) {}
  Activity5(oid_t v0,date_t v1,date_t v2,VarChar<16> v3,LongString v4,oid_t v5,oid_t v6): activity_id(v0),activity_created_at(v1),activity_updated_at(v2),activity_action(v3),activity_content(v4),activity_channel_id(v5),activity_user_id(v6) {}
  Activity5(const kandan_lg::PActivity& p): activity_id(p.id()),activity_created_at(p.created_at()),activity_updated_at(p.updated_at()),activity_action(p.action()),activity_content(p.content()),activity_channel_id(p.channel_id()),activity_user_id(p.user_id()) {}
  inline void clear() { activity_id = 0; }
  inline bool operator==(const Activity5& other) const { return activity_id==other.activity_id; }
  void print() {
    printf("[activity:id=%u, created_at=%u, updated_at=%u, action=%s, content=%s, channel_id=%u, user_id=%u]\n", activity_id, activity_created_at, activity_updated_at, activity_action.s, activity_content.s.c_str(), activity_channel_id, activity_user_id);
  }
};
extern BasicArray<Activity5, 10000000> activity_5;
inline size_t insert_activity_5_by_key(Activity5& v) {
  size_t insertpos = activity_5.insert(v);
  if (!invalid_pos(insertpos)) idptr_ds_5.insert_by_key(v.activity_id, insertpos);
}
struct  ds_10_key_type {
  oid_t channel_id;
  oid_t activity_id;
  ds_10_key_type(oid_t channel_id_,oid_t activity_id_): channel_id(channel_id_),activity_id(activity_id_) {}
  ds_10_key_type(): channel_id(0),activity_id(0) {}
  inline bool operator==(const ds_10_key_type& other) const { return (channel_id == other.channel_id)&&(activity_id == other.activity_id); }
  inline bool operator<(const ds_10_key_type& other) const { return false || (true && channel_id < other.channel_id) || (true&& channel_id == other.channel_id && activity_id < other.activity_id); }
  inline size_t get_hash() const { return (std::hash<oid_t>()(channel_id) << 0) + (std::hash<oid_t>()(activity_id) << 16); }
};
extern TreeIndex<ds_10_key_type, ItemPointer, 10000000> ds_10;
inline size_t insert_ds_10_by_key(ds_10_key_type& key, ItemPointer& v) {
  size_t insertpos = ds_10.insert_by_key(key, v);
}
struct  ds_17_key_type {
  oid_t channel_id;
  oid_t activity_id;
  ds_17_key_type(oid_t channel_id_,oid_t activity_id_): channel_id(channel_id_),activity_id(activity_id_) {}
  ds_17_key_type(): channel_id(0),activity_id(0) {}
  inline bool operator==(const ds_17_key_type& other) const { return (channel_id == other.channel_id)&&(activity_id == other.activity_id); }
  inline bool operator<(const ds_17_key_type& other) const { return false || (true && channel_id < other.channel_id) || (true&& channel_id == other.channel_id && activity_id < other.activity_id); }
  inline size_t get_hash() const { return (std::hash<oid_t>()(channel_id) << 0) + (std::hash<oid_t>()(activity_id) << 16); }
};
extern TreeIndex<ds_17_key_type, ItemPointer, 10000000> ds_17;
inline size_t insert_ds_17_by_key(ds_17_key_type& key, ItemPointer& v) {
  size_t insertpos = ds_17.insert_by_key(key, v);
}
struct  ds_25_key_type {
  oid_t activity_id;
  ds_25_key_type(oid_t activity_id_): activity_id(activity_id_) {}
  ds_25_key_type(): activity_id(0) {}
  inline bool operator==(const ds_25_key_type& other) const { return (activity_id == other.activity_id); }
  inline bool operator<(const ds_25_key_type& other) const { return false || (true && activity_id < other.activity_id); }
  inline size_t get_hash() const { return (std::hash<oid_t>()(activity_id) << 0); }
};
extern TreeIndex<ds_25_key_type, ItemPointer, 10000000> ds_25;
inline size_t insert_ds_25_by_key(ds_25_key_type& key, ItemPointer& v) {
  size_t insertpos = ds_25.insert_by_key(key, v);
}
struct Attachment31 {
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
  Attachment31(): attachment_id(0),attachment_file_file_name(0),attachment_file_content_type(0),attachment_file_file_size(0),attachment_message_id(0),attachment_file_updated_at(0),attachment_created_at(0),attachment_updated_at(0),attachment_user_id(0),attachment_channel_id(0) {}
  Attachment31(oid_t v0,VarChar<128> v1,VarChar<16> v2,uint32_t v3,uint32_t v4,date_t v5,date_t v6,date_t v7,oid_t v8,oid_t v9): attachment_id(v0),attachment_file_file_name(v1),attachment_file_content_type(v2),attachment_file_file_size(v3),attachment_message_id(v4),attachment_file_updated_at(v5),attachment_created_at(v6),attachment_updated_at(v7),attachment_user_id(v8),attachment_channel_id(v9) {}
  Attachment31(const kandan_lg::PAttachment& p): attachment_id(p.id()),attachment_file_file_name(p.file_file_name()),attachment_file_content_type(p.file_content_type()),attachment_file_file_size(p.file_file_size()),attachment_message_id(p.message_id()),attachment_file_updated_at(p.file_updated_at()),attachment_created_at(p.created_at()),attachment_updated_at(p.updated_at()),attachment_user_id(p.user_id()),attachment_channel_id(p.channel_id()) {}
  inline void clear() { attachment_id = 0; }
  inline bool operator==(const Attachment31& other) const { return attachment_id==other.attachment_id; }
  void print() {
    printf("[attachment:id=%u, file_file_name=%s, file_content_type=%s, file_file_size=%u, message_id=%u, file_updated_at=%u, created_at=%u, updated_at=%u, user_id=%u, channel_id=%u]\n", attachment_id, attachment_file_file_name.s, attachment_file_content_type.s, attachment_file_file_size, attachment_message_id, attachment_file_updated_at, attachment_created_at, attachment_updated_at, attachment_user_id, attachment_channel_id);
  }
};
struct  ds_31_key_type {
  oid_t channel_id;
  date_t attachment_created_at;
  ds_31_key_type(oid_t channel_id_,date_t attachment_created_at_): channel_id(channel_id_),attachment_created_at(attachment_created_at_) {}
  ds_31_key_type(): channel_id(0),attachment_created_at(0) {}
  inline bool operator==(const ds_31_key_type& other) const { return (channel_id == other.channel_id)&&(attachment_created_at == other.attachment_created_at); }
  inline bool operator<(const ds_31_key_type& other) const { return false || (true && channel_id < other.channel_id) || (true&& channel_id == other.channel_id && attachment_created_at < other.attachment_created_at); }
  inline size_t get_hash() const { return (std::hash<oid_t>()(channel_id) << 0) + (std::hash<date_t>()(attachment_created_at) << 16); }
};
extern SortedArray<ds_31_key_type, Attachment31, 40000> ds_31;
inline size_t insert_ds_31_by_key(ds_31_key_type& key, Attachment31& v) {
  size_t insertpos = ds_31.insert_by_key(key, v);
}
struct Channel40 {
public:
  oid_t channel_id;
  VarChar<64> channel_name;
  date_t channel_created_at;
  date_t channel_updated_at;
  oid_t channel_user_id;
    struct  ds_48_key_type {
      oid_t activity_id;
      ds_48_key_type(oid_t activity_id_): activity_id(activity_id_) {}
      ds_48_key_type(): activity_id(0) {}
      inline bool operator==(const ds_48_key_type& other) const { return (activity_id == other.activity_id); }
      inline bool operator<(const ds_48_key_type& other) const { return false || (true && activity_id < other.activity_id); }
      inline size_t get_hash() const { return (std::hash<oid_t>()(activity_id) << 0); }
    };
    SortedArray<ds_48_key_type, ItemPointer, 20000> ds_48;
    inline size_t insert_ds_48_by_key(ds_48_key_type& key, ItemPointer& v) {
      size_t insertpos = ds_48.insert_by_key(key, v);
    }


  Channel40(): channel_id(0),channel_name(0),channel_created_at(0),channel_updated_at(0),channel_user_id(0) {}
  Channel40(oid_t v0,VarChar<64> v1,date_t v2,date_t v3,oid_t v4): channel_id(v0),channel_name(v1),channel_created_at(v2),channel_updated_at(v3),channel_user_id(v4) {}
  Channel40(const kandan_lg::PChannel& p): channel_id(p.id()),channel_name(p.name()),channel_created_at(p.created_at()),channel_updated_at(p.updated_at()),channel_user_id(p.user_id()) {}
  inline void clear() { channel_id = 0; }
  inline bool operator==(const Channel40& other) const { return channel_id==other.channel_id; }
  void print() {
    printf("[channel:id=%u, name=%s, created_at=%u, updated_at=%u, user_id=%u]\n", channel_id, channel_name.s, channel_created_at, channel_updated_at, channel_user_id);
  }
};
struct  ds_40_key_type {
  oid_t channel_id;
  ds_40_key_type(oid_t channel_id_): channel_id(channel_id_) {}
  ds_40_key_type(): channel_id(0) {}
  inline bool operator==(const ds_40_key_type& other) const { return (channel_id == other.channel_id); }
  inline bool operator<(const ds_40_key_type& other) const { return false || (true && channel_id < other.channel_id); }
  inline size_t get_hash() const { return (std::hash<oid_t>()(channel_id) << 0); }
};
extern SortedArray<ds_40_key_type, Channel40, 500> ds_40;
inline size_t insert_ds_40_by_key(ds_40_key_type& key, Channel40& v) {
  size_t insertpos = ds_40.insert_by_key(key, v);
}
struct Channel56 {
public:
  oid_t channel_id;
  VarChar<64> channel_name;
  date_t channel_created_at;
  date_t channel_updated_at;
  oid_t channel_user_id;
  Channel56(): channel_id(0),channel_name(0),channel_created_at(0),channel_updated_at(0),channel_user_id(0) {}
  Channel56(oid_t v0,VarChar<64> v1,date_t v2,date_t v3,oid_t v4): channel_id(v0),channel_name(v1),channel_created_at(v2),channel_updated_at(v3),channel_user_id(v4) {}
  Channel56(const kandan_lg::PChannel& p): channel_id(p.id()),channel_name(p.name()),channel_created_at(p.created_at()),channel_updated_at(p.updated_at()),channel_user_id(p.user_id()) {}
  inline void clear() { channel_id = 0; }
  inline bool operator==(const Channel56& other) const { return channel_id==other.channel_id; }
  void print() {
    printf("[channel:id=%u, name=%s, created_at=%u, updated_at=%u, user_id=%u]\n", channel_id, channel_name.s, channel_created_at, channel_updated_at, channel_user_id);
  }
};
struct  ds_56_key_type {
  VarChar<64> channel_name;
  ds_56_key_type(VarChar<64> channel_name_): channel_name(channel_name_) {}
  ds_56_key_type(): channel_name(0) {}
  inline bool operator==(const ds_56_key_type& other) const { return (channel_name == other.channel_name); }
  inline bool operator<(const ds_56_key_type& other) const { return false || (true && channel_name < other.channel_name); }
  inline size_t get_hash() const { return channel_name.get_hash() << 0; }
};
extern SortedArray<ds_56_key_type, Channel56, 500> ds_56;
inline size_t insert_ds_56_by_key(ds_56_key_type& key, Channel56& v) {
  size_t insertpos = ds_56.insert_by_key(key, v);
}
void read_data(); 
//ds 5: [5] Basic array: Activity, value = memobj(Activity-id,created_at,updated_at,action,content,channel_id,user_id)
inline void init_ds_5_from_sql(MYSQL* conn, size_t oid) {
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
    Activity5 value(str_to_uint(row[0]),time_to_uint(row[1]),time_to_uint(row[2]),(row[3]),(row[4]),str_to_uint(row[5]),str_to_uint(row[6]));
    insert_activity_5_by_key(value);
    row = mysql_fetch_row(result);
  }
  mysql_free_result(result);
  if(oid%100000==0) printf("----ds 5 finish %u\n", oid/100000);
}
//ds 10: [10] treeindex : [table = Activity, keys = (activity:channel-channel:id,-activity:id), cond = (((activity:channel . channel:id) == Param (channel_id)) && ((activity:id >= Value (1)) && (activity:id <= Value (10000000)))), value = ptr to 5]
inline void init_ds_10_from_sql(MYSQL* conn, size_t oid) {
  oid_t key_0 = 0;
  oid_t key_1 = 0;
  char qs[2000];
  sprintf(qs, "select activity_channel.id as activity_channel_id,activity.id as activity_id from activities as activity INNER JOIN channels as activity_channel ON activity.channel_id = activity_channel.id   where activity.id = %u and activity.id >= 1 and activity.id <= 10000000 group by activity_channel_id,activity_id order by activity_channel_id,activity_id", oid);
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
    size_t* pos = idptr_ds_5.find_by_key(str_to_uint(row[1]));
    ItemPointer ipos(INVALID_POS);
    if (pos != nullptr) ipos.pos = *pos;
    key_0 = str_to_uint(row[0]);
    key_1 = str_to_uint(row[1]);
    ds_10_key_type key(key_0,key_1);
    if (pos != nullptr) insert_ds_10_by_key(key,ipos);
    row = mysql_fetch_row(result);
  }
  mysql_free_result(result);
  if(oid%100000==0) printf("----ds 10 finish %u\n", oid/100000);
}
//ds 17: [17] treeindex : [table = Activity, keys = (activity:channel-channel:id,-activity:id), cond = (((activity:channel . channel:id) == Param (channel_id)) && (activity:id <= Param (oldest))), value = ptr to 5]
inline void init_ds_17_from_sql(MYSQL* conn, size_t oid) {
  oid_t key_0 = 0;
  oid_t key_1 = 0;
  char qs[2000];
  sprintf(qs, "select activity_channel.id as activity_channel_id,activity.id as activity_id from activities as activity INNER JOIN channels as activity_channel ON activity.channel_id = activity_channel.id   where activity.id = %u group by activity_channel_id,activity_id order by activity_channel_id,activity_id", oid);
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
    size_t* pos = idptr_ds_5.find_by_key(str_to_uint(row[1]));
    ItemPointer ipos(INVALID_POS);
    if (pos != nullptr) ipos.pos = *pos;
    key_0 = str_to_uint(row[0]);
    key_1 = str_to_uint(row[1]);
    ds_17_key_type key(key_0,key_1);
    if (pos != nullptr) insert_ds_17_by_key(key,ipos);
    row = mysql_fetch_row(result);
  }
  mysql_free_result(result);
  if(oid%100000==0) printf("----ds 17 finish %u\n", oid/100000);
}
//ds 25: [25] treeindex : [table = Activity, keys = (-activity:id), cond = (activity:id == Param (id)), value = ptr to 5]
inline void init_ds_25_from_sql(MYSQL* conn, size_t oid) {
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
    size_t* pos = idptr_ds_5.find_by_key(str_to_uint(row[0]));
    ItemPointer ipos(INVALID_POS);
    if (pos != nullptr) ipos.pos = *pos;
    key_0 = str_to_uint(row[0]);
    ds_25_key_type key(key_0);
    if (pos != nullptr) insert_ds_25_by_key(key,ipos);
    row = mysql_fetch_row(result);
  }
  mysql_free_result(result);
  if(oid%100000==0) printf("----ds 25 finish %u\n", oid/100000);
}
//ds 31: [31] sorted-array : [table = Attachment, keys = (attachment:channel-channel:id,-attachment:created_at), cond = (((attachment:channel . channel:id) == Param (channel_id)) && ((attachment:created_at >= Value (0)) && (attachment:created_at <= Value (4294967295)))), value = memobj(Attachment-id,file_file_name,file_content_type,file_file_size,message_id,file_updated_at,created_at,updated_at,user_id,channel_id)]
inline void init_ds_31_from_sql(MYSQL* conn) {
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
    Attachment31 value(str_to_uint(row[0]),(row[1]),(row[2]),str_to_uint(row[3]),str_to_uint(row[4]),time_to_uint(row[5]),time_to_uint(row[6]),time_to_uint(row[7]),str_to_uint(row[8]),str_to_uint(row[9]));
    key_0 = str_to_uint(row[10]);
    key_1 = time_to_uint(row[6]);
    ds_31_key_type key(key_0,key_1);
    insert_ds_31_by_key(key,value);
    row = mysql_fetch_row(result);
  }
  mysql_free_result(result);
}
//ds 40: [40] sorted-array : [table = Channel, keys = (-channel:id), cond = (channel:id == Param (channel_id)), value = memobj(Channel-id,name,created_at,updated_at,user_id)]
inline void init_ds_40_from_sql(MYSQL* conn) {
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
    Channel40 value(str_to_uint(row[0]),(row[1]),time_to_uint(row[2]),time_to_uint(row[3]),str_to_uint(row[4]));
    key_0 = str_to_uint(row[0]);
    ds_40_key_type key(key_0);
    insert_ds_40_by_key(key,value);
    row = mysql_fetch_row(result);
  }
  mysql_free_result(result);
}
//ds 56: [56] sorted-array : [table = Channel, keys = (-channel:name), cond = (channel:name == Param (name)), value = memobj(Channel-id,name,created_at,updated_at,user_id)]
inline void init_ds_56_from_sql(MYSQL* conn) {
  VarChar<64> key_0 = 0;
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
    Channel56 value(str_to_uint(row[0]),(row[1]),time_to_uint(row[2]),time_to_uint(row[3]),str_to_uint(row[4]));
    key_0 = (row[1]);
    ds_56_key_type key(key_0);
    insert_ds_56_by_key(key,value);
    row = mysql_fetch_row(result);
  }
  mysql_free_result(result);
}
//ds 7: [7] Basic array: Activity::UserInActivity(5), value = memobj(Activity::UserInActivity-id,username)
inline void init_ds_7_from_sql(MYSQL* conn, Activity5* upper_obj) {
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
    Activity5::UserInActivity7 value(str_to_uint(row[0]),(row[1]));
    upper_obj->insert_user_by_key(value);
    row = mysql_fetch_row(result);
  }
  mysql_free_result(result);
}
//ds 48: [48] sorted-array : [table = Channel::ActivitiesInChannel(40), keys = (-activity:id), cond = ((activity:id >= Value (1)) && (activity:id <= Value (10000000))), value = ptr to 5]
inline void init_ds_48_from_sql(MYSQL* conn, Channel40* upper_obj) {
  oid_t key_0 = 0;
  char qs[2000];
  sprintf(qs, "select activity.id as activity_id from activities as activity INNER JOIN channels as activity_channel ON activity.channel_id = activity_channel.id   where activity_channel.id = %u and activity.id >= 1 and activity.id <= 10000000 group by activity_id order by activity_id", upper_obj->channel_id);
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
    size_t* pos = idptr_ds_5.find_by_key(str_to_uint(row[0]));
    ItemPointer ipos(INVALID_POS);
    if (pos != nullptr) ipos.pos = *pos;
    key_0 = str_to_uint(row[0]);
    Channel40::ds_48_key_type key(key_0);
    if (pos != nullptr) upper_obj->insert_ds_48_by_key(key,ipos);
    row = mysql_fetch_row(result);
  }
  mysql_free_result(result);
}
#endif // __KANDAN_LG_H_
