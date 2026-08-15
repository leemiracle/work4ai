# CS144: Introduction to Computer Networking

> **课程官网**: http://cs144.stanford.edu/
> **讲师**: Keith Winstein（Stanford CS 系）
> **学期**: 通常在 Autumn / Winter 开设
> **前置课程**: CS106B / CS107（C++ 编程能力）
> **评分构成**: 8 个编程作业（Labs）+ 期末考试
> **核心语言**: C++（现代 C++17/20，使用 Standard Template Library）
> **项目代码**: `topic9-systems/tcp_sim.py`（Python 教学版 TCP 模拟器）

---

## 📚 课程定位

CS144 是斯坦福大学计算机科学系的核心系统课程之一，由 **Keith Winstein** 教授主讲。与传统网络课程（按 OSI 七层模型从底向上讲授）不同，Winstein 采用**自顶向下（top-down）**的教学方法：从应用层（HTTP）出发，逐层向下剥开网络协议栈，最终到达链路层与物理层。

这门课的核心理念是 **"你亲手实现一个可工作的 TCP/IP 网络"**。学生不是被动背诵协议字段，而是用 C++ 从零构建一个用户态 TCP 实现（Sponge / Minnow），能够真正通过 Linux 的 `/dev/net/tun` 接口与真实的互联网通信——用自己写的 TCP 去下载真实的网页。这种"从构建中学习"（learning by building）的哲学是 CS144 的灵魂。

### 课程特色

- **自顶向下架构**: 应用层 → 传输层 → 网络层 → 链路层，与传统 bottom-up 教学相反
- **动手实现**: 每周一个 Lab，8 个 Lab 串联成一个完整 TCP 实现
- **工程严谨**: 使用 C++ 现代 RAII、智能指针、移动语义，强调内存安全与正确性
- **真实互联**: 最终实现的 TCP 可与真实网络通信
- **无教科书**: Winstein 教授主张从 RFC、源码和实验中学习

---

## 🎯 学习目标

完成本课程后，你将能够：

1. **理解互联网的分层架构**——数据如何从应用层逐层封装、传输、解封装
2. **实现可靠数据传输**——在不可靠的底层通道上构建可靠的字节流抽象
3. **掌握 TCP 核心机制**——三次握手、滑动窗口、流量控制、拥塞控制
4. **理解 IP 路由与转发**——子网划分、最长前缀匹配、ARP、路由协议
5. **从源码级别理解协议**——不背字段表，而是真正理解每个字段"为什么"存在
6. **用 C++ 编写健壮的系统代码**——资源管理、错误处理、并发

---

## 📅 完整模块（按周/讲）

### 第 1-2 周：应用层与网络架构

| 讲次 | 主题 | 关键概念 |
|------|------|----------|
| L1 | Course intro & the Internet | 端到端原则、分组交换、分层模型 |
| L2 | Application layer: HTTP | 请求/响应、持久连接、CDN |
| L3 | DNS & naming | 层次化命名、递归/迭代查询、缓存 |

**Lab 0**: 搭建 C++ 开发环境，实现一个 `ByteStream`（可靠的内存字节流）

### 第 3-4 周：传输层基础与可靠传输

| 讲次 | 主题 | 关键概念 |
|------|------|----------|
| L4 | Transport service overview | TCP vs UDP、多路复用/分用 |
| L5 | Reliable data transfer | ARQ、回退 N 步 (GBN)、选择重传 (SR) |
| L6 | Sliding window | 流量控制、累计确认、窗口缩放 |

**Lab 1-2**: 实现 `StreamReassembler`（乱序到达的字节流重组器）+ 完整的 `ByteStream`

### 第 5-6 周：TCP 协议详解

| 讲次 | 主题 | 关键概念 |
|------|------|----------|
| L7 | TCP connection management | 三次握手、四次挥手、状态机、TIME_WAIT |
| L8 | TCP reliability | 序列号、重传超时 (RTO)、快速重传 |
| L9 | Flow & congestion control | 慢启动、拥塞避免、Tahoe / Reno / Cubic / BBR |

**Lab 3-4**: 实现 TCP 发送端 (`TCPSender`) + TCP 接收端 (`TCPReceiver`) + 拼装为完整连接

### 第 7-8 周：网络层（IP）

