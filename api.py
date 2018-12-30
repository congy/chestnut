from parsimonious.grammar import rule_grammar, NodeVisitor, RuleVisitor, Grammar
from parsimonious.nodes import Node
from pred import *
from schema import *
from query import *

# body = obj_def? query_stmt+
language=r"""
  body = space query_stmt+

  space = ~"\s*"
  quote = "\"" / "'"
  chars = ~"[^\"^']*"
  number = ~"[0-9]+"
  digit1to9 = ~"[1-9]"
  digit = ~"[0-9]"
  digits = digit+
  comma = "," space

  identifier = ~"[A-Za-z0-9_]+"
  int = "-"? ((digit1to9 digits) / digit)
  float = int "." digits
  string = quote chars quote
  name = space identifier space
  date = date_format1 / date_format2
  date_format1 = number "-" number "-" number
  date_format2 = date_format1 " " number ":" number ":" number
  atom = "True" / "False" /  float / int / date / string
  field = identifier ("." identifier)*
  value = atom / param / multiple_values / field

  multiple_values = "[" (value (comma value)+)? "]"
  param = "param[" identifier "]"

  obj_def = space begin_def field_defs end_def space
  begin_def = "class " name  "< NRecord" ("[" number "]")? ":" space
  end_def = "end"
  field_defs = ((field_def / assoc_def) space)+
  field_def = type name (comma space value_range)?
  type = "smallint" / "int" / "uint " / "bool" / "float" / "date" / ("varchar(" number ")") / "string"
  value_range = "values" "=" "[" (value_pair / value_prob_pairs) "]"
  value_pair = atom comma atom
  value_prob_pairs = value_prob_pair (comma value_prob_pair)*
  value_prob_pair = "(" value_pair ")"
  assoc_def = assoc_type ":" name "=>" name (comma ratio)?
  assoc_type = "belongs_to" / "has_many" / "has_one"
  ratio = "ratio=" number

  query_stmt = ((identifier " = " stmt) / stmt) space
  stmt = identifier ("." query_api space)+
  query_api = "all()" / ("where(" pred ")") / ("project(" fields ")") / ("include(" fields ")") / ("aggr(" aggr_params ")") / ("orderby(" fields ")") / ("groupby(" fields ")") / ("limit(" number ")") / identifier
  fields = (field (comma field)*)?
  pred = ("exists(" field comma pred")") / ("forall(" field comma pred")") / ("(" pred ")" connect_op "(" pred ")") / (value p_binop value) 
  cmp_op = "<=" / "<" / ">=" / ">" / "==" / "!=" / "in" / "between" / "%like%"
  p_binop = space cmp_op space
  connect_op = space ("||" / "&&") space
  aggr_params = expr comma quote identifier quote
  expr = e_nop / (e_uop "(" subexpr ")")
  E = (T space "+" space E) / (T space "-" space E) / T
  T = (F space "*" space T) / (F space "/" space T) / F
  F = ("(" E ")") / value
  subexpr = ("ite(" pred comma subexpr comma subexpr")") / E
  e_nop = "count()"
  e_uop = "sum" / "avg" / "min" / "max"
  """

class PNode(object):
  def __init__(self, children):
    self.children = filter(lambda x: x is not None, children)
  def visit(self, state):
    self.visited_children = []
    for c in self.children:
      self.visited_children.append(c.visit(state))
    return self.visited_children

class PLeaf(object):
  def visit(self, state):
    return self

class VisitState(object):
  def __init__(self):
    self.tables = []
    self.associations = []
    self.queries = {}
    self.query_stack = []
    self.table_stack = []
    self.assigned_tables_and_assocs = False
  def find_table_by_name(self, name, exist=True):
    for t in self.tables:
      if t.name == name:
        return t
    if exist:
      assert False, "table {} is not defined".format(name)
    else:
      return None
  def find_query_by_name(self, name):
    for k,v in self.queries.items():
      if k == name:
        return v
    return None
  def add_to_query_stack(self, q):
    self.query_stack.append(q)
    self.table_stack.append(get_main_table(q.table))
  def pop_query_stack(self):
    self.query_stack.pop()
    self.table_stack.pop()
  def clear_query_stack(self):
    self.query_stack = []
    self.table_stack = []
  def set_tables_and_assocs(self, tables, assocs):
    self.tables = tables
    self.associations = assocs
    self.assigned_tables_and_assocs = True

