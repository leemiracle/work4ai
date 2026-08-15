# CS286: Computer Vision in Biomedicine

> Stanford University（Stanford Medicine / SAIL / Center for Artificial Intelligence in Medicine & Imaging）
> 方向：计算机视觉 × 医学影像——从 CNN 诊断到联邦学习与临床 RAG
> Prerequisites: 基础 ML/CV（推荐 CS231N）+ 一定统计/概率；医学背景非必需但加分
> Language: Python + PyTorch + MONAI / nnUNet
> Difficulty: ⭐⭐⭐⭐⭐
> 官网：http://cs286.stanford.edu/（基于公开信息整理，官网抓取时不可达）

> ⚠️ **说明**：本 OVERVIEW 基于「医学影像 CV」的标准教学主线与 Stanford 医学 AI 公开成果整理，
> 项目代码位于 `topic8-med/medical_rag.py`（X-ray 分类 + 医疗 RAG + 联邦学习 + 不确定性量化）。

---

## 📚 课程定位（独特价值）

Stanford **计算机视觉在生物医学的应用**课程。Stanford 在医学影像 AI 上是全美顶尖（CheXNet、皮肤科 AI、糖尿病视网膜病变都出自这里），这门课的独特价值：

- **不是普通 CV 套医学数据**：而是系统讲**为什么医学 CV 与自然图像 CV 本质不同**——类别极不均衡、标签噪声、长尾罕见病、像素级标注昂贵、分布漂移（不同扫描仪/医院）。
- **临床可用性优先**：不只是 AUROC，而是 **calibration、不确定性、可解释性、FDA 审批、偏倚审计**——模型不准会害人。
- **隐私是一等公民**：医疗数据出不了院 → **联邦学习**、差分隐私、合成数据是核心议题，不是附录。
- **多模态临床决策**：影像 + 电子病历（EHR）+ 临床指南 → 医疗 RAG，让 LLM 给出**有引用、不幻觉**的诊断建议。
- **覆盖全模态**：X-ray / CT / MRI / 病理切片（WSI）/ 眼底 / 皮肤镜 / 超声。

> 与普通 CV 课的区别：
> - **CS231N**：自然图像、ImageNet、追求精度
> - **CS286**：医学影像、追求**安全 + 可部署 + 可解释**，错一次代价是误诊

---

## 🎯 学习目标

1. 掌握**医学影像分类**（X-ray/CT 诊断）与**分割**（U-Net 系）。
2. 理解**类别不均衡、标签噪声、长尾**在医学中的处理。
3. 实现**不确定性量化**（MC Dropout、Deep Ensemble、Conformal）。
4. 掌握**联邦学习**在多医院协作训练中的应用（FedAvg）。
5. 构建**医疗 RAG**：LLM + 临床指南，输出带引用的诊断建议。
6. 评估**临床部署**：calibration、偏倚、FDA 路径、伦理。

---

## 📅 完整模块（基于医学影像 CV 教学主线）

### Part 1: 医学影像数据与模态
- X-ray（CXR）、CT、MRI（T1/T2/FLAIR）、超声
- 病理全切片图像（WSI，gigapixel）
- 眼底、皮肤镜、内窥镜
- DICOM 标准、窗宽窗位、配准
- 公开数据集：ChestX-ray14、CheXpert、MIMIC-CXR、NIH、ISIC、Camelyon

### Part 2: 医学影像分类
- CNN backbone（ResNet/DenseNet/EfficientNet）
- **CheXNet**（Rajpurkar 2017，121 层 DenseNet，14 种胸片病理）
- 多标签分类（一张片子多个发现）
- 长尾与不均衡：focal loss、过采样、decoupled representation
- 标签噪声（CheXpert 的 uncertain 标签策略）

### Part 3: 医学影像分割
- **U-Net**（Ronneberger 2015）— 医学分割的 Transformer
- **nnU-Net**（Isensee，自适应配置，几乎所有基准 SOTA）
- 3D 分割（V-Net、3D U-Net）
- TransUNet / Swin-UNETR / **MedSAM**（基础模型）
- 实例分割（细胞计数、病灶分割）

