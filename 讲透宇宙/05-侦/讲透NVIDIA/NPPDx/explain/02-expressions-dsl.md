# 02 · 表达式与算子 DSL 群：从 commondx 标签体系到 op_impl 特化族的编译期流水线

> 涉及文件：`include/commondx/detail/expressions.hpp`、`include/nppdx/operators.hpp`、`include/nppdx/operators/function.hpp`、`include/nppdx/detail/database/function/function_operation_implementation.hpp`（commit e7efdc12）

## 一、角色定位

NPPDx 的核心抽象不是函数调用而是**算子表达式的编译期组装**：示例代码里 `nppdx::Function<nppdx::function::resize>() + nppdx::Resize<J, K, Method>() + nppdx::TileSize<16, 16>() + nppdx::SM<Arch>() + nppdx::Block()` 这样一串 `+` 号拼出的类型，就是最终 kernel 的全部配置。这套 DSL 分三层：commondx 的**表达式标签体系**（表达式的"语法"）、nppdx/operators 的**算子词汇表**（可用的"单词"）、以及 database/function 的 **op_impl 特化族**（每个单词对应的 device 实现）。

`commondx/detail/expressions.hpp` 只有 51 行，却是整个继承树的根（图谱枢纽 fanIn=18 的 `operator_expression` 就住在这里）；`operators/function.hpp`（759 行，图谱枢纽 fanIn=14/fanOut=32）是词汇量最大的算子头；`function_operation_implementation.hpp`（660 行）把 8 种函数算子逐一映射为 `op_impl` 类模板特化。「勘误」：任务书所称"19 packing_format 宏特化族"并不在本文件——那 21 个 `format_backend<packing_format::X>` 特化实际分布在 `detail/backend/formats_impl/` 的 7 个族文件里（nv12_family.hpp:421 起，I42x_planar_family.hpp:494 起等），本文件管的是"函数算子"而非"像素格式"。

## 二、内部结构

**标签树（expressions.hpp:28-44）**：`expression` 为空基类，分两支——`operator_expression`（算子，再分 `block_operator_expression`/`device_operator_expression`）与 `description_expression`（描述，派生 `execution_description_expression`）。两个 constant 混入（L36-44）让算子同时是 `integral_constant<ValueType, Value>`，即"算子即编译期值"。L24/L49 的 namespace_wrapper 开合对把整棵树包进可重定位命名空间（定义 `COMMONDX_NAMESPACE_WRAPPER` 宏即可整体改名）。

**算子词汇表（function.hpp）**：`function` 枚举 9 值（L42-53）+ `function_tag<F>`（L55-59）构成"类别轴"；`Function<F>` 模板（L123-132）用 static_assert 白名单校验后携带枚举值。参数算子族全部继承 `commondx::detail::operator_expression` 并用 `tag_type` 指回类别：BoxBlur<W,H>（L137-152，halo=W/2）、GaussianBlur（L251-263，半径 0.1-10.0 双 static_assert 限界，wide 再限 ≤50）、Median（L297-306）、Sharpen（L329-336）、ColorConvert（L394-405）、GammaTransform（L433-442）、AffineChannelMap（L476-498，L481 特判"denominator==0 仅当 numerator==0 合法"）、Resize<J,K,Method>（L531-544，L537 强制 J/K 互素）。配套 `operation_operator_traits<function_tag<...>>` 特化提供三个查询函数 + `default_op`（box_blur 默认 `BoxBlur<3,3>` L173、gaussian `<20>` L283、resize `Resize<1,2,bilinear>` L609）。文件尾 L614-754 是 commondx::detail 侧的 `is_operator`/`get_operator_type` 特化对，让 DSL 解析器能识别每个参数算子。

**实现特化族（function_operation_implementation.hpp）**：`FuncOpImplHelper`（L40-53）先算 local_halo→output_region→aligned_cell_grid，再经 `NPPDX_MAKE_UINT2D` 把运行期值升格为模板参数，装配出 `aligned_cell_executor`。8 个 `op_impl<Operation, Layout, CellCfg, SM, BlockThreads>` 特化依次落位：ColorConvert（L61-95，寄存器+共享内存双路径）、GammaTransform（L100-147）、AffineChannelMap（L152-199）、BoxBlur（L204-297）、GaussianBlur（L303-344）、Median（L351-424）、Sharpen（L430-496）、Resize（L498-655）。

## 三、外部连接

