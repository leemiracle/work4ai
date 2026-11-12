# 第9章 XDP 与 tc：内核网络数据面编程

> 本章导读：写给要动手做高速包处理（DDoS 清洗、负载均衡、隧道、K8s 数据面）的网络/安全/内核工程师。前置：eBPF 架构与 verifier 基础（maps/helpers/tail call），即第 1 章历史线之后的架构章。读完你能：说清 XDP 在收包路径的精确挂载位置与五种 action、分清 XDP/tc cls_bpf（以及新一代 tcx/netkit）三代挂载点的分工、独立写出一个能跑的 XDP drop 程序、并且每个性能数字都能给出处。

## 9.1 直觉层

**比喻**：XDP 原始提案人 Tom Herbert 与 Alexei Starovoitov 给过一个传神的比喻——内核协议栈是一条高速公路，DPDK 这类 kernel bypass 是另建一套高铁系统（快但要全款重建、跟既有交通网不互通），而 XDP 是**给现有高速公路加一条拼车道（carpool lane）**：路还是那条路，只是最快的那类车（要丢的包、要转发的包）在入口最早点就被分流出去了（[id=67] `web/pdf-txt/67.txt`，grep `carpool`）。

**为什么需要它**：Cloudflare 的原始痛点——iptables 在一台体面的服务器上只能扛约 1 Mpps，而一次伪造源的 DDoS 可达 3 Mpps，IRQ 中断洪泛直接把机器打瘫（[id=62] `web/md/62.md` 开篇引 Cloudflare 博客）。Cloudflare 工程师 Gilberto Bertin 的金句点破本质："**Iptables is not slow. It's just executed too late in the stack**"（iptables 不慢，只是被执行得太晚了，[id=77] `web/pdf-txt/77.txt`）。在下图这条收包路径上，iptables 排在 conntrack 之后——包要先走完 DMA、NAPI、SKB 分配、GRO、IP 层、conntrack 才轮到规则匹配；攻击流量在这条路上每一步都在消耗 CPU 与内存。XDP 把"丢包决定"前移到 **SKB 还没分配的驱动 Rx ring 最早点**，被丢的包只花了 DMA 一次成本。

**它在 eBPF 栈里的位置**（挂载点全景，依据 [id=77] 调用树 + [id=54] tc 挂载点 + [id=62]）：

```
                         收包路径（RX）
 NIC ──DMA──> Rx ring ─>【① driver XDP】──PASS──> alloc_skb/build_skb ─>【② generic XDP】
   (每 CPU 一个                            |                              （SKB 层，4.12+，
    RX queue,无锁)                         |                               任意网卡可用）
   ①可 DROP（页面直接回收）                 |__ netif_receive_skb_core ─>【③ tc ingress / clsact】
   ①可 TX（同口弹回）                       |        （nftables netdev hook 也在这附近，prio -500）
   ①可 REDIRECT ──> devmap / cpumap / xskmap │ ─> ip_rcv ─> conntrack ─> iptables ─> tcp_v4_rcv ─> socket

                         发包路径（TX）
 socket ─> IP/TCP ─> __dev_queue_xmit ─>【④ tc egress / clsact】─> qdisc 队列规则 ─> driver xmit
                              （新一代：netkit pair 在 ndo_start_xmit() 挂 BPF，tcx 取代 clsact，见 9.2.9）
```

**双子星分工一句话**：XDP 是"**没有 SKB 的最早入口**"——只管 ingress，胜在极致快（丢包、转发、LB、卸载到用户态）；tc 是"**有 SKB 的全功能层**"——ingress+egress 双向都有，能改包、能配合 qdisc 整形排队、能看到隧道元数据。两者不是竞争而是分层：现代系统（Cilium、Calico）常常同时用。CoNEXT'18 论文就把 Cilium 列为"XDP 作为构建块"的代表应用（`repos/tohojo/xdp-paper/xdp-paper.tex` §XDP as a building block）。

## 9.2 原理层

### 9.2.1 挂载点的精确位置：driver XDP vs generic XDP

**driver（原生）XDP**：hook 实现在网卡驱动的 RX 函数里，"就在 NIC 把包收进 Rx ring 的最早点"（just when the NIC receives a packet in the Rx ring，[id=62] `web/md/62.md`）。此时包还是驱动持有的 DMA-mapped page fragment，**SKB 尚未分配**——Jesper Brouer 的原始表述是"在 driver RX 函数内、SKB 分配前直接操作 RX packet-pages"（[id=69] `web/pdf-txt/69.txt`）。IO Visor 官方口径补齐了处理模型：内核组件直接从 driver 处理 RX packet-pages，**不预分配 skbuff、无软件队列，一个 CPU 一个 RX queue 无锁**，busy poll 或中断模式皆可（[id=66] `web/md/66.md`）。2019 年时支持 driver 级 XDP 的接口有 ixgbe/i40e/mlx5/veth/tap/tun/virtio_net 等（[id=62]）；更早的 v4.10 时期清单是 mlx4/mlx5/nfp/qede/virtio-net（[id=71] `web/pdf-txt/71.txt`）——清单一直在扩。

