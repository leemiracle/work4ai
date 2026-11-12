# explain-12 · topi 算子库代表：python/tvm/topi/nn/conv2d.py（te 声明的终点）

## 角色定位

topi（TVM Operator Inventory）是 TVM 的**算子动物园**：`topi/__init__.py` 桶文件聚合 nn/generic/math/image/vision/sparse 各域，`testing/` 子包 52 个文件提供 numpy 参考实现（全仓测试基线），`cpp/` 是 C++ 注册路径。选 `nn/conv2d.py`（1512 行，本目录最重文件）作代表，因为它是**legalization 的最终落点**——relax 图里的 conv2d 算子经 legalize 转换后落到的 te（tensor expression）声明就在这里；同时它是新旧两代体系的交汇处：文件用 **te DSL**（`te.compute/te.sum`）写计算，产物经 `te/create_prim_func` 降级为 tirx PrimFunc 进入 explain-04/05 的调度世界。文件内并存三条实现路线：通用 `conv`（任意维+分组）、布局特化函数族（NCHWc 打包/int8）、Winograd 快速卷积线。

## 内部结构

**Workload 载体（L37-58）**：namedtuple 打包 17 个字段（dtype/shape/padding/stride/dilation/groups）——算子 dispatch 与 Winograd 决策（tile 选择要查 workload）的统一货币。

**入口与布局分发（L61-273）**：`conv2d`（L61-99）是用户入口，直接委托 `conv(..., groups=1)`（L99）；`_get_workload`（L102-151）做形状/padding 规范化（`get_pad_tuple` 把 padding 折成四边），L130-131 的 dtype 断言留了量化口子（uint8 数据 × int8 权重合法）；布局特化族 `conv2d_nchw/hwcn/nhwc`（L154/184/214）。

**打包布局族（L275-1003）**：`conv2d_NCHWc`（L275，ARM 类后端的 packed layout "NCHWnc"）、`conv2d_NCHWc_OIHWo`（L398，权重也打包）、`conv2d_NCHWc_int8`（L526，量化线）、`group_conv2d_nchw/nhwc`（L694/933）、`unpack_NCHWc_to_nchw`（L971，输出还原）——每个都是"某 target 某数据类型的专门声明"。

**Winograd 线（L659-1512）**：`conv2d_winograd_weight_transform`（L659）与 nhwc/nchw 两套入口（L1004/1060）、两套 `_impl`（L1115/1283）、`without_weight_transform` 变体（L1414/1465，权重已预变换时跳过运行期变换）——F(2×2,3×3)/F(4×4,3×3) 类快速算法把乘法数降 2-4 倍。

**通用主菜 `conv`（L732-931，本篇重点）**：支持任意维（`dim = len(inp.shape) - 2`，L805）+ 分组。前半段是**布局代数**：L820-830 用 `data_layout.find("N")/find("C")` + 正则 `[^NC]` 把任意布局（NCHW/NHWC/HWCN 甚至自定义）算成 to/from 置换表；L832-846 同法处理 kernel_layout，**未指定时按 C 与 HW 的相对位置推断默认权重布局**（L836-839）——L834-835 留着开发者 tkonolige 的坦白注释 "I don't really understand kernel ordering for NHWC"，真实代码考古现场。L848-849 与 L859-860 两处 `raise RuntimeError("LEGACY-FLOW triggered, to be removed")`——**fork 已废老 auto_scheduler 的布局改写入口**，新代码线只剩 meta_schedule/dlight。形状数学在 L864-878：dilated kernel、输出维度公式、负输出形状显式报错。计算图本体 L880-917：`pad` 前置（L882）、`te.reduce_axis` 按核维度建（L883-884）、`compute` 闭包（L886-906）里分组索引 `ff // (num_filter // groups) * (in_channel // groups) + rc`（L888-890）实现 group conv 的通道偏移；L903-905 的注释点破一个关键约定——"**Schedules depend on reduction axes being in the same order as the layout**"，所以 reduce axis 按布局置换重排后才交给 `te.sum`；最终 `te.compute` 挂 `tag=f"conv{dim}d_{layout}"`（L911，legalization 靠 tag 识别）、`layout_free_placeholders` attrs（L914，允许调度器改写权重布局）、`varargs_names`（L915，TVMScript 打印用）。

## 外部连接

- **te 层**：`tvm.te.compute/reduce_axis`（explain-03 讲过的 Reduce/CommReducer 节点在此消费）；`create_prim_func` 把本文件产物降级为 PrimFunc——relax `emit_te` 的下半程。
- **relax legalization**：`python/tvm/relax/op/nn` 的 conv2d 到 te 声明的映射按 tag/属性路由；Byoc（bring-your-own-codegen）后端也靠 Workload 结构对接。
- **调度层**：`topi/cuda/conv_*` 系列（target 专属调度）直接匹配这些声明；dlight 的 matmul/reduction 规则接管 PrimFunc 化后的 kernel；`topi/generic` 是无 target 特化时的兜底调度。
- **测试**：`topi/testing/conv2d_nchw_python.py` 等 numpy 参考实现与 CI 的全 target 回归矩阵。
- **cuda intrin 线**（任务备选主角）：`topi/cuda/tensorcore_*` 与 `src/target/source/intrin_reduction.cc` 类文件把 WMMA/MMA 内建映射进 te——同样的"声明+调度"分工。

## 数据流

relax 图 conv2d 算子 → legalize 查 target → 选 plain（本文件 conv）或 Winograd 或 Byoc → te.compute 建立惰性计算图（此刻无任何循环，只有张量级公式）→ create_prim_func 物化成 PrimFunc（te.sum 展开成 SBlock+reduce 循环，进入 explain-04 的语句世界）→ dlight/meta_schedule 调度 → codegen。te 层的"声明"与 tirx 层的"实现"严格分层：topi 只描述数学，循环结构与内存层次全部留给调度器。

## 设计决策

1. **声明与调度分离**：topi 不写一行循环绑定——同一个 conv 声明可被 CPU/GPU/NPU 各自的调度复用。这是 TVM 与"手写 kernel 库"的根本分野。
2. **布局代数而非布局枚举**：conv() 用置换表数学吃任意布局，新布局零代码接入（代价是 L834 的理解成本注释所自嘲的复杂性）。
3. **tag 与 attrs 双通道**：tag 供 pattern/legalize 识别，attrs（layout_free_placeholders）供调度器声明改写权限——元数据即接口。
4. **legacy 出口显式炸毁**（L848/L859）：不做静默兼容，跑老参数直接 RuntimeError——fork 清理历史包袱的干净姿势。
5. **reduce axis 顺序契约**（L903-905）：以注释形式钉下"归约轴顺序必须匹配布局"的不变量——违反它调度就 silently 错，这类跨层契约是 topi 维护的真正难点。

## 新人提示

- 加新算子照 conv2d 的四件套走：te 声明（generic）+ target 调度 + testing 参考实现 + relax op 映射；漏 testing 会在 CI 全 target 矩阵上还债。
- "negative output shape"（L875-878）报错先查 padding 与 stride/dilation 组合，多数是 pad 小于 (k-1)*dil。
- Winograd 不是免费午餐：tile 选择依赖 workload 形状（L659 的 transform 注释），动态形状场景常退回普通 conv。
- 想看 fork 与上游 topi 的差异面：grep "LEGACY-FLOW" 全 topi——auto_scheduler 时代的参数已全部封死，新代码别再传。
