# 01 · CDCL 引擎的 RL 状态机改造 —— Solver.cc 的挂起-恢复协程

> 对象：`minisat/minisat/core/Solver.cc`（1213 行）与 `minisat/minisat/core/Solver.h`、`minisat/minisat/core/SolverTypes.h`、`minisat/minisat/simp/SimpSolver.h`、`minisat/minisat/simp/Main.cc`
> 一句话：把一个"单次调用跑到底"的经典 CDCL 求解循环，用两个 `goto` 恢复点手术式改造成可被外部逐步驱动的强化学习环境——决策权在每一次分支选择前移交给外部 agent，传播、冲突分析、子句学习、重启仍由求解器原子完成。

## 一、角色定位

MiniSat 的 `Solver` 是教科书级的 CDCL（Conflict-Driven Clause Learning）实现：`solve_()` 外层循环管重启，`search()` 内层循环管"传播→冲突→学习→决策"的迭代。原版语义里，`pickBranchLit()`（`minisat/minisat/core/Solver.cc:260`）用 VSIDS 活动度堆自主选定下一个分支文字，调用方只在最终拿到 SAT/UNSAT/INDETERMINATE 三态。

GraphQSat 要做的则是让这个决策点变成 MDP 的决策边界：每到一次分支选择，求解器**停下**，把当前子句库/赋值/活动度打包成观测交给外部（Python 侧的 Q 网络），等 `step(decision)` 送回一个文字再继续。文件头的改造总纲写得很直白（`minisat/minisat/core/Solver.cc:28-29`）："Most of the changes in this file are related to saving the state to support variable sized states and cap the maximum number of Graph-Q-SAT decisions."

血统上这并非 NVIDIA 原创：`minisat/minisat/core/Solver.cc:3` 注明整目录拷贝改写自 feiwang3311/minisat（即 Graph-Q-SAT 论文作者的 fork），再上溯 niklasso/minisat。仓内代码带着大量 "Comments by Fei" 的改造自述注释，本身就是一份内嵌的 diff 说明。NVIDIA 版的关键代际增量是 `env_state_*` 变尺寸状态向量组（`minisat/minisat/core/Solver.h:168-172`：`std::vector<int> env_state_metadata/assignments`、`std::vector<double> env_state_activities`、`std::vector<std::vector<int>> env_state_clauses`）与配套的 `getClauses()` 观测通道——原实现是定长数组，难以支撑可变规模的问题集。

## 二、内部结构

### 2.1 挂起-恢复：goto 实现的"穷人协程"

改造的核心是两个恢复标签：

- **label2**（`minisat/minisat/core/Solver.cc:820`）：位于 `search()` 内层决策分支内部。函数入口处 `if (env_hold) {goto label2;}`（`minisat/minisat/core/Solver.cc:713`）——只要上次挂起，本次进入就直接跳到"接收 agent 决策"的位置，跳过入口处的状态初始化。
- **label1**（`minisat/minisat/core/Solver.cc:923`）：位于 `solve_()` 重启循环体内。入口处同样 `if (env_hold) {goto label1;}`（`minisat/minisat/core/Solver.cc:888`），直接跳到 `remember_status = search(0)` 调用点。

为什么要两个标签？因为挂起点在 `search()` 的深层，而"继续执行"的路径要经过 `solve_()` 的外层循环体。挂起时 `search()` 和 `solve_()` 的栈帧都已经 return 掉了，C++ 无法保留局部变量——所以恢复路径是：外部 `step()` → `SimpSolver::step()`（`minisat/minisat/simp/SimpSolver.h:115`，就一行 `{return solve_();}`）→ `solve_()` 入口 goto label1 → `search(0)` → 入口 goto label2 → 从挂起点续跑。栈帧重建的成本，用跳过两段初始化代码来补偿。

### 2.2 局部变量提升为成员：约 10 个

