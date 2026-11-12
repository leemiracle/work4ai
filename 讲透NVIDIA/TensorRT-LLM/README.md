# 讲透 TensorRT-LLM（NVIDIA/TensorRT-LLM）

> 仓：/usr-data/data2/repos/agent-repos/NVIDIA/TensorRT-LLM @ b75bcd1458048d5f61f0e45c5f3211e2b87e33f2（2026-10-01）
> 定位：NVIDIA 官方 LLM 推理引擎——PyTorch 原生执行路径 + 共享 C++ 核心（调度/批处理/KV 管理）+ PyTorch 后端之外的 VisualGen 视觉生成第二战场 + agentic 贡献生态。全仓 ~2855 分析文件（C++/Python/CUDA/CuTe DSL）。

## 全链状态表

| 阶段 | 状态 | 产物 |
|------|------|------|
| DeepWiki | ✅ 103/103 页 100%（2026-10-26 抓取） | `deepwiki/`（103 内容页 + INDEX + _coverage-check + wiki_full） |
| understand 图谱 | ✅ **7262 节点 / 17517 边 / 16 层 / 16 步 tour**，validator **0 issues 0 warnings** | 仓内 `.understand-anything/knowledge-graph.json` |
| fingerprints | ✅ 2855 文件基线 @ b75bcd1458048d5f61f0e45c5f3211e2b87e33f2 | 仓内 `.understand-anything/fingerprints.json`（支持增量更新） |
| ONBOARDING | ✅ 八节中文导览 | `onboarding/ONBOARDING.md` |
| explain | ✅ 12 篇（六节结构，行号锚全源码核实） | `explain/01-…md` ~ `12-…md` |

图谱 16 层速览：L01 服务入口与 LLMAPI · L02 模型库百家谱 · L03 VisualGen · L04 注意力后端与 KV 压缩 · L05 MoE · L06 投机解码与 pyexecutor · L07 分离式推理与跨节点传输 · L08 scaffolding/agent-flow · L09 Python 核心库与 _torch 基础 · L10 CuTe DSL 与 Triton 高层算子 · L11 C++ 引擎核心 · L12 KV Cache V1/V2 双体系 · L13 fmha_v2 与 xqa kernel 仓 · L14 thop 算子库与 cutlass_extensions · L15 agent skills 生态 · L16 基准评测与构建文档。

## explain 索引（12 篇）

| # | 篇 | 覆盖 |
|---|----|------|
| 01 | llmapi 服务入口 | LLM API 主链路（组 1） |
| 02 | 模型库百家谱 | _torch/models 模型实现族（组 1） |
| 03 | VisualGen 视觉生成 | DiT 生成线（组 1） |
| 04 | 投机解码全家族 | DFlash/DSpark/EAGLE3/MTP（组 1） |
| 05 | MoE 体系 | 契约与四变体后端（组 1） |
| 06 | 注意力后端谱系 | backends 家族与 metadata 契约（组 1） |
| 07 | disagg 与传输 | transfer.py 4588 行双层状态机 + Bounce 信用流控 + openengine/smg 双 gRPC（组 2） |
| 08 | KV Cache V1/V2 双体系 | V1 4647 行块管理 / V2 三层存储 + BlockRadixTree sha256 安全红线（组 2） |
| 09 | fmha_v2 全世代 tile | SM70-120 六世代 + setup.py 6990 行生成中枢 + train_ops fprop/dgrad + Philox（组 2） |
| 10 | xqa 与 cutlass_extensions | mha_sm90 3710 行/gmma_impl 4591 行/自足 type_traits + weight-only 家族 + multimem/red 指令（组 2） |
| 11 | thop 通信与 MoE 算子 | allreduce NVLS/GB200 拟合阈值 + mhcOp（V4 暴露面）+ 99 处 TORCH_LIBRARY（组 2） |
| 12 | agentic 生态 | scaffolding 五 Worker + agent-flow 四工作流 + .claude 11 agents/28 skills + casebook 三文件协议（组 2） |

## 勘误清单（盘上/源码实证，≥10 条）

