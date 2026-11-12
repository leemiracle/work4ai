# 讲透 F-Stack

> f-stack/f-stack @52514377b（2026-10-28，每日跟踪中）· 产物 2026-11-07
> 真源：/usr-data/data2/kylin/network/f-stack/（活体克隆）· DeepWiki 未收录（钉版），**本消化文档是唯一结构化知识源**（TIRx 先例同型）

## 产物

| 产物 | 规模 | 说明 |
|---|---|---|
| knowledge-f-stack.md | 12.9k 字符 | 8 节深剖：架构（FreeBSD 15.0 全栈移植+DPDK 轮询+每核一进程）/ff_* API 与数据面逐跳/性能实测（25×/P99 10µs/千万并发，含口径警示）/坑 7 条/学习者路径/agent 用法 |

## 一句话定位

kernel bypass 流派"最重武装"：把 FreeBSD 全栈连根搬进用户态换无锁数据面，腾讯 DNSPod 生产背书；代价是独占网卡与 CPU 核——"为 10 倍性能吃下 10 倍复杂度"的场景武器。

## 关联

- 四路线横向对比（eBPF/F-Stack/passt/networkd）：../讲透eBPF/姊妹篇四路线对比-README.md
- 仓内自带 docs/ 三层架构知识库（AI 辅助生成）；仓内 CODEBUDDY.md 等 agent 指令文件按任务纪律一律忽略

## understand 图谱（2026-11-08 新增）

| 产物 | 规模 | 状态 |
|---|---|---|
| understand/knowledge-graph.json | 1616 节点 / 2669 边 / 14 层 / 16 步 tour | ✅ validator 双验 0 issues |
| understand/ONBOARDING.md | 8925 字 8 节 | ✅ 锚 13/13 |
| understand/explain/ | 12 篇 38392 字符 | ✅ 锚两轮核验 0 坏 |

真源：仓内 /usr-data/data2/kylin/network/f-stack/.understand-anything/（fingerprints@52514377；vendored dpdk/freebsd/app/tools 已裁，口径见其 README）
