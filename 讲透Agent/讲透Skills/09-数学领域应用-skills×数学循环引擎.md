# 09 — 数学领域应用：skills × 数学循环引擎

> 「讲透 Skills」第十篇 ★（用户五问之五：**最后的最后，应用在数学领域上**）。本仓已有最厚的数学资产（MATH_LOOP_ENGINE / 讲透Lean4数学 / top-math-courses / oprover-math skill）——本章做三件事：①把数学工作流 skills 化的具体蓝图；②设计数学领域独有的 skill 类型学；③用 08 章的自动化研究把"数学循环引擎"升级为自进化系统。

---

## 1. 为什么数学是 skills 的最佳应用域

对照 skill 的本质（[00](00-什么是Skills-从咒语到技能包.md)：程序性知识的外置包），数学工作的四个特征完美匹配：

```
数学工作特征                    skills 特性                    匹配点
─────────────────────         ─────────────────────         ─────────
证明有客观对错(0 sorry)    ←→  eval 集可完全自动化         五类 reward 信号现成
(Lean/SageMath 可机器验证)      (Lean build 通过 = 通过)      (MATH_LOOP_ENGINE)
方法论高度程式化              ←→  SKILL.md = 程序性知识包    Polya/Tao 方法论
(先猜后证/特例先行/             (就是"怎么做事"的编码)        本身就是技能清单
 逆问题/类比迁移)
领域分叉极细                  ←→  渐进披露按需加载           63 个 MSC 领域
(数论≠泛函≠代数几何)            (学数论时不装代数拓扑的正文)   不互相挤占上下文
工具链确定性强                ←→  scripts/ 卸载确定性        lake build/SageMath/
(Lean/Sage/OEIS/LMFDB)          (LLM 只决定何时调)            OEIS API 全是脚本活
```

最后一条是关键：**数学的验证环节几乎全是确定性计算**——Lean 编译、SageMath 恒等式、OEIS 命中、数值阈值——这些进 `scripts/`，LLM 的角色收敛到"猜想生成 + 策略选择 + 证明骨架"，这正是当前 LLM 在数学上最被低估的用法（MATH_LOOP_ENGINE 的核心洞察）。

## 2. 数学 skill 类型学（五型）

基于 MATH_LOOP_ENGINE 的五生成规则与七阶段循环，数学 skills 应分五型：

| 型 | 内容 | 触发时机 | 例子 | scripts 搭档 |
|---|---|---|---|---|
| **方法论型** | Polya 式启发式（理解题→拟计划→执行→回顾） | 任何问题求解开始时 | `olympiad-problem-solving`（R2 叠加：先证弱版再加强） | — |
| **领域战术型** | 特定领域的标准武器库 | 领域识别后 | `inequality-tactics`（放缩方向/Cauchy 时机/取等条件检查清单） | Sage 生成随机例验证不等式方向 |
| **工具链型** | 某工具的正确用法与坑 | 需要调用工具时 | `lean4-tactics`（何时用 simp vs omega vs ring_nf；常见 sorry 消灭路径） | `lake build` 封装 + 错误解析 |
| **验证型** | 证明义务与检查清单 | 声称证明完成前 | `proof-obligations`（每个放缩标注依据引理；极限步骤给 ε 的显式选取） | Lean 端到端 0 sorry 检查 |
| **元循环型** | 循环引擎本身的操作规程 | 每轮反思阶段 | `math-loop-reflection`（R1 公理反问/R4 逆问题生成的具体话术） | coverage 仪表盘更新 |

**现有资产对号入座**：本机 `oprover-math` skill（逆向蒸馏 DeepSeek-Prover-V2）= 工具链型+方法论型混合；MATH_LOOP_ENGINE 的五 reward 信号 = 验证型的 eval 协议；`math-learning`/`ml-theory` 等本机 skill = 领域战术型的雏形（但还没有 scripts/ 层）。

## 3. 落地蓝图：三个真 skill 的完整设计

### 3.1 `basel-problem`（方法论型——以 Basel 问题为例的可复用攻坚流程）