**generic XDP**：hook 在协议栈较高点（SKB 层），**任意网卡可用**，Linux 4.12 起（[id=77] `web/pdf-txt/77.txt` 明示 "Generic XDP 自 Linux 4.12 起任意网卡可用"）。代价是性能明显不如 driver 级（[id=62]）——因为包已经付了 SKB 分配的成本，只是仍早于 tc ingress/netfilter。

**为什么 driver 级快**：XDP 原始提案的性能技术清单（[id=67]）：lockless（一核一队列）、batched I/O、page recycling 免分配/释放、无 skbuff 元数据分配、packet steering、siloed 处理减少跨 CPU/NUMA、cache prefetch/DDIO、常见 NIC offload 复用。DROP 时"返回错误码即由 driver 回收页"，连 free 都省了（[id=67]）。

### 9.2.2 五种 action 的语义

XDP 程序对每个包返回一个 action（[id=62] `web/md/62.md` 逐条）：

| action | 语义 | 备注 |
|---|---|---|
| `XDP_PASS` | 放行，包继续走正常协议栈 | |
| `XDP_DROP` | 极速丢弃 | 页面直接回收，最便宜路径 |
| `XDP_TX` | 从**同一接口**弹回（TX-bounce） | 同 CPU 独占 TX queue 免锁（[id=67]） |
| `XDP_REDIRECT` | 重定向到另一网卡 / CPU / 用户态 | 经 devmap/cpumap/xskmap，见 9.2.4 |
| `XDP_ABORTED` | 表示 eBPF 程序出错 | **实际按丢包处理**（[id=62]） |

版本代差注意：2016 年提案期只有 PASS/DROP/TX 三个 action（[id=69]），REDIRECT 到 2018 年才以 map-based 形态落地（[id=75]）。PASS/TX/REDIRECT 本质都是"转发"的三种特例（[id=62]）。

### 9.2.3 XDP vs tc cls_bpf：无 SKB 快路径 vs 有 SKB 全功能层

**tc cls_bpf 的血统**：tc 里的 BPF classifier 2013 年以 cBPF 形态出生（commit `7d1d65cb84e1`），2015 年加 eBPF 支持（commit `e2e9b6541dd4`）（[id=55] `web/pdf-txt/55.txt`）。BPF 在 eBPF 时代的第一条生产级数据面就是它——kernel 源码入口章的 digest 把 `net/sched/cls_bpf.c` 称为"BPF 的第一个生产级家"（digests/11-内核源码入口.md）。

**挂载点**（[id=54] `web/pdf-txt/54.txt` "Invocation points"页）：ingress 在 `__netif_receive_skb_core → sch_handle_ingress`（SKB 已存在，早于 IP 层）；egress 在 `__dev_queue_xmit → sch_handle_egress`——**egress 是 XDP 完全够不到的半边天**，这是两者最硬的分工边界。

**direct-action（da）模式**：cls_bpf 有两种执行模式（[id=54]）——传统模式把分类结果交给完整 tc action 引擎（`tcf_exts_exec()`，还要配 act_pedit 等改包）；**da 模式**下 classifier 直接返回 verdict，省掉 action 管线开销。verdict 码语义（[id=54]）：`ok`（继续分类链）/`shot`（丢）/`stolen`（被接管，如排队到别处）/`redirect`（重定向，da 模式免 clone skb，走 per-CPU scratch buffer + `skb_do_redirect()`）/`unspec`。

**分工对照表**（综合 [id=52]/[54]/[55]/[62]/[69]）：

| 维度 | XDP | tc cls_bpf（clsact） |
|---|---|---|
| 挂载点 | driver Rx ring 最早点（SKB 前） | ingress+egress 双向（SKB 后） |
| 包表示 | raw page fragment（`ctx->data/data_end`） | SKB（可读可写，direct packet access） |
| 改包能力 | 需 `bpf_xdp_adjust_head` 手工腾空间 | 天然可改，还带隧道元数据 helper（vxlan/geneve/gre tunnel key/options metadata 收集，[id=52] `web/pdf-txt/52.txt`） |
| 队列/整形 | 无 | 与 qdisc 体系配合（队列规则、整形是 tc 的本体） |
| 典型用途 | DDoS 早期丢包、L3/L4 LB、隧道 decap、redirect | 网络策略、NAT/改写、egress 限速、服务网格数据面 |
| 性能 | 单核 24 Mpps drop（9.2.7） | 慢一个量级，但功能全 |

**选型口诀**：要"越早丢越好/越早转越好"→ XDP；要"看得到 SKB、改包、管 egress"→ tc。Cloudflare 的实测佐证了"早丢"的价值：tc ingress u32 drop 1.8 Mpps vs XDP 10.1 Mpps（同机，[id=78] `web/md/78.md`）。

### 9.2.4 XDP_REDIRECT：devmap / cpumap / xskmap

redirect 是 2016 年畅想的 XDP_FWD 到 2018 年的落地形态，设计核心是**用 map 而不是 helper 参数做目标选择**（[id=75] `web/pdf-txt/75.txt`）：