`function.hpp` 是图谱 L08"图像算子 DSL"层的枢纽（fanIn=14/fanOut=32）：向上被 `operators.hpp` 聚合桶（operators.hpp:21-35，聚合 10 个子头）与 `traits.hpp` 引用，向下它包含 backend 的 resize_geometry/affine 操作头与 database 的 region/storage_config——**反向依赖**：算子层为算 halo/storage 不得不先知道几何细节。`function_operation_implementation.hpp` 处在 L11"函数算子后端"，由 `operation_database.hpp` 按 DSL 表达式实例化，其调用的 `backend::*_operations.hpp` 计算核位于 L12 层。commondx 侧 `is_operator_fd.hpp`/`get_operator_fd.hpp` 前置声明对（function.hpp:24-25 引入）专门打破 operators↔traits 循环包含。

## 四、数据流

全程编译期流动，共四跳：
1. **表达式求值**：用户 `+` 出的表达式类型被 nppdx_execution/描述算术（`nppdx_description_arithmetic.hpp`）折叠成"算子列表+布局+SM/Block 配置"的类型组。
2. **traits 查询**：对每个参数算子，经 `tag_type` 找到 `operation_operator_traits` 特化，拿到 `get_local_halo`（邻居半径）、`get_storage_config`（输入/输出/中间 tile 形状）、`get_output_nominal_tile`（resize 会改变 tile 尺寸，其余原样返回，如 L172/282/316）。
3. **halo 累积**：多个邻域算子串联时 MemoryHalo/CumulativeHalo 累加（见 fused_resize.cu:248 `total_halo = box_blur_halo + resize_halo`），决定 ingest 需多读的外圈。
4. **实现分发**：operation_database 解析出 `op_impl<Operation, Layout, CellCfg, SM, BlockThreads>`，execute() 按实参类型重载决议：寄存器路径收 `T*`、原地路径收单 tile 引用、双缓冲收 input+output、可分离 resize 收三 tile（function_operation_implementation.hpp:590-654）。

## 五、设计决策

- **标签/参数算子两件套**：`Function<function::box_blur>() + BoxBlur<3,3>()` 把"类别"与"参数"拆成两个类型再相加。好处是 traits 可以按 `function_tag` 键控分发（一个 tag 一份 traits，参数类型无关），新参数组合零成本。
- **dependent-false static_assert**：邻域算子不支持寄存器路径，实现用 `static_assert(!is_same_v<T,T>, "...")`（L214、L313、L359、L437、L548）而非 `=delete`——保留重载存在性，让错误信息带人话。
- **fast/slow 双路 cell**：邻域算子先判 `fully_valid`（整 cell 在有效区，L246-252），快路走专用 kernel，慢路逐像素 contains；展开度按寄存器压力启发式调（L271-273）。
- **高斯 tap 表**：tap_configs 十档半径带 3..21 tap（L203-214），wide 模式 taps=2×std−1；`get_tap_config`（L216-231）里 `gcc9_war` 假条件包住 fatal_error，是 GCC9 把非 constexpr 调用误判为必经路径的 workaround（L224-228 注释）。
- **resize 可分离两遍**：λ×λ 二维卷积拆成横竖两遍 O(2λ)，注释明言"critical for Lanczos on SM100"（L587-589）。

## 六、新人提示

1. **新增一个函数算子要动 5-6 处**：function 枚举、参数算子 struct、compute_local_halo/compute_storage_config 重载对、operation_operator_traits 特化、commondx::detail 的 is_operator/get_operator_type 对、op_impl 特化+backend 计算头。漏一处是编译期找不到实现的连锁报错。
2. **J/K 必须互素**（Resize L537），2x 缩放写 `<2,1>` 或 `<1,2>`，不要写 `<4,2>`。
3. **改 traits 的 get_output_nominal_tile 要谨慎**：只有 resize 改变 tile 尺寸，其余算子原样传递；这里错了会让下游 exgest 的 grid/block 全错。
4. **op_impl 的 execute() 是重载集**：新增存储路径时保持 `(T*, int, int)`/`(tile&, int, int)`/`(in, out, int, int)`/`(in, inter, out, int, int)` 的签名惯例，执行引擎按实参决议，别用模板万能参数破坏它。
5. **查 packing_format 后端请去 formats_impl/**：`is_implemented` 骨架在 format_backend.hpp:34-44（none/internal 空特化），真实 19 格式在 7 个族文件——function_operation_implementation.hpp 里没有它们。

