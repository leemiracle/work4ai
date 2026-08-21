# 02 · PagedAttention 深挖：vLLM 怎么把 OS 虚存搬进 LLM

> [00](./00-为什么KV Cache是推理的生命线.md) 算过 KV Cache 账：Llama-3-70B 在 batch=32 时要 86GB，**比权重还大**。问题是显存不只"总量不够"，还有"**碎片**"——不同请求序列长度各异，按最大长度预分配会浪费 60-80%。vLLM（SOSP 2023）的 PagedAttention 把 OS 虚拟内存思想直接搬进推理引擎：**把 KV Cache 切成固定大小的 block，逻辑连续/物理离散，block table 做映射**。这是 OS 思想在 AI 最经典的一次复用。
>
> 配套：[`讲透公开课/03-I1 vLLM`](<../讲透公开课/03-AI Infra 源码导读清单.md>)（源码 `vllm/core/block_manager.py`）+ [`讲透GPU与系统级/03`](../讲透GPU与系统级/03-推理引擎.md)

---

**2023 年初，伯克利。** Kwon 和同事盯着 A100 的 nvidia-smi：80GB 显存里塞了 4 个并发请求，但显存利用率只有 31%。剩下的 69% 全是"**给最长序列预分配但实际没用**"的空气。他突然想起研究生时读的《OSTEP》——分页、虚拟地址、页表。"为什么不给 KV Cache 也搞一套虚存？" 八周后 PagedAttention 出生，throughput 翻 2-4 倍。**vLLM 一夜成为开源推理引擎的事实标准**。

---

## 一、问题：连续分配的灾难

朴素做法：每个请求预分配 `max_seq_len × per_token_kv_bytes` 的连续显存。

- **内部碎片**：请求实际生成长度远小于 max → 浪费
- **外部碎片**：请求进出，显存被切得七零八落
- 实测：**有效利用率 20-40%**——一大半显存被浪费

这就是 OS 1961 年解决的问题。vLLM 的洞察：**KV Cache 就是进程地址空间，token 写入就是内存访问，请求结束就是进程退出**。

## 二、PagedAttention：分页式 KV

### 2.1 数据结构

- **Block**（页）：固定大小，存 16 个 token 的 KV（vLLM 默认 `block_size=16`）
- **Block table**（页表）：每个请求一张表，逻辑 block 序号 → 物理 block 编号
- **物理 block 池**：所有空闲 block 组成的池，全局共享

```
请求 A 的逻辑视图：    [B0][B1][B2]   ← 连续
请求 A 的 block table:  17  42   3
物理池：              ...[3][...][17][...][42]...   ← 散落
```

### 2.2 三件事被治好

| 病 | 治法 |
|----|------|
| 内部碎片 | 只浪费最后一个 block 的 < 16 token（约 3% vs 60%+）|
| 外部碎片 | 物理 block 大小统一，零外部碎片 |
| 共享前缀 | 同一物理 block 被多个请求的 block table 指向 → **CoW 复用** |

### 2.3 attention kernel 的修改

PagedAttention 重写了 CUDA kernel：给定 block table，kernel 按 block 边界循环加载 K/V，对 16 个 token 一组计算 attention。这破坏了"连续内存"假设，但换来的是显存自由——**OS 教科书里"分页加速 vs 连续访问"的 tradeoff 在 GPU 上重演**。

## 三、反模式：把分页当万能

### 3.1 L4 陷阱 1：`block_size` 选错

- 太小（如 4）：kernel launch 开销爆炸，attention 慢 30%+
- 太大（如 64）：内部碎片重新抬头
- vLLM 经验值：**16 是 sweet spot**

### 3.2 L4 陷阱 2：以为 PagedAttention 解决一切

它**只解决显存碎片，不解决显存总容量**。长上下文场景（100K+ token）仍要配合 KV 量化（[05](./05-KVCache量化.md)）或分层存储（06（待写））。

### 3.3 L4 陷阱 3：copy-on-write 的隐藏成本

多轮对话复用前缀时，第一个改写 token 触发 CoW——**长前缀的 CoW 可能比从头重算还慢**。SGLang 的 RadixAttention（03（待写））针对此优化。

## 四、费曼回炉（L2 自检）

- **F2 卡壳点**：我曾以为 PagedAttention 是"算法优化"。重读后发现它**根本没改 attention 数学**，只改了**存储布局**——是"系统工程"不是"ML 算法"。这才是它最大的启示。
- **F3 术语翻译**：
  - "block table" → 一张"目录"，告诉你"第几页 KV 存在仓库哪个货架"
  - "CoW (copy-on-write)" → 共享前缀，谁先改谁先复制一份
- **F4 回炉**：v1 我写"vLLM 比 HuggingFace 快"；v2 改成"vLLM 在**并发请求**下吞吐 2-4×，单请求无差异"——PagedAttention 的收益全在并发。

---

> 🎯 **一句话**：PagedAttention = OS 虚存思想在 LLM 推理的工程化——把 KV Cache 切成固定 block + block table 映射，治好碎片化，**显存利用率从 30% 提到 90%+**。

📌 **下一步**：03 RadixAttention（待写）（SGLang 怎么用基数树进一步治共享前缀），或 [04 MLA](./04-MLA深挖.md)（DeepSeek 怎么从架构层压缩 KV）。
