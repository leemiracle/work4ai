# 08 · TensorImpl (c10/core/TensorImpl.h) — C++ 张量内核

> 源码: `c10/core/TensorImpl.h` (3301 行) + `TensorImpl.cpp` (1078 行) | 图节点: `file:c10/core/TensorImpl.h` | 复杂度: complex
> 一句话:你在 Python 里写的每一个 `torch.Tensor`,剥掉三层壳之后真正的身体就是这个 struct——
> 一个指向 Storage(数据)的指针 + 一包"如何把这块内存看成张量"的元数据(sizes/strides/dtype/device/dispatch key 集)。
> PyTorch 官方类注释(L439-447)自己概括得最好:*low-level representation of a tensor, which contains a
> pointer to a storage and metadata describing this particular view of the data*。

---

## 1. 架构位置:整个张量体系的物理根基

knowledge graph 里它是 `c10` 核心层的枢纽节点:contains/exports `class TensorImpl`(graph 标注 lineRange
422-3279)、`size_between_dim_`、`is_strides_like_default`、`stride` 等;imports 13 个头文件,全是张量元数据
的原语——`Storage.h`/`StorageImpl.h`(数据)、`DispatchKeySet.h`(调度)、`SymInt.h`(动态形状)、
`intrusive_ptr.h`(生命周期)、`impl/SizesAndStrides.h`(形状/步长容器)、`impl/PyObjectSlot.h`(Python 互操作)。

incoming 边只有三条却极重:`TensorBase.h` imports 它(ATen 张量层的唯一后端)、`MPSGuardImpl.h`
imports 它(设备守卫要读 device)、`TensorImpl.cpp` depends_on 它。真正的依赖扇形不在文件图里而在
类型系统里:**全 PyTorch 所有后端 CUDA/MPS/XLA/Sparse/Nested 的张量实现都是它的子类**,而 Python 层的
`torch.Tensor` 经 THPVariable → at::Tensor → at::TensorBase 三跳后落在这个 struct 上。

分层视角(本系列 01/02 篇的延续):dispatcher(02 篇)在运行时靠什么决定 `add` 走 CPU kernel 还是 CUDA
kernel?答案就烙在每个张量身上——`key_set_`。TensorImpl 是**调度信息的携带者**,dispatcher 是消费者。

```
THPVariable (Python 对象壳, python_variable.h L17-20, 成员 at::Tensor cdata)
   └─ at::Tensor      (autograd 语义层: requires_grad/grad_fn 等 API)
        └─ at::TensorBase (aten/src/ATen/core/TensorBase.h L921: intrusive_ptr<TensorImpl, UndefinedTensorImpl> impl_)
             └─ c10::TensorImpl   ← 本文件 L510, 持有:
                  ├─ Storage storage_ (L2888) ──→ intrusive_ptr<StorageImpl> (Storage.h L226)
                  │                                    ├─ DataPtr data_ptr_   (真数据指针+deleter)
                  │                                    ├─ size_bytes_ / allocator_ / resizable_
                  ├─ SizesAndStrides sizes_and_strides_ (L2923, 内联 5 维)
                  ├─ autograd_meta_ / version_counter_ / pyobj_slot_ / key_set_ ...
```

关键所有权语义:**TensorImpl 不拥有数据,只拥有"视角"**。多个 TensorImpl 可以共享同一个
StorageImpl(`x.view()`/`x[0]` 就是新建一个 TensorImpl 指过去,Storage.h L197 甚至用
`storage_impl_ == other.storage_impl_` 判等)。StorageImpl 自己也是 intrusive 引用计数
(StorageImpl.h L55 `struct StorageImpl : public c10::intrusive_ptr_target`),数据指针的
唯一所有权不变量见 StorageImpl.h L38-54 注释:两个非空 data_ptr alias 当且仅当来自同一 storage。

## 2. intrusive_ptr 引用计数:为什么不用 shared_ptr

L510:`struct C10_API TensorImpl : public c10::intrusive_ptr_target`。类注释 L457-461 给出理由:
要引用计数是为了大张量能**及时**释放;要**侵入式**(计数器长在对象里,而不是像 shared_ptr 那样另开
控制块)是为了能对裸指针做计数操作——跨语言边界(Python/C++)传张量时只需带一个指针。

