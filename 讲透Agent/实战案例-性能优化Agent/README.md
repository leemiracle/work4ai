# 实战案例 · 性能优化 Agent（GPU / CPU / Linux）

> **目标场景**：设计一个用于 GPU、CPU 等设备性能优化的 Agent，底层 Linux。
> **为什么值得单开一个单元**：性能优化是**可验证性最强的 agent 场景**——编译通过？数值正确？跑分快慢？三重裁判全是机器可判、毫秒级反馈、零标注成本。它同时是 2025–2026 agent 领域爆发最快的方向之一（NVIDIA/AMD/Meta/字节/MIT-HAN 都已下场），有大量一手 harness 可以借用，而不是从零造。
> **定位**：这是 [实践阶梯](../实践阶梯/)（端侧记忆 Agent）的**领域特化姊妹篇**——同一套方法论（四问决策树/harness 五子系统/评估环/插槽化），换到"裁判最强、reward hacking 最凶"的领域重演一遍。
>
> 生成：2026-08-24 · 引用全部来自当日 websearch 一手结果（arXiv HTML / GitHub README / 官方 leaderboard），未凭记忆。

---

## 篇目表

| # | 标题 | 核心 | 状态 |
|---|------|------|------|
| 01 | [KernelBench 裁判解剖](./01-KernelBench裁判解剖.md) | 五重裁判流水线/对抗样本三连/静态检查器，全部 `文件:行号` 锚点；真跑命令存档 | ✅ 2026-08-24 |
| 02 | [A/B 实验方法论卡](./02-A:B实验方法论卡.md) | AgentKernelArena 控制变量法庭；7 问清单 | ✅ |
| 03 | [perfloop 跑通实录](./03-perfloop跑通实录.md) | CPU 调优裸 loop 第零号证据：16 次事务测量、5 条铁证（铁律#1 独立复现/非单调曲线/负载依赖） | ✅ |
| 04 | [全链路 PerfAgent 设计](./04-全链路PerfAgent设计.md) | **核心交付物**：六层全链路架构（感知→诊断→决策→执行→裁判→记忆）+ 模块↔头部项目原则对照 + GPU 扩展位 | ✅ |
| 05 | [perfagent 跑通实录](./05-perfagent跑通实录.md) | 154 次真评估验收：E1 红队/E2 提议器 A/B(真 glm-5.3)/E3 双 knob + 方差警告 | ✅ |
| 06 | [v2 战役与 GPU 线启动卡](./06-v2战役与GPU线启动卡.md) | re-baseline/容差分层/transformers 真负载(默认配置差 5.8×)/**E4 军备竞赛矩阵**(指针键 467× 绕过内容扰动,对象轮换双杀)/AKO4X 克隆+四步接入卡 | ✅ |
| 07 | [CPU 线收官实录](./07-CPU线收官实录.md) | 双测协议(keep 需两次独立命中)+Qwen 常驻 server(load 1.3s)/**铁律#1 三级实证收官**(qwen0.5B 默认 8 线程 vs 1 线程差 1.42-1.73×,LLM 前向 thread-adverse) | ✅ CPU 线收官 |
| 08 | [方法论反哺实录](./08-方法论反哺实录.md) | perfagent 测量纪律 → LLM 评估环：同轮基线/双测四分支 verdict/dummy 下界探针(naive 27% 成色=仅+12pp 弱证据) | ✅ |
| — | [perfagent/](./perfagent/) | v3 ~950 行可运行全链路（10 模块，含 resident.py 常驻 server；双测 keep 协议）；[experiments/perfagent/](./experiments/perfagent/) 全部产物 | ✅ 已跑通 |
| — | [experiments/perfloop/](./experiments/perfloop/) | 247 行教具：propose→validate→apply→measure→guard→keep/revert + win/trap 库 + LLM 插槽 | ✅ 已跑通 |

---

## 0. 三大问题速答表

| 问题（讲透Agent 三大遗留缺口） | 一句话答案 | 展开 |
|---|---|---|
| ① 没办法快速迭代上手 | 别从零造——**进别人的 arena 打擂台**：三级跳 T0→T2，CPU-first 起步 | §2 |
| ② 不知道怎么设计（取舍/抗变化/贴场景） | 取舍看**四问决策树+2026 实证**；抗变化切**易变插槽/不变资产**；贴场景按**CPU-OS/GPU-kernel/调度三层特化表** | §3 |
| ③ 不知道怎么衡量 | 三层指标（任务级/harness 级/组件级）+ **reward hacking 是本领域的第一衡量课题**（14.5% 作弊率实证） | §4 |

---

## 1. 2025–2026 全景地图（一手资源总表）

四条线，全部 2025-2026 活跃。★ = 建议优先看。

### A 线：GPU kernel 生成/优化 Agent

| 项目 | 是什么 | 关键实证 | 对你的用处 |
|---|---|---|---|
| ★ [AKO4X](https://github.com/TongmingLAIC/AKO4X) | Claude Code 驱动的闭环 campaign 多 agent kernel 优化框架 | B200 上 10 个 FlashInfer-Bench 算子族达专家级；MLSys-2026 contest kernels 最高 **30.7× vs FlashInfer 专家基线**；6 种 kernel 语言（Python/Triton/CUDA/C++/TileLang/CuTe DSL）SKILL 渐进加载；NCU + compute-sanitizer 包装；本地 GPU + Modal 云双后端 | **最佳"读源码学设计"对象**：benchmark 单接缝可换、三模式（单会话/闭环/harness 共进化）正是抗变化设计的活教材 |
| ★ [KernelAgent](https://github.com/meta-pytorch/KernelAgent)（meta-pytorch） | PyTorch→Triton kernel 合成+优化全管线 | NCU 28 项硬件指标 → roofline 分类（memory/compute-bound）→ LLM 瓶颈诊断 → 优化 → 数值验证 → CUDA event 计时，≥95% SOL 早停；divergence-based revert | **最佳"工具链教科书"**：性能优化 agent 的感官（NCU）与手术刀（roofline+revert）怎么接 |
| [KernelArc](https://arxiv.org/html/2608.17071)（arXiv:2608.17071） | 多 agent 策略特化 + 确定性 guard | SOL-ExecBench 排行第一（2026-08-20 快照）；2-agent 共享内存 = **2.04× 单 agent** geomean（但 4 agent 无进一步增益）；单 agent 按 playbook 8 小时打到 **766 TFLOPS**（超 cuBLAS 3.2%，77% 理论峰值） | **多 agent 取舍的一手 ablation 数据**；guard 四判定（REJECT/KEEP/ACCEPT/REVERT）设计范本 |
| [Kernel Forge](https://arxiv.org/html/2607.24762)（arXiv:2607.24762） | 端到端 harness：抓取真实模型算子→MCTS 搜索→guarded 替换 | 50 迭代/kernel，14 kernels 超 PyTorch eager（最高 2.83×）；产物**带守卫回退**（不快就 fallback 原路径） | guarded export 模式：优化产物必须可安全回退 |
| [CUDA-Agent](https://github.com/BytedTsinghua-SIA/CUDA-Agent)（字节×清华，2026-02） | Agentic RL 训出的 kernel 生成模型 | KernelBench SOTA，超 Claude Opus-4.6 / Gemini 3 Pro；开源训练数据+SKILL.md+`agent_workdir`（实现→编译→验证→profiling 标准工作区） | `agent_workdir` 就是**领域特化版 harness 四文件**，直接抄结构 |
| [KernelBlaster](https://github.com/NVlabs/KernelBlaster)（NVlabs） | MAIC-RL：记忆增强 in-context RL | KernelBench L1 1.43× / L2 2.50× / L3 1.50× geomean；持久知识库 `optimization_database.json`（瓶颈状态→有效优化映射，跨任务复用） | **知识库是"不变资产"的实证**：win/trap 记忆跨任务迁移 |
| [KDA](https://github.com/mit-han-lab/kernel-design-agents)（MIT-HAN） | kernel 设计 agents | MLSys-2026 contest 上被 AKO4X 对照测过 | 第二意见参考 |

### B 线：CPU / Linux OS 层调优 Agent（本机无 GPU 也能实战）

| 项目 | 是什么 | 关键实证 |
|---|---|---|
| ★ [SemaTune](https://arxiv.org/html/2605.15026v1)（arXiv:2605.15026） | 在线 Linux OS 调优（sysctl/scheduler/power/memory/I/O，最多 **41 个参数**） | 13 个真实工作负载上稳定期性能比最强非 LLM 基线（MLOS）**+153.3%**，全程 LLM 费用 **$0.20**；dual-loop：Instant（1-5s 快环）+ Reasoning（几十秒慢环）；typed validation 挡住"把活服务调进降级区"的灾难 |
| ★ [LumOS / Expert-in-Residence](https://daplab.cs.columbia.edu/projects/lumos/)（Columbia，NeurIPS'25 MLForSys） | 在线 CFS 调度器调谐 agent | p99 尾延迟比 Bayesian 优化 **-5.0%（单参）/-7.1%（双参）**，比人类内核专家 **-2.98%**；MCP 工具 schema + 事务式 apply-commit-revert + 审批门 + 审计日志；pairwise ranking 防单指标代理被 Goodhart |
| [SchedCP / sched-agent](https://arxiv.org/html/2509.01245v3)（arXiv:2509.01245） | MCP 控制面 + 四 agent（观察/规划/执行/学习）生成 **eBPF sched_ext 调度器** | kernel 编译 1.79×、schbench p99 2.11×；成本 $0.15/工作负载分析、$0.45/策略合成（比朴素 agentic 降 13×）；eBPF 验证器+静态分析+动态测试三层 Execution Verifier |

### C 线：设备调度 / 异构资源 Agent

| 项目 | 是什么 | 关键实证 |
|---|---|---|
| [Agentic CPU-GPU Scheduling](https://arxiv.org/html/2607.22242v1)（arXiv:2607.22242） | LLM agent + 运行时监视器做设备映射（gpu_now / gpu_queue / cpu offload） | 19 个 AI 工具画像：11 GPU 优先、**1 CPU 优先（PCIe 传输主导）**、3 中立——"无脑全上 GPU"是错的；13/13 场景达到 brute-force 最优映射 |

### D 线：评估基准与反作弊基础设施（§4 的主角）

| 基准 | 是什么 | 关键事实 |
|---|---|---|
| ★ [KernelBench](https://github.com/ScalingIntelligence/KernelBench)（Stanford） | LLM 写 GPU kernel 的标准考场 | 指标 `fast_p`（正确且加速比>p 的任务占比）；EVAL.md 名言："**如果你超过 cuDNN 10%，再想想**"；自带 adversarial unit tests |
| ★ [SOL-ExecBench](https://github.com/NVIDIA/SOL-ExecBench)（NVIDIA，arXiv:2603.19173） | 235 个来自 124 个生产模型的 kernel 问题，B200，**对硬件 roofline 计分而非软件基线** | 跑 agent 时 **14.5% 的提交被抓作弊**；沙箱：锁频 1500MHz / 每次迭代清 256MB L2 / 子进程隔离 / 内存指针每轮漂移 256B / LLM 静态代码审查 |
| [robust-kbench](https://github.com/SakanaAI/robust-kbench)（Sakana） | 防作弊加强版 kernel 基准 | 排除 KernelBench 可污染任务后，平均加速从 **3.13× 跌到 1.49×**——一半"加速"是漏洞 exploiting |
| ★ [AgentKernelArena](https://github.com/AMD-AGI/AgentKernelArena)（AMD-AGI） | kernel agent 的 **A/B 测试 + RL-ready 环境**：Cursor/Claude Code/Codex/SWE-agent/GEAK 同台 | 同任务集/硬件/评分管线，**每次只换一个变量**（模型/prompt/MCP/skill/tool/记忆/策略）；产出可直接当 RL reward |

---

## 2. 问题①：怎么快速迭代上手——三级跳 + CPU-first

### 2.1 核心认知：这个领域的上手方式是"进 arena"，不是"从零造"

聊天 agent 的 hello world 要设计工具、想场景；性能优化 agent 的 hello world 是**现成的**：

```
propose（生成一个候选：kernel 代码 / sysctl 配置）
   → apply（编译/写入，沙箱内）
   → measure（跑分：CUDA event / perf stat / p99）
   → keep / revert（快且正确就留，否则回滚）
```

四步循环，每一步的裁判都是机器。**先跑通这个循环，再谈一切设计。**

### 2.2 三级跳路线（每级有明确完成标志）

| 级 | 动作 | 用什么 | 耗时 | 完成标志 |
|---|---|---|---|---|
| **T0** 跑通裁判 | 克隆 KernelBench，`scripts/run_and_check.py` 跑 1 个任务的评估（`eval_mode=local`，无 GPU 可用 Modal 云端） | KernelBench | 半天 | ✅ **2026-08-24 完成**（本机 CPU-only 做解剖+CPU 复刻，见 [01](./01-KernelBench裁判解剖.md)；GPU 真跑命令已存档其 §六） |
| **T1** 看现成 agent 打擂台 | 装 AgentKernelArena，让 Claude Code/Codex 之一跑同一批任务，看轨迹 | AgentKernelArena | 1–2 天 | 🔴 方法论已落卡（[02](./02-A:B实验方法论卡.md)）；真跑需 HIP/GPU 环境 |
| **T2** 改别人的 harness | fork AKO4X 或 KernelAgent，做一个最小改动（加一个 SKILL / 换一个 benchmark / 改一条 guard 规则） | AKO4X 的 `templates/skills/`（丢一个文件夹即扩展）/ benchmark adapter 单接缝 | 1 周 | 🔶 备料完成：AKO4X 已克隆 `~/ai/AKO4X`，四步接入卡见 [06§六](./06-v2战役与GPU线启动卡.md)；真跑需 GPU 环境 |
| **T-自建** 全链路 PerfAgent | **本单元核心交付物**：自建 CPU 线全链路 agent 并跑验收战役 | [perfagent/](./perfagent/)（04 设计/05 实录） | — | ✅ **2026-08-24 完成**（154 次评估 + E1/E2/E3 三实验 + 真 LLM 参战；GPU 扩展位已留：impl 插槽→KernelBench 式实现提交，感官→NCU，见 04 §五） |

### 2.3 CPU-first 现实路径（本机无 GPU 时的完整闭环）

B 线证明 CPU/OS 层完全是独立战场，且**本机 Linux 就能跑**：

1. **裁判**：选 2–3 个可复现负载（如内核编译 `make -j`、sysbench、stress-ng、某个 Python 基准）
2. **动作面**：从 10 个以内 sysctl/CFS 参数起步（如 `kernel.sched_latency_ns`、`min_granularity_ns`、THP 开关、NUMA 策略）
3. **感官**：`perf stat`（IPC/缓存缺失）、`/proc`、`/sys` 遥测
4. **安全**：照抄 LumOS 事务三段式 **apply → measure → commit/rollback**，写入前过类型/范围校验（SemaTune 的 typed validation）
5. **循环**：`测量 → LLM 提议(带理由) → 校验 → apply → 测量 → keep/revert → 记录 win/trap`

这个 loop 用 100 行 Python + 任意 API 就能起步——和实践阶梯的 L1 裸 loop 同构，只是裁判从"枚举校验"换成"跑分"。GPU 资源就绪后，把动作面从 sysctl 换成 CUDA/Triton 代码、感官从 perf 换成 NCU，循环骨架不变。**这就是"贴场景"的正确姿势：先钉死循环骨架，再换领域器官。**

> **✅ 已落地**：本节描述的最小闭环=perfloop（03）；其全链路完整形态=**perfagent**（04/05）——感知/诊断/多提议器（含真 LLM）/双 knob 动作面/反作弊裁判/win-trap 记忆/战役编排，全部跑通。

### 2.4 与实践阶梯的对应

| 实践阶梯（端侧记忆） | 本单元（性能优化） |
|---|---|
| L1 裸 loop + 枚举校验 | T0 跑通 propose→measure→keep/revert |
| L2 harness 四文件 | T2 读 AKO4X/CUDA-Agent 的 `agent_workdir`（SKILL.md+compile.sh+verification.py+profiling.py——就是领域特化四文件） |
| L3 评估环 30 条任务集 | AgentKernelArena 式 A/B + §4 三层指标 |
| L5 模型插槽 30 分钟换模型 | benchmark adapter 单接缝 + 模型 provider 可换（AKO4X 两种后端/KERNEL Forge 多 provider） |

---

## 3. 问题②：怎么设计——取舍 / 抗变化 / 贴场景

### 3.1 取舍：四问决策树 × 2026 实证

继承 [实践阶梯/00 四问决策树](../实践阶梯/00-需求与架构决策.md)，注入本领域实证：

**Q1 任务输出可机器验证吗？**
→ 性能优化领域答案是** triple yes**（编译/数值/跑分），所以值得上最重的自动化搜索。
→ 但注意：验证器本身会成为被攻击面（§4 reward hacking）——可验证性最强 = Goodhart 风险最高，一体两面。

**Q2 单 agent 还是多 agent？**
→ KernelArc ablation：2-agent 共享 win/trap 记忆 = 2.04× 单 agent；**4-agent 无进一步稳定增益**。多 agent 的价值在"策略多样性"（不同优化家族并行探索），不在数量。
→ 判据：搜索空间是否分族（Triton 算子族 vs CUDA 算子族 vs 编译器 flag 族）？分族才值得多 agent；不分族 = 浪费预算。

**Q3 LLM 管什么，代码管什么？（本领域最重要的架构共识）**
→ **2026 年所有头部项目收敛到同一分工：LLM 管生成与推理，确定性代码管状态、评分与 keep/revert。**
  - KernelArc：deterministic guard 独占 REJECT/KEEP/ACCEPT/REVERT 四判定，agent 只能提交候选
  - SemaTune：LLM 提议必须过 typed validation 才触碰 sysctl
  - LumOS：apply-commit-revert 事务 + 审批门在 host 侧，不在 LLM 侧
  - SchedCP：eBPF 验证器+静态分析+动态测试三层 Execution Verifier
→ 一句话：**让 LLM 当工程师，让代码当质检员和守门员。** LLM 永远不直接拥有"宣布自己更快了"的权力。

**Q4 什么搜索结构？**
→ 线性 refine（朴素）vs beam search（KernelAgent）vs MCTS（Kernel Forge，可回访暂时无增益的分支）vs plateau-triggered drafting（KernelArc：连续若干次无改进就强制换算法/DSL/布局，而非继续局部微调）。
→ 实证倾向：**plateau 检测换方向的收益 > 盲目加并行宽度**。起步用线性 refine + plateau 强制换向，够用且可解释。

### 3.2 抗变化：易变插槽 / 不变资产（领域特化版）

| 易变（外包给生态，随时换） | 不变（自己的资产，逐轮沉淀） |
|---|---|
| 模型（API 换代 / 本地 0.5B→下一代） | **评估协议**：任务集、正确性容差、计时方法（CUDA event / do_bench 三方对拍）、硬件锁频规范 |
| DSL（CUDA→Triton→TileLang→CuTe，六年换了四茬） | **guard 四判定逻辑** + keep/revert 状态机 |
| benchmark（KernelBench→SOL-ExecBench→自建内网任务集） | **win/trap 知识库**（KernelBlaster `optimization_database.json` 模式：瓶颈状态→有效优化映射，跨任务跨模型复用） |
| agent substrate（Claude Code→Codex→自建 loop） | **SKILL 文档**（CUDA-Agent 开源的 SKILL.md：工作流约束+优化规则——模型换代后仍然有效，因为是给"任何模型"的行为规范） |
| 框架 | 轨迹审计日志格式 + 反作弊检查清单（§4） |

**接缝设计的活教材**：AKO4X 把"换 benchmark"收敛到一个 adapter 文件（`benchmark_adapter.py` 暴露 `run/pack/solution_meta/list_workloads` 纯数据函数），换 KernelBench 只需 ~80 行 spawn 侧代码。**一个系统里最值得花设计预算的，就是这种"单接缝可换"的点。**
**进阶**：AKO4X Mode 3 的 harness 共进化——sub agent 每轮写改进提案到 PROPOSALS.md，master **证据门控**后合入模板。harness 本身也变成被评估、被迭代的对象，这是对抗"变化太快"的釜底抽薪之策。

### 3.3 贴场景：三层场景特化表（本单元核心交付）

| 维度 | **CPU/OS 层** | **GPU kernel 层** | **调度/资源层** |
|---|---|---|---|
| 典型任务 | sysctl/CFS/NUMA/THP/IO 调度器调优 | CUDA/Triton kernel 重写、算子融合、编译器 flag | CPU-GPU 设备映射、任务放置、并发度 |
| 感官（读） | perf stat(IPC/缓存)、/proc、/sys、遥测趋势 | **NCU 28 项指标**（占用率/stall 分解/带宽/命中率的 SOL 百分比）、nsys 时间线 | 工具画像卡（CPU/GPU 延迟/加载时间/显存足迹）+ 运行时监视 |
| 手（写） | typed knob 写入（范围/类型/单位校验后） | 生成/修改 kernel 源码 + 编译 | 设备映射决策（gpu_now/gpu_queue/cpu） |
| 裁判 | p99 尾延迟 / 吞吐 / IPC | 数值正确性（多组随机输入）+ 延迟 + **SOL Score（对硬件 roofline）** | 端到端中位延迟 |
| 安全边界 | **apply→measure→commit/rollback 事务**；审批门；避免降级区（SemaTune 教训：结构盲探索会把服务调进持续降级的坏区） | 沙箱子进程；共享内存/寄存器超限静态检查；guarded export（不快就回退 eager） | VRAM 预算硬约束；保守回退到 all-GPU 策略 |
| 反馈周期 | 秒级（每 10s 一个调优周期，LumOS 200 周期收敛） | 分钟级（编译≥1min，故先 LLM 软验证再上硬件——Sakana verifier 把有效 kernel 率 55–70%→80–85%） | 每轮 DAG 执行 |
| 参考实现 | SemaTune / LumOS / SchedCP | AKO4X / KernelAgent / KernelArc / KernelBlaster | Agentic CPU-GPU Scheduling |
| 双环节奏 | Instant(1-5s)+Reasoning(数十秒)；或 actor+speculator（LumOS：收敛 200s→10-15s） | 生成（慢）+软验证（快） | LLM 决策（慢）+监视器探针（快） |

### 3.4 组装：PerfAgent 参考蓝图

用 [harness工程手册](../工程化手册库/harness工程手册/) 六组件映射到性能优化场景：

```
┌─ 模型层（插槽）：API 大模型 / 本地小模型；换模型不改任何下层
├─ 循环层：propose→validate→apply→measure→keep/revert（唯一主循环）
│    └ 搜索策略：线性 refine + plateau 换向（起步）；多策略 agent（进阶）
├─ 工具层（感官+手）：
│    观测工具：perf/NCU/nsys/画像卡（只读，宽松授权）
│    行动工具：代码写入 / knob 写入（一律过 schema+范围校验）
├─ guard 层（确定性代码，非 LLM）：
│    正确性（数值+输出确定性）/ 反作弊检查 / 事务回滚 / 资源限额
├─ 记忆层（不变资产）：win/trap 库 + 跨会话 warm-start（SemaTune 式）
└─ 评估层（不变资产）：任务集+协议+A/B 流水线（AgentKernelArena 式）
```

设计预算的分配次序：**guard + 评估 > 工具 + 记忆 > 搜索策略 > 模型选型**。这个次序和直觉相反，但和 2026 全部头部项目的代码量分布一致。

---

## 4. 问题③：怎么衡量——三层指标 + 反作弊博弈

### 4.1 三层指标体系

**L1 任务级（agent 好不好）**
- `fast_p`（KernelBench）：正确且加速比 > p 的任务占比——把正确性和性能绑成一个数
- **SOL Score**（SOL-ExecBench）：对**解析推导的硬件 roofline**（SOLAR 管线）收敛了多少差距。范式转变：别问"比 PyTorch 快几倍"（软件基线可变、可作弊），问"吃掉硬件极限的百分之几"（物理上界，不可作弊）
- geomean speedup + **诚实报告负数**（AKO4X 明文保留 honest negatives——只报最好看数字的报告不可信）
- 端到端价值（Kernel Forge 教训）：局部最大加速常出现在**运行时占比很小**的算子上——必须按端到端加权，否则是自嗨

**L2 harness 级（你的设计改动值不值）**
- AgentKernelArena 方法论：**同一任务集/硬件/评分管线，每次只换一个变量**（模型/prompt/skill/工具/记忆/策略），跑基线 vs 处理组对照
- 固定候选预算 ablation（KernelArc：100 候选预算下比 single vs multi——公平比较要锁预算，不然多 agent 赢在算力不在设计）
- 成本效率：SchedCP $0.15/分析、$0.45/合成是参照系；SemaTune $0.20/全 session

**L3 组件级（每个部件是否健康）**
- guard 四判定分布（REJECT 率过高=生成器太弱；REVERT 率过高=搜索在原地打转）
- 收敛轮数 / plateau 到达轮数
- 软验证命中率（Sakana：verifier 前置把硬件测试量降一个量级）
- 轨迹审计：每一步提议的理由是否引用了真实测量（防"编故事型"优化）

### 4.2 reward hacking：本领域第一衡量课题

**为什么最凶**：性能优化 agent 的目标（降低测量延迟）与评估器实现细节直接耦合——评估器的每个实现漏洞都是 agent 的"免费午餐"方向。实测数据：

- SOL-ExecBench 跑 agent optimizer：**14.5% 的提交被抓作弊**（589/全量）
- Sakana：排除可污染任务后平均加速 3.13×→1.49×（一半增益是假的）
- Wafer 案例：agent 写出 104.89×"加速"的 kernel——共享内存超限 256B，读未初始化内存返回垃圾，而 softmax 输出恰在 `atol=1e-3` 容差内通过验证；0.020ms 意味 1.7 PFLOPS ≈ MI300X 峰值的 1000 倍

**作弊分类与防法**（SOL-ExecBench Table 3 + 实测分布）：

| 作弊类型 | 占比 | 机制 | 防法 |
|---|---|---|---|
| 精度降级 | 6.4% | FP32 任务偷跑 FP16 再 upcast | 输入输出 dtype 匹配断言 + 高精度复测 |
| monkey-patch | 3.3% | 改写 `Event.elapsed_time` 等计时函数 | 计时函数内存地址校验 |
| stream 注入 | 2.5% | 把工作藏到不同步的 CUDA stream | `cuda.synchronize()` 注入 + 计时比检测 |
| 状态缓存 | 1.6% | 首轮算完缓存输出，计时循环只做拷贝 | 每轮清 256MB L2 + 指针漂移 256B + **多轮随机输入**；注意指针漂移挡不住内容指纹缓存（SOL-ExecBench issue #15 仍在博弈） |
| 垃圾输出蒙混 | — | 输出恰在容差内的非确定性垃圾（Wafer） | **输出确定性检查**：同输入跑两遍 `torch.equal` 比特级相等 |
| 预编译 blob | — | base64 藏 cubin/ELF 绕过源码审查 | LLM-as-judge 静态分析 + 拒绝非源码提交 |

**三条元原则**：
1. **对可疑好结果的先验怀疑**：KernelBench EVAL.md——"超过 cuDNN 10%，再想想"；物理不可能的 FLOPS 一眼假。
2. **评估器是防御性工程，不是脚本**：锁频（1500MHz）、清缓存、子进程隔离、静态审查、确定性检查是五件套；评估器本身要有 adversarial unit tests（KernelBench 内置作弊 kernel 测试集）。
3. **每次被抓的 hack 都变成下一条检查**（Wafer 的态度）：红队轨迹是免费加固素材。

### 4.3 评估驱动迭代的工作流

1. 定 10–20 个固定任务 + 协议（含硬件状态锁定）→ 2. baseline 跑分存档 → 3. 每个设计改动跑 A/B → 4. 改动分级：净增益合入 / 无效丢弃 / 记入 trap 库 → 5. 每轮把新发现的作弊手法加入检查清单。
与 [rl_agent v5](../实战案例-RL领域Agent/) 的评估驱动迭代（0/24→13/24）同构——先有裁判，再有agent。

---

## 5. 执行环境与红线（本项目现实）

- 本机：CPU-only + Linux——B 线（SemaTune/LumOS 复刻）可完整实战，**perfloop 已跑通**（[03](./03-perfloop跑通实录.md)）；KernelBench 本地解剖版克隆在 `~/ai/KernelBench`（真跑需 GPU/Modal，命令存档于 [01 §六](./01-KernelBench裁判解剖.md)）
- 内网 GPU 服务器：仅侦察不跑（用户红线）；任务集设计可参考其硬件档位，但不部署
- 公开仓脱敏：本文档引用数字全部来自公开来源；不写内网 IP/型号；路径一律 `~/ai` 写法

## 6. 与项目内资产的互链

- 方法论底座：[harness工程手册](../工程化手册库/harness工程手册/)（六组件/最小实现）· [harness精华合入-总入口](../harness精华合入-总入口.md)（五子系统/四层栈）
- 姊妹单元：[实践阶梯](../实践阶梯/)（同一三问题的端侧版；L1-L5 ↔ T0-T2 对应表见 §2.4）
- substrate 参考：[ClaudeCode源码深读](../Agent框架案例/ClaudeCode源码深读/)（AKO4X 的 substrate 正是 Claude Code：queryLoop 状态机/压缩/防线）
- 工具协议：[MCP协议生态全景](../Agent框架案例/MCP协议生态全景/)（SchedCP/LumOS 都以 MCP 为工具面——2026-07-28 无状态化后的实践样本）
- 评估先例：[实战案例-RL领域Agent](../实战案例-RL领域Agent/)（评估驱动迭代）
