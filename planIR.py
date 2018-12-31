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
    self.cost = 0
    self.new_params = {k:v for k,v in new_params.items()}
    self.variables = []
    if compute_variables:
      self.variables = self.step.get_all_variables()
    #print 'Query step var length = {}'.format(len(self.variables))
  def __str__(self, short=False):
    s = 'prepare query {} (len param = {})\n'.format(self.query.id, len(self.new_params))
    s += '{}'.format(self.step.__str__(short=True))
    return s
  def to_json(self):
    variables = [x.to_json(full_dump=True) for x in self.variables]
    steps = self.step.to_json()
    return ("ExecQueryStep", {"queryid":self.query.id, "variables":variables, "steps":steps})
  def __eq__(self, other):
    return type(self) == type(other) and self.query == other.query
  def compute_cost(self):
    if cost_computed(self.cost):
      return self.cost
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
    dsmanager.clear_placeholder()
    return cur_obj
  def copy_ds_id(self, cur_obj, dsmanager):
    self.step.copy_ds_id(cur_obj, dsmanager)
    return cur_obj

class ExecSetVarStep(ExecStepSuper):
  def __init__(self, var, expr, cond=None, proj=[]):
    self.var = var
    self.expr = expr
    self.cond = cond
    self.cost = 1
    self.projections = proj
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
  def __str__(self, short=False):
    s = 'if ({}) {} = {}\n'.format(self.cond, self.var, self.expr)
    return s
  def fork(self):
    s = ExecSetVarStep(self.var, self.expr, self.cond)
    s.projections = [p for p in self.projections]
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
    #print 'self projection = {}'.format(len(self.projections))
    used_fields += self.projections
    for f in used_fields:
      if type(f) is not tuple:
        cur_obj.add_field(f)
    return cur_obj
  def copy_ds_id(self, cur_obj, dsmanager):
    self.get_used_ds(cur_obj, dsmanager)
    return cur_obj
  def get_all_variables(self):
    return [self.var]


