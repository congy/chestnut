from schema import *
from constants import *
from query import *
from symbolic_helper import *
from symbolic_context import *
import globalv
import z3

class SymbolicTable(object):
  def __init__(self, table, sz, thread_ctx, init_tuples=True):
    self.table = table
    self.sz = sz
    self.symbols = []
    self.thread_ctx = thread_ctx
    self.exists = []
    if not init_tuples:
      return None
    if isinstance(table, DenormalizedTable):
      lst = get_denormalized_matching_lambda(thread_ctx, table)
      for pair in lst:
        tup = []
        for i in range(0, len(table.tables)):
          tup = tup + thread_ctx.get_symbs().symbolic_tables[table.tables[i]].symbols[pair[0][i]]
        self.symbols.append(tup)
        self.exists.append(pair[1])
    else:
      for i in range(0, sz):
        tup = []
        for f in table.get_fields():
          if f.name == 'id':
            tup.append(i+1)
            continue
          #FIXME: add field range assertion
          vname = '{}-{}-{}'.format(table.name, i+1, f.name)
          v = get_symbol_by_field(f, vname)
          if not is_bool(f):
            self.thread_ctx.get_symbs().solver.add(v>=int(f.get_min_value(for_z3=True)))
            self.thread_ctx.get_symbs().solver.add(v<=int(f.get_max_value(for_z3=True)))
          tup.append(v)
        self.symbols.append(tup)
      self.exists = [True for s in self.symbols]
  def update(self, write_query):
    assert(isinstance(write_query, UpdateObject))
    for i in range(0, self.sz):
      for j,f in enumerate(self.table.get_fields()):
        if f.name == 'id':
          continue
        new_v = None
        for k,v in write_query.updated_fields.items():
          if k.field_class == f:
            newv = z3.If(i+1==self.get_symbolic_param_or_value(write_query.param), \
                              self.get_symbolic_param_or_value(v), self.symbols[i][j])
            self.symbols[i][j] = newv
  def get_symbolic_param_or_value(self, v):
    return get_symbolic_param_or_value(self.thread_ctx, v)

