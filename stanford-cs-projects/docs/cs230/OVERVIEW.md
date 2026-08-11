# CS230: Deep Learning

> Stanford University, Autumn 2025
> Instructors: **Andrew Ng**（吴恩达，深度学习先驱）+ **Kian Katanforoosh**（Workera 创始人）
> Course Manager: John Cho | Head TA: Hee Jung Choi
> Time: 周二 11:30 AM–1:20 PM, Hewlett Teaching Center 200
> Format: **翻转课堂**（Coursera 在线课程 + 线下进阶讲座 + 项目指导）
> Prerequisites: 概率论 (CS109 / STATS116) + 线性代数 (MATH51) + 基础编程
> Difficulty: ⭐⭐⭐（斯坦福最热门 DL 入门课，面向广泛受众）
> 官网: https://cs230.stanford.edu/

---

## 📚 课程定位

CS230 是斯坦福**最具标志性的深度学习入门课**，也是全球数百万学习者通过 Coursera 接触 DL 的起点。它的独特之处在于三位一体的设计：

1. **Coursera 翻转课堂**——学生在家观看 deeplearning.ai Deep Learning Specialization 的视频，完成编程作业和测验
2. **线下进阶讲座**——Andrew Ng 与行业专家（如 Pranav Rajpurkar 医疗 AI）讲授视频课未深入的前沿主题
3. **真实项目驱动**——40% 的成绩来自一个完整的季度项目，由 TA 一对一指导

> **核心哲学**：不只是"会用框架"，而是**理解原理 + 能领导 ML 项目**。

Andrew Ng 把这门课设计成"从理论到工程到策略"的完整闭环——这也是为什么《Structuring Machine Learning Projects》（Course 3）作为独立模块存在，教的是**如何做 ML 决策**而非算法本身。

---

## 🎯 学习目标

完成 CS230 后，学生应能够：

1. **理解** 神经网络的前向传播与反向传播机制（从数学推导到代码实现）
2. **掌握** 关键训练技术：Adam 优化、Dropout、BatchNorm、Xavier/He 初始化、梯度裁剪
3. **构建** CNN（卷积网络）处理图像——分类、检测（YOLO）、分割（U-Net）、风格迁移、人脸识别
4. **构建** RNN/LSTM/Transformer 处理序列——字符级语言模型、机器翻译（Attention）、触发词检测
5. **应用** ML 工程策略——正交化、单一评估指标、数据集划分、错误分析、迁移学习
6. **领导** 一个端到端的深度学习项目（从想法到部署）
7. **阅读** 顶会研究论文（课程专门安排论文阅读方法论讲座）

---

## 📅 完整模块（10 讲 + 5 门 Coursera 课程）

CS230 的教学内容分为 5 门 Coursera 课程（C1–C5），每门含数个 Module（M），对应线下 10 次讲座：

### Course 1: Neural Networks and Deep Learning（神经网络基础）
- **L1 (9/23)** — 课程导论 + 深度学习项目案例
- **L2 (9/30)** — 通过案例理解关键 AI 概念
  - C1M1: 深度学习导论
  - C1M2: 神经网络基础（Logistic Regression → 浅层网络）
  - **编程作业**: Python + NumPy 基础、Logistic Regression 心智模型
- **L3 (10/7)** — DL 项目全生命周期
  - C1M3: 浅层神经网络
  - C1M4: 深度神经网络
  - **编程作业**: 平面数据分类、逐步构建 DNN、DNN 应用

### Course 2: Improving Deep Neural Networks（改进 DNN）
- **L4 (10/14)** — 对抗鲁棒性与生成模型
  - C2M1: 深度学习实践（初始化、正则化、梯度检查）
  - C2M2: 优化算法（Mini-batch GD、Momentum、Adam）
  - **编程作业**: 初始化、正则化、梯度检查、优化
- **L5 (10/21)** — 深度强化学习
  - C2M3: 超参数调优、BatchNorm、编程框架（TensorFlow）
  - C3M1 + C3M2: ML 策略 1 & 2（正交化、单一指标、错误分析）

### Course 3: Structuring Machine Learning Projects（ML 工程策略）
- 这是 Andrew Ng 的独门秘籍——**不教算法，教决策**
- 核心：如何定义目标 → 如何诊断问题 → 如何分配资源