```
basel-problem/
├── SKILL.md
│   ---
│   name: basel-problem
│   description: Systematic attack workflow for evaluating hard infinite
│     series (Basel-type problems). Use when the user asks to compute,
│     bound, or prove identities for series like Σ1/n², or when a series
│     resists direct summation. Not for telescoping series (direct method).
│   ---
│   # 硬级数攻坚工作流（五路并进）
│   1. 数值先行: scripts/numerical_probe.py 高精度求和, OEIS 反查闭式候选
│   2. 猜闭式: 数值→PSLQ 整数关系→猜想
│   3. 多路线字典（按命中顺序尝试, 见 references/roads.md）:
│      Euler 乘积sin展开 / Fourier 级数 / 双重积分 / 复分析留数 / 组合证明
│   4. 证明义务: 每步交换求和号需一致收敛论证; 截断误差显式估计
│   5. 反思钩子: R4 逆问题——把结果改造成新问题(ζ(4)? 交错版?)
├── scripts/
│   └── numerical_probe.py     # mpmath 高精度 + PSRQ + OEIS 查询
└── references/
    ├── roads.md                # 五条路线的完整推导（各<300行, 带目录）
    └── generalizations.md      # ζ(2k)/交错/Apéry——R2 叠加的素材库
```

### 3.2 `lean-sorry-hunter`（工具链+验证型——消灭 sorry 的战术手册）

```
lean-sorry-hunter/
├── SKILL.md
│   ---
│   name: lean-sorry-hunter
│   description: Tactics for eliminating 'sorry' in Lean 4 proofs and
│     debugging failed builds. Use when lake build reports sorry or
│     errors like 'motive is not type correct', or when a tactic
│     (simp/omega/ring_nf) unexpectedly fails. Also use for deciding
│     WHICH tactic to try first for a goal shape.
│   ---
│   # sorry 猎人决策树
│   1. 目标形状 → 首选 tactic 速查:
│      线性算术目标 → omega | 环恒等式 → ring_nf
│      定义展开 → simp [def] | 存在目标 → ⟨witness, proof⟩ 先猜 witness
│      归纳结构 → induction n with | zero | succ  (先写骨架!)
│   2. 卡住超过3次 → 走 references/motives.md 查 motive 错误
│   3. 证明完成后必跑: scripts/check_zero_sorry.sh（0 sorry 硬门）
│   4. 忌讳: 不要用 native_decide 蒙混(不可移植); 不要 set_option maxHeartbeats 无脑调大
├── scripts/
│   └── check_zero_sorry.sh     # lake build + grep sorry = 0 的封装
└── references/
    ├── motives.md               # motive is not type correct 专题
    └── tactic_families.md       # 十大 tactic 族的选用矩阵
```

> 这个 skill 直接蒸馏自本仓 Prover 数学 Agent 的实战教训（REBUILD-服务器迁移.md 的三坑 + e1 failed@decompose 的归因）——**失败日志是数学 skill 的第一手素材**（SkillClaw 的轨迹挖掘思路）。

### 3.3 `math-loop-driver`（元循环型——循环引擎的操作界面）

把 MATH_LOOP_ENGINE.md 的七阶段循环 + 五 reward + coverage 仪表盘压缩成一个可触发的操作规程：每轮"理论→计划→实践→观察→反思"结束后，reflection 阶段强制走 R1-R5 生成规则产出一个新锚点卡（ANCHOR_CARDS 格式），verified 条件直接绑定五类 reward 信号（Lean build/Sage 恒等/数值阈值/OEIS 命中/超 dummy）。**这把"引擎文档"变成"引擎技能"——从人读的说明书变成 agent 可加载的操作程序**。

> ### ✅ 三个蓝图已建成并实测（2026-08-25，同日）
>
> 三个 skill 已真实落地在 [`.opencode/skills/`](../../../.opencode/skills/)（项目级，opencode 自动发现）：
>
> | skill | 验证证据 |
> |---|---|
> | `basel-problem` | `numerical_probe.py` 真跑：ζ(2)→π²/6（残差 5e-41）、ζ(4)→π⁴/90（2.5e-40）锁定；references/roads.md 五路线含失败模式 |
> | `lean-sorry-hunter` | `check_zero_sorry.sh` 三用例真测三轮迭代（v1 grep 误报块注释中文"sorry" → v3 awk 状态机剥离行/嵌套块注释，正例 Wave0 exit=0、反例只报真 sorry）；本仓 `loops/lean` lake build ✔ 0 sorry |
> | `math-loop-driver` | R1-R5/七阶段/五 reward 协议 + 跨 skill 路由（lean-sorry-hunter/basel-problem/concept-3layer/paper-mastery） |
>
> 三 skill 均过 [E3](../experiments/03_spec_validator.py) 全绿（description 压到 ≤250 字符按 CC 截断线写，near-miss 反例保留）。

