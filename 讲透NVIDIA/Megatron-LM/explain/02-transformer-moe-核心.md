# 02 · transformer 层装配与 MoE 全家桶——spec 系统与专家路由

> 覆盖 `megatron/core/transformer/`（transformer_layer.py 2788 行、transformer_config.py 4034 行、transformer_block.py 890 行）与 `transformer/moe/` 全目录（13 个主文件 13161 行）。知识图谱把 MoELayer 标注为「MoE 的编排中枢」、TopKRouter 为「22 方法训练路由器」。

## ① 角色定位：这个子系统解决什么问题

两个问题。**第一，同一套 Transformer 骨架要能装出几十种模型**：GPT/DeepSeek/Qwen/Mixtral 的差别只在每层用什么注意力、什么 MLP、什么 norm，骨架（残差、bda、重计算、量化上下文）完全一致。手写 if-else 组合会爆炸，所以 Megatron 用 **spec（模块规格）系统**把"装配图纸"和数据结构分离——骨架代码只认槽位，槽位里填什么由 spec 决定，且 spec 可以延迟到运行时动态 import。

**第二，MoE 把"一层"变成了"一个小分布式系统"**：每个 token 要经 router 打分选专家、经 dispatcher 跨 EP 组搬运、被本地专家算完、再搬回来加权合并。这些步骤横跨 TP/EP/DP 三种通信域，还叠加了负载均衡损失、共享专家、CUDA graph、PP 激活 offload（paged stash）等正交特性。`moe/` 目录就是这个小系统的完整实现，README 自称 "production-ready stack"。

## ② 内部结构：关键类/函数与行号锚

**spec 系统（`transformer/spec_utils.py`）**：核心是 `ModuleSpec` dataclass（`spec_utils.py:10`）——`module` 字段既可以是 `(模块路径, 类名)` 元组也可以是已导入的类，外加 `params`/`submodules`/`metainfo`；`__call__`（:38）让它可以像构造器一样被调用。`import_module`（:41）用 `__import__` 动态解析路径元组，`build_module`（:76）完成实例化。**延迟导入是 spec 的灵魂**：同一份 spec 文件可以在 TE 不存在时构建出纯 local 实现的模型。

**层装配链**：`models/gpt/gpt_layer_specs.py:444` 的 `get_gpt_layer_local_spec` 是最典型入口——`ModuleSpec(module=TransformerLayer, submodules=get_gpt_layer_local_submodules(...))`。MoE 与否由 `get_mlp_module_spec_for_backend`（gpt_layer_specs.py:505）分岔：`num_experts=None` 走 dense MLP，否则转投 `get_moe_module_spec_for_backend`；:527-539 的弃用警告还透露了一次 API 演进——`use_te_op_fuser` 从参数变成了 backend provider 的决定。`TransformerLayer`（`transformer_layer.py:329`，同时继承 GraphableMegatronModule/BaseTransformerLayer/TwoStageAttentionLayer）持有 `TransformerLayerSubmodules` 全套槽位（norm/注意力/mhc/交叉注意力/bda，图谱节点原话）；`TransformerBlock`（`transformer_block.py:268`）在 `_build_layers`（:339）里按 PP/VP 布局逐层消费 spec。

**MoE 协议层（`moe/moe_layer.py`）**：先定义五个 Protocol——`ExpertsInterface`（:69）、`ExpertsBuilder`（:87）、`SharedExpertsInterface`（:101）、`SharedExpertsBuilder`（:113）、`RouterInterface`（:126）+ `MoESubmodules`（:166）。`BaseMoELayer`（:174）之下是主角 `MoELayer`（:227，865 行），forward 被拆成五个可被 CUDA graph 部分捕获的方法：`preprocess`（:506）/`dispatch`（:546）/`shared_experts_compute`（:558）/`routed_experts_compute`（:587）/combine。两个 autograd Function 藏在文件尾：`_RecordExpertDgradCompletion`（:804）与 `_RegisterDelayedWgradForExperts`（:827），实现 wgrad 延迟与 dispatch 反向重叠。

**路由器（`moe/router.py`）**：`Router` 抽象基类（:42）→ `TopKRouter`（:158）。命名约定写在 docstring：logits→scores→probs→routing_map 四阶段。负载均衡是全家桶：aux loss（DeepSeek 系 sigmoid+scaled 归一）、sinkhorn（:945）、quantile balancing（:947，用 per-expert 偏置 `qb_beta` 替代 aux loss，注册 buffer 于 :251-276）、expert bias（`moe_router_enable_expert_bias`，buffer 在 :200-219）、z-loss、hash 路由（V4 式前三层哈希路由，`is_hash_layer` 标志 + `hash_moe_layer_threshold` 参数贯穿构造链）。score_function 三选一：softmax/sigmoid/sqrtsoftplus（:830-841）。推理版 `InferenceTopKRouter` 在 :1132。

