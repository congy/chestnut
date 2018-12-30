import os
import sys
sys.path.append('../')
from schema import *
from constants import *
from util import *
from query import *
import globalv

def generate_proto_files(path, tables, associations, read_queries=[], write_queries=[]):
  db_name = get_db_name()
  fp = open("{}/proto_{}.proto".format(path, db_name), 'w')
  fp.write("syntax = \"proto3\";\n\n")
  fp.write("package {};\n\n".format(db_name))
  for t in tables:
    fp.write(generate_one_proto(t, None, [t], 1, read_queries))
    fp.write("\n\n")
  # for q in queries:
  #   fp.write(generate_one_proto_for_query(q))
  #   fp.write("\n\n")

  for q in read_queries:
    fp.write(generate_one_proto_for_query(q))
    fp.write('\n\n')
  
  s = ''
  for t in tables:
    s += 'message P{}List {{\n'.format(get_capitalized_name(t.name))
    s += '  repeated P{} {} = 1;\n'.format(get_capitalized_name(t.name), t.name)
    s += '}\n'
  fp.write(s)
  fp.write('\n\n')

  s = 'message QueryParam {\n'
  cnt = 2
  s += '  uint32 query_id = 1;\n'
  for i,q in enumerate(read_queries):
    for j,p in enumerate(q.get_all_params()):
      s += '  {} rq_{}_{} = {};\n'.format(get_param_proto_type(p.tipe), i, p.symbol, cnt)
      cnt += 1
  for i,q in enumerate(write_queries):
    for j,p in enumerate(q.get_all_params()):
      s += '  {} wq_{}_{} = {};\n'.format(get_param_proto_type(p.tipe), i, p.symbol, cnt)
      cnt += 1
  s += '}\n'
  fp.write(s)
  fp.write('\n\n')
  fp.close()

  os.system("protoc -I={}/ --cpp_out={}/ {}/proto_{}.proto".format(path, path, path, db_name))
  os.system("protoc --proto_path={}/ --ruby_out={}/ruby/ {}/proto_{}.proto".format(path, path, path, db_name))


def generate_one_proto(t, upper_t, tables, level, queries=[]):
  s=""
  if upper_t:
    s += "message P{}In{} {{\n".format(get_capitalized_name(t.name), get_capitalized_name(upper_t.name))
    t = t.related_table
  else:
    s += "message P{} {{\n".format(get_capitalized_name(t.name))
  cnt = 1
  for f in t.get_fields():
    s += "  {} {} = {};\n".format(get_proto_type(f.tipe), f.name, cnt)
    cnt += 1
  #s += "  uint32 position = {};\n".format(cnt)
  names = []
  if globalv.is_qr_type_proto():
    for q1 in queries:
      if get_main_table(q1.table) == t:
        for k,q in q1.includes.items():
          for v,f in q.aggrs:
            if v.is_temp == False and v.name not in names:
              names.append(v.name)
              s += "  {} {} = {};\n".format(proto_types[v.tipe], v.name, cnt)
              cnt += 1
  if level <= MAX_NESTED_LEVEL:
    for next_t in t.get_nested_tables():
      exist = False
      repeated = (t.has_one_or_many_field(next_t.name) == 0)
      new_tables = []
      for t1 in tables:
        new_tables.append(t1)
        if t1 == get_main_table(next_t):
          exist = True
      if exist:
        continue
      next_queries = []
      for q in queries:
        if get_main_table(q.table) == t:
          for k,v in q.includes.items():
            if k.field_name == next_t.name:
              next_queries.append(v)
      new_tables.append(get_main_table(next_t))
      nested = generate_one_proto(next_t, t, new_tables, level+1, next_queries)
      nested = ''.join(['  '+s1+'\n' for s1 in nested.split('\n')])
      s += nested
      s += "  {}P{}In{} {} = {};\n".format('repeated ' if repeated else '', \
            get_capitalized_name(next_t.name), get_capitalized_name(t.name), next_t.name, cnt)
      cnt += 1
  s += "}\n"
  return s

def generate_one_proto_for_query(query):
  s = 'message PQuery{}Result {{\n'.format(query.id)
  cnt = 1
  for v,aggr in query.aggrs:
    if v.is_temp:
      continue
    s += '  {} {} = {};\n'.format(proto_types[v.tipe], v.name, cnt)
    cnt += 1
  if query.return_var:
    s += '  repeated P{} {} = {};\n'.format(get_capitalized_name(query.table.name), query.table.name, cnt)
  s += '}\n'
  return s
  