class SymbolicAssociation(object):
  def __init__(self, assoc, sz, thread_ctx, init_tuples=True):
    self.assoc = assoc
    self.symbols = []
    self.sz = sz
    self.thread_ctx = thread_ctx
    if not init_tuples:
      return None
    lft_sz = self.thread_ctx.get_symbs().symbolic_tables[self.assoc.lft].sz
    rgt_sz = self.thread_ctx.get_symbs().symbolic_tables[self.assoc.rgt].sz
    if assoc.assoc_type == 'one_to_many':
      fid = get_field_pos_in_tuple(self.assoc.rgt, '{}_id'.format(self.assoc.rgt_field_name))
      self.sz = rgt_sz
      for i in range(0, rgt_sz):
        lft_symbol = self.thread_ctx.get_symbs().symbolic_tables[assoc.rgt].symbols[i][fid]
        rgt_symbol = i+1
        self.thread_ctx.get_symbs().solver.add(lft_symbol>=1)
        self.thread_ctx.get_symbs().solver.add(lft_symbol<=lft_sz)
        self.symbols.append((lft_symbol, rgt_symbol))
    else:
      self.sz = sz
      for i in range(0, sz):
        lft_symbol = z3.Int('{}-pair-{}-{}'.format(assoc.name, assoc.lft.name, i))
        rgt_symbol = z3.Int('{}-pair-{}-{}'.format(assoc.name, assoc.rgt.name, i))
        self.thread_ctx.get_symbs().solver.add(lft_symbol>=1)
        self.thread_ctx.get_symbs().solver.add(lft_symbol<=lft_sz)
        self.thread_ctx.get_symbs().solver.add(rgt_symbol>=1)
        self.thread_ctx.get_symbs().solver.add(rgt_symbol<=rgt_sz)
        self.symbols.append((lft_symbol, rgt_symbol))
    # for i in range(0, len(self.symbols)):
    #   for j in range(0, i):
    #     self.thread_ctx.get_symbs().solver.add(z3.Or(self.symbols[i][0]!=self.symbols[j][0], self.symbols[i][1]!=self.symbols[j][1]))
    # if assoc.assoc_type == 'one_to_many':
    #   for i in range(0, sz):
    #     for j in range(0, i):
    #       solver.add(self.symbols[i][1] != self.symbols[j][1])
  def update(self, write_query):
    if self.assoc.lft == write_query.qf.table:
      lft_symbol = self.get_symbolic_param_or_value(write_query.paramA)
      rgt_symbol = self.get_symbolic_param_or_value(write_query.paramB)
    else:
      lft_symbol = self.get_symbolic_param_or_value(write_query.paramB)
      rgt_symbol = self.get_symbolic_param_or_value(write_query.paramA)
    if write_query.op == INSERT:
      self.sz += 1
      self.symbols.append((lft_symbol, rgt_symbol))
    else:
      for i,pair in enumerate(self.symbols):
        match_cond = z3.And(lft_symbol==pair[0], rgt_symbol==pair[1])
        new_lft_symbol = z3.If(match_cond, 0, pair[0])
        new_rgt_symbol = z3.If(match_cond, 0, pair[1])
        self.symbols[i] = (new_lft_symbol, new_rgt_symbol)
    if self.assoc.assoc_type == 'one_to_many':
      afid = get_field_pos_in_tuple(self.assoc.rgt, '{}_id'.format(self.assoc.rgt_field_name))
      fid = get_field_pos_in_tuple(self.assoc.rgt, 'id')
      symb_table = self.thread_ctx.get_symbs().symbolic_tables[self.assoc.rgt]
      for i in range(symb_table.sz):
        old_v = symb_table.symbols[i][afid]
        if write_query.op == INSERT:
          # XXX: assume original does not exist!
          self.thread_ctx.get_symbs().solver.add(z3.If(symb_table.symbols[i][fid]==rgt_symbol, old_v==0, True))
          symb_table.symbols[i][afid] = z3.If(symb_table.symbols[i][fid]==rgt_symbol, lft_symbol, old_v)
        else: 
          cond = z3.And(symb_table.symbols[i][fid]==rgt_symbol, symb_table.symbols[i][afid]==lft_symbol)
          symb_table.symbols[i][afid] = z3.If(cond, 0, old_v)

  def delete_obj(self, write_query):
    paramv = self.get_symbolic_param_or_value(write_query.param)
    if self.assoc.lft == write_query.table:
      for i,pair in enumerate(self.symbols):
        new_lft_symbol = z3.If(paramv==pair[0], 0, pair[0])
        self.symbols[i] = (new_lft_symbol, pair[1])
    elif self.assoc.rgt == write_query.table:
      for i,pair in enumerate(self.symbols):
        new_rgt_symbol = z3.If(paramv==pair[1], 0, pair[1])
        self.symbols[i] = (pair[0], new_rgt_symbol)
  
  def get_symbolic_param_or_value(self, v):
    return get_symbolic_param_or_value(self.thread_ctx, v)
      
      
def create_symbolic_obj_graph(thread_ctx, tables, associations):
  for t in tables:
    if t.is_temp:
      # create assocs here
      for n,assoc in t.assocs:
        rgt_t = thread_ctx.get_symbs().symbolic_tables[assoc.rgt]
        lft_t = SymbolicTable(t, globalv.TABLE_SYMBOLIC_TUPLE_CNT, thread_ctx, init_tuples=False)
        symbol_a = SymbolicAssociation(assoc, globalv.ASSOC_SYMBOLIC_TUPLE_CNT, thread_ctx, init_tuples=False)
        grouped_fields = filter(lambda f:f.name != 'id', t.get_fields())
        assoc_id_pos = get_field_pos_in_tuple(assoc.rgt, '{}_id'.format(assoc.rgt_field_name))
        for i,symbol in enumerate(rgt_t.symbols):
          lft_symbol = symbol[assoc_id_pos]
          rgt_symbol = i+1
          thread_ctx.get_symbs().solver.add(lft_symbol>=1)
          thread_ctx.get_symbs().solver.add(lft_symbol<=lft_t.sz)
          symbol_a.symbols.append((lft_symbol, rgt_symbol))
        for i in range(0, globalv.TABLE_SYMBOLIC_TUPLE_CNT):
          symbol = []
          for f in t.get_fields():
            if f.name == 'id':
              symbol.append(i+1)
            else:
              #assert(f.dependent_qf)
              # init_id = 0
              # for symb_assoc in symbol_a.symbols:
              #   init_id = z3.If(symb_assoc[0]==i+1, symb_assoc[1], init_id)
              # match_value = get_symbolic_assoc_field_value(thread_ctx, f.dependent_qf, init_id)
              #field_class = get_query_field(f.dependent_qf).field_class
              field_class = f
              match_value = get_symbol_by_field(field_class, 'group-f-{}'.format(f.name))
              if not is_bool(field_class):
                thread_ctx.get_symbs().solver.add(match_value >= field_class.get_min_value(for_z3=True), match_value <= field_class.get_max_value(for_z3=True))
              symbol.append(match_value)
          lft_t.symbols.append(symbol)
        thread_ctx.get_symbs().symbolic_tables[t] = lft_t
        thread_ctx.get_symbs().symbolic_assocs[assoc] = symbol_a

    else:
      symbol_t = SymbolicTable(t, globalv.TABLE_SYMBOLIC_TUPLE_CNT, thread_ctx)
      thread_ctx.get_symbs().symbolic_tables[t] = symbol_t
  for a in associations:
    symbol_a = SymbolicAssociation(a, globalv.ASSOC_SYMBOLIC_TUPLE_CNT, thread_ctx)
    thread_ctx.get_symbs().symbolic_assocs[a] = symbol_a

