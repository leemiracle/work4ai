# 01 · parallel_state.py——Megatron 并行基座（全进程组中枢）

> 源文件：`megatron/core/parallel_state.py`（2773 行，全仓被依赖最重的单文件）。知识图谱将其标注为「一切并行策略的单一事实来源」，入边 87 条，是图谱中入度最高的 file 节点之一。

## ① 角色定位：这个子系统解决什么问题

Megatron-LM 的本质是把一个 Transformer 训练/推理作业切到成百上千张 GPU 上，切法不止一种：张量并行（TP）切权重矩阵、流水线并行（PP）切层、上下文并行（CP）切序列、数据并行（DP）复制整个模型、专家并行（EP）切 MoE 专家、广义张量并行（GTP/权重重计算分片）再叠一层权重维度。同一个全局 rank（比如 rank 37）在不同切法下属于完全不同的通信组。`parallel_state` 要解决的问题就一句话：**在进程启动时把 world_size 按 order 轴序一次性切分成几十种正交进程组，之后全框架任何模块要通信，都只问它"我在哪个组、我是组内几号、组大小多少"**。

它不做任何梯度/激活通信本身——那些在 `tensor_parallel`、`distributed`、`pipeline_parallel` 里——它只维护"组的身份"。没有它，每一次 all-reduce 都得现场算一遍自己该和谁通信。

## ② 内部结构：关键类/函数与行号锚

**模块级全局变量区（`parallel_state.py:27-164`）**：约 40 个模块私有全局变量，命名即注释——`_TENSOR_MODEL_PARALLEL_GROUP`（:28）、`_GTP_WEIGHT_REMAT_GROUP`（:30）、`_PIPELINE_MODEL_PARALLEL_GROUP`（:33）、`_EMBEDDING_GROUP`（:38）、`_CONTEXT_PARALLEL_GROUP`（:123）、`_DYNAMIC_DP_CP_GROUPS = {}`（:130，按运行时 CP 尺寸索引的字典）。专家组有一套完整镜像命名，约定写在 `parallel_state.py:48-53` 的注释块：`_EXPERT_MODEL` 表示按专家数切、`_EXPERT_TENSOR` 表示切张量、`_EXPERT_DATA` 表示复制权重。

**rank 分组的数学核心（`generate_masked_orthogonal_rank_groups`，`parallel_state.py:268`）**：函数 docstring 给出正交分解方程 `global_rank = tp_rank + dp_rank*tp_size + pp_rank*tp_size*dp_size`（:288-294），用 mask 选择哪些轴进组。例如 mask=[True,False,True] 就是 tp-dp 合并组。**Megatron 一切并行分组都由这一个函数生成**（图谱节点 summary 原话）。

**RankGenerator（`parallel_state.py:487`）**：把各轴尺寸+order 字符串封装成分组生成器。两个硬约束值得注意：`assert ep == 1 or cp == 1`（:501）——一个生成器里 EP 和 CP 不能同时大于 1，CP 只属于 dense 生成器、EP 只属于 expert 生成器；order 里漏写尺寸大于 1 的轴会直接 RuntimeError（:524-529）。`get_gtp_ranks`（:572）是 GTP 轴的专用出口。

**轴序注入（`_inject_gtp_remat_axis`，`parallel_state.py:602`）**：把 `gtp_remat` 轴插进 order 串。注释讲清了局部性原理（:604-610）：**最左 token 步长最小、rank 最相邻**；dense 网格插在 cp 之后（`tp-cp-gtp_remat-ep-dp-pp`），expert 网格插在 ep 之后，让更重的 MoE EP all-to-all 保持更局部。这是一个"字符串顺序=物理拓扑亲和性"的精巧设计。

**初始化总入口（`initialize_model_parallel`，`parallel_state.py:622`）**：签名 26 个参数（:622-648），默认 order 为 `"tp-cp-ep-dp-pp"`（:638）。千行巨函数，创建顺序依次是：

