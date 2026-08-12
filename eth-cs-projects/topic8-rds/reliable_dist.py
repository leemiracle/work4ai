"""
Reliable Distributed Systems — ETH Zürich
=========================================
覆盖主题：
- Paxos (multi-decree)
- PBFT (Practical Byzantine Fault Tolerance)
- 区块链 PoW
- CRDT (G-Counter)

核心教材/论文：
- Lamport "The Part-Time Parliament" ACM TOCS 16(2): 133-169 (1998) — Paxos
- Lamport "Paxos Made Simple" ACM SIGACT News 32(4): 51-58 (2001)
- Castro & Liskov "Practical Byzantine Fault Tolerance" OSDI 1999 — PBFT
- Shapiro, Preguiça, Baquero, Zawirski "Conflict-free Replicated Data Types" SSS 2011 — CRDT

本文件实现：
1. Multi-Paxos（Proposer / Acceptor / Learner，per-slot 状态）
2. PBFT 3 阶段（pre-prepare / prepare / commit）
3. 简易 PoW 区块链
4. CRDT G-Counter（无冲突合并）

运行：
    python reliable_dist.py
"""
from __future__ import annotations
import hashlib
import random
from dataclasses import dataclass, field


# ============ 1. Multi-Paxos ============

class PaxosAcceptor:
    """
    Paxos Acceptor — 维护 per-slot 状态。
    每个槽位 (slot) 独立跟踪 accepted (ballot, value)，
    使得 Multi-Paxos 可以对不同的命令独立达成共识。
    """

    def __init__(self, acceptor_id: int):
        self.id = acceptor_id
        self.promised_ballot: int = -1
        self.accepted: dict[int, tuple[int, object]] = {}  # slot -> (ballot, value)

    def prepare(self, slot: int, n: int):
        """Phase 1: Promise not to accept ballots < n for this slot."""
        if n > self.promised_ballot:
            self.promised_ballot = n
        if slot in self.accepted:
            return ("promise", n, self.accepted[slot])
        return ("promise", n, None)

    def accept(self, slot: int, n: int, value):
        """Phase 2: Accept (n, value) for this slot if n >= promised."""
        if n >= self.promised_ballot:
            self.accepted[slot] = (n, value)
            return ("accepted", n)
        return ("rejected", self.promised_ballot)


class PaxosProposer:
    """Paxos Proposer (Leader) — drives consensus for a specific slot."""

    def __init__(self, proposer_id: int, acceptors: list[PaxosAcceptor]):
        self.id = proposer_id
        self.acceptors = acceptors
        self.ballot = 0

    def propose(self, slot: int, value):
        """Phase 1 (Prepare) + Phase 2 (Accept) for a specific slot."""
        self.ballot += 1
        b = self.ballot

        # Phase 1: Prepare
        promises = 0
        highest_accepted = (-1, None)
        for acc in self.acceptors:
            resp = acc.prepare(slot, b)
            if resp[0] == "promise":
                promises += 1
                if resp[2] is not None:
                    ab, av = resp[2]
                    if ab > highest_accepted[0]:
                        highest_accepted = (ab, av)

        majority = len(self.acceptors) // 2 + 1
        if promises < majority:
            return None  # 未获多数 promise

        # 用该 slot 已接受的最高 ballot 的值（如有），否则用新值
        val = highest_accepted[1] if highest_accepted[1] is not None else value

        # Phase 2: Accept
        accepted = 0
        for acc in self.acceptors:
            resp = acc.accept(slot, b, val)
            if resp[0] == "accepted":
                accepted += 1

        if accepted >= majority:
            return val
        return None


class MultiPaxos:
    """Multi-Decree Paxos (复制状态机) — 每条命令对应一个独立 slot。"""

    def __init__(self, n_acceptors: int = 5):
        self.acceptors = [PaxosAcceptor(i) for i in range(n_acceptors)]
        self.proposer = PaxosProposer(0, self.acceptors)
        self.log: list[object] = []   # 已决定的值序列（按 slot 顺序）
        self.next_slot = 0

    def commit(self, value) -> bool:
        """提交一个命令到日志（在新 slot 上运行 Paxos）。"""
        slot = self.next_slot
        result = self.proposer.propose(slot, value)
        if result is not None:
            self.log.append(result)
            self.next_slot += 1
            return True
        return False


