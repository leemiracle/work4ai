"""
6.S081/6.828 Operating Systems（MIT, xv6）
================================================
覆盖主题：
- xv6 风格 inode 文件系统（Lab File System）
- 多级页表 + TLB 模拟（Lab pgtbl）
- CFS 风格调度器（Lab Multithreading）
- Trap/syscall 模拟（Lab Traps）

核心教材/论文（经典，无 arXiv ID）：
- xv6: Corbet, Cox, Kaashoek, Morris "xv6: a simple, Unix-like teaching operating system"
- Ritchie & Thompson 1974 "The UNIX Time-Sharing System" CACM
- Bovet & Cesati "Understanding the Linux Kernel" Ch 3-7
- Molnar 2007 "Linux 2.6.23 CFS design notes" (CFS design)

本文件实现：
- inode 块映射（直接块 + 间接块）+ 文件读写
- 4 级页表地址翻译 + TLB 缓存
- CFS 红黑树模拟（nice 影响时间片）
- Trap vector + syscall 分发

运行：
    python os.py
"""
from __future__ import annotations
import math
from dataclasses import dataclass, field
from collections import OrderedDict


# ============ 1. xv6 Inode FS ============

@dataclass
class Inode:
    """xv6 dinode: 12 direct + 1 single indirect + 1 double indirect block"""
    inum: int
    type: str = "file"   # file | dir
    size: int = 0
    direct: list[int] = field(default_factory=lambda: [-1]*12)
    indirect: int = -1   # 间接块号
    dindirect: int = -1  # 二级间接块号


class xv6FS:
    """简化 xv6 文件系统模拟"""
    def __init__(self, total_blocks: int = 1000, block_size: int = 512,
                 ptrs_per_block: int = 128):
        self.block_size = block_size
        self.ptrs_per_block = ptrs_per_block
        self.free_blocks = list(range(1, total_blocks))
        self.data = {}  # block_num -> bytes/list
        self.inodes: dict[int, Inode] = {}
        self.next_inum = 1
        # 模拟间接块存储（block -> [ptr, ptr, ...]）
        self.indirect_blocks: dict[int, list[int]] = {}

    def alloc_block(self) -> int:
        return self.free_blocks.pop(0) if self.free_blocks else -1

    def create(self, inum: int = None) -> Inode:
        inum = inum or self.next_inum
        self.next_inum = max(self.next_inum, inum) + 1
        inode = Inode(inum=inum)
        self.inodes[inum] = inode
        return inode

    def write(self, inum: int, data: bytes) -> int:
        """写入数据，分配块。返回写入字节数。"""
        inode = self.inodes[inum]
        n_blocks = math.ceil(len(data) / self.block_size)
        for i in range(n_blocks):
            bno = self.alloc_block()
            chunk = data[i*self.block_size:(i+1)*self.block_size]
            self.data[bno] = chunk
            self._map_block(inode, i, bno)
        inode.size = len(data)
        return len(data)

    def _map_block(self, inode: Inode, logical_idx: int, bno: int):
        direct_cap = 12
        indirect_cap = direct_cap + self.ptrs_per_block
        if logical_idx < direct_cap:
            inode.direct[logical_idx] = bno
        elif logical_idx < indirect_cap:
            if inode.indirect == -1:
                inode.indirect = self.alloc_block()
                self.indirect_blocks[inode.indirect] = [-1]*self.ptrs_per_block
            self.indirect_blocks[inode.indirect][logical_idx - direct_cap] = bno
        else:
            # 双重间接（简化）
            if inode.dindirect == -1:
                inode.dindirect = self.alloc_block()
                self.indirect_blocks[inode.dindirect] = [-1]*self.ptrs_per_block
            idx2 = logical_idx - indirect_cap
            outer = idx2 // self.ptrs_per_block
            inner = idx2 % self.ptrs_per_block
            key = (inode.dindirect, outer)
            if key not in self.indirect_blocks:
                inner_block = self.alloc_block()
                self.indirect_blocks[(inode.dindirect, outer)] = inner_block
                self.indirect_blocks[inner_block] = [-1]*self.ptrs_per_block
            inner_b = self.indirect_blocks[(inode.dindirect, outer)]
            self.indirect_blocks[inner_b][inner] = bno

    def read(self, inum: int) -> bytes:
        inode = self.inodes[inum]
        result = b""
        n_blocks = math.ceil(inode.size / self.block_size)
        for i in range(n_blocks):
            bno = self._get_block(inode, i)
            if bno >= 0 and bno in self.data:
                result += self.data[bno]
        return result[:inode.size]

    def _get_block(self, inode, logical_idx):
        direct_cap = 12
        indirect_cap = direct_cap + self.ptrs_per_block
        if logical_idx < direct_cap:
            return inode.direct[logical_idx]
        elif logical_idx < indirect_cap:
            if inode.indirect == -1:
                return -1
            return self.indirect_blocks[inode.indirect][logical_idx - direct_cap]
        else:
            # 双重间接：镜像 _map_block 的三层逻辑
            if inode.dindirect == -1:
                return -1
            idx2 = logical_idx - indirect_cap
            outer = idx2 // self.ptrs_per_block
            inner = idx2 % self.ptrs_per_block
            key = (inode.dindirect, outer)
            if key not in self.indirect_blocks:
                return -1
            inner_b = self.indirect_blocks[key]
            return self.indirect_blocks[inner_b][inner]


