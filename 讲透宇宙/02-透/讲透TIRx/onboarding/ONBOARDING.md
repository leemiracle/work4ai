# TIRx-kernels 新人上手指南

> 基于仓库知识图谱（2973 节点 / 4865 边 / 14 架构层 / 15 步导览，commit `f72461b`）自动生成，并经源码交叉验证。
> 生成日期：2026-09-04。

---

## 1. 项目总览

**TIRx-kernels** 是 mlc-ai 生态的 GPU kernel 合集与调度库：以 TVM TIR（经 TIRx 编译管线）作为 kernel 的统一表示，用自研的 **Kern DSL**（`import tirx_kernels.kern as K`）手写高性能 GPU kernel，并将它们统一注册、调度、测试与基准化。

**核心语言**：Python（kernel 与基础设施全部是 Python 源码，编译产物为 PTX/CUBIN）+ YAML（基准 workload 配置）+ Markdown（文档与 AI 协作知识层）。

**它解决什么问题**：现代 LLM 推理引擎的算子散落在多个上游项目里——flash-attention、cuDNN Frontend/CuTeDSL、FlashInfer、DeepGEMM、DeepEP、FlashMLA……每个项目都有自己的表示、构建与测试体系。TIRx-kernels 把这些 kernel 用同一套 TIR 表示重写/移植进来，配上统一的注册协议（KERNEL_META）、统一运行器（runner）、统一正确性对照（锁定的参考依赖）与统一性能门禁（pinned baseline 的 ratio_diff），为 MLC 生态提供一层"可注册、可调度、可回归"的高性能算子底座。

**为什么"统一成 TIR 表示"有价值**：其一，kernel 一旦用 Kern/TIR 表达，就同时获得了 IR 级可分析性（契约校验、源码 Span 追踪、结构分析）与 TVM 工具链的编译能力，而不再是不可审计的黑盒 C++/CUDA 源；其二，注册与运行接口统一后，任何新 kernel 只要实现 KernelModule 契约，就零成本接入全库的测试发现、端到端正确性校验与预提交基准回归——这正是"调度库"的含义：上层可以按注册名枚举、按配置调度任意 kernel；其三，移植不是抄代码，而是先把上游设计写成 `.agents/sketch/` 下的 WASP 管线草图，再用 Kern 重写并用锁定的上游参考实现逐配置对照，出处、许可证头与 provenance 全程可追溯。目标硬件以 NVIDIA sm_100a（Blackwell B200）为主，另有少量 sm_107a（Rubin）kernel；全部已注册 kernel 均面向 SM100 级特性（TMA、Tensor Memory、CLC 等）编写。

仓库还有鲜明的实验性一面：`agent_evolved/` 收录从实测 agent 演化运行中筛选出的 kernel（如 KDA forward 相对 FlashKDA 在 B200 上实测 2.27x–2.97x），`.agents/` 下则是给 AI coding agent 准备的技能与设计草图——人类与 AI 共用同一条 kernel 生产线。

---

## 2. 架构分层说明（14 层）

知识图谱把全库 2973 个节点归入 14 层。宏观上分为六大带：

```
┌─────────────────────────────────────────────────────────┐
│ L6 工程根    project-meta（README/AGENTS/锁文件/CI）      │
├─────────────────────────────────────────────────────────┤
│ L5 AI 协作   agent-skills（3 技能） agent-sketch（73 草图）│
├─────────────────────────────────────────────────────────┤
│ L4 质量基准  test │ bench-harness │ bench-config(96 YAML) │
├─────────────────────────────────────────────────────────┤
│ L3 kernel 家族（6 层，共 ~190 kernel）                    │
│   basic(原生) cudnn(63) flashinfer(62) deepseek(26)      │
│   attention(25) agent-evolved(3)                          │
├─────────────────────────────────────────────────────────┤
│ L2 库核心    core-registry（registry/runner/protocol）    │
├─────────────────────────────────────────────────────────┤
│ L1 语言基座   kern-dsl（@K.kernel/smem/pipeline/scheduler）│
└─────────────────────────────────────────────────────────┘
```

逐层职责与代表文件：

