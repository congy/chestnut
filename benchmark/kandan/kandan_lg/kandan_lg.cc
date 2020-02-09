#include "kandan_lg.h"
TreeIndex<oid_t, size_t, 10000000> idptr_ds_5;
BasicArray<Activity5, 10000000> activity_5;
TreeIndex<ds_10_key_type, ItemPointer, 10000000> ds_10;
TreeIndex<ds_17_key_type, ItemPointer, 10000000> ds_17;
TreeIndex<ds_25_key_type, ItemPointer, 10000000> ds_25;
SortedArray<ds_31_key_type, Attachment31, 40000> ds_31;
SortedArray<ds_40_key_type, Channel40, 500> ds_40;
SortedArray<ds_56_key_type, Channel56, 500> ds_56;
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
  for (size_t i=0; i<10000000; i++)
  init_ds_5_from_sql(conn, i);
  printf("finish initialize ds 5\n");
  init_ds_31_from_sql(conn);
  printf("finish initialize ds 31\n");
  init_ds_40_from_sql(conn);
  printf("finish initialize ds 40\n");
  init_ds_56_from_sql(conn);
  printf("finish initialize ds 56\n");
  for (size_t i=0; i<10000000; i++)
  init_ds_10_from_sql(conn, i);
  printf("finish initialize ds 10\n");
  for (size_t i=0; i<10000000; i++)
  init_ds_17_from_sql(conn, i);
  printf("finish initialize ds 17\n");
  for (size_t i=0; i<10000000; i++)
  init_ds_25_from_sql(conn, i);
  printf("finish initialize ds 25\n");
  oid_t obj_pos = 0;
  cnt = 0;
  BASICARRAY_FOR_BEGIN(activity_5_1, activity_5, obj_activity_1)
    init_ds_7_from_sql(conn, &obj_activity_1);

  BASICARRAY_FOR_END
    printf("finish initialize ds's object 5\n");

  cnt = 0;
  SORTEDARRAY_RANGE_FOR_BEGIN(ds_40_2, nullptr, nullptr, ds_40, obj_channel_2)
    init_ds_48_from_sql(conn, &obj_channel_2);

  SORTEDARRAY_RANGE_FOR_END
    printf("finish initialize ds's object 40\n");


  print_time_diff(msg);
  printf("ds 5 sz = %d;\n", activity_5.size());
  printf("ds 10 sz = %d;\n", ds_10.size());
  printf("ds 17 sz = %d;\n", ds_17.size());
  printf("ds 25 sz = %d;\n", ds_25.size());
  printf("ds 31 sz = %d;\n", ds_31.size());
  printf("ds 40 sz = %d;\n", ds_40.size());
  printf("ds 56 sz = %d;\n", ds_56.size());
  std::this_thread::sleep_for(std::chrono::seconds(1));
}