# steps
class ExecStepSeq(ExecStepSuper):
  def __init__(self, steps=[]):
    self.steps = [s for s in steps]
    self.cost = 0
  def to_json(self):
    return ("ExecStepSeq", [s.to_json() for s in self.steps])
  def compute_cost(self, non_zero=False):
    if cost_computed(self.cost):
      return self.cost
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
  def __str__(self, short=False):
    return ''.join([s.__str__(short) for s in self.steps])
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
  def get_used_ds(self, cur_obj, dsmanager):
    obj = cur_obj
    for s in self.steps:
      obj = s.get_used_ds(obj, dsmanager)
    return cur_obj
  def copy_ds_id(self, cur_obj, dsmanager):
    obj = cur_obj
    for s in self.steps:
      obj = s.copy_ds_id(obj, dsmanager)
    return cur_obj
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
    self.cost = 0
  def fork(self):
    return ExecSortStep(self.var, self.order)
  def to_json(self):
    return ('ExecSortStep',{"var":"{}".format(self.var.to_json()), "order":[f.to_json() for f in self.order]})
  def compute_cost(self):
    if cost_computed(self.cost):
      return self.cost
    self.cost = CostOp(self.var.get_sz(), COST_MUL, CostLogOp(self.var.get_sz()))
    return self.cost
  def __str__(self, short=False):
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
  def copy_ds_id(self, cur_obj, dsmanager):
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
  def __str__(self, short=False):
    return 'Union [{}]'.format(','.join([str(v) for v in self.union_vars]))
  def to_json(self):
    return ('ExecUnionStep',{"returnv":self.return_var.to_json(), "union_vars":[], "aggrs":[(v.to_json(), f.to_json()) for v,f in self.aggrs],\
          "order":[f.to_json() for f in self.order]})
  def compute_cost(self):
    if cost_computed(self.cost):
      return self.cost
    if len(self.union_vars) == 1:
      return 1
    else:
      self.cost = self.union_vars[0].get_sz()
      for v in self.union_vars[1:]:
        self.cost = cost_add(self.cost, v.get_sz())
    return self.cost
  def get_used_ds(self, cur_obj, ds_manager):
    return cur_obj
  def copy_ds_id(self, cur_obj, dsmanager):
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
    self.cost = 0
    name = get_envvar_name()
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
    if self.idx and self.idx.value.is_object() and not isinstance(self.idx.table, NestedTable):
      return self.idx.table.sz
    return 1
  def template_eq(self, other):
    return self.__eq__(other)
  def __str__(self, short=False):
    return 'GetAssoc {} via {}\n'.format(self.field, self.idx.value.__str__(short) if self.idx else None)
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
      return cur_obj
    next_obj = None
    idx = self.idx.fork_without_memobj()
    if idx.value.is_object():
      next_obj = idx.value.get_object()
    elif idx.value.is_main_ptr():
      primary_ary = ds_manager.find_primary_array(get_main_table(idx.table))
      idx.value.value = primary_ary
      next_obj = primary_ary.value.get_object()
    if is_main_table(self.idx.table): # top level array/index
      ds_manager.add_ds(idx, replace=True) # add foreign key index
    else:
      assert(cur_obj)
      cur_obj.add_nested_object(idx, replace=True)
    return next_obj
  def copy_ds_id(self, cur_obj, dsmanager):
    if self.idx is None:
      cur_obj.add_field(self.field)
      return cur_obj
    eq_ds = None
    if is_main_table(self.idx.table):
      for ds in dsmanager.data_structures:
        if ds.eq_without_memobj(self.idx):
          eq_ds = ds
    else:
      for ds in cur_obj.nested_objects:
        if ds.eq_without_memobj(self.idx):
          eq_ds = ds
    assert(eq_ds)
    self.idx.id = eq_ds.id
    self.idx.upper = eq_ds.upper
    if self.idx.value.is_object():
      next_obj = eq_ds.value.get_object()
    else:
      primary_ary = dsmanager.find_primary_array(get_main_table(self.idx.table))
      next_obj = primary_ary.value.get_object()
    return next_obj
  def retrieves_field(self, f): 
    if self.idx is None:
      return self.field == f
    table = self.idx.table
    if self.field == f:
      return True
    if is_atomic_field(f):
      return table.contain_table(f.table)
    else:
      return table.contain_table(f.field_class)
  def get_all_variables(self):
    return []

# scan basic ary / associated obj (only 1 obj)
class ExecScanStep(ExecStepSuper):
  def __init__(self, idx):
    self.idx = idx
    self.ele_ops = ExecStepSeq() 
    self.cost = 0
    self.op = IndexOp(RANGE)
    self.params = []
  def fork(self):
    es = ExecScanStep(self.idx)
    es.ele_ops = self.ele_ops.fork()
    return es
  def to_json(self):
    return ('ExecScanStep', {"idx":self.idx.id, "steps":self.ele_ops.to_json()})
  def __eq__(self, other):
    return type(self) == type(other) and self.idx == other.idx and self.ele_ops == other.ele_ops
  def compute_cost(self):
    if cost_computed(self.cost):
      return self.cost
    if isinstance(self.idx, ObjBasicArray):
      element_cost = self.ele_ops.compute_cost()
      # FIXME: a constant for sequential memory access
      if self.idx.value.is_object():
        self.cost = CostOp(self.idx.compute_single_size(), COST_MUL, cost_minus(element_cost, 4))
      else:
        self.cost = CostOp(self.idx.compute_single_size(), COST_MUL, element_cost)
    else:
      assert(False)
    return self.cost
  def template_eq(self, other):
    return type(self) == type(other) and self.idx == other.idx
  def __str__(self, short=False):
    ele_s = '\n'.join(['  '+line for line in self.ele_ops.__str__(short).split('\n')])
    if isinstance(self.idx, ObjBasicArray):
      s = "Scan {} : \n{}\n".format(self.idx.__str__(short), ele_s)
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
      idx.value.value = primary_ary
      assert(primary_ary)
      # if primary_ary is None:
      #   primary_ary = create_primary_array(main_t)
      #   ds_manager.add_ds(primary_ary)
      next_obj = primary_ary.value.get_object()
    #else: # aggr
    self.ele_ops.get_used_ds(next_obj, ds_manager)
    return cur_obj
  def copy_ds_id(self, cur_obj, dsmanager):
    eq_ds = None
    if is_main_table(self.idx.table):
      for ds in dsmanager.data_structures:
        if ds.eq_without_memobj(self.idx):
          eq_ds = ds
    else:
      for ds in cur_obj.nested_objects:
        if ds.eq_without_memobj(self.idx):
          eq_ds = ds
    assert(eq_ds)
    self.idx.id = eq_ds.id
    self.idx.upper = eq_ds.upper
    if self.idx.value.is_object():
      next_obj = eq_ds.value.get_object()
    else:
      primary_ary = dsmanager.find_primary_array(get_main_table(self.idx.table))
      next_obj = primary_ary.value.get_object()
    self.ele_ops.copy_ds_id(next_obj, dsmanager)
    return cur_obj
  def get_all_variables(self):
    return self.ele_ops.get_all_variables()

