# NUMA 架构精读：多处理器内存拓扑

> 参照：Patterson §5.8 / Linux NUMA / AMD Infinity Fabric / Intel UPI
>
> csdiy 对应：tinymesi + tinycpu + csapp Ch6(cache层次) + os

---

## 一、UMA vs NUMA

### UMA（Uniform Memory Access）

```
所有 CPU 核通过同一总线访问同一内存:
  CPU0 ─┐
  CPU1 ─┼─ Bus ─ Memory
  CPU2 ─┤
  CPU3 ─┘

→ 所有核访问内存延迟相同
→ 但总线成为瓶颈（核越多越慢）
→ 适合 ≤8 核
```

### NUMA（Non-Uniform Memory Access）

```
每个 CPU 插槽有自己的本地内存:
  CPU0 (本地内存 0-32GB) ──┐
                            ├─ Interconnect
  CPU1 (本地内存 32-64GB) ─┘

→ 访问本地内存: ~100ns（快）
→ 访问远端内存: ~200-400ns（慢 2-4x）
→ 适合 >8 核 / 多路服务器
```

---

## 二、NUMA 拓扑

```
NUMA Node 0                    NUMA Node 1
┌─────────────────────┐       ┌─────────────────────┐
│ CPU Core 0-15       │       │ CPU Core 16-31      │
│ L3 Cache (32MB)     │       │ L3 Cache (32MB)     │
│ Local Memory 0-64GB │       │ Local Memory 64-128GB│
└─────────┬───────────┘       └─────────┬───────────┘
          │                              │
          └──── Interconnect ───────────┘
           (UPI / Infinity Fabric / NVLink)

跨节点延迟:
  本地 L3:     ~10ns
  本地内存:    ~100ns
  远端内存:    ~200-400ns
  远端 L3:     ~150ns（某些架构可以缓存远端数据）
```

---

## 三、NUMA 对性能的影响

### 内存局部性

```python
# 场景：两个线程共享数据

# ❌ 差：数据在 Node 0，线程跑在 Node 1
Thread(Node1) → 读 Node0 的数据 → 200ns 延迟

# ✅ 好：数据和线程在同一个 Node
Thread(Node0) → 读 Node0 的数据 → 100ns 延迟

→ LLM 推理时，确保 GPU 和数据在同一个 NUMA 节点
```

### numa-aware 分配

```bash
# Linux NUMA 工具
numactl --hardware          # 查看 NUMA 拓扑
numactl --cpunodebind=0 --membind=0 python train.py  # 绑定到 Node 0

# 查看进程的 NUMA 分布
numastat -p $(pgrep python)
```

---

## 四、NUMA 和 LLM 训练

### 多 GPU + NUMA

```
服务器: 2 CPU × 16 核 + 8 GPU

NUMA Node 0: CPU 0-15 + GPU 0-3 + Memory 0-128GB
NUMA Node 1: CPU 16-31 + GPU 4-7 + Memory 128-256GB

→ GPU 0 训练时，数据应在 Node 0 的内存
→ GPU 4 训练时，数据应在 Node 1 的内存
→ 跨节点传输数据 → PCIe 延迟翻倍
```

### DataLoader 的 NUMA 感知

```python
# PyTorch 的 pin_memory + NUMA 感知
torch.multiprocessing.set_sharing_strategy('file_system')

# 每个 DataLoader worker 绑定到正确的 NUMA 节点
import os
os.sched_setaffinity(0, {0,1,2,3})  # 绑定 CPU 到 Node 0
```

---

## 五、NUMA 和 LLM 推理

### vLLM 的 NUMA 优化

```
vLLM 推理服务:
  ① 每个 GPU 绑定到最近的 NUMA 节点
  ② 模型权重预加载到对应 NUMA 内存
  ③ KV Cache 在 GPU 显存（不跨 NUMA）

→ 延迟降低 10-30%（NUMA-aware vs NUMA-oblivious）
```

---

## 六、NUMA 感知的内存分配策略

### First-Touch 策略

```python
# Linux 默认：first-touch 分配
# 数据在哪个 CPU 核上首次写入 → 就分配在哪个 NUMA 节点

import numpy as np
import os

# ❌ 差：在 Node 0 初始化 → 然后在 Node 1 使用
os.sched_setaffinity(0, {0})  # 绑定到 Node 0
data = np.zeros(1_000_000)    # 在 Node 0 分配
os.sched_setaffinity(0, {16}) # 换到 Node 1
data[:] = compute()           # 跨 NUMA 访问 → 慢

# ✅ 好：在使用数据的 NUMA 节点上初始化
os.sched_setaffinity(0, {16}) # 先绑定到 Node 1
data = np.zeros(1_000_000)    # 在 Node 1 分配
data[:] = compute()           # 本地访问 → 快
```

---

## 七、NUMA 调优命令

```bash
# 1. 查看 NUMA 拓扑
numactl --hardware
lscpu | grep NUMA

# 2. 查看内存分布
numastat
numastat -p $(pgrep python)

# 3. 绑定进程到 NUMA 节点
numactl --cpunodebind=0 --membind=0 python train.py
numactl --physcpubind=0-15 --localalloc python infer.py

# 4. 禁用 NUMA balancing（某些场景下手动管理更好）
echo 0 > /proc/sys/kernel/numa_balancing
```

---

## 八、一句话总结

> NUMA = 每个多处理器有自己的本地内存 → 访问本地快、远端慢。
>
> **NUMA 感知 = 让数据和使用它的 CPU 在同一个节点。**
>
> LLM 训练/推理的 10-30% 延迟差异来自 NUMA 配置。

---

*配套：[tinymesi/mesi.py](../projects/tinymesi/mesi.py) | [csapp Ch6](../notes/csapp-程序员视角.md) | [model-parallel精读](model-parallel-精读.md)*
