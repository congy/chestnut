require "./proto_kandan_small_pb.rb"
require "ffi-rzmq.rb"
def time_diff_milli(start, finish)
  (finish - start) * 1000.0
end

def run_rq_0
  param = KandanSmall::QueryParam.new(:query_id => 0, :q_0_param_0_id => 4118)
  serialized_param = KandanSmall::QueryParam.encode(param)

  ctx = ZMQ::Context.new
  @rep_sock = ctx.socket(ZMQ::REQ)
  rc = @rep_sock.connect('tcp://127.0.0.1:5555')
  t1 = Time.now
  @rep_sock.send_string(serialized_param)
  data = ''
  @rep_sock.recv_string(data)
  t2 = Time.now
  data = KandanSmall::PQuery0Result.decode(data)
  puts "query 0 time elapsed = #{time_diff_milli(t1, t2)} ms"
  puts "aggrs:"
  puts "size = #{data.activity.length}"
  cnt_0 = 0
  data.activity.each do |x|
  cnt_0 = cnt_0 + 1
  if cnt_0 > 20 then
    break
  end
    puts "id = #{x.id}"
    puts "created_at = #{x.created_at}"
    puts "updated_at = #{x.updated_at}"
    puts "action = #{x.action}"
    puts "content = #{x.content}"
    puts "channel_id = #{x.channel_id}"
    puts "user_id = #{x.user_id}"

  end


  @rep_sock.close()
end
def run_rq_1
  param = KandanSmall::QueryParam.new(:query_id => 1, :q_1_param_0_uid => 78)
  serialized_param = KandanSmall::QueryParam.encode(param)

  ctx = ZMQ::Context.new
  @rep_sock = ctx.socket(ZMQ::REQ)
  rc = @rep_sock.connect('tcp://127.0.0.1:5555')
  t1 = Time.now
  @rep_sock.send_string(serialized_param)
  data = ''
  @rep_sock.recv_string(data)
  t2 = Time.now
  data = KandanSmall::PQuery1Result.decode(data)
  puts "query 1 time elapsed = #{time_diff_milli(t1, t2)} ms"
  puts "aggrs:"
  puts "size = #{data.user.length}"
  cnt_0 = 0
  data.user.each do |x|
  cnt_0 = cnt_0 + 1
  if cnt_0 > 20 then
    break
  end
    puts "id = #{x.id}"
    puts "email = #{x.email}"
    puts "encrypted_password = #{x.encrypted_password}"
    puts "reset_password_token = #{x.reset_password_token}"
    puts "reset_password_sent_at = #{x.reset_password_sent_at}"
    puts "remember_created_at = #{x.remember_created_at}"
    puts "first_name = #{x.first_name}"
    puts "last_name = #{x.last_name}"
    puts "signin_count = #{x.signin_count}"
    puts "current_sign_in_at = #{x.current_sign_in_at}"
    puts "current_sign_in_ip = #{x.current_sign_in_ip}"
    puts "last_sign_in_at = #{x.last_sign_in_at}"
    puts "last_sign_in_ip = #{x.last_sign_in_ip}"
    puts "auth_token = #{x.auth_token}"
    puts "locale = #{x.locale}"
    puts "gravatar_hash = #{x.gravatar_hash}"
    puts "username = #{x.username}"
    puts "regstatus = #{x.regstatus}"
    puts "active = #{x.active}"
    puts "is_admin = #{x.is_admin}"
    puts "avatar_url = #{x.avatar_url}"
    puts "created_at = #{x.created_at}"
    puts "updated_at = #{x.updated_at}"

  end


  @rep_sock.close()
