# awesome-ebpf 全资源消化总结（SUMMARY）

> 基准：github.com/qmonnet/awesome-ebpf @dc0c2065（2026-09-14）· 288 条资源全量消化
> 产物日期：2026-11-06 · 配套：INVENTORY.md（全清单）/ AGENT-GUIDE.md（AI 检索指南）/ digests/（21 批逐条消化）
> 本地资产：repos/ 83 浅克隆仓（2.7G）+ web/md 190 篇文章 + web/pdf-txt 20 份 PDF 全文

## 一、这份语料是什么

awesome-ebpf 是 eBPF 领域公认最全的精选清单（qmonnet/Cloudflare 维护）。本次把清单 288 条全部下载到本地并逐条消化，形成三层资产：**原始物料**（仓/HTML/PDF）、**逐条消化**（digests/ 21 批，每条"是什么/核心内容/坑/学习者价值/agent 用法"）、**本总结**。资源年代横跨 1993（cBPF 开山论文）到 2026-11（仍在日更的仓），构成一部完整的 eBPF 技术演化史。

## 二、知识主地图（按消化结果综合）

### 1. 根与史前史（1992-2013）
- **cBPF 开山**：McCanne & Jacobson 1993 USENIX 论文（id 86）——寄存器机 + CFG 验证 + in-place 过滤的设计动机，对栈式 CSPF 与 STREAMS NIT 的性能论证，一切 BPF 的源头。
- **前 eBPF 时代**：libpcap 过滤语法、FreeBSD bpf(4) 是同一抽象的 API 化；BPF 引入 Linux 的版本口径以作者本人（McCanne，1997 年 2.1.75）为准，清单所写 v2.5 有误（digest 02 已钉版勘误）。
- **过渡期**：Borkmann 2013/2014 devconf 讲稿（id 88/89）记录 cBPF 被 cls_bpf/eBPF 吸收的关键转折。

### 2. eBPF 诞生与机制内核（2014-2017）
- **第一手史料**：Starovoitov 2015 netconf 演讲（id 36，PDF 全文）是 eBPF 诞生的作者答辩——两大失败原型、verifier 三层机制；2014 LWN 报道（id 24 附近）是社区视角。
- **VM 设计**：11 寄存器 + verifier 静态验证 + JIT 三件套；`bpf(2)` syscall 全命令与 map 类型（Ferris Ellis 三部曲、igalia/Collabora 系列拆解）。
- **规范层**：RFC 9669（eBPF ISA 标准化）、BTF（kernel 文档 id 83 是唯一权威二进制格式参考，22 种 kind 快照比 2018 年代的 11 种新两代——两者对照即 BTF 演进史）。
- **内核源码入口**（批次 11）：UAPI 头（include/uapi/linux/bpf.h、filter.h）→ core 三大件（kernel/bpf/syscall.c、core.c、verifier.c）→ 挂载点（net/core/filter.c、kernel/trace/bpf_trace.c、kernel/seccomp.c）→ JIT（arch/x86/net/bpf_jit_comp.c）。本地 md 被 Anubis 反爬盾拦截，但路径清单本身即阅读路线图。

### 3. 网络数据面：XDP 与 tc（2016-2019 黄金期）
- **起源**：Cloudflare 1Mpps iptables 瓶颈 → partial kernel bypass → 通用 fast path（id 62 的叙事最完整）。
- **权威基准**：CoNEXT'18 xdp-paper（id 63，仓含论文+7 组可复现实验，ACM artifact evaluated 徽章）——单核 24Mpps drop、5.2Mpps L4 LB；Cloudflare 实测丢包 10M+ pps/CPU（id 78，4.14 内核口径，与论文 24M 是不同代际/硬件——见 docs/09 9.2.7 语境辨析；iptables 基线八级阶梯为 1.8~4.8Mpps）。
- **一手编年史**：Jesper Dangaard Brouer 系列 PDF（69/71/72/75）：2016 引入 → 2017 DDoS → 2017 内存瓶颈 → 2018 redirect。
- **生产战果**：Facebook Katran（四层 LB）、Cloudflare DDoS 管线、Suricata XDP bypass（39Gbps vs 669Mbps 经典数据）、upf-bpf（5G UPF，已并入 OAI 上游）。
- **K8s 数据面**：Cilium 谱系（7 条资源，从 2016 播客首秀到 CNCF 毕业项目，本地仓 2026-11 仍日更——唯一必须持续跟踪的活体）；Calico tc/tcx/netkit 路线 vs merbridge cgroup/sockmap 路线。
- **AF_XDP**：用户态生态吃 XDP 的统一通道（kernel.org 官方文档 id 79 是权威参考；DPDK PMD 与 PcapPlusPlus 已原生支持）。

