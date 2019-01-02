from schema import *
from util import *
from constants import *
from pred import *
from query import *
from ds_manager import *
from planIR import *
from expr import *
import globalv
import symbolic_context as symbctx
from plan_helper import *
from op_synth import *
import itertools
import z3
import multiprocessing
import pickle
import sys

# enumerate all possible indexes to set upper_pred or answer query
# return (index_step, next_var_state) pair
def enumerate_indexes_for_pred(thread_ctx, upper_pred, upper_pred_var, dsmng, idx_placeholder, upper_assoc_qf=None):
  upper_pred_plans = []
  queried_table = get_table_from_pred(upper_pred)
  all_steps = helper_get_idx_step_by_pred(thread_ctx, queried_table, upper_pred, None, idx_placeholder, dsmng, upper_assoc_qf)
  
  for op_rest_pairs in all_steps:
    variable_to_set = [EnvAtomicVariable(get_envvar_name(), 'bool', init_value=True) for i in range(0, len(op_rest_pairs))] \
          if len(op_rest_pairs) > 1 else [upper_pred_var]
    
    plantree_combs = [[] for j in range(0, len(op_rest_pairs))]
    for i,pair in enumerate(op_rest_pairs):
      idx_step = pair[0]
      rest_pred = pair[1]
      next_rest_pred, placeholder, assoc_steps, nextlevel_fields, nextlevel_tree_combs  = \
         enumerate_steps_for_rest_pred(thread_ctx, dsmng, idx_placeholder, rest_pred)
      cond_expr = next_rest_pred
      setvar_step = ExecSetVarStep(variable_to_set[i], AtomValue(not upper_pred_var.init_value), cond=cond_expr)
   
      for next_level_steps in itertools.product(*nextlevel_tree_combs):
        plan_tree = PlanTree()
        plan_tree.pre_steps = get_initvar_steps([], [variable_to_set[i]])
        plan_tree.element_steps += assoc_steps
        plan_tree.element_steps.append(setvar_step)
        plan_tree.index_step = idx_step.fork()
        for i,next_step in enumerate(next_level_steps):
          plan_tree.next_level_pred[nextlevel_fields[i]] = next_step
        plantree_combs[i].append(plan_tree)

    for plan_tree_union in itertools.product(*plantree_combs):
      ptunion = PlanTreeUnion(plan_trees=[p.fork() for p in plan_tree_union])
      if len(op_rest_pairs) > 1:
        final_pred = variable_to_set[0]
        for p in variable_to_set[1:]:
          final_pred = ConnectOp(pred, OR, p)
          ptunion.after_steps.append(ExecSetVarStep(upper_pred_var, pred))
      upper_pred_plans.append(ptunion)

  return upper_pred_plans

