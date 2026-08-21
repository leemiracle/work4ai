# AgentRL 生态深读 —— 2026 开源 RL Agent 基础设施地图

> **触发**：rl_agent 成熟度评估的后续行动——把 6 个主流项目克隆到本地（`~/ai/`）+ deepwiki 全子页蒸馏 + /understand zh 管线（知识图谱/新人指南/文件深解）。
> **管线**：每项目 = 深读卡（deepwiki+本地验证）+ [小仓库] understand 三件套（knowledge-graph.json / ONBOARDING.md / CORE-FILES-EXPLAIN.md）。
> **执行日**：2026-08-17 · 全部 repo 浅克隆本地 + deepwiki 索引日期逐卡标注

## 一、项目总表

| 项目 | 规模 | 深读方式 | 产物 | 一句话定位 |
|---|---|---|---|---|
| [AgentGym-RL](./agentgym-rl/) | 17M(+127M submodule) | understand 三件套 | 图谱+onboarding+explain | 最接近"成熟版我们"：环境/agent/训练解耦（ICLR 2026 Oral）|
| [Uni-Agent](./uni-agent/) | 8.3M | understand 三件套 | 图谱+onboarding+explain | 任意 harness 接进 RL（理念最近）|
| [verl](./verl-深读卡.md) | 18M | deepwiki 90+子页+卡 | 深读卡 | 训练底座（HybridFlow EuroSys 2025）|
| [verl-tool](./verl-tool-深读卡.md) | 24M | deepwiki 50+子页+卡 | 深读卡 | Tool-as-Environment（TMLR 2026，<200行 agent loop）|
| [AWorld-RL](./AWorld-RL-深读卡.md) | 184M | deepwiki 25子页+卡 | 深读卡 | 数据闭环五子系统（RODS/EnvTuning ICLR 2026）|
| [SkyRL](./SkyRL-深读卡.md) | 51M | 本地深读（deepwiki 无索引）| 深读卡 | 全栈 RL 库 + skyrl-gym Gymnasium 环境库 |
| [torchrl](./torchrl/) + [深读卡](./torchrl-深读卡.md) | 43M | **双管线**：deepwiki 40子页 + understand 三件套 | 卡+图谱+onboarding+explain | PyTorch 官方组件化 RL 全家桶（TensorDict 中心架构，含 LLM 后训练 GRPO）（2026-08-20 入库）|
| [cleanrl](./cleanrl/) + [深读卡](./cleanrl-深读卡.md) | 179M | **双管线**：deepwiki 33子页 + understand 三件套 | 卡+图谱+onboarding+explain | 单文件 DRL 算法博物馆：可读性压倒一切（deepwiki 索引与本地 commit fe8d8a0 完全同步）（2026-08-20 入库）|

规模为浅克隆实测；代码文件数：verl 750 / verl-tool 872 / skyrl 663 / AWorld-RL 415 / uni-agent 148 / AgentGym-RL 核心增量~30 / torchrl 核心 434（全仓 816，图谱含根配置 474）/ cleanrl 全仓 206（核心算法 37 脚本）。

**torchrl/cleanrl 双管线产物**（2026-08-20，与上表 8/17 批次同管线加深）：知识图谱 torchrl 2267 节点/5854 边/10 层/13 步导览、cleanrl 487 节点/1052 边/7 层/11 步导览（校验 0 issues）；ONBOARDING 分别列 49/43 个关键文件并全部被 CORE-FILES-EXPLAIN 逐个精讲（含 file:line 实测锚点，cleanrl 精讲还纠正了 deepwiki 两处失实行号）。原始 deepwiki 全子页快照存 `.research/deepwiki-rl/`（40+33 页）。

## 二、生态演进地图（用户七层总结的深读印证）

```
训练底座(verl) → 工具扩展(verl-tool) → 垂直场景(SkyRL/SWE-bench)
  → 通用解耦(AgentGym-RL) → 任意 harness 接入(Uni-Agent)
  → 数据闭环(AWorld-RL) + [横切] 标准环境接口(skyrl-gym Gymnasium API)
  + [纵向参考系] "怎么写 RL 代码"的两极：组件化工业库(torchrl) ↔ 单文件教学库(cleanrl)
```

torchrl 与 cleanrl 构成生态的**纵向参考系**：同一个 PPO/DQN/SAC，在 cleanrl 里是一个 300 行可整读的脚本（`cleanrl/ppo.py`），在 torchrl 里是 EnvBase→Collector→TensorDictModule→PPOLoss→Trainer 五个可换零件的组装（`torchrl/objectives/ppo.py`）。所有上层框架（verl/SkyRL…）的设计选择都落在这两极之间。

## 三、与本项目资产的互链

- 差距分析：[../讲透Agent/实战案例-RL领域Agent/成熟度差距分析-vs2026生态.md](../讲透Agent/实战案例-RL领域Agent/成熟度差距分析-vs2026生态.md)（6 项核心差距 ↔ 本目录 6 项目逐一对位）
- toy 对照：[../讲透Agent/实战案例-RL领域Agent/](../讲透Agent/实战案例-RL领域Agent/)（rl_agent/skill_agent——"教学前置层"定位）
- 算法理论：[../讲透RL/](../讲透RL/)（verl core_algos.py 是 02-03 章算法的工业实现；**cleanrl 单文件是 01/02/08 章算法的最小可读实现，torchrl 是组件化工业实现**——三档对照：cleanrl 读→torchrl 组→verl 训 LLM）
- harness 镜：[../harness精华合入-总入口.md](../harness精华合入-总入口.md)（Harbor/验证即证据 ↔ SkyRL 集成）

## 四、下一步候选

1. skyrl-gym 的 Gymnasium API 是 rl_agent toy 标准化的最短路径（差距分析 P2 修订：gym Env 接口而非 HTTP server）
2. verl-tool 的 mask_observations（观察不计梯度）值得补进讲透RL/03 多轮 GRPO 节
3. AWorld-RL RODS 的"奖励方差边界探测"可进 prompt 手册 11 章的方案 B 增补

---
生成：2026-08-17 · 增补：2026-08-20（torchrl/cleanrl 双管线入库）· 挂网：[讲透Agent/README](../讲透Agent/README.md) 配套生态"工业生态对照"行 · 本地克隆 `~/ai/`（更新：`git -C <repo> pull` 或删后重浅克隆）
