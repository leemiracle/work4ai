# GDRCopy Onboarding（图谱导览 · commit fcec3ce0）

> 图谱：224 节点 / 224 边 / 4 层 / 5 步 tour / fingerprints 81 文件 @fcec3ce0。
> 本文档全部行号锚经源码逐一核实（2026-11-07），口径：`文件:行号`。

## 1. 项目定位：它解决什么问题

GDRCopy 是 NVIDIA 开源的 **GPU 显存 CPU 可直接访问映射**方案，由两个交付物组成：内核模块 `gdrdrv.ko`（把 GPU device memory 经 `nvidia_p2p_get_pages` 取物理页后 `remap_pfn_range` 进用户地址空间）与用户态库 `libgdrapi.so`（封装 ioctl+mmap，并在用户态提供绕过 CPU cache 的非临时（non-temporal）memcpy 族）。典型用途：NCCL/RDMA 框架的小消息控制面搬运、GPU 显存与主机内存间低延迟 `gdr_copy_to/from_mapping`、以及零拷贝轮询标志位。

仓根 `README.md` 定义了用户视角的 API 面；图谱 tour t01（项目全景）即以它为入口。一句话数据流：**`gdr_open` → `gdr_pin_buffer` → `gdr_map` → `gdr_copy_*` → `gdr_unmap` → `gdr_unpin_buffer` → `gdr_close`**（tour t05 收官步主题）。

## 2. 四层架构（图谱 L01-L04）

图谱 4 层把 81 个分析文件分成四个清晰职责域：

| 层 | 名 | 文件数 | 职责 |
|---|---|---|---|
| L01 | 内核驱动层 | 39 | `src/gdrdrv/gdrdrv.c`（1976 行主实现）+ `gdrdrv.h`（ABI 契约）+ `nv-p2p-dummy.c`（无 GPU 环境桩） |
| L02 | 用户态 API 层 | 40 | `src/gdrapi.c`（1677 行）+ `cuda_wrapper.c`（dlopen CUDA Driver API）+ 9 个 `memcpy_*.c` 变体 + `include/gdrapi.h` 公共头 |
| L03 | 测试与平台层 | 49 | `tests/` 六个测试二进制 + `testsuites/` 自研框架 |
| L04 | 构建打包层 | 96 | 顶层/子目录 Makefile + `config_arch` + `insmod.sh` + `scripts/` + `packages/`（deb×3 + rpm + dkms） |

L04 占了图谱近半文件数，这是"发布型"仓库（DKMS/deb/rpm 三线打包）的典型形态，读码时可以先跳过。

## 3. 内核驱动 gdrdrv（L01，tour t02）

### 3.1 生命周期与两个核心对象

模块加载入口 `gdrdrv_init`（`src/gdrdrv/gdrdrv.c:1885`）注册字符设备与 `/proc/gdrdrv`（`gdrdrv_procfs_init`，`gdrdrv.c:1817`），卸载 `gdrdrv_cleanup`（`gdrdrv.c:1947`）逆序清理。每次 `open("/dev/gdrdrv")` 生成一个会话对象 `struct gdr_info`（`gdrdrv.c:444`）：内含 mr 链表+mutex、创建进程 pid 引用（`gdrdrv_check_same_process`，`gdrdrv.c:468`，防句柄跨进程滥用）与防重叠的 handle 分配器。每个成功 pin 的显存区域是一个 `struct gdr_mr`（`gdrdrv.c:372`）：句柄、p2p_token、`nvidia_p2p_page_table` 指针、映射大小/类型、free-callback 标志与 rw_semaphore。

### 3.2 ioctl 面：9 个命令码

ABI 契约集中在 `src/gdrdrv/gdrdrv.h`（用户库经 `-I gdrdrv/` 直接包含它，见 §6）：`GDRDRV_IOC_PIN_BUFFER`（`gdrdrv.h:74`）、UNPIN(2)/GET_CB_FLAG(3)/GET_INFO(4)/GET_INFO_V2(5)/GET_ATTR(6)/PIN_BUFFER_V2(7)/REQ_MAPPING_TYPE(8)（`gdrdrv.h:84-173`）与 GET_VERSION(255)（`gdrdrv.h:184`）。分派入口 `gdrdrv_ioctl`（`gdrdrv.c:1359`）。v1/v2 双轨是本仓 ABI 演进的常态——v2 引入 flags 替代已废弃的 p2p_token/va_space（`gdrdrv_pin_buffer_v2`，`gdrdrv.c:1059`）。`__gdrdrv_pin_buffer` 内按映射模式双向拒绝旧新混用：持久模式下传 token/va_space 在 `gdrdrv.c:842` 报"deprecated and now unsupported"；非持久模式下传非默认 flags 同样 EINVAL（`gdrdrv.c:833` 附近）。