- **helper `bpf_redirect` 只有 7.5 Mpps，`bpf_redirect_map` 达 13.0 Mpps（单核）**。map 版快的两个原因：①把 RX bulking 藏进 XDP core——driver 逐包调 `xdp_do_redirect`，攒到 NAPI poll 循环末尾统一 `xdp_do_flush_map`，批量（≤64）摊销昂贵的 NIC tail pointer/doorbell 写；②新的 redirect 目标类型零 driver 改动即可发明（作者称"hopefully last XDP action code"）（[id=75]）。
- **DEVMAP**：ifindex→netdev 映射，把包从另一块网卡发出去；driver 只需实现 `ndo_xdp_xmit`（+flush）即可支持（[id=75]）。
- **CPUMAP**：把 raw XDP frame 送到远端 CPU，**在那儿才建 SKB 入协议栈**。内部结构：MPSC 模型 + per-CPU 快 enqueue（8 包一批）+ bulk 入 ptr_ring + 钉核 kthread 无锁出队（[id=75]）。两大用途：①隔离 driver XDP 层与协议栈——DDoS 防护时协议栈再慢也拖不垮 XDP 丢包；②修复 NIC 硬件 RSS 对 VXLAN/双层 VLAN 等封装协议失明造成的 CPU 分布不均（[id=75]）。
- **XSKMAP**：redirect 进 AF_XDP 用户态 socket（配套 UMEM/四环模型，详见 AF_XDP 章；[id=79] `web/md/79.md`：**必须加载 XDP 程序且 XSKMAP 至少放一个 socket 才能收到流量**）。

配套基础设施（v4.16/v4.18，[id=75]）：`xdp_rxq_info`（`ctx->ingress_ifindex`/`rx_queue_index`，替代 per-RX-queue program 的诉求）；`struct xdp_frame` 标准化排队（元数据存在 frame headroom 里免分配）；Memory return API（帧按来源 RX queue 归还给原 driver，AF_XDP zero-copy 的前提）。

**Spectre v2 实录**（安全缓解撞上数据面的经典案例，[id=75]）：`CONFIG_RETPOLINE` 开启后 XDP redirect 从 ~13 Mpps 跌到 6 Mpps——真凶不是 `ndo_xdp_xmit` 间接调用而是 DMA API 里的函数指针，Christoph Hellwig 的 PoC 补丁救回 ~10 Mpps。

### 9.2.5 headroom 与 bpf_xdp_adjust_head

XDP 的包是 page 里的裸数据，`ctx->data` 指针就是包起点。要**加包头**（VLAN push、隧道 encap）就必须先把 data 指针往前挪——前提是 page 里 data 之前预留了空间，这个预留就叫 **headroom**。腾挪靠 helper `bpf_xdp_adjust_head(ctx, offset)`：负值 push（腾出头部空间）、正值 pull（剥掉头部）。

语料中的实战用法（[id=71] `web/pdf-txt/71.txt` EXTRA slides）：DDoS scrubbing 场景用 `bpf_xdp_adjust_head()` 做 VLAN/VRF 清洗——把清洗后的包打上 VLAN header 送进独立 VRF，清洗完再回正常 VRF；还有客户直接在入向链路**预打 VLAN tag 免 push**（利用已有 headroom 省掉 adjust）。`struct xdp_frame` 的排队元数据也放在 frame headroom 里，排队转发路径零额外分配（[id=75]）。反向操作（decap）同样是 adjust_head 的主场景——隧道终点在 XDP 层剥外层头。

### 9.2.6 多缓冲（multi-buffer）与 jumbo frames 约束

XDP 初期是**单帧模型**：一个包必须整个落在一个 page 里——启用 XDP 后 RX ring 内存模型变成"每包恒 alloc 4K 页"（[id=69]），超过一个 page 的包（jumbo frames、GRO 大聚合包）处理不了，程序也拿不到完整数据。这是 AF_XDP 场景多年的实际约束。

现代解法是 multi-buffer / scatter-gather（[id=79] `web/md/79.md`，AF_XDP 官方文档）：
- `XDP_USE_SG` 模式 + `XDP_PKT_CONTD` 标志把一个包拆成多个 buffer 链式传递；
- copy 模式上限 = `CONFIG_MAX_SKB_FRAGS+1`，**可移植代码应限到 18 个 frag**；零拷贝上限要查 netlink `NETDEV_A_DEV_XDP_ZC_MAX_SEGS`；
- 程序声明支持多缓冲需要 `xdp.frags` 特性（[id=79]，grep `xdp.frags`）。

注意版本语境：论文时代（2018）AF_XDP 零拷贝 driver 支持才刚进 4.19（[id=63] tex），multi-buffer 是其后多年的演进，写可移植 XDP 程序时对 MTU>页大小的环境要显式检查驱动能力。

### 9.2.7 性能量化（全部带出处与语境）

