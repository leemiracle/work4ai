# 第八章正文与配图

[阅读版 HTML](../08-单实例推理.html) · [正文 Markdown](../08-单实例推理.md) · [写作大纲](../../outlines/08-单实例推理.md)

正文按执行基线、批处理、KV 生命周期、压缩与卸载、推测解码、服务选择六节展开，共 22 个小节、九项分层练习。贯穿设计采用 32 GiB 设备、12 GiB 状态预算、2K／8K 输入、256 输出和 3 秒期限；章末综合例题完成容量、时间、费用的选择，并通过预算和输出长度变化解释最优方案变化。

十五幅插图提供 SVG、PNG 和 PDF。图号与完整 caption 放在图片外；HTML 内嵌图片、公式和字体，可离线阅读并点击放大。

| 图 | 内容 | SVG | PNG | PDF |
|---|---|---|---|---|
| 8-1 | 请求时间线 | [SVG](figure-8-1-lifecycle.svg) | [PNG](figure-8-1-lifecycle.png) | [PDF](figure-8-1-lifecycle.pdf) |
| 8-2 | 批量与读取量 | [SVG](figure-8-2-batch.svg) | [PNG](figure-8-2-batch.png) | [PDF](figure-8-2-batch.pdf) |
| 8-3 | 调度与输出间隔 | [SVG](figure-8-3-scheduling.svg) | [PNG](figure-8-3-scheduling.png) | [PDF](figure-8-3-scheduling.pdf) |
| 8-4 | 分块注意力访问范围 | [SVG](figure-8-4-attention.svg) | [PNG](figure-8-4-attention.png) | [PDF](figure-8-4-attention.pdf) |
| 8-5 | 分页与共享 | [SVG](figure-8-5-pages.svg) | [PNG](figure-8-5-pages.png) | [PDF](figure-8-5-pages.pdf) |
| 8-6 | 多轮前缀结构 | [SVG](figure-8-6-prefix.svg) | [PNG](figure-8-6-prefix.png) | [PDF](figure-8-6-prefix.pdf) |
| 8-7 | 同一缓存空间的两种用法 | [SVG](figure-8-7-cache-choice.svg) | [PNG](figure-8-7-cache-choice.png) | [PDF](figure-8-7-cache-choice.pdf) |
| 8-8 | KV 分组格式 | [SVG](figure-8-8-kv-format.svg) | [PNG](figure-8-8-kv-format.png) | [PDF](figure-8-8-kv-format.pdf) |
| 8-9 | 预取缓冲与容量 | [SVG](figure-8-9-offload.svg) | [PNG](figure-8-9-offload.png) | [PDF](figure-8-9-offload.pdf) |
| 8-10 | KV／Q 精度与质量 | [SVG](figure-8-10-kv-quality.svg) | [PNG](figure-8-10-kv-quality.png) | [PDF](figure-8-10-kv-quality.pdf) |
| 8-11 | 草稿验证与修正 | [SVG](figure-8-11-verification.svg) | [PNG](figure-8-11-verification.png) | [PDF](figure-8-11-verification.pdf) |
| 8-12 | 查询开销与推测收益 | [SVG](figure-8-12-speculation.svg) | [PNG](figure-8-12-speculation.png) | [PDF](figure-8-12-speculation.pdf) |
| 8-13 | 到达率与有效吞吐 | [SVG](figure-8-13-service.svg) | [PNG](figure-8-13-service.png) | [PDF](figure-8-13-service.pdf) |
| 8-14 | 配置的容量与时间 | [SVG](figure-8-14-design.svg) | [PNG](figure-8-14-design.png) | [PDF](figure-8-14-design.pdf) |
| 8-15 | 局部加速与完整任务 | [SVG](figure-8-15-task.svg) | [PNG](figure-8-15-task.png) | [PDF](figure-8-15-task.pdf) |

## 来源与构建

先读已有 calculations 与 survey，再据此写作；采用范围见[阅读记录](reading-notes.md)。[来源锁](sources.json)保存实际采用文件的 SHA-256，[图数据](figure-data.json)保存绘图输入，[产物清单](manifest.json)记录正文、HTML 和图文件的校验值。模型性能来自已有记录，本轮没有重新执行 GPU 实验。

在仓库根目录运行：

```sh
python3 -m venv /tmp/ch08-book-venv
/tmp/ch08-book-venv/bin/pip install -r manuscripts/ch08/requirements.txt
/tmp/ch08-book-venv/bin/python manuscripts/ch08/build.py
/tmp/ch08-book-venv/bin/python manuscripts/ch08/verify.py
```

需要 Node.js 和中文字体；默认查找 macOS Arial Unicode 或 Linux Noto CJK，也可通过 `--font /path/to/font` 指定。KaTeX 0.16.11 与许可证放在 vendor/katex 中。来源改变时构建会停止，应先阅读变化，再更新来源锁。

可选浏览器检查另需 Playwright 与 Chrome／Chromium：

```sh
/tmp/ch08-book-venv/bin/pip install playwright
/tmp/ch08-book-venv/bin/python manuscripts/ch08/browser-check.py --executable '/path/to/chrome'
```

[内容与证据核验](validation.json)覆盖六节标题、实验与外部图注、引用、图片内无图号、源数据、算式与离线 HTML。[公式核验](math-validation.json)保存渲染数量；[浏览器检查](browser-validation.json)记录桌面与手机宽度、图片加载、公式和目录锚点。[桌面预览](preview-desktop.png)与[手机预览](preview-mobile.png)供快速查看。

## 教学组织与核对

正文由同一设计条件逐步推导：完整请求页容量、批量读取交点、共享前缀、缓存保留概率、格式容量、搬移成本、推测解码输出数与边际预算，最后比较 A—D 配置。模型与框架历史集中在延伸阅读，运行条件通过脚注进入原资料。

练习分为计算、分析、数据解释、概率推导和综合设计，核心编号仍为 8-2、8-4、8-9。配套实验目录沿用原 ID，映射见[重组记录](../../research/ch08-reorganization-2026-09-10/README.md)。[计算题参考结果](exercise-notes.md)给出主要中间结果；[教学算例检查](teaching-check.py)以有理数独立计算容量边界、时间、费用与最优方案变化，结果保存在 [teaching-validation.json](teaching-validation.json)，由 verify.py 一并执行。

批量曲线使用已有精确权重与 KV 输入；调度图的到达和最长输出间隔直接来自保存的事件；质量图逐任务对齐并发及两次重复。完整样本、版本与来源摘要保留在配套数据中。

## 与第九章的范围划分

本章现名“推理优化”，研究给定设备组合下的运行配置；第九章研究计算与状态的分布和服务规模。单卡算例的容量条件已明确，多卡实例需逐卡计算容量。正文文件路径保留，章名、目录和阅读版均已更新。[修改说明](../../research/ch08-ch09-scope-revision/README.md)。