### 3.3 pin 机制与异常释放回调

pin 核心 `__gdrdrv_pin_buffer`（`gdrdrv.c:798`）先把 addr/size 按 GPU 页粒度对齐（`gdrdrv.c:820` 附近），再调 NVIDIA 驱动的 `nvidia_p2p_get_pages` 系 API 取物理页表；持久映射模式（persistent）下 free_callback 传 NULL（`gdrdrv.c:826`），非持久模式挂 `gdrdrv_get_pages_free_callback`（`gdrdrv.c:733`）——GPU 侧显存被意外释放（如进程退出、CUDA 上下文销毁）时回调触发，标记 mr 失效并唤醒等待者，用户态可用 `gdr_get_callback_flag`（`gdrapi.c:470`）探知。unpin 对称路径 `__gdrdrv_unpin_buffer`（`gdrdrv.c:977`）内部最终走 `nvidia_p2p_put_pages_persistent`/`nvidia_p2p_put_pages`（`gdrdrv.c:587`/`gdrdrv.c:592`）。

### 3.4 mmap 与 PAT 坑

`gdrdrv_mmap`（`gdrdrv.c:1585`）用 offset 编码 handle（`gdr_generate_mr_handle`，`gdrdrv.c:767`）反查 mr，经 `gdrdrv_remap_gpu_mem`（`gdrdrv.c:1535`）把物理页塞进用户 VMA。x86 PAT 有个著名坑：内核 ≥5.13 的 `track_pfn_remap` 要求整 VMA 映射，`gdrdrv_io_remap_pfn_range`（`gdrdrv.c:1495`）在 PAT 启用且非整 VMA 时退化为逐 `PAGE_SIZE` 循环 `__gdrdrv_io_remap_pfn_range`（`gdrdrv.c:1479`）。映射类型（WC 写合并 / coherent 一致 / device BAR1）由协商 ioctl `gdrdrv_req_mapping_type`（`gdrdrv.c:1270`）与属性查询 `gdrdrv_get_attr`（`gdrdrv.c:1237`）支撑。

## 4. 用户库 libgdrapi（L02，tour t03）

### 4.1 双后端

`gdr_open`（`src/gdrapi.c:198`）运行时在两个后端间选择：传统 `gdrdrv` 后端（`gdr_open_gdrdrv_internal`，`gdrapi.c:112`，打开 `/dev/gdrdrv` 并做 GDRDRV_IOC_GET_INFO 版本握手，最低版本闸在 `gdrapi.c:132`）与新 dma-buf 后端（`gdr_open_dmabuf_internal`，`gdrapi.c:166`，依赖 CUDA 8.x+ 的 `cuMemGetFdForHandle` 路径）。后端能力探测靠 `cuda_wrapper.c` 的 dlopen 包装：`gdr_cuda_ftable_init`（`cuda_wrapper.c:105`）填 `gdr_cuda_function_table`（`cuda_wrapper.c:45`），`gdr_cuda_any_device_supports_dmabuf_mmap`（`cuda_wrapper.c:224`）与 `gdr_cuda_device_is_coherent`（`cuda_wrapper.c:288`，Grace-Hopper 一致性平台判定）决定走哪条路。每个 API（pin/map/get_info）都有 `*_gdrdrv`/`*_dmabuf` 成对实现，如 `gdr_pin_buffer_gdrdrv`（`gdrapi.c:357`）与 `gdr_pin_buffer_dmabuf`（`gdrapi.c:284`），由 `gdr_pin_buffer_internal`（`gdrapi.c:400`）分派。

### 4.2 memcpy 变体族与运行时派发

`src/` 下 9 个 `memcpy_*.c` 是同构的"每指令集一份非缓存拷贝内核"：SSE 基线（`memcpy_sse.c:105` 的 `_mm_stream_ps` store，源码 `memcpy_sse.c:126` 实证）、SSE4.1/AVX/AVX2/AVX512（x86）与 NEON/ST64/LS64（ARM64），加 `memcpy_movdir64b.c` 单向 store。链接哪些变体由 `src/Makefile:41-51` 按 `GDRAPI_ARCH` 决定；运行时 `gdr_init_cpu_flags`（`gdrapi.c:947`）用 `__builtin_cpu_supports` 探测后绑定函数指针，兜底是 `unroll8_memcpy`（`gdrapi.c:1072`）。拷贝调度链：公共 API `gdr_copy_to_mapping`（`gdrapi.c:1492`）/`gdr_copy_from_mapping`（`gdrapi.c:1504`）→ internal（`gdrapi.c:1270`/`gdrapi.c:1379`，按 16/32/64B 对齐分档）→ `aligned_copy`（`gdrapi.c:1237`）拆头/体/尾。非临时指令绕过 CPU cache 行，这正是映射显存拷贝性能与正确性（避免 cache 污染）的关键。

