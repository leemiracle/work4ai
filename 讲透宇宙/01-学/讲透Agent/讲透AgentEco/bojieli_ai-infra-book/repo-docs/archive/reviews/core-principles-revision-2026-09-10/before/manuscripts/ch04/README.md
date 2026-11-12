# 第四章正文与配图

[阅读版 HTML](../04-加速器架构.html) · [正文 Markdown](../04-加速器架构.md) · [写作大纲](../../outlines/04-加速器架构.md)

七节、二十三小节，采用问题、机制、推导与设计取舍的教材体例。用同一 Q 投影贯穿计算与存储分析，再加入注意力、专家路径、封装和专用化；章内三道带解例题与七项实验。正文包含脚注和本地引用。

十四幅插图均提供 SVG、PNG 和 PDF。图号、图题和说明全部位于正文图片外；图内仅保留机制、子面板、单位与坐标标注。阅读 HTML 嵌入图像、公式与字体，可以离线阅读。

| 图 | 内容 | 文件 |
|---|---|---|
| 4-1 | 输入行数增加怎样分摊权重读取 | [SVG](figure-4-1-reuse.svg) · [PNG](figure-4-1-reuse.png) · [PDF](figure-4-1-reuse.pdf) |
| 4-2 | 加速器组成与矩阵数据路径 | [SVG](figure-4-2-components.svg) · [PNG](figure-4-2-components.png) · [PDF](figure-4-2-components.pdf) |
| 4-3 | 专家分派怎样改变补零计算量 | [SVG](figure-4-3-expert-rows.svg) · [PNG](figure-4-3-expert-rows.png) · [PDF](figure-4-3-expert-rows.pdf) |
| 4-4 | 提高不同资源速率后的瓶颈转移 | [SVG](figure-4-4-attention.svg) · [PNG](figure-4-4-attention.png) · [PDF](figure-4-4-attention.pdf) |
| 4-5 | 低比特权重的两种计算方法 | [SVG](figure-4-5-precision.svg) · [PNG](figure-4-5-precision.png) · [PDF](figure-4-5-precision.pdf) |
| 4-6 | 权重、工作区与逐条请求的 KV 占用 | [SVG](figure-4-6-capacity.svg) · [PNG](figure-4-6-capacity.png) · [PDF](figure-4-6-capacity.pdf) |
| 4-7 | 并发请求数怎样限制有效带宽 | [SVG](figure-4-7-memory.svg) · [PNG](figure-4-7-memory.png) · [PDF](figure-4-7-memory.pdf) |
| 4-8 | 子矩阵有效数据与行步长 | [SVG](figure-4-8-layout.svg) · [PNG](figure-4-8-layout.png) · [PDF](figure-4-8-layout.pdf) |
| 4-9 | 最少三个输入槽怎样实现连续计算 | [SVG](figure-4-9-pipeline.svg) · [PNG](figure-4-9-pipeline.png) · [PDF](figure-4-9-pipeline.pdf) |
| 4-10 | 计算位置怎样改变跨裸片传输内容 | [SVG](figure-4-10-locality.svg) · [PNG](figure-4-10-locality.png) · [PDF](figure-4-10-locality.pdf) |
| 4-11 | 带宽翻倍对大小消息的不同收益 | [SVG](figure-4-11-interconnect.svg) · [PNG](figure-4-11-interconnect.png) · [PDF](figure-4-11-interconnect.pdf) |
| 4-12 | 固定权重与随 batch 增长的 KV 读取 | [SVG](figure-4-12-specialization.svg) · [PNG](figure-4-12-specialization.png) · [PDF](figure-4-12-specialization.pdf) |
| 4-13 | 输入行数怎样改变计算与传输时间 | [SVG](figure-4-13-roofline.svg) · [PNG](figure-4-13-roofline.png) · [PDF](figure-4-13-roofline.pdf) |
| 4-14 | 以 DRAM 读取检验投影耗时的缓存解释 | [SVG](figure-4-14-performance.svg) · [PNG](figure-4-14-performance.png) · [PDF](figure-4-14-performance.pdf) |

## 依据与复现

先阅读已有 calculations、survey、案例与实际实验记录，再编写正文。[reading-notes.md](reading-notes.md)说明采用范围；[sources.json](sources.json)锁定输入；[figure-data.json](figure-data.json)保存画图数据；[manifest.json](manifest.json)记录输出校验值。没有新跑 GPU 或模型质量实验。

```sh
python3 -m venv /tmp/ch04-book-venv
/tmp/ch04-book-venv/bin/pip install -r manuscripts/ch04/requirements.txt
/tmp/ch04-book-venv/bin/python manuscripts/ch04/build.py
/tmp/ch04-book-venv/bin/python manuscripts/ch04/check_browser.py
/tmp/ch04-book-venv/bin/python manuscripts/ch04/verify.py
```

构建需要 Python 3 和 Node.js。优先采用 macOS 中文字体，Linux 可安装 Noto Sans CJK 或传 `--font`。公式使用仓库已有 `../ch03/vendor/katex/` 的 KaTeX 0.16.11 和许可证，构建后字体和公式已嵌入 HTML。浏览器检查优先使用本机 Chrome，也支持 `CH04_CHROME` 指定可执行文件；没有浏览器时可安装 Playwright Chromium。

[validation.json](validation.json)包含大纲一致性、链接、图号、公式、来源与数值校验；[browser-validation.json](browser-validation.json)检查 1440 px 和 390 px 视口的图片、公式、目录与溢出。图布局另有自动边界检查与人工预览。

本次全章编辑的论证调整、有效数字规则与移入配套的细节见[编辑说明](editorial-revision.md)。

本轮全章重写增加节间递进、设计转折点和随文思考题；[教学推导与题解](teaching-notes.md)提供三槽流水、计算翻倍变体及容量、互联和 Roofline 边界。[证据记录](evidence-notes.md)集中保存版本、原始采集方法与数值检查。

[语言修订说明](language-revision.md)记录术语与中文句法调整；[段落衔接与配图修订](visual-revision.md)说明新增图的教学目的及对应推导。
