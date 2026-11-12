# 批次：04-XDP专题（17 条）

## 本批总评

本批 17 条资源完整覆盖 XDP 的"历史—机制—应用—基准"四条线：起源叙事（Cloudflare 1Mpps iptables 瓶颈催生 partial kernel bypass，最终泛化为内核通用 fast path）、核心机制（XDP 四/五 actions、driver-level vs generic XDP、eBPF verifier/maps/helpers/tail call）、落地应用（DDoS 防护、load balancer、redirect、bpfilter 替代 iptables）与量化基准（CoNEXT'18 论文的 7 组 benchmark、Cloudflare 实测丢包 10M+ pps/CPU core）。质量分布呈"少数权威 + 多数历史文献"格局：CoNEXT'18 xdp-paper（id=63）与 Cloudflare 博客（id=78）是两大支柱；Jesper Dangaard Brouer 系列 PDF（id=69/71/72/75）是 XDP 演进的一手编年史（2016 引入 → 2017 DDoS → 2017 内存瓶颈 → 2018 redirect）；Cilium Reference Guide（id=65）是唯一仍在活跃更新的现代文档，其余多为 2016-2019 时代的史料。注意两个坑：id=64/65 本地只抓了目录索引页（正文需在线读或按其结构抓子页）；id=68 slideshare 抓取几乎为空壳。这批资源串联起来就是一部 XDP 技术演化史，对理解"为什么内核要内嵌可编程数据路径"极具价值。

---

## [62] The eXpress Data Path（Igalia 博客，Diego Pino，2019-01）

- 是什么：XDP 深度科普长文，Igalia 工程师 Diego Pino 所写，从动机到可运行示例贯通。
- 核心内容：XDP 设计源于 Cloudflare 在 Netdev 1.1 的 DDoS 缓解方案——iptables 只扛 1Mpps 而 spoofed 攻击可达 3Mpps，IRQ 洪泛致死机；因不愿放弃内核协议栈（对比 DPDK 全旁路），先用 Netmap 做 "partial kernel bypass"（部分 NIC queue 给用户态程序决定丢/放），后泛化为内核栈最早收包点的 eBPF checkpoint。逐条列出 XDP actions：XDP_PASS/XDP_DROP/XDP_TX/XDP_REDIRECT/XDP_ABORTED。给出完整 IPv6 filter 示例（parse_eth 检查 ethertype 0x86dd，bpf_debug 宏封装 bpf_trace_printk 写 trace_pipe）+ veth 对 + iproute2 加载（`ip link set dev veth1 xdp object xdp_ipv6_filter.o`，section 必须叫 "prog"）+ tcpdump/tcpreplay 验证流程。
- 亮点：明确 driver-level XDP（ixgbe/i40e/mlx5/veth/tap/tun/virtio_net，hook 在 Rx ring 最早点）与 generic XDP（协议栈较高点、任意网卡可用）的性能差异；结尾点出"fast path 正在变成 normal path"——iptables→nftables→bpfilter 的演进判断（2019 年视角，bpfilter 后未如期取代，但 XDP 化思路成立）。
- 对学习者价值：最佳中文读者的 XDP 入门第二篇（前作为其 XDP/eBPF 简介），示例可复制粘贴跑通。
- 对 AI agent 用法：本地 `web/md/62.md`；可 grep `XDP_REDIRECT`、`xdp_ipv6_filter`、`partial kernel bypass`、`0x86dd`；文中推荐阅读清单是权威资源索引（CoNEXT'18 论文、LPC2018 XDP future、jvns 教程）。

## [63] tohojo/xdp-paper（CoNEXT'18 XDP 论文官方仓）

