# 讲透REA / DeepWiki 抓取

> repo: [morluto/rea](https://github.com/morluto/rea) — REA "Reverse Engineer Anything"
>（终端/agent 逆向工程 MCP server + CLI：二进制 / JS·Electron / .NET / 网站分析）

- **通道**：mcp.deepwiki.com 官方 API（deepwiki.com 网页端被 Vercel Security
  Checkpoint 拦、Wayback 零快照、zread 429——MCP 端点直连可用，钉版见
  pipeline-bin README 坑 #17）
- **抓取日期**：2026-10-16 · **覆盖**：47/47 页 100%（10 章 + 37 子页，全文 610,319 字符）
- **对账**：`_coverage-check.md` · 结构树：`INDEX.md` · 全文 raw：`wiki_full.md`
- **历史**：v6.1.0 快照（2026-10-09，43 页）见 `../deepwiki-v6.1-archive/`；
  本次重抓对应仓内 v6.5.0（commit `1bd5c5c8`），上游新增 4 页与仓内大版本对齐

## 章节速览

| 章 | 内容 |
|---|---|
| 1 | Overview / Getting Started / Configuration / Setup·Doctor·Uninstall 内部机制 |
| 2 | Architecture（入口分派 / Domain 层 / Contracts+Tool Catalog / Application 层 / MCP Server 层） |
| 3 | Tool & CLI 参考（官方代理工具 / 增强工作流 / Session·Evidence / CLI 命令面） |
| 4 | 分析 Provider（Hopper / Ghidra / Apple·macOS 原生 / .NET / Android·Firmware·IDA / **4.6 调试器与动态插桩** / **4.7 新增 provider：kuna·jeb·wasm·evm·flutter·go·rust**） |
| 5 | Artifacts 与包（读取器 / 清点与提取 / 二进制目标解析） |
| 6 | Web·JS·运行时观测（CDP 浏览器观测 / Playwright·Electron 场景捕获 / JS 静态语义分析 / 应用工作流与版本对比 / **6.5 Web 网络捕获与脚本导出**） |
| 7 | Evidence·调查·重建（证据模型与账本 / 重建验证与义务 / 进程捕获） |
| 8 | 测试与验证（单元·边界·组合测试 / Conformance 夹具与信任门 / 真实 Provider 与打包验证 / **8.4 分析效率实验与评估**） |
| 9 | CI/CD、发布与网站 |
| 10 | Glossary |

每页头部 `<details>` 附 DeepWiki 生成时引用的源文件清单，可作后续
understand 图谱 / onboarding 的交叉对账素材。

## 与仓内 v6.5.0 的对齐提示

DeepWiki 上游快照与仓内 HEAD（v6.5.0）基本同步，但注意两点：

1. 上游 wiki 未覆盖 `analysisView` 统一投影层（src/domain/analysisView/ 31 文件）
   与 evidenceEnvelope 废除（v6.2 breaking，见 docs/migration-6.2.md）等细节，
   以仓内源码与 ONBOARDING/explain 为准；
2. 新根目录（licenses/、.agents/skills/、experiments/、stryker 突变测试配置）
   在 wiki 中仅零星提及，详见 `../README.md` 的 v6.5 增量说明。
