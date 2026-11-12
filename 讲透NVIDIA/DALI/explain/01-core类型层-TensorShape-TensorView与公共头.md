# 01 · core 类型层：TensorShape / TensorView / WorkspaceBase / convert 等公共头

## 角色定位

`include/dali/core/` 是 DALI 全库的"标准库"——对外安装的头树，定义一切数据结构的根语义：形状（tensor_shape.h）、零拷贝视图（tensor_view.h/span.h）、数值转换（convert.h）、编译期分派（static_switch.h）、执行顺序（access_order）与小容器（small_vector.h）。图谱把它划为 L02「核心类型与设备原语」层（144 节点），import 入度统计坐实其基石地位：static_switch.h 被全仓 187 处 import（全库第一），convert.h 70 处、tensor_shape.h 68 处、span.h 55 处、tensor_view.h 54 处。kernels（kernel.h，76 处）、pipeline 算子框架（operator.h，98 处）都站在这层之上。它同时是 host/device 双端代码：大量成员带 `DALI_HOST_DEV` 标记，同一份头同时被 NVCC 与宿主编译器消费。

## 内部结构

形状系统走"静态/动态维度双态"设计：`DynamicDimensions = -1`（tensor_shape.h:34）、`InferDimensions = -2`（tensor_shape.h:35）两个哨兵值区分运行期与编译期维度数。通用基类 `TensorShapeBase<Container, ndim>`（tensor_shape.h:89）实现 operator[]/begin/end 与 `num_elements()` 走 `volume(shape)`（tensor_shape.h:136-137）；动态特化（tensor_shape.h:189）以 `SmallVector<int64_t, 6>` 为容器（tensor_shape.h:183），静态特化 `TensorShape<ndim>`（tensor_shape.h:268）换 `DeviceArray<int64_t, ndim>` 栈上存储。

视图层 `TensorViewBase`（tensor_view.h:102）只有 `DataType *data` 与 `TensorShape<ndim> shape` 两个成员（tensor_view.h:127-128），配坐标寻址 `operator()` 走 `CalcOffset`（tensor_view.h:110-117）与 `to_static<other_ndim>()` 升静态（tensor_view.h:121）；动态特化在 tensor_view.h:144。批级 `TensorListView` 三件套在 tensor_view.h:246/474/559；后端标签 `StorageCPU/StorageGPU` 定义于 tensor_view.h:641-642。span.h 是 C++20 前自带的 span：`dynamic_extent`（span.h:33），定长特化默认构造被 `= delete`（span.h:51）强制显式给长度。

转换层 convert.h 用 `needs_clamp` 元函数（convert.h:56，bool 特化 74）判定"目标类型装不下"，`clamp(U, ret_type<T>)` 按 signed/unsigned/FP 三路重载（convert.h:87-153）；`ConverterBase`（convert.h:239）+ `Converter` 门面（convert.h:242）按 FP/枚举组合偏特化——FP→FP 直通（convert.h:252），float16 特化先经 float 中转再截断避免双重舍入（convert.h:279-300）。`Convert/ConvertSat/ConvertNorm/ConvertSatNorm` 四语义贯穿后续所有 cast kernel。

分派层 static_switch.h：`TYPE_SWITCH`（static_switch.h:97）与 `VALUE_SWITCH`（static_switch.h:131）用 Boost.Preprocessor 把运行期 type id 炸开成 switch-case，`__CUDACC__` 下强制 `BOOST_PP_VARIADICS 1`（static_switch.h:20-25）。

## 外部连接

上游几乎没有依赖（仅标准库、CUDA runtime 与 Boost.PP），下游是全库：kernels 执行框架拿 TensorShape/TensorView 做核函数签名；pipeline/data 的 Tensor/TensorList（L07 层）在 share/views 互转时反查这层——tensor_list.h 的 State 内嵌类管理分配状态机后，对外暴露的就是这层视图类型；算子参数类型擦除（argument.h 的 `Value<T>/ArgumentInst`）与 types.h 的 `DALI_TYPE_MAP` 宏都消费 convert 的转换表。access_order（access_order.h:31 `AccessOrder`）被 workspace 与 executor 用来表达"数据在哪个流上可见"，null/host/设备三值语义（access_order.h:42 `host()`）。跨界的 workspace.h（workspace:51 `ArgumentWorkspace`、workspace:138 `WorkspaceBase<DataObject, ptr_t>` 模板、workspace:766 `Workspace`）把视图层与执行器缝在一起：算子 Run 拿到的输入输出容器就是这里的 DataObject 实例。

## 数据流

典型一次算子调用的类型流：reader/loader 产出裸指针+shape → 包装成 `TensorView`（不持有）或 `Tensor/TensorList`（持有，走 L03 内存资源）→ 执行器装进 `WorkspaceBase` 输入槽 → 算子 Setup 用 shape 推输出 shape → `TYPE_SWITCH(dtype)` 炸到具体模板实例 → kernel 以 `TensorView` 读写 → `Converter::ConvertSat` 完成 dtype 变换落盘。多流场景下 `AccessOrder::wait`（access_order.cc:31）负责跨流同步：`is_ambiguous_handle`（access_order.cc:27）识别 stream 0/PerThread/Legacy 三种歧义句柄，经 `CUDAEventPool`（access_order.cc:50）记录事件而非直接引用句柄。

## 设计决策

1. 静态/动态 ndim 双态是全库最深的取舍：静态 ndim 换编译期优化但迫使 `TYPE_SWITCH` 级实例化爆炸，DALI 用"动态外壳+to_static 内核"折中。
2. 视图不持有内存：所有权全部下沉到 mm/ 资源层（L03），视图层保持可裸拷贝的值语义，kernels 与算子间传参零引用计数开销。
3. clamp 语义显式化：负数转 unsigned 夹到 0（convert.h:67 注释）这类"安全转换"由元函数在编译期裁决，避免运行时分支。
4. TYPE_SWITCH 选宏而非 C++17 if-constexpr：case 体要同时进 host/device 两套编译单元且支持嵌套（文件头注释自述"can be safely (?) nested"）；代价是 tree-sitter 对其零提取（NOTES-DIGEST batch-32 甄别），图谱节点靠人工补扫。
5. span 定长默认构造删除（span.h:51）、AccessOrder 删 int 构造（access_order.h:37）：用删除函数挡住"看起来合法实则危险"的构造路径。

## 新人提示

阅读顺序建议 static_switch.h → tensor_shape.h → tensor_view.h → convert.h：先懂分派宏才能看懂任何 kernel 的实例化方式。记住两个哨兵：-1 是"维度运行期定"、-2 是"维度由推导得出"，代码里大量 `TensorShape<>` 空模板参即动态态。每个头在 dali/core/ 下有同名 *_test.cc/cu（如 tensor_shape_test.cc、convert_test.cc），是行为语义的最好文档。查"转换结果被夹住"先看 needs_clamp 特化表；查"stream 同步没生效"先看 access_order.cc:27 的三种歧义句柄。SmallVector（small_vector.h:155）默认容量 6 正好覆盖 DALI 常见 ndim（NCHW=4、序列+帧=5~6），热路径形状操作不进堆。
