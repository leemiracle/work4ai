# 101 · Mid-Training 全景 2026：预训练与后训练之间的"第二引擎"（深读卡）

> card_id: midtraining-panorama-2026
> universe: 前沿与媒体 / 讲透模型 交叉
> burke: 场景=预训练收益递减后、post-training 之前的能力塑造；主体=LLM 训练工程师；能动=综合 2 综述+机理研究+IBM 500 实验+本仓 DeepSeek/Transformer 资产；行动=定义→配方→机理→判据；目的=一张卡判断"该不该 mid-train、怎么配"；张力=专业化 vs 灾难遗忘、高质量小数据 vs 噪声大数据、时机不可逆 vs 配比可调；弧线=cool-down 技巧→annealing 命名→mid-training 学科化（OpenAI 2024-07 设部门→2025 定义标准化→2026 机理突破）
> status: done
> refs: arXiv 2510.06826 / 2510.23081 / 2510.14865 一手 + IBM Research 2026-04 博客一手；模型报告数字为综述转引
> updated: 2026-08-27

---

## 〇、一句话

**Mid-training = 预训练收益递减后，用 10-300B 级高质量数据 + 退火学习率 + 上下文扩展，把模型从"记忆"推向"抽象"的第二引擎——IBM 500 实验证明它改动 90% 权重、RL 只改 5%，两者是不同机制而非替代关系。**

## 一、定义与边界（2025 标准化，vintagedata 考据+OLMo 2 确立）

- **演化**：2024 各种"cool-down/annealing"杂称 → OpenAI 2024-07 设 mid-training 部门（产出 GPT-4-Turbo/4o）→ Yi 报告首学术定义 → OLMo 2 确立"晚期课程学习+退火"标准义
- **对象**：|D_pre| > |D_mid| > |D_post|，甜点区 **10-300B tokens**（Chinchilla 律照常适用）；FLOPs 占比 ~5-10%（OLMo 2）
- **三支柱**（2510.06826 分类法）：**数据分布**（降采样低质网页、升采样 code/math/STEM/多语/指令）× **学习率退火**（恒定→平滑衰减收敛到更优极小值）× **长上下文扩展**（PI/NTK/YaRN/ABF + 渐进课程）
- **vs continued pretraining**（2510.14865 关键区分）：mid-train **保留通用数据混合**（混合权重>0），continued pretraining 是全切域数据的极限情形——受控实验证明混合一致胜过全切

## 二、工业配方速查（综述转引，全部一手数字）

| 模型 | 预训练 | Mid-training |
|---|---|---|
| Qwen(范式例) | 6.3T@4k | annealing 1T@8k（降网页升 code/math）→ 长上下文 100B@32k（+合成长 QA） |
| **DeepSeek-V3** | 14.8T | 上下文两段：60B@32K → 60B@128K |
| SmolLM2 | 11T 三段 | annealing 1T（58%web/24%code/14%math/4%合成教材）→ 长上下文 75B@2k→8k |
| MiMo-7B | 25T 三段 | annealing 阶段 math+code 升到 **70%**；长上下文 8K→32K→64K +10% 合成 |
| Pangu Pro MoE | 9.6T 通用 | reasoning 3T（STEM/code/合成 CoT+32K）→ annealing 0.4T（指令 20%+高阶 STEM 18%，**7B proxy 消融选数据**） |
| OLMo 2 | ~5T web | Dolmino Mix 1124 + **多次随机序重跑取平均**（7B×3×50B） |
| MiniMax-M1 | +7.5T | 恒定 8e-5×2.5T → 衰减 8e-6×5T；四段 32K→**1M**（lightning attention） |
| Llama-3 | — | 长上下文**六段** 8K→128K（~800B）；Nemotron-4：9T 中 1T 为 mid-train |

