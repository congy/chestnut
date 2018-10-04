from util import *
from constants import *
from pred import *
from pred_helper import *
from pred_cost import *
import itertools

class IndexParam(object):
  def __init__(self):
    self.fields = []
    self.params = []
  def to_json(self):
    return [(self.fields[i].to_json(), self.params[i].to_json() if not value_is_basic_type(self.params[i]) else self.params[i]) for i in range(0, len(self.fields))]
  def add_param(self, f, p):
    self.fields.append(f)
    self.params.append(p)
  def __str__(self):
    return '({})'.format(','.join([str(p) for p in self.params]))
  def __eq__(self, other):
    return set_equal(self.fields, other.fields, lambda x, y: x.idx_pred_eq(y)) and set_equal(self.params, other.params, lambda x, y: x==y)
  def fork(self):
    new_i = IndexParam()
    new_i.fields = [i for i in self.fields]
    new_i.params = [i for i in self.params]
    return new_i
  def merge(self, other):
    for i,f in enumerate(other.fields):
      if not any([f1==f for f1 in self.fields]):
        self.fields.append(f)
        self.params.append(other.params[i])
    return self


class AggrResult(object):
  def __init__(self, aggrs=[], delta_exprs=[]):
    self.aggrs = aggrs #(var, aggr) pair
    self.delta_exprs = delta_exprs
  def to_json(self):
    return [(v.to_json(), f.to_json()) for a,f in self.aggrs]
  def __str__(self):
    return [(v.name, aggr.to_json()) for v, aggr in self.aggrs]
  def merge(self, other):
    self.aggrs += other.aggrs
    self.delta_exprs += other.delta_exprs
  def get_all_fields(self):
    r = []
    for v,aggr in self.aggrs:
      r = r + aggr.get_all_fields()
    return r
  def fork(self):
    return AggrResult(aggrs=[a for a in self.aggrs], delta_exprs=[a for a in self.delta_exprs])
  def __eq__(self, other):
    #return set_equal(self.aggrs, other.aggrs, eq_func=lambda x,y: x[0]==y[0] and x[1]==y[1])
    return True
  def __str__(self):
    return 'aggr({})'.format(','.join([aggr for v,aggr in self.aggrs]))

class MemObject(object):
  def __init__(self, table, fields=[]):
    self.table = table # Table or NestedTable or DenormalizedTable
    self.fields = fields
    self.nested_objects = [] # array of nested BasicArray / ObjSortedArray / ObjArray
  def get_all_fields(self):
    return self.fields
  def add_field(self, f):
    if not any([f==f1 for f1 in self.fields]):
      self.fields.append(f)
  def add_nested_object(self, obj):
    if not any([obj==o for o in self.nested_objects]):
      self.nested_objects.append(obj)
  def fork(self):
    newo = MemObject(self.table, [f for f in self.fields])
    newo.nested_objects = [o.fork() for o in self.nested_objects]
    return newo
  def __eq__(self, other):
    # TODO
    return True
  def __str__(self):
    if len(self.nested_objects) == 0:
      return 'memobj({})'.format(','.join([f.field_name for f in self.fields]))
    s = 'memobj({}), nested = {{'.format(','.join([f.field_name for f in self.fields]))
    for o in self.nested_objects:
      s += '\n'.join(['  '+l for l in str(o).split('\n')])
    s += '}\n'
    return s
  def to_json(self):
    return [f.field_name for f in self.fields]
  def compute_mem_cost(self, single_ele=True):
    field_sz = sum([f.get_sz() for f in self.fields])
    nested_sz = sum([o.compute_mem_cost(single_ele=True) for o in self.nested_objects])
    return cost_add(field_sz, nested_sz)
  def merge(self, other):
    for f in other.fields:
      self.add_field(f)
    for o in self.nested_objects:
      exist = False
      for o1 in other.nested_objects:
        if o == o1:
          o.merge(o1)
          exist = True
      if not exist:
        self.nested_objects.append(o1)
  def find_nested_obj_by_field(self, field):
    for o in self.nested_objects:
      if get_main_table(o.table.upper_table) == field.table and o.table.name == field.field_name:
        return o
    return None 

