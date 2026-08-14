"""
15-213 CSAPP: Computer Systems (CMU — Bryant & O'Hallaron)
================================================
覆盖主题（对应 chapter）：
- Ch 6: Memory Hierarchy — L1/L2 cache 模拟器（direct-mapped + set-assoc）
- Ch 9: Virtual Memory — 隐式空闲链表 malloc + 地址翻译 + TLB
- Ch 8: 异常控制流基础（信号/进程概念）

核心教材/论文：
- Bryant & O'Hallaron "Computer Systems: A Programmer's Perspective" 3rd ed
- Smith "Cache Memories" 1982 IEEE（缓存设计基础）
- Knuth "The Art of Computer Programming Vol 1" §2.5（首次适应分配）

本文件实现：
- Direct-mapped / 2-way / 4-way set associative cache 模拟
- 隐式空闲链表 malloc（first-fit + coalescing）
- 虚拟地址翻译（flat page table + TLB）

运行：
    python3 csapp.py
"""
from __future__ import annotations
import math
from dataclasses import dataclass, field
from collections import OrderedDict

# ============ 1. Cache Simulator ============

@dataclass
class CacheLine:
    valid: bool = False
    tag: int = 0
    last_used: int = 0  # for LRU

class Cache:
    """Set-associative cache simulator."""

    def __init__(self, sets: int, ways: int, block_size: int):
        self.sets = sets
        self.ways = ways
        self.block_size = block_size
        # each set = list of `ways` lines
        self.table = [[CacheLine() for _ in range(ways)] for _ in range(sets)]
        self.clock = 0
        self.hits = 0
        self.misses = 0

    def _addr_to_index_tag(self, addr: int):
        offset_bits = int(math.log2(self.block_size))
        index_bits = int(math.log2(self.sets))
        offset = addr & (self.block_size - 1)
        index = (addr >> offset_bits) & (self.sets - 1)
        tag = addr >> (offset_bits + index_bits)
        return index, tag

    def access(self, addr: int) -> bool:
        self.clock += 1
        idx, tag = self._addr_to_index_tag(addr)
        lines = self.table[idx]
        # check hit
        for line in lines:
            if line.valid and line.tag == tag:
                line.last_used = self.clock
                self.hits += 1
                return True
        # miss — find slot (empty or LRU)
        self.misses += 1
        victim = self._victim(lines)
        victim.valid = True
        victim.tag = tag
        victim.last_used = self.clock
        return False

    def hit_rate(self):
        total = self.hits + self.misses
        return self.hits / max(total, 1)

    @staticmethod
    def _victim(lines):
        """Select victim line: prefer invalid slot, else LRU among valid."""
        invalid = [l for l in lines if not l.valid]
        if invalid:
            return invalid[0]
        return min((l for l in lines if l.valid), key=lambda l: l.last_used)


def simulate_matrix_traversal(cache: Cache, n: int, row_major=True):
    """Access an n×n matrix in row-major or column-major order."""
    # 4 bytes per int, contiguous layout
    for i in range(n):
        for j in range(n):
            if row_major:
                addr = (i * n + j) * 4
            else:
                addr = (j * n + i) * 4
            cache.access(addr)


# ============ 2. Implicit Free List Malloc ============

@dataclass
class Block:
    size: int          # payload size
    free: bool = True
    payload: bytes = b''
    # header/footer: size | free bit packed in real impl

class Heap:
    """Implicit free list allocator (first-fit + coalescing)."""

    def __init__(self, total_size: int = 4096):
        self.blocks: list[Block] = [Block(size=total_size, free=True)]
        self.total = total_size
        self.allocated = 0

    def malloc(self, size: int) -> int:
        """Allocate, return block index."""
        # first-fit
        for i, b in enumerate(self.blocks):
            if b.free and b.size >= size:
                if b.size > size + 8:  # split threshold
                    remainder = Block(size=b.size - size, free=True)
                    b.size = size
                    b.free = False
                    self.blocks.insert(i + 1, remainder)
                else:
                    b.free = False
                b.payload = b'\x00' * size
                self.allocated += size
                return i
        raise MemoryError(f"malloc({size}) failed — fragmentation or OOM")

    def free(self, idx: int):
        self.blocks[idx].free = True
        self.allocated -= self.blocks[idx].size
        self._coalesce(idx)

    def _coalesce(self, idx: int):
        # merge with next if free
        if idx + 1 < len(self.blocks) and self.blocks[idx+1].free:
            self.blocks[idx].size += self.blocks[idx+1].size
            del self.blocks[idx+1]
        # merge with prev if free
        if idx > 0 and self.blocks[idx-1].free:
            self.blocks[idx-1].size += self.blocks[idx].size
            del self.blocks[idx]

    def fragmentation(self) -> float:
        """External fragmentation metric."""
        free_total = sum(b.size for b in self.blocks if b.free)
        if free_total == 0:
            return 0.0
        max_free = max((b.size for b in self.blocks if b.free), default=0)
        return 1.0 - (max_free / free_total) if free_total > 0 else 0.0


# ============ 3. Virtual Address Translation + TLB ============

