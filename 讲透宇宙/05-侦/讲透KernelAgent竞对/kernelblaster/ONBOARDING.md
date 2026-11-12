# KernelBlaster 新人上手指南

> 基于 understand-anything 知识图谱（269 节点 / 589 边 / 10 层 / 15 步导览，commit `84237f9`）自动生成，2026-09-03。

## 1. Project Overview

**KernelBlaster**（NVIDIA Labs，论文 [arXiv:2602.14293](https://arxiv.org/abs/2602.14293)）是一个 **MAIC-RL（Memory-Augmented In-context Reinforcement Learning）** 框架：用"持久 CUDA 优化知识库 + Nsight Compute profiling 反馈 + RL 式探索（replay buffer、策略更新）"替代昂贵的 LLM 微调，跨 GPU 代际优化 KernelBench-CUDA kernel。定位：不做固定启发式编译器，也不微调模型，而是让 agent 在上下文里持续学习——profile → 检索知识库 → 生成候选 → 验证 → reward → 更新策略。

- **语言**：Python（框架主体）、CUDA/C++（优化对象与服务端编译）、Shell、CMake、Dockerfile；主包安装后位于 `src/kernelblaster/` 下，测试与工具在 `utils/`。
- **框架**：PyTorch、Nsight Compute (ncu)、Docker、LangGraph（工作流图）、FastAPI（服务层）
- **性能声称**：vs PyTorch baseline geomean **1.43× (L1) / 2.50× (L2) / 1.50× (L3)**

**优化对象数据集** `data/kernelbench-cuda/`（注意：184 对 `init.cu` + `driver.cpp` 工件被 `.understand-anything/.understandignore` 排除在图谱外，本指南只覆盖框架源码）：目录结构为 `level{1,2,3}/<problem_name>/`，共三级难度 184 个问题，每个问题目录必须同时含 `init.cu`（待优化初始 kernel）与 `driver.cpp`（编译/运行/验证 harness）才算完整条目；`driver.cpp` 负责构建、运行并把候选 kernel 的行为与 reference 对拍验证正确性。优化产出为 `final_rl_cuda_perf.cu`，训练出的知识库落盘为 `optimization_database.json`。另一套 `data/kernelbench/` 是上游 PyTorch reference 实现（KernelBench 原始 problem.py），供基线脚本使用，需手动 clone。

**一句话心智模型**：把整个系统想象成"一个会做实验的工程师"——NCU 是她的眼睛（看瓶颈）、知识库是她的笔记本（记什么招在什么状态下有效）、replay buffer 是她的实验记录本、三级反思回路是她每晚复盘并修订笔记的方式；LLM 始终是同一只"手"，变的只是喂给它的上下文。

默认单次运行链路：`run_single_kernelblaster.sh` → `run_RL.py` → `workflow.py` → `optimization_rl_ncu.py` → `opt_ncu_rl.py`。最快上手路径是容器内三步：`docker build` → `docker run`（挂载 GPU）→ 设置 `OPENAI_API_KEY` 后执行 `bash scripts/run_single_kernelblaster.sh`，产物与轨迹都会落在 `out/<dataset>/<precision>/<experiment>/` 下。

## 2. Architecture Layers（10 层）

| # | 层 | 职责 | 关键文件 |
|---|---|---|---|
| 1 | 入口与实验脚本层 | CLI 入口与批量调度：Semaphore 并发、知识库注入、双基线评测、NCU 重剖析、GPU server 启动 | `scripts/run_RL.py`、`run_baselines.py`、`run_baselines_compile.py`、`run_reprofile.py`、`run_single_kernelblaster.sh` |
| 2 | Agent 核心层 | MAIC-RL 本体：RL 探索 agent、单发对照 agent、反馈迭代基座、RL 组件与持久知识库 | `agents/opt_ncu_rl.py`、`opt_ncu_minimal.py`、`feedback.py`、`rl_agents.py`、`database.py`、`reprofile.py` |
| 3 | Agent 基础设施层 | LLM 查询路由/重试、异步批处理队列、本地量化推理、NCU 解析标注、远程命令、JSONL IO | `agents/utils/query.py`、`batch_queue.py`、`local_llm.py`、`annotate_ncu.py`、`commands.py` |
| 4 | 图编排与工作流层 | LangGraph 图执行：图构建路由、TypedDict 状态契约、核心工作节点、带超时的异步执行器 | `graph/graph.py`、`state.py`、`nodes/optimization_rl_ncu.py`、`workflow/workflow.py` |
| 5 | 编译与 GPU 服务层 | FastAPI 无状态服务：CompileServer（CMake worker 队列）、GPUServer（GPU 绑定执行+ncu）、任务队列 API | `servers/compile.py`、`gpu.py`、`serve_api.py`、`management.py`、`cuda_env/CMakeLists.txt` |
| 6 | 资源管理层 | 服务客户端治理：1024 连接池 HTTP 单例、ManagedServer 子进程生命周期 | `resources/client.py`、`servers.py` |
| 7 | 数据与优化知识库层 | 数据集加载（基类/KernelBench/CUDA 工件变体/精度过滤）+ 出厂知识库 JSON 与 header/footer 指引 | `data/dataset.py`、`kernelbench.py`、`kernelbench_cuda.py`、`kernelblaster/optimization_database.json` |
| 8 | 配置与共享基础层 | 全库地基（fan-in 最高）：三层配置类、GPU 架构枚举探测、共享 CLI 参数 | `config/config.py`、`gpu_config.py`、`utils/arguments.py` |
| 9 | 容器基础设施层 | NGC PyTorch 25.01 单阶段构建、用户管理入口（dev/gpu/api 三模式）、依赖锁定 | `docker/Dockerfile`、`entrypoint.sh`、`requirements.txt` |
| 10 | 文档层 | README、贡献指南（DCO/SPDX）、论文图表索引 | `README.md`、`CONTRIBUTING.md`、`docs/figures/README.md` |

## 3. Key Concepts（核心概念）

1. **MAIC-RL**：不微调 LLM，而是把"学习"放进上下文——知识库随运行时经验更新，模型不动。
2. **Optimization Database（持久知识库）**：状态为中心的两张表——`StateProfile`（memory/compute/latency/hybrid bound 瓶颈状态）+ `OptimizationEntry`（预测/实测改进、置信分、使用计数）。出厂库含 3 个策展状态组 + 16 个瓶颈状态组共 73 条技术卡，但学习账本为空（confidence=0.5、usage=0、actual_speedup=null），等待运行时填充。
3. **Replay Buffer**：定长 FIFO 轨迹池（默认 100），聚合平均/极值 reward 与成功率，供反思 agent 回看。
4. **Trajectory**：每条 rollout 的逐步记录（状态、动作=优化技术、代码、周期数、预测/实测改进、reward）。
5. **NCU Profiling State**：`parse_ncu_metrics` 用正则从 NCU 日志提取 10 项指标（memory/compute throughput、occupancy、coalescing 等），构成状态判定输入；`annotate_ncu` 把周期数内联注释回 CUDA 源码。
6. **Textual-Gradient Prompt**：策略引导的 prompt 组装（标注 NCU + 原始代码 + 数据库知识 + 所选技术），用文本反馈替代梯度更新。
7. **Reward 设计**：reward = 实测改进 + 预测准确度奖励 − 变慢惩罚，同时激励"优化有效"和"预测诚实"。
8. **三级 LLM 反思回路**：PolicyEvaluation（评估预测 vs 实测）→ PerfGapAnalysis（硬件/代码/假设归因）→ ParameterUpdate（六类结构化 JSON 写回知识库）。
9. **Graph-based Workflow（LangGraph）**：`StateGraph(GraphState)` 单核心节点图 + 四个路由函数按开关分流；`GraphState` TypedDict 22 字段是全流程状态契约。
10. **探索-利用平衡**：按 relevance 加权随机选择优化技术，偏向知识库中高期望策略但保留探索。
11. **三级回退解析**：核心节点按 state → `data/kernelbench-cuda` 策展目录 → run 文件夹顺序定位输入，均缺则优雅跳过（不炸整批实验）。
12. **双服务架构**：编译（:2001）与 GPU 执行（:2002）分离的无状态 FastAPI 集群，可被多个实验进程共享；`ManagedServer` 负责按配置决定"连接既有服务"还是"自己拉起"。
13. **跨任务知识迁移**：run_RL 按 task_id/level/op_name 三元组把历史优化经验注入新问题的 user message——同一批次所有问题共用一个持续学习的知识库实例。
14. **单发对照与消融**：`opt_ncu_minimal.py` 不做状态匹配与策略选择，直接打包 prompt 单发 LLM，是验证"RL 探索+记忆到底带来多少增益"的消融基线。
15. **训练级产物的双重用途**：训练出的 `optimization_database.json` 既是框架记忆，也可独立用作通用性能工程 agent 的指引或带标注的模型训练数据。

## 4. Guided Tour（15 步学习路径）

这条路径按"从入口到闭环"的依赖顺序排列：前 7 步回答"一次优化怎么跑起来"，中间 4 步深入"RL 与记忆如何工作"，最后 4 步补齐"如何评测、如何部署"。建议边读边在仓库里打开对应文件对照。

1. **项目概览** — 读 `README.md` 与 `docs/figures/` 五张图，建立 MAIC-RL 全貌（流程图/知识库结构/状态组/记忆机制/优化分布）。
2. **一键入口** — `scripts/run_single_kernelblaster.sh`：默认 gpt-5-mini + L40S + level1 第 1 题，10 迭代 × 10 rollout × buffer 100，trap 双级清理服务。
3. **批量调度** — `scripts/run_RL.py`：Semaphore 并发调度 + 历史经验注入；共享参数见 `utils/arguments.py`。
4. **配置地基** — `config/config.py` 三层配置（ExperimentalFeatures/SystemConfig/WorkflowConfig）+ `gpu_config.py` 的 a100→sm_80 … b200→sm_100 架构映射。
5. **数据层** — `data/kernelbench_cuda.py`：索引 level{1,2,3} 问题目录，`init.cu`+`driver.cpp` 齐全才算条目；`dataset.py` 固定种子 50/50 切分。
6. **工作流编排** — `workflow/workflow.py` 的 `run_workflow`：组装输入、`asyncio.wait_for` 超时执行图；`graph/graph.py` 与 `graph/state.py` 定义图与状态契约。
7. **图核心节点** — `graph/nodes/optimization_rl_ncu.py`：三级回退解析输入，构造 agent 跑 RL 循环，落盘 `final_rl_cuda_perf.cu`。
8. **反馈基座** — `agents/feedback.py`：多 attempt × 并发生成线程的"生成→抽取→验证→反馈回填"模板；`opt_ncu_minimal.py` 是其单发消融对照。
9. **RL 主循环** — `agents/opt_ncu_rl.py`：并发 rollout、加权随机选技术、策略引导 prompt、reward 计算——项目灵魂。
10. **RL 组件** — `agents/rl_agents.py`：Trajectory 模型、ReplayBuffer、三个反思 agent 的策略更新闭环。
11. **知识库** — `agents/database.py` + `data/kernelblaster/optimization_database.json`：双 LLM agent 做状态归类与候选排序，实测回写，Markdown+JSON 双格式持久化。
12. **评测设施** — `scripts/run_baselines.py`（Eager）/`run_baselines_compile.py`（torch.compile）双基线 + `run_reprofile.py` 跨 GPU 复测。
13. **LLM 基础设施** — `agents/utils/query.py` 总路由（OpenAI/Azure 双客户端 + 裁剪 + 退避重试）、`batch_queue.py` 批聚合、`local_llm.py` Qwen2.5-Coder-32B 本地推理。
14. **服务集群** — `servers/compile.py`（CMake 模板见 `cuda_env/CMakeLists.txt`：清 PyTorch -gencode 后注入单一目标架构 + `-lineinfo`）、`servers/gpu.py`（CUDA_VISIBLE_DEVICES 绑定 + ncu 前缀）。
15. **服务化与部署** — `servers/serve_api.py` 任务队列（fan-out 全库第一）；`docker/entrypoint.sh` 三模式（dev/gpu/api）收官。

## 5. File Map（按层关键文件表）

| 层 | 文件 | 作用 | 复杂度 |
|---|---|---|---|
| 脚本 | `scripts/run_single_kernelblaster.sh` | 默认入口，环境变量+服务编排 | complex |
| 脚本 | `scripts/run_RL.py` | 批量实验主入口 | complex |
| 脚本 | `scripts/run_baselines.py` / `_compile.py` | Eager / torch.compile 基线（788/801 行） | complex |
| 脚本 | `scripts/run_reprofile.py` | 历史 success 产物 NCU 复测 | complex |
| Agent | `agents/opt_ncu_rl.py` | RL 主循环（灵魂） | complex |
| Agent | `agents/feedback.py` | 生成 agent 模板基类 | complex |
| Agent | `agents/rl_agents.py` | Trajectory/ReplayBuffer/反思 agent | complex |
| Agent | `agents/database.py` | 持久知识库核心 | complex |
| Agent | `agents/opt_ncu_minimal.py` | 单发对照（消融基线） | complex |
| Agent | `agents/reprofile.py` | 复测 agent | complex |
| Agent 工具 | `agents/utils/query.py` | LLM 查询总路由+重试 | complex |
| Agent 工具 | `agents/utils/annotate_ncu.py` | NCU 源码内联标注 | complex |
| Agent 工具 | `agents/utils/commands.py` | 远程编译/执行客户端 | complex |
| Agent 工具 | `agents/utils/batch_queue.py` / `local_llm.py` | 批处理队列 / 本地量化推理 | complex |
| 编排 | `workflow/workflow.py` | 顶层执行器+WorkflowResult | moderate |
| 编排 | `graph/graph.py` / `state.py` | 图构建路由 / 22 字段状态契约 | moderate |
| 编排 | `graph/nodes/optimization_rl_ncu.py` | 核心工作节点 | moderate |
| 服务 | `servers/compile.py` / `gpu.py` | 编译(:2001) / GPU(:2002) 服务 | complex |
| 服务 | `servers/serve_api.py` | 任务队列 API(:8000) | complex |
| 服务 | `servers/cuda_env/CMakeLists.txt` | 编译模板（架构注入+-lineinfo） | moderate |
| 资源 | `resources/client.py` / `servers.py` | 连接池单例 / 受管服务器 | simple/moderate |
| 数据 | `data/kernelbench_cuda.py` | CUDA 工件索引（driver+init 双全） | moderate |
| 数据 | `data/kernelblaster/optimization_database.json` | 出厂知识库（73 条技术卡） | complex |
| 配置 | `config/config.py` / `gpu_config.py` | 三层配置 / GPU 枚举 | moderate/simple |
| 容器 | `docker/Dockerfile` / `entrypoint.sh` | NGC 25.01 构建 / 三模式入口 | simple/moderate |

（路径前缀：`src/kernelblaster/` 省略。数据集本体 `data/kernelbench-cuda/` 184 对工件被 `.understandignore` 排除在图谱外。）

## 6. Complexity Hotspots（复杂度热点，新人谨慎区）

以下 12 个 complex 级文件是系统最难也最核心的部分：

1. **`agents/opt_ncu_rl.py`** — RL 主循环：并发 rollout、状态分析、加权随机探索、reward 三项式、周期性策略更新全部交织。**注意**：改动任何一步都会影响学习动态，先读懂 `generate_strategy_guided_prompt` 再动手。
2. **`agents/database.py`** — 知识库双表 + 双 LLM agent 归类 + 双格式持久化。**注意**：schema 是为学习闭环设计的，回写路径的并发安全要看清。
3. **`agents/rl_agents.py`** — 三个反思 agent 链式触发，ParameterUpdate 会**实际写回**知识库（六类 JSON 更新）。**注意**：这是"学习"发生的地方，bad update 会污染后续所有任务。
4. **`agents/feedback.py`** — 所有生成 agent 的模板基类：多 attempt × 并发线程、断点续跑（`.finished`/`success_*` 检测）。**注意**：子类只需实现 `get_feedback`，别绕过外层循环。
5. **`agents/utils/query.py`** — 双客户端初始化、34 万字符裁剪、按错误类型分类的抖动退避。**注意**：环境变量在**模块加载时**初始化，导入顺序敏感。
6. **`agents/utils/annotate_ncu.py`** — source/details 双 DataFrame 按 kernel 对齐 + 周期内联回源码。**注意**：喂给 LLM 的反馈形态在此定形，格式改动影响所有 prompt。
7. **`agents/utils/commands.py`** — 编译+执行+按关键字判定的复合客户端流程（重试/超时）。**注意**：远程链路的失败模式都在这暴露。
8. **`servers/compile.py` + `cuda_env/CMakeLists.txt`** — CMake worker 队列 + 架构旗标手术（清除 PyTorch 注入的 `-gencode` 再注入单目标架构）。**注意**：`-lineinfo` 供 NCU 关联源码但有计时开销，别乱删。
9. **`servers/gpu.py`** — worker 按 GPU ID 绑定 `CUDA_VISIBLE_DEVICES` 执行、ncu/nsys 前缀注入。**注意**：远程剖析全靠它，stdout/stderr 收集是唯一诊断通道。
10. **`servers/serve_api.py`** — fan-out 全库第一（26）：任务队列 + 启动时历史状态恢复。**注意**：状态恢复逻辑与 agent 状态聚合耦合。
11. **`scripts/run_baselines.py` / `_compile.py`** — 788/801 行同构双基线：动态加载 problem.py、CUDA Event 计时、`--ncu` 子进程模式。**注意**：论文加速比的分母在此，任何计时口径改动都影响可比性。
12. **`data/kernelblaster/optimization_database.json`** — 出厂知识库：73 条技术卡但学习账本全空（confidence=0.5/usage=0/speedup=null）。**注意**：不要手填字段——schema 齐全正是为了运行时回写；header/footer 的哲学（未知改进记 0%、要区间不要点估计）是理解设计意图的钥匙。

**上手建议**：第一周跑通 Quick Start（单问题 L1）并对照 Tour 步骤 2-7 读链路，重点观察 `out/` 目录下的 prompt 落盘与 metrics.jsonl，直观感受"生成→验证→反馈"循环；第二周精读 opt_ncu_rl.py + database.py + rl_agents.py 的"探索-记忆-更新"三角，并用 `opt_ncu_minimal.py` 做对照理解 RL 增益来源；改代码前先看 CONTRIBUTING.md（DCO 签署 + SPDX Apache-2.0 头 + PEP 8），改服务端代码前先读懂 CMake 模板的架构旗标手术。另注意运行环境坑：`nohup` 长任务需防 shell 超时、GPU 服务器健康探测容忍僵尸进程、`.gitmodules` 为空（KernelBench 基线需手动 clone 到 `data/KernelBench`）。