# ============ 2. Multi-level Page Table + TLB ============

class TLB:
    """Translation Lookaside Buffer"""
    def __init__(self, size=64):
        self.size = size
        self.entries: OrderedDict[int, int] = OrderedDict()  # va -> pa
        self.hits = 0
        self.misses = 0

    def lookup(self, va):
        if va in self.entries:
            self.hits += 1
            self.entries.move_to_end(va)
            return self.entries[va]
        self.misses += 1
        return None

    def insert(self, va, pa):
        if va in self.entries:
            self.entries.move_to_end(va)
        self.entries[va] = pa
        if len(self.entries) > self.size:
            self.entries.popitem(last=False)  # LRU evict


class PageTable:
    """单级页表模拟（flat dict）。模拟 TLB + page table walk 的行为，
    但实际存储为 va→pa 的扁平字典（非真正的 4 级页表树）。"""
    def __init__(self):
        self.phys_pages = {}  # frame -> data (模拟)
        self.P = 1 << 12  # 4KB page
        self.next_frame = 0x10000

    def map(self, va: int, pa: int, level_tables: dict):
        """建立 va→pa 映射（简化：直接存）。"""
        level_tables[va] = pa

    def walk(self, va: int, level_tables: dict, tlb: TLB) -> int:
        """模拟 4 级页表 walk + TLB。"""
        # 先查 TLB
        pa = tlb.lookup(va)
        if pa is not None:
            return pa
        # 4 级页表 walk
        offset = va & 0xFFF
        vpn = va >> 12
        # 模拟 4 次内存访问
        if vpn << 12 in level_tables:
            pa = level_tables[vpn << 12] | offset
            tlb.insert(va, pa)
            return pa
        return None  # fault


# ============ 3. CFS Scheduler ============

@dataclass
class CfsTask:
    pid: int
    nice: int = 0       # -20 to 19
    vruntime: float = 0  # 虚拟运行时间
    weight: int = 0

    def __post_init__(self):
        # nice 0 = weight 1024; 每 nice 差 ≈ 1.25x (δ=10%)
        self.weight = int(1024 * (1.25 ** (-self.nice)))


class CFSScheduler:
    """CFS: 按 vruntime 排序调度。低 nice = 高权重 = vruntime 增长慢。"""
    def __init__(self, min_gran=1.0, target_latency=6.0):
        self.min_gran = min_gran
        self.target_latency = target_latency
        self.runqueue: list[CfsTask] = []

    def add(self, task: CfsTask):
        self.runqueue.append(task)

    def timeslice(self, task: CfsTask) -> float:
        total_weight = sum(t.weight for t in self.runqueue) or 1
        n = len(self.runqueue)
        sched_period = max(self.target_latency, self.min_gran * n)
        return sched_period * task.weight / total_weight

    def run_step(self, task: CfsTask, real_time: float):
        slice_t = self.timeslice(task)
        # vruntime 增长 = real_time * (1024 / weight)
        task.vruntime += real_time * (1024 / task.weight)
        return slice_t

    def pick_next(self) -> CfsTask | None:
        if not self.runqueue:
            return None
        return min(self.runqueue, key=lambda t: t.vruntime)


# ============ 4. Trap / Syscall ============

class TrapSimulator:
    """xv6 风格 trap vector + syscall 分发"""
    def __init__(self):
        self.syscall_table = {
            1: self._sys_read,
            2: self._sys_write,
            3: self._sys_exit,
            4: self._sys_fork,
            5: self._sys_exec,
        }
        self.log = []

    def handle_trap(self, syscall_num: int, args: tuple = ()):
        self.log.append(f"trap: syscall #{syscall_num} args={args}")
        handler = self.syscall_table.get(syscall_num)
        if handler is None:
            self.log.append(f"  → UNKNOWN syscall {syscall_num}, killing process")
            return -1
        return handler(args)

    def _sys_read(self, args):
        self.log.append(f"  → read(fd={args[0]}, buf, n={args[1]})")
        return args[1]  # 返回读取字节数

    def _sys_write(self, args):
        self.log.append(f"  → write(fd={args[0]}, buf, n={args[1]})")
        return args[1]

    def _sys_exit(self, args):
        self.log.append(f"  → exit(status={args[0]})")
        return 0

    def _sys_fork(self, args):
        self.log.append("  → fork() → child pid=1234")
        return 1234

    def _sys_exec(self, args):
        self.log.append(f"  → exec(path='{args[0]}')")
        return 0


