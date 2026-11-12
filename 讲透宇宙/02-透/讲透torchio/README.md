# 讲透 torchio（PyTorch 医学影像 IO/预处理库）

> 2026-10-21 全链收官。DeepWiki 未索引 → understand 图谱是唯一知识源。本地仓 /usr-data/data2/repos/pytorch-landscape/repos/torchio @9b1be950（v2.0.0a2）。

| 产物 | 状态 | 规模 |
|---|---|---|
| 知识图谱 | ✅ 0 issues | 969 节点/1827 边/14 层/16 步 tour，fingerprints 295 文件 |
| ONBOARDING | ✅ | 13511 字符/86 唯一锚零失败 |
| explain | ✅ 12 篇 | 51471 字符/821 锚（两轮验证 0 错） |

## 源码级实证发现（八条）

1. **实锤 bug**：`cli.py:128` 调用不存在的 `Image.to_nifti_zarr`——`torchio convert *.nii.zarr` 必崩（一行可修）
2. CLI 实为六子命令（transform/cache 两枚常被漏计）
3. codecov.yml v1 路径前缀全失配；docs/examples 六示例仍用 v1 API
4. Affine/Resample/ElasticDeformation 统一实现在 spatial.py（无独立文件）
5. 17 张 DICOM 孤儿夹具零引用；RescaleIntensity/ZNormalization 是 v1 别名
6. Motion docstring 称 random axis，实现固定第一空间轴；Subject 文档比代码严
7. Queue max_length 非硬内存上限（在途 futures 压整卷副本）
8. 向量化门禁理论盲区：_keep 全灭时取到前一变换记录（批 6 概率 ~1.6%）

目录：onboarding/ONBOARDING.md · explain/(12 篇+README) · 图谱在仓内 .understand-anything/knowledge-graph.json
