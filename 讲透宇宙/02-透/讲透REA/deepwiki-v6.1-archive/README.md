# 讲透REA / DeepWiki 抓取

> repo: [morluto/rea](https://github.com/morluto/rea) — REA "Reverse Engineer Anything"
>（终端/agent 逆向工程 MCP server + CLI：二进制 / JS·Electron / .NET / 网站分析）

- **通道**：mcp.deepwiki.com 官方 API（deepwiki.com 网页端被 Vercel Security
  Checkpoint 拦、Wayback 零快照、zread 429——MCP 端点直连可用，钉版见
  pipeline-bin README 坑 #17）
- **抓取日期**：2026-10-09 · **覆盖**：43/43 页 100%（10 章 + 33 子页，全文 691,418 字符）
- **对账**：`_coverage-check.md` · 结构树：`INDEX.md` · 全文 raw：`wiki_full.md`

## 章节速览

| 章 | 内容 |
|---|---|
| 1 | Overview / Getting Started / Configuration / Setup·Doctor·Uninstall 内部机制 |
| 2 | Architecture（入口分派 / Domain 层 / Contracts+Tool Catalog / Application 层 / MCP Server 层） |
| 3 | Tool & CLI 参考（官方代理工具 / 增强工作流 / Session·Evidence / CLI 命令面） |
| 4 | 分析 Provider（Hopper / Ghidra / Apple·macOS 原生 / .NET / Android·Firmware·IDA） |
| 5 | Artifacts 与包（读取器 / 清点与提取 / 二进制目标解析） |
| 6 | Web·JS·运行时观测（CDP 浏览器观测 / Playwright·Electron 场景捕获 / JS 静态语义分析 / 应用工作流与版本对比） |
| 7 | Evidence·调查·重建（证据模型与账本 / 重建验证与义务 / 进程捕获） |
| 8 | 测试与验证（单元·边界·组合测试 / Conformance 夹具与信任门 / 真实 Provider 与打包验证） |
| 9 | CI/CD、发布与网站 |
| 10 | Glossary |

每页头部 `<details>` 附 DeepWiki 生成时引用的源文件清单，可作后续
understand 图谱 / onboarding 的交叉对账素材。

## 下一步（三步流水线剩余）

1. understand 中文图谱（2246 文件 → 批分析 → layers/tour → knowledge-graph.json）
2. onboarding（ONBOARDING.md 4000-6000 字 8 节）
3. explain 系列精讲（tour 关键节点 12 篇左右）
