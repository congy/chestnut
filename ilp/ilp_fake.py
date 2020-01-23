import enum

class GRB(enum.Enum):
  MINIMIZE = 1
  BINARY = 2

ILPEQ=1888
ILPLE=1889
ILPAND=1900
ILPOR=1911
ILPADD=1912
ILPMUL=1913

ILPOP_str = {ILPEQ:'==',ILPLE:'<=',ILPAND:'&&',ILPOR:'||',ILPADD:'+',ILPMUL:'*'}

# take a list of ILPVar
def and_(*argv):
  return (ILPAND, [arg for arg in argv])

def or_(*argv):
  return (ILPOR, [arg for arg in argv])

  
class ILPVar(object):
  def __init__(self, v):
    self.v = v
  def __eq__(self, other):
    return ILPOp(self, ILPEQ, other)
  def __le__(self, other):
    return ILPOp(self, ILPLE, other)
  def __ge__(self, other):
    return ILPOp(other, ILPLE, self)
  def __mul__(self, other):
    return ILPOp(self, ILPMUL, other)
  def __add__(self, other):
    return ILPOp(self, ILPADD, other)
  def __rmul__(self, other):
    return ILPOp(self, ILPMUL, other)
  def __radd__(self, other):
    return ILPOp(self, ILPADD, other)

class ILPOp(ILPVar):
  def __init__(self, lh, op, rh):
    self.lh = lh
    self.rh = rh
    self.op = op

class Model(object):
  def __init__(self, name):
    self.name = name
    self.variables = {}
    self.constraints = []
    self.vcnt = 0
    self.objective = None
  def addConstr(self, tup):
    self.constraints.append(tup)
  def addVars(self, Nvars, vtype=0):
    lst = []
    for i in range(0, Nvars):
      newv = ILPVar('v{}'.format(self.vcnt))
      self.vcnt += 1
      lst.append(newv)
      self.variables[newv] = newv.v
    return lst
  def setObjective(self, obj, p):
    self.objective = obj
  def print_stat(self):
    print('#variables = {}'.format(len(self.variables)))
    print('#constraints = {}'.format(len(self.constraints)))

