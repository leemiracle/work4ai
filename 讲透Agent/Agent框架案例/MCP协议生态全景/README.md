# MCP 协议生态全景 · 案例笔记

> 一句话定位：**github.com/topics/mcp（64,438 仓）+ 官方规范 2026-07-28 版 + modelcontextprotocol org 的系统性知识集成——MCP 已是 AI 工具的事实连接标准（用例库 279 仓 22% 提及率），本案例是它的生态观测锚点与协议演进档案。**
>
> 数据源：[topics/mcp](https://github.com/topics/mcp)（两页 star 排序快照）· [awesome-mcp-servers](https://github.com/punkpeye/awesome-mcp-servers)（92.5k★，全文本地分析）· [modelcontextprotocol.io](https://modelcontextprotocol.io) 官方 changelog（一手）
> 快照：2026-08-19（star/仓数会漂移，所有数字当日实测——项目铁律）
>
> 与姊妹资产分工：[`工程化手册库/MCP工程手册/`](../../../工程化手册库/MCP工程手册/README.md) 管"**怎么写 server**"（协议教学+FastMCP 实操，2026-08 版）；本案例管"**生态什么样、协议往哪去、知识在哪找**"（观测+演进+互链）。**总纲**：[`../Topics全链路全景/`](../Topics全链路全景/README.md)（十层 topics 索引体系，本目录是其 L3 层深潜样本）。

## 为什么值得读

1. **2026-07-28 规范是分水岭**：MCP 删掉 initialize 握手/协议级 session/ping，弃用 Sampling/Roots/Logging，全面无状态化——手头 2025 版教程（含本项目手册）已部分过时，这是中文圈少有的一手变更解读。
2. **双口径生态统计**：topic 全量（64k 仓，Python 34%）与 awesome 收录（3,371 条，TS 54%）交叉对账——单一口径都会骗人。
3. **官方治理转向档案**：servers 仓瘦身→Registry 诞生→SDK v2 重写→GitHub 平台级集成（github.com/mcp），一套"协议官方如何退守核心"的治理样本。
4. **项目内 MCP 知识总枢纽**：散落 10+ 处的手册/用例库/案例卡由此织网（04 篇）。

## 阅读顺序

| # | 笔记 | 回答的问题 |
|---|---|---|
| 1 | [01-生态统计与赛道地图](notes/01-生态统计与赛道地图.md) | 64k 仓什么结构？top41 是谁？六赛道怎么分？x402 微支付是什么趋势 |
| 2 | [02-协议演进2026-07-28](notes/02-协议演进2026-07-28.md) | 规范改了什么？为什么删握手/弃用 Sampling？MRTR 是什么 |
| 3 | [03-官方仓与SDK格局](notes/03-官方仓与SDK格局.md) | 官方 org 六支柱？SDK v2 怎么选？FastMCP 与官方什么关系 |
| 4 | [04-项目内MCP知识互链网](notes/04-项目内MCP知识互链网.md) | 本项目哪些单元藏着 MCP 知识？按听说读写四档怎么学 |

## 审计总命令

```bash
$ ls 讲透Agent/Agent框架案例/MCP协议生态全景/notes/   # 4 篇笔记
$ wc -l 讲透Agent/Agent框架案例/MCP协议生态全景/notes/*.md
# 生态统计可复现：notes/01 §6 有完整 grep 命令（对 awesome README 本地文件）
# 协议变更可核实：https://modelcontextprotocol.io/specification/2026-07-28/changelog
```

## 项目内交叉引用

- 实操教程（怎么写 server）：[`工程化手册库/MCP工程手册/`](../../../工程化手册库/MCP工程手册/README.md)——本案例是其"生态与演进"补充层
- harness 视角的 MCP 接缝：[`deepseek-harness插件化框架/notes/02-capability-seams/02-插件机制全景.md`](../deepseek-harness插件化框架/notes/02-capability-seams/02-插件机制全景.md)（`mcp__<server>__<tool>` 命名空间）
- MCP 服务器案例（工具面设计）：[`Agent上下文案例/codegraph代码知识图谱/`](../../Agent上下文案例/codegraph代码知识图谱/README.md)（默认单工具）· [`graphify知识图谱skill/`](../../Agent上下文案例/graphify知识图谱skill/README.md)（skill vs MCP 对照）
- 记忆层 MCP 样板：[`Agent记忆系统案例/mem0开源记忆层/notes/08-integrations/01-mem0-plugin.md`](../../Agent记忆系统案例/mem0开源记忆层/notes/08-integrations/01-mem0-plugin.md)
- Skills vs MCP 路线之争：[`前沿与媒体/103-AgentSkills开放标准深度解析.md`](../../../前沿与媒体/103-AgentSkills开放标准深度解析.md)——姊妹案例 [`../Skills生态全景/`](../Skills生态全景/README.md)（topics/skills 11,492 仓，2026-08-19 同日快照，MCP=插座 vs Skills=操作手册的完整对照）
- 横向谱系（279 仓坐标系）：[`实例/用例库/README.md`](../../../实例/用例库/README.md) 之"MCP 吞噬一切接口层"
- 深潜方法论母本：[`透视GitHub-AI高星仓库全景.md`](../../../透视GitHub-AI高星仓库全景.md)
