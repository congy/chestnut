from schema import *
from constants import *
from query import *
from nesting import *
from planIR import *
from symbolic_context import *
import z3

def get_field_pos_in_tuple(table, field_name):
  if isinstance(table, DenormalizedTable):
    pos = 0
    for t in table.tables:
      for i,f in enumerate(t.get_fields()):
        if f.name == field_name:
          return pos
        pos = pos + 1
    assert(False)
  for i,f in enumerate(table.get_fields()):
    if f.name == field_name:
      return i
  assert(False)

def get_id_from_symbolic_tuple(table, symbolic_tuple):
  id_pos = get_field_pos_in_tuple(table, 'id')
  return symbolic_tuple[id_pos]

def get_ids_from_denormalized_symb(table, tup):
  pos = 0
  rt = []
  for t in table.tables:
    rt = tup[pos+get_field_pos_in_tuple(t, 'id')]
    pos = pos + len(t.get_fields())
  return rt    

def get_denormalized_tables(pred):
  if isinstance(pred, ConnectOp):
    return get_denormalized_tables(pred.lh) + get_denormalized_tables(pred.rh)
  elif isinstance(pred, SetOp):
    r = get_denormalized_tables(pred.lh)
    r += [pred.lh.field_class]
    r += get_denormalized_tables(pred.rh)
    return r
  elif isinstance(pred, AssocOp):
    return [pred.lh.field_class] + get_denormalized_tables(pred.rh)
  elif isinstance(pred, BinOp):
    r = []
    r += get_denormalized_tables(pred.lh)
    r += get_denormalized_tables(pred.rh)
    return r
  else:
    return []
  
def get_denormalized_query_fields(pred):
  if isinstance(pred, ConnectOp):
    return get_denormalized_query_fields(pred.lh) + get_denormalized_query_fields(pred.rh)
  elif isinstance(pred, SetOp):
    r = get_denormalized_query_fields(pred.lh)
    r += [pred.lh]
    r += get_denormalized_query_fields(pred.rh)
    return r
  elif isinstance(pred, AssocOp):
    return [pred.lh] + get_denormalized_query_fields(pred.rh)
  elif isinstance(pred, BinOp):
    r = []
    r += get_denormalized_query_fields(pred.lh)
    r += get_denormalized_query_fields(pred.rh)
    return r
  else:
    return []

def get_denormalized_keys(pred):
  if isinstance(pred, ConnectOp):
    return get_denormalized_keys(pred.lh) + get_denormalized_keys(pred.rh)
  elif isinstance(pred, SetOp):
    r = get_denormalized_keys(pred.rh)
    return r
  elif isinstance(pred, AssocOp):
    return []
  elif isinstance(pred, BinOp):
    if isinstance(pred.rh, MultiParam):
      return []
    if isinstance(pred.rh, Parameter):
      return [pred.lh]
    else:
      return []
  else:
    return []

def get_symbolic_param_or_value(thread_ctx, v):
  if isinstance(v, Parameter):
    return thread_ctx.get_symbs().param_symbol_map[v]
  elif isinstance(v, AtomValue):
    return v.to_z3_value()


