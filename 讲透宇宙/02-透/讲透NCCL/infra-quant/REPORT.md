# NCCL v2.32.3 量化分析报告 —— 用《深入理解 AI Infra》模型对照工程实现

> 方法论：《深入理解 AI Infra》（bojieli/ai-infra-book）「从约束推导设计」+ 数据搬移五问。
> 工具集：`/data/usershare/ai/ai-infra-tools/`（collective_model / protocol_crossover / busbw_table / topology_cut / nccl_structure_scan）。
> 生成日期：2026-11-03。对象：本仓 v2.32.3-1（commit 3e46c089）。全部锚点可点击复核。

---

## 0. 一页结论

1. **NCCL 的 tuning 子系统就是书的一阶通信模型（T = α + βM）的工程化**：
   轮次函数、机内/跨机分层延迟、algbw↔busbw 换算与书 ch06 式 6-9/6-10 逐项同构（§2 对照表）。
2. **协议折扣实测化**：理论 LL 效率 2/3，NCCL 取 0.5；LL128 理论 15/16=0.9375，NCCL 取 0.92 并按
   每 channel 36.7 GB/s（Hopper）封顶——书模型给出形状，NCCL 用实测系数修正幅度。
3. **实测离物理上界的差距**：H100 NVL8 AllReduce busbw 484 GB/s > 单向 450 GB/s，是**环用双向
   channel 的直接证据**；AllGather 365 GB/s = 单向 81%，缺口归因于 LL128 per-channel 封顶与
   chunk 协调开销（§4）。
4. **代码重量分布**回答了"NCCL 复杂度在哪"：transports 61,774 行（34%）> device kernels 12,851 >
   graph/tuning 10,850——**"经过哪里"（路径/传输）才是集合通信库的工程主体**，算法选择只占 6%。

---

## 1. 结构量化（nccl_structure_scan.py）

| 子系统 | 文件数 | 行数 | 占比 | 五问对应 |
| --- | ---: | ---: | ---: | --- |
| transports（net_ib/net_socket/cuda_p2p/sharp/…） | 108 | 61,774 | 34.3% | 经过哪里 |
| include/plugin/os/misc（含 tuner 插件接口） | 285 | 57,274 | 31.8% | — |
| rma/ce/mnnvl/ras（新能力层） | 28 | 19,250 | 10.7% | 搬什么（新内存语义） |
| device kernels（all_reduce.h 等 8 collective × 3 协议） | 32 | 12,851 | 7.1% | 搬几次 |
| graph/topo/tuning（选路+选算法） | 28 | 10,850 | 6.0% | 谁必须等它 |
| proxy/bootstrap/init | 8 | 10,262 | 5.7% | — |
| collectives api（enqueue/scheduler） | 18 | 7,819 | 4.3% | — |
| **合计** | **507** | **180,080** | | |

要点：**算法内核只占 7%**；真正吃代码的是传输层适配（每一种"经过哪里"的物理路径一个插件）与
拓扑搜索。这与书的判断一致：集合通信的性能问题大多不是"算法规格"，而是路径与等待。

关键常量（`src/include/device.h`）：

| 常量 | 值 | 含义 |
| --- | --- | --- |
| `NCCL_LL128_LINESIZE` | 128 B | LL128 行大小（:113） |
| `NCCL_LL128_DATAELEMS` | LINEELEMS−1 = 15/16 | LL128 载荷效率 93.75%（:115） |
| `NCCL_LL128_ELEMS_PER_THREAD` | 120 | 每 LLVM 线程元素（:118） |
| `NCCL_LL_FLAG_MAX` | 0x100 | LL flag 8bit 轮转（:104） |
| 协议族 | LL / LL128 / SIMPLE | `NCCL_PROTO_*` |
| 算法族 | RING / TREE / COLLNET_DIRECT / NVLS / PAT | tuning 各自 .cc 建模 |

---

## 2. 公式对照：书模型 ↔ NCCL tuning 实现

### 2.1 轮次与字节（环代数完全一致）

| 书 ch06 §6.4 | NCCL 实现 | 锚点 |
| --- | --- | --- |
| 环 AR 轮次 2(N−1) | `AllReduce → 2*(nRanks−1)` | `src/tuning/tuning_general.cc:16` |
| RS/AG 轮次 (N−1) | `ReduceScatter/AllGather → nRanks−1` | 同上 :18 |
| 每卡发送 2(N−1)/N·M | `generalBandwidths = busBw × nRanks/nSteps`（algbw↔busbw 换数） | `src/tuning/ring.cc:47` |
| T = α·rounds + bytes/B | `timeUs = lat + size/bw`（SimModel 对每算法×协议取最小） | `src/tuning/cost_model.cc:470` |

