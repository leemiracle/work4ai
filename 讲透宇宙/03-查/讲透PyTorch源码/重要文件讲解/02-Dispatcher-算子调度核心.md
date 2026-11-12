# Dispatcher.h — 算子调度核心：一次 `torch.add` 背后的路由器

> 源文件：`aten/src/ATen/core/dispatch/Dispatcher.h`（958 行）
> 知识图谱节点：`file:aten/src/ATen/core/dispatch/Dispatcher.h`，complexity=complex，tags=[dispatcher, core, singleton, header]
> 图谱 commit：f634d0e91da4cc1d4d669a60ede149214b754854（2026-09-03 分析）

---

## 一、它在架构中的位置：开集调度的心脏

知识图谱把它归入 `layer:tensor-core-dispatch`（张量核心与 C++ 调度），并且是 Tour #5
「Dispatcher：算子调度核心」的头号节点，同站台的邻居正是它的三大协作者：

- `OperatorEntry.h` —— 每个算子一条的登记项（schema + per-key kernel 表）；
- `DispatchKeyExtractor.h` —— 从参数 Tensor 推导分发键的提取器；
- `c10/core/DispatchKeySet.h` —— 64 位位集，调度路由的核心数据结构（用
  `std::bit_width` 做 O(1) 最高优先级键提取）。

图谱记录的出边：`contains`/`exports` 各 5 条（`Dispatcher` 类 L71-958、`callBoxed` L861-903、
`callBoxedForDispatchKey` L906-927、`redispatchBoxed` L929-945、`DispatchTraceNestingGuard`
L32-39），`imports` 1 条（`c10/util/Exception.h`，import map 单向恢复所致，真实 include 列表
见 L3-19）。无入边只是恢复算法的盲区——事实上所有生成的算子桩代码都指向这里。

一句话定位：**它是「按 key 查表」的开集调度（open-set dispatch）中枢**。与 OOP 虚函数
"一个类一张 vtable、改功能要改类" 不同，PyTorch 把"算子 × 后端/功能"做成二维注册表：
新增一个设备后端（XPU/MPS/PrivateUse1...）不需要碰 `Tensor` 类一行代码，只要注册新的
`DispatchKey` 与对应 kernel。多后端、autograd、子类（functorch/FirstTier）、autocast 的
叠加全部由这张表统一表达。`Dispatcher` 就是这张表的持有者与查询入口。

---

## 二、文件骨架：958 行的四个区块

1. **L25-64** 辅助件：dispatch trace 的嵌套计数函数 + `DispatchTraceNestingGuard`（RAII，
   构造/析构增减计数，抑制递归 dispatch 的嵌套 trace 输出）；`OpRegistrationListener`
   接口（注册/反注册事件回调，L53-59，注释明确：只有 `def` 触发事件，`impl`/`fallback` 不触发）。
2. **L71-438** `Dispatcher` 类本体：嵌套 `OperatorDef`（L76-93）、单例访问（L110-132）、
   查询 API（findSchema 族 L145-170）、调用 API（call/redispatch/boxed 族 L178-232）、
   注册 API（L246-306）、监听器（L320-321）、诊断（L346-355）、私有数据成员（L402-437）。
3. **L440-641** 句柄层：`OperatorHandle`（类型擦除的算子句柄）与
   `TypedOperatorHandle<FuncType>`（带 C++ 签名的强类型句柄，L613-641 特化实现）。
4. **L643-945** 实现区：`CaptureKernelCall`（profiling 捕获返回值，L654-707）与四个
   内联调用入口 `call`/`redispatch`/`callBoxed`/`callBoxedForDispatchKey`/`redispatchBoxed`
   ——热路径全部 inline 在头文件里。

头文件即实现，是性能代码的典型选择：`call` 标了 `C10_ALWAYS_INLINE_UNLESS_MOBILE`（L784）。

---

## 三、数据模型：从 OperatorName 到 kernel 表

`Dispatcher` 私有区（L402-437）五个成员构成全部状态：

- `std::list<OperatorDef> operators_`（L402）——所有算子的**权威存储**。用 `std::list` 而
  非 `vector` 是刻意的：list 节点地址稳定，注册/反注册不失效指针，于是 call 热路径**完全无锁**
  （L863-864、L910-911 的注释都强调这一点）。
