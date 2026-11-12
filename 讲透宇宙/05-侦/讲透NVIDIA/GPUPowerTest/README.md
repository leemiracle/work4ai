# 讲透 GPUPowerTest

NVIDIA [GPUPowerTest](https://github.com/NVIDIA/GPUPowerTest)——GPU 功率循环压测工具 gpt（衍生自 CUDA samples）：OpenMPI 多 GPU（MPI rank↔GPU 一一对应，mpirun -np N -H 多机铺开），burn.cu 用 cublasLt 大/小矩阵交替 GEMM 制造功率方波（up 相位 8000×8000、down 相位 1000×1000 或 -L 时 10×10），叠加 CPU 自旋（-c）与随机功率跌落（-D）模拟整机供电毛刺；nvlbm.cu 是独立的 NVLink 带宽负载生成器。功耗监测走 DCGM（dcgmi dmon -e 100,155,1002,1011,1012），全仓零 NVML 引用。

## 全链状态表

| 阶段 | 状态 | 明细 |
|---|---|---|
| DeepWiki | ✗ 未收录 | 后台未索引（收录决定权钉版），**本图谱为唯一知识源** |
| understand 图谱 | ✅ | 33 节点 / 32 边 / 6 层 / 12 步 tour，validator 0 issues |
| fingerprints | ✅ | 20 文件基线 @a9534be4 |
| onboarding | ✅ | [ONBOARDING.md](onboarding/ONBOARDING.md) 4999 字（不计空格）8 节 70 锚 |
| explain | ✅ | 2 篇（均 2497 字不计空格，42/44 锚，合计 156 去重锚界内 0 坏）：[01 功耗方波引擎](explain/01-burn-cu-功率方波引擎.md) / [02 MPI 启动与 NVLink 负载](explain/02-gpt-nvlbm-mpi启动与NVLink负载.md) |

图谱位置：仓内 `.understand-anything/knowledge-graph.json`。

## 结构速览

- `gpt.c`（224 行）纯 C 的 MPI 启动器：七参数 CLI（-u/-d/-t/-c/-i/-L/-D）、sig_usr1 信号退出协议、launch_kernel 经 extern "C" 调 burn
- `burn.cu`（633 行）方波引擎：BurnGPU 类三组 up/dn 矩阵 + Drop 内嵌类（6 秒窗口随机掉载）+ core_spin CPU 自旋 + operator()() 无限方波循环（MPI_Barrier 相位同步）
- `nvlbm.cu` NVLink 带宽/功耗负载：nvl_load 循环 cudaMemcpy 打满互连，走 bld_nvlbm.sh 独立 nvcc 编译（不在 CMake 内——双轨构建）
- `examples/` MPI 教学示例族（Send/Recv+Barrier，5 份草稿变体 c_0..c_4 + 2 份 ELF 二进制直接入库）

## 甄别精选（详见 onboarding §7，全部行号实证）

1. **README:73/75 与代码不符**：README 说 nvlbm 唯一选项是 `-t`，nvlbm.cu:142 实际解析 `-d`——按 README 跑 `nvlbm -t 300` 直接打印 Usage 退出
2. **Drop 时长伪随机**：`drop_delay_sec=(ms/1000)%4`、0 提升为 1（burn.cu:181-182），实际取值 1-3 秒且由窗口起始秒数决定——真正随机的只有「掉不掉」与「何时掉」，与 README 宣传 "1 - 4 sec" 有出入
3. **As_dn/Bs_dn/Cs_dn 三元表达式陷阱**（burn.cu:123-125）：`SEED_DN_LOW : SEED_DN_HOT * (...)` 优先级下 low 模式 cudaMalloc 仅 10 元素（40 字节），layout 却按 10×10=100 元素 → cublasLt 越界读隐患
4. burn.cu L314/L325 Adesc_dn 被创建两次（复制粘贴 bug，句柄泄漏其一）
5. nvlbm.cu:188-192 pthread_join 缩进陷阱：错误检查 if 在 for 循环外，只覆盖最后一次 join
6. nvlbm.cu MAX_GPUS=8 溢出边界：每对 GPU 2 线程，8 卡恰好满格，10+ 卡写越界 tids
7. sigaction union 巧合（gpt.c:193-194）：单参 sig_usr1 赋给 sa_sigaction 但 sa_flags=0，按 sa_handler 语义调用，能工作靠 union 布局
8. gpt.c L175-180 悬空 else：up+down>load_time 校验仅无参数时生效；MPI 模式下 -i 被忽略（GPU 号由 OMPI_COMM_WORLD_LOCAL_RANK 决定）
9. burn() new BurnGPU 无 delete；operator()() catch 吞异常不重抛；主循环唯一退出=跨文件 SIGUSR1 杀线程（异步信号安全靠约定）
10. CMakeLists 被 scanner 误判 docs/txt 已纠正 config；examples/ 两份 ELF 二进制与 5 份教程草稿（c_1=定稿前身）直接入库

## 工艺备注

- importMap 全空（0 边）经逐文件重扫确证：全仓 17 源文件引号 include 为 0（真实为 0，非漏扫）；gpt.c↔burn.cu 耦合用 calls+depends_on 边表达
- .cu 文件 tree-sitter 零提取（BurnGPU/Drop/core_spin/operator()/burn 及 nvlbm 全部函数人工源码补齐）；examples 的 c_0..c_4 伪语言按 C 定性建节点
