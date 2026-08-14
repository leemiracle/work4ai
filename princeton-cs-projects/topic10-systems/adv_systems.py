"""
COS 518 Advanced Computer Systems（Princeton）
=================================================
覆盖主题：
- Lock-free stack（CAS — Compare-And-Swap）
- RCU read pattern（Read-Copy-Update）
- STM（Software Transactional Memory）
- Delta-chain KV store（Bw-tree delta-chain 概念，非完整 Bw-tree）

核心论文/教材：
- Herlihy & Shavit "The Art of Multiprocessor Programming" Ch 7 (Lock-free), Ch 10 (STM)
- Michael & Scott 1996 "Simple, Fast, and Practical Non-Blocking and Blocking Concurrent Queue Algorithms" PODC
- McKenney 2004 "Exploiting Deferred Destruction: RCU" Linux Journal
- Levandoski et al. 2013 "The Bw-Tree: A Latch-Free and Modifiable B+ Tree" (Microsoft) CIDR

本文件实现：
1. Lock-free stack（模拟 CAS）
2. RCU read-side critical section + grace period
3. STM（optimistic concurrency, read/write sets, validation）
4. Delta-chain KV store（Bw-tree 的 delta chain 思想，非完整 Bw-tree）

运行：
    python adv_systems.py
"""
from __future__ import annotations
import threading
import random
from dataclasses import dataclass, field
from typing import Optional


# ================================================================
# 1. Lock-Free Stack (CAS simulation)
# ================================================================

class CASLockFreeStack:
    """Lock-free stack using Compare-And-Swap (simulated in single-thread).

    In real systems, CAS is an atomic hardware instruction:
        CAS(addr, expected, new) → old_value (atomically)
    """

    def __init__(self):
        self.head: Optional[int] = None  # pointer (index) to top node
        self.nodes: list[dict] = []     # simulated memory
        self.cas_attempts = 0
        self.cas_failures = 0

    def _cas_head(self, expected: Optional[int], new_val: Optional[int]) -> bool:
        """Simulate CAS on head pointer."""
        self.cas_attempts += 1
        if self.head == expected:
            self.head = new_val
            return True
        self.cas_failures += 1
        return False

    def push(self, value):
        """Lock-free push:
        1. Create new node with next = current head
        2. CAS(head, old_head, new_node)
        3. Retry if CAS fails
        """
        new_idx = len(self.nodes)
        while True:
            old_head = self.head
            self.nodes.append({"value": value, "next": old_head})
            if self._cas_head(old_head, new_idx):
                return
            self.nodes.pop()  # rollback

    def pop(self):
        """Lock-free pop:
        1. Read head
        2. If null, stack empty
        3. Read next pointer
        4. CAS(head, old_head, next)
        5. Retry if CAS fails
        """
        while True:
            old_head = self.head
            if old_head is None:
                return None  # empty
            next_node = self.nodes[old_head]["next"]
            if self._cas_head(old_head, next_node):
                return self.nodes[old_head]["value"]


# ================================================================
# 2. RCU (Read-Copy-Update)
# ================================================================

class RCUStructure:
    """Simulate RCU: readers are lock-free, writers copy + atomically swap.

    Key idea:
    - Readers access data without locks (fast path)
    - Writers create a copy, modify the copy, then atomically swap pointer
    - Old version is freed only after all readers finish (grace period)

    Used in Linux kernel for hot data paths (e.g., dcache, routing tables).

    简化说明：read() 直接读 self.data 引用，不做真正的快照固定（真实 RCU 读者
    在 read-side critical section 内固定旧版本指针，写者的 synchronize_rcu()
    等待所有 pre-existing 读者退出后才释放旧版本）。demo 用 write_update() 返回
    的 old_data 模拟"看到旧值"——但在本实现中 read_lock/unlock 不影响 read() 结果。
    """

    def __init__(self, initial_data: dict):
        self.data = dict(initial_data)
        self.reader_count = 0
        self.writer_count = 0
        self.grace_periods = 0

    def read_lock(self):
        """RCU read-side critical section: no locks!"""
        self.reader_count += 1

    def read_unlock(self):
        self.reader_count -= 1

    def write_update(self, key, value):
        """RCU write: copy → modify → swap → wait for grace period."""
        self.writer_count += 1
        # 1. Copy
        new_data = dict(self.data)
        # 2. Modify copy
        new_data[key] = value
        # 3. Atomic swap
        old_data = self.data
        self.data = new_data
        # 4. Wait for grace period (all old readers to finish)
        # In real RCU: synchronize_rcu() waits for all pre-existing readers
        self.grace_periods += 1
        # Old data can now be safely freed
        return old_data

    def read(self, key):
        """Lock-free read."""
        return self.data.get(key)


