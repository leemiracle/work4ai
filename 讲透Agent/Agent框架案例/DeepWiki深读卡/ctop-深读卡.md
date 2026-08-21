# ctop 深读卡 —— "htop for AI Agents"：零依赖终端面板监控本地编码 Agent 资源与会话

> **定位**：aakashadesara 出品的零依赖实时终端运维面板——监控并管理本地 AI 编码 Agent（**Claude Code / Codex CLI / OpenCode**）：CPU/内存/token 计数/上下文窗口占用/API 成本，多并发 agent 会话统一视图。核心管线 **Poll-Enrich-Render**：发现活动进程→映射本地会话数据（JSONL/SQLite）→渲染 TUI。
> **本地**：`repos/ctop`（aakashadesara/ctop）｜**深读**：deepwiki 31 子页归档 `deepwiki/ctop/full.md`（2026-08-21）

## 一、组件栈（DeepWiki 蒸馏）

| 层 | 职责 | 关键实体 |
|---|---|---|
| 发现层 | 轮询活动 agent 进程 | Poll（Claude Code/Codex/OpenCode 进程探测） |
| 富化层 | 进程↔会话数据关联 | Enrich（JSONL/SQLite 会话文件解析：token/上下文/成本） |
| 渲染层 | 终端 UI | Render（自研 TUI，零依赖） |

## 二、核心机制

1. **Poll-Enrich-Render 三段管线**：系统级进程信息（psutil 思路）+ agent 特有会话数据（各家 CLI 的本地存储格式）join 后投影 TUI——把"Agent 当一等系统进程"来运维。
2. **零依赖**：无 Node/Python 运行时要求，单二进制（对照 phoenix 的重型可观测平台路线——这是轻量终端派）。
3. **上下文窗口利用率可视化**：不只看 CPU/内存，还看 token/上下文占用——为"上下文是 Agent 最稀缺资源"这一 2026 共识提供了运维视角证据。

## 三、与讲透系列的对位

| 概念 | 讲透系列对应概念 |
|---|---|
| Agent 资源监控 | 讲透Agent/00 §可观测性（终端轻量派 vs phoenix 平台派） |
| 会话数据解析 | 上下文工程（窗口占用度量） |

## 四、关键入口

```
源码按 Poll/Enrich/Render 三模块组织（详见 wiki System Workflow 数据流图）
```

## 五、深读子页地图（31 页精选 4）

Overview（Poll-Enrich-Render 数据流）｜System Workflow｜各 agent 适配（Claude Code/Codex/OpenCode 会话格式）｜TUI 渲染。

## 六、与"我们"的关系（一句话）

"Agent 运维（AgentOps）"最小工具样本——讲可观测性章时与 phoenix 构成"终端单机 vs 平台全栈"两极对照。

---
生成：2026-08-21 · deepwiki 31 页全归档