def create_symbolic_denormalized_table(thread_ctx, table):
  sz = 1
  for t in table.tables:
    sz = thread_ctx.get_symbs().symbolic_tables[t].sz * sz
  st = SymbolicTable(table, sz, thread_ctx)
  thread_ctx.get_symbs().symbolic_tables[table] = st
  return st

def create_param_map_for_query(thread_ctx, query):
  params = []
  if isinstance(query, ReadQuery):
    if query.pred:
      params += query.pred.get_all_params()
    for v,f in query.aggrs:
      params += f.get_all_params()
  else:
    params += query.get_all_params()
  for i,p in enumerate(params):
    if is_int_type(p.tipe) or is_unsigned_int_type(p.tipe):
      v = z3.Int('param-{}-{}'.format(p.symbol, i))
    elif is_bool_type(p.tipe):
      v = z3.Bool('param-{}-{}'.format(p.symbol, i))
    elif is_float_type(p.tipe):
      v = z3.Real('param-{}-{}'.format(p.symbol, i))
    elif is_string_type(p.tipe):
      v = z3.Int('param-{}-{}'.format(p.symbol, i))
    else:
      assert(False)
    if not is_bool_type(p.tipe):
      thread_ctx.get_symbs().solver.add(v<INVALID_VALUE)
    thread_ctx.get_symbs().param_symbol_map[p] = v

  if isinstance(query, ReadQuery):
    for k,v in query.includes.items():
      create_param_map_for_query(thread_ctx, v)


def update_symbolic_obj_graph(thread_ctx, write_query):
  if isinstance(write_query, UpdateObject):
    symb_table = thread_ctx.get_symbs().symbolic_tables[write_query.table]
    symb_table.update(write_query)
  elif isinstance(write_query, ChangeAssociation):
    assoc = write_query.qf.table.get_assoc_by_name(write_query.qf.field_name)
    symb_assoc = thread_ctx.get_symbs().symbolic_assocs[assoc]
    symb_assoc.update(write_query)
  elif isinstance(write_query, RemoveObject):
    # update on symbolic-tables is done via chaing the 'mask' in symbolic_object, not here
    for k,v in thread_ctx.get_symbs().symbolic_assocs.items():
      v.delete_obj(write_query)

class SymbolicQueryResult(object):
  def __init__(self, query):
    self.query = query
    self.oid = 0
    self.aggrs = {}
    self.includes = {} #key: field, value: array of SymbolicQueryResult
    self.includes_order = {}
  def __str__(self):
    s = 'Query {} : \n'.format(self.query.id if self.query else '')
    if self.query:
      s += ' id = {}\n'.format(self.oid)
    if len(self.aggrs) > 0:
      for v,f in self.aggrs.items():
        s += '  aggr {} = {}\n'.format(v, f)
    if len(self.includes) > 0:
      inner_s = ''
      for qf,ary in self.includes.items():
        s += '  include {}: \n'.format(qf)
        for i,sq in enumerate(ary):
          s += '   tuple {} match : '.format(i+1)
          s += '\n'.join(['  '+l for l in str(sq).split('\n')])
    return s
  # def test_not_empty(self, aggr_values=[], param_values=[]):
  #   not_empty = []
  #   for k,v in self.includes.items():
  #     not_empty += [x.oid != 0 for x in v]
  #   thread_ctx.get_symbs().solver.add(z3.Or(*not_empty))
  #   if len(aggr_values) > 0:
  #     for vname,v in aggr_values:
  #       for var,symbol in self.aggrs.items():
  #         if var.name == vname:
  #           thread_ctx.get_symbs().solver.add(symbol==v)
  #   if len(param_values) > 0:
  #     for vname,v in param_values:
  #       for var,symbol in thread_ctx.get_symbs().param_symbol_map.items():
  #         if var.symbol == vname:
  #           thread_ctx.get_symbs().solver.add(symbol==v)
  
