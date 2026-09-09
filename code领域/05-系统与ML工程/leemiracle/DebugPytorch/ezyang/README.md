# 内部机制
- 支持自动微分的tensor库：连续的存储在内存里
  - 数据类型dtype：数据的大小，如整数为4个字节
  - layout
  - device
  - stride：
    - 逻辑地址转物理内存位置
    - TensorAccessor
  - sizes: (D, H, W) 张量的尺寸
- 高级索引支持：取整行或列（创建view）
  - stride
  - sizes
  - offset
  - 如果在tensor上创建了view，但是又要去释放底层张量的内存：复制视图
- 实际存储：storage
  - size
  - dtype
- operation
  - torch.mm: 两次调用
    - operation的硬件实现（虚拟函数调用）
    - 不同数据类型，选择不同的算子实现（ switch-statement ）
- tensor wrapper(扩展)
  - device：张量物理内存实际存储位置的描述
  - layout：描述我们如何逻辑地解释这个物理内存。
  - dtype：每个元素中实际存储的内容
- autograd code
  - 计算方向
  - AutogradMeta
  - Variable 
    - warp和unwarp :记录自动微分的元信息，追踪和profiling
- 目录功能：https://github.com/pytorch/pytorch/blob/main/CONTRIBUTING.md#codebase-structure
  - torch:python 前端
    - csrc ：python binding(功能性)
      - api:c++
      - autograd
      - jit： torchscript
  - aten/src/ATen: 张量操作的实现
  - c10 核心抽象：包括 Tensor 和 Storage 数据结构的实际实现
- 代码实现torch.add
  - 构建时，DEBUG=1 在at::native::add 打断电
  - 流程：自动生成的
    1. Python 转换为 C++ （Python 参数解析） 
    2. variable dispatch：（VariableType--Type）
       1. handle device type / layout dispatch (Type)
       2. actual kernel
- 编写算子方式
  1. kernel声明：
     1. torch_check:错误检测
     2. 分配output
     3. dtype dispatch
     4. 并行化
     5. 数据访问方式：向量化？
  2. 提供的工具：native_functions.yaml  derivatives.yaml(反向运算)
     1. error check : 底层TORCH_CHECK宏，高级如checkDim（将要检查的包装成TensorArg ）
     2. 算子一般要注册3个： 
        1. 分配output
        2. assume等
        3. dispatch
     3. 访问数据：
        1. 特定位置：TensorAccessor 【将张量的维度和 dtype 硬编码为模板参数】
        2. pointwise (TensorIterator)
     4. TH风格：手动refcounted 及释放；generic中需要针对不同的数据类型编译多次
  3. 高效工具
     1. 编辑一个 headers后（尤其是被很多文件使用的），重建的时间会花很多时间
     2. ci工具要1-2小时才有反馈，使用本地
     3. 使用ccache
  4. issue tracker
     1. 高优先级问题：is:issue label:"high priority" label:triaged 
        1. triaged 的问题意味着至少有一名 PyTorch 开发人员已经查看了它并对该问题进行了初步评估
     2. **rfc**:https://github.com/pytorch/rfcs
# operators 分类
按shape behavior，了解api是如何组合在一起的
- TensorIterator（如 add、sum）
  - pointwise 及 reductions /  broadcasting /  type promotion 类型提升
- Fixed固定数量的维度（如卷积、addbmm）
  - TensorAccessor 
- N-Dimensional（如 squeeze、index_add、tensordot） 任意维度
  - Identity 返回与其输入大小相同的张量
  - Flatten 始终在内部将它们视为 1D 张量
- Composite （如kl_div, isfinite）
- Batched （如nll_loss， adaptive_avg_pool2d）类似于固定维度运算符，不同之处在于它们在开始时接受任意数量的批次维度
- Factory （如empty)没有任何张量输入的情况下生成新的张量
- Trivial （如 size、is_floating_point）运算符不是实际的 Tensor 运算，而是返回非 Tensor 信息或访问内部数据结构的方法
- Sparse 它们的大小计算同时考虑了密集维度和稀疏维度
- Dynamic （如unique）运算符生成的输出，其形状取决于其输入张量的数据
- Variadic(可变参数如cat)：采用多个输入张量;与 n 维作类似

# dispatcher
- 应该调用哪个kernel
  - dispatcher的构成：函数指针表（key-function）
    -  vtables 是按类分配的。这意味着我们只需分配一个新的调度表即可扩展受支持的运算符集
    - 实时扩展：考虑参数及线程本地状态 （TLS）
  - dispatch key set：bitset
    - Each tensor input提供了调度键集（如cpu等）
    - local include set：用于modal功能（如追踪等）
    - a global set,
    - a local exclude set常见的模式是一些处理程序处理一个 dispatch key，然后通过本地 exclude set 屏蔽自己，所以我们以后不会尝试重新处理这个 dispatch key。
    - BackendSelect： 如没tensor信息时
  - 函数指针如何进入表的？就像填 算子-backend表一样（优先级）
    - (TORCH_LIBRARY)为 Operator 定义 schema；然后为dispatch key注册实现
    - fallback 为一些 key定义handle
