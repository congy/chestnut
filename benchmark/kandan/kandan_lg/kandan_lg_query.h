
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
  };

  std::vector<PActivity> activity;
  size_t activity_size() { return activity.size(); }
  PActivity* add_activity() { activity.push_back(PActivity()); return &activity.back(); }
};

void query_0_plan_6(oid_t param_id_0, Query0Result& qresult);

struct Query1Result {
  struct PUser {
    PUser() {}
    oid_t id_0;
    inline void set_id(oid_t fv_) { id_0 = fv_; }
    inline oid_t id() const { return id_0; }
    VarChar<32> email_1;
    inline void set_email(VarChar<32> fv_) { email_1 = fv_; }
    inline VarChar<32> email() const { return email_1; }
    inline void set_email(const char* v_) { email_1 = v_; }
    VarChar<256> encrypted_password_2;
    inline void set_encrypted_password(VarChar<256> fv_) { encrypted_password_2 = fv_; }
    inline VarChar<256> encrypted_password() const { return encrypted_password_2; }
    inline void set_encrypted_password(const char* v_) { encrypted_password_2 = v_; }
    VarChar<256> reset_password_token_3;
    inline void set_reset_password_token(VarChar<256> fv_) { reset_password_token_3 = fv_; }
    inline VarChar<256> reset_password_token() const { return reset_password_token_3; }
    inline void set_reset_password_token(const char* v_) { reset_password_token_3 = v_; }
    date_t reset_password_sent_at_4;
    inline void set_reset_password_sent_at(date_t fv_) { reset_password_sent_at_4 = fv_; }
    inline date_t reset_password_sent_at() const { return reset_password_sent_at_4; }
    date_t remember_created_at_5;
    inline void set_remember_created_at(date_t fv_) { remember_created_at_5 = fv_; }
    inline date_t remember_created_at() const { return remember_created_at_5; }
    VarChar<32> first_name_6;
    inline void set_first_name(VarChar<32> fv_) { first_name_6 = fv_; }
    inline VarChar<32> first_name() const { return first_name_6; }
    inline void set_first_name(const char* v_) { first_name_6 = v_; }
    VarChar<32> last_name_7;
    inline void set_last_name(VarChar<32> fv_) { last_name_7 = fv_; }
    inline VarChar<32> last_name() const { return last_name_7; }
    inline void set_last_name(const char* v_) { last_name_7 = v_; }
    uint32_t signin_count_8;
    inline void set_signin_count(uint32_t fv_) { signin_count_8 = fv_; }
    inline uint32_t signin_count() const { return signin_count_8; }
    date_t current_sign_in_at_9;
    inline void set_current_sign_in_at(date_t fv_) { current_sign_in_at_9 = fv_; }
    inline date_t current_sign_in_at() const { return current_sign_in_at_9; }
    VarChar<16> current_sign_in_ip_10;
    inline void set_current_sign_in_ip(VarChar<16> fv_) { current_sign_in_ip_10 = fv_; }
    inline VarChar<16> current_sign_in_ip() const { return current_sign_in_ip_10; }
    inline void set_current_sign_in_ip(const char* v_) { current_sign_in_ip_10 = v_; }
    date_t last_sign_in_at_11;
    inline void set_last_sign_in_at(date_t fv_) { last_sign_in_at_11 = fv_; }
    inline date_t last_sign_in_at() const { return last_sign_in_at_11; }
    VarChar<16> last_sign_in_ip_12;
    inline void set_last_sign_in_ip(VarChar<16> fv_) { last_sign_in_ip_12 = fv_; }
    inline VarChar<16> last_sign_in_ip() const { return last_sign_in_ip_12; }
    inline void set_last_sign_in_ip(const char* v_) { last_sign_in_ip_12 = v_; }
    VarChar<128> auth_token_13;
    inline void set_auth_token(VarChar<128> fv_) { auth_token_13 = fv_; }
    inline VarChar<128> auth_token() const { return auth_token_13; }
    inline void set_auth_token(const char* v_) { auth_token_13 = v_; }
    VarChar<16> locale_14;
    inline void set_locale(VarChar<16> fv_) { locale_14 = fv_; }
    inline VarChar<16> locale() const { return locale_14; }
    inline void set_locale(const char* v_) { locale_14 = v_; }
    VarChar<256> gravatar_hash_15;
    inline void set_gravatar_hash(VarChar<256> fv_) { gravatar_hash_15 = fv_; }
    inline VarChar<256> gravatar_hash() const { return gravatar_hash_15; }
    inline void set_gravatar_hash(const char* v_) { gravatar_hash_15 = v_; }
    VarChar<32> username_16;
    inline void set_username(VarChar<32> fv_) { username_16 = fv_; }
    inline VarChar<32> username() const { return username_16; }
    inline void set_username(const char* v_) { username_16 = v_; }
    VarChar<8> regstatus_17;
    inline void set_regstatus(VarChar<8> fv_) { regstatus_17 = fv_; }
    inline VarChar<8> regstatus() const { return regstatus_17; }
    inline void set_regstatus(const char* v_) { regstatus_17 = v_; }
    bool active_18;
    inline void set_active(bool fv_) { active_18 = fv_; }
    inline bool active() const { return active_18; }
    bool is_admin_19;
    inline void set_is_admin(bool fv_) { is_admin_19 = fv_; }
    inline bool is_admin() const { return is_admin_19; }
    LongString avatar_url_20;
    inline void set_avatar_url(LongString fv_) { avatar_url_20 = fv_; }
    inline LongString avatar_url() const { return avatar_url_20; }
    inline void set_avatar_url(const char* v_) { avatar_url_20 = v_; }
    date_t created_at_21;
    inline void set_created_at(date_t fv_) { created_at_21 = fv_; }
    inline date_t created_at() const { return created_at_21; }
    date_t updated_at_22;
    inline void set_updated_at(date_t fv_) { updated_at_22 = fv_; }
    inline date_t updated_at() const { return updated_at_22; }
  };

