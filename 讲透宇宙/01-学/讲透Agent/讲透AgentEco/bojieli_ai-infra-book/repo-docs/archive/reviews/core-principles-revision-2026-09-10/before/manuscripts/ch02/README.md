# 第2章正文与配图

[Markdown 正文](../02-模型架构.md) · [HTML 阅读版](../02-模型架构.html)

本章按逐节设计组织概念、推导、例题与练习。当前共 32 幅配图，均提供 SVG 和 PNG；正文、图表中的数学表达采用 LaTeX，HTML 使用本地 KaTeX 渲染并嵌入图片与字体。

[前三章逐节设计](../../research/ch01-03-model-led-rewrite-2026-09-10/section-design.md) · [练习参考解答](../../research/ch01-03-model-led-rewrite-2026-09-10/exercise-answers.md) · [本轮修订记录](../../research/ch01-03-model-led-rewrite-2026-09-10/README.md)

## 200K 长上下文对照

新增图 2-28 对比 8K 与 200K 历史下的单步矩阵运算量，表 2-D 补充历史交互工作与状态容量。200K 按 204800 token；Qwen3-8B 为超出固定配置上限的结构外推。

[SVG](figure-2-long-context-compute.svg) · [PNG](figure-2-long-context-compute.png) · [PDF](figure-2-long-context-compute.pdf) · [计算数据](long-context-comparison.json) · [复算程序](compare_long_context.py)

运行 `python3 manuscripts/ch02/compare_long_context.py` 后再构建本章。当前完整图号以 [figure-index.json](figure-index.json) 为准；下表保留早期配图文件导航。

## 配图

图号按阅读顺序排列，文件名保持稳定。

| 图示 | SVG | PNG |
| --- | --- | --- |
| 图 2-1 序列模型的计算依赖 | [SVG](figure-2-1-dependencies.svg) | [PNG](figure-2-1-dependencies.png) |
| 图 2-2 四个模型的层数、隐藏维度与专家数 | [SVG](figure-2-architecture.svg) | [PNG](figure-2-architecture.png) |
| 图 2-3 Qwen3-8B 单层的尺寸与数据流 | [SVG](figure-2-2-layer.svg) | [PNG](figure-2-2-layer.png) |
| 图 2-4 历史读取的阶梯与批内权重复用 | [SVG](figure-2-history.svg) | [PNG](figure-2-history.png) |
| 图 2-5 查询头与共享历史的对应关系 | [SVG](figure-2-3-sharing.svg) | [PNG](figure-2-3-sharing.png) |
| 图 2-6 KV 共享与潜变量压缩 | [SVG](figure-2-4-cache.svg) | [PNG](figure-2-4-cache.png) |
| 图 2-7 V4 的窗口、压缩与索引 | [SVG](figure-2-5-sparse.svg) | [PNG](figure-2-5-sparse.png) |
| 图 2-8 逐位置历史与固定状态矩阵 | [SVG](figure-2-recurrence.svg) | [PNG](figure-2-recurrence.png) |
| 图 2-9 混合注意力与专家计算的组合 | [SVG](figure-2-6-hybrid.svg) | [PNG](figure-2-6-hybrid.png) |
| 图 2-10 状态容量、访问与输入工作 | [SVG](figure-2-7-state-growth.svg) | [PNG](figure-2-7-state-growth.png) |
| 图 2-11 同样的专家运算量与不同的权重读取量 | [SVG](figure-2-expert-reuse.svg) | [PNG](figure-2-expert-reuse.png) |
| 图 2-12 稠密层与 V4 层的数据流 | [SVG](figure-2-8-residual.svg) | [PNG](figure-2-8-residual.png) |
| 图 2-13 模型权重、单步计算与历史状态的对照 | [SVG](figure-2-resources.svg) | [PNG](figure-2-resources.png) |
| 图 2-14 权重、历史与显存可容纳的并发请求数 | [SVG](figure-2-9-capacity.svg) | [PNG](figure-2-9-capacity.png) |
| 图 2-15 请求输入与计算状态映射 | [SVG](figure-2-10-request.svg) | [PNG](figure-2-10-request.png) |

## 构建与数据

在仓库根目录安装本目录 requirements.txt 中的依赖，并准备 Node.js，运行：

```sh
python manuscripts/ch02/build.py
```

生成器查找 macOS 或 Noto 中文字体，也可使用 `--font /path/to/font.ttf`。共享机制图由 [teaching_figures.py](../teaching_figures.py) 生成。

[sources.json](sources.json) 保存输入文件及哈希；[figure-data.json](figure-data.json) 保存绘图数据；[manifest.json](manifest.json) 保存生成产物校验值；[math-validation.json](math-validation.json) 记录公式解析。输入变化时须先审查再更新来源锁。本轮使用已有 calculations、survey 与实验记录以及明确给出的教学条件，没有执行新的 GPU 实验。

完整模型表包含 Qwen3-8B、Qwen3.6、V4-Flash、Kimi K3 及 V3 历史参照。[verify_tables.py](verify_tables.py) 对照固定计算结果检查矩阵尺寸；[compare_models.py](compare_models.py) 生成统一条件的模型比较表。
