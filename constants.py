import os
import z3
import datetime

_db_name = ''
def get_db_name():
  global _db_name
  return _db_name
def set_db_name(db_name):
  global _db_name
  _db_name = db_name

_cxx_file_dir = './'
def get_cxx_file_dir():
  global _data_file_dir
  return _cxx_file_dir

_data_file_dir = './'
def set_data_file_dir(fdir):
  global _data_file_dir
  _data_file_dir = fdir
  if not os.path.exists(fdir):
    os.system('mkdir {}'.format(fdir))  

def get_data_file_dir():
  global _data_file_dir
  return _data_file_dir

words_map = {'status':'statuses', 'news':'news'}
def to_plural(word):
  global words_map
  for k,v in words_map.items():
    if word.endswith(k):
      return word.replace(k, v)
  if word[-2:] in ['ss', 'sh', 'ch'] or word[-1] in ['x', 'z', 'o']:
    return word+'es'
  if word[-2:] in ['fe']:
    return word[:-2]+'ves'
  if word[-1] in ['f']:
    return word[:-1]+'ves'
  if word[-1] in ['y']:
    return word[:-1]+'ies'
  return word+'s'
  
def get_db_table_name(name):
  return to_plural(name)


MAXINT = 4294967295
INVALID_VALUE = 4294967295+1

MAX_NESTED_LEVEL = 4
SMALL_DT_BOUND=262144
#SMALL_DT_BOUND=256

COST_ADD = 201
COST_MUL = 202
COST_DIV = 203
COST_MINUS = 204
cost_op_to_str = {COST_ADD: '+', COST_MUL: '*', COST_DIV: '/', COST_MINUS: '-'}
def get_cost_op_to_str(op):
  return cost_op_to_str[op]


CPP_PROTO_VAR = 6000
CPP_OBJ_VAR = 6001
CPP_TEMP_VAR = 6002

AGGR = 4011
MAINPTR = 4012
OBJECT = 4013

#index op type
RANGE = 1011  
POINT = 1012  
OPEN = 1013
CLOSE = 1014
index_type_to_str = {RANGE: 'range', POINT: 'point'}

INSERT=3001
UPDATE=3002
DELETE=3003

AND=0
OR=1
NOT=2
BETWEEN=3
NOTIN=4
SUBSET=5
SUPERSET=6
SETEQ=7
STRUCTEQ=8
EQ=9
NEQ=10
NE=NEQ
GE=11
GT=12
LE=13
LT=14
IN=15
SUBSTR=16

EXIST=20
EXISTS=EXIST
FORALL=21
ASSOC=22

reversed_op = {AND:OR, OR:AND, EQ:NEQ, NEQ:EQ, GE:LT, LT:GE, GT:LE, LE:GT, SUBSET:SUPERSET} #TODO

pred_op_to_cpp_map = {EQ: '==', NEQ: '!=', LT: '<', GT: '>', LE: '<=', GE: '>=', NOT: '!', IN: 'in', BETWEEN: 'between', EXIST: 'exist', FORALL: 'forall', ASSOC: '.', AND: '&&', OR: '||', SUBSTR: 'like'}
pred_op_to_sql_map = {EQ: '=', NEQ: '!=', LT: '<', GT: '>', LE: '<=', GE: '>=', NOT: '!', IN: 'in', BETWEEN: 'between', EXIST: 'exist', FORALL: 'forall', ASSOC: '.', AND: 'and', OR: 'or', SUBSTR: 'like'}
pred_op_to_z3_lambda = {EQ: lambda x,y:x==y, NEQ: lambda x,y:x!=y, LT: lambda x,y:x<y, GT: lambda x,y:x>y, \
    LE: lambda x,y:x<=y, GE: lambda x,y:x>=y, AND: lambda x,y:z3.And(x,y), OR: lambda x,y:z3.Or(x,y) }

def get_pred_op_to_cpp_map(op):
  return pred_op_to_cpp_map[op]

MAX=50
MIN=51
COUNT=52
AVG=53
SUM=54

ADD=100
MINUS=101
MULTIPLY=102
DIVIDE=103
BAND=104
BOR=105
BEQ=106
BNEQ=107
BLE=108
BGE=109

IFTHENELSE=110

