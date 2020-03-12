#include "kandan_small.h"
TreeIndex<oid_t, size_t, 100> idptr_ds_1;
SmallBasicArray<User1, 100> user_1;
SortedArray<ds_2_key_type, User2, 100> ds_2;
TreeIndex<ds_3_key_type, ItemPointer, 100> ds_3;
void read_data() {
  char msg[] = "data structure loading time ";
  get_time_start();

  MYSQL *conn = mysql_init(NULL);
  if (conn == NULL){
    fprintf(stderr, "mysql_init() failed\n");
    exit(1);
  }
  if (mysql_real_connect(conn, "localhost", "root", "", "kandan_small", 0, "/home/congy/mysqld/mysqld.sock", 0) == NULL){

    fprintf(stderr, "mysql connect failed\n");
    exit(1);
  }
  size_t cnt;
  init_ds_1_from_sql(conn);
  printf("finish initialize ds 1\n");
  init_ds_2_from_sql(conn);
  printf("finish initialize ds 2\n");
  init_ds_3_from_sql(conn);
  printf("finish initialize ds 3\n");
  oid_t obj_pos = 0;

  print_time_diff(msg);
  printf("ds 1 sz = %d;\n", user_1.size());
  printf("ds 2 sz = %d;\n", ds_2.size());
  printf("ds 3 sz = %d;\n", ds_3.size());
  std::this_thread::sleep_for(std::chrono::seconds(1));
}
