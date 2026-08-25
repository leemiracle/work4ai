# omarchy-深读 —— DeepWiki 全量归档 + quattro 文档产出的知识模块

> **触发**：把 DeepWiki（https://deepwiki.com/basecamp/omarchy）39 子页全量蒸馏，与本地分叉 `/data/usershare/linux-src/omarchy-quattro`（v4.0.0.alpha）逐条对照，补齐其 `docs/` 主题空缺——"AI coding agent 的一等公民桌面"的完整设计在此归档。
> **管线**：DeepWiki MCP（`read_wiki_structure` + `read_wiki_contents`，一次返回全 wiki 含 mermaid）→ 全文归档三件套 → wiki 断言逐条对 quattro 代码核实 → 新增 10 页 repo docs + 深读卡。同 `讲透Agent/Agent框架案例/DeepWiki深读卡/` 管线，但 omarchy 非 agent 仓，独立成模块。
> **执行日**：2026-08-25（wiki 索引 2026-08-18 @ fa955b）

## 目录

| 文件 | 内容 |
|---|---|
| [deepwiki/full.md](deepwiki/full.md) | 39 页全文（365KB，含 83 mermaid + 87 表格，页头带编号） |
| [deepwiki/structure.txt](deepwiki/structure.txt) | 官方页面树（read_wiki_structure 原样） |
| [deepwiki/skeleton.md](deepwiki/skeleton.md) | 导航骨架（每页行偏移/大小/mermaid/表格/源文件数） |
| [omarchy-深读卡.md](omarchy-深读卡.md) | 深读卡：组件栈/6 核心机制/讲透系列对位/入口树/子页地图 |
| [quattro文档映射-2026-08-25.md](quattro文档映射-2026-08-25.md) | 39 页 → quattro docs 覆盖矩阵 + wiki 失实处清单 |

## 与其他模块的关系

- **讲透Agent**：10.3 AI Agent Integration 是"agent 运行环境"维度的活教材（agent 进 OS：选择/安装/无值守/用量/崩溃诊断五件事全系统命令化）——深读卡 §三 有逐条对位。
- **工程化手册库**：bash 元数据路由、快照优先 update 管线、Lua require 遮蔽分层是三个可迁移的系统设计范式（深读卡 §二）。
- **omarchy-quattro 仓库**：本次向其 `docs/` 新增 10 页（ai-agents / boot-snapshots / capture / glossary / hardware / hyprland / package-sources / screensaver / session-services / shell-environment），全部断言本地核实；映射与失实处见 quattro文档映射。

## 抓取方法备忘（复用）

```bash
# MCP 免 session，直接 POST（SSE 返回）
curl -s -X POST https://mcp.deepwiki.com/mcp \
  -H "Content-Type: application/json" -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"read_wiki_contents","arguments":{"repoName":"basecamp/omarchy"}}}'
# 解码：SSE data: 行 → json → result.content[].text 拼接即全 wiki markdown
```

坑位：① `read_wiki_contents` 返回不带页码编号（页头 `# Page: X`），编号要从 `read_wiki_structure` 对回；② deepwiki 各子页刷新时间不一，可能混入旧版本残留（本次 3.2 Waybar/3.3 Walker 即 v3 残留），断言必须对本地代码核实；③ 单页 webfetch 会截断长页，MCP 是全量唯一可靠通道。
