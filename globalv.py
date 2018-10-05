tables = []
associations = []

assertions = []

TABLE_SYMBOLIC_TUPLE_CNT = 3
ASSOC_SYMBOLIC_TUPLE_CNT = 3

NUM_PROCESS = 32

pred_selectivity = [] # pair: (pred, selectivity)

frequencies = {}
always_nested = []
always_fk_indexed = []
pred_scope = []
use_template = False

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

qr_type = 'proto'
def set_qr_type(new_type):
  global qr_type
  qr_type = new_type
def get_qr_type():
  global qr_type
  return qr_type
def is_qr_type_proto():
  global qr_type
  return qr_type == 'proto'

ds_short_print = False
def set_ds_short_print(v):
  global ds_short_print
  ds_short_print = v