| 讲次 | 主题 | 关键概念 |
|------|------|----------|
| L10 | IP addressing | IPv4/IPv6、子网掩码、CIDR、NAT |
| L11 | IP forwarding | 最长前缀匹配、路由表、TTL |
| L12 | ARP & DHCP | 地址解析、动态配置 |

**Lab 5**: 实现网络接口层 (`NetworkInterface`)——处理 ARP 请求与应答

### 第 9-10 周：路由与链路层

| 讲次 | 主题 | 关键概念 |
|------|------|----------|
| L13 | Routing algorithms | 距离向量 (DV)、链路状态 (LS)、Dijkstra |
| L14 | Routing protocols | OSPF、BGP、自治系统 |
| L15 | Link layer | 以太网、CSMA/CD、Wi-Fi、交换机 |

**Lab 6-7**: 实现路由器 (`Router`)——最长前缀匹配转发 + 路由表更新

### 第 11 周：现代网络与总结

| 讲次 | 主题 | 关键概念 |
|------|------|----------|
| L16 | QUIC & HTTP/3 | UDP 之上的可靠传输、0-RTT、多路复用 |
| L17 | Active queue management | BBR 拥塞控制、bufferbloat、公平性 |
| L18 | Review & the future of networking | IPv6 部署、SDN、网络可编程性 |

**Lab 8** (Final): 在自己的 TCP 上运行真实应用——用 `./apps/webget` 下载真实网页

---

## 🧮 核心算法/数学

### 1. 可靠数据传输（ARQ 协议）

```
发送方：                    通道（可能丢包/乱序/损坏）        接收方
  ┌─────────┐                    ┌──────────┐              ┌─────────┐
  │ send pkt│ ──────────────────>│ 网络链路  │─────────────>│ rcv pkt │
  │ start   │                    │ (unrely)  │              │ send ACK│
  │ timer   │<───────────────────│          │<─────────────│         │
  └─────────┘   ACK / 超时重传    └──────────┘              └─────────┘
```

三种范式：
- **停等协议 (Stop-and-Wait)**: 每次只发一个包，等 ACK → 效率极低
- **回退 N 步 (Go-Back-N)**: 滑动窗口 + 累计确认，丢失则重传窗口内所有
- **选择重传 (Selective Repeat)**: 只重传丢失的包，需要更复杂的缓冲管理

### 2. TCP 拥塞控制数学

**慢启动 (Slow Start)**:
$$\text{cwnd} \leftarrow \text{cwnd} + 1 \quad \text{(每收到一个 ACK)}$$
→ 指数增长：$\text{cwnd} \approx 2^{\text{RTT}}$

**拥塞避免 (Congestion Avoidance)**:
$$\text{cwnd} \leftarrow \text{cwnd} + \frac{1}{\text{cwnd}} \quad \text{(每收到一个 ACK)}$$
→ 线性增长：$\text{cwnd} \approx \text{cwnd}_0 + \text{RTT}$

**Tahoe vs Reno 反应**:

| 事件 | Tahoe | Reno |
|------|-------|------|
| 3 次重复 ACK | $\text{ssthresh} = \text{cwnd}/2$, cwnd=1 | $\text{ssthresh} = \text{cwnd}/2$, cwnd=ssthresh |
| 超时 | $\text{ssthresh} = \text{cwnd}/2$, cwnd=1 | $\text{ssthresh} = \text{cwnd}/2$, cwnd=1 |

Reno 的关键改进：**快速恢复**（fast recovery），遇到 3 次重复 ACK 时不把 cwnd 降为 1，而是减半后继续。

### 3. 校验和（Internet Checksum）

```
将数据视为 16 位字序列，求和后取反码
sum = sum(所有 16-bit 字) + carry
checksum = ~sum
```

### 4. 最长前缀匹配（Longest Prefix Match）

路由转发核心：在路由表中找到与目的 IP 匹配的**最长前缀**条目。

```
路由表:  192.168.0.0/16 → eth0
         192.168.1.0/24 → eth1
目的地址: 192.168.1.5  → 匹配 /24（更长），转发到 eth1
```

---

## 💻 项目代码

### `topic9-systems/tcp_sim.py`

**实现内容**：Python 教学版 TCP 模拟器，涵盖 CS144 传输层核心概念。

