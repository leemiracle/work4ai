#!/usr/bin/env python3
"""tinycachesim — 参照 cachegrind 的 CPU Cache 模拟器
参照：Valgrind cachegrind / gem5 / csapp Ch6
csdiy 对应：csapp Ch6(存储器层次) + perf §Case 2
核心：L1/L2 cache 层级 + hit/miss 统计 + 行 vs 列遍历对比"""
import random

class CacheSim:
    """直接映射 Cache 模拟器（参照 csapp Ch6 §6.4.3）
    真实 CPU 用组相联，本简化版用直接映射"""
    def __init__(self, size=256, line_size=8, levels=2):
        self.line_size = line_size
        self.levels = []
        for i in range(levels):
            capacity = size * (4**i)  # L1=256, L2=1024
            n_lines = capacity // line_size
            self.levels.append({"lines": [None]*n_lines, "hits":0, "misses":0, "capacity":capacity})
    def access(self, addr):
        """模拟一次内存访问"""
        line_addr = addr // self.line_size
        for level in self.levels:
            idx = line_addr % len(level["lines"])
            if level["lines"][idx] == line_addr:
                level["hits"] += 1; return  # Cache hit
            level["lines"][idx] = line_addr  # 写入（替换）
        self.levels[-1]["misses"] += 1  # 全 miss
    def stats(self):
        return [{"level":f"L{i+1}", "hits":l["hits"], "misses":l["misses"],
                 "hit_rate": f"{l['hits']/max(1,l['hits']+l['misses'])*100:.1f}%",
                 "capacity":l["capacity"]} for i,l in enumerate(self.levels)]

def main():
    print("tinycachesim — CPU Cache 模拟器（参照 csapp Ch6）\n")

    # 对比行优先 vs 列优先遍历（参照 csapp Ch6 的例子）
    N = 32  # 32x32 矩阵
    matrix = [[random.randint(0,255) for _ in range(N)] for _ in range(N)]

    # 行优先
    cache_row = CacheSim(size=256, line_size=8)
    for i in range(N):
        for j in range(N):
            cache_row.access(i * N + j)  # 连续地址
    print("  行优先遍历（连续地址 → cache 友好）:")
    for s in cache_row.stats():
        print(f"    {s['level']}: {s['hits']} hits / {s['misses']} misses → {s['hit_rate']}")

    # 列优先
    cache_col = CacheSim(size=256, line_size=8)
    for j in range(N):
        for i in range(N):
            cache_col.access(i * N + j)  # 跨行地址
    print("\n  列优先遍历（跨行 → cache miss 频繁）:")
    for s in cache_col.stats():
        print(f"    {s['level']}: {s['hits']} hits / {s['misses']} misses → {s['hit_rate']}")

    # 对比
    row_rate = cache_row.levels[0]["hits"] / max(1, cache_row.levels[0]["hits"]+cache_row.levels[0]["misses"])
    col_rate = cache_col.levels[0]["hits"] / max(1, cache_col.levels[0]["hits"]+cache_col.levels[0]["misses"])
    print(f"\n  L1 hit rate: 行优先 {row_rate*100:.1f}% vs 列优先 {col_rate*100:.1f}%")
    print(f"  行优先快 {row_rate/max(0.01,col_rate):.1f}x（参照 csapp Ch6 分块矩阵优化）")

if __name__ == "__main__": main()