### Part 4: 检测、配准、重建
- 病灶检测（RetinaNet/U-Net 检测头）
- 弹性配准（图像对齐、随访对比）
- 低剂量 CT 重建、去噪
- 放射剂量与质量评估

### Part 5: 不确定性与可解释性 ⭐（本课重点）
- **MC Dropout**（近似贝叶斯）— 本课代码实现
- Deep Ensemble、Conformal Prediction（保证覆盖率）
- Calibration：温度缩放、expected calibration error
- 显著图 / Grad-CAM / prototype 解释
- **knows-when-it-doesn't-know**：拒绝低置信样本给医生

### Part 6: 联邦学习与隐私 ⭐
- 医疗数据不能集中 → **FedAvg**（McMahan 2017）
- 本课代码实现联邦学习模拟
- 差分隐私（DP-SGD）
- 安全聚合、同态加密
- Non-IID 问题（不同医院病种分布不同）
- 合成数据（GAN/Diffusion）缓解数据稀缺

### Part 7: 多模态与医疗 RAG ⭐
- 影像 + EHR（表格）融合
- 放射学报告生成（CNN + Transformer）
- **医疗 RAG**：LLM + 临床指南库，输出**带引用**建议 — 本课代码核心
- CHEXPERT formatter、RadGraph 报告结构化
- 生物医学 VLM（BiomedCLIP、LLaVA-Med）

### Part 8: 临床部署、伦理与法规
- 模型卡（Model Cards）、数据卡
- 偏倚审计（不同种族/性别/医院 AUROC 差异）
- 分布外（OOD）检测：换医院就掉点？
- **FDA SaMD**（Software as a Medical Device）路径
- 真实世界证据（RWE）与上市后监测
- 知情同意、数据治理（HIPAA、GDPR）

---

## 🧮 核心算法 / 数学

### Softmax + 交叉熵（本课分类器）
$$\hat{p}_c = \frac{e^{z_c}}{\sum_k e^{z_k}}, \quad \mathcal{L} = -\sum_c y_c \log \hat{p}_c$$

### MC Dropout（不确定性量化，本课代码）
- 推理时**保留 dropout**，对同一输入前向 $T$ 次
- 均值 = 预测，方差 = 认知不确定度（epistemic uncertainty）
$$\text{Var}[\hat{y}] = \frac{1}{T}\sum_t \hat{y}_t^2 - \left(\frac{1}{T}\sum_t \hat{y}_t\right)^2$$

### FedAvg（联邦平均，本课代码）
```
每轮 round:
  server 广播模型 w 给 K 个医院客户端
  每个客户端 c 在本地数据上训练 E 个 epoch → w_c
  server 聚合: w ← Σ_c (n_c / n) · w_c    (n_c = 该院样本数)
```

### Conformal Prediction（覆盖率保证）
- 用校准集求非一致性分数 $s_i$
- 选分位数 $q_{1-\alpha}$，给出**保证覆盖 $1-\alpha$** 的预测集

### U-Net 跳连（分割核心）
$$\text{decoder}_l = \text{Up}(\text{decoder}_{l+1}) \oplus \text{encoder}_l$$
- 跳连把高分辨率细节送回，恢复空间精度

### 医疗 RAG 引用约束
$$\text{answer} = \text{LLM}(\text{query}, \text{retrieve}(\text{guidelines}, \text{query})), \quad \text{每条断言附 } \text{source}_i$$
- 没有检索支撑 → 拒答（避免幻觉，本课代码 `source` 字段）

---

## 💻 项目代码

📁 `topic8-med/medical_rag.py`（CS286 + CS522 AI Healthcare 合并模块）

**实现**（纯 Python，无深度学习框架依赖）：
1. ✅ **合成 X-ray 数据** `generate_synthetic_xray`：normal / pneumonia / covid 三类（用特征向量代替像素）
2. ✅ **Softmax 分类器** `SimpleMedicalClassifier` + 交叉熵梯度下降训练
3. ✅ **评估** `evaluate_clf`：accuracy + 混淆矩阵
4. ✅ **医疗 RAG** `ClinicalGuideline` + 带引用的检索增强回答
5. ✅ **联邦学习模拟**（多客户端本地训练 → 聚合）
6. ✅ **不确定性量化**（MC Dropout 近似）

