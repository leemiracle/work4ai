# 批次 digest：06-cBPF与硬件卸载（11 条）

**本批总评**：这批资源由两条线构成。前半（id 86-91）是 cBPF 的"根与干"——1993 年 McCanne & Jacobson 的 USENIX 开山论文给出 register-based CFG 过滤机 + in-place 过滤的原始设计动机（对比栈式 CSPF 与 STREAMS NIT 的性能证据），FreeBSD bpf(4) man page 与 libpcap 过滤语法是同一套抽象在当代系统里的 API 化落地，borkmann（Daniel Borkmann）2013/2014 两篇 devconf 讲稿则记录了 cBPF 在 Linux 侧被 cls_bpf/eBPF 吸收的关键过渡期，Cloudflare BPF Tools 展示 cBPF/JIT 在生产 CDN 规模的实战。后半（id 92-96）是硬件卸载线：Netronome/Netdev 的 eBPF-XDP SmartNIC offload 两个演进会谈、rprinz08/hBPF 的"eBPF CPU 用 FPGA 实现"学术项目、以及两条计算存储线（OpenCSD qemu-csd、SambaNova/EDAN 的 Delilah 论文）。质量分布：cBPF 线全是高权威一手源（论文+man page+内核维护者讲稿），硬件卸载线呈"早期探索标本"形态——NFP SmartNIC 路线随 Netronome 淡出市场而具历史价值，FPGA/eBPF 与 computational storage offload 则是仍在演化的小众前沿。对学习者的最佳路径：86 打地基 → 87/91 查 API → 88/89 看 Linux 化 → 92/93 看 offload 的真实约束清单。

---

## [86] The BSD Packet Filter: A New Architecture for User-level Packet Capture

- **是什么**：cBPF 的开山论文（McCanne & Van Jacobson，LBL，1992-12 完稿 / 1993 Winter USENIX），整个 BPF 家族（含 eBPF）的学术起点。
- **核心内容**：两大架构革新——①放弃 CSPF 的 memory-stack 表达式树，改用 register-based 累加器伪机 + CFG（control flow graph）过滤模型，映射到现代 RISC 寄存器机，避免模拟栈的访存流量；②放弃先拷贝后过滤（SunOS NIT/STREAMS 模式），坚持 **filter in place**（在驱动 DMA 落包处原位过滤），拒绝的包零拷贝。实测：比 NIT 快 10-150 倍（reject-all 大包场景 5μs vs 450μs），过滤器本身比 CSPF 快 1.5-20 倍（Filter 3 解析类场景 150 vs 549 条指令）。
- **关键机制**：伪机 = accumulator A + index register X + scratch memory M[] + 隐式 PC；指令 opcode:16/jt:8/jf:8/k:32 定长格式；条件跳转只有 jt/jf 8 位偏移（≤256 条），长跳转靠 BPF_JA 用 32 位 k；`4*(P[k]&0xf)`（BPF_MSH）寻址模式专为变长 IP 头 IHL 计算 hack 进指令集；越界访问=终止过滤返回 0（安全默认拒绝）；除零终止；return 值=截断字节数（0 即丢包）——"过滤器不仅决定收不收，还决定收多少"（Mike Karels 建议）。
- **亮点/坑**：CFG 相对树的本质优势是"解析状态被记住"——IP 分支内不必再测 ARP，一次解析多次比较；tree 模型即使加 short-circuit 也无法避免冗余解析。对齐坑：以太网头 14 字节导致 IP 头非 longword 对齐，NIT 的对齐拷贝在内核和用户态各付一次代价。
- **对学习者价值**：理解 eBPF 为什么长成这样的唯一一手源——verifier 的"前向跳转+有界循环"约束、BPF_LD/BPF_JMP/BPF_RET 指令类、MAP 的前身 M[]，全部在此定型。读 eBPF 源码前应先读此论文。
- **对 AI agent 用法**：本地 `web/pdf-txt/86.txt`（约 920 行全文）。可 grep `BPF_MSH|4*(\[k\]&0xf)|accumulator|scratch memory|reject all` 取指令语义；grep `NIT|CSPF` 取性能对比数据。引用历史事实（1993、McCanne、20 倍）时的权威出处。

