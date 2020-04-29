
import sys
sys.path.append('../')
from constants import *
from schema import *
from pred import *
from .codegen_helper import *
from ds import *
from planIR import *

from typing import *

CodegenState = 'CodegenState'
class CodegenState(object):
  def __init__(self, upper: Optional[CodegenState] = None):
    self.level: int = 0 if upper is None else upper.level + 1
    self.topquery: ReadQuery = None
    self.ds = None

    self.qr_varmap: Dict[EnvAtomicVariable, str] = {}
    self.ir_varmap: Dict[EnvAtomicVariable, str] = {}
    self.param_map: Dict[EnvAtomicVariable, str] = {}

    self.loop_var = None # if level == 0: loop_var is None
    self.qr_var = None # if level == 0: qr_var = 'qresult'
    
    self.upper = upper
    self.dsmnger: DSManager = None

  def fork(self) -> CodegenState:
    news = CodegenState(self.upper)
    news.qr_varmap = self.qr_varmap.copy()
    news.ir_varmap = self.ir_varmap.copy()
    news.ds = self.ds
    news.loop_var = self.loop_var
    news.qr_var = self.qr_var
    news.topquery = self.topquery
    news.param_map = self.param_map.copy()
    news.dsmnger = self.dsmnger
    return news

  def merge(self, other: CodegenState):
    k: EnvAtomicVariable
    v: str
    for k, v in list(other.qr_varmap.items()):
      if k not in self.qr_varmap:
        self.qr_varmap[k] = v

    for k, v in list(other.ir_varmap.items()):
      if k not in self.ir_varmap:
        self.ir_varmap[k] = v

  def find_ir_var(self, var: EnvAtomicVariable) -> str:
    if var in self.ir_varmap:
      return self.ir_varmap[var]
    if self.upper:
      return self.upper.find_ir_var(var)
    assert(False)

  def exist_ir_var(self, var: EnvAtomicVariable) -> bool:
    if var in self.ir_varmap:
      return True
    elif self.upper:
      return self.upper.exist_ir_var(var)
    return False

  def find_or_create_ir_var(self, var: EnvAtomicVariable) -> str:
    if var in self.ir_varmap:
      return self.ir_varmap[var]
    if self.upper and self.upper.exist_ir_var(var):
      return self.upper.find_ir_var(var)
    newv: str = cgen_cxxvar(var)
    self.ir_varmap[var] = newv
    return newv

  def find_qr_var(self, var: EnvAtomicVariable) -> str:
    if var in self.qr_varmap:
      return self.qr_varmap[var]
    for k,v in list(self.qr_varmap.items()):
      if var.name == k.name:
        return v
    if self.upper:
      return self.upper.find_ir_var(var)
    assert(False)

  def exist_qr_var(self, var: EnvAtomicVariable) -> bool:
    #if var in self.qr_varmap:
    #  return True
    for k,v in list(self.qr_varmap.items()):
      if var.name == k.name:
        return True
    if self.upper:
      return self.upper.exist_qr_var(var)
    return False

  def find_or_create_qr_var(self, var: EnvAtomicVariable) -> str:
    if var in self.qr_varmap:
      return self.qr_varmap[var]
    else:
      newv = cgen_cxxvar(var)
      self.qr_varmap[var] = newv
      return newv

  def find_param_var(self, param: EnvAtomicVariable) -> str:
    assert(param in self.param_map)
    return self.param_map[param]

  def get_queryfield_var(self, qf) -> str:
    assert(self.loop_var)
    return '{}.{}'.format(self.loop_var, cgen_fname(qf))

  def find_queryfield_or_param(self, v: Union[QueryField, Parameter, AtomValue]):
    if isinstance(v, QueryField):
      r = self.get_queryfield_var(v)
    elif isinstance(v, Parameter):
      r = self.find_param_var(v)
    elif isinstance(v, AtomValue):
      r = v.to_var_or_value()
    else:
      assert(False)
    assert(r)
    return r

  def order_maintained(self, target_order) -> bool:
    if target_order is None:
      return True
    if isinstance(self.ds, ObjBasicArray):
      return False
    range_keys = [k.key for k in self.ds.keys.range_keys]
    if all([o in range_keys for o in target_order]):
      return True

  def add_nextscope_state(self, step: ExecStepSuper) -> CodegenState:
    news = CodegenState(self)
    news.dsmnger = self.dsmnger
    news.topquery = self.topquery
    news.param_map = self.param_map
    if isinstance(step, ExecScanStep) or isinstance(step, ExecIndexStep):
      news.ds = step.idx
      # FIXME: set aggr vars??
    elif isinstance(step, ExecGetAssocStep):
      news.ds = step.idx
    return news
