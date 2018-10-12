from schema import *
from util import *
from constants import *
from pred import *
from query import *
from expr import *
from ds_manager import *
from ds_helper import *
from planIR import *
import itertools

class PlansForOneNesting(object):
  def __init__(self, nesting, plans):
    self.nesting = nesting
    self.plans = plans
    self.dsmanagers = []
  def compute_used_structs(self):
    pass
  
class PlanTreesForOneNesting(object):
  def __init__(self, nesting, ptus):
    self.ptus = ptus
    self.nesting = nesting

class PlanTreeUnion(object):
  def __init__(self, plan_trees=[]):
    self.plan_trees = plan_trees
    self.after_steps = []
  def fork(self):
    ptu = PlanTreeUnion([p.fork() for p in self.plan_trees])
    ptu.after_steps = [s.fork() for s in self.after_steps]
    return ptu
  # def get_union_step(self):
  #   if len(self.plan_trees) == 1:
  #     return None
  #   else:
  #     if self.plan_trees[0].return_var is not None:
  #       union_steps = [ExecUnionStep(self.return_var, self.aggr_vars, [pt.return_var for pt in self.plan_trees])]
  #     elif self.pred_var is not None:
  #       expr = ConnectOp(self.plan_trees[0].pred_var, OR, self.plan_trees[1].pred_var)
  #       for pt in self.plan_trees[2:]:
  #         expr = ConnectOp(pt.pred_var, OR, expr)
  #       union_steps = [ExecSetVarStep(self.pred_var, expr, cond=None)]
  #     elif len(self.plan_trees[0].aggr_vars) > 0:
  #       union_steps = []
  #       for i,v in enumerate(self.aggr_vars):
  #         # FIXME
  #         expr = BinaryExpr(self.plan_trees[0].aggr_vars[i][0], ADD, self.plan_trees[1].aggr_vars[i][0])
  #         for pt in self.plan_trees[2:]:
  #           expr = BinaryExpr(pt.aggr_vars[i][0], ADD, expr)
  #         expr = UnaryExpr(SUM, expr)
  #         union_steps.append(ExecSetVarStep(v[0], expr, cond=None))
  #     else:
  #       assert(False)
  #     return union_steps
  def to_steps(self):
    if len(self.plan_trees) == 1:
      return self.plan_trees[0].to_steps() + self.after_steps
    else:
      s = []
      for pt in self.plan_trees:
        s += pt.to_steps()
      s += self.after_steps
      return s


class PlanTree(object):
  def __init__(self, pred=None):
    self.pre_steps = []
    self.pred_goal = pred
    self.index_step = None
    self.sort_step = None
    # element_steps include getting assoc fields, set vars, etc
    self.element_steps = []
    # next level key: qf; value: PlanTreeUnion
    self.next_level_pred = {}
    # next level key: qf; value: PlanTreeUnion
    self.next_level_query = {}
  def fork(self):
    pt = PlanTree()
    pt.index_step = self.index_step.fork()
    pt.sort_step = self.sort_step
    pt.element_steps = [s.fork() for s in self.element_steps]
    pt.pred_goal = self.pred_goal
    pt.next_level_pred = {k:v.fork() for k,v in self.next_level_pred.items()}
    pt.next_level_query = {k:v.fork() for k,v in self.next_level_query.items()}
    return pt
  def find_retrieve_assoc_step(self, field):
    for s in self.element_steps:
      if isinstance(s, ExecStepSeq) and s.steps[-1].retrieves_field(get_query_field(field)):
        return s
    assert(False)
  def to_steps(self):
    idx_step = self.index_step.fork()
    ele_ops = []
    for k,v in self.next_level_pred.items():
      if is_assoc_field(k):
        s = self.find_retrieve_assoc_step(k)
        s.add_steps(v.to_steps())
      else:
        ele_ops += v.to_steps()
    for k,v in self.next_level_query.items():
      if is_assoc_field(k):
        s = self.find_retrieve_assoc_step(k)
        s.add_steps(v.to_steps())
      else:
        ele_ops += v.to_steps()
    ele_ops += self.element_steps
    idx_step.ele_ops.add_steps(ele_ops)
    if self.sort_step:
      return self.pre_steps + [idx_step, self.sort_step]
    else:
      return self.pre_steps + [idx_step]

def get_initvar_steps(aggrs, preds):
  steps = []
  for a in aggrs:
    av_type = a.get_type()
    steps.append(ExecSetVarStep(a, AtomValue(get_init_value_by_type(av_type), av_type)))
  for p in preds:
    steps.append(ExecSetVarStep(p, AtomValue(False, 'bool')))
  return steps