- 是什么：ACM CoNEXT 2018 论文 "The eXpress Data Path: Fast Programmable Packet Processing in the Operating System Kernel"（Høiland-Jørgensen、Dangaard Brouer 等）的 artifact 仓，含 .tex 源码、数据集与实验笔记。
- 核心内容：论文 PDF 直接在仓内（`xdp-the-express-data-path.pdf`），slides 源为 org-reveal（`xdp-presentation.org/pdf`）。`benchmarks/` 目录是 7 组可复现实验（org-mode babel 笔记）：bench01 baseline、bench02 xdp_drop、bench03 ddos、bench04 fwd、bench05 xdp_redirect、bench06 load_balancer、bench07 latency，配套 traffic 生成脚本（udp_multi_ip.py 等）与 setup 脚本（DPDK 对照组 setup01_dpdk.org、huge pages/RX queues 配置）。测试硬件：Xeon E5-1650 v4 6 核 3.60GHz + 双口 Mellanox ConnectX-5 Ex 100Gbps NIC；论文所用内核 = Jesper 的 net-next-xdp 仓 xdp_paper01 分支 commit e641995a。figures/ 含全部论文矢量图（drop/ddos/redirect/router-fwd/load-balancer 测试曲线 + xdp-execution-diagram/kernel-diagram 架构图）。
- 亮点：**"artifact evaluated reusable" 徽章**（figures 里那张 jpg）——ACM 可复现性认证；这是 XDP 领域被引最多的系统论文（单核 24Mpps drop、5.2Mpps L4 load balancer 等结论的出处）。
- 活跃度：最后提交 2019-02-12，已冻结（论文 artifact 性质，属预期）。
- 对学习者价值：想拿到 XDP 性能主张的第一手数据与测试方法学（pktgen/T-rex/DPDK 对照），这是唯一权威源。
- 对 AI agent 用法：本地 `repos/tohojo/xdp-paper/`；论文全文 grep `xdp-the-express-data-path.pdf`（PDF）或读 `xdp-paper.tex`；实验细节 grep `benchmarks/bench0[1-7]*.org`；架构图 `figures/xdp-execution-diagram.svg`。

## [64] Work-in-progress documentation for XDP（Prototype Kernel 文档树）

- 是什么：Jesper Dangaard Brouer 维护的 prototype-kernel 项目 XDP 文档区（readthedocs）的顶层目录页，2016 年起、自称 WIP。
- 核心内容：本地抓取仅是 index 目录页，揭示文档结构：Introduction（What is XDP）、Design（overall design/requirements）、Implementation（**XDP actions / Userspace API / Missing Features / Drivers**）、Use-cases（**DDoS、DDoS scrubber、Load Balancer** 三案例）、End-user documentation（build environment、XDP programs with eBPF）。
- 亮点/坑：坑=本地只有这一页索引，正文各子页未随清单抓取；价值=它是 XDP 最早的官方设计文档（比 CoNEXT 论文早两年），源文件在 GitHub netoptimizer/prototype-kernel 仓 kernel/Documentation/networking/XDP/ 下仍可在线读。内容多为 2016-2017 时代快照（如 Missing Features 一节所列缺陷后来大多已解决），当史料读。
- 对学习者价值：了解 XDP 设计期的原始需求清单与 use-case 蓝图；"Drivers" 页是早期驱动支持矩阵的出处。
- 对 AI agent 用法：本地 `web/md/64.md` 只有目录；需子页时按 `https://prototype-kernel.readthedocs.io/en/latest/networking/XDP/<子页>.html` 补抓，或 clone netoptimizer/prototype-kernel。

## [65] BPF and XDP Reference Guide（Cilium 官方参考手册）

- 是什么：Cilium 文档站 "BPF and XDP Reference Guide" 顶层页——本批唯一仍在活跃维护（页面标注更新至 2026-11）的现代权威参考。
- 核心内容：本地抓取同为目录索引页。手册结构：**BPF Architecture**（Instruction Set、Helper Functions、Maps、Object Pinning、Tail Calls、BPF-to-BPF Calls、JIT、Hardening、Offloads、BPF sysctls）、**Development Tools**（LLVM、iproute2）、**Debugging and Testing**（bpftool、kernel testing、JIT debugging、introspection、tracing pipe）、**Program Types**（XDP、tc）。开头明确 eBPF vs cBPF 分野：kernel 3.18 起内核只跑 eBPF，cBPF（tcpdump 用的）载入时透明翻译成 eBPF。
- 亮点：这份 guide 是 eBPF 网络侧知识的事实标准（instruction set 64 位、helper 表、map 类型表都齐），且因 Cilium 商业支撑持续保鲜；旧地址 docs.cilium.io/en/latest/bpf/ 已迁到 reference-guides 路径。
- 坑：本地 `web/md/65.md` 只有 index；architecture/progtypes 等核心子页未抓。
- 对学习者价值：eBPF/XDP 查手册第一站，替代散落的 kernel Documentation。
- 对 AI agent 用法：本地仅索引，需按 `docs.cilium.io/en/stable/reference-guides/bpf/{architecture,progtypes,toolchain,debug_and_test}/` 补抓子页。

