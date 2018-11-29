from schema import *
from pred import *
from ds import *
from ds_manager import *
from query import *
import globalv
import itertools

class ObjNesting(object):
  def __init__(self, table, fields=[], level=0):
    assert(not isinstance(table, NestedTable))
    self.table = table
    self.assocs = {} #key: qf, value: ObjShape
    self.level = level
    self.fields = [f for f in fields]
  def add_field(self, f):
    if f not in self.fields:
      self.fields.append(f)
  def add_fields(self, fields):
    for f in fields:
      if f not in self.fields:
        self.fields.append(f)
  def merge(self, other):
    assert(self.table == other.table)
    for k,v in other.assocs.items():
      if k not in self.assocs:
        self.assocs[k] = v
      else:
        self.assocs[k].merge(v)
    self.add_fields(other.fields)
  def fork(self):
    o = ObjNesting(self.table, self.fields, self.level)
    for k,v in self.assocs.items():
      o.assocs[k] = v.fork()
    return o
  def fill_id_field(self):
    self.add_field(QueryField('id', self.table))
    for k,v in self.assocs.items():
      v.fill_id_field()
  def get_all_fields(self):
    r = [f for f in self.fields]
    for k,v in self.assocs.items():
      r = r + v.get_all_fields()
    return r
  def add_assoc(self, qf, assoc):
    assoc.level = self.level + 1
    assert(not isinstance(assoc.table, NestedTable))
    if qf in self.assocs:
      self.assocs[qf].merge(assoc)
    else:
      self.assocs[qf] = assoc
  def get_assoc(self, qf):
    return self.assocs[qf]
  def __str__(self):
    s = "ObjShape [{}] ({} : ({}))\n".format(self.level, self.table.name, \
            ','.join(f.field_name for f in self.fields))
    for k,v in self.assocs.items():
      temp_s = str(v)
      temp_s = ''.join('  '+l+'\n' for l in temp_s.split('\n'))
      s += "  {}: {}".format(k.field_name, temp_s)
    return s
  
def get_obj_nesting_by_query(cur_obj, query):
  #check filter pred
  if query.pred:
    cur_obj.add_fields(query.pred.get_curlevel_fields())
    get_obj_nesting_by_pred(cur_obj, query.pred)
  #check aggr
  for v,func in query.aggrs:
    for f in func.get_all_fields():
      if isinstance(f, QueryField) and f.table == get_main_table(query.table):
        cur_obj.add_field(f)
      else:
        get_obj_nesting_by_pred(cur_obj, f)
  #check order
  if query.has_order():
    for o in query.order:
      if not o.field_class.is_temp:
        if is_assoc_field(o):
          get_obj_nesting_by_pred(cur_obj, o)
        elif o.table == get_main_table(query.table):
          cur_obj.add_field(o)
  #check includes
  for k,v in query.includes.items():
    new_assoc_obj = ObjNesting(k.field_class)
    get_obj_nesting_by_query(new_assoc_obj, v)
    cur_obj.add_assoc(k, new_assoc_obj)
  
  return cur_obj

def get_obj_nesting_by_pred(cur_obj, pred):
  if isinstance(pred, ConnectOp):
    get_obj_nesting_by_pred(cur_obj, pred.lh)
    get_obj_nesting_by_pred(cur_obj, pred.rh)
    return cur_obj
  elif isinstance(pred, SetOp):
    new_assoc_obj = ObjNesting(get_query_field(pred.lh).field_class)
    get_obj_nesting_by_pred(new_assoc_obj, pred.rh)
    if is_assoc_field(pred.lh):
      next_obj = get_obj_nesting_by_pred(cur_obj, pred.lh)
      next_obj.add_assoc(get_query_field(pred.lh), new_assoc_obj)
    else:
      cur_obj.add_assoc(pred.lh, new_assoc_obj)
    return cur_obj
  elif isinstance(pred, AssocOp):
    new_assoc_obj = ObjNesting(pred.lh.field_class)
    get_obj_nesting_by_pred(new_assoc_obj, pred.rh)
    cur_obj.add_assoc(pred.lh, new_assoc_obj)
    return cur_obj.get_assoc(pred.lh)
  elif isinstance(pred, BinOp):
    if is_assoc_field(pred.lh):
      get_obj_nesting_by_pred(cur_obj, pred.lh)
    elif is_query_field(pred.lh):
      cur_obj.add_field(pred.lh)
    if is_assoc_field(pred.rh):
      get_obj_nesting_by_pred(cur_obj, pred.rh)
    elif is_query_field(pred.rh):
      cur_obj.add_field(pred.rh)
    return cur_obj
  elif isinstance(pred, UnaryOp):
    return get_obj_nesting_by_pred(cur_obj, pred.operand)
  elif isinstance(pred, QueryField):
    if is_atomic_field(pred):
      cur_obj.add_field(pred)
      return cur_obj
    else:
      new_assoc_obj = ObjNesting(pred.field_class)
      cur_obj.add_assoc(pred, new_assoc_obj)
      return cur_obj.get_assoc(pred)
  else:
    return cur_obj