# replace is a triple: qf, assoc_obj_id
def get_denormalizing_cond_helper(thread_ctx, symbolic_tuple, pred, cnt, table_ids, replace=[], updated_fields={}, only_mask=False):
  if isinstance(pred, ConnectOp):
    cnt, keys1, lh_expr = get_denormalizing_cond_helper(thread_ctx, symbolic_tuple, pred.lh, cnt, table_ids, replace, updated_fields, only_mask)
    cnt, keys2, rh_expr = get_denormalizing_cond_helper(thread_ctx, symbolic_tuple, pred.rh, cnt, table_ids, replace, updated_fields, only_mask)
    if pred.op == AND:
      return cnt, keys1+keys2, z3.And(lh_expr, rh_expr)
    elif pred.op == OR:
      return cnt, keys1+keys2, z3.Or(lh_expr, rh_expr)

  elif isinstance(pred, SetOp):
    assoc = get_query_field(pred.lh).table.get_assoc_by_name(get_query_field(pred.lh).field_name)
    assoc_pos = 0 if assoc.lft == get_query_field(pred.lh).table else 1
    id_pos = get_field_pos_in_tuple(get_query_field(pred.lh).table, 'id')
    assoc_id = table_ids[cnt]
    cnt += 1
    if pred.op == EXIST:
      r = False
    else:
      r = True
    next_symbolic_tuple = thread_ctx.get_symbs().symbolic_tables[get_query_field(pred.lh).field_class].symbols[assoc_id-1]
    cnt, keys, next_symbol_cond = get_denormalizing_cond_helper(thread_ctx, next_symbolic_tuple, pred.rh, cnt, table_ids, replace, updated_fields, only_mask)

    if any([replace[i][0] == pred.lh for i in range(0, len(replace))]):
      _replace = filter(lambda x: x[0] == pred.lh, replace)[0]
      match_cond = _replace[1]==assoc_id
      if pred.op == EXIST:
        return cnt, keys, z3.Or(z3.If(match_cond, next_symbol_cond, False), r)
      else:
        return cnt, keys, z3.And(z3.If(match_cond, next_symbol_cond, False), r)
    
    match_expr = []  
    for symbolic_assoc in thread_ctx.get_symbs().symbolic_assocs[assoc].symbols:
      match_expr.append(z3.And(assoc_id == symbolic_assoc[1-assoc_pos],  \
                                symbolic_tuple[id_pos] == symbolic_assoc[assoc_pos]))
    if pred.op == EXIST:
      r = z3.Or(z3.If(z3.Or(*match_expr), next_symbol_cond, False), r)
    else:
      r = z3.And(z3.If(z3.Or(*match_expr), next_symbol_cond, False), r)
    return cnt, keys, r

  elif isinstance(pred, AssocOp):
    assoc_id = table_ids[cnt]
    cnt += 1
    id_pos = get_field_pos_in_tuple(get_query_field(pred.lh).table, 'id')
    assoc_id_pos = get_field_pos_in_tuple(pred.lh.table, '{}_id'.format(pred.lh.field_name))
    next_symbolic_tuple = thread_ctx.get_symbs().symbolic_tables[pred.lh.field_class].symbols[assoc_id-1]
    cnt, keys, next_symbol_cond = get_denormalizing_cond_helper(thread_ctx, next_symbolic_tuple, pred.rh, cnt, table_ids, replace, updated_fields, only_mask)
    new_keys = [AssocOp(pred.lh, k) for k in keys]

    if any([replace[i][0] == pred.lh for i in range(0, len(replace))]):
      _replace = filter(lambda x: x[0] == pred.lh, replace)[0]
      match_cond = _replace[1]==assoc_id
      return cnt, new_keys, z3.If(match_cond, next_symbol_cond, get_default_z3v_by_type(get_query_field(pred.rh).field_class))
    
    r = z3.If(assoc_id==symbolic_tuple[assoc_id_pos], next_symbol_cond, get_default_z3v_by_type(get_query_field(pred.rh).field_class))
    return cnt, new_keys, r
  
  elif isinstance(pred, BinOp):
    if only_mask:
      return cnt, [], True
    cnt, keys, lh_expr = get_denormalizing_cond_helper(thread_ctx, symbolic_tuple, pred.lh, cnt, table_ids, replace, updated_fields, only_mask)
    #assert(not isinstance(pred.rh, DoubleParam))
    if pred.op == BETWEEN:
      exprs = []
      for p in [pred.rh.params[0], pred.rh.params[1]]:
        cnt, keys, rh_expr = get_denormalizing_cond_helper(thread_ctx, symbolic_tuple, p, cnt, table_ids, replace, updated_fields, only_mask)
        exprs.append(lh_expr == rh_expr)
      return cnt, [], z3.And(lh_expr >= exprs[0], lh_expr >= exprs[1])
    if isinstance(pred.rh, MultiParam):
      exprs = []
      for p in pred.rh.params:
        cnt, keys, rh_expr = get_denormalizing_cond_helper(thread_ctx, symbolic_tuple, p, cnt, table_ids, replace, updated_fields, only_mask)
        exprs.append(lh_expr == rh_expr)
      return cnt, [], z3.Or(*exprs)
    if isinstance(pred.rh, Parameter):
      return cnt, [(pred.lh, lh_expr)], True
    cnt, keys, rh_expr = get_denormalizing_cond_helper(thread_ctx, symbolic_tuple, pred.rh, cnt, table_ids, replace, updated_fields, only_mask)
    if pred.op == EQ:
      cond_expr = lh_expr == rh_expr
    elif pred.op == NEQ:
      cond_expr = lh_expr != rh_expr
    elif pred.op == GE:
      cond_expr = lh_expr >= rh_expr
    elif pred.op == GT:
      cond_expr = lh_expr > rh_expr
    elif pred.op == LE:
      cond_expr = lh_expr <= rh_expr
    elif pred.op == LT:
      cond_expr = lh_expr < rh_expr
    elif pred.op == SUBSTR:
      cond_expr = True
    else:
      assert(False)  
    if isinstance(pred.lh, AssocOp):
      cond_expr = z3.And(cond_expr, lh_expr != get_default_z3v_by_type(get_query_field(pred.lh).field_class))
    if isinstance(pred.rh, AssocOp):
      cond_expr = z3.And(cond_expr, rh_expr != get_default_z3v_by_type(get_query_field(pred.rh).field_class))
    return cnt, [], cond_expr
  elif isinstance(pred, QueryField):
    if pred in updated_fields:
      v = updated_fields[pred]
      if isinstance(v, AtomValue):
        return cnt, [], v.to_z3_value()
      else:
        assert(isinstance(v, Parameter))
        return cnt, [], thread_ctx.get_symbs().param_symbol_map[v]
    else:
      fid = get_field_pos_in_tuple(pred.table, pred.field_name)
      return cnt, [], symbolic_tuple[fid]
  elif isinstance(pred, AtomValue):
    return cnt, [], pred.to_z3_value()
  else:
    assert(False)
    
