# 06 · pytorch/ops/——算子协议、序列融合与 torch.compile 通道

> 源文件：`transformer_engine/pytorch/ops/`（op.py 1018 行、fuser.py 971 行、basic/ 20 文件、fused/ 11 文件）+ `pytorch/dynamo/`+`pytorch/optimizers/`。图谱中它是"模块层"与"量化层"之间的可组合算子骨架。

## ① 角色定位：这个子系统解决什么问题

nn.Module 粒度太粗（一个 Linear 藏 5 个 kernel），裸 kernel 又太碎（compile 接不住）。ops 体系给出中间层：**把 Transformer 层拆成可声明融合的算子序列**——quantize/swiglu/rmsnorm/all_gather 等基本算子排成流水线，fuser 按注册表把相邻子序列换成融合实现（含 userbuffers 通信），dynamo 把算子注册成 torch.library custom op 使序列可被 torch.compile 捕获。optimizers 是同思想的优化器侧延伸。

## ② 内部结构：关键类/函数与行号锚

**算子协议（`op.py`）**：`FusibleOperation`（`op.py:65`）是抽象基类——子类声明 dataclass 风格 `fwd_args_type`/`bwd_args_type`，`__init_subclass__` 自动调 `_register_compile_ops`（:80）注册 custom op；`compile_unsupported_reason`（:101）解释某算子为何不能走 compile。两个具体基类：`BasicOperation`（:302）单算子、`FusedOperation`（:937）融合算子。

**融合引擎（`fuser.py`）**：`OperationFuser`（`fuser.py:432`）docstring 写明三遍扫描：joint fwd-bwd→fwd-only→bwd-only（:853/:896/:935）。构造时把 FusedOperation 展平成 basic_ops（:457-462）；autograd 由 `_OperationFuserAutogradFunction`（:57）整体接管，未匹配的算子退回 eager。

**basic/ 算子库**：`Quantize`（`basic/quantize.py:18`，autocast 外退化 identity）、`SwiGLU`（`basic/swiglu.py:32`）与 ScaledSwiGLU（:598）、`RMSNorm`（`basic/rmsnorm.py:34`）、`AllGather`（`basic/all_gather.py:18`）。容器 `Sequential`（`sequential.py:17`）。

**fused/ 融合库**：反向主导——`BackwardAddRMSNorm`（`fused/backward_add_rmsnorm.py:25`）、`BackwardLinearAdd`（`fused/backward_linear_add.py:22`）、`UserbuffersForwardLinear`（`fused/userbuffers_forward_linear.py:35`）、`GroupedMLP_CuTeGEMMGLU`（`fused/grouped_mlp.py:2732`）；`Linear`（`linear.py:23`）也是 FusedOperation。

**compile 通道（`dynamo/custom_op.py`）**：:7 注释开门见山——把 TE 模块 eager 正反向注册为 `torch.library` custom op；:48 每 op 配 data-free `register_fake` 让 fake-tensor 追踪通过；`OpaqueValueBundle`（:158）解决 quantizer 非张量对象的展平。

**optimizers/**：`FusedAdam`（`optimizers/fused_adam.py:40`）单 kernel 多张量更新，走 `MultiTensorApply`（`multi_tensor_apply.py:9`）。

## ③ 外部连接：与哪些子系统互依

向上被 `pytorch/module/` 的新式层与用户模型消费；Quantize 的 quantizer 来自 03 篇量化器族，autocast（fp8.py）提供 recipe 上下文。fused/ 的 userbuffers 直连 02 篇 CommOverlap 类；GroupedMLP 消费 04 篇 grouped GEMM。dynamo 依赖 torch.compile custom op 机制，optimizers 依赖 common/multi_tensor 的 nvte kernel。

## ④ 数据流：一次典型调用的路径

带通信的 Linear 前向：①用户把 `[UserbuffersForwardLinear, Quantize, Bias]` 排进 Sequential；②OperationFuser 三遍扫描：UB 算子命中 fwd 融合表、Quantize+Bias 未匹配则保留 eager；③整体进 `_OperationFuserAutogradFunction`（`fuser.py:57`），UB 算子调 CommOverlap 的 split_overlap，普通算子逐个 compute；④torch.compile 下 fake impl（`custom_op.py:48`）保证 shape 推断。

## ⑤ 设计决策：为什么这么设计

**三遍扫描顺序**（joint→fwd→bwd）：融合收益 fwd+bwd 最大，先占最优区间，剩余再给单向融合。**custom op 注册放 `__init_subclass__`**：作者只声明 dataclass，注册自动发生，杜绝忘注册致 compile 静默回退；`compile_unsupported_reason`（:101）显式化原因。**反向融合多于正向**：训练大头在 bwd，`fused/backward_*` 反向主导非偶然。**UB 进 ops 体系**：通信算子化后与 GEMM/quantize 同被 fuser 调度——02 篇"通信即计算"的 Python 落点。

## ⑥ 新人提示：坑/入口/阅读顺序

- **入口**：`op.py:65` 协议→`fuser.py:432` 三遍扫描→`basic/quantize.py:18`→`fused/userbuffers_forward_linear.py:35`。
- **坑一：autocast 外 Quantize 是 identity**（`quantize.py:18`），量化没生效先查上下文。
- **坑二：compile 静默回退**——算子没注册 custom op 时仍能跑（eager），性能不对先调 `compile_unsupported_reason`。
- **坑三：fused 算子会被展平**（:457），basic 与 fused 混排是设计内行为。
- 新增算子三件套：args dataclass+compute+fake impl。
