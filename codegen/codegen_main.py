import sys
sys.path.append('../')
from schema import *
from ds import *
from constants import *
from query import *
from codegen_helper import *


def cgen_for_main_test(main_body, ds_def=True, include_query=True):
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