class IndexValue(object):
  # value: objtype / None / aggrs
  def __init__(self, value_type, value=None):
    # value type:
    # OBJECT
    # MAINPTR
    # AGGR
    self.value_type = value_type
    if value_type == AGGR:
      self.value = value.fork() if isinstance(value, AggrResult) else AggrResult(value) 
    elif value_type == OBJECT:
      self.value = value.fork() if isinstance(value, MemObject) else MemObject(value)
    else:
      self.value = None
  def to_json(self):
    if self.value_type == MAINPTR:
      return "mainptr"
    else:
      return self.value.to_json()
  def is_main_ptr(self):
    return self.value_type == MAINPTR
  def is_object(self):
    return self.value_type == OBJECT
  def is_aggr(self):
    return self.value_type == AGGR
  def __str__(self):
    if self.value_type == MAINPTR:
      return 'ptr'
    else:
      return str(self.value)
  def __eq__(self, other):
    return self.value_type == other.value_type
  def to_json(self):
    # TODO
    pass
  def fork(self):
    return IndexValue(self.value_type, self.value) 
  def add_field(self, f):
    assert(self.value_type == OBJECT)
    self.value.add_field(f)
  def add_nested_object(self, obj):
    self.value.nested_objects.append(obj)
  def get_object(self):
    return self.value
  def set_type(self, table):
    self.value.table = table

class IndexMeta(object):
  # common class members:
  # id, table, value
  def merge(self, other):
    if self.value.is_object():
      self.value.value.merge(other)

class IndexKeys(object):
  def __init__(self, keys, range_keys=[]):
    self.keys = keys
    self.range_keys = range_keys
  def __eq__(self, other):
    return set_equal(self.keys, other.keys) and list_equal(self.range_keys, other.range_keys)
  def contain_range_key(self):
    return len(self.range_keys) > 0
  def fork(self):
    return IndexKeys([k for k in self.keys], [k for k in self.range_keys])
  def __str__(self):
    return ','.join([str(k) for k in self.keys])


class IndexBase(IndexMeta):
  def __init__(self, table, keys, condition, value):
    self.id = 0 
    self.table = table #table ~ obj_type
    if isinstance(keys, IndexKeys):
      self.keys = keys.fork()
    else:
      keys_, range_keys_ = get_keys_by_pred(condition)
      assert(set_equal(keys_, keys))
      self.keys = IndexKeys(keys, range_keys_)
    self.condition = get_idx_condition(condition)
    self.value = value.fork() if isinstance(value, IndexValue) else IndexValue(value)
    if self.value.is_object():
      self.value.set_type(self.table)
  def to_json(self):
    tables = [self.table.name]
    cur_table = self.table
    if isinstance(cur_table, NestedTable):
      cur_table = cur_table.upper_table
      tables.insert(0, cur_table.name)
    keys = [k.to_json() for k in self.keys]
    condition = self.condition.to_json()
    value = self.value.to_json()
    return ("Index", {"id":self.id, "table":'.'.join([t for t in tables]), "keys":keys.to_json(), "condition":condition, "value":value})

  def is_range_key(self, key):
    return self.keys.contain_range_key()
  def get_idx_name(self):
    return 'dt_{}'.format(self.id)
  def get_key_type_name(self):
    if len(self.keys) > 0:
      return "{}_key_type".format(self.get_idx_name())
    else:
      return 'size_t'
  def get_value_type_name(self):
    if self.value.is_object():
      if isinstance(self.table, NestedTable):
        return '{}In{}{}'.format(get_capitalized_name(self.table.name),\
                        get_capitalized_name(get_main_table(self.table.upper_table).name), self.id)
      else:
        return get_capitalized_name(self.table.name)
    elif self.value.is_main_ptr():
      return 'ItemPointer'
    elif self.value.is_aggr():
      return 'AggrFor{}'.format(get_capitalized_name(self.table.name))
    else:
      assert(False)
  def get_relates(self):
    return (isinstance(self.table, NestedTable) and self.value.is_main_ptr())
  def __eq__(self, other):
    return type(self) == type(other) and self.table == other.table and self.keys == other.keys and self.value == other.value
  def compute_size(self):
    return IdxSizeUnit(self)
  def compute_single_size(self):
    return self.compute_size()

