# 03 · pipeline DAG 引擎：建图、CSE 与 executor 流着色

## 角色定位

图谱 L07「pipeline DAG执行引擎」是全库最大的节点域（195 节点/179 文件），是用户 API 与执行的中枢：pipeline.h/cc 负责建图与输出整形，graph/op_graph2 是 DAG 表示、cse 做公共子表达式消除，operator/ 是算子框架（operator.h 98 处 import 居全库前列），executor/ 目录五代执行器并存，executor2 的 stream_assignment 把 CUDA 流分配建模为图着色——GPU 管线执行器的经典设计（NOTES-DIGEST batch-135 甄别）。Python 侧 nvidia.dali 的 Pipeline 类、C API、TF 插件都以序列化 OpSpec 的形式把图交给这层。

## 内部结构

建图入口 `Pipeline::AddOperatorImpl`（pipeline.cc:377）：查重实例名（:383）、NoPrune schema 自动 preserve（:396）、ExternalSource 设 preserve_name 防 CSE 吞并（:399）、序列化前快照 spec（:403）、"support" 设备弃用警告并归一为 cpu（:408-414）、按 device/输出设备推断 requires_gpu_（:416-422）。`Build` 三重载（pipeline.cc:557/561/566）：先 GetExecutor 装配执行器（:599-607），再对每个 pipeline 输出查 edge_names_——缺 CPU/GPU 版本就 ToCPU/ToGPU 转换，非 contiguous 就 `AddMakeContiguousNode` 插入整形节点（cpu 分支 :615-628，gpu 分支 :630-643；节点名三选一 `__MakeContiguous_CpuToCpu_/CpuToGpu_/GpuToGpu_`，pipeline.cc:1142-1144）。图本体 op_graph2.h：OpNode/DataNode/DataEdge 三元组（op_graph2.h:42/84/77）、OpGraph（:121）与一次性 Builder（:244，GetGraph(prune) :261）。CSE 在 graph/cse.cc：`OpSpecCSEKey` 把 OpSpec 的关键子集序列化成 protobuf 字符串作合并键（cse.cc:30），输出名用序号占位（:45-47）实现"同构不同名"等价，schema 标了 ignore_cmp 的参数跳过比较（:54-57），入口 `EliminateCommonSubgraphs`（cse.h:84）。

算子框架两层：`OperatorBase`（operator.h:76）定 Setup/Run 模板方法（:88/:98），子类实现纯虚 SetupImpl/RunImpl（:117/:123），另有 HasContiguousOutputs（:136）与 checkpoint 四件套 Save/Restore/Serialize/Deserialize（:186-213）；OpSchema 是算子自描述体系核心（op_schema.cc），AddArg/AddArgumentImpl（:432/:401）注册参数、内置 `_random_state`（:558）支撑随机算子 checkpoint。执行器抽象 ExecutorBase（executor.h:44）定 9 个纯虚生命周期（:47-60）。executor_factory.cc 按 ExecutorType 分派六种实现（GetExecutorImpl，:107-136）：Dynamic→exec2::Executor2；AsyncPipelined 可被环境变量 DALI_USE_EXEC2 强制切到 Executor2（ForceExec2 :97-102，切换时 stderr 打"!!! Forced use of Executor 2.0 !!!"）。新一代 Executor2 用 PIMPL（exec2.h:128-129，Impl 集中于 exec2.cc:69），其 ExecGraph 三步编译：`Lower` 从 OpGraph 降级并接管算子实例（exec_graph_lowering.cc:25）、`Analyze` 标注 MakeContiguous 模式/pinned 缓冲/并行消费者（exec_graph_analysis.cc:208-215）、`Sort` 拓扑排序（:199）。执行单元 ExecNode"持有算子实例并管理 task 生命周期"（exec_graph.h:130-138），经 ExecNodeTask 包成 tasking::Task（exec_node_task.h:34/51）。

## 外部连接

上游：Python pipeline.py（单文件 2500 行，NOTES batch-27）与 c_api 以 proto 序列化进图；op_schema 的 CalculateOutputs/OutputDtypeFn 支撑前端动态类型推断（NOTES batch-49）。下游：data/tensor.h 的运行期张量与 workspace.h 的 WorkspaceBase（L02）承载算子间数据；graph2dot.cc 可把图导出 dot 可视化；pipelined_executor.h 的 stage_outputs_ 注释（:59-70）解释了"分阶段预取需对每阶段输出排队，否则覆写仍在消费的数据"——这是 prefetch_queue_depth={2,2}（:43）的由来。

## 数据流

一次完整流转：Python define → OpSpec 列表 → Builder 建 OpGraph（prune 无用节点）→ CSE 折叠同构子图 → Build() 选执行器+自动插 MakeContiguous → Executor2::Build 调 Lower 生成 ExecGraph → Sort/Analyze/Validate → StreamAssignment 着色 → 每个 iteration 为活跃 ExecNode 造 tasking::Task，经线程池按依赖调度 → Workspace 装数据 → Outputs/ShareOutputs 交付。

## 设计决策

1. 流分配三档策略（stream_assignment.h:70/105/182）：Single 全局单流、PerBackend 混合/GPU 各一流（注释 :99-104 写明 0/1/2 三种结果）、PerOperator 图着色。着色算法在 ProcessNode 注释（:263-287）：每节点维护 ready_streams（流 id→use count 快照），拓扑序逐点"取最小可用流 id，无则开新流，并集更新 ready 集，过期 use count 的流拒绝复用"——这是 interval graph 贪心着色，保证生产者-消费者共享流（天然同步）、无依赖分支各占流（并行）。
2. NeedsStream 判定（stream_assignment.h:36）：CPU 节点仅当消费 GPU 输入才占流——把"内存可见性"而非"算子类型"作为流分配依据。
3. CSE 键用 protobuf 序列化而非手工比较：schema 演进时只需改 proto 定义；代价是每次建图都要序列化全部算子。
4. MakeContiguous 自动插入（pipeline.cc:620-640）：对用户透明地保证管线输出 dense，代价是图里多了隐形节点（调试时用 graph2dot 才看得见）。
5. 五代执行器共存+工厂切换+环境变量逃生门：AsyncPipelined 是稳定默认，Executor2 是未来（Dynamic 类型直达），DALI_USE_EXEC2 提供 A/B 通道（executor_factory.cc:97-122）。
6. legacy "support" 设备不硬拒绝而是警告+归一（pipeline.cc:408-414）：兼容老脚本优先于 API 洁癖。

## 新人提示

读执行链建议顺序：pipeline.cc:377（AddOperatorImpl）→ :557（Build）→ executor.h:44 → executor_factory.cc:107 → exec2.cc:69（Impl）→ stream_assignment.h:182。调试先用 DALI_USE_EXEC2=1 对比新旧执行器行为是否一致，再怀疑算子；图结构问题用 graph2dot 导出可视化。改动 schema 参数时注意 ignore_cmp 标志——它直接决定 CSE 是否把两个实例当同一个（cse.cc:54）。stream_assignment_test.cc 有着色行为的黄金样例；exec2_test.cc 覆盖降级与分析阶段。查"输出为什么多了一个节点"先想 MakeContiguous 自动插入（pipeline.cc:672 有跳过判定）。Executor2 的配置还有 DALI_EXEC2_MAX_THREADS/DALI_EXEC2_NUM_THREADS 两个旋钮（executor_factory.cc:41/53）。
