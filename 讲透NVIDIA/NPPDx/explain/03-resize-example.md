# 03 · resize 全链：有理数重采样的数学实现与 04_resize 渐进示例互证

> 涉及文件：`include/nppdx/detail/backend/resize_geometry.hpp`、`include/nppdx/detail/backend/resize_operations.hpp`、`include/nppdx/detail/database/function/function_operation_implementation.hpp:498-655`、`example/nppdx/04_resize/resize_example.cu`、`example/nppdx/04_resize/fused_resize.cu`（commit e7efdc12）

## 一、角色定位

resize 是 NPPDx 中最复杂的函数算子——全库唯一**改变 tile 尺寸**的操作，也是唯一需要中间缓冲（intermediate tile）的算子。「勘误」：任务书所指的 `include/nppdx/resize.hpp` 并不存在；resize 的公共入口是算子 `Resize<J, K, Method>`（定义在 operators/function.hpp:531-544），实现分布在三处：输出尺寸几何（resize_geometry.hpp，46 行）、滤波核与采样数学（resize_operations.hpp，456 行）、执行编排（function_operation_implementation.hpp 的 op_impl 特化）。04_resize 两个示例是这套实现的最佳消费者：resize_example.cu 演示单算子管线，fused_resize.cu 演示 blur+resize+convert 五步融合并与 NPP 三步法对拍。

## 二、内部结构

**几何（resize_geometry.hpp:27-42）**：`compute_resize_output_nominal_dim` 实现 N_O = ⌈(2·N_I·K − J) / (2J)⌉——分子用 `long long` 防溢出（L30-33），除法用 `dir_quot<-1>`（负方向除法=向上取整，正是入口层 utils.hpp:113-121 那套有向商余的消费者）。

**滤波核（resize_operations.hpp:41-124）**：`filter_computed_properties` 汇总半径/taps；四个 1D 核全部 `__device__ __forceinline__`：nearest（L66-68）、bilinear 帐篷函数（L71-74）、bicubic Catmull-Rom（L77-85）、lanczos3（L88-94，sinc 用 `__sinf` 快速数学版 L57-63）。`evaluate_2d_kernel`（L115-124）对 lanczos3 用径向距离 sqrt(x²+y²)，其余方法退化为可分离乘积。

**相位与索引（L134-200）**：纯整数算术。`compute_phase_index`（L134-144）算 phase_num=(2n_O·J+J−K) mod 2K，L141-142 手写负数安全取模；`compute_center_input_index`（L157-163）对负分子做向下取整除法；`compute_delta`（L174-181）偶 λ 恒 2、奇 λ 按相位取 1/3。

**Q 张量（L207-267）**：`QWeightsGenerator`（L247-261）在 constexpr 循环里生成 V=K×λ 的相位×tap 权重表，运行期 gather 只做查表（`lookup` L263-267）——把 sinc/bicubic 求值从热路径挪到编译期。

**采样主体**：`gather_1d`（L301-329）查 Q 表累加并按 weight_sum 归一化（L328，边界处权重和≈0 时退回原始和）；`resize_horizontal_row`（L366-383）/`resize_vertical_pixel`（L387-401）组成可分离两遍；`resize_2d_non_separable`（L410-449）走 λ² 双层 tap 循环，`taps_for_lambda`（L285-293）规定 λ≤9 才展开。

**执行编排（function_operation_implementation.hpp:498-655）**：编译期护栏三连——tile 太小防无符号下溢（L519-521）、输出/中间 tile 超 SM 上限（L530-540）；两个 execute 重载：不可分离（L553-585，input→output）与可分离两遍（L590-654，input→intermediate→output，L587-589 注释明言 O(2λ) 对 O(λ²) 的收益"critical for Lanczos on SM100"）。

## 三、外部连接

resize_operations.hpp 被两端引用：算子侧 `operators/function.hpp:29`（引入 resize_geometry 算输出 tile）与实现侧 `function_operation_implementation.hpp:32`（引入 resize_operations 拿计算核）。示例侧经伞头 `<nppdx.hpp>`（resize_example.cu:21）接入全部公共面。`cpu_resize_reference.hpp` 提供 CPU 金标准（resize_example.cu:27 引入），是 GPU 结果的验收基准。fused_resize.cu 还可选引入 NPP（L48-50，`NPPDX_EXAMPLE_HAS_NPP` 宏门控）做三步法计时对比。