expr_op_to_cpp_map = {ADD: '+', MINUS: '-', MULTIPLY: '*', DIVIDE:'/', BAND:'&&', BOR:'||', BEQ:'==', BNEQ:'!=', BLE:'<=', BGE:'>='}
expr_op_to_str_map = {MAX: 'max', MIN: 'min', COUNT: 'count', AVG: 'avg', SUM: 'sum', ADD: '+', MINUS: '-', MULTIPLY: '*', DIVIDE:'/', BAND:'&&', BOR:'||', BEQ:'==', BNEQ:'!=', BLE:'<=', BGE:'>=', IFTHENELSE:'ite'}


types = ["int", "oid", "uint", "smallint", "float", "bool", "date", \
"string", "varchar(4)", "varchar(8)", "varchar(16)", "varchar(32)", "varchar(64)", "varchar(128)", "varchar(256)"]

cpp_types = {"int":"int", "oid":"oid_t", "smallint":"uint8_t", "date":"date_t", "uint":"uint32_t","float":"float","bool":"bool", \
"string":"std::string"}

proto_types = {"int":"int32", "oid":"uint32", "smallint":"uint32", "date":"uint32", "uint":"uint32","float":"float","bool":"bool",
"string":"string", "varchar(4)":"string", "varchar(8)":"string", "varchar(16)":"string", "varchar(32)":"string",\
"varchar(64)":"string", "varchar(128)":"string", "varchar(256)":"string"}
def get_proto_type(tipe):
  if is_string_type(tipe):
    return 'string'
  else:
    return proto_types[tipe]
def get_param_proto_type(tipe):
  if is_date_type(tipe):
    return 'string'
  else:
    return get_proto_type(tipe)

mysql_types = {"int":"int(11)", "smallint":"int(8)", "oid":"int(11)", "uint":"int(11)", "float":"float","bool":"tinyint(1)", "date":"datetime"}

type_size = {"int":1, "oid":1, "uint":1, "smallint":1, "float":2, "bool":1, "date":1}
type_to_print_symbol = {'int':'%d', 'oid':'%u', 'smallint':'%u', 'date':'%u', 'uint':'%u', 'float':'%f', 'bool':'%d',
'string':'%s', 'varchar(4)':'%s', 'varchar(8)':'%s', 'varchar(16)':'%s', 'varchar(32)':'%s', 'varchar(64)':'%s', 'varchar(128)':'%s', 'varchar(256)':'%s'}

def get_type_to_print_symbol(tipe):
  if is_string_type(tipe):
    return '%s'
  else:
    return type_to_print_symbol[tipe]

def get_symbol_by_field(f, vname):
  if is_int(f):
    v = z3.Int(vname)
  elif is_unsigned_int(f):
    v = z3.Int(vname)
  elif is_bool(f):
    v = z3.Bool(vname)
  elif is_float(f):
    v = z3.Int(vname)
  elif is_string(f):
    v = z3.Int(vname)
  else:
    assert(False)
  return v

def get_psql_type(tipe):
  if is_date_type(tipe):
    return 'TIMESTAMP'
  elif is_int_type(tipe):
    return 'INTEGER'
  elif is_unsigned_int_type(tipe):
    return 'BIGINT'
  elif is_bool_type(tipe):
    return 'INTEGER'
  elif is_float_type(tipe):
    return 'FLOAT'
  elif is_varchar_type(tipe):
    return 'VARCHAR({})'.format(get_varchar_length(tipe))
  elif is_long_string_type(tipe):
    return 'VARCHAR(256)'
  else:
    assert(False)


def get_symbol_by_field_type(tipe, vname):
  if is_int_type(tipe):
    v = z3.Int(vname)
  elif is_unsigned_int_type(tipe):
    v = z3.Int(vname)
  elif is_bool_type(tipe):
    v = z3.Bool(vname)
  elif is_float_type(tipe):
    v = z3.Int(vname)
  elif is_string_type(tipe):
    v = z3.Int(vname)
  else:
    assert(False)
  return v

def get_default_z3v_by_type(klass):
  if klass.tipe == 'bool':
    return False
  if klass.tipe == 'float':
    return INVALID_VALUE
  elif klass.tipe == 'oid':
    return 0
  elif is_string_type(klass.tipe):
    return INVALID_VALUE
  else:
    return INVALID_VALUE

def get_z3_value(v, tipe):
  if tipe == 'bool':
    return bool(v)
  elif tipe == 'float':
    return int(v)
  elif is_string_type():
    return hash(v)
  else:
    return int(v)