**长上下文工程细则**（2510.23081 Table 5 综合）：两段式最主流（32K→128K）；batch 随长度**等比缩减**（DeepSeek-V3/Pangu 均 4×：1920→480）；自然长文（书/仓级代码/论文）> 拼接合成（Phi-4 消融：≥8K 过滤、≥16K 升采样）；合成长 QA 是增强不是替代。

## 三、机理（2026 三大突破）

1. **分布桥接理论**（2510.14865）：mid-train 为 post-training 提供更好初始化；收益**随与预训练分布的距离增大**（code/math 最大）；**时机×配比强交互：早引入可耐 80% 高配比，晚引入（塑性窗口关闭后）高配比反而劣于 10%——错过窗口不能靠加数据补**
2. **IBM 500 实验**（2026-04，Granite）：mid-training 使推理能力 **3-4×**，且保住预训练知识；同数据走 RL 收益甚微。**科学推理：GPQA-Diamond 差 17-28 点**（mid-train vs 后训练喂同数据）；MATH500 行为改变： terse→逐步推理（Granite-3.3-8B 16.9%→79.5% after mid+RL）；**mid-train 改 >90% 权重且全层分布，RL 只改 ~5% 且前载 200-400 步——两机制正交，RL 不能替代 mid-train，mid-train 放大 RL**
3. **理论三视角**（2510.06826）：梯度噪声尺度（高质量数据提升信号方差）｜信息瓶颈（压缩噪声特征保预测结构）｜课程学习（分布渐进锐化强化多步推理）

## 四、判据（何时 mid-train）

```
✓ 域与 web 预训练分布距离大（code/math/STEM/多语）→ 收益最大
✓ 需要 post-training（RL/SFT）吃到域数据 → 先 mid-train 桥接（IBM：RL 在 mid-train 表征内工作）
✓ 上下文需 >8K → mid-train 阶段扩展（配 batch 缩减+自然长文）
✗ 域数据已在预训练中充分 → 增益小
✗ 错过塑性窗口的晚期强插 → 降配比（10%）或放弃
配方骨架：恒定 LR → 退火段（高质量域数据升采样+保留通用混合）→ 长上下文段（两段式+batch 等比减）
```

## 五、本仓挂接

- **DeepSeek 线一手**（.research/deepseek + 讲透Transformer/15）：V2/V3 的 **YaRN 两阶段 32K×1000 步→128K×1000 步**（s=40/α=1/β=32）= 表二配方的实仓证据
- **与 #100 蒸馏卡的关系**：distill 产出的 CoT 数据正是 mid-train annealing 段的燃料（合成 CoT 10-20% 配比）；OLMo "多跑取平均" 与 weight averaging 家族同构
- **与 RLVR 极限的关系**（讲透RL/05）：IBM"RL 在 mid-train 表征内工作不改表征"↔ RLVR"只能榨取 base 已有"——**同一发现的两面**；完整链= mid-train 塑表征 → distill 注模式 → RLVR 榨取
- 开放问题：mid-train scaling law｜与 RL 类 post-train 的次序交互｜multi-stage 课程自动化

## refs

| 引用 | 核实 |
|---|---|
| arXiv:2510.06826（首篇 mid-training 综述，2025-10） | ✅ 2026-08-27 websearch |
| arXiv:2510.23081 v2（第二综述，机理+配方表） | ✅ 同上 |
| arXiv:2510.14865（分布桥接受控实验） | ✅ 同上 |
| IBM Research 博客（2026-04-15，500 实验） | ✅ 同上 |
| vintagedata 考据博客（2025-01，术语史） | ✅ 同上 |
| 模型报告数字（Qwen/V3/SmolLM2/MiMo/Pangu/OLMo2/MiniMax/Llama3/Nemotron） | 综述转引（二手） |
| 本仓 YaRN/V3 两阶段配方 | 本仓一手 |

---
生成：2026-08-27 · 3 arXiv + IBM 一手核实 · 与 #100 蒸馏卡、讲透RL/05 构成"训练全周期三部曲"
