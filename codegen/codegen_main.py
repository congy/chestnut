import sys
sys.path.append('../')
from schema import *
from ds import *
from constants import *
from query import *
from .codegen_helper import *
from .codegen_template import *

def cgen_for_main(main_body, ds_def=True, include_query=True):
  db_name = get_db_name()
  if ds_def:
    s = "#include \"{}.h\"\n".format(db_name)
  if include_query:
    s += "#include \"{}_query.h\"\n".format(db_name)
  s += "#include \"util.h\"\n"
  s += "#include \"proto_{}.pb.h\"\n".format(db_name)
  s += "#include <zmq.h>\n"
  s += "int main() {\n"
  s += insert_indent(main_body)
  s += ' return 0;\n'
  s += '}\n'
  return s

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


def cgen_for_query_in_main(read_queries, read_plan_ids):
  s = ''
  if globalv.is_qr_type_proto():
    s += server_init_template_begin
    readp_s = "{}::QueryParam qparam;\n".format(get_db_name())
    readp_s += "qparam.ParseFromString(buffer);\n"
    for i,read_query in enumerate(read_queries):
      readp_s += "if (qparam.query_id() == {}) {{\n".format(i)
      readp_s += "{} qresult;\n".format(cgen_query_result_type(i))
      param_strs = []
      for j,p in enumerate(read_query.get_all_params()):
        if is_date_type(p.tipe):
          param_strs.append('time_to_uint(qparam.q_{}_param_{}_{}())'.format(i, j, p.symbol))
        else:
          param_strs.append('qparam.q_{}_param_{}_{}()'.format(i, j, p.symbol))
      param_strs.append('qresult')
      readp_s += '  query_{}_plan_{}({});\n'.format(i, read_plan_ids[i], ','.join(param_strs))
      readp_s += '  qresult.SerializeToString(&output);\n'
      readp_s += "}\n"
    s += insert_indent(readp_s, 2)
    s += server_init_template_end
  else: # use customized qresult data structure
    read_after = []
    for i,query in enumerate(read_queries):
      params = query.get_all_params()
      param_values = query.get_param_value_pair()
      param_str = get_param_str_for_main(param_values, params)
      param_str += (', ' if len(params) > 0 else '')
      query_str = '   query_{}_plan_{}({}q_{}_result);\n'.format(i, read_plan_ids[i], param_str, i)
      s += '  {} q_{}_result;\n'.format(cgen_query_result_type(i), i)
      s += query_str
      read_after += query_str
  return s 