## 5. 测试族（L03，tour t04）

- **功能回归 `sanity`**（`tests/sanity.cpp`，2537 行）：37 个用例（36 处 `GDRCOPY_TEST` + 1 处 `GDRCOPY_EXTENDED_TEST` 宏调用）由 `testsuites/testsuite.hpp:26`/`testsuite.hpp:37` 的宏展开为 `GDRCopy_Test_##name` 类 + 静态自注册对象（构造进 `Test` 基类注册表，`testsuite.hpp:56`）；运行器 `run_tests`（`testsuite.cpp:63`）fork 子进程隔离执行（`Test::run`，`testsuite.cpp:143`）。跨进程 fd 传递用例靠 `sendfd`/`recvfd`（`sanity.cpp:160`/`sanity.cpp:203`，SCM_RIGHTS）；平台过滤 `coherent_platform_filter`（`sanity.cpp:124`）。
- **带宽 `copybw`**（`tests/copybw.cpp`，run_test 在 `copybw.cpp:68`）与**延迟 `copylat`**（`tests/copylat.cpp:70`）互补刻画 size-bandwidth/latency 曲线。
- **API 开销 `apiperf`**（`tests/apiperf.cpp:62`）：逐 API 计时直方图。
- **ping-pong 延迟 `pplat`**（`tests/pplat.cu`）：4 个 `__global__` kernel（`pplat.cu:50`/`70`/`107`/`142`）+ 统一内存位置分配 `gh_mem_alloc`（`pplat.cu:261`），对比 GDRCopy mapping 与零拷贝内存两条路径；主循环 `main`（`pplat.cu:378`）。

公共设施在 `tests/common.cpp`：`gpu_mem_alloc`（`common.cpp:45`，cuMemAlloc 与 dma-buf 双路径）、`compare_buf`（`common.cpp:254`）、`check_gdr_support`（`common.cpp:301`）与 `gdr_open_safe`（`common.hpp:148`）。

## 6. 构建与打包（L04）

顶层 `Makefile` 递归进 `src/`、`src/gdrdrv/`、`tests/`；`config_arch`（仓根）是 bash+heredoc 生成 C 再编译执行的架构探测技巧。`src/Makefile:27` 的 `-I gdrdrv/` 使用户库能直接包含内核共享头 `gdrdrv.h`——这是 libgdrapi 与驱动同 ABI 版本的关键。内核侧 `src/gdrdrv/Makefile` 按 `HAVE_PROC_OPS`/`HAVE_VM_FLAGS_SET`（探测脚本 `scripts/test_gdrdrv_HAVE_*.sh`）适配内核 API 漂移。打包三线：deb（`packages/debian-lib|meta|tests`）、rpm（`packages/build-rpm-packages.sh`）、DKMS（`packages/dkms.conf`，占位符 `@FULL_VERSION@` 由 `packages/build-deb-packages.sh` 替换）。

## 7. 版本与兼容语义

驱动 ABI 版本 2.6 由 `gdrdrv.h:31-34` 的 `GDRDRV_MAJOR_VERSION<<16|MINOR` 编码，经 GET_VERSION ioctl（`gdrdrv_get_version`，`gdrdrv.c:1341`，赋值点 `gdrdrv.c:1346`）上报；用户库按 `MINIMUM_GDRDRV_VERSION`（`gdrapi.c:132`）与特性闸（如 `GDRDRV_MINIMUM_VERSION_WITH_REQ_MAPPING_TYPE`，消费点 `gdrapi.c:582`）做能力协商。p2p_token/va_space 参数族已标记废弃（`gdrdrv.c:838` 附近报 EINVAL）。

## 8. 图谱质量注记（读图须知）

本图谱 224 节点含 138 函数/69 文件/5 类/5 pipeline/4 文档/3 配置。甄别口径见仓库 NOTES-DIGEST（14 条）：宏调用点不建节点（`GDRCOPY_TEST` 36+1 处调用点由宏展开成类+静态对象，非函数）；三处"操作表初始化"（`gdrdrv.c:329` proc_dir_entry 变量、`gdrdrv.c:1464` gdrdrv_vm_ops、`gdrdrv.c:1777`/`1809` proc fops）未误建类节点；`pplat.cu` 因 tree-sitter 不支持 .cu 由人工补 9 函数；`config_arch` 无扩展名按 unknown 识别实为 bash 生成 C 技巧。勘误与盲区明细见本目录上级 `README.md`。
