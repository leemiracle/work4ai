# 05 · jax/——JAX/Flax 前端与 common 基座复用链

> 源文件：`transformer_engine/jax/`（77 文件：包根 16 个 flax 风格层模块 + quantize/ 9 文件 + csrc/extensions/ 24 个 C++ 绑定 + cpp_extensions/ 13 个 FFI 原语）。图谱中它是与 pytorch/ 并列的第二个前端节点群，向下汇入同一 common 基座。

## ① 角色定位：这个子系统解决什么问题

把 TE 的低精度 Transformer 算子带进 JAX/XLA 世界：用户写 flax 风格的 `dense`/`layernorm`/`moe`，底下经 FFI 进 C++ 绑定，最终调与 PyTorch 前端**完全相同**的 common C API。它要解决 JAX 特有难题：XLA 会搬迁/重布局缓冲（绑定层须容忍指针变化）、sharding 由 mesh 注解表达、量化状态塞进 flax dataclass module。

## ② 内部结构：关键类/函数与行号锚

**层族（包根）**：`dense`（`dense.py:57`）与 grouped_dense（:318）是模板——`jax.custom_vjp` 包裹（:119），规则 `_dense_fwd_rule`（:167）/`_dense_bwd_rule`（:239）；:433 注释讲 remat 下量化核会被重跑，是 JAX 前端最深的坑位。`layernorm`（`layernorm.py:42`）、`moe`（`moe.py:1208`，规则 :543/:877）、路由 `fused_topk_with_score_function`（`router.py:87`）与 aux loss（:299）、EP 自举 `ep_bootstrap`（`ep.py:119`）。

**量化器族（`quantize/quantizer.py`）**：基类 `Quantizer`（`quantizer.py:76`）+ 四实现：Current（:218）、Delayed（:321，继承 current）、BlockScale（:474）、NVFP4（:586）；`QuantizerSet`（:839）打包 A/B/bias/gradients 四角色，`QuantizerFactory`（:1059）从 recipe 构建。

**scaling 语义**：`ScalingMode` 枚举（`scaling_modes.py:783`）六值与 common 镜像（DELAYED/MXFP8_1D/CURRENT/NVFP4_1D/NVFP4_2D/NO_SCALING），每模式挂 metadata 实现（:91）；tensor 侧 `ScaledTensor`（`quantize/tensor.py:180`）与 `Dequantizer`（`quantize/dequantizer.py:25`）。

**绑定两层**：Python FFI 原语在 `cpp_extensions/`（`gemm.py:492` 注册名 `te_gemm_v2_ffi`，:695 走 `jax.ffi.ffi_lowering`；`quantization.py:924` 的 quantize）；C++ 翻译层 `csrc/extensions/`（24 文件）——`gemm.cpp:36` 的 `xla_buffer_to_nvte_gemm_operand` 把 XLA 缓冲包成 NVTE TensorWrapper，:340 调 `nvte_cublas_gemm_v2`，:86 调 `nvte_swizzle_scaling_factors`；`quantization.cpp:184` 调 `nvte_quantize_v2`。

## ③ 外部连接：与哪些子系统互依

**复用同一 common 基座的证据链**（本篇核心结论）：`csrc/extensions/quantization.cpp:184` 调的 `nvte_quantize_v2` 与 PyTorch pybind（03 篇）是同一个符号；`gemm.cpp:340` 的 GEMM、swizzle、fused_attn、MoE topk 全部来自 01/02/04 篇的同一批 .cu。差异只在包装：PyTorch 用 QuantizedTensor 代理类维持 autograd，JAX 用 custom_vjp+FFI 原语维持 XLA 追踪；EP 后端遇 XLA 缓冲搬迁重建句柄（04 篇 :419），`ep.py:119` 的 bootstrap 负责 uid 交换。sharding.py 提供 mesh 注解工具。

## ④ 数据流：一次典型调用的路径

flax 模型里的量化 dense 前向：①用户调 `dense(...)`（`dense.py:57`）带 QuantizerSet；②custom_vjp 进 `_dense_fwd_rule`（:167）→FFI 原语 quantize（`quantization.py:924`）→C++ `nvte_quantize_v2`（`quantization.cpp:184`）；③GEMM 原语 `te_gemm_v2_ffi`（`gemm.py:492`）→`xla_buffer_to_nvte_gemm_operand`（`gemm.cpp:36`）→`nvte_cublas_gemm_v2`（:340）；④反向 `_dense_bwd_rule`（:239）同类路径，remat 可能重放②。

## ⑤ 设计决策：为什么这么设计

**FFI 而非 XLA custom call 裸接口**：`jax.ffi.ffi_lowering`（`gemm.py:695`）是官方路线，规避 custom call ABI 漂移；命名原语还获得 XLA 编译期可见性。**QuantizerSet 四角色**（:839）：A/B/bias/梯度各需独立量化配置，打包避免四散传参。**ScalingMode 镜像枚举**：Python 枚举与 C 枚举同步（:783 引用 JAXX_Scaling_Mode 常量），杜绝语义漂移——与 PyTorch"每 Quantizer 类对应一 mode"殊途同归。**csrc 与 cpp_extensions 分层**：C++ 管 tensor 翻译与 NVTE 调用，Python 管原语注册与 XLA 集成，与 pytorch/csrc+pybind 同构。

## ⑥ 新人提示：坑/入口/阅读顺序

- **入口**：`quantizer.py:76`（量化语义）→`dense.py:57`+custom_vjp（层形态）→`cpp_extensions/gemm.py:492`（FFI）→`csrc/extensions/gemm.cpp:36`（翻译层）。
- **坑一：XLA 缓冲不保证稳定**——EP 句柄缓存 miss 重建（04 篇 :419）就是为它打的补丁；新绑定别缓存裸设备指针跨调用。
- **坑二：remat 会重放量化核**（`dense.py:433` 注释），量化核出现两次不是 bug。
- **坑三：ScalingMode 六值**是 JAX 侧全集，多出 NVFP4_2D/NO_SCALING——支持矩阵以枚举为准。
- 测试入口 `tests/jax/`（独立 pytest.ini，AGENTS.md）。
