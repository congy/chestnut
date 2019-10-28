#!/usr/bin/env python
# cluster.py - http://www.graphviz.org/content/cluster

from graphviz import Digraph

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