import os
from schema import *
from constants import *
#import mysql.connector

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
    pk_fields = [(xx,set()) for xx in t.primary_keys]
    for i in range(1, actual_sz+1):
      loop_cnt = 0
      while True:
        field_values_map_ = filter(lambda x: x != None, [(t.get_field_by_name('id'),i)] + [None if f.name in temp_fields else (f,f.generate_value()) for f in t.get_fields()])
        field_values_map = {xx[0].name:xx[1] for xx in field_values_map_}
        field_names = [xx[0].name for xx in field_values_map_]
        field_values = [field_values_map[xx] for xx in field_names]
        if len(pk_fields) > 0:
          exists = False
          for kk,vv in pk_fields:
            pk_value = '|'.join([str(field_values_map[kkx.field_name]) for kkx in kk])
            if pk_value in vv:
              exists = True
            else:
              vv.add(pk_value)
          if exists==False or loop_cnt > 10:
            break
          loop_cnt += 1
        else:
          break
      #field_values = filter(lambda x: x != None, [i] + [None if f.name in temp_fields else f.generate_value() for f in t.get_fields()])
      line = '|'.join([str(f) for f in field_values])
      if loop_cnt <= 10:
        fp.write("{}\n".format(line))
    fp.close()

  for a in get_assoc_tables(associations):
    i = 1
    table_name = a.name
    fp = open("{}/{}.tsv".format(fpath, table_name), 'w')
    field_name = '|'.join(['id', a.assoc_f1, a.assoc_f2])
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

def populate_database(data_dir, tables, associations, recreate=False):
  #remove_db(recreate)
  #create_db(recreate)
  create_tables(tables, associations, recreate)
  populate_tables(data_dir, tables, associations, recreate)

def create_psql_tables_script(data_dir, tables, associations, indexes={}):
  s = ''
  for t in tables:
    temp_fields = ['id']
    for assoc in t.get_assocs():
      if assoc.rgt == t and assoc.lft.is_temp:
        temp_fields.append('{}_id'.format(assoc.rgt_field_name))
    fields = filter(lambda x: x != None, [None if f.name in temp_fields or f.is_temp else f for f in t.get_fields()])
    fields.insert(0, t.get_field_by_name('id'))
    table_name = to_plural(t.name)
    s += 'DROP TABLE {};\n'.format(table_name)
    s += 'CREATE TABLE {} (\n'.format(table_name)
    s += ',\n'.join(['  {} {}'.format(f.name, get_psql_type(f.tipe)) for f in fields])
    s += ');\n'
    s += "COPY {} FROM '{}/{}.tsv' DELIMITER '|' CSV HEADER;\n\n".format(table_name, data_dir, t.name)
    s += "ALTER TABLE {} ADD PRIMARY KEY (id);\n".format(table_name)

  for a in get_assoc_tables(associations):
    field_names = ['id', a.assoc_f1, a.assoc_f2]
    table_name = a.name
    s += 'DROP TABLE {};\n'.format(table_name)
    s += 'CREATE TABLE {} (\n'.format(table_name)
    s += ',\n'.join([' {} INTEGER NOT NULL'.format(f) for f in field_names])
    s += ');\n'
    s += "COPY {} FROM '{}/{}.tsv' DELIMITER '|' CSV HEADER;\n\n".format(table_name, data_dir, a.name)

  for k,v in indexes.items():
    for idx_fields in v:
      table_name = to_plural(k.name) if isinstance(k, Table) else k.name
      index_name = 'idx_on_{}_{}'.format(table_name, '_'.join(idx_fields))
      s += 'CREATE INDEX {} ON {} ({});\n'.format(index_name, table_name, ','.join(idx_fields))
  return s

def remove_db(recreate):
  if recreate == False:
    return
  db_name = get_db_name()
  sys_cmd("mysql -u root -e \"DROP DATABASE {};\"".format(db_name))

def create_db(recreate):
  if recreate == False:
    return
  db_name = get_db_name()
  sys_cmd("mysql -u root -e \"CREATE DATABASE {}\"".format(db_name))

def create_tables(tables, associations, recreate):
  db_name = get_db_name()
  for t in tables:
    field_list=[]
    for f in t.get_fields():
      ft = f.name+" "
      sql_type = get_sql_type(f.tipe)
      ft += "{} DEFAULT NULL".format(sql_type)
      field_list.append(ft)
    if t.is_temp or recreate:
      sys_cmd("mysql -u root {} -e \"DROP TABLE IF EXISTS {};\"".format(db_name, get_db_table_name(t.name)))
      sys_cmd("mysql -u root {} -e \"CREATE TABLE {} ({});\"".format(db_name, get_db_table_name(t.name), ", ".join(field_list)))
    if recreate == False:
      temp_fields = []
      for assoc in t.get_assocs():
        if assoc.rgt == t and assoc.lft.is_temp:
          f = '{}_id'.format(assoc.rgt_field_name)
          sys_cmd("mysql -u root {} -e \"ALTER TABLE {} ADD COLUMN {} int(11) DEFAULT 0\"".format(db_name, to_plural(t.name), f))
  
  if recreate:
    for a in get_assoc_tables(associations):
      sys_cmd("mysql -u root {} -e \"CREATE TABLE {} (id INTEGER, {} INTEGER, {} INTEGER);\"".format(db_name, a.name, a.assoc_f1, a.assoc_f2))

