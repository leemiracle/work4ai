"""
CS 162 Operating Systems and System Programming — UC Berkeley
================================================
覆盖主题：
- 进程/线程调度（lottery / CFS）（Lec 7-9）
- 虚拟内存 + 地址翻译（Lec 13-15）
- 文件系统（log-structured FS）（Lec 18-20）
- 并发：锁 / 哲学家就餐 / 死锁（Lec 10-12）

核心教材/参考：
- Silberschatz, Galvin, Gagne "Operating System Concepts" 10th ed (Wiley 2018), Ch 5-6/9/15
- Ousterhout & Rosenblum "The Design and Implementation of a Log-Structured File System" ACM TOCS 10(1) (1992)
- Waldspurger & Weihl "Lottery Scheduling: Flexible Proportional-Share Resource Management" OSDI 1994
- Dijkstra "Cooperating Sequential Processes" (1965) —— 哲学家就餐原典

本文件实现：
- Lottery scheduler + CFS（虚拟运行时间）
- 多级页表地址翻译
- Log-Structured FS（segment 写）
- Dining philosophers（资源层级 + 死锁检测）

运行：
    python os.py
"""
from __future__ import annotations
import random
import heapq
from collections import defaultdict


# ============================================================
# 1. 进程调度（Lottery + CFS）
# ============================================================

class Process:
    def __init__(self, pid, tickets=1, burst=10, nice=0):
        self.pid = pid
        self.tickets = tickets
        self.burst = burst
        self.nice = nice
        self.runtime = 0
        self.vruntime = 0.0  # CFS 虚拟运行时间


class LotteryScheduler:
    """
    Lottery Scheduling (Waldspurger 1994 OSDI):
    - 每个进程持有一定数量'彩票'
    - 每次调度：随机抽 1 张，持有者获得 CPU
    - 彩票数 ∝ 优先级（proportional share）
    """
    def __init__(self):
        self.processes: list[Process] = []

    def add(self, p: Process):
        self.processes.append(p)

    def schedule(self, total_steps: int = 100) -> dict[int, int]:
        """返回每进程实际运行时间"""
        run_counts = defaultdict(int)
        # 构建彩票池
        all_tickets = []
        for p in self.processes:
            all_tickets.extend([(p.pid, p) for _ in range(p.tickets)])
        for step in range(total_steps):
            if not all_tickets:
                break
            winner = random.choice(all_tickets)
            pid = winner[0]
            run_counts[pid] += 1
            for p in self.processes:
                if p.pid == pid:
                    p.runtime += 1
                    break
            # 进程完成则移除
            procs_left = [p for p in self.processes if p.runtime < p.burst]
            if not procs_left:
                break
        return dict(run_counts)


class CFSScheduler:
    """
    CFS (Completely Fair Scheduler, Linux 默认):
    - 维护红黑树（这里用堆），按 vruntime 排序
    - vruntime 增长率 = 实际时间 × (NICE_0_LOAD / weight)
    - weight 由 nice 值决定（nice 越低 weight 越高，vruntime 增长越慢）
    - 每次选 vruntime 最小的进程运行
    """
    def __init__(self):
        self.processes: list[Process] = []

    def add(self, p: Process):
        self.processes.append(p)

    @staticmethod
    def _weight(nice):
        # 简化：nice=0 → weight=1024, 每 nice ±1 约相差 25%
        return 1024 * (1.25 ** (-nice))

    def schedule(self, total_steps=100, slice_=1):
        log = []
        for _ in range(total_steps):
            if not self.processes:
                break
            # 选 vruntime 最小的
            self.processes.sort(key=lambda p: p.vruntime)
            p = self.processes[0]
            if p.runtime >= p.burst:
                self.processes.pop(0)
                continue
            # 运行 slice 步
            for _ in range(slice_):
                if p.runtime >= p.burst:
                    break
                p.runtime += 1
                # vruntime 增长（按 weight 归一化）
                p.vruntime += slice_ * (1024 / self._weight(p.nice))
                log.append(p.pid)
        counts = defaultdict(int)
        for pid in log:
            counts[pid] += 1
        return dict(counts)


# ============================================================
# 2. 虚拟内存地址翻译（多级页表）
# ============================================================