### Course 4: Convolutional Neural Networks（卷积神经网络）
- **L6 (10/28)** — 职业建议 + 论文阅读 + 医疗 AI 嘉宾
  - C4M1: CNN 基础（卷积、池化）
  - C4M2: 深度卷积模型（LeNet → ResNet → MobileNet）
  - **编程作业**: 逐步构建 ConvNet、ResNet、MobileNet 迁移学习
- **L7 (11/4)** — Democracy Day（无课）
  - C4M3 + C4M4: ConvNet 应用
  - **编程作业**: YOLO 目标检测、神经风格迁移、人脸识别、U-Net 分割

### 期中考试
- **11/6** — 6:00–9:00 PM 线下，覆盖前半学期内容

### Course 5: Sequence Models（序列模型）
- **L8 (11/11)** — 超越模型：增强 LLM 应用
  - C5M1: RNN 基础
  - **编程作业**: 构建 RNN、Dinosaur 字符级语言模型、LSTM 即兴爵士
- **L9 (11/18)** — 职业建议 + 论文阅读 + 嘉宾讲座
  - C5M2: NLP 与词嵌入（Word2Vec、去偏）
  - C5M3: Seq2Seq + Attention
  - **编程作业**: 词向量操作、Emojify、注意力机器翻译、触发词检测
- **L10 (12/2)** — 模型内部解析 + 课程总结
  - C5M4: Transformer 网络 ⭐
  - **编程作业**: TensorFlow 实现 Transformer 架构

### 项目里程碑
| 节点 | 日期 | 内容 |
|------|------|------|
| 项目提案 | 10/14 | 与 TA 会面验证想法 |
| 项目里程碑 | 11/11 | 中期进展报告 |
| 最终报告 | 12/5 | 完整项目提交 |
| Poster Session | 12/10 | 海报展示 |

---

## 🧮 核心算法与技术

### 1. 反向传播（Backpropagation）
链式法则逐层计算梯度：
$$\frac{\partial L}{\partial W^{[l]}} = \frac{\partial L}{\partial a^{[l]}} \cdot \frac{\partial a^{[l]}}{\partial z^{[l]}} \cdot \frac{\partial z^{[l]}}{\partial W^{[l]}}$$

### 2. 优化算法谱系
| 算法 | 核心思想 | 适用场景 |
|------|---------|---------|
| **Mini-batch GD** | 小批量降低方差 | 通用 |
| **Momentum** | 指数加权移动平均 | 加速收敛 |
| **RMSprop** | 自适应学习率（二阶矩） | RNN |
| **Adam** | Momentum + RMSprop | **默认首选** |
| **AdamW** | 解耦权重衰减 | Transformer |

### 3. 正则化技术
- **L2 正则化**: $L = L_0 + \frac{\lambda}{2m} \sum \|W\|^2$
- **Dropout**: 训练时随机置零，测试时关闭
- **Early Stopping**: 监控验证集
- **Data Augmentation**: 数据增强（翻转、裁剪、色彩）

### 4. BatchNorm（批归一化）
$$\hat{z} = \gamma \cdot \frac{z - \mu_B}{\sqrt{\sigma_B^2 + \epsilon}} + \beta$$
对每层激活值做归一化，加速训练并提升稳定性。

### 5. CNN 核心操作
- **卷积**: 特征提取（边缘 → 纹理 → 物体部件）
- **池化**: 降维 + 平移不变性
- **ResNet 残差连接**: $y = F(x) + x$，解决梯度消失，训练超深网络

### 6. Transformer（Attention）
$$\text{Attention}(Q,K,V) = \text{softmax}\left(\frac{QK^T}{\sqrt{d_k}}\right)V$$
CS230 在最后一讲引入 Transformer，标志着课程内容已从经典 RNN 时代升级到大模型时代。

---

## 💻 项目代码（本仓库）

📁 `topic1-choice/choice_theory.py`

虽然该文件标注为 CS329H 的 Choice Theory 作业，其核心**用深度学习训练 Bradley-Terry 模型**恰好体现了 CS230 教授的 DL 基础——从损失函数定义到梯度下降优化：

