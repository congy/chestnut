import os
from schema import *
from constants import *

def sys_cmd(cmd):
  print cmd
  os.system(cmd)


def generate_db_data_files(data_dir, tables, associations):
  fpath = data_dir
  if not os.path.exists(fpath):
    os.system('mkdir {}'.format(fpath))

  actual_sizes = {}
  for t in tables:
    fp = open("{}/{}.tsv".format(fpath, t.name), 'w')
    actual_sz = int(t.sz - 20) if t.sz > 100 else t.sz - 2
    actual_sizes[t] = actual_sz
    temp_fields = ['id']
    for assoc in t.get_assocs():
      if assoc.rgt == t and assoc.lft.is_temp:
        temp_fields.append('{}_id'.format(assoc.rgt_field_name))
    print '{} remove fields: {}'.format(t.name, ','.join([str(f) for f in temp_fields]))
    field_name = '|'.join(filter(lambda x: x != None, [None if f.name in temp_fields else f.name for f in t.get_fields()]))
    fp.write('id|{}\n'.format(field_name))
    for i in range(1, actual_sz+1):
      field_values = filter(lambda x: x != None, [i] + [None if f.name in temp_fields else f.generate_value() for f in t.get_fields()])
      line = '|'.join([str(f) for f in field_values])
      fp.write("{}\n".format(line))
    fp.close()

  for a in get_assoc_tables(associations):
    i = 1
    table_name = a.name
    fp = open("{}/{}.tsv".format(fpath, table_name), 'w')
    field_name = '|'.join(['id', '{}_id'.format(a.lft.name), '{}_id'.format(a.rgt.name)])
    fp.write('{}\n'.format(field_name))
    for j in range(1, actual_sizes[a.lft]+1):
      repeat_list = []
      start = random.randint(1, actual_sizes[a.rgt]-1)
      for k in range(0, a.lft_ratio/2+1):
        rd = (start + k) % actual_sizes[a.rgt] + 1
        fields = [i, j, rd]
        fp.write("{}\n".format('|'.join([str(f) for f in fields])))
        i += 1
      if j % 1000 == 0:
        print "finish {} lft".format(j)
    fp.close()

def populate_database(data_dir, tables, associations):
  remove_db()
  create_db()
  create_tables(tables, associations)
  populate_tables(data_dir, tables, associations)

def remove_db():
  db_name = get_db_name()
  sys_cmd("mysql -u root -e \"DROP DATABASE {};\"".format(db_name))

def create_db():
  db_name = get_db_name()
  sys_cmd("mysql -u root -e \"CREATE DATABASE {}\"".format(db_name))

def create_tables(tables, associations):
  db_name = get_db_name()
  for t in tables:
    field_list=[]
    for f in t.get_fields():
      ft = f.name+" "
      sql_type = get_sql_type(f.tipe)
      ft += "{} DEFAULT NULL".format(sql_type)
      field_list.append(ft)
    sys_cmd("mysql -u root {} -e \"CREATE TABLE {} ({});\"".format(db_name, t.name, ", ".join(field_list)))
  
  for a in get_assoc_tables(associations):
    sys_cmd("mysql -u root {} -e \"CREATE TABLE {} (id INTEGER, {}_id INTEGER, {}_id INTEGER);\"".format(db_name, a.name, a.lft.name, a.rgt.name))

def populate_tables(data_dir, tables, associations):
  db_name = get_db_name()
  fpath = "{}/".format(data_dir)
  for t in tables:
    fname = "{}/{}.tsv".format(fpath, t.name)
    temp_fields = ['id']
    for assoc in t.get_assocs():
      if assoc.rgt == t and assoc.lft.is_temp:
        temp_fields.append('{}_id'.format(assoc.rgt_field_name))
    field_names = ','.join(filter(lambda x: x != None, [None if f.name in temp_fields else f.name for f in t.get_fields()]))
    field_names = 'id,{}'.format(field_names)
    sys_cmd("mysql -u root --local-infile {} -e \"LOAD DATA LOCAL INFILE '{}' INTO TABLE {} FIELDS TERMINATED BY '|' LINES TERMINATED BY '\\n' IGNORE 1 LINES  ({})\"".format(db_name, fname, t.name, field_names))
    #sys_cmd('mysql {} -e "select * from {}" -B > {}/{}.tsv'.format(db_name, t.name, file_dir, t.name)) 

    #create index
    sys_cmd("mysql -u root {} -e \"CREATE INDEX index_{}_id ON {} (id) USING BTREE;\"".format(db_name, t.name, t.name))
    
  for a in get_assoc_tables(associations):
    fname = "{}/{}.tsv".format(fpath, a.name)
    field_names = ','.join(['id', '{}_id'.format(a.lft.name), '{}_id'.format(a.rgt.name)])
    sys_cmd("mysql -u root --local-infile {} -e \"LOAD DATA LOCAL INFILE '{}' INTO TABLE {} FIELDS TERMINATED BY '|' LINES TERMINATED BY '\\n' IGNORE 1 LINES ({})\"".format(db_name, fname, a.name, field_names))
    #sys_cmd('mysql {} -e "select * from {}" -B > {}/{}.tsv'.format(db_name, table_name, file_dir, a.name))

    #create index
    #sys_cmd('mysql -u root {} -e "CREATE INDEX index_{}_id ON {} (id) USING BTREE;"'.format(db_name, table_name, table_name))
    sys_cmd('mysql -u root {} -e "CREATE INDEX index_{}_{}_id ON {} ({}_id) USING BTREE;"'.format(db_name, a.name, a.lft.name, a.name, a.lft.name))
    sys_cmd('mysql -u root {} -e "CREATE INDEX index_{}_{}_id ON {} ({}_id) USING BTREE;"'.format(db_name, a.name, a.rgt.name, a.name, a.rgt.name))