# ================================================================
# 3. STM (Software Transactional Memory)
# ================================================================

@dataclass
class TransactionLog:
    read_set: dict = field(default_factory=dict)   # var → value_read
    write_set: dict = field(default_factory=dict)  # var → new_value


class STMMemory:
    """Optimistic STM with read/write sets and validation.

    Transaction protocol:
    1. Read: record (var, value) in read_set
    2. Write: record in write_set (deferred)
    3. Commit:
       a. Validate: check read_set values haven't changed
       b. If valid: apply write_set atomically
       c. If invalid: abort, retry

    简化说明：compute 操作直接读 self.vars 而非从 read_set 取值，且校验仅比较
    当前值（非 version 号）。真实 STM 的 compute 应将所读变量加入 read_set，
    在 commit 时统一校验 version 以保证 opacity（事务内读到一致性快照）。
    """

    def __init__(self):
        self.vars: dict[str, int] = {}
        self.version: dict[str, int] = {}  # version counter per var
        self.aborts = 0
        self.commits = 0

    def init(self, name: str, value: int):
        self.vars[name] = value
        self.version[name] = 0

    def transaction(self, actions: list, max_retries: int = 10) -> bool:
        """Execute a transaction. actions = list of (op, var, [value])."""
        for attempt in range(max_retries):
            log = TransactionLog()
            try:
                # Execute actions
                for action in actions:
                    op = action[0]
                    var = action[1]
                    if op == "read":
                        # Record current value and version
                        log.read_set[var] = self.vars.get(var)
                    elif op == "write":
                        log.write_set[var] = action[2]
                    elif op == "compute":
                        # Read + compute + write
                        reads = action[2]
                        compute_fn = action[3]
                        vals = [self.vars.get(r, log.read_set.get(r)) for r in reads]
                        result = compute_fn(vals)
                        log.write_set[action[1]] = result

                # Validate: check reads haven't changed
                for var, val in log.read_set.items():
                    if self.vars.get(var) != val:
                        raise RuntimeError("validation failed")

                # Commit: apply writes
                for var, val in log.write_set.items():
                    self.vars[var] = val
                    self.version[var] += 1
                self.commits += 1
                return True

            except RuntimeError:
                self.aborts += 1
                continue
        return False


# ================================================================
# 4. Delta-Chain KV Store (Bw-tree delta-chain concept, simplified)
# ================================================================

class DeltaChainPage:
    """A page that supports delta updates.

    简化说明：这不是真正的 Bw-tree。真正的 Bw-tree 有 Page Mapping Table (PMT)
    的 CAS swap、内部页/叶子页、节点分裂等机制。本类仅演示 delta chain 思想：
    写操作追加 delta 记录而非原地修改，读时 consolidate 全链。
    """

    def __init__(self, pid: int):
        self.pid = pid
        self.records: dict = {}       # key → value (consolidated base)
        self.delta_chain: list = []   # list of delta records (oldest→newest)

    def apply_delta(self, delta_type: str, key, value=None):
        """Add a delta record instead of modifying in place."""
        self.delta_chain.append({"type": delta_type, "key": key, "value": value})

    def materialize(self) -> dict:
        """Consolidate delta chain into final state (oldest first; newest wins)."""
        result = dict(self.records)
        for delta in self.delta_chain:  # apply oldest first; later deltas override
            if delta["type"] == "insert":
                result[delta["key"]] = delta["value"]
            elif delta["type"] == "delete":
                result.pop(delta["key"], None)
        return result


