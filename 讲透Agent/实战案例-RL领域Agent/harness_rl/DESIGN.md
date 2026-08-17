# HarnessRL v4 设计卡 — RL agent 融合全部 harness 技术 + 双靶迭代

> card_id: harness-rl-v4
> universe: 讲透Agent/实战案例
> burke: 场景=生产式 agent 工程；主体=RL×harness 交叉工程师；能动=harness_agent+evolve 双环；行动=配置即动作空间的 bandit + AHE 编辑回滚；目的=agent 自举迭代两类 harness；张力=进化收益 vs 过拟合/配额；弧线=v3.1 三环 → v4 六组件全融合自指
> status: done（2026-08-17，实跑验证）
> refs: [harness工程手册](../../../工程化手册库/harness工程手册/README.md)（12章）· [AHE arXiv:2604.25850] · v3.1 [rl_agent.py](../rl_agent.py)

---

## 一、核心思想：配置即动作空间（Config-as-Action-Space）

v3.1 已把 **context 栈**变成 bandit 可进化对象（Ctx-APO）。v4 把这一招推到全集：
**harness 配置本身 = RL agent 的动作空间**。每章手册技术落位三处：

| 手册章 | 技术 | 在 v4 的落位 |
|---|---|---|
| 03 | E 执行循环三终止 | `run_battery` 的 natural/max_rounds/cost-cap |
| 03 | T 工具注册 | `GLM_CALL` 白名单 + schema + 结果预算 |
| 03 | L 钩子 fail-closed | `authorize()`（非白名单端点一律拒绝）+ 审计行 |
| 04 | C 上下文预算 | `components/ctx_budget.json`（prompt 截断 + keep_recent）|
| 04 | 参数趋同解 | 结果预算 16K、char/4 估算复用手册数值 |
| 05 | S 状态账本 | `ledger/trajectory.jsonl` 只追加 + `bandit_stats.json` 原子写 |
| 06 | V 验证金字塔 | L1 精确匹配 / L2 JSON schema 双层（能 L1 不升 L2）|
| 07 | 生命周期 | START 读四件套/组件 → WRAP UP 追加 progress 注记 |
| 08 | 多模型路由 | **臂**：flash / 5.3 / cascade（flash→verify 失败→5.3）|
| 09 | 方言适配 | 5.3 `reasoning_effort=low`（思考不可关只能降档）· 双端点路由 |
| 11 | 内环：进化 | contextual UCB1 over 臂 ×（extract/solve）任务型 |
| 11 | 外环：AHE | `evolve.py`：组件文件编辑 + 可证伪预测 + 回滚 + manifest |

## 二、双靶迭代（用户需求的两个对象）

```
内环（bandit，每任务）:  task-type → 选臂（harness 配置）→ reward = 2·pass − 0.2·cost
外环（AHE，每周期）:     distill 失败(GLM) → 编辑组件文件+预测 → 回归验证 → commit/revert

靶 1【RL 域 harness】 ../memory/ctx_policy.json（v3.1 的 CtxPolicy 五维——RL 领域 agent 的栈）
靶 2【自身 harness】  components/*.json（v4 自己的路由/预算/验证策略）
```

外环完全按 AHE 三观测性支柱：
① 组件=文件（JSON，可 diff 可回滚）② 失败蒸馏（GLM 归因，非原始日志）③ 决策清单（`manifest.jsonl`：edit+prediction+verdict 追加式）。

## 三、诚实边界

- cost 是**符号权重**（flash=1 / 5.3=8，近似积分系数比），非真实价格
- 任务电池 6 题（3 抽取 + 3 数学推理），L1 可判；回归子集 4 题——演示规模，非统计显著
- 5.3 thinking 不可关（手册 09 章约束），max_tokens=1024 + effort=low 控制
- 外环单周期 demo；多周期需配额与更大数据集（准入门槛见手册 11 章）

## 四、实跑战报（2026-08-17，真 GLM：flash=17+ / 5.3=5）

**内环（battery 3×6×4）**：学到的策略 `extract→A1_flash_plain(+1.80)`、`solve→A2_flash_struct(+1.80)`；
A1 在 T6 输出 python 代码块翻车拉低至 +1.30；A4 cascade 在简单 T4 上无谓升级花 9 成本——**手册 08 章
"级联预判失准的浪费"活案例**。配额：flash=16、5.3=3（熔断 cap=10 未触）。

**外环（manifest.jsonl 三周期全史）**：

| 周期 | SELF/model_route | RL-DOMAIN/ctx_policy | 机理 |
|---|---|---|---|
| c1 | **REVERT** | REVERT | 蒸馏投毒：GLM 把枚举值当字面量回显（`"model":"flash\|5.3\|cascade"`）→ 枚举校验缺失；v3.1 demo 内含 ctx-apo 自我改写靶文件 |
| c2 | REVERT | **COMMIT** topk 2→3 | 修枚举校验+本地 argmax 兜底+回归改 `--task` 纯读模式 |
| c3 | **REVERT**（正确拒绝）| COMMIT（toggle 3→2）| 便宜路由 flash-only 成本 11→3 但 pass 1.0→0.667——**质量不降门挡住成本诱惑** |

**三个诚实结论**：
1. REVERT 不是失败，是机制在工作——5 REVERT / 2 COMMIT 恰是 AHE"每次编辑=可证伪契约"的预期分布
2. RL-DOMAIN 靶目前是 **toggle probe**（2↔3 翻转，验证持久化管道）；要变成方向性改进，需接 v3.1 的
   ctx-apo 分数作为选向信号（下版 v4.1）
3. GLM 蒸馏在 toy 规模上两次未过枚举校验——**统计信号 > LLM 归因** 在小数据域成立（与 GLM-APO
   报告"判分器是瓶颈"互证）

**两处实跑中修掉的 bug**（供复现者）：`run_subset` 臂名拼接错误把 flash/struct 落入 cascade 分支
（成本假相等）；argmax 平局按臂名字典序误选 A4（改按期望成本序 A1<A2<A4<A3）。
