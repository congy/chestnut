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
      cnf = rewrite_pred_for_denormalized_table(cnf, idx_placeholder.table)
      if cnf:
        clauses = cnf.split()
      else:
        clauses = []
      newvars.append(EnvAtomicVariable(get_envvar_name(cnf), 'bool', init_value=True))
      for length in range(0, len(clauses)+1):
        for idx_combination in itertools.combinations(clauses, length):
          rest_preds = set_minus(clauses, idx_combination, eq_func=(lambda x,y: x.query_pred_eq(y)))
          index_steps, added_rest_preds = helper_get_idx_step_by_pred(idx_combination, idx_placeholder, dsmng, upper_assoc_qf)
          rest_preds = rest_preds + added_rest_preds
          rest_pred, placeholder, assoc_steps, nextlevel_fields, nextlevel_tree_combs  = \
                enumerate_steps_for_rest_pred(dsmng, idx_placeholder, rest_preds)

          if len(rest_preds) > 0:
            cond_expr = rest_pred
          else:
            cond_expr = None
          variable_to_set = newvars[j] if len(union_set) > 1 else upper_pred_var
          setvar_step = ExecSetVarStep(variable_to_set, AtomValue(not upper_pred_var.init_value), \
                    cond=UnaryOp(cond_expr) if upper_pred_var.init_value == True else cond_expr)

          for next_level_steps in itertools.product(*nextlevel_tree_combs):
            for idx_step in index_steps:
              plan_tree = PlanTree(cnf)
              plan_tree.pre_steps = get_initvar_steps([], [variable_to_set])
              plan_tree.element_steps += assoc_steps
              plan_tree.element_steps.append(setvar_step)
              plan_tree.index_step = idx_step #idx_step.fork()
              for i,next_step in enumerate(next_level_steps):
                plan_tree.next_level_pred[nextlevel_fields[i]] = next_step
              plantree_combs[j].append(plan_tree)

    for plan_tree_union in itertools.product(*plantree_combs):
      ptunion = PlanTreeUnion(plan_trees=[p.fork() for p in plan_tree_union])
      if len(union_set) > 1:
        pred = newvars[0]
        for p in newvars[1:]:
          pred = ConnectOp(pred, OR, p)
        ptunion.after_steps.append(ExecSetVarStep(upper_pred_var, pred))
      upper_pred_plans.append(ptunion)

    return upper_pred_plans

