#ifndef __UTILS_H_
#define __UTILS_H_
#include <string.h>
#include <stdlib.h>
#include <iostream>
#include <random>
#include <sys/time.h>
using namespace std;
extern struct timeval time_start;
extern struct timeval time_end;
//extern std::random_device rd;  
//extern std::mt19937* genptr; 
//extern std::uniform_int_distribution<unsigned int>* dis;

extern string null_str;

inline uint32_t str_to_uint(const string& s){
    if (s.compare(null_str) == 0){
        return 0;
    }else{
        return (uint32_t)atoi(s.c_str());
    }
}

inline uint32_t str_to_uint(const char* s){
    if (s) {
      return (uint32_t)atoi(s);
    }else{
      return 0;
    }
}
inline uint32_t char_to_uint(const char* s) {
  if (s == nullptr || strlen(s) == 0) return 0;
  else return (uint32_t)atoi(s);
}

inline int str_to_int(const string& s){
    if (s.compare(null_str) == 0){
        return 0;
    }else{
        return atoi(s.c_str());
    }
}
inline uint32_t str_to_int(const char* s){
    if (s) {
      return (uint32_t)atoi(s);
    }else{
      return 0;
    }
}

inline uint32_t time_to_uint(const string& s){
    if (s.compare(null_str) == 0) return 1;
    return time_to_uint(s.c_str());
}

inline uint32_t time_to_uint(const char* s1){
    if (s1) {
      std::string s(s1);
      int year = str_to_int(s.substr(0, 4));
      int month = str_to_int(s.substr(5, 2));
      int day = str_to_int(s.substr(8, 2));
      int lap_day = (year-2010)*365 + month*30 + day;
      if (s.length() > 10) {
        int hour = str_to_int(s.substr(11, 2));
        int minute = str_to_int(s.substr(14, 2));
        int second = str_to_int(s.substr(17, 2));
        //return (uint32_t)(second + minute*60 + hour*3600 + lap_day*86400);
        return (uint32_t)(minute + hour*60 + lap_day*1440);
      } else {
        return (uint32_t)(lap_day*1440);
      }
    } else {
      return 1;
    }
}

inline float str_to_float(const string& s){
    if (s.compare(null_str) == 0){
        return 0;
    }else{
        return atof(s.c_str());
    }
}

void print_time_diff(char* msg);
void get_time_start();

//void init_random_gen();

//inline unsigned int random_uint() {
//  return (*dis)(*genptr);
//}
#endif
