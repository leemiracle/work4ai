# 05 · perfagent 全链路跑通实录（2026-08-24）

> **地位**：perfagent（04 设计）的验收战役——154 次真实评估、3 个实验（E1 红队/E2 提议器 A/B/E3 双 knob）、真 LLM（glm-5.3，ZHIPU coding 端点）参战。
> **产物**：[experiments/perfagent/](./experiments/perfagent/)（cards.json / results.jsonl / campaign_report.md / redteam_report.md / 全程 log）
> **环境**：aarch64 · 8 物理核无 SMT · Linux · numpy（拓扑来自 cards.json，型号按脱敏规范不录）

---

## 一、profile：画像卡把 5 个负载分成三类

| 负载 | 画像 | baseline(ms) | 探针曲线 |
|---|---|---|---|
| matmul-64 | **flat** | 0.043 | 1-8 线程全等——低于 OpenBLAS 多线程门槛，负对照 |
| matmul-512 | **partial-scaling** | 38.3 | 1t:16.1 → 2t:9.3 → 4t:19.2 → **8t:98.8（灾难区）** |
| matmul-2048 | **compute-scaling** | 601.6 | 1t:1014 → 4t:337（最优探针）→ 8t:527 回落 |
| memcopy-256M | **flat** | 102.2 | 全平（带宽墙，线程无益） |
| ewise-32M | **flat** | 139.1 | 全平（numpy 逐元素单线程） |

**主叙事实锤**：默认配置远非最优——512 默认 38.3ms vs 最优 3-5ms（**8-11× 差距**），2048 默认 601.6 vs 212（**2.8×**）。"调优价值"不是理论，是本机现状。

## 二、E2：提议器 A/B（同任务集、同裁判、--fresh 隔离）

| 负载 | grid(8 评估) | heuristic(≤2) | **llm(≤4)** | fullgrid(14) |
|---|---|---|---|---|
| matmul-512 | 6.07× @4t | 4.18× @4t | **6.96× @3t/aff0-2**（第2次评估命中） | 11.45× @5t* |
| matmul-2048 | 1.72× @4t | **0.96× MISS @8t** | **1.90× @4t/aff0-3**（第1次命中） | 2.83× @5t |
| memcopy/ewise | 1.08/1.18× | 1.02/1.08× | 1.08/1.18× | 1.14/1.22× |

三个发现（每个都是设计课）：

1. **LLM 赢在读了遥测，heuristic 输在只读先验**：heuristic 的规则"compute→物理核(=8)"在 2048 上翻车（0.96×）；LLM 上下文里有 `probe_best_threads=4`，第一次提议就命中 4t（1.90×）。**提议质量 = f(上下文质量)**——SemaTune decision context 论点的本地复现。（反讽：修 heuristic 加一行 probe_best_threads 就能追平——但"人写规则要靠踩坑迭代，LLM 靠读数"本身就是结论。）
2. **LLM 会犯傻但在预算内自纠**：对 flat 的 matmul-64 提议 (8, aff 0-7)（零信息配置，全 revert 浪费 3 评估）；对 512 第一轮先提 2t（4.5×）再收敛到 3t/0-2（6.96×）。
3. **样本效率**：2048 上 llm 1 次评估 = grid 4 次评估的效果（1.90 vs 1.72）；fullgrid 14 次才到 2.83×。小空间里暴力扫描仍是绝对最优（512 的 11.45× 只有 fullgrid 扫到），**LLM 的价值窗口在"评估昂贵、空间大"的 regime**——接 GPU 后每次评估=编译+真跑，价值窗口立刻打开。

*512 的 11.45× 单 run 未复现（见 §四 方差警告）。

## 三、E1 红队：cheat_cache vs guard（比预期更尖锐）

| 模式 | baseline ms | cheat ms | speedup | verdict |
|---|---|---|---|---|
| nonce-on（防御开） | 0.0428 | 0.0795 | 0.5× | **revert**（作弊倒贴键开销） |
| nonce-off（漏洞模式） | 0.0427 | 0.0257 | 1.7× | **keep，且 flag 未触发** |

- 防御开：逐 rep 内容扰动 → 缓存键失效 → 作弊被迫真算 → 收益消失。
- 防御关：输入恒定 → 缓存命中 → 作弊**安静地进了榜单**——1.7× 低于 5× 阈值，连 SUSPICIOUS 都没挂。**结论比预设更强：怀疑阈值抓不住低调作弊，输入随机化才是第一道墙，阈值只是残网。**（若我的作弊键用 pointer 而非内容，扰动也防不住——军备竞赛见 §五。）
- 工程教训同日发生：红队行一度污染主榜单（matmul-64 最优显示 cheat 1.66×）→ 报告加 DQ 语义（作弊留痕不上榜）——**裁判写完的当天就要写它的红队和它的 DQ 规则**。

## 四、方差警告（本战役最重要的测量课）

matmul-512 同一配置跨 run 漂移 **3×**（5t: 9.86ms vs 3.34ms；4t: 6.31 vs 4.65）——OpenBLAS 在该尺寸的线程调度极不稳定，另有系统负载背景。2048 也有 1.4× 级漂移（4t: 349 vs 246ms）。**含义**：单 run 榜单（包括本报告的 11.45×）是线索不是结论；跨 run 比较必须走 [02 卡](./02-A:B实验方法论卡.md)第 4/7 问（重复≥3、报中位±离散、效应量过噪声带才宣布）。ewise 的 1.2× "全员加速"最可能是 baseline 单次偏慢的噪声——已在报告标注怀疑。

## 五、下一步（按杠杆排序）

1. **重复测量协议**：guard 前 re-baseline（每轮战役先重测 baseline 3 次取中位）——直接消解 §四 的大半方差争议
2. **pointer-key 作弊红队**：cheat 用 `data_ptr` 做键 → 现有内容扰动失效 → 防御升级为逐 rep 换输入对象（copy+扰动）——完整复刻 SOL-ExecBench issue #15 军备竞赛
3. **heuristic 补 probe_best_threads**（一行改动）→ 重跑 E2 验证"规则+遥测 vs LLM+遥测"
4. **接真负载**：transformers CPU 推理一层延迟（换 workloads.py 一处注册）
5. perf stat IPC 解析修复（-x, 格式字段位）——纯增益诊断信号

## 六、反作弊统计与成本

- 总评估 154 次：keep 58 / revert 84 / invalid 0 / measure_error 0 / SUSPICIOUS flag 10 次（全部来自弱 baseline 的真加速，验证"阈值含义取决于 baseline 强度"）
- LLM 调用 ~17 次（含 2 次超时重试），成本可忽略；崩溃 1 次（60s 超时炸 campaign）→ patch 重试+降级后不再复现

---

生成：2026-08-24 · 上级 [README](./README.md) · 设计 [04](./04-全链路PerfAgent设计.md) · 数据 [experiments/perfagent/](./experiments/perfagent/)
