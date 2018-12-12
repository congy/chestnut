includes = """
#include <fstream>
#include <vector>
#include <map>
#include <thread>
#include <chrono> 
#include "mysql.h"
#include "util.h"
#include "data_struct.h"
"""

server_init_template_begin = """
  void *context = zmq_ctx_new ();
  void *responder = zmq_socket (context, ZMQ_REP);
  int rc = zmq_bind (responder, "tcp://127.0.0.1:5555");
  if (rc != 0){
      return 0;
  }
  std::string buffer;
  std::string output;
  while (true) {
    zmq_msg_t rmsg;
    int rc = zmq_msg_init (&rmsg);
    assert (rc == 0);
    rc = zmq_msg_recv (&rmsg, responder, 0);
    buffer.assign(reinterpret_cast<char*>(zmq_msg_data(&rmsg)), zmq_msg_size(&rmsg));
    //memcpy(buffer, (char*)zmq_msg_data(&rmsg), zmq_msg_size(&rmsg));
"""
server_init_template_end = """
    //zmq_send (responder, output.c_str(), output.length()+1, 0);
    zmq_msg_t smsg;
    rc = zmq_msg_init_size (&smsg, output.length());
    assert (rc == 0);
    memcpy (zmq_msg_data (&smsg), output.c_str(), output.length());
    rc = zmq_msg_send (&smsg, responder, 0);
  }
"""

ruby_template_begin = """
  ctx = ZMQ::Context.new
  @rep_sock = ctx.socket(ZMQ::REQ)
  rc = @rep_sock.connect('tcp://127.0.0.1:5555')
  t1 = Time.now
  @rep_sock.send_string(serialized_param)
  data = ''
  @rep_sock.recv_string(data)
  t2 = Time.now
"""

ruby_template_end = """
  @rep_sock.close()
"""
