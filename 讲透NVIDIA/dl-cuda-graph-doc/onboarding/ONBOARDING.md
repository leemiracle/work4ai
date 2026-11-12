# dl-cuda-graph-doc 新手上手指南（ONBOARDING）

> NVIDIA 官方《CUDA Graph Best Practice for PyTorch》文档站源仓（在线版 https://docs.nvidia.com/dl-cuda-graph/ ，README.md:7）。
> 基于知识图谱 37 节点/77 边/2 层/6 步（commit `fd32a8f6`，2026-10-19）。行号锚全部从仓内源文件核实。
> 仓路径：`/usr-data/data2/repos/agent-repos/NVIDIA/dl-cuda-graph-doc`。本仓为纯文档仓：26 个 md（docs/ 合计 12691 行）+ Sphinx 构建链，无产品代码。

## 1. 这是什么：一篇"把 CUDA Graph 讲到生产级"的工程手册

CUDA Graph 解决的问题是 kernel launch overhead：深度学习每步数千次 kernel 启动，CPU 侧的驱动验证/参数准备/调度延迟成为瓶颈（docs/cuda-graph-basics/introduction.md 的动机主线）。本站不是 API 手册，而是**"采纳工程学"**：怎么判断值不值（docs/cuda-graph-basics/quantitative-benefits.md:146-155 的收益表：小 kernel 为主 1.5-3×、已优化负载 >90% GPU 利用率仅 1.05-1.15×）、怎么改代码（sync-free）、五个真实 MLPerf 案例怎么落地、出问题怎么排查。站内内容四大板块 + 参考（docs/index.md:132-186 的六个 toctree）：基础（4 篇）→ PyTorch 集成（7 篇）→ 实例（6 篇）→ 排查（7 篇）+ reference.md（官方文档链接集）。

## 2. 入口设计：index.md 的三路径路由

docs/index.md 是全站导航枢纽（图谱 fanOut=13 第一枢纽），"How to Use This Guide"（index.md:22）按读者状态分三条路：

- **📖 Learning Path 系统学习**（index.md:26-33）：基础 introduction → PyTorch Integration → Best Practices → Sync-Free Code → 排查，五步渐进；
- **🔍 Quick Reference 按症状速查**（index.md:36-46）：七条"症状→页面"映射——捕获失败/结果错误/显存/挂起/性能/动态模式/捕获前检查清单，全部一跳直达对应 troubleshooting 专题页；
- **⚡ Framework-Specific 框架专属**（index.md:50-54）：Megatron-LM/Transformer Engine 用户直奔 te-megatron-cuda-graphs.md（make_graphed_callables/CudaGraphManager/FullCudaGraphWrapper 三机制），PyTorch 用户看 torch-integration.md（三层 API）。

这个三路径设计是文档站的"信息架构"精髓：同一份内容服务新手、救火者、框架用户三种心智，docs/troubleshooting/introduction.md:66-73 再用"失效模式 × 症状 × 阶段 × 难度"四维表格（数值错误标 ⭐⭐⭐ Hard——静默失败最难）承接速查流量。

## 3. 基础章：概念与约束的权威定义

四篇里两篇是全站被引用最多的"宪法级"页：

- **cuda-graph.md**：图结构（节点=工作单元 :46、边=依赖 :58）、两种构建方式对比——显式 API 构造（:93，精细控制但繁琐）vs 流捕获（:155，跑一遍代码自动录制，PyTorch 生态的默认路径）、一次捕获多次重放的复用原理。
- **constraints.md**：约束清单，**实际是 9 节编号**（:15 异步限制禁同步/默认流/查询、:43 静态图拓扑、:68 静态参数含内存地址、:100 自包含流捕获 fork-join、:162 CPU 代码不被捕获、:170 多线程与三种捕获模式、:196 内存约束、:258 多设备、:294 其他）——后续 PyTorch 章与排查章的几乎所有问题都能回溯到这 9 条（页面自己明言此定位）。

## 4. PyTorch 集成章：三层 API 与两大代码改造学

