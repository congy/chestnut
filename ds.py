from util import *
from constants import *
from pred import *
from pred_helper import *
from pred_cost import *
import itertools
import globalv

class IndexParam(object):
  def __init__(self, fields=[], params=[]):
    self.fields = [f for f in fields]
    self.params = [p for p in params]
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
  def __str__(self, short=False):
    return 'aggr({})'.format(','.join([aggr for v,aggr in self.aggrs]))

class MemObject(object):
  def __init__(self, table):
    assert(table)
    self.table = table # Table or NestedTable or DenormalizedTable
    self.fields = [QueryField('id', t) for t in table.tables] if isinstance(table, DenormalizedTable) else [QueryField('id', get_main_table(table))]
    self.nested_objects = [] # array of nested BasicArray / ObjSortedArray / ObjArray
  def get_all_fields(self):
    return self.fields
  def add_field(self, f):
    # print f
    # print self.table.get_full_type()
    assert(get_main_table(self.table).contain_table(f.table))
    if not any([f==f1 for f1 in self.fields]) and f.field_name != 'id':
      self.fields.append(f)
  def add_fields(self, fs):
    for f in fs:
      self.add_field(f)
  def add_nested_object(self, obj, replace=False):
    assert(not isinstance(obj, MemObject))
    for i,o in enumerate(self.nested_objects):
      if obj==o:
        if replace:
          self.nested_objects[i]=obj
        return
    self.nested_objects.append(obj)
  def fork(self):
    newo = MemObject(self.table)
    newo.fields = [f for f in self.fields]
    newo.nested_objects = [o.fork() for o in self.nested_objects]
    return newo
  def __eq__(self, other):
    # TODO
    return self.table == other.table
  def __str__(self, short=False):
    if len(self.nested_objects) == 0 or short:
      return 'memobj({}-{})'.format(self.table.get_full_type(), ','.join([f.field_name for f in self.fields]))
    s = 'memobj({}-{}), nested = {{\n'.format(self.table.get_full_type(), ','.join([f.field_name for f in self.fields]))
    for o in self.nested_objects:
      s += '\n'.join(['  '+l for l in str(o).split('\n')])
      s += '\n'
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
    for o in other.nested_objects:
      exist = False
      for o1 in self.nested_objects:
        if o == o1:
          o1.merge(o)
          exist = True
        #if isinstance(o, IndexPlaceHolder) and isinstance(o1, IndexPlaceHolder) and o.table==o1.table and not o.value==o1.value:
        #  assert(False)
      if not exist:
        self.nested_objects.append(o)
  def find_nested_obj_by_field(self, field):
    for o in self.nested_objects:
      if get_main_table(o.table.upper_table) == field.table and o.table.name == field.field_name:
        return o
    return None 
  def get_value_type_name(self):
    if isinstance(self.table, NestedTable):
      return '{}In{}'.format(get_capitalized_name(self.table.name), get_capitalized_name(get_main_table(self.table.upper_table).name))
    else:
      return get_capitalized_name(self.table.name)

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
      self.value = value
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
  def __str__(self, short=False):
    if self.value_type == MAINPTR:
      return 'ptr to {}'.format(self.value.id if self.value else 'none')
    else:
      return self.value.__str__(short)
  def __eq__(self, other):
    if self.value_type == MAINPTR:
      return self.value_type == other.value_type and self.value == other.value
    else:
      return self.value_type == other.value_type
  def eq_without_memobj(self, other):
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
    self.value.add_nested_object(obj)
  def get_object(self):
    return self.value
  def set_type(self, table):
    self.value.table = table
  
class IndexMeta(object):
  # common class members:
  # id, table, value
  def merge(self, other):
    if self.value.is_object():
      self.value.value.merge(other.value.value)
  def clean_obj(self):
    self.value = self.value.clean_obj()
    return self
  def is_single_element(self):
    return False
  def get_value_type_name(self):
    if self.value.is_object():
      return self.value.get_object().get_value_type_name()
    elif self.value.is_main_ptr():
      return 'ItemPointer'
    elif self.value.is_aggr():
      return 'AggrFor{}'.format(get_capitalized_name(self.table.name))
    else:
      assert(False)