end
def run_rq_2
  param = KandanSmall::QueryParam.new(:query_id => 2, :q_2_param_0_channel_id => 21)
  serialized_param = KandanSmall::QueryParam.encode(param)

  ctx = ZMQ::Context.new
  @rep_sock = ctx.socket(ZMQ::REQ)
  rc = @rep_sock.connect('tcp://127.0.0.1:5555')
  t1 = Time.now
  @rep_sock.send_string(serialized_param)
  data = ''
  @rep_sock.recv_string(data)
  t2 = Time.now
  data = KandanSmall::PQuery2Result.decode(data)
  puts "query 2 time elapsed = #{time_diff_milli(t1, t2)} ms"
  puts "aggrs:"
  puts "size = #{data.attachment.length}"
  cnt_0 = 0
  data.attachment.each do |x|
  cnt_0 = cnt_0 + 1
  if cnt_0 > 20 then
    break
  end
    puts "id = #{x.id}"
    puts "file_file_name = #{x.file_file_name}"
    puts "file_content_type = #{x.file_content_type}"
    puts "file_file_size = #{x.file_file_size}"
    puts "message_id = #{x.message_id}"
    puts "file_updated_at = #{x.file_updated_at}"
    puts "created_at = #{x.created_at}"
    puts "updated_at = #{x.updated_at}"
    puts "user_id = #{x.user_id}"
    puts "channel_id = #{x.channel_id}"

  end


  @rep_sock.close()
end
def run_rq_3
  param = KandanSmall::QueryParam.new(:query_id => 3, :q_3_param_0_channel_id => 395)
  serialized_param = KandanSmall::QueryParam.encode(param)

  ctx = ZMQ::Context.new
  @rep_sock = ctx.socket(ZMQ::REQ)
  rc = @rep_sock.connect('tcp://127.0.0.1:5555')
  t1 = Time.now
  @rep_sock.send_string(serialized_param)
  data = ''
  @rep_sock.recv_string(data)
  t2 = Time.now
  data = KandanSmall::PQuery3Result.decode(data)
  puts "query 3 time elapsed = #{time_diff_milli(t1, t2)} ms"
  puts "aggrs:"
  puts "size = #{data.channel.length}"
  cnt_0 = 0
  data.channel.each do |x|
  cnt_0 = cnt_0 + 1
  if cnt_0 > 20 then
    break
  end
    puts "count = #{x.count}"
    puts "id = #{x.id}"
    puts "name = #{x.name}"
    puts "created_at = #{x.created_at}"
    puts "updated_at = #{x.updated_at}"
    puts "user_id = #{x.user_id}"
    puts "count = #{x.count}"
    puts "sz = #{x.activities.length}"
    cnt_1 = 0
    x.activities.each do |element_activities|
      cnt_1 = cnt_1 + 1
      if cnt_1 > 20 then
        break
      end
      puts "	id = #{element_activities.id}"
      puts "	created_at = #{element_activities.created_at}"
      puts "	updated_at = #{element_activities.updated_at}"
      puts "	action = #{element_activities.action}"
      puts "	content = #{element_activities.content}"
      puts "	channel_id = #{element_activities.channel_id}"
      puts "	user_id = #{element_activities.user_id}"
      if element_activities.user != nil
        puts "		id = #{element_activities.user.id}"
        puts "		email = #{element_activities.user.email}"
        puts "		encrypted_password = #{element_activities.user.encrypted_password}"
        puts "		reset_password_token = #{element_activities.user.reset_password_token}"
        puts "		reset_password_sent_at = #{element_activities.user.reset_password_sent_at}"
        puts "		remember_created_at = #{element_activities.user.remember_created_at}"
        puts "		first_name = #{element_activities.user.first_name}"
        puts "		last_name = #{element_activities.user.last_name}"
        puts "		signin_count = #{element_activities.user.signin_count}"
        puts "		current_sign_in_at = #{element_activities.user.current_sign_in_at}"
        puts "		current_sign_in_ip = #{element_activities.user.current_sign_in_ip}"
        puts "		last_sign_in_at = #{element_activities.user.last_sign_in_at}"
        puts "		last_sign_in_ip = #{element_activities.user.last_sign_in_ip}"
        puts "		auth_token = #{element_activities.user.auth_token}"
        puts "		locale = #{element_activities.user.locale}"
        puts "		gravatar_hash = #{element_activities.user.gravatar_hash}"
        puts "		username = #{element_activities.user.username}"
        puts "		regstatus = #{element_activities.user.regstatus}"
        puts "		active = #{element_activities.user.active}"
        puts "		is_admin = #{element_activities.user.is_admin}"
        puts "		avatar_url = #{element_activities.user.avatar_url}"
        puts "		created_at = #{element_activities.user.created_at}"
        puts "		updated_at = #{element_activities.user.updated_at}"

      end

    end

  end


  @rep_sock.close()