- **torch-integration.md**：三层 API 阶梯（:43-48）——`torch.cuda.graph()` 流捕获上下文（底层，:91）、`torch.cuda.make_graphed_callables()` 高层封装（自动处理 warmup/FWD+BWD 分离捕获/内存池共享，:127）、`torch.compile(mode="reduce-overhead")` 的 CUDAGraph Trees 全自动（:161-184，零手工但受 graph break 制约）。责任划分表（:48-85）明确"框架管什么/用户保什么"。全站最独特的 PyTorch 陷阱剖析在 :240-289：**autocast 缓存随上下文退出清空**——缓存住的 cast 张量若成为图输入，autocast 退出即可能被释放，图回放引用陈旧地址；解法捕获时 `cache_enabled=False`（:245），PyTorch 在 make_graphed_callables 里已强制此规则（:289）。
- **sync-free-code.md**：隐式同步大全。检测手段（:62 PyTorch sync debug 模式、:81 Nsight Systems 带 Python/C++ 调用栈捕获）；数据依赖控制流是重灾区（:218-248）——`if tensor.item() > 0`、`torch.is_nonzero` 都是 cuStreamSynchronize。
- **handling-dynamic-patterns.md**（本章最长 1025 行）：逐类拆官方实现——`loss.isnan()` 分支（:49）、`clip_grad_norm_` 内部隐式 .is_nonzero（:59-69）、`GradScaler.step` 的 inf/nan 检查（:83-95）、early-exit 网络的置信度分支（:105），并跟踪 clip_grad_norm_ 从 PyTorch 1.0 显式同步到现代无同步实现的演化（:139-145）——"把库源码翻给你看"的写法是本站口碑来源。
- **te-megatron-cuda-graphs.md**：TE v2.2 + Megatron core_v0.14.0 的三机制（:23-24）——TE `make_graphed_callables`（:90，VPP 分块×微批×交错流水线调度需手工对齐 _order，:113-131）、Megatron `CudaGraphManager`（自动 record-then-capture 逐层建图）、`FullCudaGraphWrapper`（整迭代）。FP8 挑战（:35：amax/scale 元数据是可变图状态）与 PP 挑战（:70：交错调度的内存池共享）两节是五案例的理论前奏。

## 5. 五案例：同一技术的五种落地姿势（本站精华）

docs/examples/introduction.md:63-80 的对比表是全站信息密度最高的半页——五案例在"捕获范围/图数/捕获机制/静态形状/静态控制流/并行/精度/收益"八维逐项对比（Performance Gain 行 :77）：

| 案例 | 集成方式 | 一句话核心 |
|------|---------|-----------|
| **GPT-3 175B**（gpt-3-175b.md） | TE make_graphed_callables 逐层 | 每层×微批各捕 FWD/BWD 图兼容流水线（:128-131）；核心改造=FP8 amax 全局缓冲从动态增删 realloc 变地址改为一次性持久缓冲+原地更新（:299-310，TE PR #575 前后对比） |
| **Llama 3.1 405B**（llama-31-405b.md） | Megatron FullCudaGraphWrapper 整迭代 | 捕完整训练迭代（:72-128），八大兼容性改造（:246-464：静态输入缓冲/RNG 状态/流管理/关 NCCL record streams/expandable segments/参数 gather 与 optimizer step 解耦），seq_len 8192 固定 |
| **Llama 2 70B LoRA**（llama2-70b-lora.md） | Megatron-Core CudaGraphManager 逐层 | record-then-capture 两阶段自动建图（:65-70，80 层×2 通道=160 图）；warmup 用真实训练数据边训边捕（:165-167）；FP8 状态由框架自动注册为图状态（:57） |
| **RNN-T**（rnnt.md） | 自定义 graph() 函数图化循环体 | 变长序列用分桶（audio 1600 帧 vs text 600 token 两套粒度，:179）；图化的是贪心解码主循环，encoder 留 eager（:72-74）；warmup 必须在与捕获相同的侧流上跑（:189-215） |
| **Stable Diffusion v2**（stable-diffusion-v2.md） | NeMo CUDAGraphCallback + monkey-patch | PyTorch Lightning 拿不到训练循环控制权 → monkey-patch `optimizer_step()` 捕整迭代（:136-149，NeMo cuda_graph.py L365-367）；文档直言 monkey-patch 非良构但为最优权衡（:149）；smart metrics logging 消 host-device 往返（:254） |

