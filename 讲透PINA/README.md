# 讲透 PINA（Physics-Informed Neural Networks 库）

> 2026-10-21 全链收官。DeepWiki 未索引 → understand 图谱是唯一知识源。本地仓 /usr-data/data2/repos/pytorch-landscape/repos/PINA @60ea474a（v0.3.2）。

| 产物 | 状态 | 规模 |
|---|---|---|
| 知识图谱 | ✅ 0 issues | 1326 节点/2581 边/15 层/16 步 tour，fingerprints 674 文件 |
| ONBOARDING | ✅ | 16013 字符/111 唯一锚零坏 |
| explain | ✅ 12 篇 | 50759 字符/515 锚（48/48 语义抽验命中） |

## 源码级实证勘误（七条系列级）

1. **DeepONet/MIONet 同文件继承倒挂** + model property bug（deeponet.py）
2. 方程 zoo 刻意不用塔基 advection 算子（契约原因：zoo 方程自带离散化）
3. move_discretisation_into_conditions 真实调用点在 data_module.py:120（非直觉位置）
4. 顶层 pina/ shim 只转发 3/10 函数（utils.py 等）
5. R3 refinement 残差均值阈值偏离论文设定
6. 定点维 int64 陷阱靠 RULES.md 兜底（非代码层防护）
7. API_scheme.md "pina.block" 笔误（实为 pina/model/block/）+ rbf_block.rst "Radias" 拼写

目录：onboarding/ONBOARDING.md · explain/(12 篇+README) · 图谱在仓内 .understand-anything/knowledge-graph.json