  std::vector<PUser> user;
  size_t user_size() { return user.size(); }
  PUser* add_user() { user.push_back(PUser()); return &user.back(); }
};

void query_1_plan_0(oid_t param_uid_0, Query1Result& qresult);

struct Query2Result {
  struct PAttachment {
    PAttachment() {}
    oid_t id_0;
    inline void set_id(oid_t fv_) { id_0 = fv_; }
    inline oid_t id() const { return id_0; }
    VarChar<128> file_file_name_1;
    inline void set_file_file_name(VarChar<128> fv_) { file_file_name_1 = fv_; }
    inline VarChar<128> file_file_name() const { return file_file_name_1; }
    inline void set_file_file_name(const char* v_) { file_file_name_1 = v_; }
    VarChar<16> file_content_type_2;
    inline void set_file_content_type(VarChar<16> fv_) { file_content_type_2 = fv_; }
    inline VarChar<16> file_content_type() const { return file_content_type_2; }
    inline void set_file_content_type(const char* v_) { file_content_type_2 = v_; }
    uint32_t file_file_size_3;
    inline void set_file_file_size(uint32_t fv_) { file_file_size_3 = fv_; }
    inline uint32_t file_file_size() const { return file_file_size_3; }
    uint32_t message_id_4;
    inline void set_message_id(uint32_t fv_) { message_id_4 = fv_; }
    inline uint32_t message_id() const { return message_id_4; }
    date_t file_updated_at_5;
    inline void set_file_updated_at(date_t fv_) { file_updated_at_5 = fv_; }
    inline date_t file_updated_at() const { return file_updated_at_5; }
    date_t created_at_6;
    inline void set_created_at(date_t fv_) { created_at_6 = fv_; }
    inline date_t created_at() const { return created_at_6; }
    date_t updated_at_7;
    inline void set_updated_at(date_t fv_) { updated_at_7 = fv_; }
    inline date_t updated_at() const { return updated_at_7; }
    oid_t user_id_8;
    inline void set_user_id(oid_t fv_) { user_id_8 = fv_; }
    inline oid_t user_id() const { return user_id_8; }
    oid_t channel_id_9;
    inline void set_channel_id(oid_t fv_) { channel_id_9 = fv_; }
    inline oid_t channel_id() const { return channel_id_9; }
    inline bool operator< (const PAttachment& other) const { return (this->created_at() < other.created_at()); }
  };