def check_eq_nested_t_and_qf(nested_t, qf):
  if isinstance(qf, Table):
    return nested_t.name == qf.name
  elif isinstance(qf, QueryField):
    return nested_t.name == qf.field_name
  else:
    assert(False)

def get_assoc_obj_cond_helper(thread_ctx, symbolic_tuple, cur_pred):
  if is_assoc_field(cur_pred):
    fid = get_field_pos_in_tuple(cur_pred.lh.table, '{}_id'.format(cur_pred.lh.field_name))
    r = INVALID_VALUE #get_init_value_by_type(get_query_field(cur_pred).get_type())
    for i,next_symbolic_tuple in enumerate(thread_ctx.get_symbs().symbolic_tables[cur_pred.lh.field_class].symbols):
      next_symbol_cond = get_assoc_obj_cond_helper(thread_ctx, next_symbolic_tuple, cur_pred.rh)
      r = z3.If((i+1)==symbolic_tuple[fid], next_symbol_cond, r)
    return r
  elif is_atomic_field(cur_pred):
    fid = get_field_pos_in_tuple(cur_pred.table, cur_pred.field_name)
    return symbolic_tuple[fid]
  else:
    assert(False)

# return a lambda function, providing a list of ids, return an expression
def get_denormalized_matching_lambda(thread_ctx, table):
  match_funcs = []
  for i in range(0, len(table.tables)-1):
    f = table.join_fields[i]
    reversed_f = get_reversed_assoc_qf(f)
    match_func = None
    if f.table.has_one_or_many_field(f.field_name) == 1:
      match_func = lambda x, y: x[get_field_pos_in_tuple(f.table, '{}_id'.format(f.field_name))] == y[get_field_pos_in_tuple(f.field_class, 'id')]
    elif reversed_f.has_one_or_many_field(reversed_f.field_name) == 1:
      match_func = lambda x, y: x[get_field_pos_in_tuple(reversed_f.table, '{}_id'.format(reversed_f.field_name))] \
          == y[get_field_pos_in_tuple(reversed_f.field_class, 'id')]
    else: # many to many
      assoc = f.table.get_assoc_by_name(f.field_name)
      assoc_pos = 0 if assoc.lft == f.table else 1
      lft_id_pos = get_field_pos_in_tuple(f.table, 'id')
      rgt_id_pos = get_field_pos_in_tuple(f.field_class, 'id')
      match_func = lambda x, y: z3.Or(*[z3.And(x[lft_id_pos] == symbolic_assoc[assoc_pos], y[rgt_id_pos] == symbolic_assoc[1-assoc_pos]) \
          for symbolic_assoc in thread_ctx.get_symbs().symbolic_assocs[assoc].symbols])
    match_funcs.append(match_func)  
  
  tups = []
  ids_in_table = lambda ids: z3.And(*[match_funcs[i](\
        self.thread_ctx.get_symbs().symbolic_tables[table.join_fields[i].table].symbols[ids[i]], \
        self.thread_ctx.get_symbs().symbolic_tables[table.join_fields[i].field_class].symbols[ids[i+1]])\
        for i in range(0, len(table)-1)])
  return ids_in_table

