import sys
sys.path.append('../')
from ds import *
from planIR import *
from query import *
from codegen_helper import *
from codegen_state import *
import globalv

def cgen_ruby_client(read_metas, write_metas):
  ruby_t_f = {'1':'true', 1:'true', '0':'false', 0:'false'}
  s = ''
  path = '{}/{}/ruby/'.format(get_cxx_file_dir(), get_db_name())
  os.system('mkdir {}'.format(path))
  s += 'require \"./proto_{}_pb.rb\"\n'.format(get_db_name())
  s += 'require \"ffi-rzmq.rb\"\n'
  s += 'def time_diff_milli(start, finish)\n'
  s += '  (finish - start) * 1000.0\n'
  s += 'end\n\n'

  qcnt = 0 
  for i,read_meta in enumerate(read_metas): 
    query = read_meta.read_query
    s += 'def run_rq_{}\n'.format(i)
    param_values = query.get_param_value_pair()
    param_str = ', '.join([':rq_{}_{} => {}'.format(i, p.symbol, \
            '\"{}\"'.format(param_values[p]) if is_string_type(p.tipe) or is_date_type(p.tipe) else (ruby_t_f[param_values[p]] if is_bool_type(p.tipe) else param_values[p])) \
            for p in query.get_all_params()])
    s += '  param = {}::QueryParam.new(:query_id => {}, {})\n'.format(get_capitalized_name(get_db_name()), qcnt, param_str)
    s += '  serialized_param = {}::QueryParam.encode(param)\n'.format(get_capitalized_name(get_db_name()))
    s += ruby_template_begin
    s += '  data = {}::PQuery{}Result.decode(data)\n'.format(get_capitalized_name(get_db_name()), i)
    s += '  puts \"query {} time elapsed = #{{time_diff_milli(t1, t2)}} ms\"\n'.format(i)
    # print query result
    s += insert_indent(cgen_ruby_client_print(query, 'data'))
    s += ruby_template_end
    qcnt += 1
    s += 'end\n'

  s += 'def run_queries\n'
  for i,read_meta in enumerate(read_metas): 
    s += '  run_rq_{}\n'.format(i)
  for i,write_meta in enumerate(write_metas): 
    s += '  run_wq_{}\n'.format(i)
  s += 'end\n'

  s += 'run_queries\n'
  fp = open('{}/ruby_test.rb'.format(path, get_db_name()), 'w')
  fp.write(s)


def cgen_ruby_client_print(query, result_var):
  s = ''
  s += 'puts \"aggrs:\"\n'
  for v,f in query.aggrs:
    s += 'puts \"{} = #{{{}.{}}}\"\n'.format(v.name, result_var, v.name)
  if query.return_var:
    s += 'puts \"size = #{{{}.{}.length}}\"\n'.format(result_var, 'result')
    s += 'cnt_0 = 0\n'
    s += '{}.{}.each do |{}|\n'.format(result_var, 'result', 'x')
    s += 'cnt_0 = cnt_0 + 1\n'
    s += 'if cnt_0 > 20 then\n'
    s += '  break\n'
    s += 'end\n'
    s += insert_indent(cgen_ruby_client_print_helper(query, 'x'))
    s += 'end\n' 
  return s

def cgen_ruby_client_print_helper(query, element_var, level=0):
  s = ''
  indent = ''.join(['\t' for i in range(0, level)])
  for k,q in query.includes.items():
    for v,f in q.aggrs:
      if v.is_temp == False:
        s += 'puts \"{}{} = #{{{}.{}}}\"\n'.format(indent, v.name, element_var, v.name)
  for f in query.table.get_fields():
    s += 'puts \"{}{} = #{{{}.{}}}\"\n'.format(indent, f.name, element_var, f.name)
  for k,v in query.includes.items():
    if k.table.has_one_or_many_field(k.field_name):
      s += "if {}.{} != nil\n".format(element_var, k.field_name)
      s += insert_indent(cgen_ruby_client_print_helper(v, '{}.{}'.format(element_var, k.field_name), level+1))
      s += "end\n"
    else:
      s += 'puts \"{}sz = #{{{}.{}.length}}\"\n'.format(indent, element_var, k.field_name)
      next_element_var = 'element_{}'.format(k.field_name)
      s += 'cnt_{} = 0\n'.format(level+1)
      s += '{}.{}.each do |{}|\n'.format(element_var, k.field_name, next_element_var)
      s += '  cnt_{} = cnt_{} + 1\n'.format(level+1, level+1)
      s += '  if cnt_{} > 20 then\n'.format(level+1)
      s += '    break\n'
      s += '  end\n'
      s += insert_indent(cgen_ruby_client_print_helper(v, next_element_var, level+1))
      s += 'end\n'
  return s
   
