from schema import *
from util import *
from constants import *
from pred import *
from query import *
from expr import *
from ds_manager import *
from planIR import *
import itertools

class PlansForOneNesting(object):
  def __init__(self, nesting, plans):
    self.nesting = nesting
    self.plans = plans
    self.merged_struct = StructPool()
  def compute_used_structs(self):
    for i in range(0, len(self.plans)):
      s = StructPool()
      plan = self.plans[i]
      plan.get_used_objstruct(None, s)
      self.plans[i] = (plan, s)
  def get_merged_struct(self):
    s = StructPool()
    for plan,struct in self.plans:
      s.merge(struct)
    return s
def from_plans_to_pair_nestings(qplans):
  plan_pairs = []
  nestings = []
  for qplan in qplans:
    qplan.compute_used_structs()
    plan_pairs += qplan.plans
    nestings += [qplan.nesting for i in range(0, len(qplan.plans))]
  return plan_pairs, nestings

class PlanTreesForOneNesting(object):
  def __init__(self, nesting, ptus):
    self.ptus = ptus
    self.nesting = nesting

class PlanTreeUnion(object):
  def __init__(self, plan_trees=[], steps=[]):
    self.steps = steps # steps to get union
    self.plan_trees = plan_trees
    self.var_init_steps = []
    if len(plan_trees) > 1:
      for a in self.aggr_vars:
        av_type = a[0].get_type()
        self.var_init_steps.append(ExecSetVarStep(a[0], AtomValue(get_init_value_by_type(av_type), av_type)))
    if self.pred_var:
      self.var_init_steps.append(ExecSetVarStep(self.pred_var, AtomValue(False, 'bool')))
  def fork(self):
    ptu = PlanTreeUnion(self.return_var, [v for  v in self.aggr_vars], self.pred_var, [p.fork() for p in self.plan_trees])
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
      return self.var_init_steps + self.plan_trees[0].to_steps()
    else:
      assert(len(self.plan_trees) > 1)
      step_seq = []
      for pt in self.plan_trees:
        step_seq = step_seq + pt.to_steps()
      step_seq += self.get_union_step()
      return self.var_init_steps + step_seq


class PlanTree(object):
  def __init__(self, return_var=None, aggr_vars=[], pred_var=None, pred_goal=None):
    self.return_var = return_var
    self.aggr_vars = aggr_vars
    self.pred_var = pred_var
    self.var_init_steps = []
    for a in self.aggr_vars:
      av_type = a[0].get_type()
      self.var_init_steps.append(ExecSetVarStep(a[0], AtomValue(get_init_value_by_type(av_type), av_type)))
    if self.pred_var:
      self.var_init_steps.append(ExecSetVarStep(self.pred_var, AtomValue(False, 'bool')))
    if self.return_var and self.return_var.is_temp:
      self.var_init_steps.append(ExecSetVarStep(self.return_var, None))
    self.index_step = None
    # the predicate that this plan tree is trying to answer
    self.pred_goal = pred_goal
    # element_steps include getting assoc fields, set vars, etc
    self.element_steps = []
    self.sort_step = None
    # next level key: qf; value: PlanTreeUnion
    self.next_level_pred = {}
    # next level key: qf; value: PlanTreeUnion
    self.next_level_query = {}
  def fork(self):
    pt = PlanTree(self.return_var, [v for v in self.aggr_vars], self.pred_var)
    pt.index_step = self.index_step.fork()
    pt.element_steps = [s.fork() for s in self.element_steps]
    pt.pred_goal = self.pred_goal
    pt.next_level_pred = {k:v.fork() for k,v in self.next_level_pred.items()}
    pt.next_level_query = {k:v.fork() for k,v in self.next_level_query.items()}
    if self.sort_step:
      pt.sort_step = self.sort_step.fork()
    return pt
  def to_steps(self):
    if isinstance(self.index_step, ExecGetAssocObjSuperStep):
      return self.var_init_steps + [self.index_step]
    idx_step = self.index_step.fork()
    ele_ops = []
    for k,v in self.next_level_pred.items():
      ele_ops += v.to_steps()
    for k,v in self.next_level_query.items():
      ele_ops += v.to_steps()
    ele_ops += self.element_steps
    idx_step.ele_ops.add_steps(ele_ops)
    if self.sort_step:
      return self.var_init_steps+[idx_step, self.sort_step]
    else:
      return self.var_init_steps+[idx_step]


def is_foreignkey_indexed(dsmanager, assoc_qf):
  keys, condition = helper_get_assoc_exist_idx(assoc_qf)
  for ds in dsmanager.data_structures:
    if isinstance(ds, IndexBase) and ds.condition.idx_pred_eq(condition):
      return idx 
  return None

def is_reverse_associated(table, assoc_qf):
  if isinstance(table, NestedTable) or assoc_qf is None:
    return None
  return helper_get_assoc_exist_idx(assoc_qf, for_scan_pred=True)[1]

def get_all_idxes_on_cond(value, keys, idx_pred):
  idxes = []
  table = value.get_object().table
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
        idxes.append(ObjTreeIndex(table, keys, idx_pred, value))
  else:
    if is_valid_idx_cond(idx_pred):
      idxes.append(ObjArray(table, idx_pred, value))
  return idxes

def search_steps_for_assoc(obj, dsmng, pred):
  if isinstance(pred, QueryField):
    if is_atomic_field(pred):
      return [ExecGetAssocStep(pred, None)]
    else:
      f = pred
  else:
    f = pred.lh
  steps = []
  o = obj.find_nested_obj_by_field(f)
  if o is None: # use id to retrieve
    foreignkey_idx = is_foreignkey_indexed(dsmng, f)
    if foreignkey_idx:
      steps.append(ExecGetAssocStep(f, foreignkey_idx))
      next_obj = foreignkey_idx.value.get_object()
    else:
      ary = dsmng.find_primary_array(f.field_class)
      steps.append(ExecGetAssocStep(f, ary))
      next_obj = ary.value.get_object()
  else:
    steps.append(ExecGetAssocStep(f, o))
    if o.value.is_main_ptr():
      next_obj = dsmng.find_primary_array(f.field_class).value.get_object()
  if isinstance(pred, AssocOp):
    steps = steps + search_steps_for_assoc(next_obj, dsmng, pred.rh)
  return steps
  
        
