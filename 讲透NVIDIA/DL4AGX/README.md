# 讲透 NVIDIA/DL4AGX

NVIDIA 官方 DRIVE/Jetson AGX 深度学习部署案例集（13 个 AV 部署方案 + 3 个硬件友好模型 + 2 份方法论指南）的全链知识库。

## 全链状态表

| 阶段 | 产物 | 状态 |
|---|---|---|
| understand 图谱 | `/usr-data/data2/repos/agent-repos/NVIDIA/DL4AGX/.understand-anything/knowledge-graph.json` | ✅ 635 节点 / 837 边 / 14 层 / 14 步 tour / 0 issues / fingerprints 326 文件 @ 9f7b2910 |
| deepwiki | `deepwiki/`（先行轮 2026-10-26） | ✅ 13/13 页 TRUE_100（MCP 通道，121,758 字符，见 `_coverage-check.md`） |
| onboarding | `onboarding/ONBOARDING.md` | ✅ 8 节 / 10,561 字符（不计空格）/ 56 锚（自动终验 0 坏） |
| explain | `explain/` 5 篇 | ✅ 六节结构 / 每篇 12+ 锚 / 行号全部实测 |

## explain 索引

| 篇目 | 主题 |
|---|---|
| [01-vad-trt主线](explain/01-vad-trt主线.md) | export_eval 补丁族 + 插件三家族 + 时序双版本导出 |
| [02-bev_deploy双副本对照](explain/02-bev_deploy双副本对照.md) | 同源工具库 fork 漂移实例库（拼写/防护/包结构三类漂移） |
| [03-petr-trt与constantization](explain/03-petr-trt与constantization.md) | v1/v2 双导出 + 动态分支常量化手法 |
| [04-DCNv4与UniAD](explain/04-DCNv4与UniAD.md) | 三形态算子 + 7560 行 onnx-export 补丁 + TRT 友好算子库 |
| [05-enqueueV2V3与MTMI](explain/05-enqueueV2V3与MTMI.md) | DDSOutputAllocator 动态维度 + GPU+DLA 异构 |

## 图谱层结构（14 层）

L01 仓库门面与子模块地图 · L02 vad-trt 部署主线 · L03 bev_deploy 双副本漂移 · L04 vad-trt 插件三家族 · L05 petr-trt 主线 · L06 uniad-trt 导出线 · L07 enqueueV2/V3 双代 app · L08 dcnv4 算子三形态 · L09 mtmi GPU+DLA 异构 · L10 显式量化双案例 · L11 长尾案例 · L12 硬件友好模型 · L13 补丁资产库 · L14 构建系统与容器。

## 勘误清单（源码级实证，12 条）

写作期全部行号锚经源码复核，与图谱/笔记表述有出入处钉版如下：

1. **StaefulModuleTrt 上游拼写保留**：vad 版 `AV-Solutions/vad-trt/export_eval/bev_deploy/patch/inspect.py:158` 类名 `StaefulModuleTrt`（少一个 t）；petr 版同文件 `inspect.py:146` 已修为 `StatefulModuleTrt`。且 petr 版只修了这一处——`AutoStatufulModule` 在 vad:491 / petr:482 两版都拼错。NOTES-DIGEST 把 vad 版路径记为 `export_eval/patch/inspect.py`，实际在 `export_eval/bev_deploy/patch/inspect.py`。
2. **import inspect 自环误解析**：两份 bev_deploy 的 `patch/inspect.py:18` 均有标准库 `import inspect`，静态 import 解析会把同名本文件误连成自环边（图谱中 inspect.py 上的可疑自边属工具盲区，非代码问题）。
3. **uniad.hpp include-guard 自引用残留**：enqueueV2 与 enqueueV3 的 `include/uniad.hpp:28` 均有 `#include "uniad.hpp"` 自引用（在 include guard 保护下无害），两代同款复制痕迹。
4. **Dockerfile 归类改判**：scanner 把 Dockerfile 判为 code/language=dockerfile（bevformer-int8-eq 的 `docker/tensorrt.Dockerfile`）；petr-trt 的 `dockerfile` 无扩展名小写，被判 code/language=unknown。两者语义上均为 infra，图谱改发 service 节点（含 `:base` stage 子节点）。
5. **.ptx 是文本资产**：dcnv4PtxPlugin 下 5 个 .ptx（dcnv4_stage0_b1/b128、stage1-3_b1.ptx）是 Triton→PTX 工作流前身的汇编资产，运行时经 `dcnv4_ptx.cu:119` 等 `cuModuleLoadDataEx` 加载；受 README:109 尺寸白名单（5 种组合）约束，不匹配时静默回退原 kernel。
6. **valprep.sh 51000 行 vendored**：`AV-Solutions/SparsityINT8/data/valprep.sh` 为 soumith/imagenetloader 社区标准资产的 ImageNet 验证集归类脚本（wc -l 实测 51000），纯 mkdir/mv 无控制流，勿当代码阅读。
7. **Swin-Free.patch 目标是外部仓**：`Models/SwinFree/README.md:23` 明示 `git checkout f82860bf` 后打补丁——1460 行 patch 的目标是 microsoft/Swin-Transformer 上游（外部仓），非本仓内代码；本仓只有 README 与 patch 本身。
8. **visualize.cu 行数口径**：vad 与 petr 两份 `app/lib/visualize.cu` 实测均 696 行（图谱摘要 697，末行无换行符差 1）；两份逐字节同构，是 app/lib 三件套（net.h/tensor.h/visualize.cu）整体同构的组成部分。
9. **tensor.h 结构体区间**：`struct Tensor` 实测 L45-139（NOTES-DIGEST 记 L45-146，含尾注释行口径不同）；vad/petr 两版同位。
10. **行数口径混用**：图谱摘要中「main 186 行」（vad main.cpp）、「main 390 行」（uniad export_onnx.py）等为 main 函数体行数，文件实测分别为 267 行（main.cpp:83 起）与 544 行（export_onnx.py）；「460 行」（dcnv4_plugin.cpp）实测 389 行。引用时注意区分文件/函数两种口径。
11. **onnx2trt_calib_npz.py 在 results/ 不在 tools/**：bevformer-int8-eq 的校准闭环脚本实际位于 `AV-Solutions/bevformer-int8-eq/results/onnx2trt_calib_npz.py`（tools/ 下只有 calib_data_prep.py 与 onnx_postprocess.py）。
12. **tree-sitter 对 .cu 全量零提取**：全仓 CUDA 实现文件（ms_deform_attn_kernel.cu、rotateKernel.cu、dcnv4_*.cu、kernels.cu、visualize.cu、memory.cu 等）与纯声明模板头（far3d tensor.hpp、petr/vad tensor.h 的 struct Tensor L45-139）均为手扫补录，图谱以文件级节点表达——.cu 内函数级查询需直接读源码。

## 快速上手

- 总门面：仓库根 `README.md` → `AV-Solutions/README.md`（13 方案索引）→ `Models/README.md`（3 模型索引）。
- 方法论：`AV-Solutions/onnx-export-guidance/README.md`（579 行）+ `triton2cobin-plugin-guidance/README.md`（370 行）。
- 最小闭环：vad-trt（README 248 行：插件→双版本导出→引擎→app）。
- 进阶：异构看 mtmi / 量化看 SparsityINT8 / 代差看 enqueueV3 / 算子调优看 dcnv4PtxPlugin。

（Onboarding 八节详解见 [onboarding/ONBOARDING.md](onboarding/ONBOARDING.md)。）
