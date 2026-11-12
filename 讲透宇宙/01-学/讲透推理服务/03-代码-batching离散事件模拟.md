# 三 · 代码：把 1.93x 跑出来

> [batching_sim.py](batching_sim.py)（约 100 行，纯 stdlib）按 iteration 离散推进时间轴，把 01 幕的餐厅比喻变成可执行断言。以下输出全部为 2026-11-12 真跑（`python3 batching_sim.py`）。

## 3.1 模型的最小诚实

模拟器只保留两种调度差异的本质：

- 每个请求 = 1 步 prefill + $L_i$ 步 decode（异构：$L_i \in [8,128]$ 随机）；
- 每 iteration：批内每请求走 1 步；
- **static**：批空时才凑新批，凑到 16 为止——已有批必须整体跑完；
- **continuous**：每个 iteration 结束都有人退场，等位者立刻补位。

刻意省掉：attention 计算、KV 显存上限、抢占/优先级——这些让 02 幕的公式和 04 幕的暗面去讲。**模拟器只回答一个问题：调度粒度本身值多少。**

## 3.2 核心循环对照（两种模式的分岔点）

```python
if mode == 'static':
    if not batch:                      # 只有批空了才能收新客
        while ... len(batch) < batch_size: 收到达的请求
else:                                   # continuous：每步都补位
    while ... len(batch) < batch_size and pending[idx]['arrive'] <= t: 收到达的请求
# ---- 一个 iteration：批内全员各走 1 步 ----
for rid in list(batch):
    batch[rid] -= 1
    if batch[rid] == 0: del batch[rid]  # 吃完即走（continuous 的退场即时性）
```

**两模式代码差 4 行，吞吐差 1.93 倍**——这个对比本身就是教学：最重要的优化往往不在更快地算，而在更聪明地**排**。

## 3.3 真跑输出（200 请求 / B=16 / 长度 8-128）

```
                 总时长    平均延迟    吞吐(req/it)    平均批占用
static           1679     750.3         0.119          7.7/16
continuous        872     339.8         0.229         14.9/16
吞吐提升 1.93x, 批占用提升 1.93x
```

批容量扫描（吞唂数 req/iteration）：

| B | static | continuous | 倍数 | 占用 static → cont |
|---|---|---|---|---|
| 8 | 0.068 | 0.119 | 1.76x | 4.4 → 7.7 |
| 16 | 0.119 | 0.229 | 1.93x | 7.7 → 14.9 |
| 32 | 0.210 | 0.414 | 1.97x | 13.6 → 26.8 |

两个规律：**B 越大 static 越亏**（"最慢食客"池越大）；continuous 的占用逼近 B 的 93%+——几乎每一步都在白拿 02.3 节说的"免费午餐"。

## 3.4 从模拟器到 vLLM 的距离

模拟器的一个"iteration"在真实引擎里是一整条流水：调度器（含抢占/优先级/前置 chunked prefill）→ KV 块分配（PagedAttention 的块表）→ CUDA graph 重放 → 输出采样。本仓 [讲透vLLM](../../02-透/讲透vLLM/README.md) 的 14454 节点图谱是这条流水的完整解剖（含 3222 commits 的增量手术合并范式），[讲透SGLang](../../02-透/讲透SGLang/README.md) 则展示了另一条路：RadixAttention 把"前缀共享"引入 KV 管理（模拟器里的等价物：多个请求共享同一段 system prompt 的 KV——留给读者的扩展练习）。

**模拟器到论文再到引擎的三级台阶**，正是 01 幕三个时代的代码倒影。

📌 下一步 → [04-不足：推理引擎的暗面](04-不足-推理引擎的暗面.md)

✍️ 练习一：把 `make_requests` 改同构（8,8），跑出两种调度的差距并解释归零原因。
✍️ 练习二（进阶）：给 continuous 模式加"优先级抢占"——新到的短请求插队到长请求前，观察平均延迟与 P99 延迟的反向变化（饥饿的种子在这里种下，见 04 幕）。