| 模块 | 类/函数 | 功能 |
|------|---------|------|
| TCP 状态机 | `TCPState` (Enum) + `TCPEndpoint` | 10 个状态的完整状态机转移 |
| 数据包 | `TCPPacket` (dataclass) | SYN/ACK/FIN/RST 标志位 + 序列号 |
| 三次握手 | `simulate_handshake()` | CLOSED → SYN_SENT → ESTABLISHED |
| 四次挥手 | `simulate_teardown()` | FIN_WAIT → CLOSE_WAIT → TIME_WAIT |
| 拥塞控制 | `TCPCongestionControl` | Tahoe/Reno 模式，慢启动→拥塞避免 |
| 滑动窗口 | `SlidingWindow` | Go-Back-N 发送窗口 + 累计确认 |

**运行命令**:
```bash
cd topic9-systems
python3 tcp_sim.py
# 输出: 三次握手时序 + cwnd 演化 ASCII 图 + 滑动窗口演示
```

**关键输出示例**:
```
📋 TCP Tahoe 拥塞窗口演化 (60 步):
   t=  0 █ 1.0 (slow_start)
   t=  3 ██████ 8.0 (slow_start)
   t= 20 ⚠️ Timeout → cwnd 重置
   t= 40 ⚠️ 3 Dup ACK → Reno 快速恢复
```

### 对应的 C++ Labs（课程原版）

| Lab | 名称 | 核心文件 | 难度 |
|-----|------|----------|------|
| 0 | networking setup | `apps/webget.cc` | ⭐ |
| 1 | stream reassembly | `stream_reassembler.hh` | ⭐⭐ |
| 2 | sliding window | `byte_stream.hh` | ⭐⭐ |
| 3 | TCP sender | `tcp_sender.hh` | ⭐⭐⭐ |
| 4 | TCP receiver | `tcp_receiver.hh` | ⭐⭐⭐ |
| 5 | network interface | `network_interface.hh` | ⭐⭐⭐⭐ |
| 6 | routing | `router.hh` | ⭐⭐⭐⭐ |
| 7-8 | final integration | 全栈联调 | ⭐⭐⭐⭐⭐ |

---

## 📊 关键论文/教材

### 核心 RFC（课程的"教科书"）

