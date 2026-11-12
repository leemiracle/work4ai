# 讲透 NVIDIA/nvloom（MNNVL fabric 测试工具）

| 产物 | 状态 | 位置 |
|---|---|---|
| DeepWiki | ✅ 15/15 页 TRUE_100（2026-10-26 抓取） | [deepwiki/](deepwiki/) |
| understand 图谱 | ✅ 108 节点 / 225 边 / 4 层 / 6 步导览，0 issues，fingerprints 23 文件 @ `c2995c1e` | 仓内 `.understand-anything/knowledge-graph.json` |
| ONBOARDING | ✅ 7 节 | [onboarding/ONBOARDING.md](onboarding/ONBOARDING.md) |
| explain | ✅ 2 篇 | [explain/01-分配器26类型族.md](explain/01-分配器26类型族.md) ｜ [explain/02-kernel家族与引擎.md](explain/02-kernel家族与引擎.md) |

仓库一句话：**library+CLI 双形态的 MNNVL fabric 跨节点测试工具**（v2.2.0，2026-10-19）——9 大测试套件 × CopyType 18 形态 × 三分配策略的测量空间，MPI 每 GPU 一进程（72 GPU GB200 域 = 18 节点 × 4 进程），覆盖 SM/TMA/组播/CFT/EGM 全部 NVLink fabric 访问形态，内建数据校验与 spin-kernel 负载保温。

## 勘误清单（源码实证，2026-11-09 核实）

1. **CONTRIBUTING.md 不是空文件**：图谱节点与批阶段笔记都记"0 字节空文件/贡献指南占位"。实测文件为 **90 字节单行文本**："While we appreciate your enthusiasm, we have decided not to accept external contributions."——scanner 的 sizeLines=0 只是"无换行符的单行文件"行数口径，把它读成 0 字节是字节/行数混淆。结论不变（拒绝贡献）但证据形态完全不同。
2. **CopyType 是 18 个枚举值不是 19**：图谱 L02 摘要记"19 种拷贝形态"。实测 `library/enums.h:25-46` 的枚举体恰 **18 个** `COPY_TYPE_*` 值（CE、LOCALIZED_CE、SM、组播×4、LATENCY、TMA×4、CFT×7，另有 2 行是注释）。`grep -c "    COPY_TYPE"` 双口径验证均为 18。
3. **"sm90-107 四架构"有工具链前提**：`library/CMakeLists.txt:46-49` 只在 **CUDA 编译器版本 ≥13.4** 时编 `90;100;103;107`，否则退回 `90;100;103` 三架构。引用"四架构支持"须带条件，否则旧工具链用户会误判二进制能力面。
4. **"72 GPU = 18 节点×4"是运行约定推论不是代码常量**：README.md:66 的数字来自"每 GPU 一进程"约定对 4-GPU GB200 节点的算术，nvloom 代码里不存在 72/18/4 任何硬编码——拓扑由 `discoverRanks`（`cli/util.cpp:84`）运行时按 hostname 聚类发现。引用时别说"支持 72 GPU 上限"。
5. **"26 类继承树"口径需精确化**：`library/allocators.h` 实测 25 个 `class` + 1 个 `struct`（MemoryChunk，`:40`）；且 Pools（`:31`）、RangeAllocator（`:185`）、UnicastLogicalEndpoint（`:204`）等并非 MemoryAllocation 后代——真正单一根的继承树约 20 类，其余是组合器/池（AllocationPool `:444`、MulticastPool `:474` 虽继承根类但角色是包裹器）。
6. **kernels.cu 的 12 个 kernel 全为手扫节点**：tree-sitter 对 .cu 文件零提取（图谱方法论注记），12 个 `__global__` 行号（`:64/:116/:300/:517/:562/:605/:706/:747/:812/:886/:905/:927`）系人工扫描并经主会话复核——引用这些锚是可靠的，但图谱里 kernel 节点的 fanOut 等拓扑指标不完整属预期。
7. **Dockerfile 是"样例"非部署路径**：文件注释与 README 均注明仅为 sample（builder 用 ghcr.io/astral-sh/uv 装 Python 工具链，`Dockerfile:4/17-19`）；运行 nvloom 不需要容器化，README.md:66 的裸 MPI 启动才是主路径。
8. **JSON 输出是实验特性**：v2.2.0 CHANGELOG 明言 "Experimental feature, subject to change"（`CHANGELOG.md:9`）——把 `--jsonOutput` 当稳定接口做自动化有兼容风险，CSV 才是稳定契约。

## 本目录导航

- 想懂测量空间坐标系（套件/CopyType/策略）→ onboarding 第一、四、六节；
- 想学 CUDA VMM 多节点编程 → explain 01（26 类型分配器族 = CUmemAllocation 系 API 的系统应用）；
- 想懂 TMA/组播/CFT kernel 与 warmup/保温机制 → explain 02；
- 跑大规模域 → onboarding 第七节三件套建议（gpu-to-rack / rack-to-rack / fabric-stress）与 3 秒冒烟用例 bisect_write_sm（README.md:116）。
