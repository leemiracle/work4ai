"""
Distributed Computing — ETH Zürich
==================================
覆盖主题：
- FLP 不可能性定理
- 拜占庭将军问题（Oral Messages 算法）
- 共识数（Herlihy 层级）
- 环上领导者选举

核心教材/论文：
- Fischer, Lynch, Paterson "Impossibility of Distributed Consensus with One Faulty Process" JACM 32(2): 374-382 (1985) — FLP
- Lamport, Shostak, Pease "The Byzantine Generals Problem" ACM TOPLAS 4(3): 382-401 (1982)
- Herlihy "Wait-Free Synchronization" ACM TOPLAS 13(1): 124-149 (1991) — consensus number
- Herlihy & Shavit "The Art of Multiprocessor Programming" (MIT Press, 2008)

本文件实现：
1. FLP 不可能性演示（异步共识无法终止）
2. Byzantine Oral Messages (OM(m)) 算法
3. 共识对象层级（consensus number 测试）
4. 环上 Chang-Roberts 领导者选举

运行：
    python distributed.py
"""
from __future__ import annotations
import random


# ============ 1. FLP 不可能性演示 ============

class FLPSimulator:
    """
    FLP 定理：在异步系统中，即使只有 1 个进程可能崩溃，
    也无法存在确定性共识协议同时满足 termination + agreement。

    我们演示 bivalent（二价的）初始状态：
    一个可调度序列导致 0，另一个导致 1。
    """

    def __init__(self, n: int = 3):
        self.n = n
        self.proposals = [None] * n

    def run_with_schedule(self, schedule: list[int], initial: list[int]) -> int:
        """
        按调度执行，返回系统决议值。

        异步消息传递模型：进程 i 的初始值只有在它"执行 step"（广播消息）
        后才对其他进程可见。被调度器推迟的进程 = 暂时崩溃，其值不可见。
        每个进程执行时，根据**已见值**（已广播的进程 + 自己）做多数投票。
        系统决议 = 第一个执行 step 的进程的决议。

        关键：同一初始配置，不同调度 → 不同决议 = bivalent。
        """
        broadcast: set[int] = set()
        decisions: list[int | None] = [None] * self.n
        for proc in schedule:
            if proc in broadcast:
                continue
            visible = [initial[i] for i in range(self.n)
                       if i in broadcast or i == proc]
            count0 = visible.count(0)
            count1 = visible.count(1)
            decisions[proc] = 0 if count0 >= count1 else 1
            broadcast.add(proc)
        return decisions[schedule[0]] if schedule else -1

    def demonstrate_bivalent(self):
        """
        演示 FLP bivalent 配置：**同一**初始配置，两个不同调度 → 两个不同决议。

        初始 [0, 1, 0]（两个 0，一个 1）：
        - 调度 [0, 1, 2]：进程 0 先执行，只见自己的 0 → 决议 0
        - 调度 [1, 0, 2]：进程 1 先执行，只见自己的 1 → 决议 1

        同一配置可走两条路 = bivalent。FLP 证明：异步系统中调度器
        可以无限推迟消息，让系统永远停留在 bivalent 状态，
        从而不可能同时保证 termination + agreement。
        """
        initial = [0, 1, 0]
        r0 = self.run_with_schedule([0, 1, 2], initial)  # 进程 0 先走 → 决议 0
        r1 = self.run_with_schedule([1, 0, 2], initial)  # 进程 1 先走 → 决议 1
        return r0, r1


# ============ 2. 拜占庭将军 (Oral Messages OM(m)) ============