| # | 层 | 职责 | 代表文件 |
|---|---|---|---|
| 1 | **Kern DSL 内核语言层** | PTX 级 kernel DSL：入口追踪、共享内存/TensorMap 地址构造、warp 角色分区、软件流水线协议、tile 调度与契约校验。全库 fan-in 之王（被 106 个文件依赖） | `kern/__init__.py`、`kern/entry.py`、`kern/smem.py` |
| 2 | **注册与运行时核心层** | 库级基础设施：KERNEL_META 注册表、KernelModule Protocol、统一测试/基准 runner、参考依赖解析 | `tirx_kernels/registry.py`、`runner.py`、`_protocol.py` |
| 3 | **cuDNN 移植 kernel 层**（63） | 来自 cuDNN Frontend/CuTeDSL 上游：block-sparse attention（bsa）、MoE grouped GEMM + dGLU 激活、GDN/KDA 线性注意力、blockscaled GEMM 变体。最大移植家族 | `cudnn/bsa/`、`cudnn/dglu/`、`cudnn/linear_attention/` |
| 4 | **FlashInfer 移植 kernel 层**（62） | 来自 FlashInfer 上游：RMSNorm 系列、radix/sort/filtered topk、GDN decode/prefill、KDA、mamba、量化。decode 服务主力 | `flashinfer/norm/`、`flashinfer/topk/`、`flashinfer/gdn_decode/` |
| 5 | **DeepSeek 系移植层**（26） | DeepGEMM 的 FP8/FP4 GEMM、grouped GEMM、paged MQA logits、MoE mega kernel；DeepEP 的 elastic dispatch/combine | `deepgemm/`、`deepep/dispatch.py` |
| 6 | **注意力家族移植层**（25） | FlashMLA 的 MLA、FlashAttention-4 forward/backward、MSA（K2 SparseAttention）稀疏注意力流水线 | `flashmla/`、`flashattention/flash_attention4.py`、`msa/` |
| 7 | **原生基础 kernel 层**（12） | 无单一上游的原生 kernel：FP16/BF16 GEMM、NVFP4 GEMM、RMSNorm 示范、AllGather+GEMM 等张量并行融合 kernel。**学习 Kern 写法的最佳起点** | `basic/fp16_bf16_gemm.py`、`basic/rmsnorm.py` |
| 8 | **Agent 演化精选层**（3） | 从实测 agent 演化运行筛选的精选 kernel（KDA forward，服务 Kimi K3 prefill 负载） | `agent_evolved/kda_forward_b1_t8192.py` |
| 9 | **测试与契约校验层**（22） | DSL API 契约、注册表校验、端到端正确性（文件锁预留 GPU）、runner 中断语义、12 个 no-tile/license lint 探针 | `tests/test_kern_api.py`、`tests/test_correctness.py`、`tests/lint/` |
| 10 | **基准编排层**（11） | 预提交回归基准：GpuPool 多卡协调、prepared 子进程执行、同 GPU 配对 A/B、ratio_diff 性能门禁、基线晋升 | `bench_suite/run.py`、`bench_suite/ab.py`、`bench_suite/ratio_diff.py` |
| 11 | **基准配置与基线层**（98） | 96 个按 kernel 组织的 YAML workload 配置（默认名单 263 行 × 90 kernel）+ 钉版基线 baseline.json/md | `bench_suite/config/`、`bench_suite/baseline.json` |
| 12 | **Agent 技能知识层**（112） | 面向 AI coding agent 的三个技能：codegen 诊断（101 篇按症状索引的 PTX field notes）、kernel 移植约束、接入仓库契约 | `.agents/skills/tirx-codegen-diagnostics/` 等 |
| 13 | **Kernel 设计草图层**（73） | 移植前的设计文档：WASP 管线、特化边界、warp 分工与存储规划，按上游家族组织 | `.agents/sketch/cudnn/sm100_bsa_forward_blk64.md` 等 |
| 14 | **项目根与工程配置层**（10） | README/AGENTS.md/NOTICE、pyproject、pre-commit、上游依赖锁文件、CI | `reference-dependencies.json`、`AGENTS.md` |

