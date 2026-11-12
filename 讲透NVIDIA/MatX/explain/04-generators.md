# MatX generators 生成器层：零存储数据源

## 一、角色定位

`include/matx/generators/`（19 头）提供"看起来像张量、实际无存储"的数据源：range、linspace、随机数、窗函数、meshgrid……它们全部继承 `BaseOp`（range.h:42 `class Range : public BaseOp<Range<T>>`、hamming.h:43、random.h:207 同构），因此在类型系统里与真张量平权——可以直接进表达式：`(y = fft(hamming(N) * x)).run(stream)` 里的 `hamming(N)` 不占一个字节显存，窗系数在 kernel 求值那一刻现场计算。这一层是 MatX"表达式即数据流图"哲学的最纯粹体现：**生成器=常量函数节点**。

与 operators/（组合算子）、kernels/（手写 CUDA）的分工：generators 只管"给坐标返回值"（`operator()(index_t)`），不参与归约/变换调度；汇总入口 generators.h:35-42 逐个 include 全部子生成器。

## 二、内部结构

### 2.1 序列族：一切的基础是 Range

`Range`（range.h:42）持有 `first_/step_`（:45/:98 构造），`operator()` 即 `first_ + i*step_`。值得注意它内置 **JIT 序列化协议**：`get_jit_class_name()` 返回 `"JITRange_first..._step..."`（range.h:68），`ToJitString` 直接生成 device 端 struct 源码（:80-91 `"constexpr static T step_ = ...; auto operator()(index_t idx) ... return first_ + T(i * step_)"`）——生成器可以被 CUDAJITExecutor 融合编译（见 explain 07），这是每个生成器头里出现 `JIT_Storage`（alternate.h:51、chirp.h:67、diag.h:54）的原因。

上层序列都由 Range 复合而成：`LinspaceOp`（linspace.h:41，模板参数 NUM_RC 区分半/全精度路径）、`LogspaceOp`（logspace.h:95-112）内部就是一条 `Range` 加指数——logspace.h:99 直接可见 `range_ = Range<T>{first, (last-first)/(count-1)}` 的构造。zeros/ones/fill 是退化常量：fill 类似地只存一个标量。

### 2.2 窗函数族：一个模板五种窗

hamming/hanning/blackman/bartlett/flattop 五个头结构完全同构：类 + JIT 支持 + 一个逐元素公式。以 hamming.h:94-97 为例，求值体是闭包 `.54 - .46*cos(2π·idx/(size_-1))`，`ApplyGeneratorVecFunc` 包一层能力分发（SIMT/向量化 capability），`size_==1` 时特判返回 1（:96）。改窗只需改系数——五文件几乎只差这一行数学。

### 2.3 随机数：curand 设备端 + 可复现流

`RandomOp`（random.h:207）是生成器层最重的类：

- **分布与类型的笛卡尔积**由 trait 函数族展开：curand_uniform/curand_normal/curand_uniform_double/curand_normal_double（random.h:89/92/109/112），复数走 real/imag 分别采样（:129-130）与 curand_normal2 向量化（:133）。
- **两种物化路径**：`random_direct_fill_kernel`（:175）把随机值直写输出张量（`DirectAssignLinear`），`random_materialize_kernel`（:184）写裸指针——前者是惰性求值下的按需生成，后者服务显式 materialize。host 侧另有 curand 生成器 API 路径（:368 `curandSetPseudoRandomGeneratorSeed`）。
- **seed 控制可复现性**：seed 进 JIT 缓存键（:565-566 `"_seed" + std::to_string(seed_) + "_dist"...`）；JIT 路径用 **curanddx philox4_32** 设备端引擎（:603 `curanddx::Generator<curanddx::philox4_32>`），每个线程独立子流，同一 seed 跨运行结果一致。

### 2.4 形状类生成器

