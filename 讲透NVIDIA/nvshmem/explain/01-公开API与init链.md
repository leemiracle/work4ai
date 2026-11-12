# 01 公开 API 与 init 链——一个伞头如何撑起三种编程身份

## 角色定位

`src/include/` 是用户与库的第一契约层（图谱 L01，29 节点）。NVSHMEM 的公开面极简：用户只 include 一个 `src/include/nvshmem.h`，就能以宿主程序、CUDA kernel 设备线程、CUDA stream 三种身份调用同一套 OpenSHMEM 语义 API（README.md:7-10）。伞头本身只有 22 行（nvshmem.h:1-22），它是纯分流器：`#if !defined __CUDACC_RTC__ ... #include "nvshmem_host.h"`（nvshmem.h:13-18）在 NVRTC 运行时编译/LLVM bitcode/numba/LTOIR 四种设备态下剥掉宿主声明，`#if !defined NVSHMEM_HOSTLIB_ONLY`（nvshmem.h:20-21）又把设备定义留给 hostlib 场景——一次 include、三种身份的开关全在这两个条件编译块里。

## 内部结构

伞头之下三根支柱：宿主侧 `nvshmem_host.h`→`host/nvshmem_api.h`（511 行，nvshmem_init/finalize/malloc/put/get/quiet/barrier 全原型）；设备侧 `device/nvshmem_defines.h` 的 38 个 static inline 函数 + `nvshmem_coll_defines.cuh`；扩展侧 `nvshmemx.h` 聚合 tile API（类型基础在 `device_host/nvshmem_tensor.h:1-101`）、collective launch 与设备扩展。设备-宿主共用契约在 `device_host/`：`nvshmem_api_macros.h` 处理 RTC（nvcc -dc）与宿主编译双路径 include，`nvshmem_common.cuh`（208 行）聚合公共传输头，被 include 48 次。init 链的起点 `src/host/init/init.cu`（2482 行）：`nvshmemi_init_counter` 支持嵌套 init（init.cu:95 声明，:236/:1488 递增，:1585-1586 递减返回），多 GPU 设备库由 `registered_device_states` map+once_flag 管理（init.cu:66-68），API 前置检查报错文案锚在 init.cu:1425。

## 外部连接

init 的第一外部依赖是 bootstrap 插件（dlopen，见 02 篇）；第二是 CUDA/NVML 驱动符号——`cudawrap.h`（374 行）维护 cuMemMap/cuMemCreate/cuLaunch 系函数指针表，运行期 dlopen 而非链接期绑定；第三是环境变量中枢：`src/host/util/env_vars.cpp`（179 行）解析全部 NVSHMEM_*，契约登记在 `src/include/bootstrap_host_transport/env_defs_internal.h`（385 行，7 类 env 分类枚举位于 env_defs_internal.h:24-31，SYMMETRIC_SIZE 默认 1GB 在 env_defs_internal.h:37）。诊断出口是 `nvshmem-info` CLI 与 NVSHMEM_DEBUG=INFO（README.md:61）。

## 数据流

启动序列：用户调 `nvshmem_init` → init.cu 解析 env（env_defs_internal.h 的登记表+env_vars.cpp 的解析器）→ bootstrap 握手拿 rank/size 与端点信息 → CUDA 设备状态注册（init.cu:163-167 的 registered_device_states.emplace）→ 对称堆建立 → 传输插件装载（transport.cpp:229 调 nvshmemt_init）→ 设备库（bitcode→LTOIR 链，装载点见 `src/device/init/init_device.cu`，其 Clang CUDA `__constant__` 适配注释是工具链钉版）→ counter+1 后返回。设备 API 调用则在 kernel 内直接走 `non_abi/device/` 的内联实现，不经宿主。

## 设计决策

三个值得学习的决策：其一，**伞头分流而非多入口**——用户心智模型只有 nvshmem.h，编译模式差异由宏吸收，代价是 nvshmem.h:13-21 的条件链成为全仓最敏感的修改点；其二，**驱动符号 dlopen 解耦**——wheel 包能在无 GPU 机器安装、能容忍驱动版本漂移；其三，**嵌套 init 计数**——上层框架（如 Python 的 init_fini）可安全重复初始化，init.cu:1585-1586 的递减守卫保证只有最外层 finalize 真正拆库。

## 新人提示

读 init.cu 时先抓三条线：counter、registered_device_states、bootstrap handle 的生命周期；改动公开 API 时必须同时检查 nvshmem.h 的两个条件块与 `nvshmem_host.sym` 导出表（nvshmem_*/nvshmemx_*/nvshmemid_* 三前缀）；新增环境变量只改 env_defs_internal.h 的 NVSHMEM_ENV 登记表，env_vars.cpp 的解析器是通用的。设备 API 的 38 个 static inline 在 nvshmem_defines.h，是设备侧一切展开的底座。
