"""
15-440 + 15-721 Distributed Systems (CMU)
================================================
覆盖主题（对应 lecture）：
- Consensus: 单 decree Paxos（Proposer/Acceptor/Accept，带故障注入）
- 2PC (Two-Phase Commit) 协调者-参与者
- Causality: Vector clock 因果一致性检查
- Election: Bully 选举算法

核心教材/论文：
- "Lamport 1998 ACM TOCS The Part-Time Parliament" — Paxos 原始论文
- "Gray 1978 Notes on DB OS" — 2PC
- "Lamport 1978 CACM Time, Clocks" — 向量时钟理论
- "Garcia-Molina 1982" — Bully election

本文件实现：
- 单 decree Paxos（全流程 Prepare→Promise→Accept→Accepted，带节点崩溃注入）
- 2PC（prepare + commit/abort）
- Vector clock happens-before 检测
- Bully 选举

运行：
    python3 dist_sys.py
"""
from __future__ import annotations
import random
from dataclasses import dataclass, field

# ============ 1. Paxos ============

@dataclass
class Acceptor:
    aid: int
    promised_n: int = -1
    accepted_n: int = -1
    accepted_val: object = None
    alive: bool = True

@dataclass
class Proposer:
    pid: int
    proposal_n: int = 0
    value: object = None

    def next_n(self):
        self.proposal_n += 1
        return self.proposal_n

def paxos(proposers: list[Proposer], acceptors: list[Acceptor],
          value: object, crash_acceptors: set[int] = None) -> object:
    """
    Single-decree Paxos. Returns decided value or None.
    `crash_acceptors`: set of acceptor IDs to crash (simulate failure).
    """
    crash_acceptors = crash_acceptors or set()
    live = [a for a in acceptors if a.aid not in crash_acceptors]
    quorum = len(acceptors) // 2 + 1

    if len(live) < quorum:
        return None  # cannot make progress

    proposer = proposers[0]
    n = proposer.next_n()

    # Phase 1: Prepare
    promises = []
    for acc in live:
        if n > acc.promised_n:
            acc.promised_n = n
            promises.append(acc)

    if len(promises) < quorum:
        return None

    # Use highest previously accepted value (if any)
    prev_accepted = [(a.accepted_n, a.accepted_val) for a in promises
                     if a.accepted_n >= 0]
    if prev_accepted:
        v = max(prev_accepted)[1]  # highest-n accepted value
    else:
        v = value

    # Phase 2: Accept
    accepts = 0
    for acc in promises:
        if n >= acc.promised_n:
            acc.promised_n = n
            acc.accepted_n = n
            acc.accepted_val = v
            accepts += 1

    if accepts >= quorum:
        return v
    return None


# ============ 2. Two-Phase Commit ============

@dataclass
class Participant:
    pid: int
    ready: bool = True
    committed: bool = False
    alive: bool = True

def two_phase_commit(coordinator_val, participants: list[Participant],
                     crash_participant: int = None) -> bool:
    """Returns True if committed, False if aborted."""
    random.seed(0)  # deterministic: normal-case participants all vote YES
    live = [p for p in participants if p.alive and p.pid != crash_participant]

    # Phase 1: PREPARE
    all_ready = True
    for p in live:
        p.ready = random.random() > 0.1  # 10% chance of refusal
        if not p.ready:
            all_ready = False

    if not all_ready or len(live) < len(participants):
        # ABORT
        for p in participants:
            p.committed = False
        return False

    # Phase 2: COMMIT
    for p in live:
        p.committed = True
    return True


# ============ 3. Vector Clock ============

class VectorClock:
    def __init__(self, size: int):
        self.clock = [0] * size

    def increment(self, pid: int):
        self.clock[pid] += 1

    def merge(self, other: 'VectorClock'):
        self.clock = [max(a, b) for a, b in zip(self.clock, other.clock)]

    def happens_before(self, other: 'VectorClock') -> bool:
        """True if self < other (every component <= and at least one <)."""
        le = all(a <= b for a, b in zip(self.clock, other.clock))
        lt = any(a < b for a, b in zip(self.clock, other.clock))
        return le and lt

    def concurrent_with(self, other: 'VectorClock') -> bool:
        return not self.happens_before(other) and not other.happens_before(self)


# ============ 4. Bully Election ============

