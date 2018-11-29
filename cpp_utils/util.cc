#include "util.h"
//std::random_device rd;  
//std::mt19937* genptr; 
//std::uniform_int_distribution<unsigned int>* dis;

string null_str = string("NULL");


struct timeval time_start;
struct timeval time_end;

void print_time_diff(char* msg){
    gettimeofday(&time_end, NULL);
    long seconds  = time_end.tv_sec  - time_start.tv_sec;
    long useconds = time_end.tv_usec - time_start.tv_usec;
    std::cout << msg <<": " <<((float)(seconds) * 1000.0 + (float)useconds/1000.0)<<" milisec"<<endl;
}

void get_time_start() {
  gettimeofday(&time_start, NULL);
}

//void init_random_gen() {
//  genptr = new std::mt19937(rd());
//  dis = new std::uniform_int_distribution<unsigned int>(1, 2147483600);
//}



