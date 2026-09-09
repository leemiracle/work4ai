#!/usr/bin/env python3
"""
tinymmu/tlb.py — TLB（Translation Lookaside Buffer）

参照：csapp Ch9 §9.3.4 / x86 TLB / ARM MMU
csdiy 对应：csapp Ch9(虚拟内存) + csapp Ch6(cache层次)

TLB = 页表的硬件缓存
  CPU 访问虚拟地址 → 先查 TLB
  TLB Hit: 直接得到物理地址（1 cycle）
  TLB Miss: 遍历页表（page walk）→ 填充 TLB（100+ cycles）
"""
from collections import OrderedDict

class TLBEntry:
    def __init__(self, vpn, pfn, flags, asid=0):
        self.vpn = vpn; self.pfn = pfn; self.flags = flags; self.asid = asid

class TLB:
    """TLB 缓存（参照 csapp Ch9 §9.3.4）
    全关联 + LRU 替换"""
    def __init__(self, size=64):
        self.size = size
        self.entries: dict = {}  # 使用普通 dict，Python 3.7+ 保持插入顺序
        self.order: list = []   # LRU 顺序
        self.hits = 0; self.misses = 0
    def lookup(self, vpn, asid=0):
        key = (vpn, asid)
        if key in self.entries:
            self.order.remove(key); self.order.append(key)  # LRU
            self.hits += 1
            return self.entries[key]
        self.misses += 1
        return None
    def insert(self, vpn, pfn, flags, asid=0):
        key = (vpn, asid)
        if key in self.entries:
            self.order.remove(key)
        self.entries[key] = TLBEntry(vpn, pfn, flags, asid)
        self.order.append(key)
        if len(self.entries) > self.size:
            oldest = self.order.pop(0)  # LRU 淘汰
            del self.entries[oldest]
    def invalidate(self, vpn=None, asid=0):
        if vpn is None:
            self.entries.clear(); self.order.clear()
        else:
            key = (vpn, asid)
            self.entries.pop(key, None)
            if key in self.order: self.order.remove(key)
    def hit_rate(self):
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0
    def stats(self):
        return {"size": len(self.entries), "capacity": self.size,
                "hits": self.hits, "misses": self.misses,
                "hit_rate": f"{self.hit_rate():.1%}"}