def byzantine_om(commander: int, order: int, n: int, m: int,
                 traitors: set[int], verbose: bool = False) -> dict[int, int]:
    """
    Lamport OM(m) 算法：
    - n 个将军，m 个叛徒
    - 需要 n ≥ 3m+1 才能容忍
    返回每个忠诚将军的最终决定
    """
    # 简化：递归传递命令
    # msgs[round][recipient] = set of orders received

    def om(order_val: int, commander_id: int, recipients: list[int],
           m_left: int, path: tuple) -> dict[int, int]:
        """
        递归 OM。
        path: 命令经过的将军序列（用于追踪）
        """
        results = {}
        if m_left == 0:
            for r in recipients:
                # 叛徒可能发任意值
                if commander_id in traitors:
                    sent = random.choice([0, 1])
                else:
                    sent = order_val
                results[r] = sent
            return results

        # 每个收件人收到命令后，作为新 commander 转发给其他人
        all_received: dict[int, list[int]] = {r: [] for r in recipients}
        for r in recipients:
            if commander_id in traitors:
                # 叛徒发给不同人不同值
                sent = random.choice([0, 1])
            else:
                sent = order_val
            all_received[r].append(sent)

            # 递归
            sub_recipients = [x for x in recipients if x != r]
            sub = om(sent, r, sub_recipients, m_left - 1, path + (r,))
            for sr, sv in sub.items():
                if sr in all_received:
                    all_received[sr].append(sv)

        # 多数投票
        for r in recipients:
            votes = all_received[r]
            results[r] = 1 if votes.count(1) > votes.count(0) else 0

        return results

    recipients = [i for i in range(n) if i != commander]
    return om(order, commander, recipients, m, (commander,))


def test_byzantine_agreement(n: int, m: int, order: int, traitors: set[int]) -> bool:
    """测试忠诚将军是否达成一致"""
    results = byzantine_om(commander=0, order=order, n=n, m=m, traitors=traitors)
    loyal_decisions = [results.get(i) for i in range(n) if i not in traitors and i != 0]
    # commander 自己也知道
    if 0 not in traitors:
        loyal_decisions = [order] + loyal_decisions
    return all(d == loyal_decisions[0] for d in loyal_decisions if d is not None)


# ============ 3. 共识数层级 ============

CONSENSUS_HIERARCHY = {
    1: "read/write registers",
    2: "test-and-set, swap, fetch-and-add",
    5: "atomic snapshot",
    float('inf'): "compare-and-swap, LL/SC",
}


def consensus_number_demo():
    """
    用 CAS (consensus number = ∞) 实现 consensus
    用 read/write (consensus number = 1) 无法实现 → 演示
    """
    # CAS 实现 consensus（consensus number = ∞）
    class CASConsensus:
        def __init__(self):
            self.reg = -1  # -1 = undecided
        def _cas(self, expected: int, new: int) -> bool:
            """真正的 CAS：原子地比较并交换。返回是否成功。"""
            if self.reg == expected:
                self.reg = new
                return True
            return False
        def decide(self, val: int) -> int:
            while True:
                old = self.reg            # 读
                if old != -1:
                    return old            # 已被别人决定
                if self._cas(-1, val):    # 原子 CAS（无 TOCTOU 竞争）
                    return val

    obj = CASConsensus()
    r1 = obj.decide(0)
    r2 = obj.decide(1)
    return r1, r2


# ============ 4. 环上领导者选举 (Chang-Roberts) ============

def chang_roberts_election(n: int, ids: list[int] | None = None,
                           initiators: list[int] | None = None) -> tuple[int, int]:
    """
    Chang-Roberts 算法（单向环）——真环形拓扑模拟。

    ids: 长度 n 的唯一 ID 列表，ids[i] 是环位置 i 的进程 ID。
    initiators: 哪些位置发起选举（默认全部 → 最坏 O(n²)）。

    环拓扑：进程 i 的下游邻居是 (i+1) % n。
    收到 ELECTION(k)：
      - k > 自己 ID → 转发给下游
      - k < 自己 ID → 吞掉（不转发）
      - k == 自己 ID → 绕了一圈回来 → 自己是 leader（ID 最大）
    Leader 选出后发 COORDINATOR 通知所有进程（n 条消息）。

    消息复杂度：最坏 O(n²)（全部发起 + ID 递减排列），最优 O(n)。
    """
    if ids is None:
        ids = list(range(n))
    if initiators is None:
        initiators = list(range(n))  # 全部发起 → 最坏 O(n²)
    messages = 0
    leader_id = max(ids)

    for init_pos in initiators:
        init_id = ids[init_pos]
        # init_id 的 ELECTION 消息沿环传播
        for hop in range(1, n + 1):
            cur_pos = (init_pos + hop) % n
            cur_id = ids[cur_pos]
            messages += 1                   # 消息到达 cur_pos
            if cur_id == init_id:
                break                       # 绕一圈回到自己 → 自己是 leader
            if init_id < cur_id:
                break                       # 被更大 ID 吞掉
            # init_id > cur_id → 继续转发

    messages += n                            # COORDINATOR 广播
    return leader_id, messages