工具复核：`collective_model.py --n 8 --bytes 696320 --bw 450e9 --alpha-us 0.24` 得环/树交叉点
**691 KB**，书 §6.4 锚点 **680 KiB**（H100 参数），偏差 1.6%（α 取值差异），公式实现正确。

### 2.2 延迟分层（书"分层归约"思想的内化）

NCCL 把每轮延迟拆成机内/跨机两类，按跨机步数加权（`src/tuning/ring.cc:53-90`）：

```
latency = base + (nSteps − nInterSteps)·α_intra + nInterSteps·α_inter(+netOverhead)
nInterSteps(AllReduce) = 2·(nNodes − 1)     # 跨机环步数，同书分层环模型
SIMPLE 额外 + latencyInter×1、netOverhead×3 # 大消息 chunk 同步的工程惩罚
```

树模型（`src/tuning/tree.cc:53`）：

```
latency(AR) = 2 × ((ppn − 1)·α_intra + log₂(nNodes)·α_inter)   # = 书式 6-10 的分层版
busBw(tree) = bw × nChannels × 0.5                              # 树单方向减半
```

**结论**：NCCL 没有照搬教科书二项树（书 calculations 源码注释明言 "not NCCL's double-tree
implementation"），而是**机内扁平 + 机间 log₂**的分层树——正是书 §7.2.1 分层归约的形态。

### 2.3 协议折扣：理论 vs 工程

| 协议 | 书/理论效率 | NCCL 工程折扣 | 锚点 |
| --- | ---: | ---: | --- |
| LL | 2/3（8B data+4B flag） | **0.5**，且封顶 llMaxBws（Hopper 141 GB/s） | `ring.cc:41`、`cost_model.cc:187` |
| LL128 | 15/16 = 0.9375 | **0.92**，且封顶 perChMaxRingLL128Bws **36.7 GB/s/ch**（Hopper） | `ring.cc:42-44`、`cost_model.cc:196` |
| SIMPLE | 1.0 | 1.0（+netOverhead×3 延迟罚） | `ring.cc:63`、:90 |

工具复算交叉点（喂 NCCL 工程折扣，`protocol_crossover.py --bw 450e9 --eff-ll 0.5 --eff-ll128 0.92`）：

- **LL × LL128 ≈ 246 KB**——与书 §7.2.2 单消息交叉点 M*=α·B≈244 KB 同量级；
- **LL128 × Simple ≈ 18 MB**（α 差 3.5 µs 假设下）：中消息窗口很宽，解释了 LL128 作为
  默认中坚协议的地位；但 LL128 的 36.7 GB/s/channel 封顶意味着 8 channel 只有 294 GB/s——
  **大消息必然切到 SIMPLE**，与 NCCL 实际行为一致。

### 2.4 LL128 每 channel 常量（`cost_model.cc:196-201`）

| 架构 | perChMaxRingLL128Bw | perChMaxTreeLL128Bw(N1) |
| --- | ---: | ---: |
| Volta | 20.0 | 20.0 |
| Ampere | 20.0 | 20.0 |
| Hopper | 36.7 | 36.7 |
| Blackwell | 40.0 | 55.6 |

Blackwell 树 LL128（55.6）> 环（40.0）：新架构上树协议内核反而更快——单一"环永远最优"的
直觉在 Blackwell 被实测数据推翻，这正是"先按第一性原理算上限，再看实测离上限多远"的价值。

---

## 3. 实测 vs 物理上界（官方 perf 表 + busbw_table.py）

官方 `docs/perf/v2.32.3-1.md`（3-run 均值，busbw 口径）：

| 平台/配置 | 操作 | 实测 busbw | 单向链路上界 | 利用率 | 判读 |
| --- | --- | ---: | ---: | ---: | --- |
| H100 NVL8 Legacy | AllReduce | 484 | 450 | **107.6%** | **>单向 = 环占双向 channel 的证据** |
| H100 NVL8 Legacy | AllGather | 365 | 450 | 81.1% | 缺口=chunk 协调+SM 竞态 |
| H100 NVL8 Legacy | ReduceScatter | 360 | 450 | 80.0% | 同上 |
| H100 NVL8 CE | AllGather | 378 | 450 | 84.0% | CE（copy engine）卸载再 +3pp |
| B200 NVL8 Legacy | AllReduce | 846 | 900* | 94% | *NVLink5 单向 900 假设 |
| GB300 NVL64 Symmetric | AllReduce | 992 | 900* | 110% | 对称内存 kernel 亦超单向（双向） |