# return a list of ([id], condition) pair
def get_denormalized_table_id_list(thread_ctx, table):
  match_funcs = []
  for i in range(0, len(table.tables)-1):
    f = table.join_fields[i]
    reversed_f = get_reversed_assoc_qf(f)
    match_func = None
    if f.table.has_one_or_many_field(f.field_name) == 1:
      match_func = lambda x, y: x[get_field_pos_in_tuple(f.table, '{}_id'.format(f.field_name))] == y[get_field_pos_in_tuple(f.field_class, 'id')]
    elif reversed_f.has_one_or_many_field(reversed_f.field_name) == 1:
      match_func = lambda x, y: x[get_field_pos_in_tuple(reversed_f.table, '{}_id'.format(reversed_f.field_name))] \
          == y[get_field_pos_in_tuple(reversed_f.field_class, 'id')]
    else: # many to many
      assoc = f.table.get_assoc_by_name(f.field_name)
      assoc_pos = 0 if assoc.lft == f.table else 1
      lft_id_pos = get_field_pos_in_tuple(f.table, 'id')
      rgt_id_pos = get_field_pos_in_tuple(f.field_class, 'id')
      match_func = lambda x, y: z3.And(*[z3.And(x[lft_id_pos] == symbolic_assoc[assoc_pos], y[rgt_id_pos] == symbolic_assoc[1-assoc_pos]) \
          for symbolic_assoc in thread_ctx.get_symbs().symbolic_assocs[assoc].symbols])
    match_funcs.append(match_func)  

  symbolic_sz = [range(0, self.thread_ctx.get_symbs().symbolic_tables[table].sz) for table in table.tables]
  rt = []
  for x in itertools.product(symbolic_sz):
    # x is a list of id
    # match = True
    # for i in range(0, len(x)-1):
    #   f = table.join_fields[i]
    #   tup_lft = self.thread_ctx.get_symbs().symbolic_tables[f.table].symbols[x[i]]
    #   tup_rgt = self.thread_ctx.get_symbs().symbolic_tables[f.field_class].symbols[x[i+1]]
    #   match = z3.And(match, match_func(tup_lft, tup_rgt))
    match = get_denormalized_matching_lambda(thread_ctx, table)(x)
    rt.append((x, match))
  return rt



def generate_cond_expr_with_placeholder(thread_ctx, symbolic_tuple, pred, var_state):
  if isinstance(pred, ConnectOp):
    lh_expr = generate_cond_expr_with_placeholder(thread_ctx, symbolic_tuple, pred.lh, var_state)
    rh_expr = generate_cond_expr_with_placeholder(thread_ctx, symbolic_tuple, pred.rh, var_state)
    if pred.op == AND:
      return z3.And(lh_expr, rh_expr)
    elif pred.op == OR:
      return z3.Or(lh_expr, rh_expr)
  elif isinstance(pred, BinOp):
    lh_expr = generate_cond_expr_with_placeholder(thread_ctx, symbolic_tuple, pred.lh, var_state)
    if isinstance(pred.rh, DoubleParam):
      rh_expr = [generate_cond_expr_with_placeholder(thread_ctx, symbolic_tuple, pred.rh.p1, var_state), \
                 generate_cond_expr_with_placeholder(thread_ctx, symbolic_tuple, pred.rh.p2, var_state)]
      return z3.And(lh_expr >= rh_expr[0], lh_expr <= rh_expr[1])
    elif isinstance(pred.rh, MultiParam):
      rh_expr = []
      for p in pred.rh.params:
        exp = generate_cond_expr_with_placeholder(thread_ctx, symbolic_tuple, p, var_state)
        rh_expr.append(lh_expr==exp)
      return z3.Or(*rh_expr)
    else:
      rh_expr = generate_cond_expr_with_placeholder(thread_ctx, symbolic_tuple, pred.rh, var_state)
      if pred.op == EQ:
        return lh_expr == rh_expr
      elif pred.op == NEQ:
        return lh_expr != rh_expr
      elif pred.op == GE:
        return lh_expr >= rh_expr
      elif pred.op == GT:
        return lh_expr > rh_expr
      elif pred.op == LE:
        return lh_expr <= rh_expr
      elif pred.op == LT:
        return lh_expr < rh_expr
      elif pred.op == SUBSTR:
        return True
      else:
        assert(False)
  elif isinstance(pred, UnaryOp):
    op_expr = generate_cond_expr_with_placeholder(thread_ctx, symbolic_tuple, pred.operand, var_state)
    return z3.Not(op_expr)
  elif isinstance(pred, SetOp):
    #return var_state.find_symbolic_var(pred)
    assert(False)
  elif isinstance(pred, EnvAtomicVariable):
    return var_state.find_symbolic_var(pred)
  elif isinstance(pred, AssocOp):
    #return var_state.find_symbolic_var(pred)
    assert(False)
  elif isinstance(pred, Parameter):
    return thread_ctx.get_symbs().param_symbol_map[pred]
  elif isinstance(pred, AtomValue):
    return pred.to_z3_value()
  elif isinstance(pred, QueryField):
    return var_state.find_query_field(pred)
  else:
    assert(False)

