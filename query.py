from pred import *
from pred_helper import *
from expr import *
from schema import *
from util import *
from constants import *
from cost import *
from pred_cost import *
from ds import *
import datetime
import globalv

query_cnt = 0
group_cnt = 0

class ReadQuery(object):
  def __init__(self, table):
    global query_cnt
    query_cnt += 1
    self.id = query_cnt
    self.table = table
    self.return_var = EnvCollectionVariable("result_{}".format(self.table.name), self.table, False)
    self.pred = None
    self.includes = {} 
    #key: field, value: ReadQuery
    self.order = None
    self.limit = 0
    self.aggrs = [] #(variable, aggr function) pair
    self.projections = []
    self.assigned_param_values = {}
    self.upper_query = None
  def __str__(self):
    s = 'Query {} on {} (return {}): '.format(self.id, self.table.get_full_type(), self.return_var)
    s += str(self.pred)
    s += '\n'
    if self.order:
      s += ' order: {}\n'.format(','.join([str(o) for o in self.order]))
    for k,v in self.aggrs:
      s += ' aggr: {}->({}), '.format(k.name, v)
    for k,v in self.includes.items():
      include_s = str(v)
      s += '\n'.join(['  '+l for l in include_s.split('\n')])
    return s
  
  def to_ds(self, upper=None):
  
    object = MemObject(self.table)
    object.add_fields([f for f in self.projections])
    for field,nested_query in self.includes.items():
      object.add_nested_object(nested_query.to_ds(upper=self))
   
    # TODO: handle aggregation 
    value = IndexValue(OBJECT, value=object)
    pred = replace_param_with_const(self.pred) if self.pred else None
    if self.pred is None:
      r = ObjBasicArray(self.table, value, upper)
    elif self.order is None:
      r = ObjArray(self.table, pred, value, upper)
    else:
      keys = [] if self.order is None else [KeyPath(o) for o in self.order]
      r = ObjSortedArray(self.table, IndexKeys(keys, keys), pred, value, upper)
    return r

  def project(self, fields):
    if type(fields) is str and fields == '*':
      self.projections = clean_lst([None if f.is_temp else QueryField(f.name, get_main_table(self.table)) \
        for f in get_main_table(self.table).get_fields()])
      return
    for f in fields:
      f.complete_field(get_main_table(self.table))
      self.projections.append(f)
  def has_order(self):
    return self.order
  def pfilter(self, pred):
    self.pred = ConnectOp(self.pred, AND, pred) if self.pred else pred
    self.pred.complete_field(get_main_table(self.table))
  def aggr(self, aggr_func, aggr_name):
    aggr_func.complete_field(get_main_table(self.table))
    tipe = aggr_func.get_type()
    for f in self.table.get_fields():
      assert(aggr_name != f.name)
    newv = EnvAtomicVariable('{}'.format(aggr_name), tipe, is_temp=False)
    if isinstance(self.table, NestedTable):
      new_field = Field(aggr_name, aggr_func.get_type(), is_temp=True)
      get_main_table(self.table.upper_table).add_field(new_field)
    self.aggrs.append((newv, aggr_func))
  def finclude(self, field, pfilter=None, projection='*'):
    field.complete_field(get_main_table(self.table))
    nested_table = self.table.get_nested_table_by_name(field.field_name)
    q = ReadQuery(nested_table)
    q.upper_query = self
    q.project(projection)
    if self.return_var:
      q.return_var.set_upper_var(self.return_var)
    if pfilter:
      q.pfilter(pfilter)
    self.includes[field] = q
  def get_include(self, field):
    for k,v in self.includes.items():
      if field.field_name == k.field_name:
        return v
    assert(False)
    return None
  def orderby(self, order, limit=0, ascending=True):
    self.order = order if type(order) is list else [order]
    for o in self.order:
      o.complete_field(get_main_table(self.table))
    self.limit = limit
    self.return_var.order = order
    self.return_var.limit = limit
    self.return_var.ascending = ascending
  def return_limit(self, limit):
    self.return_var.limit = limit
  def complete(self):
    # if nothing gets projected, then return only aggr
    if len(self.projections) == 0:
      if len(self.aggrs) > 0:
        self.return_var = None
      else:
        self.project('*')
    # handle avg aggregation
    contain_avg = False
    count_var = None
    for v,f in self.aggrs:
      contain_avg = True if f.op == AVG else contain_avg
      count_var = v if f.op == COUNT else count_var
    if contain_avg and not count_var:
      newv = EnvAtomicVariable('count', "uint", is_temp=True)
      self.aggrs.append((newv, UnaryExpr(COUNT, '')))
      count_var = newv
    for v,f in self.aggrs:
      if f.op == AVG:
        newv = EnvAtomicVariable('sum_{}'.format(v.name), get_sum_type(v.tipe), is_temp=True)
        self.aggrs.append((newv, UnaryExpr(SUM, f.operand)))
        f.sum_var = newv
        f.count_var = count_var
    # compute return result size
    if self.return_var:
      self.return_var.sz = get_query_result_sz(self.table, self.pred)
    for k,v in self.includes.items():
      v.complete()
  def get_aggr_var_name(self, var):
    return 'q{}_{}'.format(self.id, var.name)
  def get_aggr_var_prefix(self):
    return 'q{}_'.format(self.id)
  def get_all_params(self):
    r = []
    if self.pred:
      r = r + self.pred.get_all_params()
    for k,v in self.includes.items():
      r = r + v.get_all_params()
    #new_r = clean_lst([r1 if not any([r1==x for x in r]) else None for r1 in r])
    return r
  def get_param_value_pair(self, upper_pairs=None):
    if upper_pairs is not None:
      pairs = upper_pairs
    else:
      pairs = {}
    get_param_value_pair_by_pred(self.pred, pairs, self.assigned_param_values)
    for k,v in self.includes.items():
      pairs = map_union(pairs, v.get_param_value_pair(pairs))
    return pairs
  def groupby(self, fields, Ngroups=0):
    # only support top level groupby
    assert(not isinstance(self.table, NestedTable))
    global group_cnt
    group_cnt += 1
    # compute grouped (result) size
    if Ngroups == 0:
      Ngroups = 1
      for f in fields:
        Ngroups = Ngroups * get_query_field(f).field_class.get_number_of_possible_values()
    table = Table('{}_group{}'.format(self.table.name, group_cnt), Ngroups, is_temp=True)
    for f in fields:
      f.complete_field(get_main_table(self.table))
      temp_f = get_query_field(f).field_class
      newf = temp_f.fork()
      newf.name = get_full_assoc_field_name(f)
      newf.table = table
      newf.dependent_qf = f
      table.add_field(newf)
    field_name = '{}s'.format(self.table.name.lower())
    new_assoc = get_new_assoc("{}_group_assoc".format(self.table.name), "one_to_many", table, self.table, field_name, table.name, 0, 0)
    globalv.tables.append(table)
    globalv.associations.append(new_assoc)
    f = QueryField(field_name, table)
    new_nested_table = table.get_nested_table_by_name(field_name)
    self.table = new_nested_table
    read_query = ReadQuery(table)
    read_query.includes[f] = self
    self.upper_query = read_query
    return read_query
  
