# MatX operators 惰性算子层（CRTP 表达式模板）

## 一、角色定位

`include/matx/operators/` 下 111 个头文件是 MatX 的"语言层"：写下 `Av = fft(Bv) * cv + dv;` 时，等号右侧一切在编译期被编码进 C++ 类型，不启动 kernel、不分配显存。几乎每文件对应一个惰性算子族（`slice.h`=切片、`sum.h`=归约），而 `transforms/` 目录（39 项）才是真正调 cuFFT/cuBLAS/CUB 的执行层。

地基是 CRTP：每个算子类以自身为模板参数继承 `BaseOp`（`base_operator.h:148`），如 `matxBinaryOp : public BaseOp<matxBinaryOp<I1,I2,Op>>`（`binary_operators.h:91`）。基类零虚函数：`run()` 在 `base_operator.h:181` 用 `static_cast<T*>(this)` 下转型后分派，静态多态使整棵树在 device 代码里完全内联——GPU kernel 里没有 vtable 的生存空间。

"通行证"是一行标记 `using matxop = bool;`（`base_operator.h:151`），检测端 `is_matx_op_c`（`type_utils_both.h:160`）只要求有 `matxop` typedef。任何组合仍是 `BaseOp` 派生类，自动持有印章，可无限套娃。

## 二、内部结构

### 2.1 运算符重载 = 表达式树组装器

二元与一元运算符各有一个宏工厂。`MATX_DEFINE_BINARY_OP`（`binary_operators.h:39`）展开后，`operator+` 的全部工作就是返回新算子对象：宏体核心一行 `return detail::matxBinaryOp(base1, base2, Op())`（`binary_operators.h:49`）——不读数据，只把子表达式按值存进 `in1_`/`in2_`（`binary_operators.h:94-95`），语义内核 `AddOp` 存进 `op_`。尾部宏批量实例化挂上 `operator+/-/*/&|^` 与 `pow/max` 等（`binary_operators.h:585-606`）；`MATX_DEFINE_UNARY_OP`（`unary_operators.h:41`）同构，`sqrt/exp/log` 等在 `unary_operators.h:551-575` 展开。

"惰性"的证据在构造函数：`matxUnaryOp` 构造器（`unary_operators.h:114-121`）只把每维尺寸抄进 `size_`，零计算；`matxBinaryOp` 构造器（`binary_operators.h:146-154`）只跑尺寸兼容断言。求值发生在 kernel 内：`matxBinaryOp::operator()`（`binary_operators.h:158-173`）对左右子树各调一次 `get_value` 再调 `op_.operator()`——按线索引、逐元素递归下降的解释器。标量混写也靠 `get_value`（`operator_utils.h:387-401`）区分算子（递归 `operator()`）与标量（原样返回），`A * 2.0f` 的字面量即秩 0 节点。

### 2.2 类型标记家族：比 matxop 更细的方言

除 `matxop` 外还有细粒度印章，全部 `using X = bool`、由 concept 探测：`SliceOp` 挂 `matxoplvalue`（`slice.h:64-65`）宣告可当赋值左值（`is_matx_op_lvalue_c`，`type_utils_both.h:264`）；`set` 挂 `matx_setop`（`set.h:144`。甄别：任务书线索写作 `matx_set_op`，源码标记名实为 `matx_setop`，`is_matx_set_op` 只是 trait 名——`type_utils_both.h:252`）；`FFTOp` 挂 `matx_transform_op` 与 `can_alias`（`fft.h:84,86`），后者宣告 FFT 允许输入输出同内存；`core/tie.h:45-46` 的 `mtie` 挂 `mtie_type` 供多返回值绑定。标记即协议，`run()` 分派因此全在编译期。

### 2.3 三种算子形态

**组合算子**（`matxUnaryOp`/`matxBinaryOp`）只存子表达式与语义内核；**视图算子**（`SliceOp` `slice.h:49`、`AtOp` `at.h:45`、`CloneOp` `clone.h:43`、`PermuteOp` `permute.h:46`）只存索引描述符；**变换门面算子**（`FFTOp` `fft.h:59`、`ReduceOp` `reduce.h:44`）额外持 `tmp_out_`/`ptr`/`prerun_done_`（`fft.h:72-73`）——惰性层与立即层之间的桥。

## 三、外部连接

