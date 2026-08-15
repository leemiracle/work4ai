# CS522: AI in Healthcare Seminar

> Stanford University, Autumn 2026
> 领域: 医疗 AI / 研讨课
> Prerequisites: 研究生或高年级本科，AI/ML 基础
> Units: 1-2（研讨课）
> Difficulty: ⭐⭐⭐⭐

---

## 📚 定位

研讨型课程，探索 AI 在医疗中的前沿应用——从影像诊断到临床决策支持，关注技术、伦理与临床落地。

---

## 🎯 学习目标

- 了解 AI 在医疗各场景的应用现状与挑战
- 理解临床验证、监管（FDA）与部署的独特要求
- 批判性阅读医疗 AI 论文
- 能设计以患者为中心的 AI 解决方案

---

## 📅 核心模块（研讨主题）

### Theme 1: 医学影像 AI
- X-ray / CT / 病理切片分类
- CheXNet 与商业化影像产品
- 多模态融合（影像 + 临床文本）

### Theme 2: 临床决策支持
- 电子病历（EHR）数据挖掘
- 风险预测（败血症、再入院）
- RAG 用于临床指南问答

### Theme 3: 隐私与安全
- 联邦学习（FedAvg）保护患者隐私
- 差分隐私在医疗数据中的应用
- HIPAA 合规与去标识化

### Theme 4: 不确定性与可信
- 模型校准与置信度
- MC Dropout 不确定性量化
- 人机协作：AI 辅助而非替代医生

### Theme 5: 公平性与伦理
- 算法偏见在不同人群的表现差异
- 医疗资源不均与 AI 的双刃剑
- 知情同意与算法透明

---

## 💻 项目代码

> CS522 与 CS286（医疗计算机视觉）共享代码。

📁 `topic8-med/medical_rag.py`

**实现内容**:
1. ✅ 合成 X-ray 数据生成与特征提取
2. ✅ 简化版医学分类器（Softmax）
3. ✅ 医疗 RAG 系统（临床指南 + LLM 检索）
4. ✅ 联邦学习模拟（隐私保护训练）
5. ✅ 不确定性量化（MC Dropout 近似）

**运行**:
```bash
cd topic8-med
python3 medical_rag.py
```

---

## 📊 关键概念/论文

| 概念 | 说明 |
|------|------|
| **CheXNet** | Rajpurkar 2017, 14 种胸片疾病分类 |
| **联邦学习** | 数据不动模型动，保护隐私 |
| **MC Dropout** | 多次前向传播估计不确定性 |
| **FDA SaMD** | Software as a Medical Device |

### 关键论文
1. Rajpurkar et al. 2017 — CheXNet
2. Mireshghallah et al. — FedML-Healthcare
3. Topol 2019 — *Deep Medicine*

---

## 🎯 适用人群

| 角色 | 推荐 |
|------|------|
| **想做医疗 AI 研究** | CS522 → 博士方向 |
| **临床从业者** | 了解 AI 能力边界 |
| **AI 安全方向** | 医疗是高风险场景 |
| **创业方向** | 数字健康产品 |

---

## 🚀 扩展方向

1. 深入 CS286（医疗计算机视觉）
2. 参与 Stanford CRISP（临床 AI 项目）
3. 探索 MIMIC-III 公开医疗数据集
4. 阅读 *The Doctor Will See You Now* (Topol)

---

**对应代码**: `topic8-med/medical_rag.py`（与 CS286 共享）