## [66] XDP Project overview（iovisor.org 官方页）

- 是什么：Linux Foundation IO Visor 项目的 XDP 官方技术页，XDP 的"项目自我定位"一手文本。
- 核心内容：XDP = 内核内高性能可编程数据路径，在软件栈最低点做 bare metal 包处理、无需改内核即可动态加新功能；四大卖点：不要求专用硬件、不要求 kernel bypass、不取代 TCP/IP 栈、与协议栈+BPF 生态协同工作。处理模型：内核组件直接从 driver 处理 RX packet-pages，**不预分配 skbuff、无软件队列**，一 CPU 一 RX queue 无锁，busy poll 或中断模式皆可。Use cases：DDoS 缓解的 pre-stack 过滤、forwarding/load balancing、GRO 类 batching、flow sampling/监控、ULP 处理。
- 亮点：**"XDP vs DPDK" 六条对照**是官方口径：免第三方代码与许可、busy polling/中断可选、免 huge pages、免独占 CPU、免用户态注包回内核、免新建硬件安全模型。资源区链接了 Dave Miller Netdev 1.2 视频、Brenden Blanco 20Mpps OpenStack demo 等早期史料；还有 xdp-vagrant 快速体验仓。
- 坑：页面 2016 年后基本未更新，是历史快照。
- 对学习者价值：理解 XDP 的设计哲学定位（augment 而非 replace 内核栈）的最佳一页纸。
- 对 AI agent 用法：本地 `web/md/66.md`；grep `kernel bypass`、`skbuff`、`Generic Receive Offload`、`iovisor/xdp-vagrant`。

## [67] eXpress Data Path (XDP)（Herbert & Starovoitov 原始提案 PDF）

- 是什么：Tom Herbert 与 Alexei Starovoitov（时在 Facebook）的 XDP 原始提案 slides（iovisor/bpf-docs 仓 Express_Data_Path.pdf），XDP 概念的出生证明。
- 核心内容：定义 XDP 为 Linux 网络数据路径内可编程高性能专用包处理器；性能技术清单（对理解 XDP 快在哪里最有价值）：lockless、batched I/O、busy polling、direct queue access、page recycling 免分配/释放、无 skbuff 元数据分配、高效 flow 表查找、packet steering、siloed 处理减少跨 CPU/NUMA 操作、RX flow hash、常见 NIC offload、cache prefetch/DDIO。基本 action 四种：Forward（TX queue 同 CPU 独占免锁）、Drop（返回错误即由 driver 回收页）、Normal receive（分配 skbuff 入栈/steer 到其它 CPU）、GRO 合并。硬件要求：multi-queue NIC + checksum offload + RSS + TSO（LRO/aRFS 可选）。
- 亮点：** freeway/carpoollane 比喻**——"内核协议栈是高速公路，kernel bypass 是另建高铁系统，XDP 是给高速公路加拼车道"，一图定调 XDP 与 DPDK 的关系；**性能目标**：drop 20Mpps/CPU（DOS 缓解）、forwarding 14Mpps/CPU（ILA router）、GRO 单 CPU 服务 100Gbps——这些数字后来成为 CoNEXT'18 论文实测验证的标尺。
- 对学习者价值：XDP 设计约束（loop-free 解析、无锁、页回收）的源头解释，比二手转述准确。
- 对 AI agent 用法：本地 `web/pdf-txt/67.txt` 全文可 grep `DDIO`、`page recycling`、`20M pps`、`carpool`。

## [68] eXpress Data Path slideshare（Brenden Blanco，Linux Meetup Santa Clara 2016-07）

