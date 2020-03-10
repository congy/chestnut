#include "kandan_lg.h"
SmallBasicArray<User1, 200000> user_1;
SmallBasicArray<Channel4, 500> channel_4;
BasicArray<Activity7, 10000000> activity_7;
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
  for (size_t i=0; i<200000; i++)
  init_ds_1_from_sql(conn, i);
  printf("finish initialize ds 1\n");
  init_ds_4_from_sql(conn);
  printf("finish initialize ds 4\n");
  for (size_t i=0; i<10000000; i++)
  init_ds_7_from_sql(conn, i);
  printf("finish initialize ds 7\n");
  oid_t obj_pos = 0;
  cnt = 0;
  SMALLBASICARRAY_FOR_BEGIN(channel_4_1, channel_4, obj_channel_1)
    init_ds_5_from_sql(conn, &obj_channel_1);

  SMALLBASICARRAY_FOR_END
    printf("finish initialize ds's object 4\n");


  print_time_diff(msg);
  printf("ds 1 sz = %d;\n", user_1.size());
  printf("ds 4 sz = %d;\n", channel_4.size());
  printf("ds 7 sz = %d;\n", activity_7.size());
  std::this_thread::sleep_for(std::chrono::seconds(1));
}
