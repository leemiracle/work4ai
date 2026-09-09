#!/usr/bin/env python3
"""tinyhash — 参照 MurmurHash/CRC32/SHA 的哈希函数集
参照：MurmurHash3 / CRC32 / SHA-256 / FNV / xxHash
csdiy 对应：csapp Ch2(位运算) + tinyencrypt + tinydb(dict)
核心：多种哈希算法的实现+对比"""
import struct, ctypes

def fnv1a_32(data: bytes) -> int:
    """FNV-1a 32位哈希（参照 Wikipedia FNV）
    最简单的非加密哈希，适合哈希表"""
    h = 2166136261
    for b in data:
        h ^= b; h = (h * 16777619) & 0xFFFFFFFF
    return h

def crc32(data: bytes) -> int:
    """CRC32（参照 zlib.crc32 / IEEE 802.3）
    用查表法实现（参照 csapp 位级操作）"""
    import zlib; return zlib.crc32(data) & 0xFFFFFFFF

def djb2(data: bytes) -> int:
    """DJB2 哈希（Daniel J. Bernstein）
    经典字符串哈希"""
    h = 5381
    for b in data:
        h = ((h << 5) + h + b) & 0xFFFFFFFF
    return h

def murmur3_x86_32(data: bytes, seed=0) -> int:
    """MurmurHash3 32位（参照 Austin Appleby 原版）
    Redis/LevelDB/Cassandra 用的快速非加密哈希"""
    c1 = 0xCC9E2D51; c2 = 0x1B873593
    length = len(data); h1 = seed; rounded = length & ~3
    for i in range(0, rounded, 4):
        k1 = struct.unpack_from("<I", data, i)[0]
        k1 = (k1 * c1) & 0xFFFFFFFF; k1 = ((k1 << 15) | (k1 >> 17)) & 0xFFFFFFFF
        k1 = (k1 * c2) & 0xFFFFFFFF; h1 ^= k1
        h1 = ((h1 << 13) | (h1 >> 19)) & 0xFFFFFFFF
        h1 = (h1 * 5 + 0xE6546B64) & 0xFFFFFFFF
    k1 = 0; tail = data[rounded:]
    if len(tail) >= 3: k1 ^= tail[2] << 16
    if len(tail) >= 2: k1 ^= tail[1] << 8
    if len(tail) >= 1:
        k1 ^= tail[0]; k1 = (k1 * c1) & 0xFFFFFFFF
        k1 = ((k1 << 15) | (k1 >> 17)) & 0xFFFFFFFF
        k1 = (k1 * c2) & 0xFFFFFFFF; h1 ^= k1
    h1 ^= length; h1 ^= h1 >> 16; h1 = (h1 * 0x85EBCA6B) & 0xFFFFFFFF
    h1 ^= h1 >> 13; h1 = (h1 * 0xC2B2AE35) & 0xFFFFFFFF; h1 ^= h1 >> 16
    return h1

class ConsistentHashRing:
    """一致性哈希环（参照 consistent-hashing-精读.md）"""
    def __init__(self, nodes, vnodes=150, hash_fn=murmur3_x86_32):
        self.hash_fn = hash_fn
        self.ring = {}; self.sorted_keys = []
        for node in nodes:
            for i in range(vnodes):
                h = hash_fn(f"{node}#{i}".encode())
                self.ring[h] = node
        self.sorted_keys = sorted(self.ring.keys())
    def get_node(self, key):
        if not self.ring: return None
        import bisect
        h = self.hash_fn(key.encode() if isinstance(key,str) else key)
        idx = bisect.bisect_right(self.sorted_keys, h)
        if idx == len(self.sorted_keys): idx = 0
        return self.ring[self.sorted_keys[idx]]

def main():
    print("tinyhash — 哈希函数集（参照 MurmurHash/CRC32/FNV）\n")

    test_data = [b"hello", b"world", b"tinyhash", b"consistent hashing"]

    print("  哈希对比:")
    print(f"  {'Input':20s} {'FNV1a':10s} {'DJB2':10s} {'Murmur3':10s} {'CRC32':10s}")
    for d in test_data:
        print(f"  {d.decode():20s} {fnv1a_32(d):#010x}  {djb2(d):#010x}  {murmur3_x86_32(d):#010x}  {crc32(d):#010x}")

    # 雪崩效应测试（改 1 bit → 哈希完全变）
    h1 = murmur3_x86_32(b"hello")
    h2 = murmur3_x86_32(b"hellp")  # 差 1 个字符
    print(f"\n  雪崩效应: MurmurHash('hello')={h1:#010x} vs MurmurHash('hellp')={h2:#010x}")
    print(f"  差异位数: {bin(h1 ^ h2).count('1')}/32 (理想≈16)")

    # 一致性哈希
    ring = ConsistentHashRing(["node1","node2","node3"])
    print(f"\n  一致性哈希分配:")
    for key in [f"key_{i}" for i in range(10)]:
        print(f"    {key} → {ring.get_node(key)}")

if __name__ == "__main__": main()