#  body = obj_def+ query_stmt+
class BodyPNode(PNode):
  def __init__(self, children):
    super(BodyPNode, self).__init__(children)
  def visit(self, state):
    if state.assigned_tables_and_assocs == False:
      # handle class def first
      for c in self.children:
        if isinstance(c, ObjDefPNode):
          c.visit(state)
      # handle associations
      assocs = []
      for a in state.associations:
        assocs.append(get_new_assoc(a[0], a[1], state.find_table_by_name(a[2]), state.find_table_by_name(a[3]), a[4], a[5], a[6], a[7]))
      state.associations = assocs

      print 'tables:'
      for t in state.tables:
        print 'table {}, sz = {}'.format(t.name, t.sz)
        for f in t.get_fields():
          print '\t{} type = {}, vrange = {}, prob = {}'.format(f.name, f.tipe, f.range, f.value_with_prob)
      print 'associations:'
      for a in state.associations:
        print "{} {} {} {} {} {} {}".format(a.assoc_type, a.lft.name, a.rgt.name, a.lft_ratio, a.rgt_ratio, a.lft_field_name, a.rgt_field_name)
      
    # handle queries then
    for c in self.children:
      if isinstance(c, QueryStmtPNode):
        c.visit(state)

    print "\n-----\nqueries:"
    queries = []
    for k,v in state.queries.items():
      if v.upper_query is None:
        queries.append(v)

    for q in queries:
      print q
      print ' * '

#  space = ~"\s*"

#  quote = """ / "'"

#  chars = ~"[^"^']*"
class CharsPNode(PLeaf):
  def __init__(self, text):
    self.text = text

#  number = ~"[0-9]+"
class NumberPNode(PLeaf):
  def __init__(self, text):
    self.text = text

#  identifier = ~"[A-Za-z0-9_]+"
class IdentifierPNode(PLeaf):
  def __init__(self, text):
    self.text = text

#  int = "-"? ((digit1to9 digits) / digit)
class IntPNode(PLeaf):
  def __init__(self, number):
    self.number = number

#  float = int "." digits
class FloatPNode(PLeaf):
  def __init__(self, number):
    self.number = number

#  string = quote chars quote
class StringPNode(PLeaf):
  def __init__(self, text):
    self.text = text

#  name = space identifier space
class NamePNode(PLeaf):
  def __init__(self, text):
    self.text = text

#  date = date_format1 / date_format2
class DatePNode(PLeaf):
  def __init__(self, text):
    self.text = text

#  date_format1 = number "-" number "-" number
class DateFormat1PNode(PLeaf):
  def __init__(self, text):
    self.text = text

#  date_format2 = date_format1 " " number ":" number ":" number
class DateFormat2PNode(PLeaf):
  def __init__(self, text):
    self.text = text

#  atom = "True" / "False" /  float / int / date / string
class AtomPNode(PLeaf):
  def __init__(self, value, typ):
    self.value = value
    self.typ = typ
  def visit(self, state):
    return AtomValue(self.value, self.typ)

#  field = identifier ("." identifier)*
class FieldPNode(PNode):
  def __init__(self, children):
    super(FieldPNode, self).__init__(children)
  def visit(self, state):
    assert len(state.table_stack)>0, "table stack is empty"
    cur_table = state.table_stack[-1]
    fs = []
    for c in self.children:
      fname = cur_table.get_field_by_name(c.text)
      nextf = QueryField(c.text, cur_table)
      fs.append(nextf)
      if not is_atomic_field(nextf):
        next_table = cur_table.get_nested_table_by_name(c.text)
        cur_table = get_main_table(next_table)
    f = None
    for fi in reversed(fs):
      f = fi if f is None else AssocOp(fi, f)
    # print 'field text = {}'.format('.'.join([c.text for c in self.children]))
    # print 'field = {}'.format(f)
    return f

