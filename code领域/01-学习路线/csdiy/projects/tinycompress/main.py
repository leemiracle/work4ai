#!/usr/bin/env python3
"""
tinycompress — 参照 gzip/zstd 的 LZ77 压缩引擎

参照：gzip(DEFLATE=LZ77+Huffman) + zstd
csdiy 对应：csapp Ch2(位级操作) + perf(压缩性能)

核心：LZ77 滑动窗口 + 长度-距离编码
DEFLATE = LZ77 + Huffman，本实现只做 LZ77 部分（简化）
"""
import struct, sys, time
from typing import Optional

WINDOW_SIZE = 32768    # 滑动窗口（参照 gzip 的 32KB 窗口）
MIN_MATCH = 3          # 最小匹配长度
MAX_MATCH = 258        # 最大匹配长度（参照 gzip）

def compress(data: bytes) -> bytes:
    """
    LZ77 压缩（参照 DEFLATE 的 LZ77 部分）

    输出格式：token 序列
    - literal: [0x00][byte]（1 字节标记 + 1 字节数据）
    - match: [距离高2位|长度低6位][距离低8位]
      距离: 1-32768，长度: 3-258
    """
    output = bytearray()
    pos = 0
    n = len(data)

    while pos < n:
        # 在滑动窗口中找最长匹配
        best_len, best_dist = find_match(data, pos)

        if best_len >= MIN_MATCH:
            # 输出 match token
            length = best_len - MIN_MATCH  # 0-255 → 实际 3-258
            if length > 255: length = 255  # 简化：最大 258
            # 编码：(dist>>8) << 6 | (length-MIN_MATCH & 0x3F)... 简化用 2 字节
            output.append(0x01)  # match 标记
            output.extend(struct.pack(">HH", best_dist, best_len))
            pos += best_len
        else:
            # 输出 literal
            output.append(0x00)  # literal 标记
            output.append(data[pos])
            pos += 1

    return bytes(output)

def decompress(data: bytes, original_size: int) -> bytes:
    """LZ77 解压"""
    output = bytearray()
    pos = 0
    while pos < len(data) and len(output) < original_size:
        flag = data[pos]; pos += 1
        if flag == 0x00:
            # literal
            output.append(data[pos]); pos += 1
        elif flag == 0x01:
            # match
            dist, length = struct.unpack(">HH", data[pos:pos+4])
            pos += 4
            start = len(output) - dist
            for i in range(length):
                output.append(output[start + i])
    return bytes(output)

def find_match(data: bytes, pos: int) -> tuple[int, int]:
    """
    在滑动窗口中查找最长匹配（参照 gzip 的 lazy matching）

    使用简单的暴力搜索（真实 gzip 用 hash table 加速）。
    """
    n = len(data)
    window_start = max(0, pos - WINDOW_SIZE)
    best_len = 0
    best_dist = 0

    # 暴力搜索窗口内所有位置（简化版，真实用 hash chain）
    for start in range(window_start, pos):
        # 计算匹配长度
        match_len = 0
        while (match_len < MAX_MATCH and
               pos + match_len < n and
               data[start + match_len] == data[pos + match_len]):
            match_len += 1

        if match_len >= MIN_MATCH and match_len > best_len:
            best_len = match_len
            best_dist = pos - start
            if match_len >= MAX_MATCH:
                break  # 已经是最大匹配

    return best_len, best_dist

def compress_ratio(original: bytes, compressed: bytes) -> float:
    """压缩率"""
    return len(original) / max(1, len(compressed))

def benchmark(data: bytes, label: str = ""):
    """压缩+解压基准测试（参照 perf 精读的先量后改）"""
    print(f"\n── {label or f'{len(data)} bytes'} ──")

    t1 = time.perf_counter()
    compressed = compress(data)
    t2 = time.perf_counter()
    ratio = compress_ratio(data, compressed)
    print(f"  原始: {len(data):>8} bytes")
    print(f"  压缩: {len(compressed):>8} bytes  ({t2-t1:.3f}s)")
    print(f"  比率: {ratio:.2f}x")

    t3 = time.perf_counter()
    decompressed = decompress(compressed, len(data))
    t4 = time.perf_counter()
    ok = data == decompressed
    print(f"  解压: {len(decompressed):>8} bytes  ({t4-t3:.3f}s)")
    print(f"  校验: {'✅ PASS' if ok else '❌ FAIL'}")
    return ok

def main():
    print("tinycompress — LZ77 压缩引擎\n")

    # Test 1: 重复文本（高压缩率）
    text1 = ("Hello World! " * 100).encode()
    benchmark(text1, "重复文本 100x")

    # Test 2: 随机数据（低压缩率）
    import random; random.seed(42)
    text2 = bytes(random.randint(0,255) for _ in range(1000))
    benchmark(text2, "随机数据 1KB")

    # Test 3: 源代码（中等压缩率）
    code = b''
    code += b'def fibonacci(n):\n'
    code += b'    if n <= 1: return n\n'
    code += b'    return fibonacci(n-1) + fibonacci(n-2)\n'
    code *= 50
    benchmark(code, "源代码重复 50x")

    # Test 4: 空数据
    benchmark(b'', "空数据")

    # Test 5: 单字节
    benchmark(b'A', "单字节")

    if len(sys.argv) > 2:
        cmd = sys.argv[1]
        fname = sys.argv[2]
        data = open(fname, 'rb').read()
        if cmd == "compress":
            out = compress(data)
            open(fname + ".tc", 'wb').write(out)
            print(f"\n{fname} → {fname}.tc  ({len(data)} → {len(out)}, {compress_ratio(data,out):.2f}x)")
        elif cmd == "decompress":
            compressed = open(fname, 'rb').read()
            out = decompress(compressed, len(compressed) * 10)  # 猜测原始大小
            open(fname.replace('.tc', ''), 'wb').write(out)
            print(f"\n{fname} → {fname.replace('.tc','')}")

if __name__ == "__main__":
    main()
