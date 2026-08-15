# 讲透 AI for Robotics（机器人方向枢纽）

> **机器人 = AI 的"身体"**——让 AI 不只在屏幕里思考，而在真实世界行动。**2024-2026 是机器人 AI 的"ImageNet 时刻"**：RT-2 / π0 / OpenVLA / GR00T / Figure 涌现。
>
> 本目录是整个项目的**机器人/具身智能方向枢纽**——从学科广角（AI 改变了机器人吗）到算法硬通货（SAC/VLA/Sim2Real）到 2026 前沿谱系全覆盖。
>
> 🆕 **2026-08-13 升级**：新增 [05 机器人 RL 工程实战](./05-机器人RL工程实战.md) + [06 VLA 模型谱系 2026](./06-VLA模型谱系2026.md)，从"学科综述"升级为"**工程 + 前沿枢纽**"。

---

## 篇目（6 篇顶层 + 4 篇 advanced，全部 ✅）

### 顶层（学科视角 + 工程实战）

| # | 标题 | 核心 |
|---|------|------|
| **00** | [AI for Robotics 是什么](./00-AI%20for%20Robotics%20是什么.md) | **学科广角**：莫拉维克悖论 / 五大应用 / AI 改变了机器人什么 |
| **01** | [早期经典与历史](./早期经典与历史.md) | Shakey 1969 → Brooks 1990 → Atlas 2013 |
| **02** | [本质探索](./本质探索.md) | 机器人学的第一性问题 / 具身智能 / 从硬编码到学习 |
| **03** | [2024-2026 最新前沿](./2024-2026最新前沿.md) | 人形爆发 / Foundation Model / Open-X-Embodiment |
| **⭐ 05** | [机器人 RL 工程实战](./05-机器人RL工程实战.md) | **全链路**：仿真→示教→RL→Sim2Real→部署，呼应 [`讲透RL/08`](../../讲透RL/08-Actor-Critic-SAC-ModelBased-OfflineRL.md) |
| **⭐ 06** | [VLA 模型谱系 2026](./06-VLA模型谱系2026.md) | **π0 / OpenVLA / RT-2 / GR00T 深度对比 + 2026 前沿** |

### advanced/（博士级硬通货）

| # | 标题 | 核心 |
|---|------|------|
| **01** | [VLA 数学](./advanced/01-VLA数学.md) | Flow Matching / 动作 token 化 / Sim2Real 数学 |
| **02** | [Sim2Real 工程](./advanced/02-Sim2Real工程.md) | Domain Randomization / System ID 的工程细节 |
| **03** | [开放问题与研究方向](./advanced/03-开放问题与研究方向.md) | 通用机器人 / 人形 vs 非人形 / 家用何时 |
| **00** | [论文清单](./advanced/00-论文清单.md) | 文献地图 |

---

## 怎么用（按目标分流）

### 🛤 第一次了解机器人 AI
→ [00](./00-AI%20for%20Robotics%20是什么.md)（学科广角）→ [02 本质探索](./本质探索.md) → [03 前沿](./2024-2026最新前沿.md)

### 🛤 想搞机器人 RL（从 RL 方向过来）
→ [`讲透RL/08`](../../讲透RL/08-Actor-Critic-SAC-ModelBased-OfflineRL.md)（SAC/Model-Based 算法）→ **[05 RL 工程实战](./05-机器人RL工程实战.md)**（全链路）→ [advanced/02 Sim2Real](./advanced/02-Sim2Real工程.md)

### 🛤 想搞 VLA（LLM 时代的新范式）
→ [06 VLA 谱系](./06-VLA模型谱系2026.md)（前沿对比）→ [advanced/01 VLA 数学](./advanced/01-VLA数学.md)（数学）→ [OpenVLA 开源仓库](https://github.com/openvla/openvla) 实操

### 🛤 想做人形机器人
→ [00](./00-AI%20for%20Robotics%20是什么.md) §四（人形爆发）→ [06](./06-VLA模型谱系2026.md) GR00T 部分 → NVIDIA Isaac Lab 生态

### 🛤 想做研究
→ [advanced/03 开放问题](./advanced/03-开放问题与研究方向.md) → [advanced/00 论文清单](./advanced/00-论文清单.md) → [06 §7 待核清单](./06-VLA模型谱系2026.md)

---

## 与其他系列的关系

```
            讲透 RL（决策维度）
                │ SAC/Model-Based
                ▼
        讲透 AIfor各学科/机器人/  ← 本目录（机器人方向枢纽）
                │
        ┌───────┼───────┐
        ▼       ▼       ▼
   讲透世界模型  讲透Agent  讲透Transformer
   (具身派)    (规划)     (ViT/VLM 基础)
```

- **算法地基**：[`讲透RL/08`](../../讲透RL/08-Actor-Critic-SAC-ModelBased-OfflineRL.md)（SAC/Dreamer/Offline RL）
- **能力建设**：[`讲透RL/09 §5.2`](../../讲透RL/09-工业实践与能力建设.md) 机器人方向入门路径 + 项目
- **世界模型**：[`讲透世界模型/`](../../讲透世界模型/) 具身派（Genie/Dreamer）
- **规划**：[`讲透Agent/03`](../../讲透Agent/03-规划与搜索.md) 长程任务规划
- **视觉基础**：[`讲透Transformer/10`](../../讲透Transformer/10-VisionTransformer与多模态.md) ViT/VLM

---

## 2026 前沿速查

| 方向 | 代表 | 状态 |
|------|------|------|
| **VLA Foundation** | π0 / OpenVLA / GR00T / Octo | ✅ 已开源（详见 [06](./06-VLA模型谱系2026.md)）|
| **人形机器人** | Optimus / Figure / Unitree / Atlas | ✅ 商业化加速 |
| **Sim2Real** | 可微仿真 / 真实数据蒸馏 | 🟢 持续突破 |
| **灵巧手** | DexCap / Any-point Manipulation | 🟡 难度高 |
| **World Model for Robot** | Dreamer V3 / Genie 2 | 🟡 与世界模型交叉 |
| **VLA + RL 微调** | 把 LLM 的 RLHF 搬到机器人 | 🟢 2026 最热 |

---

## 更新日志

- **2026-08-13**：升级为机器人方向枢纽——新增 [05 RL 工程实战](./05-机器人RL工程实战.md)（全链路 SOP）+ [06 VLA 谱系 2026](./06-VLA模型谱系2026.md)（四大模型深度对比）；新建本 README 作为枢纽入口；与 [`讲透RL/09 §5.2`](../../讲透RL/09-工业实践与能力建设.md) 双向链接。
- 首版：00/01/02/03 + advanced 4 篇（学科综述视角）。
