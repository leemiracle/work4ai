# 04 · 全链路 PerfAgent 设计（perfagent 包）

> **定位**：perfloop（03）是验证循环骨架的教具；**perfagent 是本单元的核心交付物**——一个可运行的 CPU/Linux 设备性能优化 Agent 全链路实现，GPU 线的扩展插槽已预留。
> **代码**：[perfagent/](./perfagent/)（9 模块 ~700 行，除 numpy 零依赖）
> **实测**：见 [05-campaign 实录](./05-perfagent跑通实录.md)（154 次评估，E1/E2/E3 三实验）

---

## 一、架构：六层全链路

```
                        ┌────────────────────────────────┐
   campaign.py 编排      │ profile → search → redteam → report │
                        └────────────────────────────────┘
  ┌──────────┐   ┌───────────┐   ┌────────────┐   ┌─────────┐   ┌─────────┐
  │ sensors  │→ │ diagnose  │→ │ proposers  │→ │  guard  │→ │ memory  │
  │ 感知层    │   │ 诊断层     │   │ 决策层(插槽) │   │ 裁判层   │   │ 记忆层   │
  │ 拓扑/IPC  │   │ 伸缩探针→  │   │ grid/full- │   │ 四级判定 │   │ win/trap │
  │ /proc遥测 │   │ 画像卡     │   │ grid/heur/ │   │ +反作弊  │   │ 跨session│
  │          │   │ (roofline │   │ llm/mock   │   │ +SUSPIC. │   │ warm-start│
  └──────────┘   │  -lite)   │   └────────────┘   └─────────┘   └─────────┘
                 └───────────┘          ↓                ↑
                          ┌──────────────────────┐      │
                          │ actions + runner     │──────┘
                          │ 执行层：typed 验证→   │  子进程隔离测量
                          │ env注入/taskset亲和/  │  (双nonce指纹+确定性
                          │ impl 插槽(作弊红队)   │   +逐rep扰动计时)
                          └──────────────────────┘
```

**一次 search 迭代的数据流**：画像卡+trap 库 → 提议器出候选 → `validate`（类型/范围/联合约束，不过线 REJECT）→ 子进程 apply+measure → `judge`（measure_error/invalid/keep/revert + SUSPICIOUS）→ `results.jsonl` 追加 → 下轮 warm-start 去重。

## 二、模块 ↔ 头部项目原则对照（每行都有出处）

| 模块 | 实现要点 | 原则出处 |
|---|---|---|
| `sensors.py` | 拓扑探测（物理核/SMT）、可选 perf stat IPC | LumOS 零改造部署（/proc//sys 即遥测）|
| `diagnose.py` | 线程伸缩探针→四分类画像卡（thread-adverse/compute/partial/flat） | KernelAgent roofline 分类的零成本等价物；SemaTune decision context |
| `proposers.py` | 四提议器同一接口：grid(对照)/fullgrid(2-knob)/heuristic(规则)/llm(真端点) | 易变插槽：换提议器不动 guard；AKO4X SKILL 可换 |
| `actions.py` | threads 统一写 4 个 env + taskset 亲和 + impl 插槽；baseline 剥离继承 env（对称语义） | SemaTune typed validation；LumOS 审批前的 schema 校验 |
| `runner.py` | 子进程隔离；**双 nonce 随机输入指纹**（正确性两组输入成立）+ **同输入确定性** + **逐 rep 内容扰动计时** | SOL-ExecBench 多轮随机输入/清 L2；Wafer determinism check；KernelBench 对抗单测 |
| `guard.py` | 纯函数四级判定；正确性前置于性能；>5× SUSPICIOUS（怀疑但不断罪） | KernelArc deterministic guard 四判定；KernelBench eval.py:691 |
| `memory.py` | results.jsonl win/trap 库 + cards.json 画像；跨 session 去重；trap 回灌 LLM 上下文 | KernelBlaster optimization_database.json；SemaTune 跨 run 记忆 |
| `campaign.py` | 三阶段编排 + `--fresh` A/B 隔离模式 + redteam 子命令 + 报告生成（红队行 DQ 出主榜） | AgentKernelArena 控制变量；KernelBench EVAL.md 反复核对立场 |

## 三、关键设计决策记录（为什么这样而不是那样）

1. **LLM 不拥有 keep 宣布权**：proposers 只产候选 dict，judge 是纯函数。LLM 提议一个"threads=100"会被 validate 秒杀，提议作弊 impl 会被指纹抓住——权力分离是全链路的第一原则。
2. **提议器永不炸主循环**：LLM 端点超时/解析失败 → 重试 1 次 → 空列表降级（[05 实录]有真实崩溃案例：第一次 llm search 在 2048 负载 60s 超时直接炸掉 campaign，patch 后降级路径已验证）。
3. **baseline 剥离继承 env**：child_env 先 pop 全部线程变量——baseline=真默认、candidate=显式设置，杜绝"父进程环境污染造成隐性配置"。
4. **去重的双模式**：默认全局去重（真实 agent 语义：不浪费预算重测）；`--fresh` 隔离（实验语义：proposer 间公平 A/B）。第一次 E2 就踩到这个坑：heuristic 的候选全被 grid 的历史吃掉，0 评估。
5. **impl 插槽是 GPU 线的接口预留**：`impl="ref"|"cheat_cache"` 今天承载红队作弊；明天接 GPU 时，`impl="cuda_kernel"` 就是 KernelBench 式"提交自定义实现"的动作位——runner 换裁判，六层骨架不变。
6. **报告的 DQ 语义**：红队行（impl≠ref）从"每负载最优"榜剔除但保留在效率表——作弊不许上榜但必须留痕（SOL-ExecBench DQ-但可见哲学）。

## 四、诚实边界（这套设计不能做什么）

- 诊断是**经验探针**不是解析 roofline（没有 SOLAR）；画像卡够提议器用，不够写论文
- 只覆盖"配置空间"优化（threads/affinity/env），不改负载代码本身；代码变体仅红队 impl 示范
- guard 的 5% keep 边界挡不住**测量系统本身的漂移**（[05] matmul-512 同配置跨 run 差 3×——重复测量协议是评估层职责，不是 guard 职责）
- 逐 rep 扰动防内容键缓存，防不了 pointer 键作弊（军备竞赛下一手：逐 rep 换输入对象指针，对应 SOL-ExecBench 的指针漂移）
- 单机单用户假设；无并发负载隔离（02 卡第 3 问的硬件锁定只在协议层尽量做到）

## 五、GPU 线扩展路径（不改骨架的升级位）

| 层 | CPU 现状 | GPU 升级 | 参考实现 |
|---|---|---|---|
| 感官 | perf stat/探针 | NCU 28 指标 + SOL 百分比 | KernelAgent KernelProfiler |
| 诊断 | 伸缩四分类 | roofline 分类 + 瓶颈归因 LLM 诊断 | KernelAgent BottleneckAnalyzer |
| 动作 | env/taskset | Triton/CUDA 源码生成 + 编译 | KernelAgent / AKO4X |
| 裁判 | 指纹+确定性+速度 | + L2 清空、锁频、流检查、静态审查 | SOL-ExecBench harness |
| 搜索 | 线性+去重 | MCTS/plateau 换向/多策略 portfolio | Kernel Forge / KernelArc |

---

生成：2026-08-24 · 上级 [README](./README.md) · 实测 [05](./05-perfagent跑通实录.md) · 代码 [perfagent/](./perfagent/)
