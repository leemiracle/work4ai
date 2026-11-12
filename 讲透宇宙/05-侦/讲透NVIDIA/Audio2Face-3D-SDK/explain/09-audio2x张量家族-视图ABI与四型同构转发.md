# 09 · audio2x 张量家族——16 字节视图 ABI、四型同构转发与 80 行错误 switch

## 角色定位

`audio2x-common/include/audio2x/` 的 tensor 系列头（tensor_void/tensor_bool/tensor_float/tensor_int64/tensor_uint64/tensor.h/tensor_dict.h）构成整个 SDK 的**内存词汇表**：音频样本、情感向量、blendshape 权重全部以"张量视图"传递。核心设计是**类型擦除底座 + 四标量类型同构复制**：`tensor_void.h` 定义类型无关视图，四型视图同构化；`tensor_dict.h` 提供命名张量磁盘容器。它们是 L03"张量家族"层的主体。

## 内部结构

**类型擦除底座**（tensor_void.h）：`DeviceTensorVoidView` 只有 `void* _data + std::size_t _size` 两成员（tensor_void.h:52-53），私有构造器+`class Accessor;` 前置声明（tensor_void.h:47）实现"只有内部实现能造视图"；ConstView 同理（tensor_void.h:58-73）。ABI 钉子：`static_assert(sizeof==16)` 与 `alignof==8`（tensor_void.h:55-56、74-75）；View→ConstView 有隐式转换（tensor_void.h:45）。

**文档范本**（tensor_float.h）：头注释明说视图是"light-weight non-owning... equivalent of std::string_view or std::span"（tensor_float.h:33-37）。每型四视图成对：`DeviceTensorFloatView`（tensor_float.h:40-72）/`ConstView`（75-107）/`HostTensorFloatView`（111-134）/Host Const，全锁同样的 16/8 static_assert（tensor_float.h:71-72、106-107、133-134），Host 版提供 `begin/end` 支持范围 for（tensor_float.h:137-139）。带型→void 的隐式转换运算符（tensor_float.h:56-59）是类型擦除下传通道。

**四型同构转发**：`tensor_bool.cpp` 是 bool/float/int64/uint64 四个 .cpp 的模板（NOTES batch-15"完全同构不建函数节点"）。每文件 16 个转发函数五组：Create×4（tensor_bool.cpp:31-42，设备/设备空/宿主/宿主 pinned）、GetDeviceTensorView×2（47-52）、异步 Copy×4（57-72）、同步 Copy×4（77-92）、Fill×2（97-102），全转给 `TensorUtility<bool>` 模板。

**命名张量容器**（tensor_dict.h）：`IHostTensorDict` 五方法——`ReadFromBuffer`（tensor_dict.h:40，自定义二进制格式：uint32 张量数+逐张量的名字长/名字/数据长/float 数据，注释 36-39 描述了完整格式）、`ReadFromFile`（tensor_dict.h:45，.bin/.npz 双格式，npz 走 cnpy）、`At(name)`（tensor_dict.h:50）、`Size`、`Destroy`。L29 `class IHostTensorFloat;` 是前向声明——tree-sitter 曾误当类定义提取成噪声，图谱甄别忽略（NOTES batch-14）。实现 `HostTensorDict` 用 `std::unordered_map<std::string, HostTensorFloat>` 存储（internal/tensor_dict.h:43），`At` 返回协变的具体指针（internal/tensor_dict.h:38）。

## 外部连接

依赖面极小：`audio2x/export.h`（导出宏）+ `audio2x/cuda_fwd.h`（cudaStream_t 前向声明）。被三库全量消费——执行器绑 TensorRT 输入输出（inference_engine.h 的 `SetInputBinding` 就吃 `DeviceTensorVoidConstView`）、累积器以 `HostTensorFloatConstView/DeviceTensorFloatView` 收发数据、parse_helper 的 AnimatorDataOwner 成员是 `HostTensorFloat`（internal/parse_helper.h:71-78 八个矩阵）。`FillOnDevice` 等 GPU 操作经 `internal/tensor.h` 的 TensorUtility 落到 tensor_cuda.cu 的 thrust 实现。

## 数据流

宿主文件 → `IHostTensorDict::ReadFromFile("xx.npz")` → cnpy 解压 → `At("shapesMatrixSkin")` 取 `IHostTensorFloat*` → 视图化后 `Accumulate(samples, cudaStream)` 上 GPU → 推理引擎 `SetInputBinding(index, voidView)` 类型擦除进 TRT → 输出 `GetOutputBinding` 还原带型视图。四型 Copy 家族覆盖 Device↔Device/Host↔Device/Host↔Host 全组合，异步版全带 cudaStream 尾参（tensor_bool.cpp:57-72）。

## 设计决策

- **16 字节 ABI 钉死**：两指针宽（ptr+size）+ 8 对齐的 static_assert 在每个视图类后紧跟，防止编译器/平台差异悄悄改变布局——视图按值穿过 DLL 边界，尺寸漂移即未定义行为。
- **Accessor 惯用法**：公有类只留声明 `class Accessor;`，内部实现用 `Accessor` 私友访问（tensor_float.h:62）——pimpl 的轻量变体，头文件不泄漏内部头。
- **void 底座而非模板导出**：DLL 只导出 void 版与各型薄壳，避免模板实例跨边界；类型安全由隐式转换运算符保住。
- **错误面统一**：所有操作返回 `std::error_code`；`error.cpp` 的 `Audio2XErrorCategory`（audio2x-common/source/audio2x/error.cpp:25-105）以约 80 行 switch 把 34 个枚举值翻成可读文本（"Error copying CUDA memory from device to host" 等），`make_error_code` 单点构造（error.cpp:111-113）；枚举按 20/40/60/80/100 分段留增长空隙（error.h:35-70 一带）。

## 新人提示

1. **坑：`eCudaKernelError`（error.h:49）在 error.cpp 的 switch 里没有对应 case**——全仓 50+ 处 CUDA 检查用它报错（animator_cuda.cu:130 等），但转成文本时落到 default 分支的 "Unrecognized error"（error.cpp:101-102），排查时别被通用文案迷惑，先看错误码数值。
2. 改任何视图类字段前先看 static_assert——加一个成员就会编译期爆 ABI 断言，这是故意的。
3. 四个 tensor_*.cpp 是复制粘贴同构体，改一处逻辑要四文件同步（真身在 TensorUtility 模板，转发层通常不用动）。
4. `IHostTensorDict::At` 的指针有效期内不得再 Read——unordered_map 扩容会搬迁 HostTensorFloat。
