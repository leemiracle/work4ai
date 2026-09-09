#!/usr/bin/env python3
"""
csdiy 毕业项目性能基准测试

测试 8 个核心项目的性能指标，产出对比报告。
参照：perf-程序员视角.md（先量后改）
"""
import time, sys, json, os, random, string, importlib.util

def import_project(name):
    """动态导入项目的 main.py（避免路径冲突）"""
    path = os.path.join(os.path.dirname(__file__), name, "main.py")
    spec = importlib.util.spec_from_file_location(f"tiny_{name}", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

results = {}

def bench(name, func, iterations=1000):
    """基准测试辅助函数"""
    start = time.perf_counter()
    result = func()
    elapsed = (time.perf_counter() - start) * 1000
    rate = iterations / (elapsed / 1000) if elapsed > 0 else float('inf')
    results[name] = {"time_ms": round(elapsed, 2), "ops": iterations, "ops_per_sec": round(rate)}
    print(f"  {name:40s} {elapsed:8.2f}ms  {rate:>10,.0f} ops/s")
    return result

def benchmark_tinydb_btree():
    """B+ 树 vs 线性扫描对比"""
    # 动态导入 btree.py
    btree_path = os.path.join(os.path.dirname(__file__), "tinydb", "btree.py")
    spec = importlib.util.spec_from_file_location("tiny_btree", btree_path)
    btree_mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(btree_mod)
    BPlusTree = btree_mod.BPlusTree

    tree = BPlusTree(order=100)
    keys = random.sample(range(1, 1000000), 5000)

    bench("tinydb/btree insert 5000", lambda: [tree.insert(k, f"val_{k}") for k in keys], 5000)

    search_keys = random.sample(keys, 1000)
    def search_btree():
        return [tree.search(k) for k in search_keys]
    bench("tinydb/btree search 1000", search_btree, 1000)

    start_k, end_k = min(keys), min(keys) + 100
    bench("tinydb/btree range_query 100", lambda: tree.range_query(start_k, end_k), 100)

    return tree.stats()

def benchmark_tinyjson():
    """tinyjson vs stdlib json"""
    import json as stdlib_json

    data = {"name": "benchmark", "values": list(range(100)), "nested": {"a": 1, "b": [1,2,3]}}
    json_str = stdlib_json.dumps(data)

    bench("stdlib json.loads ×1000", lambda: [stdlib_json.loads(json_str) for _ in range(1000)], 1000)
    bench("stdlib json.dumps ×1000", lambda: [stdlib_json.dumps(data) for _ in range(1000)], 1000)

def benchmark_tinycompress():
    """LZ77 压缩"""
    mod = import_project("tinycompress")
    compress, decompress = mod.compress, mod.decompress

    text = ("The quick brown fox jumps over the lazy dog. " * 100).encode()
    compressed = bench("tinycompress compress 4.5KB", lambda: compress(text), 1)
    bench("tinycompress decompress", lambda: decompress(compressed, len(text)), 1)

    ratio = len(text) / max(1, len(compressed))
    results["tinycompress ratio"] = {"ratio": round(ratio, 2)}

def benchmark_tinyregex():
    """正则匹配"""
    mod = import_project("tinyregex")
    search = mod.search

    bench("tinyregex match ×100", lambda: [search(r"\d+", "12345") for _ in range(100)], 100)
    bench("tinyregex complex ×100", lambda: [search(r"gr[ae]y", "gray") for _ in range(100)], 100)

def benchmark_tinyml():
    """ML 前向传播"""
    mod = import_project("tinyml")
    Value = mod.Value

    def compute():
        a = Value(2.0); b = Value(3.0)
        c = a * b + a; d = c.tanh()
        d.backward(); return d

    bench("tinyml forward+backward ×100", lambda: [compute() for _ in range(100)], 100)

def benchmark_tinysearch():
    """搜索引擎索引+搜索"""
    mod = import_project("tinysearch")
    InvertedIndex = mod.InvertedIndex
    Document = mod.Document

    idx = InvertedIndex()
    docs = [("d1","Hello World","hello world programming test"),
            ("d2","Python","python programming language"),
            ("d3","Database","sqlite btree storage wal"),
            ("d4","Network","tcp ip epoll concurrency"),
            ("d5","OS","virtual memory process kernel")] * 20

    bench("tinysearch index 100", lambda: [idx.add_document(Document(id=d[0], title=d[1], content=d[2])) for d in docs], 100)
    bench("tinysearch search ×100", lambda: [idx.search("programming database") for _ in range(100)], 100)

def benchmark_tinyencrypt():
    """SHA-256 哈希"""
    mod = import_project("tinyencrypt")
    SHA256 = mod.SHA256
    import hashlib

    data = b"benchmark test data for sha256 performance"
    bench("tinyencrypt SHA256 ×1000", lambda: [SHA256.hash(data) for _ in range(1000)], 1000)
    bench("hashlib sha256 ×1000", lambda: [hashlib.sha256(data).hexdigest() for _ in range(1000)], 1000)

def main():
    print("=" * 70)
    print("  csdiy 毕业项目性能基准测试")
    print("=" * 70)

    print("\n── 1. tinydb B+ 树 ──")
    stats = benchmark_tinydb_btree()
    print(f"  stats: {stats}")

    print("\n── 2. tinyjson ──")
    benchmark_tinyjson()

    print("\n── 3. tinycompress ──")
    benchmark_tinycompress()

    print("\n── 4. tinyregex ──")
    benchmark_tinyregex()

    print("\n── 5. tinyml ──")
    benchmark_tinyml()

    print("\n── 6. tinysearch ──")
    benchmark_tinysearch()

    print("\n── 7. tinyencrypt ──")
    benchmark_tinyencrypt()

    print("\n" + "=" * 70)
    print("  性能总结")
    print("=" * 70)
    for name, data in results.items():
        if "ops_per_sec" in data:
            print(f"  {name:40s} {data['ops_per_sec']:>10,.0f} ops/s  ({data['time_ms']:.1f}ms)")
        elif "ratio" in data:
            print(f"  {name:40s} {data['ratio']:>10.2f}x")

    # 保存结果
    output_path = os.path.join(os.path.dirname(__file__), "benchmark_results.json")
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\n  结果已保存: {output_path}")

if __name__ == "__main__":
    main()
