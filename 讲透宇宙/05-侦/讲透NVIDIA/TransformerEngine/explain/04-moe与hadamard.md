# 04 · fused_router + ep + hadamard——MoE 三件套与随机 Hadamard 变换

> 源文件：`transformer_engine/common/fused_router/`（fused_topk_with_score_function.cu 1887 行等三核族）+ `transformer_engine/common/ep/`（ep_backend.cpp 718 行）+ `transformer_engine/common/hadamard_transform/`（10 文件最大 1499 行）+ pytorch 侧 `router.py`/`ep.py`/`quantization.py`。MoE 簇与 quantization 簇的交汇点。

## ① 角色定位：这个子系统解决什么问题

MoE 层三大开销：路由计算（top-k+softmax+辅助损失）不融合会产生一堆小 kernel；EP 的 dispatch/combine all-to-all 是带宽瓶颈；量化后 outlier 使小块 amax 失真。三件套各治一个：`fused_router` 把路由+aux loss 融进单 kernel 族；`ep` 封装 NCCL window 做 zero-copy token 搬运；`hadamard_transform` 量化前做随机 Hadamard 变换（RHT）摊平 outlier——FP8 量化精度关键技术。

## ② 内部结构：关键类/函数与行号锚

**topk 核族（`fused_topk_with_score_function.cu`）**：主前向核（`fused_topk_with_score_function.cu:335`）与反向核（:1247）。Quantile-Based 路由是特色：`QBMode` 枚举（:25）+直方图累积核（:883）按分位数截断选专家；v2 入口 :1721。

**aux loss（`fused_moe_aux_loss.cu`）**：前向核（`fused_moe_aux_loss.cu:21`）算均衡损失；graph_safe 版（:142）；反向 :230。

**EP 后端（`ep/ep_backend.cpp`）**：单例 `EPBackend`——`initialize`（`ep_backend.cpp:180`）注册 NCCL window；`prepare`（:460）按路由结果预分配接收缓冲；`dispatch`（:605）与 `combine`（:646）调 NCCL EP 原语；反向 `dispatch_bwd`（:669）。:419 注释记录 XLA 缓冲搬迁 WAR。C API 在 `ep_api.cpp:56` 起，无 NVTE_WITH_NCCL_EP 时空 stub（:132）。

**Python 侧**：`router.py` 的 autograd Functions——`FusedTopkScoreFunction`（`pytorch/router.py:140`）、QB 版（:209）、`FusedAuxLoss`（:469），:161 调 tex 绑定。`ep.py` 的 `EpConfig`（`pytorch/ep.py:95`）/`EpBuffer`（:305）、`_EpPrepareAndDispatch`（:773）。

**hadamard（`hadamard_transform.cu`）**：主核 `HadamardTransformKernel`（`hadamard_transform.cu:328`）static_assert 限定 16 维（:334），每 32 线程处理一个 16×16 块，同产正/转置输出与 amax；host 侧（:487）NVTE_CHECK 强制 BF16；随机性来自 16 位 `random_sign_mask`（utils :157）。入口 `nvte_hadamard_transform`（:684）；融合版（`hadamard_transform_cast_fusion.cu:842`）变换+量化一核完成。Python 侧 `with_rht` 开关（`pytorch/quantization.py:1734`）。

## ③ 外部连接：与哪些子系统互依

fused_router 与 ep 上下游相接：router 的 routing_map/topk_idx 正是 `prepare`/`dispatch` 的输入（`ep_backend.cpp:460`）。hadamard 消费 01 篇的 cast：融合版核直接输出 NVFP4 块尺度。`pytorch/module/moe.py` 串成 MoELayer。EP 的 window 注册依赖 `comm_window.h`；Megatron-LM 是主要外部消费方。

## ④ 数据流：一次典型调用的路径

MoE 前向：①logits 进 `tex.fused_topk_with_score_function_fwd`（`router.py:161`）→单核产出 topk_idx/weights+routing_map；②`nvte_ep_prepare_and_dispatch`（`ep_api.cpp:87`）先交换每专家 token 数再发 token；③专家 GEMM 后 `nvte_ep_combine`（:102）原路聚合。RHT 独立发生：NVFP4 量化器带 with_rht 时，quantize 前先对激活行做 16 维随机符号 Hadamard 变换（`hadamard_transform.cu:328`），块 amax 变换后统计，分布摊平再压 FP4。

## ⑤ 设计决策：为什么这么设计

**RHT 的数学动机**：Hadamard 变换保范数，随机符号去相关 outlier——块内能量均匀化，amax 不再被异常值主导，FP8/FP4 块量化误差大降。**RHT 融进量化器而非独立层**：变换结果只对量化有意义，脱壳传输 BF16 反而亏；`with_post_rht_amax` 让 amax 变换后统计。**4over6 与 RHT 互斥**（`quantization.py:1715` 显式 raise）：4over6 误差补偿假设原分布，RHT 改变分布后失效。**graph_safe aux loss**：CUDA Graph 要求指针稳定，:142 把 host 归约改 device 端。**EP 用 NCCL window 而非 userbuffers**：MoE token 流变长，NCCL EP 原语原生处理 per-expert 计数。

## ⑥ 新人提示：坑/入口/阅读顺序

- **入口**：`router.py:140`（Python 视角）→`fused_topk_with_score_function.cu:335` 主核→`ep_backend.cpp:460`→`hadamard_transform.cu:328`。
- **坑一：QB 路由有直方图预 pass**（:883），topk 不是一个核。
- **坑二：RHT 只吃 BF16**（:487）；aux loss 有 graph/非 graph 两套前向，CUDA Graph 须 graph_safe（:292）。
- **坑三：EP 后端是进程单例**，重复 initialize 要先 shutdown；JAX 缓冲搬迁触发句柄重建（:419）。
- **坑四：4over6+RHT 在 Python 层就被拦**（:1715）。
