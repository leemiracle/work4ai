# 网络系统整合 · Stanford CS144 × Berkeley CS162 × 路由(OSPF/BGP)

> 用 **mini-TCP 项目**理解可靠传输，用 **路由协议**理解数据包的旅程。
> 核心：自己造一遍 TCP + 理解 OSPF/BGP，打通"传输层 + 网络层"全栈。

---

## 🎯 为什么整合这三块？

| 来源 | 教什么 | 核心问题 |
|---|---|---|
| **Stanford CS144** | 自己实现一个 TCP（5 个 milestone） | 如何在不可靠 IP 上造可靠字节流？ |
| **Berkeley CS162** | 网络栈如何融入操作系统 | socket → 内核 → 网卡整条链怎么走？ |
| **路由（OSPF/BGP）** | 数据包如何找到路 | 域内 Dijkstra vs 域间路径矢量 |

> **核心洞察**：CS144 给你"造"（手写 TCP），CS162 给你"接"（接入 OS），路由给你"路"（怎么送达）。

---

## 📦 模块内容

| 文件 | 主题 | 核心机制 | 可跑演示 |
|---|---|---|---|
| [`mini_tcp.py`](mini_tcp.py) | TCP 实现（CS144 风格） | 字节流重组 / 三次握手 / 累积ACK重传 / AIMD拥塞控制 | 注入丢包观察重传 |
| [`routing.py`](routing.py) | 路由协议（OSPF + BGP） | 链路状态Dijkstra / 路径矢量AS_PATH | 6路由器拓扑 + 5AS传播 |

零依赖，纯标准库。

---

## 🧩 mini-TCP 的 7 个 Part

对应 CS144 的 5 个 milestone + CS162 系统视角：

| Part | 内容 | CS144 对应 |
|---|---|---|
| 0 | 为什么需要 TCP？（IP 不可靠） | — |
| 1 | 字节流重组器 StreamReassembler | M1 |
| 2 | TCP Segment + 不可靠网络模拟 | — |
| 3 | TCP Sender（序列号 + 累积ACK + 重传） | M2/M3 |
| 4 | 三次握手 + 数据传输 + 丢包重传 | M4 |
| 5 | 拥塞控制（慢启动 / 拥塞避免 / AIMD） | M5 |
| 6 | 端到端完整模拟（送 'Hello, TCP!'） | 全部串起来 |
| 7 | Berkeley CS162 系统视角（socket→网卡） | CS162 |

---

## 🔴 三个必懂的"反直觉"点

1. **TCP 序列号是字节偏移，不是包编号** — `seq=1003` 指"本段数据从字节流的第 1003 字节开始"。这是 CS144 反复强调的核心。
2. **绕路可能更近** — OSPF 里 R1→R3 直连代价 4，但绕道 R1→R2(1)→R3(2)=3 反而更便宜。人眼容易看错，Dijkstra 不会。
3. **BGP 不一定走最短路** — 域间路由靠**策略**（AS_PATH/LOCAL_PREF），可能故意走长路（商业协议、避免经过竞争对手 AS）。

---

## 🚀 快速开始

```bash
cd network-systems

# 先看 mini-TCP（核心项目）
python3 mini_tcp.py

# 再看路由协议
python3 routing.py
```

**mini-TCP 可交互修改**：改 `LossyChannel(loss_indices={...})` 注入不同丢包，观察重传和拥塞控制行为变化。

---

## 📅 学习路径（2 周速成）

| 周 | 做什么 | 产出 |
|---|---|---|
| **W1** | 跑 `mini_tcp.py` 7 个 Part + CS144 的 C++ project M1-M3 | 手写过重组器、Sender、握手 |
| **W2** | CS144 M4/M5（连接管理+拥塞控制）+ 跑 `routing.py` + traceroute 实战 | 能解释 ping 8.8.8.8 的每一跳 |

---

## 🔗 与其他模块的衔接

| 想深入 | 去这里 |
|---|---|
| Dijkstra 算法本身（OSPF 的核心） | `../algorithms/algo_integration.py` Part 3 |
| 数据库的 MVCC/事务（和 TCP 的可靠传输思想相通） | `../database-systems/db_integration.py` Part 2 |
| 各校完整网络课程 | `../mit-cs-projects/` `../cmu-cs-projects/` |

---

## 📚 核心资料

| 资料 | 来源 | 用途 |
|---|---|---|
| CS144 TCP project（C++ + SST） | Stanford | 真正实现一个能联网的 TCP |
| CS162 Lecture（Networking） | Berkeley | 理解网络栈与 OS 的关系 |
| RFC 793（TCP）/ RFC 4271（BGP）/ RFC 2328（OSPF） | IETF | 协议权威定义 |
| Kurose & Ross《Computer Networking》 | 教材 | 系统入门 |