## [87] The FreeBSD manual page about BPF（bpf(4)）

- **是什么**：FreeBSD 15.1-RELEASE 的 bpf(4) 内核接口手册页（2021-10 修订），cBPF 用户态 API 的活文档——论文 86 的设计在真实 OS 里 30 年后的样子。
- **核心内容**：/dev/bpf 字符设备 + BIOCSETIF 绑定接口 + BIOCSETF 装载过滤器的完整 ioctl 协议（BIOCSBLEN/BIOCIMMEDIATE/BIOCGSTATS/BIOCLOCK 等 30+ 个）；两种缓冲模式——默认 buffered read（read(2) 显式拷贝）与 **zero-copy 模式**（BPF_BUFMODE_ZBUF，双缓冲 struct bpf_zbuf + bzh_kernel_gen/bzh_user_gen generation number 所有权协议，用户态须用 atomic_store_rel/atomic_load_acq 内存屏障）；FILTER MACHINE 一节给出全部 cBPF 指令的规范语义（A <- P[k:4] 记法，比论文更正式，含 BPF_MOD/BPF_NEG/BPF_XOR 等 FreeBSD 后加的 ALU 扩展）；三个手写 BPF_STMT/BPF_JUMP 汇编级过滤器示例（RARP / 双主机 IP / finger TCP 端口含分片检查 jset 0x1fff）。
- **亮点/坑**：BPF_MSH 被官方称为 "a hack for efficiently loading the IP header length"；net.bpf.maxinsns=512 的程序长度上限（tcpdump -d 可估算）；BIOCLOCK 用于沙箱安全（锁死后不可再换过滤器）；BIOCFEEDBACK 可把注入包回喂为输入；BUGS 一节明示 SEESENT/DIRECTION 在硬件环回与点对点接口上不可靠。
- **对学习者价值**：从纸面设计到可编程接口的桥梁；手写 cBPF 指令数组是最硬核的入门练习（比直接写 eBPF 更能理解 verifier 在验证什么）。
- **对 AI agent 用法**：本地 `web/md/87.md`（约 55KB，前 68 行与尾部为页面导航噪声，正文在中间）。可 grep `BIOCSET|bpf_zbuf|FILTER MACHINE|BPF_MSH|maxinsns|BPF_STMT` 精确取 API 语义；写 pcap/FreeBSD 相关代码时的权威接口参照。

## [88] Linux' packet mmap(2), BPF, and Netsniff-NG（Borkmann, DevConf.CZ 2013）

