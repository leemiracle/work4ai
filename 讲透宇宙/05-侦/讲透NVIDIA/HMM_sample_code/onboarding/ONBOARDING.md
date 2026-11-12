# HMM_sample_code ONBOARDING —— CUDA 12.2 异构内存管理演示仓

仓：`NVIDIA/HMM_sample_code` @ a6a749a · 12 实文件 · 图谱 21 节点/24 边/5 层/10 步 tour

## 1. 项目定位

**HMM 语义钉版**：本仓 HMM = **Heterogeneous Memory Management（异构内存管理）**，不是 Hidden Markov Model。`README.md:1` 标题 "CUDA 12.2 Heterogeneous Memory Management (HMM) demos" 实证；全仓无前向/后向算法与概率模型，只有"GPU 直接访问 CPU 内存"一个主题。

NVIDIA 博客 *Simplifying GPU Application Development with HMM* 配套示例仓（`README.md:4`；链接是占位符，`README.md:25`）。核心命题：CUDA 12.2 起，在 ATS 使能系统上，GPU 能直接访问 CPU 侧 malloc 堆、线程栈、mmap 文件页，无需 cudaMalloc/cudaMemcpy。

**硬件门槛（跑前必查，`README.md:7-13`）**：需 ATS 或 HMM 使能系统（典型如 Grace Hopper、POWER9/10、带 ATS 的 x86）：

```shell
nvidia-smi -q | grep Addressing   # 期望: Addressing Mode : HMM
```

不满足时 src/ 三个带 `-gpu=nomanaged` 的 demo 与 miniapp 都跑不通（见 §6）。

## 2. 技术栈

- **C++20**：`std::execution::par` 作 GPU offload 载体、`std::span`/`std::views::iota`（src/file_before.cpp:46、src/ticket_lock.cpp:63）、`std::jthread`、`std::atomic`。
- **nvc++ -stdpar=gpu**：把标准并行算法编译成 CUDA kernel；`-gpu=nomanaged`（src/atomic_flag.cpp:3）关掉托管内存兜底，逼 demo 只靠 HMM 硬件跑。
- **CUDA C++ + cub**：miniapp 走传统 nvcc 路线（miniapp/Makefile:1），归约用 `cub::DeviceReduce::Sum`（weather_app.cu:239-242），gencode 三套 sm_80/sm_90/compute_90（miniapp/Makefile:6-8）。
- **nvhpc:23.5 容器**：`ci/run:4` 引 `nvcr.io/nvidia/nvhpc:23.5-devel-cuda12.1-ubuntu22.04`，免装工具链。

## 3. 模块地图（图谱 5 层）

| 层 | 内容 | 代表文件 |
|---|---|---|
| L01 文档与 CI 入口 | README 总览；ci/run 容器一键；ci/demos 编排 | `README.md`、`ci/run`、`ci/demos` |
| L02 并发原子演示 | CPU-GPU 原子通信、混合互斥排队锁 | `src/atomic_flag.cpp`、`src/ticket_lock.cpp` |
| L03 文件访问对比 | fread+sort vs mmap+sort 的 before/after | `src/file_before.cpp`、`src/file_after.cpp` |
| L04 ERA5 数据准备 | 40 年降水 nc→bin 预转换与说明 | `miniapp/era5_preicp_nc_to_bin.py`、`miniapp/README.md` |
| L05 miniapp 主程序 | 2MB 对齐 MAP_FIXED + cub 归约零拷贝 | `miniapp/weather_app.cu`、`miniapp/Makefile` |

依赖主干 ci/run→ci/demos→src 四 demo；quoted include=0，四 demo 独立成篇。

## 4. 核心数据流

**miniapp 主链路（1.3TB 零拷贝）**：ERA5 逐月 .nc（CDS 下载；721x1440 网格、40 年 480 文件≈1.3TB，`miniapp/README.md:5`）→ python(netCDF4+numpy) 转裸 float .bin（`e5.accumulated_tp_1h.YYYYMM.bin`，era5_preicp_nc_to_bin.py:39-41）→ weather_app 先 `mmap(PROT_NONE)` 预留大段 VA（weather_app.cu:147），再按 2MB 对齐步长逐月 `MAP_FIXED` 映射连续地址（weather_app.cu:174）→ 映射基址直接当 kernel 入参（weather_app.cu:207-208），366x24x721x1440≈91.2 亿线程跨年累加 → cub 归约临时存储用普通 `malloc` 直供 GPU（weather_app.cu:241，行尾注释 `// use HMM B-)`）→ 输出 `processed_log.csv` 与 `yearly_aggregates.bin`（weather_app.cu:222,271-272）。

**src/ 四 demo before/after**：atomic_flag——GPU 写 `message=42`+`flag.store(1)`（src/atomic_flag.cpp:42-44），CPU 自旋读同一内存（:49-52）；ticket_lock——64 CPU jthread+4096 GPU 线程抢同一把票据锁，校验 `message==4160`（src/ticket_lock.cpp:81）；file_before——`fread` 整读进 vector 再 GPU 排（src/file_before.cpp:44-45）；file_after——`mmap` 后 GPU 直排在映射页上（src/file_after.cpp:44,49）。

## 5. 构建与运行

