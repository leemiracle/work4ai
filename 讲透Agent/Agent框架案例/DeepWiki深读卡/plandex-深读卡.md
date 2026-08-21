# plandex 深读卡 —— 把"git 分支/沙盒/diff 审查"做成 AI 编码引擎第一公民的终端自托管系统

> **定位**：Plandex 是"版本控制优先"的 AI 编码引擎：终端 CLI/REPL + Go 自托管服务器，所有 AI 改动先写入独立 Git 沙盒（plan 内建 branch），经 `tell → build → diff → apply` 审查后才落盘项目文件。核心卖点是大型任务的多文件可靠性——2M token 直连上下文、tree-sitter 项目地图（可索引 20M+ token 仓库）、structured edits + 语法验证 + 自动修复循环，以及 none→full 五档自治级别。

> **本地**：`repos/plandex`（plandex-ai/plandex）｜**深读**：deepwiki 33 子页归档 `deepwiki/plandex/full.md`（2026-08-21）

## 一、组件栈（DeepWiki 蒸馏）

| 层 | 职责 | 关键实体 |
|---|---|---|
| Client（`app/cli`，Go） | 终端交互：命令、REPL、流式 UI | `plandex`/`pdx`、tell/chat 模式、Stream UI（Cobra） |
| Server（`app/server`，Go） | HTTP API + Plan 执行引擎 + 构建/验证 | gorilla/mux handler、ActivePlan、tell_*/build_* 状态机 |
| Shared（`app/shared`） | 跨端类型契约与工具 | API 类型、`PlanFileResult`、token 工具 |
| AI Providers | 多厂商模型接入 | OpenAI/Anthropic/Google/OpenRouter/Ollama |
| Storage | 混合存储：结构化数据 + 文件系统 Git 沙盒 | PostgreSQL（plans/contexts/users/repo_locks）、每 plan 一个 Git repo |
| 语法层 | tree-sitter 解析/验证/项目地图 | `syntax.ApplyChanges()`、`validateSyntax()`、file map |

## 二、核心机制

1. **Plan/Branch 版本模型**（来源：Introduction、Core Concepts）：plan 是工作单元（会话+上下文+pending changes 三合一），内建 Git 式 branch——每个 branch 拥有独立会话历史、独立 pending 变更、独立上下文状态；`checkout` 切换/创建、`rewind` 回滚到任意 SHA、`log` 查历史。沙盒与项目文件物理隔离，`apply` 前零污染。
2. **File Build Pipeline（多级兜底的改动管线）**（来源：File Modification Pipeline，`app/server/model/plan/build_*.go`）：AI 输出 → structured edits（`buildStructuredEdits`，带行号的 Old/New 替换）→ tree-sitter `validateSyntax` → 失败则进 validate-and-fix 循环（最多 3 次，让模型以 `<PlandexCorrect/>`/`<PlandexReplacements>` XML 自检修复）→ 仍失败降级 whole-file fallback → `GetDiffReplacements` 生成 `PlanFileResult` → `GitAddAndCommit` 提交进沙盒。全程指数退避重试 + 换更强模型。
3. **DB 锁 + 心跳的仓库并发控制**（来源：Repository Locking and Git Integration，`app/server/db/locks.go`）：所有 Git 操作走 `ExecRepoOperation` 包装——PostgreSQL 行锁表 `repo_locks`（read 锁同 branch 可共存、write 锁排他），持锁 goroutine 每 3s 更新 `last_heartbeat_at`，60s 超时自动判死锁回收；Git 层再叠 `index.lock` 清理 + 5 次指数退避。多用户/多 plan 并发安全全靠这层。
4. **角色化 Model Packs + 五档自治**（来源：Core Concepts）：Planner/Architect/Coder/Builder/Validator/Namer 六角色按需绑定不同模型（`--daily/--strong/--cheap/--oss` 打包）；自治级别 none→basic→plus→semi→full 控制 auto-continue/auto-load/auto-apply/auto-exec/auto-debug 的开放程度。

## 三、与讲透系列的对位

| Plandex 机制 | 对位主题 | 落点 |
|---|---|---|
| Plan 沙盒 + 内建 branch/rewind | Agent 记忆与规划（agent-development） | "可回滚的实验分支"是 Agent 安全性的工程答案 |
| 2M 上下文 + tree-sitter map 索引 20M+ 仓库 | llm-mastery（RAG/长上下文） | 不 retrieval 而是"地图压缩 + 选择性 load"的上下文工程 |
| 六角色 Model Packs | prompt-engineering（角色提示词） | 按任务阶段拆模型，而非单模型包打天下 |
| structured edits + 验证修复循环 | ML 工程实践（debug-helper） | 生成后必须验证（tree-sitter）→ 失败让模型自修，闭环可抄 |
| DB 锁 + heartbeat 并发 | 工程铁律（asyncio/并发） | 分布式锁的三层兜底：行锁/心跳超时/Git 锁清理 |

## 四、关键入口

```bash
repos/plandex/
├── app/cli/                      # 终端客户端（Cobra）
├── app/shared/                   # 跨端类型契约（PlanFileResult、token 工具）
└── app/server/
    ├── model/plan/               # ★ 核心：plan 执行状态机
    │   ├── tell_stream_main.go   #   tell 流式执行主循环
    │   ├── build_structured_edits.go  #   ★ structured edits 主策略
    │   ├── build_validate_and_fix.go  #   ★ 验证-修复循环（XML 自检）
    │   ├── build_whole_file.go   #   whole-file 降级路径
    │   └── build_finish.go       #   完成后 GitAddAndCommit 进沙盒
    ├── db/
    │   ├── locks.go              # ★ repo_locks 行锁 + 3s 心跳 + 60s 回收
    │   └── git.go                #   GitRepo 封装 + 重试包装
    └── syntax/                   # tree-sitter 验证/ApplyChanges
```

## 五、深读子页地图（33 页精选 6）

| 子页 | L 行号 | 价值 |
|---|---|---|
| Core Concepts | 639 | 全部概念一次讲清：plan/branch/context/model packs/自治五档 |
| File Modification Pipeline | 5338 | ★ 最核心：AI 输出→验证→修复→沙盒提交的完整管线 |
| Repository Locking and Git Integration | 10479 | ★ 版本控制优先的底座：锁/心跳/死锁恢复 |
| Plan Lifecycle and States | 4511 | plan 状态机与暂停/恢复/rewind |
| Active Plan Management | 7561 | 服务器侧 activePlans 生命周期与流管理 |
| Context and Token Management | 8711 | 2M 窗口下的上下文缓存与成本控制 |

## 六、与"我们"的关系（一句话）

Plandex 是"AI 生成必须先经过版本化沙盒 + 语法验证再落盘"这一工程范式的最完整 Go 参照系，其 build-验证-修复循环与 DB 锁并发控制可直接为讲透系列的 Agent 可靠性/上下文工程章节提供一手工业级案例。

---
生成：2026-08-21 · deepwiki 33 页全归档
