#!/usr/bin/env python3
"""
tinyalloc — 参照 dlmalloc/jemalloc 的内存分配器模拟

参照：dlmalloc (Doug Lea) / Redis zmalloc / jemalloc
csdiy 对应：csapp Ch9(虚拟内存/Malloc Lab) + os §一(OOM)

核心：free list + 分裂/合并 + first-fit
"""
import sys

class HeapBlock:
    def __init__(self, addr, size, free=True):
        self.addr = addr; self.size = size; self.free = free
        self.next = None; self.prev = None

class TinyAlloc:
    """
    简化版 malloc/free（参照 dlmalloc free list + first-fit）

    Malloc Lab 核心策略：
    1. 维护空闲链表
    2. malloc：first-fit 找到 >= size 的块 → 分裂
    3. free：标记为空闲 → 和相邻空闲块合并
    """
    def __init__(self, total=65536):
        self.total = total
        self.head = HeapBlock(0, total)
        self.stats = {"mallocs": 0, "frees": 0, "splits": 0, "coalesces": 0}

    def malloc(self, size):
        size = (size + 7) & ~7  # 8 字节对齐（参照 csapp Ch9）
        block = self._find_fit(size)
        if not block:
            return None  # OOM
        if block.size > size + 16:  # 可分裂
            new = HeapBlock(block.addr + size, block.size - size)
            new.next = block.next; new.prev = block
            if block.next: block.next.prev = new
            block.next = new; block.size = size
            self.stats["splits"] += 1
        block.free = False
        self.stats["mallocs"] += 1
        return block.addr

    def free(self, addr):
        block = self._find_block(addr)
        if not block or not block.free:
            return False
        block.free = True
        self.stats["frees"] += 1
        # 合并相邻空闲块（参照 Malloc Lab coalesce）
        if block.next and block.next.free:
            block.size += block.next.size
            block.next = block.next.next
            if block.next: block.next.prev = block
            self.stats["coalesces"] += 1
        if block.prev and block.prev.free:
            block.prev.size += block.size
            block.prev.next = block.next
            if block.next: block.next.prev = block.prev
            self.stats["coalesces"] += 1
        return True

    def _find_fit(self, size):
        """First-fit（参照 Malloc Lab）"""
        b = self.head
        while b:
            if b.free and b.size >= size:
                return b
            b = b.next
        return None

    def _find_block(self, addr):
        b = self.head
        while b:
            if b.addr == addr: return b
            b = b.next
        return None

    def dump(self):
        b = self.head; lines = []
        while b:
            status = "FREE" if b.free else "USED"
            lines.append(f"  [{b.addr:#06x} - {b.addr+b.size:#06x}] {b.size:>6}B  {status}")
            b = b.next
        return "\n".join(lines)

def main():
    alloc = TinyAlloc(65536)
    print("tinyalloc — 内存分配器（参照 dlmalloc）\n")

    # 分配
    a = alloc.malloc(1024)
    b = alloc.malloc(2048)
    c = alloc.malloc(512)
    d = alloc.malloc(4096)
    print(f"malloc(1024)  → {a:#x}")
    print(f"malloc(2048)  → {b:#x}")
    print(f"malloc(512)   → {c:#x}")
    print(f"malloc(4096)  → {d:#x}")

    # 释放 + 合并
    print(f"\nfree({b:#x}) → 合并检查")
    alloc.free(b)
    print(f"free({c:#x}) → 触发合并")
    alloc.free(c)  # 应该和 b 合并

    # 再分配（应复用合并后的空间）
    e = alloc.malloc(1500)
    print(f"\nmalloc(1500)  → {e:#x} (复用已合并空间)")
    print(f"\n{alloc.dump()}")
    print(f"\nstats: {alloc.stats}")

if __name__ == "__main__": main()
