# 05 · dev-env 与样例公共底座：让 GDS"装得起来、编得动"的两块地基

> 范围：`dev-env/` 四件套 + `gds/samples/{include,common,Makefile}` + `gds-run-container`。图谱 L02+L10。

## 1. 角色定位

跑 cuFile 样例前置是驱动-内核模块-容器整链，两块地基：`dev-env/` 负责"裸机到能跑 GDS 容器"一键化（对应 NGC magnum-io:21.07）；`gds/samples/include+common` 是 42 个样例的公共底座，参数解析/文件构造/单位换算/SHA256 下沉到两个头文件（图谱 fanIn=36/15），Makefile 双路径编起来。

## 2. 内部结构

**installer.sh（605 行 18 函数）**：版本锚 `dev-env/installer.sh:6-9`（容器 21.07/驱动 ≥470.42 等）；OS 门卫白名单（L18-36）；拒 root（L44-49）。install_driver 走 ppa 装 nvidia-driver-470（`installer.sh:108`），`.run` 残留则拒装并引导 purge（L77-93）；install_cuda 装 cuda-toolkit-11-4 并向 `~/.bashrc` 追加带 MAGNUMIO-DEV-ENV-ADDED 标记的 export（`installer.sh:196-197`）；docker_adduser 以 usermod+setfacl 授权 docker.sock；case 分发包进子 shell 统一 tee 日志（`installer.sh:606`）。

**magnum-io.Dockerfile（125 行，L1 声明 DO NOT EDIT）**：由 hpccm 配方生成（`installer.sh:561`）。底座 `cuda:11.4.0-devel-ubuntu20.04`（`magnum-io.Dockerfile:3`）叠 MOFED（L20-41）→GDRCOPY（L43-57）→UCX 1.10.1（L59-77）→NVSHMEM（L79-92）→NCCL 2.10.3 钉版（L94-108）；`magnum-io.Dockerfile:115-118` 把 Dockerfile/third_party.txt/README **COPY 进镜像自身**留生成凭据；third_party.txt 是 GPL/LGPL 源码要约（3 年）。

**样例公共库**：`cufile_sample_utils.hpp`（187 行）四层——错误宏族（L27-69，分线程安全版）、Prng（L71-83）、单位换算 constexpr 模板 KiB/MiB/GiB（`cufile_sample_utils.hpp:85-113`）、cuFileGetErrorString 双重载（L139）。实现 `cufile_sample_utils.cc`（83 行）：GetFileSize fstat（L24-28）、parseInt ERANGE 校验（L30-47）、createTestFile 随机字节一次 write+fsync（`cufile_sample_utils.cc:49-83`）。`cufile_sample_shasum`：hpp 列三候选 so；cc 的 LoadSHA256Symbols 按序 dlopen（`cufile_sample_shasum.cc:68-80`），命中 `.so.3` 走 EVP 否则走旧 SHA256_Init 系（L89-104），兼容 OpenSSL 1.0/1.1/3.x；SHASUM256 对文件、SHASUM256_MEM 对 host/device 内存（`cufile_sample_shasum.cc:205/289`）。

**Makefile（116 行）**：CUFILE_PATH 按 arch 分 sbsa/x86_64-linux（L39-45）；`%` 与 `%_static` 双模式规则分链共享/静态 libcufile（L100-103）；vectorAdd.cu 先编成 .o 供样例链接（L95-98）；memmap_thrust 单独走 nvcc（L105-107）。Makefile.pip 把 CUDA 根指到 venv `nvidia/cu13`，须手工 symlink libcufile.so，且不产 `_static`。

## 3. 外部连接（图谱佐证）

图谱边证：`dev-env/README.md → installer.sh` 文档边，installer fanOut=36；`shasum.hpp imports utils.hpp`；36 样例→utils.hpp、15→shasum.hpp。跨层：`gds/docker/gds-run-container:56-57` 按 `ls /dev/nvidia-fs*` **动态枚举**设备注入 docker run，与 deepCam 脚本硬编码 fs0…fs15 对照（见 04 篇）。

## 4. 数据流

裸机：`setup-system` → 三探（nvidia-smi/version.txt/docker）→ REBOOT 提示 → run-container。容器：hpccm 配方→Dockerfile→build-container。构建：wildcard 收源（L79-84）→ 编 vectorAdd.o → 每样例出双二进制。运行：createTestFile 造随机文件 → cuFile 读写 → SHASUM256_MEM vs SHASUM256 双端摘要对账。

## 5. 设计决策

1. **HPCCM 生成而非手写**：25 行配方表达 120 行 Dockerfile；代价是 DO NOT EDIT。
2. **dlopen 而非硬链 OpenSSL**：运行时按序探测三个 so，同一二进制跑 CentOS 7 到 OpenSSL 3 都不崩。
3. **单位换算进 constexpr**：`KiB(128)` 编译期折叠成字节数。
4. **双 Makefile 而非条件分支**：系统与 pip CUDA 隔离两文件，pip 侧自带 debug-paths。
5. **错误宏分线程版**：`check_cudaruntimecall_thread` 失败时 set promise+return 而非 exit，保住 Multithreaded 组其他线程。

## 6. 新人提示（坑与勘误）

- **`gds/samples/Makefile:68-69` 死引用**：`release_samples` 指向不存在的 `../../docker/manylinux_2_28-docker/...` 与 `/nvme-direct/tools/samples`——内部 cufile 仓拷入的上游布局残迹，该目标必失败。
- **KiB 口径 1024 倍错位**：`highly_concurrent_halfreg.cc` 头注释称 256 MiB（L16）、示例输出写 262144 KiB（L24-25），实参 `KiB(256)`（`highly_concurrent_halfreg.cc:56`）=262144 **字节**——差 1024 倍；姊妹样例 many_buffers_set_bar.cc 打印同一字段却标 bytes（`many_buffers_set_bar.cc:183`），三口径打架。
- **EULA 三轨混装**：根 LICENSE=Apache-2.0；`gds/samples/` 带 NVIDIA 商业 NOTICE/EULA 头（Makefile:1-30）；`gds/benchmarks/pytorch/`=MIT——复制样例代码前先认清轨道。
- **install_nccl 空函数**：`installer.sh:379-383` 只有起止 nvlog，case 亦无此子命令——NCCL 由容器 apt 层负责。
- **hpccm 陈旧注释**：nvshmem 行注"See hack in instaler.sh..."（拼写亦错），现行无此逻辑。
- **LDFLAGS 首赋即死**：`Makefile:58` 引用未定义的 `CUFILE_LIB` 且被 L61 覆盖。
- **版本三处联动与 CC 硬编码**：installer.sh L6、Dockerfile L120 ENV、NGC TAG 须一致；hpccm 重生成后 COPY 清单缺新文件静默缺货；`Makefile:67` `CC:=/usr/bin/g++` 硬编码，交叉编译被无视。

---

*自报：3472；路径锚 18。*