- 是什么：Brenden Blanco（iovisor/BCC 作者）的 slides "eXpress Data Path: Getting Linux to 20Mpps"，XDP 早期性能宣讲。
- 状态：**本地抓取为空壳**——slideshare 的 JS Client Challenge 反爬页，仅 13 行错误提示，零内容。
- 补救：该 slides 与 id=67（Herbert/Starovoitov 提案）主题高度重叠（"Getting Linux to 20Mpps" 即 67 中的 drop 性能目标），66 号 iovisor 页也直接链接它；需要内容时从 slideshare 换通道（r.jina.ai / wayback）重抓，或直接看 iovisor 仓同名材料。
- 对 AI agent 用法：本地 `web/md/68.md` 无消化价值，标记为抓取失败条目，勿引用。

## [69] XDP − Intro and future use-cases（Jesper Brouer，2016-09）

- 是什么：Red Hat 首席工程师 Jesper Dangaard Brouer（XDP 三大推手之一）在 One.com 的早期宣讲，副标题"Linux Kernel's fight against DPDK"，XDP 项目 4.8 合入前夕的状态全景。
- 核心内容：XDP = NetDev1.1 "packet-page" 想法的 rebrand，在 driver RX 函数内、SKB 分配前直接操作 RX packet-pages；责任二分法：kernel 管 fabric（快速搬包），eBPF 管 policy（决定 action+读写包）。当时实测（mlx4 40G 单核+DDIO）：drop 20Mpps / TX-bounce 12Mpps / 带 udp+mac 改写 10Mpps；无 DDIO 时 prefetch loop trick 可救回 8.5→12.3Mpps。诚实的 Disclaimer：启用 XDP 改变 RX ring 内存模型（每包恒 alloc 4K 页）、理论上拖慢正常入栈路径（page allocator 瓶颈，催生 page_pool 项目）、影响 skb->truesize 与 TCP 吞吐。当时仅 3 个 action（PASS/DROP/TX），畅想未来 XDP_FWD 多端口转发、capture to userspace（AF_XDP 前身，零拷贝需 HW ring+HW filter+page_pool+premapping 四件套）、port abstraction table。use-case 全景：DDoS 过滤/scrubbing、LB（Facebook one-legged LB、ILA router）、tunneling encap/decap、sampling、L2 learning bridge、VM 交付。
- 亮点：**Linux 网络性能两年编年史**一页（TX 4→14.8Mpps、RX 6.4→12Mpps、XDP drop 20Mpps 已触 HW limit、IPv4 fwd 单核 1→2.5Mpps/多核 6→12Mpps）；EXTRA slides 讲 page_pool 设计（MM-summit 2016 来源、反馈环、可当 circuit breaker）与 RPS bulk enqueue 实验（4→9Mpps）。
- 对学习者价值：理解 XDP 早期设计取舍与"哪些畅想后来兑现了"（XDP_FWD→REDIRECT、capture→AF_XDP）的最佳史料。
- 对 AI agent 用法：本地 `web/pdf-txt/69.txt`；grep `page_pool`、`prefetch`、`one-legged`、`port abstraction`、`truesize`。

## [70] Network Performance Workshop（Jesper Brouer，Netdev 1.2 session 页）

- 是什么：Netdev 1.2（2016-10）Jesper 的 Network Performance Workshop 会议 session 元数据页，非内容正文。
- 核心内容：仅一段描述——workshop 讨论 Linux 网络性能的进展、当前问题与下一步；附 slides PDF 链接（people.netfilter.org/hawk/presentations/NetDev1.2_2016/net_performance_workshop_netdev1.2.pdf）与 YouTube 视频链接（vsjxgOpv1n8）。
- 价值定位：本条是入口型条目，真正内容在 slides 与视频（均未本地化）；与 id=69/72 同属 Jesper 性能方法学区，主题（pktgen 基准、time_based bulk 方法学）在 72 号 PDF 中有更完整展开。
- 对 AI agent 用法：本地 `web/md/70.md` 仅 31 行元数据；需要实质内容时按页内链接抓 slides PDF。

## [71] XDP – Used for DDoS protection（Jesper Brouer，OpenSourceDays 2017-03）

