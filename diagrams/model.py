from functional import seq

class ChestnutModel:

  def __init__(self, model):
    self.items = seq(model.values()) \
      .map(get_ds) \
      .to_list()

  # self.render(table data, graph)
  def render(self, data, g):
    # print('Root')

    for item in self.items:
      item.render(data, g, g)


def get_ds(model):
  typ = model['type']
  if 'Index' == typ:
    return IndexDS(model)
  if 'BasicArray' == typ:
    return ArrayDS(model)
  raise Exception(f"Unknown type: '{typ}'.")


def make_table_row(vals):
  return '\n'.join([ '<<table><tr>' ] + vals + [ '</tr></table>>' ])


class DS():

  def __init__(self, model):
    self.type = model['type']
    self.path = model['table']
    self.table = self.path.split('.')[-1]
    self.value = model['value']

    self.nested = []

    if 'nested' in self.value:
      self.nested = seq(self.value['nested']) \
        .map(get_ds) \
        .to_list()

  def canon_name(self):
    return f'{self.type}_{self.path}'

  # self.render(table data, graph, direct subgraph)
  def render(self, data, g, d):



    (head, rows) = data[self.table]

    # Create a new subgraph for this DS.
    with d.subgraph(name='cluster_' + self.canon_name()) as d_new:
      d_new.attr(label=f'{self.type}[{self.path}]')

      data_table_label = make_table_row([
        f'<td port="{i}"></td>'
        for i, row in enumerate(rows)
      ])

      d_new.node(self.canon_name(), label=data_table_label)

      #c.attr(style='filled', color='lightgrey')
      #c.node_attr.update(style='filled', color='white')
      #c.edges([('a0', 'a1'), ('a1', 'a2'), ('a2', 'a3')])
      #c.attr(label='process #1')

      for nested in self.nested:
        nested.render(data, g, d_new)



class IndexDS(DS):
  def __init__(self, model):
    super().__init__(model)


class ArrayDS(DS):
  def __init__(self, model):
    super().__init__(model)