**派发器与专家**：`token_dispatcher.py` 四层——`MoETokenDispatcher`（:64）基类、`MoEAllGatherTokenDispatcher`（:233）、`MoEAlltoAllTokenDispatcher`（:375）、`MoEFlexTokenDispatcher`（:1809，DeepEP/HybridEP 后端）。推理专用在 `token_dispatcher_inference.py`（NCCLAllGatherDispatcher/NVLSAllGatherVDispatcher）。专家本体在 `experts.py`：`TEGroupedMLP`（:233）与 `SequentialMLP`（:1642）。共享专家 `shared_experts.py`（661 行）。

**paged_stash 双实现**——这是 2026/01 的 "Pipeline-aware fine-grained activation offloading"：
- Python 管理面（`moe/paged_stash.py`，1357 行）：`PagedStashBuffer`（:60，页表/自由表/dtype）、`PagedTensor`（:167）、一对 autograd 钩子 `PipelinePreScheduleFunction`（:332）/`PipelinePostScheduleFunction`（:362，图谱：「把 stash 织入反向」）、单例 `PagedStashManager`（:415，`STASH_MGR` 类变量 + `get_instance` :422-426，管理 pack/unpack 流与 VP 调度状态机）、`PagedStashRunner`（:1001，训练循环侧的运行器）。
- Triton 内核面（`moe/ops/paged_stash.py`）：`paged_stash_copy_kernel`（:13）与 `paged_stash_pop_kernel`（:147）。内核 docstring 讲透了设计动机：「token 数只在运行时才知道且驻留 device……页分配、元数据记录、激活拷贝**融合成一次 GPU launch**以避免 host 同步并保持 CUDA-graph 友好；固定页尺寸相对超配的静态专家缓冲减少碎片」。dtype 策略在 `_stash_buffer_dtype`（moe/paged_stash.py:44）：FP8/FP4 一律按 uint8 字节搬运（`_STASH_NATIVE_DTYPES` 白名单 :27-38）。

## ③ 外部连接：与哪些子系统互依

图谱里 parallel_state 的最大消费方就是 `megatron/core/transformer`（13 条入边），而 MoE 是其中最重的——`MoELayer.__init__`（:240-244）在 `pg_collection is None` 时回落 `get_default_pg_collection()`，旁边留着 TODO 注释「delete the usage of the global parallel_state」，印证第 01 篇讲的依赖注入迁移尚未走完。GTP 广义张量并行经由 `resolve_gtp_remat_group`（process_groups_config.py）进入 MoE：latent 投影若在 `gtp_remat_opt_in_modules` 白名单里（moe_layer.py:293-301），TELinear 会拿到 `gtp_remat_group`+`gtp_replica_group`——**专家权重同样可被 GTP 轴分片**（对应 parallel_state 的 expert_gtp_remat/EGTP 组）。向下：`fused_a2a.py`（807 行）提供 NCCL EP 上下文（`nccl_ep_release_context` 被 paged_stash.py:19 导入；`nccl_ep_finalize` 被 destroy_model_parallel 调用）。向侧：`moe_layer.py` 头部同时 import 推理子系统（`megatron.core.inference.moe` 的 GroupedGemm 后端枚举、`token_dispatcher_inference`），训练/推理共用同一 MoE 层，靠 `InferenceMode.is_active()` 分岔（:613）。

## ④ 数据流：一次典型调用的路径

以「TP=2/EP=4、AlltoAll 派发、带共享专家」的训练前向为例：