- 是什么：XDP DDoS 防护实战教程 slides（32+5 页），从理念一路讲到可抄的 eBPF C 代码，本批"工程落地"浓度最高的一份。
- 核心内容：两大场景——①Linux 内核自保护（引用 Thomas Graf："Empower Linux kernels to self protect in exposed environments"）：IPv4 blacklist 即插即用；②volume attack scrubbing：在网络边缘部署 XDP scrubber，改用 XDP_TX bounce、改写 VLAN header 进独立 VRF、清洗后包再回正常 VRF（非对称路由下 XDP_TX 即够）。代码教学线：kernel samples/bpf 的文件命名约定（`xxxxx_kern.c` eBPF 侧 / `xxxxx_user.c` 加载器 / `_cmdline.c` 运维工具）；`xdp_bench01_mem_access_cost` 样板教你在写自己程序前先测 NIC 硬件上限（--readmem/--action XDP_PASS）当 baseline；`xdp_ddos01_blacklist` 完整演示 PERCPU_HASH 黑名单 map、bpf_obj_pin 导出到 /sys/fs/bpf、chown 给非特权用户增删 IP、热重载 _kern.o 保持 map 数据、userspace 读 percpu map 需按 possible CPUs 求和。
- 亮点：**iptables vs XDP 同机对比**（i7-6700K + ConnectX-4 50G）：iptables raw 表最快 drop 4.5-4.7Mpps，XDP blacklist drop 9.7Mpps（mlx5 prefetch trick 未上游版 16.9Mpps）——约 2-3.6 倍差距；v4.10 驱动支持清单（mlx4/mlx5/nfp/qede/virtio-net）；EXTRA slides 讲 bpf_xdp_adjust_head() 做 VLAN/VRF scrubbing（某客户直接在入向链路预打 VLAN tag 免 push）。
- 对学习者价值：想"第一天就用 XDP 防 DDoS"的读者照抄即可用；也是学 eBPF map 用户态/内核态两侧编程范式的干净教材。
- 对 AI agent 用法：本地 `web/pdf-txt/71.txt`；grep `xdp_ddos01_blacklist`、`BPF_MAP_TYPE_PERCPU_HASH`、`bpf_obj_pin`、`xdp_bench01`、`scrubber`；示例代码真身在 netoptimizer/prototype-kernel 仓 kernel/samples/bpf/。

## [72] Memory vs. Networking（Jesper Brouer，LSF/MM-summit 2017-03）

- 是什么：Jesper 走进 Linux 内存管理峰会（MM 圈）的"跨圈"演讲——用 XDP 的需求倒逼 page allocator 改进，是 **page_pool 项目的立项陈词**。
- 核心内容：先把速度账算给 MM 圈听：10G 最小包线速 14.88Mpps = 包间隔 67.2ns = 3GHz 下仅 201 cycles；bulking 摊销不线性（SLUB bulk API 只提速 60%）。XDP 快的前提三条：不碰 MM 层、页保持 DMA mapped、钉在同 CPU（mlx5 50G 单核 DROP 17Mpps/TX 10Mpps）；而 XDP 真转发（跨设备 redirect）做不到，因为无法避免与 MM 层交互——页要在远端设备 TX 完成后归还。指出所有高速 NIC 驱动各自重新发明 page recycling（Intel 驱动直接拿 RX ring 当回收队列、靠 refcnt==1 判复用），向 MM 层提两个诉求：per-device 保持 DMA mapped 的页缓存分配器 API、页 refcnt 归零时的 destructor callback（盯上 page->compound_dtor 基础设施）。微基准数据：order-0 fast path 在 Mel Gorman 系列补丁下 276→143 cycles（v4.6→v4.11-rc1，-48%）；PCP cache=128 页、内部 bulk 32；跨 CPU 还页代价从 ptr_ring 基线 31 cycles 涨到 210 cycles（zone→lock 热锁，prefetchw 可省 58 cycles）；关 CONFIG_NUMA/zone_statistics 省 46 cycles（32%）。
- 亮点：本批唯一的"网络×内存管理"交叉视角，解释了 XDP redirect 与 page_pool 的因果链；"drivers' high-order allocation trick 坏处"（攻击者可钉死内存、reclaim/compaction stall）是系统设计教训。
- 对学习者价值：想懂 XDP 为什么需要 page_pool、以及 microbenchmark 方法学（隔离放大单一代码路径、勿被 provoked lock congestion 吓到）的必读。
- 对 AI agent 用法：本地 `web/pdf-txt/72.txt`；grep `page_pool`（本篇尚叫 recycle/destructor）、`compound_dtor`、`zone_statistics`、`ptr_ring`、`14.88`。