- `LeftRight<flat_hash_map<OperatorName, OperatorHandle>> operatorLookupTable_`（L404）——
  名字 → 句柄的读多写少并发索引（LeftRight 是读者永远无锁的 RCU 风格结构；移动端退化为
  `RWSafeLeftRightWrapper`，L407）。
- `std::array<impl::AnnotatedKernel, num_runtime_entries> backendFallbackKernels_`（L414-415）
  ——**每个后端一份**的全局 fallback kernel（如 PrivateUse1 后端没给某算子写实现时兜底，
  通常打印 "not implemented" 报错）。这就是 `registerFallback`（L296-299）的落点，也是
  `friend class impl::OperatorEntry`（L74）的原因：OperatorEntry 建表时要反向读它。
- `libraries_` / `listeners_`（L412、L417）——命名空间登记与监听器链。
- `cond_var_` + `guard_`（L431、L437）——multipy/torchdeploy 多解释器竞态时等待注册的
  条件变量（`waitForDef`/`waitForImpl`，L229-232）；`guard_` 用 `shared_ptr` 包着
  `{atomic<bool> alive; mutex}`（L98-102），防止 Dispatcher 析构后回调悬空。

每个 `OperatorDef`（L76-93）= `impl::OperatorEntry op` + 两个引用计数
`def_count` / `def_and_impl_count`（L91-92）。计数注释（L81-90）解释了一个精细的析构时序：
最后一个 `def()` 注销时必须立刻通知 Deregistered 监听器，但**不能真删** OperatorDef——
还有未到期的 `impl` RAII 句柄要析构，它们手里的 handle 必须仍然可用。

---

## 四、单例的正确姿势（L110-132）

```cpp
static Dispatcher& realSingleton();               // out-of-line, 定义在 Dispatcher.cpp
C10_ALWAYS_INLINE static Dispatcher& singleton() {
#if !defined C10_MOBILE
  static Dispatcher& s = realSingleton();  // 函数局部引用缓存
  return s;
#else
  return realSingleton();                  // 移动端不内联
#endif
}
```

这里的注释（L114-131）是一堂 C++ 工程课：如果把 `realSingleton` 直接 inline，每个包含此
头的 DSO 都会复制一份函数局部 static，进程里出现**多个单例**；所以真单例藏在 .cpp 里，
头文件里再内联一层"引用缓存"让稳态调用零函数开销。移动端反过来**禁止**内联——内联版本
会为每个算子桩生成 `__cxa_guard_acquire/release`（static 局部变量的一次性初始化保护），
几千个算子 × 每个后端的桩代码会把体积撑爆。同一份代码，两个平台两种取舍。

---

## 五、注册面：def / impl / fallback 与 RAII 生命周期

`TORCH_LIBRARY` / `TORCH_LIBRARY_IMPL` 宏最终都落到这四个入口（注释 L236：非用户 API，
用户应走 op_registration 层）：

- **`registerDef`（L246-249）**：注册 schema（`FunctionSchema`）。同名 schema 已存在时
  会比对一致性（`checkSchemaCompatibility`，L397）。触发 listener 事件的只有这条路径。
- **`registerImpl`（L260-266）**：把 `KernelFunction` 挂到指定 `DispatchKey` 的表项；
  `dispatch_key == nullopt` 时注册的是 catch-all fallback。参数里还带
  `cpp_signature`（签名校验用）和 `inferred_function_schema`（"偷"来的推断 schema，
  先拿着等真 schema 出现，L258-259 注释）。
- **`registerFallback`（L296-299）**：写全局 `backendFallbackKernels_[idx]`。
- **`registerName`/`registerLibrary`（L288、L306）**：仅登记名字/命名空间。

所有注册都返回 **`RegistrationHandleRAII`**——RAII 反注册：句柄析构即调
`deregisterDef_`/`deregisterImpl_`/...（L387-396）。这决定了 PyTorch 的动态注册玩法：
`torch.library` 在 Python 里注册自定义 op，Python 对象被 GC 时 kernel 自动从表里摘除，
不留悬空。诊断函数 `findDanglingImpls`（L346）专门抓"有 impl 没 def"的静态初始化顺序
bug——静态初始化期 `.def()`/`.impl()` 顺序无保证，只能事后检查。

---

## 六、调用面：调度算法四步走

### 6.1 `call` 主线（L783-839）——unboxed 热路径

