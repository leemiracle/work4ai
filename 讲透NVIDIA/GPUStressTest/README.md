# 讲透 GPUStressTest

NVIDIA [GPUStressTest](https://github.com/NVIDIA/GPUStressTest)——GPU 压力测试工具 gst：每次调用选第一块可见 GPU 循环跑五项 BLAS 压测（-T=n 次，PASS/FAIL 判定），watchdog 线程 600 秒挂起检测，支持 Ubuntu/WSL、Windows MSVC/MinGW 双工具链与 Docker/k8s/mpirun 集群部署。

## 全链状态表

| 阶段 | 状态 | 明细 |
|---|---|---|
| DeepWiki | ✗ 未收录 | 后台未索引（收录决定权钉版），**本图谱为唯一知识源** |
| understand 图谱 | ✅ | 105 节点 / 163 边 / 8 层 / 13 步 tour，validator 0 issues |
| fingerprints | ✅ | 41 文件基线 @c7c15627 |
| onboarding | ✅ | [ONBOARDING.md](onboarding/ONBOARDING.md) 4990 字（不计空格）8 节 44 锚 |
| explain | ✅ | 3 篇（2472/2433/2479 字，12/15/14 锚，84 长式锚界内 0 坏）：[01 watchdog 主流程](explain/01-main-cu-watchdog与测试主流程.md) / [02 GST 与参数解析](explain/02-GST-h与参数解析层.md) / [03 util 工具族与容器化](explain/03-util工具族与容器化部署.md) |

图谱位置：仓内 `.understand-anything/knowledge-graph.json`。

## 结构速览

- `main.cu`（1374 行）单文件主体：main→watchdog 线程→GST 套件循环→test_engine→lt_gemm（cublasLt）
- `util/` 两级工具：原子层（type_convert/memory/exceptions/common_header）+ 生成解析层（fillMatrixDevice 内核族、CommandLine、test_args 十种 -P 精度、GST.h 12 型号套件、measure SOL）
- `Docker/` 三 Dockerfile（含 nodriver 变体）+populate_software 驱动注入+mpirun 多机脚本+k8s 清单
- data/ 两份实跑证据（nvidia-smi 采样 + 8xA100 全程日志）

## 甄别精选（详见 onboarding §7，全部行号实证）

1. **PASS 路径跳过 watchdog 握手（最重要）**：main.cu:1344 的 `continue` 在 1334 else 块内，PASS 后直达下一循环、跳过 1356 sem_post(&done)/1359 sem_wait(&go) 与 test_state 复位——总时长超 600 秒的健康长跑会被 watchdog 误判 hung 并连带后续 PASS 报 FAILED；归档日志全程 PASS 证明旧代二进制握手完整，属后来引入的回归
2. **标记三方互不吻合**：parse_memory_targets.bash 盼 /FINAL/，当前 main.cu 只打 "STARTING TEST"（:1317），"RETURN TEST" 只存在于旧代日志 data/WGST_full_run_A100——脚本/当前码/旧日志三方标记各不相同
3. init_v100_16（GST.h:233-283）死代码：构造函数把 V100_16 映到 init_t4
4. CMakeLists.txt:33-34 foreach 迭代未定义的 `${SMS_LIST}`（实为 SM_LIST）→ -gencode 循环从不执行，靠 :103 CUDA_ARCHITECTURES 兜底；:17 消息说 Debug 实设 Release
5. gst.vcxproj.filters 引用不存在的 util\gpu_stress.h 与 packages.config（幽灵条目）
6. README 基线表含 H200 FP8 行但 init_h200() 五项无 FP8（文档与代码代差）
7. 杂项：printGemmSOL 无调用方且 assert 只认 SM≤8；DEFAULT_1024=2048 名不副实（common_header.h:77）；-dv 边界 `>` 应为 `>=`（main.cu:1028）；DEBUG_MATRIX_SIZES 的 13 项名字列表比 12 值枚举多一个；wgst_all_gpu.sh 引用未定义 $dev；CMakeLists 硬编码开发者路径；populate_software.sh libcuda.so.1 重复拷贝两次
8. scanner 只捕获 10 条 imports（util 头间），main.cu→10 个 util 头等 15 条 .cu 引号 include 已补扫（Makefile/vcxproj include 路径解析坐实）

## 工艺备注

- batch-5 因 61 节点>60 拆 2 part（规范分片）
- 全部 .cu 文件 tree-sitter 零提取（main.cu 8 函数、test_args 8、test_util 2、device_info 1 人工源码补齐）
