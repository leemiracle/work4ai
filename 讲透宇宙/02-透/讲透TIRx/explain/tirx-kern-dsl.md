# tirx-kern-dsl.md — kern/__init__.py：TIRx 的 PTX 级 Kernel DSL 总纲

> 源码：`tirx_kernels/kern/__init__.py`（576 行）｜图谱层：`layer:kern-dsl`｜fan-in **105，全库最高**

## 角色定位

在 14 层知识图谱架构中，本文件单独撑起 **Kern DSL 内核语言层**——全部 GPU kernel 的编写基座。库内 105 个文件（deepgemm/cudnn/flashinfer/deepep/msa/flashattention/agent_evolved 六大类别全覆盖）以 `import tirx_kernels.kern as K` 开头，一个文件的 import 面就是整个库的生产面。

它存在的理由写在模块 docstring 里：基础语言是 tirx script 加上 in-tree 的 `T.ptx` 指令表，"一次调用就是一条指令，按 ISA 的拼写"。但 TVMScript 的世界是 **parser** 的世界，而 Kern 把它改造成 **tracer** 的世界——`@K.kernel` 的函数体用 IRBuilder 追踪执行而非解析源码。这个范式转换丢掉了一批语句语义，K 的使命就是把它们补回来，并在三处"PTX 和 lang 都没有词"的地方新增原语族：**specialize**（入口追踪与 warp 角色分区）、**address**（smem_pool/TensorMap 地址构造）、**ring**（无符号跨步的 `(stage, phase)` 游标）。

## 内部结构

图谱 contains 边给出 9 个子节点，源码可归为五组：

| 组 | 成员 | 职责 |
|---|---|---|
| 语句语义代理 | `_StmtProxy` / `_PTXProxy` / `_CUDAProxy` / `_is_void_call` | 恢复追踪模式下的语句发射；ptx 版附加 `addr()`；cuda 版退役非纯值内联函数 |
| 指令收严 | `_cp_async_needs_src_size` | K 比 ISA 表更严的唯一指令：cp.async 尾操作数必填 |
| 张量族 | `alloc_buffer` / `decl_buffer` / `alloc_local` / `local_scalar` / `stack_alloca` / `assign` | 普通默认布局张量的分配与标量写回（显式拒绝 tmem scope） |
| warp 语义 | `uniform` | 把 lane 值广播为 warp-uniform，对已 uniform 值是语义 no-op |
| 属性网关 | 模块级 `__getattr__` | 拦截退役拼写并给迁移指引，其余透传到 `tvm.script.tirx` |

此外它是 barrel 文件：底部 re-export `entry`（`kernel`/`gptr`/`TensorMap`/`cta_id`…）、`smem`（`smem_pool`/`KTile`…）、`specialize`、`pipeline`（`MBarrier`/`Pipeline`/`TMABar`…）、`ring`、`scheduler`、`idioms` 七个子模块的全部原语，并定义 `f16/bf16/SW128B` 等 dtype/swizzle token。

## 外部连接

- **向下**（imports 出边 8 条）：7 个 kern 子模块 + `tests/test_kern_api.py` 的 tested_by。底层依赖 `tvm.script.tirx`（`_T`）、`tvm.tirx.script.builder.ir`（`_I`）、`IRBuilder`、TVM 的 `SwizzleMode`。
- **向上**（imports 入边 117 条，全库之最）：每个 kernel 文件 import 它；两处 `calls` 来自 deepgemm 的 `build_kernel`/`get_kernel`——说明 DSL 深入到了 kernel 的构造函数内部，不止于模块头。

## 数据流

以 rmsnorm 里一行 `K.ptx.barrier.sync.aligned(0, 128)` 为例走读：

1. `K.ptx` 在模块加载时已是 `_PTXProxy(_T.ptx)`；
2. `.barrier.sync.aligned` 每级 `__getattr__` 都返回新的 `_StmtProxy`，形成属性链代理；
3. `__call__` 先过 `_cp_async_needs_src_size` 体检，然后 `obj(*args)` 真正构建 `tvm.ir.Expr`，并在追踪会话内挂 source span；
4. `_is_void_call` 判定返回类型是 dtype 为空的 `PrimType` → 这是一条语句 → `_T.evaluate(result)` 发射进 IR 树，返回 `None`；
5. 若返回真实 dtype（`elect_sync`、`get_tmem_addr`…）则原样透传给 Python 表达式继续参与运算。

