from pred import *
from pred_helper import *
import z3

class EnumPredHelper(object):
  def __init__(self, cnfs=[]):
    self.cnfs = cnfs
  def to_expr(self):
    if len(self.cnfs) > 1:
      return z3.Or(*[s.to_expr() for s in self.cnfs])
    else:
      return self.cnfs[0].to_expr()
  def get_all_svs(self, r):
    for s in self.cnfs:
      s.get_all_svs(r)
  def apply(self, sv_map):
    if len(self.cnfs) > 1:
      return any([s.apply(sv_map) for s in self.cnfs])
    else:
      return self.cnfs[0].apply(sv_map)
  def __str__(self):
    return '({})'.format(' V '.join([str(s) for s in self.cnfs]))

class PredCNFNode(object):
  def __init__(self, clauses=[]):
    self.clauses = clauses # a list of PredOrNode or AtomicNode
  def to_expr(self):
    if len(self.clauses) > 1:
      return z3.And(*[s.to_expr() for s in self.clauses])
    else:
      return self.clauses[0].to_expr()
  def get_all_svs(self, r):
    for s in self.clauses:
      s.get_all_svs(r)
  def apply(self, sv_map):
    if len(self.clauses) > 1:
      return all([s.apply(sv_map) for s in self.clauses])
    else:
      return self.clauses[0].apply(sv_map)
  def __str__(self):
    return '({})'.format('^'.join([str(s) for s in self.clauses]))
  def get_sz(self):
    return sum([s.get_sz() for s in self.clauses])

class PredOrNode(object):
  def __init__(self, atomic_nodes=[]):
    self.atomic_nodes = atomic_nodes
  def to_expr(self):
    assert(len(self.atomic_nodes) > 1)
    return z3.Or(*[s.to_expr() for s in self.atomic_nodes])
  def get_all_svs(self, r):
    for s in self.atomic_nodes:
      s.get_all_svs(r)
  def apply(self, sv_map):
    return any([s.apply(sv_map) for s in self.atomic_nodes])
  def __str__(self):
    return '({})'.format('v'.join([str(s) for s in self.atomic_nodes]))
  def get_sz(self):
    return sum([s.get_sz() for s in self.atomic_nodes])

class PredAtomicNode(object):
  def __init__(self, v, neg=False):
    self.neg = neg
    self.v = v
  def to_expr(self):
    if self.neg:
      return z3.Not(self.v)
    else:
      return self.v
  def get_all_svs(self, r):
    r.append(self.v)
  def apply(self, sv_map):
    if self.neg:
      return not sv_map[self.v]
    else:
      return sv_map[self.v]
  def __str__(self):
    if self.neg:
      return '~{}'.format(self.v)
    else:
      return str(self.v)
  def get_sz(self):
    return 1
  
def collect_atomic_pred(pred):
  if isinstance(pred, ConnectOp):
    return collect_atomic_pred(pred.lh) + collect_atomic_pred(pred.rh)
  elif isinstance(pred, BinOp) or isinstance(pred, SetOp):
    return [pred]
  elif isinstance(pred, UnaryOp):
    return collect_atomic_pred(pred.operand)

def get_target_expr(pred, pred_replace):
  if isinstance(pred, ConnectOp):
    if pred.op == OR:
      return z3.Or(get_target_expr(pred.lh, pred_replace), get_target_expr(pred.rh, pred_replace))
    else:
      return z3.And(get_target_expr(pred.lh, pred_replace), get_target_expr(pred.rh, pred_replace))
  elif isinstance(pred, BinOp) or isinstance(pred, SetOp):
    return pred_replace[pred]
  elif isinstance(pred, UnaryOp):
    return z3.Not(get_target_expr(pred.operand, pred_replace))

# return a list of:
#   a set of cnfs
#   the query result will be a union
def enumerate_pred_combinations(pred):
  if pred is None:
    return [[None]]
  #if is_cnf_without_negation(pred):
  if is_cnf(pred):
    return [[pred]]
  elif is_dnf(pred):
    return [pred.split_into_dnf()]
  
  Nors = count_ors(pred)
  atomic_preds = collect_atomic_pred(pred)
  sv_atomic_pred = {}
  pred_replace = {}
  enum_solver = z3.Solver()
  for i,a in enumerate(atomic_preds):
    exist_sv = None
    for sv1,a1 in sv_atomic_pred.items():
      if a.query_pred_eq(a1):
        exist_sv = sv1
    if exist_sv is not None:
      pred_replace[a] = exist_sv
    else:
      sv = z3.Bool('b_{}'.format(i))
      pred_replace[a] = sv
      sv_atomic_pred[sv] = a
  target_expr = get_target_expr(pred, pred_replace)

  for k,v in sv_atomic_pred.items():
    print '{} = {}'.format(k, v)

  print 'Nors = {}'.format(Nors)
  all_svs = [k for k,v in sv_atomic_pred.items()]
  all_literals = [PredAtomicNode(k) for k,v in sv_atomic_pred.items()]
  if contain_neg(pred):
    all_literals += [PredAtomicNode(k, neg=True) for k,v in sv_atomic_pred.items()]
  temp_literals = [a for a in all_literals]
  for N in range(2, Nors+2):
    for comb in itertools.combinations(temp_literals, N):
      all_literals.append(PredOrNode(list(comb)))

  all_cnfs = []
  for N in range(1, len(sv_atomic_pred)):
    for comb in itertools.combinations(all_literals, N):
      all_cnfs.append(PredCNFNode(list(comb)))

  print 'all literals = {}'.format(','.join([str(xs) for xs in all_literals]))
  print 'all cnfs = {}'.format(','.join([str(xs) for xs in all_cnfs]))
  eqv_exprs = []
  examples = [] # (sv_value_map, target_value) pair
  for N in range(1, Nors+2):
    # find pred of the union of N cnfs
    for comb in itertools.combinations(all_cnfs, N):
      union = EnumPredHelper(list(comb))
      contained_svs = []
      union.get_all_svs(contained_svs)
      if any([x.get_sz() > len(all_svs) for x in comb]):
        continue
      if not all([(x in all_svs) for x in contained_svs]):
        continue
      fail = False
      for example in examples:
        if str(union.apply(example[0])) != example[1]:
          fail = True
          break
      if fail:
        continue
      enum_solver.push()
      enum_solver.add(z3.Not(union.to_expr() == target_expr))
      if enum_solver.check() == z3.unsat:
        orig = str(union.to_expr())
        simplified = str(z3.simplify(union.to_expr()))
        #print 'orig_expr == simplified = {}'.format(orig==simplified)
        if orig == simplified:
          eqv_exprs.append(union)
          print 'Find an eqv expr: {}'.format(union)
      else:
        print union
        # retrieve model
        model = enum_solver.model()
        sv_map = {k:model[k] for k in all_svs}
        examples.append((sv_map, str(not union.apply(sv_map))))
      enum_solver.pop()
    