#  value = atom / param / multiple_values / field
class ValuePNode(PLeaf):
  def __init__(self, value):
    self.value = value
  def visit(self, state):
    return self.value.visit(state)

#  multiple_values = "[" (value (", " value)+)? "]"
class MultipleValuesPNode(PNode):
  def __init__(self, children):
    super(MultipleValuesPNode, self).__init__(children)
  def visit(self, state):
    super(MultipleValuesPNode, self).visit(state)
    return MultiParam(params=self.visited_children)

#  param = "param[" identifier "]"
class ParamPNode(PLeaf):
  def __init__(self, text):
   self.text = text 
  def visit(self, state):
    return Parameter(self.text)

#  obj_def = space begin_def field_defs end_def space
class ObjDefPNode(PNode):
  def __init__(self, children):
    super(ObjDefPNode, self).__init__(children)
    assert(len(self.children)==2) #begin_def and field_defs
  def visit(self, state):
    assert isinstance(self.children[0], BeginDefPNode)
    table = self.children[0].visit(state)
    state.tables.append(table)
    state.table_stack.append(table)
    for c in self.children[1:]:
      r = c.visit(state)
      for f in r:
        if f and isinstance(f, Field):
          table.add_field(f)
      #associations are ignored for now
    state.table_stack.pop(-1)
    

#  begin_def = "class " name  "< NRecord" ("[" number "]")? ":" space
class BeginDefPNode(PLeaf):
  def __init__(self, name, sz=1000):
    self.name = name
    self.sz = sz
  def visit(self, state):
    return Table(self.name, self.sz)

#  end_def = "end"

#  field_defs = ((field_def / assoc_def) space)+
class FieldDefsPNode(PNode):
  def __init__(self, children):
    super(FieldDefsPNode, self).__init__(children)

#  field_def = type name ("," space value_range)?
class FieldDefPNode(PLeaf):
  def __init__(self, field):
    self.field = field
  def visit(self, state):
    return self.field

#  type = "smallint" / "int" / "uint " / "bool" / "float" / "date" / ("varchar(" number ")") / "string"
class TypePNode(PLeaf):
  def __init__(self, text):
    self.text = text

#  value_range = "values" "=" "[" (value_pair / value_prob_pairs) "]"
#  value_pair = atom ", " atom
#  value_prob_pairs = value_prob_pair ("," space value_prob_pair)*
#  value_prob_pair = "(" value_pair ")"

#  assoc_def = assoc_type ":" name "=>" name ("," space ratio)?
class AssocDefPNode(PLeaf):
  def __init__(self, assoc_type, assoc_name, klass, ratio):
    self.assoc_type = assoc_type
    self.assoc_name = assoc_name
    self.klass = klass
    self.ratio = ratio
  def visit(self, state):
    #get_new_assoc("order_to_item", "one_to_many", order, lineitem, "lineitems", "order")
    # first check existing associations
    exist_assoc = False
    if self.assoc_type == "belongs_to" or self.assoc_type == "has_one":
      lft_table = self.klass
      rgt_table = state.table_stack[-1].name
      assoc_type = "one_to_many"
      for a in state.associations:
        if a[2] == lft_table and a[3] == rgt_table:
          assert a[1] == "one_to_many"
          a[5] = self.assoc_name
          exist_assoc = True
      if not exist_assoc:
        state.associations.append(["{}_to_{}".format(lft_table, rgt_table),\
             assoc_type, lft_table, rgt_table, lft_table.lower(), self.assoc_name, 0, 0])
    elif self.assoc_type == "has_many":
      lft_table = state.table_stack[-1].name
      rgt_table = self.klass
      assoc_type = None
      for a in state.associations:
        if a[2] == lft_table and a[3] == rgt_table: # defined as one_to_many before
          assert a[1] == "one_to_many"
          a[4] = self.assoc_name
          exist_assoc = True
        elif a[2] == rgt_table and a[3] == lft_table: # defined as `has_many` before
          assert a[1] is None
          a[1] = "many_to_many"
          a[5] = self.assoc_name
          a[7] = self.ratio
          exist_assoc = True
      if not exist_assoc:
        state.associations.append(["{}_to_{}".format(lft_table, rgt_table),\
             assoc_type, lft_table, rgt_table, self.assoc_name, lft_table.lower(), self.ratio, rgt_table.lower()+'s'])
    return None