  std::vector<PAttachment> attachment;
  size_t attachment_size() { return attachment.size(); }
  PAttachment* add_attachment() { attachment.push_back(PAttachment()); return &attachment.back(); }
  inline void sort_attachment() { std::sort(attachment.begin(), attachment.end()); }
};

void query_2_plan_13(oid_t param_channel_id_0, Query2Result& qresult);

struct Query3Result {
  struct PChannel {
    PChannel() {}
    oid_t id_0;
    inline void set_id(oid_t fv_) { id_0 = fv_; }
    inline oid_t id() const { return id_0; }
    VarChar<64> name_1;
    inline void set_name(VarChar<64> fv_) { name_1 = fv_; }
    inline VarChar<64> name() const { return name_1; }
    inline void set_name(const char* v_) { name_1 = v_; }
    date_t created_at_2;
    inline void set_created_at(date_t fv_) { created_at_2 = fv_; }
    inline date_t created_at() const { return created_at_2; }
    date_t updated_at_3;
    inline void set_updated_at(date_t fv_) { updated_at_3 = fv_; }
    inline date_t updated_at() const { return updated_at_3; }
    oid_t user_id_4;
    inline void set_user_id(oid_t fv_) { user_id_4 = fv_; }
    inline oid_t user_id() const { return user_id_4; }
    struct PActivitiesInChannel {
      PActivitiesInChannel() {}
      LongString content_0;
      inline void set_content(LongString fv_) { content_0 = fv_; }
      inline LongString content() const { return content_0; }
      inline void set_content(const char* v_) { content_0 = v_; }
      VarChar<16> action_1;
      inline void set_action(VarChar<16> fv_) { action_1 = fv_; }
      inline VarChar<16> action() const { return action_1; }
      inline void set_action(const char* v_) { action_1 = v_; }
      date_t created_at_2;
      inline void set_created_at(date_t fv_) { created_at_2 = fv_; }
      inline date_t created_at() const { return created_at_2; }
      date_t updated_at_3;
      inline void set_updated_at(date_t fv_) { updated_at_3 = fv_; }
      inline date_t updated_at() const { return updated_at_3; }
      oid_t id_4;
      inline void set_id(oid_t fv_) { id_4 = fv_; }
      inline oid_t id() const { return id_4; }
      inline bool operator< (const PActivitiesInChannel& other) const { return (this->id() < other.id()); }
      struct PUserInActivity {
        PUserInActivity() {}
        oid_t id_0;
        inline void set_id(oid_t fv_) { id_0 = fv_; }
        inline oid_t id() const { return id_0; }
        VarChar<32> username_1;
        inline void set_username(VarChar<32> fv_) { username_1 = fv_; }
        inline VarChar<32> username() const { return username_1; }
        inline void set_username(const char* v_) { username_1 = v_; }
      };

      PUserInActivity user;
      PUserInActivity* mutable_user() { return &user; };
    };

    uint32_t count_0;
    inline uint32_t count() const { return count_0; }
    inline void set_count(uint32_t fv_) {  count_0 = fv_; }
    std::vector<PActivitiesInChannel> activities;
    size_t activities_size() { return activities.size(); }
    PActivitiesInChannel* add_activities() { activities.push_back(PActivitiesInChannel()); return &activities.back(); }
    inline void sort_activities() { std::sort(activities.begin(), activities.end()); }
  };

  std::vector<PChannel> channel;
  size_t channel_size() { return channel.size(); }
  PChannel* add_channel() { channel.push_back(PChannel()); return &channel.back(); }
};

void query_3_plan_14(oid_t param_channel_id_0, Query3Result& qresult);

struct Query4Result {
  struct PChannel {
    PChannel() {}
    oid_t id_0;
    inline void set_id(oid_t fv_) { id_0 = fv_; }
    inline oid_t id() const { return id_0; }
    VarChar<64> name_1;
    inline void set_name(VarChar<64> fv_) { name_1 = fv_; }
    inline VarChar<64> name() const { return name_1; }
    inline void set_name(const char* v_) { name_1 = v_; }
    date_t created_at_2;
    inline void set_created_at(date_t fv_) { created_at_2 = fv_; }
    inline date_t created_at() const { return created_at_2; }
    date_t updated_at_3;
    inline void set_updated_at(date_t fv_) { updated_at_3 = fv_; }
    inline date_t updated_at() const { return updated_at_3; }
    oid_t user_id_4;
    inline void set_user_id(oid_t fv_) { user_id_4 = fv_; }
    inline oid_t user_id() const { return user_id_4; }
  };

