from pred import *
import z3

def merge_into_cnf(preds):
  if len(preds) == 0:
    return None
  r = preds[0]
  if len(preds) > 1:
    for i in range(1, len(preds)):
      r = ConnectOp(r, AND, preds[i])
  return r

def is_cnf(pred):
  if isinstance(pred, ConnectOp):
    if pred.op == OR:
      return False
    lh = is_cnf(pred.lh)
    rh = is_cnf(pred.rh)
    return lh and rh
  elif isinstance(pred, UnaryOp):
    if isinstance(pred.operand, BinOp) or isinstance(pred.operand, SetOp):
      return True
    else:
      return False
  elif isinstance(pred, BinOp):
    return True
  elif isinstance(pred, SetOp):
    return True
  return False

def is_cnf_without_negation(pred):
  if isinstance(pred, ConnectOp):
    if pred.op == OR:
      return False
    lh = is_cnf_without_negation(pred.lh)
    rh = is_cnf_without_negation(pred.rh)
    return lh and rh
  elif isinstance(pred, UnaryOp):
    return False
  elif isinstance(pred, BinOp):
    return True
  elif isinstance(pred, SetOp):
    return True

def is_dnf(pred):
  if isinstance(pred, ConnectOp):
    if pred.op == OR:
      lh = is_dnf(pred.lh)
      rh = is_dnf(pred.rh)
    else:
      lh = is_cnf(pred.lh)
      rh = is_cnf(pred.rh)
    return lh and rh
  elif isinstance(pred, UnaryOp):
    if isinstance(pred.operand, BinOp) or isinstance(pred.operand, SetOp):
      return True
    else:
      return False
  else:
    return True
  
def get_z3_expr_from_pred(pred, vmap):
  if isinstance(pred, ConnectOp):
    lh_expr = get_z3_expr_from_pred(pred.lh, vmap)
    rh_expr = get_z3_expr_from_pred(pred.rh, vmap)
    return pred_op_to_z3_lambda[pred.op](lh_expr, rh_expr)
  elif isinstance(pred, BinOp):
    lh_expr = get_z3_expr_from_pred(pred.lh, vmap)
    rh_expr = get_z3_expr_from_pred(pred.rh, vmap)
    if pred.op == BETWEEN:
      return z3.And(lh_expr>=rh_expr[0], lh_expr<=rh_expr[1])
    elif pred.op == IN:
      return z3.Or(*[lh_expr==p for p in rh_expr])
    else:
      assert(pred.op in pred_op_to_z3_lambda)
      return pred_op_to_z3_lambda[pred.op](lh_expr, rh_expr)
  elif isinstance(pred, UnaryOp):
    operand = get_z3_expr_from_pred(pred.operand, vmap)
    return z3.Not(operand)
  else: # setop, query field, parameter, ...
    for k,v in vmap:
      if k == pred:
        return v
    newv_name = 'v-{}'.format(len(vmap))
    if isinstance(pred, SetOp):
      newv = z3.Bool(newv_name)
    elif isinstance(pred, DoubleParam):
      newv1 = get_symbol_by_field_type(pred.p1.get_type(), newv_name+'-0')
      newv2 = get_symbol_by_field_type(pred.p2.get_type(), newv_name+'-1')
      return [newv1, newv2]
    elif isinstance(pred, MultiParam):
      symbol_params = [get_z3_expr_from_pred(p, vmap) for p in pred.params]
      return symbol_params
    elif isinstance(pred, AtomValue):
      if is_string_type(pred.get_type()):
        return hash(pred.v) % MAXINT
      else:
        return pred.v
    else:
      newv = get_symbol_by_field_type(pred.get_type(), newv_name)
    vmap.append((pred, newv))
    return newv
    
def not_exclusive(cnfs):
  # FIXME!!
  vmap = []
  exprs = [get_z3_expr_from_pred(pred, vmap) for pred in cnfs]
  temp_solver = z3.Solver()
  for i in range(0, len(cnfs)):
    for j in range(i+1, len(cnfs)):
      temp_solver.push()
      temp_solver.add(z3.And(exprs[i], exprs[j]))
      if temp_solver.check() != z3.unsat:
        return True
      temp_solver.pop()
  return False

