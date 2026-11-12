# GDS nvidia-fs Onboarding（GPUDirect Storage 内核模块 · commit 6a65099b）

> 图谱：139 节点/190 边/5 层/6 步 tour/fingerprints 30 文件 @6a65099b（"2.31.5" 分支合入点）。
> 全部行号锚经源码核实（2026-11-07），口径 `文件:行号`，仓址 `/usr-data/data2/repos/agent-repos/NVIDIA/gds-nvidia-fs`。

## 1. 它是什么：存储 DMA 直达 GPU 显存的内核侧

本仓只包含 GPUDirect Storage（GDS）的**内核半边**：`nvidia-fs.ko`。它让 NVMe/分布式文件系统的 DMA 引擎把数据直接搬进用户态 CUDA 分配的 GPU 显存，绕开 CPU 中转与 bounce buffer；用户半边是 NVIDIA 闭源的 cuFile 库（不在本仓），两者以 `/dev/nvidia-fs` 字符设备为契约面。`README.md` 列出支持的文件系统（XFS/EXT4 ordered、NFS over RDMA、DDN/WEKA/VAST、ScaleFlux）与软硬件要求；`ChangeLog` 按 2.x 版本记录对各内核版本、MOFED 与各存储后端的适配史。

用户视角的一句话数据流：**cuFile → ioctl(NVFS_IOCTL_MAP) pin GPU 页 → mmap 取 CPU 可访问映射 → read/write 直接 I/O 路径组 scatterlist（GPU 物理地址）→ 存储设备 DMA 直达**；完成通知可走 endfence 页。

## 2. 五层子系统地图（core/rdma/batch/dma/mmap + fault）

| 层 | 文件（行数） | 职责 |
|---|---|---|
| core | `src/nvfs-core.c`（2582） | 字符设备与 ioctl 面、直接 I/O 主路径、GPU 页 pin/unmap、endfence、稀疏段、I/O 状态机 |
| rdma | `src/nvfs-rdma.c`（232） | 内核 RDMA 注册信息（rkey/gid/远端地址）挂到 mgroup，服务 NFS over RDMA/分布式 FS |
| batch | `src/nvfs-batch.c`（178） | 一次 ioctl 组装多请求（`nvfs_io_batch_init` `nvfs-batch.c:71` → `nvfs_io_batch_submit` `nvfs-batch.c:148`），降小 I/O 提交开销 |
| dma | `src/nvfs-dma.c`（1898） | 块层 DMA 挂接：5 份 `nvfs_dma_rw_ops` 实例（声明 `nvfs-dma.c:80-84`，初始化 `nvfs-dma.c:1862+`，dev/NVMe/SFX/NVMesh/IBM Scale 五后端） |
| mmap | `src/nvfs-mmap.c`（1555） | mgroup（映射组）生命周期、CPU 可访问 GPU 内存映射、shadow page pin、页→mgroup 反查与 DMA 状态标记 |
| fault | `src/nvfs-fault.c`（74） | debugfs 错误注入：7 个 `DECLARE_FAULT_ATTR`（`nvfs-fault.c:31-37`），init 在 `nvfs-fault.c:39` |

支撑模块：`nvfs-pci.c`（866，PCI 拓扑与 GPU↔peer 距离矩阵）、`nvfs-proc.c`（295，`/proc/nvidia-fs` 观测面，init `nvfs-proc.c:241`）、`nvfs-stat.c`（640，per-GPU 吞吐/时延直方图，如 `nvfs-stat.c:399`）、`nvfs-mod.c`（162，后端探测 `probe_module_list` `nvfs-mod.c:40`）、`nvfs-kernel-interface.c`（70，内核版本兼容，`nvfs_check_access` `nvfs-kernel-interface.c:26`）。中枢头 `nvfs-core.h` 几乎被全部 .c 引用。

## 3. core 层走读：ioctl 面与直接 I/O 主链