class ObjTreeIndex(IndexBase):
  def __init__(self, table, keys, condition=None, value=MAINPTR):
    super(ObjTreeIndex, self).__init__(table, keys, condition, value)
  def compute_mem_cost(self):
    temp = IdxSizeUnit(self)
    #self.mem_cost = CostOp(temp, COST_ADD, CostLogOp(temp))
    self.mem_cost = temp
    if isinstance(self.table, NestedTable):
      self.mem_cost = CostOp(self.mem_cost, COST_MUL, self.table.get_duplication_number())
    return self.mem_cost
  def __str__(self):
    return '[{}] treeindex : [table = {}, keys = ({}), cond = {}, value = {}]'.format(\
    self.id, self.table.get_full_type(), str(self.keys), \
    self.condition, self.value)
  def fork(self):
    return ObjTreeIndex(self.table, self.keys, self.condition, self.value) 

class ObjSortedArray(IndexBase):
  def __init__(self, table, keys, condition=None, value=OBJECT):
    assert(isinstance(table, NestedTable))
    super(ObjSortedArray, self).__init__(table, keys, condition, value)
  def compute_mem_cost(self):
    self.mem_cost = IdxSizeUnit(self)
    if isinstance(self.table, NestedTable):
      self.mem_cost = CostOp(self.mem_cost, COST_MUL, self.table.get_duplication_number())
    return self.mem_cost
  def __str__(self):
    return '[{}] sorted-array : [table = {}, keys = ({}), cond = {}, value = {}]'.format(\
    self.id, self.table.get_full_type(), \
    ','.join([str(k) for k in self.keys]), self.condition, self.value)
  def fork(self):
    return ObjSortedArray(self.table, self.keys, self.condition, self.value) 

  
class ObjArray(IndexBase):
  def __init__(self, table, condition=None, value=MAINPTR):
    super(ObjArray, self).__init__(table, [], condition, value)
  def compute_mem_cost(self):
    self.mem_cost = IdxSizeUnit(self)
    if isinstance(self.table, NestedTable):
      self.mem_cost = CostOp(self.mem_cost, COST_MUL, self.table.get_duplication_number())
    return self.mem_cost
  def __str__(self):
    return '[{}] array : [table = {}, cond = {}, value = {}]'.format(\
    self.id, self.table.get_full_type(), \
    self.condition, self.value)
  def fork(self):
    return ObjArray(self.table, self.condition, self.value) 


class ObjHashIndex(IndexBase):
  def __init__(self, table, keys, condition=None, value=MAINPTR):
    super(ObjHashIndex, self).__init__(table, keys, condition, value)
  def compute_mem_cost(self):
    temp = IdxSizeUnit(self)
    self.mem_cost = CostOp(temp, COST_MUL, 2)
    if isinstance(self.table, NestedTable):
      self.mem_cost = CostOp(self.mem_cost, COST_MUL, self.table.get_duplication_number())
    return self.mem_cost
  def __str__(self):
    return '[{}] hashindex : [table = {}, keys = ({}), cond = {}, value = {}]'.format(\
    self.id, self.table.get_full_type(), ','.join([str(k) for k in self.keys]), \
    self.condition, self.value)
  def fork(self):
    return ObjTreeIndex(self.table, self.keys, self.condition, self.value)