## 四、数据流

**单算子示例（resize_example.cu:35-55 的 resize_kernel）**：三步 `Ingest().execute(input, input_tile) → Resize().execute(input_tile, intermediate_tile, output_tile) → Exgest().execute(output_tile, output)`。类型组装在 run_nppdx_resize（L64-143）：先用 `ResizePre` 探问 `local_halo`（L75-77），据此构造带 halo 的 Ingest（L80-82，`NPPDX_MAKE_HALO(MemoryHalo, resize_halo)`）、三 tile 的 Resize（L85-86）与空 halo 的 Exgest（L92-97）；`output_storage_of_t`/`temp_storage_of_t`（L87/99-100）从 DSL 类型直接提取存储类型；共享内存经 `slice_into_tile_storage` 切片（L41-45），超 48KB 时 `cudaFuncSetAttribute` 申请（L128-130）。

**融合示例（fused_resize.cu:192-222）**：五步 ingest→boxblur→resize→colorconvert→exgest 全在一个 kernel 的 smem 里接力；halo 预算 `total_halo = box_blur_halo + resize_halo`（L248），逐算子**递减消费**——blur 用 MemoryHalo=total 但 CumulativeHalo=total（L257-258），resize 把 CumulativeHalo 收窄到 resize_halo（L262-263）。

## 五、设计决策

- **有理数 J/K 而非浮点比例**：互素整数让相位 m∈[0,K) 有限可枚举，Q 权重表因此能在编译期算满 K×λ 项；运行期零三角函数（热路径只剩查表+乘加）。
- **λ 取偶策略**：taps 向上取偶（function.hpp:557-565）避免奇 λ 的半像素相位特例，代价是某些比例多做一点无效 tap——resize_operations.hpp:357-361 注释明说这是简化公式的取舍。
- **「勘误」示例注释与实际方向相反**：resize_example.cu:58 头注释写"2x Upscale"，但 L158-159 实际 j=2、k=1（J=2 输入采样→K=1 输出采样），是 **2x downscale**（输出 156x188）；运行打印也自我矛盾（L111 会打印 downscale）。fused_resize.cu:469-476 才是真 2x upscale（J=1,K=2，输出 624x752）。
- **clamp 策略差异是融合示例的真正主题**：NPPDx 在 exgest 才 clamp Y/U/V（fclampf +0.5 四舍五入，fused_resize.cu:85-88），NPP 风格是 YUV 转换前先饱和 RGB（L90-93）；CPU 参考用 `ClampRgbBeforeYuv` 模板双臂复现两种语义（L115-180），blur+nearest 下两者数值一致（凸组合不越界，L559-561 的判定打印）。
- **占位架构的诚实标注**：文件头 L22-25 明言"整块 resized RGB 驻留 smem 只适用于小 tile，未来由 exgestResize 流式方案取代"——这是设计债的显式记录而非隐藏。

## 六、新人提示

1. **tile 尺寸必须被 J/K 整除前提**：resize_example.cu:69-70 注释选 16x16 因其整除 312x376；改测试图或 tile 时先算 `compute_resize_output_nominal_dim`，否则触发 op_impl 的 static_assert 护栏（function_operation_implementation.hpp:519-540 会给出人话报错）。
2. **grid/block 随缩放方向切换**（resize_example.cu:119-121）：downscale 按 Ingest 的输入网格，upscale 按 Exgest 的输出网格——两个方向的"每线程一像素"锚点不同，抄示例时别删这个三目。
3. **改采样数学须同步 CPU 金标准**：Q 表、λ 取偶、clamp 顺序三处任何一变，cpu_resize_reference 与 GPU 立即对拍失败；这个示例的可信度正建立在双侧同构上。
4. **中间 tile 生命周期**：可分离两遍之间有 `__syncthreads()`（function_operation_implementation.hpp:627/653），给 Resize 增 pass 时每遍末尾同步不可省。
5. **新增插值方法**：改 `NPPDX_FOR_INTERPOLATION_METHODS` 宏（function.hpp:108-112）、补 kernel 函数与 `get_filter_props` 分支（L568-576）、再补 constexpr_math 对应核（compute_Q_weight 的编译期版本 resize_operations.hpp:221-238），三处缺一不可。

