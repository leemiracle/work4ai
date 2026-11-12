# tile_kernels/engram/engram_gate_kernel.py 精讲

> 原文件：`tile_kernels/engram/engram_gate_kernel.py`（570 行）

## ① 角色定位

仓库**最大的单文件内核**，实现 Engram 架构的记忆门控算子：对每 token 的 `hc_mult` 个头通道做 `output = x + g·v`，门控 `g = sigmoid(signed_sqrt(clamp(dot(x̂, k̂·w))))`，`x̂/k̂` 为 RMSNorm 后的隐状态与键嵌入，是"用 TileLang 把完整非线性算子压进持久内核"的代表作。

## ② 内部结构

- **`get_engram_gate_fwd_kernel`**（11-182 行）：`@tilelang.jit` 工厂，参数含 `hidden_size/eps/scalar/stride 系列/num_sms/clamp_value/hc_mult=4/save_for_backward`。两个启发式：`_choose_blk_d` 从 `{1024,768,512,256}` 选整除且 ≥2 倍的块；`_choose_num_persistent_blocks` 按 smem 估每 SM 块数（寄存器压力帽 16）。grid `(hc_mult, num_persistent_blocks)`，32 线程一 CTA；`T.StridedTensor` 把 k/v 的 stride 编译期绑定。
- **`get_engram_gate_bwd_kernel`**（192-467 行）：8 warps（每头两 warp），go 与 v 全量驻 smem，x/k/w 双 bank 流水，`T.Fragment` 指定 async_copy 线程映射。
- **Python 封装**：取 stride 与 SM 数、分配输出。

## ③ 外部连接

`config.get_num_sms/get_max_smem_per_sm` 是占用估算输入；modeling 层把 fwd/bwd 包成 autograd.Function，反向再调 `grad_w_reduce` 把部分梯度归约到 `grad_wh/grad_we`，支持 `main_grad` 就地累积。前向保存 `dot/gate_score/rstd_x/rstd_k` 四个小张量；`save_for_backward=False` 时全 None（推理省显存）。

## ④ 数据流

**前向两遍**（每 token）：Pass 1 归约——`cp.async` 双缓冲（`kv_smem (2, blk_d)` 交替 + `x_smem` 全量）流水加载 x 与 k，寄存器累积 `Σx²、Σk²、Σx·w·k`；warp 归约后 `rstd = rsqrt(sum/h+eps)`，`z = dot·scalar·rstd_x·rstd_k`，`g = sigmoid(copysign(sqrt(clamp(|z|,clamp_value,∞)), z))`。Pass 2 输出——v 复用 `kv_smem` 双 bank，逐 tile 写 `x + g·v`；最后 tile 处预取**下一 token** 的 k/x，token 间也流水。**反向三段**：Pass 1a 算 `dL/dg`——每头两 warp 各算 `Σ go·v` 一半，经 smem 合并，乘门控导数（clamp 死区零梯度）；Pass 1b 算 `grad_v = Σ_h go·g`；Pass 2 逐 tile 算 `grad_x = go + dldg·(k·w − x·dot_x)`、`grad_k = dldg·(x·w − k·dot_k)`（`dot_x/dot_k` 是 RMSNorm 均值回传项），`grad_w` 寄存器跨 token 累积、块尾写部分和。

## ⑤ 设计决策

- **持久内核模式**：grid 由 SM 占用估算定死而非随 token 数膨胀，token 循环在内核里跑——省掉千次 launch，流水跨 token 延续。
- **双 bank cp.async + `ptx_wait_group(N)` 分组等待**：只等最老 N 组 copy、新 copy 继续飞——Ampere 异步拷贝的标准手动流水。
- **smem 复用**：`kv_smem` 先当 k 的流水缓冲、Pass 2 摇身变 v 的流水缓冲。
- **梯度两级归约**：`grad_w` 先寄存器累加、再落部分和、最后独立小内核归约——避免原子加竞争；`clamp_value=1e-6` 前向防 `sqrt(0)`、反向死区零梯度。

## ⑥ 新人提示

1. 先读懂前向"双遍"再攻反向：反向三段是链式法则按数据依赖的重排，`dldg` 是贯穿两者的标量枢纽。
2. 调流水气泡时 `TK_PRINT_KERNEL_SOURCE=1` 看生成的 CUDA，`cp.async` 原语与④一一对应。
3. 换 hidden_size 先跑基准再优化；改启发式记得 `go_blk_d + x_blk_d <= hidden_size` 守恒约束。