def populate_tables(data_dir, tables, associations, recreate_db=False):
  db_name = get_db_name()
  fpath = "{}/".format(data_dir)
  for t in tables:
    fname = "{}/{}.tsv".format(fpath, t.name)
    temp_fields = ['id']
    for assoc in t.get_assocs():
      if assoc.rgt == t and assoc.lft.is_temp:
        temp_fields.append('{}_id'.format(assoc.rgt_field_name))
    field_names = filter(lambda x: x != None, [None if f.name in temp_fields or f.is_temp else f.name for f in t.get_fields()])
    field_names = 'id,{}'.format(','.join(field_names))
    sys_cmd("mysql -u root {} -e \"delete from {}\"".format(db_name, to_plural(t.name)))
    sys_cmd("mysql -u root --local-infile {} -e \"LOAD DATA LOCAL INFILE '{}' INTO TABLE {} FIELDS TERMINATED BY '|' LINES TERMINATED BY '\\n' IGNORE 1 LINES  ({})\"".format(db_name, fname, to_plural(t.name), field_names))
    #sys_cmd('mysql {} -e "select * from {}" -B > {}/{}.tsv'.format(db_name, t.name, file_dir, t.name)) 

    #create index
    if recreate_db:
      for idf in temp_fields[1:]:
        sys_cmd("mysql -u root {} -e \"CREATE INDEX index_{}_{} ON {} ({}) USING BTREE;\"".format(db_name, t.name, idf, to_plural(t.name), idf))
      sys_cmd("mysql -u root {} -e \"CREATE INDEX index_{}_id ON {} (id) USING BTREE;\"".format(db_name, t.name, to_plural(t.name)))
    
  for a in get_assoc_tables(associations):
    fname = "{}/{}.tsv".format(fpath, a.name)
    field_names = ','.join(['id', a.assoc_f1, a.assoc_f2])
    sys_cmd("mysql -u root {} -e \"delete from {}\"".format(db_name, a.name))
    sys_cmd("mysql -u root --local-infile {} -e \"LOAD DATA LOCAL INFILE '{}' INTO TABLE {} FIELDS TERMINATED BY '|' LINES TERMINATED BY '\\n' IGNORE 1 LINES ({})\"".format(db_name, fname, a.name, field_names))
    #sys_cmd('mysql {} -e "select * from {}" -B > {}/{}.tsv'.format(db_name, table_name, file_dir, a.name))

    #create index
    #sys_cmd('mysql -u root {} -e "CREATE INDEX index_{}_id ON {} (id) USING BTREE;"'.format(db_name, table_name, table_name))
    if recreate_db:
      sys_cmd('mysql -u root {} -e "CREATE INDEX index_{}_{}_id ON {} ({}) USING BTREE;"'.format(db_name, a.name, a.lft.name, a.name, a.assoc_f1))
      sys_cmd('mysql -u root {} -e "CREATE INDEX index_{}_{}_id ON {} ({}) USING BTREE;"'.format(db_name, a.name, a.rgt.name, a.name, a.assoc_f2))


def test_schema(tables, associations):
  mysql_tables = []
  mysql_fields = {}
  mydb = mysql.connector.connect(host="localhost", user="root", passwd="", database=get_db_name())
  mycursor = mydb.cursor()
  mycursor.execute('show tables')
  myresult = mycursor.fetchall()
  for t in myresult:
    mysql_tables.append(str(t[0]))
    mycursor.execute('describe {}'.format(t[0]))
    fields = mycursor.fetchall()
    mysql_fields[t[0]] = [str(f[0]) for f in fields]

  for t in tables:
    if t.is_temp:
      continue
    db_table_name = get_db_table_name(t.name)
    if db_table_name not in mysql_tables:
      print 'table {} not in mysql tables!'.format(db_table_name)
      continue
    temp_fields = ['id']
    for assoc in t.get_assocs():
      if assoc.rgt == t and assoc.lft.is_temp:
        temp_fields.append('{}_id'.format(assoc.rgt_field_name))
    field_names = filter(lambda x: x != None, [None if f.name in temp_fields or f.is_temp else f.name for f in t.get_fields()])
    field_names.append('id')
    for f in field_names:
      if f not in mysql_fields[db_table_name]:
        print '  field {} not in mysql fields of table {}!'.format(f, db_table_name)

  for a in get_assoc_tables(associations):
    field_names = ['id', a.assoc_f1, a.assoc_f2]
    db_table_name = a.name
    if db_table_name not in mysql_tables:
      print 'table {} not in mysql tables!'.format(db_table_name)
      continue
    for f in field_names:
      if f not in mysql_fields[db_table_name]:
        print '  field {} not in mysql fields of table {}!'.format(f, db_table_name)
  