#  assoc_type = "belongs_to" / "has_many" / "has_one"
class AssocTypePNode(PLeaf):
  def __init__(self, text):
    self.text = text

#  ratio = "ratio=" number
class RatioPNode(PLeaf):
  def __init__(self, ratio):
    self.ratio = ratio

#  query_stmt = ((identifier " = " stmt) / stmt) space
class QueryStmtPNode(PNode):
  def __init__(self, variable, stmt):
    self.variable = variable
    self.children = [stmt]
  def visit(self, state):
    state.clear_query_stack()
    q = self.children[0].visit(state)
    if self.variable is not None:
      state.queries[self.variable] = q

#  stmt = identifier ("." query_api space)+
class StmtPNode(PNode):
  def __init__(self, variable, queries):
    self.variable = variable
    self.children = queries
  def visit(self, state):
    q = state.find_query_by_name(self.variable)
    if q is None:
      table = state.find_table_by_name(self.variable)
      q = get_all_records(table)
    state.add_to_query_stack(q)
    super(StmtPNode, self).visit(state)
    q = state.query_stack[-1]
    #state.pop_query_stack()
    return q

#  query_api = "all()" / ("where(" pred ")") / ("project(" fields ")") / ("include(" fields ")") / ("aggr(" aggr_params ")") / ("orderby(" fields ")") / ("groupby(" fields ")") / ("limit(" number ")") / identifier
class QueryApiPNode(PNode):
  def __init__(self, children):
    super(QueryApiPNode, self).__init__(children)
  def visit(self, state):
    cur_query = state.query_stack[-1]
    if isinstance(self.children[0], IdentifierPNode):
      f = QueryField(self.children[0].text, cur_query.table)
      if f not in cur_query.includes:
        cur_query.finclude(f)
      q = cur_query.get_include(f)
      state.add_to_query_stack(q)
    elif self.children[0].text.startswith("all()"):
      pass
    elif self.children[0].text.startswith("where("):
      pred = self.children[1].visit(state)
      cur_query.pfilter(pred)
    elif self.children[0].text.startswith("project("):
      fields = self.children[1].visit(state)
      cur_query.project(fields)
    elif self.children[0].text.startswith("include("):
      for f in self.children[1].visit(state):
        if f not in cur_query.includes:
          cur_query.finclude(f)
    elif self.children[0].text.startswith("aggr("):
      expr = self.children[1].expr.visit(state)
      cur_query.aggr(expr, self.children[1].identifier)
    elif self.children[0].text.startswith("orderby("):
      fields = self.children[1].visit(state)
      cur_query.orderby(fields)
    elif self.children[0].text.startswith("groupby("):
      fields = self.children[1].visit(state)
      # TODO: now assume every groupby result is assigned to a variable
      newq = cur_query.groupby(fields)
      state.query_stack.append(newq)
    elif self.children[0].text.startswith("limit("):
      cur_query.return_limit(int(self.children[1].text))
    else:
      assert(False)
    
#  fields = (field (", " field)*)?
class FieldsPNode(PNode):
  def __init__(self, children):
    super(FieldsPNode, self).__init__(children)

