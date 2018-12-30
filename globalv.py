tables = []
associations = []

assertions = []

memory_bound = 4294967295

TABLE_SYMBOLIC_TUPLE_CNT = 3
ASSOC_SYMBOLIC_TUPLE_CNT = 3

NUM_PROCESS = 32

pred_selectivity = [] # pair: (pred, selectivity)

frequencies = {}
always_nested = []
always_fk_indexed = []
reversely_visited = []
pred_scope = []
use_template = False

op_synth_cache = []
def order_equal(o1, o2):
  if o1 is None and o2 is None:
    return True
  if o1 is None or o2 is None:
    return False
  return len(o1) == len(o2) and all([o1[i]==o2[i] for i in range(0, len(o1))])
def fk_equal(fk1, fk2):
  if fk1 is None and fk2 is None:
    return True
  if fk1 is None or fk2 is None:
    return False
  return fk1==fk2
def add_to_synth_cache(pred, order, fk, state):
  global op_synth_cache
  op_synth_cache.append((pred, order, fk, state))
def check_synth_cache(pred, order, fk):
  global op_synth_cache
  for p,o,k,s in op_synth_cache:
    if p == pred and order_equal(o, order) and fk_equal(k,fk):
      return s
  return None

def set_use_template():
  global use_template
  use_template = True

def set_always_nested(qfs):
  global always_nested
  for qf in qfs:
    always_nested.append(qf)

def set_always_fk_indexed(qfs):
  global always_fk_indexed
  for qf in qfs:
    always_fk_indexed.append(qf)

def add_pred_scope(scopes):
  global pred_scope
  for scope in scopes:
    pred_scope.append(scope)

always_nested = []

def extend_tables(tables, associations, queries):
  for q in queries:
    if q.table.is_temp:
      tables.append(q.table)
      for a in q.table.get_assocs():
        associations.append(a)

qr_type = 'struct'
def set_qr_type(new_type):
  global qr_type
  qr_type = new_type
def get_qr_type():
  global qr_type
  return qr_type
def is_qr_type_proto():
  global qr_type
  return qr_type == 'proto'

symbolic_verify = False
