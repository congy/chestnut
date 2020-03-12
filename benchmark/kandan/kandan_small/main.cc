#include "kandan_small.h"
#include "kandan_small_query.h"
#include "util.h"
#include "proto_kandan_small.pb.h"
#include <zmq.h>
int main() {
  read_data();

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
      kandan_small::QueryParam qparam;
      qparam.ParseFromString(buffer);
      if (qparam.query_id() == 0) {
      kandan_small::PQuery0Result qresult;
        query_0_plan_0(qparam.q_0_param_0_uid(),qresult);
        qresult.SerializeToString(&output);
      }


      //zmq_send (responder, output.c_str(), output.length()+1, 0);
      zmq_msg_t smsg;
      rc = zmq_msg_init_size (&smsg, output.length());
      assert (rc == 0);
      memcpy (zmq_msg_data (&smsg), output.c_str(), output.length());
      rc = zmq_msg_send (&smsg, responder, 0);
    }

 return 0;
}