| RFC | 标题 | 重要性 |
|-----|------|--------|
| [RFC 793](https://datatracker.ietf.org/doc/html/rfc793) | **TCP 传输控制协议** | ⭐⭐⭐⭐⭐ 必读 |
| [RFC 1180](https://tools.ietf.org/html/rfc1180) | A TCP/IP Tutorial | ⭐⭐⭐⭐⭐ 入门 |
| [RFC 1122](https://tools.ietf.org/html/rfc1122) | Host Requirements | ⭐⭐⭐⭐ |
| [RFC 791](https://tools.ietf.org/html/rfc791) | **IP 网际协议** | ⭐⭐⭐⭐⭐ |
| [RFC 2616](https://tools.ietf.org/html/rfc2616) | HTTP/1.1 | ⭐⭐⭐⭐ |
| [RFC 9000](https://datatracker.ietf.org/doc/html/rfc9000) | **QUIC: A UDP-Based Multiplexed Transport** | ⭐⭐⭐⭐ 现代 |
| [RFC 5681](https://tools.ietf.org/html/rfc5681) | TCP Congestion Control | ⭐⭐⭐⭐ |

### 经典论文

- **Jacobson (1988)**. [Congestion Avoidance and Control](https://dl.acm.org/doi/10.1145/52324.52356). *SIGCOMM*. — TCP 拥塞控制的奠基论文，定义了 Tahoe/Reno
- **Cardwell et al. (2017)**. [BBR: Congestion-Based Congestion Control](https://research.google/pubs/pub45646/). *ACM QUEUE*. — Google 的现代拥塞控制算法
- **Saltzer, Reed, Clark (1984)**. [End-to-End Arguments in System Design](https://web.mit.edu/Saltzer/www/publications/endtoend/endtoend.pdf). *ACM TOCS*. — 互联网设计哲学

### 推荐教材（参考，非必读）

- **Kurose & Ross**. *Computer Networking: A Top-Down Approach*.（自顶向下经典教材）
- **Fall & Stevens**. *TCP/IP Illustrated, Volume 1*.（协议实现细节宝典）
- **Tanenbaum & Wetherall**. *Computer Networks*.（百科全书式参考）

---

## 🎯 学习路径

```
Week 1-2  ┌─ 应用层: HTTP/DNS（直觉理解网络在做什么）
          │
Week 3-4  ├─ 可靠传输: ARQ/滑动窗口（核心抽象：不可靠→可靠）
          │   └─ Lab 1-2: StreamReassembler + ByteStream
          │
Week 5-6  ├─ TCP: 连接管理 + 拥塞控制（核心难点）
          │   └─ Lab 3-4: TCPSender + TCPReceiver
          │   ⚠️ 这是整个课程最烧脑的部分
          │
Week 7-8  ├─ 网络层: IP/ARP/路由（从端到端到全网）
          │   └─ Lab 5-6: NetworkInterface + Router
          │
Week 9-10 ├─ 链路层 + 现代网络（完整图景）
          │
Week 11   └─ Lab 7-8: 集成联调，用自己写的 TCP 上网！
```

### 给自学者的建议

1. **先跑 Python 版模拟器**（`tcp_sim.py`）建立直觉，再去啃 C++ Labs
2. **手画状态机**：TCP 11 个状态转移图必须能默写
3. **抓包实践**：用 Wireshark 抓真实流量，对比自己的实现
4. **从失败中学习**：Labs 的自动测试（autograder）极其严格，培养工程严谨性
5. **读 Winstein 的 [Network Reader](https://cs144.github.io/)**：他写的课程笔记本身就是优秀的系统设计教材

---

## 💡 反思

### 为什么 CS144 是"神课"

1. **教学哲学**：Winstein 不教你"记住 TCP 头部有 20 字节"，而是让你"写出能用自己 TCP 下载网页的代码"。知识从记忆变成肌肉记忆。
2. **分层抽象的教科书级演示**：每个 Lab 恰好是一层抽象——`ByteStream`（可靠流）← `StreamReassembler`（重组）← `TCPSender/Receiver`（协议）← `NetworkInterface`（链路）← `Router`（转发）。这是 **计算机科学中最优雅的分层设计教学**之一。
3. **C++ 工程训练**：强迫学生使用现代 C++ 的 RAII、移动语义、`std::optional`、`std::unique_ptr`，这是极好的系统编程训练。
4. **真实世界的连接**：当你用自己手写的 TCP 通过 TUN 接口下载到第一个真实网页时，那种"我真正理解了互联网"的震撼是无可替代的。

### 常见学习陷阱

- **过早优化**：学生常想把 TCP 写得"高效"，但正确性远比性能重要
- **状态机不清晰**：TCP 的 11 个状态必须先画清楚再写代码
- **忽略边界条件**：窗口为零、序列号回绕、重复 ACK——这些细节才是难点
- **不读 RFC**：CS144 的很多答案直接在 RFC 里，但你得读懂

---

## 🚀 扩展

### 深入方向

| 方向 | 推荐课程/资源 |
|------|---------------|
| 分布式系统 | Stanford CS240/CS244B（分布式系统）|
| 软件定义网络 | Nick McKeown 的 CS344（SDN 之父在 Stanford）|
| 网络安全 | Dan Boneh 的 CS155（网络安全）|
| 高性能网络 | DPDK、RDMA、内核旁路技术 |
| QUIC 深入 | 阅读 [Google QUIC 设计文档](https://www.chromium.org/quic) + Chromium 源码 |

### 实战项目建议

1. **用你自己的 TCP 实现 HTTP 服务器**——在 Lab 8 基础上扩展
2. **实现简化版 BBR 拥塞控制**——替换 Reno，对比性能
3. **写一个简易网络抓包分析器**——用 `libpcap` 解析 Ethernet/IP/TCP 帧
4. **实现 NAT 穿透**——理解 STUN/TURN/ICE 协议

### 与其他课程的关系

```
CS106B (编程基础) ──> CS107 (系统编程, C++) ──> CS144 (网络)
                                                   │
                          CS110 (操作系统) <───────┘
                                                   │
                          CS244B (分布式系统) <───┘
```

CS144 是系统课程的"桥梁"——它假设你有 CS107 的 C++ 能力和系统思维，同时为 CS244B（分布式系统）和 CS240（高级系统）打下网络基础设施的理解基础。

---

> *"The Internet is the most complex machine humanity has ever built, and you can understand every bit of it."* — CS144 精神
