# CodeGraph 代码知识图谱 · 案例笔记

> 一句话定位：**预索引的代码知识图谱 + 代码变更自动同步——给 Claude Code / Codex / Cursor / OpenCode / Gemini / Antigravity / Kiro / Copilot 九类 agent 用的"本地代码智能"MCP 服务器。Rust 内核解析，SQLite 存储，100% 本地。**
>
> 上游：https://github.com/colbymchenry/codegraph （MIT，66.4k★，877 commits）
> 文档站：https://colbymchenry.github.io/codegraph/
> 本地验证（2026-08-14，npm registry 实测）：`@colbymchenry/codegraph` v1.5.0，首发 2026-01-18，最后发布 2026-07-21
>
> 本案例组织方式参照 [`Agent框架案例/deepseek-harness插件化框架`](../../Agent框架案例/deepseek-harness插件化框架/README.md) 的分层笔记约定；领域全景见上级 [`Agent上下文案例/README.md`](../README.md)。

## 为什么值得深读

1. **R3 路线（预构建图）的当前标杆**：Rust 内核 20 语言原生解析、每语言**字节级等价验收**（与参考引擎 byte-for-byte 一致才发布）、容器感知的自适应并行——Linux 内核（70k 文件、2M 符号、6.4M 关系）在 2核/6GB VPS 上 <12 分钟索引完。
2. **Agent-first 工具设计**：MCP 面默认**只暴露一个工具** `codegraph_explore`（实测一个强工具比一堆窄工具更能引导 agent）；其余 7 个工具按需开启。
3. **新鲜度三层机制**：watcher（原生 OS 事件 + 2s debounce）→ 过期文件⚠️横幅（点名让 agent 直接 Read）→ 连接时对账——把"索引会说谎（过期）"这个 R3 路线的死穴做成了**显式信号**而非沉默错误。
4. **基准即反欺骗教材**：双臂封锁 CLI（0/28 污染）、诚实披露 residual context +80%——见 [笔记 02](notes/02-基准方法论与诚实披露.md)，与 [`欺骗动力学-AI纪实验包.md`](../../欺骗动力学-AI纪实验包.md) 直接互文。

## 阅读顺序

| # | 笔记 | 回答的问题 |
|---|---|---|
| 1 | [01-架构Rust内核与AutoSync](notes/01-架构Rust内核与AutoSync.md) | 怎么建图、怎么存、怎么秒级保鲜、agent 怎么接 |
| 2 | [02-基准方法论与诚实披露](notes/02-基准方法论与诚实披露.md) | 7 仓库基准怎么测的、为什么可信、诚实在哪里 |
| 3 | [03-领域对比与选型](notes/03-领域对比与选型.md) | vs Serena / Greptile / Aider / Cursor 六路线，什么时候选谁 |

## 审计总命令

```bash
# 证据 A: npm 包真实存在且为 MIT（2026-08-14 实测输出）
$ npm view @colbymchenry/codegraph name version license
name = '@colbymchenry/codegraph'
version = '1.5.0'
license = 'MIT'

# 证据 B: 首发时间（领域时间线锚点）
$ npm view @colbymchenry/codegraph time.created
2026-01-18T22:53:32.067Z

# 证据 C: 仓库规模（上游 GitHub 页面，2026-08-14）
#   66.4k stars / 4.2k forks / 877 commits / MIT
#   目录含 codegraph-kernel/（Rust 内核）、src/mcp/（MCP server）、
#   telemetry-worker/（遥测 ingest 开源）、docs/benchmarks/
```

> 注：本案例为**文档级审计**（README/文档站/npm 元数据逐条核对），未做源码级 clone——与 dsh 案例的"行号可验"深度不同，属于轻量案例。引用均标明出处（README 章节 / npm 实测）。

## 项目内交叉引用

- 领域全景（六路线 + 全项目速查）：[`../README.md`](../README.md)
- ContextEngineering 理论接口：[`工程化手册库/ContextEngineering手册`](../../工程化手册库/ContextEngineering手册/README.md) §SPACC-S
- 反欺骗切面：[`欺骗动力学-AI纪实验包.md`](../../欺骗动力学-AI纪实验包.md) 实验 5（dsh 是 harness 层结构对齐，codegraph 是工具层证据诚实——两条正交路线）
- harness 层如何接 MCP 工具：dsh 案例 [`02-capability-seams`](../../Agent框架案例/deepseek-harness插件化框架/notes/02-capability-seams/01-接缝模式与能力矩阵.md)（外部工具强制 `mcp__<server>__<name>` 命名空间）
