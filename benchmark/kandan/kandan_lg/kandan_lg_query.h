
#include "util.h"
#include "data_struct.h"
#include "kandan_lg.h"

struct Query0Result {
  struct PActivity {
    PActivity() {}
    oid_t id_0;
    inline void set_id(oid_t fv_) { id_0 = fv_; }
    inline oid_t id() const { return id_0; }
    date_t created_at_1;
    inline void set_created_at(date_t fv_) { created_at_1 = fv_; }
    inline date_t created_at() const { return created_at_1; }
    date_t updated_at_2;
    inline void set_updated_at(date_t fv_) { updated_at_2 = fv_; }
    inline date_t updated_at() const { return updated_at_2; }
    VarChar<16> action_3;
    inline void set_action(VarChar<16> fv_) { action_3 = fv_; }
    inline VarChar<16> action() const { return action_3; }
    inline void set_action(const char* v_) { action_3 = v_; }
    LongString content_4;
    inline void set_content(LongString fv_) { content_4 = fv_; }
    inline LongString content() const { return content_4; }
    inline void set_content(const char* v_) { content_4 = v_; }
    oid_t channel_id_5;
    inline void set_channel_id(oid_t fv_) { channel_id_5 = fv_; }
    inline oid_t channel_id() const { return channel_id_5; }
    oid_t user_id_6;
    inline void set_user_id(oid_t fv_) { user_id_6 = fv_; }
    inline oid_t user_id() const { return user_id_6; }
    inline bool operator< (const PActivity& other) const { return (this->id() < other.id()); }
  };

  std::vector<PActivity> activity;
  size_t activity_size() { return activity.size(); }
  PActivity* add_activity() { activity.push_back(PActivity()); return &activity.back(); }
  inline void sort_activity() { std::sort(activity.begin(), activity.end()); }
};

void query_0_plan_13(oid_t param_channel_id_0, Query0Result& qresult);
