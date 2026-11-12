# 第十章写作阅读记录

2026-09-10。先核对本轮六节 outline、扩写资料、已有 calculations 与 survey，再撰写正文和生成插图。没有重新运行 GPU 训练，也没有把摘要筛选登记为完整论文阅读。

## 已读材料与采用方式

| 材料 | 阅读范围 | 正文用途与边界 |
|---|---|---|
| calculations：training-state、training-deadline | JSON 的输入、summary、逐阶段状态与逐设备结果；巨大逐张量表未逐行人工复读 | 16-byte Adam、ZeRO 各阶段、矩阵口径任务下界 |
| calculations：gradient-cast | 两路径操作、缓冲、summary 与快链路结果 | 推导转换位置交点；只计梯度就绪到 CPU 可消费 |
| calculations：training-pipeline-gpipe/1f1b-m8 | scenario、summary、事件 schema；脚本读取完整事件集合画图 | 337／347 ms 与激活预留反例；128-token 微批、声明服务时间 |
| calculations：checkpoint-async、checkpoint-interval | 捕获与完成行、载荷、故障率、最优周期 | 持久化新鲜度、一阶周期；不当作远端存储实测 |
| calculations：weight-handoff、routing-metadata、dense-training-scale | 状态峰值、ID 载荷、逐设备／规模结果 | 交接次序、6／12 MiB、Dense 期限曲线 |
| survey QA：training-state-scope-review | 全文 | 梯度与主权重格式、转换峰值和检查点口径分离 |
| survey QA：verl-recipe-loss-closure | 全文 | 4 prompt × 2 回答、20-token 分母、一次裁剪／更新；no_sync=False、NO_SHARD |
| survey QA：rl-recipe-editorial-reading | 正文入口与 loss 补读记录 | 固定配方承担流程验证，较大模型承担规模推算 |
| survey：NSDI 2024 MegaScale 条目与阅读范围 | 对应条目及选读范围 | 固定 batch 扩展；不归因于单个通信技巧 |
| survey：NSDI 2025 ByteCheckpoint 条目与阅读范围 | 对应条目及选读范围 | 布局、数据状态、异步提交，GPU states 与 full states 分开 |
| survey：ASPLOS 2026 SuperOffload 专节 | 专节全文 | 转换吞吐、链路与暂存的联合取舍；历史配置差异 |
| survey：OSDI 2026 Weave／RobustRL、MLSys 2026 MPG | 对应条目和实际阅读范围 | 资源池与角色恢复交给下一章；进展指标保持一致分母 |
| case-studies：training-offload-and-casting、checkpoint-layout-and-loading、rl-state-and-reproducibility | 全文 | 机制推导、独立算例、定义与版本边界 |
| case-studies：kernel-and-fleet-efficiency | MPG 设备时间例与定义 | 97.22% 分配率与 33.33% 计算基准产出 |
| case-studies：training-compute | 长度分布及硬件计量段 | 因果注意力有效配对数，不将注意力增长率当整步增长率 |
| experiments/ch10/10-08 | README 全文 | 小模型真实阶段、梯度与接收权重、质量负结果；共享设备下两步不拟合趋势 |
| experiments/ch10/10-09/source-readiness | 版本、history、四对配置与指标边界 | 作者已有日志，未在本机独立重训；不声称普遍质量收益 |
| experiments/ch10/10-07 | 保存与提交前故障记录 | API 返回与可用恢复点分离；人为屏障不当作慢磁盘 |

来源锁见 [sources.json](sources.json)，图中实际数据见 [figure-data.json](figure-data.json)。正文脚注链接到完整计算、案例和原实验。survey 中旧章号和题号保持历史含义，正文使用重组后的第十章编号。

## 写作与制图约定

每节从一个系统问题开始，定义对象、假设和工作单位，再给定量例题及取舍。教学预测、已有实测与论文结果分别说明；不模仿现成教材的原句或挪用其图表。所有插图为本章自行绘制，使用已有结果与显式公式；编号和完整标题只出现在图片外部 caption。