机制全在 `c10/util/intrusive_ptr.h`:

- **一个 8 字节 `std::atomic<uint64_t> combined_refcount_` 装三样东西**(L189,拆分见 L60-74):
  低 32 位 strong refcount,高 32 位 weak refcount(weak 方案见 L146-170:refcount>0 时
  weakcount 恒多 1,所以 strong/weak 能合在一个 64 位字里原子地同时增减——纯性能考量),
  最高位 `kHasPyObject`(L42,`1<<63`)标记"有 Python 包装对象"(见 §6)。
- 增计数 relaxed、减计数 acq-rel(L78-103 注释:最后一个减引用必须与前面的修改同步,干脆全用
  acq-rel,现代架构上反而最快)。
- TensorImpl 重写 `release_resources()`(L582,实现于 cpp)在析构前先放掉 Storage 引用,这是
  weak tensor 机制的挂点。

对照:如果用 `shared_ptr<TensorImpl>`,每个张量要多一次堆分配(控制块)+ 两级指针跳转;而
Facebook 生产训练中存活 4 亿张量(L3081-3083 的原话:400M live tensors,每多一个 64-bit 字
= 多 3.2 GB 内存),这种级别的账只能算到每个字节。

## 3. 数据成员全景:一个 struct 就是一个张量

private/protected 区(L2887-3045)按顺序排开,配合文件尾部 L3098-3121 的官方内存布局清单:

| 成员 | 行号 | 作用 |
|---|---|---|
| `Storage storage_` | L2888 | 指向数据(间接持有,共享) |
| `unique_ptr<AutogradMetaInterface> autograd_meta_` | L2914 | autograd 挂点,惰性可空(§5) |
| `unique_ptr<ExtraMeta> extra_meta_` | L2917 | 冷字段打包:符号形状/后端 meta/FakeTensor(§7) |
| `VariableVersion version_counter_` | L2919 | in-place 修改计数,autograd 正确性基石 |
| `impl::PyObjectSlot pyobj_slot_` | L2921 | 惰性 Python 互操作指针(§6) |
| `SizesAndStrides sizes_and_strides_` | L2923 | sizes+strides 联合容器(§4) |
| `int64_t storage_offset_ / numel_` | L2925/2930 | 视角偏移(单位:元素非字节,L747)/元素数缓存 |
| `caffe2::TypeMeta data_type_` | L2934 | dtype,须与 storage 的一致(L2932 不变式) |
| `optional<Device> device_opt_` | L2948 | 仅 undefined tensor 可为 nullopt(L2946 不变式) |
| 6 个 contiguity 位域 | L2951-2979 | `is_contiguous_:1` 等,contiguous 快路径缓存(§4) |
| 约 12 个 policy 位域 | L3010-3040 | `sizes_strides_policy_:2` 等,subclass 定制开关 |
| `DispatchKeySet key_set_` | L3045 | 烙进张量里的调度身份(§8 之前先记住:8 字节位图) |

## 4. sizes_and_strides_ 与 contiguous 快路径

### 4.1 SizesAndStrides:特化版 SmallVector

`impl/SizesAndStrides.h` L10-22:定长内联阈值 5(`C10_SIZES_AND_STRIDES_MAX_INLINE_SIZE 5`),
布局为 1 个 size_t + 内联 5 个 size + 内联 5 个 stride,超过 5 维退化为指向堆数组的指针。
总大小恒 88 字节(TensorImpl.h L3267 的 static_assert 锁死)。它取代了老的
`SmallVector<int64_t,5>` 对,专门化在"sizes 与 strides 数量必须相等"这条不变式上,拷贝/判等
直接 memcmp(L53-65)——绝大多数张量 ≤5 维,零堆分配、零间接跳转。

### 4.2 contiguity:算一次,缓存成位