```cpp
C10_ALWAYS_INLINE_UNLESS_MOBILE Return Dispatcher::call(
    const TypedOperatorHandle<Return(Args...)>& op, Args... args) const {
  auto dispatchKeySet = op.operatorDef_->op.dispatchKeyExtractor()
          .template getDispatchKeySetUnboxed<Args...>(args...);   // (1) 算 key set
  ...
  const KernelFunction& kernel = op.operatorDef_->op.lookup(dispatchKeySet);  // (2) 查表
  ...  // (3) 可选 profiling 分支
  return kernel.template call<Return, Args...>(op, dispatchKeySet, ...);      // (4) 调用
}
```

四步：**算 key → 查表 → (可选插桩) → 调 kernel**。没有虚调用、没有字符串比较、没有锁。

### 6.2 第一步的公式：DispatchKeySet 计算（TLS 的主场）

`getDispatchKeySetUnboxed`（DispatchKeyExtractor.h L194）先用 `MultiDispatchKeySet`
（L54-102）对参数包做变参折叠：遍历每个参数，Tensor 取 `x.key_set()`、`optional<Tensor>`
判空、TensorList 逐个 OR（L56-82），全部 OR 出"参数携带的原始 key 集"。注意
`Tensor::key_set()` 读的是 `TensorImpl::key_set_`——`Tensor` 本身就是
`intrusive_ptr<TensorImpl>` 的薄壳，**key 集随张量出生地（设备/dtype/子类）固化为
TensorImpl 的一个 64 位字段**，读取零开销。

原始 key 集再经自由函数 `computeDispatchKeySet`（DispatchKeyExtractor.h L24-47）加工：

```cpp
return (((ks | local.included_) - local.excluded_) & key_mask);
```

- `local = c10::impl::tls_local_dispatch_key_set()`（L39-40）——**thread_local 的
  包含/排除集**。这是 dispatcher 的"环境开关"层：`GradMode` 关掉时把 Autograd 系 key
  放进 `excluded_`（推理跳过 autograd）；`torch.functionize`/vmap 等模式往 `included_`
  里塞功能层。每线程独立，所以不同线程可以一个训练一个推理。
- `key_mask` 是**算子级**掩码：fallthrough 的 key 与 redispatch 要排除的 key 在这里清零。
  L26-37 注释解释了为什么 mask 不能并入 TLS——排除可能发生在 TLS include 之后，必须最后施加。
- 减号是集合差。最终集合里位序最高的 key 即 `highestPriorityTypeId()`（功能位段优先于
  后端位段，Autograd > backend 是靠位布局保证的）。

### 6.3 第二步：`lookup` 与建表优先级

`OperatorEntry::lookup`（OperatorEntry.h L182-200）本身极薄：
`getDispatchTableIndexForDispatchKeySet()` O(1) 算出表下标 → `dispatchTable_[idx]`
→ 校验 unboxed 有效性（L194，注释说明先查 unboxed 再查 boxed 是分支预测优化）→ 返回。
查不到就 `reportError`（L185/196）。

真正的"调度算法"发生在**建表时**而非查询时：`computeDispatchTableEntryWithDebug`
（OperatorEntry.cpp L352-471）给每个 runtime key 预计算表项，优先级为：

1. 直接注册到该 key 的 kernel（L356-390，"kernel"）；
2. 别名/composite 键展开（L358-374）：`CompositeExplicitAutogradNonFunctional` >
   `CompositeExplicitAutograd` > `CompositeImplicitAutograd`（写一个数学公式 kernel
   服务所有后端的机制，AutogradOther 有歧义保护）> `Autograd` > `FuncTorchBatchedDecomposition`；
3. **backend fallback**（L460-467）：查 `Dispatcher::backendFallbackKernels_`；
4. 都没有 → `missingKernel()`（L469-470，调用时报 "not implemented"）。

**fallthrough** 是其中的特殊哨兵：当表项被解析成 fallthrough kernel 时，`computeDispatchKeySet`
的 `key_mask` 直接把这个 key 清零（DispatchKeyExtractor.h L29-30），dispatch 继续**滑向
次优先级 key**——这就是 functorch 层叠包装不干预某些算子的实现方式。是否 fallthrough 由
`setOperatorHasFallthroughForKey`（DispatchKeyExtractor.h L203）维护成
`nonFallthroughKeys_`/per-backend 两张位图（L269-274）。