class KeyPath(object):
  def __init__(self, key, path=[]):
    self.path = path
    self.key = key
    self.hashstr = '-'.join([str(x) for x in self.path])+'-'+str(self.key)
  def __eq__(self, other):
    return len(self.path) == len(other.path) and all([self.path[i]==other.path[i] for i in range(0, len(self.path))]) and self.key == other.key
  def __str__(self):
    return self.hashstr
  def __hash__(self):
    return hash(self.hashstr)
  def get_query_field(self):
    return get_query_field(self.key)
    
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
  def add_denormalized_id_key(self, idf):
    if any([k==idf for k in self.keys]):
      if not any([k==idf for k in self.range_keys]):
        self.range_keys.append(idf)
    else:
      self.keys.append(idf)
      self.range_keys.append(idf)
  def __str__(self):
    return ','.join([str(k) for k in self.keys])

class IndexBase(IndexMeta):
  def __init__(self, table, keys, condition, value):
    self.id = 0 
    self.table = table #table ~ obj_type
    self.keys = keys.fork()
    self.condition = get_idx_condition(condition, keys.keys) #used to compute cost
    self.value = value.fork()
    if self.value.is_object() and (not isinstance(value, IndexValue)):
      self.value.set_type(self.table)
    self.mem_cost = 0
    self.is_refered = False
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
  def get_ds_name(self):
    return 'ds_{}'.format(self.id)
  def get_key_type_name(self):
    if len(self.key_fields()) > 0:
      return "{}_key_type".format(self.get_ds_name())
    else:
      return 'size_t'
  def get_relates(self):
    return (isinstance(self.table, NestedTable) and self.value.is_main_ptr())
  def __eq__(self, other):
    return type(self) == type(other) and self.table == other.table and \
    self.keys == other.keys and self.value == other.value and \
    self.condition.idx_pred_eq(other.condition)
  def eq_without_memobj(self, other):
    return type(self) == type(other) and self.table == other.table and \
    self.keys == other.keys and self.value.eq_without_memobj(other.value) and \
    self.condition.idx_pred_eq(other.condition)
  def compute_size(self):
    return IdxSizeUnit(self)
  def compute_single_size(self):
    return self.compute_size()
  def key_fields(self):
    return self.keys.keys

class ObjTreeIndex(IndexBase):
  def __init__(self, table, keys, condition, value):
    super(ObjTreeIndex, self).__init__(table, keys, condition, value)
    self.basic_ary = None
  def compute_mem_cost(self):
    if cost_computed(self.mem_cost):
      return self.mem_cost
    temp = IdxSizeUnit(self)
    #self.mem_cost = CostOp(temp, COST_ADD, CostLogOp(temp))
    self.mem_cost = temp
    self.mem_cost = cost_mul(self.mem_cost, sum([k.get_query_field().field_class.get_sz() for k in self.key_fields()])+1)
    return self.mem_cost
  def element_count(self):
    return IdxSizeUnit(self)
  def __str__(self, short=False):
    return '[{}] treeindex : [table = {}, keys = ({}), cond = {}, value = {}]'.format(\
    self.id, self.table.get_full_type(), self.keys, self.condition, self.value.__str__(short))
  def fork(self):
    return ObjTreeIndex(self.table, self.keys, self.condition, self.value) 
  def fork_without_memobj(self):
    if self.value.is_object():
      return ObjTreeIndex(self.table, self.keys, self.condition, IndexValue(OBJECT, self.table)) 
    else:
      return self.fork()

