# eBPF 知识库（docs/）· 总索引

> 定位：基于 awesome-ebpf 全量语料（288 条资源、83 仓、190 篇文章、20 份 PDF）写成的**专家向教学知识库**。
> 读者：想从初学者成长为专家的工程师；AI agent（配合上级目录 AGENT-GUIDE.md 使用）。
> 全部 16 章 ≈ 29 万字符，每章 8 节固定结构：导读 → 直觉层 → 原理层 → 实践层 → 深水区与坑 → 章间关系 → 语料索引 → AI agent 用法。
> 事实纪律：断言带语料锚点（[id=N] 或本地路径），语料未证实的标"待核实"；性能数字带出处与语境。

## 章节地图

### 第一部分：内核机制（第 1-6 章）——"eBPF 是什么、为什么安全"

| 章 | 标题 | 一句话 | 规模 |
|---|---|---|---|
| 1 | [历史与总论](01-历史与总论.md) | 1992 cBPF 到 2026 sched_ext 的完整演化史与第一性动机（含 13 条勘误） | 19.8k |
| 2 | [VM 与指令集](02-VM与指令集.md) | 11 寄存器、8 字节指令编码、JIT/解释器双模、RFC 9669（含真实字节码逐字段解码） | 17.7k |
| 3 | [Verifier](03-Verifier.md) | 两阶段验证、状态剪枝、日志读法、PREVAIL 理论对照（xdp-newbies 三篇为骨架） | 16.4k |
| 4 | [Maps](04-Maps.md) | 类型全表、并发语义、ringbuf vs perf array、生命周期与 pin | 21.6k |
| 5 | [程序类型与挂载点](05-程序类型与挂载点.md) | 30+ prog type 四域全景表，"岗位合同三绑定"选型心智 | 14.3k |
| 6 | [Helpers](06-Helpers.md) | 211 个 helper 的 13 功能族分类 + top20 速查 + prog type×map×helper 三重兼容机制 | 17.6k |

### 第二部分：现代工程（第 7-8 章）——"怎么写出可移植的程序"

| 章 | 标题 | 一句话 | 规模 |
|---|---|---|---|
| 7 | [加载与 libbpf](07-加载与libbpf.md) | ELF→内核完整加载链、三代前端对比、skeleton/bpf link/pin 生命周期、bpftool 速查 | 19.0k |
| 8 | [CO-RE 与 BTF](08-CORE与BTF.md) | 结构体漂移问题、BTF 二进制格式、dedup 算法、vmlinux.h 与 BPF_CORE_READ 实操 | 17.3k |

### 第三部分：应用域（第 9-13 章）——"拿它做什么"

| 章 | 标题 | 一句话 | 规模 |
|---|---|---|---|
| 9 | [XDP 与 tc](09-XDP与tc.md) | 内核数据面编程：五 action、devmap/cpumap、CoNEXT'18 权威基准、bpfilter | 19.1k |
| 10 | [AF_XDP 与用户态网络](10-AF_XDP与用户态网络.md) | UMEM 四环机制 + 用户态网络三路线对比（AF_XDP/f-stack/passt）+ 选型决策树 | 14.1k |
| 11 | [可观测性](11-可观测性.md) | 三类探针、栈回溯、bpftrace/bcc 实战、SSL 明文观测、连续 profiling、"何时不该用"反例 | 17.3k |
| 12 | [安全](12-安全.md) | 三代防御演进（Falco→detect→enforce→LSM MAC）、攻击标本三级台阶（bad-bpf/ebpfkit/TripleCross） | 17.3k |
| 13 | [sched_ext 调度器](13-sched_ext调度器.md) | struct_ops→DSQ→四步调度周期、三层安全兜底、scx 生态（rusty/layered/eevdf） | 15.6k |

### 第四部分：生态与边界（第 14-16 章）——"外面的世界与活下来"

