# 01 · src/nccl.h.in — NCCL 的公共 API 面（构建模板版头文件）

## 一、角色定位

`src/nccl.h.in`（1025 行）是 NCCL 对外世界的全部契约：句柄类型、错误码、版本宏、communicator 生命周期函数、集合通信原语及 `*Config` 变体、window/param 访问接口。Makefile 说得很死："The only public headers are nccl.h and nccl_device.h"（`src/Makefile:11`）。后缀 `.in` 表明这是**构建模板**而非可用头：版本占位符 `${nccl:Major}` 等（`src/nccl.h.in:20-25`）在构建时替换成真值——make 路径用 sed（`src/Makefile:159-165`，版本源头 `makefiles/version.mk:10-13`）；CMake 路径用 `src/generate_header.cmake:8-12` 的 `string(REPLACE)`，注释明说替代 sed 是为兼容 Windows。仓库里不存在现成 `src/nccl.h`，知识图谱因此把全库 70 个文件的 `#include "nccl.h"` 都归并到 `src/nccl.h.in` 实体上。

产品形态也在此定格：C ABI 库（`extern "C"`，`src/nccl.h.in:28-30`），单一 `.so` 只导出 `nccl*` 与 `pnccl*`（`src/libnccl.map:15-16`），其余 `local:*`，改导出须团队批准（`src/libnccl.map:2-8`）。

## 二、内部结构

**1) 版本与基础类型（20-58 行）。** `NCCL_VERSION(X,Y,Z)` 藏着 ABI 妙笔：`(X)<=2 && (Y)<=8` 按千进制、之后改万进制（`src/nccl.h.in:26`）——老公式必须保留，否则老应用的编译期比较静默错乱。`ncclUniqueId` 是 128 字节不透明体（`src/nccl.h.in:40-41`），实际装 `ncclBootstrapHandle{magic,addr,nRanks}`（`src/include/bootstrap.h:14-18`）。

**2) 版本化配置结构族（102-257 行）。** `ncclConfig_t` 真名 `ncclConfig_v23100`（`src/nccl.h.in:104`），头部 `size/magic/version` 用户不可触碰（`src/nccl.h.in:105-108`），必须用 `NCCL_CONFIG_INITIALIZER` 初始化（`src/nccl.h.in:137`）——magic 固定 `0xcafebeef`（`src/nccl.h.in:61`）。新字段只允许尾部追加：v2.32 的 `hostCftMode/nvlsHostMode` 等全在尾部（`src/nccl.h.in:129-132`）。同族 per-call 的 `ncclCollConfig_v23200`（`src/nccl.h.in:193-222`：`algSelection` 算法过滤、`launchCompletionEvent` kernel 完成事件）与厂商扩展链表 `ncclConfigExt_t`（`src/nccl.h.in:173-184`，vendorId 自选随机数防撞，官方 NCCL 忽略所有 ext——给 kccl 这类厂商 fork 留的正规后门）。

**3) 生命周期与内存 API（262-471 行）。** communicator 全家桶：`ncclCommInitRank/All/Config`（`src/nccl.h.in:283-302`）、`ncclCommInitRankScalable`（每 rank 一个 uniqueId 加速建链，`src/nccl.h.in:365-370`）、`ncclCommFinalize/Destroy/Abort/Revoke`（`src/nccl.h.in:309-328`）、弹性族 Split/Shrink/Grow（`src/nccl.h.in:337-363`）及 window 注册（`src/nccl.h.in:415-466`）。

**4) 算子与类型（469-535 行）。** `ncclMaxRedOp` 用 dummy enum 钉死枚举宽度防编译器放大（`src/nccl.h.in:484`），给 `ncclRedOpCreatePreMulSum` 动态算子留值域（`ncclNumOps=5` 起，`src/nccl.h.in:475-478`）。12 种 datatype 含 fp8（`src/nccl.h.in:488-501`）。

**5) 集合原语（550-759 行）。** 9 个经典原语各配尾参 `ncclCollConfig_t*` 的 `*Config` 变体（`src/nccl.h.in:683-725`），plus `ncclSend/ncclRecv`；注释明说 in-place 判定（如 ReduceScatter 的 `recvbuff==sendbuff+rank*recvcount`，`src/nccl.h.in:616`）。

**6) 单边通信（762-842 行）。** v2.32 重头：`ncclPutSignal`（写远端注册 window+信号）、`ncclSignal`、`ncclWaitSignal`（按 `ncclWaitSignalDesc_t{opCnt,peer,sigIdx,ctx}` 数组等待，`src/nccl.h.in:818-823`）；window flags 有 `NCCL_WIN_GIN_ONLY/NCCL_WIN_CFT_COUNTED`（`src/nccl.h.in:64-72`）。