要让局部变量跨栈帧存活，只能提升为类成员。`minisat/minisat/core/Solver.h:174-186` 的注释逐个自述了来源（"Adopted from a local variable in search()/solve_()"）：

| 成员 | 原身份 | 用途 |
|---|---|---|
| `conflictCounts` | `search()` 局部 `conflictC` | 当前重启周期内冲突计数（`minisat/minisat/core/Solver.cc:718` 显式归零） |
| `number_of_conflicts` | `search()` 参数 `nof_conflicts` | 本周期冲突预算；`search(int)` 签名保留但参数已废（`minisat/minisat/core/Solver.cc:711` 注释 "The parameter is now dummy!"） |
| `confl` | `search()` 局部 | 当前冲突引用（`minisat/minisat/core/Solver.cc:723` `confl = propagate()`） |
| `field_of_next` | `search()` 局部 `next` | 下一个待入队文字（`minisat/minisat/core/Solver.cc:781`/`835`） |
| `remember_status` | `solve_()` 局部 `status` | 三态返回值（`minisat/minisat/core/Solver.cc:903`/`924`） |
| `current_restarts` | `solve_()` 局部 `curr_restarts` | 重启轮数（`minisat/minisat/core/Solver.cc:914`） |
| `agent_decision` | 无（新增） | 外部 agent 决策的落点（`minisat/minisat/core/Solver.cc:823`） |
| `env_hold`/`env_reward`/`state_mode` | 无（新增） | 挂起协议三件套 |

另有 `with_restarts`/`max_decision_cap` 两个行为开关由 `GymSolver` 构造时注入（见 `minisat/minisat/gym/GymSolver.cc:42-43`）。

### 2.3 决策点挂起块

无冲突且无 assumption 待注入时到达决策点（`minisat/minisat/core/Solver.cc:799`）。首次到达：

1. `saveState(assumptions, decisionLevel())`（`minisat/minisat/core/Solver.cc:804`）快照当前状态；异常时打印消息并 `return l_False` 直接终止（`minisat/minisat/core/Solver.cc:807` 注释自认 "Not Sure if good"）；
2. 若 `state_mode` 已是 `STATE_CONFLICT`/`STATE_SOLVED`（`minisat/minisat/core/SolverTypes.h:487` 的三值枚举），直接返回 `l_False`/`l_True`（`minisat/minisat/core/Solver.cc:809-815`）——后者对应"模型可能尚未完整但所有子句已满足"的退化情形，注释特意指出原版 MiniSat 会继续把模型填满；
3. 否则 `env_hold = true; env_reward = -1.0; return l_Undef`（`minisat/minisat/core/Solver.cc:817-819`）——这就是挂起。

恢复时（label2 之后）：`field_of_next = agent_decision`（`minisat/minisat/core/Solver.cc:823`），复位 `env_hold = false`、`env_reward = 0.0`（`minisat/minisat/core/Solver.cc:825-826`）。若 agent 送回 `lit_Undef`，视为"无可再决策"，返回 `l_True`（`minisat/minisat/core/Solver.cc:828-830`）。随后正常 `newDecisionLevel(); uncheckedEnqueue(field_of_next)`（`minisat/minisat/core/Solver.cc:834-835`）回到 CDCL 主循环。

### 2.4 l_Undef 的语义分裂

这是理解挂起协议的关键：`search()`/`solve_()` 返回 `l_Undef` 现在有**两种**含义——

- 冲突预算耗尽：`cancelUntil(0)` 后返回（`minisat/minisat/core/Solver.cc:763-767`），此时 `env_hold == false`，`solve_()` 会继续重启循环；
- 挂起等待决策：`env_hold == true`，`solve_()` 在 `minisat/minisat/core/Solver.cc:925` 检查后立即透传返回。

调用方（`minisat/minisat/simp/Main.cc:145-148` 的 `while (S.env_hold)` 循环、Python 侧的 `getDone()`）一律以 `env_hold` 而非返回值区分二者。`minisat/minisat/core/Solver.cc:819` 注释直言返回值此时 "is dummy"。

