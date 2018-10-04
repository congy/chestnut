from ds import *


def create_primary_array(self, table):
  t = ObjBasicArray(table)
  return t

class DSManager(object):
  def __init__(self):
    self.data_structures = [] # a set of indexes / arrays
  def add_ds(self, ds):
    if not any([ds_==ds for ds_ in self.data_structures]):
      self.data_structures.append(ds)
  def remove_ds(self, ds):
    for i,ds_ in enumerate(self.data_structures):
      if ds == ds_:
        self.data_structures.pop(i)
        return
  def find_primary_array(self, table):
    # return the vertically partitioned primary array
    # or return the table arry if not partitioned
    # this can also be denormalized table
    for ds in self.data_structures:
      if isinstance(ds, ObjBasicArray):
        if isinstance(ds.table, DenormalizedTable) and ds.table.contain_table(table):
          return ds
        if ds.table == table:
          return ds
    return None
  def merge(self, other):
    for o1 in other.data_structures:
      for o in self.data_structures:
        if o == o1:
          o.merge(o1)
  def fork(self):
    new_ds = DSManager()
    for ds in self.data_structures:
      new_ds.data_structures.append(ds.fork())
    return new_ds
  def __str__(self):
    s = ""
    for i,ds in enumerate(self.data_structures):
      s += 'ds[{}]: {}\n'.format(i, ds)
    return s