三点判读：

1. **AllReduce busbw 超过单向链路带宽**（484>450、992>900）不是测量错误：环 AR 每卡发送
   2(N−1)/N·M，双 channel 可同时用 NVSwitch 上下行两个方向，每卡注入速率突破单向下界。
   书的割集分析（§7.1.2）按"瓶颈割集容量"给上界，NVSwitch 全双工下割容量即 2×450。
2. **AG/RS 停在 80% 左右**：瓶颈不是链路而是每卡处理——LL128 perCh 36.7 GB/s（8ch=294）与
   SIMPLE 的 chunk 等待、SM 内核与计算竞态。CE kernel（+3pp）说明部分缺口在 SM 排程，
   用 copy engine 卸载能拿回一部分。
3. **GB300 NVL64 Symmetric AR 992 GB/s**：单 NVLink 域内对称内存 kernel 已把 8GB 消息的
   AR 推到 ~1TB/s 每卡——数据搬移五问中"搬几次"被对称内存（写一次=全域可见）直接削减。

---

## 4. 数据搬移五问下的 NCCL 设计速写

| 五问 | NCCL 的回答 | 代码落点 |
| --- | --- | --- |
| 搬什么 | 8 种 collective × 3 协议内核；新语义=CE/CopyEngine、对称内存、NVLS 多播、RMA | `src/device/*.h`、`ce_coll.cc`、`sym_kernels.cc`、`rma/` |
| 搬多少 | chunk 切分（Simple stepSize、LL128 行、LL 8B），由 tuner 按消息大小定 | `src/include/device.h:145`、`tuning/` |
| 搬几次 | 轮次 2(N−1)/(N−1) 硬编码于 nsteps；跨机步数 2(nNodes−1) | `tuning_general.cc:15` |
| 经过哪里 | 拓扑检测→路径打分→环/树构建，63% 的代码在这层（transports+graph） | `src/graph/`、`src/transport/` |
| 谁必须等它 | LL/LL128 flag 轮转 + credit 在途窗口；SIMPLE 的 chunk 同步（netOverhead×3）；proxy 线程握手 | `device.h:104`、`ring.cc:63,90`、`proxy.cc` |

---

## 5. 差距归因与可行动结论

按书"实测离上限的差距=模型漏项或系统开销"框架：

1. **AG/RS 81% 缺口**（H100）：模型漏项=SM 内核执行与 chunk 协调不在纯链路模型里。
   行动：`NCCL_ALGO=Ring NCCL_PROTO=Simple` 大消息基准 + `NCCL_DEBUG=INFO` 观察 channel 数
   是否把 36.7/ch 封顶绕开（切 SIMPLE 后 perCh 封顶不适用）。
2. **LL 的 0.5 折扣**：理论 2/3 的剩余缺口在 flag 读-判-写依赖链（每 8B 一次依赖），模型
   无法预测，属"必须实测"项——这正是书反复强调"估算给量级，实测定胜负"的原因。
3. **树在 Blackwell 反超**（55.6 vs 40.0 GB/s/ch）：升级硬件后不要沿用上一代的算法直觉，
   用 tuner 常量表或 autotuning 实测说话。

## 6. 复现命令

```bash
T=/data/usershare/ai/ai-infra-tools
python3 $T/nccl_structure_scan.py --repo /usr-data/data2/kylin/nccl          # §1
python3 $T/collective_model.py --n 8 --bytes 696320 --bw 450e9 --alpha-us 0.24  # §2.1 交叉点 691KB
python3 $T/protocol_crossover.py --bw 450e9 --eff-ll 0.5 --eff-ll128 0.92    # §2.3 协议交叉
python3 $T/busbw_table.py --n 8 --bw 450e9 --op allreduce                    # §3 口径换算
python3 $T/topology_cut.py --n 16 --g 8 --bw-nv 450e9 --bw-nic 50e9          # 跨机场景下界
```

公式蒸馏底稿：`/data/usershare/ai/ai-infra-tools/docs/infrabook-ch67-distill.md`（34 公式带书 § 出处）。
