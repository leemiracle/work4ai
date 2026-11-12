# 三 · 代码：90 行模拟器把公式跑给你看

> 本单元的立场：**没跑过的公式只是传说**。[ring_sim.py](ring_sim.py)（约 90 行，纯 NumPy，零依赖）把 01/02 幕的每个论断变成可执行断言。以下全部输出为 2026-11-12 真跑结果（`python3 ring_sim.py 8` 等，四种规模全绿）。

## 3.1 数据结构：一张表看懂环状态

每卡向量 `v` 切成 N 块存进 `blocks[r][k]`（rank r 手中第 k 块）。环算法每步只改这张表的一行两格：发一块、收一块。

```python
blocks = [v.reshape(n, per).copy() for v in vectors]  # blocks[r][k] = rank r 手中第 k 块
```

## 3.2 两阶段的核心循环

reduce-scatter：第 $i$ 步 rank $r$ 发送块 $(r-i) \bmod N$（这个"错位发块"让每块的累加责任沿环轮转，N-1 步后每块的完全和恰好各归其主）：

```python
for i in range(n - 1):
    send_idx = [((r - i) % n) for r in range(n)]
    for r in range(n):
        blk = send_idx[r]
        sent[r] += blocks[r][blk].nbytes          # 记账：真实字节数
        incoming[(r + 1) % n] = (blk, blocks[r][blk].copy())
    for r in range(n):                             # 收块并累加
        blk, data = incoming[r]
        blocks[r][blk] += data
```

all-gather 循环同构，把 `+=` 换成 `=`（和分片已在手，只需扩散）。**两个阶段唯一区别是一个字符**——这是环算法结构对称性在代码里的倒影。

## 3.3 真跑输出（N=8，每卡 1MB float64）

```
N=8 卡, 每卡向量 125000 float64 (每卡消息 1.0 MB)
[环法]   每 rank 发送 1.75 MB, 理论 2(N-1)/N*S = 1.75 MB  ✓
[朴素法] rank0 发送 8.00 MB, 其余各 1.00 MB
[负载均衡] 环法最忙/最闲 rank = 1.00 倍; 朴素法 = 8.0 倍
[数值] 全部 8 rank 与 rank0 求和结果逐元素一致 ✓ (allclose)
[步数] reduce-scatter 7 步 + all-gather 7 步 = 14 步
```

规模扫描（通信量对账表，理论 $2\frac{N-1}{N}S$）：

| N | 模拟每 rank 发送 | 理论 | 朴素法 rank0 | 环法不均衡 |
|---|---|---|---|---|
| 2 | 1.00×S | 1.00×S ✓ | 2×S | 1.0 |
| 4 | 1.50×S | 1.50×S ✓ | 4×S | 1.0 |
| 8 | 1.75×S | 1.75×S ✓ | 8×S | 1.0 |
| 16 | 1.875×S | 1.875×S ✓ | 16×S | 1.0 |

**逐字节精确吻合**——模拟器没有近似，理论系数 $2(N-1)/N$ 在整数层面就是"每步发 S/N、共 2(N-1) 步"。

## 3.4 断言即教学：模拟器如何反过来抓笔误

本模拟器孵化时真实发生过一次"公式打脸"：初版把理论式的 $S$ 写成全体总大小（$\sum N \times S$），断言 2 当场炸出 `[1750000, ...] != 14000000`——模拟值恰好等于正确公式的 1.75MB。**代码是公式的考官**：纸上推导的量纲错误在断言面前无处可逃（该坑已回写 02 幕的"量纲警告"）。这也是仓库的方法论传统：宣称必须实测、对账先于结论。

## 3.5 从模拟器到真实 NCCL 的距离

模拟器故意省掉的三层，正是真实库的厚度：

1. **传输层**：模拟器 `incoming[(r+1)%n]` 是内存拷贝；NCCL 同一行对应的是 P2P channel 上的多协议引擎（LL/Simple 打包、代理线程跨 NIC 中转——[讲透NCCL/explain/08-p2p-channel.md](../../02-透/讲透NCCL/explain/08-p2p-channel.md)、[11-proxy.md](../../02-透/讲透NCCL/explain/11-proxy.md)）；
2. **拓扑层**：模拟器的环是给定的；NCCL 要自己"找到"环——bootstrap 探测、拓扑搜索、通道分配三段式（[04-topo-search.md](../../02-透/讲透NCCL/explain/05-topo-search.md)），这是它最玄学的部分；
3. **流水层**：模拟器逐步同步；NCCL 把消息再切块让多 channel 流水重叠，逼近 2.3 节理论时间的下界。

📌 下一步 → [04-不足：NCCL 的局限与失败模式](04-不足-NCCL的局限与失败模式.md)

✍️ 练习：给 `ring_allreduce` 加一个 `topo_bw` 参数（每条链路带宽不同，如环上一条慢 10 倍的 PCIe 桥），观察完成时间由最慢链路的哪一段决定——这就是"跨机环的致命一跳"。
