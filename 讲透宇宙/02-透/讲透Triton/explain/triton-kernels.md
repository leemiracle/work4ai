# python/triton_kernels/triton_kernels/matmul_details/_matmul.py — 参考算子库的工业级 matmul 内核

## 1. 角色定位

13 层架构中属 **kernels-library（triton_kernels 算子库层）**，tour 第 11 步。`python/triton_kernels/` 是官方参考算子库。主角 `_matmul.py`（672 行）是**非 persistent 主内核**：单文件覆盖 dense/MoE-ragged/gather-scatter/MX 低精度/融合通信全部形态；宿主 `matmul.py` 负责规范化、opt_flags 决策与参数装配。

## 2. 内部结构

- **`_matmul`**（L41-672）：`@triton.jit(do_not_specialize=[...])`（L41-42，标注参数禁特化防重编译）。约 110 参数 12 组：三层 scale（L44-54）、MoE 与 ragged 调度（L60-66）、激活/epilogue 闭包（L70-74）、精度与优化 constexpr（L78-96）。契约靠 `tl.assume`（L111-131）与 `tl.static_assert`（L145-198）编译期把关。
- 设备侧 helper：`round_f32_to_tf32`（L26，Hopper+ 用 `cvt.rn` 匹配 TMA 舍入）。
- 宿主 `matmul.py`：`SpecializationModule`（L81-87）把激活/epilogue 注册成闭包 constexpr；`make_opt_flags`（L425-436）定全部启动参数；五处 `make_tma`（L528-610）；launch（L659-726）；split_k>1 接 `reduce` 后处理。

## 3. 外部连接

`_matmul.py` 出边（图谱 imports）：`_common.py`（compute_pids/compute_offsets 等）、四代硬件 scale 反 swizzle（blackwell/hopper/cdna4/gfx1250_scale）、numerics、`target_info`。入边：`matmul.py` 唯一生产消费者；后者再挂 `_p_matmul`（persistent 版）/opt_flags/reduce/tensor，被 test_matmul.py 等引用。

## 4. 数据流（一次 dense 前向）

宿主：断言布局（fp8 权重在 capability<10 必须列主，L308-309）→ `make_opt_flags` 定 block/warps/stages/split_k → persistent 路径建 TMA 描述符 → `kernels._matmul[(grid,)](...)`（L659）。设备侧：

1. pid（L215）→ padding 早退 → `compute_pids`（L232，GROUP_M 分组 + XCD swizzle 保 L2 局部）→ `compute_offsets`（L234，ragged 到块偏移）。
2. 指针装配（L285-382）：`offs_x_m` 先 `%eM` 回绕再 `tl.multiple_of/max_contiguous`（L286）给向量化证据；gather 走 `GatherIndx` 免边界检查；W scale 按四代硬件分支算 swizzle 偏移。
3. K 主循环（L389-506）：`EVEN_K` 免 mask；f32 按需 tf32 舍入；MX 块 scale 反 swizzle；dot 按精度派发：fp4 上采（L459/L468）、`tl.dot_scaled`（L484-489）、稠密 `tl.dot`（L497-501）；SWAP_XW 时累加器转置（L385）。
4. epilogue（L507-668）：tensor scale 循环外一次乘回 → bias/betas/gammas → flexpoint scale → 激活 → 写回（scatter、fp4 打包、MX 在线量化、fused comm 写远端）。

## 5. 设计决策

**弃 @triton.autotune 改查表**：全库 grep 不到 `triton.autotune`（实证）。工业部署付不起每个 (M,N,K,dtype,arch) 组合的 bench 税与首调用延迟抖动；`opt_flags_nvidia.py` 的 `compute_block_n/block_k/split_k/num_stages` 用经验查表在 launch 前定死参数——确定性换峰值。**megakernel + constexpr 死代码消除**：约 40 个 constexpr 编译期裁变体，static_assert 构成契约；代价 672 行 110 参换变体集中管理。**tiling 与调度**：GROUP_M swizzle 同行块聚簇提升 W 复用；`tl.assume/multiple_of/max_contiguous` 三件套（L111/L286/L353）是"向编译器递证明"惯用法。**管线**：num_stages 查表，A100 ragged-K 强制 stages=1（宿主 L456-457）；persistent 版独立成 `_p_matmul.py`（CLC 动态调度）保主内核可读。**精度**：行级 tensor scale 留 K 循环外一次乘（L477-478），省 K 次乘法。

## 6. 新人提示

切入点：`tests/test_matmul.py`（与 matmul_torch 对拍）。易错点：① fp8 权重在 capability<10 必须 `b.stride(-2)==1`；② Blackwell shuffled 布局强制 persistent kernel 且 block 尺寸须与布局一致（宿主 L441-453）；③ 加精度路径先补 static_assert 否则静默错值；④ SWAP_XW 时 acc 与写回全转置（L385）。
