# 06 · v2 战役实录 + GPU 线启动卡（2026-08-24 第二轮）

> **上一轮**：[05](./05-perfagent跑通实录.md)（v1，154 次评估）。本轮把 05§五 的全部下一步执行完：
> re-baseline / pointer-key 军备竞赛 / heuristic 补遥测 / transformers 真负载 / T2 备料。
> **产物**：[experiments/perfagent/](./experiments/perfagent/)（*-v2*.log、redteam_report.md v2、cards.json）

---

## 一、v2 代码升级清单（全部对应 05§五 条目）

| 升级 | 位置 | 动机 |
|---|---|---|
| re-baseline：search 前每负载 3 次独立子进程测量取中位（`--rebase`，默认 3） | campaign.py | 消跨 run 漂移（05§四：512 同配置漂 3×） |
| runner 扰动三档：0 恒定 / 1 内容扰动 / 2 **对象轮换**（copy 新指针+新内容） | runner.py | 防指针键缓存（SOL-ExecBench issue#15 防御） |
| 作弊双实现：`cheat_content`（内容键）+ `cheat_ptr`（指针键） | workloads.py | 红队军备竞赛的攻方 |
| heuristic 补 `probe_best_threads` 遥测通道（insert 首位） | proposers.py | E2-v2 验证"规则+遥测 vs LLM+遥测" |
| **transformers 真负载** `bert4-256-fw`（BertModel from_config 4 层 256 hidden，随机权重钉种子，惰性 torch import） | workloads.py | 从合成 matmul 走向真框架 |
| guard 容差分层：同实现复跑 bitwise（1e-12）/ 跨实现数值级（1e-4） | guard.py | bert 教训（见 §三） |

## 二、E4 红队矩阵 v2：军备竞赛阶梯完整复现（本日核心成果）

| 作弊 \ 防御 | 0 无防御 | 1 内容扰动 | 2 对象轮换 |
|---|---|---|---|
| 内容键 | vs-ref **154×** | vs-ref **0.9×**（死） | vs-ref **1.0×**（死） |
| 指针键 | vs-ref **471×** | vs-ref **467×**（**原样存活**） | vs-ref **0.5×**（死+倒贴） |

（vs-ref = 同 threads 同 perturb 下 ref 真算耗时 / cheat 耗时，即**纯作弊收益**；矩阵见 [redteam_report.md](./experiments/perfagent/redteam_report.md)）

三条结论：
1. **防御必须与攻击键型匹配**：内容扰动（防御 1）对指针键完全无效（467× ≈ 无防御 471×）——SOL-ExecBench 当年指针漂移防住了 pointer 键却被 issue#15 的内容指纹绕过，我们反向复刻了同一课：**每种防御只封一种键**。
2. **对象轮换（防御 2）是双杀**：新对象=新指针+新内容，两种键全失效；且 0.5× 显示作弊者倒贴键计算+字典查找后每次还得真算——**比诚实计算更慢就是防御的理想终态**。
3. **verdict 维度与纯作弊收益维度必须分开**：矩阵里全部 6 格 verdict 都是 keep（对默认 baseline 的混合 speedup 仍 >1）——因为 cheat 配了 threads=4 本来就快。若只看 verdict，六格全"通过"，军备竞赛隐身。

**红队元教训（当日两次失误）**：① v1 用 matmul-64 信噪比不足；② v1 矩阵 cheat=4 线程 vs baseline=默认 8 线程——speedup 混入配置收益，把"作弊存活"读成"配置差异"。**红队的对照组与实验组一样需要设计**：纯作弊收益必须同配置对照（ref_ms/cheat_ms）。

## 三、bert 负载带来的两堂裁判课

1. **随机权重负载必须钉种子**（torch.manual_seed）：否则每个子进程权重不同，跨进程指纹必然 mismatch——threads 1/2 全 INVALID 的根因。**负载自带的随机性会变成裁判的随机性**。
2. **容差分层**：钉种子后 3/5/6 线程仍 INVALID——不同线程数走不同 BLAS 分块，浮点求和顺序不同，经 LayerNorm/softmax 放大后超出 1e-6。正确设计是两级：同实现复跑 bitwise 严格（det_ok，1e-12）；跨实现比对数值级宽松（1e-4——放过实现差，仍抓 O(1) 级垃圾输出/作弊）。与 KernelBench `allclose(rtol/atol)` 哲学一致。
3. **附带铁证**：bert 默认 8 线程 399.8ms vs 搜索到的 4 线程 68.7ms——**transformers 真框架上默认配置差 5.8×**，铁律#1（小模型 set_num_threads）从 numpy 扩展到 torch+transformers 的独立实证。

