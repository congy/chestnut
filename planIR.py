from util import *
from constants import *
from pred import *
from query import *
from ds import *
from pred_cost import *
from ds_manager import *
from ds_helper import *
from nesting import *
import globalv

class ExecStepSuper(object):
  def compatible(self, other):
    return type(self) == type(other)

class ExecQueryStep(ExecStepSuper):
  def __init__(self, query, steps=[], new_params={}, compute_variables=True):
    self.query = query
    self.step = ExecStepSeq(steps)
    self.cost = 1
    self.new_params = {k:v for k,v in new_params.items()}
    self.variables = []
    if compute_variables:
      self.variables = self.step.get_all_variables()
    #print 'Query step var length = {}'.format(len(self.variables))
  def __str__(self):
    s = 'prepare query {} (len param = {})\n'.format(self.query.id, len(self.new_params))
    globalv.set_ds_short_print(True)
    s += '{}'.format(self.step)
    globalv.set_ds_short_print(False)
    return s
  def to_json(self):
    variables = [x.to_json(full_dump=True) for x in self.variables]
    steps = self.step.to_json()
    return ("ExecQueryStep", {"queryid":self.query.id, "variables":variables, "steps":steps})
  def __eq__(self, other):
    return type(self) == type(other) and self.query == other.query
  def compute_cost(self):
    self.cost = self.step.compute_cost()
    return self.cost
  def fork(self):
    e = ExecQueryStep(self.query, self.new_params)
    e.step = self.step.fork() if self.step else None
    assert(len(self.new_params) == 0)
    return e
  def get_read_queries(self):
    if isinstance(self.query, ReadQuery):
      return [self.query] + self.step.get_read_queries()
    else:
      return self.step.get_read_queries()
  def contain_set_entryobj_var(self):
    return self.step.contain_set_entryobj_var()
  def get_most_inner_step(self, check_setvar=True):
    return self.step.get_most_inner_step(check_setvar)
  def get_used_ds(self, cur_obj, dsmanager):
    self.step.get_used_ds(cur_obj, dsmanager)
    return cur_obj

class ExecSetVarStep(ExecStepSuper):
  def __init__(self, var, expr, cond=None):
    self.var = var
    self.expr = expr
    self.cond = cond
    self.cost = 1
  def __eq__(self, other):
    var_eq = False
    expr_eq = False
    cond_eq = False
    if self.var == other.var:
      var_eq = True
    if self.expr == None and other.expr == None:
      expr_eq = True
    elif self.expr.query_pred_eq(other.expr):
      expr_eq = True
    if self.cond.query_pred_eq(other.cond):
      cond_eq = True
    return var_eq and expr_eq and cond_eq
  def to_json(self):
    return ("ExecSetVarStep",{"var":self.var.to_json(), \
                "expr":self.expr.to_json() if self.expr else None, \
                "cond":self.cond.to_json() if self.cond else None})
  def compute_cost(self):
    return self.cost
  def __str__(self):
    s = 'if ({}) {} = {}\n'.format(self.cond, self.var, self.expr)
    return s
  def fork(self):
    s = ExecSetVarStep(self.var, self.expr, self.cond)
    return s
  def get_read_queries(self):
    return []
  def contain_set_entryobj_var(self):
    return isinstance(self.var, EnvCollectionVariable) or isinstance(self.var, StepPlaceHolder)
  def get_most_inner_step(self, check_setvar=True):
    return self
  def get_used_ds(self, cur_obj, dsmanager):
    used_fields = []
    if self.cond:
      used_fields += get_curlevel_fields(self.cond)
    if self.expr:
      used_fields += get_curlevel_fields(self.expr)
    for f in used_fields:
      cur_obj.add_field(f)
    return cur_obj
  def get_all_variables(self):
    return [self.var]

