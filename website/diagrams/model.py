from functional import seq


REP_ATTRS = {
  'style': 'invisible',
  'fixedsize': 'true',
  'width': '0',
  'height': '0'
  }


class ChestnutModel:

  def __init__(self, model):
    self.items = seq(model.values()) \
      .map(get_ds) \
      .to_list()

  # self.render(table data, graph)
  def render(self, data, g):
    # print('Root')

    g.attr(rankdir='LR')

    rep_names = [
      item.render(data, g, g, [])
      for item in self.items
    ]

    align_names = [
      rep_name + '_align' for rep_name in rep_names
    ]

    with g.subgraph() as r:
      r.attr(rank='same')
      for align_name in align_names:
        r.node(align_name)
    for align_name, rep_name in zip(align_names, rep_names):
      g.edge(align_name, rep_name)
    g.edges(zip(align_names, align_names[1:]))



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
  def render(self, data, g, d, path):

    (head, rows) = data[self.table]

    path = path + [ self.canon_name() ]
    rep_name = '_'.join(path + [ 'rep' ])

    # Create a new subgraph for this DS.
    with d.subgraph(name='_'.join([ 'cluster' ] + path),
        graph_attr={ 'style': 'filled', 'color': '#f3f3f3' }) as d_new:

      d_new.attr(label=f'{self.type}[{self.path}]')
      d_new.node(rep_name, label='', **REP_ATTRS)

      subrep_names = []
      for i, row in enumerate(rows):
        row_path = path + [ str(i) ]

        subrep_name = '_'.join(row_path + [ 'rep' ])
        subrep_names.append(subrep_name)

        label_name = f'{head[0]}={row[0]}'

        # NESTED CASE
        if self.nested:
          with d_new.subgraph(name='_'.join([ 'cluster' ] + row_path),
              graph_attr={ 'style': 'solid', 'color': 'black' }) as d_row:

            d_row.attr(label=label_name)
            # Rep node.
            d_row.node(subrep_name, label='', **REP_ATTRS)

            for nested in self.nested:
              nested.render(data, g, d_row, row_path)
        # NON NESTED CASE
        else:
          d_new.node(subrep_name, label=label_name, shape='square')

      #if not self.nested:
      d_new.edges(zip(subrep_names, subrep_names[1:]))



    # data_table_label = make_table_row([
    #   f'<td port="{i}"> </td>'
    #   for i, row in enumerate(rows)
    # ])
    #
    # d_new.node(self.canon_name(),
    #   label=data_table_label, shape='plaintext')
    #
    # for nested in self.nested:
    #   nested.render(data, g, d_new)

    return rep_name



class IndexDS(DS):
  def __init__(self, model):
    super().__init__(model)


class ArrayDS(DS):
  def __init__(self, model):
    super().__init__(model)