**① CoNEXT'18 论文基准**（`repos/tohojo/xdp-paper/`，ACM "artifact evaluated reusable" 可复现认证；硬件 Xeon E5-1650 v4 6 核 3.60GHz + 双口 ConnectX-5 Ex 100G，内核 = net-next-xdp 仓 xdp_paper01 分支 commit e641995a；digests/04 + tex 原文核对）：
- **drop：24 Mpps/CPU**（tex L852/L961/L1317；对应 41.6 ns/包），DPDK 对照 43.5 Mpps（22.9 ns/包），差距但换内核兼容；PCI 总线在该机器上限 70 Mpps；消融：去掉间接函数调用后 29 Mpps，全部去函数调用外推 37.6 Mpps（tex L976-977）。
- **iptables 对照：带 conntrack 1.8 Mpps/核，raw 模式 4.8 Mpps/核**（tex L849-850）——"从 conntrack 的 1.8 到 raw 的 4.8"就是 XDP 单核 24 Mpps 的分母语境。
- **L4 负载均衡（Katran 移植）：5.2 Mpps/CPU，对内核 IPVS（1.2 Mpps/CPU）4.3 倍增益**，随核数线性扩展到 6 核 29.3 Mpps（tex `tbl:load-balancer`，L1147-1157）。
- **DDoS 曲线**：iptables filter 在 3 Mpps 攻击流量下吞吐减半、3.5 Mpps 附近归零；换 XDP filter 后吞吐保持到 **19.5 Mpps** 攻击流量才回落（tex L1116-1119）。
- **AF_XDP 早期数字：单核 20+ Mpps 送用户态**（tex L1298）。
- 7 组 benchmark 全部可复现：bench01 baseline / bench02 xdp_drop / bench03 ddos / bench04 fwd / bench05 xdp_redirect / bench06 load_balancer / bench07 latency（`repos/tohojo/xdp-paper/benchmarks/`）。

**② Cloudflare "drop 10M pps" 八级阶梯**（[id=78] `web/md/78.md`，2018-07，内核 4.14，KPTI+retpoline 已开，14 Mpps 小 UDP 包全导入单核）：应用 recvmmsg 175 kpps → NOTRACK 关 conntrack 333 k → socket 挂 cBPF filter 512 k → iptables INPUT DROP 608 k → **iptables raw 表 1.688 M** → nftables netdev ingress 1.53 M → tc ingress u32 1.8 M → **XDP_DROP 10.1 Mpps**——应用到 XDP 约 **58 倍**差距。注意这里 XDP 是 10M 而非论文的 24M：不同硬件/内核/网卡，引用时必须带语境。

**③ Jesper 的 iptables vs XDP 同机对比**（[id=71] `web/pdf-txt/71.txt`，i7-6700K + ConnectX-4 50G）：iptables raw 表最快 drop 4.5-4.7 Mpps，XDP blacklist drop 9.7 Mpps，mlx5 prefetch trick 未上游版 16.9 Mpps（约 2-3.6 倍差距）。Julia Evans 听课笔记复述同一组数字并强调：性能之外"可写任意代码"才是相对 iptables 的本质优势（[id=74] `web/md/74.md`）。

**④ Suricata IDS bypass**（[id=190] `web/md/190.md`，Stamus Networks 博客，iperf/1500MTU 实测）：标准 IPS 内联 669 Mbps → local bypass 899 Mbps → **XDP NFQ bypass 39 Gbps（58 倍）**——"XDP bypass 让 IDS 旁路化"价值的最常被引用论据。

**⑤ 设计目标 vs 兑现**（[id=67] 提案期立下的标尺）：drop 20 Mpps/CPU（实测 24，超额）、forwarding 14 Mpps/CPU（ILA router 预期）、GRO 单 CPU 服务 100Gbps。2016 年 mlx4 40G 单核+DDIO 实测：drop 20M / TX-bounce 12M / 带 udp+mac 改写 10M（[id=69]）。

### 9.2.8 bpfilter：iptables 的 eBPF 新后端（未竟的野心）

bpfilter 的目标：**iptables 二进制一字不动，规则被翻译成 eBPF 程序挂到 XDP/tc**（[id=82] `web/pdf-txt/82.txt` L129-131）。RFC "net: add bpfilter" 2018-02 由 Daniel Borkmann 发 netdev，代码出自 Miller/Starovoitov/Borkmann（[id=82]）。

**最大胆的设计是 bpfilter.ko——"新形态内核模块"**（[id=82] L133-143，全文核实）：一个 ELF 文件却跑在**用户态**（user mode helpers/UMH 机制），在特殊线程里、全权限、root namespace 运行；随内核树构建但兼容 modprobe/modinfo。设计目标：好开发/好调试/好测试、缩小攻击面（**崩不了内核**）、数据面（内核）与控制面（用户态）清晰解耦；bpfilter.ko 经 `bpf()` syscall 与内核通信。

**翻译实例**（[id=82] L232-241）：`iptables -A INPUT -d 10.0.0.4/32 -j DROP` 一条规则翻译成 **26 条 eBPF 指令**，`bpftool prog dump xlated` 可见，其中指令 #19 就是比对 `0x400000a`——即 `ntohl(10.0.0.4)`。性能测试环境 Xeon E5-2630 v3 + Agilio CX 40Gbps（结论页 bpfilter 领先，图未 OCR 出具体数字，引用需谨慎）。

