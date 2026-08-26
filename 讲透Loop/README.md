# 讲透 Loop：让 Agent 转起来的循环设计学（Loop Engineering）

> 知识卡宇宙：`讲透X` 系列 | 三层宪法：**直觉 → 公式 → 代码（bash 跑通）** | 五幕：直觉→数学→代码→不足→应用
> 定位：三部曲**终章**——`讲透Prompt/` 研究**单次调用一句话怎么写**，`讲透Context/` 研究**每次调用窗口里放什么**，本单元研究**跨调用的循环怎么设计**：谁触发、怎么验证、何时停、状态放哪、怎么叠。
> 🌱 2026-08-26 谱系升级：loop = 最简单的有向**环**图（LangChain 原话），本单元现由 `讲透Graph/` 收口为五环谱系（Prompt→Context→Harness→Loop→Graph，arXiv 2608.21156）的第四环。
> 本章证据标准：每个知识点配一个可跑实验（`experiments/`），前沿全部一手核实（`papers.md`）。

## 为什么要有这个单元（2026-08-26 建）

**Loop Engineering 是 2026 年 6 月才被命名的新学科**——Addy Osmani 2026-06-07 的博客把它从"跑个 while true 的民间技巧"提升为命名学科，比 Context Engineering（Anthropic 2025 命名）还年轻。定义（Osmani）：

> "Loop engineering is replacing yourself as the person who prompts the agent. You design the system that does it instead."（循环工程就是把你从"给 agent 打 prompt 的人"这个岗位上替换下来——你去设计那个替你打 prompt 的系统。）

四层堆栈（学术定版，arXiv:2607.00038 / 2608.21884）：

```
L3  Loop Engineering     谁触发运行、怎么验证结果、何时停、状态存哪      ← 本单元
L2  Harness Engineering  单次 agent run 的环境（工具/钩子/skills）        ← 讲透Agent/讲透Skills
L1  Context Engineering  模型每轮看到什么（策展/压缩/记忆）              ← 讲透Context
L0  Prompt Engineering   单次调用怎么问                                  ← 讲透Prompt
```

本单元的三个增量：

1. **一手实证化**：两篇学术论文刚落地——arXiv:2607.00038（loop specification 解剖 + Loop Library 50 个真实 loop 人工编码）与 arXiv:2608.21884（36,710 仓挖掘，仅 0.59% 真跑 loop、几乎无人提交 state file）——全部读原文，不转述二手；
2. **循环动力学实验**：本单元实验线的核心不是"再跑一个真 LLM"，而是**行为模拟器**——循环的成本/停止/收敛是确定性数学，模拟器能精确控制参数（自评偏差、验证器漏检率、停滞概率）做消融，这是真小模型给不了的（0.5B 在循环任务上退化为噪声，项目已知教训）；
3. **活案例独家**：本仓库自己就是 loop engineering 现场——MATH_LOOP_ENGINE（七阶段循环 + 五类机器可判 reward + Wave BFS）= goal loop + 验证阶梯的活体；Prover harness（提议→Lean 验证→专家迭代）= AlphaProof 同构闭环；opencode 的 auto_continue / delegation / 定时任务 = loop primitives。

## 核心心智模型（一图流）

```
   ┌────────────────────── 外循环（本单元的主对象）──────────────────────┐
   │  触发 Trigger          验证 Verify          停止 Stop               │
   │  heartbeat/cron/  →    maker≠checker   →    机器可查条件            │
   │  hook/goal             五级验证阶梯          + hard cap + 熔断       │
   │        ▲                                           │               │
   │        │            状态 State（循环的脊椎）        │               │
   │        └────────────  state file：读帧→写验·事实非vibes·resume点 ◀─┘  │
   └───────────────────────────┬────────────────────────────────────────┘
                               ▼ 包住
   ┌────────────────────── 内循环（harness 自带）────────────────────────┐
   │   while not done: perceive → reason → plan → act → observe          │
   └───────────────────────────┬────────────────────────────────────────┘
                               ▼ 包住
         LLM 单次调用（prompt ✓ context ✓ —— 前两部曲已讲透）
```

三句话记住本单元：
1. **循环里唯一不能省的是"查"**——中央技能是 verification，不是 prompting（2607.00038 结论）；
2. **停止条件必须机器可查**——"看起来完成了"是判断，"测试绿"才是条件；模型对自己的完成度系统性过度自信；
3. **写循环的是工程师，不是按钮员**——同一个 loop，理解工作的人用来加速，逃避理解的人用来慢性自杀（Osmani 收尾）。

## 篇目表（目录宪法）

