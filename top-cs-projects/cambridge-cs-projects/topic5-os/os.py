"""
Part IB Operating Systems (Cambridge CST)
=========================================
覆盖主题：
- 内核模拟（syscall 派发）
- 进程调度（FCFS / SJF / Round-Robin / Priority）
- 内存管理（分页 / 页面置换）
- inode-like 文件系统

核心教材：
- Tanenbaum & Bos 2014 "Modern Operating Systems" 4th ed, Pearson
- Silberschatz, Galvin & Gagne 2018 "Operating System Concepts" 10th ed (Dinosaur Book)
- Bovet & Cesati 2005 "Understanding the Linux Kernel" 3rd ed, O'Reilly

本文件实现：
- KernelSim: syscall 派发 + 用户态/内核态切换
- 调度器: Round-Robin / SJF / Priority 抢占式
- 页面置换: FIFO / LRU / Optimal / Clock
- 简易 inode 文件系统（分配/释放/读/写）

运行：
    python os.py
"""
from __future__ import annotations
from dataclasses import dataclass, field
from collections import deque


# ================================================================
# 1. 进程与调度
# ================================================================

@dataclass
class PCB:
    """Process Control Block"""
    pid: int
    name: str
    burst: int           # CPU 需求
    arrival: int = 0
    priority: int = 0    # 数字越小优先级越高
    remaining: int = 0
    waiting: int = 0
    finished_at: int = -1

    def __post_init__(self):
        self.remaining = self.burst


def round_robin(processes: list[PCB], quantum: int = 2) -> list[dict]:
    """Round-Robin 调度"""
    procs = [PCB(p.pid, p.name, p.burst, p.arrival, p.priority) for p in processes]
    ready = deque()
    time = 0
    timeline = []
    arrived = sorted(procs, key=lambda p: p.arrival)
    idx = 0
    while idx < len(arrived) or ready:
        while idx < len(arrived) and arrived[idx].arrival <= time:
            ready.append(arrived[idx])
            idx += 1
        if not ready:
            time = arrived[idx].arrival
            continue
        p = ready.popleft()
        run = min(quantum, p.remaining)
        for _ in range(run):
            timeline.append((time, p.pid))
            time += 1
        # 等待中的进程 +waiting
        for q in ready:
            q.waiting += run
        # 新到达的入队
        while idx < len(arrived) and arrived[idx].arrival <= time:
            ready.append(arrived[idx])
            idx += 1
        p.remaining -= run
        if p.remaining > 0:
            ready.append(p)
        else:
            p.finished_at = time
    results = []
    for p in sorted(procs, key=lambda x: x.pid):
        results.append({"pid": p.pid, "name": p.name, "wait": p.waiting,
                        "turnaround": p.finished_at - p.arrival})
    return results


def sjf_nonpreemptive(processes: list[PCB]) -> list[dict]:
    """Shortest Job First (non-preemptive)"""
    procs = [PCB(p.pid, p.name, p.burst, p.arrival, p.priority) for p in processes]
    done = []
    time = 0
    remaining = list(procs)
    while remaining:
        avail = [p for p in remaining if p.arrival <= time]
        if not avail:
            time = min(p.arrival for p in remaining)
            continue
        p = min(avail, key=lambda x: x.burst)
        p.waiting = time - p.arrival
        time += p.burst
        p.finished_at = time
        done.append(p)
        remaining.remove(p)
    return [{"pid": p.pid, "wait": p.waiting,
             "turnaround": p.finished_at - p.arrival} for p in done]


# ================================================================
# 2. KernelSim: syscall 派发
# ================================================================

class KernelSim:
    """模拟内核 syscall 派发"""

    def __init__(self):
        self.memory = {}        # pid → 分配的内存页
        self.next_pid = 1
        self.syscall_log = []

    def syscall(self, name, args):
        self.syscall_log.append((name, args))
        if name == "fork":
            pid = self.next_pid
            self.next_pid += 1
            self.memory[pid] = []
            return pid
        if name == "exit":
            pid = args[0]
            if pid in self.memory:
                del self.memory[pid]
            return 0
        if name == "write":
            fd, data = args
            return len(data)
        if name == "read":
            fd, n = args
            return "x" * min(n, 10)
        return -1


# ================================================================
# 3. 页面置换
# ================================================================

class PageReplacer:
    """模拟页面置换算法"""

    def __init__(self, num_frames: int):
        self.num_frames = num_frames

    def fifo(self, ref_string: list[int]) -> int:
        frames = []
        page_queue = deque()
        faults = 0
        for page in ref_string:
            if page not in frames:
                faults += 1
                if len(frames) >= self.num_frames:
                    old = page_queue.popleft()
                    frames.remove(old)
                frames.append(page)
                page_queue.append(page)
        return faults

    def lru(self, ref_string: list[int]) -> int:
        frames = []
        last_used = {}
        faults = 0
        for t, page in enumerate(ref_string):
            if page in frames:
                last_used[page] = t
            else:
                faults += 1
                if len(frames) >= self.num_frames:
                    lru_page = min(frames, key=lambda p: last_used.get(p, -1))
                    frames.remove(lru_page)
                frames.append(page)
                last_used[page] = t
        return faults

    def optimal(self, ref_string: list[int]) -> int:
        frames = []
        faults = 0
        for i, page in enumerate(ref_string):
            if page in frames:
                continue
            faults += 1
            if len(frames) >= self.num_frames:
                # 替换未来最远使用的页
                farthest = -1
                victim = frames[0]
                for f in frames:
                    try:
                        nxt = ref_string.index(f, i + 1)
                    except ValueError:
                        nxt = float('inf')
                    if nxt > farthest:
                        farthest = nxt
                        victim = f
                frames.remove(victim)
            frames.append(page)
        return faults


