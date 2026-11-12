# TransformerEngine 新人导航（ONBOARDING）

> 知识图谱版（commit 0838ecbe，5816 节点/12573 边/16 层/16 步 tour，validator 0 issues，fingerprints 1037 文件，2026-11-11 分析）；文中行号锚均经源码核实（约 90 个 path:line 锚，逐条比对文件内容后写入）。锚路径约定：`common/`、`pytorch/`、`jax/`、`debug/` 开头的路径省略统一前缀 `transformer_engine/`（如 `common/recipe/__init__.py:107` 实指 `transformer_engine/common/recipe/__init__.py` 行 107）；仓根文件（setup.py/AGENTS.md/README.rst 等）与 tests/、docs/、qa/、build_tools/、examples/、benchmarks/ 均为完整路径。

## 一、一图看懂

TransformerEngine（TE）是 NVIDIA 的 FP8/FP4 低精度 Transformer 训练加速库：一套 framework-independent 的 `transformer_engine/common` C++/CUDA 内核（NVTE C API），同时服务 PyTorch 与 JAX 两个前端（README.rst:17）。它管理低精度训练所需的 scaling factor、amax 历史与量化元数据，模块覆盖 attention、linear、normalization、MoE 与大规模分布式通信；是 Megatron-LM/TRT-LLM 的量化引擎基座（README 集成列表点名 Megatron-LM、Accelerate、Lightning 等）。仓库形态：`common`（双前端共享内核+recipe）+ `pytorch`/`jax`（各自门面）+ `debug`（可插拔调试特性）+ `tests`/`qa`（L0-L3 四级门禁）。16 层：

| 层 | 职责 | 代表文件 |
|---|---|---|
| L01 工程门面·构建·CI·QA | 包根/构建/CI 门禁 | setup.py、build_tools/utils.py、qa/ |
| L02 公共 C++ 基座 | NVTE C API 总头+util+cudnn 封装+tvm_ffi 桥 | common/include/transformer_engine/transformer_engine.h |
| L03 FP8 转换与量化配方 | cast 逐元素/分组/blocked+recipe+swizzle | common/cast/cast.cu、common/recipe/__init__.py |
| L04 激活·Softmax·多张量 | gated/swiglu 反向+multi_tensor 优化器+Muon | common/activation/activation_template.h |
| L05 归一化与转置核 | LN/RMSNorm+cast_transpose 融合 | common/normalization/、common/transpose/cast_transpose.h |
| L06 融合注意力·GEMM·通信重叠 | cuDNN/Flash 注意力+KV cache+UB 重叠 | common/fused_attn/fused_attn.cpp、common/comm_gemm_overlap/ |
| L07 MoE 与多语言后备 | ep NCCL provider+router topk+triton/CuTeDSL | common/ep/ep_backend.h、common/fused_router/ |
| L08 PyTorch C++ 绑定 | pybind+extensions 全集 | pytorch/csrc/extensions/pybind.cpp |
| L09 PyTorch 门面与模块层 | autocast 主流程+nn.Module 族 | pytorch/quantization.py、pytorch/module/linear.py |
| L10 量化张量族 | Float8/Blockwise/MXFP8/NVFP4/Hybrid+storage 分离 | pytorch/tensor/float8_tensor.py |
| L11 注意力 Python 封装 | dot_product_attention 多后端+MLA+RoPE+CP | pytorch/attention/dot_product_attention/ |
| L12 统一算子体系 | ops basic+fused+fuser+optimizers+dynamo | pytorch/ops/op.py |
| L13 JAX 后端 | 77 文件第二前端全栈 | jax/__init__.py、jax/quantize/helper.py |
| L14 Debug 特性子系统 | 可插拔 fake_quant/dump/统计 | debug/features/api.py |
| L15 测试矩阵 | pytorch 123 py+cpp 46+jax 28+cpp_distributed | tests/pytorch/utils.py |
| L16 文档·示例·基准 | docs/features+examples+benchmarks | docs/features/low_precision_training/ |

依赖方向：L02 是全仓 API 收敛点（transformer_engine.h 总头 fanIn 123）→ L03-L07 各内核域向上 → L08 把内核绑进 PyTorch → L09-L12 Python 门面 → L13 JAX 平行复用 L02-L07 → L14 横切 L09 → L15/L16 外围。

## 二、五分钟路线（16 步 tour→6 里程碑）

