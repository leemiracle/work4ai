# 03 · perfloop 跑通实录（CPU 调优裸 loop 第零号证据）

> **代码**：[experiments/perfloop/perfloop.py](./experiments/perfloop/perfloop.py)（~240 行，numpy 除外零依赖）
> **运行**：2026-08-24，本机 8 核 CPU / Linux / numpy 2.5.2，`python3 perfloop.py`
> **原始日志**：[experiments/perfloop/run.log](./experiments/perfloop/run.log) · 数据：[experiments/perfloop/results.jsonl](./experiments/perfloop/results.jsonl)
> **地位**：本单元的"第零号证据"（对照 [实践阶梯第零号证据](../实践阶梯/README.md)）——一切设计讨论的出发点。

---

## 一、跑通的闭环长什么样

```
grid proposer（8 个 threads 配置）
  → validate（类型/范围/联合约束，typed validation）
  → apply+measure（子进程隔离，env 注入，事务式）
  → guard 四级判定（measure_error / invalid / keep / revert + SUSPICIOUS flag）
  → results.jsonl 追加（win/trap 库，下次运行 warm-start 跳过已测）
```

16 次事务测量（8 配置 × 2 负载）全部完成，KEEP/REVERT 判定分布合理。

## 二、实测结果（2026-08-24，8 核）

基准（全默认配置，OpenBLAS 用满核）：matmul-256 = **35.3 ms**，matmul-2048 = **410.6 ms**

| threads | matmul-256 | speedup | matmul-2048 | speedup |
|---|---|---|---|---|
| 1 | 2.0 ms | 17.8× ⚠ | 977.3 ms | 0.42 |
| 2 | 1.1 ms | 33.3× ⚠ | 482.5 ms | 0.85 |
| 3 | 0.7 ms | 47.5× ⚠ | 365.6 ms | **1.12 KEEP** |
| 4 | 0.6 ms | 57.7× ⚠ | **350.8 ms** | **1.17 KEEP（最优）** |
| 6 | **0.5 ms（最优）** | 74.7× ⚠ | 420.5 ms | 0.98 |
| 7 | 75.8 ms | 0.47 | 759.8 ms | 0.54 |
| 8 | 68.4 ms | 0.52 | 496.4 ms | 0.83 |

## 三、五条铁证（每条都是教学点）

1. **项目铁律 #1 的独立复现**：默认满线程对小矩阵是灾难（35.3ms → 0.5ms，74×差距）。OpenBLAS 多线程同步开销 >> 256³ 计算量——这正是全项目"torch 小矩阵 set_num_threads(1)"铁律的 perfloop 实证。**agent 用 30 秒的 grid 扫描独立"发现"了人类踩坑总结的铁律**——这就是可验证闭环的价值。
2. **SUSPICIOUS flag 全部触发，但全部为真**：>5× 怀疑阈值在 256 负载上全挂了。这里没有作弊——是 baseline 太弱（全默认）而非 kernel 太强。**教训：怀疑阈值的含义取决于 baseline 强度**（KernelBench 名言"超 cuDNN 10% 再想想"的前提是 cuDNN 是强基线；弱基线下大 speedup 是常态）。flag 是"怀疑但不断罪"，与 reject 分离——KernelBench 哲学的现场验证。
3. **性能曲线非单调**：7/8 线程比 4 线程慢一倍（75.8 vs 350.8ms 于 2048）。**贪心爬山会永久掉坑**，grid/多起点搜索的价值证明；也是 KernelArc "plateau 换向"设计的微观缩影。
4. **两负载最优配置不同**（256→6 线程，2048→4 线程）：**调优结论依赖负载，不存在万能配置**——任何"最优 threads"结论都必须绑定负载画像。这正是 Kernel Forge "端到端加权"教训的微缩版。
5. **256 负载 0.5-0.7ms 段在噪声带边缘**：threads 3/4/6 的差距（0.7/0.6/0.5ms）未做重复实验验证，按 [02 A/B 卡](./02-A:B实验方法论卡.md) 第 4/7 条，这个排序**不应过度解读**——教学点：报告里主动标注自己的置信边界。

## 四、代码里埋的"头部项目防法"对照表

| perfloop 实现 | 来源 |
|---|---|
| verdict 四级分类（measure_error/invalid/keep/revert） | KernelBench eval.py 五重裁判（[01 §一](./01-KernelBench裁判解剖.md)） |
| guard 是纯函数，proposer 无 keep 宣布权 | KernelArc deterministic guard 四判定 |
| 子进程隔离 + 每次全新 env | SOL-ExecBench 子进程隔离（防状态泄漏/缓存作弊） |
| 首 vs 末迭代指纹必须 bitwise 一致 | Wafer 104× 假加速案的 determinism check |
| 统计指纹（sum/mean/max/norm）比对基准 | 抓"垃圾输出恰好蒙混 allclose"（全零/NaN 一眼假） |
| validate 先于一切（类型/范围/联合约束） | SemaTune typed validation：提议不过线不配碰机器 |
| results.jsonl win/trap 库 + warm-start 跳过 | KernelBlaster optimization_database.json |
| LLMProposer 插槽（OpenAI 兼容 env 三件套） | 易变/不变分离：proposer 是插槽，guard/评估是资产 |

## 五、下一步实验位（留给后续迭代）

- [ ] `--proposer llm` 对照 `--proposer grid`：同一任务集 A/B（[02 卡](./02-A:B实验方法论卡.md) 七问清单走一遍）——LLM 能否用更少提议次数逼近 grid 最优？（搜索效率 vs 零成本扫描的经典权衡）
- [ ] 加第二个 knob（如 `NPY_DISABLE_CPU_FEATURES` 或 CPU 亲和 taskset）→ 搜索空间平方增长，grid 开始吃力，LLM/贝叶斯提议的价值窗口出现
- [ ] 对抗测试：写一个"作弊 proposer"（返回缓存结果），验证 guard 能否抓住——把 KernelBench adversarial 单测模式搬过来
- [ ] 接真实负载（如 transformers CPU 推理一层的 latency），从合成 matmul 走向真场景

---

生成：2026-08-24 · 上级 [README](./README.md) · 前篇 [01 裁判解剖](./01-KernelBench裁判解剖.md) · [02 A/B 方法论](./02-A:B实验方法论卡.md)
