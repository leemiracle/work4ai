# 讲透 NVIDIA/FastPhotoStyle

> A 层清库 #8（小仓全链一体）· 2026-11-02

| 链路 | 状态 |
|---|---|
| 图谱 | 仓内 knowledge-graph.json：42n/89e/9层/8步，0 issues，fingerprints 21@af0c8fec |
| 综合讲透 | `讲透.md`：4000 字 28 锚 |

**一句话**：PhotoWCT 闭式解风格迁移（**无任何训练代码**）——标签对齐+两层平滑管线；converter.py 是纯考古层（load_lua 已删+.t7 不在仓）。

**勘误精选**：实际入口 4 个非教程宣称 3 个（批量入口未文档化）/submodule 帮助文本误导（实为手工 clone）/ReMapping 潜伏 bug（`[]` 初始化 vs `.items()`）/smooth_filter 硬编码 CUDA include+每次重编译/scanner 把 .npy 误归 code 类别。
