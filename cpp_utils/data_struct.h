#pragma once

#ifndef _DATA_STRUCTURE_H_
#define _DATA_STRUCTURE_H_

#include <cstdint>
#include <vector>
#include <map>
#include <unordered_map>
#include <iostream>
#include <cstring>
#include <stx/btree_map.h>
#include <stx/btree_multimap.h>
#include <string>
typedef uint32_t oid_t;
#define INVALID_POS UINT32_MAX
#define INVALID_TYPE_ID 0
typedef uint32_t oid_t;
typedef size_t hash_t;
typedef uint32_t length_t;
typedef uint32_t count_t;
typedef uint32_t date_t;
static const oid_t INVALID_OID = 0;

#define ALIGNED __attribute__((__aligned__(8)))
#define PACKED  __attribute__((__packed__))

#define BLOCK_SZ 262144
//#define BLOCK_SZ 256
#define BWTREE_INDEX_TYPE BWTreeIndex <KeyType, \
                                       ValueType, \
                                       ObjectType, \
                                       KeyComparator, \
                                       KeyEqualityChecker, \
                                       KeyHashFunc, \
                                       ValueEqualityChecker, \
                                       ValueHashFunc>

#define BWTREE_INDEX_TEMPLATE_ARGUMENTS template <typename KeyType, \
                                                  typename ValueType, \
                                                  typename ObjectType, \
                                                  typename KeyComparator, \
                                                  typename KeyEqualityChecker, \
                                                  typename KeyHashFunc, \
                                                  typename ValueEqualityChecker, \
                                                  typename ValueHashFunc>


struct KeyId{
  oid_t id;
  KeyId() : id (0) {}
  KeyId(oid_t id_) : id(id_) {}
  inline bool operator < (const KeyId& other) const {
    return id < other.id;
  }
  inline bool operator == (const KeyId& other) const {
    return id == other.id;
  }
  inline size_t get_hash() const {
    return id;
  }
};                                                  
struct ItemPointer{
  size_t pos;
  ItemPointer () : pos (0) {}
  ItemPointer (size_t pos_) : pos(pos_) {}
  ItemPointer (const ItemPointer& other) : pos(other.pos) {}
  inline void clear() { pos = 0; }
  inline size_t get_hash () const {return pos;}
  inline bool operator<(const ItemPointer& other) const {return pos < other.pos;}
  inline bool operator==(const ItemPointer& other) const {return pos == other.pos;}
  inline bool is_valid() const { return pos != INVALID_POS; }
  //ItemPointer (const ItemPointer& other) : pos (other.pos) {}
};
inline bool invalid_pos(size_t pos){
  return pos == INVALID_POS;
}
inline bool invalid_id(size_t id){
  return id == 0;
}

template<size_t LENGTH>
class VarChar {
public:
  char s[LENGTH];
  VarChar() {memset(s, 0, LENGTH);}
  VarChar(const VarChar& x) {memcpy(s, x.s, LENGTH);}
  VarChar(const char* x) {memset(s, 0, LENGTH); if (x != nullptr) {memset(s, 0, LENGTH); memcpy(s, x, LENGTH);}}
  VarChar(int x) {memset(s, 0, LENGTH);}
  VarChar(const std::string& x) {memset(s, 0, LENGTH); memcpy(s, x.c_str(), LENGTH > x.size()? x.size(): LENGTH);}
  inline size_t get_hash() const { size_t x = 0; for (size_t i=0; i<LENGTH-1; i++) x += ((i+1)*size_t(s[i])); return x; }
  inline const char* c_str() const { return s; }
  inline bool operator<(const VarChar& other) const {return strcmp(s, other.s) < 0;}
  inline bool operator<=(const VarChar& other) const {return strcmp(s, other.s) <= 0;}
  inline bool operator>(const VarChar& other) const {return strcmp(s, other.s) > 0;}
  inline bool operator>=(const VarChar& other) const {return strcmp(s, other.s) >= 0;}
  inline bool operator==(const VarChar& other) const {return strcmp(s, other.s) == 0;}
  inline bool operator!=(const VarChar& other) const {return strcmp(s, other.s) != 0;}
};

