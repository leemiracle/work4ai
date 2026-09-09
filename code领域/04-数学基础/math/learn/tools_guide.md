# 离散数学学习工具推荐指南

> 不是代码库，而是**直接打开就能学**的工具

---

## 一、本地可用工具（已安装）

### 1. Jupyter Notebook / JupyterLab ★★★★★

**是什么**: 交互式笔记本，可以边写公式边运行代码，即时看到结果

**适合**: 所有离散数学内容的学习笔记、实验验证

**启动方式**:
```bash
cd ~/workspace/math/learn
jupyter lab
# 或
jupyter notebook
```

**学习用法**:
- 一个格子写 Markdown 公式（如 $A \cup B$），下一个格子写代码验证
- 支持 LaTeX 公式渲染
- 图论可以直接画图显示在笔记本里
- 做完的笔记就是 `.ipynb` 文件，随时回看

---

### 2. Manim（3Blue1Brown 数学动画引擎）★★★★★

**是什么**: YouTube 数学博主 3Blue1Brown 开发的数学动画工具，能做出教科书级的可视化动画

**适合**: 图论动画、集合运算可视化、逻辑门动画、算法执行过程动画

**命令**:
```bash
# 渲染动画为 mp4
manim -pql script.py SceneName
# -pql = 预览 + 低质量（快速预览）
# -pqh = 预览 + 高质量
```

**能做什么**:
- 真值表逐步生成动画
- 图的遍历过程动画（BFS/DFS 箭头移动）
- 集合交并补的文氏图动画
- 数列递推过程的可视化
- 矩阵运算逐步展示

---

### 3. Graphviz（已装）★★★★

**是什么**: 图的描述语言 + 渲染引擎，用文字描述图，自动画出来

**适合**: 画有限状态机、二叉树、Hasse图、流程图

**用法**: 写 `.dot` 文件，渲染为图片
```bash
dot -Tpng graph.dot -o graph.png
```

---

### 4. Z3 + automata-lib（已装）★★★★

**是什么**: 不需要写代码的"验证器"

- **Z3**: 输入逻辑公式 → 自动判断真假/找解（数独秒解）
- **automata-lib**: 输入 DFA/NFA → 自动最小化、等价判断、转正则表达式

---

## 二、强烈推荐的在线工具（免费）

### 1. Wolfram Alpha ★★★★★
> https://www.wolframalpha.com

**最强数学搜索引擎**，输入自然语言就能算：

| 输入示例 | 功能 |
|---|---|
| `truth table (p and q) implies r` | 自动生成真值表 |
| `solve x^3 = 2 mod 7` | 模运算 |
| `gcd(120, 84)` | 最大公约数 + 步骤 |
| `is 561 prime?` | 素性检测 |
| `C(10,3)` | 组合数 |
| `Fibonacci sequence` | Fibonacci 数列 |
| `prime factorization 360` | 素因子分解 |
| `Euler totient 30` | 欧拉函数 |
| `inverse of 7 mod 11` | 模逆 |

**付费版**还能显示**详细求解步骤**。

---

### 2. VisuAlgo ★★★★★
> https://visualgo.net

**算法可视化平台**，动画演示每一步：

- 图算法：BFS、DFS、Dijkstra、Prim、Kruskal、拓扑排序
- 排序算法
- 二叉搜索树、AVL树
- **可以自己画图**，然后看算法在上面跑

---

### 3. Automata Tutor / JFLAP ★★★★★
> https://automatatutor.com (需注册)
> http://www.jflap.org (桌面应用，Java)

**自动机理论专用学习工具**：

- 画 DFA/NFA，自动验证是否正确
- NFA → DFA 转换可视化
- 正则表达式 ↔ 自动机互转
- 上下文无关文法推导树
- 图灵机模拟器
- **做练习题，系统自动批改**

---

### 4. CS Academy Graph Editor ★★★★
> https://csacademy.com/app/graph_editor/

**最简洁好用的在线画图工具**：
- 左边输入边列表，右边实时显示图
- 支持有向/无向/带权图
- 自动布局
- 截图直接用于笔记

---

### 5. Desmos ★★★★
> https://www.desmos.com/calculator

**在线图形计算器**：
- 画函数图像
- 画 Venn 图
- 验证生成函数系数
- 支持参数滑块（看参数变化的影响）

---

### 6. MathBits NoteMath / Mathway ★★★★
> https://www.mathway.com

输入题目 → **显示详细求解步骤**，覆盖：
- 逻辑化简
- 组合计数
- 矩阵运算
- 方程求解

---

### 7. ProofWiki ★★★★
> https://proofwiki.org

**数学证明维基百科**：
- 每个定理都有完整证明
- 逻辑学、集合论、图论、数论全覆盖
- 证明过程超链接到每个用到的引理

---

## 三、桌面应用推荐

### 1. Obsidian ★★★★★
> https://obsidian.md

**最适合数学学习的笔记软件**：
- Markdown + LaTeX 公式（用 `$...$` 或 `$$...$$`）
- 双向链接，构建知识图谱
- 知识之间自动生成关系图（本身就是离散数学！）
- 插件丰富：Excalidraw 画图、间隔重复记忆

**安装**:
```bash
# 下载 AppImage
wget https://github.com/obsidianmd/obsidian-releases/releases/latest/download/Obsidian-1.7.7.AppImage -O ~/Obsidian.AppImage
chmod +x ~/Obsidian.AppImage
~/Obsidian.AppImage
```

---

### 2. Anki ★★★★★
> https://apps.ankiweb.net

**间隔重复记忆卡片**，背定理/定义神器：
- 定理名称 → 定理内容
- 公式 → 含义
- 每天自动安排复习
- 支持 LaTeX 公式卡片

**安装**:
```bash
sudo apt install anki
```

---

### 3. Xournal++ ★★★★
> https://xournalpp.github.io

**手写数学笔记**（如果你有手写板/触屏）：
- 直接在 PDF 课件上做笔记
- 手写公式 + LaTeX
- 图形绘制工具

```bash
sudo apt install xournalpp
```

---

### 4. Lean 4 (证明助手) ★★★★
> https://lean-lang.org  |  https://live.lean-lang.org（在线版）

**交互式定理证明器**：
- 输入定理，系统**实时检查**证明是否正确
- 像写代码一样写证明
- **Lean 4 游戏** (https://adam.math.hhu.de) 从零学证明：
  - Natural Number Game（自然数游戏）
  - Set Theory Game（集合论游戏）
  - Logic Game（逻辑游戏）

---

## 四、学习路径推荐

```
入门（看动画理解）
  ├─ VisuAlgo ──── 图算法动画
  ├─ 3Blue1Brown ── YouTube 数学直觉
  └─ Wolfram Alpha ─ 随时验证计算

理解（做练习巩固）
  ├─ Automata Tutor ── 自动机练习
  ├─ JFLAP ──── 形式语言实验
  └─ Jupyter Notebook ─ 自己动手验证

证明（写证明训练）
  ├─ ProofWiki ──── 阅读标准证明
  ├─ Lean 4 ──── 交互式写证明
  └─ Obsidian ──── 整理知识体系

记忆（间隔重复）
  └─ Anki ──── 背定理和公式
```

---

## 五、快速启动命令汇总

```bash
# Jupyter 笔记本（学习主战场）
jupyter lab

# Manim 数学动画
manim -pql your_script.py YourScene

# Graphviz 画图
dot -Tpng file.dot -o output.png

# Obsidian 笔记
~/Obsidian.AppImage

# Anki 背卡片
anki
```
