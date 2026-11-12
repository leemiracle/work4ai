# MatX 张量核心体系（core/）

## 一、角色定位

core/ 是 MatX 全库地基。MatX 定位"现代 C++ 的 NumPy 替代"——header-only、纯模板、值语义张量+惰性求值，支点全在 core/：**张量本体**（tensor.h / tensor_impl.h / tensor_desc.h）、**存储内存**（storage.h / allocator.h / cache.h）、**创建与互操作门面**（make_tensor.h / dynamic_tensor.h / sparse_tensor.h / tie.h / dlpack.h）。伞头有硬纪律：`defines.h should always be included first`（include/matx.h:41-43）——它决定索引宽度与 DefaultDescriptor 类型（tensor_desc.h:503-508），顺序错则 ABI 漂移。分层角色：上层算"算什么/在哪算"，core 管"数据住哪、什么形状、谁释放"——张量既是数据宿主，也是惰性表达式的 LHS。

## 二、内部结构

### 2.1 三层：tensor_t → tensor_impl_t → tensor_desc_t

**`tensor_impl_t`**（include/matx/core/tensor_impl.h:91）是"裸张量"：只持 `T* ldata_` 与描述符，提供主机/设备双端 getter/setter（tensor_impl.h:1168）。头注释明言不含所有权——视图才能以 POD 代价传进 kernel。甄别点：常见文档写三模板参数，源码实为四个（tensor_impl.h:90）——第四参数 TensorData 是稠密/稀疏策略（DenseTensorData 仅 `T* ldata_`，:49；SparseTensorData 含三组指针，:58）。

**`tensor_t`**（tensor.h:76）在 impl 上加且仅加一件事：`Storage<T> storage_` 的所有权与引用计数。拷贝构造共享 `storage_`（tensor.h:108）——值语义：拷贝张量=拷贝句柄不拷数据，末个视图析构才释放。视图族全走"共享 storage、只换描述符"：`View()`/`Slice()`/`Permute()`（tensor.h:643/:1427/:923）落到统一构造（:194）。Permute 实现在 `PermuteImpl`（tensor_impl.h:884），只重算 shape/stride、指针不动。

**`tensor_desc_t`**（tensor_desc.h:55）把形状/步长剥离成独立类型维度，32/64 位宽度参与类型编码。姊妹类型 `static_tensor_desc_t<I, Is...>`（:365）把形状编码进模板参数，`Size()/TotalSize()` 全 `static constexpr`（:429），运行期版（:243）——前者编译期折叠 kernel 寻址，后者保留重塑。

### 2.2 存储与内存

`Storage<T>`（storage.h:80）是 owning/non-owning 统一句柄，内部 `std::shared_ptr<T>`（非拥有指针走空删除器，:90）。注释自白"duck-typed custom allocators while avoiding virtual functions"（storage.h:71-73）——虚表污染 POD 布局，自定义分配器走编译期 duck typing。

底层 `matxAlloc/matxFree`（allocator.h:410、420）按 `matxMemorySpace_t` 分派：MATX_HOST_MEMORY=cudaHostAlloc 页锁定（:60）、MATX_ASYNC_DEVICE_MEMORY=cudaMallocAsync 绑流（:63）。`MemTracker`（:89）登记每笔分配的 `matxPointerAttr_t`（:78）：`GetPointerKind()`（:379）供 DLPack 反查；析构路径（:143-158）保证 cudaFreeAsync 用登记的流。

`cache.h` 服务 transforms：`matxCache_t`（cache.h:167）以 CacheId 缓存 plan/句柄，`LookupAndExec`（:222）"查不到现做"（单例 :742）。

### 2.3 创建路径与变体张量

`make_tensor.h` 四类重载：形状+空间+流（make_tensor.h:59）、已有 Storage（:87）、裸指针（:320）、编译期形状 `make_tensor<T,10,20>()`（:859）。三个变体各有动机：**`dynamic_tensor_t`**（dynamic_tensor.h:133）把 rank 从类型擦除（注释 :123 明言）——运行期才知维度的脚本场景须 vtable 分派；**`sparse_tensor_t`**（sparse_tensor.h:81）基于 TACO 式层级格式（LVL 级 crd/pos 数组），应走 COO/CSR 工厂（:106）；**mtie**（tie.h:44）是多输出绑定，因无法重载 `cuda::std::tuple` 的 operator= 而独立成类型（tie.h:42）。

## 三、外部连接

