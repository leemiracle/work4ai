# ReGraphT × DeepWiki 关联文档（更新于 2026-09-03）

## 本仓索引状态（钉版）

- **blacknickwield/ReGraphT 未被 DeepWiki 索引**（2026-09-03 核验：页面为 "Loading..." 壳）。且本仓为 ICLR2026 投稿的早期形态：README 仅 2 行，`reasoner/{standard,cot,code_rag}.py` 为 0 字节空占位——源码深读是唯一途径（已完成：understand 图谱 48 节点 + 5 篇 explain + ONBOARDING，见 `../docs/`）。
- **领域关联仓 KernelBench（ScalingIntelligence）已被 DeepWiki 全量索引**（36 子页，快照 2026-01-16），全文快照在本目录 `kernelbench/`。关联性质说明（诚实披露）：ReGraphT 仓内**不含**任何数据集/评测代码，论文主题（CUDA optimization expertise 迁移）的领域公共评测基座是 KernelBench——wiki 供理解其评测语境（正确性协议/fast_p/timing 方法）；若论文实验用了 KernelBench，复现时须自行补数据。

## 交叉引用要点

| DeepWiki 章节 | 对理解 ReGraphT 的价值 |
|---|---|
| `2.1` + `7.1` | CUDA kernel 优化的「效果」如何被定义与度量（正确性+speedup/fast_p）——reasoning graph 迁移的收益最终要落在这套度量上 |
| `4-prompt-engineering` 全家 | 上游的静态提示工程（TOML/few-shot/硬件感知）——ReGraphT 的主张恰是用「可检索推理图」替代静态 few-shot，两相对照见创新点 |
| `5.1~5.4` | 若复现需任务集，KernelBench L1/L2/L3 是默认选择 |

## 覆盖检查

`kernelbench/` 36/36 子页全量快照（`_coverage-check.md`），抓取于 2026-09-03。
