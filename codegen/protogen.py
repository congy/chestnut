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

def get_query_result_type(query):
  if globalv.is_qr_type_proto():
    return '{}::PQuery{}Result'.format(get_db_name(), query.id)
  else:
    return 'Query{}Result'.format(query.id)

def generate_one_proto_for_query(query):
  s = 'message PQuery{}Result {{\n'.format(query.id)
  cnt = 1
  for v,aggr in query.aggrs:
    if v.is_temp:
      continue
    s += '  {} {} = {};\n'.format(proto_types[v.tipe], v.name, cnt)
    cnt += 1
  if query.return_var:
    #s += ''.join(['  ' + l + '\n' for l in generate_one_proto_for_query_helper(query).split('\n')])
    s += '  repeated P{} result = {};\n'.format(get_capitalized_name(query.table.name), cnt)
  s += '}\n'
  return s
  
def generate_one_proto_for_query_helper(query, upper_query=None):
  s = ""
  table = query.table
  main_t = get_main_table(query.table)
  if upper_query:
    s += 'message P{}In{} {{\n'.format(get_capitalized_name(table.name), \
          get_capitalized_name(get_main_table(upper_query.table).name))
  else:
    s += 'message P{} {{\n'.format(get_capitalized_name(query.table.name))
  cnt = 1
  for f in table.get_fields():
    s += "  {} {} = {};\n".format(proto_types[f.tipe], f.name, cnt)
    cnt += 1
  names = []
  for k,q in query.includes.items():
    for v,f in q.aggrs:
      if v.is_temp == False and v.name not in names:
        names.append(v.name)
        s += "  {} {} = {};\n".format(proto_types[v.tipe], v.name, cnt)
        cnt += 1
  for k,q in query.includes.items():
    repeated = (k.table.has_one_or_many_field(k.field_name) == 0)
    nested = generate_one_proto_for_query_helper(q, query)
    s += ''.join(['  ' + l + '\n' for l in nested.split('\n')])
    s += "  {}P{}In{} {} = {};\n".format('repeated ' if repeated else '', \
            get_capitalized_name(k.field_name), get_capitalized_name(k.table.name), k.field_name, cnt)
    cnt += 1
  return s


def generate_structure_for_query_result(query):
  s = 'struct Query{}Result {{\n'.format(query.id)
  cnt = 1
  for v,aggr in query.aggrs:
    if v.is_temp:
      continue
    s += '  {} {}_{};\n'.format(get_cpp_type(v.tipe), v.name, cnt)
    s += '  inline void set_{}({} v_) {{ {}_{} = v_; }}\n'.format(v.name, get_cpp_type(v.tipe), v.name, cnt)
    s += '  inline {} {}() const {{ return {}_{};\n }}\n'.format(get_cpp_type(v.tipe), v.name, v.name, cnt)
    cnt += 1
  s += ''.join(['  '+l+'\n' for l in generate_structure_for_query_result_helper(query).split('\n')])
  typename = 'P'+get_capitalized_name(query.table.name)
  s += '  std::vector<{}> result;\n'.format(typename)
  s += '  inline size_t size() { return result.size(); }\n'
  s += '  inline size_t result_size() { return result.size(); }\n'
  s += '  inline {}* add() {{ result.push_back({}()); return &result[result.size()-1]; }}\n'.format(typename, typename)
  s += '  inline void append({}& v_) {{ result.push_back(v_); }}\n'.format(typename)
  if query.order:
    s += '  inline void sort() { std::sort(result.begin(), result.end()); }\n'
  s += '};\n'
  return s