**张量是 BaseOp 体系的赋值目标。** tensor_t 用类型 trait 自我标注：`matxop = bool` 标记"我是 MatX 算子"（tensor.h:82），`matxoplvalue = bool` 标记"可作方程左值"（:83）。operator= 被重载为返回 `detail::set(*this, op)`（tensor.h:262）；`set` 类（operators/set.h:121）继承 BaseOp，构造时静态断言 `is_matx_op_lvalue<T>() == true`（set.h:189）。`B = A*C; B.run(stream)` 即：operator= 造 set 算子树 → run() 触发 executor → 对每输出元素回调设备端 `operator()`（tensor_impl.h:1168）写数据。

**mtie 多返回值协议**：operator= 带 `requires is_matx_transform_op_c<RHS>`（tie.h:74）只收 transform 算子；`Exec` 取 tuple 末元素为 RHS、余为输出（tie.h:104-111）。

**Python/NumPy 三条桥**：①DLPack——`ToDlPackImpl`（tensor.h:1503）先经 GetPointerKind 反查空间，视图指针不在登记表则退到 Driver API `cuPointerGetAttributes`（tensor.h:1526-1536）；dtype 经 `TypeToDLPackType`（tensor_utils.h:190）；生命周期靠 manager_ctx+deleter 接力（tensor.h:1600-1606）。②pybind——MatXPybind 包在 `#ifdef MATX_ENABLE_PYBIND11`（pybind.h:37）内，默认编译关闭。③dynamic_tensor_t 承担 rank 运行期化。数值底座：`matxHalf<T>`（half.h:130）修复半精度对齐。

## 四、数据流

1. **创建**：`make_tensor<float>({M,N}, MATX_DEVICE_MEMORY, stream)` → make_owning_storage（storage.h:194）→ matxAlloc（allocator.h:410）→ cudaMallocAsync+登记。
2. **视图零拷贝**：`A.Slice(...).Permute({1,0})` → 描述符逐级重算（tensor_impl.h:884），引用计数+1，指针不动。
3. **惰性赋值**：`B = A*2` 立即返回不碰数据——只造 set 算子树（tensor.h:262）。
4. **执行**：`.run(stream)` → executor 把 impl 视图按值传入 kernel，`operator()`（tensor_impl.h:1168）折叠下标为偏移（tensor_impl.h:982），再按 CapType 单元素或 `Vector<T,EPT>` 向量化读写（:1185/:1188）。
5. **互操作**：ToDlPackImpl（tensor.h:1503）零拷贝交指针。
6. **析构**：末个视图 storage_ 归零 → matxFree（allocator.h:420）→ ASYNC 内存按登记流 cudaFreeAsync（:155-158）保序。

## 五、设计决策

**① 值语义+引用计数。** "拷贝视图句柄、共享数据"（tensor.h:108）规避"张量析构时 kernel 还在用"：视图按值进 kernel 不延长生命周期，释放走流保序（allocator.h:143-158）。代价：改任一视图全部可见。

**② 描述符独立成模板维度。** 静态/动态描述符实现同一契约，静态版寻址编译期折叠（tensor_desc.h:365/429），动态版保留 flex（:55）——代价是类型爆炸：T×RANK×Desc×TensorData 笛卡尔积。

**③ 所有权下沉、算力上浮，全链无虚表。** tensor_impl_t 无所有权（POD 进 kernel），tensor_t 只有所有权，描述符只管几何——层间用 trait 而非虚函数对话（storage.h:71-73）。

**④ 稀疏作为 TensorData 策略内联。** SparseTensorData 进同一 tensor_impl_t，`operator()` 内 `if constexpr` 分支稠密/稀疏（tensor_impl.h:1176）——基础设施全套复用；experimental（matx.h:55）。

**⑤ 互操作选 DLPack 而非自造 ABI。** dlpack.h 内嵌完整 DLPack 头，v0.8 与 legacy 双轨（dlpack.h:341）；指针空间探测宁可调 Driver API（tensor.h:1529）也不猜。

## 六、新人提示

1. **永远从 make_tensor 进门**（make_tensor.h:59/87/320/859），别手写 tensor_t 构造。
2. **operator= 不执行计算**。`B = A + 1` 忘 `.run(stream)` 不报错、什么都不发生（tensor.h:253 注释明言 deferred）。
3. **include 红线**：绕过 matx.h 引 core 头须先 include defines.h（matx.h:41-43），否则宏中途改类型 → ODR 违规。
4. **拷贝是视图语义**：`auto B = A; B(0,0)=1;` 后 A(0,0) 也是 1。
5. **内存空间匹配消费者**：pinned 张量提速拷贝但 kernel 直读慢；matxPointerAttr_t 登记表（allocator.h:78-90）是跨界导出唯一事实来源。
6. **读源码顺序**：tensor_desc.h → tensor_impl.h:91 → tensor.h:76。
7. **甄别提示**：旧文档常把 tensor_impl_t 写成三参数、把 tie.h 写成有 tie_t 类——源码实为四参数（tensor_impl.h:90），只有 mtie（tie.h:44）。