ioctl 命令码在 `nvfs-core.h:225-235`：REMOVE(1)/READ(2)/MAP(3)/WRITE(4)/SET_RDMA_REG_INFO(5)/GET_RDMA_REG_INFO(6)/CLEAR_RDMA_REG_INFO(7)/BATCH_IO(8)，全 `_IOW(NVFS_MAGIC, n, int)`；分派入口 `nvfs_ioctl`（`nvfs-core.c:2199`，先整体 `copy_from_user` 一个 union）。file_operations 挂接在 `nvfs-core.c:2437-2440`：`.unlocked_ioctl/.open(nvfs_open :1022)/.release(nvfs_close :1049)/.mmap(nvfs_mgroup_mmap)`。

MAP 主链：`nvfs_map`（`nvfs-core.c:1448`）→ `nvfs_pin_gpu_pages`（`nvfs-core.c:1193`，调 NVIDIA 驱动 `nvidia_p2p_get_pages` 取页表、校验对齐、登记 mgroup）→ `nvfs_map_gpu_info`（`nvfs-core.c:1373`）→ `nvfs_map_commit_if_vma_alive`（`nvfs-core.c:1401`，防并发 munmap 竞态）。读写主链：`nvfs_direct_io`（`nvfs-core.c:945`）串起 `nvfs_rw_verify_area`（`nvfs-core.c:882`）→ `nvfs_get_dma`（`nvfs-core.c:461`，选后端 ops、组 scatterlist）→ 同步/异步完成（`nvfs_io_signal_async_completion` `nvfs-core.c:646`），收尾 `nvfs_io_free`（`nvfs-core.c:662`）；状态机骨架 `nvfs_transit_state`（`nvfs-core.c:158`）支撑取消与错误回滚；完成栅栏页 `nvfs_get_endfence_page`（`nvfs-core.c:1085`）。DMA 地址分段见 `nvfs_get_dma_address`（`nvfs-core.c:267`，处理页边界与 peer 路由）。

多后端热插拔靠引用计数：`nvfs_get_ops`/`nvfs_put_ops`（`nvfs-core.c:123`/`nvfs-core.c:128`）配合模块符号表，`nvfs-mod.c:40` 的 probe 链逐个探测本地 NVMe/SFX/NVMesh/Mellanox RDMA 后端并逆序清理。

## 4. dma 与 mmap 层：块层挂接和 CPU 侧映射

dma 层把 GDS 能力注入内核块层：请求合法性三闸 `nvfs_blk_rq_check`（`nvfs-dma.c:294`）/`nvfs_req_payload_supported`（`nvfs-dma.c:314`）/`nvfs_is_request_valid`（`nvfs-dma.c:325`）后，按后端用对应 `nvfs_dma_rw_ops` 做 map_page/unmap_page（结构定义 `nvfs-dma.h:75`）；内核版本差异以 `HAVE_*` 宏适配。

mmap 层的核心对象是 mgroup：建立走 `nvfs_mgroup_mmap_internal`（`nvfs-mmap.c:677`，创建 mgroup+基址索引+挂 vm_ops），区间登记 `nvfs_mgroup_check_and_set`（`nvfs-mmap.c:895`），CPU 缺页时 `nvfs_mgroup_pin_shadow_pages`（`nvfs-mmap.c:379`）pin shadow pages。反查协议是 RDMA/dma 侧的基石：`__nvfs_mgroup_from_page`（`nvfs-mmap.c:1203`，处理复合页）与 `nvfs_is_gpu_page`（`nvfs-mmap.c:1440`，按 `page->pgmap` 判 GPU 页），DMA 进行中/完成状态由 `nvfs_mgroup_metadata_set_dma_state`（`nvfs-mmap.c:1345`）标记，配合 invalidate 协议保证 CPU/GPU 一致性视角。

## 5. 拓扑与观测：pci/proc/stat