### 运行
```bash
cd stanford-cs-projects
python3 topic8-med/medical_rag.py
```

**输出示例**（分类 + 混淆矩阵）：
```
📋 CS286: Medical CV
   训练 X-ray 分类器 (normal/pneumonia/covid)...
   Accuracy: 0.92
   混淆矩阵:
              pred_normal  pred_pneumonia  pred_covid
   normal          28              2           0
   pneumonia        1             27           2
   covid            0              3          22
```

### 代码与课程的对应关系

| 课程概念 | 代码位置 |
|----------|----------|
| 医学影像分类（Part 2） | `SimpleMedicalClassifier` + `train_classifier` |
| 类别先验/特征（Part 1） | `generate_synthetic_xray` 三类不同高斯 |
| 评估与混淆矩阵（Part 5） | `evaluate_clf` |
| 不确定性（Part 5 MC Dropout） | `medical_rag.py` 不确定性量化段 |
| 联邦学习（Part 6 FedAvg） | `medical_rag.py` 联邦学习段 |
| 医疗 RAG + 引用（Part 7） | `ClinicalGuideline` + RAG 回答段 |
| 隐私保护（Part 6/8） | 联邦学习「数据不出院」的设计动机 |

> 注：本项目用纯 Python 演示医学 CV 全链路思想；真实作业会用 **PyTorch + MONAI/nnUNet + MIMIC-CXR 真实数据**，并要求跑 calibration、conformal、FedAvg 实验。

---

## 📊 关键论文（按 P0/P1/P2 分级）

