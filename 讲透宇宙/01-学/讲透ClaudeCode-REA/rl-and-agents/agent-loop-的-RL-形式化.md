# Agent Loop 的强化学习形式化 —— 以逆向出的 Claude Code 为参照系

> 本文把 Claude Code（v2.1.261，逆向实证）的 agent loop 放进 RL 理论框架：
> MDP/POMDP、bandit、credit assignment、reward 设计、RLHF/test-time compute 的关系。
> 目标：读完后你能（a）用 RL 语言精确描述任何 coding agent；（b）知道哪些部位可以
> 上 RL、哪些部位 RL 是错误工具；（c）对照 mini_claude.py 看每个抽象的落地。
> 标注约定：[S]=逆向源码实证，[T]=RL 理论，[I]=推断。

## 1. Agent Loop 是什么（实证版）

逆向还原的 Claude Code 主循环（细节见 ../02-agent-loop.md）可以压缩成：

```
state S_t = (system_prompt, CLAUDE.md, messages[0..t], 可用工具集)
loop:
    a_t ~ π_θ(· | S_t)          # LLM 采样：文本 token 或 tool_use 块
    if a_t 是文本且无 tool_use: 终止（end_turn）
    r_env = execute(tool_use)    # 工具在真实环境执行
    S_{t+1} = S_t ∪ {a_t, tool_result(r_env)}   # 上下文窗口更新
    if tokens(S_{t+1}) > threshold: S_{t+1} ← compact(S_{t+1})  # autocompact [S]
```

三层结构 [S]：**模型（π_θ）→ 工具层（环境转移核）→ 上下文窗口（状态载体）**。
上下文窗口既是 state 又是 memory——这是 agent 与经典 RL 环境最大的差异。

## 2. 形式化：POMDP 而非 MDP

**[T]** 一个 POMDP 是 `(S, A, T, R, Ω, O, γ)`：真实状态 S、动作 A、转移核 T、
奖励 R、观测函数 O: S→Ω、折扣 γ。

| POMDP 元素 | Claude Code 中的对应物 | 备注 |
|---|---|---|
| 真实状态 S | 整个文件系统 + 进程 + git + 外部世界的全部事实 | 不可完全观测 |
| 观测 Ω | 上下文窗口内容（历史 messages + 工具结果） | agent 只见 Ω 不见 S |
| 动作 A | {tool_use(工具,参数)} ∪ {文本回复} ∪ {end_turn} | 文本也是动作（影响用户） |
| 转移核 T | 工具执行：bash 改文件系统、read 返回文件切片 | **确定性为主**，网络/时间引入随机性 |
| 观测函数 O | 工具输出的**有损投影**：截断（20KB 限制 [S]）、行数上限、`grep` 只返回匹配行 | **有损是设计出来的**，见 §4 |
| 奖励 R | 无显式 reward（见 §5） | 用户目标隐式存在 |
| 折扣 γ | 上下文预算：每轮消耗 token，超额触发 compaction（信息丢失） | γ 的物理实现是"钱和窗口" |
| 策略 π_θ | LLM 本身（预训练+后训练出来的条件分布） | θ 冻结，运行时不更新 |

三个关键洞察：

**洞察 1：这是 POMDP 不是 MDP。** agent 从不看到真实状态，只看到观测历史。
`Read` 一个文件 ≠ 知道文件全貌——offset/limit、truncation、以及"文件在你读之后被改了"
都会让 agent 的信念偏离真实状态。Claude Code 的 file-state 跟踪（"file state is current
in your context"提示 [S]）就是在缓解 belief-state 漂移。

**洞察 2：转移核大部分是确定性的、且是"免费"的。** 经典 RL 里 T 未知需要学习；
这里 T 就是 bash/文件系统语义，可靠可得。**要学的是 π（选哪个动作），不是 T。**
这决定了 §6 的结论：agent 的 RL 化重点在策略层（LLM 后训练），不在模型层（学环境模型）。

**洞察 3：γ 的工程化身是上下文预算。** 折扣因子的本质是"未来信息的重要度衰减"。
Agent 的版本：上下文窗口有限 → 老信息被 compact 挤掉 → 相当于对远期历史打折。
`--autocompact <100k-1M>` [S] 就是在调 γ。

## 3. 单轮内部：结构化输出的 bandit 视角

一个 turn 内的并行工具调用（Claude Code 支持一轮多个 tool_use 块 [S]）是
**contextual bandit**：给定观测 x_t（当前上下文），从 K 个动作臂（工具×参数空间）
中选一个/几个，环境返回即时反馈（工具输出），没有跨轮的状态耦合——
因为每个工具调用本身不改变"哪个工具好"的长期统计。

