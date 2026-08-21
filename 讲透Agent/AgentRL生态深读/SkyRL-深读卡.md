# SkyRL 深读卡 —— Berkeley 全栈 RL 库（长程真实任务）

> **定位**：UC Berkeley Sky Computing Lab 的 full-stack RL 库——从训练框架到 agent 层到**环境 gymnasium** 的垂直整合；SWE-bench 级长程任务的 RL 标杆。
> **本地**：`~/ai/skyrl`（51M，663 文件）｜**深读**：deepwiki **无索引**（如实标注）→ 本地 README+目录深读（2026-08-17）

## 一、四大组件（本地 README，v0.3.0 2026-07）

| 组件 | 职责 | 备注 |
|---|---|---|
| `skyrl` | 统一库 = **skyrl-train**（模块化训练框架）+ **skyrl-tx**（Tinker API 跨平台后端，训推统一引擎）| 自有硬件跑 RL，支持 Tinker API 脚本 |
| `skyrl-agent` | 长程真实任务 agent 层 | SkyRL-v0：SWE-bench（OpenHands 上构建）|
| **`skyrl-gym`** | **工具任务 gymnasium**——math/coding/search/SQL 环境实现为标准 Gymnasium API | ⭐ 本卡最重要发现 |
| integrations | Harbor 终端 agent 训练集成（2026-02）| Terminal-Bench 2.0 配套评测 harness |

**代表成果**（SkyRL-v0）：~300 训练样本，SWE-Bench-Verified：OpenHands-7B 11.0→14.6%；Qwen3-8B 3.6→9.4%；Qwen3-14B(thinking) 18.0→21.6%。

## 二、skyrl-gym：Gymnasium API 的工具环境（⭐）

把"环境"降到最标准接口——`reset()/step(action)→(obs, reward, done, info)` 的 gym 生态，工具任务（数学/代码/搜索/SQL）全走同一协议。**与 AgentGym 的 HTTP env server 是两条路线**：
- AgentGym：环境=独立 HTTP 服务（跨语言/可分布式，重）
- skyrl-gym：环境=进程内 gym 对象（轻/标准/即插即用，复用 gymnasium 生态）

## 三、与本项目知识的对位

| SkyRL | 本项目 | 互证 |
|---|---|---|
| skyrl-gym Gymnasium API | 成熟度差距分析 P2（toy 包 env server）| **比 AgentGym HTTP 更轻的桥**——rl_agent 的 6 toy 可直接实现 gym Env 接口 |
| Harbor 集成训终端 agent | harness 精华（Harbor=Terminal-Bench 配套通用评测 harness）| harness 镜 §二 基准观的训练侧延伸 ✅ |
| SWE-bench 长程稀疏奖励 | 讲透RL/05 稀疏奖励讨论 | 300 样本即提升——RLVR 样本效率实证 |
| Tinker API 本地后端 | —— | 训推统一引擎的另一种解法（vs verl 混合引擎）|

## 四、关键入口（本地验证）

```
skyrl/            # 统一库（train+tx）
skyrl-agent/      # 长程 agent 层（examples/configs）
skyrl-gym/        # ⭐ Gymnasium API 环境库（math/coding/search/SQL）
examples/ docs/   # 配方与文档
CLAUDE.md         # 项目自带 AI 协作契约（对齐本项目 AGENTS.md 惯例）
```

## 五、与"我们"的关系（一句话）

SkyRL 的 skyrl-gym 给出了 rl_agent toy 走向标准化的**最短路径**（实现 `gymnasium.Env` 接口即可接入其训练栈）——若做差距分析 P2 的"env 桥"，选 gym API 而非 HTTP server，成本再降一半。

---
生成：2026-08-17 · 本地 51M 克隆深读（deepwiki 暂无索引，信息源如实标注：README v0.3.0 + 目录结构）
