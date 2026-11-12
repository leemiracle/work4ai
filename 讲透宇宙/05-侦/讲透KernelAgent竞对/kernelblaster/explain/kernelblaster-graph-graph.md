# KernelBlaster 图编排三件套深解：graph.py / optimization_rl_ncu.py / state.py

> 层级定位：orchestration 层（图编排与工作流层）。依据 `.understand-anything/knowledge-graph.json`，三文件同属 `layer:orchestration`，其上是 `workflow/workflow.py` 执行器，其下是 `agents/` 智能体群。

## ① 角色定位：基于 LangGraph 的工作流骨架（依赖库，非自研）

三件套回答一个问题：**"拿到一个 kernel 优化任务后，系统按什么顺序做事、中间状态放在哪"**。执行引擎直接用 **LangGraph 库**（`docker/requirements.txt` 钉版 `langgraph==0.2.68`），非自研：`graph.py` 第 16 行 `from langgraph.graph import StateGraph, START, END` 是唯一框架依赖。自研的只有三样东西——状态契约（state.py）、图节点（nodes/）、路由决策函数。

分工：`state.py` 定义全局状态 `GraphState`（所有节点读写的"共享黑板"）；`nodes/optimization_rl_ncu.py` 是真正干活的节点；`graph.py` 的 `build_graph()` 把两者组装成可执行图并 `compile()`。

理解这套图的关键机制是 **LangGraph 的状态合并语义**：每个节点收到完整 `GraphState` 作入参，但只需返回一个"增量 dict"（如 `{"rl_ncu_cuda_fp": ...}`），框架自动把增量合并回全局状态再传给后继节点——所以节点代码里看不到整状态的组装，写回动作极轻。这也是为什么 `GraphState` 用 TypedDict 而非 dataclass：LangGraph 按键覆盖合并，TypedDict 恰好是"带类型注解的 dict"。

## ② graph.py 内部结构：单节点图 + 四个"化石"路由

**当前实际拓扑极简**：`build_graph()` 只注册一个节点 `"Baseline RL Optimization"`（处理函数即 `optimization_rl_ncu`），连边 `START → Baseline RL Optimization → END`，compile 后返回。执行序因此是一条直线：`workflow.py:114` 调 `build_graph()`，128 行 `workflow.ainvoke(workflow_input)` 异步触发——传入初始 state（含 folder/user_message/RL 参数），图启动 → 唯一节点跑完整个 RL 优化 → 返回终态。一个请求就是一次图执行；节点内部耗时完全由 `rl_iterations` 与 agent 决定，图本身零循环零分支。

**四个路由函数是历史遗留**：`route_kernel_generation` / `route_baseline_or_generation` / `route_ncu_benchmark` / `route_original_cuda_kernel` 会返回 "Generate CUDA"、"Perf Optimization"、"RL Optimization" 等节点名，但全仓 grep 证实这些函数**无任何调用点**，也未通过 `add_conditional_edges` 挂接——它们是多节点旧图（生成→perf→bench→NCU 流水线）收缩成单节点 RL 图后的化石。其中 `route_baseline_or_generation`（复杂度 complex）保留了完整决策逻辑：实验开关 `OPT_RL_NCU` 开启且 state 含 RL 三参数时，用正则从 `user_message`/`folder` 提取 problem 编号，查 `baseline_selector` 找策展基线，找到走 RL、找不到强制 `run_cuda=True` 回退传统生成。读它可理解设计意图，但改图不用改它。

## ③ optimization_rl_ncu.py 数据流：problem 文件夹 → final_rl_cuda_perf.cu

输入是一个 `GraphState`，核心是 `folder`（形如 `.../level1/<problem_name>/`）。流程五步：