# ============ 2. PBFT (简化) ============

class PBFTNode:
    """
    PBFT 节点：3f+1 个副本，容忍 f 个拜占庭节点
    三阶段：pre-prepare -> prepare -> commit
    """

    def __init__(self, node_id: int, n: int):
        self.id = node_id
        self.n = n
        self.f = (n - 1) // 3
        self.sequence = 0
        self.pre_prepares: dict[int, tuple] = {}  # seq -> (request, view)
        self.prepares: dict[int, set] = {}  # seq -> set of node ids
        self.commits: dict[int, set] = {}
        self.decided: dict[int, object] = {}

    def pre_prepare(self, request, view: int = 0):
        self.sequence += 1
        seq = self.sequence
        self.pre_prepares[seq] = (request, view)
        self.prepares[seq] = set()
        self.commits[seq] = set()
        return seq

    def receive_prepare(self, seq: int, from_node: int):
        if seq in self.prepares:
            self.prepares[seq].add(from_node)

    def can_commit(self, seq: int) -> bool:
        """达到 2f+1 个 prepare 消息"""
        return seq in self.prepares and len(self.prepares[seq]) >= 2 * self.f + 1

    def receive_commit(self, seq: int, from_node: int):
        if seq in self.commits:
            self.commits[seq].add(from_node)

    def is_decided(self, seq: int) -> bool:
        """达到 2f+1 个 commit 消息"""
        return seq in self.commits and len(self.commits[seq]) >= 2 * self.f + 1


def simulate_pbft(n: int = 4, f: int = 1):
    """模拟 PBFT 共识"""
    nodes = [PBFTNode(i, n) for i in range(n)]
    primary = nodes[0]
    request = "transfer $100"

    # Phase 1: Pre-prepare
    seq = primary.pre_prepare(request)
    for node in nodes[1:]:
        node.pre_prepares[seq] = (request, 0)
        node.prepares[seq] = set()
        node.commits[seq] = set()

    # Phase 2: Prepare (所有副本互相发 prepare)
    for node in nodes[1:]:
        for other in nodes:
            other.receive_prepare(seq, node.id)

    # Phase 3: Commit
    for node in nodes:
        for other in nodes:
            other.receive_commit(seq, node.id)

    decided = sum(1 for node in nodes if node.is_decided(seq))
    return seq, decided, n, f


# ============ 3. PoW 区块链 ============

@dataclass
class Block:
    index: int
    data: str
    prev_hash: str
    nonce: int = 0
    hash: str = ""

    def compute_hash(self, difficulty: int = 3) -> str:
        target = "0" * difficulty
        while True:
            content = f"{self.index}{self.data}{self.prev_hash}{self.nonce}"
            h = hashlib.sha256(content.encode()).hexdigest()
            if h.startswith(target):
                return h
            self.nonce += 1


class SimpleBlockchain:
    def __init__(self, difficulty: int = 3):
        self.difficulty = difficulty
        self.chain: list[Block] = []
        # 创世块
        genesis = Block(0, "Genesis", "0" * 64)
        genesis.hash = genesis.compute_hash(difficulty)
        self.chain.append(genesis)

    def add_block(self, data: str) -> Block:
        prev = self.chain[-1]
        block = Block(len(self.chain), data, prev.hash)
        block.hash = block.compute_hash(self.difficulty)
        self.chain.append(block)
        return block

    def verify(self) -> bool:
        for i in range(1, len(self.chain)):
            if self.chain[i].prev_hash != self.chain[i - 1].hash:
                return False
            target = "0" * self.difficulty
            if not self.chain[i].hash.startswith(target):
                return False
        return True


# ============ 4. CRDT G-Counter ============