**M1 全景（步 0）**：README.rst:17 定位段+News（最新 v2.19 09/2026）；setup.py:33 `frameworks = get_frameworks()` 与 build_tools/utils.py:439 的四态选择（pytorch/jax/pytorch,jax/none）；transformer_engine/__init__.py:55 `is_nccl_ep_available` 看运行时 dlopen 探测风格。**M2 C++ 基座与配方（步 1-3）**：common/include/transformer_engine/transformer_engine.h:155 `nvte_create_tensors` 是 C ABI 对象协议；common/recipe/__init__.py:107 `Recipe` 基类与 :489 `NVFP4BlockScaling`（六配方）；common/include/transformer_engine/cast.h:90 `nvte_quantize` 到 common/cast/cast.cu:21 的声明→实现落点。**M3 PyTorch 线（步 4-8）**：pytorch/csrc/extensions/pybind.cpp:209 `m.def("quantize")` 是 Python→C++ 单点；pytorch/quantization.py:415 `FP8GlobalStateManager`；pytorch/tensor/float8_tensor.py:53 `Float8Quantizer`；pytorch/module/base.py:935 `TransformerEngineBaseModule`；pytorch/ops/op.py:65 `FusibleOperation`。**M4 C++ 深水区（步 9-11）**：common/include/transformer_engine/fused_attn.h:542 `nvte_fused_attn_fwd`、common/fused_attn/graph_cache.h:45 `GraphCache`；common/include/transformer_engine/hadamard_transform.h:30/:74（RHT 与 FP8 注意力量化）；normalization RTC dispatch。**M5 MoE 与通信（步 12-13）**：common/ep/ep_backend.h:32 `EPBackend`、pytorch/router.py:140 topk、common/comm_gemm_overlap/userbuffers/userbuffers.h:90 `communicator`。**M6 JAX 与收尾（步 14-15）**：jax/__init__.py:32 `load_framework_extension("jax")`、jax/quantize/helper.py:751 `autocast`；最后 debug/features/api.py 与 tests/qa。

## 三、核心子系统深读

### 3.1 common C++ 基座：NVTE C API、cast 与 recipe

全库稳定锚是 common/include/transformer_engine/transformer_engine.h（1517 行）：`nvte_create_tensors`（:155）/`nvte_destroy_tensor`（:164）/`nvte_tensor_data`（:183）定义 NVTETensor 不透明对象协议——两个前端的张量最终都降维成这个 C ABI。cast 域在 common/cast/ 按 backend 分目录（fp8/fp8_blockwise/mxfp8/nvfp4 + core/dispatch），入口 common/cast/cast.cu:21 `nvte_quantize` 与 common/include/transformer_engine/cast.h:90 声明对齐；mxfp8/nvfp4 走 swizzle 排布（common/swizzle/）。Python 侧配方注册表 common/recipe/__init__.py（714 行）六类：DelayedScaling（:173，历史主力）→ Float8CurrentScaling（:286）→ MXFP8BlockScaling（:337）→ Float8BlockScaling（:392）→ NVFP4BlockScaling（:489）→ CustomRecipe（:630，自定义钩子）。common/__init__.py 是双后端共享的 Python 对象层：:123 `_get_shared_object_file` 定位 libtransformer_engine.so、:173 `load_framework_extension`（PyTorch/JAX 都调它装内核扩展）、:483 `_load_core_library`。

### 3.2 融合注意力（fused_attn/RoPE/RHT）与 UserBuffers/NVSHMEM 通信重叠

