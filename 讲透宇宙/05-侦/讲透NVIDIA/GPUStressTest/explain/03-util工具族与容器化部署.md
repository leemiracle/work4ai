# 03 · util 工具族与容器化部署

## 角色定位

本篇覆盖两翼：左翼是 util/ 的 GPU 侧工具族——矩阵数据生成（fill_matrix.h + fillMatrixDevice_kernel.h）、host-device 同步（test_util）、性能测量（measure.cc）；右翼是 Docker/ 部署面——三镜像、依赖收集与多机多卡编排。前者给 gst 供数据与计时，后者把 gst 变成可铺整机架的 wgst。

## 内部结构

**fill_matrix.h**：`bufferBatchVariant`（util/fill_matrix.h:46-65）以 union 统一 strided/指针数组两种批量缓冲，`batch_ptr`（:67-79）取第 i 批首址；API `fillMatrixDevice`（:108-120）转发给 impl::helper。

**fillMatrixDevice_kernel.h**：pseudorandom generator 整数版用 (lda*row+col+seed)%MAX 确定性算术（:60-82），浮点版按 quant_params 归一化（:96-121，FP8 有专属特化 :90-94）；normal 版持 curandStateMRG32k3a（:132-156）。__global__ kernel（:160-210）每线程按 gridDim*blockDim 步长跨条带写整 buffer，支持三角填充/fillNaN 越界涂 NaN；启动器（:212-245）取 multiProcessorCount*4 grid、warpSize*4 block，按 'r'/'P' 选 generator。

**test_util**：`wait_kernel_impl`（util/test_util.cu:45-55）单线程自旋，上限 10 秒防死锁；`wait_kernel`（:57）<<<1,1>>> 发射；`wait_kernel_set_semaphore`（util/test_util.h:91-93）volatile 写 pinned 计数器，`gpuAllocPinnedAndMap`（:95-102）零拷贝映射——合成 host-device 计数握手。

**measure.cc**：`cublasPrintPerf`（util/measure.cc:49-111）统一 "^^^^ CUDA : elapsed/Gflops" 输出（:101-104）；`coefGemmSOL`（:114-191）按类型×架构给相对 sgemm 倍率；`printGemmSOL`（:213-267）已无调用方且 assert（:242）只认 SM≤8。

**Docker/**：Dockerfile_0 COPY gst+自备 libcublasLt/libcudart/libcuda 设 LD_LIBRARY_PATH（Docker/Dockerfile_0:3-17）；Dockerfile_1 换 run.sh 入口；Dockerfile_nodriver_0（wgst 版）ldconfig 后 ENTRYPOINT /nvidia/run.sh（Docker/Dockerfile_nodriver_0:8-9）。populate_software.sh 收集三库（libcuda.so.1 拷两遍，Docker/populate_software.sh:3-4）；入口 run.sh 以 `-T=$loop` 启动（Docker/software/run.sh:8）。

## 外部连接

fillMatrixDevice 被 test_engine 与 lt_gemm 的 Bias 填充调用（main.cu:774-827/:524）；wait_kernel 握手只被 calc_matmul_perf_time 用（main.cu:277-303）；cublasPrintPerf 由 lt_gemm 报告（main.cu:633）。build_nodriver_0.sh 打 nvcr.io/nvidian/wgst:1.1；Docker/k8s/wgst.yaml 以 privileged Pod 申请 1 块 GPU（:10-15）。

## 数据流

生成：host 调 fillMatrixDevice → launcher 查设备属性 → kernel 条带写可复现伪随机值。计时：host set 计数器 n → GPU 自旋到 n → cudaEvent 计一轮 → set n+1 隔离。部署：populate_software.sh → build_*.sh → docker run --gpus device=N（Docker/run.sh:1）→ run.sh → wgst -T。

## 设计决策

1. **确定性伪随机优先**：验收数据可复现比统计性质重要，curand 只在 'r' 模式保留。
2. **越界涂 NaN**：fillNaN 把矩阵外区域写 NaN，让未初始化读在后续计算里显形。
3. **容器自带用户态驱动库**：libcuda.so.1 打进镜像，宿主只需内核态驱动+设备节点。
4. **rank=GPU 绑定**：wgst_mpirun_rank_cpu.sh 校验 OMPI rank 后绑同号卡（Docker/wgst_mpirun_rank_cpu.sh:8-18），一 rank 一卡铺满多机。

## 新人提示

排查"压不满显存"先看 fillMatrixDevice 是否走 'P' 且 fillNaN=true。解析 gst 输出别用 parse_memory_targets.bash——其期望的 /FINAL/ 标记当前代码不打印（util/parse_memory_targets.bash:19 对 main.cu:1317/1330 解析失败，`$8i` 亦笔误），需自己从 "Allocate matrixSize" 行抓字节数。wgst_all_gpu.sh:13 与 wgst_mpirun_rank_cpu.sh:22 的 `$dev` 未定义。数据证据在 data/：功耗爬坡与 8×A100 全程日志（"RETURN TEST" 属旧代二进制）。