**[T]** bandit 的探索-利用权衡在 prompt 层显式出现：Claude Code 的系统提示词
要求"先读后改、不要猜"（[S]，见 ../05-system-prompts.md）——这是在策略层
注入**信息价值导向的探索**（value of information）：读文件的即时 reward 为负
（花 token），但降低后续 Edit 失败率。VOI 最优的 agent 应当在
`E[信息增益] > E[执行成本]` 时才调用观测类工具。

**[I] 推论**：agent 的"过度调用 Read"与"过度自信直接 Edit"两种失败模式，
就是 bandit 意义上的过探索与过利用。调 temperature、换模型（5.3 vs 4.5-air）
实际在移动这条权衡曲线。

## 4. 观测函数的设计就是特征工程

**[S]** 逆向实证的有损观测点（每一处都是设计决策）：

| 观测点 | 有损方式 | 设计意图 |
|---|---|---|
| Read | 默认 2000 行上限；`cat -n` 行号格式 | 大文件分页，行号供 Edit 精确定位 |
| Bash 辥出 | 截断到 ~30KB，尾部保留 | 失败信息通常在尾部 |
| Grep | 匹配行数上限；`path:line:text` 格式 | 控制噪音，格式可被模型复用 |
| Edit 错误 | "not found / appears N times" 语义化错误 | 促使模型自纠（重 Read） |
| WebFetch | 抓全文后用小模型按 prompt 提炼 [S] | 上下文经济学：用便宜模型换 token |
| system-reminder | 结构化注入（file state、任务通知） | 不污染用户消息流的状态更新 |

**[T]** 这就是 POMDP 的观测函数设计 = RL 特征工程。Mini-claude 里你改一个
`TOOL_OUTPUT_LIMIT`，就是在重设 O。**Agent 性能的上限常常卡在 O 而不是 π**——
这就是"上下文工程 > prompt 工程"的理论表述。

## 5. Reward：不存在的函数与它的替身

Claude Code **没有显式 reward 函数** [S]。但训练与产品层面存在多层替身：

1. **用户反馈（显式稀疏 reward）**：`/bug`、thumbs up/down、SendFeedback 工具 [S]——
   1-bit 稀疏信号，噪声大、延迟大（整条轨迹结束后才来）。
2. **任务完成的代理信号（dense proxy）**：会话是否以成功 commit 结束、测试是否通过、
   用户是否继续追问（不满意的行为信号）[I]。
3. **遥测埋点（状态特征，非 reward）**：版本内嵌 statsig/OTel 事件 [S]——
   工具调用时序、重试、token 消耗是 trajectory log，喂给离线分析。

**[T] 为什么不能直接 RLHF 这个 loop？** 三个结构性困难：

- **Credit assignment**：一条 40 步轨迹只有 1 个 1-bit 反馈。第 7 步的 grep 模式
  写得好不好？方差大到无法归因。需要 process reward model（PRM）级别的逐步标注，
  或 MC/TD 折中。
- **Reward hacking 面**：reward = "用户点头" → agent 学会讨好而非正确；
  reward = "测试通过" → agent 学会改测试。任何 proxy 都会被优化压力腐蚀
  （Goodhart）。数学发现系统的账本经验（novelty 通胀）同构。
- **非平稳环境**：文件系统、依赖、用户意图都在轨迹中途变化，return 的分布漂移。

**[T] 业界实际路线**（截至 2026）：不走在线 RL，走**离线后训练**：
SFT on 精选轨迹（ReACT 格式的 tool-use 轨迹）→ 拒绝采样（best-of-N 筛选）→
在可验证环境（单测可判定的 coding 任务）上做 RLVR（RL with Verifiable Rewards）。
可验证 = reward 从"人嘴"换成"机器可判定的谓词"，Goodhart 面收窄。
Claude 模型的 tool-use 能力即此路线产物 [I]。

## 6. 什么值得上 RL，什么不值得（决策表）

| 部位 | RL 化价值 | 理由 |
|---|---|---|
| LLM 本体（π_θ） | ★★★★★ | 但这是模型厂商的事：RLVR/SFT 后训练 |
| **模型/路由选择**（5.3 vs flash vs 4.5-air） | ★★★★ | 纯 contextual bandit，状态=任务特征，臂=模型，reward=成本×质量。你的 hpc-agent T0-T4 五级路由就是这个 [I] |
| **工具选择时机**（何时 Read 何时直接改） | ★★★ | 需要轨迹级标注；先用 prompt 规则顶住 |
| **上下文管理策略**（compact 时机、保什么丢什么） | ★★★ | 状态空间清晰（窗口内容），reward=后续任务成功率；Claude Code 用规则 heuristic [S]，是可学习空区 |
| **Bash 命令生成** | ★★ | 安全敏感、非法动作多；蒸馏+规则更稳 |
| **观测函数**（截断策略、格式） | ★★ | 离散设计空间小，A/B 实验即可，不需要 RL |