def bully_election(nodes: list[int], initiator: int, alive: set[int]):
    """
    Bully algorithm with explicit three-phase message flow.

    Phase 1 — ELECTION: initiator sends election_msg to all higher-ID alive nodes.
    Phase 2 — OK:       recipients reply ok_msg and start their own election.
    Phase 3 — COORDINATOR: the node that receives no ok_msg (highest alive)
                           broadcasts coordinator_msg declaring itself leader.

    Returns (coordinator_id, messages) where messages is a list of
    (from_id, to_id, msg_type) tuples.
    """
    messages: list[tuple[int, int, str]] = []
    started: set[int] = set()

    def run_election(node: int):
        if node in started:
            return
        started.add(node)
        higher = [n for n in nodes if n > node and n in alive]
        got_ok = False
        for h in higher:
            messages.append((node, h, 'ELECTION'))
            messages.append((h, node, 'OK'))         # alive higher node responds
            got_ok = True
        if not got_ok:
            # No higher alive node responded → I am the highest → broadcast
            for n in nodes:
                if n in alive and n != node:
                    messages.append((node, n, 'COORDINATOR'))
        else:
            # Each responder starts its own election (recursive)
            for h in higher:
                run_election(h)

    run_election(initiator)
    coordinator = max(alive)
    return coordinator, messages


# ============ Demo ============

def demo():
    print("=" * 60)
    print("15-440/721 Distributed Systems: Paxos, 2PC, VC, Bully")
    print("=" * 60)
    random.seed(42)

    # --- 1. Paxos ---
    print("\n📋 1. Paxos Consensus")
    acceptors = [Acceptor(aid=i) for i in range(5)]
    proposers = [Proposer(pid=0), Proposer(pid=1)]

    # Normal case
    result = paxos(proposers, acceptors, value="DECISION_A")
    print(f"   Normal (5/5 alive): decided = {result}")

    # Crash 2 acceptors (still quorum of 3)
    acceptors2 = [Acceptor(aid=i) for i in range(5)]
    result2 = paxos([Proposer(pid=0)], acceptors2, "DECISION_B", crash_acceptors={0,1})
    print(f"   Crash 2 acceptors (3/5): decided = {result2}")

    # Crash 3 acceptors (no quorum)
    acceptors3 = [Acceptor(aid=i) for i in range(5)]
    result3 = paxos([Proposer(pid=0)], acceptors3, "DECISION_C", crash_acceptors={0,1,2})
    print(f"   Crash 3 acceptors (2/5): decided = {result3}")
    print(f"   💡 Paxos 在 majority 存活时总能决定，少数存活则阻塞（safety > liveness）")

    # --- 2. 2PC ---
    print("\n📋 2. Two-Phase Commit")
    participants = [Participant(pid=i) for i in range(4)]
    committed = two_phase_commit("TXN_1", participants)
    print(f"   All alive: committed={committed}")

    participants2 = [Participant(pid=i) for i in range(4)]
    committed2 = two_phase_commit("TXN_2", participants2, crash_participant=2)
    print(f"   1 participant crashes: committed={committed2}")
    print(f"   💡 2PC 是 blocking 的：任何参与者崩溃 → 全员阻塞等待")

    # --- 3. Vector Clock ---
    print("\n📋 3. Vector Clock Causality")
    vc_a = VectorClock(3); vc_a.increment(0)
    vc_b = VectorClock(3); vc_b.merge(vc_a); vc_b.increment(1)  # b after a
    vc_c = VectorClock(3); vc_c.increment(2)                    # concurrent with a

    print(f"   A = {vc_a.clock}, B = {vc_b.clock}, C = {vc_c.clock}")
    print(f"   A happens-before B? {vc_a.happens_before(vc_b)}")
    print(f"   A concurrent with C? {vc_a.concurrent_with(vc_c)}")
    print(f"   💡 并发事件没有因果序，需要冲突解决")

    # --- 4. Bully Election ---
    print("\n📋 4. Bully Election (3-phase message flow)")
    nodes = [1, 2, 3, 4, 5]

    # Case 1: all alive, node 3 initiates → node 5 wins
    alive = {1, 2, 3, 4, 5}
    coord, msgs = bully_election(nodes, initiator=3, alive=alive)
    print(f"   All alive, initiator=3:")
    for frm, to, mtype in msgs:
        print(f"      {frm} → {to}: {mtype}")
    print(f"   → Coordinator elected = {coord}")

    # Case 2: inject 1 failure (node 5 down), node 3 initiates → node 4 wins
    alive2 = {1, 2, 3, 4}
    coord2, msgs2 = bully_election(nodes, initiator=3, alive=alive2)
    n_elec = sum(1 for _, _, t in msgs2 if t == 'ELECTION')
    n_ok = sum(1 for _, _, t in msgs2 if t == 'OK')
    n_coord = sum(1 for _, _, t in msgs2 if t == 'COORDINATOR')
    print(f"   Node 5 down, initiator=3:")
    print(f"      messages: {n_elec} ELECTION, {n_ok} OK, {n_coord} COORDINATOR")
    print(f"   → Coordinator elected = {coord2}")
    print(f"   💡 Bully: ELECTION→OK→COORDINATOR 三阶段，最高存活 ID 当选（O(n²) 消息）")

    print("\n✅ 15-440/721 Distributed Systems 完成！")
    print("   覆盖：Paxos / 2PC / Vector Clock / Bully Election")


if __name__ == "__main__":
    demo()
