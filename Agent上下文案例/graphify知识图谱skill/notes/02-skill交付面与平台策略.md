# 02 · Skill 交付面与平台策略：`/graphify` 怎么跑、20+ 平台怎么接

> 出处：上游 README（v8）Install / Make your assistant always use the graph / Team setup / Using the graph directly / Full command reference。

## 1. 交付形态总览

graphify 的交付是**三层叠加**，用户按需取用：

| 层 | 形态 | 命令 | 适合 |
|---|---|---|---|
| L1 skill | `/graphify .` 按需构建，产物三件套 | `/graphify .` | 单人探索（30 秒上手）|
| L2 常驻引导 | hook / 指令文件把 agent 的检索行为导向图 | `graphify <platform> install` | 每天在此仓库工作的开发者 |
| L3 服务化 | MCP stdio / HTTP，团队共享一个图 | `python -m graphify.serve ...` | 团队/CI |

产物三件套（`graphify-out/`）：

```
graph.html       # 浏览器交互图：点节点、过滤、搜索（>5000 节点建议 --no-viz）
GRAPH_REPORT.md  # god nodes / 意外连接 / why 注释 / 建议问题 / AMBIGUOUS 清单
graph.json       # 全图（上限 512 MiB，env 可调）——查询不再读源文件
```

## 2. 安装矩阵：20+ 平台，四种接线机制

`graphify install [--project] [--platform <p>]`：全局装到用户 profile；`--project` 装进仓库（如 `.claude/skills/graphify/SKILL.md` + `references/` sidecar，可 git 提交）。平台清单（节选）：Claude Code、Codex、**OpenCode**、Cursor、Gemini CLI、Copilot（CLI/VS Code）、Aider、Amp、Kiro、Devin、Antigravity、Kimi、Hermes、Trae(±CN)、Factory Droid、OpenClaw、Kilo、Pi、CodeBuddy、跨框架 `agents`（`~/.agents/skills/`，Anthropic Agent-Skills 规范）。

"让 assistant 总是用图"的四种机制（按平台能力降级）：

| 机制 | 平台 | 行为 |
|---|---|---|
| **PreToolUse hook** | Claude Code、Gemini CLI、CodeBuddy | 搜索类工具调用（及 Claude 的 Read/Glob 逐文件读）**之前**拦截，nudge 去 `graphify query` |
| **strict mode** | Claude Code（`--strict`）| **阻断会话首次裸读源码**并重定向到图，之后回退为 nudge（至多触发一次/会话，不会卡死）；运行时 `GRAPHIFY_HOOK_STRICT=1/0` 切换 |
| 指令文件 | Codex（AGENTS.md）、OpenCode、Cursor（`.cursor/rules/*.mdc` `alwaysApply:true`）| 常驻文字引导 query-first |
| 原生插件 | Kilo（`tool.execute.before` 插件）| 等价 hook |

两个值得记录的平台适配细节（适配层"诚实降级"的范本）：
- **Codex 的 hook 是故意的 no-op**：Codex Desktop 拒绝 `PreToolUse` 的 `additionalContext`，发 nudge 会弄坏 Bash 调用——于是 hook 照装但什么都不做，AGENTS.md 承担全部引导。**装了不等于用了**，注释写明。
- **并行提取按平台能力分化**：Claude Code/CodeBuddy/Factory Droid 用 Agent/Task 工具并行 subagent 提取；Codex 需手开 `multi_agent=true`；OpenClaw/Aider **顺序提取**（并行支持尚早）；Trae 有 Agent 工具但无 PreToolUse hook。

> 对本项目的意义：`graphify install --platform opencode` 写的正是 opencode 的 skill/指令位置——本仓库 `.opencode/` 体系可直接吃进这个案例的实操经验（skill 文件 + AGENTS.md 引导 + 可选 MCP 三件全在 opencode 支持面上）。

## 3. 团队工作流：图是共享工件，不是私人索引

1. 一人跑 `/graphify .` 并**提交 `graphify-out/`**（推荐 gitignore 仅排除 `cost.json`；`manifest.json` 已可移植——相对路径存储、加载时重锚定，提交它可免队友全量重建）。
2. `graphify hook install`：git post-commit 自动重建（**AST only，零 API 成本**）+ 设置 **git merge driver**——两人并行提交 `graph.json` 冲突时自动 union-merge，不留冲突标记。
3. docs/papers 变更后 `/graphify --update` 只刷新对应节点（语义缓存 `cache.py` 记住哪些文件已提取）。

