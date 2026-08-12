"""
6.5840/6.824 Distributed Systems（MIT, Kaashoek）
================================================
覆盖主题：
- MapReduce wordcount（Lab 1）
- GFS-style chunk 管理（Lab 2 背景）
- Raft 日志复制 mini（Lab 3-4 核心）
- Paxos multi-instance（经典共识）
- 线性一致 KV store

核心论文（经典，无 arXiv ID）：
- Lamport 1998 "The Part-Time Parliament" ACM TOCS (Paxos)
- Ongaro & Ousterhout 2014 "In Search of an Understandable Consensus Algorithm" USENIX ATC (Raft)
- Dean & Ghemawat 2004 "MapReduce: Simplified Data Processing on Large Clusters" OSDI
- Ghemawat, Gobioff, Leung 2003 "The Google File System" SOSP
- Herlihy & Wing 1990 "Linearizability: A Correctness Condition for Concurrent Objects" ACM TOPLAS

本文件实现：
- MapReduce wordcount（map→shuffle→reduce 全流程）
- GFS-style chunk 分配 + 副本
- Raft leader election + log append mini
- Paxos Prepare/Promise/Accept/Ack 状态机
- 线性一致性 KV（顺序记录）

运行：
    python distributed.py
"""
from __future__ import annotations
import random
from dataclasses import dataclass, field


# ============ 1. MapReduce ============

def map_wordcount(doc: str) -> list[tuple[str, int]]:
    """Map: 文档 → (word, 1) 列表"""
    return [(w.lower().strip('.,!?;:"()[]'), 1) for w in doc.split()]


def shuffle(pairs: list[tuple]) -> dict[str, list[int]]:
    """Shuffle: 按 key 聚合"""
    grouped = {}
    for k, v in pairs:
        grouped.setdefault(k, []).append(v)
    return grouped


def reduce_sum(key: str, values: list[int]) -> tuple[str, int]:
    """Reduce: key, [1,1,...] → key, sum"""
    return key, sum(values)


def mapreduce_wordcount(docs: list[str]) -> dict[str, int]:
    """完整 MapReduce wordcount"""
    mapped = []
    for doc in docs:
        mapped.extend(map_wordcount(doc))
    shuffled = shuffle(mapped)
    results = {}
    for k, vs in shuffled.items():
        results[k] = reduce_sum(k, vs)[1]
    return dict(sorted(results.items(), key=lambda x: -x[1]))


# ============ 2. GFS-style Chunk Server ============

@dataclass
class Chunk:
    chunk_id: str
    data: bytes
    replicas: list[str] = field(default_factory=list)  # chunkserver 地址


class GFSMaster:
    """GFS Master: 管理文件→chunk 映射 + 副本位置"""
    def __init__(self, chunk_size: int = 64, num_replicas: int = 3, num_chunkservers: int = 5):
        self.chunk_size = chunk_size
        self.num_replicas = num_replicas
        self.chunkservers = [f"CS{i}" for i in range(num_chunkservers)]
        self.file_table: dict[str, list[str]] = {}  # file -> [chunk_id]
        self.chunk_locations: dict[str, list[str]] = {}  # chunk_id -> [CS addrs]
        self.next_chunk = 0

    def create(self, filename: str, data: bytes) -> int:
        """写入文件：分 chunk + 分配副本"""
        chunk_ids = []
        offset = 0
        while offset < len(data):
            cid = f"chunk_{self.next_chunk}"; self.next_chunk += 1
            chunk_data = data[offset:offset + self.chunk_size]
            # 随机选 replicas 个 chunkserver
            replicas = random.sample(self.chunkservers, min(self.num_replicas, len(self.chunkservers)))
            self.chunk_locations[cid] = replicas
            chunk_ids.append(cid)
            offset += self.chunk_size
        self.file_table[filename] = chunk_ids
        return len(chunk_ids)

    def stat(self, filename: str):
        cids = self.file_table.get(filename, [])
        total_replicas = sum(len(self.chunk_locations[c]) for c in cids)
        return len(cids), total_replicas


# ============ 3. Raft Leader Election + Log ============

