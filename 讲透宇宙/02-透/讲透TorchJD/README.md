# 讲透 TorchJD（PyTorch Jacobian 工具库）

> 2026-10-21 全链收官。DeepWiki 未索引 → understand 图谱是唯一知识源。本地仓 /usr-data/data2/repos/pytorch-landscape/repos/TorchJD @5ccd6e69。

| 产物 | 状态 | 规模 |
|---|---|---|
| 知识图谱 | ✅ 0 issues | 590 节点/1687 边/14 层/16 步 tour，fingerprints 278 文件 |
| ONBOARDING | ✅ | 16527 字符/108 唯一锚零失败 |
| explain | ✅ 12 篇 | 54764 字符/636 锚（172 机器复核 + 63 内容抽查全过） |

## 源码级实证发现

1. autogram 兼容 Weighting 实测 15 项（ONBOARDING 记 16，差 1 已勘误）
2. `__all__` 43 项精细分解：16 对孪生（Aggregator+Weighting）+ 4 纯 Aggregator + 3 纯 Weighting + 4 基类
3. 实现模块实测 28 非 27、顶层 class 54 非 60（图谱汇总口径 vs 实测）
4. PEP 562 惰性再导出 + `<<` 运算符 DSL（_weighting_bases.py __lshift__）+ trusted publishing 全链
5. 聚合三层基类（_aggregator_bases）+ Weighting 泛型体系（_T 协变 + 组合子）

目录：onboarding/ONBOARDING.md · explain/(12 篇+README) · 图谱在仓内 .understand-anything/knowledge-graph.json