1. `TransformerLayer.forward` 按残差规范进入 mlp 槽位——该槽位装的是 `MoELayer`（由 spec 决定）。
2. `router` 打分：gating 线性层产 logits → score_function（sigmoid）→ `topk_routing_with_score_function`（moe_utils.py:768）产出 probs + routing_map；训练步还会累积 aux loss/bias 统计 buffer。
3. `preprocess`（:506）：可选 latent 投影（hidden→moe_latent_size 降维，:534-536）→ `dispatch_preprocess` 做 token 重排准备。
4. `dispatch`（:546）：`MoEAlltoAllTokenDispatcher.token_dispatch` 发起 all-to-all，把 token 按专家归属搬到 EP 对端；若开 overlap，先过 `_RegisterDelayedWgradForExperts`。
5. `shared_experts_compute`（:558）与 all-to-all 通信并行跑共享专家（overlap 模式下在 preprocess 阶段已用侧流提前发射，:515-522）。
6. `routed_experts_compute`（:587）：`dispatch_postprocess` 得到按专家 permute 的输入 + tokens_per_expert → `TEGroupedMLP` grouped GEMM（NCCL-EP 零拷贝时直接写进 combine 对称缓冲，:617-627）→ `combine_preprocess`。
7. combine（反向 all-to-all）→ unpermute 加权合并 → 与共享专家输出相加回残差流。
8. PP 训练且开 `moe_paged_stash` 时：激活经 `paged_stash_group_start/commit`（:880/:905）登记，Triton `paged_stash_copy_kernel` 把变长激活装进固定页；溢出时 `PagedStashRunner` 检测 `check_over_budget` 并触发 dropless 重跑（`_MAX_RERUN_ATTEMPTS=2`，:23-25 注释：重跑会清容量因子，不可能再失败）。

## ⑤ 设计决策：为什么这么设计

**为什么 forward 拆成五段方法？** 每个 `@maybe_skip_or_early_return_by_cudagraph` 装饰器（:505 等）对应 CUDA graph 的**部分捕获**——MoE 的通信不适合进 graph，计算适合。拆段让 graph 边界可以落在任意方法之间（v0.12 起的 `--cuda-graph-scope attn` 就是这套机制）。这是"算子级 graph 兼容性"驱动的接口切分（推断依据：装饰器命名与 moe_utils 里 `MoECudaGraphPartialCaptureSignal` 的存在）。

**为什么 Protocol 先行？** `ExpertsBuilder` 等五个 Protocol（:69-151）把"MoE 层怎么组合 router/dispatcher/experts"做成结构化类型而非继承——spec 的 `MoESubmodules`（:166）填什么 builder 都行（TE 后端、local 后端、推理后端），MoELayer 不关心。这与外层 ModuleSpec 是同一哲学在两层落地：外层换骨架实现，内层换 MoE 部件。

**为什么 paged stash 要 Python 管理面 + Triton 内核面两套？** 分工：页分配生命周期、VP 调度状态机、与优化器/训练循环的联动必须留在 Python（`PagedStashRunner` 甚至要遍历模型找 MoE 层并同步多份 config，:1014-1031 注释解释了 config 需逐份跟踪的原因）；而"token 数在 device 上才知道"决定了分配+拷贝必须在 GPU 端一次完成，否则一次 stash 就要一次 host sync，CUDA graph 也会被打断。双层结构各取所长。

**为什么 latent MoE 的共享专家要提前到 preprocess？** :511-522 注释写明：latent 投影会把 hidden_states 降维，共享专家若不抢在 fc1_latent_proj 之前发射就只能看到降维后的表征——所以用侧流在 preprocess 里提前算，postprocess 里再 join+add。且训练路径直接 AssertionError 拒绝该组合（:527-533）：特性只在推理 NVLS dispatcher 下成立。

## ⑥ 新人提示：坑/入口/阅读顺序

- **阅读顺序**：`moe/README.md`（特性路线图，含各版本 flag 名）→ `spec_utils.py`（80 行，短）→ `gpt_layer_specs.py` 的 `get_gpt_layer_local_spec`（:444）→ `transformer_layer.py:329` 的 forward → `moe_layer.py:227` 五段式 → `router.py:158` → `token_dispatcher.py` 挑一个 dispatcher 精读。
- **spec 是数据不是代码**：看到 `ModuleSpec(module=(path, Class))` 先意识到这是延迟导入——调试时断点要下在 `build_module`（spec_utils.py:76），直接找 Class 文件可能扑空。
- **transformer_config.py 有 4034 行**，绝大多数 MoE 超参（moe_router_* / moe_* 全家）都在这里，改行为先查 config 字段而不是改层代码。
- **routing_type 与 score_function 是两个正交开关**，别混：前者管负载均衡策略（aux_loss/sinkhorn/quantile_balancing/none），后者管打分函数（softmax/sigmoid/sqrtsoftplus）。DeepSeek 系典型组合是 sigmoid + noaux_tc 式 expert bias。
- **paged_stash 是训练期 PP 激活 offload，不是推理特性**；它改写 PP schedule 的时序（两个 autograd 钩子挂的就是 pre/post schedule），单独读 moe_layer 会漏掉这层，需要结合 `pipeline_parallel/schedules.py`（该文件 import 了 paged_stash）。
- graph 甄别补充：`moe/` 下还有三个诊断文件 `router_trace.py`（492 行）/`router_replay.py`（208 行）/`router_diagnostics.py`（130 行）组成路由观测线，读代码时可先跳过。
