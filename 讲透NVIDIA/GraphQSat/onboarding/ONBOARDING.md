# GraphQSat（GQSAT）新人入门指南

> 图谱 155n/273e/11 层/14 步 tour；锚点均经源码逐行核实。

## 一、项目定位：Q-learning × 图网络 × SAT 分支启发式

README 开篇即研究问题（README.md:3）：*"Can Q-learning with Graph Networks learn a Generalizable Branching Heuristic for a SAT solver?"*——GQSAT（NeurIPS 2020）把 CDCL 求解器最内层的**分支决策**（下一个给哪个变量赋什么值）交给 Q-learning 训练的图神经网络，子句学习/传播/重启/预处理全保留 MiniSAT 原实现。三条设计决策定调全仓：

1. **环境即求解器**：把 C++ 主循环改造成可挂起-恢复的 gym 环境——每到分支点即暂停，序列化状态给 agent，决策回传再继续。
2. **观测即图**：CNF 是"变量×子句"二部图，GNN 输出候选分支 Q 值，epsilon-greedy 选支。
3. **基线即自身**：agent 可随时"弃权"（回传哨兵值），求解器回落原生 VSIDS——两类 agent 共用同一环境。

全仓四条线：C++ 求解器改造（minisat/）、gym 环境线（sat-v0）、Python 训练线（gqsat/ + dqn.py）、容器运维。血统：minisat/__init__.py:1-4 注明 minisat/ 源自 feiwang3311/minisat（更早自 niklasso/minisat）。图谱阅读顺序：t01 鸟瞰 → t10 Solver 改造 → t09 GymSolver → t08 SWIG → t07 gym 封装 → t02-t06 训练栈；自底向上则 t13 → t12。

## 二、技术栈与代码版图：11 层图谱导读

11 层呈"上游底座→GQSAT 手术层→Python 应用层"漏斗，**L04-L07 是改造重灾区，L01-L03 基本上游原样**：

| 层 | 名称 | 定位 |
|---|---|---|
| L01 | mtl 模板容器 | 11 | Vec/Heap/Alloc 纯头文件，容器之母，上游原样 |
| L02 | utils 解析工具 | 5 | ParseUtils（zlib 流）/Options/System |
| L03 | 类型系统与 DIMACS | 2 | SolverTypes.h（Lit/lbool/Clause）+ Dimacs.h |
| L04 | Solver 核心 CDCL | 3 | **重灾区**：search()/solve_() 变挂起-恢复状态机 |
| L05 | SimpSolver 预处理 | 3 | 变量消除层；定制 step()/solveLimited() |
| L06 | GymSolver RL 环境 | 2 | C++ 侧 gym 语义七方法 |
| L07 | SWIG 绑定链 | 5 | .i → wrap.cxx → _GymSolver.so → GymSolver.py |
| L08 | Python gym 封装 | 3 | sat-v0 注册 + gym_sat_Env（图观测/步数惩罚） |
| L09 | gqsat 训练库 | 6 | agents/models/learners/buffer/utils |
| L10 | 训练评估入口 | 5 | dqn.py/evaluate.py/add_metadata.py + 两 shell |
| L11 | 构建容器运维 | 7 | Makefile(python-wrap)/CMakeLists/Dockerfile |

技术栈：C++（zlib+SWIG 3.0.12）+ Python 3.6 栈（PyTorch 1.1+PyG+gym）。双构建并存：CMakeLists.txt 只管库与可执行文件，**不含 SWIG**。层与 tour 映射：t13=L01/L02、t12=L03、t10=L04、t11=L05、t09=L06、t08=L07、t07=L08、t02-t05=L09、t06=L10、t14=L11。

## 三、核心架构：挂起-恢复状态机与 agent_decision hook

上游 `search()` 跑到底、局部变量记状态；GQSAT（注释署名 Fei）做了三刀手术：

**第一刀：goto 恢复点**。`if (env_hold) {goto label2;}`（minisat/minisat/core/Solver.cc:713，label2 于同文件:820）与 `if (env_hold) {goto label1;}`（minisat/minisat/core/Solver.cc:888，label1 于同文件:923）。env_hold 为真即跳到恢复点（跳过传播/冲突分析），下次 step 从 label 继续——goto 模拟协程。

**第二刀：局部变量提升为成员**。挂起后局部状态随栈帧销毁，约 10 个局部量升为成员：solve_ 返回值变 `remember_status`（minisat/minisat/core/Solver.cc:903）、分支目标变 `field_of_next`、`env_hold`（minisat/minisat/core/Solver.h:162）、四个 env_state_* 观测向量（minisat/minisat/core/Solver.h:168-171）、`agent_decision`（minisat/minisat/core/Solver.h:177）、直通 VSIDS 的 `default_pickLit()`（minisat/minisat/core/Solver.h:184）。

