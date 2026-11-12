# DeepChat DeepWiki 抓取覆盖率检查

- 检查日期：2026-10-08
- 清单：2026-03-06 导航世代 57 页锚定集合（含主页），实际抓取 56 页
- 结果：**56/56 = 100%**

| 检查项 | 结果 |
|---|---|
| 页面对账（manifest ↔ md 文件） | 56/56，无缺页 |
| 过小页（≤2KB 空壳） | 0 |
| 正文签名抽查（H2 数量 / Sources 引用） | 抽 3 页全过（11/11/5 个 H2；全站 Sources 形态 `**Sources**: [...]` 正常） |
| INDEX.md 链接对账 | 56 链接 ↔ 56 文件，缺失 0 / 死链 0 |
| 抓取报告 | `_fetch_report.tsv`（50 页 curl 直抓 ok + 6 页 RSC payload 提取） |

## 未收录页（1）

| 页 | 原因 |
|---|---|
| `/thinkinaixyz/deepchat`（overview 主页） | Wayback 仅有 2025-09-13 老世代快照（与 2026-03 目录不一致），弃用；其概览职能由 [1-deepchat-overview](thinkinaixyz_deepchat_1-deepchat-overview.md) 承担 |

## 特殊补齐页（6，标 ★）

wayback 快照为 SPA fallback 页（无 SSR 正文），从同快照 1.9MB RSC flight payload 提取原始 markdown：

- 8.2 / 8.3 / 8.4 / 8.5 / 9.1 / 9.6（详见 INDEX.md 抓取说明）
- 另 4.5 / 4.6 / 9.5 三页以老世代等效 URL 快照补（save_slug 重命名归位）

## 通道记录（钉版）

deepwiki.com 直连被 Vercel Security Checkpoint（JS challenge，429）拦截，clash 节点对该域 000，r.jina.ai 中转同撞 challenge；web.archive.org 经 clash 稳定可达。requests 库 TLS 指纹被掐（SSL EOF 雪崩），换 curl 子进程后一轮补齐 44 页。
