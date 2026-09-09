# 讲透 DeepSeek-LLM

> DeepSeek 首代基座的技术宣言：自己重拟合 scaling law 的"长期主义"，从零训练 7B/67B（2T tokens 中英双语），67B 代码/数学/推理全面超越 LLaMA-2 70B——V2/V3/R1 全系起点。commit `6712a86`（2024-02-04）· 生成 2026-09-05

## 产物清单

| 产物 | 规模 / 说明 |
|---|---|
| DeepWiki | 20 页（deepwiki/） |
| 论文精读 | 1 篇：《DeepSeek LLM: Scaling Open-Source Language Models with Longtermism》（arXiv:2401.02954，单篇已含 SFT+DPO 全流程） |
| 知识图谱 | 23 节点 / 17 边 / 4 层 / 8 步导览（发布仓，源码薄，重点在论文） |

## 论文精读要点

- **自己重推 scaling law**：按"数据充裕"假设重拟合超参（batch size/lr 调度跟随模型规模），确立"长期主义"路线
- 2T tokens 中英语料 + 100K BBPE tokenizer + HAI-LLM 框架——后续全系的数据与基建底座
- **Chat = SFT + DPO**：单篇报告完整给出对齐配方（当时 DPO 尚新），中文开放域超 GPT-3.5
- ⚠️ **勘误（ID 核实）**：README 引用的 2311.07911 是 Google 的 **IFEval 指令遵循基准**（评测工具），**不是 DeepSeek 论文**；本仓正主论文 = 2401.02954 单篇
- "V1 攒数据与配方，V2 换骨架"——读懂 V2 之前先读本文

## 知识图谱

路径：`~/ai/explore/deepseek-ai/DeepSeek-LLM/.understand-anything/knowledge-graph.json`。发布仓（脚本+评测），图谱小属正常，重点在论文。

## 姊妹篇

- 直系后继：[讲透DeepSeek-V2](../讲透DeepSeek-V2/README.md)、[讲透DeepSeek-V3](../讲透DeepSeek-V3/README.md)
- 基座下游：[讲透DeepSeek-Math](../讲透DeepSeek-Math/README.md)（基座=LLM+Coder-v1.5）、[讲透DeepSeek-VL](../讲透DeepSeek-VL/README.md)（text-only 70% 配比同款语料）