class ObjSortedArray(IndexBase):
  def __init__(self, table, keys, condition, value):
    #assert(isinstance(table, NestedTable))
    super(ObjSortedArray, self).__init__(table, keys, condition, value)
  def compute_mem_cost(self):
    if cost_computed(self.mem_cost):
      return self.mem_cost
    self.mem_cost = IdxSizeUnit(self)
    if isinstance(self.table, NestedTable):
      self.mem_cost = CostOp(self.mem_cost, COST_MUL, self.table.get_duplication_number())
    self.mem_cost = cost_mul(self.mem_cost, sum([k.get_query_field().field_class.get_sz() for k in self.key_fields()])+1)
    return self.mem_cost
  def element_count(self):
    mem_cost = IdxSizeUnit(self)
    if isinstance(self.table, NestedTable):
      mem_cost = CostOp(mem_cost, COST_MUL, self.table.get_duplication_number())
    return mem_cost
  def __str__(self, short=False):
    return '[{}] sorted-array : [table = {}, keys = ({}), cond = {}, value = {}]'.format(\
    self.id, self.table.get_full_type(), self.keys, self.condition, self.value.__str__(short))
  def fork(self):
    return ObjSortedArray(self.table, self.keys, self.condition, self.value) 
  def fork_without_memobj(self):
    if self.value.is_object():
      return ObjSortedArray(self.table, self.keys, self.condition, IndexValue(OBJECT, self.table)) 
    else:
      return self.fork()
  
class ObjArray(IndexBase):
  def __init__(self, table, condition=None, value=MAINPTR):
    super(ObjArray, self).__init__(table, IndexKeys([]), condition, value)
  def compute_mem_cost(self):
    if cost_computed(self.mem_cost):
      return self.mem_cost
    self.mem_cost = IdxSizeUnit(self)
    if isinstance(self.table, NestedTable):
      self.mem_cost = CostOp(self.mem_cost, COST_MUL, self.table.get_duplication_number())
    return self.mem_cost
  def element_count(self):
    mem_cost = IdxSizeUnit(self)
    if isinstance(self.table, NestedTable):
      mem_cost = CostOp(mem_cost, COST_MUL, self.table.get_duplication_number())
    return mem_cost
  def __str__(self, short=False):
    return '[{}] array : [table = {}, cond = {}, value = {}]'.format(\
    self.id, self.table.get_full_type(), \
    self.condition, self.value.__str__(short))
  def fork(self):
    return ObjArray(self.table, self.condition, self.value) 
  def fork_without_memobj(self):
    if self.value.is_object():
      return ObjArray(self.table, self.condition, IndexValue(OBJECT, self.table)) 
    else:
      return self.fork()

class ObjHashIndex(IndexBase):
  def __init__(self, table, keys, condition=None, value=MAINPTR):
    super(ObjHashIndex, self).__init__(table, keys, condition, value)
  def compute_mem_cost(self):
    if cost_computed(self.mem_cost):
      return self.mem_cost
    temp = IdxSizeUnit(self)
    self.mem_cost = CostOp(temp, COST_MUL, 2)
    if isinstance(self.table, NestedTable):
      self.mem_cost = CostOp(self.mem_cost, COST_MUL, self.table.get_duplication_number())
    return self.mem_cost
  def __str__(self, short=False):
    return '[{}] hashindex : [table = {}, keys = ({}), cond = {}, value = {}]'.format(\
    self.id, self.table.get_full_type(), ','.join([str(k) for k in self.keys]), \
    self.condition, self.value.__str__(short))
  def fork(self):
    return ObjHashIndex(self.table, self.keys, self.condition, self.value)
  def fork_without_memobj(self):
    if self.value.is_object():
      return ObjHashIndex(self.table, self.keys, self.condition, IndexValue(OBJECT, self.table))
    else:
      return self.fork()

