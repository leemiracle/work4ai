# 讲透 modelcontextprotocol

> modelcontextprotocol/modelcontextprotocol —— MCP（Model Context Protocol）协议规范+SDK 仓（Anthropic 发起，AAIF 托管）：JSON-RPC 消息/传输层/连接生命周期/能力协商的权威源。
> 本地仓：/usr-data/data2/repos/aaif-projects/repos/modelcontextprotocol（HEAD 80041ab0，2026-10-21 聚合）

## 状态（2026-11-01 全链完成 ✅）

| 步骤 | 状态 | 产物 |
|---|---|---|
| DeepWiki 全量 | ✅ | [deepwiki/](deepwiki)（**46 页 100%**，全文 466K 字符，mcp.deepwiki.com 直连，2026-10-21） |
| understand 中文图谱 | ✅ | 仓内 `.understand-anything/knowledge-graph.json`（**633 节点/1800 边/14 层/15 步 tour，validator 0 issues 0 warnings，fingerprints 573 文件@80041ab0**；79 批——schema examples 夹具与 seps 双树精简镜像已裁，2026-10-26~27。**勘误：10-22 曾改判"不适用"，10-26 复议重启**——SEP 工具链（sep-automation 30 文件）与构建生成链是真代码，图谱价值成立） |
| onboarding | ✅ | [onboarding/ONBOARDING.md](onboarding/ONBOARDING.md)（4110 汉字/15,817 非空白字符/8 节） |
| explain 系列 | ✅ | [explain/](explain) 12 篇（主线：01 schema 契约真源 draft 终态 · 02 规范总纲 · 03 六代演进 · 04 Skills 扩展 · 05 SEP processor · 06 github client · 07 generate-schemas · 08 render-seps · 09 migrate_seps · 10 version-warning · 11 SEP 状态机三件套 · 12 validate-examples；11/12 篇 2026-11-01 补齐，主会话独立抽验 11 锚全中） |

## 源码级勘误钉版（explain 系列实证，2026-10-27/11-01）

1. **schema.ts 不用 zod**——纯 TS interface + typescript-json-schema 编译，`schema/<v>/schema.mdx` 是 typedoc 模板非产物。
2. **`AUTO_TRANSITION_RULES`（rules.ts L123）与 `getStalenessRule`（L166）是死导出**——全仓零消费；真实自动迁移硬编码在 processor.ts L135+，staleness 查表 config.ts L63-65 用裸 `.find` 绕过。
3. **"CI 门禁"不成立**——validate-examples.ts 在全部 GitHub workflows 零调用（main.yml 仅 ts/json/md 三步 check），门禁只活在 `npm run check` 本地荣誉制路径。
4. **examples 只有两版本**——仅 2026-07-28 与 draft 有 examples 目录（129 文件字节级一致镜像），老四版本无目录走静默通过（L54-55 catch return）。
5. **SEP 状态机输入是 GitHub label/事件/评论非 markdown 正文**——seps/*.md 的 Status 行是平行的人类维护表示（render-seps.ts 消费），词汇表是六态超集。
6. analyzer.ts L180 JSDoc 与 L204 实现矛盾（proposal 态责任人）；rules.ts L67 注释 pingTarget 三值 vs L74 类型两值。

## DeepWiki 章节速览（10 章）

1 Overview · 2 Protocol Specification · 3 Authorization and Security · 4 Client Ecosystem · 5 Server Development · 6 SDK Ecosystem · 7 Development Guide · 8 Governance and Community · 9 Tools and Debugging · 10 Glossary

入口：[deepwiki/INDEX.md](deepwiki/INDEX.md) · 覆盖率：[deepwiki/_coverage-check.md](deepwiki/_coverage-check.md)