**7) Group/加密/参数访问（844-1019 行）。** `ncclGroupStart/End`（`src/nccl.h.in:866-892`）；`ncclSetEncryption` PSK（`src/nccl.h.in:899-923`，详见 04 篇）；v2.32 全新 param C API——handle 式 `ncclParamBind/GetI8..U64/GetStr/Get` 与 key 式 `ncclParamGetParameter/GetAllParameterKeys/DumpAll`（`src/nccl.h.in:938-1019`，见 02 篇）。

每对声明旁的 `pncclXxx` 不是手写重复：`PROFAPI` 编译期由 `NCCL_API` 宏生成 `p##func` 强符号别名 + weak 的 `func` 本体（`src/include/core.h:15-21`）——profiler 可 preload 覆盖 weak 符号插桩，同时经 `pnccl*` 永远调得到真实现。

## 三、外部连接

- **被包含**：图谱口径 70 个文件 import `nccl.h`（实体=`src/nccl.h.in`）。它只 include CUDA 头（CUDART≥11000 加 bf16、≥11080 加 fp8，`src/nccl.h.in:11-18`）与 stdint/limits，零内部依赖——最底层头必须自持。
- **谁实现**：init 族在 `src/init.cc`（`ncclCommInitRankConfig` 声明于 `src/nccl.h.in:283`，实现 `src/init.cc:3047`）；集合原语在 `src/collectives.cc:206-212`（ncclAllReduce 转发 ConfigImpl）；param C API 在 `src/param/c_api.cc:55`；`ncclSetEncryption` 在 `src/misc/crypt.cc:460`。
- **构建侧**：`src/Makefile:156-166`、`src/generate_header.cmake:5-14`、`makefiles/version.mk:10-13`。

## 四、数据流

用户典型流：`NCCL_CONFIG_INITIALIZER` 初始化 config → rank0 `ncclGetUniqueId`（实为 bootstrapGetUniqueId，`src/init.cc:208-222`）→ uniqueId 经 MPI/文件广播 → `ncclCommInitRankConfig` → 之后 `ncclAllReduce(...)` 只把指针入队 CUDA stream，返回即"已 enqueue"，CPU 不等 GPU（`src/nccl.h.in:543-547`）。

模板数据流是一次性的：version.mk → sed/cmake → `$(INCDIR)/nccl.h` 定型。**直接拿 `nccl.h.in` 当头用会得到 `${nccl:Major}` 非法 C 代码**——下游 fork 原样拷贝而未跑替换是经典事故。

所有权约定：`ncclCollConfig_t` 用户拥有存储且须在调用期间保持 struct 与 ext 链表存活（`src/nccl.h.in:189-192`）；`ncclParamGetStr` 返回指针只在同线程下次调用前有效（`src/nccl.h.in:977-983`，实现是 thread_local buffer，`src/param/c_api.cc:109-111`）。

## 五、设计决策

1. **模板而非写死版本**：版本值单点维护于 version.mk，头文件、`ncclGetVersion` 返回值、config.version 校验全库同步，杜绝头与 so 漂移；sed/cmake 双路径是 Windows 兼容的代价。
2. **append-only + size/magic/version 三件套**：C 结构体跨版本 ABI 兼容的标准解法——库侧按 `config.size` 判断调用方结构大小，字段只尾追不重排（`src/nccl.h.in:186-192` 显式承诺）；magic 把"忘用 INITIALIZER"变成可诊断错误而非内存乱读。
3. **weak/strong 双符号**：可插桩与"总有一条真路径"同时满足，零运行期开销；**新能力走 `*Config` 变体而非改老签名**——`config==NULL` 等价老 API（`src/nccl.h.in:683-686`），老 ABI 寸步不动。
4. **`NCCL_VERSION` 公式断层**（`src/nccl.h.in:26`）：不为优雅，为不背叛 2.0-2.8 时代已编译进用户二进制的比较逻辑。

## 六、新人提示

- 改 API 先读 `src/libnccl.map:2-8` 警告：加导出符号、改签名、结构体中间插字段，三类都是 ABI 事故，牢记 append-only。
- 排查"config 没生效"：先确认用了 `NCCL_CONFIG_INITIALIZER`（magic 校验在 `src/init.cc:2572` 的 parseCommConfig；**2026-11-03 勘误**：原记 :2558，verify-deepseek 锚点复核实测 +22 漂移）；再确认不是新字段配旧库——旧库必忽略尾部新字段。
- 找 API 实现：`grep -rn "NCCL_API(ncclResult_t, ncclXxx" src/` 一步命中；实现文件里那行宏声明不是注释，它负责 visibility 与 pnccl 别名（`src/include/core.h:15-31`）。
- 调"版本号不对"直接查 `makefiles/version.mk`；构建产物 nccl.h 不入库。延伸：03 篇生命周期、04 篇 uniqueId、02 篇 param C API。
