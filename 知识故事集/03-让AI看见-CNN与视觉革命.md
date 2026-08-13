# 03 · 让 AI 看见：CNN 与视觉革命（1989-2017）

> **时间**：1989-2017，28 年
> **核心冲突**：怎么让机器"看见"？从生物视觉启发到抛弃生物视觉。
> **嵌入概念**：CNN、卷积、池化、ResNet、ViT

---

## 🎬 故事

### 1959 · 猫的视觉皮层

David Hubel 和 Torsten Wiesel，Harvard 神经科学家。他们把电极插入猫的视觉皮层，给猫看不同图片，记录神经元激活。

**惊人发现**：猫脑视觉皮层有**简单细胞**（检测边缘）和**复杂细胞**（检测移动边缘）。**层次化结构**：底层检测简单特征，高层检测复杂特征。

1981 年他俩拿 **Nobel 奖**。

### 1989 · LeCun 的"层级结构"模仿

Yann LeCun，Bell Labs。受 Hubel-Wiesel 启发：**机器能不能也用层级结构？**

1989 年，他设计 **LeNet**——卷积神经网络（CNN）：

```
图片 → [卷积层] → [池化层] → [卷积层] → [池化层] → [全连接] → 输出
       ↑检测边缘    ↑压缩         ↑检测形状   ↑压缩        ↑分类
```

**卷积（convolution）核心思想**：
- 用一个小窗口（3×3 或 5×5）逐格扫过图片
- 每个窗口学一个**特征检测器**（边缘 / 纹理 / 形状）
- **同一窗口的权重在整张图共享**（translation invariance）

**为什么有效**：
- 图片里"猫耳朵"在左上还是在右下，都是"猫耳朵"。**权值共享**让网络自动学到这种平移不变性。
- 参数从全连接的几百万 → CNN 的几万。**可训练**。

LeNet 用在邮编识别——**美国银行 10% 的支票由 LeNet 自动识别**。但没人觉得这是革命。

### 1998-2012 · 黑暗年代

LeCun 论文 1998 年发表，被引用很多但**没有真正流行**。原因：
- 算力不够（CPU 训 CNN 太慢）
- 数据不够（MNIST 6 万张被认为"很大"）
- SVM / random forest 数学清晰，效果稳定

LeCun 在 NYU 当教授，继续做 CNN，**但整个领域沉睡了 13 年**。

### 2012 · AlexNet 唤醒

AlexNet 用了 LeNet 的架构，**但深得多（8 层 vs 5 层）+ 大得多（60M vs 60K 参数）+ GPU 训练**。

CNN 一夜复活。

### 2014 · VGG 和 GoogLeNet

2014 ILSVRC：
- **VGG**（Oxford）：把 AlexNet 推到 16-19 层。简洁漂亮。错误率 7.3%。
- **GoogLeNet**（Google）：22 层 + Inception module（多尺度特征）。错误率 6.7%。

但 VGG 和 GoogLeNet 都遇到问题：**网络再深就训不动了**。

### 2015 · ResNet 的天才跳跃

He Kaiming（何恺明），微软研究院。30 岁。

2015 年他问一个简单问题：**为什么网络不能更深？**

直觉：**更深的网络至少应该和浅网络一样好**——浅网络是深网络的子集（深层可以学 identity）。

但实际：**深层网络反而更差**。为什么？

**He Kaiming 的洞察**：**网络学 identity 很难**——非线性层很难学到 "什么都不做"。

**解决方案**：**残差连接（residual connection）**——把输入直接跳过几层加到输出：
```
output = F(x) + x
```

如果这一层该做"什么都不做"，**F(x) 学到 0**——比学 identity 容易。

2015 年 12 月，**ResNet** 发布：**152 层**。错误率 **3.57%**——**比人眼（5%）还低**。

**ResNet 是深度学习的 iPhone 时刻**——之后所有深层网络都用残差连接。

### 2017 · Attention 侵入视觉

2017 年 Transformer 诞生后，视觉圈开始想：**Transformer 能做视觉吗？**