**第三刀：分支点 hook**。search 需要新决策时：`saveState(assumptions, decisionLevel())`（minisat/minisat/core/Solver.cc:804）打包观测，`env_hold = true; env_reward = -1.0;`（minisat/minisat/core/Solver.cc:817-818）后 return l_Undef 交还控制权；恢复后 `field_of_next = agent_decision;`（minisat/minisat/core/Solver.cc:823，覆盖 pickBranchLit 输出），随即 newDecisionLevel + uncheckedEnqueue 完成分支。

**最小完整示例**：minisat/minisat/simp/Main.cc:145-147 的三行循环（`while (S.env_hold) { agent_decision = default_pickLit(); step(); }`）——"agent 永远弃权"的最小主循环，读懂即懂整个协议。Python 侧等价物 `GymSolver::step(int decision)`（minisat/minisat/gym/GymSolver.cc:64-71）：32767 哨兵回落 VSIDS（minisat/minisat/gym/GymSolver.cc:65-66），否则 `mkLit(abs(decision)-1, decision<0)`（正=取真/负=取假）；getReward/getDone 分别返 env_reward 与 `!env_hold`（minisat/minisat/gym/GymSolver.cc:74-78）——每步默认 -1.0 步罚，env_hold 翻回 false 即 episode 结束。`lbool step() {return solve_();}`（minisat/minisat/simp/SimpSolver.h:115）：一次 step=推进到下一分支点，非一个传播步。

## 四、观测工程：saveState 序列化与 GNN 图构造

**C++ 打包**：`Solver::saveState`（minisat/minisat/core/Solver.cc:1049-1134）输出四向量（声明 minisat/minisat/core/Solver.h:168-171）：`env_state_metadata`（6 槽元信息）、`env_state_assignments`（逐变量指派三态）、`env_state_activities`（逐变量 VSIDS 活动度）、`env_state_clauses`（逐子句文字表=二部图子句侧邻接，含学习子句）。异常路径见 minisat/minisat/core/Solver.cc:806-809（return l_False 终止环境）。

**Python 图构造**：gym_sat_Env（minisat/minisat/gym/MiniSATEnv.py:45）的 `parse_state_as_graph()`（minisat/minisat/gym/MiniSATEnv.py:105）把向量拼成异构二部图（reset 读 CNF、step 调 GymSolver 取新观测）；奖励在 Python 层重标定为成功 0/失败 -penalty_size（minisat/minisat/gym/MiniSATEnv.py:309-311）；`normalized_score()`（minisat/minisat/gym/MiniSATEnv.py:324）用 METADATA 基线归一化。

数据流：**Solver 状态 → saveState 四向量 → SWIG 装箱 list → parse_state_as_graph 二部图 → GNN 输入**；变长图由 `batch_graphs`（gqsat/utils.py:381）拼批量。

## 五、Python 训练栈：dqn/agents/buffer/models

**动作编码链（Python↔C++ 契约）**：动作空间 2×nVars——`decision_to_var_mapping`（minisat/minisat/gym/MiniSATEnv.py:233）做消除后的变量重映射；`decision < 0` 换成 `MINISAT_DECISION_CONSTANT = 32767`（minisat/minisat/gym/MiniSATEnv.py:39）=弃权回落 VSIDS；偶数动作映射 `+(decision/2+1)`、奇数 `-(decision/2+1)`（minisat/minisat/gym/MiniSATEnv.py:284 起）。**MiniSATAgent.act 恒返 -1（gqsat/agents.py:32）即每步弃权=纯 VSIDS 基线**。

**gqsat/agents.py**：基类 `Agent`（gqsat/agents.py:20）；基线 `MiniSATAgent`（gqsat/agents.py:28）与 `RandomAgent`（gqsat/agents.py:38）；`GraphAgent`（gqsat/agents.py:52）**不继承 Agent**（图谱标注独立实现），`act(hist_buffer, eps)`（gqsat/agents.py:75）为 epsilon-greedy。

**gqsat/models.py**：`ModifiedMetaLayer`（gqsat/models.py:35）改造 PyG MetaLayer 传批量偏移；`GraphNet`（gqsat/models.py:112）边-节点-全局三体消息传递；`EncoderCoreDecoder`（gqsat/models.py:236）组装 encode→core×steps→decode。基类 `SatModel`（gqsat/models.py:53）：`save_to_yaml`（gqsat/models.py:60）用 `inspect.stack()`（gqsat/models.py:64）从调用栈内省构造实参写 YAML，`load_from_yaml`（gqsat/models.py:79）按类名+参数重建网络——评估时结构零差恢复。

**buffer 与 learner**：`ReplayGraphBuffer`（gqsat/buffer.py:20）环形回放，`sample`（gqsat/buffer.py:48）经 batch_graphs 拼图。`GraphLearner`（gqsat/learners.py:22）持 online/target 双网，TD 目标 `scatter_max` 按图聚合（gqsat/learners.py:85），损失+梯度裁剪，按频硬同步 target。工具箱 gqsat/utils.py：三层 argparse、`batch_graphs`（gqsat/utils.py:381）、`make_env`（gqsat/utils.py:435）、`evaluate`（gqsat/utils.py:456）。

