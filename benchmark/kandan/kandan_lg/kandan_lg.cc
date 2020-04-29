#include "kandan_lg.h"
SortedArray<ds_6_key_type, Activity6, 20> ds_6;
void read_data() {
  char msg[] = "data structure loading time ";
  get_time_start();

  MYSQL *conn = mysql_init(NULL);
  if (conn == NULL){
    fprintf(stderr, "mysql_init() failed\n");
    exit(1);
  }
  if (mysql_real_connect(conn, "localhost", "root", "", "kandan_lg", 0, "/home/congy/mysqld/mysqld.sock", 0) == NULL){

    fprintf(stderr, "mysql connect failed\n");
    exit(1);
  }
  size_t cnt;
  init_ds_6_from_sql(conn);
  printf("finish initialize ds 6\n");
  oid_t obj_pos = 0;

  print_time_diff(msg);
  printf("ds 6 sz = %d;\n", ds_6.size());
  std::this_thread::sleep_for(std::chrono::seconds(1));
}
