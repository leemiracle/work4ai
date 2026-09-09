# 图像分类器 - 实现指南

本指南将逐步指导你完成图像分类器的实现。

---

## 第1步: 环境搭建

### 安装依赖

```bash
pip install -r requirements.txt
```

### 验证安装

```bash
python -c "import torch; print(torch.__version__)"
```

---

## 第2步: 数据准备

### 下载数据

CIFAR-10、ImageNet或自定义数据集

### 预处理数据

```python

# 数据预处理示例
from torchvision import transforms

transform = transforms.Compose([
    transforms.Resize(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                        std=[0.229, 0.224, 0.225])
])
            
```

---

## 第3步: 模型实现

### 核心模块

```python

# CNN图像分类器
import torch
import torch.nn as nn

class ImageClassifier(nn.Module):
    def __init__(self, num_classes=10):
        super().__init__()
        # TODO: 实现CNN网络
        pass
    
    def forward(self, x):
        # TODO: 实现前向传播
        pass
            
```

### 辅助函数

```python
# TODO: 添加辅助函数
```

---

## 第4步: 训练模型

### 训练脚本

```bash
python main.py --mode train
```

### 监控训练

查看 `logs/` 目录下的日志文件。

---

## 第5步: 测试评估

### 运行测试

```bash
python test.py
```

### 评估指标

准确率（Accuracy）、F1分数、混淆矩阵

---

## 第6步: 优化改进

### 性能优化

数据增强、学习率调度、Dropout正则化

### 功能扩展

迁移学习、模型蒸馏、对抗训练

---

## 常见问题

### Q1: 训练速度慢怎么办？
A: ...

### Q2: 模型不收敛怎么办？
A: ...

---

## 进阶方向

1. [进阶方向1]
2. [进阶方向2]
3. [进阶方向3]

---

**祝你学习愉快！** 🚀
