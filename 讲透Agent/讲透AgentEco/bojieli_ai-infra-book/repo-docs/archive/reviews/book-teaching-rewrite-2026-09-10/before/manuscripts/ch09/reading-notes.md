# 第九章写作前阅读与取舍

2026-09-10。本章依据当前七节 outline、配套扩写、已完成计算结果及既有 survey 的相关专题撰写。正文为原创教材式讲解：先建立服务模型，给定量例题，再改变条件并检验结论。未开展新 GPU 测量，未将公开记录或教学能力当作本书实测。

## 已读材料及采用位置

| 材料 | 本次阅读范围 | 正文使用 |
| --- | --- | --- |
| research/2026-infra-survey/README.md | 当前工作决定、范围与收敛原则 | 不新增广泛调研，优先闭合已有案例 |
| research/2026-infra-survey/parallel-moe-ownership/NOTES.md | 模型、逐卡所有权、通信、服务实例定义及限制 | 9.1、9.4，EP组不等于独立请求副本；dispatch由token所有权决定 |
| calculations/PLAN.md | C47–C52与相关缺口 | 区分已完成子账与完整系统尚未验证项 |
| calculations/results/pd-pool-*.json、pd-pool-book.md | 基线、同构、网络、前缀、长输出场景及条件 | 9.2与9.7；图中直接读取冻结结果 |
| calculations/results/pd-af-handoff-qwen8.md/.json | 状态字节、消息、缓冲、串行假设 | 9.2与9.3；一次PD不能直接与一步AF排名 |
| calculations/results/expert-locality-{single,prefill,boundary78,boundary79}.json | 场景、资源时间与逐专家复用边界 | 9.3；采用2 TFLOP/s、200 GB/s等明确题设，区分早期案例笔记的100 GiB/s |
| calculations/results/replica-payback-book.json/.md | 逐rank额外容量、复制、每批收益和严格回本 | 9.4；复制与KV竞争容量 |
| calculations/results/cache-route-{book,fast-remote,stale}.json/.md | 路径依赖、均值和p99、链路需求 | 9.5；高命中率与更短完成时间分开 |
| calculations/results/cache-restart-book.json | 页、读取、有效复用及输出核验 | 9.5；144 MiB读取与141.75 MiB有效复用 |
| calculations/results/router-pressure-book.json | 配对目标延迟与完整任务完成 | 9.5；两种目标可能相反 |
| calculations/results/reconfiguration-declared-serial.json | 网络下界、声明切换、未知实测字段 | 9.6；服务切换时间不以传输下界代替 |
| case-studies/weight-offload-execution.md | 执行路径、专家复用、公开成绩边界 | 9.3；主存驻留不等于CPU执行 |
| references/framework-history/2026-09-08/offload-execution/README.md | 版本证据与所读源码范围 | KTransformers、SGLang的submit/compute/sync路径 |
| case-studies/moe-and-startup.md | MoE Serving Tax、CRAFT、Breaking the Ice的已读研究与限制 | 9.4、9.6；不转用历史性能倍数 |
| case-studies/cache-tiers-and-routing.md、cache-events-and-routing.md | 全文 | 9.5；共享范围、事件、可用前缀和预测位置 |
| experiments/ch09/09-03/README.md、09-05/README.md | 公开证据表、硬件与质量边界 | 9.3；公开配置提供容量入口，不用于同平台排名 |
| experiments/ch09/09-07/shared-kv/README.md | 配置、受控命中、原生复制证据与边界 | 9.5；同GPU双引擎CPU池，不作跨机测量 |
| experiments/ch09/09-10/branch-observation/README.md | 同请求事件链、限额与有效命中 | 9.6；文件读取与有效复用之间的缺口 |

完整第九章扩写资料保留更多来源与变体。本次不把未读原论文全文计为新阅读，使用 survey 已明确核读范围的研究结论，并给出可追溯入口。来源SHA256在sources.json封存。

## 图片安排

九幅图对应既有九个配图主题。流程图自绘，数值图读取已完成calculations结果或按公开的条件公式生成；不预画尚未测得的GPU性能趋势。图内无图号、无caption，编号仅在正文图注中出现。图5使用明确的单层八热点专家教学输入，不能当作KTransformers整机性能曲线；图9采用假设的启动与服务率展示积压守恒，不当作9-10实测曲线。

## 数字论证修订补记

本轮沿上述同一组来源改写论证，新增64-token／512分派的128专家均匀与集中对照、八卡最忙设备计算、命中后整数配比推导、等待预算推导远端等时带宽，以及声明带宽／串行准备／费用的敏感性例子。新增条件均在正文显式给出，原始数据不覆盖。图片按一个关系重组；最新图号与用途以本目录README为准。精确形状和整数交点保留，性能值按足以支持比较的有效数字显示，哈希与版本记录留在配套。


## 连贯性修订时的回读

再次阅读 pd-pool-book 的有效能力、25 个整数分配与输入约定，以及 cache-tiers-and-routing 的状态身份、串行取回路径和有效复用说明。沿用此前已读的专家局部性、replica-payback、缓存失效、启动分支与迁移资料；本轮新增推导的独立算术检查写入 verify.py。章末容量、公共通道和恢复期限作为显式教学输入，不归属现有硬件实验。
