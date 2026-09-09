#!/usr/bin/env python3
"""tinyindex — 多种索引引擎对比（Hash/B+Tree/LSM）
参照：PostgreSQL index types / LevelDB / Redis
csdiy 对应：tinydb(B+树) + leveldb-lsm精读 + storage-comparison精读
核心：同数据 × 三种索引 → 插入/查询/范围性能对比"""
import time, random, bisect
from collections import defaultdict

class HashIndex:
    """哈希索引（参照 PostgreSQL Hash Index）"""
    def __init__(self): self.idx=defaultdict(list)
    def insert(self,key,val): self.idx[key].append(val); return True
    def lookup(self,key): return self.idx.get(key,[])
    def range(self,lo,hi): return [v for k in range(lo,hi+1) for v in self.idx.get(k,[])]

class SortedIndex:
    """有序索引（参照 PostgreSQL B-tree Index，简化为排序数组+二分）"""
    def __init__(self): self.keys=[]; self.vals={}
    def insert(self,key,val):
        pos=bisect.bisect_left(self.keys,key)
        if pos<len(self.keys) and self.keys[pos]==key:
            self.vals[key]=val
        else:
            self.keys.insert(pos,key); self.vals[key]=val
    def lookup(self,key):
        pos=bisect.bisect_left(self.keys,key)
        return [self.vals[key]] if pos<len(self.keys) and self.keys[pos]==key else []
    def range(self,lo,hi):
        lo_pos=bisect.bisect_left(self.keys,lo)
        hi_pos=bisect.bisect_right(self.keys,hi)
        return [self.vals[k] for k in self.keys[lo_pos:hi_pos]]

class LSMIndex:
    """LSM 索引（参照 LevelDB，简化为 MemTable + sorted segments）"""
    def __init__(self): self.memtable={}; self.segments=[]; self.threshold=100
    def insert(self,key,val):
        self.memtable[key]=val
        if len(self.memtable)>=self.threshold: self._flush()
    def _flush(self):
        if self.memtable:
            sorted_items=sorted(self.memtable.items())
            self.segments.insert(0,sorted_items); self.memtable={}
    def lookup(self,key):
        if key in self.memtable: return [self.memtable[key]]
        for seg in self.segments:
            keys=[k for k,_ in seg]
            pos=bisect.bisect_left(keys,key)
            if pos<len(keys) and keys[pos]==key: return [seg[pos][1]]
        return []
    def range(self,lo,hi):
        result=[]
        seen=set()
        for k,v in self.memtable.items():
            if lo<=k<=hi and k not in seen: result.append(v); seen.add(k)
        for seg in self.segments:
            for k,v in seg:
                if lo<=k<=hi and k not in seen: result.append(v); seen.add(k)
        return sorted(result)

def bench(name,idx,data,queries):
    t1=time.perf_counter()
    for k,v in data: idx.insert(k,v)
    t2=time.perf_counter()
    for q in queries: idx.lookup(q)
    t3=time.perf_counter()
    idx.range(min(data)[0],min(data)[0]+50)
    t4=time.perf_counter()
    return {"insert_ms":(t2-t1)*1000,"lookup_ms":(t3-t2)*1000,"range_ms":(t4-t3)*1000}

def main():
    print("tinyindex — 索引引擎对比（Hash vs B+Tree vs LSM）\n")
    N=1000; data=[(i,f"val_{i}") for i in range(N)]
    random.shuffle(data); queries=random.sample(range(N),100)

    for name,idx_cls in [("Hash",HashIndex),("Sorted(B+)",SortedIndex),("LSM",LSMIndex)]:
        r=bench(name,idx_cls(),data,queries)
        print(f"  {name:12s} insert={r['insert_ms']:6.1f}ms lookup={r['lookup_ms']:6.1f}ms range={r['range_ms']:6.1f}ms")

    print(f"\n  结论: Hash查找最快但不能范围查; B+Tree均衡; LSM写入快读取慢")

if __name__=="__main__": main()