def get_param_value_pair_by_pred(pred, r, assigned_values={}):
  if isinstance(pred, ConnectOp):
    p_lh = get_param_value_pair_by_pred(pred.lh, r, assigned_values)
    p_rh = get_param_value_pair_by_pred(pred.rh, r, assigned_values)
  elif isinstance(pred, SetOp):
    get_param_value_pair_by_pred(pred.rh, r, assigned_values)
  elif isinstance(pred, UnaryOp):
    get_param_value_pair_by_pred(pred.operand, r, assigned_values)
  elif isinstance(pred, BinOp):
    pairs = []
    actual_values = []
    if isinstance(pred.rh, MultiParam):
      for p in pred.rh.get_all_params():
        pairs.append((pred.lh, p))
    elif isinstance(pred.rh, Parameter):
      pairs.append((pred.lh, pred.rh))
    for lh,rh in pairs:
      if rh.dependence == None:
        if any([assigned_p==rh for assigned_p,value in assigned_values.items()]):
          r[rh] = filter(lambda x: x is not None, [value if assigned_p==rh else None for assigned_p,value in assigned_values.items()])[0]
        else:
          r[rh] = get_query_field(lh).field_class.generate_value()
    for lh,rh in pairs:
      if rh.dependence:
        dep_var = None
        for k,v in r.items():
          if k.symbol == rh.dependence[0].symbol:
            dep_var = v
        assert(dep_var)
        if get_query_field(lh).field_class.tipe == 'date':
          r[rh] = str(datetime.datetime.strptime(dep_var, \
              "%Y-%m-%d %H:%M:%S")+datetime.timedelta(days=rh.dependence[1]))
        else:
          r[rh] = '({}+({}))'.format(dep_var, rh.dependence[1])

class WriteQuery(object):
  def __init__(self, op=INSERT, new_id=True):
    global query_cnt
    self.op = op
    if new_id:
      self.id = query_cnt
      query_cnt += 1
    self.assigned_param_values = {}
  def find_assigned_value(self, param):
    for k,v in self.assigned_param_values.items():
      if k == param:
        return v
    return None
  def set_assigned_value(self, param, value):
    self.assigned_param_values[param] = value
  
