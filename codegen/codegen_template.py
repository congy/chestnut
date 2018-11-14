includes = """
#include <fstream>
#include <vector>
#include <map>
#include <thread>
#include <chrono>  
#include "util.h"
//#include "parameter.h"
//#include "query.h"
//#include "simple_values.h"
#include "data_struct.h"
//#include "cache_unit.h"
typedef uint32_t date_t;
"""

template_head = """
  char filename[200];
  sprintf(filename, "%s/{}.tsv", DATA_DIR);
  std::ifstream fp(filename);
  string content;
  string header;
  int i = 0;
  getline(fp, header);
  while (getline(fp, content, '\\t')) {{
    {}
    i = 0;
    while (i < {} ) {{
"""

#tablename repeated for 3 times
def fill_template_head(tablename, init_code, max_i):
  return template_head.format(tablename, init_code, max_i)

template_end = """
      i += 1;
      if (i < {}) {{
          getline(fp, content, '\\t');
      }}else if (i == {}) {{
          getline(fp, content);
      }}
    }}
    {}
  }}
  fp.close();
}}
"""
def fill_template_end(sz, some_code):
  return template_end.format(sz, sz, some_code)

template_mid2 = """
      if (i == 0) {{ //id
      }} else if (i == 1) {{ //{}_id
          {}_id = str_to_int(content);
      }} else if (i == 2) {{ //{}_id
          {}_id =  str_to_int(content);
      }}
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
