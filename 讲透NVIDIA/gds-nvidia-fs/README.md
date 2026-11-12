# 讲透 gds-nvidia-fs（NVIDIA/gds-nvidia-fs @6a65099b）

GPUDirect Storage（GDS）内核驱动 `nvidia-fs.ko`：存储 DMA/RDMA 直达 GPU 显存。本仓是内核半边（用户半边 cuFile 闭源不在仓内）。仓址 `/usr-data/data2/repos/agent-repos/NVIDIA/gds-nvidia-fs`。

## 全链状态表

| 阶段 | 产物 | 状态 |
|---|---|---|
| DeepWiki | `deepwiki/`（上游已收录） | ✅ 前轮完成 |
| understand 图谱 | 仓内 `.understand-anything/knowledge-graph.json`：139 节点/190 边/5 层/6 步 tour，validator 0 issues，fingerprints 30 文件 @6a65099b | ✅ |
| NOTES 收割 | 仓内 `.understand-anything/NOTES-DIGEST.md`（12 条批阶段甄别笔记） | ✅ |
| onboard 输入 | 仓内 `.understand-anything/onboard-input.json`（27KB，5 层/6 步/hubs30） | ✅ 2026-11-07 |
| ONBOARDING | `onboarding/ONBOARDING.md`（8 节，与本文合并口径；行号锚 40+） | ✅ |
| explain | 未拆分（微仓合并进 ONBOARDING §3-§5 分层走读） | — 合并口径 |

字数口径：不计空格总字符。本 README+ONBOARDING 合计 3000 字级（系列钉版口径）。

## 源码级勘误与甄别清单（本轮钉版）

1. **版本三口径不一致（最重磅）**：`src/GDS_VERSION`=1.20.0（GDS 发布口径，`src/Makefile:58-59` cat 注入 `-DGDS_VERSION`）vs `src/dkms.conf:25`=`PACKAGE_VERSION="2.7"`（DKMS 打包口径，`:24` 注释要求与 GDS_VERSION 同步但已脱节）vs `src/nvfs-vers.h:27/29/32`=2.31.5（驱动 ABI 口径，procfs/ioctl 上报值；commit 6a65099b 即 "from NVIDIA/2.31.5"）。引用版本号必须注明口径。
2. **`#ifdef` 整文件盲区三个**：`src/nvfs-batch.c`（CONFIG_NVFS_BATCH_SUPPORT，`src/Makefile:68`）、`src/nvfs-rdma.c`（CONFIG_DISABLE_NVFS_KERN_RDMA_SUPPORT，`src/Makefile:64`）、`src/nvfs-fault.c`（CONFIG_FAULT_INJECTION，`src/Makefile:57`）——整文件条件编译致 tree-sitter 零提取，图谱内函数（如 `nvfs-batch.c:71`/`nvfs-rdma.c:33`/`nvfs-fault.c:39`）全部人工补扫，勿用 scanner 复跑对账。
3. **`nvfs-dma.c` 的"类"实为函数表**：5 份 `nvfs_dma_rw_ops` 实例（声明 `nvfs-dma.c:80-84`，初始化 `nvfs-dma.c:1862+`）被 tree-sitter 记为类，实为操作表变量初始化；结构真身在 `nvfs-dma.h:75`。
4. **`nvfs-vers.h` 三个内联函数未建节点**：`nvfs_driver_version()` 等过短（`nvfs-vers.h:27-35` 区段），属"过短不建"而非盲区。
5. **`nvfs-mmap.c` 甄别双例**：`vm_operations_struct` 检测实为 `nvfs_mmap_ops` 静态操作表（约 663 行处）；ref 三兄弟为 static inline 未建节点。真实核心是 mgroup 族函数（`nvfs-mmap.c:677` 等）。
6. **`nvfs-p2p.h` 是转发头**：真身 `nv-p2p.h` 来自 NVIDIA 驱动源码目录（`-I$(NVIDIA_SRC_DIR)`），不在仓内——仓内 grep `nvidia_p2p_*` 原型会落空属预期。
7. **`config-host.h` 幽灵依赖**：`src/configure`（697 行 bash 特性探测，try_compile 模式）的产物，被几乎所有头引用但不在仓内；未跑 configure 前静态分析会报大量缺头。
8. **`nvfs-proc.c`/`nvfs-core.c` 的 extern"类"误检**：module_entry/mutex、"class/device"两处均为 extern 声明或静态变量，未建节点属正确处置。
9. **图谱形态缺陷（诚实记录）**：L01-L04 层与 tour t02-t05 的 nodeIds 全空、139 节点全集中 L05——层导航以 ONBOARDING §2 五层表为准，勿依赖图谱 layers 数组。

## 快速上手

- 全链走读：`onboarding/ONBOARDING.md`（§2 五层表 → §3 core 走读 → §4 dma/mmap → §6 构建 → §7 版本三口径）
- 深挖某层：core=`nvfs-core.c:945` 直接 I/O 主链起读；dma=`nvfs-dma.c:1862` 函数表；mmap=`nvfs-mmap.c:677` mgroup 建立
- 图谱：仓内 `.understand-anything/knowledge-graph.json`