2020 年 **ViT**（Dosovitskiy et al.，Google）：**完全抛弃卷积**。把图片切成 16×16 的 patch，每个 patch 当一个 token，扔进 Transformer。

**结果**：在大量数据上预训练后，ViT 比 ResNet 还好。

**2022 后，ViT 成为主流**。CNN 没死，但 Transformer 一统视觉。

### CNN → ViT 的哲学转变

CNN 的核心信念：**先验很重要**（卷积 = 平移不变性先验）。
ViT 的核心信念：**数据可以替代先验**（足够大的 Transformer + 足够多的数据，自己学到先验）。

**这是从"人在设计架构"到"人在 scale 数据"的范式转变**。

---

## 🧠 核心概念

- **卷积（Convolution）**：小窗口 + 权值共享。检测局部特征。
- **池化（Pooling）**：下采样，降维 + 增强平移不变性。
- **感受野（Receptive Field）**：一个神经元能"看到"的原图区域。越深的神经元感受野越大。
- **ResNet / 残差连接**：`output = F(x) + x`。让深层网络可训。
- **ViT（Vision Transformer）**：把图片当 token 序列，用 Transformer。2022+ 视觉主流。

## 🎨 类比

- **CNN** = 一个用放大镜逐格扫图片的侦探：每个放大镜学一个特定特征（边缘 / 纹理 / 形状）
- **池化** = 侦探每隔几步眯起眼看大致轮廓，丢掉精确位置
- **卷积 + 池化 + 卷积 + 池化** = 侦探从细节（边缘）→ 中层（部件）→ 整体（物体），层级抽象
- **ResNet 残差** = 在每层旁边修一条"应急通道"。如果主路堵了（学不动），数据走应急通道（identity）。深层不再退化。
- **ViT** = 抛弃卷积，让 transformer 自己学。**像语言模型看图片**——把图片切成 patch 当句子读

## 💡 反直觉发现

1. **生物启发的 CNN 不是终点**：CNN 模仿猫脑视觉皮层，但 ViT 完全不模仿——结果更好。**自然选择不是最优解**。

2. **简单跳跃改变一切**：ResNet 的核心创新就一行代码 `x + F(x)`。**最伟大的发明有时极简**。

3. **数据 > 先验**：CNN 用了 40 年先验（卷积 = 平移不变性）。但 ViT 用更多数据替代先验。**这预示着 LLM 的 scale 路线**。

4. **机器视觉已超过人类**：2015 年 ResNet 错误率 3.57% < 人眼 5%。**视觉任务"解决"了**——但理解（captioning / reasoning）还远未解决。

5. **LeCun 候了 25 年**：1989 LeNet → 2014 退休论调。**LeCun 现在还在做 world model / JEPA**——同样的耐心。

## 🛠️ 我该深挖什么

### work4ai 系列
- [`../讲透基础模型/`](../讲透基础模型/)：CNN → ViT 完整演进
- [`../讲透Transformer/`](../讲透Transformer/)：ViT 用 transformer
- [`../讲透泛化/`](../讲透泛化/)：为什么深层网络能泛化

### 必读
- **LeCun et al. 1998 "Gradient-Based Learning Applied to Document Recognition"**（LeNet 圣经）
- **He et al. 2015 "Deep Residual Learning"**（ResNet）
- **Dosovitskiy et al. 2020 "An Image is Worth 16×16 Words"**（ViT）

### 实验
```python
# 用 PyTorch 实现 LeNet on MNIST（5 层，<60K 参数，几分钟训练）
# 然后实现 ResNet-18 on CIFAR-10
# 看 ResNet 的残差连接如何让 18 层可训
```

---

## 🔗 下一篇

下一篇：[**04 · Transformer 的诞生**（2017）](04-Transformer的诞生.md)—— Google Brain 8 人如何用一个 attention 公式杀死整个 NLP 圈。

---

**版本**：v1.0（2026-08-13）
**核心隐喻**：**视觉从模仿猫脑到不模仿任何脑。LeCun 候了 25 年，He Kaiming 一行代码改变一切。**
