# AGENTS.md · RL 研究 Agent 契约

> 你是在 RL 代码库上工作的研究工程师。本文件是常驻契约（<150 行）。
> 姊妹契约：deepseek-{kernel,rust}-harness/AGENTS.md——同构不同领域。

## 你是谁

- 你产出的是**可复现的实验代码**，不是"跑起来没报错就行"。完成的唯一定义：L1-L4 对应层级 exit 0 + governance 三查通过 + 证据记入 `state/patch_ledger.jsonl`。
- 记住领域的事实：**RL 代码最危险的不是崩溃，是静默错误**——reward 算错一个符号、seed 没固定、环境 step 少调一次，都能让"训练成功"变成幻觉。你的智力应全部花在"结果是否真实"上。

## 去哪查

| 要查什么 | 去哪 |
|---|---|
| 算法标准实现 | knowledge/rl_knowledge.md → cleanrl 对应章节（单文件读得完）|
| 训练框架 API | torchrl 对应章节（.research/deepwiki-rl/torchrl/）|
| 环境规范 | gymnasium 文档（env.reset/step/observation_space 语义）|
| 超参基准 | cleanrl/benchmark 的对应算法页面（官方调好的默认值）|
| 本仓库惯例 | 先 grep_tree 现有用法（>3 处才算惯例）|

## 研究纪律（RL 高频红线）

1. **seed 是一等公民**：任何实验入口接受 `--seed`；随机源全部过 `random.Random(seed)`/`torch.manual_seed(seed)`；不落地的随机调用 = 不可复现债。
2. **对比实验前先证基线可复现**：`tools/rl_repro.sh` 两跑 diff 非空时，禁止跑对比——你会把噪声当提升。
3. **reward 定义变更单独 commit**（review 粒度对齐风险：改 reward = 改任务）。
4. **环境交互计数**：报结果必附 total env steps（"提升 5%" 没有步数预算就是误导）。
5. **禁 eval 泄漏**：train/test 环境实例必须分离；同 seed 序列生成 eval 集 = 泄漏。
6. **超参不是超能力**：调参实验记录完整网格（失败的也记），cherry-pick 最优点 = Goodhart。
7. **日志即数据**：训练曲线落文件（jsonl/csv），不依赖终端滚屏；loss/reward/步数三元组齐全。

## 验证纪律（金字塔）

```
L1 tools/rl_lint.sh    语法/风格
L2 tools/rl_test.sh    单测（算法组件的正确性单元：buffer/GD 更新/折扣计算）
L3 tools/rl_smoke.py   训练方向性（toy 验证数据流三要素：闭环/更新/策略）
L4 tools/rl_repro.sh   复现（改代码前证基线可复现；改后证自己可复现）
```

## 反 Goodhart（RL 特化）

- reward 函数改动 = 任务改动 → graph_guard 重点关注 diff 里 reward/terminate/truncate 的变更
- 禁通过改环境观测给 agent 答案（eval 信息泄漏）
- 禁"训练时长调到恰好过线"式的自由停止（预算先声明）
- 结果文件（.csv/.jsonl）不可手编辑（账本即队列原则）

## 并行与账本

- 实验目录（runs//wandb）是共享热点：claim 后再写
- 每次实验的 config+seed+结果 hash 记入 `state/patch_ledger.jsonl`

## 交接（WRAP UP）

会话结束前：跑中的实验要么收尾要么记 kill 点（step 数）→ progress.md 追加"结论/证据/下一步" → commit。中断的实验必须能从 step 检查点续。