## 三、外部连接

- **上行（状态外送）**：`env_state_*` 四个 vector 组被 `GymSolver.cc` 的 getter 直接以指针引用（`minisat/minisat/gym/GymSolver.cc:82-96`），经 SWIG 变成 Python list——详见本系列第 2 篇。
- **下行（决策注入）**：`agent_decision` 由 `GymSolver::step(int)` 写入：`decision == 32767` 时回落 `S.default_pickLit()`（即 VSIDS `pickBranchLit()` 的公开短路，`minisat/minisat/core/Solver.h:184`）；否则 `mkLit(abs(decision)-1, decision < 0)`——正数=变量取真、负数=变量取假、32767=让 MiniSat 自主决策（`minisat/minisat/gym/GymSolver.cc:64-71`）。变量号减 1 是 DIMACS 1-based 到内部 0-based 的换算。
- **CLI 对偶入口**：`minisat/minisat/simp/Main.cc:141-148` 用 `while (S.env_hold) { S.agent_decision = S.default_pickLit(); ret = S.step(); }` 模拟一个"永远投弃权票"的 agent——这让改造后的求解器在命令行下行为等价于原版 MiniSat，也解释了 32767 哨兵的语义来源。
- **初始化协议**：`SimpSolver::solveLimited` 内联开头 `env_hold = false; env_reward = 0.0; state_mode = STATE_SOLVED;`（`minisat/minisat/simp/SimpSolver.h:227-228`，注释 "RL env init"）——每次"episode"开始时复位挂起态。析构函数还会把 `STATE_IN_PROGRESS` 归档为 `STATE_SOLVED` 防悬挂（`minisat/minisat/core/Solver.cc:117-121`）。

## 四、数据流

一次 `saveState`（`minisat/minisat/core/Solver.cc:1049-1134`）的产出结构：

1. **哨兵检查**：`!ok` 时标记 `STATE_CONFLICT` 直接返回（`minisat/minisat/core/Solver.cc:1051-1057`）；未满足子句数为 0 时标记 `STATE_SOLVED` 返回（`minisat/minisat/core/Solver.cc:1070-1076`）——即 UNSAT/SAT 可在快照阶段就被判定，`search()` 随后据 `state_mode` 收尾。
2. **6 元 metadata 头**：`env_state_metadata[0..4] = next_var / (原始子句数+学习子句数) / 当前决策深度 / 原始子句数（界定 clauses 与 learnts 分界）/ 重启轮数`（`minisat/minisat/core/Solver.cc:1081-1083`、`minisat/minisat/core/Solver.cc:1116-1118`）；第 5 槽 `progressEstimate()` 被注释掉弃用（`minisat/minisat/core/Solver.cc:1119`）。
3. **决策截断**：`decisions > max_decision_cap` 时提前 return（`minisat/minisat/core/Solver.cc:1087-1089`）——此后不再构建子句观测，`env_state_clauses` 保持为空，Python 侧据此走 dummy 观测、"剩下全交 VSIDS"。这正是文件头注释 "cap the maximum number of Graph-Q-SAT decisions" 的落点。
4. **逐变量**：`env_state_assignments[i] = toInt(assigns[i])`、`env_state_activities[i] = activity[i]`（`minisat/minisat/core/Solver.cc:1091-1096`）。注意 `toInt` 的编码是 `l_True=0 / l_False=1 / l_Undef=2`——Python 侧 `el == 2` 判未赋值（`minisat/minisat/gym/MiniSATEnv.py:130`）完全依赖这个隐式约定。
5. **逐子句**：先原始后学习（`minisat/minisat/core/Solver.cc:1100-1113`、`minisat/minisat/core/Solver.cc:1121-1133`），跳过已满足子句与已赋假文字，文字编码为 DIMACS 风格 `sign ? -(var+1) : (var+1)`（`minisat/minisat/core/Solver.cc:1108`）——+1 偏移把 0 留作保留字，与外部 CNF 文件格式对齐。

