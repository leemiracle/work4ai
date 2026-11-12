# 讲透 A2A

> a2aproject/A2A —— Agent2Agent 协议（AAIF/Linux Foundation 托管）：agent 间互操作开放标准（AgentCard 发现 / JSON-RPC 消息 / 任务生命周期 / 流式与推送）。
> 本地仓：/usr-data/data2/repos/aaif-projects/repos/A2A（HEAD 98279d62，2026-10-21 聚合）

## 状态（2026-10-24 全链完成 ✅）

| 步骤 | 状态 | 产物 |
|---|---|---|
| DeepWiki 全量 | ✅ | [deepwiki/](deepwiki)（**36 页 100%**，全文 368K 字符，mcp.deepwiki.com 直连，2026-10-21） |
| understand 中文图谱 | ✅ | 仓内 `.understand-anything/knowledge-graph.json`（**183 节点/352 边/8 层/8 步 tour，validator 0 issues，fingerprints 113 文件@98279d62**；spec/docs 型仓——schema:specification/a2a.proto 为全图锚点（46 message+11 endpoint 子节点），2026-10-24） |
| onboarding | ✅ | [onboarding/ONBOARDING.md](onboarding/ONBOARDING.md)（3018 汉字/84 锚/8 节，docs 仓口径） |
| explain 系列 | ✅ | [explain/](explain) 6 篇（合计 15,530 汉字/103,769 非空白字符，每篇 36-163 锚全源码核验，2026-10-24） |

字数口径（SB3 轮钉版双轨）：汉字数=正则计数；非空白字符=`tr -d '[:space:]'`。

## explain 6 篇索引（docs 仓按知识密度 6 篇）

| # | 篇 | 主角 | 汉字 |
|---|---|---|---|
| 01 | [specification.md 精读](explain/01-specification-deepread.md) | v1.0 叙事主线/16 组章节↔proto 双锚表/七步交互 | 2918 |
| 02 | [a2a.proto 精读](explain/02-proto-schema.md) | 44 message 族谱/tenant=4 错位 git 考古/三层 lint | 2373 |
| 03 | [教程线与 SDK](explain/03-tutorials-sdk-blog.md) | 8 步 Quickstart 递进/学习漏斗/教程安装口径矛盾 | 2290 |
| 04 | [文档站构建链](explain/04-docs-site-build.md) | mkdocs 宏系统/八脚本流水/llms 三件套 | 2966 |
| 05 | [治理与 CI](explain/05-governance-ci.md) | TSC/投票/11 workflow/lint 三层/PR 门禁七步 | 2834 |
| 06 | [topics 概念群](explain/06-topics-deepread.md) | key-concepts 枢纽/扩展三角互链/五叶子 | 2149 |

## 实证勘误（批分析+explain 系列，10 条钉版）

1. **tenant 字段号 4 错位=同日双提交竞态化石**（#1486/#1494 diff 零命中，git 考古与图谱互证）；Next ID: 20 为忘改残留（现最大字段号 14）（02）
2. buf.gen.yaml 实为 4 语言 7 远端插件；"第五语言" C# 仅命名预留，生成配置不在本仓；proto:385 孤儿 `protolint:enable`（02）
3. **dependabot 策略与 agentgateway 相反**——无 limit: 0，实为三路 monthly 分组更新（groups patterns '*' 单 PR 合并）；策略不可跨仓外推（05）
4. `.github/conventional-commit-lint.yaml` 全仓零引用=死配置块（真实规则内联在 conventional-commits.yml）；linters 实为 5 件非 6 件（05）
5. 教程第 2 步 `pip install -r` 与第 7 步 `pip install -e .[dev]` 安装口径自相矛盾；`build_docs.ps1` 不存在（README Windows 分支失效）（03）
6. `sdk/python/api/` 被 .gitignore:214 排除、源仓缺失；blog 实为 3 篇非 4（03）
7. **mkdocs nav 实为 32 叶条目非 26 页**（29 本地 md+2 外链+1 生成 html）；llms 三件套=两份手写源+一份构建产物（04）
8. topics 实名勘误：无 agent-user-interaction/multi-agent-systems/security 独立页；extensions.md 299 行非 255（06）
9. **push-notifications.md 已并入 streaming-and-async**（mkdocs.yml:181 重定向表化石）——解释该页双段结构（06）
10. 构建产物五处 gitignore 排除钉版（docs/spec/、json/a2a.json、llms-full.txt 等）；宏三处直读 proto 是规范单源机制的机械证据（specification.md:776/:897 宏占位符）（04/01）

## DeepWiki 章节速览（7 章）

1 Overview · 2 Protocol Specification · 3 SDK & Implementation Guide · 4 Development Infrastructure · 5 Community & Governance · 6 Technical Reference · 7 Glossary

入口：[deepwiki/INDEX.md](deepwiki/INDEX.md) · 覆盖率：[deepwiki/_coverage-check.md](deepwiki/_coverage-check.md)