#  pred = ("exists(" field ", " pred")") / ("forall(" field ", " pred")") / ("(" pred ")" connect_op "(" pred ")") / (value p_binop value)
class PredPNode(PNode):
  def __init__(self, qtype, children):
    self.qtype = qtype
    super(PredPNode, self).__init__(children)
  def visit(self, state):
    if self.qtype == 'exists':
      qf = self.children[0].visit(state)
      state.table_stack.append(get_main_table(qf.field_class))
      pred = self.children[1].visit(state)
      state.table_stack.pop(-1)
      return SetOp(qf, EXIST, pred)
    elif self.qtype == 'forall':
      pass
    elif self.qtype == 'connectop':
      lft = self.children[0].visit(state)
      op = self.children[1].visit(state)
      rgt = self.children[2].visit(state)
      return ConnectOp(lft, op, rgt)
    elif self.qtype == 'binop':
      lft = self.children[0].visit(state)
      op = self.children[1].visit(state)
      rgt = self.children[2].visit(state)
      return BinOp(lft, op, rgt)

#  cmp_op = "<" / "<=" / ">" / ">=" / "==" / "!=" / "in" / "between" / "%like%"
class CmpOpPNode(PLeaf):
  def __init__(self, text):
    self.text = text

#  p_binop = space (cmp_op) space
class PBinopPNode(PLeaf):
  def __init__(self, text):
    self.text = text
  def visit(self, state):
    if self.text == '<':
      return LT
    elif self.text == '<=':
      return LE
    elif self.text == '>':
      return GT
    elif self.text == '>=':
      return GE
    elif self.text == '==':
      return EQ
    elif self.text == '!=':
      return NE
    elif self.text == 'in':
      return IN
    elif self.text == 'between':
      return BETWEEN
    elif self.text == '%like':
      return SUBSTR

#  connect_op = space ("||" / "&&") space
class ConnectOpPNode(PNode):
  def __init__(self, text):
    self.text = text
  def visit(self, state):
    if self.text == '||':
      return OR
    elif self.text == '&&':
      return AND
  

#  aggr_params = expr ", " quote identifier quote
class AggrParamsPNode(PLeaf):
  def __init__(self, expr, identifier):
    self.expr = expr
    self.identifier = identifier

#  expr = e_nop / (e_uop "(" subexpr ")")
class ExprPNode(PNode):
  def __init__(self, children):
    super(ExprPNode, self).__init__(children)
  def visit(self, state):
    if len(self.children) == 1:
      return UnaryExpr(COUNT)
    else:
      op = self.children[0].visit(state)
      expr = self.children[1].visit(state)
      return UnaryExpr(op, expr)

#  E = (T space "+" space E) / (T space "-" space E) / T
class EPNode(PNode):
  def __init__(self, children):
    super(EPNode, self).__init__(children)
  def visit(self, state):
    if len(self.children) == 1:
      return self.children[0].visit(state)
    else:
      lh = self.children[0].visit(state)
      op = ADD if self.children[1] == '+' else MINUS
      rh = self.children[2].visit(state)
      return BinaryExpr(lh, op, rh)

#  T = (F space "*" space T) / (F space "/" space T) / F
class TPNode(PNode):
  def __init__(self, children):
    super(TPNode, self).__init__(children)
  def visit(self, state):
    if len(self.children) == 1:
      return self.children[0].visit(state)
    else:
      lh = self.children[0].visit(state)
      op = MULTIPLY if self.children[1] == '*' else DIVIDE
      rh = self.children[2].visit(state)
      return BinaryExpr(lh, op, rh)

#  F = ("(" E ")") / value
class FPNode(PLeaf):
  def __init__(self, node):
    self.node = node
  def visit(self, state):
    return self.node.visit(state)

#  subexpr = ("ite(" pred ", " subexpr ", " subexpr")") / E
class SubexprPNode(PNode):
  def __init__(self, children):
    super(SubexprPNode, self).__init__(children)
  def visit(self, state):
    if len(self.children) == 1:
      return self.children[0].visit(state)
    else:
      op1 = self.children[1].visit(state)
      print op1
      op2 = self.children[2].visit(state)
      op3 = self.children[3].visit(state)
      return IfThenElseExpr(op1, op2, op3)

