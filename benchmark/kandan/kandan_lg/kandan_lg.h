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
//ds[0]: [6] sorted-array : [table = Activity, keys = (activity:channel-channel:id,-activity:id), cond = (((activity:channel . channel:id) == Param (channel_id)) && ((activity:id >= Value (1)) && (activity:id <= Value (20)))), value = memobj(Activity-id,created_at,updated_at,action,content,channel_id,user_id)]
//
struct Activity6 {
public:
  oid_t activity_id;
  date_t activity_created_at;
  date_t activity_updated_at;
  VarChar<16> activity_action;
  LongString activity_content;
  oid_t activity_channel_id;
  oid_t activity_user_id;
  Activity6(): activity_id(0),activity_created_at(0),activity_updated_at(0),activity_action(0),activity_content(0),activity_channel_id(0),activity_user_id(0) {}
  Activity6(oid_t v0,date_t v1,date_t v2,VarChar<16> v3,LongString v4,oid_t v5,oid_t v6): activity_id(v0),activity_created_at(v1),activity_updated_at(v2),activity_action(v3),activity_content(v4),activity_channel_id(v5),activity_user_id(v6) {}
  Activity6(const kandan_lg::PActivity& p): activity_id(p.id()),activity_created_at(p.created_at()),activity_updated_at(p.updated_at()),activity_action(p.action()),activity_content(p.content()),activity_channel_id(p.channel_id()),activity_user_id(p.user_id()) {}
  inline void clear() { activity_id = 0; }
  inline bool operator==(const Activity6& other) const { return activity_id==other.activity_id; }
  void print() {
    printf("[activity:id=%u, created_at=%u, updated_at=%u, action=%s, content=%s, channel_id=%u, user_id=%u]\n", activity_id, activity_created_at, activity_updated_at, activity_action.s, activity_content.s.c_str(), activity_channel_id, activity_user_id);
  }
};
struct  ds_6_key_type {
  oid_t channel_id;
  oid_t activity_id;
  ds_6_key_type(oid_t channel_id_,oid_t activity_id_): channel_id(channel_id_),activity_id(activity_id_) {}
  ds_6_key_type(): channel_id(0),activity_id(0) {}
  inline bool operator==(const ds_6_key_type& other) const { return (channel_id == other.channel_id)&&(activity_id == other.activity_id); }
  inline bool operator<(const ds_6_key_type& other) const { return false || (true && channel_id < other.channel_id) || (true&& channel_id == other.channel_id && activity_id < other.activity_id); }
  inline size_t get_hash() const { return (std::hash<oid_t>()(channel_id) << 0) + (std::hash<oid_t>()(activity_id) << 16); }
};
extern SortedArray<ds_6_key_type, Activity6, 20> ds_6;
inline size_t insert_ds_6_by_key(ds_6_key_type& key, Activity6& v) {
  size_t insertpos = ds_6.insert_by_key(key, v);
}
void read_data(); 
//ds 6: [6] sorted-array : [table = Activity, keys = (activity:channel-channel:id,-activity:id), cond = (((activity:channel . channel:id) == Param (channel_id)) && ((activity:id >= Value (1)) && (activity:id <= Value (20)))), value = memobj(Activity-id,created_at,updated_at,action,content,channel_id,user_id)]
inline void init_ds_6_from_sql(MYSQL* conn) {
  oid_t key_0 = 0;
  oid_t key_1 = 0;
  std::string query_str("select activity.id as activity_id,activity.created_at as activity_created_at,activity.updated_at as activity_updated_at,activity.action as activity_action,activity.content as activity_content,activity.channel_id as activity_channel_id,activity.user_id as activity_user_id from activities as activity INNER JOIN channels as activity_channel ON activity.channel_id = activity_channel.id   where activity.id >= 1 and activity.id <= 20 group by activity_id,activity_created_at,activity_updated_at,activity_action,activity_content,activity_channel_id,activity_user_id order by activity_id");

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
    Activity6 value(str_to_uint(row[0]),time_to_uint(row[1]),time_to_uint(row[2]),(row[3]),(row[4]),str_to_uint(row[5]),str_to_uint(row[6]));
    key_0 = str_to_uint(row[7]);
    key_1 = str_to_uint(row[0]);
    ds_6_key_type key(key_0,key_1);
    insert_ds_6_by_key(key,value);
    row = mysql_fetch_row(result);
  }
  mysql_free_result(result);
}
#endif // __KANDAN_LG_H_