## [73] XDP for the Rest of Us（Gospodarek & Brouer，Netdev 2.1 tutorial session 页）

- 是什么：Netdev 2.1（2017-04）面向"普通人"（kernel 开发者/sysadmin/DevOps）的 XDP 入门 tutorial 的 session 元数据页。
- 核心内容：定位——XDP 不只属于大型数据中心；XDP 已进多个驱动、x86 与 arm64 可用。教程案例：**logtrigger / fail2ban 类工具与应用 + BPF 程序联动**，在包处理早期做 drop/allow 决策，比传统高位丢包获得更强 DDoS 防护；内容覆盖写/改简单 BPF 程序、编程式操作 BPF maps、early drop 的性能收益对比。slides（netdev 站内 apr7 目录）+ YouTube 视频（iBkR4gvjxtE）。
- 亮点：把 XDP 从"datacenter 专属"拉回普通服务器运维场景的开山 tutorial；与 id=74（Julia Evans 笔记）是同一活动的两个视角——74 号是该 tutorial 的第三方听课笔记，两者互补。
- 坑：本地只有 session 描述页，slides/video 未本地化。
- 对 AI agent 用法：本地 `web/md/73.md`；slides 需按 `http://netdevconf.org/2.1/slides/apr7/gospodarek-Netdev2.1-XDP-for-the-Rest-of-Us_Final.pdf` 抓取。

## [74] How to filter packets super fast: XDP & eBPF!（Julia Evans 笔记，2017-04-07）

- 是什么：Julia Evans（jvns.ca）在 Netdev 2.1 现场听 "XDP for the Rest of Us" tutorial（即 id=73）写的笔记——本批最好的"新手视角 XDP 教程"。
- 核心内容：eBPF 三事实：与 userspace 的一切交互走 maps（当时约 12 种）、**无循环故非图灵完备**、程序有界时间完成。教程产物 = DDoS blacklist 三件套（kern.c 过滤 + user.c 加载 + cmdline.c 运维），若干"祛魅"点：cmdline 工具无需 root——map 导出到 sysfs 文件后改 owner 即可；XDP 程序在内核树内编译故可直接复用 `struct ethhdr` 等内核结构体；整个解析+查表+裁决程序仅 270 行 C；不做 bounds check（`eth + offset > data_end`）verifier 直接拒载（静态分析保安全）。6 条实战 tips：perf top 见 `__bpf_prog_run` 就开 JIT；调 ulimit；用 readelf/objdump 看 kern.o——"It's just an ELF file, it's not magic"；`bpf_trace_printk` 输出在 trace_pipe；黑名单子网用 trie map；maps 可在 attach/detach 间持久化。
- 亮点：性能对照复述：iptables 4.5Mpps vs XDP 9.7Mpps（2 倍+），且强调性能之外"可写任意代码"才是相对 iptables 的本质优势。
- 对学习者价值：把 XDP 从论文概念变成"我也写得出来"的心理门槛击穿文，适合作为第一篇上手指引（配合 id=71 代码细讲）。
- 对 AI agent 用法：本地 `web/md/74.md`；grep `trace_pipe`、`PERCPU_HASH`、`bpf_load.c`、`72e473c`（prototype-kernel 锚定 commit）。

## [75] XDP now with REDIRECT（Jesper Brouer，Lund Linux Conf 2018-05）

