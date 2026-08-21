# loongflow 深读卡 —— 百度百舸 PES 认知范式框架：Plan-Execute-Summarize × 进化记忆（MAP-Elites 多岛）

> **定位**：baidu-baige（百度百舸）出品的专家级 Agent 框架——用 **PES（Plan-Execute-Summarize）思考范式**解长程推理任务：像人类专家一样系统规划、审慎执行、从成败中学习。三件套：`PESAgent`（范式实现，worker 注册三阶段）、**进化记忆系统**（`EvolveDatabase`：多岛架构+MAP-Elites 多样性保持+自适应 Boltzmann 选择）、三个专用 Agent（math/ml/general）+ LiteLLM 全模型兼容。
> **本地**：`repos/loongflow`（baidu-baige/LoongFlow）｜**深读**：deepwiki 50 子页归档 `deepwiki/loongflow/full.md`（2026-08-21）

## 一、组件栈（DeepWiki 蒸馏）

| 层 | 职责 | 关键实体 |
|---|---|---|
| 范式层 | PES 循环 | `PESAgent`（register_planner_worker/execute/summarize 三阶段注册） |
| 记忆层 | 进化数据库 | `EvolveDatabase`：多岛+MAP-Elites+Boltzmann 自适应选择 |
| Agent 层 | 三专家 | agents/math_agent、ml_agent、general_agent |
| 模型层 | 无关接入 | LiteLLMFormatter（OpenAI 兼容） |

## 二、核心机制

1. **PES 三阶段范式**：Plan（系统设计）→Execute（审慎执行）→Summarize（成败双学习）每进化周期一轮——把"专家解题流程"固化为框架级循环。
2. **MAP-Elites 进化记忆**：经验库按"行为描述子"分岛存优（质量-多样性算法），Boltzmann 探索温度自适应——**真正把进化计算算法用进 Agent 记忆**的罕见实现（对照 ACE 的 BM25/向量检索：这里是 QD 算法检索）。
3. **专家领域分化**：math/ml/general 三 Agent 各自调 PES——范式与领域解耦。

## 三、与讲透系列的对位

| 概念 | 讲透系列对应概念 |
|---|---|
| PES 范式 | 讲透Agent/03 §规划（plan-execute 范式+总结学习闭环） |
| MAP-Elites 记忆 | 讲透学习型Agent §质量多样性进化（真实工程应用！） |
| Boltzmann 选择 | 讲透RL §探索策略 |

## 四、关键入口

```
（PESAgent/EvolveDatabase/agents/*；详见 wiki PES Paradigm 页）
```

## 五、深读子页地图（50 页精选 5）

Overview（PES 范式表）｜PES Paradigm｜EvolveDatabase/进化记忆｜General/Math/ML Agent｜LiteLLM 集成。

## 六、与"我们"的关系（一句话）

把进化计算（MAP-Elites/Boltzmann）严肃接入 Agent 记忆的稀缺样本——讲透学习型Agent 进化章的最强工程对照，大厂（百度）出品保证完成度。

---
生成：2026-08-21 · deepwiki 50 页全归档
