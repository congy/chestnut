from ds import *
from util import *
from cost import *


def create_primary_array(table, value=OBJECT):
  t = ObjBasicArray(table, value)
  return t

def table_contains(tbl1, tbl2): #return True if tbl1 contains tbl2
  if isinstance(tbl1, DenormalizedTable) and tbl1.contain_table(tbl2):
    return True
  if tbl1 == tbl2:
    return True
  return False

class DSManager(object):
  def __init__(self):
    self.data_structures = [] # a set of indexes / arrays
  def add_ds(self, ds, replace=False):
    for i,ds_ in enumerate(self.data_structures):
      if ds_ == ds:
        if replace:
          self.data_structures[i] = ds
        else:
         self.data_structures[i].merge(ds)
        return
    self.data_structures.append(ds)
  def remove_ds(self, ds):
    for i,ds_ in enumerate(self.data_structures):
      if ds == ds_:
        self.data_structures.pop(i)
        return
  def find_primary_array(self, table, create_new=False):
    # return the vertically partitioned primary array
    # or return the table arry if not partitioned
    # this can also be denormalized table
    for ds in self.data_structures:
      if (isinstance(ds, ObjBasicArray) or isinstance(ds, ObjSortedArray) or isinstance(ds, ObjArray)) and ds.value.is_object() and ds.table == table:
        return ds
    for ds in self.data_structures:
      if (isinstance(ds, ObjBasicArray) or isinstance(ds, ObjSortedArray) or isinstance(ds, ObjArray)) and ds.value.is_object() and table_contains(ds.table, table):
        return ds
    for ds in self.data_structures:
      if isinstance(ds, IndexPlaceHolder) and ds.table == table:
        new_ary = create_primary_array(ds.table)
        self.data_structures.append(new_ary)
        return new_ary
    for ds in self.data_structures:
      if isinstance(ds, IndexPlaceHolder) and table_contains(ds.table, table):
        new_ary = create_primary_array(ds.table)
        self.data_structures.append(new_ary)
        return new_ary
    return None
  def find_placeholder(self, table):
    for ds in self.data_structures:
      if isinstance(ds, IndexPlaceHolder) and ds.table == table:
        return ds
    for ds in self.data_structures:
      if isinstance(ds, IndexPlaceHolder) and table_contains(ds.table, table):
        return ds
    return None
  def find_primary_array_exact_match(self, table):
    for ds in self.data_structures:
      if isinstance(ds, ObjBasicArray) and ds.table == table and ds.value.is_object():
        return ds
    return None
  def merge(self, other):
    for o1 in other.data_structures:
      exist = False
      for o in self.data_structures:
        if o == o1:
          o.merge(o1)
          exist = True
      if not exist:
        self.data_structures.append(o1)
  def merge_self(self):
    # TODO: should be more than 1 pass?
    temp_ds = []
    groups = []
    group_major_table = []
    for i in range(0, len(self.data_structures)):
      o1 = self.data_structures[i]
      contained = False
      for gi,g_ds in enumerate(groups):
        if group_major_table[gi][0] == o1.table:
          if isinstance(o1, IndexPlaceHolder):
            group_major_table[gi] = (o1.table, len(g_ds))
          g_ds.append(o1)
          contained = True 
        elif group_major_table[gi][0].contain_table(o1.table):
          g_ds.append(o1)
          contained = True 
        elif o1.table.contain_table(group_major_table[gi][0]):
          group_major_table[gi] = (o1.table, len(g_ds))
          g_ds.append(o1)
          contained = True 
      if not contained:
        groups.append([o1])
        group_major_table.append((o1.table, 0))
    temp_ds = []
    for gi, g_ds in enumerate(groups):
      if len(g_ds) == 0:
        temp_ds.append(g_ds[0])
        continue
      ind = group_major_table[gi][1]
      main_ds = g_ds[ind]
      assert(isinstance(main_ds, IndexPlaceHolder))
      for i,ds in enumerate(g_ds):
        if i != ind and isinstance(ds, IndexPlaceHolder):
          main_ds.merge(ds)
        elif i != ind:
          if not ds.table == main_ds.table:
            ds.table = main_ds.table
          temp_ds.append(ds)
      temp_ds.append(main_ds)
    self.data_structures = temp_ds
  def fork(self):
    new_ds = DSManager()
    for ds in self.data_structures:
      new_ds.data_structures.append(ds.fork())
    return new_ds
  def compute_mem_cost(self):
    cost = 0
    ds_lst, memobj = collect_all_ds_helper1(self.data_structures)
    for ds in ds_lst:
      cost = cost_add(cost, ds.compute_mem_cost())
    for k,v in memobj.items():
      cnt = k.element_count()
      field_sz = sum([f.field_class.get_sz() for f in v.fields])
      cost = cost_add(cost, cost_mul(cnt, field_sz))
    return cost
  def copy_tables(self):
    dsmng = DSManager()
    new_ds = []
    for ds in self.data_structures:
      if isinstance(ds, ObjBasicArray) or isinstance(ds, IndexPlaceHolder):
        # if not any([ds.table==ds_.table for ds_ in new_ds]):
        #   nd = create_primary_array(ds.table)
        #   new_ds.append(nd)
        new_ds.append(IndexPlaceHolder(ds.table, OBJECT))
    dsmng.data_structures = new_ds
    return dsmng
  def clear_placeholder(self):
    temp_ds = []
    for ds in self.data_structures:
      if not isinstance(ds, IndexPlaceHolder):
        temp_ds.append(ds)
    self.data_structures = temp_ds
  def __str__(self):
    s = ""
    for i,ds in enumerate(self.data_structures):
      s += 'ds[{}]: {}\n'.format(i, ds)
    return s

def print_ds_with_cost(dsmnger):
  ds_lst, memobj = collect_all_ds_helper1(dsmnger.data_structures)
  for ds in ds_lst:
    cost = ds.compute_mem_cost()
    print 'ds {}, cost = {}, value = {}'.format(ds, to_symbol(cost), to_real_value(cost))
    print '------'
  print '\n * * * *\n'
  for k,v in memobj.items():
    cnt = k.element_count()
    field_sz = sum([f.field_class.get_sz() for f in v.fields])
    cost = cost_mul(cnt, field_sz)
    print 'object {}, cost = {}, value = {}'.format(v, to_symbol(cost), to_real_value(cost))
    print '------'

def collect_all_ds_helper1(lst):
  ds_lst = []
  memobj = {}
  for ds in lst:
    ds_lst.append(ds)
    if ds.value.is_object():
      next_lst, next_memobj = collect_all_ds_helper2(ds)
      memobj = map_union(memobj, next_memobj)
      ds_lst += next_lst
  return ds_lst, memobj

def collect_all_ds_helper2(ds, symbol=False):
  obj = ds.value.get_object()
  next_lst, next_memobj = collect_all_ds_helper1(obj.nested_objects)
  next_memobj[ds] = obj
  return next_lst, next_memobj
