
import random
import string

def clean_lst(lst):
  return filter(lambda x: x is not None, lst)

def get_capitalized_name(name):
  return ''.join([s.capitalize() for s in name.split('_')])

def set_minus(a, b, eq_func=(lambda x,y: x==y)):
  r = []
  for ele in a:
    exist = any([eq_func(ele, ele1) for ele1 in b])
    if not exist:
      r.append(ele)
  return r

def set_intersect(a, b, eq_func=(lambda x,y: x==y)):
  r = []
  for ele in a:
    exist = False
    for ele1 in b:
      if eq_func(ele, ele1):
        exist = True
    if exist:
      r.append(ele)
  return r

def map_contain(a, key, eq_func=(lambda x,y: x==y)):
  for k,v in a.items():
    if k == key:
      return v
  return None


def set_equal(a, b, eq_func=(lambda x,y: x==y)):
  if len(a) != len(b):
    return False
  for ele in a:
    exist = False
    for ele1 in b:
      if eq_func(ele, ele1):
        exist = True
    if not exist:
      return False
  return True

def list_equal(a, b, eq_func=(lambda x,y: x==y)):
  return len(a) == len(b) and all([eq_func(a[i],b[i]) for i in range(0, len(a))])
def map_equal(a, b, value_func=(lambda x,y: x==y)):
  return len(a) == len(b) and all([k in b and value_func(v, b[k]) for k,v in a.items()])

def set_no_duplicate(a, eq_func=(lambda x,y: x==y)):
  for i,ele in enumerate(a):
    for j,ele in enumerate(a):
      if i != j and eq_func(i, j):
        return False
  return True
      
def set_union(a, b, eq_func=(lambda x,y: x==y)):
  for ele in b:
    if not any([eq_func(x,ele) for x in a]): 
      a.append(ele)
  return a

def map_union(a, b, merge_func=(lambda x,y: x)):
  r = {}
  for k,v in a.items():
    r[k] = v
  for k,v in b.items():
    if k not in a:
      r[k] = v
    else:
      r[k] = merge_func(a[k], v)
  return r

def map_intersect(a, b, intersect_func=(lambda x,y: x)):
  r = {}
  for k,v in b.items():
    if k in a:
      r[k] = intersect_func(a[k], v)
  return r
  
def set_include(a, b, eq_func=(lambda x,y: x==y)): #a include b
  for ele in b:
    exist = False
    for ele1 in a:
      if eq_func(ele, ele1):
        exist = True
    if not exist:
      return False
  return True

def set_conjunct(a, b, eq_func):
  r = []
  for ele in a:
    for ele1 in b:
      if eq_func(ele, ele1):
        r.append(ele)
        break
  return r

def list_map_union(list_map):
  r = {}
  for m in list_map:
    r = map_union(r, m)
  return r

def list_union(lsts):
  r = []
  for l in lsts:
    r = r + l
  return r

def add_to_list_map(k, v, mp):
  for k1,v1 in mp.items():
    if k1==k:
      v1.append(v)
      return
  mp[k] = [v]

def list_combine(lsts):
  r = [s for s in lsts[0]]
  for l in lsts[1:]:
    r = r + l
  return r

def insert_no_duplicate(lst, ele, eq_func=(lambda x,y:x==y)):
  if not any([eq_func(x,ele) for x in lst]):
    lst.append(ele)

def insert_indent(s, indent_level=1):
  indent = ''.join(['  ' for i in range(0, indent_level)])
  return ('\n'.join([indent+l if len(l) > 0 else l for l in s.split('\n')])+'\n')

def get_random_string(length):
	chars = "".join( [random.choice(string.letters) for i in xrange(length)] )
	return chars

def get_random_length(minl,maxl):
  return random.randint(minl, maxl)