**社区辩论与未竟现状**（[id=82] 68 回复 + digest 07 后验）：nftables 派反弹（速度已有大改进）、"iptables 100% 行为复刻不可能"、ELF 模块安全性被质疑（回应：有 BPF verifier，不比传统内核模块更不安全）。**历史后验：bpfilter 最终未按 UMH ELF 模块形态进主线**——2020 年后项目换维护者与实现路线，转向 userspace + BPF 的 daemon 形态。这份幻灯是"UMH ELF 内核模块"这条未竟路线的最佳存档，也是 Borkmann"fast path 正在变成 normal path"判断（[id=62] 结尾 iptables→nftables→bpfilter 演进图，2019 视角）的历史注脚。

### 9.2.9 tcx 与 netkit：新一代挂载点

tc 的 clsact 挂载是 2014-2017 时代的主流接口，近年内核出现两个新挂载形态（语料出处逐一标注）：

- **tcx**：kernel/bpf/ 下已有独立的 `tcx.c`（主线文件，2026-11 快照；digests/11-内核源码入口.md——该 digest 把"tc-BPF vs XDP vs tcx"称为三代挂载方式的演进史）。Go 生态的 cilium/ebpf 库 `link` 包已支持 tcx 挂载，`examples/` 里有可运行 tcx 示例（digests/13-工具链·语言库与测试.md）。教程侧，eBPF 初学者课程已有 TCX 与 BPF Qdisc egress pacer 专题课（digests/09-教程·下.md）。⚠️ tcx 的机制细节（link-based 挂载、免建 clsact qdisc 等）本地语料未覆盖，标注**待核实**，可从 kernel/bpf/tcx.c 在线源码补。
- **netkit**：Linux 6.7+ 提供的 L2 veth 替代品。Calico 官方文档（[id=194] `web/md/194.md`，digests/15）实测口径：netkit pair 经 `BPF_NETKIT_PRIMARY` 在 `ndo_start_xmit()` 挂 BPF 程序，**吞吐/尾延迟优于 TC/TCX**；Calico 的 `bpfAttachType` 已支持 Netkit/TCX/TC 三种挂载可选（tech preview）。
- 同一条 digest 线还记录了 K8s 数据面两条路线的现状：Calico 走 tc/tcx/netkit（Pod veth/netkit 接口），Cilium 同为 tc 体系大户——选型时 XDP（ingress 极速）与 tc 系（Pod 双向策略）仍是互补而非替代（digests/15-项目·网络下.md）。

## 9.3 实践层

### 9.3.1 最小程序逐行讲：XDP 包过滤（drop 的最简形态）

以下程序来自 Igalia 的 XDP 教程文（[id=62] `web/md/62.md`，源码仓 dpino/xdp_ipv6_filter）——只放行 IPv6、其余全丢，是"DDoS drop"的极简骨架：

```c
SEC("prog")
int xdp_ipv6_filter_program(struct xdp_md *ctx)
{
    void *data_end = (void *)(long)ctx->data_end;
    void *data     = (void *)(long)ctx->data;
    struct ethhdr *eth = data;
    u16 eth_type = 0;

    if (!(parse_eth(eth, data_end, eth_type))) {
        bpf_debug("Debug: Cannot parse L2\n");
        return XDP_PASS;
    }
    bpf_debug("Debug: eth_type:0x%x\n", ntohs(eth_type));
    if (eth_type == ntohs(0x86dd)) {
        return XDP_PASS;
    } else {
        return XDP_DROP;
    }
}
```

逐行拆解（[id=62]）：
- `SEC("prog")`：ELF section 名。用 iproute2 加载时**必须叫 `prog`**，换名直接报错（[id=62] 明示这是 iproute2 的约定）。
- `struct xdp_md *ctx`：XDP 上下文。XDP 里没有 SKB，访问包数据全靠 ctx 里的 `data`/`data_end` 两个指针圈出的合法区间。
- `(void *)(long)` 强转：把 32 位 u32 字段转成指针的两段式惯用法（verifier 认这个写法）。
- `parse_eth()`：先做边界检查再读以太网头（见下）。
- 解析失败 `return XDP_PASS`：**fail-open 设计**——解析不了的包放行交给协议栈兜底，宁可慢不可错杀。
- `eth_type == ntohs(0x86dd)`：0x86dd 是 IPv6 的 ethertype。注意这里两边都过了 `ntohs`（网字节序统一比较），是常见易错点。
- 命中 IPv6 → `XDP_PASS`；否则 `XDP_DROP`——丢包就这一个返回值，连页回收都是驱动顺手做的（[id=67]）。

边界检查函数（verifier 的硬要求）：

```c
static __always_inline
bool parse_eth(struct ethhdr *eth, void *data_end, u16 *eth_type)
{
    u64 offset;
    offset = sizeof(*eth);
    if ((void *)eth + offset > data_end)
        return false;
    *eth_type = eth->h_proto;
    return true;
}
```

`eth + offset > data_end` 这一行**不可省略**：verifier 静态分析所有路径，任何读包内存前没有 bounds check 的程序直接拒载（[id=74] `web/md/74.md`——"不做 bounds check，verifier 直接拒载（静态分析保安全）"）。`__always_inline` 是让调用被内联后 verifier 能看到完整路径。

