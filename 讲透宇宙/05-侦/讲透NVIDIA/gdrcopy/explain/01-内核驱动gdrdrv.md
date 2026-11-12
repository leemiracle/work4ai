# 01 · 内核驱动 gdrdrv：把 GPU 显存钉进用户页表

> 对象：`src/gdrdrv/gdrdrv.c`（1976 行）+ `src/gdrdrv/gdrdrv.h`（ABI 契约）+ `src/gdrdrv/nv-p2p-dummy.c`。行号锚 @fcec3ce0 源码核实。

## 一、角色定位

gdrdrv 是 GDRCopy 的内核半边：一个misc 字符设备驱动（`/dev/gdrdrv`），职责是把用户指定的 GPU device memory 区间经 NVIDIA 闭源驱动的 P2P API（`nvidia_p2p_get_pages`）钉住物理页，再用 `remap_pfn_range` 系列映射进用户进程地址空间。它不做数据搬运——拷贝由用户态 libgdrapi 完成；它只负责"页的产权与映射"。模块加载入口 `gdrdrv_init`（`gdrdrv.c:1885`），卸载 `gdrdrv_cleanup`（`gdrdrv.c:1947`）。

## 二、内部结构

两个核心对象撑起全部状态：会话级 `struct gdr_info`（`gdrdrv.c:444`）——每次 open 一个，内含 mr 链表+mutex、创建者 pid（`gdrdrv_check_same_process`，`gdrdrv.c:468`，跨进程句柄滥用防线）与单调递增的 handle 分配；区域级 `struct gdr_mr`（`gdrdrv.c:372`）——每个成功 pin 的显存区间一个，持有 `nvidia_p2p_page_table` 指针、映射类型与 free-callback 标志。`gdrdrv_open`（`gdrdrv.c:512`）创建前者，`gdrdrv_release`（`gdrdrv.c:622`）与 `gdr_free_mr_unlocked`（`gdrdrv.c:566`）负责回收。

ioctl 面共 9 个命令码，全部定义在共享头 `gdrdrv.h`：PIN_BUFFER(1)（`gdrdrv.h:74`）、UNPIN(2)/GET_CB_FLAG(3)/GET_INFO(4)/GET_INFO_V2(5)/GET_ATTR(6)/PIN_BUFFER_V2(7)/REQ_MAPPING_TYPE(8)（`gdrdrv.h:84-173`）、GET_VERSION(255)（`gdrdrv.h:184`）。主分派 `gdrdrv_ioctl`（`gdrdrv.c:1359`）。

## 三、外部连接

- **向 NVIDIA 闭源驱动**：pin/unpin 调 `nvidia_p2p_get_pages*`/`nvidia_p2p_put_pages*`（unpin 侧实证 `gdrdrv.c:587`/`gdrdrv.c:592`）；`nv-p2p-dummy.c:70-92` 提供 5 个弱符号桩，让无 GPU 环境也能编译加载。
- **向用户库**：`gdrdrv.h` 被用户态 `src/gdrapi.c` 经 `-I gdrdrv/`（`src/Makefile:27`）直接包含——内核头即 ABI 契约，两侧版本号（2.6，`gdrdrv.h:31-34`）借此对齐。
- **向运维**：`/proc/gdrdrv/params` 与 `nv_get_pages_refcount` 只读节点（`gdrdrv_procfs_init`，`gdrdrv.c:1817`）。

## 四、数据流（pin→map→unmap）

1. 用户 `ioctl(GDRDRV_IOC_PIN_BUFFER)` → `gdrdrv_pin_buffer_v2`（`gdrdrv.c:1059`）→ `__gdrdrv_pin_buffer`（`gdrdrv.c:798`）：addr/size 按 GPU 页对齐，非持久模式挂回调 `gdrdrv_get_pages_free_callback`（`gdrdrv.c:733`），取页表填 gdr_mr。
2. 用户 `mmap` → `gdrdrv_mmap`（`gdrdrv.c:1585`）：offset 即 handle（`gdr_generate_mr_handle`，`gdrdrv.c:767`）反查 mr → `gdrdrv_remap_gpu_mem`（`gdrdrv.c:1535`）。
3. `munmap` → `gdrdrv_vma_close`（`gdrdrv.c:1437`）递减引用；异常路径（GPU 侧先释放）走 free callback 置失效标志，用户态以 `gdr_get_callback_flag`（`gdrapi.c:470`）探知。

## 五、设计决策

- **PAT 逐页退化**：内核 ≥5.13 的 `track_pfn_remap` 要求整 VMA 映射，`gdrdrv_io_remap_pfn_range`（`gdrdrv.c:1495`）在 PAT 启用且区间非整 VMA 时逐 `PAGE_SIZE` 循环调用 `__gdrdrv_io_remap_pfn_range`（`gdrdrv.c:1479`），源码注释直接引用 elixir 链接说明 WAR 动机。
- **映射类型协商**：`gdrdrv_req_mapping_type`（`gdrdrv.c:1270`）让用户在 WC/ coherent/ device 间协商，属性面由 `gdrdrv_get_attr`（`gdrdrv.c:1237`）+ `gdrdrv_get_info_v2`（`gdrdrv.c:1199`）暴露——一致性平台（Grace-Hopper）与老平台分开处理。
- **新旧参数双向拒绝**：`__gdrdrv_pin_buffer` 在 `gdrdrv.c:842`（持久模式收 token 即 EINVAL"deprecated"）与 `gdrdrv.c:833`（非持久模式收非默认 flags 即 EINVAL）强制两条参数轨不混用。
- **vm_ops 钩子**：`gdrdrv_vm_ops`（`gdrdrv.c:1464`）只挂 close，映射生命周期完全绑定 VMA 引用计数。

## 六、新人提示

读码顺序建议：`gdrdrv.h`（ioctl 结构）→ `gdrdrv_ioctl`（`gdrdrv.c:1359`，命令码全景）→ `__gdrdrv_pin_buffer`（`gdrdrv.c:798`，最核心 175 行）→ `gdrdrv_mmap`（`gdrdrv.c:1585`）。注意图谱甄别：`gdrdrv.c:1464` 的 `vm_operations_struct` 与 `gdrdrv.c:1777`/`gdrdrv.c:1809` 的两处 `file_operations` 是操作表初始化而非类，未建节点属正确决策；`/proc/gdrdrv` 相关的 `proc_dir_entry`（`gdrdrv.c:329`）是静态变量。适配新内核 API 漂移的探测脚本在 `scripts/test_gdrdrv_HAVE_PROC_OPS.sh` 与 `scripts/test_gdrdrv_HAVE_VM_FLAGS_SET.sh`。