#TODO: groupby is not handled!
def generate_symbolic_query_result(thread_ctx, query):
  r = SymbolicQueryResult(None)
  table = get_main_table(query.table)
  symbolic_table = thread_ctx.get_symbs().symbolic_tables[table]
  upper_id_symbols = [i+1 for i in range(0, symbolic_table.sz)]
  new_r = generate_symbolic_query_result_helper(thread_ctx, query, r, upper_id_symbols)
  if query.return_var:
    r.includes[table] = new_r
    r.includes_order[table] = query.order
  return r

# return an array
def generate_symbolic_query_result_helper(thread_ctx, query, upper_symbolic_q, upper_id_symbols):
  table = get_main_table(query.table)
  symbolic_table = thread_ctx.get_symbs().symbolic_tables[table]

  elements = []
  #filter
  for i,symbolic_tuple in enumerate(symbolic_table.symbols):
    element = SymbolicQueryResult(query)
    if query.pred:
      cond_expr = generate_condition_for_pred(thread_ctx, symbolic_tuple, query.pred)
    else:
      cond_expr = True
    or_exprs = [z3.And(uid != 0, (i+1)==uid) for uid in upper_id_symbols]
    element.oid = z3.If(z3.And(cond_expr, z3.Or(*or_exprs)), i+1, 0)
    elements.append(element)
  
  #includes
  for qf,next_query in query.includes.items():
    assoc = table.get_assoc_by_name(qf.field_name)
    assoc_pos = 0 if assoc.lft == table else 1
    for i in range(0, symbolic_table.sz):
      element = elements[i]
      next_ids = []
      for j,next_symbolic_tuple in enumerate(thread_ctx.get_symbs().symbolic_tables[qf.field_class].symbols):
        match_expr = []
        for symbolic_assoc in thread_ctx.get_symbs().symbolic_assocs[assoc].symbols:
          match_expr.append(z3.And((j+1) == symbolic_assoc[1-assoc_pos],  \
                                   (i+1) == symbolic_assoc[assoc_pos]))
        next_ids.append(z3.If(z3.Or(*match_expr), j+1, 0))
      
      next_symbolic_results = generate_symbolic_query_result_helper(thread_ctx, next_query, element, next_ids)
      if next_query.return_var:
        element.includes[qf] = next_symbolic_results
        element.includes_order[qf] = next_query.order
    
  #aggr
  for v,expr in query.aggrs:
    accu_var = 0
    for i,symbolic_tuple in enumerate(symbolic_table.symbols):
      accu_var = z3.If(elements[i].oid==0, accu_var, \
              generate_expr_for_aggr(thread_ctx, symbolic_tuple, accu_var, expr))
    upper_symbolic_q.aggrs[v] = accu_var
  
  return elements