# steps
class ExecStepSeq(ExecStepSuper):
  def __init__(self, steps=[]):
    self.steps = [s for s in steps]
    self.cost = None
  def to_json(self):
    return ("ExecStepSeq", [s.to_json() for s in self.steps])
  def compute_cost(self, non_zero=False):
    c = 0 
    for i in range(0, len(self.steps)):
      c = CostOp(c, COST_ADD, self.steps[i].compute_cost())
    if type(c) is int and non_zero:
      c = 1
    self.cost = c
    return c
  def is_empty(self):
    return len(self.steps) == 0
  def fork(self):
    d = ExecStepSeq()
    for s in self.steps:
      d.steps.append(s.fork())
    return d
  def __eq__(self, other):
    return type(self) == type(other) and \
      len(self.steps) == len(other.steps) and \
      all([self.steps[i] == other.steps[i] for i in range(0, len(self.steps))])
  def add_step(self, s):
    self.steps.append(s)
    assert(all([type(s) is not list for s in self.steps]))
  def add_steps(self, s):
    self.steps = self.steps + s
    assert(all([type(s) is not list for s in self.steps]))
  def __str__(self):
    return ''.join([str(s) for s in self.steps])
  def merge_step(self, other):
    step_to_remove = []
    for i in range(0, len(self.steps)):
      for j in range(0, len(other.steps)):
        if self.steps[i].compatible(other.steps[j]):
          step_to_remove.append(j)
          self.steps[i].merge_step(other.steps[j].fork())
    for i in range(0, len(other.steps)):
      if i not in step_to_remove:
        self.steps.append(other.steps[i].fork())
  def get_read_queries(self):
    r = []
    for s in self.steps:
      r += s.get_read_queries()
    return r
  def contain_set_entryobj_var(self):
    for s in self.steps:
      if s.contain_set_entryobj_var():
        return True
    return False
  def get_most_inner_step(self, check_setvar=True):
    for s in self.steps:
      if isinstance(s, ExecScanStep) or isinstance(s, ExecIndexStep) or isinstance(s, ExecGetAssocObjSuperStep) or isinstance(s, ExecGetAssocObjStep) or \
            isinstance(s, ExecConditionStep) or isinstance(s, ExecStepSeq):
        if check_setvar==False or s.contain_set_entryobj_var():
          return s.get_most_inner_step(check_setvar)
    return self
  def get_used_ds(self, cur_obj, struct_pool):
    obj = cur_obj
    for s in self.steps:
      obj = s.get_used_ds(obj, struct_pool)
    return obj
  def get_all_variables(self):
    r = []
    for s in self.steps:
      r1 = s.get_all_variables()
      for v in r1:
        if not any([v==vr for vr in r]):
          r.append(v)
    return r

# sort result 
class ExecSortStep(ExecStepSuper):
  def __init__(self, var, order):
    self.order = order
    self.var = var
    self.cost = None
  def fork(self):
    return ExecSortStep(self.var, self.order)
  def to_json(self):
    return ('ExecSortStep',{"var":"{}".format(self.var.to_json()), "order":[f.to_json() for f in self.order]})
  def compute_cost(self):
    self.cost = CostOp(self.var.get_sz(), COST_MUL, CostLogOp(self.var.get_sz()))
    return self.cost
  def __str__(self):
    return 'Sort on {}: ({})\n'.format(self.var, ','.join([str(o) for o in self.order]))
  def __eq__(self, other):
    return type(self) == type(other) and set_equal(self.order, other.order) and self.table == other.table
  def compatible(self, other):
    return False
  def get_read_queries(self):
    return []
  def get_most_inner_step(self, check_setvar=True):
    return self
  def contain_set_entryobj_var(self):
    return False
  def get_used_ds(self, cur_obj, ds_manager):
    return cur_obj
  def get_all_variables(self):
    return []

