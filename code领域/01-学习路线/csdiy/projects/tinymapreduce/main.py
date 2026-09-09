#!/usr/bin/env python3
"""tinymapreduce — 参照 Hadoop MapReduce 的数据处理
参照：Hadoop MapReduce / Spark / MongoDB MapReduce
csdiy 对应：tinysearch + tinykafka
核心：Map(分片) → Shuffle(分组) → Reduce(聚合)"""
from collections import defaultdict

class TinyMapReduce:
    """MapReduce 引擎（参照 Hadoop）"""
    def __init__(self, num_workers=4): self.num_workers = num_workers

    def run(self, data, map_fn, reduce_fn):
        """执行 MapReduce"""
        # ① Map 阶段（分片并行模拟）
        mapped = []
        for item in data:
            mapped.extend(map_fn(item))
        # ② Shuffle 阶段（按 key 分组）
        shuffled = defaultdict(list)
        for key, value in mapped:
            shuffled[key].append(value)
        # ③ Reduce 阶段（每组聚合）
        results = {}
        for key, values in shuffled.items():
            results[key] = reduce_fn(key, values)
        return results

def main():
    print("tinymapreduce — MapReduce（参照 Hadoop）\n")
    mr = TinyMapReduce()

    # Word Count（经典 MapReduce 示例）
    text = ["hello world", "hello mapreduce", "world of distributed", "hello hadoop world"]
    print(f"  输入: {text}")

    def map_fn(line):
        return [(word.lower(), 1) for word in line.split()]

    def reduce_fn(key, values):
        return sum(values)

    result = mr.run(text, map_fn, reduce_fn)
    print(f"\n  Word Count 结果:")
    for word, count in sorted(result.items(), key=lambda x: -x[1]):
        print(f"    {word:15s} → {count}")

    # 另一个示例：按城市统计人口
    cities = [("北京", 1000), ("上海", 800), ("北京", 500),
              ("广州", 600), ("上海", 300), ("深圳", 700), ("广州", 200)]
    print(f"\n  人口统计:")
    result2 = mr.run(cities, lambda x: [(x[0], x[1])], lambda k,v: sum(v))
    for city, pop in sorted(result2.items(), key=lambda x: -x[1]):
        print(f"    {city:10s} → {pop}")

if __name__ == "__main__": main()
