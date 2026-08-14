# TOOLS_STACK：数学家工具栈

> **本章核心**：现代数学家不只用纸笔。完整的工具栈决定你的效率。下面是**所有必装/推荐**的工具，按优先级。
>
> 标注：[必装] [推荐] [选学]

---

## 一、证明助手（形式化）⭐ 你的最大杠杆

| 工具 | 用途 | 优先级 | 备注 |
|------|------|--------|------|
| **Lean 4** | 主流数学形式化，配 Mathlib | [必装] ⭐ | 你已会（ai-os-dd 经验）。详见 [`LEAN_MATH_TRACK.md`](LEAN_MATH_TRACK.md) |
| **Mathlib4** | Lean 的数学库 | [必装] | https://github.com/leanprover-community/mathlib4 |
| **Coq / Rocq** | 另一主流证明助手 | [选学] | 数学 / CS 双强。Compcert 用它 |
| **Isabelle / HOL Light** | 第三大证明助手 | [选学] | 用于形式化 Flyspeck（开普勒猜想）|
| **Agda** | 依赖类型论 | [选学] | 更"理论" |

---

## 二、符号计算

| 工具 | 用途 | 优先级 | 备注 |
|------|------|--------|------|
| **SageMath** | 开源 Mathematica 替代 | [必装] | Python 接口，免费，覆盖数论/代数/微积分 |
| **SymPy** | Python 轻量符号 | [必装] | 已熟 NumPy，半天上手 |
| **Mathematica** | 商业级符号 + 数值 | [推荐] | 如有机构访问 |
| **Maple** | 商业替代 | [选学] | 较老 |
| **Magma** | 数论 / 代数几何专用 | [选学] | 商业但强大 |

---

## 三、数值计算

| 工具 | 用途 | 优先级 | 备注 |
|------|------|--------|------|
| **Python + NumPy / SciPy** | 数值计算主力 | [必装] | 你已会 |
| **Julia** | 高性能数值 | [推荐] | 语法像 Python，性能近 C |
| **MATLAB** | 工程 / 控制 | [选学] | 商业，被 Julia 替代 |
| **R** | 统计 | [推荐] | 如果你做统计方向 |
| **JAX** | ML + 自动微分 | [推荐] | 你已会（PyTorch 背景容易迁移）|

---

## 四、LaTeX / 数学写作

| 工具 | 用途 | 优先级 | 备注 |
|------|------|--------|------|
| **TeX Live**（Linux）| LaTeX 发行版 | [必装] | `apt install texlive-full` |
| **MacTeX**（Mac）| 同上 | [必装] | |
| **MiKTeX**（Windows）| 同上 | [必装] | |
| **VS Code + LaTeX Workshop** | 编辑器 | [必装] | 你已用 VS Code |
| **Overleaf** | 在线协作 | [必装] | 免费版够用 |
| **TeXstudio** | 专门 LaTeX IDE | [选学] | |
| **MacDown / Typora** | Markdown 写作 | [推荐] | blog 用 |

### 必会宏包

```latex
\usepackage{amsmath, amssymb, amsthm}  % 数学符号
\usepackage{mathtools}                  % amsmath 增强
\usepackage{thmtools}                   % 自定义定理环境
\usepackage{hyperref, cleveref}         % 引用
\usepackage{tikz, pgfplots}             % 图
\usepackage{biblatex}                   % 文献（替代 bibtex）
\usepackage{geometry, fancyhdr}         % 排版
\usepackage{enumitem}                   % 列表
\usepackage{booktabs}                   % 表格
```

---

## 五、文献管理

| 工具 | 用途 | 优先级 | 备注 |
|------|------|--------|------|
| **Zotero** | 文献管理 | [必装] | 开源，跨平台 |
| **Better BibTeX for Zotero** | Zotero ↔ LaTeX 自动同步 | [必装] | |
| **Mendeley** | 替代 | [选学] | 商业 |
| **Papers (ReadCube)** | 替代 | [选学] | 商业 |

---

## 六、文献检索

| 数据库 | 用途 | 备注 |
|--------|------|------|
| **arXiv** | 预印本 | 免费必 RSS |
| **MathSciNet (MR)** | Mathematical Reviews | 机构订阅 |
| **zbMATH Open** | 欧洲 counterpart | 2021 起部分免费 |
| **Google Scholar** | 通用 | 免费 |
| **MathOverflow** | 研究级问答 | 免费 |
| **OEIS** | 整数序列 | 免费 |
| **MacTutor** | 数学史 | 免费 |

### 推荐工具

- **arxiv-vanity**（https://www.arxiv-vanity.com/）：arXiv 论文 HTML 渲染
- **ar5iv**（https://ar5iv.org/）：arXiv 论文 HTML 版
- **Connected Papers**（https://www.connectedpapers.com/）：可视化论文引用图
- **Semantic Scholar**：AI 增强的搜索