class LongString {
public:
  std::string s;
  LongString() {}
  LongString(const LongString& x) {s = x.s;}
  LongString(const std::string& x) {s = x;}
  LongString(const char* x) {if (x != nullptr) s = x;}
  LongString(int x) {}
  inline size_t get_hash() const { return std::hash<std::string>{}(s); }
  inline const char* c_str() const { return s.c_str(); }
  inline size_t find(const char* subs) { return s.find(subs); }
  inline size_t find(const LongString& subs) { return s.find(subs.s); }
  inline bool operator<(const LongString& other) const {return s.compare(other.s) < 0;}
  inline bool operator==(const LongString& other) const {return s.compare(other.s) == 0;}
  inline bool operator!=(const LongString& other) const {return s.compare(other.s) != 0;}
};

template<size_t LENGTH>
inline bool operator==(const std::string& a, const VarChar<LENGTH>& b) {
  return a.compare(b.s) == 0;
}

inline bool operator==(const std::string& a, const LongString& b) {
  return a.compare(b.s) == 0;
}

template<typename ValueType>
class MyIterator : public std::iterator<std::input_iterator_tag, ValueType>
{
public:
  ValueType* p;
  MyIterator(ValueType* x) :p(x) {}
  MyIterator(const MyIterator& mit) : p(mit.p) {}
  MyIterator& operator++() {++p; return *this;}
  MyIterator operator++(int) {MyIterator tmp(*this); operator++(); return tmp;}
  bool operator==(const MyIterator& rhs) const {return p==rhs.p;}
  bool operator!=(const MyIterator& rhs) const {return p!=rhs.p;}
  ValueType& operator*() {return *p;}
};


