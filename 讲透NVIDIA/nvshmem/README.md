# 讲透 NVIDIA/nvshmem——总索引与状态表

> 仓：`/usr-data/data2/repos/agent-repos/NVIDIA/nvshmem`（本地 clone，commit `7bb2e99c619677c0ba94fb64cadcf660ccf7884b`，2026-11-09 分析）
> NVSHMEM = OpenSHMEM PGAS 模型的 GPU 延伸：宿主/CUDA kernel/CUDA stream 三身份发起通信，对称堆+设备直通（IBGDA 直造 WQE）+NVLS 多播归约。

## 状态表

| 产物 | 状态 | 说明 |
|---|---|---|
| deepwiki | ✅ 37 页全量 TRUE_100 | MCP 通道抓取 2026-10-26，全文 857,940 字符（`deepwiki/INDEX.md`，含 x1 CuPy/x2 PyTorch/x3 起结构外页） |
| understand 图谱 | ✅ 1458n / 3529e / 16 层 / 16 步 | validator 0 issues 0 warnings；fingerprints 基线 1043 文件@`7bb2e99c`；节点构成 file 771/function 383/config 184/document 88/class 32；边构成 imports 2412/contains 414/exports 322/tested_by 101/related 98/configures 89/depends_on 76/documents 16/inherits 1 |
| NOTES-DIGEST | ✅ 81 条 | 批阶段甄别笔记收割（仓内 `.understand-anything/NOTES-DIGEST.md`） |
| onboarding | ✅ | `onboarding/ONBOARDING.md`，8 节，不计空格 8,200+ 字符，文件锚 100 处（唯一文件 79，行号锚 30+） |
| explain | ✅ 6 篇 | 六节结构（角色定位/内部结构/外部连接/数据流/设计决策/新人提示），每篇 2,100-2,600 字符（不计空格），行号锚 12+ |

## explain 索引

1. [01 公开 API 与 init 链](explain/01-公开API与init链.md)——nvshmem.h 22 行伞头的双编译分流 + init.cu 2482 行启动链
2. [02 bootstrap 四插件与对称堆](explain/02-bootstrap四插件与对称堆.md)——婚介所（mpi/pmi/pmix/shmem+uid）+ dlmalloc 6419 行
3. [03 proxy 与宿主 RMA](explain/03-proxy与宿主RMA.md)——8 字节槽位协议 + proxy.cpp:1469 命令分派
4. [04 传输插件六族](explain/04-传输插件六族.md)——transport.h ops 表 + ibgda 设备直造 WQE
5. [05 设备算法与 NVLS](explain/05-设备算法与NVLS.md)——reduce.cuh 2739 行 multimem 多播 + team/NVLS 资源
6. [06 Python 三后端与 vendored](explain/06-Python三后端与vendored.md)——numba/mlir/cute 三后端 + gpunetio vendored

## 勘误清单（源码实证，10 条）

