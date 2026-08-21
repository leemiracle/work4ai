# hcom 深读卡 —— Rust 终端 Agent 通信总线：PTY 包装 + hook 拦截让 CLI Agent 互相说话

> **定位**：aannoo 出品的多 Agent 通信系统——打通**各自跑在独立终端会话**的 AI 工具（Claude Code/Gemini CLI/Codex/OpenCode）之间的隔阂：互相发消息（request/inform/ack 三意图+线程+@提及）、互相监听（文件编辑/命令历史/状态变化防冲突）、互相编排（spawn/fork/resume 到新终端窗格）、共享上下文（transcripts+事件历史结构化交接）。Rust 实现（maturin 打 Python wheel），PTY 包装 AI 工具进程+hook 拦截活动。
> **本地**：`repos/hcom`（aannoo/hcom）｜**深读**：deepwiki 45 子页归档 `deepwiki/hcom/full.md`（2026-08-21）

## 一、组件栈（DeepWiki 蒸馏）

| 层 | 职责 | 关键实体 |
|---|---|---|
| 进程层 | PTY 包装 AI CLI | PTY wrapper（拦截工具活动） |
| Hook 层 | 活动拦截上报 | hooks 系统（文件编辑/命令历史捕获） |
| 消息层 | Agent 间通信 | 意图（request/inform/ack）、线程、@mentions |
| 监听层 | 活动监控防碰撞 | watching（file edits/commands/status: listening/active/blocked） |
| 编排层 | 跨终端派生 | spawn/fork/resume（新终端 pane） |
| 上下文层 | 交接包 | structured bundles（transcripts+events） |

## 二、核心机制

1. **PTY+Hook 无侵入集成**：不改各家 CLI 源码，PTY 包装进程+hook 捕获活动——任何终端 AI 工具零改造接入（对照 dorothy 同用 PTY 但做了桌面壳；hcom 是纯通信层）。
2. **三意图消息协议**：request/inform/ack 的 speech-act 语义+线程化+@提及——agent 间通信的最小完整协议（对照 A2A 的重协议路线）。
3. **监听防碰撞**：agent 可 watch 其他 agent 的文件编辑/命令——并行工作流冲突预警（blocked 状态）。

## 三、与讲透系列的对位

| 概念 | 讲透系列对应概念 |
|---|---|
| Agent 间消息协议 | 讲透多Agent协作/02 §通信协议（轻量 speech-act 派） |
| PTY+hook 集成 | 讲透Agent/02 §工具接入（无侵入路线） |
| 上下文交接包 | 讲透Agent/04 §记忆（交接即记忆迁移） |

## 四、关键入口

```
src/commands/*.rs       # 命令实现（help.rs 含协议文档）
Cargo.toml              # Rust 主体
```

## 五、深读子页地图（45 页精选 5）

Overview（实体映射图）｜消息/监听协议｜PTY/Hook 架构｜spawn/resume 编排｜上下文 bundle。

## 六、与"我们"的关系（一句话）

"Agent 互联"最轻量实现——与 A2A（平台级协议）构成"终端黑客派 vs 企业标准派"的绝妙对照，讲多 Agent 通信章双例并排。

---
生成：2026-08-21 · deepwiki 45 页全归档