1. 尺寸校验：`model_size = tp*pp*cp*gtp_remat`（:848-853），world_size 整除检查（:855-856），`data_parallel_size = world_size // model_size`（:861）；GTP 与多 DistOpt 实例互斥断言（:840-844）；虚拟流水线要求 pp>1（:863-867）。
2. 双 RankGenerator：dense 的（:893-903，ep=1）和 expert 的（:904-928），并断言两者的 pp 分组必须一致（:932-935）。
3. **GTP 权重分片组最先建**（:965-984），注释点明 GTP 与 CP-DP 域重叠的原因：GTP 只切权重、CP 只切激活，二者独立可共享 rank（:967-968）；GTP>1 时强制关掉 gloo 组（:987-988，GTP 优化器走 DCP）。
4. **dp-cp 组紧随其后**（:998），注释（:991-993）解释了为什么它必须最先于其它组建：NCCL COLLNET/SHARP 硬件限制只青睐**最先创建**的通信组。
5. SHARP barrier+开关清理（:1043-1058）→ 动态 CP 组（:1085-1110）→ CP 组（:1175）→ TP 组（:1220-1233）→ PP+embedding+position embedding 组（:1237-1351，其中 PP 可选 UCC 后端，:1249-1298 设置一大串 UCX/UCC 环境变量）→ TP×DP 组（:1353）→ 全套专家组（:1396-1580）→ DistOpt 实例组（:1616）→ 全局内存 buffer（:1641）。

**访问器家族（`parallel_state.py:1743-2580`）**：约 95 个 `get_*` 查询函数（图谱计数），全部模式一致——`check_initialized=True` 断言全局变量非 None 后返回。典型如 `get_tensor_model_parallel_group`（:1766）、`get_gtp_weight_remat_group`（:1775）、`get_data_parallel_group`（:1820，按 with_context_parallel/with_gtp_remat/partial 组合返回**不同粒度**的 DP 组——这个函数一个顶五个）。

**销毁（`destroy_model_parallel`，`parallel_state.py:2584`）**：把全部全局变量置 None；对 gloo 组显式调 `torch.distributed.destroy_process_group`（先查 `pg_map` 确认还活着，:2705-2712 等）；结尾两句最见功力——开头延迟导入 `nccl_ep_finalize()` 释放 TE 的 NCCL EP 上下文（:2587-2596，注释解释：TE 的 atexit 钩子若晚于 dist 销毁会撞 "corrupted comm object"），末行 `SymmetricMemoryManager.destroy()`（:2773）。

## ③ 外部连接：与哪些子系统互依

图谱入边 87 条，消费方 TOP5：`megatron/core/transformer`（13 条）、`megatron/core/inference`（7 条）、`megatron/core/models` 与 `megatron/core/tensor_parallel`（各 5 条）、`megatron/core/distributed`（4 条）。这印证了它的基座地位：模型装配、算子层通信、DDP 梯度规约、推理引擎全部向下依赖它。

两个特殊依赖方向值得注意：其一，`parallel_state.py:14` 反向 `from megatron.core.inference.symmetric_memory import SymmetricMemoryManager`——基座模块 import 推理子系统，制造了 parallel_state ↔ inference 的双向纠缠（destroy 时要终结对称内存）。其二，官方迁移方向是 `ProcessGroupCollection`（`megatron/core/process_groups_config.py:27`）：dataclass 把 tp/pp/mp/embd/cp/ep 等二十多个组打包成**显式传参**的对象。仓根 CLAUDE.md 明文规定：mcore 生产代码**禁止新增**对 `parallel_state.get_*_group()` 的直接调用，只允许 `parallel_state.py`、`process_groups_config.py`、bootstrap 代码等兼容点——这是"全局单例 → 依赖注入"的进行时重构（标注推断：新旧两套并存，访问器仍约 95 个说明迁移远未完成）。

## ④ 数据流：一次典型调用的路径

以 8 卡 TP=2/PP=2、order=`tp-cp-ep-dp-pp` 为例走一遍：