五案例合读的模式提炼（docs/examples/introduction.md:85-92）：捕获路径从手工逐层（GPT-3/Llama2）到框架自动整迭代（SD2/Llama3.1）的演进光谱；收益从 RNN-T "significant"、SD2 累计 1.58×、GPT-3 大规模 2.2-3.0%、到 Llama3.1 ~15-25%（对比表 Performance Gain 行）——规模越大、kernel 越大，launch overhead 占比越低。

## 6. 排查章：五类失效模式专题

troubleshooting 七篇按失效模式切分（docs/troubleshooting/introduction.md:66-73 四维表）：**capture-failures.md**（1289 行，同步/内存分配/流三类失败逐条报错样例+✅解法，pinned 内存预分配与 relaxed 捕获模式）；**numerical-errors.md**（1773 行全站最长，⭐⭐⭐ 难度——静默失败：捕获期冻结的分支/索引在回放期不再跟随数据变化，:45-142 有逐迭代输出演示"i=3 起减法分支被永久捕获"）；**memory-issues.md**（caching allocator 统计解读 :41、多图显存叠加与三种省显存模式 :185-229：共享 static_input/顺序图共享缓冲/图输出接图输入）；**process-hang.md**（NCCL 2.26 起通信器销毁轮询等图先释放——`del graph`/`graph.reset()`+atexit 注册清理，:21-58）；**performance-issues.md**（Nsight Systems 有/无图双 profile 对比法 :19、torch.compile graph break 碎裂成小图 :59-77、GPU 利用率已 >95% 则图无收益 :55）。debugging-strategies.md:137 的调试检查清单（热身/静态性/同步/流规则逐项核对）是兜底方法论。

## 7. 构建与工程链（图谱 L02 层）

Sphinx + MyST 栈：docs/conf.py 启用 myst_parser/copybutton/design/mermaid 四扩展（conf.py:22-27），`myst_fence_as_directive=["mermaid"]`（:40）让 ```mermaid 代码块构建时真渲染成图；主题 nvidia_sphinx_theme + versions.json 版本切换器（:55-66）；master_doc=index.md（:50）。本地服务一条命令：`./scripts/sphinx-serve.sh`（README.md:22）——`set -e` 严格模式，uv 缺失自动 curl 官方安装器（sphinx-serve.sh:11-16），`uv sync --group docs` 装依赖（:19），sphinx-autobuild 起 127.0.0.1:8000 热重载并开浏览器（:23）。依赖声明在 pyproject.toml：hatch 后端但 `packages=[]`——不为发 Python 包，纯承载依赖与元信息。双许可：文档 CC-BY-4.0（LICENSE-DOCS）、代码 MIT（README.md:42-43）——引用/改写本站内容时按介质选许可。贡献流程 15 节在 CONTRIBUTING.md（MyST 写作规范+发版流程），docs/contributing.md 是站内指回页。

## 8. 上手建议与勘误提示

按 index 三路径选入口：新手走 Learning Path 五步（第 1 节）；有报错直接跳 troubleshooting 速查表（第 2 节）；做框架集成读 te-megatron 专文+对应案例。改文档跑 sphinx-serve.sh 即时预览。已知站内瑕疵见 ../README.md 勘误节：约束章实为 9 节编号（多处第三方转述"七类约束"不准）；examples 对比表把 Llama2 的 CudaGraphManager 标为 "TE" 与专页归属矛盾（实为 Megatron-Core）；conf.py 版权年份 2025 与源文件 SPDX 2026 不一致。图谱层另注意：docs/assets/.gitkeep 节点摘要把同目录两张插图（lora-arch.png/pp-execution.png）说成 gitkeep 的属性，实为并列文件。