- **是什么**：Daniel Borkmann（Red Hat，后来的 eBPF 共同维护者）2013 年的 devconf 讲稿，讲 Linux 用户态抓包全栈：AF_PACKET + packet mmap(2) 环 + cBPF 过滤 + netsniff-ng 工具链。eBPF 诞生（3.18, 2014）前一年 cBPF 在 Linux 的状态快照。
- **核心内容**：PF_PACKET SOCK_RAW 三种打开姿势对比；每包一系统调用的浪费 → 三大优化原则（借 Varghese《Network Algorithmics》命名）：RX/TX_RING 零拷贝环（"avoid obvious waste"）、packet fanout 多核分簇（"leverage off system components"）、内核 BPF 早丢弃（"shift computation in time"）；RX/TX 架构图给出 tpacket_rcv/run_filter/tpacket_snd 的精确内核路径；2013 年的 cBPF = net/core/filter.c 的 sk_run_filter 解释器 + x86_64/SPARC/PPC/ARM/s390 五架构 JIT。
- **亮点/坑**：最有价值的部分是 **bpfc + BPF JIT off-by-one 漏洞实录**（Markus Kötter, Linux 3.0）：x86_64 JIT 条件跳转目标差一字节 → 跳进指令中间；攻击者用精心构造的 BPF 程序在 JIT 镜像里"拼出"x86 机器码（`add r8,0x2a; call r8` 把 skb->data 指针当代码执行），实现内核任意代码执行——这是历史上 BPF JIT 缺乏 constant blinding 时代的经典内核提权路径，直接解释了后来 `bpf_jit_harden` 的存在理由。
- **对学习者价值**：一张讲稿同时覆盖高性能抓包三件套（mmap/fanout/filter）与 JIT 安全攻防史；ifpps 案例教"测量工具本身会丢包"（iptraf 24.6 万 pps vs 实际 137.8 万 pps）。
- **对 AI agent 用法**：本地 `web/pdf-txt/88.txt`（67KB，pdftotext 转换、逐页渐显有大量重复段落，去重后实际 28 页）。可 grep `off-by-one|call r8|bpf jit enable|TX_RING|fanout`；netsniff-ng 八工具清单（trafgen/mausezahn/ifpps/bpfc 等）与 trafgen 配置语法实例可作流量生成参考。

## [89] tc and cls bpf: lightweight packet classifying with BPF（Borkmann, DevConf.CZ 2014）

- **是什么**：Borkmann 2014 年讲稿，cBPF 进入 Linux 流量控制子系统（tc）的分类器——cls_bpf（3.13/3.14 合入）。这是 cBPF 从"抓包过滤器"扩展为"通用内核可编程部件"的关键一步，直接铺路 2014 年底的 eBPF。
- **核心内容**：tc 术语全景（qdisc classful/classless、class、classifier/ematch、pfifo_fast/mq 示例）+ 三张内核路径图（output path ×2 + ingress sch_ingress）；cls_bpf 的核心 trick——**把 packet(7) 的 BPF verdict 复用为 qdisc classid**（ret #0 = drop，ret #N = classid），一个 BPF 程序多个退出点即可做多类分类；Linux BPF extensions（K 区间 [0xfffff000,0xffffffff] 重载 load 指令读 ifindex/cpu/vlan_tci/mark/rxhash 等内核元数据，3.8/3.14 getsockopt SO_BPF_EXTENSIONS）。
- **亮点/坑**：性能对比硬数据——cls_bpf JIT 后 best 26 cycles（miss）/ worst 45 cycles（hit）vs cls_u32 的 64/113，快约 2.5 倍；工具链三件套 bpf_asm（asm→字节码）/bpf_jit_disasm（反汇编 JIT 镜像）/bpf_dbg（用户态单步调试 BPF，带断点与寄存器 dump，全部进 tools/net/）；ingress 只能 police 不能 shape 的限制讲得清楚（sch_ingress 入口在 __netif_receive_skb_core）。
- **对学习者价值**：理解 tc 数据面为什么最终被 cls_bpf/direct-action 统一（对比 cls_u32 配置地狱）；ingress/egress 内核挂载点图是读 XDP 前的必要背景。
- **对 AI agent 用法**：本地 `web/pdf-txt/89.txt`（21KB，无重复页问题）。可 grep `cls_bpf|classid|bpf_asm|bpf_dbg|ingress|26 cyc`；bpf_asm 输出格式（`4,40 0 0 12,...`）与 C 初始化器格式是生成/校验 cBPF 字节码的直接模板。

## [90] Introducing Cloudflare's BPF Tools（Marek Majkowski, 2014-07-03）