1. `torch.distributed` 先初始化默认组，每个进程拿到全局 rank。
2. 训练脚本（如 `megatron/training/initialize.py`）调 `initialize_model_parallel(2, 2)`：RankGenerator 按 order 展开 2×2×2 网格，`get_ranks('tp')` 得到 [[0,2],[1,3],[4,6],[5,7]] 等 4 个 TP 组；`create_group`（:231）对每个组调 `torch.distributed.new_group`——注意**所有 rank 都要迭代所有组**（:1141 注释），new_group 本身是集合调用；只有 `rank in ranks` 时才把返回值写进本进程的全局变量（:263），并追加进 `_global_process_group_list`（:164）供 `update_pg_timeout`（:202）批量改超时。
3. 训练循环里，`ColumnParallelLinear` 做 all-reduce 前调 `get_tensor_model_parallel_group()` 拿组句柄；PP 调度器用 `is_pipeline_first_stage`（:2072）/`get_pipeline_model_parallel_next_rank`（:2182）决定收发方向；MoE 层则换用 `get_expert_tensor_parallel_group`（:2365）等专家组。
4. 作业结束或需要重组拓扑时 `destroy_model_parallel()` 清场，全部变量复位为 None。

## ⑤ 设计决策：为什么这么设计

**为什么用约 40 个模块级全局变量而不是一个对象？** 历史路径：这是 Megatron V1 时代延续下来的形态，全框架上百处直接 `from megatron.core import parallel_state` 使用，改对象传参要动整个生态。官方自己的解法印证了这一点——不动旧变量，新加 `ProcessGroupCollection` 显式传参路线并写进贡献规范（推断依据：CLAUDE.md 的 advisory 条款 + dataclass 注释里"pass through"的示例）。

**为什么创建顺序有讲究？** 两组证据直接写在代码注释里：SHARP/COLLNET 只认最先创建的组（:991-993），所以 dp-cp 组抢在所有组之前；UCC 后端能吃满 IB 带宽且零 SM 占用（:1250-1256），PP 通信重的场景值得整段环境变量配置。**顺序在这里不是风格问题，是硬件语义。**

**为什么 EP 和 CP 塞不进同一个 RankGenerator？** :501 的断言背后是 MoE 的现实：EP 的 all-to-all 要求专家维连续，CP 的 KV 交换要求序列维连续，两者对 order 的要求冲突，于是干脆拆成 dense/expert 两套生成器，再用 :932 的断言钉住"两套生成器的 PP 分组必须相同"这一交汇点（推断：这是保证 dense 层和 MoE 层能共存于同一条流水线的前提）。

**为什么 destroy 里 gloo 组显式销毁而 NCCL 组只置 None？** NCCL 组的生命周期归 `torch.distributed` 默认组管辖，gloo 组是 Megatron 额外创建的备份通道，需要自己负责到底；`pg_map` 存活检查防止重复销毁（:2705-2712）。

## ⑥ 新人提示：坑/入口/阅读顺序

- **入口顺序**：先读 :27-164 变量区（当目录用）→ `generate_masked_orthogonal_rank_groups`（:268，手算一个 2×3×4 例子）→ `RankGenerator`（:487）→ 跳着读 `initialize_model_parallel` 的注释而非全读（千行函数，按上面第②节给出的 5 段顺序索引行号）→ `destroy_model_parallel`（:2584）收尾。
- **最大的坑：初始化前查询**。所有 `get_*` 默认 `check_initialized=True` 会断言崩溃，但传 False 的静默 None 更危险——下游拿到 None 组常见报错是 `ProcessGroupNCCL` 空指针而非"未初始化"，排查时先查 `is_initialized()`（:1743）。
- **重复初始化必炸**：每组创建前都有 `assert _XXX_GROUP is None, "... is already initialized"`（如 :1224-1226），单元测试里切换拓扑必须先 destroy。
- **get_data_parallel_group 语义陷阱**：`with_context_parallel`/`with_gtp_remat`/`partial_data_parallel` 三个开关组合出不同粒度的组（:1820-1870），梯度规约、数据分发、DistOpt 分片用的是**不同**的 DP 组，抄别的模块调用前先想清楚自己要哪个语义。
- **别再加全局组读取**：写新 mcore 代码时按仓规走 `ProcessGroupCollection` 传参（`process_groups_config.py:27`），PR review 会拦直接读并行态的新代码。
- `order` 字符串可配（`--no-pp-last` 等场景），但 :929-935 的断言限制：非 pp-last 排序时必须保证 MoE 层与 dense 层 data_parallel_size 相同，自定义 order 前先过这条。