def enumerate_indexes_for_query(query, dsmng, idx_placeholder, upper_assoc_qf=None):
  query_plans = []
  aggr_assoc_fields = []
  for v,aggr in query.aggrs:
    for f in aggr.get_curlevel_fields(include_assoc=True):
      if is_assoc_field(f):
        aggr_assoc_fields.append(f)

  for union_set in enumerate_pred_combinations(query.pred):
    plantree_combs = [[] for j in range(0, len(union_set))]
    newvars = [] # a list of return_var
    for j,cnf in enumerate(union_set):
      cnf = rewrite_pred_for_denormalized_table(cnf, idx_placeholder.table)
      if cnf:
        clauses = cnf.split()
      else:
        clauses = []
      return_var = EnvCollectionVariable("query{}_part{}".format(query.id, j), query.table, is_temp=True)
      return_var.sz = get_query_result_sz(query.table, cnf)
      newvars.append(return_var)
      for length in range(0, len(clauses)+1):
        for idx_combination in itertools.combinations(clauses, length):
          rest_preds = set_minus(clauses, idx_combination, eq_func=(lambda x,y: x.query_pred_eq(y)))
          index_steps, added_rest_preds = helper_get_idx_step_by_pred(idx_combination, idx_placeholder, dsmng, upper_assoc_qf)
          rest_preds = rest_preds + added_rest_preds
          rest_pred, placeholder, assoc_steps, nextlevel_fields, nextlevel_tree_combs = \
                enumerate_steps_for_rest_pred(dsmng, idx_placeholder, rest_preds, assoc_fields=aggr_assoc_fields)
          if len(rest_preds) > 0:
            cond_expr = rest_pred
          else:
            cond_expr = None
          variable_to_set = newvars[j] if len(union_set) > 1 else query.return_var
          set_steps = []
          if len(union_set) == 1:
            for v,aggr in query.aggrs:
              new_aggr = replace_subexpr_with_var(aggr, placeholder)
              set_steps.append(ExecSetVarStep(v, new_aggr, cond=cond_expr))
            if variable_to_set:
              set_steps.append(ExecSetVarStep(variable_to_set, None, cond=cond_expr, proj=query.projections))
          else:
            if variable_to_set:
              set_steps.append(ExecSetVarStep(variable_to_set, None, cond=cond_expr, proj=query.projections))

          Nsteps_to_add_sort = len(index_steps)
          if query.order:
            for index_step in [idxs for idxs in index_steps]:
              idx_step = index_step.fork()
              new_step = add_order_to_idx(idx_step, query.order)
              if new_step:
                index_steps.append(new_step)

          for next_level_steps in itertools.product(*nextlevel_tree_combs):
            for k,idx_step in enumerate(index_steps):
              plan_tree = PlanTree(cnf)
              plan_tree.pre_steps = get_initvar_steps([v for v,aggr in query.aggrs], [])
              plan_tree.element_steps += assoc_steps
              plan_tree.element_steps += set_steps
              plan_tree.index_step = idx_step.fork()
              if k < Nsteps_to_add_sort and query.order and len(union_set) == 1:
                plan_tree.sort_step = ExecSortStep(query.return_var, query.order)
              for i,next_step in enumerate(next_level_steps):
                plan_tree.next_level_pred[nextlevel_fields[i]] = next_step
              plantree_combs[j].append(plan_tree)
    
    total_comb_length = 1
    for xx in plantree_combs:
      total_comb_length = total_comb_length * len(xx)
    for plan_tree_union in itertools.product(*plantree_combs):
      ptunion = PlanTreeUnion(plan_trees=[p.fork() for p in plan_tree_union])
      if total_comb_length < 4000 or (not is_opt_out_plan(ptunion)):
        # sort / union / distinct 
        if len(union_set) > 1:
          ptunion.after_steps.append(ExecUnionStep(query.return_var, query.aggrs, newvars))
          if query.order:
            ptunion.after_steps.append(ExecSortStep(query.return_var, query.order))
        query_plans.append(ptunion)

    # TODO: aggr result not implemented...

  if len(query.includes) == 0:
    return query_plans

  if idx_placeholder.value.is_main_ptr():
    idx_placeholder = dsmng.find_placeholder(get_main_table(idx_placeholder.table))
  obj = idx_placeholder.value.get_object()

  full_plans = []
  next_level_query = []
  next_fields = []
  assoc_steps = []
  for qf,next_query in query.includes.items():
    steps = search_steps_for_assoc(obj, dsmng, qf)
    field = qf
    next_fields.append(qf)
    if len(steps) == 0:
      assert(idx_placeholder.table.contain_table(qf.field_class))
      next_idx_placeholder = idx_placeholder
    else:
      step = ExecStepSeq(steps)
      assoc_steps.append(step)
      #if qf.table.has_one_or_many_field(qf.field_name) != 1:
      assert(steps[-1].idx is not None)
      if isinstance(steps[-1].idx, ObjBasicArray):
        next_idx_placeholder = steps[-1].idx
      elif isinstance(steps[-1].idx, ObjTreeIndex):
        next_idx_placeholder = dsmng.find_placeholder(steps[-1].idx.table)
      else:
        next_idx_placeholder = dsmng.find_placeholder(field.field_class)
    #print 'obj = {}'.format(obj)
    #print 'ASSOC = {}, step = {}, next_idx_placeholder = {}'.format(qf, step, next_idx_placeholder)
    next_level_query.append(\
      enumerate_indexes_for_query(next_query, dsmng, next_idx_placeholder, upper_assoc_qf=field))

  for ptu in query_plans:
    plan_tree_combs = [[] for i in range(0, len(ptu.plan_trees))]
    for i,pt in enumerate(ptu.plan_trees):
      for next_plan_comb in itertools.product(*next_level_query):
        new_plan_tree = pt.fork()
        new_plan_tree.element_steps += assoc_steps
        for j,next_plan in enumerate(next_plan_comb):
          new_plan_tree.next_level_query[next_fields[j]] = next_plan
        plan_tree_combs[i].append(new_plan_tree)
    for plan_trees in itertools.product(*plan_tree_combs):
      new_ptu = PlanTreeUnion(plan_trees)
      full_plans.append(new_ptu)

  return full_plans


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
      op, params = get_idxop_and_params_by_pred(foreignkey_idx.condition, foreignkey_idx.key_fields(), nonexternal={foreignkey_idx.key_fields()[0]:reverse_key})
      return [ExecIndexStep(foreignkey_idx.fork(), foreignkey_idx.condition, op, params)], added_rest_pred
    else:
      basic_ary = ObjBasicArray(idx_placeholder.table, idx_placeholder.value)
      return [ExecScanStep(basic_ary)], added_rest_pred

  idx_pred = merge_into_cnf(idx_combination)
  keys = idx_pred.get_necessary_index_keys() 
  if foreignkey_idx:
    temp_idx_pred = merge_into_cnf([foreignkey_idx.condition, idx_pred])
    idx_pred = temp_idx_pred
    new_idxes = get_all_idxes_on_cond(idx_placeholder, foreignkey_idx.key_fields()+keys, temp_idx_pred)
    reverse_key = QueryField('id', upper_table)
    assert(len(foreignkey_idx.key_fields())==1)
    if len(new_idxes) > 0:
      op, params = get_idxop_and_params_by_pred(temp_idx_pred, new_idxes[0].key_fields(), nonexternal={foreignkey_idx.key_fields()[0]:reverse_key})
  else:
    new_idxes = get_all_idxes_on_cond(idx_placeholder, keys, idx_pred)
    if len(new_idxes) > 0:
      op, params = get_idxop_and_params_by_pred(idx_pred, new_idxes[0].key_fields())  
  for idx in new_idxes:
    index_steps.append(ExecIndexStep(idx, idx_pred, op, params))
  return index_steps, added_rest_pred