---

## 七、绘图

| 工具 | 用途 | 备注 |
|------|------|------|
| **TikZ** | LaTeX 内嵌矢量图 | 出版级必备 |
| **matplotlib** | 数据图 | 你已会 |
| **Asymptote** | 矢量图 | 比 TikZ 强大，语法复杂 |
| **GeoGebra** | 交互几何 | 学实分析/几何用 |
| **Ipe** | 矢量图（牛津派）| |
| **Inkscape** | SVG 编辑 | 修图用 |

---

## 八、AI 辅助

| 工具 | 用途 | 备注 |
|------|------|------|
| **GitHub Copilot** | 自动补全（Lean / LaTeX / Python）| Tao 在用 |
| **Lean Copilot** | 专门的 Lean AI | https://github.com/lean-dojo/LeanCopilot |
| **Claude / GPT-4 / Gemini** | 解释 / 生成 / 头脑风暴 | 你已用 |
| **ChatGPT Advanced Data Analysis** | 跑 Python | |

> ⚠️ **AI 是助手不是答案**。LLM 会**幻觉**数学。所有 AI 给的证明都要手动验。Lean 是金标准。

---

## 九、笔记本 / 实验环境

| 工具 | 用途 | 备注 |
|------|------|------|
| **Jupyter Notebook** | Python / Julia / SageMath 笔记本 | 必装 |
| **JupyterLab** | Jupyter 升级版 | 推荐 |
| **Observable** | JS 交互笔记本 | 选学 |
| **Marimo** | Python 反应式笔记本 | 选学，新潮 |
| **Quarto** | 科学/技术文档（含 R/Python/Julia）| 推荐 |

---

## 十、协作 / 版本控制

| 工具 | 用途 | 备注 |
|------|------|------|
| **Git + GitHub** | 版本控制 | 必装 |
| **GitLab** | 替代（自托管）| 选学 |
| **Overleaf** | LaTeX 协作 | 必装 |
| **CoCalc** | 在线 SageMath / Jupyter | 选学 |
| **Notion / Obsidian** | 笔记 / 知识管理 | 选学 |

---

## 十一、阅读 / 标注

| 工具 | 用途 | 备注 |
|------|------|------|
| **Zotero** | PDF 阅读 + 标注 | 已列 |
| **Skim**（Mac）| PDF 阅读 | |
| **Okular**（Linux）| PDF 阅读 | |
| **Hypothesis** | 网页标注 | 选学 |

---

## 十二、通信 / 社区

| 工具 | 用途 |
|------|------|
| **Lean Zulip**（https://leanprover.zulipchat.com）| Lean 社区主战场 |
| **MathOverflow**（https://mathoverflow.net）| 研究级问答 |
| **math.stackexchange** | 教学-硕士级 |
| **Discord 数学频道** | 浅一些 |
| **Twitter 数学圈** | Tao / Gowers / Buzzard |

---

## 十三、安装清单（一键脚本参考）

```bash
# Linux / Mac（你已用 Linux）
# 1. 系统包
sudo apt install texlive-full         # LaTeX
sudo apt install python3 python3-pip  # Python
sudo apt install git                  # Git

# 2. Python 包
pip install numpy scipy sympy matplotlib jupyter
pip install sagemath-standard          # SageMath（或用 apt）
pip install julia                      # 或单独装 Julia

# 3. Lean
curl https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh -sSf | sh
# elan 是 Lean 版本管理（类似 rustup / pyenv）

# 4. Mathlib
git clone https://github.com/leanprover-community/mathlib4
cd mathlib4 && lake build

# 5. VS Code 扩展
code --install-extension leanprover.lean4
code --install-extension James-Yu.latex-workshop
code --install-extension ms-azuretools.vscode-docker

# 6. Zotero
# 从 https://www.zotero.org/ 下载
# 安装 Better BibTeX 插件

# 7.（可选）Julia
curl -fsSL https://install.julialang.org | sh
```

---

## 十四、最小起步套装（本周装好）

如果你只能装 5 个：

1. **Lean 4 + Mathlib**（你的杠杆）
2. **TeX Live**（写论文）
3. **SageMath**（符号实验）
4. **Zotero**（文献管理）
5. **VS Code + LaTeX Workshop + Lean 4 扩展**

---

## 十五、工具不是答案

记住 Tao 在 2025-02 演讲里说的：

> "工具是放大器，不是替代品。坏工具让人慢，但**好工具不能让人变聪明**。"

你的工具栈应该**服务于你的思考**，不是让你"看起来像在做数学"。

---

📌 **下一步**：
- 本周装好 §十四的 5 个最小工具
- 注册 Lean Zulip + MathOverflow
- 看 [`COMMUNITY_AND_CAREER.md`](COMMUNITY_AND_CAREER.md) 找社区接入
