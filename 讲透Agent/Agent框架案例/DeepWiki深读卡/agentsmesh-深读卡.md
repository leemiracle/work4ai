# agentsmesh 深读卡 —— 团队级终端编码 Agent 编排平台：AgentPod（PTY+worktree 沙盒）×BYOK×自托管 Runner

> **定位**：AgentsMesh——团队规模运行/协调终端编码 Agent（Claude Code/Codex CLI/Gemini CLI/Aider 等）的平台：**AgentPods** 隔离执行环境（PTY 终端+Git worktree 沙盒+浏览器可访问终端视图）、多 agent 协作（Channels 通信/Bindings 观察控制同伴终端/MCP 工具自主 spawn 新 Pod）、看板任务管理（agent-ticket 绑定+MR/PR webhook）、**自托管 Runner**（代码执行全在用户基建，平台只编排生命周期）。**BYOK**：不代理 AI 调用，用户自带 API key。
> **本地**：`repos/agentsmesh`（AgentsMesh/AgentsMesh）｜**深读**：deepwiki 41 子页归档 `deepwiki/agentsmesh/full.md`（2026-08-21）

## 一、组件栈（DeepWiki 蒸馏）

| 层 | 职责 | 关键实体 |
|---|---|---|
| AgentPod | 隔离执行 | PTY 终端+Git worktree 沙盒+浏览器终端 |
| 协作 | agent 间 | Channels（通信）/Bindings（观察控制）/MCP（spawn Pod） |
| 任务 | 看板 | Kanban+agent-ticket 绑定+webhook |
| Runner | 自托管执行 | Go daemon（用户基建上跑代码） |
| 计费模型 | BYOK | 平台零 API 代理，key 直传 Runner 环境 |

## 二、核心机制

1. **Pod=PTY+worktree 双隔离**：进程（PTY）与代码（git worktree）双沙盒——并行 agent 不互踩终端与文件（与 dorothy PTY 对照：mesh 加了 worktree+网络协作维度）。
2. **Bindings 跨终端观察控制**：agent 可绑定同伴 agent 的终端观察甚至操控——团队协作的"结对编程"agent 化（对照 hcom 的 watch：mesh 更进一步到控制）。
3. **BYOK+自托管双坚持**：平台不经手 AI 流量与用户代码——企业信任模型的最硬承诺（对照 Steel/Dust 的托管路线）。

## 三、与讲透系列的对位

| 概念 | 讲透系列对应概念 |
|---|---|
| Pod/worktree 隔离 | 讲透多Agent协作 §执行隔离 |
| Channels/Bindings | hcom 对照（通信→观察→控制三级） |
| BYOK 自托管 | ai-deployment §信任模型 |

## 四、关键入口

```
runner/             # Go Runner daemon
deploy/dev/docker-compose.yml  # key 环境变量清单（L279-288）
```

## 五、深读子页地图（41 页精选 5）

Overview（五组件+BYOK）｜Architecture（协议级通信）｜Core Concepts（Pod/Channel/Binding/Sandbox）｜Runner｜Ticket 管理。

## 六、与"我们"的关系（一句话）

"多编码 Agent 团队协作"的完整平台化样本——与 hcom（通信库）/dorothy（桌面）构成终端 agent 协作的三种产品形态。

---
生成：2026-08-21 · deepwiki 41 页全归档
