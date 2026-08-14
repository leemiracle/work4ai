# 04 · Ray 分布式调度：Task / Actor / Object 三原语

> [00-03](./00-为什么必须分布式.md) 讲的是"模型怎么切"——但训练 / 推理服务是**完整系统**：数据预处理、推理、后处理、多副本路由、自动扩缩容、训练任务编排、超参搜索、强化学习 rollout……这些**编排问题**才是工程大头。**Ray**（UC Berkeley 2018，Anyscale 公司化）用三个原语解决了"Python 分布式系统"——这是 OpenAI / Anthropic 训练框架的隐藏地基（[RLHF 训练栈](https://www.anyscale.com/blog) 几乎都跑在 Ray 上）。
>
> 配套：[Ray 论文 (OSDI 2018)](https://www.usenney.edu/...) + [`讲透公开课/03-D1 Ray`](<../讲透公开课/03-AI Infra 源码导读清单.md>)

---

**2017 年，伯克利 RISELab。** Robert 看着 RL 训练脚本崩溃第 N 次——不是模型崩，是**编排崩**：policy inference 在 GPU、env rollout 在 CPU、reward model 在另一台机器；三个 Python 进程互相 `socket.recv()`，一卡死全卡死。他意识到：**RLHF 这类场景根本不是"训练一个大模型"，而是"协调几十个分布式任务的 DAG"**。他和团队写了 Ray，让"分布式 Python"像写函数一样简单——`@ray.remote` 一行装饰器，函数立刻可以远程执行。**OpenAI 2018 年起用 Ray 做 RL 训练，2022 年 ChatGPT 的 RLHF 栈同样跑在 Ray 上**。

---

## 一、Ray 的三原语

### 1.1 Task（无状态函数远程执行）

```python
@ray.remote
def train_one_batch(data):
    ...
fut = train_one_batch.remote(batch)   # 立刻返回 future
result = ray.get(fut)                  # 阻塞拿结果
```

- **无状态**：函数幂等，失败可在别的机器重启
- **异步**：`.remote()` 立刻返回，`.get()` 才阻塞
- **数据 locality**：调度器优先把 task 调度到数据所在节点

### 1.2 Actor（有状态服务）

```python
@ray.remote
class Policy:
    def __init__(self): self.model = load_model()
    def infer(self, obs): return self.model(obs)

p = Policy.remote()        # 在某节点实例化
a1 = p.infer.remote(obs1)  # 方法调用 = task
```

- **有状态**：状态封装在 actor 内，单线程串行化方法调用
- **生命周期**：actor 长驻，跨 task 复用（避免每次重载模型）
- **场景**：推理服务、env simulator、parameter server

### 1.3 Object（不可变共享值）

```python
obj = ray.put(big_tensor)        # 进 Plasma 内存存储
fut = f.remote(obj)              # 传引用，不传数据
```

- **不可变**：一次写入，多次读取
- **零拷贝**：同节点用 mmap、跨节点用 Apache Arrow + RDMA
- **Plasma**：基于共享内存的对象存储，是大批量数据传递的"显存"

## 二、为什么对 AI 场景特别契合

### 2.1 RL 训练的天然 fit

RL = env（actor）+ policy（actor）+ learner（task）+ replay buffer（object）——**几乎一比一对应 Ray 三原语**。这是 OpenAI 选 Ray 的根本原因。

### 2.2 与 PyTorch / TensorFlow 解耦

Ray 不管你训练框架，**只负责调度**——所以可以同时跑 PyTorch learner + TensorFlow env，灵活组合。

### 2.3 Ray Train / Ray Serve / RLlib

Ray 上层栈：
- **Ray Train**：分布式训练（与 FSDP/ZeRO 集成）
- **Ray Serve**：推理服务（路由 / autoscale / 多模型）
- **RLlib**：RL 算法库（PPO / SAC / IMPALA 都内置）
- **Ray Tune**：超参搜索

> 📌 现代 AI 平台 = Ray（编排）+ PyTorch（训练）+ vLLM（推理）—— **Ray 是胶水层的事实标准**。

## 三、反模式与陷阱

### 3.1 L4 陷阱 1：把 actor 当服务发现

Ray actor **不是微服务**——重启策略、健康检查、负载均衡都是手动的。要生产部署，**套 Ray Serve**，不要直接暴露 actor。

### 3.2 L4 陷阱 2：忽视 object store 容量

Plasma 默认占 30% 系统内存。**放大 batch 或大模型参数时**，object store 容易 OOM——导致 task 卡在调度。生产环境要显式调大 `object_store_memory`。

### 3.3 L4 陷阱 3：`ray.get()` 滥用

`ray.get()` 是阻塞 + 全量反序列化——**循环里 ray.get 等于回到同步世界**。要用 `ray.wait()` + 异步流水线。

### 3.4 L4 陷阱 4：训练大模型用 Ray Train 的预期错位

Ray Train **不是 Megatron / DeepSpeed 的替代品**——它是**编排层**，底层模型并行仍由 FSDP / Megatron 实现。Ray 负责启停 worker、汇总指标。混淆两者会写出极烂的训练代码。

## 四、和 [分布式 03](./03-TP与PP.md) / [05](./05-推理分布式.md) 的关系

| 层 | 谁负责 |
|----|--------|
| 模型并行（TP/PP/ZeRO）| Megatron / DeepSpeed / PyTorch FSDP |
| **任务调度 + actor 编排** | **Ray**（本章）|
| 推理服务（batching / KV cache）| vLLM / SGLang（[05](./05-推理分布式.md)）|

三者叠加：Ray Serve 调度多个 vLLM 副本，每个副本内部跑自己的 PagedAttention——**Ray 不管 KV Cache，vLLM 不管路由**。

## 五、费曼回炉（L2 自检）

- **F2 卡壳点**：我曾以为 Ray 是"另一种 Spark"。重读论文后发现：**Spark 是数据流（DAG 静态），Ray 是 actor 模型（动态拓扑）**——Spark 适合 ETL，Ray 适合 RL / 推理这种有状态 + 动态拓扑。
- **F3 术语翻译**：
  - "actor" → 一个"住"在某台机器上的服务对象，记得自己上一句话
  - "Plasma object store" → 集群的"快递中转仓"，task 之间传大件不直接交手，丢仓里取
- **F4 回炉**：v1 我写"Ray 是分布式训练框架"；v2 改成"Ray 是**调度 + 编排**框架，训练靠它下面挂的 PyTorch/Megatron"——它的核心价值在编排不在并行算法。

---

> 🎯 **一句话**：Ray = 分布式 Python 的三原语（Task / Actor / Object）——**不替代训练框架，是它们的胶水层**，是 RLHF / 多模型推理 / 超参搜索场景的事实标准。

📌 **下一步**：[05 推理分布式](./05-推理分布式vLLM-SGLang.md)（vLLM/SGLang TP+EP），或 [06 通信优化](./06-通信优化.md)（NCCL + 计算通信重叠）。