def is_foreignkey_indexed(dsmanager, assoc_qf):
  if assoc_qf is None:
    return None
  keys, condition = helper_get_assoc_exist_idx(assoc_qf)
  for ds in dsmanager.data_structures:
    if isinstance(ds, IndexBase) and ds.condition.idx_pred_eq(condition):
      return ds
  return None

def is_reverse_associated(table, assoc_qf):
  if isinstance(table, NestedTable) or assoc_qf is None:
    return None
  return helper_get_assoc_exist_idx(assoc_qf, for_scan_pred=True)[1]

def get_all_idxes_on_cond(idx_placeholder, keys, idx_pred):
  idxes = []
  table = idx_placeholder.table
  value = idx_placeholder.value
  # FIXME: For efficiency reasons, do not include basic array...
  #if is_valid_idx_cond(idx_pred):
  #  idxes.append(ObjSortedArray(table, keys, idx_pred, value=value_type))
  if len(keys) > 0:
    # if is_valid_idx_cond(idx_pred, hash_idx=True):
    #   idxes.append(ObjHashIndex(table, keys, idx_pred, value=value_type))
    if is_valid_idx_cond(idx_pred):
      if isinstance(table, NestedTable):
        idxes.append(ObjSortedArray(table, keys, idx_pred, value))
      else:
        idxes.append(ObjSortedArray(table, keys, idx_pred, value))
        idxes.append(ObjTreeIndex(table, keys, idx_pred, MAINPTR))
  else:
    if is_valid_idx_cond(idx_pred):
      if isinstance(table, NestedTable):
        idxes.append(ObjArray(table, idx_pred, value))
      else:
        idxes.append(ObjArray(table, idx_pred, value))
        idxes.append(ObjArray(table, idx_pred, MAINPTR))
  return idxes

def search_steps_for_assoc(obj, dsmng, pred):
  if isinstance(pred, QueryField):
    if is_atomic_field(pred):
      assert(get_main_table(obj.table).contain_table(pred.table))
      return [ExecGetAssocStep(pred, None)]
    else:
      f = pred
  else:
    f = pred.lh
  steps = []
  #print 'obj.table = {}, contain_table = {} {}'.format(obj.table.get_full_type(), f.field_class, obj.table.contain_table(f.field_class))
  if obj.table.contain_table(f.field_class):
    next_obj = obj
  else:
    o = obj.find_nested_obj_by_field(f)
    #print 'find nested: o = {}'.format(o)
    if o is None: # use id to retrieve
      foreignkey_idx = is_foreignkey_indexed(dsmng, f)
      #print 'foreign key? {}'.format(foreignkey_idx)
      if foreignkey_idx:
        ary = dsmng.find_placeholder(foreignkey_idx.table)
        steps.append(ExecGetAssocStep(f, foreignkey_idx))
      else:
        ary = dsmng.find_placeholder(f.field_class)
        steps.append(ExecGetAssocStep(f, ObjBasicArray(ary.table, ary.value)))
      next_obj = ary.value.get_object()
    else:
      steps.append(ExecGetAssocStep(f, ObjBasicArray(o.table, o.value)))
      if o.value.is_main_ptr():
        next_obj = dsmng.find_placeholder(f.field_class).value.get_object()
      else:
        next_obj = o.value.get_object()
  if isinstance(pred, AssocOp):
    steps = steps + search_steps_for_assoc(next_obj, dsmng, pred.rh)
  return steps

def find_next_idx_placeholder(idx_placeholder, dsmng, field):
  if idx_placeholder.table.contain_table(field.field_class):
    return idx_placeholder
  cur_obj = idx_placeholder.value.get_object()
  foreignkey_idx = is_foreignkey_indexed(dsmng, field)
  if foreignkey_idx:
    return dsmng.find_placeholder(foreignkey_idx.table)
  next_ds = cur_obj.find_nested_obj_by_field(field)
  if next_ds:
    return next_ds
  else:
    return dsmng.find_placeholder(field.field_class)

def rewrite_pred_for_denormalized_table(pred, table):
  if not isinstance(table, DenormalizedTable) or pred is None:
    return pred
  clauses = pred.split()
  has_change = True
  while has_change:
    has_change = False
    temp_clauses = [c for c in clauses]
    for i,c in enumerate(temp_clauses):
      if isinstance(c, SetOp):
        if is_assoc_field(c.lh) and table.contain_table(c.lh.lh.field_class):
          clauses.pop(i)
          clauses.append(SetOp(c.lh.rh, c.op, c.rh))
          has_change = True
        elif (not is_assoc_field(c.lh)) and table.contain_table(c.lh.field_class):
          clauses.pop(i)
          clauses = clauses + c.rh.split()
          has_change = True
        if has_change:
          break
  new_pred = merge_into_cnf(clauses)
  #print 'REWRITE: table = {}, old = {}, new = {}'.format(table.get_full_type(), pred, new_pred)
  return new_pred

