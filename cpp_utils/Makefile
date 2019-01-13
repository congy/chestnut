#!/bin/bash
CC=g++-5

.SUFFIXES: .o .cc .h

SRC_DIRS = ./
INCLUDE = -I. -I/usr/include/mysql
#INCLUDE = -I. -I/usr/local/mysql-5.7.24-macos10.14-x86_64/include/

CFLAGS += -Wall -g -std=c++11 $(INCLUDE) -flto -O3
LDFLAGS = -std=c++11 -flto `pkg-config --cflags --libs protobuf` -latomic -lzmq -lmysqlclient #-Wall -L. -O3 -g -mcx16 -Wno-invalid-offsetof -lpapi -latomic -pthread -L/usr/include/mysql 
LDFLAGS += $(CFLAGS)

CPPS = $(foreach dir, $(SRC_DIRS), $(wildcard $(dir)*.cc))
OBJS = $(CPPS:.cc=.o)
DEPS = $(CPPS:.cc=.d)

all: opt_server

opt_server : $(OBJS)
	$(CC) -o $@ $^ $(LDFLAGS)

-include $(OBJS:%.o=%.d)

%.d: %.cc
	$(CC) -MM -MT $*.o -MF $@ $(CFLAGS) $<

%.o: %.cc
	$(CC) -c $(CFLAGS) -o $@ $<

.PHONY: clean
clean:
	rm -f opt_server $(OBJS) $(DEPS)