def contain_neg(pred):
  if isinstance(pred, ConnectOp):
    return contain_neg(pred.lh) or contain_neg(pred.rh)
  if isinstance(pred, UnaryOp):
    return True
  return False
 
def count_ors(pred):
  if isinstance(pred, ConnectOp):
    init = 0
    if pred.op == OR:
      init = 1
    lh = count_ors(pred.lh)
    rh = count_ors(pred.rh)
    return lh + rh + init
  else:
    return 0

def find_nextlevel_preds(preds):
  r = []
  for pred in preds:
    r = r + find_nextlevel_pred(pred)
  return r

def find_nextlevel_pred(pred):
  if isinstance(pred, ConnectOp):
    return find_nextlevel_pred(pred.lh) + find_nextlevel_pred(pred.rh)
  elif isinstance(pred, SetOp):
    return [pred]
  elif isinstance(pred, UnaryOp):
    return find_nextlevel_pred(pred.operand)
  else:
    return []
    
def break_pred_assoc_field(pred):
  if isinstance(pred, ConnectOp):
    pred.lh = break_pred_assoc_field(pred.lh)
    pred.rh = break_pred_assoc_field(pred.rh)
    return pred
  else:
    if is_next_level_op(pred.op):
      pred.rh = break_pred_assoc_field(pred.rh)
      pred.lh = break_pred_assoc_field_helper(pred.lh)
      return pred
    else:
      pred.lh = break_pred_assoc_field_helper(pred.lh)
      pred.rh = break_pred_assoc_field_helper(pred.rh)
      return pred

def table_contain_association(table, pred):
  if isinstance(pred, QueryField):
    return table.contain_table(pred.field_class)
  elif isinstance(pred, AssocOp):
    if table.contain_table(pred.lh.field_class):
      return table_contain_association(table, pred.rh)

def get_assoc_fieldname_list(f):
  if isinstance(f, QueryField):
    return [f.field_name]
  elif isinstance(f, AssocOp):
    return [f.lh.field_name] + get_assoc_fieldname_list(f.rh)

def get_assoc_field_list(f):
  if isinstance(f, QueryField):
    return [f]
  elif isinstance(f, AssocOp):
    return [f.lh] + get_assoc_field_list(f.rh)

def reconstruct_assoc_from_list(lst):
  if len(lst) == 1:
    return lst[0]
  else:
    return AssocOp(lst[0], reconstruct_assoc_from_list(lst[1:]))

def get_full_assoc_field_name(f):
  if isinstance(f, QueryField):
    return f.field_name
  elif isinstance(f, AssocOp):
    return f.lh.field_name + '_' + get_full_assoc_field_name(f.rh)

def get_fieldname_cap(f):
  return ''.join([c.capitalize() for c in get_query_field(f).field_name.split('_')])

def get_table_from_pred(pred):
  if isinstance(pred, SetOp):
    return get_query_table(pred.lh)
  elif isinstance(pred, ConnectOp):
    return get_table_from_pred(pred.lh)
  elif isinstance(pred, BinOp):
    return get_query_table(pred.lh)
  else:
    assert(False)

def get_reversed_assoc_qf(qf):
  assoc = qf.table.get_assoc_by_name(qf.field_name)
  new_qf_table = qf.field_class
  new_qf_name = assoc.lft_field_name if new_qf_table == assoc.lft else assoc.rgt_field_name
  new_qf = QueryField(new_qf_name, table=new_qf_table)
  return new_qf

def qf_match_either_direction(qf1, qf2):
  if qf1 == qf2:
    return True
  qf2_ = get_reversed_assoc_qf(qf2)
  if qf1 == qf2_:
    return True
  return False

def get_qf_from_nested_t(table):
  if isinstance(table, NestedTable):
    qf = QueryField(table.name)
    qf.complete_field(get_main_table(table.upper_table))
    return qf
  else:
    return table

def get_nested_t_from_qf(qf):
  return qf.table.get_nested_table_by_name(qf.field_name)