整条链路：CDCL 内部堆/区/分配器结构 → 每决策点全量线性化 → Python 图观测 → Q 网络决策 → ±var 编码回到 `Lit`。观测是**每步重建**而非增量更新，换来的是观测自包含、无 need 反向同步。

## 五、设计决策

**为什么用 goto 而不是线程/协程/回调？** 这是 2019-2020 年的 C++ 工程，没有 C++20 coroutine；线程方案要锁住整个求解器状态、付出上下文切换与内存屏障；回调方案要求把 `search()` 的控制流倒转为状态机重写，对一个 900 行的紧耦合循环风险极高。`goto` 恢复点的代价是：所有跨挂起点的局部变量必须手工提升成员（漏一个就是状态污染 bug）、函数可重入性依赖调用纪律。对 fork-改写型研究代码，这是侵入最小、diff 可读性最好的选择——每处改动都有 "Comments by Fei" 标注，等价于一份行级 patch 说明。

**为什么观测全量重建？** 变长状态（子句可增删、变量可被简化消除）让增量观测的版本管理非常复杂；全量序列化在每次决策点做一次，把复杂度从"维护观测一致性"换成"多花序列化时间"——对 RL 训练这个本身就慢的环节是合理交换。

**冗余信令**：`env_reward` 被认真维护（挂起时 -1.0、恢复时 0.0，`minisat/minisat/core/Solver.cc:818/826`）并有 `getReward()` 暴露，但 Python 侧实际奖励由 `MiniSATEnv.step` 自己按 `penalty_size` 计算，`getReward()` 全仓零消费——它是挂起协议里的冗余信号，读代码时不要被它带偏以为奖励来自 C++ 侧。

**`search()` 的 dummy 参数**（`minisat/minisat/core/Solver.cc:711`）是典型的"接口兼容优先"：保留签名少改调用方，冲突预算改由成员 `number_of_conflicts` 承载，`solve_()` 按重启策略计算它（`minisat/minisat/core/Solver.cc:917-921`：`with_restarts` 为假时置 -1 表示无穷）。

## 六、新人提示

1. **读码入口顺序**：先 `minisat/minisat/core/Solver.cc:711-840`（search 全函数）再 `885-943`（solve_），对照 `minisat/minisat/core/Solver.h:162-186` 的成员注释，改造逻辑半小时可通。
2. **调试挂起状态污染**：若发现求解器"跳步"或决策错乱，优先排查两个 goto 之间是否还有未被提升成员的局部变量在写状态；`conflictCounts` 这类计数器的归零点（`minisat/minisat/core/Solver.cc:718`）在 goto label2 路径上被跳过是有意为之——挂起永远发生在周期中途，计数必须延续。
3. **32767 的两侧常量必须同步**：`minisat/minisat/gym/GymSolver.cc:65` 与 `minisat/minisat/gym/MiniSATEnv.py:39`（`MINISAT_DECISION_CONSTANT`）各写一份，无编译期一致性保证；改动任一侧都会让"弃权决策"静默变成"选第 32767 号变量的错误文字"。同理注意 `toInt` 的 0/1/2 赋值编码是跨语言契约。
4. **别信返回值，信 env_hold**：所有判断求解器是否在等待决策的地方（`minisat/minisat/simp/Main.cc:145`、`minisat/minisat/gym/GymSolver.cc:78` 的 `getDone()`）都只看 `env_hold`。
5. **对照阅读**：本系列第 2 篇讲这些 `env_state_*` 向量如何穿过 SWIG 到 Python，第 3 篇讲谁在消费它们；`saveState` 输出的 metadata 槽位语义（`minisat/minisat/core/Solver.cc:1081-1118`）是三篇共用的一张密码表。