- 是什么：XDP_REDIRECT 机制专题 slides——69 号（2016）里畅想的 XDP_FWD 到 2018 年以 map-based redirect 落地，本篇讲清了"为什么这个设计 brilliance"。
- 核心内容：driver 实现 `ndo_xdp_xmit`(+flush) 即可支持 redirect。关键性能事实：helper `bpf_redirect` 仅 7.5Mpps，而 `bpf_redirect_map` 达 13.0Mpps（单核）——map 版快的两个原因：①把 RX bulking 藏进 XDP core（driver 逐包调 xdp_do_redirect，NAPI poll 末尾统一 xdp_do_flush_map，批量≤64，摊销昂贵的 NIC tailptr/doorbell 写）；②新 redirect 类型零 driver 改动即可发明（"hopefully last XDP action code"）。三大 map 类型：**DEVMAP**（ifindex→netdev 出另一网卡）、**CPUMAP**（raw XDP frame 送远端 CPU、在那儿才建 SKB 入协议栈；MPSC 模型+per-CPU 快enqueue(8包)+bulk 入 ptr_ring+钉核 kthread 无锁出队）、**XSKMAP**（redirect 进 AF_XDP 用户态，即将落地）。cpumap 三用：隔离 driver XDP 层与协议栈（DDoS 防护时不拖慢 XDP）、修复 NIC HW RSS 对 VXLAN/双层 VLAN 等协议失明的 CPU 分布不均。附带 v4.16/v4.18 新机制：xdp_rxq_info（ctx->ingress_ifindex/rx_queue_index 替代 per-RX-queue program 诉求）、struct xdp_frame 标准化排队（信息存 frame headroom 免分配）、Memory return API（帧归还给来源 RX driver 的 per-RX-queue 级 API，AF_XDP zero-copy 的前提）。
- 亮点：**Spectre v2 实录**——CONFIG_RETPOLINE 把 XDP redirect 从 ~13Mpps 打到 6Mpps，真凶不是 ndo_xdp_xmit 间接调用而是 DMA API 的函数指针，Christoph Hellwig PoC 补丁救回 ~10Mpps；安全缓解与高性能数据路径冲突的典型案例。另有一页 "Why kernel developers should love BPF"：hook 只定义 action 集+受限 helpers，用户策略走 userspace API/BPF map，**终结了为每个新策略造内核 ABI（sysctl/procfs/ioctl）的循环**。
- 对学习者价值：redirect 家族（devmap/cpumap/xskmap）设计动机与内部结构的一手讲解，XDP 进阶必读。
- 对 AI agent 用法：本地 `web/pdf-txt/75.txt`；grep `bpf_redirect_map`、`CPUMAP`、`ptr_ring`、`xdp_frame`、`RETPOLINE`。

## [76] XDP workshop — Introduction, experience, and future development（Tom Herbert，Netdev 1.2 session 页）

- 是什么：Tom Herbert（Facebook，XDP 原始提案人）在 Netdev 1.2（2016-10）的 XDP workshop 会议页，视频条目（slides 标注 "to be added" 未上传）。
- 核心内容：定位 XDP 为"尽可能靠近硬件的可编程高性能数据路径"，BPF 提供可编程性实现 virtual switch/LB/firewall 等 middlebox 功能；关键愿景——**XDP 程序可移植到多个 XDP 平台**（不止 Linux 内核，还有 NIC offload、switch、DPDK、其它 OS）。workshop 四议题：XDP 设计原则与 API 模型（期望配套论文，即后来的 CoNEXT'18）；写/跑/调 XDP 程序实战（ILA router 与 L4 load balancer，预计首批生产用例）；其它平台上的 XDP（HW offload、DPDK、Windows/BSD）；未来方向清单——Cilium、Ceth、网络虚拟化、virtual switch、**P4 to XDP compiler**、XDP over DPDK/VPP。
- 价值定位：入口元数据页，正文在 YouTube 视频（lpJk_HcCLnQ）；其议题清单是 2016 年视角的"XDP 路线图"，可对照后来兑现情况（Cilium 大成、ILA 消亡、P4→XDP 有 eBPF backend 但未成主流）。
- 对 AI agent 用法：本地 `web/md/76.md` 仅元数据；需视频转录才能深挖。

## [77] High Speed Packet Filtering on Linux（Gilberto Bertin，Cloudflare，2017）