class ChangeAssociation(WriteQuery):
  def __init__(self, qf, op, paramA, paramB, new_id=True):
    self.tableA = qf.table
    self.tableB = qf.field_class
    self.qf = qf
    self.op = op
    self.paramA = paramA
    self.paramB = paramB
    super(ChangeAssociation, self).__init__(op, new_id)
  def get_reverse_direction(self):
    assoc = self.tableA.get_assoc_by_name(self.qf.field_name)
    reverse_qf_name = assoc.lft_field_name if assoc.lft == self.tableB else assoc.rgt_field_name
    reverse_qf = QueryField(reverse_qf_name)
    reverse_qf.complete_field(self.tableB)
    wq = ChangeAssociation(reverse_qf, self.op, self.paramB, self.paramA, new_id=False)
    wq.id = self.id
    return wq
  def get_all_params(self):
    return [self.paramA, self.paramB]
  def get_param_value_pair(self):
    fA = self.tableA.get_field_by_name('id')
    fB = self.tableB.get_field_by_name('id')
    assigned_valueA = self.find_assigned_value(self.paramA)
    assigned_valueB = self.find_assigned_value(self.paramB)
    return {self.paramA:fA.generate_value() if assigned_valueA is None else assigned_valueA, \
            self.paramB:fB.generate_value() if assigned_valueB is None else assigned_valueB} 
  def __str__(self):
    op = 'DELETE' if self.op == DELETE else 'INSERT'
    return '{} Assoc {}: {}({}) - {}({})'.format(op, self.qf, self.tableA.name, self.paramA, self.tableB.name, self.paramB)
    

class AddObject(WriteQuery):
  def __init__(self, table, field_values={}, new_id=True):
    self.table = table
    self.field_values = {}
    for k,v in field_values.items():
      k.complete_field(self.table)
      self.field_values[k] = v
      v.tipe = k.get_type()
    super(AddObject, self).__init__(INSERT, new_id)
  def set_field(self, f, v):
    self.field_values[f] = v
    v.tipe = f.get_type()
  def get_all_params(self):
    r = []
    for k,v in self.field_values.items():
      if isinstance(v, Parameter):
        r.append(v)
    return r
  def get_param_value_pair(self):
    #pairs = {self.param:self.table.get_field_by_name('id').generate_value()}
    pairs = {}
    for k,v in self.field_values.items():
      if isinstance(v, Parameter):
        assigned_value = self.find_assigned_value(v)
        pairs[v] = k.field_class.generate_value() if assigned_value is None else assigned_value
    return pairs
  def __str__(self):
    return 'Insert obj to {} ({})'.format(self.table.name, ','.join(['{}:{}'.format(k,v) for k,v in self.field_values.items()]))


class RemoveObject(WriteQuery):
  def __init__(self, table, param):
    self.table = table
    self.param = param
    super(AddObject, self).__init__(DELETE)
  def set_field(self, f, v):
    self.field_values[f] = v
  def get_all_params(self):
    return [self.param]
  def get_param_value_pair(self):
    assigned_value = self.find_assigned_value(self.param)
    return {self.param:self.table.get_field_by_name('id').generate_value() if assigned_value is None else assigned_value}
  def __str__(self):
    return 'Remove obj to {} ({})'.format(self.table.name, self.param)

class UpdateObject(WriteQuery):
  def __init__(self, table, param, updated_fields={}):
    self.table = table
    self.updated_fields = {}
    for k,v in updated_fields.items():
      k.complete_field(self.table)
      self.updated_fields[k] = v
      v.tipe = k.get_type()
    self.param = param
    super(UpdateObject, self).__init__(UPDATE)
  def set_field(self, k, v):
    k.complete_field(self.table)
    self.updated_fields[k] = v
    v.tipe = k.get_type()
  def get_all_params(self):
    r = [self.param]
    for k,v in self.updated_fields.items():
      if isinstance(v, Parameter):
        r.append(v)
    return r
  def get_param_value_pair(self):
    assigned_value = self.find_assigned_value(self.param)
    pairs = {self.param:self.table.get_field_by_name('id').generate_value() if assigned_value is None else assigned_value}
    for k,v in self.updated_fields.items():
      if isinstance(v, Parameter):
        assigned_value = self.find_assigned_value(v)
        pairs[v] = k.field_class.generate_value() if assigned_value is None else assigned_value
    return pairs
  def __str__(self):
    update_s = []
    for k,v in self.updated_fields.items():
      update_s.append('{}={}'.format(k.field_name, v))
    return 'Update obj {} ({}): {}'.format(self.table.name, self.param, ','.join(update_s))
  

def get_all_records(table):
  return ReadQuery(table)

def replace_param_with_const(pred):
  if isinstance(pred, ConnectOp):
    p_lh = replace_param_with_const(pred.lh)
    p_rh = replace_param_with_const(pred.rh)
    return ConnectOp(p_lh, pred.op, p_rh)
  elif isinstance(pred, SetOp):
    return SetOp(pred.lh, pred.op, replace_param_with_const(pred.rh))
  elif isinstance(pred, UnaryOp):
    return UnaryOp(replace_param_with_const(pred.op))
  elif isinstance(pred, BinOp):
    qf = get_query_field(pred.lh)
    if isinstance(pred.rh, MultiParam):
      new_rh = MultiParam([AtomValue(qf.field_class.generate_value()) for i in range(len(pred.rh.params))])
    elif isinstance(pred.rh, Parameter):
      new_rh = AtomValue(qf.field_class.generate_value())
    else:
      new_rh = pred.rh
    return BinOp(pred.lh, pred.op, new_rh)
