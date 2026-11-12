# 网络技术姊妹篇知识库（knowledge/）· 总索引与横向对比

> 本目录是 kylin/network 工作区对三个"非 eBPF"网络仓的深度消化，与 awesome-ebpf 语料库（../awesome-ebpf/，eBPF 主线）互补。四条技术路线合起来回答同一个问题：**Linux 网络栈的性能、隔离与可编程性困局，各自怎么解？**

## 文档索引

| 文档 | 对象 | 规模 | 一句话定位 |
|---|---|---|---|
| [f-stack.md](f-stack.md) | f-stack/f-stack @2026-10 | 12.9k 字符 | kernel bypass 最重路线：FreeBSD 全栈连根搬进用户态 + DPDK 轮询 |
| [passt.md](passt.md) | passt.top/passt @2026-10 | 12.3k 字符 | 协议翻译器流派：无特权进程"说"网络协议，砍掉中间 TCP/IP 栈 |
| [systemd-network.md](systemd-network.md) | systemd/systemd @2026-11 | 22.4k 字符 | in-kernel 路线的管理面：networkd 状态机 + 38 种 netdev + 自研协议库 + systemd×eBPF 交汇 |
| （姊妹篇）awesome-ebpf/docs/ | eBPF 全生态 | 16 章 29.3 万字符 | in-kernel 可编程路线：XDP/tc/AF_XDP/可观测/安全/调度 |

## 四路线横向对比（数字全部带各文档内部出处）

| 维度 | eBPF（XDP/tc） | F-Stack（DPDK+FreeBSD） | passt（用户态翻译器） | systemd-networkd（内核栈管理面） |
|---|---|---|---|---|
| **核心思想** | 内核里嵌可编程沙箱，包最早点（Rx ring）处理 | 整个协议栈搬进用户态，网卡轮询独占 | 不做栈，做协议翻译：L2 帧↔原生 L4 socket | 不动数据面，把内核栈配置收敛成状态机 |
| **旁路程度** | 半旁路（驱动仍在内核） | 全旁路（PMD 用户态驱动） | 不旁路（两端都是内核栈，中间削一层） | 不旁路（管理面） |
| **性能量级** | 单核 24Mpps drop / 5.2Mpps L4 LB（CoNEXT'18）；iptables 1.8~4.8Mpps（八级阶梯）→XDP 10.1~24Mpps 的经典跃迁（口径辨析见 awesome-ebpf/docs/09 9.2.7） | RPS 5M vs 调优内核 200K（25×）、P99 10µs vs 100µs、千万并发（README 口径） | slirp 系 4-50×（IPv4 TCP）；长肥管道受 16MiB 窗口顶 | N/A（目标是正确性/可运维性） |
| **特权要求** | CAP_BPF/CAP_NET_ADMIN（root 或授权） | hugepage + 独占网卡 + 独占 CPU 核 | **零 capability**（passt-repair 帮手除外） | root（降权后留 6 个 capability 含 CAP_BPF） |
| **编程模型** | 受限 C（verifier 约束、无循环→有界循环、512B 栈） | 完整 C（FreeBSD 栈原样），run-to-complete 每核一进程 | 无（终端用户不编程），事件循环 + 静态缓冲 | 声明式（.network/.netdev/.link 配置） |
| **生态成熟度** | 主线内核 + CNCF 毕业项目群（Cilium 等） | 腾讯 DNSPod 生产背书，社区中量级 | QEMU/Podman/Aardvark 事实标准后端 | 所有主流发行版的默认网络管理器 |
| **致命代价** | verifier 复杂度天花板；跨版本可移植性靠 CO-RE | 独占网卡/CPU、运维复杂度陡增（10×性能吃 10×复杂度） | 无 SACK/PAWS、窗口硬顶、时延受翻译路径拖累 | 单线程事件循环上限；状态序列化欠账（官方 TODO） |
| **适用场景** | DDoS 防护/LB/可观测/安全策略/调度 | 专用接入层：DNS、静态 CDN、极致 RPS 的网关 | rootless 容器/VM 联网、无特权环境 | 一切需要"网卡从枚举到可路由"生命周期管理的系统 |

**选型口诀**：要可编程+生态 → eBPF；要极致吞吐且养得起专属核 → F-Stack；要无特权容器/VM 联网 → passt；要管好内核栈 → networkd。**路线正交可组合**：Cilium（eBPF 数据面）跑在 systemd（管理面）之上；passt 给 eBPF 观测的容器供网；F-Stack 的接入层前面可以再挂 XDP 抗 D。

## 四条路线的交汇趋势（2025-2026）

1. **eBPF 进管理面**：systemd 自身已用 BPF 做三件事——sysctl 写入 ringbuf 监控（cgroup syscall 拦截）、netlink socket cBPF 预过滤、IPIngressFilterPath 等网络 BPF 挂载（systemd-network.md §7 源码实证）——"用 eBPF 管理不用 eBPF 的系统"正在成为范式。
2. **用户态路线吸收内核特性**：passt 的 vhost-user 单拷贝数据面（2025）与 F-Stack 的内核栈共存模式（2026）都在软化"全旁路"的排他性。
3. **eBPF 语料库中的对照**：Suricata XDP bypass（NFQ 39Gbps 口径勘误见 docs/10）与 DPDK PMD 的 AF_XDP 通道，是 eBPF 路线与用户态生态互通的桥。

## 使用方式

- 每份文档自带：架构逐层剖析 / 关键文件表 / 坑清单 / 学习者路径 / AI agent 用法（本地路径 + grep 关键词）
- 交叉引用：awesome-ebpf/docs/10-AF_XDP与用户态网络.md 的三路线对比表与本 README 互为详略两级
- 活体跟踪：三仓均在每日 06:17 的 track_alive.sh 跟踪清单内（awesome-ebpf/manifest/track/track.log）