def cgen_nonproto_query_result(query, qid):
  s = 'struct Query{}Result {{\n'.format(qid)
  nexts, next_uppers = cgen_nonproto_query_result_element(query, upper_query=None, repeated=True)
  s += insert_indent(nexts)
  s += next_uppers
  s += '};\n'
  return s

def cgen_nonproto_query_result_element(query, upper_query=None, repeated=True):
  if upper_query:
    typename = 'P{}In{}'.format(get_capitalized_name(query.table.name), \
          get_capitalized_name(get_main_table(upper_query.table).name))
  else:
    typename = 'P{}'.format(get_capitalized_name(query.table.name))
  fmap = {}
  cnt = 0
  upper_s = ''
  for v,aggr in query.aggrs:
    if v.is_temp:
      continue
    upper_s += '  {} {}_{};\n'.format(get_cpp_type(v.get_type()), v.name, cnt)
    fmap[v] = cnt
    cnt += 1
  for v,aggr in query.aggrs:
    if v.is_temp:
      continue
    upper_s += '  void set_{}({} fv_) {{ {}_{} = fv_; }}\n'.format(v.name, get_cpp_type(v.get_type()), v.name, fmap[v])
    upper_s += '  {} {}() {{ return {}_{}; }}\n'.format(get_cpp_type(v.get_type()), v.name, v.name, fmap[v])
  
  s = ''
  if query.return_var:
    s += 'struct {} {{\n'.format(typename)
    s += '  {}() {{}}\n'.format(typename)
    projections = [f for f in query.projections]
    insert_no_duplicate(projections, QueryField('id', get_main_table(query.table)))
    projections = clean_lst([None if f.field_class.is_temp else f for f in projections])
    if query.order:
      for o in query.order:
        insert_no_duplicate(projections, o)
    for f in projections:
      s += '  {} {}_{};\n'.format(get_cpp_type(f.get_type()), f.field_name, cnt)
      fmap[f] = cnt
      cnt += 1
    for f in projections:
      s += '  inline void set_{}({} fv_) {{ {}_{} = fv_; }}\n'.format(f.field_name, get_cpp_type(f.get_type()), f.field_name, fmap[f])
      s += '  inline {} {}() const {{ return {}_{}; }}\n'.format(get_cpp_type(f.get_type()), f.field_name, f.field_name, fmap[f])
      if is_string(f.field_class):
        s += '  inline void set_{}(const char* v_) {{ {}_{} = v_; }}\n'.format(f.field_name, f.field_name, fmap[f])
    
    rs_var = query.table.name
    retv = query.return_var
    if repeated:
      upper_s += '  std::vector<{}> {};\n'.format(typename, rs_var)
      upper_s += '  size_t {}_size() {{ return {}.size(); }}\n'.format(retv.tipe.name, rs_var)
      upper_s += '  {}* add_{}() {{ {}.push_back({}()); return &{}.back(); }}\n'.format(\
              typename, retv.tipe.name, rs_var, typename, rs_var)
      #upper_s += '  {}& get_{}(size_t ix) const {{ return {}[ix]; }}\n'.format(typename, retv.tipe.name, rs_var)
    else:
      upper_s += '  {} {};\n'.format(typename, rs_var)
      upper_s += '  {}* mutable_{}() {{ return &{}; }};\n'.format(typename, retv.tipe.name, rs_var)
      #upper_s += '  {} get_{}() const {{ return {}; }}\n'.format(typename, retv.tipe.name, rs_var)
      
    if query.order:
      s += '  inline bool operator< (const {}& other) const {{ return '.format(typename)
      cmp_expr = '(this->{}() < other.{}())'.format(query.order[0].field_name, query.order[0].field_name)
      cmp_accu = 'this->{}() == other.{}()'.format(query.order[0].field_name, query.order[0].field_name)
      for o in query.order[1:]:
        cmp_expr += ' || ({} && this->{}() < other.{}())'.format(cmp_accu, o.field_name, o.field_name)
        cmp_accu += '&& this->{}() == other.{}()'.format(o.field_name, o.field_name)
      s += '{}; }}\n'.format(cmp_expr)
      upper_s += '  inline void sort() {{ std::sort({}.begin(), {}.end()); }}\n'.format(rs_var, rs_var)
    
    for k,q in query.includes.items():
      repeated = (k.table.has_one_or_many_field(k.field_name) == 0)
      inner_s, inner_upper_s = cgen_nonproto_query_result_element(q, upper_query=query, repeated=repeated)
      s += insert_indent(inner_s)
      s += inner_upper_s
    s += '};\n'

  return s, upper_s



        