**向下扎进 core/**。类型身份靠 `type_utils_both.h` 的 concept 家族（`is_matx_op_c`:160、`is_mtie_c`:142、`is_matx_set_op`:252、`is_matx_op_lvalue`:264），求值与尺寸查询靠 `operator_utils.h` 的 `get_value`:387、`get_rank`:284；惰性世界入口在 `core/tensor.h:262-265`——张量 `operator=` 被重载为 `return detail::set(*this, op)`，**赋值本身只生产一个 `set` 对象**。

**向上调 transforms/**。`operators/reduce.h:38` 直接 `#include "matx/transforms/reduce.h"`，`operators/fft.h:44` 包下 `transforms/fft/fft_cuda.h`；`ReduceOp::Exec`（`reduce.h:105-112`）调 `reduce_impl`，`FFTOp::Exec`（`fft.h:451-484`）调 `fft_impl`/`ifft_impl`（`transforms/fft/fft_cuda.h:681,730`），非恒等轴排列时两侧自动套 `permute`（`fft.h:478-481`）。这就是"operators 声明 vs transforms 执行"的物理分工。

**执行接口**是 `run()` 重载族：`run(Ex&&)`（`base_operator.h:181`）面向任意 executor，`run(cudaStream_t)`（`base_operator.h:307-311`）把裸流包成 `cudaExecutor`；`operators/operators.h`（141 行）是聚合伞头。

## 四、数据流

一条 `(Av = slice(Bv,{0,0},{4,4}) * 2.0f).run(stream);` 的完整生命周期分三段：

**组装期（host，零 GPU 调用）**：`slice()`（`slice.h:361`）构造 `SliceOp`，成员只有描述符 `op_`/`sizes_`/`dims_`/`starts_`/`strides_`（`slice.h:57-61`），**无任何数据拷贝**；构造器（`slice.h:150-162`）做负索引归一化与 stride 折算。随后 `operator*` 把它包进 `matxBinaryOp`，`Av = ...` 再把整棵树包进 `set`。

**执行期（device kernel 内）**：`set::operator()` 对每个输出坐标执行 `out_(i,j) = get_value(op_, i,j)`；递归到 `SliceOp::get_impl`（`slice.h:194-231`）把输出索引重映射回源坐标 `ind[i] = starts[j] + inds[j] * strides[i]`，再调底层视图取元素。全树一遍即完成，无中间缓冲。

**变换算子的三段式**：`FFTOp` 被求值时，`PreRun`（`fft.h:495-505`）先 `AllocateTempTensor` 给 `tmp_out_` 申请显存并就地调 `Exec` 跑完 FFT；此后逐元素 `operator()` 只读 `tmp_out_`；`PostRun`（`fft.h:509-517`）归还内存。FFT 在赋值管线里是"提前物化、后续查表"的子表达式，`ReduceOp` 同款（`reduce.h:53-55`）；触发时机即 `base_operator.h:275-283` 的 `PreRun → ex.Exec → PostRun`。

## 五、设计决策

**run() 的编译期分派链**（`base_operator.h:181-300`）用 `if constexpr` 依次五路：①JIT executor 直通 `ex.Exec`（L188-190，无需 PreRun 异步分配）；②动态秩表达式只许走 CUDAJITExecutor，否则 `static_assert` 拒绝（L191-193）；③`mtie` 多返回值先查 LHS/RHS 内存重叠（L195-197）；④`set` 赋值算子进入内层子分派（L199-285）；⑤其余走 `PreRun→Exec→PostRun`（L286-299）。④内部再分四路：分布式约束（L200-214）；**transform 快捷路径**——RHS 是变换算子时直接 `TransformExec` 免掉临时分配（L215-222）；**direct_assign** 直填（L224-239）；**张量到张量**且连续同型时改 `cudaMemcpyAsync` 不启 kernel（L241-263）。每个分支都在省一次分配或 kernel 启动。

一文件一算子有两个推手：JIT 代码生成要求算子自描述——`get_jit_op_str` 能把自身 struct 源码生成字符串（`binary_operators.h:197-252` 生成 `JITBinOp`），文件边界即代码生成单元；且按值存子节点的表达式对象尺寸随树增长，小头文件控制编译成本。例外是 `operators.h`/`all.h` 伞头与 `scalar_ops.h` 标量库。

## 六、新人提示

调试表达式树先用 `str()`——每个算子都递归拼接它（`unary_operators.h:106-108`、`slice.h:148`），开日志即见整棵树。警惕惰性陷阱：`Av = Bv * 2;` 单独一行什么都不执行——`operator=` 返回的 `set` 标着 `[[nodiscard]]`（`tensor.h:261-265`），编译器警告"结果未使用"正是提醒你忘了 `.run(stream)`。自定义算子继承 `BaseOpCustom`（`base_operator.h:391-392`）可省 Rank/Size 样板；想当左值须照 `base_operator.h:378-380` 注释手写 `operator=` 转 `set`，且 LHS 不能是变换算子（`set.h:190` static_assert）。改 slice/clone 索引逻辑时，构造器与 `get_impl` 之外还有 JIT 平行实现（`slice.h:100-145`）须同步。