- 是什么：Cloudflare DDoS mitigation 团队工程师的"Linux 高速包过滤过去/现在/未来"演讲，XDP 时代来临前的完整决策链，含**全批最详细的内核 RX 路径标注调用树**。
- 核心内容：Cloudflare 规模（115 PoPs、6M+ 域名、4.8M HTTP rps、1.2M DNS qps；日常攻击 50-100Mpps/50-250Gbps，峰值 250Mpps/480Gbps）。演进阶梯：①iptables+xt_bpf 时代——用 bpfgen p0f 生成 cBPF 字节码配 iptables -m bpf 做 SYN flood OS 指纹过滤（cloudflare/bpftools），但 iptables 最多 2-3Mpps 且 CPU 耗尽；金句 "**Iptables is not slow. It's just executed too late in the stack**"；②kernel bypass（Netmap/EF_VI/PF_RING/DPDK）单核 6-8Mpps，比 iptables 快一个数量级，但合法流量要 reinject、要占核、有上下文切换；③XDP——同 bypass 的优点（无 skb 分配、无内核处理、无 DMA map/unmap）又保留内核集成（无需 reinject），e1000 代码示例展示 XDP_DROP 直接复用已 DMA mapped 的页。全篇最有价值的是 net_rx_action→napi→build_skb→GRO→ip_rcv→conntrack→iptables→tcp_v4_rcv 的逐函数标注图，直观展示 XDP 在 build_skb 之前的插入点。
- 亮点：**p0f2ebpf 自动代码生成器**——把 p0f 被动 OS 指纹签名直接编译成 XDP eBPF C 代码（示例生成物逐项匹配 TTL 区间/DF 位/TCP options 布局），"为什么手写规则，不自动生成 XDP 程序"的前 LLM 时代思路；实操指引：Generic XDP 自 Linux 4.12 起任意网卡可用。
- 对学习者价值：一张调用树看懂"包在内核里走了多少路才到 iptables"，是理解 XDP 价值的最直观材料。
- 对 AI agent 用法：本地 `web/pdf-txt/77.txt`；grep `napi_gro_receive`、`xt_bpf`、`p0f2ebpf`、`buffer_info->dma`、`Generic XDP`。

## [78] How to drop 10 million packets per second（Marek Majkowski，Cloudflare Blog，2018-07-06）

- 是什么：Cloudflare 经典博文——同机同流量下逐层对比 Linux 全部丢包手段的 8 级阶梯，XDP 系列科普中被引最多的一篇（有官方中文版）。
- 核心内容：测试方法学本身即教材：14Mpps 小 UDP 包、ethtool flow steering 全部导入单 CPU 单 RX queue、随机源 IP/port 专打 conntrack；两个基准卫生坑——**残留的 raw socket（如忘了杀的 tcpdump）会毁掉全部性能**（`ss -A raw,packet_raw -l -p` 检查）、关 Turbo Boost 把标准差从 ±1.5% 压到 0.25%；测试内核 4.14（KPTI+retpoline 已开）。8 级结果（单核丢包速率）：①应用 recvmmsg 循环 **175kpps**（瓶颈是 100% 占用的 SOFTIRQ）→ ②NOTRACK 关 conntrack **333k**（SO_BUSY_POLL 可到 470k）→ ③socket 挂 cBPF filter（SO_ATTACH_FILTER）**512k**（在 softirq 里丢、省唤醒应用）→ ④iptables INPUT DROP **608k** → ⑤iptables raw 表 PREROUTING DROP **1.688M**（大幅跳升，作者自承没完全搞懂为何 raw 快这么多）→ ⑥nftables netdev ingress hook（priority -500）**1.53M**（反而比 raw iptables 略慢，反直觉）→ ⑦tc ingress u32 match action drop **1.8M** → ⑧**XDP_DROP 10.1Mpps**（iproute2 一行加载 `ip link set dev ext0 xdp obj xdp-drop-ebpf.o`，ethtool -S 看 rx_xdp_drop 计数）——从应用到 XDP 约 **58 倍**差距。IPv6 各档略低（包更大）。
- 亮点：结论务实的分层建议（随机/伪造源 IP 攻击关 conntrack 有收益但要小心 conntrack 有用的攻击；raw 表显著快于 filter 表；Cloudflare 实际混用全部手段，iptables 由 Gatebot 管线管理，专有 kernel offload 正被 XDP 替代）；全部复现代码在 cloudflare/cloudflare-blog 仓 2018-07-dropping-packets/。
- 对学习者价值：Linux 各过滤钩子（socket BPF/iptables/nftables ingress/tc ingress/XDP）的位置-性能-易用性三维对照的唯一单表，面试与选型级常识。
- 对 AI agent 用法：本地 `web/md/78.md`（正文在 L865-1208，前面 800 行是站点导航噪声可跳过）；grep `NOTRACK`、`SO_ATTACH_FILTER`、`flow-type udp4`、`no_turbo`、`rx_xdp_drop`、`mmwatch`。
