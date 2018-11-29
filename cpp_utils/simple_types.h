#pragma once
#ifndef __TYPES_H_
#define __TYPES_H_
#include <climits>
#include <cstdint>
#include <functional>
#include <limits>
#include <memory>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <vector>

#define INVALID_TYPE_ID 0

typedef uint32_t oid_t;
typedef size_t hash_t;
typedef uint32_t length_t;
typedef uint32_t count_t;
typedef uint32_t date_t;

enum class ScanDirectionType {
  INVALID = INVALID_TYPE_ID,  // invalid scan direction
  FORWARD = 1,                // forward
  BACKWARD = 2                // backward
};


static const oid_t INVALID_OID = 0;

#define ALIGNED __attribute__((__aligned__(8)))
#define PACKED  __attribute__((__packed__))
#endif