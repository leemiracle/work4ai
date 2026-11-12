# explain-11 · Relax VM 虚拟机运行时：src/runtime/vm/vm.cc

## 角色定位

`vm.cc`（977 行）是 relax 图的**执行终点**：`src/relax/backend/vm/codegen_vm.cc` 把 relax 函数编成字节码（Executable），本文件的 `VirtualMachineImpl` 就是那台解释执行的栈式-寄存器混合虚拟机。fork 的 LLM 推理全链路在此收官——VM 调度的 kernel 可能是 tirx 编译产物（DLPack 函数）、FlashInfer 外部库（explain-09 的函数对象），或另一个 VM 函数；`invoke_closure` 同时是 Python 侧 `VirtualMachine` 模块的入口（L221-234 的 vtable 把它注册成名为 `relax.VirtualMachine` 的 runtime Module）。文件顶部还是理解 TVM 参数流动的关键：`ConvertArgToDevice` 系列函数（L90-146）回答"张量怎么从 CPU 进 GPU"。

## 内部结构

**闭包与工具层（L40-146）**：`VMClosure`（L44-49）= 函数名 + `ffi::Function` 的轻包装；`BindLastArgs`（L57-66）做尾部参数柯里化（新函数把 last_args 追加在调用尾部——LLM 推理里保存"绑定好 KV cache 与权重"的闭包就靠它）；`IndexIntoNestedObject`（L73-88）支持嵌套 Array 解索引（多输出 tuple 取分量）；设备搬运三连 `ConvertTensorToDevice/ConvertObjectToDevice/ConvertArgToDevice`（L90/101/117）——注释 L118-121 给出关键语义：**DLTensor 参数一律深拷贝**（"To be extra careful"），零拷贝需要显式走 TVM Native API 或 `Tensor::FromDLPack`。

**VMFrame 栈帧（L154-188）**：寄存器机型而非纯栈机——每帧有 `register_file`（静态分配的 RegType=ffi::Any 数组，L167）、返回 pc、**caller_return_register**（返回值直写调用者寄存器的编号，L169）、复用的 `call_args` 缓冲（L171）。`ResetForRecycle`（L184-187）支持帧对象回收复用，避免逐调用分配。

**VirtualMachineImpl（L190 起）**：公共接口 LoadExecutable/Init/GetClosure/InvokeClosurePacked/SetInstrument（L195-203）；模块 vtable（L221-234）注册 12 个入口——`vm_initialization/save_function/invoke_closure/invoke_stateful/set_instrument/get_output*/set_input*`，**`_LookupFunction` 作为默认入口**（L234）使任意函数名查询都能拿到可调用闭包——Python 侧 `vm["main"](x)` 的魔法来源。`SetInput`（L250-258 注释）解释了 RPC 场景下 Tensor 转 DLTensor 的兼容设计。

**调用路径（L460-698）**：`Init`（L465）按设备列表建 Allocator；`InitFuncPool`（L700-725）预解析函数表——kPackedFunc 依次查 imports → 全局 registry → 报错三连（L705-716 的错误文案本身就是排查指南），kVMFunc/kVMTIRFunc 则现场建闭包；`InvokeBytecode`（L660-698）：校验参数个数（L674-690 的报错连参数名列表都拼出来）、PushFrame、**把可能的 Call 调用者 dst 记进新帧**（L669-671，返回值路由的伏笔）、写寄存器、跳 start_instr 进 RunLoop。

