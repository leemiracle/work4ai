# CNN 卷积精读：参数共享与平移不变性

> 参照：LeCun 1989 / He 2015 (ResNet) / csapp Ch6(局部性原理)
>
> csdiy 对应：tinycnn(原) + csapp Ch6(cache局部性) + tinytorch

---

## 一、全连接 vs 卷积：为什么 FC 不适合图像

```
图片: 224×224×3 = 150,528 个输入

全连接层（FC）: 150528 → 1000
  参数量: 150528 × 1000 = 150M 参数（一层！）

卷积层（Conv）: 3×3 kernel, 64 filters
  参数量: 3×3×3×64 = 1,728 参数（少 100,000 倍）
```

**关键**：FC 每个 pixel 连接都独立权重 → 参数爆炸。
Conv 的 kernel 在整张图上**滑动共享** → 参数极少。

---

## 二、Conv2d 的数学

### 互相关（实际用的）vs 卷积（数学定义）

```
互相关（Cross-Correlation）:  Y[i,j] = Σ X[i+m, j+n] × K[m,n]
卷积（Convolution）:          Y[i,j] = Σ X[i-m, j-n] × K[m,n]

深度学习的 "卷积" 实际是互相关（kernel 不翻转）
→ 但效果一样（因为 K 是可学习的，翻转不翻转等价）
```

### 计算示例

```
输入 X (5×5):          Kernel K (3×3):
1 2 3 4 5              1 0 -1
6 7 8 9 0              1 0 -1
1 2 3 4 5              1 0 -1
6 7 8 9 0
1 2 3 4 5

输出 Y[0,0] = 1×1+2×0+3×(-1) + 6×1+7×0+8×(-1) + 1×1+2×0+3×(-1)
            = 1-3 + 6-8 + 1-3 = -6
```

---

## 三、三个超参数

### Stride（步长）

```
Stride=1: kernel 每次移动 1 pixel → 输出大小 ≈ 输入大小
Stride=2: kernel 每次移动 2 pixel → 输出缩小一半（下采样）
```

### Padding（填充）

```
Same Padding: 输出大小 = 输入大小（在边缘补 0）
Valid Padding: 不补 0 → 输出比输入小

输出大小 = (W - K + 2P) / S + 1
  W=输入宽, K=kernel宽, P=padding, S=stride
```

### Dilation（空洞）

```
普通卷积（dilation=1）: kernel 连续 3×3
空洞卷积（dilation=2）: kernel 间隔取 → 实际感受野 5×5

→ 不增加参数量 → 扩大感受野
→ 用于语义分割（DeepLab）
```

---

## 四、感受野（Receptive Field）

```
Layer 1: 3×3 conv → 每个输出 pixel 看到 3×3 的输入
Layer 2: 3×3 conv → 每个 Layer 2 pixel 看到 3 个 Layer 1 pixel
  → 每个 Layer 1 pixel 看到 3×3 输入
  → Layer 2 感受野 = 5×5

Layer N 的感受野 = 1 + N × (K - 1)
  K=3, N=10 → 感受野 = 21×21

→ 深层网络看到更大的区域（为什么 ResNet 需要 100+ 层）
```

---

## 五、参数共享的直觉

```
全连接: 每个 pixel 位置有独立权重
  → 学到的 "边缘检测器" 只能在一个位置用

卷积: kernel 在所有位置共享权重
  → 学到的 "边缘检测器" 可以在任何位置用
  → 平移不变性（Translation Invariance）

数学等价: 卷积 = 在所有位置应用同一个 FC + 共享权重
```

---

## 六、经典 CNN 架构演化

| 模型 | 年份 | 创新 | 参数 |
|------|------|------|------|
| LeNet-5 | 1998 | 第一个 CNN | 60K |
| AlexNet | 2012 | ReLU + Dropout + GPU | 60M |
| VGG | 2014 | 3×3 小 kernel 堆叠 | 138M |
| ResNet | 2015 | 残差连接（跳 100+ 层）| 25M |
| Inception | 2015 | 多尺度并行 kernel | 23M |
| MobileNet | 2017 | 深度可分离卷积 | 4M |
| EfficientNet | 2019 | 复合缩放 | 66M |
| ConvNeXt | 2022 | 用 CNN 技巧追赶 Transformer | 89M |

---

## 七、深度可分离卷积（MobileNet）

```
标准 Conv (3×3, 64 filters, RGB):
  3 × 3 × 3 × 64 = 1,728 参数

深度可分离:
  ① Depthwise: 每个 channel 独立卷积 → 3×3×3 = 27 参数
  ② Pointwise: 1×1 conv 改变 channel 数 → 3×64 = 192 参数
  总计: 27 + 192 = 219 参数（少 8 倍！）

→ MobileNet 在手机上实时运行的关键
```

---

## 八、CNN vs Transformer

```
CNN:
  ✅ 平移不变性（内置归纳偏置）
  ✅ 参数效率高（参数共享）
  ✅ 局部特征提取强
  ❌ 全局建模弱（需要深层堆叠扩大感受野）

ViT (Vision Transformer):
  ✅ 全局注意力（一眼看到整张图）
  ✅ 大数据下超越 CNN
  ❌ 参数效率低（没有归纳偏置）
  ❌ 小数据集上不如 CNN

趋势: ViT 在大数据下胜出，CNN 在效率/边缘设备上仍有优势
ConvNeXt: 用 CNN 技巧追赶 Transformer → 在某些任务上超越 ViT
```

---

## 九、一句话总结

> CNN = kernel 在整张图上滑动共享 → 参数少 + 平移不变性。
>
> 感受野 = 每层 +K-1 → 深层网络看到更大区域。
>
> **参数共享是 CNN 的灵魂——用 1,728 个参数学习"边缘检测器"，比 FC 的 150M 参数高效 100,000 倍。**

---

*配套：[tinycnn(原)](../projects/tinycnn/) | [csapp Ch6(cache局部性)](../notes/csapp-程序员视角.md) | [tinytorch/nn.py](../projects/tinytorch/nn.py)*
