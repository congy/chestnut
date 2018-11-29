import sys
sys.path.append('../')
import random
from schema import *
from pred import *
from pred_helper import *
from ds import *
from query_manager import *

# FIXME: currently we do not deal with NULL value:
# if key is (f1, f2), then (v1, NULL) will not be considered as a valid key 
#     i.e., any object with such key (v1, NULL), (NULL, v2), etc., will not be inserted into the data structure

def sql_for_ds_query(ds, upper_qf=None):
  table = ds.table
  join_strs = []
  if upper_qf:
    join_strs.append(get_join_condition(upper_qf, 'INNER JOIN'))
    #pred_strs = ['{}.id = ?'.format(upper_qf.table.name)]
    pred_strs = ['{}.id = {}'.format(upper_qf.table.name, random.randint(1, upper_qf.table.sz-2))]
  else:
    pred_strs = []
  if ds.value.is_object():
    fields = [f for f in ds.value.get_object().fields]
  else:
    fields = [get_query_field(f) for f in ds.key_fields()]
  if isinstance(table, DenormalizedTable):
    maint = table.get_main_table()
    for qf in table.join_fields:
      join_strs.append(get_join_condition(qf, 'OUTER JOIN'))
    fields = [QueryField('id', t) for t in table.tables] + fields
  else:
    maint = table
  if isinstance(ds, ObjBasicArray):
    pred = None
  else:
    pred = ds.condition
  if pred:
    sql_for_ds_pred(pred, fields, join_strs, pred_strs)
    field_str = ','.join(['{}.{} as {}_{}'.format(f.table.name, f.field_name, f.table.name, f.field_name) for f in fields])
    group_str = ','.join(['{}.{}'.format(f.table.name, f.field_name) for f in fields])
    tables = []
    for f in fields:
      insert_no_duplicate(tables, f.table)
    order_str = ','.join(['{}.id'.format(t.name) for t in tables])
    s = 'select {} from {} {} where {} group by {} order by {}'.format(field_str, maint.name, ' '.join(join_strs), \
                            ' and '.join(pred_strs), group_str, order_str)
  else:
    field_str = ','.join(['{}.{} as {}_{}'.format(f.table.name, f.field_name, f.table.name, f.field_name) for f in fields])
    s = 'select {} from {} {}'.format(field_str, maint.name, ' '.join(join_strs))
  return s

def sql_get_element_str(pred, fields, join_strs):
  if isinstance(pred, QueryField):
    insert_no_duplicate(fields, pred)
    insert_no_duplicate(fields, QueryField('id', pred.table))
    return '{}.{}'.format(pred.table.name, pred.field_name)
  elif isinstance(pred, AssocOp):
    join_strs.append(get_join_condition(pred, 'INNER JOIN'))
    f = get_query_field(pred)
    return sql_get_element_str(f, fields, join_strs)
  elif isinstance(pred, MultiParam):
    return '({})'.format(','.join([sql_get_element_str(p, join_strs) for p in pred.params]))
  elif isinstance(pred, AtomValue):
    return pred.to_var_or_value()
  else:
    assert(False)