end
def run_rq_4
  param = KandanSmall::QueryParam.new(:query_id => 4, :q_4_param_0_name => "Kristen Watkins")
  serialized_param = KandanSmall::QueryParam.encode(param)

  ctx = ZMQ::Context.new
  @rep_sock = ctx.socket(ZMQ::REQ)
  rc = @rep_sock.connect('tcp://127.0.0.1:5555')
  t1 = Time.now
  @rep_sock.send_string(serialized_param)
  data = ''
  @rep_sock.recv_string(data)
  t2 = Time.now
  data = KandanSmall::PQuery4Result.decode(data)
  puts "query 4 time elapsed = #{time_diff_milli(t1, t2)} ms"
  puts "aggrs:"
  puts "size = #{data.channel.length}"
  cnt_0 = 0
  data.channel.each do |x|
  cnt_0 = cnt_0 + 1
  if cnt_0 > 20 then
    break
  end
    puts "id = #{x.id}"
    puts "name = #{x.name}"
    puts "created_at = #{x.created_at}"
    puts "updated_at = #{x.updated_at}"
    puts "user_id = #{x.user_id}"
    puts "count = #{x.count}"

  end


  @rep_sock.close()
end
def run_rq_5
  param = KandanSmall::QueryParam.new(:query_id => 5, )
  serialized_param = KandanSmall::QueryParam.encode(param)

  ctx = ZMQ::Context.new
  @rep_sock = ctx.socket(ZMQ::REQ)
  rc = @rep_sock.connect('tcp://127.0.0.1:5555')
  t1 = Time.now
  @rep_sock.send_string(serialized_param)
  data = ''
  @rep_sock.recv_string(data)
  t2 = Time.now
  data = KandanSmall::PQuery5Result.decode(data)
  puts "query 5 time elapsed = #{time_diff_milli(t1, t2)} ms"
  puts "aggrs:"
  puts "size = #{data.channel.length}"
  cnt_0 = 0
  data.channel.each do |x|
  cnt_0 = cnt_0 + 1
  if cnt_0 > 20 then
    break
  end
    puts "id = #{x.id}"
    puts "name = #{x.name}"
    puts "created_at = #{x.created_at}"
    puts "updated_at = #{x.updated_at}"
    puts "user_id = #{x.user_id}"
    puts "count = #{x.count}"
    puts "sz = #{x.activities.length}"
    cnt_1 = 0
    x.activities.each do |element_activities|
      cnt_1 = cnt_1 + 1
      if cnt_1 > 20 then
        break
      end
      puts "	id = #{element_activities.id}"
      puts "	created_at = #{element_activities.created_at}"
      puts "	updated_at = #{element_activities.updated_at}"
      puts "	action = #{element_activities.action}"
      puts "	content = #{element_activities.content}"
      puts "	channel_id = #{element_activities.channel_id}"
      puts "	user_id = #{element_activities.user_id}"
      if element_activities.user != nil
        puts "		id = #{element_activities.user.id}"
        puts "		email = #{element_activities.user.email}"
        puts "		encrypted_password = #{element_activities.user.encrypted_password}"
        puts "		reset_password_token = #{element_activities.user.reset_password_token}"
        puts "		reset_password_sent_at = #{element_activities.user.reset_password_sent_at}"
        puts "		remember_created_at = #{element_activities.user.remember_created_at}"
        puts "		first_name = #{element_activities.user.first_name}"
        puts "		last_name = #{element_activities.user.last_name}"
        puts "		signin_count = #{element_activities.user.signin_count}"
        puts "		current_sign_in_at = #{element_activities.user.current_sign_in_at}"
        puts "		current_sign_in_ip = #{element_activities.user.current_sign_in_ip}"
        puts "		last_sign_in_at = #{element_activities.user.last_sign_in_at}"
        puts "		last_sign_in_ip = #{element_activities.user.last_sign_in_ip}"
        puts "		auth_token = #{element_activities.user.auth_token}"
        puts "		locale = #{element_activities.user.locale}"
        puts "		gravatar_hash = #{element_activities.user.gravatar_hash}"
        puts "		username = #{element_activities.user.username}"
        puts "		regstatus = #{element_activities.user.regstatus}"
        puts "		active = #{element_activities.user.active}"
        puts "		is_admin = #{element_activities.user.is_admin}"
        puts "		avatar_url = #{element_activities.user.avatar_url}"
        puts "		created_at = #{element_activities.user.created_at}"
        puts "		updated_at = #{element_activities.user.updated_at}"

      end

    end

  end


  @rep_sock.close()