- **是什么**：Cloudflare 开源 bpftools（github.com/cloudflare/bpftools）的发布公告——用 Python 工具链生成 cBPF 字节码 + iptables xt_bpf 模块，在大规模 DDoS（DNS flood）到达应用前内核丢弃。cBPF 生产级实战的代表案例。
- **核心内容**：工作流五步：tcpdump 抓 pcap（须 EN10MB，`any` 接口的 LINUX_SLL 头可用 pcap2hex/hex2pcap 修复）→ parsedns 逐包解析 DNS 找攻击指纹 → **bpfgen** 生成匹配字节码（dns/dns_validate/suffix 三种生成器，`*.www.example.uk` 通配域名匹配）→ filter 脚本在 pcap 上离线验证（本例匹配 99.97% flood、--negate 查漏杀）→ iptables_bpf 生成部署脚本。实战案例：随机子域 NXDOMAIN flood 榨干 DNS 服务器 CPU，防御=直接按 `*.域名` 模式在 iptables 层丢包。
- **亮点/坑**：**xt_bpf 与 tcpdump 的字节码不可互换**——xt_bpf 的包从 IP 头开始（无 L2 头），tcpdump 假设有 Ethernet 头，bpfgen 靠 `--offset=0`（xt_bpf）/`--offset=14`（tcpdump）切换，这是最常被踩的坑；部署安全设计=ipset match-set 做"默认不生效"灰度开关（先加 IP 到 ipset 规则才激活），iptables_bpf_chain 可生成 accept/drop 多规则链。
- **对学习者价值**：完整展示"分析→生成→验证→灰度部署"的过滤器工程闭环；理解为什么 Cloudflare 后来全面转向 eBPF/XDP（此工具链 2017 年起被 bpf-tools→eBPF 生态取代）。
- **对 AI agent 用法**：本地 `web/md/90.md`（52KB，正文在 L855-1093，前后是海量 Cloudflare 导航/标签噪声）。可 grep `bpfgen|xt_bpf|--offset|ipset|parsedns`；实战命令行（tcpdump/bpfgen/iptables -m bpf --bytecode）可直接复用为 DDoS 缓解 runbook 素材。

## [91] Libpcap filters syntax（tcpdump filter 表达式语法）

- **是什么**：biot.com 摘录的 tcpdump/libpcap 过滤表达式语法参考（源自 tcpdump man page），cBPF 高层 DSL 的完整词典——libpcap 编译器把这些表达式翻译成 86 号论文定义的 cBPF 字节码。
- **核心内容**：三类限定符组合语法——type（host/net/port/portrange）× dir（src/dst/src or dst/src and dst，SLIP 与 Linux cooked 模式支持 inbound/outbound）× proto（ether/fddi/tr/wlan/ip/ip6/arp/rarp/decnet/tcp/udp）；fddi/tr/wlan 是 ether 的别名（802.11 只测 DA/SA，BSSID/RA/TA 不测）；特殊原语 gateway/broadcast/less/greater；`proto[expr:size]` 算术包内寻址（`ip[0]&0xf!=5` 抓带选项 IPv4、`ip[6:2]&0x1fff=0` 抓非分片、`tcp[tcpflags]&(tcp-syn|tcp-fin)!=0` 抓会话边界）。
- **亮点/坑**：**vlan/mpls/pppoes 关键字会"移动"后续表达式的解码偏移**（`vlan 100 && vlan 200` = QinQ 内层，每用一次偏移 +4）；ip6 protochain 6 会追踪扩展头链但生成的 BPF 代码无法被优化器优化（慢）；关键字转义（\tcp 在 C-shell 要 \\tcp）；IPv4 网络号的四种子网掩码缩写规则（192.168.1.0/192.168.1/192.16/10 分别对应 /32/24/16/8）。
- **对学习者价值**：这是把"英语式过滤意图"翻译成 cBPF 的中间层——读懂它才能理解 libpcap 编译器输出（tcpdump -d）的来源；示例区 12 个实战表达式（HTTP 载荷非空过滤的长表达式等）是最佳练习素材。
- **对 AI agent 用法**：本地 `web/md/91.md`（25KB 纯净无噪声）。查语法时 grep `portrange|protochain|tcpflags|vlan \[|proto.*\[expr` ；给 tcpdump/libpcap 写过滤器或解释 tcpdump -d 输出时的语义权威。