class IndexOp(object):
  def __init__(self, op, left=CLOSE, right=CLOSE):
    self.op = op
    self.left = left
    self.right = right
  def __eq__(self, other):
    return self.op == other.op and self.left == other.left and self.right == other.right
  def is_range(self):
    return self.op==RANGE
  def is_point(self):
    return self.op==POINT
  def fork(self):
    return IndexOp(self.op, self.left, self.right)
  def __str__(self):
    if self.op == POINT:
      return 'point'
    else:
      return 'range{}{}'.format('[' if self.left == CLOSE else '(', ']' if self.right == CLOSE else ')')
# scan
class ExecIndexStep(ExecScanStep):
  def __init__(self, idx, idx_pred, idx_op, params):
    self.idx = idx
    self.op = idx_op
    self.params = params
    self.ele_ops = ExecStepSeq()
    self.idx_pred = idx_pred
    self.cost = 0
  def fork(self):
    e = ExecIndexStep(self.idx, self.idx_pred, self.op.fork(), self.params)
    e.ele_ops = self.ele_ops.fork() 
    return e 
  def __eq__(self, other):
    return type(self) == type(other) and \
            self.idx == other.idx and \
            self.op == other.op and \
            self.idx_pred == other.idx_pred and \
            self.ele_ops == other.ele_ops
  def template_eq(self, other):
    return type(self) == type(other) and self.idx_pred.template_eq(other.idx_pred) and self.idx.value == other.idx.value
  def __str__(self, short=False):
    ele_s = '\n'.join(['  '+line for line in self.ele_ops.__str__(short).split('\n')])
    param_s = ','.join([str(p) for p in self.params])
    s = "Index {} on [{}] (params = [{}]): \n{}\n".format(self.op, self.idx.__str__(short), param_s, ele_s)
    return s
  def compute_cost(self):
    if cost_computed(self.cost):
      return self.cost
    total_ele_cnt = self.idx.compute_single_size()
    lookup_cost = cost_mul(CostLogOp(total_ele_cnt), 2)
    element_cost = self.ele_ops.compute_cost()
    div_ratio = get_idx_op_cost_div(self.op, self.params)
    left_ele_cnt = CostOp(total_ele_cnt, COST_DIV, div_ratio)
    if isinstance(self.idx, ObjHashIndex):
      self.cost = CostOp(left_ele_cnt, COST_MUL, element_cost)
    else:
      self.cost = CostOp(lookup_cost, COST_ADD, CostOp(left_ele_cnt, COST_MUL, element_cost))
    return self.cost
  def compatible(self, other):
    return type(self) == type(other) and self.idx == other.idx and self.op == other.op \
          and self.params == other.params
    

class StepPlaceHolder(object):
  def __init__(self):
    self.name = 0
    self.is_temp = False
  def __str__(self):
    return 'step_placeholder'
  def get_used_ds(self, objstruct, struct_pool):
    assert(False)