`nvfs-pci.c` 枚举全部 GPU 与 peer 存储设备（`__nvfs_find_all_device_paths` 系），计算 GPU×peer 距离矩阵：核心 `__nvfs_get_gpu2peer_distance`（`nvfs-pci.c:485`，综合 ACS 检查 `nvfs-pci.c:229`、公共桥层级、NUMA 距离与可用带宽 `nvfs_pcie_bw_available`（`nvfs-pci.c:260`）），幂等一次性填充 `nvfs_fill_gpu2peer_distance_table_once`（`nvfs-pci.c:646`），对外查询 `nvfs_get_gpu2peer_distance`；`nvfs_rank_data`（`nvfs-pci.c:91`）是矩阵元素类型（图谱唯一 class 节点）。观测面：`/proc/nvidia-fs/{version,modules,bridge,devices,...}`（`nvfs-proc.c:241` 注册，modules 清单回调 `nvfs-proc.c:41`）；统计直方图按设备累计读写吞吐/时延（`nvfs-stat.c:399` 等 8 个 update 函数），procfs 写触发整表重置（`nvfs-stats_reset` `nvfs-stat.c:551`）。

## 6. 构建面：configure 协商与四个条件编译开关

`src/configure`（697 行 bash）探测内核树、MOFED 与 `HAVE_*` 内核特性，产出 `config-host.h`（不在仓内）与 Makefile 参数。`src/Makefile` 的四个开关决定子系统是否参与编译：`CONFIG_NVFS_STATS`（`src/Makefile:56`，nvfs-stat.o）、`CONFIG_FAULT_INJECTION`（`src/Makefile:57`，nvfs-fault.o）、`CONFIG_DISABLE_NVFS_KERN_RDMA_SUPPORT`（`src/Makefile:64`，nvfs-rdma.o）、`CONFIG_NVFS_BATCH_SUPPORT`（`src/Makefile:68`，nvfs-batch.o）；core/dma/mmap/pci/proc/mod/kernel-interface 必选。`src/Makefile:58-59` 把 `GDS_VERSION` 文件内容 cat 出来注入 `-DGDS_VERSION`。NVIDIA 驱动的 `nv-p2p.h` 不在仓内（`-I$(NVIDIA_SRC_DIR)` 提供，经 `src/nvfs-p2p.h` 转发引用）；无 symvers 时用 `src/create_nv.symvers.sh` 自造（其探测函数 `try_compile_nvidia_sources` 在 `create_nv.symvers.sh:36`）。DKMS 配置 `src/dkms.conf` 让驱动随内核更新重编。

## 7. 版本三口径不一致（重要勘误域）

同一份源码树里有三个互不同步的版本号，引用时必须注明口径：

1. **`src/GDS_VERSION` = 1.20.0**（单行文件）：GDS 上游发布口径，`src/Makefile:58-59` 读入注入编译宏。
2. **`src/dkms.conf:25` `PACKAGE_VERSION="2.7"`**：DKMS 打包口径；上一行 `src/dkms.conf:24` 注释明说"please update when GDS_VERSION is updated"，但当前 2.7 与 1.20.0 明显脱节。
3. **`src/nvfs-vers.h:27/29/32` = 2.31.5**（NVFS_DRIVER_MAJOR/MINOR/PATCH）：驱动自身 ABI 口径，procfs 与 ioctl 上报的是它；本 commit（6a65099b）正是 "Merge pull request #89 from NVIDIA/2.31.5"。

## 8. 图谱质量注记

图谱 139 节点（108 函数/25 文件/1 类/3 文档/1 配置/1 pipeline）。已知形态缺陷：L01-L04 的 nodeIds 为空、全部 139 节点集中在 L05，tour t02-t05 的 nodeIds 也为空——层/步仅存标题与描述，内容层级的导航请以本文 §2 的五层表为准。`#ifdef` 整文件盲区三个（nvfs-batch.c/nvfs-rdma.c/nvfs-fault.c，tree-sitter 零提取、函数人工补扫）；`nvfs-dma.c` 主体是 5 份函数表初始化（tree-sitter 记为"类"，实为变量）；`nvfs-vers.h` 三个版本内联函数因过短未建节点。勘误明细见上级 `README.md`。