def generate_condition_for_pred(thread_ctx, symbolic_tuple, pred):
  if isinstance(pred, ConnectOp):
    lh_expr = generate_condition_for_pred(thread_ctx, symbolic_tuple, pred.lh)
    rh_expr = generate_condition_for_pred(thread_ctx, symbolic_tuple, pred.rh)
    if pred.op == AND:
      return z3.And(lh_expr, rh_expr)
    elif pred.op == OR:
      return z3.Or(lh_expr, rh_expr)
  elif isinstance(pred, SetOp):
    #FIXME
    lh_table = get_leftmost_qf(pred.lh).table
    rh_table = get_query_field(pred.lh).field_class
    assoc = get_query_field(pred.lh).table.get_assoc_by_name(get_query_field(pred.lh).field_name)
    assoc_pos = 0 if assoc.rgt == rh_table else 1
    lh_id_pos = get_field_pos_in_tuple(lh_table, 'id')
    rh_id_pos = get_field_pos_in_tuple(rh_table, 'id')
    exprs = []
    for i,next_symbolic_tuple in enumerate(thread_ctx.get_symbs().symbolic_tables[rh_table].symbols):
      next_symbol_cond = generate_condition_for_pred(thread_ctx, next_symbolic_tuple, pred.rh)
      match_expr = []  
      for symbolic_assoc in thread_ctx.get_symbs().symbolic_assocs[assoc].symbols:
        match_expr.append(z3.And((i+1) == symbolic_assoc[1-assoc_pos],  \
                                  symbolic_tuple[lh_id_pos] == symbolic_assoc[assoc_pos]))
      exprs.append(z3.And(z3.Or(*match_expr), next_symbol_cond))
    if pred.op == EXIST:
      return z3.Or(*exprs)
    else:
      return z3.And(*exprs)
  elif isinstance(pred, AssocOp):
    fid = get_field_pos_in_tuple(pred.lh.table, '{}_id'.format(pred.lh.field_name))
    r = INVALID_VALUE
    for i,next_symbolic_tuple in enumerate(thread_ctx.get_symbs().symbolic_tables[pred.lh.field_class].symbols):
      next_symbol_cond = generate_condition_for_pred(thread_ctx, next_symbolic_tuple, pred.rh)
      r = z3.If((i+1)==symbolic_tuple[fid], next_symbol_cond, r)
    return r
  elif isinstance(pred, BinOp):
    lh_expr = generate_condition_for_pred(thread_ctx, symbolic_tuple, pred.lh)
    if pred.op == BETWEEN: #isinstance(pred.rh, DoubleParam):
      rh_expr = [generate_condition_for_pred(thread_ctx, symbolic_tuple, pred.rh.params[0]), \
                 generate_condition_for_pred(thread_ctx, symbolic_tuple, pred.rh.params[1])]
      return z3.And(lh_expr >= rh_expr[0], lh_expr <= rh_expr[1])
    elif isinstance(pred.rh, MultiParam):
      rh_expr = []
      for p in pred.rh.params:
        exp = generate_condition_for_pred(thread_ctx, symbolic_tuple, p)
        rh_expr.append(lh_expr==exp)
      return z3.Or(*rh_expr)
    else:
      rh_expr = generate_condition_for_pred(thread_ctx, symbolic_tuple, pred.rh)
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
  elif isinstance(pred, QueryField):
    fid = get_field_pos_in_tuple(pred.table, pred.field_name)
    return symbolic_tuple[fid]
  elif isinstance(pred, AtomValue):
    return pred.to_z3_value()
  elif isinstance(pred, UnaryOp):
    operand  = generate_condition_for_pred(thread_ctx, symbolic_tuple, pred.operand)
    return z3.Not(operand)
  elif isinstance(pred, Parameter):
    return thread_ctx.get_symbs().get_param_symbol_map(pred)
  else:
    assert(False)

def generate_expr_for_aggr(thread_ctx, symbolic_tuple, accu_var, expr, varmap=None):
  if isinstance(expr, BinaryExpr):
    lh_expr = generate_expr_for_aggr(thread_ctx, symbolic_tuple, accu_var, expr.lh, varmap)
    rh_expr = generate_expr_for_aggr(thread_ctx, symbolic_tuple, accu_var, expr.rh, varmap)
    if expr.op == ADD:
      return lh_expr + rh_expr
    elif expr.op == MINUS:
      return lh_expr - rh_expr
    elif expr.op == MULTIPLY:
      return lh_expr * rh_expr
    elif expr.op == DIVIDE:
      return lh_expr / rh_expr
    elif expr.op == BAND:
      return z3.And(lh_expr,rh_expr)
    elif expr.op == BOR:
      return z3.Or(lh_expr,rh_expr)
    elif expr.op == BEQ:
      return lh_expr == rh_expr
    elif expr.op == BNEQ:
      return lh_expr != rh_expr
    elif expr.op == BLE:
      return lh_expr <= rh_expr
    elif expr.op == BGE:
      return lh_expr >= rh_expr
    elif expr.op == MIN:
      return z3.If(lh_expr<rh_expr, lh_expr, rh_expr)
    elif expr.op == MAX:
      return z3.If(lh_expr>rh_expr, lh_expr, rh_expr)
  elif isinstance(expr, UnaryExpr):
    operand_expr = generate_expr_for_aggr(thread_ctx, symbolic_tuple, accu_var, expr.operand, varmap)
    if expr.op == MAX:
      return z3.If(operand_expr > accu_var, operand_expr, accu_var)
    elif expr.op == MIN:
      return z3.If(operand_expr < accu_var, operand_expr, accu_var)
    elif expr.op == COUNT:
      return accu_var + 1
    elif expr.op == AVG:
      # currently treat avg as sum
      return operand_expr + accu_var
    elif expr.op == SUM:
      return operand_expr + accu_var
  elif isinstance(expr, IfThenElseExpr):
    cond_expr = generate_expr_for_aggr(thread_ctx, symbolic_tuple, accu_var, expr.cond, varmap)
    expr1 = generate_expr_for_aggr(thread_ctx, symbolic_tuple, accu_var, expr.expr1, varmap)
    expr2 = generate_expr_for_aggr(thread_ctx, symbolic_tuple, accu_var, expr.expr2, varmap)
    return z3.If(cond_expr, expr1, expr2)
  elif isinstance(expr, AssocOp):
    fid = get_field_pos_in_tuple(expr.lh.table, '{}_id'.format(expr.lh.field_name))
    r = 0
    for i,next_symbolic_tuple in enumerate(thread_ctx.get_symbs().symbolic_tables[expr.lh.field_class].symbols):
      next_expr = generate_expr_for_aggr(thread_ctx, next_symbolic_tuple, accu_var, expr.rh, varmap)
      r = z3.If((i+1)==symbolic_tuple[fid], next_expr, r)
    return r
  elif isinstance(expr, QueryField):
    fid = get_field_pos_in_tuple(expr.table, expr.field_name)
    return symbolic_tuple[fid]
  elif isinstance(expr, AtomValue):
    return expr.to_z3_value()
  elif isinstance(expr, Parameter):
    return thread_ctx.get_symbs().get_param_symbol_map(expr)
  elif type(expr) is int or type(expr) is bool or type(expr) is float:
    return expr
  elif isinstance(expr, EnvAtomicVariable):
    return varmap[expr].v
  else:
    return expr

