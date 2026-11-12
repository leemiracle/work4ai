# 第七章写作来源与采用范围

本章先阅读既有 calculations、survey 的相关条目与案例，再组织正文。作者文章《Unified Bus 背后的思考》（用户所称“背后的故事”）在提纲重组时已阅读；正文沿设计问题、备选方案与责任划分展开，不将早期经历当成现行产品保证。本轮没有重新通读所有被引论文 PDF，也没有新增 GPU 性能测量。

| 来源 | 采用内容 | 边界 |
|---|---|---|
| [UB 作者文章](../../references/files/documents/ub-reflection.html)、[规范核对笔记](../../references/UB-ASCEND-NOTES.md) | 总线与网络统一、KV-Direct、1Pipe、Jetty／传输分离、引用寿命 | 经历用于解释动机；规范模式、物理实现和产品版本分别处理 |
| [路径与诊断](../../case-studies/collective-paths-and-diagnosis.md) | MegaScale 就绪等待、可路由 PCIe 的服务限制 | 保留论文平台与证据范围 |
| [远端排序与完成](../../case-studies/remote-ordering-and-completion.md) | 必要依赖、目标端检查、旧值与完成消费 | 新硬件提案不写成现有网卡已支持 |
| [网络规划与集合通信](../../case-studies/network-planning-and-collectives.md) | CASSINI 周期与相位、消息大小和启动成本 | 周期、放置与校准条件不可省略 |
| [资源共享与放置](../../case-studies/resource-sharing-and-placement.md) | FuseLink 多 NIC 与共享出口 | 教学路径算式不当成论文测量 |
| [NSDI 2024 survey](../../research/2026-infra-survey/reading-nsdi-2024.md)、[OSDI 2025 survey](../../research/2026-infra-survey/reading-osdi-2025.md)、[ASPLOS 2026 survey](../../research/2026-infra-survey/reading-asplos-2026.md) | 本章相关论文的阅读范围、设计问题和适用条件 | 阅读相关条目及已有案例，不声称本轮重读全部会议论文 |

## calculations 与图片

直接核对 `calculations/results/` 的相应 Markdown 说明、JSON 摘要、输入与事件记录：

- `gradient-fp32-*-nic2`：相同逻辑求和下的跨边界字节绘入图 7-3；逐轮资源下界用于正文比较。
- `remote-window-*`、`remote-state-reused`、`rpc-trace-1048576`：在途窗口、服务间隔、不变快照复用与 RPC 阶段。
- `connection-states-*`：保留端点和关系绑定后再比较共享，绘入图 7-5。
- `operation-ordering-*`、`completion-reclaim-*`：依赖、附加恢复、可见性和回收，图 7-6 使用保存的任务时间线。
- `periodic-queue-*`、`feedback-queue-overflow`、`packet-reorder-*`：图 7-7 仅绘周期队列分段；反馈和收包事件用于正文算例。
- `collective-tail-*`：就绪与尾部的教学条件。图 7-9 仅绘就绪与交换的教学时间线；Gloo 结果和消息大小比较留在正文。

完整路径和 SHA256 见 [sources.json](sources.json)；实际绘图数据见 [figure-data.json](figure-data.json)。锁定来源表示追踪构建输入和引用，并不表示每个被链接文档都在本轮全文重读。

## 既有实验与提纲更新

直接阅读实验 [7-3](../../experiments/ch07/07-03/README.md)、[7-4](../../experiments/ch07/07-04/README.md)、[7-8](../../experiments/ch07/07-08/README.md) 和 [7-10 的 rank-readiness](../../experiments/ch07/07-10/rank-readiness/README.md)，分别保留公开 NCCL 记录、264 次 RPC、CPU DDP 错峰及本机 Gloo 的实验边界。

收尾时发现提纲新增了实验结果摘要，已补读 7-1、7-2、7-5、7-6、7-7、7-9、7-10 的 README。六节、23 个小节的结构未变。正文保留可以独立解释的原始算式与条件，没有直接采用新增摘要中的一般化判断：

- 容量不足不能单独排除“服务器内 TP／EP 加服务器间 PP”；通信项占期限的一定比例，也不足以证明完整推理可行或不可行。
- 有限教学配置不能推出 TP／EP 必须留在超节点内部。10.17、10.51、10.68 ms 也不能表述为规模增加后“不倒退”。
- 40 GB/s、2 μs、256 B 得到 312.5 个在途请求，整数需求为 **313**。批量暂存时间不变是该扫描固定搬运参数的结果，不是实际传输对延迟不敏感的定律。
- 7-6 新扫描使用四类隔离，正文使用已保存计算中的八类隔离，两者不可混写。
- 7-7 的 102 μs 发布链与 6 μs 旧值反例来自不同输入，不能直接作性能对比。
- 7-10 的消息减半、80% 重叠、故障倍数属于反事实输入；不能据此声称实际分层算法实现该收益，或普遍判定避免退化比优化更有价值。正文用关键路径公式给出有条件的收益判断。

这些区别记录在此，供后续修订实验解说使用；本轮交付以正文和配图为范围。

## 论证与插图修订

按同一组条件—推导—比较—下一问题改写全章算例。配置、维度与整数边界保持精确，性能展示按判断需要舍入，源数据精度不变。图 7-2、7-3、7-6、7-7、7-9 重新构图，每张图聚焦一个关系；图数据中的 `plotted` 字段区分实际绘图项和正文计算依据。修订前快照与说明见 `research/ch07-prose-revision-2026-09-10/`。

## 教材体例重写（当前版本）

当前稿以两台服务器的 192 MiB 梯度归约为主线，建立流量与资源、并发与吞吐、依赖与关键路径三个模型，并在章末同一个训练步中合并使用。笔者设计经历采用第一人称。章节组织变化和六道完整例题见[结构说明](../../research/ch07-textbook-revision-2026-09-10/README.md)。

图 7-2 已改用主线的每方向 336 MiB、40 GB/s 出口、20 ms 计算；图 7-3 补充参与者连接与分片交换，图 7-6 补充必要依赖和额外串行边。新增推导保存在 [teaching-data.json](teaching-data.json)，由 [models.py](models.py) 生成。约 80 GB/s 分层选择边界、2／18 次复用、三个隔离类、17.5 μs 重叠预算及整步比较均属于显式教学模型，既有测量数据没有改写。

## 中文表达修订

逐段调整主谓搭配、语序、指代和段间衔接，统一正文与图中的术语。数学推导和原始数据保持不变；改写时省去一次重复变量引用，当前渲染 98 个数学表达式。修改记录及验证结果见[语言修订说明](../../research/ch07-language-revision-2026-09-10/README.md)。

## 图文衔接修订（当前图号）

新增流水线、专家接收路径、多网卡中继、快照复用、在途请求、缓冲区寿命、旧值读取、请求回收、反馈队列、多路径接收、整步执行与消息大小等 12 幅图。当前共 21 幅图，旧修订记录中的九图编号属于当时版本；当前对应关系见配图 README。回收、反馈和收包图直接使用既有 calculations 事件，其他图采用正文已给定的教学条件。

本轮复核了既有阅读笔记、相关计算与事件记录，没有新增性能测量。正文补充从图中观察到数值推导的解释，尤其区分了链路空闲与槽位占用、报文到达与按序交付、通信结束与训练步结束。