- **一键**：`./ci/run`（`README.md:18`）= docker `--gpus=all` 挂仓库跑 `./ci/demos`（ci/run:5-11）；后者进 src/ 依次 bash 四个 .cpp（ci/demos:5-9）——polyglot 机制见 §6。
- **手动**：`nvc++ -std=c++20 -stdpar=gpu -gpu=nomanaged -o demo demo.cpp`（file_before 故意省该 flag，见 §6）。
- **miniapp**：`cd miniapp && make && ./weather_app 1981 2020 /PATH_TO_BINARY/`（参数见 `miniapp/README.md:11`；目录必须以 `/` 结尾——weather_app.cu:157 是裸字符串拼接）。

## 6. 设计决策

1. **2MB 对齐不是洁癖**：月文件最大 ≈3.09GB，向上取整到 2MB 倍数（weather_app.cu:135-137）：① `MAP_FIXED` 要求对齐，统一步长让 480 文件等距排布，kernel 一个乘法定位任意年月（weather_app.cu:99）；② 注释 "probably need 2 MB pages for perf"（weather_app.cu:172）——大页降 TLB 压力。
2. **polyglot `#if 0`**：.cpp 首行 `#if 0`（src/atomic_flag.cpp:1）对 bash 是注释、对预处理器是条件开关，`bash xxx.cpp` 即触发内嵌 `nvc++ ... $0` 自编译自运行（:3-5），demo 零构建系统。
3. **`-gpu=nomanaged` 的有无是叙事**：默认 stdpar 堆走 managed memory；带该 flag 的三个 demo 关掉兜底，栈/malloc/mmap 全靠 HMM 硬件直访——这正是演示对象。file_before **故意不带**（src/file_before.cpp:3）：vector 走 managed，是"HMM 之前"的旧姿势。
4. **零拷贝直连 vs fread**：file_after 排序直接发生在 CPU 页缓存的文件页上（src/file_after.cpp:44,49），省掉整读一步；miniapp 放大到 1.3TB——GPU 按需缺页取数，单文件不必整体装入。
5. **PROT_NONE VA 预留**：先匿名 mmap 占 VA（weather_app.cu:147）再逐月 MAP_FIXED 覆盖，布局确定零冲突。

## 7. 已知坑与勘误

1. **HMM≠隐马尔可夫**（§1 钉版）；ATS=Address Translation Services。
2. **硬件门槛**：Addressing Mode 非 HMM 时 `-gpu=nomanaged` 系 demo 会挂，非代码 bug。
3. **typo 两处**：src/ticket_lock.cpp:86 成功串拼作 `SUCESS`（少一个 C）；数据脚本文件名拼错 `era5_preicp_nc_to_bin.py`（preicp≠precip）。
4. **weather_app.cu:282 用 `argc` 当文件数**：只处理 3 个月度文件，其余靠 weather_app.cu:291 整段 munmap 兜底，fd 泄漏被退出掩盖——能跑但别学。
5. **cub 归约只算半张网格**：weather_app.cu:235 `num_items=(721/2)*1440`（=360 行），只覆盖 721 行网格前 360 行；对比博客数字须带此口径。
6. **VA 预留多乘 sizeof(float)**：weather_app.cu:145 字节数又乘 4，预留 4 倍需求（无害）。
7. **argv 不校验**：weather_app.cu:126-128 直取 `argv[1..3]`，少参段错误。
8. **闰年简化**：weather_app.cu:104 只判 `year%4`，对 1981-2020 无伤，换区间重审。
9. **工具链勘误**：ci/demos、ci/run 是 POSIX sh（无扩展名，探测标 unknown，同样有行号可锚）；tree-sitter 对 .cpp/.cu 提取为空——图谱函数与类节点全为批分析手工补齐；era5 脚本无函数；demo 编译产物留在 src/。
## 8. 新人上手路径

1. 读 `README.md`：钉死 HMM 语义，查 Addressing Mode 确认 ATS 使能。
2. 跑 `./ci/run`：atomic_flag 打印 "CPU read message sent by GPU thread: 42"、ticket_lock 打印 `SUCESS: message = 4160`、file 两版打印 10 字节降序序列。
3. 精读 atomic_flag（56 行）：最小 HMM 样本——栈上一个 atomic 让 CPU 与 GPU 说同一句话。
4. ticket_lock 看跨设备互斥：guard_t 析构 fetch_add 的 release（src/ticket_lock.cpp:42）与取号 relaxed（:46）搭配。
5. 并排 diff file_before/file_after：只差 sortfile 一个函数（fread+vector vs mmap+指针），体会"消失的那次拷贝"。
6. miniapp 前先算账：直方图 `cudaMalloc`≈34GiB 显存（366x24x721x1440 个 float，weather_app.cu:191-194）+1.3TB 数据盘，80G 卡才稳。
7. miniapp 三步：CDS 下载（`miniapp/README.md:5`）→ python 转 bin → make 运行；读 main（weather_app.cu:117-295）抓 :147 预留、:174 MAP_FIXED、:241 `malloc // use HMM B-)`。

> 一句话：**src/ 教你"HMM 让 GPU 把 CPU 内存当自己家"，miniapp 证明这事在 1.3TB 真实数据上依然成立。**
