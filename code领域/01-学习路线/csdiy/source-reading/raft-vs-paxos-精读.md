# Raft vs Paxos 对比精读：共识算法的简洁性之争

> Paxos 难到 Google 的工程师都说" chew on glass "。Raft 为了"可理解性"而生。
>
> csdiy 对应：tinyraft + mit6.824 lab + db §二(锁/两阶段)

---

## 一、共识问题

N 个节点，如何在网络分区/节点崩溃的情况下，对**同一个值**达成一致？

应用场景：
- Leader 选举（谁当 leader？）
- 日志复制（操作顺序一致？）
- 分布式锁（谁拿到锁？）
- 配置管理（配置变更生效？）

---

## 二、Paxos：经典但难懂

### Classic Paxos（单值共识）

三个角色：
- **Proposer**：提出提案（"我建议 value=X"）
- **Acceptor**：投票接受/拒绝提案
- **Learner**：学习最终决定的值

```
Phase 1: Prepare
  Proposer → Acceptor: "Prepare(n)"  // n = 提案编号
  Acceptor: 如果 n > 已见过的最大编号 → 承诺"不再接受 <n 的提案"

Phase 2: Accept
  Proposer → Acceptor: "Accept(n, value)"
  Acceptor: 如果 n >= 已承诺的编号 → 接受 value
  多数 Acceptor 接受 → value 被选定
```

### 为什么 Paxos 难

1. **单值**：Classic Paxos 只对一个值达成共识。实际系统需要连续的值（日志）→ Multi-Paxos
2. **Multi-Paxos 无标准实现**：论文只给了概念，具体怎么映射到日志复制由实现者决定
3. **Leader 优化是可选的**：Paxos 可以无 Leader（更复杂），也可以有 Leader（就是 Multi-Paxos 的常见优化）
4. **论文写得抽象**：Lamport 用"岛屿/议会"比喻，很多人看了更晕

Google 的 Tushar Chandra 在 Paxos Made Live 中说：
> *"While Paxos provided a solid foundation, converting it into a practical system required significant engineering effort."*

---

## 三、Raft：为了可理解性而生

Diego Ongaro 在 Raft 论文（2014）的开篇就说：
> *"Raft is a consensus algorithm for managing a replicate log, designed as a foundation for practical systems. Its main innovation is its decomposed structure."*

### Raft 的三个子问题

1. **Leader 选举**：选一个 Leader
2. **日志复制**：Leader 接收命令 → 复制到 followers → commit
3. **安全性**：保证已 commit 的日志不会丢失

### Raft 的设计选择（对比 Paxos）

| 设计选择 | Paxos | Raft | 为什么 |
|---------|-------|------|--------|
| 强 Leader | 可选 | 必须 | 简化客户端路由 |
| 日志结构 | 无标准 | 连续有序 | 状态机复制 |
| 成员变更 | 复杂 | 联合共识（joint consensus） | 安全的在线变更 |
| 选举 | 复杂 | 随机超时 | 简单避免活锁 |

---

## 四、核心对比

| 维度 | Paxos | Raft |
|------|-------|------|
| 复杂度 | 极高 | 中等 |
| 论文 | 1998（The Part-Time Parliament） | 2014（In Search of an Understandable Consensus Algorithm） |
| 角色 | Proposer/Acceptor/Learner | Leader/Follower/Candidate |
| 日志 | 无标准 | 有序追加 |
| Leader | 可选 | 必须 |
| 选举 | 复杂（可能活锁） | 随机超时（简单） |
| 成员变更 | 复杂 | joint consensus |
| 实现 | Chubby(Spanner) | etcd/TiKV/Consul |
| 可理解性 | "像嚼玻璃" | "本科生能懂" |

### 选举的简洁性

**Paxos** 选举可能活锁（多个 Proposer 不断用更高编号互相抢占）。

**Raft** 用**随机超时**解决：
```
每个节点有随机超时 150-300ms
超时 → 变 Candidate → 向所有节点要票
多数同意 → 成为 Leader

随机性保证：两个 Candidate 几乎不会同时超时 → 活锁概率极低
```

### 日志的连续性

**Paxos**：每个 log entry 独立 Paxos 实例（互相不知道）。

**Raft**：日志连续追加，有**日志匹配属性**：
```
如果两个日志 entry 在同一个 index 且 term 相同 → 它们的命令相同
且之前所有 entry 也相同
```

这保证了：一旦 Leader commit 了某 entry → 所有未来 Leader 的日志都包含它。

---

## 五、Multi-Paxos ≈ Raft

实际上，**Multi-Paxos 加上 Leader 优化 + 连续日志 ≈ Raft**。

区别在于：
- Multi-Paxos 是"概念框架"（没有标准实现）
- Raft 是"工程规格"（有精确定义的实现）

```
Paxos 论文 → 你自己想怎么映射到日志复制
Raft 论文 → 逐条规则告诉你怎么实现 → 甚至有伪代码
```

---

## 六、和 tinyraft 的交叉

你的 tinyraft 实现了 Raft 的核心：
- ✅ Leader 选举（随机超时 + RequestVote）
- ✅ 心跳（AppendEntries with empty entries）
- ✅ 日志复制（AppendEntries with entries）
- ❌ 未实现：日志匹配检查 + commit 规则 + Snapshot

**如果你想深化 tinyraft**：
```python
# 日志匹配检查（参照 Raft paper §5.3）
def append_entries(self, msg):
    # 检查 prevLogIndex 和 prevLogTerm
    if msg["prevLogIndex"] >= len(self.log):
        return {"success": False, "reason": "log too short"}
    if self.log[msg["prevLogIndex"]].term != msg["prevLogTerm"]:
        return {"success": False, "reason": "term mismatch"}
    # 日志匹配 → 追加新 entries
    for entry in msg["entries"]:
        ...
```

---

## 七、一句话总结

> Paxos 证明了"共识是可能的"，Raft 证明了"共识可以是可理解的"。
>
> Multi-Paxos + Leader 优化 ≈ Raft。区别在于 Raft 是工程规格（有精确实现），Paxos 是概念框架（实现者自由发挥）。
>
> **etcd/TiKV/Consul 全选 Raft。** Google Spanner/Chubby 用 Paxos（因为 Raft 出现前它们就在了）。

---

*配套：[tinyraft](../projects/tinyraft/) | [mit6.824 lab](../labs/mit6.824-raft-从零跑起来.md)*
