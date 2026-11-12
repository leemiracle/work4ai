# sage 深读卡 —— 拜占庭容错的机构记忆基建：CometBFT 共识验证的 Agent 知识层

> **定位**：SAGE（Sovereign Agent Governed Experience）——**拜占庭容错（BFT）的机构记忆基础设施**：不是向量库或 flat-file 技能，而是经**共识验证的持久知识层**——agent 跨对话/跨组织边界积累的 facts/observations/inferences 带**可验证审计链**，防 LLM 无状态"失忆"。双模式部署：个人模式（sage-gui 单二进制跑本地 CometBFT + 4 进程内验证者）与多 Agent 组织模式。
> **本地**：`repos/sage`（l33tdawg/sage）｜**深读**：deepwiki 38 子页归档 `deepwiki/sage/full.md`（2026-08-21）

## 一、组件栈（DeepWiki 蒸馏）

| 层 | 职责 | 关键实体 |
|---|---|---|
| 共识层 | BFT 验证 | CometBFT（Tendermint 系）+ 应用链 |
| 部署 | 双模式 | sage-gui（个人：单二进制+4 进程内验证者）/多组织 |
| 知识层 | 记忆单元 | facts/observations/inferences（共识入链） |
| 审计 | 可验证轨迹 | verifiable audit trail |

## 二、核心机制

1. **共识即记忆可信**：每条记忆经 CometBFT 验证者共识才入库——记忆写入=区块链交易，不可篡改可审计（对照 bernstein HMAC 链：sage 用真 BFT 共识，更重更强）。
2. **三种知识类型**：事实（客观）/观察（经历）/推断（推理结论）分类上链——结构化而非平铺。
3. **个人模式单二进制**：本地 4 验证者进程内跑——BFT 基建的"桌面化"罕见尝试。

## 三、与讲透系列的对位

| 概念 | 讲透系列对应概念 |
|---|---|
| BFT 记忆共识 | 讲透分布式AI系统 §拜占庭容错（Agent 记忆场景应用！） |
| 可验证审计 | bernstein HMAC 对照（轻重两极） |

## 四、关键入口

```
sage-gui/           # 个人模式单二进制
（CometBFT 应用链；详见 wiki Deployment Modes）
```

## 五、深读子页地图（38 页精选 5）

SAGE Overview｜Deployment Modes｜共识/验证章节｜知识类型模型｜审计链。

## 六、与"我们"的关系（一句话）

"区块链×Agent 记忆"的认真实现——讲分布式 Agent 或记忆可信专题时的极端样本：当审计要求高到需要 BFT 共识时，记忆系统长这样。

---
生成：2026-08-21 · deepwiki 38 页全归档
