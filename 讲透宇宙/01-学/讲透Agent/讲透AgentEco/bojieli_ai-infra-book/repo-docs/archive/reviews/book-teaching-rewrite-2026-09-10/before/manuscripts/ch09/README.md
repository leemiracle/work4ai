# 第九章正文与插图

[阅读版 HTML](../09-分布式推理.html) · [正文 Markdown](../09-分布式推理.md) · [写作前阅读记录](reading-notes.md)

正文按七节 outline 展开，包含24个小节、7个定量例题及1份解题示范、17幅原创插图、10道练习及来源注释。采用提出问题、定义计量口径、推导、代入例题、改变条件的教材体例；已有实测与条件计算分别呈现。正文及注释约1.84万汉字（不含数字和英文），为可继续编辑的完整初稿。

## 插图

全章共 17 幅原创图，按正文顺序编号。新增图重点展示任务分配、数据复用和时间依赖。

| 文件 | 内容 |
| --- | --- |
| figure-9-1-organization | 多卡协作完整副本和计算分工 |
| figure-9-2-state | 请求阶段、实例分工与状态寿命 |
| figure-9-3-pd | 阶段配比与请求率 |
| figure-9-4-allocation | 不同请求下八个执行单元的分工 |
| figure-9-5-local | 专家权重搬运与CPU就地计算 |
| figure-9-6-reuse | 专家复用与执行位置边界 |
| figure-9-7-footprint | 同样分派次数下的专家数与输入行数 |
| figure-9-8-handoff | 消息数量与启动开销 |
| figure-9-9-balance | 八张卡的任务分布与结果合并时刻 |
| figure-9-10-experts | 专家副本的准备与回本 |
| figure-9-11-overlap | 专家分派计算与结果合并的流水时间线 |
| figure-9-12-cache | 读取页与可复用连续前缀 |
| figure-9-13-route | 缓存路由中排队取回与计算的时间关系 |
| figure-9-14-migration | 状态生成与后台复制的进度 |
| figure-9-15-recovery | 输出记录与KV检查点的恢复位置 |
| figure-9-16-composition | 直接交接与共享池中转 |
| figure-9-17-service | 服务能力与启动积压消退 |

每幅图均提供 SVG、PNG、PDF。图号只在外部图注中出现。build.py 与 extra-figures.py 共同生成插图，figure-data.json 保存数值。阅读版内嵌全部图片和公式字体，可离线阅读。

## 复现

在仓库根目录，使用独立Python环境安装本目录requirements.txt。构建另外需要Node.js与CJK字体；默认尝试macOS Arial Unicode或Linux Noto Sans CJK，也可传入`--font /path/to/font`。数学排版复用仓库已有的`manuscripts/ch06/vendor/katex`，不联网加载CDN。

```sh
python3 -m venv /tmp/ai-infra-ch09-build
/tmp/ai-infra-ch09-build/bin/pip install -r manuscripts/ch09/requirements.txt
/tmp/ai-infra-ch09-build/bin/python manuscripts/ch09/build.py
python3 manuscripts/ch09/verify.py
```

build.py在绘图前核对sources.json。来源文件变化时应先复核它是否影响本章，再更新锁定记录，不跳过哈希检查。构建不启动模型，不运行新的GPU实验。

浏览器验证为可选项，需Playwright与本地Chrome／Chromium：

```sh
python manuscripts/ch09/browser-check.py --executable /path/to/chrome
```

## 已完成检查

- [validation.json](validation.json)：章节与outline一致，实验和图注顺序、引用、来源、图片内部无图号、关键数值独立复算、导出哈希等302项检查。
- [browser-validation.json](browser-validation.json)：1440px和390px视口，17张图片、109个公式正常，目录锚点有效，无页面级横向溢出。
- [figure-layout-check.json](figure-layout-check.json)：图中文字均在画布范围内。
- [math-validation.json](math-validation.json)：KaTeX构建时严格解析全部公式。
- [manifest.json](manifest.json)：正文、阅读版、图数据和51份图片导出的SHA256。

已目视检查九图缩略总览、桌面正文与手机组合图页面；配套浏览器截图保存在本目录。验证证明本次书稿与证据的一致性，不把既有计算子账提升为尚未完成的跨机性能实验。

## 数字论证修订

本轮按[修订说明](revision-numeric/README.md)改写各节数字推导，统一精度并重组主图。原图4／5依正文出现顺序交换：新图4讲专家复用，新图5讲消息频次；实验9-4／9-5编号保持原义。正文、outline配图计划、生成器和导出文件均同步，历史计算与实验记录中的图号按原记录解释。

## 连贯性与教材体例修订

本轮以八 worker 服务设计贯穿开篇、阶段配比、缓存和生命周期，例 9.7 在相同资源与负载下选择直接 PD，并推导 25 秒排空目标所需的最低能力。MoE 的第二条推导从批内复用连接到执行位置、最忙设备和副本回本。正文删去段末泛化提醒与自我辩护，必要条件放入例题，版本与证据说明放在注释。

CPU 专家先用低复用、高复用数值解释选择翻转，再给出路径公式；缓存与迁移新增依赖关系的具体解释。练习加入完整设计题和一份已解示范，区分 CPU 自身的资源交点与 CPU/GPU 路径交点。详见[修订记录](revision-coherence/README.md)。

## 中文表达修订

正文、表格、图注和练习已按语境统一术语，并逐句调整主语、语序及修饰关系。两处小节标题与 outline 同步，插图文字同步重绘。[修订记录](revision-language/README.md)。

## 段落衔接与图示修订

新增七幅机制图，重写各节之间和数字段落之间的衔接。图前说明观察对象，图后解释因果关系；专家复用、最忙卡、流水执行、缓存路由、状态迁移与输出恢复均可沿图推导。[修订记录](revision-visual/README.md)。

## 与第八章的范围划分

第八章现名“推理优化”，本章现名“分布式推理”。本章以计算和状态的执行位置为主线，适用于单实例内的多卡协作，也适用于多个副本和阶段服务池。新图 9-1 说明硬件组织与服务组织；原有 16 图顺延一号。详细修改见 [两章范围修订](../../research/ch08-ch09-scope-revision/README.md)。正文文件路径保留，链接标题使用新章名。
