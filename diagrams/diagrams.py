#!/usr/bin/env python
# cluster.py - http://www.graphviz.org/content/cluster
import os

from graphviz import Digraph

from model import *




SCHEMA_JSON = {0: {'keys': [{'path': [], 'key': 'id'}], 'value': {'type': 'ptr', 'target': 0}, 'table': 'user', 'type': 'Index', 'id': 0, 'condition': 'id < param[uid]'}, 1: {'table': 'user', 'type': 'BasicArray', 'id': 0, 'value': {'fields': ['id', 'email', 'encrypted_password', 'reset_password_token', 'reset_password_sent_at', 'remember_created_at', 'first_name', 'last_name', 'signin_count', 'current_sign_in_at', 'current_sign_in_ip', 'last_sign_in_at', 'last_sign_in_ip', 'auth_token', 'locale', 'gravatar_hash', 'username', 'regstatus', 'active', 'is_admin', 'avatar_url', 'created_at', 'updated_at'], 'nested': []}}}

TSV_DIR = '../benchmark/kandan/data/kandan_diag/'





def load_data(path):
  data = {}
  # Read each row into data[name].
  for tsv_name in os.listdir(path):
    name = tsv_name[:-4]
    data[name] = []
    with open(path + tsv_name, 'r') as tsv_open:
      for line in tsv_open:
        data[name].append(line.strip().split('|'))
  # Use first row as header, represented as tuple.
  for k in data:
    data[k] = (data[k][0], data[k][1:])
  return data

def get_chestnut_model(model):
  return ChestnutModel(model)

def render(model, data):
  

  return

  g = Digraph('G', filename='cluster.gv', format='svg')

  # NOTE: the subgraph name needs to begin with 'cluster' (all lowercase)
  #       so that Graphviz recognizes it as a special cluster subgraph

  g.node("tab", label='''<<table>
    <tr>
      <td port="left">left</td>
      <td port="right">right</td>
    </tr>
  </table>>''')

  g.node("b", 'big boy')

  g.edge("tab:left", "b")
  g.edge("tab:right", "b")

  g.view()



if '__main__' == __name__:
  data = load_data(TSV_DIR)
  print(data)
  model = get_chestnut_model(SCHEMA_JSON)
  print(model)
  exit(0)
