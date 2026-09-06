# 16 · 状态图与 XState:Agent/RL/AI 的可执行形式模型

> 番外·二:15 章按 CMU 15-414 的教学顺序补了证明论缺口,本章补另一个端点——**形式方法的工程化落地**。主角是状态图(Statecharts):Harel 1987 的可视化形式体系,到 [XState](https://github.com/statelyai/xstate)(TS 生态的可执行实现)再到 2025-2026 的 agent 编排热潮。它的动物园位置很妙:07 章的 LTL 模型检测是 PSPACE-complete,但如果**系统本身就是显式写出的状态机**,验证退化为可达性(P)——状态图的哲学是"与其事后验证一个隐式系统,不如把系统写成显式形式模型"。先给四领域适用性判定(含 HPC 负结果),仪器是 [`experiments/lab16_statecharts.py`](./experiments/lab16_statecharts.py)(纯 Python:mini 状态图引擎 guard=guardrail + 奖励机器 Q-learning)。【显式 FSM 验证 = P;奖励机器 = 乘积 MDP】

---

**2026 年春。** 一支团队的生产 agent 在凌晨三点进入重试风暴:工具调用超时 → LLM 决定"再试一次" → 又超时 → 上下文越滚越长 → 账单五位数。事后复盘,根因平庸得让人恼火——**没人定义过"重试两次之后该去哪"**。prompt chain 把控制流外包给了概率模型,而概率模型不保证记住自己走过的路。同一季,行业话术悄悄换血:["你的 AI agent 需要的是状态机,不是提示链"](https://brightlume.ai/blog/why-ai-agent-needs-state-machine-not-prompt-chain)、Stately 官方开源 [statelyai/agent](https://github.com/statelyai/agent)("用 XState 打造状态机驱动的 LLM agent")、HN 上连 [Statewright](https://news.ycombinator.com/item?id=48108778) 这种"编排干脆不用 LLM"的 Rust 状态机引擎都上了热榜。**确定性编排**成了 2026 年 agent 工程的关键词——本章讲清楚这件事的形式根基,以及它到底能迁到哪、迁不到哪。

---

## 一、适用性判定:先判定,再展开

| 领域 | 判定 | 一句话依据 |
|---|---|---|
| **Agent 编排** | ✅ 强可用 | 状态机定骨架、LLM 只在节点干活、guard 天然是 guardrail——与 omega-guard 一脉(§三) |
| **RL** | ⚠️ 思想可用,库不在栈里 | 奖励机器(Icarte 系)就是 FSM 编码非马尔可夫奖励;XState 本身不出现在 RL 生态(§四) |
| **AI 工作流** | ✅ 可用 | human-in-loop 审批、确定性重试、可审计 trace——TS 系流水线的正经选择(§三) |
| **高性能计算** | ❌ 不可用,别硬包装 | XState 是 TS 运行时;HPC 的形式需求在数值正确性,不在控制流编排(§五) |

负结果也是判定。本章不把"NCCL 内部有个状态机"包装成"XState 的 HPC 应用"——思想的远亲不等于工具的落点,这是 [00 章](./00-为什么形式化+Lean4SOTA.md)"验证剧场"批判在选型场景的镜像。

## 二、状态图本体:Harel 1987 → SCXML → XState v5

FSM 的经典病是**状态爆炸**:n 个独立布尔特征,平铺 FSM 要 2ⁿ 个状态。Harel 1987(*Statecharts: A visual formalism for complex systems*)的三味药:

1. **层级(OR 状态)**:状态可以嵌套——"传输中"内部再分"握手/流式/收尾",公共迁移画在外层,内部细节折叠。组合方式从 2ⁿ 降为结构性增长。
2. **正交(AND 区域)**:真正独立的部件画成并列区域,各自迁移、互不组合——正交的 n 个部件是**相加**,不是相乘。
3. **广播事件**:迁移可以发事件,别的区域听见即动——比"轮询全局状态" disciplined。

状态图有精确的形式语义(事件进入的先后、迁移优先级都定死),W3C 把它标准化为 SCXML(2015);[XState](https://github.com/statelyai/xstate) 是这个体系在 TS/JS 的旗舰实现(v5,2023 年末定型):`createMachine` 声明状态与迁移,`guard` 是迁移上的谓词,`actor` 是状态里挂的计算单元(LLM 调用正是 actor)。它的工程卖点一句话:**状态图是可执行的形式模型**——画出来的是图,跑起来的是代码,验证起来是显式转移表。

**显式 FSM 的验证 = 可达性**。lab16 E0 对一台编排机跑 BFS:

```
编排机状态:['archived', 'done', 'executing', 'idle', 'planning', 'reviewing']
从初态 idle 可达:{'done', 'executing', 'idle', 'planning', 'reviewing'}
不可达:['archived'] —— 'archived' 无入边,死配置一眼看出
```

线性时间 O(|V|+|E|),P 格。对比 [07 章](./07-LTL与Spin.md)的 PSPACE:LTL 模型检测的复杂度在"**性质公式 × 系统**"的联合乘积上,显式小机器上这层爆炸根本不存在。状态图不新增复杂度格——它是**把问题搬进 P 格的设计纪律**。这正是它和 Petri 网、LTL 综合的分工起点(§三)。

## 三、Agent 落点:guard = guardrail

[statelyai/agent](https://github.com/statelyai/agent) 的架构一句话:**状态机定义 agent 能做什么,应用侧决定模型是谁、请求怎么发、执行怎么控**。LLM 的非确定性被关进节点(actor)里,节点之间的路只有状态机认识。关键映射在 guard 上:

```
guard: (ctx, payload) → bool     ← 这就是 Guardrail 的 enforce 判定
guard 拒绝 → 状态保持、零副作用   ← 这就是 fail-closed 拦截
```

lab16 E1 把一台 `idle→planning→executing→reviewing→done` 的编排机交给"只会提议事件的 LLM",三判决逐条落地:

```
  [executing] --tool-- → executing ✓
  [executing] --tool-- ✗ guard `tool_allowed` 拒绝 → 状态保持 executing(零副作用)
  [executing] --tool-- ✗ 未建模事件 → 拒绝(fail-closed)
放行 6 条,拦截 3 条(delete_db/rm-rf 被 guard 拒、self_destruct 未建模拒)
→ 确定性骨架包住非确定性模型——LLM 提议,状态机裁决
```

这与本库 **omega-guard** 工程 monitor 的 observe/enforce 是同一个形状:监控器看事件流、guard 在迁移点上裁决、拒绝不改变受控状态。区别只在粒度——omega-guard 的谓词跑在事件 trace 上(时序属性),状态图的 guard 跑在单次迁移上(瞬时属性);前者表达力强([07 章](./07-LTL与Spin.md)的地盘),后者工程上便宜得多。**同一谱系,两个档位**。

**形态学对比**——三种"agent 编排形式模型"的形式语义差异决定适用场景:

| | 状态图(XState) | 图路由(LangGraph 系) | Petri 网(ProMoAI/Formal-LLM 系) |
|---|---|---|---|
| 本体 | 层级状态 + 迁移 | 数据流节点 + 条件边 | 库所 + token + 变迁 |
| 并发 | 正交区域(并行但同步组装) | 显式 fan-out/checkpoint | **真并发**(token 语义,资源流) |
| 形式根基 | Harel 状态图/SCXML | 无强形式语义(工程图) | WF-net soundness([文献笔记](./文献-Petri网与LLM-Agent编排.md)) |
| 强项 | 单对象控制流、guard 天然 | 状态传递、人肉直觉 | 资源竞争、流程钉死 |
| 生态 | TS/前端、statelyai/agent | Python/LLM 栈 | BPM/过程挖掘、RWTH 系 |

分工一句话(本库文献笔记的原话改写):**要"系统自动生成策略"找 LTL 综合,要"钉死流程、LLM 只准在轨道内发挥"找 Petri 网;要在工程上便宜地把骨架写死、逐点把关,找状态图**。三者不互斥——状态图管单 agent 内部,Petri 网管多 agent 资源流,[07 章](./07-LTL与Spin.md)管跨轨迹的时序承诺。

## 四、RL 落点:奖励机器——把规格装进自动机

RL 里 FSM 的正经学术身份是**奖励机器**(Reward Machine,[Icarte et al., ICML 2018](https://proceedings.mlr.press/v80/icarte18a/icarte18a.pdf);扩展版 [JAIR 2022](https://jair.org/index.php/jair/article/download/12440/26759/29354),500+ 引)。问题:"先到 A 再到 B 再到 C"这类**非马尔可夫奖励**——同一个位置,奖励取决于之前去过哪,单看当前状态定不了 r。解法:奖励装进自动机,状态空间取乘积:

```
RM:u0 --a--> u1 --b--> u2 --c--> u3(done)     ← 规格(人写/LLM 写)编译成自动机
乘积 MDP:(位置, RM 状态) = 36 × 4 = 144 状态   ← 奖励变回马尔可夫
奖励:每条 RM 推进边 +1(sparse 版只在终态 +1)
```

lab16 E2 在 6×6 网格上对拍两种奖励的 Q-learning(同种子、同乘积状态、最优 20 步):

```
[sparse] 前200幕成功 162 次 | 滑动100幕成功率≥90% = 第 136 幕 | 最终贪心策略 20 步到达 C ✓
[RM形  ] 前200幕成功 193 次 | 滑动100幕成功率≥90% = 第  99 幕 | 最终贪心策略 20 步到达 C ✓
```

读数两条:**(1) 乘积状态使奖励马尔可夫化,是两者能解的共同前提**——不带记忆的 36 状态上,"同位置不同奖"直接违反 MDP 定义;**(2) RM 把 20 步的延迟奖励拆成 3 段 ≤10 步的近奖励,信用分配被自动机结构砍薄**——收敛快一截(99 是百幕滑窗的下限,136 是 sparse 的实际爬坡)。LTL→自动机→奖励的整条管线([JMLR/JAIR 系综述线索](https://www.cs.toronto.edu/~sheila/reward_machines/))是 [07 章](./07-LTL与Spin.md) LTL 的工程下游,而"奖励从 ad-hoc 代码变成可检验的形式结构"与 [01 章](./01-Lean4作为RL奖励验证器.md)"奖励作为形式对象"同向——RM 是可执行规约,Lean4 验的是它的证明侧亲戚。

另两条 RL 连接,一句话各:**(a) options/分层 RL** 的宏观骨架天然是状态图(选项=带入口/终止条件的子策略);**(b) 策略蒸馏成 FSM**——把训好的 agent 当黑盒,用 [14 章](./14-自动机学习Lstar.md) 的 Angluin L* 通过成员/等价查询重建其策略自动机,是 L* 在 RL 上的反向应用(14 章讲"从黑盒学协议",这里是"从黑盒学策略")。

## 五、HPC 负结果:为什么不可用

三刀切干净:**(1) 生态位**——XState 是 TS/JS 运行时,HPC 的代码是 CUDA/Fortran/C++,没有交集;**(2) 病灶错位**——HPC 的正确性风险集中在数值(浮点结合序、并行归约的确定性、tile 边界),控制流简单到不值得上状态图;**(3) 思想 vs 工具**——NCCL 集合通信的状态机、MPI 进程的生命周期,确实是 FSM 思想的用武之地,但那是手写 C 里的枚举+switch,不需要也不依赖 XState。把这三条包装成"XState 在 HPC 的应用"就是选型场景的验证剧场。真要在性能线吃形式化红利,路在 [01 章](./01-Lean4作为RL奖励验证器.md)的 Alive2/验证器赛道和 00 章的 Atmosphere 谱系,不在本章。**边界由你裁**:如果你的编译/推理引擎里出现了"重试-降级-熔断"这类控制流怪物,状态图思想(显式状态+guard)是值得借的——借思想,不引库。

## 六、复杂度格与造桥

- **格籍**:显式 FSM 验证(可达性/死锁/不变式)= P,线性;LTL 模型检测 = PSPACE([07 章](./07-LTL与Spin.md));奖励机器 = 乘积 MDP 上的标准 RL,复杂度同 [10 章](./10-PRISM概率模型检测.md)的 P 格。状态图不占新格——它是**搬运工**:把系统写小、写显式,让问题落进 P。
- **造桥**:→[07](./07-LTL与Spin.md)(RM 是 LTL 的下游;跨轨迹时序属性仍是 LTL 的地盘);→[10](./10-PRISM概率模型检测.md)(乘积 MDP=价值迭代吃的那个对象);→[14](./14-自动机学习Lstar.md)(策略蒸馏=从黑盒 agent 学自动机);→[01](./01-Lean4作为RL奖励验证器.md)(奖励作为形式对象);→[00](./00-为什么形式化+Lean4SOTA.md)(验证剧场警告:状态图≠已验证——可达性检查不等于性质全覆盖,但比 prompt chain 强一个数量级);→[15](./15-漏洞捕捉CMU15414.md)(guard 的谓词就是 15 章的契约断言,验证它的义务同属 WP 世界)。
- **一句总结**:状态图是把形式方法从"证明别人的代码"翻转为"把系统本身写成形式对象"的最便宜入口——表达力天花板低(时序属性、数值属性都够不着),但工程摩擦也最低。

## 七、仪器

```bash
python experiments/lab16_statecharts.py   # 零第三方依赖(numpy 都不用)
```

E0 可达性(P 格验证)/ E1 guard=guardrail 三判决 / E2 奖励机器 6×6 对拍。全 assert 自检;输出即本章 §二/§三/§四 引文。

---

**番外收束,主线回到卷一**:[04 章](./04-有界模型检查CBMC.md)——当不变式写不出来时,把循环展开 k 步,交给 SAT。