## [92] eBPF/XDP hardware offload to SmartNICs（Kicinski & Viljoen, netdev 1.2, 2017-10）

- **是什么**：Netronome 团队（Jakub Kicinski、Nic Viljoen）在 netdevconf 1.2 的会谈页——eBPF/XDP 程序卸载到 NFP SmartNIC 的首个系统性方案（配套 slides/video/paper 三件套链接）。
- **核心内容**：会谈大纲 a-j：透明卸载程序员模型（不需为卸载改代码）→ NFP（Network Flow Processor）硬件架构（packet path/chip layout/microengines/内存架构）→ 内核基础设施改造（TC/XDP hook、eBPF verifier 扩展、map hooks）→ **eBPF 字节码→NFP 汇编的翻译器**（非线性映射处理）→ 32 位架构上的 eBPF JIT 与 A/B 寄存器分配 → map 卸载到独立内存域 → 透明时分复用多线程加速 → 挑战与未来（解析/加密引擎）。
- **亮点/坑**：本页只是 session 元数据（2.3KB），无正文；价值在于锚定"通用 eBPF 硬件卸载"这一方向的开山位置——verifier 需要理解"程序将跑在设备上"这一全新验证目标，map 需跨内核/设备两个内存域同步。
- **对学习者价值**：eBPF offload 的编年史起点；配合 93 号（一年后的续集）构成完整演进线。
- **对 AI agent 用法**：本地 `web/md/92.md`（2.3KB，一分钟读完）。可 grep `NFP|verifier|microengine` 取大纲；深挖须走 paper 链接 eBPF_HW_OFFLOAD.pdf（netdevconf.org）。

## [93] Comprehensive XDP offload — Handling the edge cases（Kicinski & Viljoen, netdev 2.2, 2018）

- **是什么**：同团队一年后在 netdevconf 2.2 的续集会谈页——从"能卸载"推进到"全面卸载的边角案例"。session 元数据页（1.8KB）。
- **核心内容**：五大边角议题：① map 卸载的内核-FW 双侧架构与限制；② 工具链与可调试性（**bpftool 查看已卸载程序**——offload 后程序脱离内核可视域，调试是硬问题）；③ 32 位嵌入式架构实现（LLVM 的相关性、性能改进）；④ tail call 与多程序处理；⑤ **partial offload——判断哪些程序该卸载**（"最大挑战之一：以透明高效的方式决定卸载谁"）。
- **亮点/坑**：点出 XDP 比 tc 更适合 offload 的结构性原因——位于协议栈最底层；以及 offload 工程的真痛点不在翻译器而在 map 一致性、调试可见性、卸载决策。这批问题清单至今仍是 SmartNIC offload 的通用约束。
- **对学习者价值**：两篇连读=Netronome NFP eBPF offload 从 PoC 到产品化的完整问题演化史；Netronome 2020 年后淡出，但 nfp 驱动（drivers/net/ethernet/netronome）与这套内核 offload 框架仍在主线。
- **对 AI agent 用法**：本地 `web/md/93.md`（1.8KB）。grep `partial offload|tail call|bpftool` 取议题清单；内核侧配套代码关键词 `nfp/bpf/jit.c|BPF_F_TXR` 可在 linux 源码树定位。

## [94] hBPF - eBPF in hardware（rprinz08/hBPF）

