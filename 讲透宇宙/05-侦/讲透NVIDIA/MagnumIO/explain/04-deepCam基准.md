# 04 · deepCam 推理基准：GDS 加速 DL 数据加载的端到端实证

> 范围：`gds/benchmarks/pytorch/deepCam-inference/`（19 源码文件 + 53 权重分片）与 `docker/`。图谱归属 L15+L16。

## 1. 角色定位

`samples/` 是 cuFile 的字母表，`readers/` 是工程化，deepCam 则是**毕业答辩**：真实 MLPerf HPC 负载（气候分割 DeepCAM，NERSC 数据 ~12 万 HDF5、约 10 TB，README.md:30），DeepLabv3+ 推理，对比"GDS 直读显存"与 posix 两条加载链路的吞吐与 CPU 占用——回答 GDS 的终极问题：**存储→显存交给 cuFile，端到端快多少**。

## 2. 内部结构

**入口 `driver/test_numpy_dali.py`（290 行）**：mpi4py 多进程（第 63 行）；硬编码 `channels=[0,1,2,10]`（第 80 行）取 4 个气候通道；主循环 `range(-warmup, runs)`（第 168 行）用负数区间实现"warmup 不落盘"（第 273 行）。

**数据 `data/cam_numpy_dali_dataset.py`（195 行）**：`fn.readers.numpy(device=self.io_device)` 一参数定两路——GDS 时 `"gpu"` 走 cuFile（第 114 行）。`register_buffers=True`（第 47 行）预注册缓冲；`dont_use_mmap` 在 GDS 下强制真（第 48 行）；HWC→CHW 的 `fn.transpose` 在 GPU 上做（第 63-65 行）；`sample_sizes` 按 `np.prod(shape)*4` 估字节（第 172-174 行）。

**模型 `utils/model_handler.py`（199 行）**：`DeepLabv3_plus(nInputChannels=4, n_classes=3, os=16)`（第 79 行）；`reload_model` 剥 DDP 的 `"module."` 前缀（第 53-54 行）。三加速线：FP16（第 89 行）、Torch-TensorRT（缓存名 `model_fp16_bs{bs}_gpu{id}.trt`，第 101-102 行）、CUDA Graph（空跑 10 次再 capture，第 147-157 行）。输入 shape 硬编码 `(bs,4,768,1152)`（第 115 行）。`architecture/deeplab_xception.py`：`Xception`(124)、`ASPP_module`(281)、`DeepLabv3_plus`(340 行)，os=16 空洞率 `[1,6,12,18]`（第 355-356 行）。

**编排 `scripts/run_benchmark.sh`**：`gds=${1:-0}`（第 48 行）切换 A/B 臂；测量臂统一 fp16+trt+graphs（第 77 行）；GDS 臂 inter×intra 双扫、posix 臂固定 intra=1（第 51-57 行）；mpirun 恒套 `bind.sh --cpu=exclusive`（第 128 行）。**对比口径**在 `utils/parser.py:57-60`：`--enable_gds` 强制 `drop_fs_cache=False`+`disable_mmap=True`；posix 臂每轮写 `/proc/sys/vm/drop_caches` 模拟冷缓存（driver 第 171-174 行），GDS 天然绕 page cache。

## 3. 外部连接（图谱佐证）

L15+L16 合计 72 节点。`driver` imports dataset/model_handler/losses/parser 四件套；**`docker/Dockerfile → deeplab_xception.py` 的 deploys 边**把容器与模型源码显式关联；L16 的 53 个 `model_partXX` 各一条边指向 `model_handler.py`（fanIn=53，全仓最高入度之一）。`run_docker_deepcam.sh → run_benchmark.sh → bind.sh` 三层 depends_on 对应"容器→编排→绑核"。外部依赖（DALI、mpi4py、Torch-TensorRT）全由 docker/ 固化。

## 4. 数据流

冷启动：53 分片 → `cat share/model_part* > share/model.pth`（README.md:12）→ 加载（`model_handler.py:70` 硬编码 `/share/model.pth`，与 Dockerfile:102 咬合）。稳态：HDF5 → `download_data.py` 转 npy → DALI 分 shard、GDS 直读显存 → GPU transpose → 选通道（dataset 第 184 行）→ 可选 FP16/NHWC → argmax（driver 第 210 行）。带宽按 `(it*batch_size*sample_size)/(tend-tstart)`（第 269 行）。

## 5. 设计决策

1. **权重分片 53 份**：单文件 ~209 MB 超 GitHub 100 MB 限，切 53×4 MiB（每片 4194304 字节、末片 839097，pickle 协议 2 头 `80 02`），`cat` 重装——不引 git-lfs，代价是手动拼装。
2. **IO/推理解耦**：`--mode=io` 只加载不前向，GDS 收益精确归因到"省掉的 memcpy+CPU"。
3. **一份 Python 双路径**：GDS/posix 仅差 DALI 一个 `device` 参数，对照零额外变量；posix 臂 drop_caches+禁 mmap 对齐"GDS 无 page cache"语义。
4. **容器内缝合 CUDA**：NGC `pytorch:21.11-py3`（11.5）为底，另装 11.6 repo 只为 `libcufile-dev-11-6`，再把 11.6 头/库拷进 11.5 树（Dockerfile:38-43）。
5. **TRT 缓存按 (bs,gpu,精度) 寻址**：规避引擎与 GPU 架构绑定（README.md:65）。

## 6. 新人提示（坑与勘误）

- **拼装是硬前置**：不 `cat` 出 `model.pth` 必失败；裸机跑须先改 `model_handler.py:70` 硬编码路径。
- **"GB/s" 实为 GiB/s**：driver 第 268 行按 `/1024^3` 换算却印 GB/s，跨文对比差 ~7%。
- **`--visualize` 死路**：driver 第 159 行 `vizc` 无 import，开了必 NameError。
- **h52npy 命名不一致**：`download_data.py` 产出 `data-*.npy`（匹配 loader glob），`h52npy.py:52-57` 产出 `*_data.npy`——后者转的数据一个都不会被读。
- **fp_loss 假惩罚**：`losses.py:40-47` 的 `eq(preds,1)&ne(preds,1)` 恒 False，fpw 权重无效。
- **脚本失败退出码 0**：`run_benchmark.sh:141-143` 的无参 `exit` 继承测试命令的 0，错误码被吞，CI 化须改 `exit 1`。
- **bind.sh NUMA 是算的不是测的**：第 123 行按 `local_rank/gpus_per_node` 整除推节点，不查 `nvidia-smi topo`，非均匀拓扑绑错核。
- **设备枚举两套**：`run_docker_deepcam.sh:50-65` 硬编码 fs0…fs15，样例侧 `gds-run-container` 动态 `ls /dev/nvidia-fs*`——fs>16 的机器前者漏。
- **2021 工具链化石**：NGC 21.11 + bazel-4.0.0（Dockerfile:51）+ Torch-TensorRT stable-21.12 还 merge PR#719（第 68-74 行）+ DALI nightly（第 97 行）；新 CUDA 复现应换现代镜像。
- **`lazy_init` 死参数**：dataset 第 136/151 行只存值从不消费，不延迟第 99 行的 np.load。

---

*字数自报：3488 字符（去空白）；行号锚 40 处，全部源码核实（路径相对 `gds/benchmarks/pytorch/`）。*