def helper_get_assoc_exist_idx(qf, for_scan_pred=False):
  table = qf.table
  main_t = qf.field_class
  assoc = table.get_assoc_by_name(qf.field_name)
  reverse_assoc_field_name = assoc.lft_field_name if assoc.lft == main_t else assoc.rgt_field_name
  if main_t.has_one_or_many_field(reverse_assoc_field_name) == 0:
    id_qf = QueryField('id', table)
    assoc_qf = QueryField(reverse_assoc_field_name, main_t)
    keys = [id_qf]
    if for_scan_pred:
      condition = SetOp(assoc_qf, EXIST, BinOp(id_qf, EQ, UpperQueryField('id', table)))
    else:
      condition = SetOp(assoc_qf, EXIST, BinOp(id_qf, EQ, Parameter('{}_id'.format(table.name))))
  else:
    if for_scan_pred:
      assoc_qf = QueryField('{}_id'.format(reverse_assoc_field_name), main_t)
      # not index pred, so do not add parameter, but query field instead
      return [assoc_qf], BinOp(assoc_qf, EQ, UpperQueryField('id', table=qf.table))
    else:
      assoc_qf = AssocOp(QueryField(reverse_assoc_field_name, main_t), QueryField('id', table))
      keys = [assoc_qf]
      condition = BinOp(assoc_qf, EQ, Parameter('{}_id'.format(get_main_table(table).name)))
  return keys, condition

def table_already_contained(dsmng, table):
  for ds in dsmng.data_structures:
    if isinstance(ds, IndexPlaceHolder) and isinstance(ds.table, DenormalizedTable) and ds.table.contain_table(table):
      return ds
  return None

def enumerate_nesting(nesting):
  table = nesting.table
  ds_managers = []
  for i,(obj, dsmng) in enumerate(enumerate_nesting_helper(nesting, table, 1)):
    dsmng.add_ds(IndexPlaceHolder(table, IndexValue(OBJECT, obj)))
    dsmng.merge_self()
    ds_managers.append(dsmng)
  return ds_managers