### 4. 可观测性（论文 → 产业标配）
- 三条路线并存：全栈 APM 平台（DeepFlow/Coroot/SkyWalking Rover/Pixie，零侵扰 auto-instrumentation）、单点做深（kyanos 抓包回放、parca 连续 profiling、Hubble 网络流、Caretta 服务拓扑）、实验级样本。
- 采集点全覆盖：kprobe/tracepoint/uprobe/perf_event/XDP + ringbuf + DWARF/帧指针栈回溯。
- 珍贵发现：rstat 的"何时不该用 eBPF"定量弃用实录（sched_switch probe 在切换风暴时吃 1.8 核）；parca-agent CPU profiler 核心已切 otel ebpf-profiler fork（与 OTel 汇流的直接证据）；kyanos 的 openssl 1.0.2a→3.5.0 逐版本 uprobe 明文还原矩阵。
- 追踪工具祖师爷：bpftrace（高层语言 + Brendan Gregg 速查表=最实用资产）与 bcc（70+ 现成观测工具的工具箱属性 > 开发框架属性）。

### 5. 安全（攻防两线完整标本）
- **防御世代差**：Falco（CNCF 毕业级检测）世代 → Tetragon/Bombini/owLSM 的"内核态 detect→enforce"范式；LSM BPF 强制访问控制一线尤其拥挤（BPFJailer/owLSM/Bombini/bpflock）。
- **攻击面研究**：ebpfkit（Datadog 员工 rootkit，BlackHat 2021）+ ebpfkit-monitor（配套检测）攻防成对；bad-bpf（DEF CON 29 六件套数据面篡改教学）；TripleCross（UC3M 论文级，GOT 注入 + 仿 NSA Bvp47/CIA Hive 的 C2 触发器）。
- **老内核难题**：Red Canary（oxidebpf+LKCCB）与 Sysinternals（BTF autodiscovery）两套 CO-RE/offset 解法。
- **最新动向**：Inner Warden 上游改名转型 AI agent 护栏（eBPF 部分闭源化）——安全线与 agent 线开始交汇；AgentSight/ActPlane（批次 16）直接用 eBPF 观测并管控 AI agent。

### 6. 调度器与前沿
- sched-ext（scx）：Meta+Google 投入，6.12 主线；Gthulhu 桥接 K8s 分配→sched_ext 执行面。
- BPF arena/token、GPU/NPU 追踪等新特性在 eunomia 54+ 课系统教程（批次 09）中有覆盖。
- 硬件卸载三条岔路（批次 06）：Netronome NFP SmartNIC（已退场，历史价值）、hBPF FPGA CPU（停更但教学价值高）、计算存储 offload（Delilah——venue 勘误：DaMoN'23 非 HotStorage，digest 已钉版）。

### 7. 工具链与语言生态
- **现代正统**：libbpf + CO-RE + libbpf-bootstrap（脚手架范式）；LLVM BPF backend 是编译侧唯一主流。
- **语言库三条路线**：纯语言重实现（cilium/ebpf 纯 Go=事实标准、aya 纯 Rust=事实标准、zbpf Zig 实验）、C 库薄封装（libbpfgo）、配置/wasm 化分发（eunomia-bpf）。
- **用户态复刻**：uBPF/rbpf/PREVAIL（抽象解释验证器，PLDI'19）——"eBPF everywhere"；微软 eBPF for Windows 证明 verifier/执行引擎可解耦跨平台。
- **加载器演进**：bpfd 两代同名项目均停滞 → bpfman（CNCF，OCI 镜像分发 eBPF 程序，2026-11 仍活跃）是现代正统。
- **测试**：bpfcompat（真内核 VM 矩阵实测 .bpf.o 兼容性，已被 Falco/Inspektor Gadget 收进上游 CI）代表当代最佳实践；selftests/bpf 是权威测试语料。