#  e_nop = "count()"
class ENopPNode(PLeaf):
  def __init__(self, text):
    self.text = text

#  e_uop = "sum" / "avg" / "min" / "max"
class EUopPNode(PLeaf):
  def __init__(self, text):
    self.text = text
  def visit(self, state):
    if self.text == "sum":
      return SUM
    elif self.text == "avg":
      return AVG
    elif self.text == "min":
      return MIN
    elif self.text == "max":
      return MAX


class MyVisitor(RuleVisitor):
  global language
  grammar = Grammar(language)
  #  body = obj_def+ query_stmt+
  #  body = space query_stmt+
  def visit_body(self, node, visited_children):
    #return BodyPNode(visited_children[0] + visited_children[1])
    return BodyPNode(visited_children[1])

  #  space = ~"\s*"
  def visit_space(self, node, visited_children):
    return None 

  #  quote = """ / "'"
  def visit_quote(self, node, visited_children):
    return None

  #  chars = ~"[^"^']*"
  def visit_chars(self, node, visited_children):
    return CharsPNode(node.text)

  #  identifier = ~"[A-Za-z0-9_]+"
  def visit_identifier(self, node, visited_children):
    return IdentifierPNode(node.text)

  #  int = "-"? ((digit1to9 digits) / digit)
  def visit_int(self, node, visited_children):
    return IntPNode(int(node.text))

  #  float = int "." digits
  def visit_float(self, node, visited_children):
    #TODO: children = visited_children
    return FloatPNode(float(node.text))

  #  string = quote chars quote
  def visit_string(self, node, visited_children):
    #TODO: children = visited_children
    return StringPNode(visited_children[1].text)

  #  name = space identifier space
  def visit_name(self, node, visited_children):
    return NamePNode(visited_children[1].text)

  #  date = date_format1 / date_format2
  def visit_date(self, node, visited_children):
    #TODO: children = visited_children
    return DatePNode(visited_children[0].text)

  #  date_format1 = number "-" number "-" number
  def visit_date_format1(self, node, visited_children):
    return DateFormat1PNode(node.text)

  #  date_format2 = date_format1 " " number ":" number ":" number
  def visit_date_format2(self, node, visited_children):
    return DateFormat2PNode(node.text)

  #  atom = "True" / "False" /  float / int / date / string
  def visit_atom(self, node, visited_children):
    if node.text == "True":
      return AtomPNode(True, 'bool')
    elif node.text == "False":
      return AtomPNode(False, 'bool')
    elif isinstance(visited_children[0], FloatPNode):
      return AtomPNode(visited_children[0].number, 'float')
    elif isinstance(visited_children[0], IntPNode):
      return AtomPNode(visited_children[0].number, 'int')
    elif isinstance(visited_children[0], DatePNode):
      return AtomPNode(visited_children[0].text, 'date')
    elif isinstance(visited_children[0], StringPNode):
      return AtomPNode(visited_children[0].text, 'string')

  #  field = identifier ("." identifier)*
  def visit_field(self, node, visited_children):
    flist = []
    if type(visited_children[1]) is Node:
      flist.append(visited_children[0])
    else:
      flist.append(visited_children[0])
      for c in visited_children[1]:
        flist.append(c[1])
    return FieldPNode(flist)

  #  value = atom / param / multiple_values / field
  def visit_value(self, node, visited_children):
    return ValuePNode(visited_children[0])

  #  multiple_values = "[" (value (", " value)+)? "]"
  def visit_multiple_values(self, node, visited_children):
    nodes = [visited_children[1][0][0]]
    if len(visited_children[1][0]) > 1:
      for c in visited_children[1][0][1]:
        nodes.append(c[1])
    return MultipleValuesPNode(nodes)

  #  param = "param[" identifier "]"
  def visit_param(self, node, visited_children):
    return ParamPNode(visited_children[1].text)

  #  obj_def = space begin_def field_defs end_def space
  def visit_obj_def(self, node, visited_children):
    return ObjDefPNode(visited_children)

  #  begin_def = "class " name  "< NRecord" ("[" number "]")? ":" space
  def visit_begin_def(self, node, visited_children):
    table_name = visited_children[1].text
    sz = 1000
    if type(visited_children[3]) is not Node:
      sz = int(visited_children[3][0][1].text)
    return BeginDefPNode(table_name, sz)

  #  end_def = "end"
  def visit_end_def(self, node, visited_children):
    return None 

  #  field_defs = ((field_def / assoc_def) space)+
  def visit_field_defs(self, node, visited_children):
    fields = []
    for i,c in enumerate(visited_children):
      fields.append(c[0][0])
    return FieldDefsPNode(fields)

  #  field_def = type name ("," space value_range)?
  def visit_field_def(self, node, visited_children):
    typ = visited_children[0].text
    name = visited_children[1].text
    f = Field(name, typ)
    if type(visited_children[-1]) is not Node:
      value = visited_children[-1][-1][-1]
      if type(value) is tuple:
        f.range = [value[0], value[1]]
      else: #type(value_range) is list:
        f.value_with_prob = value
    return FieldDefPNode(f)

  #  type = "smallint" / "int" / "uint " / "bool" / "float" / "date" / ("varchar(" number ")") / "string"
  def visit_type(self, node, visited_children):
    return TypePNode(node.text)

  #  value_range = "values" "=" "[" (value_pair / value_prob_pairs) "]"
  def visit_value_range(self, node, visited_children):
    return visited_children[3][0] 

  #  value_pair = atom ", " atom
  def visit_value_pair(self, node, visited_children):
    return (visited_children[0].value, visited_children[-1].value) 

  #  value_prob_pairs = value_prob_pair (comma value_prob_pair)*
  def visit_value_prob_pairs(self, node, visited_children):
    pairs = [visited_children[0]]
    for c in visited_children[1]:
      pairs.append(c[1])
    return pairs

  #  value_prob_pair = "(" value_pair ")"
  def visit_value_prob_pair(self, node, visited_children):
    return visited_children[1] 

  #  assoc_def = assoc_type ":" name "=>" name (comma ratio)?
  def visit_assoc_def(self, node, visited_children):
    assoc_type = visited_children[0].text
    lft_name = visited_children[2].text
    rgt_class = visited_children[4].text
    ratio = None
    if not isinstance(visited_children[-1], Node):
      ratio = visited_children[-1][0][1]
    return AssocDefPNode(assoc_type, lft_name, rgt_class, ratio)

  #  assoc_type = "belongs_to" / "has_many" / "has_one"
  def visit_assoc_type(self, node, visited_children):
    return AssocTypePNode(node.text)

  #  ratio = "ratio=" number
  def visit_ratio(self, node, visited_children):
    return RatioPNode(int(visited_children[1].text))

  #  query_stmt = ((identifier " = " stmt) / stmt) space
  def visit_query_stmt(self, node, visited_children):
    variable = None
    if isinstance(visited_children[0][0], StmtPNode):
      stmt = visited_children[0][0]
    else:
      variable = visited_children[0][0][0].text
      stmt = visited_children[0][0][2]
    return QueryStmtPNode(variable, stmt)

  #  stmt = identifier ("." query_api space)+
  def visit_stmt(self, node, visited_children):
    identifier = visited_children[0].text
    queries = []
    for i,c in enumerate(visited_children[1]):
      queries.append(c[1])
    return StmtPNode(identifier, queries)

  #  query_api = "all()" / ("where(" pred ")") / ("project(" fields ")") / ("include(" fields ")") / ("aggr(" aggr_params ")") / ("orderby(" fields ")") / ("groupby(" fields ")") / ("limit(" number ")") / identifier
  def visit_query_api(self, node, visited_children):
    if isinstance(visited_children[0], Node):
      return QueryApiPNode(visited_children)
    elif isinstance(visited_children[0], IdentifierPNode):
      return QueryApiPNode(visited_children)
    else:
      return QueryApiPNode(visited_children[0])

  #  fields = (field (", " field)*)?
  def visit_fields(self, node, visited_children):
    #TODO: children = visited_children
    if isinstance(visited_children[0], Node):
      return []
    flist = []
    if isinstance(visited_children[0][1], Node):
      flist.append(visited_children[0][0])
    else:
      for c in visited_children[0][1]:
        flist.append(c[1])
    return FieldsPNode(flist)

  #  pred = ("exists(" field ", " pred ")") / ("forall(" field ", " pred")") / ("(" pred ")" connect_op "(" pred ")") / (value p_binop value)
  def visit_pred(self, node, visited_children):
    if node.text.startswith('exists'):
      qtype = 'exists' 
      children = [visited_children[0][1], visited_children[0][3]]
    elif node.text.startswith('forall'):
      qtype = 'forall'
      children = [visited_children[0][1], visited_children[0][3]]
    elif node.text.startswith('('):
      qtype = 'connectop'
      children = [visited_children[0][1], visited_children[0][3], visited_children[0][5]]
    else:
      qtype = 'binop'
      children = [visited_children[0][0], visited_children[0][1], visited_children[0][2]]
    return PredPNode(qtype, children)

  #  cmp_op = "<" / "<=" / ">" / ">=" / "==" / "!=" / "in" / "between" / "%like%"
  def visit_cmp_op(self, node, visited_children):
    return CmpOpPNode(node.text)

  #  p_binop = space cmp_op space
  def visit_p_binop(self, node, visited_children):
    return PBinopPNode(visited_children[1].text)

  #  connect_op = space ("||" / "&&") space
  def visit_connect_op(self, node, visited_children):
    return ConnectOpPNode(visited_children[1][0].text)

  #  aggr_params = expr ", " quote identifier quote
  def visit_aggr_params(self, node, visited_children):
    return AggrParamsPNode(visited_children[0], visited_children[3].text)

  #  expr = e_nop / (e_uop "(" subexpr ")")
  def visit_expr(self, node, visited_children):
    if isinstance(visited_children[0], ENopPNode):
      return ExprPNode([visited_children[0]])
    else:
      return ExprPNode([visited_children[0][0], visited_children[0][2]])

  #  E = (T space "+" space E) / (T space "-" space E) / T
  def visit_E(self, node, visited_children):
    if isinstance(visited_children[0], TPNode):
      return EPNode([visited_children[0]])
    else:
      return EPNode([visited_children[0][0], visited_children[0][2].text, visited_children[0][4]])

  #  T = (F space "*" space T) / (F space "/" space T) / F
  def visit_T(self, node, visited_children):
    if isinstance(visited_children[0], FPNode):
      return TPNode([visited_children[0]])
    else:
      return TPNode([visited_children[0][0], visited_children[0][2].text, visited_children[0][4]])

  #  F = ("(" E ")") / value
  def visit_F(self, node, visited_children):
    if isinstance(visited_children[0], ValuePNode):
      return FPNode(visited_children[0])
    else:
      return FPNode(visited_children[0][1])

  #  subexpr = ("ite(" pred ", " subexpr ", " subexpr")") / E
  def visit_subexpr(self, node, visited_children):
    if isinstance(visited_children[0], EPNode):
      return SubexprPNode([visited_children[0]])
    else:
      return SubexprPNode([visited_children[0][0].text, visited_children[0][1], visited_children[0][3], visited_children[0][5]])

  #  e_nop = "count()"
  def visit_e_nop(self, node, visited_children):
    return ENopPNode(node.text)

  #  e_uop = "sum" / "avg" / "min" / "max"
  def visit_e_uop(self, node, visited_children):
    #TODO: children = visited_children
    return EUopPNode(node.text)