# if has parameter --- select that field
# if no parameter --- just predicate
def sql_for_ds_pred(pred, fields, join_strs, pred_strs):
  if isinstance(pred, ConnectOp):
    sql_for_ds_pred(pred.lh, fields, join_strs, pred_strs)
    sql_for_ds_pred(pred.rh, fields, join_strs, pred_strs)
  elif isinstance(pred, BinOp):
    if len(pred.get_all_params()) == 0:
      lft_str = sql_get_element_str(pred.lh, fields, join_strs)
      rgt_str = sql_get_element_str(pred.rh, fields, join_strs)
      if pred.op == SUBSTR:
        rgt_str = '%{}'.format(rgt_str[1:-1])
      else:
        pred_strs.append('{} {} {}'.format(lft_str, pred_op_to_sql_map[pred.op], rgt_str))
    else:
      assert(isinstance(pred.rh, Parameter))
      if isinstance(pred.lh, QueryField):
        field = pred.lh
      elif isinstance(pred.lh, AssocOp):
        join_strs.append(get_join_condition(pred.lh, 'INNER JOIN'))
        field = get_query_field(pred.lh)
      else:
        assert(False)
      insert_no_duplicate(fields, field)
      insert_no_duplicate(fields, QueryField('id', field.table))
  elif isinstance(pred, SetOp):
    if len(pred.get_all_params()) == 0:
      new_pred_strs = []
      new_join_strs = []
      lqf = get_get_leftmost_qf(pred.lh)
      if pred.op == EXIST:
        if isinstance(lqf, QueryField):
          new_pred = pred.rh
        else:
          new_pred = SetOp(lqf.lh, pred.op, pred.rh)
        joinp = 'INNER JOIN'
      else:
        if isinstance(lqf, QueryField):
          new_pred = UnaryOp(pred.rh)
        else: # FIXME
          new_pred = SetOp(lqf.lh, pred.op, UnaryOp(pred.rh))
        joinp = 'LEFT OUTER JOIN'
      table_name, outer_pred = get_join_condition_helper2(lqf, joinp)
      subq_prefix = 'select 1 from {} '.format(table_name)
      new_pred_strs.append(outer_pred)
      sql_for_ds_pred(new_pred, [], new_join_strs, new_pred_strs)
      if pred.op == EXIST:
        pred_strs.append('exists ({} {} where {})'.format(subq_prefix, ' '.join(new_join_strs), ' and '.join(new_pred_strs)))
      else:
        pred_strs.append('not exists ({} {} where {})'.format(subq_prefix, ' '.join(new_join_strs), ' and '.join(new_pred_strs)))
    else:
      join_strs.append(get_join_condition(pred.lh, 'INNER JOIN'))
      sql_for_ds_pred(pred.rh, fields, join_strs, pred_strs)
  elif isinstance(pred, UnaryOp):
    if len(pred.operand.get_all_params()) == 0:
      return 'not ({})'.format(sql_for_ds_pred(pred.operand, fields, join_strs, pred_strs))
    else:
      return sql_for_ds_pred(pred.operand, fields, join_strs, pred_strs)

# def sql_for_query_pred(pred, fields):

def get_join_condition(qf, joinq):
  if isinstance(qf, AssocOp):
    return get_join_condition_helper(qf.lh, joinq) + get_join_condition(qf.rh, joinq)
  else:
    if is_atomic_field(qf):
      return ''
    return get_join_condition_helper(qf, joinq)
def get_join_condition_helper(qf, joinq):
  table, pred = get_join_condition_helper2(qf, joinq)
  return '{} {} ON {}'.format(joinq, table, pred)
  
# return a pair: table_name, outer_pred
# used for:
#   -> exists (select 1 from table_name .... where ... and outer_pred)
#   -> left outer join table_name on outer_pred
def get_join_condition_helper2(qf, joinq):
  if qf.table.has_one_or_many_field(qf.field_name) == 1:
    return qf.field_class.table.name, '{}.{}_id = {}.id' .format(\
                      qf.table.name, qf.field_name, qf.field_class.name)
  elif qf.field_class.has_one_or_many_field(get_reversed_assoc_qf(qf).field_name) == 1:
    return qf.field_class.table.name, '{}.id = {}.{}_id '.format(\
                      qf.table.name, qf.field_class.name, get_reversed_assoc_qf(qf).field_name)
  else:
    connect_table_name = qf.table.get_assoc_by_name(qf.field_name).name
    return connect_table_name, '{}.id = {}.{}_id {} {} ON {}.id = {}.{}_id '.format(\
                                                    qf.table.name, connect_table_name, qf.table.name, \
                                                    joinq, qf.field_class.name,
                                                    qf.field_class.name, connect_table_name, qf.field_class.name)  


def test_generate_sql(read_queries):
  rqmanagers, dsmeta = get_dsmeta(read_queries)
  for ds in dsmeta.data_structures:
    test_generate_sql_helper(ds)

def test_generate_sql_helper(ds, upper_qf=None):
  print 'ds = {}, query = {}'.format(ds.__str__(short=True), sql_for_ds_query(ds, upper_qf))
  print '----\n'
  if ds.value.is_object():
    for nextds in ds.value.get_object().nested_objects:
      nextqf = get_qf_from_nested_t(nextds.table)
      test_generate_sql_helper(nextds, nextqf)