### 🔴 P0（必读，奠基）
1. **Rajpurkar et al. 2017** "CheXNet: Radiologist-Level Pneumonia Detection"（[arXiv:1711.05225](https://arxiv.org/abs/1711.05225)）— 胸片分类里程碑
2. **Ronneberger, Fischer & Brox 2015** "U-Net: Convolutional Networks for Biomedical Image Segmentation"（[arXiv:1505.04597](https://arxiv.org/abs/1505.04597)）— 医学分割的 VGG
3. **Esteva et al. 2017** "Dermatologist-level classification of skin cancer with deep neural networks" *Nature* — 皮肤科 AI
4. **Gulshan et al. 2016** "Development and Validation of a Deep Learning Algorithm for Diabetic Retinopathy" *JAMA* — 眼底 AI

### 🟡 P1（重要方法 + 隐私）
5. **McMahan et al. 2017** "Communication-Efficient Learning of Deep Networks from Decentralized Data"（**FedAvg**）（[arXiv:1602.05629](https://arxiv.org/abs/1602.05629)）— 本课联邦学习来源
6. **Gal & Ghahramani 2016** "Dropout as a Bayesian Approximation"（[arXiv:1506.02142](https://arxiv.org/abs/1506.02142)）— MC Dropout
7. **Irvin et al. 2019** "CheXpert: Automated Chest Radiograph Interpretation"（[arXiv:1901.07031](https://arxiv.org/abs/1901.07031)）— 不确定标签
8. **Isensee et al. 2021** "nnU-Net: a self-configuring method for deep learning-based biomedical image segmentation" *Nature Methods*
9. **McKinney et al. 2020** "International evaluation of an AI system for breast cancer screening" *Nature* — 乳腺 AI（也引争议）
10. **Johnson et al. 2019** "MIMIC-CXR: A de-identified publicly available database of chest radiographs" *Sci. Data*

### 🟢 P2（基础模型 + 拓展）
11. **Ma et al. 2024** "Segment Anything in Medical Images"（**MedSAM**）（[arXiv:2304.12306](https://arxiv.org/abs/2304.12306)）
12. **Zhang et al. 2023** "BiomedCLIP: a multimodal biomedical foundation model"（[arXiv:2303.00915](https://arxiv.org/abs/2303.00915)）
13. **Chen et al. 2023** "LLaVA-Med: Training a Large Language-and-Vision Assistant for Biomedicine"
14. **Dosovitskiy et al. 2020** "An Image is Worth 16x16 Words"（ViT）（[arXiv:2010.11929](https://arxiv.org/abs/2010.11929)）— TransUNet 基础
15. **Lakshminarayanan, Pritzel, Blundell 2017** "Simple and Scalable Predictive Uncertainty Estimation"（Deep Ensemble）（[arXiv:1612.01474](https://arxiv.org/abs/1612.01474)）

---

## 🎯 学习路径（按角色）

| 角色 | 推荐路线 |
|------|----------|
| **医学影像 AI 研究** | CS286 → CheXNet/U-Net/nnU-Net → 投 MICCAI |
| **临床 AI 部署** | CS286 → 读 FDA SaMD → 实习 Stanford Health Care |
| **隐私/联邦学习** | CS286 Part 6 → 读 FedAvg/Optimus → FedML 实战 |
| **医疗 LLM/RAG** | CS286 Part 7 → BiomedCLIP/LLaVA-Med → 医院信息科 |
| **跨学科（MD+CS）** | CS286 + 统计 + 临床轮转 → 医学 AI 创业 |

---

## 💡 反思与批判

1. **AUROC 的陷阱**：医学论文普遍报 AUROC，但临床决策看的是**特定阈值下的 sensitivity/specificity** 和 **calibration**。一个 AUROC 0.95 但过度自信的模型会误导医生。本项目用混淆矩阵，比单一 accuracy 更诚实，但仍不够——生产要报 calibration curve。
2. **「放射科医生水平」的过度宣称**：CheXNet 等常被媒体说「超越医生」，但评估常在**单一数据集、回顾性、富样本**上做。换医院（distribution shift）就掉点，前瞻性多中心试验才是金标准。McKinney 乳腺 AI 的可重复性争议就是教训。
3. **标签噪声比想象严重**：CheXpert 的 uncertain 标签、不同放射科医生的标注差异（κ 一致性常只有 0.4-0.6）——模型在学什么？是病还是标注者的偏见？需要**soft label / 多标注者建模**。
4. **联邦学习的现实鸿沟**：FedAvg 在仿真里漂亮，但医院间 non-IID 严重（社区医院 vs 三甲病种完全不同），且沟通成本高、防投毒难。很多「联邦」最后退回「集中 + 合同」。
5. **医疗 RAG 的引用 ≠ 正确**：本项目强调 `source` 字段防幻觉，这是对的。但**检索到指南不等于建议合适**——指南会过时、会矛盾、患者有个体差异。RAG 是助手不是诊断者，必须留 human-in-the-loop。
6. **公平性常被事后补**：不同种族/性别/医院的 AUROC 差异若不在训练阶段就处理，后补 bias mitigation 效果有限。课程应把公平性放进 loss 而非只在评估。
7. **合成数据的双刃剑**：本项目用合成 X-ray（高斯特征）是为了无依赖演示，但**真实医学影像的纹理、伪影、解剖变异无法用简单分布模拟**——结论不能外推到临床。

---

## 🚀 扩展阅读

完成后推荐：
1. **CS522** AI in Healthcare（与本课合并的项目）
2. **BMI 215 / BIOMEDIN 231**（Stanford 生物医学信息学）
3. **MICCAI** 会议论文（医学影像 AI 顶会）
4. 工具栈：MONAI + nnUNet + 3D Slicer + ITK + SimpleITK
5. 数据集：MIMIC-CXR、CheXpert、NIH ChestX-ray14、ISIC、Camelyon17、BraTS
6. 监管深读：FDA *Artificial Intelligence/Machine Learning-Based Software as a Medical Device* 指南
7. 公平性：Obermeyer 2019 *Science*「Dissecting racial bias in an algorithm」——必读的 bias 警示案例

---

**对应代码**：`topic8-med/medical_rag.py`（X-ray 分类 + 医疗 RAG + 联邦学习 + 不确定性量化）
