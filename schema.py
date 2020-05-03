import datetime
import random
from util import *
from constants import *
from cost import *

value_generators = {}

class Field(object):
  def __init__(self, name, tipe, vrange=[], default=0, is_temp=False):
    self.name = name
    self.table = None
    self.tipe = tipe
    self.range = vrange
    self.value_with_prob = []
    self.default = default
    self.is_temp = is_temp
    self.dependent_qf = None
    if len(vrange) == 0:
      # types = ["int", "oid", "uint", "smallint", "float", "bool", "date"]
      if self.tipe in ['oid','uint','date']:
        self.range = [0, MAXINT]
      elif self.tipe in ['smallint']:
        self.range = [0, 256]
      elif self.tipe in ['int','float'] or is_string_type(self.tipe):
        self.range = [0-MAXINT, MAXINT]
  def set_value_with_prob(self, vprob):
    if is_date_type(self.tipe):
      
      self.value_with_prob = [(datetime_to_int(x[0]),x[1]) for x in vprob]
    else:
      self.value_with_prob = vprob
  def fork(self):
    new_f = Field(self.name, self.tipe, self.range, self.default, self.is_temp)
    new_f.value_with_prob = [k for k in self.value_with_prob]
    new_f.table = self.table
    new_f.dependent_qf = self.dependent_qf
    return new_f
  def get_sz(self):
    if is_varchar_type(self.tipe):
      return get_varchar_length(self.tipe) / 4 if get_varchar_length(self.tipe) > 4 else 1
    elif is_string_type(self.tipe):
      return 8
    else:
      return type_size[self.tipe]
  def get_min_value(self, for_z3=False):
    if is_string_type(self.tipe):
      return 0 if for_z3 else ''
    if len(self.value_with_prob) > 0:
      minv = MAXINT
      for v,p in self.value_with_prob:
        if minv > v:
          minv = v
      return minv
    elif self.tipe == "date":
      return 0
    elif self.tipe == 'bool':
      return 0
    elif len(self.range) == 2:
      return self.range[0]
  def get_max_value(self, for_z3=False):
    if is_string_type(self.tipe):
      return MAXINT if for_z3 else '{}'.format(''.join(['z' for i in range(0, get_varchar_length(self.tipe))]))
    if len(self.value_with_prob) > 0:
      maxv = 0-MAXINT
      for v,p in self.value_with_prob:
        if maxv < v:
          maxv = v
      return maxv
    elif self.tipe == "date":
      return MAXINT
    elif self.tipe == 'bool':
      return 1
    elif len(self.range) == 2:
      lft = self.range[0].table.sz if isinstance(self.range[0], CostTableUnit) else self.range[0]
      rgt = self.range[1].table.sz if isinstance(self.range[1], CostTableUnit) else self.range[1]
      return rgt
  def set_value_generator(self, f):
    global value_generators
    value_generators[self] = f
  def generate_value(self):
    global value_generators
    if self in value_generators:
      return value_generators[self]()
    if is_long_string_type(self.tipe):
      return get_random_string(get_random_length(8, 1024))
    if is_varchar_type(self.tipe) and len(self.value_with_prob) == 0:
      return get_random_string(get_varchar_length(self.tipe))
    if len(self.value_with_prob) > 0:
      key = random.randint(0, 100)
      tmp = 0
      last_v = None
      for v,p in self.value_with_prob:
        if key < tmp + p:
          return v if v is not None else ''
        tmp = tmp + p
        last_v = v
      return last_v if last_v is not None else ''
    elif self.tipe == "date":
      t = ''
      while len(t) < 18:
        t = str(datetime.datetime.now()-datetime.timedelta(days=random.randint(0, 365), hours=random.randint(0, 24), seconds=random.randint(0, 3600)))[0:-7]
      return t
    elif self.tipe == 'bool':
      key = random.randint(0, 100)
      return '1' if key > 50 else '0'
    elif len(self.range) == 2:
      lft = self.range[0].table.sz if isinstance(self.range[0], CostTableUnit) else self.range[0]
      rgt = self.range[1].table.sz if isinstance(self.range[1], CostTableUnit) else self.range[1]
      if self.tipe == 'float':
        return lft + random.random() * float(rgt-lft)
      else:
        return random.randint(lft, rgt)
  def get_number_of_possible_values(self):
    if len(self.value_with_prob) > 0:
      return len(self.value_with_prob)
    else:
      return min(int(self.range[1]-self.range[0]), 10000)
  def get_nv_for_cost(self, v=None, exclude=False):
    prob_cnt = 0
    if len(self.value_with_prob) > 0:
      if v is None:
        return 100/min([prob for v1,prob in self.value_with_prob])
      for v1,prob in self.value_with_prob:
        if v1 == v:
          prob_cnt = prob
      if prob_cnt == 0:
        return 1
      if exclude:
        tempv = 100 - prob_cnt
      else:
        tempv = prob_cnt
      if tempv == 0:
        return 1
      else:
        return 100.0 / float(tempv)
    elif len(self.range) == 2:
      if self.tipe == 'float':
        return 1
      else:
        return (to_real_value(self.range[1]) - to_real_value(self.range[0]) + 1)
    elif is_bool_type(self.tipe):
      return 2
    elif is_string_type(self.tipe):
      return 1

