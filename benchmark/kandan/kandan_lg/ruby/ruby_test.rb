require "./proto_kandan_lg_pb.rb"
require "ffi-rzmq.rb"
def time_diff_milli(start, finish)
  (finish - start) * 1000.0
end

def run_rq_0
  param = KandanLg::QueryParam.new(:query_id => 0, :q_0_param_0_uid => 52)
  serialized_param = KandanLg::QueryParam.encode(param)

  ctx = ZMQ::Context.new
  @rep_sock = ctx.socket(ZMQ::REQ)
  rc = @rep_sock.connect('tcp://127.0.0.1:5555')
  t1 = Time.now
  @rep_sock.send_string(serialized_param)
  data = ''
  @rep_sock.recv_string(data)
  t2 = Time.now
  data = KandanLg::PQuery0Result.decode(data)
  puts "query 0 time elapsed = #{time_diff_milli(t1, t2)} ms"
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
def run_queries
  run_rq_0
end
run_queries
