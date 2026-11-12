# 第2章正文与配图

[Markdown 正文](../02-模型架构.md) · [HTML 阅读版](../02-模型架构.md)

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

## 当前阅读版配图（2026-09-10）

正文现引用 33 幅图，以下清单按当前阅读顺序列出；上文旧图号用于追溯构建记录。

| 图号 | 内容 | SVG | PNG | PDF |
| --- | --- | --- | --- | --- |
| 2-1 | 循环神经网络的依赖。相同颜色的圆点表示各位置的计算，箭头指向需要前一结果的节点；同层位置沿横向逐次推进。 | [SVG](figure-2-1-dependencies.svg) | [PNG](figure-2-1-dependencies.png) | [PDF](figure-2-1-dependencies.pdf) |
| 2-2 | 因果 Transformer 的层间依赖。各查询读取上一层中允许访问的位置；上一层完成后，同一层的已知输入位置可以并行计算。 | [SVG](figure-2-causal-dependencies.svg) | [PNG](figure-2-causal-dependencies.png) | [PDF](figure-2-causal-dependencies.pdf) |
| 2-3 | 同一位置的输入经不同投影产生查询、键和值。注意力先用查询与键计算位置间关系，再用这些关系汇总值。 | [SVG](figure-2-qkv-objects.svg) | [PNG](figure-2-qkv-objects.png) | [PDF](figure-2-qkv-objects.pdf) |
| 2-4 | 两段上下文形成长方形加三角形。蓝色为三个新位置分别读取两个旧位置，绿色为新输入内部的因果访问，空白为被屏蔽的未来位置。 | [SVG](figure-2-causal-pairs.svg) | [PNG](figure-2-causal-pairs.png) | [PDF](figure-2-causal-pairs.pdf) |
| 2-5 | SwiGLU 的两条升维分支。gate 经 SiLU 后调节 up 的对应元素，乘积再由 down 投影降回主干维度。 | [SVG](figure-2-ffn-gates.svg) | [PNG](figure-2-ffn-gates.png) | [PDF](figure-2-ffn-gates.pdf) |
| 2-6 | Qwen3-8B 一层的骨架。先完成注意力子层，再完成前馈子层；左侧旁路保留子层输入，与变换结果相加，这种连接称为残差连接。 | [SVG](figure-2-2-layer.svg) | [PNG](figure-2-2-layer.png) | [PDF](figure-2-2-layer.pdf) |
| 2-7 | 四步生成的上下文读写。每一步读取蓝色的已有位置，再追加一个橙色新位置；本图初始上下文为四，四步后保留八个位置。 | [SVG](figure-2-history.svg) | [PNG](figure-2-history.png) | [PDF](figure-2-history.pdf) |
| 2-8 | 同一批次的主要投影权重可共享读取，各请求则各有一份上下文。图中固定每请求 8K 上下文，分别累计共享权重与独立 KV 的逻辑读取量。 | [SVG](figure-2-history-batch.svg) | [PNG](figure-2-history-batch.png) | [PDF](figure-2-history-batch.pdf) |
| 2-9 | 固定四个查询头，分别为每头、每组和全部查询保存 KV。连线表示使用关系；共享上下文后，各查询仍分别产生自己的评分与输出。 | [SVG](figure-2-3-sharing.svg) | [PNG](figure-2-3-sharing.png) | [PDF](figure-2-3-sharing.pdf) |
| 2-10 | 固定 Qwen 层数、头宽、8192 个上下文位置与 BF16，只改变 KV 组数。实际模型采用 GQA；其余两柱是用于分析共享比例的结构变体。 | [SVG](figure-2-4-cache.svg) | [PNG](figure-2-4-cache.png) | [PDF](figure-2-4-cache.pdf) |
| 2-11 | 两种计算路径改变上投影的位置。展开路径先恢复上下文键，紧凑路径先变换当前查询，再直接读取潜变量；结合律保证对应点积可以按这两种次序计算。 | [SVG](figure-2-mla-paths.svg) | [PNG](figure-2-mla-paths.png) | [PDF](figure-2-mla-paths.pdf) |
| 2-12 | Kimi K3 的 24 层 MLA 在相同 8K 上下文、BF16 下的两种保存量。紧凑路径保存上投影前的表示，展开路径保存各头的键和值。 | [SVG](figure-2-mla-capacity.svg) | [PNG](figure-2-mla-capacity.png) | [PDF](figure-2-mla-capacity.pdf) |
| 2-13 | 上下文压缩与索引选择的先后关系。上方用八个位置、每四个合成一条演示压缩，下方展示一次查询先扫描索引再读取主状态的过程。 | [SVG](figure-2-5-sparse.svg) | [PNG](figure-2-5-sparse.png) | [PDF](figure-2-5-sparse.pdf) |
| 2-14 | DeepSeek V4-Flash 在 8K 上下文下的四项状态。窗口、压缩上下文和索引是已保留的上下文；压缩缓冲保存尚在汇总或更新中的数据，单独计入容量。 | [SVG](figure-2-sparse-capacity.svg) | [PNG](figure-2-sparse-capacity.png) | [PDF](figure-2-sparse-capacity.pdf) |
| 2-15 | 压缩比为四时的一次块完成过程。前几次输入更新同一块内缓冲，第四个位置到来后形成可供后续查询使用的压缩条目。 | [SVG](figure-2-compression-steps.svg) | [PNG](figure-2-compression-steps.png) | [PDF](figure-2-compression-steps.pdf) |
| 2-16 | 固定矩阵的递推更新。新键和值的外积加入旧状态，矩阵形状保持不变；查询使用更新后的状态计算输出。本图采用简单累加递推。 | [SVG](figure-2-recurrence.svg) | [PNG](figure-2-recurrence.png) | [PDF](figure-2-recurrence.pdf) |
| 2-17 | Qwen3.6 的两类层。配置决定每层采用线性或完整注意力，随后都执行路由专家和共享专家；上方两个分支分别表示线性注意力和完整注意力，模型分别有 30 层与 10 层。 | [SVG](figure-2-6-hybrid.svg) | [PNG](figure-2-6-hybrid.png) | [PDF](figure-2-6-hybrid.pdf) |
| 2-18 | 上下文增长时的状态容量。横纵轴均为对数刻度；Qwen 逐位置追加 KV，Kimi K3 紧凑表示包含固定递推状态和增长的 MLA 上下文，DeepSeek V4-Flash 按压缩块增加条目。 | [SVG](figure-2-7-state-growth.svg) | [PNG](figure-2-7-state-growth.png) | [PDF](figure-2-7-state-growth.pdf) |
| 2-19 | 同一组模型每步计入的状态访问。逐位置上下文计读取，递推矩阵计一读一写；这些是指定路径的逻辑数据量，用于比较容量与访问的不同增长方式。 | [SVG](figure-2-state-access.svg) | [PNG](figure-2-state-access.png) | [PDF](figure-2-state-access.pdf) |
| 2-20 | 64 个 token 各选八个专家，总计 512 次分派。分散时可覆盖 256 个专家，集中时只访问八个；每专家处理的行数随之改变。 | [SVG](figure-2-expert-reuse.svg) | [PNG](figure-2-expert-reuse.png) | [PDF](figure-2-expert-reuse.pdf) |
| 2-21 | 普通残差与四路 mHC 的连接范围。普通残差保留一条子层输入旁路；mHC 汇合多路状态供子层计算，再混合输出。两种图中的子层输入均为 4096 维。 | [SVG](figure-2-8-residual.svg) | [PNG](figure-2-8-residual.png) | [PDF](figure-2-8-residual.pdf) |
| 2-22 | 四模型的主干层数，使用同一线性尺度。层数决定同类工作沿网络深度重复多少次。 | [SVG](figure-2-architecture.svg) | [PNG](figure-2-architecture.png) | [PDF](figure-2-architecture.pdf) |
| 2-23 | 同一线性尺度下的主干隐藏维度。每个位置的特征宽度决定投影的输入或输出尺寸。 | [SVG](figure-2-architecture-width.svg) | [PNG](figure-2-architecture-width.png) | [PDF](figure-2-architecture-width.pdf) |
| 2-24 | 每个 MoE 层保存的路由专家数量。Qwen3-8B 使用稠密前馈层，其路由专家数为零；每个 token 实际选中数见表 2-A。 | [SVG](figure-2-architecture-experts.svg) | [PNG](figure-2-architecture-experts.png) | [PDF](figure-2-architecture-experts.pdf) |
| 2-25 | 四模型完整权重统一用 BF16 表示时的容量，使用同一线性尺度。这里累计全部参数，包括每次仅选中部分的路由专家。 | [SVG](figure-2-resources.svg) | [PNG](figure-2-resources.png) | [PDF](figure-2-resources.pdf) |
| 2-26 | 相同单请求、已有 8K 上下文时的单步矩阵运算量。按各模型在表 2-C 说明的执行路径累计，Kimi K3 采用紧凑 MLA。 | [SVG](figure-2-resources-compute.svg) | [PNG](figure-2-resources-compute.png) | [PDF](figure-2-resources-compute.pdf) |
| 2-27 | 相同 8K 上下文下的每请求状态。上下文表示采用 BF16，递推矩阵和压缩缓冲采用相应实现的精度；各项合计对应表 2-C。 | [SVG](figure-2-resources-state.svg) | [PNG](figure-2-resources-state.png) | [PDF](figure-2-resources-state.pdf) |
| 2-28 | 已有 8K／200K 上下文后再处理一个 token 的矩阵运算量。蓝、橙分别对应两种上下文长度，横轴为对数刻度，柱端标出 GFLOPs。沿用表 2-C 的 decode 路径，Kimi K3 的 KDA 使用递推、MLA 使用紧凑表示。星号表示 Qwen3-8B 的 200K 条件超过本章固定配置的未缩放上下文上限，仅按原结构外推。 | [SVG](figure-2-long-context-compute.svg) | [PNG](figure-2-long-context-compute.png) | [PDF](figure-2-long-context-compute.pdf) |
| 2-29 | 权重、固定预留和一条请求 KV 的逐项容量。短竖线标出各设备容量；KV 采用 BF16、上下文长度 8192，固定预留为 2 GiB。 | [SVG](figure-2-9-capacity.svg) | [PNG](figure-2-9-capacity.png) | [PDF](figure-2-9-capacity.pdf) |
| 2-30 | 70B 的 4-bit 方案在同一张 80 GB 设备上，上下文长度从 8K 增至 32K 时允许保留的独立请求数。每请求状态增加，使剩余空间容纳的请求数减少。 | [SVG](figure-2-history-capacity.svg) | [PNG](figure-2-history-capacity.png) | [PDF](figure-2-history-capacity.pdf) |
| 2-31 | 从设备反推权重预算。24 GB 中先保留 4 条 8K 请求的 KV 和 2 GiB 工作区，余量给出 BF16 参数上界；图中容量均为十进制 GB。 | [SVG](figure-2-reverse-budget.svg) | [PNG](figure-2-reverse-budget.png) | [PDF](figure-2-reverse-budget.pdf) |
| 2-32 | 生成四个输出的调用顺序。prefill 处理 128 个输入并产生首输出，随后三次 decode 各将前一输出送回模型；最终保留 131 个位置。 | [SVG](figure-2-10-request.svg) | [PNG](figure-2-10-request.png) | [PDF](figure-2-10-request.pdf) |
| 2-33 | 同一 128 输入、四输出请求的矩阵运算量。模型执行范围与缓存路径见本节题设；这是逐调用累计的计算量。 | [SVG](figure-2-request-compute.svg) | [PNG](figure-2-request-compute.png) | [PDF](figure-2-request-compute.pdf) |