调试宏（仅开发期用）：

```c
#define bpf_debug(fmt, ...) ({ \
    char ____fmt[] = fmt; \
    bpf_trace_printk(____fmt, sizeof(____fmt), ##__VA_ARGS__); \
})
```

输出走 `/sys/kernel/debug/tracing/trace_pipe`（[id=62]）。生产环境别留它——每包一次 printk 是实打实的快路径开销（深水区 9.4）。

### 9.3.2 veth 实验环境：十分钟跑通

不需要 100G 网卡，veth 对就支持 driver 级 XDP（[id=62]）：

```bash
# 1. 建 veth 对（虚拟跳线，一端进另一端出）
sudo ip link add dev veth0 type veth peer name veth1
sudo ip link set up dev veth0 && sudo ip link set up dev veth1
# 2. 编译并挂载（clang -O2 -target bpf 产出 .o，section 名必须是 prog）
make   # -> xdp_ipv6_filter.o
sudo ip link set dev veth1 xdp object xdp_ipv6_filter.o
# 3. 验证挂载成功：看到 xdp flag 和 prog/xdp id ... jited
sudo ip link sh veth1
# 4. 验证语义：veth0 侧灌混合流量，veth1 侧只抓 IPv6
sudo tcpdump "ip6" -i veth1 -w captured.pcap -c 10
sudo tcpreplay -i veth0 ipv4-and-ipv6-data.pcap   # 20 包=10 IPv4+10 IPv6
# 结果：10 packets captured, 0 dropped —— IPv4 全被 XDP 丢了
sudo cat /sys/kernel/debug/tracing/trace_pipe      # 逐包 ethertype 日志
```

（命令与输出全部出自 [id=62]，实验结果：IPv4 包 0 到达，trace_pipe 里 0x800/0x86dd 逐条可见。）

### 9.3.3 进阶：DDoS 黑名单三件套与"先测硬件上限"

真正抗 DDoS 的形态是 **map 驱动的黑名单**（[id=71]/[id=74]，示例真身 netoptimizer/prototype-kernel 仓 `kernel/samples/bpf/`，本地 `repos/netoptimizer/prototype-kernel/`）：
- 文件命名约定：`xxxxx_kern.c`（eBPF 侧）+ `xxxxx_user.c`（加载器）+ `_cmdline.c`（运维工具）；
- 核心是 `BPF_MAP_TYPE_PERCPU_HASH` 黑名单：kern 侧查表决定 drop；`bpf_obj_pin` 导出到 /sys/fs/bpf 后 chown 给非特权用户，运维工具免 root 增删 IP；热重载 `_kern.o` 时 map 数据不丢；用户态读 percpu map 要按 possible CPUs 求和（[id=71]）；
- 整个"解析+查表+裁决"程序仅约 **270 行 C**，还能直接复用内核树的 `struct ethhdr`（[id=74]）。
- **写自己程序前先测 NIC 硬件上限当 baseline**：跑 `xdp_bench01_mem_access_cost --readmem --action XDP_PASS`，先知道你的卡在 XDP_PASS 下能到多少 Mpps，再谈优化（[id=71]）。

tc 侧挂载最小命令（[id=54] 一页 slide 可直接照抄）：

```bash
tc qdisc add dev eth0 clsact                       # 无分类 qdisc，提供 ingress+egress 挂点
tc filter add dev eth0 ingress bpf da obj prog.o    # da = direct-action
tc filter add dev eth0 egress  bpf da obj prog.o
tc filter del dev eth0 ingress                     # 删除
```

### 9.3.4 本地示例仓与观测工具

- **`repos/xdp-project/xdp-tutorial/`**：官方 XDP 教程仓，课程即目录——`basic01-xdp-pass/`（xdp_pass_kern.c + xdp_pass_user.c 最小骨架）→ `packet01-parsing` → `packet02-rewriting` → `packet03-redirecting`（redirect 实战）→ `advanced01-xdp-tc-interact`（XDP 与 tc 协同）→ `advanced03-AF_XDP` → `tracing01-04`（调试/tcpdump 配合）。学本章的配套上机路线。
- `repos/lizrice/ebpf-beginners/`：入门补充（注意归属：lizrice 的仓，非 xdp-project）。
- 观测三件套：`ethtool -S` 看驱动计数（如 `rx_xdp_drop`，[id=78]）；`bpftool prog dump xlated` 看翻译后的指令（[id=82] 用它看 bpfilter 生成的 26 条指令）；`perf top` 里看到 `__bpf_prog_run` 说明没开 JIT（[id=74]）。

## 9.4 深水区与坑

