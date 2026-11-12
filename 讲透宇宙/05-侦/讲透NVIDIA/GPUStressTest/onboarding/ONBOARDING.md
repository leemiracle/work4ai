# GPUStressTest（gst/wgst）Onboarding 指南

> commit c7c1562｜图谱 105n/163e/8 层。锚均经源码核实（2026-11-07）。

## 一、项目定位：五项压测 + PASS/FAIL + 挂起检测

gst 是 NVIDIA 应微软请求、由内部 cublasMatmulBench 改造的 **GPU 验收测试工具**（main.cu:43-46）：把每块 GPU 拉到满功率、满 TFLOPS、满显存，逐项报 PASS/FAIL，失败 `exit(-1)`（main.cu:50）；正确性只看"没异常、没挂死"。

骨架：枚举设备 → 按 GPU 型号名挑 12 套预置套件之一 → 每卡跑 5 项 GEMM 压测（`NUM_TESTS=5`，util/GST.h:83），巨型矩阵显存占比 0.90-0.95（README 基线表），INT8/FP16/TF32/FP64/FP32 轮番打到 cublasLt；watchdog 以 600 秒门限（util/GST.h:84）检测挂死。`data/` 存 nvidia-smi 功耗采样与 8×A100 实跑日志；容器版 wgst 可铺 docker/mpirun/k8s。

## 二、技术栈

- **CUDA Runtime + cuBLASLt**：压测全走 `cublasLtMatmul`（main.cu:295）；workspace SM90 用 32MB、其余 4MB（main.cu:476-477）。
- **POSIX 线程/信号量**：watchdog 走 pthread+三信号量（main.cu:1004/114）；Windows 靠 vcpkg 装 pthread（vcpkg.json:3 唯一依赖）。
- **C++14 模板**：test_engine/lt_gemm 等为六类型参数模板，运行时枚举→编译期类型靠 TEST_ENGINE_MAPPING 宏（main.cu:885-896）。构建三轨：Linux CMake / MSVC VS2022+CUDA 12.6（gst.vcxproj:187）/ Windows GNU 未完成。

## 三、模块地图（按图谱 8 层）

- **L01 许可与数据**：OSS_License/l4source（MIT）+ data/ 实测日志。
- **L02 原子工具**：type_convert.h（cuGet/cuMakeNaN）、memory.h（allocate/free util/memory.h:62-73）、exceptions.h、common_header.h（BlasOpts util/common_header.h:84-125）、common.h（CHECK 宏）。
- **L03 生成与同步**：fill_matrix.h（fillMatrixDevice 入口）、fillMatrixDevice_kernel.h、test_util.h/.cu（wait_kernel）、measure.cc（util/measure.cc:49-111）。
- **L04 参数与套件**：command_line.h、test_args.cu（13 种 -P 组合宏表）、GST.h、device_info.cu。
- **L05 主程序**：main.cu 1374 行——watchdog(119)/calc_matmul_perf_time(195)/auto_tuning(361)/lt_gemm(455)/test_engine(671)/test_cublasLt(899)/main(988)。
- **L06 结果解析**：parse_memory_targets.bash（awk 算显存占比判 good）。
- **L07 容器化**：三 Dockerfile + build 脚本链 + 多卡脚本 + k8s/wgst.yaml。
- **L08 构建与文档**：CMakeLists.txt、vcpkg 双 json、VS 工程三件套、README.md。

## 四、控制流：main → watchdog 握手 → GST 循环 → lt_gemm

`main`（main.cu:988）sem_init 三信号量、起 watchdog（1004），枚举设备并做**各卡显存一致性检查**，不一致退出（1057-1062）；按 GPU 名 if-chain 构造 GST 套件（1091-1164）。

**watchdog 协议**（main.cu:108-114）：wd=测试开始、go=跑下一项、done=测试完成。循环 `sem_wait(&wd)` → `sem_timedwait(&done, now+600s)`（main.cu:143）→ 超时且 test_state==1 判 hung（144-149）；`GST_WATCHDOG_TIMEOUT_SEC` 可覆盖（123-125）。

每项测试：parse P_arg（1194）→ reset 只留 -T（1203，缺省 10）→ **main.cu:1206-1302 if-chain 再硬映射一遍类型** → sem_post(&wd)（1325）→ test_cublasLt（1329）按 math_type 六分支实例化 test_engine：校验 ld、allocate A/B/C(/D)（763-768）、fillMatrixDevice 填充、调 lt_gemm（844-850）→ 配 Layout（IMMA 强制 COL32 系+NT/TN，test_cublasLt:952-963）→ 可选 auto_tuning（8 候选×5 次中位）→ calc_matmul_perf_time 计时（277-303）→ cublasPrintPerf 报 Gflops（633）。

## 五、构建与部署

**CMake**：`cmake -DDEBUG_MATRIX_SIZES:BOOL="ON"` 进尺寸调优（CMakeLists.txt:81-84）；SM 表 70/75/80/90 经 CUDA_ARCHITECTURES 生效（:103）。**MSVC**：vcpkg 装 pthread；**Debug|x64 预定义 DEBUG_MATRIX_SIZES**（gst.vcxproj:114）——Debug 默认"只调尺寸"，Release 才真压测；include 硬编码开发机路径（:126）。