- **是什么**：纯 Python3（LiteX/Migen 框架）写的 eBPF CPU，可仿真、可综合到 FPGA——"eBPF 指令集直接做成硬件 CPU"的实验项目（2021 年起，BSD-3）。学术玩具而非产品，明确声明不与 Alveo 类加速卡竞争。
- **核心内容**：三层实现共享同一套测试——Python 模拟器（快速）/ FPGA 仿真 / 真硬件（Wishbone 串口桥 + LiteScope 调试）；Harvard 架构分离程序存储（64-bit 宽，默认 1024 条指令）与数据存储（8-bit，默认 2048 字节装网络包）；可直接跑 LLVM 编译的 C 或汇编产物（无需修改）；R1-R5 输入参数、R0 返回、ticks 计数器测执行周期；三块 Xilinx 板（Arty-S7/Arty-A7/Zybo-Z7）+ LiteETH 网卡例程；CPU 核约 8000 LUT，100MHz 验证，多数指令 1 cycle，跳转 2 cycles，div/mod 最慢。
- **亮点/坑**：与 Linux eBPF 的三处偏差——`call` 不再调内核 helper 而是触发可扩展的 **call-handlers**（FPGA 硬件扩展点）；R1 不再是 context 指针而是普通参数；**无栈**（stack 不支持）。测试体系很讲究：.test 文件格式（asm/args/result/expected 四段，expect 里直接断言 clock 数，如 Fibonacci r1=9 → 324 cycles）。
- **对学习者价值**：想真懂 eBPF ISA 就读它的 cpu.py——每条指令的硬件语义裸露无遗；"每指令多少 cycle"这种在内核里问不出的问题这里有实测表（doc/opcodes.md）。
- **对 AI agent 用法**：本地 `repos/rprinz08/hBPF`（最后提交 2023-01-27，已停更）。可 grep 源码 `source/fpga/cpu.py`（指令实现）、`doc/opcodes.md`（周期表）、`tests/`（.test 用例格式）；引用时注意"无栈+call-handler"是 hBPF 方言，不是标准 eBPF。

## [95] OpenCSD eBPF SSD offloading（Dantali0n/qemu-csd）

- **是什么**：VU 阿姆斯特丹自由大学系列工作（ZCSD→OpenCSD）的实现仓：用 QEMU + uBPF + SPDK **仿真**一台 eBPF 可编程的计算存储设备（CSD），把文件系统操作（LFS 日志结构文件系统 FluffleFS）卸载到"SSD"上跑。含 2022 硕士论文全文（LaTeX 源码）、FOSDEM 2023 与 ICT.OPEN 2022 演讲。
- **核心内容**：九个模块——nvme_csd（QEMU 里仿真扩展 NVMe 命令承载 BPF 加载/执行）、nvme_zns（ZNS zoned I/O 抽象后端，memory 非持久与 SPDK 持久两种）、bpf_helpers/bpf_programs（CSD 内 BPF 程序与 helper 头）、fuse_lfs（**用户态 FUSE 实现的 LFS**，普通用户与 CSD 卸载可并发访问同一文件）、spdk_init；依赖矩阵庞大（QEMU 7.2/SPDK 22.09/DPDK/uBPF/libbpf 0.5/RocksDB 6.25 等，Meson 必须 <0.60 的 DPDK bug 钉版）。
- **亮点/坑**：设计目标是 snapshot consistency 的 LFS on ZNS CSD；测量数据（fio/entropy/passthrough）随仓分发可复现；ZCSD 前身论文（arXiv:2112.00142）与计算存储综述（arXiv:2112.09691）都在 README 挂链。工程上是研究原型：构建链脆弱（依赖精确锁版）、2023-11 后停更。
- **对学习者价值**："eBPF 不只属于网络"的最完整教材级示范——NVMe 协议扩展、ZNS 分区存储、用户态文件系统三件事被 eBPF 串起来；thesis/ 目录就是一篇完整硕士论文。
- **对 AI agent 用法**：本地 `repos/Dantali0n/qemu-csd`（最后提交 2023-11-01）。可查 `opencsd/nvme_csd`（BPF-NVMe 命令映射）、`opencsd/bpf_programs`（卸载程序样例）、`thesis/`（论文 LaTeX 章节）、`measurements/`（原始实验数据）；grep `nvme_csd|fuse_lfs|ubpf` 定位仿真链路。