class Table(object):
  def __init__(self, name: str, sz: int, is_temp: bool = False):
    self.name: str = name
    self.sz: int = sz
    id_field: Field = Field('id', 'oid', vrange=[1, sz])
    self.fields: List[Field] = [('id', id_field)]
    self.assocs: List[Tuple[str, Association]] = []
    self.nested_tables: Dict[str, NestedTable] = {} #key: assoc name
    self.indexes: ... = []
    self.id_index: ... = None
    self.is_temp: bool = is_temp
    self.primary_keys: ... = []
  def __eq__(self, other) -> bool:
    return type(self) == type(other) and self.name == other.name
  def __str__(self) -> str:
    return 'Table({})'.format(self.name)
  def __hash__(self) -> int:
    return hash(self.name)
  def get_sz_for_cost(self) -> CostTableUnit:
    return CostTableUnit(self)
  def cost_str_symbol(self) -> str:
    return 'N{}'.format(self.name)
  def cost_real_size(self) -> int:
    return self.sz
  def cost_all_sz(self) -> int:
    return self.sz
  def cost_range_size(self, take_min=True):
    return get_table_size_range(self, take_min)
  def add_field(self, f):
    f.table = self
    self.fields.append((f.name, f))
  def add_fields(self, fs):
    for f in fs:
      f.table = self
      self.fields.append((f.name, f))
  def add_assoc(self, name, a):
    self.assocs.append((name, a))
    self.nested_tables[name] = NestedTable(self, a.rgt if a.lft.name == self.name else a.lft, name, a.lft_ratio if a.lft.name == self.name else a.rgt_ratio)
  def get_fields(self):
    r = []
    for fn,f in self.fields:
      r.append(f)
    return r
  #return -- 1: one; 0: many
  def has_one_or_many_field(self, fn) -> int:
    assoc = self.get_assoc_by_name(fn)
    assert(assoc)
    if assoc.assoc_type == "one_to_many" and assoc.rgt == self:
      return 1
    return 0
  def get_assocs(self):
    r = []
    for an,a in self.assocs:
      r.append(a)
    return r
  def get_field_pairs(self):
    return self.fields
  def get_assoc_pairs(self):
    return self.assocs
  def get_field_by_name(self, n):
    for fn,f in self.fields:
      if n == fn:
        return f 
    return None
  def has_field(self, n):
    return self.get_field_by_name(n) != None 
  def get_assoc_by_name(self, n):
    for an,a in self.assocs:
      if an == n:
        return a
    return None
  def get_nested_tables(self):
    r = []
    for k,v in list(self.nested_tables.items()):
      r.append(v)
    return r
  def get_nested_table_by_name(self, n):
    return self.nested_tables[n]
  def has_assoc(self, n):
    return self.get_assoc_by_name(n) != None 
  def add_nested_table(self, name, table):
    self.nested_tables[name] = table
  def get_full_type(self, return_list=False):
    if return_list:
      return [get_capitalized_name(self.name)]
    else:
      return get_capitalized_name(self.name)
  def get_id_index(self):
    return self.id_index
  def contain_table(self, table):
    return self == table

