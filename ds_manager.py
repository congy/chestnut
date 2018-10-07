from ds import *


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
        return
    self.data_structures.append(ds)
  def remove_ds(self, ds):
    for i,ds_ in enumerate(self.data_structures):
      if ds == ds_:
        self.data_structures.pop(i)
        return
  def find_primary_array(self, table, return_exist=False):
    # return the vertically partitioned primary array
    # or return the table arry if not partitioned
    # this can also be denormalized table
    for ds in self.data_structures:
      if isinstance(ds, ObjBasicArray) and table_contains(ds.table, table):
        return ds
    for ds in self.data_structures:
      if isinstance(ds, IndexPlaceHolder) and table_contains(ds.table, table):
        new_ary = create_primary_array(ds.table)
        self.data_structures.append(new_ary)
        return new_ary
    return None
  def find_placeholder(self, table):
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
    for i in range(0, len(self.data_structures)):
      merged = False
      o1 = self.data_structures[i]
      for j in range(0, len(self.data_structures)):
        if i == j:
          continue
        o2 = self.data_structures[j]
        # only keep the denormalized table if both table A and denormalized A*B exist (merge them if necessary)
        if type(o1) == type(o2) and (not o1.table == o2.table):
          if o2.table.contain_table(o1.table):
            o2.merge(o1)
            merged = True
            break
      if not merged:
        temp_ds.append(o1)
    self.data_structures = temp_ds
  def fork(self):
    new_ds = DSManager()
    for ds in self.data_structures:
      new_ds.data_structures.append(ds.fork())
    return new_ds
  def copy_tables(self):
    dsmng = DSManager()
    new_ds = []
    for ds in self.data_structures:
      if isinstance(ds, ObjBasicArray) or isinstance(ds, IndexPlaceHolder):
        if not any([ds.table==ds_.table for ds_ in new_ds]):
          nd = create_primary_array(ds.table)
          new_ds.append(nd)
    dsmng.data_structures = new_ds
    return dsmng
  def __str__(self):
    s = ""
    for i,ds in enumerate(self.data_structures):
      s += 'ds[{}]: {}\n'.format(i, ds)
    return s