## 四、E2-v2：re-baseline + heuristic 补遥测后的提议器对比

| 负载 | grid(8) | heuristic-v2(≤3) | llm(≤4) |
|---|---|---|---|
| matmul-512 | 7.09× @6t | 3.10× @4t(第1次) | 11.27× @5t |
| matmul-2048 | 1.72× @5t | **1.56× @4t**（v1 曾 0.96× MISS） | 1.75× @4t+aff |
| bert4-256 | **5.21× @4t** | — | 2.62× @4t |

- **"一行遥测修复规则盲区"验证成功**：v1 heuristic 在 2048 只提 8t（0.96× MISS）；v2 插入 probe_best_threads=4 → 首次评估即 1.56× KEEP。先验+遥测双通道后，heuristic 与 LLM 的差距从"翻车 vs 命中"缩到 1.56 vs 1.75。
- **跨轮 speedup 不可直接比**：每轮 re-baseline 的 baseline 不同（512 三轮：24.9/12.6/44.9ms），同配置 speedup 波动大——严格 A/B 应共享同轮基线（本轮教训，已记入 02 卡修订待办）。
- **llm 在 512 上 11.27×**：部分来自当轮 baseline 偏高（44.9ms）——正是 §五方差课的活例，单格数字是线索不是结论。

## 五、方差与 re-baseline 效果

rebase3 中位把漂移压到可用区间（如 512 三次 [20.6, 27.8, 24.9]→中位 24.9），但 **matmul-512 的 OpenBLAS 线程调度不稳是负载固有属性**，跨轮基线仍差 2-3×。彻底解法（下一轮）：候选也测 2 次取中位 + 报告只保留跨轮复现的结论（keep 需两次独立命中）。

## 六、T2 备料：AKO4X 已克隆（GPU 线启动卡）

**本地仓**：`~/ai/AKO4X`（gh-proxy，--depth 1）。关键结构：`spawn.py`（子环境生成）/`master/`（闭环 master agent）/`templates/skills/`（SKILL 目录，丢文件夹即扩展）/`scripts/benchmark_adapter.py`（**benchmark 单接缝**——换 KernelBench 只需 ~80 行 spawn 侧代码）。

**GPU 就绪后的接入路径（不改 perfagent 骨架的升级位，接 04§五）**：

| 步 | 动作 | 验收 |
|---|---|---|
| 1 | 读 AKO4X docs/porting.md + benchmark_adapter.py，把 perfagent 的 workloads/runner 换成 KernelBench problem 适配（走 adapter 接缝） | spawn 出的子环境能跑 level1 单题 |
| 2 | proposers 的 llm 换成 kernel 生成模式（上下文=operator card 而非画像卡，Kernel Forge 的 operator card 结构） | 1 个 task 上 propose→compile→verify 闭环 |
| 3 | guard 接 SOL-ExecBench 式五件套（锁频/清 L2/子进程/确定性/静态审查）——我们的 runner 已有后三者的 CPU 版 | E4 矩阵在 GPU 作弊 kernel 上重演 |
| 4 | campaign --rebase 照用（GPU 版=re-基线 eager） | fast_p 报告 |

**Qwen2.5-0.5B 接入位**（本机 `~/ai/models/` 有真权重）：bert4-256 换成 Qwen 前向负载（transformers AutoModelForCausalLM，1 层 decode），子进程加载成本 ~15s/次——需 runner 加"进程内多 workload 复用"或模型常驻 server 模式，属下一轮工程。

## 七、v2 战役总账

- 总评估 87+ 次（v2 轮）+ v1 154 次 ≈ 240+ 次；invalid 0（容差分层后）；SUSPICIOUS 14 次
- 代码增量：+110 行（runner 三档/双作弊、rebaseline、heuristic 遥测、bert 负载、容差分层、E4 矩阵）
- 当日 bug 修复 5 个：measure bool→int 签名、numpy data_ptr、bert 种子、容差分层、E4 对照设计

---

生成：2026-08-24 · 上级 [README](./README.md) · 设计 [04](./04-全链路PerfAgent设计.md) · 前轮 [05](./05-perfagent跑通实录.md)
