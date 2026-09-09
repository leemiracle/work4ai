# 文本分类器 - 实现指南

本指南将逐步指导你完成文本分类器的实现。

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

IMDB情感分析、AG News、自定义文本数据集

### 预处理数据

```python

# 文本预处理示例
from transformers import AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")

def preprocess_text(text):
    tokens = tokenizer(text, 
                      padding=True, 
                      truncation=True, 
                      max_length=128,
                      return_tensors="pt")
    return tokens
            
```

---

## 第3步: 模型实现

### 核心模块

```python

# Transformer文本分类器
import torch
import torch.nn as nn

class TextClassifier(nn.Module):
    def __init__(self, num_classes, model_name="bert-base-uncased"):
        super().__init__()
        # TODO: 加载预训练模型
        pass
    
    def forward(self, input_ids, attention_mask):
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

准确率、精确率、召回率、F1分数

---

## 第6步: 优化改进

### 性能优化

调整batch size、使用预训练模型、添加正则化

### 功能扩展

多标签分类、层级分类、零样本分类

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
