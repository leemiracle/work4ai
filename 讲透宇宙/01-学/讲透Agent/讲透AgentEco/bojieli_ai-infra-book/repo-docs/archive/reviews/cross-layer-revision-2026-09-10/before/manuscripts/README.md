# 正文书稿

十二章正文已系统补入三条主线：应用可编程性向模型与上下文上移、模型与基础设施的双向协同，以及改变约束后重新选择系统。此前新增九幅插图沿用全书统一的 Hands-On Large Language Models 风格，以 SVG、PNG、PDF 提供。

各章均以“本章小结”收尾，资料说明移出正文，来源保留为脚注。

[全书 PDF](../book/AI-Infra-Book.pdf) · [本轮修改与验证](../reviews/core-principles-revision-2026-09-10/README.md) · [思想实验复算](../calculations/results/core-principles.json)

| 章 | 正文 | 配图 |
| --- | --- | ---: |
| 1 | [初识 AI Infra](<01-初识 AI Infra.md>) | 17 |
| 2 | [模型架构](<02-模型架构.md>) | 35 |
| 3 | [推理与训练负载](<03-推理与训练负载.md>) | 33 |
| 4 | [加速器架构](<04-加速器架构.md>) | 26 |
| 5 | [算子与运行时](<05-算子与运行时.md>) | 31 |
| 6 | [超节点](<06-超节点.md>) | 36 |
| 7 | [数据中心网络](<07-数据中心网络.md>) | 48 |
| 8 | [单实例推理](<08-单实例推理.md>) | 36 |
| 9 | [分布式推理](<09-分布式推理.md>) | 34 |
| 10 | [训练系统](<10-训练系统.md>) | 41 |
| 11 | [资源调度与运行环境](<11-资源调度与运行环境.md>) | 39 |
| 12 | [端边云协同](<12-端边云协同.md>) | 32 |

配图由各章 `build.py` 生成，统一样式位于 `figure_style/`，本轮新增图位于 `core_principles_figures.py`。图号与阅读顺序由正文派生，记录在各章 `figure-index.json`。

在线阅读由 Markdown 自动构建，详见[网站构建与发布](../website/README.md)。章节构建脚本的临时 HTML 预览写入 `build/legacy/`，不提交到仓库。

在安装 matplotlib、numpy、Markdown、PyMuPDF 和 Playwright 的 Python 环境中，运行 `python manuscripts/ch01/build.py`（其他章节替换章号）；全书 PDF 运行 `python book/build_pdf.py`，另需 Pandoc 与 XeLaTeX。

这里的条件比较属于教学推导，未新增 GPU 性能实测；原始实验、模型配置和版本来源仍保留在对应目录。


V4／V4.1 贯穿案例已沿十二章展开，新增六幅图，见[修改与验证记录](../reviews/v41-throughline-2026-09-10/README.md)。模型状态、CED 输入处理、缓存恢复和路由选择采用同一组[固定条件与复算](../calculations/results/v41-throughline.json)。