**分层解读**：这张分层表其实就是一张依赖单向图——底层不认识上层。**L1 语言基座**是自封闭的：kern 模块只依赖 TIRx/TVM，不 import 任何 kernel；所有家族 kernel 反过来依赖它（fan-in 106）。**L2 库核心**横切所有家族：registry 只读源码字面量、runner 只认 Protocol 契约，二者都不关心 kernel 来自哪个上游——这就是六类家族能和平共处的原因。**L3 家族层**内部彼此几乎零依赖（各家族独立子包），唯一强约定是四文件模块形状与 KERNEL_META 协议。**L4 质量基准层**是家族层的"消费者"：test 按注册名发现、bench 按配置驱动，互不越界。**L5 AI 协作层**最特殊——它不是运行时依赖而是"知识依赖"，文档量约占全库三分之一，是图谱中节点数最多的带。新人理解了这条"语言 → 核心 → 家族 → 质量 → 知识"的单向链，就能在任一文件里定位自己的坐标。

---

## 3. 核心模块

### 3.1 Kern DSL（`tirx_kernels/kern/`）

全库的编写基座。`kern/__init__.py`（576 行，barrel 导出）把子模块组成 `K` 命名空间：

- **`entry.py`**：`@K.kernel` 装饰器。装饰期用 IRBuilder **追踪**函数体一次生成 PrimFunc，管理 Session 状态（CTA/warp/lane 作用域、launch_bounds、host_prelude）与源码 Span。得到的 `K.Kernel` 有三个主视图：`func`（pre-lowering PrimFunc，供分析工具用）、`mod`（IRModule）、`compile()`（经 TIRx 管线的可运行模块）。
- **`smem.py`**：共享内存分配与地址构造——`K.smem_pool`（可选 swizzle 布局）、`KTile[stage]` 阶段视图、`KTileView` 四个地址构造器（`ptr_to/m8n8/m8n8x4/mma_desc`），后者即 TMA/TensorMap 描述符与 MMA 描述符的入口。
- **`specialize.py`**：`K.specialize`——CTA 的 warp 角色分区：发射 dispatch guard + `setmaxnreg` 指令，用 Role/WarpGroup/RegisterScope 上下文管理器声明角色，finalize 时校验寄存器配额的硬件不变量。这是 warp specialization（生产者/消费者 warp 分工）的载体。
- **`pipeline.py` / `ring.py`**：软件流水线协议——`PipelineState` 通用 (stage, phase) 游标、MBarrier（init/wait/arrive）、单向 barrier TMABar/TCGen05Bar。`ring.py` 提供相位追踪软件环的无符号回绕游标，用于通用 PipelineState 会改变 lowering 语义的场景。
- **`scheduler.py`**：tile 调度器与 CLC 助手——ClusterPersistentScheduler2D（集群持久 2D 调度）、FlashAttention 线性/LPT 调度、ClusterLaunchControlScheduler。
- **`idioms.py`**：mma_chain、warp_scan_add 等反复出现的多指令形状的惯用法库。
- **`low_level_ir.py`**：pre-lowering 契约校验器（见关键概念 §4.3）。

### 3.2 registry（`tirx_kernels/registry.py`，374 行）

kernel 注册表。**仅凭源码中的字面量 `KERNEL_META` 字典构建索引**——用 `tokenize` 提取字面量，解析期完全不导入 kernel 树（"静态可发现、零导入成本"）；真正导入模块时再校验模块元数据与索引一致。CLI：`python -m tirx_kernels.registry --format json` 输出权威配置清单。配套 `reference_requirements.py` 把 KERNEL_META 里的 reference_requirements 解析为规范化依赖声明并探测本地安装是否满足。

### 3.3 runner（`tirx_kernels/runner.py`，885 行，fan-in 42）

统一 kernel 测试与基准运行器：定义 `run_test/run_gpu/run_bench` 模块契约（即 KernelModule Protocol 的运行面）、进程局部不可序列化的 PreparedBenchmark 桥、CUDA UUID 绑定与校验、离线/GPU 编译模式守卫、GPU 中断延迟机制（临界区内延迟重投递、嵌套推迟到最外层）。**任何 kernel 模块只要实现这套契约，就自动接入全库测试与基准体系**。入口是 `python -m tirx_kernels.test`（按 registry 发现 kernel、逐配置跑正确性、输出 JSON）与 `python -m tirx_kernels.bench`（单 kernel 基准）。

### 3.4 bench_suite（`tirx_kernels/bench_suite/`）

