# 讲透 NVIDIA/AMGX（AmgX GPU 加速代数多重网格求解器库）

> 源码仓 `/usr-data/data2/repos/agent-repos/NVIDIA/AMGX` @ commit 91a8413（v2.5.0，"Fix CUDA 13 tuple compatibility"）。
> 知识基座为 understand 图谱 + DeepWiki 快照 + 全量 explain 精讲，行号锚均从源码核实。

## 状态表

| 阶段 | 状态 | 产物与口径 |
|---|---|---|
| DeepWiki | ✅ 完成 | `deepwiki/` 46 内容页（结构 25 全命中+21 结构外增量，**真一百分**终判；wiki_full.md 862K 全文快照；抓取 2026-10-26，MCP 通道）|
| understand 图谱 | ✅ 完成 | 仓内 `.understand-anything/knowledge-graph.json`：**1233 节点 / 3136 边 / 15 层 / 16 步 tour / validator 0 issues**；fingerprints **661 文件 @ 91a8413e**；节点构成 file 582 / function 385 / class 187 / config 73 / document 6 |
| onboarding | ✅ 完成 | `onboarding/ONBOARDING.md`（约 2.4 万字符，8 节，2026-11-06）|
| explain 组 1（篇 1-6）| ⏳ 进行中 | 并行实例撰写（盘上已见 `explain/01-amg.cu-AMG_Setup主流程.md`），主线=AMG 三变体/层级/循环/选择插值/聚合线 |
| explain 组 2（篇 7-12）| ✅ 完成 | 本轮 6 篇，求解器/基础设施线，见下索引 |
| NOTES-DIGEST | ✅ 完成 | 仓内 `.understand-anything/NOTES-DIGEST.md`（36 条批阶段甄别笔记）|

## explain 索引

| 篇 | 文件 | 主题 |
|---|---|---|
| 07 | `explain/07-求解器家族与工厂.md` | solver.h 310 行契约+静态注册表工厂；Krylov/松弛/多项式 28 头；core.cu 集中注册；block_common 纯函数层 |
| 08 | `explain/08-Matrix与算子层.md` | matrix.h 1361 行三段式（MatrixBase/host/device 特化）；Operator 根与四个派生算子；cuSPARSE 挂点；generic_spmv_csr 内核 |
| 09 | `explain/09-cusp内嵌库.md` | vendored cusp v0.3.0；五格式容器+krylov/precond/gallery 用户面；dispatch 编译期路由；scipy 同源参考实现面 |
| 10 | `explain/10-分布式通信层.md` | DistributedManagerBase 账本；CommsMPI 三层；访问者模式 24 struct；ETI 四清单；GPUDirect 继承式回退 |
| 11 | `explain/11-C-API门面.md` | 72 个导出声明；AMGX_Mode 位组合 ABI；amgx_c.cu 49 处 switch 的 CASE_LINE 宏分派范式 |
| 12 | `explain/12-着色特征值与测试.md` | 11 着色头 10 注册名；eigensolver 工厂 9 名 7 类；testframework 四件套+60 .cu；哈希链确定性检验 |

## 勘误清单（源码核实）

以下为 explain/图谱生产过程中发现的口径修正与源码级勘误。1-8 为本轮独立核实，9-12 为批阶段甄别笔记钉版（intermediate 已随 finalize 清理，按 NOTES-DIGEST 口径转录）：

1. **block_common_solver.h 图谱摘要函数名失实**：摘要称含 blockAddTail/blockScalarNorm 等 free function——两个名字全仓（include/+src/）**零命中**；实际内容是六个块求逆模板 `compute_block_inverse_{row,col}_major*`（`include/solvers/block_common_solver.h:106-341`）。383 行零 class 属实。
2. **amgx_c.h "81 个导出"口径错误**：81 是 `AMGX_API` 字符串原始 grep 命中数，含 9 行宏定义/条件编译上下文（`amgx_c.h:8-26`）；真实导出声明（`AMGX_RC AMGX_API AMGX_xxx` 形态）为 **72 个**（L150-L603）。
3. **amgx_config.h 复数 mode 行尾注释为复制粘贴错值**：`amgx_config.h:116-118` 的 hZZI/hZCI/hCCI 注释写 `// mode == 8192/8448/8464`（与 DDI 系雷同）；**编译实测 hZZI=9008、dZZI=9009**（gcc 组装枚举验证）——枚举值本身正确，注释失真。
4. **DistributedManagerBase 行数口径**："2111 行大类"中 2111 是 `distributed_manager.h` 整文件行数；类本体 L194 起、至约 L1342（含 friend 区），其后还有派生内容；类体约 1149 行，仍是全库最大类之一。
5. **cusp 节点面计数口径**：任务口径"用户面 63+detail 87"与盘上不符——实测 267 节点=148 file（用户面 45+detail 103）+30 class（23+7）+**87 function（全部在 detail 参考实现）**；"87"疑为函数节点数误植为实现面总数。
6. **solvers 域"55 节点"口径**：include/solvers 实测 **42 节点**（28 file+14 class）；含 src/solvers 实现文件的全 solver 线共 200 节点。
7. **"11 种着色策略"实为 11 头 10 名**：include/matrix_coloring/ 13 头中 `bfs.h`（426 行）是 greedy 族共享的 BFS 遍历基础设施，**无独立工厂**；core.cu:669-678 注册 10 个名字。
8. **eigensolver 注册 9 名映射 7 类**：POWER_ITERATION/INVERSE_ITERATION/PAGERANK/SINGLE_ITERATION 四名共享 SingleIteration 工厂（`src/eigensolvers/eigensolvers.cu:38-43`）——工厂名与类解耦，按名计数会高估算法数。
9. **tree-sitter 对 .inl 文件盲区**（批阶段钉版）：amgx_c_wrappers.inl / hash_containers_detail.inl / hash_index.inl 结构为手工补扫；C 方言模板头提取率极低（约九成靠手补）。
10. **ETI 清单头无结构属预期**：comms_visitors1-4_eti.h 为纯显式实例化清单，tree-sitter 提取为空不是缺陷。
11. **scanner 归类修正已落地**：根/ src 两份 CMakeLists.txt 由 docs 改判 config（终图谱实测均为 config 节点）；`.understandignore` 是流水线自身裁剪清单被建为 config 节点，非 AMGX 运行时配置。
12. **AMG 前置声明不建类+模板参数特例**：`amg.h:11` 前置声明未生成 class 节点（正确），真身在 `amg.h:47-48`；AMG 是全库唯一以 3 个精度枚举作模板参数（而非 T_Config）的顶层类，按精度组合显式特化——读图谱继承边时勿套 T_Config 惯例。

## 双实例协作说明

explain 组 1（篇 1-6，AMG 主线）与组 2（篇 7-12，求解器/基础设施线）由两会话并行撰写；本 README 由组 2 会话于 2026-11-06 落盘，组 1 状态按当时盘上实证标注（⏳），组 1 完成后请更新本表。