| # | 章节 | 核心实验 | 状态 |
|---|------|---------|------|
| 00 | 开场白：从 Prompt 到 Context 到 Loop——控制权的三次上交 | — | ✅ |
| 01 | 内循环解剖：Agent Loop 就是 while not done | E1 内循环最小实现 ✅ | ✅ |
| 02 | ★ 循环规格五件套：trigger/goal/verification/stopping/memory | Loop Library 50-loop 数据复述 | ✅ |
| 03 | ★ 验证的阶梯：maker-checker 分离与五级验证 | E2 停止条件三守卫对比 ✅ | ✅ |
| 04 | 四种循环形状：Heartbeat/Cron/Hook/Goal | E3 形状×成本×事故模拟 ✅ | ✅ |
| 05 | ★ 三大守卫：hard cap / 机器可查条件 / 独立验证 | 并入 E2/E3 | ✅ |
| 06 | 外部状态：state file 是循环的脊椎 | state 协议设计 | ✅ |
| 07 | ★ 循环堆叠 loopcraft：从 agent loop 到 hill climbing | E4 外环改内环最小闭环 ✅ | ✅ |
| 08 | ★ 自改进循环与 RSI 悬崖：A_{t+1}=IMPROVE(A_t; S_t) | 文献综合（2607.13104/2607.07663） | ✅ |
| 09 | 数学下场：循环即算子（不动点/收敛/同构族） | E5 收敛条件数值演示 ✅ | ✅ |
| 10 | ★ 活案例：本仓库就是 Loop Engineering 现场 | 现场分析 | ✅ |
| 11 | 不足与批判：成本曲线/comprehension debt/认知投降 | — | ✅ |
| 12 | 循环设计清单 + 三部曲总纲 | Checklist | ✅ |

★ = 用户重点主题（循环规格/验证阶梯/守卫/堆叠/RSI 边界/活案例）。
**完成态（2026-08-26）**：00-12 章 + E1-E5 五实验全跑通 + papers.md 全核实（4 arXiv + 7 灰色一手）。十条定律全数值验证（87.3% 早停 / p<ε/T / 1/p_leak / 5.7 倍 / Goodhart 剪刀差 / e*=f/(r+f)…见 12 章速查表）。断点期权见 `RESUME-0826.md` §四。

## 实验环境与设计决策

- **行为模拟器优先**：循环级动力学（成本累积、停止时点、停滞检测）用参数化模拟器做消融——控制变量精确、可复现、不依赖 GPU。真模型实验线在三部曲姊妹篇（讲透Context E6）与本单元 E5（外环闭环）。
- **铁律**：①实验独立可跑（`python experiments/XX_*.py`）②结果存 json+png ③matplotlib 中文字体 Noto Sans CJK SC ④模拟器参数全部显式写在结果 json 里 ⑤arXiv ID 全部核实（见 `papers.md`）。

## 与姊妹篇的分工（互不重复）

| 问题 | 讲透Prompt | 讲透Context | 讲透Loop |
|------|-----------|-------------|----------|
| 研究对象 | 单条 prompt 的措辞 | 整个窗口的信息构成 | 跨运行的控制结构 |
| 典型技巧 | CoT/few-shot/ToT | compaction/memory/sub-agent | trigger/verifier/stop/state/堆叠 |
| 失败模式 | 注入/敏感性 | Context Rot/压缩失真 | 失控烧钱/早停/状态失忆/验证自欺 |
| 数学接口 | OPRO 优化循环 | 通信复杂度/Bloom | 不动点迭代/验证层级/成本模型 |
| 时间尺度 | 单次调用 | 单次 run 内 | 多 run 之间 |

## 挂网（本单元的桥）

- 上游：`../讲透Prompt/`（07-ReAct 是内循环的 prompt 侧起源）、`../讲透Context/`（state file = 窗口外记忆的循环版）
- 下游：`../讲透Agent/`（harness 是循环的 L2 内件；`讲透Agent/讲透Skills/` 的 skills 是循环的构建块）、`../讲透Agent/实战案例-Prover数学Agent/`（提议-验证闭环活体）
- 横向：`../top-math-courses/MATH_LOOP_ENGINE.md`（Ch10 活案例的主角）、`../讲透强化学习RL/`（loop = RL episode 的工程化表亲）

## 来源与核实

- 学术：arXiv:2607.00038 / 2608.21884 / 2607.13104 / 2607.07663（全部 websearch 直抓 HTML 全文核实，2026-08-26；arxiv.org abs 页当日网络不通，已用 arXiv 官方列表页交叉确认 2608.21884 在 2026-08-25 cs.SE 提交）
- 灰色文献：Osmani 命名文（2026-06-07/08）、LangChain（2026-06-16）、DataScienceDojo（2026-06-24）、vibeengines handbook（2026-07-16）等 7 篇，逐条核实状态见 `papers.md`
