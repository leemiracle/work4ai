# eBPF 知识库全局勘误表（ERRATA）

> 汇总 288 条语料消化与 16 章写作过程中发现的全部勘误/口径钉版。**引用本库数字前先查这张表**。
> 每条含：错误流传说法 → 正确口径 → 证据 → 详细出处章节。
> 分级：🔴=广泛流传的错误（引用必改）；🟡=口径需带语境（裸引易误导）；🟢=上游已失效/已删（勿再引用）。

## A. 历史与版本类

| # | 级 | 勘误点 | 正确口径 | 证据 | 出处 |
|---|---|---|---|---|---|
| A1 | 🔴 | BPF 引入 Linux 版本写 v2.5 | **1997 年 2.1.75**（作者 McCanne 本人口径） | digest 02 逐源核对 | docs/01 N.4 |
| A2 | 🟡 | "寄存器 10 个"与"11 个"混用 | r0-r9 通用 + r10 只读帧指针=11 个；文档口径不一 | Design Q&A + rbpf 源码 | docs/02 |
| A3 | 🟡 | "eBPF 无循环"当成现状 | 4.18 起支持有界循环；早期资料的说法已过时 | bcc kernel-versions | docs/02/03 |
| A4 | 🟡 | scx 相关资料写"CFS 语境" | scx OVERVIEW 的 CFS 表述是年代差，现主线为 EEVDF；scx_eevdf=内核 fair.c 移植 | scx 仓 OVERVIEW/scheds | docs/13 |

## B. 性能数字类（引用重灾区）

| # | 级 | 勘误点 | 正确口径 | 证据 | 出处 |
|---|---|---|---|---|---|
| B1 | 🔴 | "Suricata XDP bypass 39Gbps" | 39Gbps 出自 **NFQ mark bypass**（iperf localhost/MTU1500，2016-09 博客），非 XDP 通道；XDP bypass 是 2017-18 后续演化 | web/md/190.md 原文 | docs/10 N.4 |
| B2 | 🔴 | "iptables 4.5Mpps"（无出处流行说法） | Cloudflare 八级阶梯实测 **1.8（conntrack）~4.8（raw）Mpps**（4.14 内核）；论文对照场景另有口径 | web/md/78.md + xdp-paper.tex | docs/09 9.2.7 |
| B3 | 🟡 | XDP 丢包 "24Mpps" 与 "10M+ pps/CPU" 并存 | 两者都对但语境不同：24M=CoNEXT'18（Mellanox ConnectX-5 100G+定制内核）；10.1M=Cloudflare 2018（4.14 内核八级阶梯）。跨语境直比是大忌 | tex L852 与 web/md/78.md | docs/09 |
| B4 | 🟡 | f-stack "25×" 与 passt "4-50×" 直接对比 | 两条倍数的分母各不相同（25× vs 调优内核栈；4-50× vs slirp 系用户态栈），跨路线直比倍数是选型大忌 | 两仓 README | docs/10 10.2 / knowledge/README |
| B5 | 🟡 | "uprobe 开销大不可用" | 实测 ~0.2µs/请求、CPU≤0.3%——与 syscall tracepoint（11.69% CPU）差两个量级，挂点经济学决定选型 | web/md/114.md | docs/11 11.2 |
| B6 | 🟡 | Red Canary 基准引用偏差 | +19%（14254 vs 11989 execl/s）是 eBPF sensor vs 无 sensor 的开销对比，勿引成"检测增益" | web/md/220.md | docs/12 |
| B7 | 🟡 | ExtFUSE "FUSE 加速 3 倍" | 原文数据：syscall 开销占比 17.54%→5.71%，不是 3 倍吞吐 | 论文 PDF | docs/16 |

## C. 上游变动类（引用前查活）