### 6.4 `redispatch`（L842-859）：kernel 内部的"再调度"

```cpp
inline Return Dispatcher::redispatch(op, DispatchKeySet currentDispatchKeySet, Args... args) const {
  const KernelFunction& kernel = op.operatorDef_->op.lookup(currentDispatchKeySet);
  return kernel.template call<Return, Args...>(op, currentDispatchKeySet, ...);
}
```

与 `call` 的差别：**不重算 key、不做 RecordFunction 插桩**（L847 注释），把调用方传入的
key set 原样用掉（L190-196 的注释链 `Note [Plumbing Keys Through The Dispatcher]`）。
经典用法是 autograd kernel 的标准结尾：Autograd kernel 先建 graph，然后
`redispatch(op, ks - AutogradKey, args...)` 落到真正的后端 kernel。Include/Exclude 语义
（`c10::impl::tls_set_dispatch_key_excluded`）则供 Python dispatcher 等场景屏蔽某层。
参数转发语义见 `[Note: Argument forwarding in the dispatcher]`——`Args` 不用 `&&`，
按值传 + `std::forward`，避免完美转发在重入时把 lvalue 移走。

### 6.5 boxed 家族（L861-945）：IValue 栈式调用

- `callBoxed`（L861-903）：参数打包在 `Stack`（`vector<IValue>`）里，用
  `getDispatchBoxedSet(stack)` 从栈上提取 key。Python→C++ 边界、torchscript、RPC 走这条路。
  L738-746 有个精彩细节：需要把参数盒装给 profiler 时，用 `alignas(IValue) std::byte[]`
  手工 placement——跳过 `std::array` 的默认构造开销。
- `callBoxedForDispatchKey`（L906-927）：**跳过 key 计算**直接指名 DispatchKey 调用，
  kernel 缺失时回落 `backendFallbackKernels_`（L917-925 的立即调用表达式）。Python 的
  `torch._C._dispatch` 测试工具用它做精准探针。
- `redispatchBoxed`（L929-945）：同 `redispatch` 的 boxed 版。

### 6.6 profiling 慢路径隔离（L718-810）

`call` 里 `C10_UNLIKELY(step_callbacks.has_value() && op.isObserved())`（L801-802）把
profiler 拦截隔离进 `callWithDispatchKeySlowPath`（L718-780）：`RecordFunction` guard、
盒装参数喂回调、`CaptureKernelCall`（L654-707，含 `void` 与 `at::Tensor&` 的特化处理
返回值）捕获输出。`ObservedOperators.h` 维护"无需观测"名单避免全量插桩。慢路径与
`C10_UNLIKELY` 分支提示保证没开 profiler 时零损耗。

---

## 七、`torch.add` 全链路走读

```
torch.add(a, b)                          # Python
  └─ torch/csrc 的生成绑定 THPVariable_add → at::add(...)        # pybind 拆包
      └─ at::_ops::add_Tensor::call(...)   # torchgen 生成桩
```

生成桩的模板在 `torchgen/gen.py` L652-670：每个算子生成一个 `struct add_Tensor`，其
`create_add_Tensor_typed_handle()`（L666-670）就是
`c10::Dispatcher::singleton().findSchemaOrThrow("aten::add", "").typed<schema>()`
——`findSchemaOrThrow`（Dispatcher.h L160）查 `operatorLookupTable_` 拿
`OperatorHandle`，`typed<>()`（L530-546）顺带做 C++ 签名校验
（`assertSignatureIsCorrect`，防止你用错误签名 smuggle kernel；SymInt 还有二次校验 L540-543）。

随后 `TypedOperatorHandle::call`（L623-626）内联进 `Dispatcher::call`（L784）：

1. **算 key**：两个 CUDA 张量 → ks = `{CUDA, AutogradCUDA}`（功能位优先）；若当前线程
   `GradMode(false)`，TLS `excluded_` 抹掉 AutogradCUDA；
2. **查表**：`lookup(ks)` → dispatchTable_ 里 AutogradCUDA 槽位的预计算 kernel；
3. **调用**：autograd 包装 kernel（建 autograd graph 节点）内部
   `redispatch(op, ks - AutogradCUDA, ...)` → CUDA kernel 执行；
4. 返回 `Tensor`（`intrusive_ptr<TensorImpl>`）给 Python。

