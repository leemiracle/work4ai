# 讲透 openai/CLIP

> A 层清库 #6（小仓全链一体）· 2026-11-02

| 链路 | 状态 |
|---|---|
| 图谱 | 仓内 knowledge-graph.json：45n/81e/6层/8步，0 issues，fingerprints 18@d05afc43 |
| 综合讲透 | `讲透.md`：3998 字 61 锚（五节+论文对应表） |
| 勘误 | 6 条（**纯推理侧实现：论文 Eq.1 训练损失未随仓发布**/README tokenize LongTensor 过时实为 IntTensor/"times 100" 实为可学习 logit_scale/hubconf 入口 README 零记载+deps 漏 packaging/setup.py py_modules 指向不存在模块/视觉塔无因果掩码注释易误读） |

**一句话**：CLIP 官方推理实现——build_model 是"权重考古"（超参全从 state_dict 形状反推，无 config 依赖）；GPU 加载即无条件 fp16；1.36MB BPE 词表是运行硬依赖。
