#!/usr/bin/env python3
"""
tinytx — 参照 PostgreSQL MVCC 的事务引擎

参照：PostgreSQL MVCC + SQLite WAL + DMV Chapter 22
csdiy 对应：db §四(MVCC/隔离级别) + §二(锁)

核心：多版本并发控制 + 隔离级别 + Snapshot Isolation
"""
import time, threading
from dataclasses import dataclass, field
from typing import Any, Optional

@dataclass
class Version:
    """一个数据的版本（参照 PostgreSQL tuple 的 xmin/xmax）"""
    value: Any
    created_tx: int   # xmin: 创建此版本的事务 ID
    deleted_tx: int = 0  # xmax: 删除此版本的事务 ID（0 = 未删除）

class Transaction:
    """事务（参照 PostgreSQL BEGIN/COMMIT/ROLLBACK）"""
    def __init__(self, txid, snapshot):
        self.txid = txid
        self.snapshot = snapshot  # 快照（开始时的活跃事务列表）
        self.committed = False
        self.aborted = False

class TinyMVCC:
    """
    MVCC 引擎（参照 PostgreSQL + DMV §22.3）

    每个写操作创建新版本（不是原地更新）。
    读操作看到的是快照时刻的版本（读不阻塞写）。
    """
    def __init__(self):
        self.data: dict[str, list[Version]] = {}
        self.next_txid = 1
        self.committed_txns = set()  # 已提交的事务 ID
        self.lock = threading.Lock()

    def begin(self) -> Transaction:
        """BEGIN（参照 PostgreSQL BEGIN）"""
        with self.lock:
            txid = self.next_txid
            self.next_txid += 1
            # 快照：当前已提交的事务
            snapshot = set(self.committed_txns)
            return Transaction(txid, snapshot)

    def read(self, tx: Transaction, key: str) -> Any:
        """
        读取（参照 PostgreSQL 的 Snapshot Isolation）

        规则：看到创建事务在快照中 AND 未被删除 或 被在快照之后的事务删除
        """
        versions = self.data.get(key, [])
        for v in reversed(versions):  # 从新到旧找
            # 版本可见条件（参照 DMV §22.3）:
            # 1. created_tx 已提交且在快照中
            # 2. deleted_tx == 0 或 deleted_tx 不在快照中
            if v.created_tx in tx.snapshot and (v.deleted_tx == 0 or v.deleted_tx not in tx.snapshot):
                return v.value
        return None

    def write(self, tx: Transaction, key: str, value: Any):
        """写入（创建新版本，参照 PostgreSQL INSERT/UPDATE）"""
        # 标记旧版本为"被删除"（xmax = 当前事务）
        for v in self.data.get(key, []):
            if v.created_tx in tx.snapshot and v.deleted_tx == 0:
                v.deleted_tx = tx.txid
                break
        # 创建新版本（xmin = 当前事务）
        self.data.setdefault(key, []).append(Version(value, tx.txid))

    def commit(self, tx: Transaction):
        """COMMIT"""
        tx.committed = True
        self.committed_txns.add(tx.txid)

    def abort(self, tx: Transaction):
        """ROLLBACK（回滚：标记当前事务的版本为已中止）"""
        tx.aborted = True

    def isolation_demo(self):
        """隔离级别演示"""
        print("tinytx — MVCC 事务引擎\n")

        # Read Committed：读到已提交的最新值
        tx0 = self.begin(); self.write(tx0, "balance", 100); self.commit(tx0)
        print(f"  初始: balance = 100")

        tx1 = self.begin()
        val1 = self.read(tx1, "balance")
        print(f"  TX1 BEGIN → read balance = {val1}")

        tx2 = self.begin(); self.write(tx2, "balance", 200); self.commit(tx2)
        print(f"  TX2 BEGIN → write balance = 200 → COMMIT")

        val1_after = self.read(tx1, "balance")
        print(f"  TX1 read balance again = {val1_after} {'(看到新值=Read Committed)' if val1_after != val1 else '(看到旧值=Repeatable Read)'}")

        # 可重复读 vs 读已提交
        print(f"\n  隔离级别对比:")
        print(f"    Snapshot Isolation: TX1 始终看到 {val1}（快照不变）")
        print(f"    Read Committed:     TX1 第二次读看到 {val1_after}（每次读新快照）")

        self.commit(tx1)

        # Abort 演示
        print(f"\n  Abort 演示:")
        tx3 = self.begin(); self.write(tx3, "balance", 999); self.abort(tx3)
        tx4 = self.begin()
        val4 = self.read(tx4, "balance")
        print(f"    TX3 write 999 → ABORT")
        print(f"    TX4 read balance = {val4} (看到的是已提交值，不是 aborted 的)")

if __name__ == "__main__":
    mvcc = TinyMVCC()
    mvcc.isolation_demo()
