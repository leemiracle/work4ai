# 讲透 anomalib（工业异常检测库）

> 2026-10-22 全链收官。DeepWiki 未索引 → understand 图谱是唯一知识源。本地仓 /usr-data/data2/repos/pytorch-landscape/repos/anomalib @dc087d5c（v2.7.0+5）。

| 产物 | 状态 | 规模 |
|---|---|---|
| 批分析 | ✅ 97/97（补批 80-97 共 18 批，137 产物文件含分片） | — |
| 知识图谱 | ✅ 0 issues/0 warnings | **3235 节点/7721 边/15 层/16 步 tour**，fingerprints 1584 文件 |
| ONBOARDING | ✅ 8 节 | 7482 总字符（去空格 7005）/56 锚抽验命中 |
| explain | ✅ 12 篇+索引 | 63703 总字符/128 行号锚（24/24 抽验命中） |

## 流水线纪要

- 批 80-97 补齐全程 4 并发滚动（09:13-10:05 约 52 分钟，18 批零重派）；merge 悬空边 10 条全为前缀错位（DinomalyMLP barrel→layers.py、package.json/pyproject/tauri.conf 的 file:→config:、README 的 file:→document:），手工回补后悬空归零
- layers 15 层（project-config→repo-automation→core-utils→data→model-components→metrics→model-zoo(223)→engine→cli/pipelines/deploy→app-backend(166)→app-frontend(279)→app-packaging→tests(190)→examples-tools→docs(205)），1..1592 全覆盖零重复双重校验
- finalize 校验 0 issues/0 warnings；fingerprints 1584 文件基线支持增量

## 源码级实证勘误（批分析+写作累积）

1. `pre_processing/utils/__init__.py` 纯 docstring barrel——docstring 承诺的 `get_exportable_transform` 实际定义在 `transform.py:17`，`__init__` 无 re-export（示例按磁盘状态无法成立）
2. tiled_ensemble `__init__` 文档字符串引用 `tools/tiled_ensemble/train_ensemble.py`，实际磁盘文件是 `train.py`（上游文档漂移）
3. `video/README.md` 示例类名 AiVad 对应实际目录 `ai_vad/`（下划线）
4. callbacks 真实类名 `LoadModelCallback`（model_loader.py:36）/`GraphLogger`（graph.py:44），非 ModelLoader/GraphCallback；`SingleXPUStrategy` 在 `strategy/xpu_single.py`
5. `DinomalyMLP` 定义在 `dinomaly/components/layers.py` 非 barrel `__init__`（merge 悬空边根因）
6. examples：`basic_torch_inference.py` 纯注释占位（legacy 声明零语句）；`api/default.txt`/`cli/default.txt` 是无 literalinclude 消费的孤儿片段；`basic_training.sh:29` 有 `echo .e` 上游笔误
7. `test_pimo.py` docstring 仍写 `anomalib.metrics.per_image.functional`，实际已迁移 `anomalib.metrics.pimo`
8. notebooks 全为 Git LFS 指针（本机无 LFS 对象），图谱按 README 主题+YAML class_path 旁证发 depends_on/documents 边
9. scanner `batchImportData` 对 src-layout 裸导入（`anomalib.*`）几乎全空——18 批普遍 ast.walk 重扫补回（batch-87 补 39 条、batch-91 补 52 条、batch-82 补 81 条实测）
10. **Tiler `stride=None` 直接 AttributeError**（docstring 承诺未实现，连带 TilerConfigurationCallback 默认参数必崩）；tile/untile 往返 torch.equal=True 已实证（torch 2.10）
11. EfficientAd 的 teacher 非 EfficientNet 实为 PDN；`padding` 注解 int 实为 bool；PDN/AE 输出形状 56×56/64×64 实跑核实
12. PaDiM `fit` 报错文案"coreset selection"系 PatchCore 复制残留；`_deduce_dims` 是死代码
13. 特征提取器真实路径 `feature_extractors/`（非 feature/）；19 个模型消费它（图谱仅记 3 类）

目录：onboarding/ONBOARDING.md · explain/(12 篇+README) · 图谱在仓内 .understand-anything/knowledge-graph.json