1. **scanner batchImportData 对本仓全空**——1043 文件的 C/C++/CUDA/Python 混合仓，import/include 解析零产出，2,412 条 imports 边全部由批阶段子代理从源码手扫对账（1,718 条含 include/python import 双路重扫），图谱 imports 层可信度依赖该人工层。
2. **"三个 vendored"实为五处第三方代码**——vendored 大件三处（MPICH pmi-2：`src/modules/bootstrap/pmi/pmi-2/pmi2_api.c` 2187 行；Doug Lea dlmalloc 2.8.6：`src/host/mem/dlmalloc.cpp` 6419 行，出处注释在 :6-11；DOCA GPUNetIO：`externals/gpunetio/` 66 节点），另有小件 NCCL 拷贝（`bootstrap/uid/ncclSocket/`，ncclsocket_* 前缀保留+重映射隔离）与 nvtx3 单头（`src/include/internal/host/nvtx3.hpp`）。审阅/改动这些区域前先认出血统。
3. **两枚 LFS 指针勿当源码**——`nvshmem4py/nvshmem/bindings/device/numba/_numbast.py`（oid sha256 53ed32a2…，size 3,931,716）与 `numba_cuda_mlir/_numbast.py`（oid a82143e2…，size 4,295,068）在仓内只有 3 行指针文本；两枚 oid/size 均不同（非同一文件两份拷贝）。DeepWiki/图谱对它们的描述均基于文件名推断。
4. **nvshmem_linux.pyx 是 nvshmem.pyx 的逐字节复制体**——两文件均 7,859 行，`diff -q` 实证相同；是平台别名（构建期选择）而非独立实现，改一处必须同步另一处。
5. **mlx5_ifc.h 双副本已漂移**——`externals/gpunetio/include/gpunetio/host/mlx5_ifc.h`（5,699 行）与 `src/modules/transport/common/mlx5_ifc.h`（5,542 行）同源但相差 157 行，"同源拷贝"说法不精确；两份均零函数纯布局映射（tree-sitter 提取为空属预期）。
6. **宏展开生成器口径**——`src/host/coll/rdxn/rdxn.cpp` 全文件 37 行，靠 `DEFN_NVSHMEM_TYPENAME_OP_REDUCE`（rdxn.cpp:16）× 三族类型表宏（BITWISE rdxn.cpp:29-31 / STANDARD :33-34 / ARITH :36-37）展开出上百符号；reducescatter.cpp 与 on-stream 族同构。"某文件很小但符号很多"先查宏生成器，勿按行数估工作量。
7. **批笔记的 "(NNNL)" 是函数长度非行号**——NOTES 中 `PMI2_Init(171L)` 实为"长 171 行、起于 pmi2_api.c:183"；`init_team_pool_and_psync(121L)` 实为"长 121 行、起于 team_internal.cpp:1478"。照抄当行号会定位到无关代码。
8. **"create_keyval 单函数 777 行"不实**——批阶段笔记高估；实测 create_keyval 仅 33 行（pmi2_api.c:1411-1443），pmi2_api.c 真正最长函数是 PMIi_ReadCommand（187 行，pmi2_api.c:1447）。
9. **bootstrap "四插件"口径不完整**——`src/modules/bootstrap/` 实为 5 插件目录+1 公共目录：mpi/pmi/pmix/shmem 四主族之外还有 uid（socket 直连，无作业系统场景），另有 common 共用握手工具。README.md:42-57 的三种启动方式只覆盖 mpi/pmi 两族。
10. **perftest 标准场景是 7 个 .list 非 8 个**——`perftest/` 下唯一 .list 文件为 ib/mmap-full/mmap-sanity/p2p-cudagraph/p2p-nvlink/p2p-pcie/region 共 7 个（图谱层描述写 8）。

## 甄别精选（补充事实，非勘误）

- **ibgda 的宿主 ops 表 rma/amo 显式为 NULL**（ibgda.cpp:5310-5311）——声明式路由"数据面全在设备"（ibgda_device.cuh:309 直造 WQE），读宿主插件别找 RMA 实现。
- **proxy 命令 = 四类数据命令 + 三类控制命令**（proxy.cpp:1469-1531）：DMA(PUT/GET)、inline P、AMO、PUT_SIGNAL + FENCE/QUIET/REGION_END，各带 _QP 批量变体。
- **传输插件数硬编码 6**（transport.cpp:31 `NVSHMEM_TRANSPORT_COUNT 6`）：ibgda/ucx/libfabric/gpunetio/ibrc/ibdevx；节点内 p2p 不走插件。
- **test/unit 链接期符号替换法**：重定义 cudaMalloc 等为本地桩实现无 GPU 单测；`test/unit/mem/heap/internal/host/nvshmemi_mem_transport.hpp` 是 src 头的测试树拷贝（隔离手段，非第二实现）。
- **nvshmem.h 伞头仅 22 行**：价值在 nvshmem.h:13-21 的条件编译分流（RTC/宿主/hostlib 三态），不在行数。

## 口径说明

- 字数口径=不计空格字符（中文场景本仓 explain 实测 2,114-2,561/篇，onboarding 8,207）。
- 行号锚格式 `路径:行号`，全部经源码 `grep -n`/函数边界解析独立核实（2026-11-09）；简写 `:N` 指同段落前一个具名文件。
- 图谱在仓内 `.understand-anything/knowledge-graph.json`（meta `lastAnalyzedAt` 2026-11-09T19:53:17+08:00）。