fused_attn 域双后端：flash_attn.cu 与 fused_attn_f16_arbitrary_seqlen.cu（Flash 系）、fused_attn_fp8.cu（FP8 路径）、context_parallel.cu（CP）、common/fused_attn/kv_cache.cu:174 `copy_to_kv_cache`（推理 KV cache 写入+THD→BSHD 转换）；common/fused_attn/graph_cache.h:45 `GraphCache` 管理 cuDNN graph 复用（含 graph_cache_debug.h 命中/未命中打点）。API 面 common/include/transformer_engine/fused_attn.h:542 `nvte_fused_attn_fwd`。Python 封装三后端分发：pytorch/attention/dot_product_attention/backends.py:412 `UnfusedDotProductAttention`（朴素）、:912 `FlashAttention`（FA2/3）、:2326 `FusedAttention`（cuDNN），统一入口 pytorch/attention/dot_product_attention/dot_product_attention.py:594 `DotProductAttention`。common/include/transformer_engine/fused_rope.h:40 `nvte_fused_rope_forward` 与 :102 `nvte_fused_qkv_rope_forward`（QKV+RoPE 一次完成）。common/include/transformer_engine/hadamard_transform.h:30 `nvte_hadamard_transform`、:74 `nvte_quantize_with_hadamard_transform`——随机 Hadamard 变换（RHT）把激活推成近似高斯分布再做 FP8 量化，是 current scaling 的数值稳定器（benchmarks/benchmark_rht_cast.py 可复现）。通信-计算重叠走 common/comm_gemm_overlap/：common/comm_gemm_overlap/userbuffers/userbuffers.h:90 `communicator` 结构持有 NVSHMEM/NCCL/MPI buffer，comm_gemm_overlap.cpp 实现 IBGMM（通信即 GEMM）的 AG/RS overlap；NVSHMEM 原语在 common/nvshmem_api/（waitkernel）。Python 侧入口 pytorch/module/base.py:152 `initialize_ub`/:620 `get_ub`。

### 3.3 MoE 专家并行：ep backend + fused_router + permutation

新式 EP 是"NCCL EP"：common/ep/ep_backend.h:32 `EPBackend` 单例按 CUDA 设备持有 EP 子通信器，prepare/dispatch/combine/dispatch_bwd 五阶段（全部 NVTECommWindow 窗口参数）；nccl_ep_provider.cpp 是 NCCL 侧 provider。独立构建为 libnccl_ep.so（setup.py:221 `build_nccl_ep_submodule`），运行时 dlopen 探测：transformer_engine/__init__.py:19 要求 `_NCCL_EP_MIN_VERSION = (2, 30, 4)`、:55 `is_nccl_ep_available` 校验。Python 入口 pytorch/ep.py:139 `ep_bootstrap`（+:95 `EpConfig` 配置对象）。路由核 common/fused_router/：fused_topk_with_score_function.cu、fused_moe_aux_loss.cu、fused_score_for_moe_aux_loss.cu，Python 包装 pytorch/router.py:140 `FusedTopkScoreFunction`/:530 `fused_moe_aux_loss`（含 QB bin bounds 校验 :74）。permutation 域做 token 重排（common/permutation/），pytorch/permutation.py:35 `moe_permute_index_map_forward` 带 fake impl（torch.compile 兼容）。GroupedLinear 在 pytorch/module/grouped_linear.py:1625，JAX 侧 jax/flax/moe.py:53 `_MoEBlock` 是 1369 行 jax/moe.py 的薄 Flax 壳。

### 3.4 PyTorch 绑定层（csrc+cpp_extensions）与量化张量族

pytorch/csrc/ 是 pybind11 绑定：pytorch/csrc/pybind.h:49 `init_extension()`，pytorch/csrc/extensions/pybind.cpp:209 注册 `quantize`/`dequantize`/GEMM/attention 全部入口；pytorch/csrc/extensions.h（934 行）集中声明全部扩展函数原型。Python 包装层 pytorch/cpp_extensions/（pytorch/cpp_extensions/gemm.py:192 `general_gemm`/:380 `general_grouped_gemm`、pytorch/cpp_extensions/fused_attn.py:175 `fused_attn_fwd`/:448 `fused_attn_bwd`、pytorch/cpp_extensions/gemm.py:41 cublas workspace 管理）。量化张量族两层分离：pytorch/quantized_tensor.py 定义协议——:53 `QuantizedTensorStorage`（data/scale_inv/量化元数据的 storage 层）、:370 `Quantizer`（builder 抽象基类，:445 `quantize` 模板方法→子类 `quantize_impl`，:479 `__call__` 直通）、:723 `QuantizedTensor(torch.Tensor)`（dispatch 层）；pytorch/tensor/ 按格式实现：pytorch/tensor/float8_tensor.py:53 `Float8Quantizer`+:440 `Float8Tensor`（per-tensor delayed）、:197 `Float8CurrentScalingQuantizer`，另有 mxfp8/nvfp4/float8_blockwise/hybrid/identity 五个 storage（pytorch/tensor/storage/ 目录，FSDP2/swap_tensors 兼容在 float8_tensor.py 内处理）。

### 3.5 统一算子体系 ops 与模块层