class VirtualMemory:
    """Flat page table + TLB simulator."""

    def __init__(self, vaddr_bits=16, page_size=256, tlb_entries=4):
        self.page_size = page_size
        self.offset_bits = int(math.log2(page_size))
        self.vpn_bits = vaddr_bits - self.offset_bits
        # page table (flat for simplicity): vpn → pfn
        self.page_table: dict[int, int] = {}
        self.used_pfn = 0
        # TLB (LRU)
        self.tlb_size = tlb_entries
        self.tlb: OrderedDict[int, int] = OrderedDict()
        self.tlb_hits = 0
        self.tlb_misses = 0

    def map(self, vpn: int):
        """Allocate a physical frame for vpn."""
        if vpn not in self.page_table:
            self.page_table[vpn] = self.used_pfn
            self.used_pfn += 1

    def translate(self, vaddr: int) -> int:
        offset = vaddr & (self.page_size - 1)
        vpn = vaddr >> self.offset_bits
        # check TLB
        if vpn in self.tlb:
            self.tlb.move_to_end(vpn)
            self.tlb_hits += 1
            pfn = self.tlb[vpn]
        else:
            self.tlb_misses += 1
            # page table walk
            if vpn not in self.page_table:
                self.map(vpn)
            pfn = self.page_table[vpn]
            self.tlb[vpn] = pfn
            if len(self.tlb) > self.tlb_size:
                self.tlb.popitem(last=False)  # evict LRU
        return (pfn << self.offset_bits) | offset


# ============ Demo ============

def demo():
    print("=" * 60)
    print("15-213 CSAPP: Cache, Malloc, Virtual Memory")
    print("=" * 60)

    # --- 1. Cache ---
    print("\n📋 1. Cache Simulation — Matrix Traversal")
    n = 32  # 32x32 matrix

    configs = [
        ("Direct-mapped (1-way)", 1),
        ("2-way set assoc", 2),
        ("4-way set assoc", 4),
    ]
    print(f"\n   Matrix: {n}×{n} × 4 bytes = {n*n*4} bytes")
    for name, ways in configs:
        for mode, row_major in [("row-major", True), ("col-major", False)]:
            c = Cache(sets=8, ways=ways, block_size=16)
            simulate_matrix_traversal(c, n, row_major)
            print(f"   {name:28s} {mode:12s} hit_rate={c.hit_rate():.1%}")
    print("   💡 反直觉：行优先 ~75% 命中，列优先 ~0% 命中（尽管 cache 相同！）")

    print("\n   b) Set Conflict — associativity benefit")
    # 3 addresses all alias to set 0; access pattern with temporal locality
    for name, ways in configs:
        c = Cache(sets=4, ways=ways, block_size=4)
        for _ in range(100):
            c.access(0)    # hot — accessed twice per cycle
            c.access(64)   # hot
            c.access(0)    # hot again
            c.access(128)  # cold — accessed once per cycle
        print(f"   {name:28s} conflict     hit_rate={c.hit_rate():.1%}")
    print("   💡 组相联解决 conflict miss：1-way 0% → 2-way ~50% → 4-way ~99%")

    # --- 2. Malloc ---
    print("\n📋 2. Implicit Free List Malloc")
    heap = Heap(total_size=256)
    indices = {}
    sizes = [('a', 64), ('b', 32), ('c', 64), ('d', 32)]
    for name, sz in sizes:
        indices[name] = heap.malloc(sz)
        print(f"   malloc({name},{sz}) → block {indices[name]}")

    print(f"   Allocated: {heap.allocated}/{heap.total}, frag={heap.fragmentation():.0%}")

    print("   free(b) and free(d)...")
    heap.free(indices['b'])
    heap.free(indices['d'])
    print(f"   After free: {len(heap.blocks)} blocks, frag={heap.fragmentation():.0%}")

    # Try to allocate 100 (won't fit in either hole → coalesce test)
    try:
        heap.malloc(100)
        print("   malloc(100) succeeded (coalescing worked)")
    except MemoryError:
        print(f"   malloc(100) FAILED — fragmentation! free={heap.total - heap.allocated}")

    # --- 3. Virtual Memory + TLB ---
    print("\n📋 3. Virtual Address Translation + TLB")
    vm = VirtualMemory(vaddr_bits=16, page_size=256, tlb_entries=4)
    # Access pattern: sequential (good locality) vs random
    sequential = list(range(0, 256*20, 4))
    for addr in sequential:
        vm.translate(addr)
    print(f"   Sequential access ({len(sequential)} addrs): "
          f"TLB hit_rate={vm.tlb_hits/(vm.tlb_hits+vm.tlb_misses):.1%}")

    vm2 = VirtualMemory(vaddr_bits=16, page_size=256, tlb_entries=4)
    random_addrs = [(i * 256 + j) for i in range(20) for j in range(0, 256, 60)]
    for addr in random_addrs:
        vm2.translate(addr)
    print(f"   Strided access ({len(random_addrs)} addrs): "
          f"TLB hit_rate={vm2.tlb_hits/(vm2.tlb_hits+vm2.tlb_misses):.1%}")
    print("   💡 TLB 仅 4 entries，strided 跳页 → thrashing → hit rate 暴跌")

    print("\n✅ 15-213 CSAPP 完成！")
    print("   覆盖：cache 设计 / malloc 分配 / 虚拟内存翻译")


if __name__ == "__main__":
    demo()
