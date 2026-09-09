#!/usr/bin/env python3

class HashTable:
    def __init__(self, size=1000):
        self.size = size
        self.buckets = [[] for _ in range(size)]
        self.count = 0
    
    def _hash(self, key):
        return hash(key) % self.size
    
    def insert(self, key, value):
        index = self._hash(key)
        bucket = self.buckets[index]
        
        for i, (k, v) in enumerate(bucket):
            if k == key:
                bucket[i] = (key, value)
                return
        
        bucket.append((key, value))
        self.count += 1
        
        # 自动扩容
        if self.count / self.size > 0.7:
            self._resize()
    
    def _resize(self):
        old_buckets = self.buckets
        self.size *= 2
        self.buckets = [[] for _ in range(self.size)]
        self.count = 0
        
        for bucket in old_buckets:
            for key, value in bucket:
                self.insert(key, value)
    
    def get(self, key):
        index = self._hash(key)
        bucket = self.buckets[index]
        
        for k, v in bucket:
            if k == key:
                return v
        
        raise KeyError(f"Key not found: {key}")
    
    def remove(self, key):
        index = self._hash(key)
        bucket = self.buckets[index]
        
        for i, (k, v) in enumerate(bucket):
            if k == key:
                bucket.pop(i)
                self.count -= 1
                return
        
        raise KeyError(f"Key not found: {key}")
    
    def __contains__(self, key):
        try:
            self.get(key)
            return True
        except KeyError:
            return False


class OpenAddressingHashTable:
    def __init__(self, size=1000):
        self.size = size
        self.keys = [None] * size
        self.values = [None] * size
        self.count = 0
    
    def _hash(self, key, attempt=0):
        return (hash(key) + attempt) % self.size
    
    def insert(self, key, value):
        if self.count / self.size > 0.7:
            self._resize()
        
        attempt = 0
        first_deleted = None
        
        while attempt < self.size:
            index = self._hash(key, attempt)
            
            if self.keys[index] is None:
                if first_deleted is not None:
                    index = first_deleted
                self.keys[index] = key
                self.values[index] = value
                self.count += 1
                return
            
            if self.keys[index] == key:
                self.values[index] = value
                return
            
            if self.keys[index] == "DELETED" and first_deleted is None:
                first_deleted = index
            
            attempt += 1
        
        raise Exception("Table is full")
    
    def _resize(self):
        old_keys = self.keys
        old_values = self.values
        
        self.size *= 2
        self.keys = [None] * self.size
        self.values = [None] * self.size
        self.count = 0
        
        for key, value in zip(old_keys, old_values):
            if key is not None and key != "DELETED":
                self.insert(key, value)
    
    def get(self, key):
        attempt = 0
        
        while attempt < self.size:
            index = self._hash(key, attempt)
            
            if self.keys[index] is None:
                raise KeyError(f"Key not found: {key}")
            
            if self.keys[index] == key:
                return self.values[index]
            
            attempt += 1
        
        raise KeyError(f"Key not found: {key}")
    
    def remove(self, key):
        attempt = 0
        
        while attempt < self.size:
            index = self._hash(key, attempt)
            
            if self.keys[index] is None:
                raise KeyError(f"Key not found: {key}")
            
            if self.keys[index] == key:
                self.keys[index] = "DELETED"
                self.values[index] = None
                self.count -= 1
                return
            
            attempt += 1
        
        raise KeyError(f"Key not found: {key}")


if __name__ == "__main__":
    # 测试哈希表
    print("Testing HashTable...")
    ht = HashTable()
    
    ht.insert("name", "Alice")
    ht.insert("age", 25)
    ht.insert("city", "Beijing")
    
    print(f"name: {ht.get('name')}")
    print(f"age: {ht.get('age')}")
    print(f"'name' in ht: {'name' in ht}")
    
    ht.remove("age")
    try:
        ht.get("age")
    except KeyError:
        print("age removed successfully")
    
    print(f"Count: {ht.count}")
    print(f"Load factor: {ht.count / ht.size:.2f}")
    
    # 测试开放寻址哈希表
    print("\nTesting OpenAddressingHashTable...")
    oht = OpenAddressingHashTable()
    
    oht.insert("name", "Bob")
    oht.insert("age", 30)
    oht.insert("city", "Shanghai")
    
    print(f"name: {oht.get('name')}")
    print(f"age: {oht.get('age')}")
    print(f"'name' in oht: {'name' in oht}")
    
    oht.remove("age")
    try:
        oht.get("age")
    except KeyError:
        print("age removed successfully")
    
    print(f"Count: {oht.count}")
    print(f"Load factor: {oht.count / oht.size:.2f}")