**Docker 三镜像**：Dockerfile_0（gst+自备 cublasLt/cudart/libcuda）、Dockerfile_1（切 run.sh 入口）、Dockerfile_nodriver_0（wgst+ldconfig → nvcr.io/nvidian/wgst:1.1）。多卡两路：wgst_all_gpu.sh（每卡一容器）/ mpirun+wgst_mpirun_rank_cpu.sh（OMPI rank 绑同号 GPU）；k8s 清单以 privileged Pod 申请 1 块 GPU。

## 六、设计决策

1. **12 型号映射同参**：复用只在构造 switch——T4/P100/V100_16 共用 init_t4（util/GST.h:113-117）、H100 复用 init_a100_80（:121-124）、M60 复用 init_generic（:137-140）；显存档位而非微架构决定尺寸。
2. **600 秒门限**：util/GST.h:84 硬编码（README.md:38、main.cu:49 同值）；环境变量覆盖为长循环留口。
3. **DEBUG_MATRIX_SIZES**（README.md:66-74）：main.cu:1071-1089 把真实 GPU 名换成 13 项列表逐套件跑（1077 列表比枚举多一项）；但该宏**不豁免**分配计算——小卡跑大显存套件仍会分配失败退出。
4. **A100 Benchmark Guide 倍数策略**：util/GST.h:146-149 注释钉版，init_* 巨型维度按其倍数取值（如 :184-187）以同时压满算力与显存。
5. **伪随机可复现**：GST 用 'P' 确定性模式（fillMatrixDevice_kernel.h:60-121，FP8 有专属特化）；curand normal 保留但不用——验收要可复现。
6. **GPU 侧计时握手**：wait_kernel 自旋监控 pinned 计数器（util/test_util.cu:45-57，10 秒上限防死锁）。

## 七、已知坑与勘误（行号已复核）

1. **VS 幽灵条目**：gst.vcxproj:37 与 gst.vcxproj.filters:21 引用不存在的 gpu_stress.h；gst.vcxproj:48 引用不存在的 packages.config。
2. **README 代差**：README.md:99/:119 的 H200 FP8 行无代码支撑——init_h200（util/GST.h:393-445）五项无 FP8。
3. **解析脚本标记代差**：parse_memory_targets.bash:19 期望 `/FINAL/` 行取 A/B/C 元素数，当前 main.cu 从不打印 FINAL（1317/1330 标记行均无；字节数只在 757 Allocate 行给总数）；`$8i` 亦笔误。data/WGST_full_run_A100 的 "RETURN TEST"/"TEST n DONE" 属旧代二进制——三方标记互不匹配，脚本对当前输出只得 ratio 0。
4. **类型映射两处维护**：main.cu:1206-1302 if-chain 与 test_args.cu:132-175 宏表是同一映射的两份拷贝。
5. **脚本/构建卫生**：wgst_all_gpu.sh:13（wgst_mpirun_rank_cpu.sh:22 同）echo 未定义 `$dev`；CMakeLists.txt:4 硬编码 /home/josephw 路径且无消费者；populate_software.sh:3-4 重复拷 libcuda.so.1 两次。
6. **PASS 路径跳过 watchdog 握手（本轮复核新发现）**：main.cu:1344 `continue` 位于 1334 else 块内，PASS 后直达下一循环，跳过 1356 sem_post(&done)、1359 sem_wait(&go) 与 1347 test_state 复位——超 600 秒的健康长跑会被误判 hung 并连带报 FAILED（归档日志全 PASS=旧代握手完整）。
7. **死代码**：init_v100_16（util/GST.h:233-283）与 printGemmSOL（util/measure.cc:213-267）均无调用方；后者 assert（:242）只认 SM≤8。
8. **CMake 拼写坑**：CMakeLists.txt:33-34 foreach 迭代未定义的 `${SMS_LIST}`（实为 SM_LIST）→ -gencode 循环死路，靠 :103 兜底；:17 消息说 Debug 实设 Release；util/common_header.h:77 `DEFAULT_1024=2048` 名不副实。
9. **图谱勘误**：scanner 只捕获 10 条 util 头间 imports；main.cu:53-61 等 .cu 引号 include 共 15 条已补扫。

## 八、新人上手路径
1. **读**：README.md → main.cu:43-51 头注释 → util/GST.h:44-76（套件参数全表）。
2. **建**：Linux `cmake .. && make`，验尺寸加 `-DDEBUG_MATRIX_SIZES:BOOL="ON"`；Windows VS2022+vcpkg（Debug|x64 已预定义该宏）。
3. **跑**：`./gst -T=1` 快验；`-T=10` 压功耗；`-dv=N` 选卡（main.cu:1028 边界 `>` 应为 `>=`）。
4. **扩型号**：GST.h 枚举加值+init_xxx+main.cu:1091 加分支；集群从 mpirun 起步。
5. **代码阅读序**：watchdog → main 套件选择 → test_cublasLt 分发 → test_engine → lt_gemm → calc_matmul_perf_time → fill/wait 内核；动手前先过坑清单。