def add_order_to_idx(idx_step, order):
  if not all([isinstance(o.field_class, Field) for o in order]):
    return None
  if isinstance(idx_step, ExecScanStep):
    idx_pred = BinOp(order[0], EQ, Parameter('order_{}'.format(order[0].field_name)))
    for o in order[1:]:
      idx_pred = ConnectOp(BinOp(o, EQ, Parameter('order_{}'.format(o.field_name))), AND, idx_pred)
    new_idx = ObjTreeIndex(idx_step.idx.table, order, idx_pred, value=idx_step.idx.value)
    r_params = get_order_param(order)
    new_idx_step = ExecIndexStep(new_idx, None, RANGE, r_params)
    return new_idx_step
  elif idx_step.idx_op_type == POINT and not isinstance(idx_step.idx, ObjHashIndex):
    if len(idx_step.idx.keys) > len(order) and all([o==idx_step.idx.keys[i] for i,o in enumerate(order)]):
      return idx_step.fork()
    new_idx, op, params = merge_order_pred(idx_step.idx, order)
    old_param = idx_step.params
    if len(idx_step.idx.keys) > 0:
      new_params = [old_param[0].fork().merge(params[0]), old_param[0].fork().merge(params[1])]
    else:
      new_params = [params[0], params[1]]
    assert(len(new_params[0].fields) == len(new_idx.keys))
    new_idx_step = ExecIndexStep(new_idx, idx_step.idx_pred, op, new_params)
    return new_idx_step
  else:
    return None

  
# used to filter out bad plans
class OptimizerGoalTree(object):
  def __init__(self):
    self.pred_pts_pairs = [] # (pred, [plan_tree])
    self.next_level = {}
  def merge(self, other):
    for k,v in other.pred_pts_pairs:
      for k1, v1 in self.pred_pts_pairs:
        if k.idx_pred_eq(k1):
          v1.append(v)
    for k,v in other.next_level.items():
      if k not in self.next_level:
        self.next_level[k] = v
      else:
        self.next_level[k].merge(v)
  def check_valid(self):
    for pred, plan_trees in self.pred_pts_pairs:
      for plan_tree in plan_trees[1:]:
        if not plan_tree.index_step.template_eq(plan_trees[0].index_step):
          #print 'p1 step = {}'.format(plan_tree.index_step)
          #print 'p2 step = {}'.format(plan_trees[0].index_step)
          return False
    for k,v in self.next_level.items():
      if not v.check_valid():
        return False
    return True
  def __str__(self):
    s = ''
    for pred, plan_trees in self.pred_pts_pairs:
      s += 'pred: {}, plan_trees = {}'.format(pred, '\n'.join(['    * {}'.format(plan_tree.index_step) for plan_tree in plan_trees]))
    for k,v in self.next_level.items():
      s += 'next level {}'.format(k)
      s += ''.join(['  '+l+'\n' for l in str(v).split('\n')])
    return s


def to_optimizer_goal_tree(ptus):
  gt = OptimizerGoalTree()
  next_level_ptus = {}
  for ptu in ptus:
    for plan_tree in ptu.plan_trees:
      pred_goal = plan_tree.pred_goal
      exist = False
      if pred_goal is not None:
        for k,v in gt.pred_pts_pairs:
          if k.template_eq(pred_goal):
            v.append(plan_tree)
            exist = True
      if not exist:
        gt.pred_pts_pairs.append((pred_goal, [plan_tree]))
      for k,v in plan_tree.next_level_pred.items():
        if k not in next_level_ptus:
          next_level_ptus[k] = [v]
        else:
          next_level_ptus[k].append(v)
      for k,v in plan_tree.next_level_query.items():
        if k not in next_level_ptus:
          next_level_ptus[k] = [v]
        else:
          next_level_ptus[k].append(v)
  for k,v in next_level_ptus.items():
    gt.next_level[k] = to_optimizer_goal_tree(v)
  return gt



def is_opt_out_plan(ptu):
  gt = to_optimizer_goal_tree([ptu])
  # print "\n\n-- GT :"
  # print gt
  r = gt.check_valid()
  # print 'GT VALID: {}'.format(r)
  # if not r:
  #   exit(0)
  return (not r)