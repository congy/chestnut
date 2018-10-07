class RQManager(object):
  def __init__(self, query, plans=[]):
    self.query = query
    self.frequency = 1
    self.plans = plans # list of PlansForOneNesting

class WQManager(object):
  def __init__(self, query):
    self.query = query
    self.frequency = 1
    self.ds = [] # TODO