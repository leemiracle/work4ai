# explain 索引（anomalib 重要文件精讲 12 篇）

> 六节结构：角色定位/内部结构/外部连接/数据流/设计决策/新人提示。字数口径=不计空格字符 2500-4800/篇；行号锚全部 grep -n 实证（24/24 抽验命中）。

## 核心库主线

| 篇 | 文件 | 主题 |
|---|---|---|
| 01 | src/anomalib/models/components/base/anomalib_module.py | AnomalibModule 基类——全 model-zoo 的统一心脏 |
| 02 | src/anomalib/engine/ | Engine 训练引擎（Lightning 封装+XPU 策略/插件） |
| 03 | src/anomalib/cli/ | AnomalibCLI 入口与 install/pipelines 子命令 |
| 04 | src/anomalib/data/ | DataModule/Dataset/Split 数据层主线 |

## model-zoo 与组件

| 篇 | 文件 | 主题 |
|---|---|---|
| 05 | src/anomalib/models/image/padim/ | PaDiM（协方差+马氏距离经典基线） |
| 06 | src/anomalib/models/image/efficient_ad/ | EfficientAd（轻量学生-教师+模拟异常） |
| 07 | src/anomalib/models/components/feature/ | 特征提取器（timm backbone 抽象） |
| 08 | src/anomalib/data/utils/ensemble_tiling.py | Tiler/TileCollater 平铺集成 |

## 应用与部署

| 篇 | 文件 | 主题 |
|---|---|---|
| 09 | application/backend/ | anomalib Studio 后端（FastAPI router/service/repository） |
| 10 | application/ui/ | anomalib Studio 前端（React+stream/SSE 数据流） |
| 11 | src/anomalib/deploy/ | OpenVINO/Torch 部署推理 |
| 12 | src/anomalib/pipelines/ | Pipelines 体系（Job/Pipeline 抽象+benchmark+grid_search） |

## 锚勘误要点（写作中实证发现）

- callbacks 真实类名 `LoadModelCallback`（model_loader.py:36）与 `GraphLogger`（graph.py:44），非直觉的 ModelLoader/GraphCallback
- `SingleXPUStrategy` 所在文件是 `strategy/xpu_single.py`（非 single_xpu）
- `DinomalyMLP` 定义在 `components/layers.py` 而非 barrel `__init__`
- pipelines runners 真实路径 `pipelines/components/runners/`；`ensemble_engine.py` 在 `pipelines/tiled_ensemble/components/utils/`
