# connectonion 深读卡 —— 极简 Python Agent 框架：两行起 Agent + 钩子内核 + P2P relay 网络

> **定位**：openonion 的 ConnectOnion——"Keep simple things simple, make complicated things possible"：**两行代码起 agent**（LLM 脚本级简单），复杂时给你行为追踪/交互调试/多 agent 协作/auto_compact 上下文管理/自主子 agent 生成/**P2P relay 网络**——定位"LLM 周边基础设施"（工具 schema 生成/会话状态/活动日志框架包办，开发者只写 prompt 和函数）。
> **本地**：`repos/connectonion`（openonion/connectonion）｜**深读**：deepwiki 50 子页归档 `deepwiki/connectonion/full.md`（2026-08-21）

## 一、组件栈（DeepWiki 蒸馏）

| 层 | 职责 | 关键实体 |
|---|---|---|
| Agent 核心 | 两行起步 | Agent + 工具 schema 自动生成 |
| 行为层 | 追踪调试 | behavior tracking + interactive debugging |
| 上下文 | 窗口管理 | auto_compact（自动压缩） |
| 多 Agent | 协作 | 信任验证 + 自主子 agent spawn |
| 网络 | P2P | P2P relay networking |
| 钩子 | 扩展 | event hooks |

## 二、核心机制

1. **两行代码承诺**：`Agent(model, tools)` + `agent("prompt")` 即跑——比 swarm 还少一行的启动成本（工具 schema 从函数签名自动生成）。
2. **auto_compact**：上下文窗口自动管理——窗口将满自动压缩，开发者无感（对照 opencode 三级防御：这里是自动化单级）。
3. **P2P relay 网络**：agent 经 relay 互联——去中心化协作选项（对照 uAgents 的 agentverse：更轻的 P2P 路线）。

## 三、与讲透系列的对位

| 概念 | 讲透系列对应概念 |
|---|---|
| 两行起步 | swarm 对照（极简双雄） |
| auto_compact | 讲透Agent/00 §上下文自动管理 |
| P2P relay | 讲透分布式AI系统 §P2P |

## 四、关键入口

```
（Python 包：Agent 核心+hooks+网络层；README L29-34 两行示例）
```

## 五、深读子页地图（50 页精选 5）

Overview（哲学）｜Agent 快速上手｜auto_compact/上下文｜多 agent 与子 spawn｜P2P 网络。

## 六、与"我们"的关系（一句话）

"极简派"最新样本——与 swarm（已废弃教学版）对照看 2024-2026 极简框架的进化：两行启动不变，复杂能力（压缩/子agent/P2P）变成可选项。

---
生成：2026-08-21 · deepwiki 50 页全归档