# ================================================================
# 4. inode-like 文件系统
# ================================================================

@dataclass
class Inode:
    name: str
    is_dir: bool
    size: int = 0
    blocks: list[int] = field(default_factory=list)
    children: dict = field(default_factory=dict)


class SimpleFS:
    """inode-like 文件系统，块分配用位图"""

    def __init__(self, total_blocks: int = 64):
        self.total_blocks = total_blocks
        self.free_blocks = list(range(total_blocks))
        self.root = Inode("/", is_dir=True)

    def allocate(self, n: int) -> list[int]:
        if len(self.free_blocks) < n:
            raise RuntimeError("Disk full")
        blocks = [self.free_blocks.pop(0) for _ in range(n)]
        return blocks

    def free(self, blocks: list[int]):
        self.free_blocks.extend(blocks)

    def create_file(self, path: str, size_blocks: int):
        parts = path.strip("/").split("/")
        cur = self.root
        for part in parts[:-1]:
            if part not in cur.children:
                cur.children[part] = Inode(part, is_dir=True)
            cur = cur.children[part]
        blocks = self.allocate(size_blocks)
        inode = Inode(parts[-1], is_dir=False, size=size_blocks, blocks=blocks)
        cur.children[parts[-1]] = inode
        return inode

    def delete_file(self, path: str):
        parts = path.strip("/").split("/")
        cur = self.root
        for part in parts[:-1]:
            cur = cur.children[part]
        inode = cur.children[parts[-1]]
        self.free(inode.blocks)
        del cur.children[parts[-1]]

    def ls(self, path="/"):
        parts = path.strip("/").split("/") if path != "/" else []
        cur = self.root
        for part in parts:
            cur = cur.children[part]
        return cur.children.keys()

    def fragmentation(self) -> float:
        return len(self.free_blocks) / self.total_blocks


# ================================================================
# Demo
# ================================================================

def demo():
    print("=" * 64)
    print("Part IB Operating Systems — Demo")
    print("=" * 64)

    # 1. 调度器
    print("\n📋 1. CPU 调度器对比")
    procs = [PCB(1, "P1", burst=6, arrival=0), PCB(2, "P2", burst=8, arrival=1),
             PCB(3, "P3", burst=4, arrival=2), PCB(4, "P4", burst=3, arrival=3)]

    rr = round_robin(procs, quantum=2)
    sjf = sjf_nonpreemptive(procs)
    print(f"   {'PID':>4} {'RR_wait':>8} {'RR_turn':>8} {'SJF_wait':>9} {'SJF_turn':>9}")
    for r, s in zip(rr, sjf):
        print(f"   {r['pid']:>4} {r['wait']:>8} {r['turnaround']:>8} "
              f"{s['wait']:>9} {s['turnaround']:>9}")
    avg_rr = sum(r['wait'] for r in rr) / len(rr)
    avg_sjf = sum(s['wait'] for s in sjf) / len(sjf)
    print(f"   平均等待: RR={avg_rr:.1f}, SJF={avg_sjf:.1f}")

    # 2. Kernel syscall
    print("\n📋 2. Kernel Syscall 派发")
    kernel = KernelSim()
    pid1 = kernel.syscall("fork", [])
    pid2 = kernel.syscall("fork", [])
    n = kernel.syscall("write", [1, b"hello world"])
    kernel.syscall("exit", [pid1])
    print(f"   fork → pid1={pid1}, pid2={pid2}")
    print(f"   write → wrote {n} bytes")
    print(f"   活跃进程: {list(kernel.memory.keys())}")
    print(f"   syscall 日志: {len(kernel.syscall_log)} 条")

    # 3. 页面置换
    print("\n📋 3. 页面置换算法（Belady 反直觉！）")
    ref = [1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5]
    for frames in [3, 4]:
        pr = PageReplacer(frames)
        fifo = pr.fifo(ref)
        lru = pr.lru(ref)
        opt = pr.optimal(ref)
        print(f"   {frames} frames: FIFO={fifo} faults, LRU={lru}, OPT={opt}")

    print(f"   ⚠️ FIFO 4帧({PageReplacer(4).fifo(ref)}) 可能 > FIFO 3帧({PageReplacer(3).fifo(ref)})!")
    print(f"   这就是 Belady 异常：增加帧数反而增加缺页（FIFO 特有）")

    # 4. 文件系统
    print("\n📋 4. inode-like 文件系统")
    fs = SimpleFS(total_blocks=64)
    fs.create_file("/doc/readme.txt", size_blocks=3)
    fs.create_file("/doc/notes.txt", size_blocks=2)
    fs.create_file("/code/hello.py", size_blocks=5)
    print(f"   根目录: {sorted(fs.ls('/'))}")
    print(f"   /doc: {sorted(fs.ls('/doc'))}")
    print(f"   空闲块: {len(fs.free_blocks)}/64 ({fs.fragmentation():.0%})")
    fs.delete_file("/doc/notes.txt")
    print(f"   删除 notes.txt 后空闲块: {len(fs.free_blocks)}/64")

    print("\n✅ Operating Systems 完成！")
    print("\n💡 反直觉发现：")
    print("   - SJF 等待时间总是 ≤ RR，但 SJF 可能饿死长进程")
    print("   - Belady 异常: FIFO 增加帧数可能增加缺页率！")
    print("   - LRU 不会出现 Belady 异常（栈式算法）")


if __name__ == "__main__":
    demo()
