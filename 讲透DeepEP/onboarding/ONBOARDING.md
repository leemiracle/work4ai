# DeepEP 新人指南（ONBOARDING）

> 基于 knowledge-graph（9 层/11 步导览）与 README。

## ① 项目是什么与定位

DeepEP 是 DeepSeek 开源的高性能通信库，聚焦 MoE 专家并行（EP）：提供高吞吐/低延迟 all-to-all 内核——dispatch 把 token 发往专家所在 rank、combine 加权归约回原 rank，原生 FP8；另有实验性 Engram（RDMA 远程访存）/PP/CP 原语，零/极小 SM 占用。

V2 三大换血：全 JIT（装包只编宿主，CUDA 运行时编译）；后端 NVSHMEM→NCCL Gin（header-only）；高吞吐/低延迟统一进 ElasticBuffer，SM/QP 解析式计算免调优，V3 式训练 SM 从 24 降至 4-6 而峰值 1.3×，支持 EP2048。注意：V2 缓冲占用更大，0-SM RDMA 低延迟 EP 不再支持。

定位：解决 MoE 通信"吃 SM、难调优"，极少 SM 打满 NVLink/RDMA 带宽。

## ② 架构分层（按图谱 layers）

- **L1 Python API**：deep_ep 门面（init_jit）、buffers 双世代（elastic V2/legacy V1）、utils 工具集。
- **L2 Elastic 宿主运行时（V2 核心）**：csrc/elastic/buffer.hpp 编排 + kernels/elastic 五组 JIT 运行时（dispatch/combine/engram/pp/barrier）。
- **L3 JIT 编译设施**：Compiler、IncludeParser（依赖哈希缓存失效）、KernelRuntimeCache。
- **L4 通信后端与对称内存**：NCCL Gin（V2 默认）/NVSHMEM（V1）/CUDA driver；symmetric.hpp 五类对称句柄。
- **L5 JIT 设备内核模板**：deep_ep/include——common（comm/layout/ptx）+ impls 11 个模板。
- **L6 V1 Legacy**：NVSHMEM 预编译旧路径（intranode/internode/internode_ll/layout）。
- **L7 测试套件**：elastic 五件（ep/agrs/barrier/engram/pp）+ legacy 三件。
- **L8 构建与 CI**：pyproject（JIT 只编宿主）与 CMake（仅调试）双轨 + format.sh 门禁。
- **L9 文档工件**：README（V2）、docs/legacy.md（V1 手册）、docs/nvshmem.md。

## ③ 核心模块

- **ElasticBuffer**（csrc/elastic/buffer.hpp）：V2 宿主大脑。dispatch 485 行（布局/FP8 分支/hybrid-direct 选择）；combine 还原顺序；engram_fetch 远程拉取；all_gather（AGRS）。
- **JIT 子系统**（csrc/jit）：改 .cuh 经依赖哈希触发重编译（缓存在 ~/.deep_ep）；handle.hpp 三件套类型安全启动。
- **五组运行时**：fmt 渲染模板参数成源码交 Compiler。
- **impls 家族**：dispatch/combine 的 direct 与 hybrid（NVLink 域内+RDMA 跨域）变体、epilogue、engram、pp_send_recv。
- **公共库三件**：comm.cuh 设备侧对称内存 API、layout.cuh 布局真理来源、ptx.cuh 458 行内联 PTX（TMA/mbarrier/atomic）。
- **后端抽象**：NCCLSymmetricMemoryContext 持 ncclComm 与注册窗口；symmetric.hpp 编译期切换 Gin/NVSHMEM。

## ④ 快速上手（摘自 README）

**环境**：SM90 或支持其 PTX ISA；Python≥3.8、CUDA≥12.3、PyTorch≥2.10、NCCL≥2.30.4；节点内 NVLink、节点间 RDMA。

**依赖**：`pip install "nvidia-nccl-cu13>=2.30.4" --no-deps`；legacy 路径另需 NVSHMEM（docs/nvshmem.md）。

**开发与安装**：python setup.py build 后为 SO 建软链；按集群改 tests/utils/envs.py 的 init_dist，多节点跑 tests/elastic/test_ep.py（另有 agrs/engram/pp）；正式安装 setup.py install，import deep_ep 即用。

**使用范式**：以 MoE 配置构造 ElasticBuffer，get_theoretical_num_sms 取 SM 数；dispatch/combine 支持 async_with_compute_stream + EventOverlap 重叠；反向对偶（dispatch 反向即 combine）；decode 可缓存 EPHandle 免 CPU 同步。环境变量见 README。

## ⑤ 学习路径（按 11 步导览串讲）

1. 总览：README+`__init__.py`+setup.py，弄清 V2/V1 分野。2. Python 门面：两个 Buffer 与 init_jit 时序。3. JIT 流水线：理解改头文件为何触发重编译。4. 内核运行时：KernelRuntime + handle.hpp 泛型启动。5. V2 心脏：buffer.hpp 走通 dispatch 宿主全路径。6. 运行时工厂：五组运行时拼装源码。7. impls：direct/hybrid 两级流水的域划分。8. 公共库三件：改布局常量的波及面。9. 后端：对称内存注册与物理/逻辑域划分。10. V1 legacy：对照旧形态、固定槽低延迟的由来。11. 质量闭环：测试分层、format.sh --check、双构建分工。

节奏：1-2 天走 1-2 步建地图，一周精读 3-6 步主线；改 .cuh 后首跑重编属预期。
