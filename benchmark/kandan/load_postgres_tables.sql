DROP TABLE users;
CREATE TABLE users (
  id BIGINT,
  email VARCHAR(32),
  encrypted_password VARCHAR(256),
  reset_password_token VARCHAR(256),
  reset_password_sent_at TIMESTAMP,
  remember_created_at TIMESTAMP,
  first_name VARCHAR(32),
  last_name VARCHAR(32),
  signin_count BIGINT,
  current_sign_in_at TIMESTAMP,
  current_sign_in_ip VARCHAR(16),
  last_sign_in_at TIMESTAMP,
  last_sign_in_ip VARCHAR(16),
  auth_token VARCHAR(128),
  locale VARCHAR(16),
  gravatar_hash VARCHAR(256),
  username VARCHAR(32),
  regstatus VARCHAR(8),
  active INTEGER,
  is_admin INTEGER,
  avatar_url VARCHAR(256),
  created_at TIMESTAMP,
  updated_at TIMESTAMP);
COPY users FROM 'C:\Users\Mingw\Projects\chestnut-demo-website\chestnut\repo\benchmark\kandan/data/kandan_lg//user.tsv' DELIMITER '|' CSV HEADER;

ALTER TABLE users ADD PRIMARY KEY (id);
DROP TABLE channels;
CREATE TABLE channels (
  id BIGINT,
  name VARCHAR(64),
  created_at TIMESTAMP,
  updated_at TIMESTAMP,
  user_id BIGINT);
COPY channels FROM 'C:\Users\Mingw\Projects\chestnut-demo-website\chestnut\repo\benchmark\kandan/data/kandan_lg//channel.tsv' DELIMITER '|' CSV HEADER;

ALTER TABLE channels ADD PRIMARY KEY (id);
DROP TABLE activities;
CREATE TABLE activities (
  id BIGINT,
  created_at TIMESTAMP,
  updated_at TIMESTAMP,
  action VARCHAR(16),
  content VARCHAR(256),
  channel_id BIGINT,
  user_id BIGINT);
COPY activities FROM 'C:\Users\Mingw\Projects\chestnut-demo-website\chestnut\repo\benchmark\kandan/data/kandan_lg//activity.tsv' DELIMITER '|' CSV HEADER;

ALTER TABLE activities ADD PRIMARY KEY (id);
DROP TABLE attachments;
CREATE TABLE attachments (
  id BIGINT,
  file_file_name VARCHAR(128),
  file_content_type VARCHAR(16),
  file_file_size BIGINT,
  message_id BIGINT,
  file_updated_at TIMESTAMP,
  created_at TIMESTAMP,
  updated_at TIMESTAMP,
  user_id BIGINT,
  channel_id BIGINT);
COPY attachments FROM 'C:\Users\Mingw\Projects\chestnut-demo-website\chestnut\repo\benchmark\kandan/data/kandan_lg//attachment.tsv' DELIMITER '|' CSV HEADER;

ALTER TABLE attachments ADD PRIMARY KEY (id);