本章图 10-8 采用通用硬件敏感性模型，原因是既有资料没有同条件 A100／A800／H20 全参训练日志。未以假想柱状成绩填补缺项。图 10-4 使用配套生成的真实事件表，不手画预期加速趋势。图 10-5 只比较 112 GB 教学快照在两种写带宽下的可用恢复点；保存周期的比较留在正文表格，按每参数 14 bytes 计算。


## 定量叙述修订

补读 pipeline-gemm-recompute-products 与 pipeline-gemm-save-1f1b 的配置、逐阶段保存量和汇总，区分每阶段保存量与全模型新增运算量。重计算例注明 128-token 微批和 FP32 激活。

正文用同一组条件推进容量、时间与恢复收益的比较。新增的通信分桶（72 MiB、16 GiB/s、0.1 ms 启动）、输入 worker、共享 I/O、RL 阶段速率和教师输出头算例均为显式假设下的推导，不登记为新测量。性能与容量按论证需要取有效数字，维度、设备数和整数边界保持精确。版本、实现边界和来源保留于脚注及原始配套。

九幅图按各自解释的关系收拢：持久状态倍率、容量与计算设备下界、分片数与容量、流水时间与保存量、带宽与恢复点、交接顺序与峰值、路由选择与当前重算、通信敏感性、规模与期限。图内不含图号，完整条件置于外部图注。


## 教学结构重写（2026-09-10）

全章围绕对象寿命、关键路径与保留进展组织。贯穿任务固定 100B token、384 条 8192-token 序列全局 batch，比较 32／48 卡；给定容量、局部效率、通信和输入预算，按已有工作量和检查点公式推导完成时间与阈值。全部假设和复算放入 design-case.py／json／md，不作为 GPU 测量。

重读 training-state-scope-review；核对 pipeline-gemm 两种保存策略的对象形状和 reservation，以及 GPipe／1F1B 的原始事件：阶段 3 的 B:3:1 在 93 ms 完成，F:3:2 在 95 ms 开始。重计算由每层 6+2+2 MiB 乘积推导九层节省；图 10-4 标注实际等待。图 10-9 从原规模时间数据换算为固定 90 天的设备边界。

八条不等长回答的归一化前移至微批节；RL 保留供给、权重交接、策略身份与路由重放，原流程细节收为案例框。教师缓存、MPG 和部分系统名称从主文移出，资料仍可由上述阅读表访问。十题收至章末，分基础、分析和综合设计，另加四项误区讨论。删除正文反复的段末自我辩护，将推导条件在设题时给出。

## 术语与中文句式修订

按具体含义区分训练迭代、参数更新和权重同步，解释页锁定内存，改写通信等待、样本标识及过期样本筛选等表述。对六节正文、案例、图注和章末习题逐段调整语序与动宾搭配；图中文字和设计题说明同步修改。原始计算来源和公式语义保持不变。


## 图示与段落衔接修订

新增十一幅机制图：参数分片与临时全收集、乘积重计算的保存时间、CPU/GPU 梯度转换路径、链路排队与通信等待、因果注意力面积、预取进度、检查点重分片、保存周期曲线、RL 阶段瓶颈、异步执行时间轴和完成时间分解。数值来自现有章节计算和显式教学例；未引入新的测量结果。shape、字节、时刻、配对数与曲线最低点均纳入 verify.py 检查。

段落以问题之间的因果关系衔接：容量到速度、参数副本到激活保存、计算等待到链路等待、预取进度到可恢复状态、快照提交到保存周期、独立阶段到异步版本差异。图前交代问题，图后解释读图结果，再进入数值计算。对数据密集的长段，在机制与算例、原因与后果之间分段。

图号按正文顺序统一为 10-1 至 10-20；本文件此前修订记录中的旧图号保留历史含义，对应关系见 figure-number-map.json。当前 figure-data.json 的数字键与正文图号一致。原始数据的命名与实验编号保持不变。