# ============ Demo ============

def demo():
    print("=" * 60)
    print("Distributed Computing: FLP + Byzantine + Consensus")
    print("=" * 60)
    random.seed(42)

    # 1. FLP
    print("\n📋 1. FLP 不可能性")
    flp = FLPSimulator(n=3)
    r0, r1 = flp.demonstrate_bivalent()
    print(f"   异步 3 进程，同一初始 [0, 1, 0]")
    print(f"   调度1 → 决定 {r0}")
    print(f"   调度2 → 决定 {r1}")
    print(f"   → bivalent 状态：调度决定结果，无法保证 termination")

    # 2. Byzantine
    print("\n📋 2. 拜占庭将军 (OM(m))")
    # n=4, m=1, 需要 4 ≥ 3*1+1 = 4 ✓
    n, m = 4, 1
    order = 1  # attack
    traitors = {3}
    agreed = test_byzantine_agreement(n, m, order, traitors)
    print(f"   n={n}, m={m} 叛徒, order={order}, traitors={traitors}")
    print(f"   n≥3m+1? {n}≥{3*m+1} → {'✓' if n >= 3*m+1 else '✗'}")
    print(f"   忠诚将军达成一致: {'✓' if agreed else '✗'}")

    # m=1, n=3 < 4 → 失败
    n2, m2 = 3, 1
    agreed2 = test_byzantine_agreement(n2, m2, 1, {2})
    print(f"   n={n2}, m={m2}: n<3m+1 → 达成一致: {'✓(意外)' if agreed2 else '✗(预期失败)'}")

    # 3. 共识数
    print("\n📋 3. 共识数层级 (Herlihy)")
    r1, r2 = consensus_number_demo()
    print(f"   CAS consensus: P1 decide={r1}, P2 decide={r2}, agree={r1==r2}")
    for cn, obj in CONSENSUS_HIERARCHY.items():
        cn_str = "∞" if cn == float('inf') else str(cn)
        print(f"   consensus number {cn_str}: {obj}")

    # 4. Chang-Roberts
    print("\n📋 4. 环上领导者选举 (Chang-Roberts)")
    print(f"   真环形拓扑模拟，单向消息传递")
    for n in [5, 10, 20]:
        # 最坏情况：ID 递减排列 + 全部进程发起
        worst_ids = list(range(n, 0, -1))  # [n, n-1, ..., 1]
        leader_w, msgs_w = chang_roberts_election(n, ids=worst_ids)
        # 最优情况：只有最大 ID 进程发起
        best_ids = list(range(1, n + 1))
        max_pos = best_ids.index(max(best_ids))
        leader_b, msgs_b = chang_roberts_election(n, ids=best_ids, initiators=[max_pos])
        print(f"   n={n:2d}: 最坏 msgs={msgs_w:4d} (≈n(n+1)/2={n*(n+1)//2:4d}), "
              f"最优 msgs={msgs_b:3d} (≈2n={2*n:3d}), leader={leader_w}")

    # 反直觉
    print("\n💡 反直觉发现：FLP 定理的深刻性")
    print(f"   只需 1 个进程可能崩溃，异步系统就不存在确定性共识！")
    print(f"   → Paxos/Raft 不得不靠随机化或部分同步假设绕过")
    print(f"   → 这就是为什么区块链/分布式系统设计如此微妙")

    print("\n✅ Distributed Computing 完成！")


if __name__ == "__main__":
    demo()
