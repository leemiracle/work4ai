
# merge代码的规则（兴趣组：）
https://github.com/pytorch/pytorch/blob/main/.github/merge_rules.yaml 
- ONNX exporter
- NVFuser
- OSS CI
  - pytorchbot
    - slow tests
    - Executorch
    - XLA
- Documentation
- Mobile
- PrimTorch
- Linear Algebra
- FFT
- Sparse
- MPS
- Distributed
- DCP
- IDEEP
- oneDNN graph
- CPU ATen backend
- CPU frontend
- CPU inductor
- Autocast
- NNC
- Lazy Tensor
- functorch
- ROCm
- XPU
- 人
  - superuser
  - Core Reviewers
  - Core Maintainers

# 设计理念
纲领性文件，理解代码编写及设计意图的基础
1. 可用性胜于性能：尽量避免在没有对权衡有清晰认识的情况下限制用户。无缝移动到不同的硬件和软件平台，与不同的库和框架进行互作
   1. 性能优势不够引人注目
   2. 会将生态系统分割成不同的限制集，用户很快就会无法理解这些限制
2. Simple Over Easy：显式优于隐式，简单胜于复杂
   1. 倾向于公开简单而明确的构建块，而不是从业者易于使用的 API【】
3. Python First：利用python的生态（可调试、可修改和灵活的框架）
   1. TorchDynamo,a Python frame evaluation tool 
   2. torch_function and torch_dispatch 

# 社区
PyTorch Governance | Build + CI
- PyTorch Contribution Guide
  - https://discuss.pytorch.org/categories
  - https://github.com/pytorch/pytorch/issues
- PyTorch Design Philosophy
  - 易用性优于性能：想法和项目只有在很多人都感兴趣并愿意花时间在一起的情况下才能有机地成长。
    - https://soumith.ch/blog/2021-08-02-growing-opensource.md.html
    - 考虑项目：以技术为中心？传播什么思想？
      - 做的建模将需要更多的灵活性和可调试性
      - 测量和比较【用户体验：灵活性、API 设计和可调试性】
      - https://blog.ezyang.com/2021/01/pytorch-open-source-process/
      - 整合：水平或垂直（正确的激励）
    - 关于 PyTorch 的决定和建议：
      - ML compiler 为中心
        - TorchScript （ jit.script）： 
          - 使硬件供应商能够build out-of-tree backends
      - libtorch :移动端
      - distributed:
    - 设计的起源
      - torch-autograd：来源HIPS/autograd 库，以及之后创建的jax
      - Chainer 
    - 大规模训练
      - 并行化及节省内存的技巧
      - 尽快在这些 GPU 之间传递状态
      - 从故障（硬件、软件等）中恢复尽可能快
  - 简单胜过容易（python之禅）：简单胜过容易
    - 专注于简单的底层构建块有助于指导“容易”API 的设计：一开始不自动化使我们能够更快地达到良好的自动化水平
  - Python优先，并提供一流的语言互操作性
- PyTorch Governance | Mechanics
- PyTorch Governance | Maintainers
  - 核心topic：https://pytorch.ac.cn/docs/stable/community/persons_of_interest.html

# 开发者关注
- Automatic Mixed Precision examples 混合精度
  - torch.autocast 的实例允许对选定的区域进行自动类型转换
  - torch.amp.GradScaler 的实例有助于方便地执行梯度缩放步骤
- Autograd mechanics
  - 有向无环图：通过从根节点追溯到叶节点，您可以使用链式法则自动计算梯度
- Broadcasting semantics
  - 其张量参数可以自动扩展到相同大小（无需复制数据） https://numpy.com.cn/doc/stable/user/basics.broadcasting.html
- CPU threading and TorchScript inference
  - @torch.jit.script 使用一个线程池来实现算子间并行性，该线程池由应用进程内所有分叉的推理任务共享
  - 内部库（ATen） 外部库（openMP TBB）
- CUDA semantics
  - flag：allow_tf32 allow_bf16_reduced_precision_reduction 
  - 异步执行：CUDA_LAUNCH_BLOCKING=1 来强制进行同步计算
    - 在测量之前调用 torch.cuda.synchronize()，或者使用 torch.cuda.Event 记录时间
  - CUDA 流：不同流的操作可以以任何相对顺序并发执行，除非使用了显式同步函数（例如 synchronize() 或 wait_stream()）
  - 反向传播的流语义
  - 内存管理： 
    - 理解内存使用
      - pytorch.org/memory_viz 【一种生成内存快照的方法，可以记录任意时间点已分配 CUDA 内存的状态，并可选择记录导致该快照的分配事件历史。】
      - 启用内存历史记录，运行待观察的代码，然后将序列化（pickled）的快照保存到文件中
      - 快照 API 
    - 使用 PYTORCH_CUDA_ALLOC_CONF 优化：各种配置
      - PYTORCH_NO_CUDA_MEMORY_CACHING=1 以禁用缓存
    - 使用 CUDA 的自定义内存分配器
    - 在同一个程序中混合不同的 CUDA 系统分配器
  - cuBLAS 工作区
  - cuFFT plan 缓存
  - 即时编译
- PyTorch Custom Operators Landing Page
  - PyTorch 自定义算子