class ExecUnionStep(ExecStepSuper):
  def __init__(self, return_var=None, aggrs=[], union_vars=[], order=None):
    self.return_var = return_var
    self.aggrs = aggrs
    self.union_vars = union_vars
    self.order = order
    # if len(self.union_vars) == 1: just reset query result (add distinct??)
    # if query.order: merge sort
    # recompute aggrs
    self.cost = 0
  def __str__(self):
    return 'Union [{}]'.format(','.join([str(v) for v in self.union_vars]))
  def to_json(self):
    return ('ExecUnionStep',{"returnv":self.return_var.to_json(), "union_vars":[], "aggrs":[(v.to_json(), f.to_json()) for v,f in self.aggrs],\
          "order":[f.to_json() for f in self.order]})
  def compute_cost(self):
    if len(self.union_vars) == 1:
      return 1
    else:
      self.cost = self.union_vars[0].get_sz()
      for v in self.union_vars[1:]:
        self.cost = cost_add(self.cost, v.get_sz())
    return self.cost
  def get_used_ds(self, cur_obj, ds_manager):
    return cur_obj
  def fork(self):
    s = ExecUnionStep(self.return_var, [v for v in self.aggrs], [v for v in self.union_vars], self.order)
    return s
  def get_all_variables(self):
    return [self.return_var]

class ExecGetAssocStep(ExecStepSuper):
  def __init__(self, field, idx):
    self.field = field
    self.idx = idx # can be nested object (BasicArray), FK index, or main_obj (scan to find a match)
    self.cost = None
    name = get_envvar_name(f)
    self.var = EnvAtomicVariable(name, field.get_type())
  def fork(self):
    es = ExecGetAssocStep(self.field, self.idx)
    es.var = self.var
    return es
  def to_json(self):
    # TODO
    pass
  def __eq__(self, other):
    return type(self) == type(other) and self.field == other.field and self.idx == other.idx
  def compute_cost(self):
    # TODO
    self.cost = 1
    return 1
  def template_eq(self, other):
    return self.__eq__(other)
  def __str__(self):
    return 'GetAssoc {} via {}\n'.format(self.field, self.idx.value)
  def compatible(self, other):
    return self.__eq__(other)
  def get_read_queries(self):
    return []
  def contain_set_entryobj_var(self):
    return False
  def get_most_inner_step(self, check_setvar=True):
    return self
  def get_used_ds(self, cur_obj, ds_manager):
    if self.idx is None:
      cur_obj.add_field(self.field)
      return
    next_obj = None
    idx = self.idx.fork_without_memobj()
    assert(cur_obj is not None)
    if idx.value.is_object():
      next_obj = idx.value.get_object()
    elif idx.value.is_main_ptr():
      primary_ary = ds_manager.find_primary_array(self.field.field_class)
      next_obj = primary_ary.value.get_object()
    return next_obj
  def get_all_variables(self):
    return []

# scan basic ary / associated obj (only 1 obj)
class ExecScanStep(ExecStepSuper):
  def __init__(self, idx):
    self.idx = idx
    self.ele_ops = ExecStepSeq() 
    self.cost = None
  def fork(self):
    es = ExecScanStep(self.idx)
    es.ele_ops = self.ele_ops.fork()
    return es
  def to_json(self):
    return ('ExecScanStep', {"idx":self.idx.id, "steps":self.ele_ops.to_json()})
  def __eq__(self, other):
    return type(self) == type(other) and self.idx == other.idx and self.ele_ops == other.ele_ops
  def compute_cost(self):
    if isinstance(self.idx, ObjBasicArray):
      element_cost = self.ele_ops.compute_cost()
      # FIXME: a constant for sequential memory access
      if self.idx.value.is_object():
        self.cost = CostOp(self.idx.table.get_sz_for_cost(), COST_MUL, cost_minus(element_cost, 4))
      else:
        self.cost = CostOp(self.idx.table.get_sz_for_cost(), COST_MUL, element_cost)
    else:
      assert(False)
    return self.cost
  def template_eq(self, other):
    return type(self) == type(other) and self.idx == other.idx
  def __str__(self):
    ele_s = '\n'.join(['  '+line for line in str(self.ele_ops).split('\n')])
    if isinstance(self.idx, ObjBasicArray):
      s = "Scan {} : \n{}\n".format(self.idx, ele_s)
    elif isinstance(self.idx, ReadQuery):
      s = "Scan on result {} : \n{}\n".format(self.idx.return_var.name, ele_s)
    else:
      assert(False)
    return s
  def compatible(self, other):
    return type(self) == type(other) and self.idx == other.idx
  def add_step(self, step):
    self.ele_ops.add_step(step)
  def merge_step(self, other):
    assert(self.compatible(other))
    self.ele_ops.merge_step(other.ele_ops)
  def get_read_queries(self):
    return self.ele_ops.get_read_queries()
  def contain_set_entryobj_var(self):
    return self.ele_ops.contain_set_entryobj_var()
  def get_most_inner_step(self, check_setvar=True):
    return self.ele_ops.get_most_inner_step(check_setvar)
  def get_used_ds(self, cur_obj, ds_manager):
    next_obj = None
    idx = self.idx.fork_without_memobj()
    if is_main_table(self.idx.table): # top level array/index
      ds_manager.add_ds(idx, replace=True)
    else:
      assert(cur_obj)
      cur_obj.add_nested_object(idx, replace=True)
    if idx.value.is_object():
      next_obj = idx.value.get_object()
    elif idx.value.is_main_ptr():
      main_t = get_main_table(idx.table)
      primary_ary = ds_manager.find_primary_array(main_t)
      assert(primary_ary)
      # if primary_ary is None:
      #   primary_ary = create_primary_array(main_t)
      #   ds_manager.add_ds(primary_ary)
      next_obj = primary_ary.value.get_object()
    #else: # aggr
    self.ele_ops.get_used_ds(next_obj, ds_manager)
    return cur_obj
  def get_all_variables(self):
    return self.ele_ops.get_all_variables()