预提交回归基准编排：`run.py`（2612 行，fan-in 59）从 kernel YAML 配置生成工作负载，GpuPool 协调多卡占用，prepared 子进程执行并采集 provenance，最后与钉版基线对比；`ab.py` 实现同 GPU 配对 A/B（从 git 抽取 before 树、同一物理 GPU 交替运行、检测干扰整对重试）；`ratio_diff.py` 是固定性能门禁；`promote_baseline.py` 负责基线晋升。`config/` 下 96 个 YAML 是 workload 的事实源。

### 3.5 kernel 家族速览

- **basic（原生）**：`fp16_bf16_gemm`（标准 GEMM 教科书写法）、`nvfp4_gemm`、`rmsnorm`（最小示范）、`allgather_gemm`/`gemm_reduce_scatter`（通信+计算融合的张量并行 kernel）。
- **cudnn（63 个，最大移植家族）**：bsa block-sparse attention 前向/反向/combine、MoE grouped GEMM + dGLU、GDN/KDA 线性注意力、persistent blockscaled GEMM（amax/swiglu/srelu/dsrelu + 量化变体）。
- **flashinfer（62 个）**：norm 家族（rmsnorm/layernorm/fp4/fp8 量化融合）、topk 家族（radix/sort/filtered）、gdn_decode 多变体（ilp4/wide_vec/mtp）、KDA decode t1–t6、mamba selective_state_update、量化 kernel。
- **deepseek 系**：DeepGEMM 的 `fp8_gemm_1d1d`（FP8/FP4 GEMM 体系）、`_sm100_fp8_fp4_mega_moe`（4288 行的 MoE mega kernel）、paged MQA logits；DeepEP 的 `dispatch.py`/`combine.py`（NVLink 直达 elastic all-to-all）。
- **attention 家族**：`flashmla/sparse_decode_head64.py`（3167 行，main+split-combine 双核结构、TMEM 累加 + CLC 调度）、`flashattention/flash_attention4.py`（FA4 前向）与 backward、`msa/` 稀疏注意力 prepare/fwd/combine 流水线。
- **agent_evolved**：`kda_forward_b1_t8192.py`——agent 演化精选，B200 相对 FlashKDA 2.27x–2.97x。

移植家族普遍采用**四文件模块形状**：`kernel.py`（Kern 实现）+ `spec.py`（配置域/测试矩阵）+ `data.py`（数据生成/校验）+ `reference.py`（上游参考实现对接）。

---

## 4. 关键概念（从图谱 summary/tags 提炼）