class ObjBasicArray(IndexMeta):
  def __init__(self, table, value):
    self.id = 0 
    self.table = table #table ~ obj_type
    self.value = value.fork()
    if self.value.is_object() and (not isinstance(value, IndexValue)):
      self.value.set_type(self.table)
    self.mem_cost = 0
    self.is_refered = False
  def to_json(self):
    tables = [self.table.name]
    cur_table = self.table
    if isinstance(cur_table, NestedTable):
      cur_table = cur_table.upper_table
      tables.insert(0, cur_table.name)
    value = self.value.to_json()
    return ("BasicArray", {"id":self.id, "table":'.'.join([t for t in tables]), "value":value})
  def get_key_type_name(self):
    return 'size_t'
  def key_fields(self):
    return []
  def get_ds_name(self):
    if self.is_single_element():
      return self.table.name
    else:
      return self.table.name+'_{}'.format(self.id)
  def get_relates(self):
    return (isinstance(self.table, NestedTable) and self.value.is_main_ptr())
  def __eq__(self, other):
    return type(self) == type(other) and self.table == other.table and self.value == other.value
  def eq_without_memobj(self, other):
    return type(self) == type(other) and self.table == other.table and self.value.eq_without_memobj(other.value)
  def __str__(self, short=False):
    return '[{}] Basic array: {}, value = {}'.format(self.id, self.table.get_full_type(), self.value.__str__(short))
  def compute_mem_cost(self):
    if cost_computed(self.mem_cost):
      return self.mem_cost
    self.mem_cost = self.compute_size()
    self.mem_cost = cost_mul(self.mem_cost, (len(self.table.tables) if isinstance(self.table, DenormalizedTable) else 1))
    return self.mem_cost
  def compute_size(self):
    return self.table.cost_all_sz() 
  def element_count(self):
    return self.table.cost_all_sz() 
  def compute_single_size(self):
    return self.table.sz 
  def is_single_element(self):
    return isinstance(self.table, NestedTable) and get_main_table(self.table.upper_table).has_one_or_many_field(self.table.name) == 1
  def fork(self):
    return ObjBasicArray(self.table, self.value)
  def fork_without_memobj(self):
    if self.value.is_object():
      return ObjBasicArray(self.table, IndexValue(OBJECT, self.table))
    else:
      return self.fork()

# used in enumerate nestings, only indicate the type of indexed value, no concrete index is created yet
class IndexPlaceHolder(IndexMeta):
  def __init__(self, table, value):
    self.table = table
    self.value = value.fork() if isinstance(value, IndexValue) else IndexValue(value)
  def fork(self):
    return IndexPlaceHolder(self.table, self.value)
  def fork_without_memobj(self):
    assert(False)
  def __eq__(self, other):
    return type(self) == type(other) and self.table == other.table and self.value == other.value
  def __str__(self, short=False):
    s = 'Placeholder [table = {}, value = {}]'.format(self.table.get_full_type(), self.value.__str__(short))
    return s
  def is_single_element(self):
    return isinstance(self.table, NestedTable) and get_main_table(self.table.upper_table).has_one_or_many_field(self.table.name) == 1


def get_idx_condition(pred, keys):
  if isinstance(pred, ConnectOp):
    return ConnectOp(get_idx_condition(pred.lh, keys), pred.op, get_idx_condition(pred.rh, keys))
  elif isinstance(pred, SetOp):
    return SetOp(pred.lh, pred.op, get_idx_condition(pred.rh, keys))
  elif isinstance(pred, BinOp):
    if pred.lh in keys and not is_query_field(pred.rh):
      return BinOp(pred.lh, EQ, Parameter('idx_param_{}'.format(get_query_field(pred.lh).field_name), tipe=pred.lh.get_type()))
    else:
      return pred
    # if isinstance(pred.rh, MultiParam) and len(pred.get_all_params()) == 0:
    #   return pred
    # if isinstance(pred.rh, Parameter):
    #   return BinOp(pred.lh, EQ, Parameter('idx_param_{}'.format(get_query_field(pred.lh).field_name), tipe=pred.lh.get_type()))
    # elif isinstance(pred.rh, AtomValue) or is_query_field(pred.rh):
    #   return pred
    # else:
    #   assert(False)
  else:
    assert(False)