end
def run_rq_6
  param = KandanSmall::QueryParam.new(:query_id => 6, :q_6_param_0_keyword => "Run question same ahead piece. Brother class debate have research sister board. Believe middle man system especially grow. What sit direction gun term any southern value. Glass behind land time size small marriage. Civil TV management hold tough list yet dark. Force man democratic daughter product thus. Interview off section mother. Participant paper catch. Paper new Democrat score carry. Peace member main record general. Leg director phone wait. Figure professor season shoulder instead. Fund up base effort heavy enough. Mention avoid general. Young adult include. Themselves outside chance. Six year bill someone. Total candidate call total affect. Face box out moment. Performance set describe point term section pretty always. Plan painting participant article push. Senior us station draw along chair seven. Crime old technology shoulder return. House open art agent. He manager once car. Whatever season hair factor show available. Inside street attorney somebody up sign news.")
  serialized_param = KandanSmall::QueryParam.encode(param)

  ctx = ZMQ::Context.new
  @rep_sock = ctx.socket(ZMQ::REQ)
  rc = @rep_sock.connect('tcp://127.0.0.1:5555')
  t1 = Time.now
  @rep_sock.send_string(serialized_param)
  data = ''
  @rep_sock.recv_string(data)
  t2 = Time.now
  data = KandanSmall::PQuery6Result.decode(data)
  puts "query 6 time elapsed = #{time_diff_milli(t1, t2)} ms"
  puts "aggrs:"
  puts "size = #{data.activity.length}"
  cnt_0 = 0
  data.activity.each do |x|
  cnt_0 = cnt_0 + 1
  if cnt_0 > 20 then
    break
  end
    puts "id = #{x.id}"
    puts "created_at = #{x.created_at}"
    puts "updated_at = #{x.updated_at}"
    puts "action = #{x.action}"
    puts "content = #{x.content}"
    puts "channel_id = #{x.channel_id}"
    puts "user_id = #{x.user_id}"
    if x.user != nil
      puts "	id = #{x.user.id}"
      puts "	email = #{x.user.email}"
      puts "	encrypted_password = #{x.user.encrypted_password}"
      puts "	reset_password_token = #{x.user.reset_password_token}"
      puts "	reset_password_sent_at = #{x.user.reset_password_sent_at}"
      puts "	remember_created_at = #{x.user.remember_created_at}"
      puts "	first_name = #{x.user.first_name}"
      puts "	last_name = #{x.user.last_name}"
      puts "	signin_count = #{x.user.signin_count}"
      puts "	current_sign_in_at = #{x.user.current_sign_in_at}"
      puts "	current_sign_in_ip = #{x.user.current_sign_in_ip}"
      puts "	last_sign_in_at = #{x.user.last_sign_in_at}"
      puts "	last_sign_in_ip = #{x.user.last_sign_in_ip}"
      puts "	auth_token = #{x.user.auth_token}"
      puts "	locale = #{x.user.locale}"
      puts "	gravatar_hash = #{x.user.gravatar_hash}"
      puts "	username = #{x.user.username}"
      puts "	regstatus = #{x.user.regstatus}"
      puts "	active = #{x.user.active}"
      puts "	is_admin = #{x.user.is_admin}"
      puts "	avatar_url = #{x.user.avatar_url}"
      puts "	created_at = #{x.user.created_at}"
      puts "	updated_at = #{x.user.updated_at}"

    end

  end


  @rep_sock.close()
end
def run_queries
  run_rq_0
  run_rq_1
  run_rq_2
  run_rq_3
  run_rq_4
  run_rq_5
  run_rq_6
end
run_queries