## 4. 自动化闭环：数学版 run_loop（08 章研究的落地）

数学域的独特优势让 skill 自动优化比通用域**更可行**——因为 eval 全自动：

```
数学 skill 自动优化循环（MCE 思想 + 数学 reward）
┌──────────────────────────────────────────────────┐
│ ① 造卷: 从锚点卡/练习题库出题（Lean 可判/数值可判）  │
│ ② 双跑: with-skill vs baseline（同题并行）          │
│ ③ 判分: 五类 reward 全自动（0 sorry / 误差阈值 /     │
│         OEIS 命中）——零人工评分                    │
│ ④ 归因: 失败分类→证明卡在哪步→战术字典哪条没覆盖     │
│ ⑤ 进化: 按 MCE agentic crossover——成功/失败轨迹    │
│         杂交出新战术条目; Mcnemar 判显著            │
│ ⑥ 回写: 新条目进 references/, description 按触发    │
│         失败样本重写（03章协议）                     │
└──────────────────────────────────────────────────┘
```

对照 08 章六条研究线：这个循环 = SkillRL 的经验蒸馏（成功轨迹→演示、失败→教训）+ MemSkill 的 designer（hard case 挖掘）+ 官方 run_loop（trigger eval）——**但判分环节全部换成数学的机器可验证 reward**，是全部研究里"人工最少"的优化域。这也是数学循环引擎 Wave 1+ 的自然扩展：锚点卡 verified 的副产物（解题轨迹）直接喂给 ⑤。

## 5. 与现有数学资产的挂网图

```
top-math-courses/MATH_LOOP_ENGINE.md ──── math-loop-driver skill 化 ←─ 本章
        │                                      │
        ├─ ANCHOR_CARDS_30 (30卡)         ② 造卷素材
        ├─ loops/lean/ (v4.21)            lean-sorry-hunter 的 scripts 环境
        └─ 五类 reward 信号                ③ 判分协议
讲透Lean4数学/ ──────────────────── lean-sorry-hunter 的 references 素材
oprover-math skill（已装） ──────── 工具链型先例, DeepSeek-Prover 蒸馏
讲透Agent/实战案例-Prover数学Agent ── 失败日志 = 轨迹蒸馏素材
数学家资源中心 AI_FOR_MATH_TOOLS ─── AlphaProof/LeanDojo 生态对照
```

## 6. 诚实边界

1. **skills 放大的是流程纪律，不是数学天赋**。猜想质量仍由模型（或人）决定——skill 保证的是"该试的路都试到、该验的步都验到"。
2. **Lean 侧 skill 的宿主要求高**：触发它的 agent 需要有 shell（跑 lake build）——纯聊天界面里工具链型 skill 退化成建议文本。
3. **循环引擎的自动优化目前是设计而非实测**：本章 §4 是蓝图，落地需要先跑通 Wave 1 的锚点积累（当前 6/30 verified）——顺序应是先攒轨迹数据，再谈进化。

## ✍️ 练习

1. 把 §3.2 的 `lean-sorry-hunter` 真的建出来（本仓 `loops/lean/` 环境现成），用一个真 sorry 场景走一遍决策树。
2. 为你最熟的数学领域写一张"领域战术卡"（inequality-tactics 的同构物），要求：≥5 条带"何时用/何时失效"的战术，每条附一个 scripts 可验证的例子。
3. （思考）§2 五型分类里哪型最难自动化进化？为什么？（提示：方法论型的"知道何时该放弃某条路"涉及品味——回到 [06](06-模型适配-同一个skill跨九种模型.md) 的 judgmental 成分）

---

## 🏁 全系列收官

「讲透 Skills」00-09 + 实验室三实验（E1 触发评测 / E2 token 账本 / E3 合规检查器）至此完成。

> **一句话总结**：Skill 是 prompt 的进化形态——**可版本控制、可分层加载、可跨工具携带的程序性知识包**。它的威力来自三个机制（渐进披露的经济学、description 即检索键、scripts 卸载确定性），它的未来在三个方向（自动进化闭环、行为对齐路由、机器可验证域的率先落地——而数学，正是那个机器可验证域）。

**回 [README 站点地图](README.md)**