与 codegraph 的"每开发者各自 auto-sync"对照：graphify 把**图当成交付物**（commit 进 repo），codegraph 把图当**本地派生物**（`.codegraph/` 不共享）。两种团队哲学：共享工件（一致但有人维护成本）vs 各自索引（零协调但可能漂移）。

## 4. 查询与服务面

```bash
# CLI 直查
graphify query "what connects auth to the database?"   # 自然语言→范围化子图
graphify path "UserService" "DatabasePool"             # 最短路
graphify explain "RateLimiter"                          # 节点全档案：源位置/社区/度/47 条连接逐条列出
graphify merge-graphs a.json b.json                     # 图合并

# MCP 服务（extra: pip install "graphifyy[mcp]"）
python -m graphify.serve graphify-out/graph.json                    # stdio（本地）
python -m graphify.serve ... --transport http --port 8080 \
       --host 0.0.0.0 --api-key "$SECRET" --stateless                # 团队/CI 共享
```

MCP 工具：`query_graph`、`get_node`、`get_neighbors`、`shortest_path`、`list_prs`、`get_pr_impact`、`triage_prs`。HTTP 面默认 `127.0.0.1` 回环；对外暴露必须 `--host 0.0.0.0` **与** `--api-key` 同设——与 dsh 的 DNS-rebinding 栅栏同一威胁模型的简化版（但没有 Host/Origin 校验，安全深度不如 dsh）。

多项目：`GRAPHIFY_MAX_CONTEXTS`（默认 8）限制单个 MCP server 保留的非默认项目图数。

## 5. 工作记忆闭环：save-result → reflect → LESSONS.md

graphify 不只建静态图，还有**会话经验回写**机制：

```bash
graphify save-result --question "..." --answer "..." --nodes Foo Bar --outcome useful|dead_end|corrected
graphify reflect   # 聚合 graphify-out/memory/ → reflections/LESSONS.md（按社区分组）
                   # 写 overlay .graphify_learning.json；节点打 preferred/tentative/contested 标签
                   # 之后 explain/query 输出会带 "Lesson:" 提示
```

`--outcome dead_end|corrected` 意味着**失败也会沉淀**（哪条路走过没用）。这与 [`Agent记忆系统案例/mem0开源记忆层`](../../../Agent记忆系统案例/mem0开源记忆层/) 的检索式记忆构成第三条路线：dsh 重放日志（不检索）、mem0 向量检索（语义）、graphify 图叠加（结构化经验贴在图节点上）——**记忆贴着图走，经验有坐标**。

## 6. PR 工作流与全局图

- `graphify prs`：PR 仪表盘（CI 状态/评审/worktree 映射）；`prs 42` 用图做影响面深挖；`--triage` 用配置的 backend 给评审队列排序；`--conflicts` 找**共享图社区的 PR**（合并顺序风险）——图分析直接进 CI/协作流。
- `graphify global add|remove|list`：跨项目的全局图（`~/.graphify/global-graph.json`），`graphify add <arxiv-url>` / `<youtube-url>` 把论文/视频转写后收编入图——个人知识管理的进料口。
- 导出面：`--obsidian`（Obsidian vault！）、`--wiki`（每社区一篇 md）、`--svg`、`--graphml`、`--neo4j-push`/`--falkordb-push`（外部图数据库）、`export callflow-html`（Mermaid 架构图，hook 后随 commit 自动再生）。

## 7. 隐私与日志的诚实账

- 代码/音视频：全本地（tree-sitter / faster-whisper）；docs/PDF/图片：出网到所配 backend。
- **无遥测、无使用追踪**（对比 codegraph 有匿名遥测但可关）。
- 查询日志：README 的 Privacy 节与 env 表存在**文档漂移**——Privacy 节说"每次 query/path/explain 记入 `~/.cache/graphify-queries.log`（JSON Lines），`GRAPHIFY_QUERY_LOG_DISABLE=1` 可退"；env 表却说默认**关**、`GRAPHIFY_QUERY_LOG_ENABLE=1` 才开（引用 PR #1797）。两处矛盾，真实默认需以代码为准——记录在案，作为"README 也会漂移"的实例（不影响结论：日志只在本地，两种描述下都不出网）。

→ 下一篇：[03-基准对比与领域定位](03-基准对比与领域定位.md)