1. **verifier 拒载最常见的因**：读包前缺 bounds check（`eth + offset > data_end`），或触犯"无循环/有界执行"约束——循环必须编译期常量可展开，否则拒载（[id=55]/[id=74]）。
2. **基准卫生两坑**（[id=78]，代价是全部数字作废）：①残留的 raw socket（忘了杀的 tcpdump）会毁掉全部性能——先 `ss -A raw,packet_raw -l -p` 检查；②关 Turbo Boost 把标准差从 ±1.5% 压到 0.25%。
3. **数字引用要带语境**："XDP drop 10.1M（Cloudflare, 4.14）" vs "24M（CoNEXT'18, net-next-xdp e641995a + ConnectX-5）" vs "9.7M（Jesper, ConnectX-4）"是三台机器三个时代，直接混引必翻车。cloudflare-blog 仓 2018-07-dropping-packets/ 有全部复现代码（[id=78]）。
4. **generic XDP 的性能幻觉**：任意网卡可用 ≠ 快——它已在 SKB 层之后（[id=62]），性能显著低于 driver 级；生产抗 DDoS 必须确认驱动在原生支持清单里。
5. **XDP 不是免费的**：启用即改变 RX ring 内存模型——每包恒 alloc 4K 页，理论上拖慢正常入栈路径（page allocator 瓶颈，催生 page_pool 项目），并影响 `skb->truesize` 与 TCP 吞吐（[id=69] 诚实 Disclaimer）。XDP 真转发（跨设备 redirect）无法完全避开与 MM 层交互——页要等远端设备 TX 完成后归还（[id=72] `web/pdf-txt/72.txt`）。page_pool 后来成为标准解法（[id=72] 立项陈词）。
6. **反直觉数据**：nftables netdev ingress（1.53M）反而比 iptables raw（1.688M）略慢（[id=78]）；iptables raw 比 filter 快近 3 倍连作者都自承"没完全搞懂为何"（[id=78]）——别用直觉代替实测。
7. **安全缓解可能打断腿**：Spectre v2 retpoline 把 redirect 13M→6M，特定 DMA API 函数指针是根因（[id=75]）。升级内核后性能骤降先查 mitigations。
8. **AF_XDP 双坑**（[id=79] FAQ）：绑了 queue 0 收不到包——NIC 每核一 queue，用 `ethtool -L combined 1` 或 ntuple 规则导流；同一 UMEM 缓冲区同时喂 FILL 和 TX 环会**包损坏**。
9. **XDP_TX 只能同口弹回**；跨设备必须 REDIRECT + 目标驱动实现 `ndo_xdp_xmit`（[id=75]）。
10. **bpfilter 教训**："UMH ELF 模块"路线最终未进主线，2020 年后换维护者转向 daemon 形态（[id=82] + digest 07）——引用 bpfilter 时务必注明是历史方案。同理，[id=64] prototype-kernel 文档的 "Missing Features" 清单是 2016 快照，所列缺陷大多已解决，当史料读。
11. **jumbo frames/大包**：单帧模型时代超页大小的包是硬伤，multi-buffer（XDP_USE_SG + XDP_PKT_CONTD）才解决，可移植代码限 18 frag（[id=79]）。
12. **资源坑**：本语料库中 id=68（slideshare XDP 宣讲）是 JS 反爬空壳，零内容勿引用（digests/04 明示）；[id=65]/`web/md/7.md` Cilium Reference Guide 本地只有目录索引页，正文需在线补抓子页（architecture/progtypes 等）。

## 9.5 与其他章的关系

- **前驱**：第 1 章（历史与总论）给出 BPF 从包过滤器到通用 VM 的时代线——本章是"回到本职"：BPF 名字里的 Packet Filter 在 XDP/tc 上完成闭环（[id=82] 正是这个视角）；eBPF 架构/verifier 章的 maps、helpers 调用约定（R1-R5 参数/R6-R9 callee-saved）、tail call、object pinning 在 XDP/tc 上原样生效（[id=54]/[id=55] 是机制主源）；BTF/CO-RE 章决定你的 XDP 程序能否跨内核版本分发。
- **后继**：AF_XDP 与用户态包处理章展开 XSKMAP/UMEM/四环模型（[id=79]）；硬件卸载章（digests/06）覆盖 NFP/SmartNIC 上的 XDP/tc offload（[id=52] 提到 Netronome offload 起点）；教程与示例代码章（digests/08-10）与项目章（digests/14-15）里 Cilium/Calico/Suricata/XDP-tools 都是本章机制的生产级消费者。

## 9.6 语料索引