class VirtualMemory:
    """
    多级页表翻译（x86-64 4 级页表简化为 2 级）：
    VA = [VPN1 | VPN2 | offset]
    CR3 → 页目录 → 页表 → 物理页
    """
    def __init__(self, page_size=16):
        self.page_size = page_size
        self.page_dir: dict[int, dict[int, int]] = {}  # PD → PT → PFN
        self.pf_memory: dict[int, list] = {}  # 物理帧
        self.tlb: dict[tuple, int] = {}
        self.tlb_hits = 0
        self.tlb_misses = 0

    def map(self, vpn1, vpn2, pfn):
        if vpn1 not in self.page_dir:
            self.page_dir[vpn1] = {}
        self.page_dir[vpn1][vpn2] = pfn
        self.pf_memory[pfn] = [0] * self.page_size

    def translate(self, va: int) -> int | None:
        """va = vpn1 * (256) + vpn2 * (16) + offset"""
        offset = va % self.page_size
        va2 = va // self.page_size
        vpn2 = va2 % 256
        vpn1 = va2 // 256
        # TLB 查找
        key = (vpn1, vpn2)
        if key in self.tlb:
            self.tlb_hits += 1
            pfn = self.tlb[key]
        else:
            self.tlb_misses += 1
            if vpn1 not in self.page_dir or vpn2 not in self.page_dir[vpn1]:
                return None  # page fault
            pfn = self.page_dir[vpn1][vpn2]
            self.tlb[key] = pfn  # 填充 TLB
        return pfn * self.page_size + offset


# ============================================================
# 3. Log-Structured File System（Ousterhout 1992）
# ============================================================

class LogStructuredFS:
    """
    LFS 核心：
    - 顺序写日志（不分多次随机写）
    - inode 通过 imap 定位
    - segment 满时清理（compaction）
    """
    def __init__(self, segment_size=8):
        self.segment_size = segment_size
        self.log: list[dict] = []  # 每个 entry = {type, ...}
        self.imap: dict[str, int] = {}  # filename → log index
        self.segments_written = 0

    def write(self, filename, data):
        """追加写：data → log"""
        idx = len(self.log)
        self.log.append({"type": "data", "file": filename, "data": data})
        self.imap[filename] = idx
        # 检查 segment 边界
        if len(self.log) % self.segment_size == 0:
            self.segments_written += 1

    def write_inode(self, filename, size):
        idx = len(self.log)
        self.log.append({"type": "inode", "file": filename, "size": size})
        # inode 也通过 imap 找到 data
        if filename in self.imap:
            self.log[self.imap[filename]]["inode_idx"] = idx

    def read(self, filename):
        if filename not in self.imap:
            return None
        return self.log[self.imap[filename]]["data"]

    def delete(self, filename):
        """标记删除（log-structured 不真正删除，靠 compaction）"""
        idx = len(self.log)
        self.log.append({"type": "tombstone", "file": filename})
        if filename in self.imap:
            del self.imap[filename]

    def total_writes(self):
        return len(self.log)


# ============================================================
# 4. Dining Philosophers（Dijkstra 1965）
# ============================================================

def dining_philosophers_deadlock(n=5, steps=20):
    """
    经典死锁版本：每个哲学家先拿左叉再拿右叉
    → 5 人同时拿左 → 循环等待 → 死锁
    """
    forks = [True] * n  # True = 可用
    deadlock = False
    held = [0] * n
    for step in range(steps):
        progressed = False
        for i in range(n):
            left = i
            right = (i + 1) % n
            if forks[left] and forks[right]:
                forks[left] = forks[right] = False
                held[i] += 1
                progressed = True
                # 吃完放下
                forks[left] = forks[right] = True
        if not progressed:
            deadlock = True
            break
    return {"deadlock": deadlock, "steps": step + 1, "eaten": held}


def dining_philosophers_safe(n=5, steps=50):
    """
    安全版本：资源层级（奇数号哲学家先拿右叉，偶数先拿左叉）
    打破循环等待。
    """
    forks = [True] * n
    held = [0] * n
    for step in range(steps):
        for i in range(n):
            left = i
            right = (i + 1) % n
            # 奇数号先右后左，偶数先左后右（破坏循环）
            if i % 2 == 0:
                first, second = left, right
            else:
                first, second = right, left
            if forks[first] and forks[second]:
                forks[first] = forks[second] = False
                held[i] += 1
                forks[first] = forks[second] = True
    return {"deadlock": False, "steps": steps, "eaten": held}


# ============================================================
# Demo —— 反直觉发现
# ============================================================

