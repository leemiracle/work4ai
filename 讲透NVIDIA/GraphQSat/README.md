# 讲透 GraphQSat（NVIDIA GQSAT）

Q-learning+图网络学 SAT 求解器通用分支启发式的研究仓（README 首句即研究问题："Can Q-learning with Graph Networks learn a Generalizable Branching Heuristic for a SAT solver?"）。三层结构：gqsat/ Python Q-learning 训练库、minisat/minisat/ 被改造成 RL 环境的 C++ CDCL 求解器（feiwang3311/minisat fork 血统）、SWIG 绑定链连通两界。

## 全链状态表（2026-11-07/08 实例B）

| 阶段 | 状态 | 产物 |
|---|---|---|
| prepare | ✅ | 51 文件/7 批（既有） |
| 批分析 7 批 | ✅ | 155n/273e（imports 85=21 scanner+**64 手扫**——C/C++ #include 盲区全补偿；shell/Dockerfile 特规处理） |
| 终验 | ✅ | 0 问题/0 重复 ID/0 悬空 |
| merge+phase4 | ✅ | 155n/273e → 52 file 级/103 边 |
| layers/tour | ✅ | 11 层/14 步/52 节点全覆盖零交集（C++ 依赖方向 gym→simp→core→utils→mtl 与层序一致零逆向） |
| finalize | ✅ | **knowledge-graph.json 155n/273e/11层/14步，issues=0 warnings=0，fingerprints=51@cfc8f386（444 锁）** |
| onboarding | ✅ | onboarding/ONBOARDING.md 9465 字 8 节 102 锚（0 坏） |
| explain | ✅ | 3 篇 25,919 字符/219 锚（0 坏） |
| README | ✅ | 本文件 |

图谱在仓内：`/usr-data/data2/repos/agent-repos/NVIDIA/GraphQSat/.understand-anything/knowledge-graph.json`

（1308 事故注：23:43 首派写作线死于五小时限额零产出，03:11 重置后重派零损失闭环）

## 十一层架构

L01 mtl 模板容器(11) → L02 utils 工具(5) → L03 类型系统 DIMACS(2) → L04 Solver 核心 CDCL(3) → L05 SimpSolver(3) → L06 GymSolver C++ RL 环境(2) → L07 SWIG 绑定链(5) → L08 Python gym 封装(3) → L09 gqsat Q-learning 库(6) → L10 训练评估入口(5) → L11 构建容器运维(7)

## explain 索引

1. `explain/01-solver-state-machine.md` — CDCL 引擎的 RL 状态机改造（search() 挂起-恢复/goto 恢复点/agent_decision hook/saveState）
2. `explain/02-gym-binding-chain.md` — SWIG 到 Python 环境的绑定链（typemap/wrap.cxx/sat-v0 注册）
3. `explain/03-dqn-training-stack.md` — Python Q-learning 训练栈（dqn 主循环/Agent 族/SatModel/buffer）

## 源码级甄别清单（钉版）

1. **分支 hook 链（核心）**：GymSolver::step(decision)（GymSolver.cc:64-71）写 S.agent_decision（正=取真/负=取假/**32767 哨兵=回落 minisat 自身 VSIDS** default_pickLit）→ Solver.cc:823 field_of_next=agent_decision 直接取代 pickBranchLit 输出；agent 未接管时挂起：L804 saveState 快照+L817-819 env_hold=true/env_reward=-1.0/return l_Undef。
2. **search()/solve_() 被改造成可挂起-恢复的逐步状态机**：L713 `if(env_hold) goto label2`/L887(实际 888) `goto label1` 恢复点+约 10 局部变量提升成员——单次跑完的 CDCL 循环变成外部逐步驱动的协程，这是 RL 环境化的全部枢纽。
3. **saveState（Solver.cc:1049-1134，GQSAT 新增）**：6 元 metadata 头+逐子句序列化+trail 指派+变量活动度→env_state_* 四向量，构成 GNN 图观测。
4. **改动血统双层**：feiwang3311/minisat fork（"Comments by Fei"代际：env_hold/agent_decision/saveState 骨架）+GQSAT 代际（env_state_* 状态向量组/python3.6 wrap/getClauses 观测）。
5. **Main.cc while 循环实际在 simp/Main.cc:145-148**（core/Main.cc 的 L143-148 是结果文件写出）——CLI 侧 RL 步进对偶入口 `while(S.env_hold){agent_decision=default_pickLit(); step();}`。
6. **dqn.py/evaluate.py/add_metadata.py 在仓库根而非 gqsat/ 内**（gqsat/ 只含 agents/models/buffer/learners/utils）。
7. **C++ env_reward 完整维护+getReward 通道，但 Python 全仓零消费**（奖励实为 Python 侧 penalty_size）；getActivities 同属建好未用管线。
8. **三组跨语言隐式契约无编译期保障**：toInt 赋值编码 {0,1,2}、32767 哨兵、VAR_ID_IDX 常量。动作编码链在 MiniSATEnv.py:39/233/281-284（decision<0→32767、奇偶→±极性）；`return -1`（VSIDS 弃权）在 gqsat/agents.py:32。
8a. 行号精修：`goto label1` 实际在 Solver.cc:888（批分析口径 887 差一行）；`while(S.env_hold)` 起点 simp/Main.cc:145。
9. Makefile:225 注释"bump python version"与 :226 仍硬编码 /usr/include/python3.6 的反差；python-wrap 目标。CMakeLists 与 gym/SWIG 无关（两构建线分管）。
10. GraphAgent 不继承 Agent（独立类；仅 MiniSATAgent/RandomAgent 继承）；dqn.py 训练主循环全在 __main__ 块。
11. SatModel.save_to_yaml 用 inspect.stack 抓叶子构造实参（源码自认不支持多重继承）。
12. **Dockerfile 全文件零 COPY**——镜像只装环境，运行时靠 docker_run.sh 挂载仓根到 WORKDIR；LD_LIBRARY_PATH/PATH 硬编码 minisat/build/release/{lib,bin}。
13. **train.sh 硬编码 ./data/uf50-218-tvt/{train,validation} 而仓内无 data/ 目录**（用户自备）；evaluate.sh 含 MODEL_DIR/CHECKPOINT.chkp/PATH_TO_EVAL_DATA 三个占位符必须手填。
14. GymSolver_wrap.cxx（4455 行，SWIG 3.0.12 生成）按 auto-generated 规范只建 file 节点；GymSolver.py 的 _swig_* 样板同理。
15. merge/mkElimClause 双重载合并为单节点（避免 ID 重复）；.i 文件手写嵌套 vector→Python list 的 out typemap。

## 流水线备注

- 台账：仓内 `.understand-anything/PROGRESS.md`（含 1308 团灭-复活全程记录）
- 字数口径：不计空格字符；onboard 9465/explain 8136-9617（全路径锚密度推高，系列 norm 偏高端，如实报数）