推理模式/训练模式、CPU/GPU、普通 Tensor/子类——**全在同一条四步流水线上，只是 key 集
不同**。这就是"表驱动开集调度"的全部含义。

---

## 八、C++ 惯用语清单

1. **单例（L110-132）**：函数局部 static 引用缓存 + out-of-line 真单例，防 DSO 复制；
   移动端反向选择不内联省体积。两个平台同一段代码各取所需。
2. **RAII 统治生命周期**：`RegistrationHandleRAII`（注册↔反注册）、
   `DispatchTraceNestingGuard`（L32-39，trace 嵌套计数）、`RecordFunction` guard、
   `Guard{atomic alive + mutex}`（L98-102，析构竞态防御）。
3. **`OperatorHandle` 的双指针微优化（L578-598）**：同时存 `OperatorDef*` 裸指针和
   `std::list` 迭代器。注释算过账：libstdc++ 的 list 节点里 prev/next 指针在前、元素
   偏移 16 字节，iterator→element 要一条 add 指令；热路径直接用裸指针省掉这条指令，
   迭代器留给 `cleanup()`（L396，程序退出时高频）用。**这是对 intrusive_ptr 的刻意
   反其道而行**：Tensor 用 `intrusive_ptr<TensorImpl>` 是因为张量生命周期开放共享；
   而 OperatorDef 的生命周期由 `std::list` 锚定、节点地址永不移动，句柄只需"借"不需要
   "拥有"——引用计数反而是纯开销。两套方案在同一个 dispatch 流程里各司其职。
4. **`std::list` + LeftRight 的读写并发设计（L402-409）**：权威数据放 list（地址稳定），
   索引放 LeftRight（读者无锁），call 路径零锁零原子指令。
5. **TLS 状态（经 DispatchKeyExtractor.h L39-46）**：`(ks | included) - excluded & mask`
   一个公式同时承载 GradMode、vmap/functionize 分层与 redispatch 排除——"环境"不进
   参数、不进全局变量，进线程局部。
6. **模板元编程**：`MultiDispatchKeySet` 继承 `IterArgs` 折叠参数包（L54-102）；
   `TypedOperatorHandle` 对非法 FuncType 走 `guts::false_t` static_assert（L609-611）；
   `CaptureKernelCall` 对 `void`/左值引用偏特化（L685-707）。
7. **冷热分离**：`C10_ALWAYS_INLINE` 热路径 vs `C10_NOINLINE`（生成桩的
   `create_typed_handle`）慢初始化；`C10_UNLIKELY` 引导分支预测；
   `aligned_storage` 手工盒装避免默认构造。
8. **`std::hash<OperatorHandle>` 特化（L949-957）**：直接 hash 内部指针，让句柄可做
   unordered_map 的 key——工具链（如 op 重载收集器）的日常需求。

---

## 九、调试抓手与阅读顺序

- **看路由**：编译带 `HAS_TORCH_SHOW_DISPATCH_TRACE`（L790）或 debug build 下开
  `show_dispatch_trace()`，`_print_dispatch_trace`（L709-712）会打印每次 call/redispatch
  的 `[call] aten::add {key set}`；`DispatchTraceNestingGuard` 保证嵌套调用缩进正确。
- **看表**：`OperatorHandle::dumpComputedTable()`（L501）导出某算子整张 dispatch 表，
  配合 `getRegistrationsForDispatchKey`（L354）查"谁注册了什么"。
- **查注册完整性**：`checkInvariants`（L323）、`findDanglingImpls`（L346）。
- **推荐阅读序**：`DispatchKeySet.h`（位布局与优先级从何而来）→ 本文
  `Dispatcher.h` L783-839（四步主线）→ `DispatchKeyExtractor.h`（TLS 公式与
  fallthrough 位图）→ `OperatorEntry.cpp` L352-471（建表优先级，调度"算法"本体）→
  回头看 `RegistrationHandleRAII.h` 收尾。

**核心 takeaway**：Dispatcher 把"选哪份实现"从编译期虚表挪到运行期位集查表，用
建表时预计算 + 查表时 O(1) 索引 + TLS 环境叠加，换来"任意后端 × 任意功能层自由组合
且互不需要认识对方"的扩展性——这是 PyTorch 能同时长出 CUDA/MPS/XLA、autograd、
functorch、torch.compile 的地基。
