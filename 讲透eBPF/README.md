# 讲透 eBPF

> 基于 github.com/qmonnet/awesome-ebpf 清单（@dc0c2065，2026-09-14）**288 条资源全量消化**产出的 eBPF 知识库 · 语料快照 2026-11-06/07 · 归档 2026-11-07
> 真源（活体，含 2.7G 克隆仓与每日跟踪）：`/usr-data/data2/kylin/network/awesome-ebpf/`——本目录是知识产物快照，引用数字以真源为准

## 产物清单

| 产物 | 规模 | 说明 |
|---|---|---|
| docs/ 16 章 | 29.3 万字符 | 每章 8 节（导读/直觉/原理/实践/深水区坑/章间关系/语料索引/agent 用法），断言带语料锚 |
| docs/ 配套三件套 | GLOSSARY 129 词条 / EXERCISES 64 题 / CHEATSHEET 8 块 | 自学闭环：查词/做题（答案要点文末）/命令速查 |
| docs/README.md | — | 章节地图 + 双学习路径（2 周快速 / 3-4 月系统）+ 三件套用法 |
| digests/ 21 批 | 288/288 条对账零缺失 | 逐条消化：是什么/核心/坑/学习者价值/agent 用法+grep 词 |
| ERRATA.md | 33 条勘误 | 三级分级（🔴必改/🟡带语境/🟢勿引用），**引用数字前必查** |
| AGENT-GUIDE.md | — | AI agent 检索地图：问题路由 → 章节 → digest → 原始语料三级动线 |
| INVENTORY.md | 320 行 | 全 288 条清单+盘上状态+每仓 commit |
| SUMMARY.md | — | 人用总览（知识主地图+勘误表） |
| PROGRESS.md | — | 全程台账（五阶段+四轮追加，可审计） |

## 语料基座（在真源，未随档）

- 83 浅克隆仓（2.7G，82 活档 + ingero/synapse 上游已删）
- web/md 190 篇文章全有正文（slideshare 12 条经 Wayback transcript 救回）
- web/pdf-txt 20 份 PDF 全文
- 活体仓跟踪：14+3 仓每日 06:17 cron（manifest/track/track.log）

## 核心勘误速览（完整版见 ERRATA.md）

- BPF 引入 Linux = **1997 年 2.1.75**（作者口径，非流传的 v2.5）
- Suricata **39Gbps 出自 NFQ mark bypass**，不是 XDP 通道
- iptables 基线八级阶梯 **1.8~4.8Mpps**（"4.5Mpps" 流行说法无出处）
- XDP 24Mpps（CoNEXT'18）与 10.1Mpps（Cloudflare 4.14）是不同代际/硬件语境，不可直比

## 推荐阅读顺序

1. [docs/README.md](docs/README.md)——章节地图，选学习路径
2. 快速通道：第 1 章 → 第 7 章实践层跑通 minimal → 第 2/3 章机制 → 第 8 章 CO-RE → 第 11 章动手
3. 系统通道（3-4 月）：机制（1-6）→ 工程（7-8）→ 应用（9-13 选主线）→ 生态（14-16），每章配 EXERCISES 4 题
4. AI agent：直接读 [AGENT-GUIDE.md](AGENT-GUIDE.md) 按问题路由查

## 姊妹篇（同工作区）

`/usr-data/data2/kylin/network/knowledge/`：f-stack（DPDK+FreeBSD 全旁路）/ passt（无特权协议翻译器）/ systemd-network（networkd 状态机+38 种 netdev）三仓深度消化 + 四路线（eBPF/F-Stack/passt/networkd）横向对比 README
- systemd 另档：../讲透systemd/（DeepWiki 43 页 TRUE_100 + 网络线深度消化）
- f-stack/passt 另档：../讲透F-Stack/、../讲透passt/（两仓无 DeepWiki 收录，消化文档即唯一结构化知识源；passt 另有 understand 图谱 989n/16 层+ONBOARDING+explain 12 篇）