template<typename ValueType>
class TempArray {
public:
  std::vector<ValueType> vec;
  inline typename std::vector<ValueType>::iterator begin(){
    return vec.begin();
  }
  inline typename std::vector<ValueType>::iterator end(){
    return vec.end();
  }
  inline bool append(const ValueType& value){
    vec.emplace_back(value);
    return true;
  }
  inline ValueType& add() {
    ValueType new_ele = ValueType();
    vec.push_back(new_ele);
    return vec.back();
  }
  inline size_t size() {
    return vec.size();
  }

#define TEMPARRAY_FOR_BEGIN(prefix, dt_varname, ele_varname) \
for(auto prefix##_i = dt_varname.vec.begin(); prefix##_i != dt_varname.vec.end(); prefix##_i++) {\
auto ele_varname = *( prefix##_i );
#define TEMPARRAY_FOR_END  }

  inline void sort(std::function<bool(const ValueType& a, const ValueType& b)> cmp) {
    std::sort(vec.begin(), vec.end(), cmp);
  }
  inline void sort() {
    std::sort(vec.begin(), vec.end());
  }  
};

template<typename KeyType>
class SimpleComparator {
public:
  inline bool operator()(const KeyType& k1, const KeyType& k2) const {
    return k1 < k2;
  }
  SimpleComparator(const SimpleComparator& other) {}
  SimpleComparator() {}
};

template<typename KeyType>
class SimpleEqualityChecker {
public:
  inline bool operator()(const KeyType& k1, const KeyType& k2) const {
    return k1 == k2;
  }
  SimpleEqualityChecker(const SimpleEqualityChecker& other) {}
  SimpleEqualityChecker() {}
};

template<typename KeyType>
class SimpleHasher {
public:
  inline size_t operator()(const KeyType& k) const {
    return k.get_hash();
  }
  SimpleHasher(const SimpleHasher& other) {}
  SimpleHasher() {}
};


template<typename KeyType, typename ValueType, size_t MAX_NODES_PER_ARRAY>
class SmallTreeIndex {
public:
  std::multimap<KeyType, ValueType> multimap;
  inline size_t size(){ 
    return multimap.size(); 
  }
  // inline bool insert_by_key(const KeyType& key, const ValueType& value){
  //   multimap.insert(std::pair<KeyType,ValueType>(key, value));
  // }
  inline size_t insert_by_key(const KeyType& key, const ValueType& value){
    auto prefix_ret = multimap.equal_range(key);
    bool exist = false;
    for (auto prefix_it=prefix_ret.first; prefix_it!=prefix_ret.second; ++prefix_it) { 
      if (prefix_it->second == value) exist = true;
    }
    if (!exist)
      multimap.insert(std::pair<KeyType,ValueType>(key, value));
    return 0;
  }
  inline bool remove_by_key(const KeyType& key, const ValueType& value){
    auto prefix_ret = multimap.equal_range(key);
    for (auto prefix_it=prefix_ret.first; prefix_it!=prefix_ret.second; ++prefix_it) { 
      if (prefix_it->second == value) {
        multimap.erase(prefix_it);
        break;
      }
    }
  }

#define SMALLTREEINDEX_INDEX_FOR_BEGIN(prefix, key, dt_varname, ele_varname) \
auto prefix##_ret = dt_varname.multimap.equal_range(*key); \
for (auto prefix##_it=prefix##_ret.first; prefix##_it!=prefix##_ret.second; ++prefix##_it) { \
  auto & ele_varname = prefix##_it->second;
#define SMALLTREEINDEX_INDEX_FOR_END }

#define SMALLTREEINDEX_RANGE_FOR_BEGIN(prefix, key1, key2, dt_varname, ele_varname) \
auto prefix##_it_begin = dt_varname.lowerkey(key1); \
auto prefix##_it_end = dt_varname.upperkey(key2); \
for (auto prefix##_it=prefix##_it_begin; prefix##_it!=prefix##_it_end; ++prefix##_it) { \
  auto ele_varname = prefix##_it->second;
#define SMALLTREEINDEX_RANGE_FOR_END }

  inline ValueType* find_by_key(const KeyType& key) {
    auto itr = multimap.find(key);
    if (itr != multimap.end()) return &(itr->second);
    else return nullptr;
  }
  inline const typename std::multimap<KeyType, ValueType>::iterator lowerkey(const KeyType* key) {
    if (key != nullptr) return multimap.lower_bound(*key);
    else return multimap.begin();
  }
  inline const typename std::multimap<KeyType, ValueType>::iterator upperkey(const KeyType* key) {
    if (key != nullptr) return multimap.upper_bound(*key);
    else return multimap.end();
  }
};

// template<typename KeyType, typename ValueType, size_t MAX_NODES_PER_ARRAY>
// using TreeIndex = SmallTreeIndex<KeyType, ValueType, MAX_NODES_PER_ARRAY>;
// #define TREEINDEX_INDEX_FOR_BEGIN SMALLTREEINDEX_INDEX_FOR_BEGIN
// #define TREEINDEX_INDEX_FOR_END SMALLTREEINDEX_INDEX_FOR_END
// #define TREEINDEX_RANGE_FOR_BEGIN SMALLTREEINDEX_RANGE_FOR_BEGIN
// #define TREEINDEX_RANGE_FOR_END SMALLTREEINDEX_RANGE_FOR_END

template<typename KeyType, typename ValueType, size_t MAX_NODES_PER_ARRAY>
class TreeIndex {
public:
  stx::btree_multimap<KeyType, ValueType> multimap;
  ValueType buffer;
  inline size_t size(){ 
    return multimap.size(); 
  }
  // inline bool insert_by_key(const KeyType& key, const ValueType& value){
  //   multimap.insert(std::pair<KeyType,ValueType>(key, value));
  // }
  inline size_t insert_by_key(const KeyType& key, const ValueType& value){
    auto prefix_ret = multimap.equal_range(key);
    bool exist = false;
    for (auto prefix_it=prefix_ret.first; prefix_it!=prefix_ret.second; ++prefix_it) { 
      if (prefix_it->second == value) exist = true;
    }
    if (!exist)
      multimap.insert2(key, value);
    return 0;
  }
  inline bool remove_by_key(const KeyType& key, const ValueType& value){
    auto prefix_ret = multimap.equal_range(key);
    for (auto prefix_it=prefix_ret.first; prefix_it!=prefix_ret.second; ++prefix_it) { 
      if (prefix_it->second == value) {
        multimap.erase(prefix_it);
        break;
      }
    }
  }


#define TREEINDEX_INDEX_FOR_BEGIN(prefix, key, dt_varname, ele_varname) \
auto prefix##_ret = dt_varname.multimap.equal_range(*key); \
for (auto prefix##_it=prefix##_ret.first; prefix##_it!=prefix##_ret.second; ++prefix##_it) { \
  auto & ele_varname = prefix##_it->second;
#define TREEINDEX_INDEX_FOR_END }

#define TREEINDEX_RANGE_FOR_BEGIN(prefix, key1, key2, dt_varname, ele_varname) \
auto prefix##_it_begin = dt_varname.lowerkey(key1); \
auto prefix##_it_end = dt_varname.upperkey(key2); \
for (auto prefix##_it=prefix##_it_begin; prefix##_it!=prefix##_it_end; ++prefix##_it) { \
  auto ele_varname = prefix##_it->second;
#define TREEINDEX_RANGE_FOR_END }

  inline ValueType* find_by_key(const KeyType& key) {
    auto itr = multimap.find(key);
    if (itr != multimap.end()) {
      buffer = (itr->second);
      return &buffer;
    }
    else return nullptr;
  }
  inline const typename stx::btree_multimap<KeyType, ValueType>::iterator lowerkey(const KeyType* key) {
    if (key != nullptr) return multimap.lower_bound(*key);
    else return multimap.begin();
  }
  inline const typename stx::btree_multimap<KeyType, ValueType>::iterator upperkey(const KeyType* key) {
    if (key != nullptr) return multimap.upper_bound(*key);
    else return multimap.end();
  }
};


template<typename KeyType, typename ValueType, size_t MAX_NODES_PER_ARRAY>
class HashIndex {
public:
  std::unordered_multimap<KeyType, ValueType, SimpleHasher<KeyType>> multimap;
  inline size_t size(){ 
    return multimap.size(); 
  }
  // inline bool insert_by_key(const KeyType& key, const ValueType& value){
  //   multimap.insert(std::pair<KeyType,ValueType>(key, value));
  // }
  inline size_t insert_by_key(const KeyType& key, const ValueType& value){
    auto range = multimap.equal_range(key); 
    bool exist = false;
    for (auto prefix_itr = range.first; prefix_itr != range.second; ++prefix_itr) {
      if (prefix_itr->second == value) exist = true;
    }
    if (!exist)
      multimap.insert(std::pair<KeyType,ValueType>(key, value));
    return 0;
  }
  inline bool remove_by_key(const KeyType& key, const ValueType& value){
    auto range = multimap.equal_range(key); 
    for (auto prefix_itr = range.first; prefix_itr != range.second; ++prefix_itr) {
      if (prefix_itr->second == value) {
        multimap.erase(prefix_itr);
        break;
      }
    }
  }
  

#define HASHINDEX_INDEX_FOR_BEGIN(prefix, key, dt_varname, ele_varname) \
  auto prefix##_range = dt_varname.multimap.equal_range(*key); \
  for (auto prefix##_itr = prefix##_range.first; prefix##_itr != prefix##_range.second; ++prefix##_itr) { \
    auto ele_varname = prefix##_itr->second;
#define HASHINDEX_INDEX_FOR_END }

#define SMALLHASHINDEX_INDEX_FOR_BEGIN HASHINDEX_INDEX_FOR_BEGIN
#define SMALLHASHINDEX_INDEX_FOR_END HASHINDEX_INDEX_FOR_END

};
template <typename KeyType, typename ValueType, size_t MAX_NODES_PER_ARRAY>
using SmallHashIndex = HashIndex<KeyType, ValueType, MAX_NODES_PER_ARRAY>;


template<typename ValueType, size_t MAX_NODES_PER_ARRAY>
class SmallBasicArray {
public:

  ValueType* elements;
  SmallBasicArray() {
    cur_idx = 0;
    elements = new ValueType[MAX_NODES_PER_ARRAY+1];
  }
  size_t cur_idx;
  inline bool invalid_key(oid_t key){
    return key >= cur_idx;
  }
  inline ValueType* get_ptr_by_pos(oid_t pos){
    if (invalid_pos(pos)) return nullptr;
    return &elements[pos];
  }
  inline oid_t get_pos_by_id(oid_t id){
    for (size_t prefix_i=0; prefix_i<cur_idx; prefix_i++) {
      if (elements[prefix_i].id == id) {
        return prefix_i;
      }
    }
    return INVALID_POS;
  }
  inline size_t size(){
    return cur_idx;
  }
  inline ValueType* get_last_element() {
    if (cur_idx == 0) return nullptr;
    return &elements[cur_idx-1];
  }
  inline size_t insert(const ValueType& value) {
    if (cur_idx > MAX_NODES_PER_ARRAY) return cur_idx;
    elements[cur_idx] = value;
    cur_idx++;
    return cur_idx-1;
  }
  inline size_t insert_no_duplicate(const ValueType& value) {
    if (cur_idx > MAX_NODES_PER_ARRAY) return cur_idx;
    bool exist = false;
    for (size_t prefix_i=0; prefix_i<cur_idx; prefix_i++) {
      if (elements[prefix_i] == value) {
        exist = true;
        break;
      }
    }
    if (!exist) {
      elements[cur_idx] = value;
      cur_idx++;
      return cur_idx-1;
    } else {
      return 0;
    }
  }
  inline size_t remove(const ValueType& value) {
    for (size_t prefix_i=0; prefix_i<cur_idx; prefix_i++) {
      if (elements[prefix_i] == value) {
        memset(&elements[prefix_i], 0, sizeof(ValueType));
        cur_idx -= 1;
        return prefix_i;
      }
    }
    return 0;
  }
#define SMALLBASICARRAY_FOR_BEGIN(prefix, dt_name, ele_name) \
for (size_t prefix##_i=0; prefix##_i<dt_name.cur_idx; prefix##_i++) { \
  auto & ele_name = dt_name.elements[prefix##_i];
#define SMALLBASICARRAY_FOR_END }
/*
  std::vector<ValueType> elements;
  inline bool invalid_key(oid_t key) { return key >= elements.size(); }
  inline ValueType* get_ptr_by_pos(oid_t pos) {
    if (invalid_key(pos)) return nullptr;
    return &elements[pos];
  }
  inline oid_t get_pos_by_id(oid_t id){
    for (size_t prefix_i=0; prefix_i<elements.size(); prefix_i++) {
      if (elements[prefix_i].id == id) {
        return prefix_i;
      }
    }
    return INVALID_POS;
  }
  inline size_t size() { return elements.size(); }
  inline ValueType* get_last_element() {
    if (elements.size() == 0) return nullptr;
    return &elements[elements.size()-1];
  }
  inline size_t insert(const ValueType& value) {
    elements.push_back(value);
    return elements.size()-1;
  }
  inline size_t insert_no_duplicate(const ValueType& value) {
    bool exist = false;
    for (size_t prefix_i=0; prefix_i<elements.size(); prefix_i++) {
      if (elements[prefix_i] == value) {
        exist = true;
        break;
      }
    }
    if (!exist) {
      elements.push_back(value);
      return elements.size()-1;
    } else {
      return 0;
    }
  }
  inline size_t remove(const ValueType& value) {
    for (size_t prefix_i=0; prefix_i<elements.size(); prefix_i++) {
      if (elements[prefix_i] == value) {
        memset(&elements[prefix_i], 0, sizeof(ValueType));
        return prefix_i;
      }
    }
    return 0;
  }
#define SMALLBASICARRAY_FOR_BEGIN(prefix, dt_name, ele_name) \
for (size_t prefix##_i=0; prefix##_i<dt_name.elements.size(); prefix##_i++) { \
  auto & ele_name = dt_name.elements[prefix##_i];
#define SMALLBASICARRAY_FOR_END }
*/
};

//template<typename ValueType, size_t MAX_NODES_PER_ARRAY>
//using BasicArray = SmallBasicArray<ValueType, MAX_NODES_PER_ARRAY>;
//#define BASICARRAY_FOR_BEGIN SMALLBASICARRAY_FOR_BEGIN
//#define BASICARRAY_FOR_END SMALLBASICARRAY_FOR_END


#define SINGLE_ELEMENT_FOR_BEGIN(prefix, dt_name, ele_name) \
{ \
  auto & ele_name = dt_name;
#define SINGLE_ELEMENT_FOR_END }

template<typename ValueType, size_t MAX_NODES_PER_ARRAY>
class BasicArray {
public:
  std::vector<ValueType> elements;
  BasicArray() {
    elements.reserve(MAX_NODES_PER_ARRAY);
  }
  inline bool invalid_key(oid_t key) { return key >= elements.size(); }
  inline ValueType* get_ptr_by_pos(oid_t pos) {
    if (invalid_pos(pos)) return nullptr;
    return &elements[pos];
  }
  inline oid_t get_pos_by_id(oid_t id){
    for (size_t prefix_i=0; prefix_i<elements.size(); prefix_i++) {
      if (elements[prefix_i].id == id) {
        return prefix_i;
      }
    }
    return INVALID_POS;
  }
  inline size_t size() { return elements.size(); }
  inline ValueType* get_last_element() {
    if (elements.size() == 0) return nullptr;
    return &elements[elements.size()-1];
  }
  inline size_t insert(const ValueType& value) {
    elements.push_back(value);
    return elements.size()-1;
  }
  inline size_t insert_no_duplicate(const ValueType& value) {
    bool exist = false;
    for (size_t prefix_i=0; prefix_i<elements.size(); prefix_i++) {
      if (elements[prefix_i] == value) {
        exist = true;
        break;
      }
    }
    if (!exist) {
      elements.push_back(value);
      return elements.size()-1;
    } else {
      return 0;
    }
  }
  inline size_t remove(const ValueType& value) {
    for (size_t prefix_i=0; prefix_i<elements.size(); prefix_i++) {
      if (elements[prefix_i] == value) {
        memset(&elements[prefix_i], 0, sizeof(ValueType));
        return prefix_i;
      }
    }
    return 0;
  }
#define BASICARRAY_FOR_BEGIN(prefix, dt_name, ele_name) \
for (size_t prefix##_i=0; prefix##_i<dt_name.elements.size(); prefix##_i++) { \
  auto & ele_name = dt_name.elements[prefix##_i];
#define BASICARRAY_FOR_END }
/*
  struct Block {
    ValueType elements[BLOCK_SZ];
  };
  size_t cur_idx;
  size_t cur_block;
  Block** blocks;
  BasicArray() {
    cur_idx = 0;
    cur_block = 0;
    blocks = reinterpret_cast<Block**>(malloc(sizeof(Block*)*(MAX_NODES_PER_ARRAY/BLOCK_SZ+1)));
    blocks[0] = new Block();
  }
  inline bool invalid_key(oid_t key){
    return key >= cur_idx;
  }
  inline ValueType* get_ptr_by_pos(oid_t pos){
    if (invalid_key(pos)) return nullptr;
    size_t block = (pos)/BLOCK_SZ;
    size_t offset = (pos)%BLOCK_SZ;
    return &(blocks[block]->elements[offset]);
  }
  inline oid_t get_pos_by_id(oid_t id){
    for (size_t i=0; i<cur_idx; i++) {
      size_t block = (i)/BLOCK_SZ;
      size_t offset = (i)%BLOCK_SZ;
      if (blocks[block]->elements[offset].id == id) {
        return i;
      }
    }
    return INVALID_POS;
  }
  inline size_t size(){
    return cur_idx;
  }
  inline ValueType* get_last_element() {
    if (cur_idx == 0) return nullptr;
    size_t block = (cur_idx-1)/BLOCK_SZ;
    size_t offset = (cur_idx-1)%BLOCK_SZ;
    return &(blocks[block]->elements[offset]);
  }
  inline void resize() {
    Block** old_ptr = blocks;
    blocks = reinterpret_cast<Block**>(malloc(sizeof(Block*)*(cur_block+MAX_NODES_PER_ARRAY/BLOCK_SZ+1)));
    memcpy(blocks, old_ptr, sizeof(Block*)*(cur_block+1));
    free(old_ptr);
  }
  inline bool insert_by_key(oid_t key, const ValueType& value){
    //if (invalid_key(key)) return false;
    if (key > cur_idx) cur_idx = key;
    size_t block = (key)/BLOCK_SZ;
    size_t offset = (key)%BLOCK_SZ;
    if (block > cur_block && block % (MAX_NODES_PER_ARRAY/BLOCK_SZ+1)==0) resize();
    size_t before_block = cur_block;
    if (block > cur_block) {
      cur_block = block;
      blocks[cur_block] = reinterpret_cast<Block*>(malloc(sizeof(Block)));
    }
    blocks[block]->elements[offset] = value;
    return true;
  }
  inline size_t insert(const ValueType& value) {
    size_t block = cur_idx/BLOCK_SZ;
    size_t offset = cur_idx%BLOCK_SZ;
    cur_idx++;
    if (block > cur_block && block % (MAX_NODES_PER_ARRAY/BLOCK_SZ+1)==0) resize();
    size_t before_block = cur_block;
    if (block > cur_block) {
      cur_block = block;
      blocks[cur_block] = reinterpret_cast<Block*>(malloc(sizeof(Block)));
    }
    blocks[block]->elements[offset] = value;
    return cur_idx-1;
  }
  inline size_t insert_no_duplicate(const ValueType& value) {
    //FIXME
    insert(value);
  }
  inline size_t remove(const ValueType& value) {
    //FIXME
    return 0;
  }
#define BASICARRAY_FOR_BEGIN(prefix, dt_varname, ele_varname) \
for(size_t prefix##_i = 0; prefix##_i <= dt_varname.cur_block; prefix##_i++) { \
  for(size_t prefix##_j = 0; prefix##_j < BLOCK_SZ && prefix##_i*BLOCK_SZ + prefix##_j < dt_varname.cur_idx; prefix##_j++) { \
    auto & ele_varname = dt_varname.blocks[prefix##_i]->elements[prefix##_j];
#define BASICARRAY_FOR_END } }
*/
};


template<typename KeyType, typename ValueType, size_t MAX_NODES_PER_ARRAY>
class SmallSortedArray {
 public:
  struct Element{
    KeyType key;
    ValueType value;
  };
  Element e[MAX_NODES_PER_ARRAY+1];
  size_t cur_idx;
  SmallSortedArray()  {
    cur_idx = 0;
  }
  inline ValueType* get_ptr_by_pos(oid_t pos){
    if (invalid_pos(pos)) return nullptr;
    return &e[pos];
  }
  inline size_t get_pos_by_key(const KeyType& key) {
    size_t i = 0;
    for (; i<cur_idx; i++){
      if (key == e[i].key || key < e[i].key) return i;
    }
    return i;
  }
  inline size_t size() {
    return cur_idx;
  }
  inline size_t insert_by_key(const KeyType& key, const ValueType& value) {
    if (cur_idx >= MAX_NODES_PER_ARRAY) return false;
    size_t insert_pos = get_pos_by_key(key);
    if (e[insert_pos].value == value) return false;
    cur_idx ++;
    for (size_t i=cur_idx-1; i>insert_pos; i--) {
      memcpy(&e[i], &e[i-1], sizeof(Element));
    }
    e[insert_pos].key = key;
    e[insert_pos].value = value;
    return insert_pos;
  }
  inline bool remove_by_key(const KeyType& key, const ValueType& value) {
    size_t insert_pos = get_pos_by_key(key);
    for (size_t i=cur_idx-1; i>insert_pos; i--) {
      memcpy(&e[i-1], &e[i], sizeof(Element));
    }
    cur_idx --;
    return true;
  }

#define SMALLSORTEDARRAY_INDEX_FOR_BEGIN(prefix, ptrkey, dt_varname, ele_varname) \
  size_t prefix##_pos = dt_varname.get_pos_by_key(*(ptrkey)); \
  for(size_t prefix##_i=prefix##_pos; prefix##_i<dt_varname.cur_idx; prefix##_i++) { \
    if (*(ptrkey) < dt_varname.e[prefix##_i].key) break; \
    auto & ele_varname = dt_varname.e[prefix##_i].value;
#define SMALLSORTEDARRAY_INDEX_FOR_END }

#define SMALLSORTEDARRAY_RANGE_FOR_BEGIN(prefix, key1, key2, dt_varname, ele_varname) \
size_t prefix##_pos_start = dt_varname.lowerkey(key1); \
size_t prefix##_pos_end = dt_varname.upperkey(key2); \
for(size_t prefix##_i=prefix##_pos_start; prefix##_i<prefix##_pos_end; prefix##_i++) { \
  auto & ele_varname = dt_varname.e[prefix##_i].value;
#define SMALLSORTEDARRAY_RANGE_FOR_END }

  inline ValueType* find_by_key(const KeyType& key) {
    size_t start_idx = get_pos_by_key(key);
    if (start_idx > MAX_NODES_PER_ARRAY) return nullptr;
    return &(e[start_idx].value);
  }
  inline size_t lowerkey(const KeyType* key) {
    if (key != nullptr) return get_pos_by_key(*key);
    return 0; 
  }
  inline size_t upperkey(const KeyType* key) {
    if (key != nullptr) return get_pos_by_key(*key);
    return cur_idx; 
  }
};

template<typename KeyType, typename ValueType, size_t MAX_NODES_PER_ARRAY>
class SortedArray {
 public:
  struct Element{
    KeyType key;
    ValueType value;
    inline bool operator < (const Element& e) const {
      return this->key < e.key;
    }
    inline bool operator == (const Element& e) const {
      return this->key == e.key;
    }
    Element () {}
    Element (const KeyType& _key) : key(_key) {}
    Element (const KeyType& _key, const ValueType& _value) : key(_key), value(_value) {}
  };
  std::vector<Element> e;
  inline typename std::vector<Element>::iterator get_pos_by_key(const KeyType& key) {
    auto i = std::lower_bound(e.begin(), e.end(), Element(key));
    return i;
  }
  inline size_t size() {
    return e.size();
  }
  inline ValueType* get_ptr_by_pos(oid_t pos){
    if (invalid_pos(pos)) return nullptr;
    return &e[pos];
  }
  // inline bool insert_by_key(const KeyType& key, const ValueType& value) {
  //   auto i = get_pos_by_key(key);
  //   e.insert(i, Element(key, value));
  //   return true;
  // }
  inline size_t insert_by_key(const KeyType& key, const ValueType& value) {
    auto i0 = std::lower_bound(e.begin(), e.end(), Element(key));
    auto i1 = std::upper_bound(e.begin(), e.end(), Element(key));
    bool exist = false;
    for (auto i=i0; i!=i1; i++){
      if ((*i).value == value) exist = true;
    }
    if (!exist)  {
      auto v = e.insert(i0, Element(key, value));
      return std::distance(e.begin(), v);
    } else {
      return INVALID_POS;
    }
  }
  inline bool remove_by_key(const KeyType& key, const ValueType& value) {
    auto i0 = std::lower_bound(e.begin(), e.end(), Element(key));
    auto i1 = std::upper_bound(e.begin(), e.end(), Element(key));
    bool exist = false;
    for (auto i=i0; i!=i1; i++){
      if ((*i).value == value) {
        e.erase(i);
        break;
      }
    }
    return true;
  }


#define SORTEDARRAY_INDEX_FOR_BEGIN(prefix, ptrkey, dt_varname, ele_varname) \
  auto prefix##_pos = dt_varname.get_pos_by_key(*(ptrkey)); \
  for(auto prefix##_i=prefix##_pos; prefix##_i!=dt_varname.e.end(); prefix##_i++) { \
    if (*(ptrkey) < (*prefix##_i).key) break; \
    auto & ele_varname = (*prefix##_i).value;
#define SORTEDARRAY_INDEX_FOR_END }

#define SORTEDARRAY_RANGE_FOR_BEGIN(prefix, key1, key2, dt_varname, ele_varname) \
auto prefix##_pos_start = dt_varname.lowerkey(key1); \
auto prefix##_pos_end = dt_varname.upperkey(key2); \
for(auto prefix##_i=prefix##_pos_start; prefix##_i!=prefix##_pos_end; prefix##_i++) { \
  auto & ele_varname = (*prefix##_i).value;
#define SORTEDARRAY_RANGE_FOR_END }
  
  inline ValueType* find_by_key(const KeyType& key) {
    auto start_idx = get_pos_by_key(key);
    if (start_idx == e.end()) return nullptr;
    return &((*start_idx).value);
  }
  inline const typename std::vector<Element>::iterator lowerkey(const KeyType* key) {
    if (key != nullptr) return get_pos_by_key(*key);
    return e.begin(); 
  }
  inline const typename std::vector<Element>::iterator upperkey(const KeyType* key) {
    if (key != nullptr) return get_pos_by_key(*key);
    return e.end(); 
  }
};

#define ARENA_SZ 65536
class TempArena {
public:
  char** ptrs;
  char* ptr;
  size_t cur_offset;
  size_t cur_block;
  TempArena() {
    ptrs = reinterpret_cast<char**>(malloc(sizeof(char*)*64));
    cur_offset = 0;
    cur_block = 0;
    ptrs[0] = reinterpret_cast<char*>(malloc(ARENA_SZ));
    ptr = ptrs[0];
  }
  inline void resize() {
    //TODO
  }
  inline void increment_ptr(size_t sz){
    if (cur_offset + sz > ARENA_SZ) {
      cur_block ++;
      if (cur_block > 64) resize();
      ptrs[cur_block] = reinterpret_cast<char*>(malloc(ARENA_SZ));
      ptr = ptrs[cur_block];
      cur_offset = sz;
    } else {
      cur_offset += sz;
      ptr = ptr + sz;
    }
  }
  ~TempArena() {
    for (size_t i=0; i<cur_block; i++){
      free(ptrs[i]);
    }
    free(ptrs);
  }
};

#endif // _DATA_STRUCTURE_H_
