# deepseek-rl-harness

> DeepSeek 引擎 + 六组件骨架 + **RL 研究领域插件**。deepseek-{kernel,rust}-harness 的第三个家族成员（2026-08-20）：
> 同一宿主骨架（harness工程手册 12 章）、同一引擎方言层（engines/ 复用）——**换领域 = 换 tools/ + governance/ + AGENTS.md + knowledge/**。

## 定位：RL 算法研究 + 强化学习应用

- **研究侧**：算法实现/魔改的验证闭环（cleanrl 哲学：单文件读得完）
- **应用侧**：把 RL 问题的工程化门槛降下来——金字塔四层对应 RL 特有的失败模式

## RL 版金字塔（为什么变形）

| 层 | rust 版 | rl 版 | RL 领域的失败模式 |
|---|---|---|---|
| L1 | fmt | py_compile/ruff | — |
| L2 | clippy | pytest | 算法组件单元（buffer/更新式/折扣）|
| L3 | build+test | **训练冒烟（方向性断言）** | **静默不学习**（循环空转/reward 恒 0）——RL 特有 |
| L4 | miri+audit | **复现检查（同 seed 两跑 diff 空）** | **不可复现的提升**（seed/GPU 非确定/环境漂移）——RL 特有 |

governance 三病的 RL 形态：Goodhart = **reward hacking**（伪造/泄漏/预算滥用）；盲区 = 环境版本+超参文件；冲突 = 实验目录与结果文件。

## 知识底座

`knowledge/rl_knowledge.md`——算法族谱 + 按任务选读路径 + **.research/deepwiki-rl/ 73 篇的挂网索引**（torchrl 40 + cleanrl 33，DeepWiki 抓取于 2026-08-20，零失败）。

## 快速开始

```bash
python3 rl_host.py --self-test          # 零依赖自检（含 L3 冒烟真实跑）
python3 tools/rl_smoke.py               # 单独跑训练冒烟（纯标准库，秒级）
bash tools/rl_repro.sh "python3 tools/rl_smoke.py"   # 复现检查示例
export KH_API_KEY=... RL_PROJECT=/path/to/rl-code
python3 rl_host.py --task "给 DQN 实现补 Double DQN 的目标网络更新并过 L2-L4"
```

## 结构

```
rl_host.py          宿主：六组件 + cascade，RL 特化工具表
engines/ hooks/ governance/    与 rust 版完全复用（插件化的结构验证）
tools/rl_lint.sh    L1  语法+风格
tools/rl_test.sh    L2  单测
tools/rl_smoke.py   L3  训练冒烟（bandit+Q-learning 方向性断言，实测 PASS）
tools/rl_repro.sh   L4  复现（strip 时间戳后 diff，实测 OK）
knowledge/rl_knowledge.md   算法族谱+选读+deepwiki 索引挂网
AGENTS.md           RL 研究契约（seed 一等公民/预算先声明/结果文件不可手编）
```
