# 00 · 开场白：从 Prompt 到 Context 到 Loop——控制权的三次上交

> 讲透Loop 第 0 章 | 三层宪法：直觉 → 数学 → 代码 | 前置：讲透Prompt 00、讲透Context 00（不强制）

## 一、直觉层：一句话说清这门学科

**Loop Engineering = 设计"替你给 agent 打 prompt 的系统"，而不是自己给 agent 打 prompt。**（Osmani 2026-06-07 命名文的原话："Loop engineering is replacing yourself as the person who prompts the agent. You design the system that does it instead."）

为什么需要它？看你过去三个月干的事：

- 每天早上打开 opencode，说"继续讲透X"——这是**你在当循环的调度器**；
- 跑完一个实验，肉眼看结果对不对——这是**你在当循环的验证器**；
- 感觉"差不多了"就停——这是**你在当循环的停止条件**（而且是靠直觉的那种，最不可靠的一种）。

三个角色你都是人工的。Loop Engineering 说：把这三个角色**写成系统**——cron 触发、独立 verifier 判卷、机器可查条件叫停、state file 记账。然后你去睡觉。

## 二、命名史：一门三周岁的学科（按月记龄）

```
2023-2024  Prompt Engineering 全盛    —— "会问就会赢"
2025       Anthropic 命名 Context Eng —— 单次 run 内的信息策展
2025-09-30 Simon Willison "Designing agentic loops" —— 民间版（一年后它成了引用源头）
2026-06-07 Addy Osmani《Loop Engineering》—— 命名学科，五构建块+记忆
2026-06-16 LangChain 四层循环堆叠     —— loopcraft，产品化
2026-06-24 DataScienceDojo 10 模式    —— 模式语言成型
2026-07   学术下场：2607.00038（loop specification + 50-loop 语料）
           2608.21884（36,710 仓实证：0.59% 采用率）—— 8 月 25 日才提交！
```

注意这个时间线的含义：**你学这门学科时，它比大多数本科课程都年轻**。好处是没人比你早多少；坏处是课本会过时，必须盯一手（本单元 papers.md 就是干这个的）。

## 三、四层堆栈：Loop 在哪一层

```
L3  Loop Engineering      跨 run 的控制结构：触发/验证/停止/状态/堆叠
L2  Harness Engineering   单次 run 的环境：工具/钩子/skills/sub-agents
L1  Context Engineering   每轮窗口里放什么：策展/压缩/记忆/隔离
L0  Prompt Engineering    单次调用怎么问：CoT/few-shot/结构化
```

三层递进的逻辑是**控制权的三次上交**：

1. **第一次上交（L0→L1）**：你不再逐句雕琢 prompt，而是把"模型该知道的一切"当作策展问题——窗口是预算，token 是弹药；
2. **第二次上交（L1→L2）**：你不再手排每轮上下文，而是设计 harness（工具+skills+钩子）让 agent 在一次 run 内自己走；
3. **第三次上交（L2→L3，本单元）**：你不再守着单次 run，而是设计循环——**谁按下的启动键、谁判卷、谁喊停、账本在哪**。

每次上交都不是"退休"，是杠杆转移：Osmani 转述 Boris Cherny 的话——"不是工作变简单了，是杠杆点移动了"（the leverage point moved）。

## 四、内循环 vs 外循环：先把词掰开

这门学科最容易混的三个"循环"（2607.00038 专门用一节区分，这是全学科的地基）：

| 对象 | 是什么 | 谁负责 | 本单元位置 |
|------|--------|--------|-----------|
| **编程循环** | `for`/`while` 语句 | 你，程序员 | 不是研究对象（只是实现材料） |
| **内循环**（agent loop） | harness 自带的 perceive→reason→plan→act→observe 圈 | 工具厂商 | Ch01 解剖，之后当"黑盒内件" |
| **外循环**（the loop） | 触发→验证→停止→记账，跨 run 反复 | **你，循环工程师** | 本单元主体 |

一句话：**内循环是 plumbing（管道），外循环才是设计对象**。你买来的 agent 已经会转内循环；Loop Engineering 问的是这个内循环该什么时候被谁点燃、烧多久、怎么验收。

## 五、为什么"验证"是全学科的中心

三个独立来源在 2026 年 6-8 月收敛到同一个结论：

1. **实践侧**（Osmani）：verifier sub-agent 是"你能走开的唯一理由"——/goal 的实现就是让一个 fresh model（不是干活那个）判卷；
2. **模式侧**（DataScienceDojo 10 模式）：生产故障大多来自跳过 8-10 号模式（熔断/心跳锁/有界执行），而这三者全是"验证与止损"的变体；
3. **学术侧**（2607.00038 对 50 个真实 loop 的编码）：实践在验证上最成熟（70% 自主验证、74% 命名终态），在自治上最幼稚（22% 自动触发、32% 持久记忆）——**"怎么知道做完了"解决得远好于"怎么没人也能跑"**。

而验证的核心公理只有一条：**写代码的模型不能给自己的代码判卷**（maker ≠ checker）。这跟你 review 自己 PR 的利益冲突同构，只不过模型"失败得更可靠"（Osmani）。

更深一层是**验证层级**（2607.07663，1,250 篇综述的结论）：formal verifier（Lean/测试）> 外部工具 > 判官模型 > 过程奖励 > 内在自评。自改进的强度沿这个阶梯排列，失败模式（自我确认循环、模型塌缩）恰是违反层级的后果——**你的循环能自治到什么程度，取决于你的验证器强到什么程度**（aipatternbook："autonomy is capped by verification reach"）。