`is_contiguous()` 是全框架调用频度 top 级的查询,设计成**读缓存位而非计算**:
L856-862 → `is_contiguous_default_impl`(L821-839)→ 直接 `return is_contiguous_;`(L828)。
缓存位共 6 个:contiguous / channels_last / channels_last_contiguous / 3d 版两个 /
non_overlapping_and_dense(L2951-2979),全部是 1-bit 位域。

写路径负责维护缓存:任何 set_sizes/set_stride 之后调 `refresh_contiguous()` →
`_refresh_contiguous()`(L2731-2754):按 `dim()` switch——4 维只查 channels_last 2d,
5 维查 3d,其余维度只刷 contiguous 与 dense 两位;底层 O(dim) 的 `compute_contiguous()`
(L2617,实现 cpp L254-262)只在缓存失效时跑。**contiguous 快路径的本质:把 O(dim) 计算摊销成
写时一次、读时一个 bit**。`set_sizes_contiguous`(L1887-1900)是正反两向的极致:写入端直接
用"行主序步长是规范事实"跳过重扫(`empty_tensor_restride(MemoryFormat::Contiguous)` +
`assume_contiguous` 参数,L2725-2730 注释)。

### 4.3 policy 机制:sparse/nested 不走这条快路径

每个 sizes/strides 查询开头都有同一个模式,如 `sizes()`(L615-620):

```cpp
if (C10_UNLIKELY(matches_policy(SizesStridesPolicy::CustomSizes))) {
  return sizes_custom();          // 子类虚函数
}
return sizes_and_strides_.sizes_arrayref();  // 快路径:零检查直读字段
```

`SizesStridesPolicy`(L948-962)三档:Default(稠密张量)/ CustomStrides(sparse、mkldnn——strides
无意义)/ CustomSizes(nested tensor——连 sizes 都是动态的)。L597-608 的注释明确了配方:
**快路径函数只做一次 unlikely 位测试,不命中就直接读字段,绝不查 ExtraMeta**;稀疏张量付出的
一次间接调用,换来稠密张量(99% 的场景)零开销。同一套位测试开关(`device_policy_`/`layout_policy_`)
也覆盖了 `is_cuda()`(L1149)等设备查询。

## 5. autograd 挂点:autograd_meta_ 与 version_counter_

设计约束:c10 是最底层库,不能依赖 torch 的 autograd 实现。解法是三层间接:

1. **接口**:`AutogradMetaInterface`(L163-178)纯虚定义 set_requires_grad/mutable_grad/fw_grad 等;
2. **工厂**:`AutogradMetaFactory`(L188-197)+ `GetAutogradMetaFactory()`——L182-186 注释说明原因:
   AutogradMeta 的定义在 libtorch.so 而 TensorImpl 在 libc10.so,**跨 .so 无法直接构造**,只能由
   libtorch 加载时注册工厂;
3. **惰性空优化**:`autograd_meta_` 为 `nullptr` 表示"语义上等价于默认构造"(L2895-2914 长注释,
   三态:nullptr / 默认构造 / 有内容)。`requires_grad=False` 的张量——训练中大多数中间量——
   一个字节都不为 autograd 花。首次需要时才 `make()`,见 cpp L40-44 的 `mutable_grad()`。

**version counter 特意不放在 AutogradMeta 里**(L287-327 的 NOTE [Version Counter Sharing] 专门
回答了这个问题):Variable/Tensor 合并后,`requires_grad=False` 的张量没有 AutogradMeta,但只要它
被 forward 保存过(saved for backward),backward 时就必须能检测"它后来有没有被 in-place 改过"。
所以 version counter 必须永远可用 → 放 TensorImpl(L2919)。它是 `VariableVersion`(L328-418)
包着的一个 `atomic<uint32_t>`(L330-333),且是**可共享**的 intrusive_ptr:view 与 base 共享、
`detach()` 共享、`x.data` 不共享(L293-304 列全了)。in-place 算子 dispatch 时经
ADInplaceOrView kernel 调 `bump_version()`(L2157);inference tensor 干脆没有 counter
(L349 的 Disabled 廉价构造,省一次 intrusive 分配)。