## 三、给人类学习者的路径推荐

1. **第 0 层（建框架）**：ebpf.io what-is-ebpf（id 3）→ 项目全景页（id 4）
2. **入门长文**：igalia/Collabora 系列 + Ferris Ellis 三部曲（批次 02）→ Oracle Maguire 六部曲（批次 03，基于 4.14，注意口径代差）
3. **动手**：Liz Rice beginners 仓（id 48）→ libbpf-bootstrap → xdp-tutorial（官方实验仓）
4. **网络方向**：批次 04 XDP 专题（62 入门 → 63 论文 → 78 生产）+ 07 批 AF_XDP 文档
5. **追踪方向**：bpftrace 教程（id 58）→ bcc reference guide → eBPFChirp 7 篇实战（批次 09，篇篇带代码+µs 级实测数字）
6. **安全方向**：批次 18+20（先防御谱系后攻防标本，TripleCross 代码可读）
7. **查细节**：man 三件套（bpf(2)/bpf-helpers(7)/tc-bpf(8)）+ RFC 9669 + bcc kernel-versions 矩阵

## 四、消化过程中的重要勘误与发现

| # | 发现 | 出处 |
|---|---|---|
| 1 | BPF 引入 Linux 版本：清单/部分文档写 v2.5，作者本人口径=1997 年 2.1.75，采信后者 | digest 02 |
| 2 | Delilah 论文 venue 是 DaMoN'23 非 HotStorage（ACM Reference Format 实证） | digest 06 |
| 3 | Ingero 与 Synapse 两仓上游已删（404）；Inner Warden 改名转型 AI agent 护栏 | digest 17/18 |
| 4 | Cilium BPF/XDP Reference Guide 的 docs.cilium.io 旧路径已迁 reference-guides/（抓取时跳转壳，已补抓） | Phase 3 |
| 5 | bpf-docs 仓的 sigcomm 论文 PDF 文件名与清单 URL 差一截（-paper 后缀），本地映射修正 | Phase 3 |
| 6 | 285/286 为同 URL 重复条目（Other Lists 与 Acknowledgement 各链一次） | digest 19 |
| 7 | Netronome bpf-samples、ebpfkit 等多个仓浅克隆损坏，消化期已从 pack 文件/raw 恢复 | digest 10/20/18 |
| 8 | parca-agent CPU profiler 核心=otel ebpf-profiler fork | digest 17 |
| 9 | ExtFUSE 论文数据：FUSE 加速 17.54%→5.71% | digest 16 |
| 10 | Suricata XDP bypass：39Gbps vs 669Mbps | digest 15 |

## 五、已知缺口（诚实边界）

- ~~**slideshare 12 条**：JS 挡墙，幻灯片文本不可得~~（**2026-11-06 更新：已全数救回**——Wayback 快照含服务端 transcript，12/12 提取成功 1.6k-21k 字符，含 Brendan Gregg 两场名演讲全文）
- **git.kernel.org cgit 页 15+ 条**：Anubis 反爬盾（PoW 挑战），本地仅壳页——但 git 协议与 GitHub 镜像不受影响，digest 已补验关键目录
- **r.jina.ai**：对本网络（AS20473）要求认证，匿名兜底通道失效
- **2 仓上游已删**：ingero-io/ingero、gen0sec/synapse
- **个别 Cilium 手册页**（64/65 等）：仅抓到索引页，正文在子页（在线读 docs.cilium.io）

## 六、快速统计

- 288 条：web 170 · github_repo 84（82 本地+2 已删）· pdf 20 · github_other 13 · video 1
- 21 批 digest 全部通过 288/288 条目对账（manifest/_bin/verify_digests.py 可复验）
- 仓活跃度两极：Cilium/libbpf/PREVAIL/bpfman/DeepFlow 等 2026-11 仍日更；约 1/3 仓为 2016-2019 年代冻结史料
