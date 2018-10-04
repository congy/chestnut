from schema import *
from util import *
from constants import *
from pred import *
from query import *
from ds_manager import *
from planIR import *
from expr import *
import globalv
#import symbolic_context as symbctx
from pred_enum import *
from plan_helper import *
#from plan_refine import *
import itertools
import z3
import multiprocessing
import pickle
import sys

# enumerate all possible indexes to set upper_pred or answer query
# return (index_step, next_var_state) pair
def enumerate_indexes_for_pred(upper_pred, upper_pred_var, dsmng, idx_placeholder, upper_assoc_qf=None):
  upper_pred_plans = []
  for union_set in enumerate_pred_combinations(upper_pred):
    plantree_combs = [[] for j in range(0, len(union_set))]
    newvars = []
    for j,cnf in enumerate(union_set):
      if cnf:
        clauses = cnf.split()
      else:
        clauses = []
      newvars.append(EnvAtomicVariable(get_envvar_name(cnf), 'bool', init_value=True))
      for length in range(0, len(clauses)+1):
        for idx_combination in itertools.combinations(clauses, length):
          idx_pred = merge_into_cnf(idx_combination)
          rest_preds = set_minus(clauses, idx_combination, eq_func=(lambda x,y: x.query_pred_eq(y)))
          index_steps, added_rest_preds = helper_get_idx_step_by_pred(idx_combination, idx_placeholder, dsmng, upper_assoc_qf)
          rest_preds = rest_preds + added_rest_preds
          placeholder, assoc_vars, assoc_steps, nextlevel_fields, nextlevel_vars, nextlevel_tree_combs = \
                enumerate_steps_for_rest_pred(dsmng, idx_placeholder, rest_preds)

          if len(rest_preds) > 0:
            cond_expr = replace_subpred_with_var(merge_into_cnf(rest_preds), placeholder)
          else:
            cond_expr = None
          variable_to_set = newvars[j] if len(union_set) > 1 else upper_pred_var
          setvar_step = ExecSetVarStep(variable_to_set, AtomValue(not upper_pred_var.init_value), \
                    cond=UnaryOp(cond_expr) if upper_pred_var.init_value == True else cond_expr)


def helper_get_idx_step_by_pred(idx_combination, idx_placeholder, dsmng, upper_assoc_qf=None):
  # FK indexed, merge the foreign key into index
  foreignkey_idx = is_foreignkey_indexed(dsmng, upper_assoc_qf)
  # retrieve A.B, but store A as nested object in B, so need to add B.A as ``added_rest_pred''
  reverse_associated = is_reverse_associated(idx_placeholder.table, upper_assoc_qf)
  added_rest_pred = [reverse_associated] if reverse_associated and foreignkey_idx is None else []
  upper_table = upper_assoc_qf.table if upper_assoc_qf else None
  index_steps = []
  if len(idx_combination) == 0:
    if foreignkey_idx:
      reverse_key = QueryField('id', upper_table)
      op, params = get_idxop_and_params_by_pred(foreignkey_idx.condition, foreignkey_idx.keys, nonexternal={foreignkey_idx.keys[0]:reverse_key})
      return [ExecIndexStep(foreignkey_idx, foreignkey_idx.condition, op, params)], added_rest_pred
    else:
      basic_ary = ObjBasicArray(idx_placeholder.table, idx_placeholder.value)
      return [ExecScanStep(basic_ary)], added_rest_pred

  idx_pred = merge_into_cnf(idx_combination)
  keys = idx_pred.get_necessary_index_keys() 
  if foreignkey_idx:
    temp_idx_pred = merge_into_cnf([foreignkey_idx.condition, idx_pred])
    idx_pred = temp_idx_pred
    new_idxes = get_all_idxes_on_cond(idx_placeholder.value, foreignkey_idx.keys+keys, temp_idx_pred)
    reverse_key = QueryField('id', upper_table)
    assert(len(foreignkey_idx.keys)==1)
    if len(new_idxes) > 0:
      op, params = get_idxop_and_params_by_pred(temp_idx_pred, new_idxes[0].keys, nonexternal={foreignkey_idx.keys[0]:reverse_key})
  else:
    new_idxes = get_all_idxes_on_cond(idx_placeholder.value, keys, idx_pred)
    if len(new_idxes) > 0:
      op, params = get_idxop_and_params_by_pred(idx_pred, new_idxes[0].keys)  
  for idx in new_idxes:
    index_steps.append(ExecIndexStep(idx, idx_pred, op, params))
  return index_steps, added_rest_pred

def enumerate_steps_for_rest_pred(dsmng, idx_placeholder, rest_preds, assoc_fields=[]):
  if idx_placeholder.value.is_main_ptr():
    idx_placeholder = dsmng.find_primary_array(get_main_table(idx_placeholder.table))
  obj = idx_placeholder.value.get_object()
  #relates_objstruct = pool.get_obj(objstruct.table) if objstruct.relates else objstruct
  placeholder = {}

  _rest_assoc_fields = [a for a in assoc_fields]
  if len(rest_preds) > 0:
    _rest_assoc_fields += filter(lambda x: x is not None, \
        [x if is_assoc_field(x) else None for x in merge_into_cnf(rest_preds).get_curlevel_fields(include_assoc=True)])
  rest_assoc_fields = []
  for f in _rest_assoc_fields:
    if not any([x == f for x in rest_assoc_fields]):
      rest_assoc_fields.append(f)
  assoc_steps = []
  for f in rest_assoc_fields:   
    steps = search_steps_for_assoc(obj, dsmng, f)     
    placeholder[f] = steps[-1].var
    assoc_steps.append(steps)
  if len(rest_preds) == 0:
    return (placeholder, assoc_vars, assoc_steps, [], [], [])
  
  nextlevel_preds = find_nextlevel_pred(merge_into_cnf(rest_preds))
  nextlevel_vars = []
  nextlevel_step_combs = []
  nextlevel_fields = []
  for p in nextlevel_preds:
    #FIXME
    #assert(not is_assoc_field(p.lh))
    if is_assoc_field(p.lh):
      field = p.lh.lh
      pred_to_set = SetOp(p.lh.rh, p.op, p.rh)
    else:
      field = p.lh
      pred_to_set = p.rh
    newvar = EnvAtomicVariable(get_envvar_name(p), 'bool', init_value=(p.op == FORALL))
    nextlevel_vars.append((newvar, pred_to_set))
    nextlevel_fields.append(field)
    placeholder[p] = newvar

    next_objstruct = get_next_objstruct(pool, objstruct, field)
    nextlevel_step_combs.append(enumerate_indexes_for_pred(pred_to_set, newvar, pool, next_objstruct, \
            upper_assoc_qf=field))
  
  return (placeholder, assoc_vars, assoc_steps, nextlevel_fields, nextlevel_vars, nextlevel_step_combs)

