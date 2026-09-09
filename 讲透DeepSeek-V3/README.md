# 讲透 DeepSeek-V3

> DeepSeek 第三代 671B MoE 旗舰（37B 激活）：MLA + DeepSeekMoE + 首创 aux-loss-free 负载均衡 + MTP + FP8 混合精度，全流程训练成本压到 557.6 万美元，追平 GPT-4o/Claude-3.5-Sonnet。commit `9b4e978`（2025-08-28）· 生成 2026-09-05

## 产物清单

| 产物 | 规模 / 说明 |
|---|---|
| DeepWiki | 33 页（deepwiki/） |
| 论文精读 | 1 篇：《DeepSeek-V3 Technical Report》（arXiv:2412.19437） |
| 知识图谱 | 46 节点 / 77 边 / 4 层 / 7 步导览（发布仓，源码薄，重点在论文） |

## 论文精读要点

- **成本核算标杆**：2.788M H800 GPU 小时 ≈ $5.576M 完成全部预训练+后训练，全程零不可恢复 loss spike、零回滚
- 架构件全部继承前作（MLA/DeepSeekMoE 出自 V2 与 DeepSeekMoE 论文），V3 的增量是 **auxiliary-loss-free 负载均衡**（独立论文 Wang et al. 2410.05240）、**MTP 多 token 预测训练目标**、首次超大规模 **FP8 训练**验证
- 14.8T tokens 预训练；37B 激活参数在多数 benchmark 追平 GPT-4o 与 Claude-3.5-Sonnet
- 读法建议：像读"大模型工程总装图纸"——所有件拧成一个整体并给出完整成本账
- 200 人署名；MLA 关键创新者在 V2 论文附录致谢中点名（Huazuo Gao、Wangding Zeng）

## 知识图谱

路径：`~/ai/explore/deepseek-ai/DeepSeek-V3/.understand-anything/knowledge-graph.json`。发布仓特性：inference 脚本为主、源码薄，图谱小是正常现象，知识重心在论文精读与 DeepWiki。

## 姊妹篇

- 上游架构：[讲透DeepSeek-V2](../讲透DeepSeek-V2/README.md)（MLA/MoE 直系祖先）、[讲透DeepSeek-MoE](../讲透DeepSeek-MoE/README.md)
- 同底座推理线：[讲透DeepSeek-R1](../讲透DeepSeek-R1/README.md)
- 后继：[讲透DeepSeek-V3.2-Exp](../讲透DeepSeek-V3.2-Exp/README.md)（DSA 稀疏注意力下一代）