## V4／V4.1 会话修订后的当前图表

当前正文共 35 幅图；下表是当前图号，前文旧图号保留作历史记录。

| 图号 | 内容 | 文件 |
| --- | --- | --- |
| 2-1 | 循环神经网络的依赖。相同颜色的圆点表示各位置的计算，箭头指向需要前一结果的节点；同层位置沿横向逐次推进。 | [SVG](figure-2-1-dependencies.svg) |
| 2-2 | 因果 Transformer 的层间依赖。各查询读取上一层中允许访问的位置；上一层完成后，同一层的已知输入位置可以并行计算。 | [SVG](figure-2-causal-dependencies.svg) |
| 2-3 | 同一位置的输入经不同投影产生查询、键和值。注意力先用查询与键计算位置间关系，再用这些关系汇总值。 | [SVG](figure-2-qkv-objects.svg) |
| 2-4 | 两段上下文形成长方形加三角形。蓝色为三个新位置分别读取两个旧位置，绿色为新输入内部的因果访问，空白为被屏蔽的未来位置。 | [SVG](figure-2-causal-pairs.svg) |
| 2-5 | SwiGLU 的两条升维分支。gate 经 SiLU 后调节 up 的对应元素，乘积再由 down 投影降回主干维度。 | [SVG](figure-2-ffn-gates.svg) |
| 2-6 | Qwen3-8B 一层的骨架。先完成注意力子层，再完成前馈子层；左侧旁路保留子层输入，与变换结果相加，这种连接称为残差连接。 | [SVG](figure-2-2-layer.svg) |
| 2-7 | 四步生成的上下文读写。每一步读取蓝色的已有位置，再追加一个橙色新位置；本图初始上下文为四，四步后保留八个位置。 | [SVG](figure-2-history.svg) |
| 2-8 | 同一批次的主要投影权重可共享读取，各请求则各有一份上下文。图中固定每请求 8K 上下文，分别累计共享权重与独立 KV 的逻辑读取量。 | [SVG](figure-2-history-batch.svg) |
| 2-9 | 固定四个查询头，分别为每头、每组和全部查询保存 KV。连线表示使用关系；共享上下文后，各查询仍分别产生自己的评分与输出。 | [SVG](figure-2-3-sharing.svg) |
| 2-10 | 固定 Qwen 层数、头宽、8192 个上下文位置与 BF16，只改变 KV 组数。实际模型采用 GQA；其余两柱是用于分析共享比例的结构变体。 | [SVG](figure-2-4-cache.svg) |
| 2-11 | 两种计算路径改变上投影的位置。展开路径先恢复上下文键，紧凑路径先变换当前查询，再直接读取潜变量；结合律保证对应点积可以按这两种次序计算。 | [SVG](figure-2-mla-paths.svg) |
| 2-12 | Kimi K3 的 24 层 MLA 在相同 8K 上下文、BF16 下的两种保存量。紧凑路径保存上投影前的表示，展开路径保存各头的键和值。 | [SVG](figure-2-mla-capacity.svg) |
| 2-13 | 上下文压缩与索引选择的先后关系。上方用八个位置、每四个合成一条演示压缩，下方展示一次查询先扫描索引再读取主状态的过程。 | [SVG](figure-2-5-sparse.svg) |
| 2-14 | DeepSeek V4-Flash 在 8K 上下文下的四项状态。窗口、压缩上下文和索引是已保留的上下文；压缩缓冲保存尚在汇总或更新中的数据，单独计入容量。 | [SVG](figure-2-sparse-capacity.svg) |
| 2-15 | 压缩比为四时的一次块完成过程。前几次输入更新同一块内缓冲，第四个位置到来后形成可供后续查询使用的压缩条目。 | [SVG](figure-2-compression-steps.svg) |
| 2-16 | 固定矩阵的递推更新。新键和值的外积加入旧状态，矩阵形状保持不变；查询使用更新后的状态计算输出。本图采用简单累加递推。 | [SVG](figure-2-recurrence.svg) |
| 2-17 | Qwen3.6 的两类层。配置决定每层采用线性或完整注意力，随后都执行路由专家和共享专家；上方两个分支分别表示线性注意力和完整注意力，模型分别有 30 层与 10 层。 | [SVG](figure-2-6-hybrid.svg) |
| 2-18 | 上下文增长时的状态容量。横纵轴均为对数刻度；Qwen 逐位置追加 KV，Kimi K3 紧凑表示包含固定递推状态和增长的 MLA 上下文，DeepSeek V4-Flash 按压缩块增加条目。 | [SVG](figure-2-7-state-growth.svg) |
| 2-19 | 同一组模型每步计入的状态访问。逐位置上下文计读取，递推矩阵计一读一写；这些是指定路径的逻辑数据量，用于比较容量与访问的不同增长方式。 | [SVG](figure-2-state-access.svg) |
| 2-20 | V4 与 V4.1 的全局 KV 保存方式。左侧以三个代表层示意逐层保存；右侧显示 V4.1 四个全局 KV 拥有层及共享关系。实线表示数据读取；各使用层仍有自己的 Q 与局部 SWA，图中省略其他计算。 | [SVG](figure-2-v41-sharing.svg) |
| 2-21 | V4.1 解码器的层级位置选择。首个 Full 层先扫描全局，构造最多 16,384 个候选；后续 Reindex 在候选内重新选 512 个，Reuse 使用已有选择。示意位置数量不按比例；各层独立 Q 与局部 SWA 未画出。 | [SVG](figure-2-v41-selection.svg) |
| 2-22 | 64 个 token 各选八个专家，总计 512 次分派。分散时可覆盖 256 个专家，集中时只访问八个；每专家处理的行数随之改变。 | [SVG](figure-2-expert-reuse.svg) |
| 2-23 | 普通残差与四路 mHC 的连接范围。普通残差保留一条子层输入旁路；mHC 汇合多路状态供子层计算，再混合输出。两种图中的子层输入均为 4096 维。 | [SVG](figure-2-8-residual.svg) |
| 2-24 | 四模型的主干层数，使用同一线性尺度。层数决定同类工作沿网络深度重复多少次。 | [SVG](figure-2-architecture.svg) |
| 2-25 | 同一线性尺度下的主干隐藏维度。每个位置的特征宽度决定投影的输入或输出尺寸。 | [SVG](figure-2-architecture-width.svg) |
| 2-26 | 每个 MoE 层保存的路由专家数量。Qwen3-8B 使用稠密前馈层，其路由专家数为零；每个 token 实际选中数见表 2-A。 | [SVG](figure-2-architecture-experts.svg) |
| 2-27 | 四模型完整权重统一用 BF16 表示时的容量，使用同一线性尺度。这里累计全部参数，包括每次仅选中部分的路由专家。 | [SVG](figure-2-resources.svg) |
| 2-28 | 相同单请求、已有 8K 上下文时的单步矩阵运算量。按各模型在表 2-C 说明的执行路径累计，Kimi K3 采用紧凑 MLA。 | [SVG](figure-2-resources-compute.svg) |
| 2-29 | 相同 8K 上下文下的每请求状态。上下文表示采用 BF16，递推矩阵和压缩缓冲采用相应实现的精度；各项合计对应表 2-C。 | [SVG](figure-2-resources-state.svg) |
| 2-30 | 已有 8K／200K 上下文后再处理一个 token 的矩阵运算量。蓝、橙分别对应两种上下文长度，横轴为对数刻度，柱端标出 GFLOPs。沿用表 2-C 的 decode 路径，Kimi K3 的 KDA 使用递推、MLA 使用紧凑表示。星号表示 Qwen3-8B 的 200K 条件超过本章固定配置的未缩放上下文上限，仅按原结构外推。 | [SVG](figure-2-long-context-compute.svg) |
| 2-31 | 权重、固定预留和一条请求 KV 的逐项容量。短竖线标出各设备容量；KV 采用 BF16、上下文长度 8192，固定预留为 2 GiB。 | [SVG](figure-2-9-capacity.svg) |
| 2-32 | 70B 的 4-bit 方案在同一张 80 GB 设备上，上下文长度从 8K 增至 32K 时允许保留的独立请求数。每请求状态增加，使剩余空间容纳的请求数减少。 | [SVG](figure-2-history-capacity.svg) |
| 2-33 | 从设备反推权重预算。24 GB 中先保留 4 条 8K 请求的 KV 和 2 GiB 工作区，余量给出 BF16 参数上界；图中容量均为十进制 GB。 | [SVG](figure-2-reverse-budget.svg) |
| 2-34 | 生成四个输出的调用顺序。prefill 处理 128 个输入并产生首输出，随后三次 decode 各将前一输出送回模型；最终保留 131 个位置。 | [SVG](figure-2-10-request.svg) |
| 2-35 | 同一 128 输入、四输出请求的矩阵运算量。模型执行范围与缓存路径见本节题设；这是逐调用累计的计算量。 | [SVG](figure-2-request-compute.svg) |