张量族同理：`local_scalar(dtype, init=x)` 等价于"声明 + assign"两条语句，`assign` 校验目标是 local scope 的可写标量后调 `_I.buffer_store` 落 IR；`name` 参数是因为追踪无法像 parser 那样从赋值目标反推源码名。`uniform(x, lane=0)` 的展开在 docstring 里写成了三行伪码：分配一个 `alloc_local([1])`，用 `_shfl_sync(0xFFFFFFFF, x, lane, width)` 写入，返回 `t[0]`——集武操作在发射点物化，而不是在使用点惰性重放。最终 `@K.kernel` 收束出 PrimFunc，交给 `runner.compile_kernel`（tirx pipeline）编译。

入口侧的流向也值得一走：kernel 签名里的指针用 `K.gptr(T)` 声明，TMA 描述符用 `K.TensorMap` 承接；`K.cta_id`/`warp_id`/`lane_id`/`thread_id` 是入口坐标，`K.specialize` 之后的 `tid_in_role`/`warp_id_in_role` 则是角色相对坐标——同一个 warp 在不同 role 里拿到不同的编号视图，这是 specialize 族的全部魔法。两个边角函数各有专属场景：`keep_alive(buf)` 发射一次 no-op 使用，钉住"函数体只经由 TensorMap 触达"的 buffer 参数，否则参数被死代码消除、launch ABI 悄悄改变；`call_packed(...)` 给返回 int32 的 `tvm_call_packed` 补语句语义（int32 不是 void，不在自动发射范围内，而 kernel 侧用例全部丢弃返回值）。

## 设计决策

1. **Proxy 恢复"调用即语句"契约**。TVMScript parser 会把裸表达式语句转成 `T.evaluate(...)`，tracer 却会构建 Call 后静默丢弃——`_StmtProxy` 用引擎自己的契约（void 调用必发射、目标操作数在前）补齐语义。这是整个 DSL 能用的前提。
2. **负面 API + 可操作报错**。`__getattr__` 维护四张黑名单：21 个 tirx 逃逸名（`tile`/`smem`/`prim_func`…）、绑定中态（`Bind`/`Let`）、`evaluate`、parser 转发口（`ir`/`parser`），每个都附迁移指引文案（如 `_BINDING_HELP` 讲清"纯算术用普通变量、须单次求值用 `K.local_scalar`"）。错误信息本身就是文档。
3. **cp.async 尾操作数强制**。三种拼写（拷 n 字节 / zero-fill / ignore-src）在 false lane 上留下**不同**的目的地内容，而 `pred=` 整指令谓词是第四种（保留旧值）。K 按指令表兄弟项（`_src_size`/`_ignore_src`）判定而非字符串匹配助记符，拒绝唯一不说清意图的缺尾拼写——注释里还记录了 GDN 冻结内核里一处"pre-store 是 load-bearing"的真实案例。
4. **`_CUDAProxy` 退役非纯值内联函数**（`_shfl_sync`/`ldg`/`atomic_add`…）：惰性求值的值返回型 intrinsic 会被每个文本使用点重求值且无法提升，强制走 DPS 的 ptx 拼写让"目的地和求值次数"显式到不可拼错。
5. **`uniform` 必须物化到 local**：`__shfl_sync` 是 warp 集体操作，追踪体在使用点发射值返回 intrinsic，落在 guard 内会让被排除的 lane 永远到不了集合点——CTA 挂死。物化 + 广播在 GDN prefill 实测 3.7% 端到端收益。
6. **barrel 底部延迟 import**：`pipeline`/`ring`/`scheduler` 在 Kern 公共原语就位后才导入，"协议层的原生覆写透过 K 而非第二套私有 IRBuilder 表达自己"——import 顺序即架构。

## 新人提示

- 从 `tests/test_kern_api.py` 与 `tirx_kernels/basic/rmsnorm.py` 切入，一个讲 API 边界、一个是完整最小实例；模块 docstring（38 行）就是 DSL 规范正文，值得先读三遍。
- `K` 是**命名空间**不是对象；`K.idioms` 是库不是第四原语族——调用点写 `K.idioms.xxx` 是在声明"我命名的是一个形状而非一条指令"。
- 想知道某属性到底存不存在：`K.<name>` 的解析顺序是先查四张黑名单与本地定义，再透传 `tvm.script.tirx`；所以"K 没有"可能意味着"被故意收走了"，报错文案会告诉你新拼写。
- 易混淆三连：`K.evaluate` 不存在（void 调用自动发射）；绑定只有两种拼写；tmem 不是 buffer 而是 tcgen05 列操作数 + `K.cuda.get_tmem_addr`。
- 性能调试时的一个反直觉点：`threadIdx.x >> 5` 这种"事实上 uniform"的值，ptxas 无法证明，值和它 predicate 的一切都滞留向量数据通路——`K.uniform` 一次 `__shfl_sync` 就能把它们放行（GDN prefill 3.7% 端到端收益的来源），且输出位级一致。