1. **@K.kernel 追踪式 DSL**：Kern 是"traced, PTX-level DSL over TIRx"——装饰期追踪一次 Python 函数体生成 PrimFunc；入口 ABI 由 `K.gptr`/`K.TensorMap`/标量 dtype 注解定义；不要在 Kern 模块开 `from __future__ import annotations`（追踪期要读活注解）。
2. **KERNEL_META 注册协议**：kernel 公开身份的唯一权威是模块源码里的 `KERNEL_META` 字面量字典；registry 用 tokenize 零导入解析，导入期再校验一致性——"静态可发现、零导入成本"。
3. **KernelModule Protocol**：`_protocol.py` 定义的模块契约（run_test/run_gpu/run_bench + spec/data），实现即自动接入测试与基准。
4. **no-tile 契约与 lint 门禁**：`low_level_ir.py` 基于 TVM Visitor 在 pre-lowering 检查：不得使用 tile 原语（violation id `tile_primitive`）、不得直接访问 global/shared scope buffer、`setmaxnreg` 必须搭配 `min_blocks_per_sm`、func_call 只能调白名单。`tests/lint/` 下 12 个 AST/IR 探针脚本为特定 kernel 守护此契约——"契约即测试"。
5. **pinned sweep 基准**：bench_suite 对照一份**钉版的 before-run 基线**（baseline.json）跑全部 workload；`ratio_diff.py` 固定门禁 `after_us / before_us < 1.01` 才算过；外部参考实现只做诊断，永不替代直接判定。
6. **WASP 流水线**：sketch 层反复出现的粗粒度 warp 异步软件流水线形态——producer/consumer 角色分离（如 `Q_PROD/Q_CONS`、`KV_PROD/KV_CONS`、`CLC_PROD/CLC_CONS`），以 `pipeline_state(stage, index, phase, count)` 与 mbarrier 解耦，存储规划只经命名管线流动。
7. **warp specialization（K.specialize）**：CTA 内 warp 角色分区 + `setmaxnreg` 动态寄存器配额，Role/WarpGroup/RegisterScope 上下文管理器，finalize 校验硬件不变量。
8. **TMA / TensorMap 描述符**：`smem.py` 的 `KTileView` 地址构造器负责 TMA 描述符与 `mma_desc`；spec 层还有 tma-descriptor 启发式（如 deepgemm spec.py）。
9. **MBarrier / TCGen05 单向 barrier**：`pipeline.py` 的同步原语族——通用 MBarrier（init/wait/arrive）与面向 TMA/TCGen05 的单向 barrier。
10. **CLC（Cluster Launch Control）持久调度**：`scheduler.py` 的 ClusterLaunchControlScheduler 与集群持久化调度（ClusterPersistentScheduler2D），Blackwell 上 persistent kernel 的核心机制。
11. **参考依赖锁**：`reference-dependencies.json` 以精确 git revision 锁定 10 个上游源码仓（DeepGEMM/FlashInfer/flash-attention/FlashMLA/DeepEP/SGLang/FlashKDA 等），自称"single source of truth"；`scripts/install_reference_dependencies.py` 负责克隆/检出/软链/校验，移植 kernel 的正确性对照全部锚在这份锁上。
12. **同 GPU 配对 A/B**：`ab.py` 从 git 抽 before 树、同一物理 GPU 交替运行两侧、检测干扰并整对重试——消除卡间差异的性能测量卫生学。
13. **四文件模块形状**：kernel/spec/data/reference 的移植 kernel 标准组织方式（bsa、deepgemm 家族均如此）。
14. **agent-evolved kernel**：从实测演化运行中筛选、保留稳定 workload 与 provenance 的精选 kernel；运行日志与中间候选不入包。
15. **AI 协作层**：AGENTS.md 是仓库级行为指令（改 emitted instructions/流水线深度等性能敏感代码前必须先调 codegen 诊断技能）；`.agents/skills` 三技能 + `.agents/sketch` 73 篇草图，约占全库三分之一文档节点——人类与 AI agent 共用"草图 → 移植技能 → Kern DSL → registry/runner → 测试基准"同一条生产线。

---

## 5. 推荐学习路径（15 步递进）

按导览改写，分四个阶段。每步：**看什么 → 理解什么 → 自检**。阶段目标：A 建立语言模型（能读懂任意 kernel 的骨架），B 掌握库级机制（知道 kernel 如何被发现、运行、对照），C 遍历家族形态（见过内存受限/分支密集/计算密集三类形态的不同打法），D 进入质量与协作闭环（能安全地改第一个 kernel）。全程建议对照源码阅读，遇到不懂的 DSL 原语随时回查 `kern/README.md`。

**阶段 A：全局与语言（步 1–5）**

1. **项目总览**：读 `README.md`（按来源分节列全部注册 kernel）与 `NOTICE`（cuDNN Frontend/FlashInfer/DeepEP 修改软件的多重许可）。理解：Kern 编写、TIRx 编译、面向 SM100。自检：native/cudnn/flashinfer/deepseek/attention/agent-evolved 六类来源各举一例？
2. **Kern DSL 总纲**：读 `kern/README.md` + `kern/__init__.py` + `entry.py`。理解：`@K.kernel` 追踪生成 PrimFunc、Kernel 三视图 func/mod/compile()、入口 ABI（gptr/TensorMap 注解）。自检：为什么追踪期不能开 future annotations？
3. **存储与 warp 角色**：读 `smem.py` + `specialize.py` + `idioms.py`。理解：smem_pool/KTile 阶段视图/四地址构造器；specialize 的 warp 角色与 setmaxnreg 配额。自检：mma_desc 构造器与 ptr_to 的差别是什么场景？
4. **流水线与调度**：读 `pipeline.py` + `ring.py` + `scheduler.py`。理解：PipelineState 的 (stage, phase) 游标、MBarrier 族、ring 回绕游标的适用场景、CLC 持久调度。自检：为什么有些 kernel 要用 ring 而不是通用 PipelineState？
5. **低层 IR 契约**：读 `low_level_ir.py` + `tests/test_low_level_ir.py`。理解：四条禁令（no-tile、no 直接 global/shared 访问、setmaxnreg 搭配属性、func_call 白名单）及其"故意收窄自由度"的动机。自检：哪条禁令由哪些探针 kernel 验证？