class GCounter:
    """
    Grow-only Counter (state-based CRDT)
    每个副本维护自己的计数器，合并时取 max
    """

    def __init__(self, node_id: int, n_nodes: int):
        self.node_id = node_id
        self.counts = [0] * n_nodes

    def increment(self):
        self.counts[self.node_id] += 1

    def value(self) -> int:
        return sum(self.counts)

    def merge(self, other: 'GCounter'):
        """合并：取每个位置 max"""
        for i in range(len(self.counts)):
            self.counts[i] = max(self.counts[i], other.counts[i])


# ============ Demo ============

def demo():
    print("=" * 60)
    print("Reliable Distributed Systems: Paxos+PBFT+PoW+CRDT")
    print("=" * 60)
    random.seed(42)

    # 1. Multi-Paxos
    print("\n[1] Multi-Paxos (per-slot 状态)")
    mp = MultiPaxos(n_acceptors=5)
    commands = ["SET x=1", "SET y=2", "SET z=3", "DELETE a"]
    for cmd in commands:
        ok = mp.commit(cmd)
        print(f"   commit('{cmd}'): {'ok' if ok else 'FAIL'}")
    print(f"   复制日志: {mp.log}")
    all_distinct = len(set(mp.log)) == len(mp.log)
    print(f"   所有命令互不相同: {all_distinct} ({len(set(mp.log))} unique / {len(mp.log)} total)")
    # 验证所有 acceptor 对每个 slot 一致
    consistent = True
    for slot in range(len(commands)):
        vals = [acc.accepted.get(slot, (None, None))[1] for acc in mp.acceptors]
        if len(set(repr(v) for v in vals)) != 1:
            consistent = False
    print(f"   所有 acceptor 每个 slot 一致: {'ok' if consistent else 'FAIL'}")

    # 2. PBFT
    print("\n[2] PBFT (n=4, f=1)")
    seq, decided, n, f = simulate_pbft(n=4, f=1)
    print(f"   n={n}, f={f}, 需要 3f+1={3*f+1} 个副本")
    print(f"   seq={seq}, 达成决定: {decided}/{n} (需要 2f+1={2*f+1})")
    print(f"   容忍: {'ok' if decided >= 2*f+1 else 'FAIL'}")

    # 3. PoW 区块链
    print("\n[3] PoW 区块链")
    bc = SimpleBlockchain(difficulty=3)
    for data in ["tx1", "tx2", "tx3"]:
        block = bc.add_block(data)
        print(f"   Block {block.index}: data='{block.data}', nonce={block.nonce}, hash={block.hash[:16]}...")
    print(f"   链验证: {'ok' if bc.verify() else 'FAIL'}")

    # 4. CRDT
    print("\n[4] CRDT G-Counter")
    c1 = GCounter(0, 3)  # 副本 0
    c2 = GCounter(1, 3)  # 副本 1
    for _ in range(5):
        c1.increment()
    for _ in range(3):
        c2.increment()
    print(f"   副本0: {c1.value()}, 副本1: {c2.value()}")
    c1.merge(c2)
    c2.merge(c1)
    print(f"   合并后: 副本0={c1.value()}, 副本1={c2.value()}, 一致={c1.value()==c2.value()}")

    # 反直觉
    print("\n[*] 反直觉发现：PBFT vs Paxos 的副本代价")
    print(f"   Paxos (crash fault): 需要 2f+1 副本容忍 f 个崩溃")
    print(f"   PBFT (byzantine):   需要 3f+1 副本容忍 f 个拜占庭")
    print(f"   拜占庭代价 = 3f+1 vs 2f+1 approx 1.5x (非 3x!)")
    print()
    print(f"   f | Paxos(2f+1) | PBFT(3f+1) | 比值")
    print(f"   --+-------------+------------+-----")
    for ff in [1, 2, 3, 4]:
        paxos = 2 * ff + 1
        pbft = 3 * ff + 1
        ratio = pbft / paxos
        print(f"   {ff} |     {paxos:>2}     |     {pbft:>2}    | {ratio:.2f}x")
    print()
    print(f"   -> 拜占庭容错的代价是约 50% 额外副本，不是 3 倍。")
    print(f"   这就是为什么联盟链 (PBFT) 比公链 (PoW) 快得多：不需要算力竞争。")

    print("\n[done] Reliable Distributed Systems 完成!")


if __name__ == "__main__":
    demo()