def enumerate_indexes_for_query(thread_ctx, query, dsmng, idx_placeholder, upper_assoc_qf=None):
  query_plans = []
  aggr_assoc_fields = []
  queried_table = get_main_table(query.table)
  for v,aggr in query.aggrs:
    for f in aggr.get_curlevel_fields(include_assoc=True):
      if is_assoc_field(f):
        aggr_assoc_fields.append(f)

  all_steps = helper_get_idx_step_by_pred(thread_ctx, queried_table, query.pred, query.order, idx_placeholder, dsmng, upper_assoc_qf)
  sortedN = len(all_steps)
  if query.order:
    all_steps += helper_get_idx_step_by_pred(thread_ctx, queried_table, query.pred, None, idx_placeholder, dsmng, upper_assoc_qf)
  total_comb_length = len(all_steps)

  for x,op_rest_pairs in enumerate(all_steps):
    plantree_nodes = []
    variable_to_set = []
    if len(op_rest_pairs) > 1 and query.return_var.sz:
      for i in range(0, len(op_rest_pairs)):
        variable_to_set.append(EnvCollectionVariable("query{}_part{}".format(query.id, i), query.table, is_temp=True))
        variable_to_set[i].sz = query.return_var.sz
    else:
      variable_to_set = [query.return_var]
    
    plantree_combs = [[] for j in range(0, len(op_rest_pairs))]
    for i,pair in enumerate(op_rest_pairs):
      idx_step = pair[0]
      rest_pred = pair[1]
      next_rest_pred, placeholder, assoc_steps, nextlevel_fields, nextlevel_tree_combs = \
          enumerate_steps_for_rest_pred(thread_ctx, dsmng, idx_placeholder, rest_pred, assoc_fields=aggr_assoc_fields)
      cond_expr = next_rest_pred
          
      set_steps = []
      projections = query.projections + query.aggrs
      if len(op_rest_pairs) == 1:
        for v,aggr in query.aggrs:
          new_aggr = replace_subexpr_with_var(aggr, placeholder)
          set_steps.append(ExecSetVarStep(v, new_aggr, cond=cond_expr))
        if variable_to_set[i]:
          set_steps.append(ExecSetVarStep(variable_to_set[i], None, cond=cond_expr, proj=projections))
      else:
        if variable_to_set[i]:
          set_steps.append(ExecSetVarStep(variable_to_set[i], None, cond=cond_expr, proj=projections))

      if len(op_rest_pairs) > 1:
        init_qr_var = [variable_to_set[i]]
      else:
        init_qr_var = []
      for next_level_steps in itertools.product(*nextlevel_tree_combs):
        plan_tree = PlanTree()
        plan_tree.pre_steps = get_initvar_steps([v for v,aggr in query.aggrs], [], init_qr_var)
        plan_tree.element_steps += assoc_steps
        plan_tree.element_steps += set_steps
        plan_tree.index_step = idx_step
        if x > sortedN:
          plan_tree.sort_step = ExecSortStep(query.return_var, query.order)
        for i2,next_step in enumerate(next_level_steps):
          plan_tree.next_level_pred[nextlevel_fields[i2]] = next_step
        plantree_combs[i].append(plan_tree)
        #print 'PLAN TREE = {}'.format(ExecStepSeq(plan_tree.to_steps()))
    
    for plan_tree_union in itertools.product(*plantree_combs):
      ptunion = PlanTreeUnion(plan_trees=[p.fork() for p in plan_tree_union])
      if total_comb_length < 4000 or (not is_opt_out_plan(ptunion)):
        # sort / union / distinct 
        if len(op_rest_pairs) > 1:
          ptunion.after_steps.append(ExecUnionStep(query.return_var, query.aggrs, variable_to_set, order=query.order))
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
    #if qf.table.has_one_or_many_field(qf.field_name) != 1:
    assert(steps[-1].idx is not None)
    if isinstance(steps[-1].idx, ObjBasicArray):
      next_idx_placeholder = steps[-1].idx
    elif isinstance(steps[-1].idx, ObjTreeIndex):
      next_idx_placeholder = dsmng.find_placeholder(steps[-1].idx.table)
    else:
      next_idx_placeholder = dsmng.find_placeholder(field.field_class)
    if is_assoc_field(field):
      step = ExecStepSeq(steps[:-1])
      assoc_steps.append(step)
    #print 'obj = {}'.format(obj)
    #print 'ASSOC = {}, step = {}, next_idx_placeholder = {}'.format(qf, step, next_idx_placeholder)
    next_level_query.append(\
      enumerate_indexes_for_query(thread_ctx, next_query, dsmng, next_idx_placeholder, upper_assoc_qf=field))

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


def helper_get_idx_step_by_pred(thread_ctx, queried_table, pred, order, idx_placeholder, dsmng, upper_assoc_qf=None):
  # FK indexed, merge the foreign key into index
  foreignkey_idx = is_foreignkey_indexed(dsmng, upper_assoc_qf)
  # retrieve A.B, but store A as nested object in B, so need to add B.A as ``added_rest_pred''
  reverse_associated = is_reverse_associated(idx_placeholder.table, upper_assoc_qf)
  added_rest_pred = reverse_associated if reverse_associated and foreignkey_idx is None else None
  upper_table = upper_assoc_qf.table if upper_assoc_qf else None
  index_steps = []
  idx_pred = pred
  fk_pred = None
  if foreignkey_idx:
    if isinstance(foreignkey_idx.condition, SetOp):
      fk_pred = foreignkey_idx.condition
    else:
      if pred is None:
        idx_pred = foreignkey_idx.condition
      else:
        idx_pred = merge_into_cnf([foreignkey_idx.condition, idx_pred])
  if foreignkey_idx:
    reverse_key = QueryField('id', upper_table)
    fk_key = foreignkey_idx.key_fields()[0]
    fk_param = foreignkey_idx.condition.get_all_params()[0]
    nonexternal={foreignkey_idx.key_fields()[0]:(reverse_key,fk_param)}
    thread_ctx.get_symbs().param_symbol_map[fk_param] = \
        get_symbol_by_field(fk_key.get_query_field().field_class,'fk-{}'.format(fk_param.symbol))
  else:
    nonexternal={}
  
  all_steps = \
    get_ds_and_op_on_cond(thread_ctx, idx_placeholder.table, idx_pred, idx_placeholder.value, order, fk_pred, nonexternal)
  
  #print 'table = {}, pred = {}, idxvalue = {}, len steps = {}'.format(idx_placeholder.table, idx_pred, idx_placeholder.value, len(all_steps))

  if added_rest_pred:
    for op_rest_pairs in all_steps:
      for i,pair in enumerate(op_rest_pairs):
        newpred = ConnectOp(pair[1], AND, added_rest_pred) if pair[1] else added_rest_pred
        op_rest_pairs[i] = (pair[0], newpred)
  return all_steps