**dqn.py 总入口**：`save_training_state`（dqn.py:33）落盘三件套（chkp+buffer.pkl+status.yaml）断点续训；**训练主循环全在 `if __name__ == "__main__":`（dqn.py:99）**，无可复用 train() 函数。gym 注册一行 minisat/__init__.py:33 `register(id="sat-v0", ...)`。

## 六、训练与评估实操：add_metadata → train → evaluate

**第 1 步 元数据**：`python3 add_metadata.py --eval-problems-paths <cnf 目录>`——add_metadata.py:30 起 with/without restarts 双 rollout，用 VSIDS 跑出每 CNF 两种基线步数写 METADATA，供归一化。

**第 2 步 训练**：train.sh:15 调 `python3 dqn.py` 带 47 个 `--` 超参。**最大坑：路径硬编码 `./data/uf50-218-tvt/{train,validation}`（train.sh:18-19）而仓内无 data/ 目录**——须自备 SATLIB uf50-218 按此摆放或改脚本。

**第 3 步 评估**：evaluate.sh:15 调 `python3 evaluate.py`，**三个占位符必须手工替换**：`PATH_TO_EVAL_DATA`/`MODEL_DIR`/`CHECKPOINT.chkp`（evaluate.sh:23-25）；脚本定死 --core-steps -1、eps=0、--no_restarts。恢复链：status.yaml（evaluate.py:31）→ load_from_yaml（evaluate.py:44）→ checkpoint 打分（evaluate.py:74）。

**容器**：Dockerfile 单阶段 CUDA 10.1+PyTorch 1.1+PyG（Dockerfile:15），**零 COPY**——代码不进镜像，docker_run.sh 把仓根以 rw 挂载进容器，训练产物直接落宿主。

## 七、构建链：SWIG + Makefile python-wrap

五件套（t08）：①接口 minisat/minisat/gym/GymSolver.i——为四个观测 getter 手写 out 类型映射，把 std::vector 及嵌套 vector 逐元素装箱成 Python list（minisat/minisat/gym/GymSolver.i:19-40）；②生成物 GymSolver_wrap.cxx（4455 行，SWIG 3.0.12）；改 .i 或 C++ 接口后按 README.md:24-26 重跑 swig 重生成；③编译 minisat/Makefile:224 的 python-wrap 目标：**硬编码 `-I/usr/include/python3.6`**（minisat/Makefile:226），换 Python 版本必改此行；链接 libminisat 产出 _GymSolver.so，入口 `make && make python-wrap`（README.md:22）；④运行时代理 minisat/minisat/gym/GymSolver.py（SWIG 生成，勿手改——改 .i）；⑤导入面=minisat/minisat/gym/GymSolver.h:41-47 的七方法，MiniSATEnv 只用这七个。

CMakeLists.txt 不含 SWIG；minisat/minisat/core/Main.cc 是未改造上游 CLI，可当"手术前"对照。

## 八、上手清单与避坑

**首日清单**：① 读 README，记三步流水与 `make && make python-wrap`（README.md:22）；② 精读 minisat/minisat/simp/Main.cc:145-147；③ 精读 minisat/minisat/core/Solver.cc:795-825 与 saveState（minisat/minisat/core/Solver.cc:1049-1134）画状态机；④ 备 SATLIB uf50-218 放 data/uf50-218-tvt/；⑤ 补 evaluate.sh:23-25 占位符再评估。

**避坑**（全部源码实证）：
- **行号勘误**：`goto label1` 实际在 minisat/minisat/core/Solver.cc:888（非 887）；`while (S.env_hold)` 在 minisat/minisat/simp/Main.cc:145（非 143）。
- **step 粒度**：一次 step=推进到下一分支点（minisat/minisat/simp/SimpSolver.h:115）。
- **奖励双口径**：C++ 每步 -1.0（minisat/minisat/core/Solver.cc:818），Python 重标定成功 0/失败 -penalty_size（minisat/minisat/gym/MiniSATEnv.py:309-311），训练读 Python 口径。
- **动作三段转换**：agent 输出 → minisat/minisat/gym/MiniSATEnv.py:233 重映射 → 同文件:281-287 极性/弃权编码 → minisat/minisat/gym/GymSolver.cc:65-68 mkLit；动作错位沿此链排查。
- **时代栈锁定**：minisat/Makefile:226 硬编码 python3.6、镜像锁 PyTorch 1.1+SWIG 3.0.12，优先用仓内 Dockerfile。
- **弃权可混用**：32767 哨兵只回落当步（minisat/minisat/gym/GymSolver.cc:66），混合策略合法且论文使用。
- **预处理改编号**：构造先 eliminate（minisat/minisat/gym/GymSolver.cc:52），GNN 变量集小于原始 CNF。
- **wrap.cxx 是生成物**：直接改会被 swig 覆盖（README.md:24-26 是正规流程）；**dqn.py:99 起全是 __main__ 顶层代码**，不可 import 复用。

**练习**：① 在 Main.cc 循环打印每步 agent_decision/env_reward；② RandomAgent 跑 add_metadata 对比 METADATA；③ 读 GraphLearner（gqsat/learners.py:22）画 TD 聚合示意。