pytorch/ops/ 是新式算子协议：pytorch/ops/op.py:65 `FusibleOperation`（量化元数据+融合兼容性检查+前反向计划）、:302 `BasicOperation`、:937 `FusedOperation`——basic/ 下 20+ 原子算子（basic_linear/activation/layer_norm/all_gather/reduce_scatter/swiglu…），fused/ 是反向融合族（backward_linear_add 等），fuser.py 按兼容性自动拼融合。模块层 pytorch/module/base.py:935 `TransformerEngineBaseModule`（2124 行）：quantizers 字典、fp8_meta、TP/SP 状态、weight workspace 管理；具体层 pytorch/module/linear.py:1901 `Linear`（2790 行，:1804 `_Linear` autograd Function 是真实计算体，:353 `_linear_forward_impl` 为前向实现）、pytorch/module/layernorm_linear.py:1545 `LayerNormLinear`、pytorch/module/layernorm_mlp.py:2171 `LayerNormMLP`。pytorch/distributed.py（2271 行）：:167 `get_distributed_world_size`、:1682 `gather_along_first_dim` 等 TP 基础设施。辅助子系统：pytorch/graph.py:66 `is_graph_capturing`（CUDA graph 兼容判定）、pytorch/cpu_offload.py（参数/梯度/优化器状态分层卸载）、pytorch/optimizers/（multi_tensor fused adam/sgd + pytorch/optimizers/newton_schulz.py:126 `CusolverMpCtx`，对应 common/include/transformer_engine/newton_schulz.h:58 `nvte_newton_schulz` 的 Muon 优化器核）。

### 3.6 JAX 后端（第二前端全栈）

transformer_engine/jax/ 77 文件自成全栈：jax/__init__.py:32 `load_framework_extension("jax")` 装载内核扩展；jax/quantize/helper.py:751 `autocast`（:814 `fp8_autocast` 已弃用）+tensor.py/dequantizer.py/scaling_modes.py 量化栈；jax/sharding.py:321 `MeshResource` 做 NamedSharding 映射；jax/flax/ 子包给 Flax 模块（jax/flax/module.py:372 `TransformerEngineBase`、:421 `DenseGeneral`、:879 `LayerNormMLP`、jax/flax/moe.py:53 `_MoEBlock`）；jax/moe.py:1208 `moe` 等 primitive（jax/dense.py/jax/attention.py/jax/permutation.py）走 custom call 进 C++。jax/quantize/hadamard.py 是 RHT 的 JAX 版。triton 后备双轨：common/triton/（框架无关核：cross_entropy/mhc/pad/permutation/grouped_dbias_dscales）+ pytorch/triton/（PyTorch 适配层，如 pytorch/triton/mhc.py:12 从 common/triton/mhc import 复用实现而非复制）；common/CuTeDSL/ 同理（Blackwell CuTeDSL cast/activation）。

## 四、数据流走查：一次 autocast 下 Linear 前反向全链

1. **进入 autocast**：`with autocast(enabled=True, recipe=...)` → pytorch/quantization.py:1037 `__enter__` → FP8GlobalStateManager.autocast_enter（pytorch/quantization.py:730）注册全局 recipe/分组；注意 fp8_autocast（pytorch/quantization.py:941）是弃用别名，pytorch/fp8.py 整文件也是弃用壳（pytorch/fp8.py:6）。
2. **模块前向**：Linear（pytorch/module/linear.py:1901）的 forward（:2339）把 weight/inp/bias 装进 `LinearFwdArgs`，调 `_Linear.apply`（:1804，torch.autograd.Function）。
3. **前向实现**：`_linear_forward_impl`（pytorch/module/linear.py:353）先定量化器角色与 UB overlap 类型（tex.CommOverlapType.RS/AG），再准备输入：`input_quantizer(inputmat)`（:483）。
4. **量化执行**：Quantizer.__call__（pytorch/quantized_tensor.py:479）→ quantize（:445）→ `_QuantizeFunc.apply` → 子类 quantize_impl：Float8Quantizer 在 pytorch/tensor/float8_tensor.py:123，一行 `tex.quantize(tensor, self)`（:125）。
5. **进 C++**：tex.quantize 经 pytorch/csrc/extensions/pybind.cpp:209 绑定进入 common 层 → NVTE C API `nvte_quantize`（common/cast/cast.cu:21，common/include/transformer_engine/cast.h:90 声明）→ cast/dispatch/quantize.cuh 按 recipe/dtype 分发到 fp8/fp8_blockwise/mxfp8/nvfp4 各模板核；当前缩放配方会先走 RHT（common/include/transformer_engine/hadamard_transform.h:74）。
6. **GEMM**：量化后的 weight workspace 与 input 进 `general_gemm`（pytorch/cpp_extensions/gemm.py:192），cuBLAS/cuBLASLt workspace 由 :41/:50 管理；输出按 output_quantizer 决定留在低精度或 cast 回 bf16。
7. **反向**：`_Linear.backward`（pytorch/module/linear.py:1862）→ `_linear_backward_impl` 出梯度后，若 fp8 开启且无 backward_override，调 FP8GlobalStateManager.reduce_and_update_fp8_tensors（pytorch/quantization.py:656，forward=False）跨卡规约 amax。
8. **退出 autocast**：`__exit__`（pytorch/quantization.py:1056）→ autocast_exit（:772）完成 delayed scaling 的 amax→scale 推进（common/recipe/__init__.py:173 DelayedScaling 语义）。