## [96] Delilah: eBPF-offload on Computational Storage（Hedam et al., DaMoN '23, DOI 10.1145/3592980.3595319）

- **是什么**：哥本哈根大学/弗里堡大学团队（Niclas Hedam, Morten Tychsen Clausen, Philippe Bonnet, Sangin Lee, Ken Friis Larsen）在 DaMoN'23（SIGMOD 数据管理新硬件工作坊，2023-06，Seattle）发表的论文——**首个公开描述的、在真实计算存储设备上支持 eBPF 代码卸载的系统**。EU DAPHNE 项目产出，代码开源 github.com/delilah-csp。
- **核心内容**：背景锚定 NVMe TP4091 Computational Programs 标准——downloadable functions（运行时从 host 卸载，eBPF 为例）与 device-defined functions（预装 OS 镜像/FPGA bitstream）两类；SNIA 计算存储三分类（processor/drive/array）与三种架构（on-path PCIe / off-path p2pDMA / SmartNIC）。实现选型分析比较三种 eBPF 运行时——Linux 内核运行时（最成熟但适合 SmartNIC 场景）、硬件 eBPF（hBPF/Sephirot，适合 off-path FPGA 卡）、**uBPF（选中，跑在 PS 侧 ARM Cortex-A53 嵌入式 Linux 上，探索自由度最大）**。平台=OpenSSD Daisy（汉阳大学，CRZ 商售）：Zynq Ultrascale+ MPSoC（FPGA PL + ARM PS）+ PCIe Gen3x16 + 2x M.2。协议扩展 Eid-Hermes：XDMA 传程序与数据、BAR aperture 发执行命令、驱动用 **io_uring 异步 uring 命令**（比 ioctl 先进）。
- **亮点/坑**：最有价值的实测发现两条——①执行延迟有 ~15ms 不可接受的地板，分解后主凶是**全量 cache flush/invalidate**（A-53 无 DDIO/cache stashing，DMA 一致性只能靠刷整 cache，代价正比 cache 大小而非数据量）；引入 **selective cache flushing**（host 声明需失效的字节数）后延迟终于正比数据量。②BAR vs DMA 传输交叉点：**<1KB 用 BAR 快，>10KB 用 DMA 快** → 程序走 BAR、数据走 DMA 的结论。诚实声明：verifier 留作 future work（Linux verifier 禁无界循环不适合数据按摩场景，backward jump 又是必需的——这是计算存储 eBPF 化的真实张力点）。
- **对本批的串联**：论文背景一节直接引用了本批的 86（McCanne & Jacobson 1993）和 94（hBPF，被列为"eBPF foundation 最突出的硬件实现"），三条资源形成"cBPF 起源→硬件化→计算存储卸载"的闭环。
- **对学习者价值**：计算存储 + eBPF 交叉方向的最佳入门论文（7 页短文，覆盖标准、架构、实现、实测）；cache 一致性是嵌入式 offload 的隐形大头这一教训普适。
- **对 AI agent 用法**：**注意本地 `web/md/96.md` 是损坏的**（Wayback 把 PDF 原始字节存成了 .md，null 字节被替换，pdftotext/gs 均无法解析）；已修复性归档干净全文到 `web/pdf-txt/96.txt`（705 行，来源=作者版 hed.am/papers/2023-DaMoN.pdf，同 DOI）。可 grep `TP4091|selective cache|uBPF|XDMA|io_uring|BAR aperture` 取关键机制；引用 venue 请写 DaMoN'23（勿写成 HotStorage）。

---

## 附注（资源健康度）

- `web/md/96.md`：损坏（PDF 二进制误存为 md，838KB），已用作者版 PDF 提取文本补档至 `web/pdf-txt/96.txt`。
- 其余 10 条资源本地完好；`web/pdf-txt/88.txt` 含 pdftotext 渐显重复（去重后 28 页），`web/md/87.md` 与 `90.md` 有站点导航噪声，grep 时注意限定正文区。
