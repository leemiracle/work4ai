#!/usr/bin/env python3
"""tinsketch — 概率数据结构集（Bloom/Count-Min/HyperLogLog）
参照：Bloom Filter / Count-Min Sketch / HyperLogLog
csdiy 对应：bloom-filter精读 + tinysearch + 大数据
核心：亚线性空间的数据统计"""
import hashlib, math, random

class BloomFilter:
    def __init__(self,capacity,fp=0.01):
        self.m=int(-capacity*math.log(fp)/(math.log(2)**2))
        self.k=int(self.m/capacity*0.693)
        self.bits=bytearray(self.m//8+1)
    def _hash(self,item):
        h1,h2=hashlib.md5(item.encode()).digest()[:8],hashlib.md5(item.encode()).digest()[8:16]
        i1=int.from_bytes(h1,'big'); i2=int.from_bytes(h2,'big')
        for i in range(self.k): yield (i1+i*i2)%self.m
    def add(self,item):
        for idx in self._hash(item): self.bits[idx//8]|=1<<(idx%8)
    def contains(self,item):
        return all(self.bits[idx//8]&(1<<(idx%8)) for idx in self._hash(item))

class CountMinSketch:
    """Count-Min Sketch（参照 Cormode-Muthukrishnan 2005）
    频率估计，空间 O(w*d)"""
    def __init__(self,width=1000,depth=5):
        self.w=width; self.d=depth; self.table=[[0]*width for _ in range(depth)]
        self.seeds=[random.randint(0,99999) for _ in range(depth)]
    def add(self,item,count=1):
        for i in range(self.d):
            idx=hash(f"{self.seeds[i]}:{item}")%self.w
            self.table[i][idx]+=count
    def estimate(self,item):
        return min(self.table[i][hash(f"{self.seeds[i]}:{item}")%self.w] for i in range(self.d))

class HyperLogLog:
    """HyperLogLog（参照 Flajolet 2007）
    去重计数，空间 O(2^b)"""
    def __init__(self,b=12):
        self.b=b; self.m=2**b; self.registers=[0]*self.m
    def add(self,item):
        x=int.from_bytes(hashlib.md5(item.encode()).digest()[:8],'big')
        idx=x>>(64-self.b); w=(x<<self.b)&((1<<64)-1)
        rank=64-self.b-w.bit_length()+1 if w>0 else 64-self.b+1
        if rank>self.registers[idx]: self.registers[idx]=rank
    def cardinality(self):
        alpha=0.7213/(1+1.079/self.m)
        Z=sum(2**(-r) for r in self.registers)
        return int(alpha*self.m**2/Z)

def main():
    print("tinsketch — 概率数据结构集（参照 Bloom/CMS/HLL）\n")

    bf=BloomFilter(10000)
    for i in range(5000): bf.add(f"item_{i}")
    tp=sum(bf.contains(f"item_{i}") for i in range(5000))
    fp=sum(bf.contains(f"miss_{i}") for i in range(500))
    print(f"  BloomFilter: TP={tp}/5000, FP={fp}/500 ({fp/500*100:.1f}%)")

    cms=CountMinSketch()
    for _ in range(1000): cms.add("hello")
    for _ in range(500): cms.add("world")
    for _ in range(100): cms.add("foo")
    print(f"  CountMinSketch: hello≈{cms.estimate('hello')}, world≈{cms.estimate('world')}")

    hll=HyperLogLog()
    for i in range(100000): hll.add(f"uuid_{i}")
    print(f"  HyperLogLog: estimated unique={hll.cardinality():,} (actual=100,000)")

if __name__=="__main__": main()