- box / unbox: 将值封装（box）特定的类型，后再ubox原来的值
  - boxed api ---- boxed fallback
  - boxed api -- 适配器（c++模版） --  boxed fallback
  - 装箱和取消装箱是实现装箱回退的一个关键功能：没有它们，我们就无法让人们编写可以在任何地方工作的单个内核
  - jit(boxed api)
  - eager(unboxed api)
- jax类似功能：https://jax.readthedocs.io/en/latest/notebooks/Writing_custom_interpreters_in_Jax.html
- 文档：https://pytorch.org/tutorials/advanced/dispatcher.html
# 开源
- 外围应用很大。CPU、CUDA、ROCm、ONNX、XLA、服务、分布、量化等。单个贡献者不可能精通项目的每个领域，因此一些挑战就是确保合适的人看到他们需要看到的东西。
  - Issue triage分类（适当的 GitHub 标签将 bug 路由到正确的人员;高优先级 bug 并提高对这些 bug 的认识）
    - 分类标签：https://github.com/pytorch/pytorch/issues/24422
    -  label:"high priority" 
  - Pull request triage
  - Tree hugging oncall(CI系统各类配置)
  - RFCs：pytorch/rfcs 学习了rust的流程
- 有关如何管理大型开源项目（问题及请求的分发、提案）
- oncall：一两小时能处理好的事情

# Podcast
10-20分钟的pytorch主题
- Binding C++ objects to Python
    - Python bindings for Tensor in PyTorch：https://github.com/pytorch/pytorch/blob/65968ab817db323a532f50a2f2ea131ae27dada5/torch/csrc/autograd/python_variable.cpp
    - pybind11 hash map for maintaining object identity：https://github.com/pybind/pybind11/blob/54430436fee2afc4f8443691075a6208f9ea8eba/include/pybind11/detail/internals.h#L99
    - Tensor subclasses don't save their properties：https://github.com/pytorch/pytorch/issues/47117
- History and constraints of the dispatcher
- Dynamic library structure
- Vectorization
- Inference mode
- Just enough CUDA to be dangerous
- Functionalization
- The road to structured kernels
- Backend extensibility
- The life and death of Variable
- How new operators are authored
- History and constraints of Tensor
- Conjugate views
- Automatic mixed precision
- Shared memory
- Stacked diffs and ghstack
- Continuous integration
- Serialization
- native_functions.yaml
- TensorIterator
- __torch_function__
- Why is autograd so complicated
- Code generation
- torch.nn
- Mobile selective build
- PyObject preservation
- C++ frontend
- torchdeploy
- CMake
- TorchScript
- TH
- XLA
- Expect tests
- vmap
- Random number generators
- TensorAccessor
- Anatomy of a domain library
- Default arguments
- CUDA graphs
- Functional modules
- Double backwards
- Intro to distributed
- API design via lexical and dynamic scoping
- pytorch-probot
- Memory layout
- Reference counting
- torch.use_deterministic_algorithms
- gradcheck
- Asynchronous versus synchronous execution
- Multithreading
- Multiple dispatch in __torch_function__
- Batching
- DataLoader with multiple workers leaks memory
- Half precision
- Tensor subclasses and Liskov substitution principle
- All about NVIDIA GPUs
- Torch vs ATen APIs
- Python exceptions
- New CI
- Dispatcher questions with Sherlock
- AOTAutograd
- Strides
- Weak references
- Learning rate schedulers
- History of functorch
- PyTorch 2.0
- torchdynamo
- Zero-one specialization
- Unbacked SymInts
- Dynamo - VariableTracker
- Inductor - IR
- Unsigned integers
- Inductor - Define-by-run IR
- PT2 extension points
- Compiled autograd
- Tensor subclasses and PT2
- AOTInductor
- Min-cut partitioner
- CUDA graph trees
- Inductor - Post-grad FX passes
- Higher order operators
- TORCH_TRACE and tlparse
- Compiler collectives

#  tensordict：SQL的方式查询tensor

# torch.compile的使用
- 提高中小规模的训练效率
- 仅编译您需要的模块：
  - missing manual
- 开源示例：torchtune 、torchtitan
  - 编译的复杂性
  - 编译时间可能很长
  - Eager模式：即时执行
- 提高python的推理效率
  - mode="max-autotune" 自动微调
  - Warmup inference processes before serving traffic to them
  - skip_guard_eval_unsafe
  - 开源实例：vllm、sglang、tensorrt-llm、gpt-fast
  - 缺点
    - 需要以某种方式打包和部署构成模型的实际 Python 代码（及其所有依赖项
    - 缓存不能保证命中：可以缓存由 torch.compile 生成的所有 cubin
    - 多线程目前存在 bug：https://github.com/pytorch/pytorch/issues/136833
- bearing 方式
  - 性能：如SimpleFSDP 
  - Memory
  - 开源实例：FlexAttention
# 使用torch.export
- 仅依赖于一个较小的运行时 ABI（没有 CPython 依赖项），因此二进制文件可以跨 libtorch 版本使用
- 条件：先执行torch.compile
  - 你的模型必须使用 fullgraph=True 进行编译
  - 模型的输入/输出必须仅在 torch.export 支持的参数类型集中
  - 您的模型绝不能重新编译 
  - 模型的顶层必须是 NN
- 小技巧
  - 编程模型
  - 导出的模型的时间：
  - 中间值调试