def generate_structure_for_query_result_helper(query, upper_query=None):
  s = ""
  table = query.table
  main_t = get_main_table(query.table)
  if upper_query:
    tipe = 'P{}In{}'.format(get_capitalized_name(table.name), \
          get_capitalized_name(get_main_table(upper_query.table).name))
  else:
    tipe = 'P{}'.format(get_capitalized_name(query.table.name))
  s += 'struct {} {{\n'.format(tipe)
  
  copy_str = []
  init_str = []
  cnt = 1
  for f in main_t.get_fields():
    s += "  {} {}_{};\n".format(get_cpp_type(f.tipe), f.name, cnt)
    if is_string(f):
      s += '  inline void set_{}(const char* v_) {{ {}_{} = v_; }}\n'.format(f.name, f.name, cnt)
    else:
      s += '  inline void set_{}({} v_) {{ {}_{} = v_; }}\n'.format(f.name, get_cpp_type(f.tipe), f.name, cnt)
    s += '  inline {} {}() const {{ return {}_{}; }}\n'.format(get_cpp_type(f.tipe), f.name, f.name, cnt)
    copy_str.append('  {}_{} = other.{}_{};'.format(f.name, cnt, f.name, cnt))
    init_str.append('  {}_{} = 0;\n'.format(f.name, cnt))
    cnt += 1
  names = []
  for k,q in query.includes.items():
    for v,f in q.aggrs:
      if v.is_temp == False and v.name not in names:
        names.append(v.name)
        s += "  {} {}_{};\n".format(get_cpp_type(v.tipe), v.name, cnt)
        s += '  inline void set_{}({} v_) {{ {}_{} = v_; }}\n'.format(v.name, get_cpp_type(v.tipe), v.name, cnt)
        s += '  inline {} {}() const {{ return {}_{};\n }}\n'.format(get_cpp_type(v.tipe), v.name, v.name, cnt)
        copy_str.append('  {}_{} = other.{}_{};'.format(v.name, cnt, v.name, cnt))
        init_str.append('  {}_{} = 0;\n'.format(v.name, cnt))
        cnt += 1
  if query.order:
    s += '  inline bool operator< (const {}& other) const {{ return '.format(tipe)
    cmp_expr = '(this->{}() < other.{}())'.format(query.order[0].field_name, query.order[0].field_name)
    cmp_accu = 'this->{}() == other.{}()'.format(query.order[0].field_name, query.order[0].field_name)
    for o in query.order[1:]:
      cmp_expr += ' || ({} && this->{}() < other.{}())'.format(cmp_accu, o.field_name, o.field_name)
      cmp_accu += '&& this->{}() == other.{}()'.format(o.field_name, o.field_name)
    s += '{}; }}\n'.format(cmp_expr)

  for k,q in query.includes.items():
    repeated = (k.table.has_one_or_many_field(k.field_name) == 0)
    nested = generate_structure_for_query_result_helper(q, query)
    s += ''.join(['  ' + l + '\n' for l in nested.split('\n')])
    typename = 'P{}In{}'.format(get_capitalized_name(k.field_name), get_capitalized_name(k.table.name))
    if repeated:
      s += '  std::vector<{}> {}_{};\n'.format(typename, k.field_name, cnt)
      s += '  inline size_t {}_size() {{ return {}_{}.size(); }}\n'.format(k.field_name, k.field_name, cnt)
      s += '  inline const {} {}(size_t index) const {{ return {}_{}[index]; }}\n'.format(typename, k.field_name, k.field_name, cnt)
      s += '  inline {}* add_{}() {{ {}_{}.push_back({}()); return &{}_{}[{}_{}.size()-1]; }}\n'.format(\
              typename, k.field_name, k.field_name, cnt, typename, k.field_name, cnt, k.field_name, cnt)
      s += '  inline void append_{}({}& v_) {{ {}_{}.push_back(v_); }}\n'.format(k.field_name, typename, k.field_name, cnt)
      copy_str.append('  for (auto x_{}=other.{}_{}.begin(); x_{}!=other.{}_{}.end(); x_{}++) {{ {}_{}.push_back(*x_{}); }}'.format(\
              k.field_name, k.field_name, cnt, k.field_name, k.field_name, cnt, k.field_name, k.field_name, cnt, k.field_name,))
      if q.order:
        s += '  inline void sort_{}() {{ std::sort({}_{}.begin(), {}_{}.end()); }}\n'.format(k.field_name, k.field_name, cnt, k.field_name, cnt)
    else:
      s += '  {} {}_{};\n'.format(typename, k.field_name, cnt)
      s += '  inline {}* mutable_{}() {{ return &{}_{}; }}\n'.format(typename, k.field_name, k.field_name, cnt)
      s += '  inline const {}& {}() const {{ return {}_{}; }}\n'.format(typename, k.field_name, k.field_name, cnt)
      copy_str.append('  {}_{} = other.{}_{};\n'.format(k.field_name, cnt, k.field_name, cnt))
    cnt += 1
  s += '  {} (const {}& other) {{ {} }}\n'.format(tipe, tipe, '\n'.join(copy_str))
  s += '  {} () {{}}\n'.format(tipe)
  s += '};\n'
  return s