**`.detach()` 怎么实现**:NOTE [TensorImpl Shallow-Copying](L2011-2048)。`shallow_copy_and_detach`
(L2109)→ `shallow_copy_and_detach_core`(cpp L562-598):新建一个 TensorImpl,把
sizes/strides/storage 指针/offset 全部按值抄过去(`copy_tensor_metadata`,cpp L686-711 →
`copy_generic_tensor_metadata` L625-664,注释列明**不抄**的四样:key_set_/storage_ 引用之外的
身份、version_counter_ 按参数、autograd_meta_ **永不拷贝**——每个 Variable 独占自己的 autograd
历史。这就是"共享数据与形状、切断计算图"的全部机制。

## 6. pyobj_slot_:C++ 对象的反向 Python 影子

`impl::PyObjectSlot`(PyObjectSlot.h L16-70)只有一个成员:`std::atomic<PyObject*> pyobj_`
(L67),acquire/release 语义存取(L20-26)。设计要点:

- **惰性**:张量在 C++ 世界诞生时没有 PyObject(纯 C++ 计算可以永远不付这笔钱),第一次进入
  Python 才填充。这就是构造函数里 [Note: Python key removal](cpp L86-101) 的存在理由:Python
  dispatch key 的不变式是"有非平凡 `__torch_dispatch__` 的 PyObject 存在",新 TensorImpl 还没有
  PyObject,所以构造时先 `key_set_ - c10::python_ks`(cpp L112/L152),等 `Tensor._make_subclass`
  填了 pyobj 再加回。
- **双向保活**:PyObject 持有对 TensorImpl 的强引用;反过来 intrusive_ptr 里 `kHasPyObject` 位
  (§2)记录"有影子",当 C++ 侧 refcount 从 1→2 时 incref PyObject、2→1 时 decref
  (intrusive_ptr.h L172-187 的 Note [PyObject preservation])——**只要有 C++ 引用在,Python 侧
  的 `t.data_ptr()` 就不会悬空**,反之亦然。`incref_pyobject()` 等虚函数由 TensorImpl 实现
  (声明 L2169),PyObjectSlot 提供 helper(PyObjectSlot.h L37-39 注释点名 TensorImpl/StorageImpl/
  autograd Node 三类用户)。多解释器(subinterpreter)场景则经 PyInterpreter 虚表间接。

## 7. ExtraMeta:冷字段的统一垃圾场

L245-285 的 `ExtraMeta` 把使用率极低的字段打包成单个 unique_ptr(L2917,默认 nullptr):
`SymbolicShapeMeta`(动态形状,配合 SymInt——`has_symbolic_sizes_strides_` 位域 L3014 触发后,
sizes/strides 查询全部改道 `symbolic_shape_meta()`,如 L638-645)、`BackendMeta`(L221-227,
后端自定义元数据的虚基类,如 CUDA rnn state)、`fake_device_`/`fake_tensor_mode_`(FakeTensor
机制,见本系列 05 篇;cpp L194-216 `set_fake_device` 会同时改 key_set_ 加 DispatchKey::Fake)、
以及 sparse subclass 的报错文案槽位(L1768-1769)。**热路径永远不碰它**(L597-608 注释:
非平凡 ExtraMeta 必然伴随 policy 触发,所以快路径无需检查)——这是把"每张量固定成本"压到
最小的典型手法。

## 8. key_set_:张量为什么知道自己该走哪条调度路

L3045-3046:`DispatchKeySet key_set_;`(8 字节位图,见 02 篇 Dispatcher)。注释点出历史:
**现在不含 Autograd key 了**(曾经含)。

它由构造函数烹饪(cpp L125-173):取调用方传入的裸 backend key 集 → 补 autocast 相关键
(L149)→ 剥 python_ks(L152)→ 若在 InferenceMode 里,把 Autograd/ADInplaceOrView 键全部
剥掉(L155-159);否则补上 Autograd相关键(L164,TODO 注释坦言:理想情况只有 requires_grad
才补,但 key_set 在构造期就得定死,而那时还不知道)。换设备时 `_change_backend_component_keys`
(cpp L175-192)原位换 backend 位。

它带来两类零虚函数快查:
- `is_sparse()`(L1101)/`is_quantized()`(L1117)/`is_fake()`(L1133):直接 `key_set_.has_all(...)`,
  注释特意标明"non-virtual for performance";
- dispatcher 的核心流程:`operator()` 收集参数张量的 key_set 做交集/并集,直接定位 kernel 表
  槽位(02 篇 §dispatch),**全程不查字符串不查 type_info,只做位运算**。

而设备类查询(`is_cpu()` L1137、`is_cuda()` L1149)反而**不**信 dispatch key 而信
`device_opt_`——L1143-1145 注释解释:FunctionalTensorWrapper 这类 wrapper 张量的 key_set 不含
backend 位。这个不对称是读这份文件最容易踩的坑。

TensorBase/Tensor 之上还提供 `has_compatible_shallow_copy_type`(L2062-2094):两个 key_set
相同的稠密/稀疏后端之间允许 O(1) 元数据浅拷贝,这是 `Tensor.to()` 类转换能走快路径的前提。

## 9. 三层壳的分工:TensorBase / Tensor / THPVariable

- **`at::TensorBase`**(TensorBase.h L921 `intrusive_ptr<TensorImpl, UndefinedTensorImpl> impl_`):
  最薄的一层,只做指针管理 + 转发元数据查询(`sizes()`/`dtype()`/`key_set()`...)。第二个模板参数
  `UndefinedTensorImpl` 把"未定义张量"做成单例空指针策略——默认构造的 TensorBase 不分配任何东西。
  内部代码(尤其实现层)尽量用 TensorBase 传参,省一次指针计数;
- **`at::Tensor`**:继承 TensorBase,加 autograd 语义与全部用户 API;
- **`THPVariable`**(python_variable.h L17-20):CPython 对象壳,成员就一个 `at::Tensor cdata`,
  与 TensorImpl::pyobj_slot_ 互为反向指针(§6)。

于是"张量"在三个世界里各有一个轻代表,而**真相只在 TensorImpl 一处**——`x.transpose(0,1)`
在 Python 层只是让 cdata 换了个指向新 TensorImpl(共享同一 StorageImpl、不同 strides)的指针。

## 10. 208 字节的预算:Note [TensorImpl size constraints]

L3075-3122 是全文件最有"生产感"的注释:4 亿活张量的训练任务里,每个 64-bit 字 = 3.2 GB;
历史上在 160 字节/张量时直接 OOM 过(L3089)。因此文件尾部放了整段编译期哨兵
`C10_TensorImpl_Size_Check_Dummy_Class`(L3168-3289):用 static_assert 逐字段锁死大小
(storage_ 8B、pyobj_slot_ 8B、sizes_and_strides_ 88B、key_set_ 8B...),总量
`26 * sizeof(int64_t)` = 208 字节(64 位,L3256),任何人加字段导致膨胀会**直接编译失败**,
且报错信息里带着字段名枚举(L3180-3193)。SmallVector 内联、位域、ExtraMeta 冷拆、惰性
autograd_meta——§4/§5/§7 的每个设计最终都在给这张 208 字节的账单还债。

## 11. 心智模型小结

- TensorImpl = **Storage 的指针 + 一个"视角"描述(sizes/strides/offset)+ 烙在身上的调度身份
  (key_set_)+ 三个可空挂点(autograd_meta_ / extra_meta_ / pyobj_slot_)**;
- 生命周期:intrusive 8 字节合并计数,Python 影子经 kHasPyObject 位双向保活;
- 性能哲学:热查询(sizes/is_contiguous/is_cuda/key_set)全部走**位测试 + 缓存位直读**,
  慢路径(sparse/nested/symbolic)用 policy 位域买断离权;
- autograd 不在 c10 里,但 autograd 的**骨架**(version counter、可浅拷贝性)必须长在
  TensorImpl 里,这是当年 Variable/Tensor 合并(本系列 03 篇)留下的形状。

下一步阅读路线:`impl/SizesAndStrides.h`(331 行,容器细节)→ `StorageImpl.h`(数据与
DataPtr/deleter)→ `aten/src/ATen/core/TensorBase.h`(壳层如何转发)→ 回到 02 篇 Dispatcher
看 key_set_ 被消费的地方。