1. **三级回退解析输入文件**：`cuda_fp`（待优化 kernel）按 state → 策展目录 `data/kernelbench-cuda/<level>/<problem>/init.cu` → run 文件夹 `init.cu` 顺序找；`test_code_fp`（正确性判据）同样三级找 `driver.cpp`。均缺失则**优雅跳过**——log error 后返回 `{"rl_ncu_cuda_fp": None}`，不抛异常（注释明言"curated CUDA files are required"，与竞对情报"KB 仅 3 策展状态组"呼应：策展数据是硬依赖）。
2. `save_state_to_json` 落盘 `state.json`（断点可见）。
3. 构造 `FeedbackConfig`（model/gpu/`num_pgen=4`——注释说 RL 节点用更少并行 coder 因为"更战略性"）+ `RLNCUAgent`（rollout 步数/buffer 大小/更新频率取自 state，默认 5/100/3；`database` 接 state 的 `shared_optimization_database` 实现跨 problem 共享经验）。
4. `await agent.initialize()` → 设 `num_rl_iterations`（默认 10，覆盖 agent 内部默认 50）→ `await agent.run()`。`RLNCUAgent` 继承 `FeedbackAgent`，`run()` 返回 `Path`；其内部把 `num_rl_iterations` 轮迭代拆成 `asyncio.create_task` 并发执行，每轮走 `run_rollout(initial_code, initial_state) -> Trajectory` 采样轨迹、以 NCU profile 反馈为奖励信号更新策略——真正的 RL 循环（rollout/奖励/回放 buffer/经验入库）全在 `agents/opt_ncu_rl.py`，节点只做编排与文件搬运。
5. **输出**：最优 kernel 复制为 `base_folder/final_rl_cuda_perf.cu`，返回 `{"rl_ncu_cuda_fp": best_filename}` 合并回 state。

## ④ state.py：22 字段 TypedDict + 三个工具函数

`GraphState` 四组字段：**配置**（model、gpu）；**流程开关**（run_cuda / run_cuda_perf / run_cuda_bench / run_cuda_perf_bench + retry_failed）；**RL 超参**（rl_iterations / rl_rollout_steps / rl_buffer_size / rl_update_frequency——三者同时在场即被路由视为"RL 模式"信号）；**文件指针族**（filepath、test_code_fp、cuda_fp → cuda_bench_fp → ncu_cuda_fp → ncu_cuda_bench_fp → rl_ncu_cuda_fp，串起从生成到 RL 优化的产物链）。另有 user_message/folder/logger/reference_code。

工具函数：`save_state_to_json` 跳过不可序列化的 logger/shared_optimization_database，Path 转 resolve 字符串；`load_state_from_json` 的巧思是 `read_fp=True` 时把每个 `X_fp` 字段指向的文件内容读进去后缀的同名字段（`cuda_fp` → `cuda`），实现"状态+产物一键恢复"；`compare_states` 忽略 logger 逐键比对。

## ⑤ 外部连接

- **上游**：`workflow.py:run_workflow`（调 build_graph + ainvoke，带超时与并发控制）；`servers/serve_api.py` 直接 import state.py（API 侧复用状态契约）；`graph/__init__.py` re-export。
- **下游**：`agents/opt_ncu_rl.py:RLNCUAgent`（继承 FeedbackAgent，`run()->Path`）、`agents/__init__.py:FeedbackConfig`、`config`（GPUType/实验开关）。
- **数据**：`data/kernelbench-cuda` 策展库（driver.cpp+init.cu per problem），图谱另记 `README.md` 有 documents 边指向本节点模块，是官方文档重点描写的组件。

## ⑥ 设计决策与新人提示

1. **图很薄、Agent 很厚**：LangGraph 只负责"何时调谁"，所有智能在 agents 层。改优化策略→去 opt_ncu_rl.py；只有改流程拓扑才动 graph.py。
2. **优雅降级优于崩溃**：缺策展文件返回 None 跳过该 problem，批量跑 165 题时个别缺数据不炸全局。配合"三级回退"（state → 策展库 → run 文件夹），既支持复用外部真值，也容忍手工放置的文件。
3. **状态持久化双保险**：进 agent 前存一次 `state.json`、结束时带 `rl_ncu_cuda_fp` 再存一次——中途崩溃也能从 JSON 恢复现场（`load_state_from_json(read_fp=True)` 连产物内容一起恢复）。
4. **陷阱一**：TypedDict 未设 `total=False`，22 键名义上全必填，初始化 state 缺键时路由函数 `state["run_cuda"]` 直接 KeyError（所以路由函数大量用 `.get`，直取和 .get 混用是历史伤疤）。
5. **陷阱二**：`route_*` 是死代码，读时别当成现行控制流；想恢复"生成→perf→bench"多节点流水线需自行 `add_conditional_edges` 把这四个函数挂回去。
6. **陷阱三**：`repo_root = Path(__file__).parents[4]` 假设容器内固定安装路径 `/kernelblaster`，换布局会指错策展根，可用 state 的 `kernelbench_cuda_root` 键覆盖。
7. **读代码路线建议**：graph.py（5 分钟看懂骨架）→ state.py（字段表）→ optimization_rl_ncu.py（胶水层）→ opt_ncu_rl.py（真正的深度所在）。