**阶段 B：库级基础设施（步 6–8）**

6. **注册表**：读 `registry.py`。理解：KERNEL_META 唯一权威、tokenize 零导入解析、导入期一致性校验。自检：registry 如何做到解析期不导入 kernel 树？
7. **统一运行器**：读 `runner.py` + `test/__main__.py`。理解：run_test/run_gpu/run_bench 契约、PreparedBenchmark、GPU 中断延迟语义。自检：`python -m tirx_kernels.test` 的发现机制是什么？
8. **参考依赖锁**：读 `reference-dependencies.json` + `scripts/install_reference_dependencies.py` + `cudnn/_reference.py`。理解：锁版本 → 装源码 → 加载参考的完整链路。自检：移植 kernel 的正确性对照锚在哪里？

**阶段 C：kernel 家族全景（步 9–12）**

9. **家族 I（原生 + FA4）**：从 `basic/README.md` 与 `rmsnorm.py`（最小示范）起步，再读 `fp16_bf16_gemm.py`、`allgather_gemm.py`、`flashattention/flash_attention4.py`。理解：标准 GEMM 写法、通信计算融合。自检：能否不查文档写出 rmsnorm 的 kernel 骨架？
10. **家族 II（cuDNN）**：读 `cudnn/dglu/_moe_grouped_gemm_dglu_dbias/kernel.py`、`bsa/block_sparse_attention_forward_sm100_blk128.py`、`linear_attention/gdn_prefill_f16.py`。理解：四文件模块形状、MoE 融合、split-KV 体系。自检：bsa 子目录四个文件各自职责？
11. **家族 III（FlashInfer）**：读 `norm/fused_add_rmsnorm.py`（内存受限型）、`topk/filtered_topk.py`（分支密集型）、`gdn_decode/gdn_decode_bf16_wide_vec_t1.py`（带专属 no-tile lint）。理解：同一 DSL 服务不同 kernel 形态。自检：为什么 filtered_topk 有专门 lint？
12. **家族 IV（DeepSeek 系 + 演化）**：读 `deepgemm/fp8_gemm_1d1d.py`、`deepep/dispatch.py`、`flashmla/sparse_decode_head64.py`、`agent_evolved/README.md`。理解：FP8/FP4 GEMM 体系、elastic all-to-all、双核结构 MLA、agent 演化实验面。自检：KDA 精选 kernel 的实测收益区间？

**阶段 D：质量保障与协作（步 13–15）**

13. **测试体系**：读 `tests/test_kern_api.py`（DSL 行为契约）、`test_registry.py`、`test_correctness.py`（端到端主力：文件锁跨进程预留 GPU）、`test_runner_interrupts.py`。自检：端到端正确性测试如何在多进程间预约 GPU？
14. **基准编排**：读 `bench_suite/run.py` + `ab.py` + `ratio_diff.py` + `config/basic/fp16_bf16_gemm.yaml` + `bench_suite/README.md`。理解：96 YAML/263 行×90 kernel 默认名单、1.01 门禁、A/B 配对、基线冻结与晋升流程。自检：外部参考实现在门禁里扮演什么角色？（答：仅诊断。）
15. **AI 协作层**：读 `AGENTS.md` + `.agents/skills/tirx-kernel-porting/SKILL.md` + 任选一篇 sketch（如 `sm100_bsa_forward_blk64.md`，它是 bsa kernel 的前身）。理解：草图 → 移植 → 集成的 AI 生产线与自己的位置。自检：改流水线深度前按 AGENTS.md 该先做什么？

---

## 6. 文件地图（按层速查）

