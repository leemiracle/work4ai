# EPLB 新人指南（简版）

> 依据仓库知识图谱（8 节点/12 边/4 层/8 步导览）与 README 整理。姊妹篇：《讲透LPLB》（内嵌本仓算法做静态重排）、《讲透DualPipe》（流水线维度）。

## 一、项目定位

EPLB（Expert Parallelism Load Balancer）是 DeepSeek-V3 开源的**专家并行静态负载均衡器**：专家并行（EP）下各专家负载随 workload 波动，EPLB 用**冗余专家**策略复制重载专家，再启发式装箱到 GPU 使各卡负载均衡；并借助 group-limited expert routing 尽量让同组专家落同节点以减少跨节点流量。

它处理的是**静态/准静态不均衡**（数据分布导致的持续过载专家），输入是历史负载统计（常用滑动平均，预测方法不在本仓范围）。家族定位：EPLB 静态重排 + LPLB 线性规划每 batch 动态分流 + DualPipe 流水线重叠，配合 DeepEP/3FS 构成 DeepSeek 训推基础设施。

## 二、架构分层

全仓核心就一个文件，知识图谱 4 层：

1. **重排入口与策略层**：`rebalance_experts` 按拓扑选择分层或全局策略。
2. **专家复制与装箱层**：`replicate_experts` 决定复制倍数、`balanced_packing` 贪心装箱。
3. **文档层**：README 讲清策略与适用场景。
4. **工具配置层**：understand 插件配置（可忽略）。

## 三、核心模块

四个函数全部落在 **`eplb.py` 单文件**，纯 torch 张量实现、无第三方求解器：

- **`rebalance_experts(weight, num_replicas, num_groups, num_nodes, num_gpus)`**——唯一对外入口：组数能被节点数整除时走**分层策略**（先组装箱到节点 → 节点内复制 → 副本装箱到 GPU，适合 prefill 阶段较小 EP 规模），否则走**全局策略**（不分组建制全局复制+装箱，适合 decode 阶段较大 EP 规模）。返回 `phy2log / log2phy / logcnt` 三个物理↔逻辑重排映射。
- **`replicate_experts`**：按"平均每副本负载最大化"（weight/logcnt 取 max）决定每个逻辑专家复制几份，把专家扩充到 num_phy 个物理槽位。
- **`balanced_packing`**：最底层构件——专家按负载降序排序后交替放入当前最轻的包，保证各包总负载尽量均衡；分层与全局策略都复用它。
- 索引换算靠 gather/scatter/unflatten 在逻辑/物理两层间转换。

## 四、快速上手

无安装，单文件即用，README 示例：2 层 MoE、每层 12 专家、每层 4 个冗余专家、16 副本放 2 节点 8 GPU：

```python
import torch, eplb

weight = torch.tensor([[ 90, 132,  40,  61, 104, 165,  39,   4,  73,  56, 183,  86],
                       [ 20, 107, 104,  64,  19, 197, 187, 157, 172,  86,  16,  27]])
phy2log, log2phy, logcnt = eplb.rebalance_experts(
    weight, num_replicas=16, num_groups=4, num_nodes=2, num_gpus=8)
```

`phy2log` 每行是一层、每格是一个物理槽位上放的逻辑专家编号——对照 README 的 example.png 可直观看懂复制与放置方案。

## 五、学习路径

1. 读 README 理解"为什么需要冗余专家"与两种策略的适用场景（prefill 小 EP vs decode 大 EP）。
2. 跑通上面示例，画出 phy2log 对应的放置图。
3. 精读 `eplb.py`（百行级）：从 `balanced_packing` 逆向往上——贪心装箱 → `replicate_experts` → 分层策略 → `rebalance_experts` 分派。
4. 理解 phy2log/log2phy/logcnt 三映射如何在训练框架里驱动专家权重重排与路由改写。
5. 延伸阅读 LPLB 仓：其 `lplb/eplb.py` 内嵌了本仓算法（reordering-only），并在此之上做每 batch 的 LP 动态均衡——先懂 EPLB 再看 LPLB 事半功倍。