class DeltaChainKVStore:
    """Delta-chain key-value store（演示 Bw-tree 的 delta chain 思想）.

    简化说明：这不是真正的 Bw-tree。真正的 Bw-tree (Levandoski et al. 2013) 有：
    - PMT (Page Mapping Table) 上的 CAS swap 实现 latch-free 更新
    - 内部页/叶子页分离 + 节点分裂/合并
    - 结构修改 delta (SplitDelta, RemoveDelta 等)
    本类仅保留 delta chain consolidate 机制，无 PMT CAS、无分裂、单 root page。
    """

    def __init__(self):
        self.pages: dict[int, DeltaChainPage] = {}
        self.next_pid = 0
        self.root_pid = self._allocate_page()

    def _allocate_page(self) -> int:
        pid = self.next_pid
        self.next_pid += 1
        self.pages[pid] = DeltaChainPage(pid)
        return pid

    def upsert(self, key, value):
        """Insert/update: append delta record to root page."""
        page = self.pages[self.root_pid]
        page.apply_delta("insert", key, value)

    def delete(self, key):
        page = self.pages[self.root_pid]
        page.apply_delta("delete", key)

    def get(self, key):
        page = self.pages[self.root_pid]
        materialized = page.materialize()
        return materialized.get(key)

    def consolidate(self):
        """Merge delta chain into base page (garbage collect)."""
        page = self.pages[self.root_pid]
        page.records = page.materialize()
        page.delta_chain = []


# ================================================================
# Demo
# ================================================================

def demo():
    print("=" * 60)
    print("COS 518: Advanced Systems Demo")
    print("=" * 60)

    # --- 1. Lock-Free Stack ---
    print("\n📋 1. Lock-Free Stack (CAS)")
    stack = CASLockFreeStack()
    for i in range(5):
        stack.push(i)
    print(f"   Push 0..4")
    popped = []
    for _ in range(5):
        popped.append(stack.pop())
    print(f"   Pop: {popped}")
    print(f"   CAS 尝试: {stack.cas_attempts}, 失败: {stack.cas_failures}")
    print(f"   → 无锁数据结构依赖硬件 CAS 原子指令")

    # --- 2. RCU ---
    print("\n📋 2. RCU (Read-Copy-Update)")
    rcu = RCUStructure({"name": "Alice", "age": 30})
    # Concurrent reads
    rcu.read_lock()
    print(f"   读线程: name={rcu.read('name')}")
    # Writer updates
    old = rcu.write_update("name", "Bob")
    print(f"   写线程更新: name → Bob (old: {old['name']})")
    print(f"   读线程仍看到旧值: name={old['name']} (在 read-side critical section 内)")
    rcu.read_unlock()
    print(f"   新读取: name={rcu.read('name')}")
    print(f"   Grace periods: {rcu.grace_periods}")

    # --- 3. STM ---
    print("\n📋 3. STM (Software Transactional Memory)")
    stm = STMMemory()
    stm.init("balance", 100)
    stm.init("credit", 0)

    # Transfer 30 from balance to credit
    success = stm.transaction([
        ("read", "balance"),
        ("read", "credit"),
        ("compute", "balance", ["balance", "credit"],
         lambda vals: vals[0] - 30),
        ("compute", "credit", ["credit"],
         lambda vals: vals[0] + 30),
    ])
    print(f"   转账 30: balance={stm.vars['balance']}, credit={stm.vars['credit']}")
    print(f"   提交: {stm.commits}, 中止: {stm.aborts}")

    # --- 4. Delta-Chain KV Store ---
    print("\n📋 4. Delta-Chain KV Store (Bw-tree delta-chain 概念)")
    store = DeltaChainKVStore()
    for i in range(10):
        store.upsert(f"key_{i}", f"value_{i}")
    print(f"   插入 10 个 key (via delta chain)")
    root_page = store.pages[store.root_pid]
    print(f"   Root page delta chain 长度: {len(root_page.delta_chain)}")
    print(f"   get('key_5') = {store.get('key_5')}")

    store.delete("key_3")
    print(f"   删除 key_3, get('key_3') = {store.get('key_3')}")

    # Consolidate
    store.consolidate()
    print(f"   合并后 delta chain 长度: {len(store.pages[store.root_pid].delta_chain)}")
    print(f"   get('key_5') after consolidation = {store.get('key_5')}")

    # 反直觉发现
    print("\n💡 反直觉发现：")
    print(f"   RCU 读者完全无锁、无原子操作——直接读！")
    print(f"   → 在读多写少场景（Linux dcache 99.99% 读），RCU 比读写锁快 10-100×")
    print(f"   → 代价：写者需要拷贝整个数据结构 + 等待 grace period")
    print(f"   Delta-chain KV store 演示了 Bw-tree 的 delta chain 思想：")
    print(f"   → 写者追加 delta 记录而非原地修改（真正的 Bw-tree 还需 CAS PMT 指针）")
    print(f"   → 真正的 Bw-tree 在高并发 OLTP 场景大幅超越传统 B+ tree")

    print("\n✅ COS 518 Demo 完成！")


if __name__ == "__main__":
    demo()