def is_ptr_for_update(var):
  return var.updateptr_type

def is_fast_type(var):
  return var.fast_type

def get_cpp_type(tipe):
  if is_varchar_type(tipe):
    return 'VarChar<{}>'.format(get_varchar_length(tipe))
  elif is_long_string_type(tipe):
    return 'LongString'
  else:
    return cpp_types[tipe]

def get_sql_type(tipe):
  if is_varchar_type(tipe):
    return tipe
  elif is_long_string_type(tipe):
    return 'text'
  else:
    assert(tipe in mysql_types)
    return mysql_types[tipe]

def get_varchar_length(tipe):
  if is_long_string_type(tipe):
    return 1024
  v = tipe.replace('varchar(', '')
  return int(v[:-1])

def is_unsigned_int_type(tipe):
    return tipe == "uint" or tipe == "oid" or tipe == "date" or tipe == "smallint"
def is_unsigned_int(f):
  return is_unsigned_int_type(f.tipe)

def is_any_int_type(tipe):
    return tipe == "uint" or tipe == "oid" or tipe == "date" or tipe == "smallint" or tipe == "int"

def is_string_type(tipe):
  return tipe.startswith('varchar(') or tipe == 'string'
def is_string(f):
  return is_string_type(f.tipe)

def is_varchar_type(tipe):
  return tipe.startswith('varchar(')
def is_varchar(f):
  return is_varchar_type(f.tipe)

def is_long_string_type(tipe):
  return tipe == 'string'
def is_long_string(f):
  return is_long_string_type(f.tipe)

def is_int_type(tipe):
  return tipe == 'int'
def is_int(f):
  return is_int_type(f.tipe)

def is_float_type(tipe):
  return tipe == "float"
def is_float(f):
  return is_float_type(f.tipe)

def is_bool_type(tipe):
  return tipe == "bool"
def is_bool(f):
  return is_bool_type(f.tipe)

def is_date_type(tipe):
  return tipe == "date"
def is_date(f):
  return is_date_type(f.tipe)

def value_is_basic_type(v):
  return type(v) is int or type(v) is bool or type(v) is float or type(v) is str

def type_min_value(tipe):
  if tipe == 'int':
    return 0-MAXINT
  elif tipe == 'float':
    return 0-MAXINT
  elif tipe == 'date' or tipe == 'oid' or tipe == 'uint':
    return 0
  elif tipe.startswith('varchar(') or tipe == 'string':
    return ''

def datetime_to_int(dt):
   if dt == '0000-00-00 00:00:00':
     return 0
   idt = datetime.datetime.strptime(dt,"%Y-%m-%d %H:%M:%S")
   return idt.year*356+idt.month*12+idt.day

def type_max_value(tipe):
  if tipe == 'int':
    return MAXINT
  elif tipe == 'float':
    return MAXINT
  elif tipe == 'date' or tipe == 'oid' or tipe == 'uint':
    return MAXINT
  elif tipe.startswith('varchar(') or tipe == 'string':
    return ''

def get_sum_type(tipe):
  if tipe == 'smallint':
    return 'uint'
  else:
    return tipe

def get_init_value_by_type(tipe):
  if type(tipe) is str:
    if is_unsigned_int_type(tipe) or is_int_type(tipe):
      return 0
    elif is_bool_type(tipe):
      return False
    elif is_float_type(tipe):
      return 0.0
    elif is_varchar_type(tipe):
      return '""'
      #return ''.join(['0' for i in range(0, get_varchar_length(tipe))])
  else:
    return 0

cpp_files_to_copy = [
  'util.cc',
  'util.h',
  'data_struct.h',
  'simple_types.h',
  'Makefile',
  'atomic_stack.h',
  'bloom_filter.h',
  'bwtree.cc',
  'bwtree.h',
  'sorted_small_set.h'
]
cpp_files_to_copy_path = '../../'

def set_files_to_copy_path(new_path):
  global cpp_files_to_copy_path
  cpp_files_to_copy_path = new_path

def get_cpp_files_to_copy_path():
  global cpp_files_to_copy_path
  return cpp_files_to_copy_path

cpp_file_path = '../../'
def set_cpp_file_path(new_path):
  global cpp_file_path
  cpp_file_path = new_path

def get_cpp_file_path():
  global cpp_file_path
  return cpp_file_path
