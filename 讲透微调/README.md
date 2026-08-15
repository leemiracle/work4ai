# 讲透微调 (Fine-tuning, 透) · 完整版

> 用「直觉 → 数学 → 代码跑通 → 不足 → 应用」讲透微调。从"为什么 LoRA 用 1% 参数就够"到"QLoRA 单卡训 70B"再到实战骨架。姊妹项目：`../讲透激活函数/`、`../讲透基础模型/`。

**7 篇全部完成**（00 原理 + 01-02 方法 + 03 高效化 + 04 数据 + 05 失败 + 06 实战）。

---

## 阅读顺序

```
00-为什么LoRA用1%参数逼近全参数微调 (第一性原理)
   │
   01-LoRA数学深挖 (B=0初始化/α缩放/本征维度)
   │
   02-PEFT全家桶 (LoRA vs Adapter vs Prefix/Prompt)
   │
03-QLoRA (4bit量化基座+LoRA, 显存革命)
   │
04-微调数据工程 (质量>数量) → 05-失败模式 (遗忘/过拟合/alignment tax) → 06-实战
```

## 全部章节

| # | 文件 | 核心 | 实验关键数字 |
|---|---|---|---|
| 00 | `00-为什么LoRA能用1%参数逼近全参数微调.md` | LoRA=ΔW=B·A 低秩 | r=1 用5.9%参数 taskB=0.0002≈Full FT 0.0001 |
| | `experiments/00_lora_ft.py` ✅ | Full FT vs LoRA | |
| 01 | `01-LoRA数学深挖.md` | B=0初始化、α/r缩放、本征维度 | B=0 初始严格=基座；α=4 scale=1 最优 |
| | `experiments/01_lora_math.py` ✅ | 初始化+α对比 | |
| 02 | `02-PEFT全家桶.md` | LoRA/Adapter/Prefix/Prompt 横向对比 | LoRA推理0开销 vs Adapter +1024 FLOPs/层 |
| | `experiments/02_peft.py` ✅ | LoRA vs Adapter | |
| 03 | `03-QLoRA.md` | 4bit量化基座+LoRA | INT4基座省8x存储，效果0.0002≈LoRA |
| | `experiments/03_qlora.py` ✅ | QLoRA vs LoRA | |
| 04 | `04-微调数据工程.md` | 质量>数量（LIMA/AlpaGasus） | (概念为主) |
| 05 | `05-微调失败模式.md` | 灾难遗忘/过拟合/alignment tax | lr大遗忘多；缓解策略 |
| | `experiments/05_failure.py` ✅ | 遗忘+过拟合 | |
| 06 | `06-实战.md` | PEFT/LLaMA-Factory 代码骨架 | (需GPU机器跑) |

## 怎么跑

```bash
cd 讲透微调
for f in experiments/0*.py experiments/1*.py; do echo "=== $f ==="; python3 -u "$f"; done
```
小模型纯 CPU 可跑（01–05），06 实战需 GPU。

## 五大核心洞见

1. **LoRA work 的本质**：微调的 ΔW 是低秩的（本征维度），用 ΔW=B·A 参数化，1% 参数逼近 Full FT。
2. **LoRA 的稳定性**：B=0 初始化（起点=基座）+ A 高斯（打破对称）+ α/r 缩放（强度旋钮）。
3. **LoRA 淘汰 Adapter**：两者参数效果相近，但 LoRA 可合并（推理无延迟），Adapter 永久多算。
4. **QLoRA 显存革命**：4bit 量化冻结基座 + LoRA 全精度增量，70B 从 1TB→35GB 单卡可训。
5. **决策铁律**：改行为用微调（LoRA），注知识用 RAG，临时用 Prompt；质量>数量；评估别忘原能力（alignment tax）。

## 环境备忘
本机无 GPU/无 peft 库。01–05 用小 MLP 在 CPU 上讲透数学（已跑通）；06 实战给可移植代码骨架，在有 GPU 的机器上跑。

---

## 🔗 理论锚点（§12-15 横向打通）

> 本系列讲"LoRA/QLoRA/RLHF"的微调实战；这门课把 RLHF 背后的**偏好聚合数学**公理化：
> 枢纽：[`§12-15 整合`](../§12-15%20理论·形式化·安全·可信AI%20整合.md) §21

| 课程 | 产物 | 公理化的内容 |
|---|---|---|
| §15.3 Stanford CS329T/CS324（Percy Liang）| [`pluralistic_safety.py`](../top-cs-projects/stanford-cs-projects/topic3-safety/pluralistic_safety.py) | preference aggregation（Plurality/Borda/Approval）+ Condorcet 悖论 + Arrow 不可能性——RLHF "对齐谁的偏好"的社会选择理论根基 |

---

🔗 **交叉链接**：Stanford CS336 论文精读 · 对齐与后训练（SFT/RLHF/DPO/GRPO/R1，8 篇），见 [`讲透公开课/06-CS336论文精读/H-对齐与后训练.md`](../讲透公开课/06-CS336论文精读/H-对齐与后训练.md)；配套可运行验证实验见 [`其 experiments/`](../讲透公开课/06-CS336论文精读/experiments/)。

## 🔗 与其他宇宙的连接

- **[`讲透优化理论/`](../讲透优化理论/)**：每一行微调代码背后是一条优化定理——拉格朗日对偶见优化宇宙
