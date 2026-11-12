# 03 · attention 栈——DISCO 的对偶、显式布局与 ring 版 online softmax

> 源文件：`torch_harmonics/attention/attention.py`（588）+ `_layout.py`（186）+ fwd_ring.cu（1198）/bwd_ring.cu（2212，最重）/ attention_torch.py（874），共 5058 行。图谱定位：与 disco 同构的第二次 instantiation。

## ① 角色定位：这个子系统解决什么问题

`NeighborhoodAttentionS2`（`torch_harmonics/attention/attention.py:253`）把注意力限制在测地邻域盘内——O(N²) 降到 O(kN)，softmax 对求积权重积分（Bonev 2025），近似 SO(3) 等变。它是 DISCO 的 attention 对偶：**复用同一个 `_precompute_convolution_tensor_s2` 构造稀疏邻域**（dummy zernike 基只取支撑，`torch_harmonics/attention/attention.py:379`），同一 ψ 邻域做 QK^T·V；全局版 `AttentionS2`（`torch_harmonics/attention/attention.py:49`）走谱域。栈分三层：Python 分发/CPU 内核/CUDA 内核。

## ② 内部结构：关键类/函数与行号锚

**方向与布局**：`__init__` 按 nlon 整除关系选 gather/scatter 方向（`torch_harmonics/attention/attention.py:340`）。CUDA 消费"连续弧"稀疏结构 `_build_psi_segments`（`torch_harmonics/attention/attention.py:422`）——邻居列号由计数推出，省掉 GPU 无指令的 64 位整除。forward 在模块边界转 NHWC 全程驻留（`torch_harmonics/attention/attention.py:533`）：1×1 投影变 GEMM，:568 分派。

**布局层（`torch_harmonics/attention/_layout.py`）**：docstring 钉死"never infer"规则（:40）——**退化维度下 stride 无法区分 NCHW/NHWC**（H·W==1 或 C==1 时互相欺骗），猜错会静默改变输出形状。CUDA 路径用 tiled transpose，互逆设计使反向也走快内核；`_permuted_copy`（`torch_harmonics/attention/_layout.py:122`）view 已连续时也 clone。

**ring 前向（`attention_cuda_fwd_ring.cu`）**：服务分布式版——K/V 在 azimuth 组间轮转，每 chunk 一次调用，softmax 状态累积进外部 buffer（y_acc/alpha_sum/qdotk_max）。generic 内核（`torch_harmonics/attention/optimized/kernels_cuda/attention_cuda_fwd_ring.cu:67`）核心是 flash 式流式更新 `alpha_sum = alpha + alpha_sum*exp_save`（:160-166）；极点长行走三段式 softmax→rescale（`torch_harmonics/attention/optimized/kernels_cuda/attention_cuda_fwd_ring.cu:361`）→finalize（:423）。

**ring 反向（`attention_cuda_bwd_ring.cu`，2212 行）**：头注释 :55-60 钉死两遍结构——pass1 重算 softmax 统计量并缓存 dq 终算缓冲；pass2 用终态对当前 KV chunk scatter dk/dv。generic（pass1 `torch_harmonics/attention/optimized/kernels_cuda/attention_cuda_bwd_ring.cu:78`/pass2 :1312）与 special（双块向量化，:1477）双路径各两遍。

**纯 torch 参考（`attention_torch.py`）**：反向拆 dv/dk/dq 三函数对应三梯度路径（`torch_harmonics/attention/kernels_torch/attention_torch.py:133` 起）；`register_fake`（`torch_harmonics/attention/kernels_torch/attention_torch.py:466`）为 PT2 注册 meta 内核，:431-457 注释记录真实 bug：5D permute 链输出逻辑 NHWC 物理 NCHW stride，违反 meta 承诺布局，aten.view 在真实 stride 上炸，eager/autocast 都察觉不到。

## ③ 外部连接：与哪些子系统互依

向下复用 disco 构造器与 quadrature；ring 内核被 `distributed/distributed_attention.py` 独家消费。向上 S2Transformer/S2Segformer；`tests/test_attention.py` 15 测试覆盖等价/perf/形状。

## ④ 数据流：一次典型调用的路径

以 self-attention、H100 为例：query NCHW 进 forward → `to_nhwc`（同名只转一次）→ 三次 F.linear → 可选 rms_norm+scale → handle 带 ψ 三件套进内核：warp 按 (ho,wo) 认领输出点，沿 ψ 行 qdotk→在线 softmax→加权 V 累加 → 输出投影 → `to_nchw` 回 NCHW。分布式时换 ring 版，softmax 状态用 buffer 续传。

## ⑤ 设计决策：为什么这么设计

**为什么复用 DISCO 构造器？** attention.py:369-372 注释直言：稀疏模式预计算与常值滤波器卷积一致，挂 kernel_shape=1 的 dummy 基即免代码重复——限带/旋转/支撑代码服务两种算子，邻域语义严格一致。

**为什么反向两遍？** 归一化因子依赖全部 ring step 的统计量，dk/dv 又依赖归一化后权重——pass1 先算完统计量与 dq 中间缓冲，pass2 才能对每 chunk 独立 scatter。

## ⑥ 新人提示：坑/入口/阅读顺序

- **阅读顺序**：`attention.py:253` docstring（数学最全）→ `_layout.py:32` 模块 docstring → 两个 ring.cu 的头注释 → register_fake 节。
- **nlon 整除是硬约束**（:341-342）；改布局代码先读 :40——"从 stride 推断布局"被明令禁止。
- **bwd_ring 的 printf 残留**在 `#if 0` 块（:747），死代码非开关。
- **分布式 ring 的 col_idx 已预移位**：单独复用内核必须自己重算，否则邻居定位错位。