1. **moeOp.cpp 路径**：thop 根目录无 moeOp.cpp；真实位置 `cpp/tensorrt_llm/thop/moe/cutlass/moeOp.cpp`（2509 行）。按直觉在 thop 根找 MoE 入口必扑空。
2. **transfer.py 双文件**：4588 行的双层状态机巨文件是 `tensorrt_llm/_torch/disaggregation/native/transfer.py`；`base/transfer.py` 仅 220 行（SenderBase/ReceiverBase 契约层）。两个同名文件，锚定必须带目录。
3. **KV V1/V2 并存实证**：V1 `kvCacheManager.cpp` 4647 行（163 处成员函数定义，图谱口径 167 含少量内联）与 V2 `kv_cache_manager_v2/`（31 文件）**并存非替换**；图谱节点 V1 侧 21 / V2 侧 110，运行时由 `pyexecutor/_util.py` 特性开关（`resolved_kv_cache_manager_is_v2` 等函数）选择。
4. **全仓最大 CuTe DSL 文件**：NOTES-DIGEST 称 gvr_topk_decode_self_sampling.py（6828 行）最大——实测其姊妹 `gvr_topk_decode.py` 8507 行更大；CuTeDSL 树合计 161,273 行。引用"最大文件"以前者为准需更正。
5. **step 节点矛盾裁定**：digest 批注称 fmha_v2 Makefile 的 all/dirs/clean 提取为 steps 子节点；**终态图谱 step: 节点 0 个**，Makefile 仅 2 个以 `pipeline:` 类型入图（fmha_v2 与 train_ops），xqa/nvrtc 与 enroot 的 Makefile 是普通 file 节点。裁定：Makefile targets 未入最终图，以图谱终态为准。
6. **cpp include 双树**：公共头树 `cpp/include/`（171 图节点）与实现树 `cpp/tensorrt_llm/` 之间 **738 条跨树边**——公共头以 `tensorrt_llm/...` 路径被实现树 include，任何锚定/寻址须双根解析；这是图上最密的 C++ 跨树耦合带。
7. **.xlsx 数据载荷**：`cpp/kernels/xqa/mha_sm90_transpose.xlsx` 被 scanner 归为 code——实为 mha_sm90 转置排布的**设计记录数据**（无代码语义、不参与构建），explain 10 已按设计底稿引用。同型：`deep_ep/nvshmem_src_3.2.5-1.txz` 为 vendored 源载荷非代码单元。
8. **TORCH_LIBRARY class_ 注册盲区**：tree-sitter 对 `torch::class_` 注册零提取；全仓**唯二** class_ 注册 = `FusedMoeRunner`（moeOp.cpp:2501）与 `CublasLtFP4GemmRunner`（cublasFp4ScaledMM.cpp:464），均为批阶段手补节点。Python 侧同型盲区：`@torch.library.custom_op` 嵌套函数（flashinfer_custom_ops.py 9 个算子手补）。
9. **templatedTrie.h 零提取**：batch 114 对 618 行纯模板头 `cpp/include/tensorrt_llm/batch_manager/templatedTrie.h` tree-sitter 零提取，Node/Trie 符号经手扫补齐（图谱 file+class 节点在档）——模板头是 scanner 结构性盲区，同批还有 smem_tile.h（hopper）、scheduler.cuh。
10. **triton_kernels vendored v3.8.0**：顶层 `triton_kernels/` 是从 triton-lang/triton v3.8.0 整体 vendored 的副本；**升级走重新 vendoring 而非就地修改**（批注钉版）。
11. **usage 自引用合规过滤**：`tensorrt_llm/usage/architecture_allowlist.py` 的 `PUBLIC_MODEL_ARCHITECTURES` frozenset 是遥测可明文上报的架构名单（隐私 allowlist，注释明言"故意保守、禁加私有/客户名"）；`usage_lib.py` 匿名遥测走 NvTelemetry/GXT 后台守护线程。AGENTS.md 规定新增公共架构标识必须同步更新该文件——这是仓的合规闸门而非普通数据文件。
12. **fmha_v2 世代覆盖**：sm2name 映射实际 70-120（70/72 volta、75 turing、80/86/87 ampere、89 ada、90 hopper、120 blackwell），"SM80 起"的说法漏了 volta/turing 两档（setup.py:21-33 实测）。
13. **BlockRadixTree 哈希红线**：BlockKey 必须是全长 SHA-256（blockRadixTree.h:67-79 SECURITY INVARIANT：前缀匹配纯靠摘要相等、不复核 token，cache_salt 隔离完全押在碰撞阻力上）——任何"换 xxHash/截断提性能"的提议在该数据结构上是**安全违规**而非优化。
14. **thop 注册面口径**：106 文件中 99 个含 TORCH_LIBRARY 注册；统一三段式 FRAGMENT + IMPL(CUDA) + IMPL(CompositeExplicitAutograd)。引用 thop 规模时以 99 为准（另 7 个是纯头/工具）。

## 图谱与工具链备注

- 校验：validate-report.json = `{issues: [], warnings: [], stats: 7262/17517/16/16}`。
- 增量：fingerprints 2855 文件基线支持后续 commit 增量更新（参考 vLLM 手术合并范式）。
- 台账：批阶段甄别笔记 211 条全收 `.understand-anything/NOTES-DIGEST.md`（intermediate 已清理，digest 为批产物唯一存档）。
- explain 字数口径：不计空格总字符；行号锚以仓 @ b75bcd1458 为基准，抽验命中记录在各篇写作过程。