| 文件 | 一句话职责 |
|---|---|
| **kern-dsl 层** | |
| `tirx_kernels/kern/__init__.py` | K 命名空间 barrel（576 行，fan-in 106 全库最高） |
| `kern/entry.py` | @K.kernel 装饰器与追踪框架、Session 状态 |
| `kern/smem.py` | 共享内存池/KTile/TensorMap 与 mma_desc 地址构造 |
| `kern/specialize.py` | warp 角色分区 + setmaxnreg 寄存器配额 |
| `kern/pipeline.py` / `ring.py` | 软件流水线协议 / 回绕游标环 |
| `kern/scheduler.py` | tile 调度器与 CLC 助手 |
| `kern/idioms.py` | mma_chain 等多指令惯用法库 |
| `kern/low_level_ir.py` | pre-lowering 契约校验器（质量闸） |
| **core-registry 层** | |
| `tirx_kernels/registry.py` | KERNEL_META 注册表（tokenize 零导入） |
| `tirx_kernels/runner.py` | 统一测试/基准运行器（885 行） |
| `tirx_kernels/_protocol.py` | KernelModule Protocol 标准接口 |
| `tirx_kernels/reference_requirements.py` | 参考依赖声明解析与探测 |
| **家族层（代表）** | |
| `basic/rmsnorm.py` | 最小 Kern 示范 kernel |
| `basic/fp16_bf16_gemm.py` | 标准 GEMM 写法范本 |
| `basic/allgather_gemm.py` | AllGather+GEMM 张量并行融合 |
| `cudnn/bsa/` | block-sparse attention 家族（四文件形状） |
| `cudnn/dglu/_moe_grouped_gemm_dglu_dbias/` | MoE grouped GEMM+dGLU 融合 |
| `flashinfer/norm/`、`flashinfer/topk/`、`flashinfer/gdn_decode/` | norm/topk/GDN decode 三大件 |
| `deepgemm/fp8_gemm_1d1d.py` | DeepGEMM FP8/FP4 GEMM 入口 |
| `deepgemm/_sm100_fp8_fp4_mega_moe/kernel.py` | MoE mega kernel（4288 行） |
| `deepep/dispatch.py` / `combine.py` | elastic all-to-all 两半 |
| `flashmla/sparse_decode_head64.py` | MLA 双核结构 decode kernel |
| `flashattention/flash_attention4.py` | FA4 forward 移植 |
| `agent_evolved/kda_forward_b1_t8192.py` | agent 演化精选 KDA |
| **test 层** | |
| `tests/test_correctness.py` | 端到端正确性主力 |
| `tests/test_kern_api.py` | DSL 行为契约（数十条） |
| `tests/lint/check_*_no_tile.py` | 特定 kernel 的 no-tile 探针（12 个） |
| **bench 层** | |
| `tirx_kernels/bench_suite/run.py` | 基准编排核心（2612 行，fan-in 59） |
| `bench_suite/ab.py` | 同 GPU 配对 A/B |
| `bench_suite/ratio_diff.py` | 1.01 性能门禁 |
| `bench_suite/config/<family>/<kernel>.yaml` | workload 事实源（96 个） |
| `tirx_kernels/bench/__main__.py` | 单 kernel 基准 CLI |
| **工程/AI 层** | |
| `reference-dependencies.json` | 10 个上游仓 git revision 锁 |
| `scripts/install_reference_dependencies.py` | 参考依赖安装/校验 |
| `AGENTS.md` | AI agent 仓库级行为指令 |
| `.agents/sketch/*.md` | 73 篇移植前设计草图 |

---

## 7. 复杂度热点（新人慎入）

图谱中 complexity=complex 的代码文件共 120+，以下按行数与耦合度列出最需谨慎的（先跑通小 kernel 再来）：

| 文件 | 行数 | 为什么难 |
|---|---|---|
| `deepgemm/_sm100_fp8_fp4_mega_moe/kernel.py` | 4288 | MoE mega kernel 工厂：FP8/FP4 + grouped GEMM + 激活 + TMA 描述符布局全融合，多路特化编译 |
| `flashmla/sparse_decode_head64.py` | 3167 | 双核结构（main + split-combine）、TMEM 累加、CLC 调度大成 |
| `agent_evolved/kda_forward_b1_t8192.py` | 2757 | agent 演化产物，warp 交织密集，provenance 特殊 |
| `bench_suite/run.py` | 2612 | 基准编排核心：GpuPool/prepared 子进程/provenance/基线对比全在此（fan-in 59） |
| `flashattention/flash_attention4.py` | 1724 | FA4 前向完整移植，流水线与调度深度耦合 |
| `flashinfer/topk/filtered_topk.py` | 1434 | 分支密集型 topk，子图复杂度全库前列，附专属 no-tile lint |
| `deepep/dispatch.py` / `combine.py` | 1303 / — | 分布式 all-to-all + NVLink 直达路径，调试需多卡多进程 |
| `cudnn/bsa/*/kernel.py`、`cudnn/dglu/*/kernel.py` | — | block-sparse attention 与 MoE 融合 kernel，四文件形状里最重的一环 |
| `flashinfer/gdn_decode/*`（4 变体） | — | GDN decode 家族互为变体，读懂一个再对比其余 |
| `kern/__init__.py` + `kern/entry.py` | 576+653 | 行数不大但 fan-in 全库最高：改一行影响 106 个文件，动 DSL 前先读 kern/README 与 low_level_ir 契约 |
| `registry.py` / `runner.py` | 374 / 885 | 逻辑密度高（tokenize 解析、中断延迟语义），改动需配 tests |

