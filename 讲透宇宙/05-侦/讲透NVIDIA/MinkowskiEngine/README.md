# MinkowskiEngine 知识库（understand 全链）

> NVIDIA/MinkowskiEngine@02fc608（2023-03-22）——4D 稀疏张量与 GPU 稀疏卷积自动微分引擎（Python 前端 + CUDA/C++ kernel + pybind11 绑定）。commit 固化基线，图谱支持增量。

| 阶段 | 状态 | 产物 |
|---|---|---|
| deepwiki（L0） | ✅ | `deepwiki/` |
| understand 批分析 | ✅ 15/15 批（b1-15 全终验 PASS，part 切分合规） | 仓内 `.understand-anything/` |
| merge | ✅ 832n/1812e（52 孤儿 tested_by 清理 + 3 前缀错位悬空边手工回补 → 0 悬空） | `intermediate/assembled-graph.json` |
| layers/tour | ✅ 12 层 / 14 步，230/230 file 节点唯一分配零重复 | 同上 |
| finalize | ✅ validator 0 issues/0 warnings；fingerprints 229 文件@02fc608b | `.understand-anything/knowledge-graph.json` |
| onboarding | ✅ 6935 字（不计空格）8 节，67 行号锚全界内 | `onboarding/ONBOARDING.md` |
| explain | ✅ 5 篇 2816-2994 字/篇，87 锚零坏 | `explain/01-05` |
| 甄别清单 | ✅ 12 条（下） | 本文件 |

## explain 索引

1. `01-sparse-tensor-前端.md` — SparseTensor/Tensor 基类：COO 表示、双操作模式、量化 SPMM
2. `02-coordinate-manager与kernel-map.md` — 坐标管理器三层：图池+kernel map 缓存、25 个 GPU kernel
3. `03-convolution-kernel.md` — gather-GEMM 卷积：Direct/Copy 二选一、转置复用、魔数启发式
4. `04-ops调度与pybind绑定.md` — get_minkowski_function 8 调用点、绑定面四块、sys.path hack
5. `05-math-functions双实现.md` — ATen 风格双实现、mkl_alternate 宏、cpu_div<double> 死代码 bug

## 源码级甄别（12 条钉版）

1. **`src/math_functions_cpu.cpp:94` 真 bug**：`cpu_div<double>` 调 `vdMul` 而非 `vdDiv`——double"除法"实为乘法；grep 全仓零调用方（BroadcastMode 只有加/乘两枚举），真 bug 处于死代码故无测试拦截，上游未修；
2. **torch 版本三口径冲突**：`requirements.txt` 钉 `torch>=1.4,<1.7`（陈旧）vs README `>=1.7` vs Docker 镜像 `pytorch:1.12.0-cuda11.3`（容器不装 requirements）；
3. **三条平行构建线**：root `setup.py`（主线，SOURCE_SETS 29 TU）与 Makefile 互不调用（CHANGELOG 0.5.0a 明言"Remove Makefile for installation"），`tests/cpp/setup.py` 第三条线（11 组 SOURCE_SETS）——批 8 实证 setup.py 零引用 Makefile；
4. **tests/cpp 陈旧引用**：`convolution_cpu/gpu` 两组 SOURCE_SETS 引已更名的 `src/math_functions.cpp`（现 `_cpu.cpp`）；`convolution_cpu.py` 跨目标混合调其他 harness 符号（构建+运行双失败）；`test_all.sh:15 --test=region_cpu` 与键 `kernel_region_cpu` 不匹配；
5. **tests 笔误三处**：`type_test.py:10 assertErtTrue`；`convolution_cpu_test.py:9 from gradcheck import gradcheck` 目标不存在（已搬 utils/）且导入后未用；`coordinate_map_key_test.py` 两个同名 `def test`（L7/L15）后者遮蔽前者；
6. **死代码**：`MinkowskiEngine/modules/senet_block.py`（全仓零消费且 SE 块 D= 参数与父类 dimension= 签名不符，实例化即 TypeError）；`MinkowskiEngine/utils/coords.py:26` 断路导入（`utils/__init__.py:26` 已注释）；`MinkowskiFunctional` 死导出若干；
7. **文档术语滞后一代**：docs 教 `coords_man`，真实 API 是 `coordinate_manager`/`coordinate_map_key`（v0.5 改名）；`coordiante_map_key` 拼写笔误在 docstring（`MinkowskiSparseTensor.py:83`）；
8. **裸模块名 import + sys.path hack**：`__init__.py:31-32` 把包目录挂进 sys.path，包内 `from MinkowskiCommon import ...` 平铺导入可解析——非相对导入、非包名前缀，scanner 与人双易踩；
9. **`MinkowskiConvolutionTranspose.py` 不存在**——转置/生成式转置类全在 `MinkowskiConvolution.py`（L124/454/539）；`MinkowskiChannelwiseConvolution.forward` 是纯 Python kernel_map 聚合，不走 C++ 后端（与 docstring 声明风格相左）；
10. **`pruning_gpu.cu:36` `#include "pruning_cpu.cpp"`**——CPU 实现编入 GPU 翻译单元，文件边界是假的；
11. **`src/common.hpp` 死 include**：coords_key.hpp/coords_manager.hpp/types.cuh/gpu_memory_manager.hpp 四个目标不存在（改名遗留）；
12. **Dockerfile 与文档漂移**：单 stage 且源码经 git clone 而非 COPY 本地；`docs/demo/modelnet40_classification.rst` 仍指旧名 `examples/modelnet40.py`（现 classification_modelnet40.py）。

## 复跑入口

- 批终验：`python3 /tmp/ua2/verify_batch.py <repo> <N>`（part 文件聚合）；merge：`python3 ~/.agents/skills/understand/merge-batch-graphs.py <repo>`；finalize：`python3 /data/usershare/ai/pipeline-bin/understand/finalize_graph.py <repo>`
- 台账：仓内 `.understand-anything/PROGRESS.md`；派发模板：`DISPATCH-TEMPLATE.md`
