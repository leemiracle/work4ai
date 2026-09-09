#!/usr/bin/env python3
"""
tinygossip — 参照 Cassandra/Serf 的 Gossip 协议

参照：Cassandra Gossip / HashiCorp Serf / SWIM 协议
csdiy 对应：tinyraft + 分布式

核心：每个节点定期和随机邻居交换状态信息 → 最终一致
"""
import asyncio, random, time
from dataclasses import dataclass, field

@dataclass
class NodeState:
    """节点状态（参照 Cassandra Gossiper.EndpointState）"""
    name: str
    status: str = "ALIVE"   # ALIVE / SUSPECT / DEAD
    heartbeat: int = 0
    timestamp: float = field(default_factory=time.time)
    meta: dict = field(default_factory=dict)

class GossipNode:
    """
    Gossip 节点（参照 Cassandra SeedsGossiper）

    核心循环（每秒一次）：
    1. 随机选 1-3 个邻居
    2. 发送自己的状态表
    3. 接收对方的状态表 → 合并（取更新的）
    → 最终所有节点知道所有节点的状态
    """
    def __init__(self, name, seed_nodes=None):
        self.name = name
        self.nodes: dict[str, NodeState] = {}
        self.nodes[name] = NodeState(name=name, heartbeat=1)
        self.peers = seed_nodes or []
        self.msg_count = 0

    def heartbeat_tick(self):
        """心跳递增（每秒调用）"""
        self.nodes[self.name].heartbeat += 1
        self.nodes[self.name].timestamp = time.time()

    def gossip_exchange(self, other):
        """和另一个节点交换状态（参照 Cassandra GossipDigestSyn）"""
        self.msg_count += 2  # 发送 + 接收
        # 合并：对每个 key，取 heartbeat 更大的版本
        updated = 0
        for name, state in other.nodes.items():
            existing = self.nodes.get(name)
            if not existing or state.heartbeat > existing.heartbeat:
                self.nodes[name] = NodeState(
                    name=state.name, status=state.status,
                    heartbeat=state.heartbeat, timestamp=state.timestamp,
                    meta=state.meta.copy()
                )
                updated += 1
        return updated

    def fail_node(self, name):
        """标记节点为故障（参照 Cassandra markAsShutdown）"""
        if name in self.nodes:
            self.nodes[name].status = "DEAD"

    def random_gossip(self):
        """随机选邻居交换"""
        alive_peers = [p for p in self.peers if p != self.name]
        if not alive_peers:
            return None
        return random.choice(alive_peers)

    def cluster_view(self):
        return {name: {"status": s.status, "heartbeat": s.heartbeat}
                for name, s in self.nodes.items()}

def main():
    print("tinygossip — Gossip 协议（参照 Cassandra/Serf）\n")

    # 创建 5 个节点
    nodes = [GossipNode(f"node{i}") for i in range(5)]
    # 设置彼此为 peer
    for node in nodes:
        node.peers = [n.name for n in nodes]

    # node0 知道所有节点的初始状态
    for n in nodes:
        nodes[0].nodes[n.name] = NodeState(name=n.name, heartbeat=1)

    print("  初始状态: 只有 node0 知道全部 5 个节点")
    for n in nodes:
        print(f"    {n.name}: knows {list(n.nodes.keys())}")

    # 模拟 Gossip 轮次
    for tick in range(15):
        for node in nodes:
            node.heartbeat_tick()

        # 每个节点和随机邻居交换
        for node in nodes:
            target_name = node.random_gossip()
            if target_name:
                target_idx = int(target_name.replace("node", ""))
                target = nodes[target_idx]
                node.gossip_exchange(target)

    print(f"\n  15 轮 Gossip 后:")
    for n in nodes:
        known = list(n.nodes.keys())
        print(f"    {n.name}: knows {known}")

    # 模拟节点故障
    print(f"\n  node3 宕机！")
    for n in nodes:
        n.fail_node("node3")

    # 继续 Gossip
    for tick in range(10):
        for node in nodes:
            if node.name != "node3":
                node.heartbeat_tick()
                target_name = node.random_gossip()
                if target_name:
                    target = nodes[int(target_name.replace("node",""))]
                    if target.name != "node3":
                        node.gossip_exchange(target)

    print(f"\n  10 轮后（node3 宕机传播）:")
    for n in nodes:
        view = n.cluster_view()
        node3_status = view.get("node3", {}).get("status", "unknown")
        print(f"    {n.name}: node3 = {node3_status}, knows {len(n.nodes)} nodes, msgs={n.msg_count}")

    print(f"\n  Gossip 特点:")
    print(f"    - 最终一致：所有节点最终知道所有节点状态")
    print(f"    - O(log N) 收敛：信息以指数速度传播")
    print(f"    - 容错：节点宕机不影响其他节点的 Gossip")

if __name__ == "__main__": main()