# scan
class ExecIndexStep(ExecScanStep):
  def __init__(self, idx, idx_pred, idx_op_type, params):
    self.idx = idx
    self.idx_op_type = idx_op_type
    self.params = params
    self.ele_ops = ExecStepSeq()
    self.idx_pred = idx_pred
  def to_json(self):
    return ('ExecIndexStep', {"idx":self.idx.id, "steps":self.ele_ops.to_json(), "params":[p.to_json() for p in self.params], \
          "op-type":'range' if self.idx_op_type == RANGE else 'point', "idx-pred":self.idx_pred.to_json() if self.idx_pred else None})
  def fork(self):
    e = ExecIndexStep(self.idx, self.idx_pred, self.idx_op_type, self.params)
    e.ele_ops = self.ele_ops.fork() 
    return e 
  def __eq__(self, other):
    return type(self) == type(other) and \
            self.idx == other.idx and \
            self.idx_op_type == other.idx_op_type and \
            self.idx_pred == other.idx_pred and \
            self.ele_ops == other.ele_ops
  def template_eq(self, other):
    return type(self) == type(other) and self.idx_pred.template_eq(other.idx_pred) and self.idx.value == other.idx.value
  def __str__(self):
    ele_s = '\n'.join(['  '+line for line in str(self.ele_ops).split('\n')])
    param_s = ','.join([str(p) for p in self.params])
    s = "Index {} on [{}] (params = [{}]): \n{}\n".format(index_type_to_str[self.idx_op_type], self.idx, param_s, ele_s)
    return s
  def compute_cost(self):
    total_ele_cnt = self.idx.compute_size()
    if self.idx_pred:
      filter_ratio = get_div_ratio_by_pred(self.idx_pred) 
    else:
      filter_ratio = 1
    ele_cost = self.ele_ops.compute_cost(non_zero=True)
    lookup_cost = CostLogOp(total_ele_cnt)
    if is_type_or_subtype(self.idx, ObjHashIndex):
      self.cost = CostOp(CostOp(total_ele_cnt, COST_DIV, filter_ratio), COST_MUL, ele_cost)
    else:
      self.cost = CostOp(lookup_cost, COST_ADD, CostOp(CostOp(total_ele_cnt, COST_DIV, filter_ratio), COST_MUL, ele_cost))
    return self.cost
  def compatible(self, other):
    return type(self) == type(other) and self.idx == other.idx and self.idx_op_type == other.idx_op_type \
          and self.params == other.params
    

class StepPlaceHolder(object):
  def __init__(self):
    self.name = 0
    self.is_temp = False
  def __str__(self):
    return 'step_placeholder'
  def get_used_ds(self, objstruct, struct_pool):
    assert(False)

