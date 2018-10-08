import os
from schema import *
from constants import *

def sys_cmd(cmd):
  print cmd
  os.system(cmd)

def get_mysql_file_dir():
  return '/home/congy/mysql/data/'

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
    field_name = '\t'.join(filter(lambda x: x != None, [None if f.name in temp_fields else f.name for f in t.get_fields()]))
    fp.write('id\t{}\n'.format(field_name))
    for i in range(1, actual_sz+1):
      field_values = filter(lambda x: x != None, [i] + [None if f.name in temp_fields else f.generate_value() for f in t.get_fields()])
      line = '\t'.join([str(f) for f in field_values])
      fp.write("{}\n".format(line))
    fp.close()

  for a in get_assoc_tables(associations):
    i = 1
    table_name = a.name
    fp = open("{}/{}.tsv".format(fpath, table_name), 'w')
    field_name = '\t'.join(['id', '{}_id'.format(a.lft.name), '{}_id'.format(a.rgt.name)])
    fp.write('{}\n'.format(field_name))
    for j in range(1, actual_sizes[a.lft]+1):
      repeat_list = []
      start = random.randint(1, actual_sizes[a.rgt]-1)
      for k in range(0, a.lft_ratio/2+1):
        rd = (start + k) % actual_sizes[a.rgt] + 1
        fields = [i, j, rd]
        fp.write("{}\n".format('\t'.join([str(f) for f in fields])))
        i += 1
      if j % 1000 == 0:
        print "finish {} lft".format(j)
    fp.close()

def populate_database(db_name, data_dir, tables, associations):
  remove_db(db_name)
  create_db(db_name)
  create_tables(db_name, tables, associations)
  sys_cmd("mkdir {}".format(data_dir))
  populate_tables(data_dir, get_mysql_file_dir(), db_name, tables, associations)

def remove_db(db_name):
  sys_cmd("mysql -u root -e \"DROP DATABASE {};\"".format(db_name))

def create_db(db_name):
  sys_cmd("mysql -u root -e \"CREATE DATABASE {}\"".format(db_name))

def create_tables(db_name, tables, associations):
  for t in tables:
    field_list=[]
    for f in t.get_fields():
      ft = f.name+" "
      assert(f.tipe in mysql_types)
      ft += "{} DEFAULT NULL".format(mysql_types[f.tipe])
      field_list.append(ft)
    sys_cmd("mysql -u root {} -e \"CREATE TABLE {} ({});\"".format(db_name, t.name, ", ".join(field_list)))
  
  for a in get_assoc_tables(associations):
    sys_cmd("mysql -u root {} -e \"CREATE TABLE {} (id INTEGER, {}_id INTEGER, {}_id INTEGER);\"".format(db_name, a.name, a.lft.name, a.rgt.name))

def populate_tables(file_dir, mysql_file_dir, db_name, tables, associations):
  for t in tables:

    fp = open("{}.txt".format(t.name), 'w')
    for i in range(1, t.sz+1):
      field_values = filter(lambda x: x != None, [i] + [None if f.name == 'id' else f.generate_value() for f in t.get_fields()])
      line = '|'.join([str(f) for f in field_values])
      fp.write("{}\n".format(line))
    
    fp.close()
    field_name = ', '.join([f.name for f in t.get_fields()])
    sys_cmd("sudo mv {}.txt {}/{}/".format(t.name, mysql_file_dir, db_name))
    sys_cmd("mysql -u root {} -e \"LOAD DATA INFILE '{}.txt' IGNORE INTO TABLE {} FIELDS TERMINATED BY '|' LINES TERMINATED BY '\\n' ({})\"".format(db_name, t.name, t.name, field_name))
    sys_cmd('mysql {} -e "select * from {}" -B > {}/{}.tsv'.format(db_name, t.name, file_dir, t.name)) 

    #create index
    #sys_cmd("mysql -u root {} -e \"CREATE INDEX index_{}_id ON {} (id) USING BTREE;\"".format(db_name, t.name, t.name))
    #for f in t.get_fields():
    #  sys_cmd("mysql -u root {} -e \"CREATE INDEX index_{}_{} ON {} ({}) USING BTREE;\"".format(db_name, t.name, f.name, t.name, f.name))

  for a in get_assoc_tables(associations):
    i = 1
    table_name = a.name
    fp = open("{}.txt".format(table_name), 'w')
    for j in range(1, a.lft.sz+1):
      repeat_list = []
      start = random.randint(1, a.rgt.sz-1)
      for k in range(0, a.lft_ratio):
        #rd = random.randint(1, a.rgt.sz)
        #while rd in repeat_list:
        #  rd = random.randint(1, a.rgt.sz)
        rd = (start + k) % a.rgt.sz + 1
        #repeat_list.append(rd)
        fields = [i, j, rd]
        fp.write("{}\n".format('|'.join([str(f) for f in fields])))
        i += 1
      if j % 1000 == 0:
        print "finish {} lft".format(j)
    fp.close()

    field_name = ', '.join(['id', '{}_id'.format(a.lft.name), '{}_id'.format(a.rgt.name)])
    sys_cmd("sudo mv {}.txt {}/{}/".format(table_name, mysql_file_dir, db_name))
    sys_cmd("mysql -u root {} -e \"LOAD DATA INFILE '{}.txt' IGNORE INTO TABLE {} FIELDS TERMINATED BY '|' LINES TERMINATED BY '\\n' ({})\"".format(db_name, table_name, table_name, field_name))
    sys_cmd('mysql {} -e "select * from {}" -B > {}/{}.tsv'.format(db_name, table_name, file_dir, table_name))

    #create index
    #sys_cmd('mysql -u root {} -e "CREATE INDEX index_{}_id ON {} (id) USING BTREE;"'.format(db_name, table_name, table_name))
    #sys_cmd('mysql -u root {} -e "CREATE INDEX index_{}_{}_id ON {} ({}_id) USING BTREE;"'.format(db_name, table_name, a.lft.name, table_name, a.lft.name))
    #sys_cmd('mysql -u root {} -e "CREATE INDEX index_{}_{}_id ON {} ({}_id) USING BTREE;"'.format(db_name, table_name, a.rgt.name, table_name, a.rgt.name))
