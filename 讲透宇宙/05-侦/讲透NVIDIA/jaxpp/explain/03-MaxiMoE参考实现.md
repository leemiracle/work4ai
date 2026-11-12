# 03 · MaxiMoE：DSV3 形状 MoE 参考实现与 SM90/SM100 ragged GEMM

## 角色定位

`examples/maximoe/` 不是普通 example，而是 JaxPP 能力的最大集成样例：一个 DeepSeek V3 形状的 MoE transformer 端到端训练器（模型 1676 行、训练器 2114 行），跑在 MPMD 流水线上，ragged GEMM 内核直接写到 SM90（Hopper）/SM100（Blackwell）两级硬件。包结构：model.py 模型、train.py 训练循环、profile.py 剖析、warmup.py 预热、kernels/ 内核层（pyproject 暴露 maximoe-train/profile 入口）。

## 内部结构

**模型层**（`examples/maximoe/src/maximoe/model.py`）：RaggedArray（`model.py:160`）是变长 token 的一等容器；路由核心 dedup_token_routing（`model.py:316`）生成去重路由计划（同一 token 到同一专家只算一次再散射回去）；专家通信两条路——all_to_all（`model.py:75`）常规路线与 ring_of_experts（`model.py:562`）环形收集路线，后者由 use_ring_of_experts 开关控制（默认 False，`model.py:1443`，`model.py:1467` 注释解释其 gather-every-token 语义）。**训练层**（`examples/maximoe/src/maximoe/train.py`）：BF16 计算+FP32 主权重与 router bias 混合精度，`train.py:249` 显式断言"expert master compression requires FP32 masters and BF16 compute"（compress_expert_master_params `train.py:178` 才允许开）；auxiliary-loss-free 风格 router bias 更新率 0.001（`train.py:218`，RouterState 初始化 `train.py:839`）；host offload 正则把状态叶放 pinned host 内存（host_offload_regex `train.py:172`，内存标记 `train.py:852/:918`）；入口 main（`train.py:1920`）。**内核层**：Implementation 枚举+resolve（`examples/maximoe/src/maximoe/kernels/backend.py:35/:43`）按环境变量/硬件分派；gpu.py 的 GpuArchitecture 区分 SM90/SM100。

## 外部连接

内核层三族：①ragged_dot（变长专家 GEMM）——ops.py 定义抽象基类 RaggedOperation（`examples/maximoe/src/maximoe/kernels/ragged_dot/ops.py:95`）与三算子 RaggedDot/RaggedDotSwiGLU/RaggedDotCombine（`ops.py:150/:206/:237`），按 get_implementation（`ops.py:55`）选后端，dx/dw 反向同分派（`ops.py:450/:469`）；sm90.py（1431 行）Hopper 路线：ragged_dot_kernel（`kernels/ragged_dot/sm90.py:249`）+ warp 特化 kernel_warp_specialized（`sm90.py:413`）+ emit_pipeline_warp_specialized（`sm90.py:456`）；sm100.py（1424 行）Blackwell 路线：TuningConfig（`kernels/ragged_dot/sm100.py:52`）按形状查表 tile/block 参数、persistent_grid（`sm100.py:69`）持久网格、store_swiglu/store_identity（`sm100.py:115`/`sm100.py:101`）区分激活融合与直写；swiglu.py 独立 SwiGLU 内核（gate/up 交错布局）。②moe_routing——mosaic_gpu.py 用 Mosaic GPU DSL 写 persistent_group_loop（`examples/maximoe/src/maximoe/kernels/moe_routing/mosaic_gpu.py:118`）配 union_varying_axes（`mosaic_gpu.py:83`）处理不规则组形状，xla.py 纯 XLA 兜底。③模型侧 all_to_all/ring_of_experts 依赖 jaxpp 跨任务原语。外围 warmup_tasks（`examples/maximoe/src/maximoe/warmup.py:32`，正式训练前逐任务预热编译与 NCCL 建连）与 profile.py 的 numerical_signatures 防数值静默漂移。

## 数据流

一个 MoE 层的 token 之旅：router 打分（bias 修正）→ dedup_token_routing 去重得 ragged 布局 → RaggedArray 变长段排列 → ragged GEMM 三连（SwiGLU 前向 → dx → dw，SM90 走 warp 特化、SM100 走持久网格）→ combine 聚合回原位 → all_to_all 或 ring_of_experts 回各自设备。训练步外围：reshard_params_for_compute 换存储/计算分片布局，FP32 master 更新后舍回 BF16，host offload 状态叶按正则进出 pinned host。五份启动脚本对应五档：`examples/maximoe/scripts/` 下 dsv3-h100.sh、dsv3-h100-16k.sh、dsv3-h100-16k-dropless.sh、dsv3-h100-16k-dropless-gb64.sh、dsv3-gb200.sh。

## 设计决策

四个亮点：①ragged 而非 padding——专家 token 用变长段布局省掉补零 FLOPs，代价是内核复杂度（trap_if_rows_exceed 防越界、tile swizzle 都进 `examples/maximoe/src/maximoe/kernels/ragged_dot/common.py`）；②两级硬件双后端而非单内核跨代——SM90 的 warp 特化与 SM100 的持久网格是两种范式，TuningConfig 查表把形状-参数耦合显式化；③数值诚实——profile.py 的 numerical_signatures 与 `train.py:249` 的混合精度断言，把"训练结果对不对"做成可对比指纹；④训练器自身也是 jaxpp 教材——make_mesh 物理轴、tscan/treduce 搬运状态、host offload 全用库自身原语。

## 新人提示

按 model.py → ops.py → sm90.py/sm100.py 顺序读，先只看 RaggedOperation 的算子边界。跑不了真机时，`examples/maximoe/tests/ragged_dot_test.py`（跨后端规格）与 ragged_dot_sm90/sm100_test.py（数值对照）就是可执行文档；model_test.py（1899 行）覆盖优化路由 EP、context parallel attention 等大场景。改内核后必跑 kernel_launches 计数（`examples/maximoe/src/maximoe/test_util.py:26`）确认没退化到 XLA 兜底。