**入口建议**：第一周只读 `basic/rmsnorm.py` 与 `basic/fp16_bf16_gemm.py` 并跑 `python -m tirx_kernels.test --kernel rmsnorm`（需 GPU），热点文件留到熟悉 DSL 与流水线协议之后。

**靠近热点的安全路径**：热点并非禁区，而是"有前置功课的进阶区"。推荐顺序：先读该 kernel 对应的 `.agents/sketch/*.md` 设计草图（它记录了 WASP 管线、warp 分工与存储规划，相当于带注释的地图），再读同目录 `spec.py`/`data.py` 理解配置域与数据形状，最后才进 `kernel.py` 主体；改任何性能敏感代码（发射指令、谓词、寄存器生命周期、流水线深度）之前，按 `AGENTS.md` 的仓库级指令先调用 `$tirx-codegen-diagnostics` 技能查症状索引的 field notes。另外两个纪律：改 `kern/` 下任何文件先跑 `tests/test_kern_api.py` 与 `tests/test_low_level_ir.py`（106 个下游文件会被波及）；跑基准只信 `bench_suite` 的钉版门禁结果，不要拿手写的单次计时下结论。

---

## 8. 与 MLC/TVM 生态的关系

- **TIRx 与 TVM**：TIRx 是 Apache TVM 的 TIR（TensorIR）路线的延伸编译栈（README 直接链接 apache/tvm）。传统 TVM 用 schedule 原语从高层算子自动调度（te/tir 的变换式调优），生成代码的可控性受调度空间限制；TIRx-kernels 反其道——**直接在 PTX 级 TIR 上手写 kernel**（Kern DSL 的 `K.ptx`/`K.cuda` 直拼底层指令，smem 地址、mbarrier、warp 角色全部显式声明），再经 TIRx pipeline 下降到 PTX/CUBIN。它享用了 TVM 的 IR 基础设施（PrimFunc/IRModule/StmtExprVisitor/源码 Span），但把"调优"换成了"受契约约束的手写"：low_level_ir 校验器刻意收窄可用 IR 面（禁 tile 原语、禁直接 scope 访问），换取下降结果的完全可控——这是手写性能与编译器可分析性之间的折中设计。
- **与 MLC-LLM**：TIRx-kernels 属于 mlc-ai 组织，定位是给 MLC 生态（含 MLC-LLM 推理引擎）提供高性能算子层——把 FlashInfer/cuDNN/DeepGEMM 等散落上游收编为统一 TIR 表示的可注册算子，供上层引擎按注册名调度。收编对象的选择也说明其服务前沿 LLM 推理负载的定位：Kimi K3 prefill（KDA agent-evolved kernel，B200 实测 2.27x–2.97x）、DeepSeek 系 MoE/FP8 GEMM、FlashMLA 稀疏 MLA、GDN/mamba 线性注意力 decode 全景。
- **正确性哲学**：移植 kernel 不信任"看起来等价"，而是用 `reference-dependencies.json` 锁定的上游源码作为参考对照、registry/runner 统一驱动、bench_suite 钉版基线守护性能——外部参考实现再快也只做诊断、永不进入判定，判定只看 TIRx 自身实现的 before/after 墙钟比。这套"锁 → 对照 → 门禁"链路本身就是它作为 MLC 生态底座的工程价值。

---

*指南完。建议下一步：按 §5 阶段 A 开跑，遇到 DSL 疑问优先查 `kern/README.md` 与 `.agents/skills/tirx-codegen-diagnostics/` 的 field notes。*
