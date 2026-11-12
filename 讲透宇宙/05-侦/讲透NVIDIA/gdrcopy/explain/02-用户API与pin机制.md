# 02 · libgdrapi 用户库：双后端、pin 语义与非缓存 memcpy

> 对象：`src/gdrapi.c`（1677 行）+ `src/cuda_wrapper.c` + `src/memcpy_*.c`×9 + `src/gdrapi_internal.h` + `include/gdrapi.h`。行号锚 @fcec3ce0 源码核实。

## 一、角色定位

libgdrapi 是 GDRCopy 的用户半边：对上层暴露 `gdr_open/pin_buffer/map/copy_to|from_mapping/unmap/unpin_buffer/close` 七步 API（公共原型全在 `include/gdrapi.h`，该头纯声明、零函数体，符合消费者视角），对下层同时兼容两条内核通道——传统 gdrdrv 字符设备与新 CUDA dma-buf。它还自带一个"小型 SIMD 库"：9 份按指令集拆分的非临时（non-temporal）memcpy 内核，专为绕过 CPU cache 的显存映射拷贝设计。

## 二、内部结构

`gdr_open`（`gdrapi.c:198`）是后端选择点：先经 cuda_wrapper 探测，gdrdrv 路径走 `gdr_open_gdrdrv_internal`（`gdrapi.c:112`，打开 `/dev/gdrdrv` + GET_INFO 握手，最低版本闸 `gdrapi.c:132`），dma-buf 路径走 `gdr_open_dmabuf_internal`（`gdrapi.c:166`）。会话对象 `gdr_t` 与映射句柄 `gdr_memh_t` 定义在 `src/gdrapi_internal.h`（后端类型/fd/属性）。每个多态 API 都有 `*_gdrdrv`/`*_dmabuf` 成对实现+一个 internal 分派器：pin 组 `gdr_pin_buffer_gdrdrv`（`gdrapi.c:357`）/`gdr_pin_buffer_dmabuf`（`gdrapi.c:284`）/`gdr_pin_buffer_internal`（`gdrapi.c:400`）；map 组 `gdr_map_gdrdrv`（`gdrapi.c:570`）/`gdr_map_dmabuf`（`gdrapi.c:637`）/`gdr_map_v2`（`gdrapi.c:682`）。

cuda_wrapper 是 dlopen 薄包装：`gdr_cuda_ftable_init`（`cuda_wrapper.c:105`）dlopen libcuda 并按符号清单填 `gdr_cuda_function_table`（`cuda_wrapper.c:45`），引用计数单次初始化；`gdr_cuda_any_device_supports_dmabuf_mmap`（`cuda_wrapper.c:224`）与 `gdr_cuda_device_is_coherent`（`cuda_wrapper.c:288`）是两个后端/映射类型探测点。好处：libgdrapi 不在链接期依赖 CUDA。

## 三、外部连接

- **内核**：ioctl 命令码来自共享头 `gdrdrv.h`（经 `src/Makefile:27` 的 `-I gdrdrv/`）；gdrdrv 后端版本协商点如 `gdrapi.c:582`（`GDRDRV_MINIMUM_VERSION_WITH_REQ_MAPPING_TYPE` 特性闸）。
- **CUDA Driver API**：仅 dlopen，入口 `gdr_cuda_init`（`cuda_wrapper.c:194`）。
- **CPU 指令集**：运行时 `gdr_init_cpu_flags`（`gdrapi.c:947`）用 `__builtin_cpu_supports` 探测，绑定函数指针；编译期按 `GDRAPI_ARCH`（`src/Makefile:41-51`）决定链接哪些 `memcpy_*.c`。

## 四、数据流（pin→map→copy）

1. **pin**：`gdr_pin_buffer`（`gdrapi.c:433`，v1 兼容包装）或 `gdr_pin_buffer_v2`（`gdrapi.c:438`，flags 版）→ internal → gdrdrv 侧填 `GDRDRV_IOC_PIN_BUFFER_PARAMS` 发 ioctl；dma-buf 侧则把显存导出为 fd 登记。
2. **map**：`gdr_map_gdrdrv`（`gdrapi.c:570`）先发 REQ_MAPPING_TYPE 协商（`gdrapi.c:582`），再以 `handle << page_shift` 为 offset 直接 `mmap` 设备 fd（`gdrapi.c:589` 附近），随后 `gdr_get_info_v2` 回读确认映射类型。`gdr_unmap`（`gdrapi.c:724`）对称 munmap。
3. **copy**：公共 API `gdr_copy_to_mapping`（`gdrapi.c:1492`）/`gdr_copy_from_mapping`（`gdrapi.c:1504`）→ internal（`gdrapi.c:1270`/`gdrapi.c:1379`，按 16/32/64B 对齐分档）→ `aligned_copy`（`gdrapi.c:1237`）拆头/体/尾三段后调选定内核；无特殊指令集兜底 `unroll8_memcpy`（`gdrapi.c:1072`）。

## 五、设计决策

- **非临时指令是性能核心**：WC 映射的显存若用普通 memcpy 会把 CPU cache 行打脏；SSE 内核用 `_mm_stream_ps`（实证 `memcpy_sse.c:126`）等流式 store 绕过 cache。变体族覆盖 SSE/AVX/AVX2/AVX512/NEON/ST64/LS64/MOVDIR64B，同构"一份指令集一个文件"，运行时选最优——这是典型的"编译期矩阵 + 运行时单选"模式。
- **双后端共存而非替换**：dma-buf 是无内核模块的世界（依赖较新 CUDA），gdrdrv 是全功能路径（回调/BAR1/协商）；探测逻辑集中在 open 阶段，API 层完全透明。
- **能力协商而非大版本锁**：`gdr_get_attribute`（`gdrapi.c:1542`）+ 各 `GDRDRV_MINIMUM_VERSION_WITH_*` 闸，让旧驱动+新库组合降级可用。
- **日志分级**：`gdr_msg`（`gdrapi.c:72`）受环境变量控制级别，排障先开 GDRCOPY_DEBUG。

## 六、新人提示

从 `include/gdrapi.h` 的函数原型清单切入最快；内部头 `gdrapi_internal.h` 的 `gdr_t`/`gdr_memh_t` 是理解双后端的钥匙。改拷贝性能先读 `aligned_copy`（`gdrapi.c:1237`）与两个 internal 的分档逻辑，再对照具体 `memcpy_*.c`。注意图谱甄别：`cuda_wrapper.c` 的函数表条目（`cuda_wrapper.c:45-48`）中 45-48 是 struct 定义、50 行才是变量声明，静态函数表+dlsym 逐符号填充是它的全部模式；`gdr_close`（`gdrapi.c:250`）会通知驱动减引用，忘记 unmap 直接 close 也能回收但绕过统计。
