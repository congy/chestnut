from pred import *
from pred_helper import *
from constants import *
from ds import *
from util import *
import z3
import itertools

def get_ds_type_lambda(tp):
  if tp == 'ObjSortedArray':
    return (lambda *args: ObjSortedArray(*args))
  elif tp == 'ObjArray':
    return (lambda *args: ObjArray(*args))
  elif tp == 'ObjTreeIndex':
    return (lambda *args: ObjTreeIndex(*args))
  else:
    assert(False)
    
def dispatch_not(pred, getnot=False):
  if isinstance(pred, UnaryOp):
    return dispatch_not(pred, (not getnot))
  elif isinstance(pred, SetOp):
    if getnot:
      return UnaryOp(pred)
    else:
      return pred
  elif isinstance(pred, ConnectOp):
    if getnot:
      return ConnectOp(dispatch_not(UnaryOp(pred.lh)), reversed_op(pred.op), dispatch_not(UnaryOp(pred.rh)))
    else:
      return pred
  elif isinstance(pred, BinOp):
    if getnot:
      if pred.op in [SUBSTR, IN, BETWEEN]:
        return UnaryOp(pred)
      else:
        return BinOp(pred.lh, reversed_op(pred.op), pred.rh)
    else:
      return pred

def break_pred_into_compares(pred, r):
  if isinstance(pred, UnaryOp):
    insert_no_duplicate(r, pred, eq_func=(lambda x,y:x.query_pred_eq(y)))
  elif isinstance(pred, SetOp):
    insert_no_duplicate(r, pred, eq_func=(lambda x,y:x.query_pred_eq(y)))
  elif isinstance(pred, ConnectOp):
    break_pred_into_compares(pred.lh, r)
    break_pred_into_compares(pred.rh, r)
  elif isinstance(pred, BinOp):
    insert_no_duplicate(r, pred, eq_func=(lambda x,y:x.query_pred_eq(y)))

def get_compare_map_by_field(pred, mp, upper_path=[], reverse=False):
  if isinstance(pred, UnaryOp):
    get_compare_map_by_field(pred.operand, mp, upper_path, (not reverse))
  elif isinstance(pred, SetOp):
    next_upper = upper_path + [pred.lh]
    get_compare_map_by_field(pred.rh, mp, next_upper, reverse)
  elif isinstance(pred, ConnectOp):
    get_compare_map_by_field(pred.lh, mp, upper_path, reverse)
    get_compare_map_by_field(pred.rh, mp, upper_path, reverse)
  elif isinstance(pred, BinOp):
    if is_query_field(pred.lh):
      key = KeyPath(pred.lh, upper_path)
      if is_query_field(pred.rh):
        if reverse:
          pass
        else:
          add_to_list_map(key, (pred.op, pred.rh), mp)
      elif isinstance(pred.rh, MultiParam):
        if pred.op == BETWEEN:
          if reverse:
            add_to_list_map(key, (LE, pred.rh.params[0]), mp)
            add_to_list_map(key, (GE, pred.rh.params[1]), mp)
          else:
            add_to_list_map(key, (GT, pred.rh.params[0]), mp)
            add_to_list_map(key, (LT, pred.rh.params[1]), mp)
        elif pred.op == IN:
          if reverse:
            # TODO
            for param in pred.rh.params:
              add_to_list_map(key, (LT, param), mp)
              add_to_list_map(key, (GT, param), mp)
          else:
            for param in pred.rh.params:
              add_to_list_map(key, (EQ, param), mp)
      elif isinstance(pred.rh, Parameter):
        if pred.op == NEQ or (pred.op==EQ and reverse):
          add_to_list_map(key, (GT, pred.rh), mp)
          add_to_list_map(key, (LT, pred.rh), mp)
        else:
          if reverse:
            pass
          else:
            add_to_list_map(key, (pred.op, pred.rh), mp)
      elif isinstance(pred.rh, AtomValue):
        if reverse:
          pass
        else:
          add_to_list_map(key, (pred.op, pred.rh), mp)

def enumerate_rest_pred(pred_pool, original_pred):
  if not is_dnf(original_pred):
    assert(False)
    # FIXME: rewrite to dnf
  dnf = original_pred.split_into_dnf()
  restp_clauses = []
  for clause in dnf:
    cmps = []
    break_pred_into_compares(clause, cmps)
    resti = []
    for p in pred_pool:
      if any([p.query_pred_eq(p1) for p1 in cmps]):
        resti.append(p)
    if len(resti) > 0:
      restp_clauses.append(merge_into_cnf(resti))
  if len(restp_clauses) == 0:
    return [None]
  else:
    r = restp_clauses[0]
    for p in restp_clauses[1:]:
      r = ConnectOp(r, OR, p)
    return [r]