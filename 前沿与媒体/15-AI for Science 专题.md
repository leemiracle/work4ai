# 前沿与媒体 · 15 - AI for Science 专题

> 姊妹篇：[`../讲透基础模型/`](../讲透基础模型/)（NTP 范式）｜[`13-学术圈`](./13-AI学术圈与PhD招聘专题.md)（科研生态）。
>
> AI for Science 是 2024–2026 最让人兴奋的方向——AlphaFold 拿诺奖，AI 数学奥赛超人类，AI 发现新材料。**AI 不只是工程工具，正在重塑科学方法本身**。
>
> **核对日期**：2026-08-03（首版；AlphaFold/DeepChem/ESM/OpenMM/PySCF 实抓 stars）
> **图例**：🟢 = 活跃　🟡 = 稳定　⚠️ = 反爬

---

## 0. AI for Science 的"四象限"

```
              数据驱动 ←─────────→ 第一性原理
                  ┌──────────────┬──────────────┐
       生物/化学  │ AlphaFold    │ 量子化学     │
                  │ ESM/RoseTTAFold │ PySCF       │
                  │ Schrödinger  │ OpenMM/AMBER │
                  ├──────────────┼──────────────┤
       物理/材料  │ GNoME        │ DeePMD       │
                  │ MACE         │ JAX-MD       │
                  │ GNoME        │ FermiNet     │
                  └──────────────┴──────────────┘
                  + 数学：AI 数学奥赛（AlphaProof/AlphaGeometry 2）
                  + 推理：o1 / DeepSeek-R1 类推理模型在科学问题上的能力
```

---

## 一、AI for Biology / 药物

| # | 项目 / 模型 | 公司/机构 | Stars / 状态 | 强项 |
|---|---|---|---|---|
| B1 | **AlphaFold 2 / 3** | Google DeepMind / Isomorphic Labs | 🟢 ✅ 14.8k ⭐ | 蛋白结构预测里程碑，**2024 诺奖** |
| B2 | **ESM-2 / ESM-3** (Evolutionary Scale Modeling) | Meta | 🟢 ✅ 4.2k ⭐（push 2024-02）| 蛋白语言模型 |
| B3 | **RoseTTAFold / RFdiffusion** | Baker Lab（UW）| 🟢 | 蛋白设计（与 AlphaFold 互补）|
| B4 | **DeepChem** `deepchem/deepchem` | 社区 | 🟢 ✅ **6.9k ⭐** | Drug Discovery + Materials Science Python 库 |
| B5 | **RDKit** | 社区 | 🟢 | 化学信息学事实标准 |
| B6 | **ChEMBL / PubChem** | EBI / NIH | 🟡 | 化学数据库 |
| B7 | **Boltz-1 / Boltz-2** | MIT / Recursion | 🟢 新 | 2024 开源 AlphaFold 3 替代 |

---

## 二、AI for Chemistry / Materials

| # | 项目 | 公司/机构 | 强项 |
|---|---|---|---|
| C1 | **GNoME** | Google DeepMind | 2023-11，发现 220 万新晶体（38 万稳定）|
| C2 | **MACE**（Materials 3）| Cambridge | 等变消息传递神经网络，材料模拟 SOTA |
| C3 | **PySCF** `pyscf/pyscf` | 社区 | 🟢 ✅ **1.6k ⭐**，量子化学 Python 库（当日 push）|
| C4 | **OpenMM** `openmm/openmm` | Stanford / Pande | 🟢 ✅ **1.9k ⭐**，分子动力学 GPU 加速 |
| C5 | **DP-GEN / DeePMD-kit** | 中科院 OAID | 深度势能，中国 AI4Physics 领军 |
| C6 | **Matlantis / MatGenAI** | 产业 | 商业材料发现 |
| C7 | **GNoME / Azure Quantum Elements** | Microsoft | 商业 |

---

## 三、AI for Math / 推理

| # | 项目 | 公司 | 强项 |
|---|---|---|---|
| M1 | **AlphaProof / AlphaGeometry 2** | DeepMind | IMO 银牌水平（2024），2026 进一步突破 |
| M2 | **o1 / o3 / GPT-5 Reasoning** | OpenAI | 科学推理通用 |
| M3 | **DeepSeek-R1 / V4** | DeepSeek | 开源推理 |
| M4 | **Lean / Mathlib** | 社区 | 形式化数学（AI 用 Lean 证明）|
| M5 | **AlphaEvolve**（进化算法）| DeepMind | 2024 发现新算法（矩阵乘法等）|

---

## 四、AI for Physics

| # | 项目 | 公司/机构 | 强项 |
|---|---|---|---|
| P1 | **DeepMind AI 飞控** | DeepMind | F-16 实机空战超人类飞行员 |
| P2 | **DeepMind 聚变等离子控制** | EPFL + DeepMind | Tokamak 实时控制 |
| P3 | **GraphCast / GenCast** | DeepMind | 天气预测超 ECMWF IFS |
| P4 | **AI 天文学** | 多方 | 系外行星发现 / 引力波检测 |
| P5 | **AI 高能物理** | CERN | 粒子碰撞事件分类 |

---

## 五、AI for Medicine（详见 [`16-AI 重点行业`](./16-AI重点行业（医疗+金融+法律+教育）.md)）

- Med-PaLM / Med-Gemini / AlphaFold-Drug
- Hippocratic AI / OpenEvidence / Glass Health
- 医学影像（Paige / Aidoc / Zebra Medical）

---

## 六、关键论文 / 综述

| # | 论文 | 一句话 |
|---|---|---|
| R1 | **AlphaFold 2** (Nature 2021) | CASP14 革命性突破 |
| R2 | **AlphaFold 3** (Nature 2024) | 扩展到蛋白 + DNA/RNA + 小分子 |
| R3 | **AlphaProof / AlphaGeometry 2** (2024) | IMO 数学 |
| R4 | **GNoME** (Nature 2023) | 38 万稳定新材料 |
| R5 | **DeepMind GraphCast** (Science 2023) | 天气 |
| R6 | **"The Impact of Large Language Models on Science"**（Stanford HAI）| 综述 |

---

## 七、关键机构 / 人物

| 机构 / 人 | 角色 |
|---|---|
| **Google DeepMind** | AlphaFold/AlphaProof/GNoME/GraphCast，绝对领先 |
| **Demis Hassabis / John Jumper** | 2024 诺奖化学 |
| **Meta AI（FAIR）Protein Team** | ESM |
| **David Baker**（UW）| 2024 诺奖化学（蛋白设计，RoseTTAFold）|
| **MIT / Stanford / Berkeley** | 学术三强 |
| **上海交大 / 中科院 OAID** | 中国 AI4Physics（DeePMD）|
| **Microsoft Research** | MatterGen / Q# |

---

## 八、维护说明

- **2026-08-03 首版**：✅ AlphaFold/DeepChem/ESM/OpenMM/PySCF 实抓 stars；⚠️ 商业产品（Schrödinger/Recursion）反爬。
- **下次重核**：每 6 个月（诺奖年度级变化）。
- **重点跟踪**：AlphaFold 4 / AlphaEvolve 2 / Boltz 系列 / DeepMind 科学 AI。

📌 **下一步**：想跑 AlphaFold 3 / Boltz-2？告诉我用途（蛋白结构/对接/材料），我给 Docker 命令。

---

> 🔗 相关：[`../讲透基础模型/`](../讲透基础模型/) ｜ [`../讲透生成模型/`](../讲透生成模型/)（扩散模型 → AlphaFold 3）｜ [`13-学术圈`](./13-AI学术圈与PhD招聘专题.md)