@dataclass
class RaftNode:
    node_id: int
    term: int = 0
    voted_for: int | None = None
    state: str = "follower"  # follower | candidate | leader
    log: list[tuple] = field(default_factory=list)  # [(term, cmd), ...]
    commit_index: int = -1


def raft_election(nodes: list[RaftNode], candidate_id: int) -> bool:
    """模拟一次 Raft 选举"""
    cand = nodes[candidate_id]
    cand.state = "candidate"
    cand.term += 1
    cand.voted_for = candidate_id
    votes = 1
    for n in nodes:
        if n.node_id == candidate_id:
            continue
        # 节点投票条件：候选者 term >= 自己 term 且未投过票（或投给同一人）
        if (n.voted_for is None or n.voted_for == candidate_id) and n.term <= cand.term:
            n.voted_for = candidate_id
            n.term = cand.term
            votes += 1
    majority = len(nodes) // 2 + 1
    if votes >= majority:
        cand.state = "leader"
        for n in nodes:
            if n.node_id != candidate_id:
                n.state = "follower"
        return True
    cand.state = "follower"
    return False


def raft_append(leader: RaftNode, nodes: list[RaftNode], cmd: str) -> int:
    """Leader 追加日志 + 复制到多数派"""
    leader.log.append((leader.term, cmd))
    idx = len(leader.log) - 1
    # 模拟复制
    replicated = 1
    for n in nodes:
        if n is leader:
            continue
        n.log.append((leader.term, cmd))
        replicated += 1
    majority = len(nodes) // 2 + 1
    if replicated >= majority:
        leader.commit_index = idx
        for n in nodes:
            n.commit_index = max(n.commit_index, idx)
    return idx


# ============ 4. Paxos Multi-Instance ============

class PaxosAcceptor:
    """Paxos Acceptor"""
    def __init__(self, aid):
        self.aid = aid
        self.promised_n = -1
        self.accepted_n = -1
        self.accepted_v = None

    def prepare(self, n: int):
        if n > self.promised_n:
            self.promised_n = n
            return True, self.accepted_n, self.accepted_v
        return False, None, None

    def accept(self, n: int, v):
        if n >= self.promised_n:
            self.promised_n = n
            self.accepted_n = n
            self.accepted_v = v
            return True
        return False


def paxos_run(acceptors: list[PaxosAcceptor], proposer_id: int, value) -> any:
    """单实例 Paxos。返回 chosen value（可能是之前已选的）。"""
    n = proposer_id
    # Phase 1: Prepare
    promises = 0
    highest_accepted = (-1, None)
    for acc in acceptors:
        ok, an, av = acc.prepare(n)
        if ok:
            promises += 1
            if an > highest_accepted[0] and av is not None:
                highest_accepted = (an, av)
    majority = len(acceptors) // 2 + 1
    if promises < majority:
        return None
    # 如果有人已 accept 过，必须用那个值（Paxos 安全性）
    propose_v = highest_accepted[1] if highest_accepted[1] is not None else value
    # Phase 2: Accept
    accepts = 0
    for acc in acceptors:
        if acc.accept(n, propose_v):
            accepts += 1
    if accepts >= majority:
        return propose_v
    return None


# ============ 5. Linearizable KV Store ============

class LinearKVStore:
    """线性一致 KV：所有操作串行化到一个 log。"""
    def __init__(self):
        self.data = {}
        self.log = []  # 操作历史（线性化序列）

    def put(self, key, val, client_id=0):
        self.log.append(('PUT', key, val, client_id))
        self.data[key] = val

    def get(self, key, client_id=0):
        v = self.data.get(key, None)
        self.log.append(('GET', key, v, client_id))
        return v

    def cas(self, key, expected, new_val, client_id=0):
        """Compare-And-Set：线性一致的核心原子操作"""
        old = self.data.get(key)
        self.log.append(('CAS', key, expected, new_val, old, client_id))
        if old == expected:
            self.data[key] = new_val
            return True, old
        return False, old


# ============ Demo ============