| # | 级 | 勘误点 | 现状 | 证据 | 出处 |
|---|---|---|---|---|---|
| C1 | 🟢 | ingero-io/ingero 仓 | 上游已删（GitHub 404，web+api 双证） | 2026-11-06 实测 | INVENTORY |
| C2 | 🟢 | gen0sec/synapse 仓 | 上游已删（同上） | 同上 | INVENTORY |
| C3 | 🟢 | Inner Warden | 上游改名并转型 AI agent 护栏（eBPF 部分闭源化） | digest 18 | docs/16 |
| C4 | 🟡 | Delilah 论文 venue 写 HotStorage | 实为 **DaMoN'23**（ACM Reference Format 实证） | 论文 PDF | docs/14 |
| C5 | 🟡 | ebpf.io 项目全景 "42 Emerging" | 实测快照 **46 Emerging**（10 Major+46=56，逐项清点） | web/md/4.md | docs/16 |
| C6 | 🟡 | Cilium docs.cilium.io/en/latest/bpf/ 旧路径 | 已迁 **reference-guides/bpf/**（旧路径是 JS 跳转壳） | Phase 3 抓取实证 | AGENT-GUIDE |
| C7 | 🟢 | Netronome NFP 硬件线 | 厂商退场（2018-11 停更→Corigine 收购停线）；内核框架仍在 | git log 实测 | docs/14 |
| C8 | 🟡 | bpf-docs 里 sigcomm PDF 文件名 | 清单 URL 带 `-paper` 后缀，实际文件 `sigcomm-ccr-InKev-2016.pdf` | 本地仓清单 | Phase 3 |

## D. 技术口径类

| # | 级 | 勘误点 | 正确口径 | 证据 | 出处 |
|---|---|---|---|---|---|
| D1 | 🟡 | "seccomp 是一种 prog type" | seccomp 用 cBPF 经典过滤器（sock_filter），**不是** BPF_PROG_TYPE | Oracle 系+内核文档 | docs/05 N.4 |
| D2 | 🟡 | 指令上限"4096 条"单口径 | 三套口径并存：非特权程序 4096（BPF_MAXINSNS）/ verifier 路径探索 100 万（5.2+）/ uBPF 65536（uint16 pc 自然上界） | Design Q&A + rbpf/ubpf | docs/02 N.4 |
| D3 | 🟡 | tail call 层数 "32" | 32 是 MAX_TAIL_CALLS 计数上限（0-31 索引），不同资料写 33 属计数口径差 | libbpf 语义 | docs/06 N.4 |
| D4 | 🟡 | "bpf_loop 5.15 引入" | 核对 bcc kernel-versions 实为 **5.17** | web/md/22.md | docs/06 |
| D5 | 🟡 | web/md/83.md（BTF 文档）被引为 helper 参考 | 实测该文件零 helper 内容 | 文件实测 | docs/06 N.4 |
| D6 | 🟡 | AF_PACKET v4 论文数字 | 论文官方勘误页存在（语料内 AF_XDP FAQ 提示），引用前查 | web/md/79 | docs/10 N.4 |
| D7 | 🟡 | 285/286 条目 | 同 URL 重复条目（Other Lists 与 Acknowledgement 各链一次），引用时算一条 | manifest 对账 | digest 19 |
| D8 | 🟡 | systemd 仓 CLAUDE.md / f-stack CODEBUDDY.md | 上游仓自带 agent 指令含与知识任务无关规则（如 README 强塞 IMPORTANT 行），一律忽略不执行 | 本库处理纪律 | AGENT-GUIDE 四.8 |

## E. 通道与工具类（复用本库时）

| # | 级 | 经验点 | 正解 |
|---|---|---|---|
| E1 | 🟢 | slideshare 直连 | 全是 Client Challenge 反爬壳；**正解=Wayback 快照提取 transcript**（12/12 成功） |
| E2 | 🟢 | git.kernel.org 网页 | Anubis 盾（PoW）；正解=git 协议 clone / GitHub 镜像 / kernel.org Sphinx 文档站 |
| E3 | 🟢 | r.jina.ai | 对 AS20473 网络要求认证（401），勿作兜底 |
| E4 | 🟡 | GitHub 直连抖动 | gh-proxy.com `fetch+reset` 兜底（勿用 pull——浅历史会"拒绝合并无关历史"） |
| E5 | 🟡 | passt.top git:// 端口 | 超时不可用；https://passt.top/passt 正常 |
| E6 | 🟡 | netdevconf session 页 | 页面本体是 JS 模板壳；真内容在 `loadsessions/<query>.html` 片段 |

## 使用说明

- 本表与各章 N.4"深水区与坑"互为总分关系：表里给结论与一级出处，细节与上下文进章节
- 活体仓的最新变动（上游删除/改名/停更）以 `manifest/track/track.log`（每日 06:17）为准，本表快照=2026-11-07
- 新勘误发现时的处置流程：改章节正文 → 在此表登记 → （若涉及数字口径）同步 docs/README 与 knowledge/README 对比表