class NestedTable(Table):
  def __init__(self, upper_table, related_table, name, sz, is_temp=False):
    super(NestedTable, self).__init__(name, sz)
    self.upper_table = upper_table
    self.related_table = related_table # Issue.projects relates to Project
    id_field = Field('id', 'oid', vrange=[1, CostTableUnit(self)])
    id_field.table = self
    self.fields = [('id', id_field)]
    self.indexes = []
    self.sz_name = 'MAX_{}_PER_{}'.format(self.name.upper(), self.upper_table.name.upper())
    self.is_temp = is_temp
  def __str__(self):
    return 'Table({})'.format(self.get_full_type())
  def __eq__(self, other):
    return type(self) == type(other) and self.upper_table == other.upper_table and self.related_table == other.related_table and self.name == other.name
  def __hash__(self):
    return hash(self.upper_table) + hash(self.name)
  def get_fields(self):
    return get_main_table(self).get_fields()
  def cost_str_symbol(self):
    return '{}_per_{}'.format(self.name, self.upper_table.name)
  def cost_all_sz(self):
    return cost_mul(self.sz, self.upper_table.cost_all_sz())
  def get_nested_table_by_name(self, name):
    if name not in self.nested_tables:
      nested_t_to_be_copied = self.related_table.get_nested_table_by_name(name)
      t = NestedTable(self, nested_t_to_be_copied.related_table, nested_t_to_be_copied.name, nested_t_to_be_copied.sz)
      self.nested_tables[name] = t
      return t
    else:
      return self.nested_tables[name]
  def get_duplication_number(self): #how many times this is used...
    cur_table = self
    cnt = 1
    while isinstance(cur_table, NestedTable):
      cnt = CostOp(cnt, COST_MUL, cur_table.upper_table.get_sz_for_cost())
      cur_table = cur_table.upper_table
    return cnt
  def copy(self):
    new_t = NestedTable(self.upper_table, self.related_table, self.name, self.sz)
    new_t.fields = [('id', id_field)]
    return new_t
  def get_full_type(self, return_list=False):
    cur_table = self
    name = []
    while isinstance(cur_table, NestedTable):
      name.append("{}In{}".format(get_capitalized_name(cur_table.name), get_capitalized_name(get_main_table(cur_table.upper_table).name)))
      cur_table = cur_table.upper_table
    name.append(get_capitalized_name(cur_table.name))
    name = reversed(name)
    if return_list:
      return name
    else:
      return '::'.join(name)
  def get_partial_type(self):
    return "{}In{}".format(self.name.capitalize(), self.upper_table.name.capitalize())
  def get_assoc_by_name(self, n):
    #return related table's assoc
    return self.related_table.get_assoc_by_name(n)

class DenormalizedTable(object):
  def __init__(self, tables, fields=[]):
    self.tables = tables
    self.join_fields = fields
    self.name = 'XX'.join([t.name for t in self.tables])
    self.is_temp = False
    self.sz = to_real_value(self.cost_real_size())
  def __eq__(self, other):
    return type(self) == type(other) and set_equal(self.tables, other.tables)
  def get_full_type(self):
    return self.name
  def get_main_table(self):
    cur_tables = [self.tables[0]]
    for qf in self.join_fields:
      assert(qf.table in cur_tables)
      cur_tables.append(qf.field_class)
    return self.tables[0]
  def contain_table(self, table):
    if isinstance(table, Table):
      return any([t==table for t in self.tables])
    elif isinstance(table, DenormalizedTable):
      return set_include(self.tables, table.tables)
    else:
      return False
  def cost_str_symbol(self):
    return 'N{}'.format(self.name)
  def get_qf_by_tables(self, maint, assoct):
    # TODO: may return AssocOp
    for f in self.join_fields:
      if f.table == maint and f.field_class == assoct:
        return f
    assert(False)
  def cost_real_size(self):
    assert(len(self.join_fields) + 1 == len(self.tables))
    cost = self.tables[0].sz
    cur_table = self.tables[0]
    for f in self.join_fields:
      if cur_table.has_one_or_many_field(f.field_name) != 1:
        cost = cost * cur_table.get_nested_table_by_name(f.field_name).sz
      cur_table = f.field_class
    return cost
  def cost_all_sz(self):
    return self.cost_real_size()
  def get_sz_for_cost(self):
    return CostTableUnit(self)