meshgrid（MeshGridOp meshgrid.h:44，从多个 rank-1 张量构造广播网格，:193 组形状）、diag（diag.h:41，对角矩阵生成）、fftfreq（FFTFreqOp fftfreq.h:41，NumPy fftfreq 语义：正负频率交错）、alternate（Alternating alternate.h:42，交替序列）、chirp（Chirp chirp.h:51，枚举 ChirpMethod/ChirpType :40/:44 区分线性/二次/对数调频）。generator1d.h 的 `matxGenerator1D_t`（:40）是 1D 生成器的 CRTP 中间基类，给"沿某一维生成"的族（fftfreq 等）提供公共形状/求值骨架。

## 三、外部连接

- **向上**：被 operators/ 的运算符直接消费（生成器是 BaseOp，`Range + Range`、`hamming * x` 都是合法组合）；
- **向内**：被 transforms/ 与 kernels/ 内部使用——pwelch 谱估计内部要加窗（kernels/pwelch.cuh 引窗函数语义），random 是 test/00_tensor 大量测试的造数工具；
- **向 JIT**：每个生成器的 `ToJitString/get_jit_class_name` 把自身序列化成 NVRTC 可编译源码（Range range.h:68、Alternating alternate.h:59、Diag diag.h:81、MeshGrid meshgrid.h:77），与 executors/jit_cuda.h 的融合管线对接——**生成器层是全库 JIT 化最彻底的层**，因为它天生无状态。

## 四、数据流

典型链路（雷达脉冲生成 + 加窗 + FFT）：`make_tensor` 建输出 → 表达式树 `y = fft(hamming(N) * chirp(f0, f1))` → `.run(cudaExecutor)` → BaseOp::run 分派（base_operator.h:181 起）→ JIT 路径把 hamming/chirp 的 ToJitString 源码与 fft 算子拼成单个 kernel → NVRTC 编译缓存（按生成器参数+seed+dist 键）→ 启动。非 JIT 路径则在每个线程的 `operator()` 里现调 hamming 公式与 chirp 相位——两条路都不存在"窗数组"这个中间物。

## 五、设计决策

1. **零存储优先于预计算**：窗函数 N 点只省 N 个乘加，却要多一次显存往返；让 `operator()` 现算使窗完全融合进消费者 kernel。代价是每次求值重算 cos——对 FFT 这种 O(N log N) 的消费者可忽略。
2. **Range 作为原子**：linspace/logspace 复合 Range 而非各写公式，减少浮点路径分叉（logspace.h:99-112 四个特化覆盖 float/double/int/半精度）。
3. **JIT 序列化进类型**：每个生成器自带源码生成方法，是把"数据源"变"代码"的关键——对比 NumPy 生成器只能物化数组，MatX 生成器可整树编译。
4. **随机数双引擎**：curand（库调用，host 建流）+ curanddx philox（device 端，JIT 融合）并存，兼容性与融合性各取所需。
5. **甄别**：任务书曾记"generator1d.h 是 1D 基类"——源码实证它是 CRTP 中间基类（generator1d.h:40）但不被全部 1D 生成器继承（range.h:42 直接继承 BaseOp），定位是"带形状的参数化 1D 族骨架"。

## 六、新人提示

1. 生成器没有 `.Size()` 之外的存储，`print(range)` 前必须先赋给真张量物化；
2. 窗函数 size==1 特判返回 1（hamming.h:96），别在外面再除 size；
3. 随机数要可复现就显式传 seed，JIT 缓存键含 seed（random.h:565）——同 seed 同参数命中同一编译产物；
4. `fftfreq(N)` 返回 [0,1,...,-2,-1]/N 交错序（fftfreq.h:41 的 NumPy 语义），配 fftshift 用；
5. 写新生成器的最短路径：拷 hamming.h，改类名/公式/ToJitString 三处，在 generators.h 加 include。

*锚清单：range.h:42/45/68/80-91/98、linspace.h:41、logspace.h:95/99-112、hamming.h:43/94-97/96、random.h:38/67/70/89/92/109/112/129-130/133/175/184/207/215/301/309/312/320/368-369/565-566/585/603、alternate.h:42/51/59、chirp.h:40/44/51/67、diag.h:41/54/81、meshgrid.h:44/55/77/193、fftfreq.h:41、generator1d.h:40、generators.h:35-42、base_operator.h:181。*