class ObjBasicArray(IndexMeta):
  def __init__(self, table, value=OBJECT):
    self.id = 0 
    self.table = table #table ~ obj_type
    self.value = value.fork() if isinstance(value, IndexValue) else IndexValue(value)
    if self.value.is_object():
      self.value.set_type(self.table)
  def to_json(self):
    tables = [self.table.name]
    cur_table = self.table
    if isinstance(cur_table, NestedTable):
      cur_table = cur_table.upper_table
      tables.insert(0, cur_table.name)
    value = self.value.to_json()
    return ("BasicArray", {"id":self.id, "table":'.'.join([t for t in tables]), "value":value})
  def get_idx_name(self):
    if self.is_single_element():
      return self.table.name
    if isinstance(self.table, NestedTable):
      return self.table.name+'_{}'.format(self.id)
    else:
      return self.table.name
  def get_value_type_name(self):
    if self.value.is_object():
      if isinstance(self.table, NestedTable):
        return '{}In{}{}'.format(get_capitalized_name(self.table.name),\
                        get_capitalized_name(get_main_table(self.table.upper_table).name), self.id)
      else:
        return get_capitalized_name(self.table.name)
    elif self.value.is_main_ptr() or self.value.is_nested_ptr():
      return 'ItemPointer'
  def get_relates(self):
    return (isinstance(self.table, NestedTable) and self.value.is_main_ptr())
  def __eq__(self, other):
    return type(self) == type(other) and self.table == other.table and self.value == other.value
  def __str__(self):
    return 'Basic array: {}, value = {}'.format(self.table.get_full_type(), self.value)
  def compute_mem_cost(self):
    self.cost = self.compute_size()
    ele_sz = 1 if self.value.is_main_ptr() else sum([f.field_class.get_sz() for f in self.pool_ref.fields])
    self.cost = cost_mul(self.cost, ele_sz)
    return self.cost
  def compute_size(self):
    return self.table.cost_all_sz() 
  def compute_single_size(self):
    return self.table.sz 
  def is_single_element(self):
    return isinstance(self.table, NestedTable) and get_main_table(self.table.upper_table).has_one_or_many_field(self.table.name) == 1
  def fork(self):
    newo = ObjBasicArray(self.table, self.value.value_type, self.single_element)
    newo.fields = [f for f in self.fields]
    return newo

# used in enumerate nestings, only indicate the type of indexed value, no concrete index is created yet
class IndexPlaceHolder(IndexMeta):
  def __init__(self, table, value):
    self.table = table
    self.value = value.fork() if isinstance(value, IndexValue) else IndexValue(value)
    if self.value.is_object():
      self.value.set_type(self.table)
  def fork(self):
    return IndexPlaceHolder(self.table, self.value.fork())
  def __eq__(self, other):
    return type(self) == type(other) and self.table == other.table and self.value == other.value
  def __str__(self):
    s = 'Placeholder [table = {}, value = {}]'.format(self.table.get_full_type(), self.value)
    return s
  def is_single_element(self):
    return isinstance(self.table, NestedTable) and get_main_table(self.table.upper_table).has_one_or_many_field(self.table.name) == 1


def get_idx_condition(pred):
  if isinstance(pred, ConnectOp):
    return ConnectOp(get_idx_condition(pred.lh), pred.op, get_idx_condition(pred.rh))
  elif isinstance(pred, SetOp):
    return SetOp(pred.lh, pred.op, get_idx_condition(pred.rh))
  elif isinstance(pred, BinOp):
    if isinstance(pred.rh, MultiParam) and len(pred.get_all_params()) == 0:
      return pred
    if isinstance(pred.rh, Parameter):
      return BinOp(pred.lh, EQ, Parameter('idx_param_{}'.format(get_query_field(pred.lh).field_name), tipe=pred.lh.get_type()))
    elif isinstance(pred.rh, AtomValue) or is_query_field(pred.rh):
      return pred
    else:
      assert(False)
  else:
    assert(False)

def get_keys_by_pred(idx_pred):
  qs = [idx_pred]
  keys = []
  range_keys = []
  while len(qs) > 0:
    q = qs.pop()
    if isinstance(q, ConnectOp):
      qs.append(q.lh)
      qs.append(q.rh)
    elif isinstance(q, SetOp):
      qs.append(q.rh)
    elif isinstance(q, BinOp) and isinstance(q.rh, Parameter):
      if q.op in [LT, LE, GT, GE, BETWEEN]:
        keys.append(q.lh)
        range_keys.append(q.lh) 
      elif q.op in [EQ]:
        keys.append(q.lh)
      elif q.op in [IN, SUBSTR, NEQ]:
        pass
      else:
        assert(False)
        # currently do not support NEQ... needs more hacks to handle this
  for k in range_keys:
    keys.remove(k)
  for k in range_keys:
    keys.append(k)
  return keys, range_keys