class Association:
  def __init__(self, assoc_name, tp, tablea, tableb, lft_field_name, rgt_field_name, assoc_f1, assoc_f2):
    self.assoc_type = tp
    self.lft = tablea
    self.rgt = tableb
    self.lft_ratio = 0
    self.rgt_ratio = 0
    self.lft_field_name = lft_field_name
    self.rgt_field_name = rgt_field_name
    self.assoc_f1 = '{}_id'.format(lft_field_name) if assoc_f1 == "" else assoc_f1
    self.assoc_f2 = '{}_id'.format(rgt_field_name) if assoc_f2 == "" else assoc_f2
    #optional to many_to_many assoc
    if assoc_name == "":
      self.name = "{}_and_{}".format(tablea.name, tableb.name)
    else:
      self.name = assoc_name
  def __hash__(self):
    return hash(self.name)
  def __str__(self):
    return '{}-{}'.format(self.lft.name, self.rgt.name)
  def to_json(self):
    return {
      'assocType': self.assoc_type,
      'leftTable': self.lft.name,
      'rightTable': self.rgt.name,
      #'leftField': self.lft_field_name,
      #'rightField': self.rgt_field_name,
      'leftFkField': self.assoc_f1,
      'rightFkField': self.assoc_f2,
      'table': self.name if 'many_to_many' == self.assoc_type else None
    }
  def reset_lft_ratio(self, lft_ratio):
    self.lft_ratio = lft_ratio
    if self.assoc_type == "many_to_many":
      assoc.rgt_ratio = lft_ratio * self.lft.sz / self.rgt.sz
  def reset_rgt_ratio(self, rgt_ratio):
    self.rgt_ratio = rgt_ratio
    if self.assoc_type == "many_to_many":
      assoc.lft_ratio = rgt_ratio * self.rgt.sz / self.lft.sz

def get_new_assoc(assoc_name, assoc_type, lft, rgt, lft_name, rgt_name, lft_ratio=0, rgt_ratio=0, assoc_f1="", assoc_f2=""):
  assoc = Association(assoc_name, assoc_type, lft, rgt, lft_name, rgt_name, assoc_f1, assoc_f2)
  if lft_ratio > 0:
    assoc.lft_ratio = lft_ratio
  if rgt_ratio > 0:
    assoc.rgt_ratio = rgt_ratio
  if assoc_type == "many_to_many":
    assert(lft_ratio > 0 or rgt_ratio > 0)
    if rgt_ratio == 0:
      assoc.rgt_ratio = max(lft_ratio * lft.sz / rgt.sz, 2)
    if lft_ratio == 0:
      assoc.lft_ratio = max(rgt_ratio * rgt.sz / lft.sz, 2)
  elif assoc_type == "one_to_many":
    assoc.lft_ratio = max(rgt.sz / lft.sz, 2)
    assoc.rgt_ratio = 1
  if lft_name == "":
    lft_name = rgt.name
  if rgt_name == "":
    rgt_name = lft.name
  lft.add_assoc(lft_name, assoc)
  rgt.add_assoc(rgt_name, assoc)
  if assoc_type == "one_to_many":
    field_name = assoc.rgt_field_name + "_id"
    new_field = Field(field_name, 'oid', vrange=[1, assoc.lft.sz])
    rgt.add_field(new_field) 
  return assoc

def get_assoc_tables(associations):
  r = []
  for a in associations:
    if a.assoc_type == "many_to_many":
      r.append(a)
  return r
  
def get_one_to_many_relations(associations):
  r = []
  for a in associations:
    if a.assoc_type == "one_to_many":
      r.append(a)
  return r 

def get_main_table(table):
  if isinstance(table, NestedTable):
    return table.related_table
  else:
    return table

def is_main_table(table):
  return not isinstance(table, NestedTable)

def get_upper_table_list(table):
  if isinstance(table, NestedTable):
    return get_upper_table_list(table.upper_table)+[table.related_table.name]
  else:
    return [table.name]
