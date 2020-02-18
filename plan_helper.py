from schema import *
from util import *
from constants import *
from pred import *
from query import *
from expr import *
from ds_manager import *
from ds_helper import *
from planIR import *
from symbolic_ds import *
import itertools
import globalv

# Nestings have different types of data structures.
# Therefore one nesting has multiple plan/datastructures.
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
  def __init__(self, plan_trees: ['PlanTree'] = []):
    self.plan_trees: ['PlanTree'] = plan_trees # Surely plan_trees is a list of PlanTree.
    self.after_steps: [ExecStepSuper] = [] # Unsure about type.
  def fork(self) -> 'PlanTreeUnion':
    ptu = PlanTreeUnion([p.fork() for p in self.plan_trees])
    ptu.after_steps = [s.fork() for s in self.after_steps]
    return ptu
  def to_steps(self) -> [ExecStepSuper]:
    s: [ExecStepSuper] = []
    for pt in self.plan_trees:
      s += pt.to_steps()
    s += self.after_steps
    return s

class PlanTree(object):
  def __init__(self):
    self.pre_steps: [ExecStepSuper] = [] # Not 100% sure about type.
    self.index_step = None
    self.sort_step = None
    # element_steps include getting assoc fields, set vars, etc
    self.assoc_pred_steps = []
    self.assoc_query_steps = []
    self.setv_steps = []
    # next level key: qf; value: PlanTreeUnion
    self.next_level_pred = {}
    # next level key: qf; value: PlanTreeUnion
    self.next_level_query = {}

  def fork(self):
    pt = PlanTree()
    pt.index_step = self.index_step.fork()
    pt.sort_step = self.sort_step
    pt.pre_steps = [s for s in self.pre_steps]
    pt.assoc_pred_steps = [s.fork() for s in self.assoc_pred_steps]
    pt.assoc_query_steps = [s.fork() for s in self.assoc_query_steps]
    pt.setv_steps = [s.fork() for s in self.setv_steps]
    pt.next_level_pred = {k:v.fork() for k,v in list(self.next_level_pred.items())}
    pt.next_level_query = {k:v.fork() for k,v in list(self.next_level_query.items())}
    return pt

  def find_retrieve_assoc_step(self, field, query=False):
    ary = self.assoc_query_steps if query else self.assoc_pred_steps 
    for s in ary:
      fields = get_fields_from_assocop(field)
      if len(s.steps) <= len(fields) and all([s.steps[i].field == fields[i] for i in range(0, len(s.steps))]):
        return s
    assert(False)

  def to_steps(self) -> [ExecStepSuper]:
    idx_step = self.index_step.fork()
    # assoc_pred_steps
    # nextlevel pred
    # setv
    # assoc query steps
    # nextlevel query
    ele_ops = [s for s in self.assoc_pred_steps]
    for k,v in list(self.next_level_pred.items()):
      if is_assoc_field(k):
        s = self.find_retrieve_assoc_step(k)
        s.add_steps(v.to_steps())
      else:
        ele_ops += v.to_steps()
    ele_ops += self.setv_steps
    ele_ops += self.assoc_query_steps
    for k,v in list(self.next_level_query.items()):
      if is_assoc_field(k):
        s = self.find_retrieve_assoc_step(k, True)
        s.add_steps(v.to_steps())
      else:
        ele_ops += v.to_steps()
    idx_step.ele_ops.add_steps(ele_ops)
    # if len(self.pre_steps):
    #   print(f'TYPE: {type(self.pre_steps[0])}')
    # print(f'TYPE: {type(idx_step)}')
    # print(f'TYPE: {type(self.sort_step)}')
    # print('!!DONE!!')
    if self.sort_step:
      return self.pre_steps + [idx_step, self.sort_step]
    else:
      return self.pre_steps + [idx_step]

class NestingFailException(Exception):
  def __init__(self, message):
    super(NestingFailException, self).__init__(message)

def get_initvar_steps(aggrs, preds, arrays=[]):
  steps = []
  for a in aggrs:
    av_type = a.get_type()
    steps.append(ExecSetVarStep(a, AtomValue(get_init_value_by_type(av_type), av_type)))
  for p in preds:
    steps.append(ExecSetVarStep(p, AtomValue(False, 'bool')))
  for a in arrays:
    steps.append(ExecSetVarStep(a, 'init'))
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
        try:
          ary = dsmng.find_placeholder(f.field_class)
          steps.append(ExecGetAssocStep(f, ObjBasicArray(ary.table, ary.value)))
        except:
          raise NestingFailException('place1')
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

def set_upperds_helper(ds_lst, upperds=None):
  for ds in ds_lst:
    ds.upper = upperds
    if ds.value.is_object():
      set_upperds_helper(ds.value.get_object().nested_objects, ds)