## 五、依赖地图（枢纽 top，按 fanIn）

| 枢纽文件 | fanIn | fanOut | 角色 |
|---|---|---|---|
| pytorch/__init__.py | 149 | 28 | PyTorch 门面总入口 |
| common/include/transformer_engine/transformer_engine.h | 123 | 1 | NVTE C API 总头（公共 API 之锚） |
| common/recipe/__init__.py | 121 | 36 | 六配方注册表 |
| common/common.h | 97 | 5 | 内核 API 声明中央接口 |
| pytorch/utils.py | 70 | 117 | 工具总库（fanOut 全仓第一） |
| jax/__init__.py | 66 | 5 | JAX 门面 |
| pytorch/quantization.py | 61 | 98 | 量化 Python 中枢 |
| pytorch/constants.py | 60 | 4 | dtype 范围/枚举映射 |
| common/utils.cuh | 59 | 0 | kernel 侧最大公共头 |
| pytorch/quantized_tensor.py | 54 | 21 | 量化张量协议层 |
| common/util/math.h | 47 | 0 | device 数学函数集 |
| tests/cpp/test_common.h | 45 | 85 | C++ 测试框架 |
| pytorch/tensor/__init__.py | 41 | 20 | 张量族 barrel |
| jax/sharding.py | 39 | 53 | JAX 分片工具 |
| pytorch/distributed.py | 30 | 120 | 分布式基础设施总库 |

（前缀 transformer_engine/ 省略。）规律：C++ 侧 transformer_engine.h/common.h/utils.cuh 三个头是"改一处全仓重编"；Python 侧 quantization.py（fanOut 98）与 distributed.py（fanOut 120）/utils.py（fanOut 117）是行为发散点；两个前端各有一个门面枢纽（pytorch/__init__.py 与 jax/__init__.py），但都向下收敛到 common 层——"一套内核双前端"在依赖图上直接可见。

## 六、坑与勘误（源码级发现）

