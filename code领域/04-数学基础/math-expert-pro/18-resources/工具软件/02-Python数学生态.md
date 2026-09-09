# Python 数学生态与替代工具对比

> Python 不是唯一选择，但对学数学最实用。以下按任务推荐工具。

---

## 一、按任务推荐工具

| 任务 | 首选 | 替代 | 说明 |
|------|------|------|------|
| 线代计算 | NumPy | MATLAB/Julia | NumPy 最通用 |
| 科学计算 | SciPy | MATLAB | ODE/优化/统计 |
| 符号计算 | SymPy | Mathematica/Maple | SymPy 免费 |
| 可视化 | matplotlib | Plotly/Desmos | matplotlib 最灵活 |
| 统计建模 | statsmodels | R/Stata | R 更专业 |
| ML | scikit-learn/PyTorch | TensorFlow | PyTorch 研究友好 |
| 图论 | networkx | igraph | networkx 最易用 |
| 形式化 | Lean 4 | Coq/Agda | Lean 4 最活跃 |
| 笔记 | Jupyter | Obsidian | Jupyter=代码+文档 |

## 二、Python 数学栈速查

```python
import numpy as np        # 线代/数组
import scipy.linalg as la # 矩阵分解
import scipy.optimize     # 优化
import sympy as sp        # 符号计算
import matplotlib.pyplot  # 可视化
import networkx as nx     # 图论
from sklearn...           # 机器学习
```

## 三、替代语言对比

| 语言 | 数学优势 | 劣势 |
|------|---------|------|
| Python | 生态最全 | 速度中等 |
| Julia | 数学语法优美 | 生态小 |
| MATLAB | 矩阵运算原生 | 昂贵 |
| Mathematica | 符号计算最强 | 昂贵+封闭 |
| R | 统计最强 | 通用编程弱 |
| Lean 4 | 形式化验证 | 学习曲线陡 |

## 四、Desmos / GeoGebra（交互可视化）
- [Desmos](https://www.desmos.com/calculator)：在线图形计算器，快速可视化
- [GeoGebra](https://www.geogebra.org)：几何+代数交互
- [Wolfram Alpha](https://www.wolframalpha.com)：计算知识引擎
