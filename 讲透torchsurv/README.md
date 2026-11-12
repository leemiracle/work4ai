# 讲透 torchsurv（PyTorch 生存分析工具箱）

> 2026-10-21 全链收官。DeepWiki 未索引（MCP 口径 Repository not found）→ understand 图谱是唯一知识源。本地仓 /usr-data/data2/repos/pytorch-landscape/repos/torchsurv @a28dac5e。

| 产物 | 状态 | 规模 |
|---|---|---|
| 知识图谱 | ✅ 0 issues | 236 节点/452 边/11 层/13 步 tour，fingerprints 102 文件 |
| ONBOARDING | ✅ | 15014 字符（不计空格）/99 行号锚零坏/8 节 |
| explain | ✅ 12 篇 | 48006 字符/492 行号锚（两轮自动验证，10 处初稿坏锚已修） |

## 源码级实证勘误清单（五条）

1. `stats/ipcw.py:115` 死赋值被 L116 覆盖 + L112 告警文案与实际行为不符（宣称返回 1 实际 1/ct）
2. `conftest.py` 夹具零消费（近死文件），各测试模块自建数据
3. `test_hypothesis.py:26` 丢弃策略值——[-50,50]/[-10,10] 值域设计未生效，退化为样本量发生器
4. `_find_torch_unique_indices` 在 brier_score.py:760 与 auc.py:1104 逐字重复
5. Auc/Brier 对 new_time 严格度分裂（NewTimeInputs within_follow_up 默认值不同）

目录：onboarding/ONBOARDING.md · explain/(12 篇+README) · 图谱在仓内 .understand-anything/knowledge-graph.json