def enumerate_nesting_helper(nesting, table, level):
  lst = [[] for i in range(0, len(nesting.assocs))]
  new_dsmng = DSManager()
  if len(lst) == 0:
    return [(MemObject(table), new_dsmng)]
  i = 0
  qfs = []
  for qf,assoc in nesting.assocs.items():
    qfs.append(qf)
    if isinstance(table, DenormalizedTable):
      nested_t = qf.table.get_nested_table_by_name(qf.field_name)
    else:
      nested_t = table.get_nested_table_by_name(qf.field_name)
    main_t = assoc.table

    if qf not in globalv.always_fk_indexed:
      #nested obj
      next_lst = enumerate_nesting_helper(assoc, nested_t, level+1)
      for (next_obj,next_dsmng) in next_lst:
        temp_obj = MemObject(table)
        next_ds = IndexPlaceHolder(nested_t, IndexValue(OBJECT, next_obj))
        temp_obj.add_nested_object(next_ds)
        lst[i].append((temp_obj, next_dsmng))

      if qf.table.has_one_or_many_field(qf.field_name) != 1:
        # nested ptrs
        next_lst = enumerate_nesting_helper(assoc, main_t, 1)
        for (next_obj,next_dsmng) in next_lst:
          temp_obj = MemObject(table)
          next_ds = IndexPlaceHolder(nested_t, MAINPTR)
          temp_obj.add_nested_object(next_ds)
          next_dsmng.add_ds(IndexPlaceHolder(next_obj.table, IndexValue(OBJECT, next_obj)))
          lst[i].append((temp_obj, next_dsmng))

    if qf not in globalv.always_nested:
      # maintable exist/associd index
      next_lst = enumerate_nesting_helper(assoc, main_t, 1)
      keys, condition = helper_get_assoc_exist_idx(qf)
      for (next_obj,next_dsmng) in next_lst:
        exist_idx1 = ObjTreeIndex(next_obj.table, keys, condition, value=MAINPTR)
        next_dsmng.add_ds(IndexPlaceHolder(next_obj.table, IndexValue(OBJECT, next_obj)))
        next_dsmng.add_ds(exist_idx1)
        lst[i].append((MemObject(table), next_dsmng))

    
    if qf not in globalv.reversely_visited and qf not in globalv.always_nested \
      and qf not in globalv.always_fk_indexed \
      and is_main_table(table) and not table.is_temp:
      # denormalized table
      if isinstance(table, DenormalizedTable):
        denorm_t = DenormalizedTable(table.tables+[main_t], table.join_fields+[qf])
        next_lst = enumerate_nesting_helper(assoc, denorm_t, 1)
        for (next_obj,next_dsmng) in next_lst:
          exist_ds = table_already_contained(next_dsmng, denorm_t)
          if exist_ds is None:
            next_obj.table = denorm_t
          new_ds = IndexPlaceHolder(denorm_t, IndexValue(OBJECT, next_obj))
          next_dsmng.add_ds(new_ds)
          lst[i].append((MemObject(denorm_t), next_dsmng))
      denorm_t = DenormalizedTable([qf.table, main_t], [qf])
      next_lst = enumerate_nesting_helper(assoc, denorm_t, 1)
      for (next_obj,next_dsmng) in next_lst:
        exist_ds = table_already_contained(next_dsmng, denorm_t) 
        if exist_ds is None:
          next_obj.table = denorm_t
        new_ds = IndexPlaceHolder(denorm_t, IndexValue(OBJECT, next_obj))
        next_dsmng.add_ds(new_ds)
        lst[i].append((MemObject(denorm_t), next_dsmng))

    """
    # FIXME: only consider such plan in a few circumstances
    if qf.table.is_temp==False:
      i += 1
      continue
    reversed_qf = get_reversed_assoc_qf(qf)
    next_lst = enumerate_nesting_helper(assoc, main_t, 1)
    reversed_obj = MemObject(get_nested_t_from_qf(reversed_qf))
    for (next_obj,next_dsmng) in next_lst:
      

    if reversed_qf.table.has_one_or_many_field(reversed_qf.field_name) == 1:
      next_lst = obj_logical_nesting_to_struct_pools_helper(assoc, main_t, 1)
      for (next_obj,next_pool) in next_lst:
        next_pool.add_obj(main_t, next_obj)
        lst[i].append((temp_obj.fork(), next_pool))
    else:
      # main table, nested obj next level
      next_lst = obj_logical_nesting_to_struct_pools_helper(assoc, main_t, 1)
      reversed_obj = ObjectStruct(get_nested_t_from_qf(reversed_qf))
      for (next_obj,next_pool) in next_lst:
        next_obj.add_next_level(reversed_qf, reversed_obj.fork())
        next_pool.add_obj(main_t, next_obj)
        lst[i].append((temp_obj.fork(), next_pool))

      # main table, nested array of ptr next level
      next_lst = obj_logical_nesting_to_struct_pools_helper(assoc, main_t, 1)
      reversed_obj = ObjectStruct(get_nested_t_from_qf(reversed_qf), relates=True)
      for (next_obj,next_pool) in next_lst:
        next_obj.add_next_level(reversed_qf, reversed_obj.fork())
        next_pool.add_obj(main_t, next_obj)
        lst[i].append((temp_obj.fork(), next_pool))
    """

    i += 1

  r = []
  # print "{}: len lst = {} || {}".format(table, len(lst), ','.join([str(len(x)) for x in lst]))
  for x in itertools.product(*lst):
    #x: list of pairs
    _obj = x[0][0].fork()
    _dsmng = x[0][1].fork()
    for i, (temp_obj, temp_dsmng) in enumerate(x[1:]):
      _obj.merge(temp_obj.fork())
      _dsmng.merge(temp_dsmng.fork())
    if len(r) == 116:
      print 'to be merged:'
      for x1 in x:
        print x1[0]
        print x1[1]
        print '----'
      print 'after merge:'
      print _obj
      print _dsmng
      print '====* * ==='
    r.append((_obj, _dsmng))
  #print "len r = {}".format(len(r))
  return r

def enumerate_nestings_for_query(query):
  cur_obj = ObjNesting(query.table)
  get_obj_nesting_by_query(cur_obj, query)
  print cur_obj
  dsmanagers = enumerate_nesting(cur_obj)
  return dsmanagers