def enumerate_steps_for_rest_pred(dsmng, idx_placeholder, rest_preds, assoc_fields=[]):
  if idx_placeholder.value.is_main_ptr():
    idx_placeholder = dsmng.find_placeholder(get_main_table(idx_placeholder.table))
  obj = idx_placeholder.value.get_object()
  placeholder = {}

  _rest_assoc_fields = [a for a in assoc_fields]
  if len(rest_preds) > 0:
    _rest_assoc_fields += filter(lambda x: x is not None, \
        [x if is_assoc_field(x) else None for x in merge_into_cnf(rest_preds).get_curlevel_fields(include_assoc=True)])
  new_pred = rewrite_pred_for_denormalized_table(merge_into_cnf(rest_preds), idx_placeholder.table)
  nextlevel_preds = find_nextlevel_pred(new_pred)
  for p in nextlevel_preds:
    if is_assoc_field(p.lh):
      _rest_assoc_fields.append(p.lh)
  rest_assoc_fields = []
  for f in _rest_assoc_fields:
    if not any([x == f for x in rest_assoc_fields]):
      rest_assoc_fields.append(f)
  assoc_steps_map = {}
  assoc_steps = []
  for f in rest_assoc_fields:  
    steps = search_steps_for_assoc(obj, dsmng, f) 
    step = ExecStepSeq(steps)
    assoc_steps_map[f] = step 
    if len(steps) > 0:   
      placeholder[f] = steps[-1].var
      assoc_steps.append(step)
      #print 'assoc steps = {}'.format(step)
  if len(rest_preds) == 0:
    return (None, placeholder, assoc_steps, [], [])
  
  nextlevel_step_combs = []
  nextlevel_fields = []
  for p in nextlevel_preds:
    field = get_query_field(p.lh)
    nextlevel_fields.append(p.lh)
    if is_assoc_field(p.lh):
      steps = assoc_steps_map[p.lh].steps
      if len(steps) == 0:
        assert(obj.table.contain_table(get_query_field(p.lh).field_class))
        next_idx_placeholder = idx_placeholder
      else:
        assert(steps[-1].idx is not None)
        if isinstance(steps[-1].idx, ObjBasicArray):
          next_idx_placeholder = steps[-1].idx
        elif isinstance(steps[-1].idx, ObjTreeIndex):
          next_idx_placeholder = dsmng.find_placeholder(steps[-1].idx.table)
        else:
          next_idx_placeholder = dsmng.find_placeholder(get_query_field(p.lh).field_class)
    else:
      next_idx_placeholder = find_next_idx_placeholder(idx_placeholder, dsmng, p.lh)
      
    assert(next_idx_placeholder)
    newvar = EnvAtomicVariable(get_envvar_name(p), 'bool', init_value=(p.op == FORALL))
    placeholder[p] = newvar
    nextlevel_step_combs.append(enumerate_indexes_for_pred(p.rh, newvar, dsmng, next_idx_placeholder, \
            upper_assoc_qf=field))
  
  rest_pred = replace_subpred_with_var(new_pred, placeholder)
  return (rest_pred, placeholder, assoc_steps, nextlevel_fields, nextlevel_step_combs)