# ============ Demo ============

def demo():
    print("=" * 65)
    print("6.S081 OS: xv6 inode FS / Page Table / CFS / Trap")
    print("=" * 65)

    # --- Inode FS ---
    print("\n📋 1. xv6 Inode 文件系统 (12 direct + 1 indirect + 1 dindirect)")
    fs = xv6FS(total_blocks=10000, block_size=64, ptrs_per_block=16)
    inode = fs.create(inum=1)
    # 写入超过直接+间接块（(12+16)*64=1792）进入双重间接区域
    data = bytes(range(256)) * 10  # 2560 bytes → 40 blocks (12 direct + 16 indirect + 12 double-indirect)
    written = fs.write(1, data)
    print(f"  写入 {written} bytes → 需要 {math.ceil(written/64)} blocks")
    print(f"    (12 direct=768B + 16 indirect=1024B + 12 double-indirect=768B = 2560B)")
    print(f"  inode: direct={inode.direct[:5]}... indirect={inode.indirect}, dindirect={inode.dindirect}")
    # 验证读回
    read_back = fs.read(1)
    assert read_back == data, "读写不一致!"
    print(f"  读回 {len(read_back)} bytes, 数据一致性 ✓")

    # --- Page Table + TLB ---
    print("\n📋 2. 多级页表 + TLB")
    tlb = TLB(size=8)
    tables = {}
    pt = PageTable()
    # 映射一些虚拟页
    for i in range(20):
        va = i << 12
        pa = (0x80000 + i) << 12
        pt.map(va, pa, tables)
    # 访问模式：局部性（反复访问前 5 页）
    accesses = []
    for _ in range(3):
        for i in range(5):
            accesses.append(i << 12)
    # 加一些随机远距离访问
    for i in [10, 11, 15, 10, 11]:
        accesses.append(i << 12)
    print(f"  TLB size={tlb.size}, 访问序列长度={len(accesses)}")
    for va in accesses:
        pt.walk(va, tables, tlb)
    hit_rate = tlb.hits / (tlb.hits + tlb.misses) * 100
    print(f"  TLB hits={tlb.hits}, misses={tlb.misses}, hit rate={hit_rate:.1f}%")
    print(f"  → 局部性让小 TLB 也能高命中率。")

    # --- CFS ---
    print("\n📋 3. CFS 调度器 (nice 影响时间片)")
    sched = CFSScheduler(min_gran=1.0, target_latency=6.0)
    tasks = [
        CfsTask(1, nice=0),
        CfsTask(2, nice=-5),
        CfsTask(3, nice=5),
    ]
    for t in tasks:
        sched.add(t)
    print(f"  3 任务: PID1(nice=0), PID2(nice=-5), PID3(nice=+5)")
    print(f"  {'PID':<5}{'nice':<6}{'weight':<8}{'timeslice':<10}{'vruntime增速':<12}")
    for t in tasks:
        sl = sched.timeslice(t)
        rate = 1024 / t.weight
        print(f"  {t.pid:<5}{t.nice:<6}{t.weight:<8}{sl:<10.2f}{rate:<12.3f}")
    print("  模拟 10 步调度:")
    for step in range(10):
        t = sched.pick_next()
        if t is None:
            break
        sl = sched.run_step(t, sched.timeslice(t))
        print(f"    step {step}: run PID{t.pid}, vruntime={t.vruntime:.2f}, slice={sl:.2f}")

    # --- Trap ---
    print("\n📋 4. Trap / Syscall 分发")
    trap = TrapSimulator()
    syscalls = [(2, (1, 100)), (1, (0, 50)), (4, ()), (3, (0,)), (99, ())]
    for num, args in syscalls:
        ret = trap.handle_trap(num, args)
        print(f"  syscall #{num} → return {ret}")
    print(f"  trap 日志:")
    for line in trap.log:
        print(f"    {line}")

    # --- 反直觉发现 ---
    print("\n" + "=" * 65)
    print("💡 反直觉发现：TLB 容量极小但命中率极高（空间/时间局部性）")
    print("=" * 65)
    for tlb_size in [4, 8, 16, 32, 64]:
        tlb2 = TLB(size=tlb_size)
        tables2 = {}
        for i in range(1000):
            pt.map(i << 12, (0x80000+i) << 12, tables2)
        # 模拟循环访问 working set
        ws = 8  # working set 大小
        for _ in range(500):
            for i in range(ws):
                pt.walk(i << 12, tables2, tlb2)
        hr = tlb2.hits / (tlb2.hits + tlb2.misses) * 100
        print(f"  TLB={tlb_size:>2} entries, working_set={ws} pages: "
              f"hits={tlb2.hits}, hit_rate={hr:.1f}%")
    print("  → 只要 TLB >= working set，命中率接近 100%。")
    print("    这就是为什么分页（paging）在实践中几乎'免费'。")

    print("\n✅ 6.S081 Demo 完成！")


if __name__ == "__main__":
    demo()