本仓库的活证据：MATH_LOOP_ENGINE 把 reward 定为五类**全机器可判**信号（Lean 0-sorry / SymPy 恒等 / 数值阈值 / OEIS 命中 / 超 dummy）——这正是验证阶梯的顶层配置。你已经在顶层实践了，只是没用这个名字。

## 六、数学层预告：循环即算子

先把最核心的一个公式放这（Ch08/Ch09 展开）：

$$\mathcal{A}_{t+1} = \mathrm{IMPROVE}(\mathcal{A}_{1:t};\ \mathcal{S}_t)$$

把 agent 系统看作配置 $\mathcal{A}$（基础模型 + prompt + memory + 工具 + 控制逻辑），每轮循环接收信号 $\mathcal{S}_t$（测试结果/判官反馈/环境回报），由改进算子 IMPROVE 产出新配置。这个框架统一了：

- **Ralph Loop**：$\mathcal{S}_t$ = 测试输出，IMPROVE = 改代码直到绿——不动点就是"测试全绿"；
- **RL**：$\mathcal{S}_t$ = 奖励，IMPROVE = 策略梯度——循环的连续化；
- **AlphaProof/你的 Prover harness**：$\mathcal{S}_t$ = Lean 验证结果，IMPROVE = 提议-分解-再试；
- **hill climbing**：IMPROVE 作用在 harness 配置而非任务产物上——外环改内环。

数学层问的老三样：**这个算子有不动点吗？迭代收敛吗？收敛到的是你要的那个点吗？**（第三个问题最难——reward hacking 的全部故事就是"收敛到了你没想要的点"。）

## 七、代码层预告：两个最小的"啊哈"

**啊哈 1——最小内循环**（Ch01 完整版）：

```python
while not done:
    action  = agent.decide(observation)   # 内循环的"转"
    observation = env.execute(action)      # 世界给出反馈
    done = stop_condition(observation)     # ← Loop Engineering 全部押在这一行
```

前三行 harness 送你；**这门学科只研究第四行，以及第四行外面包着的一切**。

**啊哈 2——为什么"看起来完成了"不算停止条件**（E2 实验将量化）：设模型对未完成任务自报"完成"的概率为 $p_{\text{早停}}$，每轮 token 成本 $c$，则：

$$\mathbb{E}[\text{ wasted tokens }] = \frac{p_{\text{早停}}}{1-p_{\text{早停}}} \times c \times (\text{剩余工作量})$$

自评停止把 $p_{\text{早停}}$ 完全交给模型的过度自信；机器可查条件把它压到验证器的漏检率。**停止策略的差 = 烧钱速度的差**——这不是比喻，是 E2 模拟器要画的曲线。

## 八、本单元的学习承诺

学完这个单元，你应该能：

1. 拿到任何"让 agent 自动干活"的需求，先画出**四形状卡**（heartbeat/cron/hook/goal 里选触发×停止组合）而不是先写 prompt；
2. 给任何循环装上**三守卫**（hard cap / 机器可查条件 / 独立验证），并说明缺哪守卫会怎么死；
3. 把 MATH_LOOP_ENGINE、Prover harness、opencode 的 auto_continue **读成循环规格**（五件套），并能指出它们的验证层级位置；
4. 对"自改进 agent"的宣传保持数学冷静：说出 bounded self-refinement 与 open-ended RSI 的边界，以及为什么验证层级决定自改上限。

## 九、批判收尾（先泼三盆冷水）

1. **成本无 ROI 研究**（Willison 警告，2607.00038 引用）：goal loop 无上限一小时能烧几百美元且零进展；heartbeat + verifier sub-agent = 每小时几十次模型调用，不管有没有活干。循环把一切它碰到的东西相乘——**包括你的账单**；
2. **满足 gate ≠ 满足 goal**（Lindenberg 警告，2608.21884 转述）：循环满足的是你写的那个 gate，不是 gate 背后的意图。测试绿了不等于重构对了——你写的停止条件错一个字，循环就"成功"地收敛到错误的地方；
3. **认知投降风险**（2607.00038 的 limits 节）：同一个 loop，理解工作的人用来加速，逃避理解的人用来慢性放弃理解——"the loop doesn't know the difference. You do."（Osmani）。还有 2608.21884 的硬数据：36,710 仓里只有 0.59% 真跑循环、只有 2 个合格 state file——**这门学科的宣传声量与真实采用率之间差着两个数量级**。

---

## 📌 下一步

- 读 01 章：内循环解剖（E1 已跑通，`experiments/01_min_inner_loop.py`）
- 或直接跳 03 章：验证的阶梯（本单元的心脏，E2 三守卫对比）
- 前沿速览：`papers.md`（4 篇 arXiv + 7 篇灰色文献，全部一手核实）

## ✍️ 练习（10 分钟）

1. 把你最近一次"用 opencode 干活"的过程写成循环规格五件套：trigger 是什么（你手动？）、goal 是什么、谁验证的（你自己肉眼？）、停止条件是什么（感觉差不多？）、状态记在哪（对话里=没记）。哪一件最弱？
2. 找出你工作流里三个"你在人工当循环部件"的角色（调度器/验证器/停止条件），各写一句：怎么把它变成机器可查的？
3. 思考题：MATH_LOOP_ENGINE 的七阶段循环里，"④观察：跑出数字/build 通过才算观察"对应验证阶梯的哪一级？为什么"⑤反思产出的新锚点卡"反而**不能**全靠机器验证？（答案方向：观察=形式验证，反思产出=需要人判断方向性——这正是"研究方向的设定留在人手里"的 RSI 瓶颈。）
