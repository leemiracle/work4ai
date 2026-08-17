# 多角色审查报告 · 实战案例-RL领域Agent

> **审查日期**：2026-08-17
> **审查角色**：5 视角（4 个专家 subagent 并行委派 + 主 agent 完整性审计）
> **审查对象**：rl_agent.py v1（390 行）+ README v1
> **状态**：✅ 全部 P0/P1 已修，P2 修 18/20（v2 = 716 行，战报 5/6 设计内）

---

## 一、角色与结论速览

| 角色 | Agent | 核心判词 | 评分 |
|---|---|---|---|
| 🔬 RL 技术深度 | @oracle | gridworld TD 实现全对（off-policy max/goal 不进 Q 构造性正确）；**GRPO 实验在教错误的方法论**（结论印死非测出）；UCB 分支运行必崩 | 齐全度 7/15 全+4/15 半 → 修复后 13/15 |
| 🔒 安全合规 | @security-auditor | 无 P0（无 shell/eval 面）；RAG 注入+记忆污染两条真实 P1；Safety 齐全度 2/5 | 修复后 ~4/5 |
| ⚙️ 工程质量 | @performance-analyst | 实测 0.36s 达标；**reward 虚高实锤**（战报 4/4 假）；semantic 缓存层是"文档宣称的记忆层不存在" | kb 占 99% 耗时 → 缓存后消除 |
| 🎯 战略完整性 | @councillor | 20 项映射 15 项名实相符；#16 纯虚构；孤儿卡违反目录宪法 | 映射可信度 62 → 90+ |
| 📊 完整性审计 | 主 agent | GRPO"无 baseline 更优"跨 3 seed 稳定复现（非噪声是设计缺陷）；councillor 的"姊妹案例断链"经 find 复核为**误报**（目录实存于 讲透Agent/Agent框架案例/），但顺带发现 讲透Agent/README 两个真断链 | — |

## 二、统一问题清单（修复状态）

### 🔴 P0（6 项，全部已修 ✅）

| # | 问题 | 来源 | 修复 |
|---|---|---|---|
| P0-1 | reward 虚高：paper_locate/recall 恒 True，"未匹配"计成功；**reward hacking 活体**（污染 Q[experiment][paper_locate]=0.83）| perf/oracle/主 | 未匹配→False；recall 永不计证据；experiment 态必须真跑实验；删除污染 Q 表重训 |
| P0-2 | UCB 分支 `np.log_safe` NameError（bandit 整体崩溃，Thompson 永不执行）| oracle | `log_safe()` 顶部定义 |
| P0-3 | `--sc` 声称未实现（映射表#16 纯虚构）| councillor | `solve_sc` 真实现：3 seed 采样→证据引用投票→平票诚实标注 |
| P0-4 | AGENTS.md 缺失但 README 称"已提交" | councillor | 已写（含行为契约 6 条）|
| P0-5 | 孤儿卡：两个母宇宙 README 均未挂 | councillor | 已挂 讲透Agent/README 篇目表 |
| P0-6 | 乱码任务靠"默认 gridworld"假成功（我方修复中自造的新 hack）| 主 | 未指明实验名→False |

### 🟠 P1（13 项，全部已修 ✅）