**与 CS230 的映射**：
1. ✅ **损失函数设计**（C2M1）—— Bradley-Terry 的负对数似然 $L = -\sum \log \sigma(v_w - v_l)$
2. ✅ **梯度下降**（C1M4 / C2M2）—— 手写梯度 $\frac{\partial L}{\partial v_w} = -(1 - \sigma(v_w - v_l))$
3. ✅ **优化器**（C2M2）—— 等价于 SGD，可无缝替换为 Adam
4. ✅ **NumPy/纯 Python 实现**（C1M1）—— 呼应 CS230 "Python Basics with NumPy" 的理念：**不依赖框架，从零理解**

```bash
cd topic1-choice
python3 choice_theory.py
```

**输出示例**:
```
📋 2. Bradley-Terry 模型训练
   训练数据: 500 偏好对
   学到的 v: {'A': 0.81, 'B': -0.21, 'C': -0.60}
   真实 v: {'A': 2.0, 'B': 1.0, 'C': 0.5}
```

> 💡 这正是 Andrew Ng 反复强调的理念：**先从零实现理解原理，再用框架提效**。

---

## 📊 关键论文与资源

### 🔴 课程推荐阅读
1. **Srivastava et al. 2014** "Dropout: A Simple Way to Prevent Neural Networks from Overfitting" (JMLR)
2. **Huang et al. 2017** "DenseNet: Densely Connected Convolutional Networks" (CVPR)
3. **He et al. 2016** "Deep Residual Learning for Image Recognition" (ResNet, CVPR)

### 🟡 Coursera 配套教材
4. **Deep Learning Specialization** (deeplearning.ai) — 5 门课的完整视频
5. Goodfellow, Bengio, Courville "Deep Learning" (2016) — 经典教材

### 🟢 扩展
6. Vaswani et al. 2017 "Attention Is All You Need"（Transformer，CS230 L10）
7. Rajpurkar et al. 2017 "CheXNet"（嘉宾 Pranav Rajpurkar 的工作）
8. Ng, Andrew "Machine Learning Yearning"（ML 工程策略的免费书）

---

## 🎯 学习路径建议

| 角色 | 推荐路径 |
|------|---------|
| **零基础入门 AI** | CS230（基础）→ CS224N（NLP）→ CS231N（CV）|
| **想转行做 DL 工程** | CS230 + CS312（训练工程）→ 实战项目 |
| **想做 AI 研究** | CS230 → CS229（ML 理论）→ CS329 系列 |
| **非技术背景理解 AI** | 只看 Coursera Course 1+3（理论 + 策略）|

### CS230 vs CS229 vs CS231N
| 课程 | 定位 | 偏向 |
|------|------|------|
| **CS230** | DL 工程入门 | 实践 + 项目 |
| **CS229** | ML 理论基础 | 数学推导 |
| **CS231N** | CV 深度学习 | 视觉专项 |

---

## 💡 反思

### 课程优势
1. **Andrew Ng 的教学法**——极擅长将复杂概念拆解为直觉 + 数学 + 代码三层
2. **翻转课堂效率高**——Coursera 视频打磨成熟，线下时间留给进阶与互动
3. **项目导向**——40% 的项目权重让学生产出真实作品，许多人以此进入 AI 行业
4. **ML Strategy 独一无二**——Course 3 教的工程决策思维在其他课程中罕见

### 潜在局限
1. **内容更新滞后**——Coursera 视频录制较早，Transformer 仅在最后触及
2. **理论深度有限**——相比 CS229，数学严谨性不足
3. **框架绑定 TensorFlow**——编程作业以 TF 为主，PyTorch 生态未充分覆盖
4. **缺乏大模型训练**——不会涉及 LLM 预训练/微调的工程实践（需 CS312 补充）

---

## 🚀 扩展阅读

完成 CS230 后推荐：
1. **CS231N** — 深入卷积网络与计算机视觉
2. **CS224N** — 深入 NLP 与 Transformer
3. **CS312** Deep Learning Alchemy — 大规模训练工程（如何把 loss 真正跑下来）
4. **CS329H** — 从人类偏好学习（RLHF 的理论基础）
5. Andrew Ng 的《Machine Learning Yearning》—— 免费的 ML 工程策略手册

---

**最后更新**: 2026-08-11
**对应代码**: `topic1-choice/choice_theory.py`（DL 基础训练演示）
**数据来源**: cs230.stanford.edu + Coursera Deep Learning Specialization