  std::vector<PChannel> channel;
  size_t channel_size() { return channel.size(); }
  PChannel* add_channel() { channel.push_back(PChannel()); return &channel.back(); }
};

void query_4_plan_2(VarChar<64> param_name_0, Query4Result& qresult);

struct Query5Result {
  struct PChannel {
    PChannel() {}
    oid_t id_0;
    inline void set_id(oid_t fv_) { id_0 = fv_; }
    inline oid_t id() const { return id_0; }
    VarChar<64> name_1;
    inline void set_name(VarChar<64> fv_) { name_1 = fv_; }
    inline VarChar<64> name() const { return name_1; }
    inline void set_name(const char* v_) { name_1 = v_; }
    date_t created_at_2;
    inline void set_created_at(date_t fv_) { created_at_2 = fv_; }
    inline date_t created_at() const { return created_at_2; }
    date_t updated_at_3;
    inline void set_updated_at(date_t fv_) { updated_at_3 = fv_; }
    inline date_t updated_at() const { return updated_at_3; }
    oid_t user_id_4;
    inline void set_user_id(oid_t fv_) { user_id_4 = fv_; }
    inline oid_t user_id() const { return user_id_4; }
    struct PActivitiesInChannel {
      PActivitiesInChannel() {}
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
      struct PUserInActivity {
        PUserInActivity() {}
        oid_t id_0;
        inline void set_id(oid_t fv_) { id_0 = fv_; }
        inline oid_t id() const { return id_0; }
        VarChar<32> email_1;
        inline void set_email(VarChar<32> fv_) { email_1 = fv_; }
        inline VarChar<32> email() const { return email_1; }
        inline void set_email(const char* v_) { email_1 = v_; }
        VarChar<256> encrypted_password_2;
        inline void set_encrypted_password(VarChar<256> fv_) { encrypted_password_2 = fv_; }
        inline VarChar<256> encrypted_password() const { return encrypted_password_2; }
        inline void set_encrypted_password(const char* v_) { encrypted_password_2 = v_; }
        VarChar<256> reset_password_token_3;
        inline void set_reset_password_token(VarChar<256> fv_) { reset_password_token_3 = fv_; }
        inline VarChar<256> reset_password_token() const { return reset_password_token_3; }
        inline void set_reset_password_token(const char* v_) { reset_password_token_3 = v_; }
        date_t reset_password_sent_at_4;
        inline void set_reset_password_sent_at(date_t fv_) { reset_password_sent_at_4 = fv_; }
        inline date_t reset_password_sent_at() const { return reset_password_sent_at_4; }
        date_t remember_created_at_5;
        inline void set_remember_created_at(date_t fv_) { remember_created_at_5 = fv_; }
        inline date_t remember_created_at() const { return remember_created_at_5; }
        VarChar<32> first_name_6;
        inline void set_first_name(VarChar<32> fv_) { first_name_6 = fv_; }
        inline VarChar<32> first_name() const { return first_name_6; }
        inline void set_first_name(const char* v_) { first_name_6 = v_; }
        VarChar<32> last_name_7;
        inline void set_last_name(VarChar<32> fv_) { last_name_7 = fv_; }
        inline VarChar<32> last_name() const { return last_name_7; }
        inline void set_last_name(const char* v_) { last_name_7 = v_; }
        uint32_t signin_count_8;
        inline void set_signin_count(uint32_t fv_) { signin_count_8 = fv_; }
        inline uint32_t signin_count() const { return signin_count_8; }
        date_t current_sign_in_at_9;
        inline void set_current_sign_in_at(date_t fv_) { current_sign_in_at_9 = fv_; }
        inline date_t current_sign_in_at() const { return current_sign_in_at_9; }
        VarChar<16> current_sign_in_ip_10;
        inline void set_current_sign_in_ip(VarChar<16> fv_) { current_sign_in_ip_10 = fv_; }
        inline VarChar<16> current_sign_in_ip() const { return current_sign_in_ip_10; }
        inline void set_current_sign_in_ip(const char* v_) { current_sign_in_ip_10 = v_; }
        date_t last_sign_in_at_11;
        inline void set_last_sign_in_at(date_t fv_) { last_sign_in_at_11 = fv_; }
        inline date_t last_sign_in_at() const { return last_sign_in_at_11; }
        VarChar<16> last_sign_in_ip_12;
        inline void set_last_sign_in_ip(VarChar<16> fv_) { last_sign_in_ip_12 = fv_; }
        inline VarChar<16> last_sign_in_ip() const { return last_sign_in_ip_12; }
        inline void set_last_sign_in_ip(const char* v_) { last_sign_in_ip_12 = v_; }
        VarChar<128> auth_token_13;
        inline void set_auth_token(VarChar<128> fv_) { auth_token_13 = fv_; }
        inline VarChar<128> auth_token() const { return auth_token_13; }
        inline void set_auth_token(const char* v_) { auth_token_13 = v_; }
        VarChar<16> locale_14;
        inline void set_locale(VarChar<16> fv_) { locale_14 = fv_; }
        inline VarChar<16> locale() const { return locale_14; }
        inline void set_locale(const char* v_) { locale_14 = v_; }
        VarChar<256> gravatar_hash_15;
        inline void set_gravatar_hash(VarChar<256> fv_) { gravatar_hash_15 = fv_; }
        inline VarChar<256> gravatar_hash() const { return gravatar_hash_15; }
        inline void set_gravatar_hash(const char* v_) { gravatar_hash_15 = v_; }
        VarChar<32> username_16;
        inline void set_username(VarChar<32> fv_) { username_16 = fv_; }
        inline VarChar<32> username() const { return username_16; }
        inline void set_username(const char* v_) { username_16 = v_; }
        VarChar<8> regstatus_17;
        inline void set_regstatus(VarChar<8> fv_) { regstatus_17 = fv_; }
        inline VarChar<8> regstatus() const { return regstatus_17; }
        inline void set_regstatus(const char* v_) { regstatus_17 = v_; }
        bool active_18;
        inline void set_active(bool fv_) { active_18 = fv_; }
        inline bool active() const { return active_18; }
        bool is_admin_19;
        inline void set_is_admin(bool fv_) { is_admin_19 = fv_; }
        inline bool is_admin() const { return is_admin_19; }
        LongString avatar_url_20;
        inline void set_avatar_url(LongString fv_) { avatar_url_20 = fv_; }
        inline LongString avatar_url() const { return avatar_url_20; }
        inline void set_avatar_url(const char* v_) { avatar_url_20 = v_; }
        date_t created_at_21;
        inline void set_created_at(date_t fv_) { created_at_21 = fv_; }
        inline date_t created_at() const { return created_at_21; }
        date_t updated_at_22;
        inline void set_updated_at(date_t fv_) { updated_at_22 = fv_; }
        inline date_t updated_at() const { return updated_at_22; }
      };