| # | 问题 | 来源 | 修复 |
|---|---|---|---|
| P1-1 | GRPO 单 seed+指标不度量方差+共享 rng 流+结论印死 | oracle/主 | 21 seed×配对 rng×mean±std×noise=3.0；**实测结论**：baseline std 0.02 vs 0.06（方向终于正确）|
| P1-2 | GRPO 缺 /std 归一（与讲透RL/03 概念漂移）| oracle | (r−mean)/(std+ε) + 乘法 clip∈[0.8,1.25]（PPO 近似，诚实标注）|
| P1-3 | 链式折扣方向反（失败先手 1.0 > 成功后手 0.6ⁱ）且与 γ=0 声明矛盾 | oracle | 证据工具得 r_task、试而不成得 0、未试不动 |
| P1-4 | kb 命中即短路满分（experiment 可不跑实验）| oracle | experiment 态 run_experiment 必须在链上 |
| P1-5 | RAG 注入：kb 原文直拼 system prompt | security | kb 走 user 消息+"数据非指令"边界声明 |
| P1-6 | 记忆污染零校验（KeyError DoS/输出注入/行为劫持）| security | load_qtable/load_lessons schema+值域+控制符校验，坏条目丢弃 |
| P1-7 | demo 四场景 Reflexion 零触发 | councillor | 设计内必失败任务（乱码）→ reflect→教训落盘全链路可见 |
| P1-8 | LLMBrain 假 ReAct（单发 RAG）| councillor | 真 JSON 协议工具循环（LLM 无执行权）+引用回查 verify_citation |
| P1-9 | semantic 缓存层宣称未实现（实测两次同查零缓存）| perf | 进程级 mtime 感知索引缓存 |
| P1-10 | "5 工具"实为 4 动作 | councillor | 文档改"4 动作+1 系统触发器（reflect）"并写成教学点 |
| P1-11 | demo 无 mixed 态 | perf | 任务措辞修正，四态全覆盖（Q 表 4 键）|
| P1-12 | APO 评估被已训 Q 表掩蔽（v1→v2 轮实测发现）| 主 | persist=False fresh 大脑评估，隔离 prompt 变量 |
| P1-13 | APO 无梯度（全成功满分）| 主 | 目标=reward−0.02×步数（效率塑形⑤，本身是活教材）|

### 🟡 P2（20 项，修 18；2 项说明）

已修：墙 BFS 连通性+足量采样 / ε 统一 0.2 / Q_INIT 注释改"中性" / 死变量清除 / 证据取最后成功项 / 原子写(os.replace) / progress 400 行滚动 / save 每 solve 一次 / `with` 句柄 / 异常类型打印 / https 强制 / API 24 次熔断 / ANSI 剥离 / kb 预算(400 文件/2MB) / 自指污染(跳过本案例目录) / 唯一关键词计分防堆砌 / 行数实测 390→716 / feature_list 同步。
未修（有意保留）：① curriculum 在确定性 toy 上收益有限——**已改为诚实输出**（"迁移收益有限，真实价值在高维任务"）；② DQN replay 在确定性环境收益小——**同上诚实标注**（replay 主场是 off-policy/随机环境）。二者是"教学诚实"而非缺陷。

### ❌ 误报澄清

- councillor P1-6"deepseek-harness 姊妹案例不存在"：经 `find` 复核**目录实存**（讲透Agent/Agent框架案例/deepseek-harness插件化框架/），本案 README 的 `../Agent框架案例/` 相对路径正确；但该检查顺带发现 **讲透Agent/README.md 两处真断链**（`../Agent框架案例/` 应为 `./Agent框架案例/`），本轮已顺手修复。

## 三、五维齐全度（v2 后）

| 维度 | v1 | v2 | 证据 |
|---|---|---|---|
| RL 技术清单（oracle 15 项）| 7 全+4 半 | **13 全+2 诚实半** | +DQN replay/target、DPO、熵正则、PPO-clip 近似、课程学习；缺 RLHF-RM（toy 下与 DPO 对照已示意）|
| Agent 技术映射 | 15/20 名实 | **24/24 名实** | 删虚构项；+SC/prompt 五模式/ROIF-CSE/APO/真 ReAct |
| Safety 五子系统 | 2/5 | **4.5/5** | Instructions(AGENTS.md+注入边界)/State(校验+原子写)/Verification(引用回查)/Scope(三预算)✓；Lifecycle 仍无回滚版本化（留观）|
| 性能 | 0.36s 无缓存 | **4.7s 含缓存+APO+SC+6 实验** | kb 缓存后单查 <1ms；增长来自新增实验非瓶颈 |
| 诚实边界 | bandit 声明 ✓ | **全链路** | GRPO/DQN/curriculum 三处"toy 局限"标注；反短路奖励；战报含设计内失败 |

## 四、定位句（采纳 councillor 判词，v2 修订版）

> 讲透Agent × 讲透RL × 讲透Prompt 的 716 行可跑缝合器——用 contextual bandit 内核 + prompt 先验 + APO 进化环，把三系列理论接成一件，30 秒在终端看见 ε-greedy、Reflexion、RLVR、reward hacking 的最小形态（以及它们如何被修掉）。

---
审查方法：4 专家并行委派（只读不改）+ 主 agent 数值复验（GRPO 三 seed 复现 + noise 扫描假说验证）；修复后全部经 demo 实跑回归。