| 章 | 标题 | 一句话 | 规模 |
|---|---|---|---|
| 14 | [硬件卸载与跨平台](14-硬件卸载与跨平台.md) | NFP 兴衰、FPGA/hBPF、计算存储 offload、Windows 移植、用户态运行时谱系 | 20.2k |
| 15 | [工具链与工程实践](15-工具链与工程实践.md) | 源码到生产全链路：三代加载器、语言库三路线、四层测试金字塔、排障四板斧、选型决策表 | 21.8k |
| 16 | [生态与社区](16-生态与社区.md) | L0-L6 生态分层地图、治理谱系（IO Visor 兴衰→基金会/CNCF）、邮件列表主战场、活跃度五档表、入行路径 | 23.3k |

## 配套三件套（自学闭环 + 速查）

| 产物 | 用途 | 规模 |
|---|---|---|
| [GLOSSARY.md](GLOSSARY.md) | 术语表：129 词条中英对照，定义口径=16 章原文，含 10+ 处易混词辨析（fentry vs kprobe、ringbuf vs perf array…） | 36k |
| [EXERCISES.md](EXERCISES.md) | 练习册：64 题（16 章×4）三档渐进（概念/实操/深水），实操题路径与 grep 提示全部实证，答案要点文末闭环 | 103k |
| [CHEATSHEET.md](CHEATSHEET.md) | 速查手册：bpftool/bpftrace one-liners/libbpf API/SEC 对照/verifier 报错对策/map 选型/排障四板斧 | 16k |

学习路径用法：系统通道每学完一章 → 做 EXERCISES 对应 4 题；查词用 GLOSSARY；日常操作翻 CHEATSHEET。

## 姊妹篇：工作区级网络知识库

同工作区 `../../knowledge/` 另有三份深度消化（与第 10 章交叉引用）：

- [f-stack](../../knowledge/f-stack.md)（12.9k）——DPDK+FreeBSD 全栈 kernel-bypass 路线
- [passt](../../knowledge/passt.md)（12.3k）——无特权用户态协议栈"协议翻译器"流派
- [systemd-network](../../knowledge/systemd-network.md)（22.4k）——networkd 状态机、38 种 netdev、自研协议库、resolved、systemd×eBPF 交汇

## 推荐学习路径

**快速通道（有内核/C 基础，2 周）**：第 1 章 → 第 7 章实践层跑通 minimal → 第 2 章 → 回到第 7 章原理层 → 第 8 章 → 第 11 章用 bpftrace 玩起来 → 按兴趣选第 9/12 章。

**系统通道（零基础到专家，3-4 月）**：
1. 月 1（机制）：第 1→2→3→4 章（配合 Liz Rice 教学仓动手）
2. 月 2（工程）：第 5→6→7→8 章（libbpf-bootstrap 全部样例跑一遍）
3. 月 3（应用）：第 9 或 11 章（网络或可观测选主线）+ 第 15 章工具链
4. 月 4（纵深）：第 10/12/13/14 章按方向选修 + 第 16 章进入社区

**AI agent 通道**：读 [../AGENT-GUIDE.md](../AGENT-GUIDE.md)（任务→章节→语料三级检索地图），知识库当工具书按需查，不必线性读。

## 质量与已知边界

- **引用数字前必查 [../ERRATA.md](../ERRATA.md)**——33 条全局勘误总表（🔴必改/🟡带语境/🟢勿引用三级），与各章 N.4 互为总分
- 16/16 章通过结构验收（`manifest/_bin/verify_chapters.py`）；语料引用 148/288 资源带正式 [id=N] 锚，其余以名称/路径方式覆盖（Cilium/kyanos/netdev 等名称级引用密布全文）
- 章内自带的勘误合计 30+ 条（各章 N.4 深水区），最重要的三条：BPF 入 Linux 版本采信作者口径 2.1.75；Delilah venue=DaMoN'23；39Gbps 出自 NFQ mark bypass 非 XDP
- 语料固有缺口（第 16 章 16.4 与各章坑节有详表）：~~slideshare 12 条无正文~~（**已救回**：Wayback 快照提取 12/12 幻灯片 transcript）、git.kernel.org 网页被 Anubis 盾（digest 已补验路径）、2 仓上游已删
- 章节事实基准 = 2026-11-06 语料快照；活体仓演进由每日 06:17 的 track_alive.sh 跟踪（manifest/track/track.log）