- Distributed Data Parallel 分布式数据并行 torch.nn.parallel.DistributedDataParallel
- Extending PyTorch
  - 添加新算子，拓展 torch.autograd
  - tensor类型拓展
  - __torch_function__ 能够拦截 torch 的所有 Python API 和 Tensor 方法
  - __torch_dispatch__ 能够拦截所有对 aten 原生 API 的调用【Tensor 上的所有方法在进入分发器之前都会转换为函数调用，因此会在此处显示为函数调用】
  - 使用模式 (Modes) 扩展所有 torch API： 如from torch.overrides import TorchFunctionMode, resolve_name
- Extending torch.func with autograd.Function
  - torch.autograd.Function 的 forward() 和 backward() 都调用其他系统（如 C++、CUDA、numpy、triton）中的函数。
  - torch.autograd.Function 是用 PyTorch 算子实现的。PyTorch 能够自动计算 PyTorch 算子的梯度，但也许我们希望自定义梯度计算方式
- Frequently Asked Questions
- FSDP Notes
- Getting Started on Intel GPU
- Gradcheck mechanics： Gradcheck 机制

- HIP (ROCm) semantics
- Features for large-scale deployments 大规模部署特性
  -  torch.autograd.profiler，能够按需测量单个算子花费的时间。
  -  使用 torch::addGlobalCallback 为任何算子调用添加新的回调函数。钩子将通过描述调用上下文（例如 name）的 torch::RecordFunction 结构体进行调用
  -  算子回调函数还可以访问 c10::ThreadLocalDebugInfo::get() 接口，该接口返回指向保存调试信息的结构体的指针
  -  通过将可选的采样率传递给 torch::addGlobalCallback，针对每个回调函数启用
  -  API 使用情况日志记录
     -  使用 c10::SetAPIUsageHandler：event_name
        -  在代码中使用 C++ 中的 C10_LOG_API_USAGE_ONCE("my_api")或 Python 中的 torch._C._log_api_usage_once("my.api") 添加新的 API 触发点
  -  为保存的 TorchScript 模型附加元数据
- LibTorch Stable ABI
- Modules 表示神经网络
  - 作为构建块
  - 状态state_dict
  - 初始化
  - hook：
    - 前向： register_forward_pre_hook() 和 register_forward_hook() 
    - register_full_backward_pre_hook() 和 register_full_backward_hook()
    -  FX 组件提供了一种灵活的方式，通过直接操作 Module 计算图来转换 Module。
- MPS backend
- Multiprocessing best practices
- Numerical accuracy
- Reproducibility 可复现性
  - 使用 torch.manual_seed() 为所有设备（包括 CPU 和 CUDA）设置 RNG 的种子
  - 用 torch.backends.cudnn.benchmark = False 禁用基准测试功能，会导致 cuDNN 确定性地选择一种算法，这可能会以降低性能为代价。
  - torch.use_deterministic_algorithms() 使用确定性算法
- Serialization semantics
- Windows FAQ
# Language Bindings
- C++
- torch::deploy 迁移到 pytorch/multipy

# Python API
- torch
- torch.nn
- torch.nn.functional
- torch.Tensor
- Tensor Attributes
- Tensor Views
- torch.amp
- torch.autograd
- torch.library
- torch.accelerator
- torch.cpu
- torch.cuda
- Understanding CUDA Memory Usage
- Generating a Snapshot
- Using the visualizer
- Snapshot API Reference
- torch.mps
- torch.xpu
- torch.mtia
- torch.mtia.memory
- Meta device
- torch.backends
- torch.export
- torch.distributed
- torch.distributed.tensor
- torch.distributed.algorithms.join
- torch.distributed.elastic
- torch.distributed.fsdp
- torch.distributed.fsdp.fully_shard
- torch.distributed.tensor.parallel
- torch.distributed.optim
- torch.distributed.pipelining
- torch.distributed.checkpoint
- torch.distributions
- torch.compiler
  - 结合了 TorchDynamo 和 TorchInductor 两大组件，将动态图（Eager Mode）转换为高效的静态图（Graph Mode），并进一步生成优化后的 CUDA 代码，显著提升模型的训练和推理性能。
    - TorchInductor 将静态图转换为 Triton DSL（一种面向 GPU 的低级语言），并进行算子融合、内存优化等操作。
    - 生成高效的 CUDA PTX 指令，在 GPU 上运行
- torch.fft
- torch.func
- torch.futures
- torch.fx
- torch.fx.experimental
- torch.hub
- torch.jit
- torch.linalg
- torch.monitor
- torch.signal
- torch.special
- torch.overrides
- torch.package
- torch.profiler
- torch.nn.init
- torch.nn.attention
- torch.onnx
- torch.optim
- Complex Numbers
- DDP Communication Hooks
- Quantization
- Distributed RPC Framework
- torch.random
- torch.masked
- torch.nested
- torch.Size
- torch.sparse
- torch.Storage
- torch.testing
- torch.utils
- torch.utils.benchmark
- torch.utils.bottleneck
- torch.utils.checkpoint
- torch.utils.cpp_extension
- torch.utils.data
- torch.utils.deterministic
- torch.utils.jit
- torch.utils.dlpack
- torch.utils.mobile_optimizer
- torch.utils.model_zoo
- torch.utils.tensorboard
- torch.utils.module_tracker
- Type Info
- Named Tensors
- Named Tensors operator coverage
- torch.__config__
- torch.__future__
- torch._logging
- Torch Environment Variables

# 库

- torchaudio
- TorchData
- TorchRec
- TorchServe
- torchtext
- torchvision
- PyTorch on XLA Devices
- torchao