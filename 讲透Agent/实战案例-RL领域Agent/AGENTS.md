# AGENTS.md —— rl_agent 案例的行为契约（harness 五子系统之 Instructions）

> 本文件是给"在本目录工作的任何 agent（人或 AI）"的指令边界。存在即 README "harness 四件套"承诺的第四件。

## 是什么
`rl_agent.py`：讲透Agent × 讲透RL × 讲透Prompt 的可跑缝合器（v3.1 829+ 行纯标准库）。定位见 ../README.md——**不是生产级 RL 框架，是活教材**。

## 在此目录工作的规则
1. **改代码前先跑** `python3 rl_agent.py demo`（基线 ~2.4s，战报 5/6——含 1 个设计内必失败任务）；改完必须重跑对比。
2. **宪法**：纯标准库零依赖 / demo <10s / toy 实验诚实标注简化处（GRPO 缺 PPO 目标用乘法 clip 近似、bandit 是 γ=0 退化）。
3. **红线**：`memory/` 与 `progress.md` 是运行产物**绝不进 git**（.gitignore 已设）；API key 只走 env，不进代码/日志/聊天。
4. **新增实验**：函数名 `exp_*`、注册进 `EXPERIMENTS`、输出必须带 `← 章节锚点`、几秒跑完、诚实标注与真算法的差距。
5. **奖励设计**：改动 reward 判定前重读 rl_agent.py 头部"诚实声明"与讲透RL/09 失败模式——本案例的 P0 教训就是"未匹配也算成功"的 reward hacking。
6. 审查历史见 `多角色审查报告-RL领域Agent.md`（2026-08-17 五角色），修 bug 前先查该报告避免回归。