def search_plans_for_one_nesting(query, dsmng):
  idx_placeholder = dsmng.find_placeholder(query.table)
  ptunions = enumerate_indexes_for_query(query, dsmng, idx_placeholder)
  steps = []
  for ptu in ptunions:
    steps.append(ptu.to_steps())
  print "one nesting steps = {}".format(len(steps))
  return steps

def thread_search_plans_for_one_nesting(query_id, tasks, results, idx):
  plans = []
  for query, dsmng in tasks:
    temp_plans = search_plans_for_one_nesting(query, dsmng)
    res = [ExecQueryStep(query, steps=steps) for steps in temp_plans]
    p = PlansForOneNesting(dsmng, res)
    plans.append(p)

  # if query_id > 0:
  #   struct = StructPool()
  #   cnt = 0
  #   for nesting_plans in plans:
  #     for plan in nesting_plans.plans:
  #       cnt += 1
  #       s = StructPool()
  #       plan.get_used_objstruct(None, s)
  #       struct.merge(s)
  #   pickle.dump((plans, struct), open('query_{}_{}.pickle'.format(query_id, idx), 'w'))
  #   results[idx] = cnt
  # else:
  results[idx] = plans

def search_plans_for_one_query(query, query_id=0, multiprocess=False, print_plan=True):
  dsmngers = enumerate_nestings_for_query(query)
  print 'all nestings = {} ({})'.format(len(dsmngers), query_id)
  plans = []
  if multiprocess:
    # TODO
    pass
  else:
    cnt = 0
    fail_nesting = []
    for k,dsmng in enumerate(dsmngers):
      if print_plan:
        print 'nesting {} = {}'.format(k, dsmng)
      try:
        temp_plans = search_plans_for_one_nesting(query, dsmng)
      except NestingFailException as e:
        fail_nesting.append(dsmng)
        continue
      res = [ExecQueryStep(query, steps=steps) for steps in temp_plans]
      p = PlansForOneNesting(dsmng, res)
      for plan in res:
        if print_plan:
          print 'PLAN {}'.format(cnt)
          print plan
        new_dsmnger = dsmng.copy_tables()
        plan.get_used_ds(None, new_dsmnger)
        new_dsmnger.clear_placeholder()
        if print_plan:
          print '** struct:'
          print new_dsmnger
          print '=============\n'
        cnt += 1
      plans.append(p)
  # print '#Fail nestings: {}'.format(len(fail_nesting))
  # for i,f in enumerate(fail_nesting):
  #   print 'FAIL {}'.format(i)
  #   print f
  #   print '-----'
  return plans