def get_symbolic_assoc_field_value(thread_ctx, pred, lh_id):
  if isinstance(pred, QueryField):
    fpos = get_field_pos_in_tuple(pred.table, pred.field_class.name)
    if type(lh_id) is int:
      return thread_ctx.get_symbs().symbolic_tables[pred.table].symbols[lh_id-1][fpos]
    else:
      init_v = get_default_z3v_by_type(pred.field_class)
      for i,symb in enumerate(thread_ctx.get_symbs().symbolic_tables[pred.table].symbols):
        init_v = z3.If(lh_id==i+1, symb[fpos], init_v)
      return init_v
  else:
    lft_symb_t = thread_ctx.get_symbs().symbolic_tables[pred.lh.table]
    rgt_symb_t = thread_ctx.get_symbs().symbolic_tables[pred.lh.field_class]
    assoc_fpos = get_field_pos_in_tuple(pred.lh.table, '{}_id'.format(pred.lh.field_name))
    rgt_id = 0
    if type(lh_id) is int:
      rgt_id = lft_symb_t.symbols[lh_id-1][assoc_fpos]
    else:
      for i,symb in enumerate(lft_symb_t.symbols):
        rgt_id = z3.If(lh_id==i+1, symb[assoc_fpos], rgt_id)
    return get_symbolic_assoc_field_value(thread_ctx, pred.rh, rgt_id)


def results_ordered(actual_order, target_order):
  if target_order is None:
    return True
  if actual_order is None:
    return False
  idx = -1
  for i,o in enumerate(actual_order):
    if o == target_order[0]:
      idx = i
  if idx == -1 or len(actual_order) < idx + len(target_order):
    return False
  return all([actual_order[i+idx]==target_order[i] for i in range(0, len(target_order))])

def and_exprs(exprs, default=True):
  if len(exprs)==0:
    return default
  elif len(exprs) == 1:
    return exprs[0]
  else:
    return z3.And(*exprs)

def or_exprs(exprs, default=True):
  if len(exprs) == 0:
    return default
  elif len(exprs) == 1:
    return exprs[0]
  else:
    return z3.Or(*exprs)

def print_table_in_model(thread_ctx, m):
  s = ''
  for table,v in thread_ctx.get_symbs().symbolic_tables.items():
    s +='Table {}\n'.format(table.name)
    s += '\t'.join([f.name for f in table.get_fields()])
    s += '\n'
    id_pos = get_field_pos_in_tuple(table, 'id')
    for i in range(0, v.sz):
      s += '\t'.join([str(m[v.symbols[i][j]]) if j != id_pos else str(v.symbols[i][j]) for j in range(0, len(table.get_fields()))])
      s += '\n'
  s += '\n'
  for assoc,v in thread_ctx.get_symbs().symbolic_assocs.items():
    s += 'Assoc {}\n'.format(assoc.name)
    s += '{}_id\t{}_id\n'.format(assoc.lft.name, assoc.rgt.name)
    for i in range(0, v.sz):
      s += '\t'.join([str(v.symbols[i][j]) if type(v.symbols[i][j]) is int else str(m[v.symbols[i][j]]) for j in range(0, 2)])
      s += '\n'
  s += '\n'
  s += 'Params:'
  s += '\n'.join(['{}:{}'.format(k, str(m[v])) for k,v in thread_ctx.get_symbs().param_symbol_map.items()])
  return s

def check_eq_debug(thread_ctx, msg, expr, exprs=[]):
  thread_ctx.get_symbs().solver.push()
  thread_ctx.get_symbs().solver.add(z3.Not(expr))
  if thread_ctx.get_symbs().solver.check() != z3.unsat:
    print '{} {}'.format(msg, expr)
    print 'CONSTRAINT FAILED!'
    print print_table_in_model(thread_ctx, thread_ctx.get_symbs().solver.model())
    print ''
    for i,expr in enumerate(exprs):
      print 'expr {} = {}'.format(expr[0], thread_ctx.get_symbs().solver.model().eval(expr[1]))
    exit(0)
  thread_ctx.get_symbs().solver.pop()