def demo():
    print("=" * 65)
    print("6.824 Distributed Systems: MapReduce/GFS/Raft/Paxos")
    print("=" * 65)
    random.seed(42)

    # --- MapReduce ---
    print("\n📋 1. MapReduce WordCount")
    docs = [
        "the quick brown fox jumps",
        "the lazy dog the fox sees",
        "quick brown quick dog runs",
    ]
    result = mapreduce_wordcount(docs)
    print(f"  文档 {len(docs)} 篇，词频 Top 5:")
    for w, c in list(result.items())[:5]:
        bar = '#' * c
        print(f"    {w:<8} {c} {bar}")

    # --- GFS ---
    print("\n📋 2. GFS-style Chunk 分配")
    master = GFSMaster(chunk_size=16, num_replicas=3, num_chunkservers=5)
    data = b"Hello GFS distributed file system " * 5
    n_chunks, n_replicas = master.create("test.log", data), None
    n_chunks, n_replicas = master.stat("test.log")
    print(f"  文件大小 {len(data)} bytes → {n_chunks} chunks")
    print(f"  总副本数 {n_replicas} (期望 3/chunk)")
    print(f"  chunk 分布:")
    for cid in master.file_table["test.log"]:
        locs = master.chunk_locations[cid]
        print(f"    {cid}: {locs}")

    # --- Raft ---
    print("\n📋 3. Raft Leader Election + Log Replication")
    nodes = [RaftNode(i) for i in range(5)]
    won = raft_election(nodes, 2)  # node 2 发起选举
    leader = next(n for n in nodes if n.state == "leader")
    print(f"  5 节点集群, node 2 当选: {won}, leader={leader.node_id}")
    for n in nodes:
        print(f"    node{n.node_id}: state={n.state}, term={n.term}")
    raft_append(leader, nodes, "SET x=1")
    raft_append(leader, nodes, "SET y=2")
    raft_append(leader, nodes, "SET x=3")
    print(f"  追加 3 条命令后:")
    for n in nodes:
        print(f"    node{n.node_id}: log_len={len(n.log)}, commit={n.commit_index}")

    # --- Paxos ---
    print("\n📋 4. Paxos Multi-Instance 共识")
    acceptors = [PaxosAcceptor(i) for i in range(5)]
    chosen = paxos_run(acceptors, proposer_id=10, value="command_A")
    print(f"  Round 1: proposer#10 提议 'command_A' → chosen={chosen}")
    # 第二个 proposer 提议不同值，但应学到已选值
    chosen2 = paxos_run(acceptors, proposer_id=20, value="command_B")
    print(f"  Round 2: proposer#20 提议 'command_B' → chosen={chosen2}")
    print(f"  → Paxos 保证已决议的值不会被覆盖（安全性）")

    # --- Linearizable KV ---
    print("\n📋 5. 线性一致 KV Store")
    kv = LinearKVStore()
    kv.put("x", 0, client_id="C1")
    ok, old = kv.cas("x", 0, 1, client_id="C1")
    print(f"  C1: CAS(x, 0→1) = {ok} (old={old})")
    ok, old = kv.cas("x", 0, 2, client_id="C2")  # 应失败，x 已是 1
    print(f"  C2: CAS(x, 0→2) = {ok} (old={old}) ← 并发冲突，CAS 失败")
    print(f"  操作日志（线性化序列）: {len(kv.log)} 条")

    # --- 反直觉发现 ---
    print("\n" + "=" * 65)
    print("💡 反直觉发现：Paxos/Raft 不需要'所有'节点同意，只需'多数派'")
    print("=" * 65)
    for n_nodes in [3, 5, 7, 9, 11]:
        majority = n_nodes // 2 + 1
        tolerates = n_nodes - majority
        print(f"  {n_nodes} 节点: 需 {majority} 票, 可容忍 {tolerates} 个故障 "
              f"({tolerates/n_nodes:.0%} 容错)")
    print("  → 3 节点容忍 1 故障（33%），但 2 节点容忍 0 故障——")
    print("    多 1 个节点的边际价值巨大。这就是为什么 Raft/Paxos 部署"
           "总是奇数节点。")

    print("\n✅ 6.824 Demo 完成！")


if __name__ == "__main__":
    demo()