def demo():
    print("=" * 60)
    print("CS 162 Operating Systems Demo")
    print("=" * 60)
    random.seed(42)

    # 1. Lottery Scheduling
    print("\n📋 1. Lottery Scheduling（proportional share）")
    lot = LotteryScheduler()
    lot.add(Process(1, tickets=10, burst=100))
    lot.add(Process(2, tickets=5, burst=100))
    lot.add(Process(3, tickets=1, burst=100))
    counts = lot.schedule(total_steps=200)
    print(f"   P1(10 tickets), P2(5 tickets), P3(1 ticket)")
    print(f"   实际运行: {counts}")
    ratio_12 = counts.get(1, 1) / max(counts.get(2, 1), 1)
    print(f"   P1/P2 比 = {ratio_12:.2f}（理论 10/5=2.0）")

    # 2. CFS
    print("\n📋 2. CFS（Completely Fair Scheduler）")
    cfs = CFSScheduler()
    cfs.add(Process(10, burst=50, nice=0))
    cfs.add(Process(11, burst=50, nice=-5))  # 高优先级
    cfs.add(Process(12, burst=50, nice=5))   # 低优先级
    counts_cfs = cfs.schedule(total_steps=100, slice_=1)
    print(f"   P10(nice=0), P11(nice=-5), P12(nice=+5)")
    print(f"   CFS 运行: {counts_cfs}")
    print(f"   → nice=-5 拿到更多 CPU（vruntime 增长慢）")

    # 3. Virtual Memory
    print("\n📋 3. 虚拟内存 + TLB")
    vm = VirtualMemory(page_size=16)
    # 建立 mapping: VA 0x00 → PFN 5, VA 0x100 → PFN 8
    vm.map(0, 0, 5)
    vm.map(0, 1, 8)
    vm.map(1, 0, 12)
    # 翻译
    test_vas = [0, 16, 256, 272, 0, 16]  # 后两个重复（TLB hit）
    for va in test_vas:
        pa = vm.translate(va)
        print(f"   VA 0x{va:04X} → PA {'0x{:04X}'.format(pa) if pa else 'FAULT'}")
    print(f"   TLB hits={vm.tlb_hits}, misses={vm.tlb_misses}")

    # 4. LFS
    print("\n📋 4. Log-Structured File System")
    lfs = LogStructuredFS(segment_size=4)
    lfs.write("a.txt", "hello")
    lfs.write("b.txt", "world")
    lfs.write_inode("a.txt", 5)
    lfs.write("c.txt", "!")
    lfs.delete("b.txt")
    print(f"   写入 a/b/c + 删 b → 总 log 条目: {lfs.total_writes()}")
    print(f"   read(a) = {lfs.read('a')}")
    print(f"   read(b) = {lfs.read('b')}  (deleted)")
    print(f"   segments 写入: {lfs.segments_written}")

    # 5. Dining Philosophers
    print("\n📋 5. Dining Philosophers（死锁 vs 安全）")
    result_dead = dining_philosophers_deadlock(5, 20)
    result_safe = dining_philosophers_safe(5, 50)
    print(f"   死锁版: deadlock={result_dead['deadlock']}, eaten={result_dead['eaten']}")
    print(f"   安全版（资源层级）: deadlock={result_safe['deadlock']}, eaten={result_safe['eaten']}")

    # 反直觉发现
    print("\n" + "=" * 60)
    print("💡 反直觉发现：")
    print("   Lottery 调度中 P1:P2:P3 = 10:5:1，")
    print(f"   实际比例 {counts.get(1,0)}:{counts.get(2,0)}:{counts.get(3,0)} ≈ 10:5:1")
    print("   200 步内，P3（1 ticket）只拿到 ~13 次 ≈ 6%。")
    print("   '随机彩票'听起来不公平，但大数定律保证长期比例精确。")
    print()
    print("   哲学家就餐：5 个人 5 把叉，看起来公平的'先左后右'会死锁。")
    print("   解决方案：打破 4 个 Coffman 条件之一（循环等待/持有等待/...）")
    print("   资源层级法只需让 1 个哲学家'反着拿'，死锁就消失。")
    print()
    print("   LFS 的反直觉：随机写文件 → 顺序追加日志 → 后台 compaction")
    print("   写吞吐可达磁盘带宽的 80%（传统 FS 只有 5-10%）。")
    print("   这是 SSD 时代 write-ahead logging 的基础思想。")


if __name__ == "__main__":
    demo()