def check_dsop_pred_equiv(thread_ctx, table, ds_exprs, target_pred):
  tup = thread_ctx.get_symbs().symbolic_tables[get_main_table(table)].symbols[0]
  target_expr = generate_condition_for_pred(thread_ctx, tup, target_pred) 
  new_ds_exprs = []
  for pair in ds_exprs:
    rest_pred = pair[1]
    ds_expr = pair[0]
    rest_expr = generate_condition_for_pred(thread_ctx, tup, rest_pred) if rest_pred else True
    new_ds_exprs.append(z3.And(ds_expr, rest_expr))
  ds_expr = or_exprs(new_ds_exprs)

  #print 'target_expr = {}; ds_expr = {}'.format(z3.simplify(target_expr), z3.simplify(ds_expr))
  thread_ctx.get_symbs().solver.push()
  thread_ctx.get_symbs().solver.add(z3.Not(target_expr==ds_expr))
  r = (thread_ctx.get_symbs().solver.check() == z3.unsat)
  # if r == False:
  #   print print_table_in_model(thread_ctx, thread_ctx.get_symbs().solver.model())
  #   print_all_debug_expr(thread_ctx.get_symbs().solver.model())
  thread_ctx.get_symbs().solver.pop()
  return r

def check_pred_equiv(thread_ctx, table, pred1, pred2):
  tup = thread_ctx.get_symbs().symbolic_tables[get_main_table(table)].symbols[0]
  symb_pred1 = generate_condition_for_pred(thread_ctx, tup, pred1) if pred1 else True
  symb_pred2 = generate_condition_for_pred(thread_ctx, tup, pred2) if pred2 else True

  thread_ctx.get_symbs().solver.push()
  thread_ctx.get_symbs().solver.add(z3.Not(symb_pred1==symb_pred2))
  r = (thread_ctx.get_symbs().solver.check() == z3.unsat)
  #if r == False:
  #  print print_table_in_model(thread_ctx, thread_ctx.get_symbs().solver.model())
  thread_ctx.get_symbs().solver.pop()
  return r

def check_pred_subset(thread_ctx, table, pred1, pred2): # pred1 -> pred2
  tup = thread_ctx.get_symbs().symbolic_tables[get_main_table(table)].symbols[0]
  symb_pred1 = generate_condition_for_pred(thread_ctx, tup, pred1) if pred1 else True
  symb_pred2 = generate_condition_for_pred(thread_ctx, tup, pred2) if pred2 else True

  thread_ctx.get_symbs().solver.push()
  thread_ctx.get_symbs().solver.add(z3.Not(z3.Implies(symb_pred1, symb_pred2)))
  r = (thread_ctx.get_symbs().solver.check() == z3.unsat)
  thread_ctx.get_symbs().solver.pop()
  return r