**[T] bandit 是 agent 工程师真正用得上的 RL**：单步决策、反馈快、无 credit
assignment 疼痛。LinUCB / Thompson Sampling / ε-greedy 都能在几百次交互内
收敛出"哪类任务该路由到哪个模型"。多步 RL（PPO 一类）在 agent 外围系统里
几乎总是过度设计。

## 7. Test-time compute：没有梯度上升的搜索

**[T]** Agent 的"多跑几遍挑最好"= 测试时搜索，与 RL 的关系是把
`argmax` 换成 `sample × k`：

- **best-of-N 轨迹**：N 次 rollouts，用可验证判据（测试通过 [S]——Claude Code
  会真的跑测试）选优。等价于一次性 policy 改进的拒绝采样。
- **子代理并行**（Task 工具 fan-out [S]）：把同一问题的不同侧面分给独立
  POMDP（互不共享观测），主 agent 做信息融合。这是**观测分治**，不是集成。
- **计划-执行分离**（EnterPlanMode [S]）：先在抽象空间（计划）搜索，再在
  具体空间执行——缩小动作空间的有效搜索方法。
- **CronCreate/ScheduleWakeup 自主循环**（[S]）：把 agent 自己变成环境的一部分
  （自己给自己发观测），是 poor man's 的 self-play。

## 8. 对照 mini_claude.py：每个 RL 概念的落点

```
mini_claude.py                    RL 概念
─────────────────────────────────────────────────────────
messages 列表                     belief state b_t（观测历史）
SYSTEM_PROMPT + CLAUDE.md          先验 / 指令条件（in-context policy shaping）
chat(messages, TOOLS)              π_θ(a|b)：策略网络前向（θ 冻结）
tool_use 执行                      环境转移 T + 观测 O（截断=有损投影）
"(continue)" 占位                  轮间衔接（Anthropic 原生协议里是 tool_result 回填）
est_tokens > CONTEXT_BUDGET        γ 的显式检查
compact(messages)                  belief 压缩（信息丢弃点 = RL 的 abstraction）
max_turns                          轨迹截断（horizon）
Bash 黑名单/白名单                 非法动作掩码 action masking
🔧 打印的轨迹                      trajectory log（离线 RL 的数据源）
```

**给 mini-claude 加 RL 的最短路径**（练习设计）：
1. 在 run_agent 里记录 `(task_hash, tool_seq, 成功?, token_cost)` 转出 JSONL——
   这是 bandit 数据集；
2. 模型选择改成查表：`model = argmax_q[task_class]`，q 用 ε-greedy 更新；
3. compact 策略从"保最近 6 轮"改为"保 todo 状态+最近 3 轮+最老 1 轮"，A/B 对比
   任务成功率——这就是上下文管理的在线实验。

## 9. 一页总结

- Agent loop = **POMDP**：上下文窗口是 belief state，工具是有损观测，γ 是 token 预算。
- **要学的是策略不是环境**：转移核是免费的（bash 语义），观测函数是设计出来的。
- **没有显式 reward**：用户反馈太稀疏，可验证判据（测试）才是可用信号。
- **工程上最实用的 RL 是 contextual bandit**（模型路由）；多步 RL 留给模型厂商的 RLVR。
- **test-time compute 是无梯度的搜索**：best-of-N、子代理分治、计划先行。
- 改 agent 性能的杠杆排序：**观测函数（上下文工程） > 策略（换模型/后训练） > 搜索（多跑几遍）**。

## 延伸阅读（理论源流）

- POMDP：Kaelbling, Littman & Cassandra (1998), *Planning and acting in partially observable stochastic domains*
- Bandit：Lattimore & Szepesvári (2020), *Bandit Algorithms*（免费版）
- RLHF：Christiano et al. (2017)；RLVR/可验证奖励：openai/gym → 2024 后 coding-agent 后训练主流
- ReAct：Yao et al. (2022)——tool-use 轨迹格式的原型
- Process reward：Lightman et al. (2023) *Let's Verify Step by Step*——解决 credit assignment 的 PRM 路线
- Agent 上下文经济学：Anthropic 工程博客 *Building effective agents*（2024-12）与 *Managing context* 系列

---
配套实现 → [mini_claude.py](mini_claude.py) · 构建指南 → [build-guide.md](build-guide.md)