**指令执行核心（L727-855）**：`RunInstrCall`（L727）是 Call 指令的全过程——参数四类分发（kRegister/kImmediate/kConstIdx/kFuncIdx，L741-762）填入帧内复用的 call_args；L734 的 NOTE 注释警告"不得 resize 那个 vector ref 否则 segfault"——**复用缓冲的生存期陷阱**亲笔记录；无 instrument 直接调闭包，有 instrument 则前插 4 个回调槽位做 before/after 钩子（L769-800，dtype 转 string 因为"py callback cannot handle dtype atm"）；返回值写回 dst 寄存器，**特殊寄存器号是 NOP**（L804-806）。`RunLoop`（L811-855）是整个 VM 的心脏——四指令派发循环：Call（L819）→ RunInstrCall；Ret（L823-838）读结果寄存器、单帧直接返回/多帧写父帧 caller_return_register 后 return；Goto（L839）pc 相对跳转；If（L843-851）条件走 pc+1 否则 false_offset（L848 校验必须 >1）。**只有四条指令**——relax 的高级控制流在 codegen 期已全部降级。

## 外部连接

- **上游**：`bytecode.cc/executable.cc`（指令编码与序列化格式，Instruction 的变长编码在此定义）；`codegen_vm.cc`（字节码生产者）。
- **kernel 世界**：func_pool_ 里的 ffi::Function 可能是 libtvm_runtime 加载的 PrimFunc（explain-10 产物）、FlashInfer 包装（explain-09）、或 builtin（`builtin.cc` 798 行——`vm.builtin.*` 一族，shape 函数/alloc_storage/attention 入口等）。
- **Python 面**：`python/tvm/runtime/relax_vm.py` 的 VirtualMachine 类包装本模块；`set_instrument` 支撑执行级 profiling（每条 Call 的前后钩子）。
- **LLM 线收口**：paged KV cache 由 VM 的全局对象槽持有，attention 算子作为普通 Call 执行——explain-09 的三方协议在 VM 层就是几次 builtin 调用。

## 数据流

`vm = VirtualMachine(exec, device)` → Python invoke "main" → `_InvokeClosure` → GetClosure 找到入口闭包 → InvokeClosureInternal → InvokeBytecode：PushFrame、参数写寄存器 → RunLoop 循环取指执行：Call 指令拼参数调 kernel（tensor 在此被 ConvertArgToDevice 搬运至目标设备）、结果回寄存器；If/Goto 控制流推进 pc；Ret 弹帧回值——直到最外层帧返回。LLM 推理时同一 Executable 被反复 invoke，帧与 call_args 缓冲被复用，KV cache 对象跨 invoke 存活。

## 设计决策

1. **四指令极简 ISA**：Call/Ret/Goto/If 之外无它——复杂度全部前移到编译期（图优化、fusion、寄存器分配），运行时保持可审计的最小内核。与解释器复杂度常年失控的教训对照鲜明。
2. **寄存器机 + 返回值直写**：caller_return_register（L169）让跨帧返回零中间栈操作；寄存器文件静态定长，帧可整体回收（L184）。
3. **参数缓冲帧内复用**（L732）：每次 Call 不再分配 vector——热点路径的分配消除，代价是 L734 的 resize 禁令必须人人遵守。
4. **instrument 作为一等能力**（L769-800）：before/after 钩子 + kSkipRun 返回可跳过执行——profiler/debugger 不需要改 VM 源码。
5. **DLTensor 深拷贝保守默认**（L118-121）：正确性优先于性能，零拷贝作为显式 opt-in——与众多框架"默认零拷贝、用户踩坑"的路线相反。

## 新人提示

- "Cannot find ffi::Function xxx in either..."（L712-715）是部署最常见错误：kernel 库没随 Executable 一起加载，查 `executable_stats`/imports 顺序。
- 排查性能用 `set_instrument`（Python 侧 `vm.set_instrument`）——每条 Call 的函数名与耗时唾手可得，比猜 fusion 是否生效高效得多。
- 多输出函数取分量靠 `get_output_arity/get_output`（L227-228），直接在 Python 下标 tuple 也行（IndexIntoNestedObject L73）。
- 读指令格式去 `bytecode.h`；本文件只见 Opcode 四值。VM 序列化产物（.so 里嵌的 code section）在 executable.cc。
