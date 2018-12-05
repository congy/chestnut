import sys
sys.path.append('../')
from constants import *
from schema import *

def cgen_fname(f):
  if isinstance(f, QueryField):
    f = f.field_class
    return '{}_{}'.format(f.table.name, f.field_name)
  elif isinstance(f, AssocOp):
    lst = get_assoc_field_list(f)
    s = '_'.join([f1.field_name for f1 in lst])
  elif isinstance(f, Field):
    return '{}_{}'.format(f.table.name, f.name)

def cgen_ftype(f):
  if isinstance(f, QueryField):
    return get_cpp_type(f.field_class.tipe)
  elif isinstance(f, Field):
    return get_cpp_type(f.tipe)

def cgen_init_from_proto(typename, proto, fields):
  return "  {}(const {}& p): {} {{}}\n".format(typenmae, proto, \
                                ','.join(['{}(p.{}())'.format(cgen_fname(f), f.name) for f in fields]))

def cgen_proto_type(t):
  if isinstance(t, NestedTable):
    r = ''
    while isinstance(t, NestedTable):
      r = '::P{}In{}'.format(get_capitalized_name(t.name),get_capitalized_name(get_main_table(t.upper_table).name)) + r
      t = t.upper_table
    r = '{}::P{}{}'.format(get_db_name(), get_capitalized_name(t.name), r)
    return r
  else:
    assert(not isinstance(t, DenormalizedTable))
    return '{}::P{}'.format(get_db_name(), get_capitalized_name(t.name))
def cgen_get_fproto(f):
  if isinstance(f, QueryField):
    return '{}()'.format(f.field_name)
  elif isinstance(f, AssocOp):
    lst = get_assoc_field_list(f)
    s = []
    for qf in lst:
      if qf.table.has_one_or_many_field(qf.field_name) == 1:
        s.append('{}()'.format(qf.field_name))
      else:
        s.append('{}(0)'.format(qf.field_name))
    return '.'.join([s1 for s1 in s])
  elif isinstance(f, Field):
    return '{}()'.format(f.name)

def cgen_fprint(f):
  if is_int(f) or is_bool(f):
    return "{}=%d".format(f.name), cgen_fname(f)
  elif is_unsigned_int(f):
    return "{}=%u".format(f.name), cgen_fname(f)
  elif is_float(f):
    return "{}=%f".format(f.name), cgen_fname(f)
  elif is_string(f):
   return '{}=%s'.format(f.name), '{}.s'.format(cgen_fname(f)) if is_varchar(f) else '{}.s.c_str()'.format(cgen_fname(f))
  else:
    assert(False)

def cgen_ds_type(idx):
  if isinstance(idx, ObjBasicArray):
    if idx.single_element:
      qf = get_qf_from_nested_t(idx.table)
      return '{}In{}'.format(get_capitalized_name(qf.field_name), get_capitalized_name(qf.table.name))
    sz = to_real_value(idx.compute_size())
    if sz < SMALL_DT_BOUND: 
      return 'SmallBasicArray'
    else:
      return 'BasicArray'
  elif isinstance(idx, IndexBase):
    prefix = ''
    if to_real_value(idx.compute_size()) < SMALL_DT_BOUND:
      prefix='Small'
    if isinstance(idx, ObjTreeIndex):
      return '{}TreeIndex'.format(prefix)
    elif isinstance(idx, ObjSortedArray):
      return '{}SortedArray'.format(prefix)
    elif isinstance(idx, ObjHashIndex):
      return '{}HashIndex'.format(prefix)
    elif isinstance(idx, ObjArray):
      return '{}ObjArray'.format(prefix)
  assert(False)

def merge_assoc_qf(assoc, qf):
  if isinstance(assoc, QueryField):
    return AssocOp(assoc, qf)
  elif isinstance(assoc, AssocOp):
    return AssocOp(assoc.lh, merge_assoc_qf(assoc.rh, qf))
  else:
    assert(False)

def merge_qf_assoc(qf, assoc):
  pass