1. **fp8.py 不是主流程**：仅 68 行弃用壳，pytorch/fp8.py:6 明言 "DEPRECATED in favor of transformer_engine.pytorch.quantization.py"；图谱 L09 层摘要的"fp8.py 主流程"应读作 quantization.py（1992 行，autocast:972/FP8GlobalStateManager:415）。
2. **fp8_autocast 双前端同步弃用**：PyTorch 侧 pytorch/quantization.py:941 与 JAX 侧 jax/quantize/helper.py:814 都发 DeprecationWarning 指向 autocast；旧代码迁移注意 jax 版签名不同（mesh_resource 而非 group）。
3. **CLAUDE.md 非孪生**：仅 3 行（标题+"@AGENTS.md"引用），与 Megatron-LM 的逐字节孪生形态不同；AGENTS.md（407 行）才是唯一正文。
4. **版本三口径漂移**：build_tools/VERSION.txt=2.21.0.dev0，README.rst News 最新条目停在 v2.19（09/2026），docs/release_notes.md 是"vX.YZ"空模板——版本公告在 GitHub Releases，仓内两处均滞后。
5. **envvars.rst 缺 5 个构建变量**：NVTE_WITH_NCCL_EP/NVTE_WITH_CUBLASMP/NVTE_WITH_CUSOLVERMP/NVTE_BUILD_METAPACKAGE/NVTE_NO_LOCAL_VERSION 在 setup.py 与 build_tools/ 真实消费但 docs/envvars.rst 零记载（grep 实测 doc=0）。
6. **pyproject.toml 构建依赖双框架捆绑**：build-system requires 同时列 torch>=2.1 与 jax>=0.5.0/flax>=0.7.1（pyproject.toml:6）——build isolation 会强装两框架，故 README/AGENTS 的 `--no-build-isolation` 不是建议而是必须。
7. **triton/CuTeDSL 双目录非重复**：pytorch/triton/* 从 common/triton/* import 复用（pytorch/triton/mhc.py:12 等），是"框架无关核+PyTorch 适配层"分层，勿当 dead copy 删。
8. **qa/ 才是权威 CI**：AGENTS.md:55-56 明言「qa/ launchers … authoritative CI test suites. The GitHub Actions workflows expose only a subset of the full CI」，qa/L0-L3 才是完整门禁；L0 脚本默认 TE_PATH=/opt/transformerengine、XML_LOG_DIR=/logs（qa/L0_pytorch_unittest/test.sh:21-22），本地跑必须覆写。
9. **libtransformer_engine.version 导出面**：nvte_* + transformer_engine::cuda::sm_count*（common/libtransformer_engine.version）——sm_count 是少数以 C++ 符号导出的例外，链接独立可执行文件时注意。
10. **NCCL EP 是独立 so 的运行时探测**：libnccl_ep.so 单独构建（setup.py:221），dlopen+版本闸门 NCCL>=2.30.4（transformer_engine/__init__.py:19）；容器里"EP 不可用"先查 NCCL 版本再查库路径。

## 七、如何跑起来

**构建**（AGENTS.md:130-187 区段）：先 `git submodule update --init --recursive`（AGENTS.md:141，3rdparty=cutlass/googletest/nccl-extensions）；开发构建四态选前端：`NVTE_FRAMEWORK=pytorch python -m pip install -e . -v --no-build-isolation`（AGENTS.md:149；可换 jax / pytorch,jax / none）。常用控制：NVTE_CUDA_ARCHS（Blackwell 用 100a 别用 100 族选择器）、MAX_JOBS、NVTE_USE_CCACHE=1、NVTE_BUILD_DEBUG=1；可选组件 NVTE_WITH_NCCL_EP（默认开）/NVTE_ENABLE_NVSHMEM（要 NVSHMEM_HOME）/NVTE_UB_WITH_MPI/NVTE_WITH_CUBLASMP/NVTE_WITH_CUSOLVERMP。**验证**：`python -c 'import torch, transformer_engine, transformer_engine.pytorch; ...'`（AGENTS.md:206 区段，注意 NGC 容器预装 TE 需确认解析到工作树）。**测试**：迭代期 `python -m pytest -v tests/pytorch/test_sanity.py`，JAX 必须带 `-c tests/jax/pytest.ini`（AGENTS.md:241）；C++ 核 `cmake -GNinja -S tests/cpp -B tests/cpp/build && ctest --test-dir tests/cpp/build`；门禁 `TE_PATH="$PWD" XML_LOG_DIR=/tmp/te-test-logs bash qa/L0_pytorch_unittest/test.sh`（AGENTS.md:271；L0_license/L0_pytorch_unittest/L0_jax_unittest/L0_cppunittest 是贡献必过，L1 分布式、L2 JAX 分布式、L3 FA 版本矩阵升阶）。**性能与示例**：benchmarks/（gemm/linear/attention+RHT 基准）；examples/pytorch（含 mhc.py 混合头聚类注意力）与 examples/jax。

## 八、延伸阅读

- docs/features/low_precision_training/：introduction、fp8_delayed_scaling、fp8_current_scaling、fp8_blockwise_scaling、mxfp8、nvfp4、fine_grained_quantization、performance_considerations——数值语义权威。
- docs/features/other_optimizations/：comm_gemm_overlap、cpu_offloading、ep、fsdp、quantized_model_init。
- docs/envvars.rst（628 行，注意第六节勘误 5 的缺口）、docs/installation.rst、docs/debug/。
- DeepWiki 快照：../deepwiki/（36 页全量，2026-10-26）。
- examples/（pytorch/jax 双目录）与 benchmarks/（含 benchmark_rht_cast.py）。
- 图谱资产：.understand-anything/onboard-input.json（30 枢纽+16 步 tour），完整 knowledge-graph.json 可下钻。

---
*行号随上游演进可能漂移，以语义定位为准。*