      PUserInActivity user;
      PUserInActivity* mutable_user() { return &user; };
    };

    std::vector<PActivitiesInChannel> activities;
    size_t activities_size() { return activities.size(); }
    PActivitiesInChannel* add_activities() { activities.push_back(PActivitiesInChannel()); return &activities.back(); }
  };

  std::vector<PChannel> channel;
  size_t channel_size() { return channel.size(); }
  PChannel* add_channel() { channel.push_back(PChannel()); return &channel.back(); }
};

void query_5_plan_3(Query5Result& qresult);

struct Query6Result {
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
    struct PUserInActivity {
      PUserInActivity() {}
      oid_t id_0;
      inline void set_id(oid_t fv_) { id_0 = fv_; }
      inline oid_t id() const { return id_0; }
      VarChar<32> username_1;
      inline void set_username(VarChar<32> fv_) { username_1 = fv_; }
      inline VarChar<32> username() const { return username_1; }
      inline void set_username(const char* v_) { username_1 = v_; }
    };

    PUserInActivity user;
    PUserInActivity* mutable_user() { return &user; };
  };

  std::vector<PActivity> activity;
  size_t activity_size() { return activity.size(); }
  PActivity* add_activity() { activity.push_back(PActivity()); return &activity.back(); }
};

void query_6_plan_0(LongString param_keyword_0, Query6Result& qresult);