def enumerate_steps_for_rest_pred(thread_ctx, dsmng, idx_placeholder, rest_pred, assoc_fields=[]):
  if idx_placeholder.value.is_main_ptr():
    idx_placeholder = dsmng.find_placeholder(get_main_table(idx_placeholder.table))
  obj = idx_placeholder.value.get_object()
  placeholder = {}

  _rest_assoc_fields = [a for a in assoc_fields]
  if rest_pred:
    _rest_assoc_fields += filter(lambda x: x is not None, \
        [x if is_assoc_field(x) else None for x in rest_pred.get_curlevel_fields(include_assoc=True)])
  nextlevel_preds = find_nextlevel_pred(rest_pred)
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
  if rest_pred is None:
    return (None, placeholder, assoc_steps, [], [])
  
  nextlevel_step_combs = []
  nextlevel_fields = []
  for p in nextlevel_preds:
    field = get_query_field(p.lh)
    nextlevel_fields.append(p.lh)
    if is_assoc_field(p.lh):
      steps = assoc_steps_map[p.lh].steps
      assert(steps[-1].idx is not None)
      if isinstance(steps[-1].idx, ObjBasicArray):
        next_idx_placeholder = steps[-1].idx
      elif isinstance(steps[-1].idx, ObjTreeIndex):
        next_idx_placeholder = dsmng.find_placeholder(steps[-1].idx.table)
      else:
        next_idx_placeholder = dsmng.find_placeholder(get_query_field(p.lh).field_class)
      assoc_steps_map[p.lh].steps = assoc_steps_map[p.lh].steps[:-1]
    else:
      next_idx_placeholder = find_next_idx_placeholder(idx_placeholder, dsmng, p.lh)
    assert(next_idx_placeholder)
    newvar = EnvAtomicVariable(get_envvar_name(), 'bool', init_value=(p.op == FORALL))
    placeholder[p] = newvar
    nextlevel_step_combs.append(enumerate_indexes_for_pred(thread_ctx, p.rh, newvar, dsmng, next_idx_placeholder, \
            upper_assoc_qf=field))
  
  rest_pred = replace_subpred_with_var(rest_pred, placeholder)
  return (rest_pred, placeholder, assoc_steps, nextlevel_fields, nextlevel_step_combs)


def search_plans_for_one_nesting(query, dsmng):
  thread_ctx = symbctx.create_thread_ctx()
  create_symbolic_obj_graph(thread_ctx, globalv.tables, globalv.associations)
  create_param_map_for_query(thread_ctx, query)
  idx_placeholder = dsmng.find_placeholder(query.table)
  ptunions = enumerate_indexes_for_query(thread_ctx, query, dsmng, idx_placeholder)
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

import time
def search_plans_for_one_query(query, query_id=0, multiprocess=False, print_plan=True):
  dsmngers = enumerate_nestings_for_query(query)
  compute_mem_bound()
  assert(globalv.memory_bound > 1000)
  print 'all nestings = {} ({})'.format(len(dsmngers), query_id)
  plans = []
  if multiprocess:
    # TODO
    pass
  else:
    cnt = 0
    fail_nesting = []
    start_time = time.time()
    for k,dsmng in enumerate(dsmngers):
      if print_plan:
        print 'nesting {} = {}'.format(k, dsmng)
      try:
        temp_plans = search_plans_for_one_nesting(query, dsmng)
      except NestingFailException as e:
        fail_nesting.append(dsmng)
        continue
      res = [ExecQueryStep(query, steps=steps) for steps in temp_plans]
      old_count = len(res)
      p = PlansForOneNesting(dsmng, res)
      for plan in res:
        new_dsmnger = dsmng.copy_tables()
        plan.get_used_ds(None, new_dsmnger)
        new_dsmnger.clear_placeholder()
        set_upperds_helper(new_dsmnger.data_structures)
        plan.copy_ds_id(None, new_dsmnger)
        if print_plan: 
          print 'PLAN {}'.format(cnt)
          print plan
          print 'plan cost = {}'.format(to_real_value(plan.compute_cost()))
          print '** struct:'
          print new_dsmnger
          print '=============\n'
          cnt += 1
      res = clean_lst([None if to_real_value(step.compute_cost()) > globalv.memory_bound else step for step in res])
      new_count = len(res)
      print 'pruned by memory bound: {} {}'.format(old_count, new_count)
      plans.append(p)
  # print '#Fail nestings: {}'.format(len(fail_nesting))
  # for i,f in enumerate(fail_nesting):
  #   print 'FAIL {}'.format(i)
  #   print f
  #   print '-----'
  print 'query plan search time = {}'.format(time.time()-start_time)
  return plans
