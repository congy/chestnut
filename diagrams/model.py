from functional import seq

class ChestnutModel:

  def __init__(self, model):
    self.items = seq(model.values()) \
      .map(get_ds) \
      .to_list()



def get_ds(model):
  typ = model['type']
  if 'Index' == typ:
    return IndexDS(model)
  if 'BasicArray' == typ:
    return ArrayDS(model)
  raise Exception(f"Unknown type: '{typ}'.")

class DS():
  def __init__(self, model):
    self.type = model['type']
    self.table = model['table']
    self.value = model['value']

    self.nested = []

    if 'nested' in self.value:
      self.nested = seq(self.value['nested']) \
        .map(get_ds) \
        .to_list()


class IndexDS(DS):
  def __init__(self, model):
    super().__init__(model)

class ArrayDS(DS):
  def __init__(self, model):
    super().__init__(model)