| id | 名称 | 本地路径 | 本章用了什么 |
|---|---|---|---|
| 62 | The eXpress Data Path（Igalia, 2019） | web/md/62.md | 五 action 清单、最小示例全文与逐行讲解、veth 实验流程、driver vs generic、fail-open、"fast path→normal path" |
| 63 | tohojo/xdp-paper（CoNEXT'18 论文仓） | repos/tohojo/xdp-paper/ | 24 Mpps drop、Katran 5.2 Mpps vs IPVS 4.3x、iptables 1.8/4.8 对照、DDoS 19.5 Mpps 曲线、AF_XDP 20 Mpps、测试硬件与内核 commit、7 组 benchmark 目录 |
| 7/65 | Cilium BPF and XDP Reference Guide | web/md/7.md | 手册结构（Program Types: XDP+tc）、cBPF 载入时透明翻译为 eBPF |
| 67 | Herbert & Starovoitov XDP 原始提案 | web/pdf-txt/67.txt | carpool lane 比喻、性能技术清单、性能目标标尺、action 语义补注 |
| 69 | XDP Intro and future use-cases（2016） | web/pdf-txt/69.txt | driver RX/SKB 前定位、早期 3 action、内存模型代价与 page_pool、mlx4 实测 |
| 71 | XDP for DDoS protection（2017） | web/pdf-txt/71.txt | iptables 4.5-4.7 vs XDP 9.7/16.9 对比、blacklist 三件套、bpf_xdp_adjust_head VLAN/VRF、先测硬件上限方法论 |
| 72 | Memory vs. Networking（LSF/MM 2017） | web/pdf-txt/72.txt | page recycling 与 MM 层因果、redirect 跨设备归还页 |
| 74 | Julia Evans XDP 笔记（2017） | web/md/74.md | 270 行 C、bounds check 拒载、6 条实战 tips |
| 75 | XDP now with REDIRECT（2018） | web/pdf-txt/75.txt | bpf_redirect 7.5M vs map 13M、devmap/cpumap/xskmap 内部结构、xdp_frame/xdp_rxq_info、retpoline 案例 |
| 77 | High Speed Packet Filtering（Cloudflare 2017） | web/pdf-txt/77.txt | RX 调用树、"executed too late"金句、generic XDP 4.12、p0f2ebpf |
| 78 | How to drop 10 million pps（Cloudflare 2018） | web/md/78.md | 八级丢包阶梯全文数字、基准卫生坑、ethtool rx_xdp_drop |
| 79 | AF_XDP kernel.org 官方文档 | web/md/79.md | XSKMAP 前提、multi-buffer/XDP_PKT_CONTD/18 frag、FAQ 两坑 |
| 82 | bpfilter: Linux firewall with eBPF sauce | web/pdf-txt/82.txt | UMH ELF 模块设计、26 指令翻译实例、社区辩论、未竟后验 |
| 54/55 | cls_bpf netdev 1.1 slides+论文 | web/pdf-txt/54.txt, 55.txt | tc 挂载点、da 模式、verdict 码、cls_bpf 历史 commit、512 字节栈/无循环约束、tc 命令 |
| 52 | cls_bpf updates netdev 1.2 | web/pdf-txt/52.txt | tunnel metadata helpers（tc 与 XDP 能力差异点）、Netronome offload |
| 190 | Suricata bypass 博客 | web/md/190.md | 669 Mbps→39 Gbps（58x） |
| 194 | Calico eBPF data plane 手册 | web/md/194.md | netkit/tcx 挂载、bpfAttachType 三选 |
| — | digests/11/13/09/15 | digests/*.md | tcx.c 主线化、cilium/ebpf link tcx、TCX 课程、K8s 数据面两路线 |
| — | xdp-tutorial | repos/xdp-project/xdp-tutorial/ | 课程目录（basic01/packet03/advanced01-xdp-tc-interact） |
| — | prototype-kernel | repos/netoptimizer/prototype-kernel/ | DDoS 黑名单示例真身（kernel/samples/bpf/） |

## 9.7 AI agent 用法

本章知识被 agent 检索复用的配方（问题 → grep 词 → 命中位置）：

1. **"XDP 五种 action 语义/早期只有几个 action？"** → grep `XDP_ABORTED` → `web/md/62.md`（action 清单）；grep `PASS/DROP/TX` → `web/pdf-txt/69.txt`（2016 三 action 时代差）。
2. **"XDP vs iptables/tc 性能差多少？数字出处？"** → grep `24\\,Mpps`、`Katran`、`tbl:load-balancer` → `repos/tohojo/xdp-paper/xdp-paper.tex`（论文原文数字+硬件语境）；grep `1.688M`、`10.1Mpps`、`no_turbo` → `web/md/78.md`（八级阶梯+方法学）；grep `9.7` → `web/pdf-txt/71.txt`（同机对比）。
3. **"bpf_redirect 与 bpf_redirect_map 差异/cpumap 干什么用？"** → grep `bpf_redirect_map`、`CPUMAP`、`ptr_ring` → `web/pdf-txt/75.txt`。
4. **"bpfilter 为什么没成/UMH ELF 模块是什么？"** → grep `user mode helpers`、`UMH`、`ntohl` → `web/pdf-txt/82.txt`（L133-143 设计段、L232-241 指令实例）。
5. **"tc cls_bpf verdict 码/direct-action 怎么回事？"** → grep `TC_ACT`、`direct-action`、`sch_handle_ingress` → `web/pdf-txt/54.txt`；历史 commit 查 `web/pdf-txt/55.txt`。
6. **"tcx/netkit 怎么选？"** → grep `netkit`、`bpfAttachType` → `web/md/194.md`（Calico 实测口径：netkit 优于 TC/TCX）。
7. **"帮我跑通第一个 XDP 程序"** → `repos/xdp-project/xdp-tutorial/basic01-xdp-pass/`（骨架）+ `web/md/62.md`（veth+tcpreplay 完整命令流）。
8. **勘误提示**：`web/md/7.md` 与 id=65 是同一 Cilium 手册的两份目录快照（本地均只有索引页）；id=68 slideshare 为空壳，勿引用（digests/04 总评）。
