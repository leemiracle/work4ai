# 深度解析：`python/sglang/srt/layers/dp_attention.py`

> 源码: `python/sglang/srt/layers/dp_attention.py` @ commit `ec075d8bc`（全文 629 行）

本文解析 SGLang **DP Attention**（Attention Data Parallelism）的通信基础设施。该文件回答一个核心问题：当 attention 用 DP、MoE 用 TP/EP 这种"混合并行"运行时，不同 DP rank 上**长度不一**的 token 序列如何在进入 MoE 前拼成全局 batch、算完后再拆回去？为此它实现了四件事：① DP/TP/CP 各通信组的 rank 代数与初始化（`compute_dp_attention_world_info` / `initialize_dp_attention`）；② padding 策略枚举 `DpPaddingMode`（MAX_LEN vs SUM_LEN 的成本模型择优）；③ gather/scatter 通信原语（`_dp_gather_via_all_gather` / `_dp_gather_via_all_reduce` / `dp_scatter`，含手写 triton memcpy）；④ 全局 gather 缓冲的元数据中心 `_DpGatheredBufferWrapper`。它是 DeepSeek V3 经典配置（`--enable-dp-attention --tp 8 --ep 8`）中 attention 与 MoE 两种并行度切换的枢纽。

---

## 目录

1. [为什么需要 DP Attention：问题与收益](#1-为什么需要-dp-attention)
2. [全局状态与初始化流程](#2-全局状态与初始化)
3. [rank 代数：world_info 与 local_info](#3-rank-代数)
4. [通信组体系：TP/CP/attn-TP/DP/MoE-DP 组](#4-通信组体系)
5. [padding 语义：DpPaddingMode 双模式](#5-padding-语义)
6. [gather 缓冲元数据中心：_DpGatheredBufferWrapper](#6-gather-缓冲元数据中心)
7. [gather/scatter 通信原语拆解](#7-gatherscatter-通信原语)
8. [MoE 侧通信包装：dp_reduce_scatter 与 moe_cp 家族](#8-moe-侧通信包装)
9. [CUDA Graph 的适配：slice_cpu 与图内默认模式](#9-cuda-graph-适配)
10. [`_RUN_DP_CTX` 考据与现行等价机制](#10-_run_dp_ctx-考据)
11. [与 MoE EP 的配合：DeepSeek 经典配置走读](#11-与-moe-ep-的配合)
12. [与其他模块的交互](#12-与其他模块的交互)
13. [关键设计决策](#13-关键设计决策)
14. [阅读建议](#14-阅读建议)

---

## 1. 为什么需要 DP Attention

长上下文时代 attention 与 MoE 的并行特性分裂：

- **attention**：prefill/extend 阶段是 compute-bound，但 TP 切分 attention 头会引入大量 all-reduce 通信，且 batch 内 KV cache/序列长短不一，TP 下所有 rank 被迫处理同一批序列；
- **MoE**：专家天然可切分（EP），但每个专家需要看到**尽量多的 token** 才能摊平负载——token 越集中越好。

DP Attention 的答案：**attention 沿 batch 维切**（每个 DP rank 独立跑自己那份请求的 attention，零通信），**MoE 沿专家维切但共享全部 token**（把各 DP rank 的 token 拼成全局 batch 再进 MoE）。于是每个 transformer 层内部发生两次"并行度切换"：

```
attn (DP)  ──dp_gather──▶  MoE (TP/EP, 全局 batch)  ──dp_scatter──▶  attn (DP)
```

本文件就是这两个箭头 + 全部 rank/组记账。代价是：DP rank 间 token 数不均 → **必须 padding**（§5）；gather/scatter 本身是通信（§7）；CUDA Graph 需要静态形状（§9）。

---

## 2. 全局状态与初始化

模块级可变全局量（L43–47）：

```python
_ATTN_DP_RANK / _ATTN_DP_SIZE          # 全局 DP 视角
_LOCAL_ATTN_DP_SIZE / _LOCAL_ATTN_DP_RANK  # moe_dense_tp_size 引入的局部 DP 视角
_ENABLE_DP_ATTENTION_FLAG              # 一次性开关
```

`initialize_dp_attention`（L274–311）在模型启动时被调用一次：

1. 从 `server_args` 取 `enable_dp_attention / dp_size / moe_dense_tp_size / attn_cp_size`（L280–283）；
2. 用全局 `tp_rank/tp_size`（L287–288）调 `compute_dp_attention_world_info` 算出 `_ATTN_DP_RANK`（L290–292）和 `compute_dp_attention_local_info` 算出 `_LOCAL_ATTN_DP_RANK`（L293–295）；
3. 确定 `_ATTN_DP_SIZE` 与 `_LOCAL_ATTN_DP_SIZE`：无 `moe_dense_tp_size` 时局部=全局（L299–302）；
4. 给 `_DpGatheredBufferWrapper.set_metadata` 灌 hidden_size/dtype/device（L307–311）。

与之配套的查询函数族（L314–363）全部带 `assert ... is not None, "dp attention not initialized!"` 防御——**初始化前查询直接崩溃**而不是返回静默错误值，这是分布式代码排障的善意设计。

`disable_dp_size`（L366–384）是唯一的运行期动态 patch：contextmanager 临时把 `_ATTN_DP_SIZE` 置 1，供投机解码的 **draft worker 以与 target 不同的 TP 度**运行 draft 模型（docstring L368–372）。这是全局状态方案对"多模型共存"场景的让步。

---

## 3. rank 代数

### 3.1 compute_dp_attention_world_info（L240–254）

核心是把全局 `tp_rank` 分解到 `(attn_dp, attn_cp, attn_tp)` 三维布局，L250–251 的注释给出公式：

```
tp_rank = (attn_dp_rank * attn_cp_size + attn_cp_rank) * attn_tp_size + attn_tp_rank
```

即 **tp 是最快变化维**（同一 attention TP 组的 rank 相邻，符合 NVLink 亲和性）。推导（L243–252）：

```python
attn_dp_size = dp_size if enable_dp_attention else 1
attn_tp_size = tp_size // attn_dp_size // attn_cp_size
attn_tp_rank = tp_rank % attn_tp_size
attn_dp_rank = tp_rank // (attn_tp_size * attn_cp_size)   # enable 时
```

例：tp_size=8, dp=4, cp=1 → attn_tp_size=2；rank 0..7 的 (dp, tp) = (0,0)(0,1)(1,0)(1,1)(2,0)(2,1)(3,0)(3,1)。

**8 卡数值实例**（建议读者亲手排一遍，后面所有章节都以此为坐标底图）：

| tp_rank | attn_dp_rank | attn_tp_rank | 归属组 |
|---|---|---|---|
| 0 | 0 | 0 | DP0：attn-TP 组 {0,1}；全 TP 组 {0..7} |
| 1 | 0 | 1 | 同上 |
| 2 | 1 | 0 | DP1：attn-TP 组 {2,3} |
| 3 | 1 | 1 | 同上 |
| 4 | 2 | 0 | DP2：attn-TP 组 {4,5} |
| 5 | 2 | 1 | 同上 |
| 6 | 3 | 0 | DP3：attn-TP 组 {6,7} |
| 7 | 3 | 1 | 同上 |

验证公式：`tp_rank 5 = (dp 2 × cp 1 + cp 0) × tp 2 + tp 1` ✓。若再叠 attn_cp_size=2（需要 tp_size=dp×cp×attn_tp 整除，如 16 卡 dp=2,cp=2,attn_tp=4），CP 组则由跨 DP 的同 tp 位 rank 组成（parallel_state 文档 L1802–1803 的 `[g0,g4][g1,g5]...` 布局）。

### 3.2 compute_dp_attention_local_info（L257–271）

`moe_dense_tp_size` 是为 **MoE 模型中的 dense 层**（如 DeepSeek 的前几层 dense FFN）单独设置的较小 TP 度。当 dense 层以 `moe_dense_tp_size` 运行时，全局 TP 组被重新划分出一套"局部 DP"坐标（L263–269），本质是同一 rank 代数在子 TP 域上的重放。`local_dp_size = max(1, dp_size // (tp_size // local_tp_size))`（L265）保证整除失败时退化为 1。

---

## 4. 通信组体系

本文件是**查询门面**，组的创建在 `sglang/srt/distributed/parallel_state.py` 的 `initialize_model_parallel`（L1758+）。三套组的关系：

| 组 | 本文件查询函数 | 行号 | parallel_state 侧 | 成员 |
|---|---|---|---|---|
| 全局 TP 组 | `get_tp_group`（经 import） | L26 | `_TP` | 连续 tp_size 个 rank，**DP rank 也在其中** |
| attn TP 组 | `get_attention_tp_group` | L322–323 | `_ATTN_TP` | 同一 DP rank 内的 attn-tp 成员 |
| attn CP 组 | `get_attention_cp_group` | L334–335 | `_ATTN_CP`（cp==tp 时直接复用 `_TP`，parallel_state L1875–1876） | 跨 DP rank 的同 tp 位 rank（ring attention 伙伴） |
| MoE DP 组 | `get_moe_cp_group` → `_get_moe_dp_group` | L603–605 | `_MOE_DP` | **名字叫 cp、实为 moe 数据并行组** |

parallel_state 的文档注释（L1796–1807）给出 8 卡实例：tp=4+cp=2 时，TP 组 `[g0..g3][g4..g7]`，CP 组 `[g0,g4][g1,g5]...`，MoE DP 组与 CP 组同构。

两个易混淆点的辨析：

1. **"全局 TP 组"在 DP attention 语境下扮演 DP gather 组**：因为 `tp_size = dp_size × attn_tp_size(× cp)`，一次跨全 TP 组的 all-gather 天然把所有 DP rank 的 token 拼起来——§7 的 `_dp_gather_via_all_gather` 正是利用这一点；
2. **`get_moe_cp_group` 的命名陷阱**（L604 docstring："Returns the MOE_DP group, which includes CP partners when attn_cp_size > moe_dp_size"）：当 attention 用了 CP 而 MoE 不用（`attn_cp_size > moe_dp_size`，`is_enable_moe_cp_allgather` L616–621 返回 True），MoE 前需要沿这个组把 CP 切片 all-gather 回完整序列。它服务的是 **MoE 的数据聚合**，与 attention 的 CP 组是两码事。

---

## 5. padding 语义

### 5.1 为什么必须 pad

DP attention 下每个 rank 的 token 数 = 本 rank 请求的真实长度和，各 rank **天然不均**。而 MoE 前的全局 gather 依赖两类集合通信，它们都要求**每个 rank 贡献等长的数据块**：

- `all_gather_into_tensor`：输出 = 各 rank 块的顺序拼接，块长必须一致；
- CUDA Graph：捕获的计算图形状静态，pad 到固定长度才能复用（§9）；
- symmetric memory（NVLink 零拷贝通信）：要求各 rank 缓冲**对称分配**（同形状、注册窗口对齐）——这正是 `is_allocation_symmetric`（L318–319）的判据：`not dp_attention_enabled or is_dp_max_padding()`，且被 `topk.py` L98 反向 import 用于决定 topk 输出能否走对称内存（topk.py L443–445/L496–498）。

所以"pad 到 max len"不是浪费，而是**为 all-gather/静态图/对称内存三种优化一次性付费**。

### 5.2 DpPaddingMode 的成本模型（L53–95）

两种模式（L55–59）：

- **MAX_LEN**：各 rank pad 到 `max(global_num_tokens)`，用 `all_gather_into_tensor` 拼接——通信量 ∝ `max_len × dp_size`（全局缓冲大小）；
- **SUM_LEN**：不 pad，各 rank 写进长度 `sum(global_num_tokens)` 的零缓冲中自己的偏移段，用 `all_reduce` 求和——通信量 ∝ `2 × sum_len`（all_reduce 近似两倍数据搬运）。

`get_dp_padding_mode`（L66–86）的决策：

```python
if is_extend_in_batch and dp_size > 1:      # L76–77
    return DpPaddingMode.SUM_LEN            # extend 阶段长度差异大，宁可用 all_reduce
max_len = max(global_num_tokens)
sum_len = sum(global_num_tokens)
if sum_len * 2 >= max_len * dp_size:        # L83
    return cls.MAX_LEN                      # MAX_LEN 更便宜（或持平）
else:
    return cls.SUM_LEN
```

两条经验规则藏在注释里：

- L72–75：extend（prefill）批次天然倾斜，直接选 SUM_LEN 省掉 pad 开销；但 **dp_size=1 时 max_len==sum_len**，反而固定选 MAX_LEN——为了让 symmetric memory 生效（DSA CP 等特性依赖它，L75 注释）；
- L79–80：**成本打平时优先 MAX_LEN**（"prefer MAX_LEN when communication cost is equal to enable symmetric memory"）——把通信加速器的收益折进了决策。

**数值感受一下成本差**：设 dp=4、各 rank token 数 `[1000, 100, 100, 100]`（一条长请求 + 三条短请求）：

- MAX_LEN 通信量 ∝ `max_len × dp_size = 1000×4 = 4000`（且浪费 2700 个 pad 槽位的计算）；
- SUM_LEN 通信量 ∝ `2 × sum_len = 2×1300 = 2600`；
- 判据 `sum_len×2=2600 >= max_len×dp=4000`？否 → 选 SUM_LEN ✓。

反过来若分布是 `[400, 300, 200, 100]`：`2×1000=2000 >= 400×4=1600` → 是 → 选 MAX_LEN。可见 **MAX_LEN 只在分布较均匀时胜出**，这正是 L76–77 对 extend 批次直接判 SUM_LEN 的直觉依据。

`get_default_mode_in_cuda_graph`（L88–95）是 ROCm 7.0.0a 的 NCCL bug 规避（环境变量 `SGLANG_USE_ROCM700A` 时图内强制 SUM_LEN，L90–93 注释），正常情况图内默认 MAX_LEN——静态形状 + 对称内存双收益。

### 5.3 pad 的两种"布局"

- **MAX_LEN pack 布局**：全局缓冲第 r 段起始 = `r × max_len`（每 rank 等长段）；
- **SUM_LEN pack 布局**：第 r 段起始 = `sum(global_num_tokens[:r])`（紧凑拼接），由 `get_dp_local_info`（L387–402）用 `torch.cumsum(global_num_tokens_gpu)` 算出并**缓存在 forward_batch** 上（L399–400，避免每层重复 cumsum）；
- **CUDA Graph rank-padded 布局**：第 r 段起始 = `r × cuda_graph_batch`（§9）。

三种布局的切换全部集中在 `get_dp_local_info` / `get_dp_local_slice_cpu` 两个小函数里，是读 scatter 代码前必须先钉死的坐标系。

---

## 6. gather 缓冲元数据中心

`_DpGatheredBufferWrapper`（L98–182）是一个**纯类属性容器**（无实例，全 classmethod）——模块级单例的 class 化写法，好处是可集中 `set_metadata` / `set_dp_buffer_len` 并保持类型注解（L100–107）。

职责三件事：

1. **元数据**：hidden_size/dtype/device 在 `initialize_dp_attention` 时设置一次（L110–113）；
2. **每步缓冲长度**：`set_dp_buffer_len(global_len, local_len, dp_max_padding, global_num_tokens)`（L115–126）由 scheduler/forward 每步刷新——调度器算完本步各 rank token 数后调用，之后模型各层通过 `get_global_dp_buffer_len()`（L204–209）取全局缓冲长度分配张量；
3. **缓冲分配**：`get_global_dp_buffer/get_local_dp_buffer`（L128–146）在 `use_symmetric_memory(group, disabled=not dp_max_padding)` 上下文里 `torch.empty`——**MAX_LEN pad 时才启用对称内存**，SUM_LEN 下各 rank 长度不齐无法对称注册（L130/L140 的 disabled 参数）。

L185–237 是对 wrapper 的模块级函数转发（`set_dp_buffer_len` / `get_global_dp_buffer` / ... 共 13 个），纯粹为了给外部一个稳定的过程式 API、隐藏 wrapper 存在——这是本文件明显的"两层 API"风格。

---

## 7. gather/scatter 通信原语

### 7.1 入口与分流（L518–547）

```python
def _dp_gather(global_tokens, local_tokens, forward_batch, is_partial):
    if forward_batch.dp_padding_mode.is_max_len():
        _dp_gather_via_all_gather(...)
    else:
        _dp_gather_via_all_reduce(...)
```

两个公开包装：`dp_gather_partial`（L534–539，`is_partial=True`）与 `dp_gather_replicate`（L542–547，`is_partial=False`）。**is_partial 的语义是注意力输出的冗余状态**：

- **partial**：attention 输出在 attn-TP 组内是**部分和**（row-parallel 之后尚未 all-reduce），每个 attn-tp rank 都持有一份不同的部分值——gather 时大家的贡献要**相加**；
- **replicate**：输出已在 attn-TP 组内 all-reduce 过，各 attn-tp rank 值相同——gather 时**只能让一个 rank 写**，否则重复相加会放大错误。

### 7.2 _dp_gather_via_all_reduce（L463–495，SUM_LEN 路径）

四步：

1. 取本 rank 的 `(local_start_pos, local_num_tokens)`（L469）；
2. `global_tokens.fill_(0)` 清零（L471）——all_reduce 是加法语义，目标缓冲必须先归零；
3. 条件写入本 rank 段（L475–482）：`is_partial or get_attention_tp_rank() == 0` 时才 memcpy——直接体现 §7.1 的语义；`memcpy_triton`（L452–460）是手写 triton 拷贝 kernel（L422–445），BLOCK_SIZE=8192 分块、int64 偏移防溢出。两个 assert（L476–478）禁止 src/dst 共享 storage（别名会导致写覆盖）；
4. 跨全 TP 组 all_reduce（L484–495）：**非浮点（如 int32 input_ids）且 tp_size≤8（单机）走 `inplace_all_reduce`**——注释 L484 点明这是为了 custom all reduce（one-shot 算子对 int 支持更好）；否则标准 `tensor_model_parallel_all_reduce`。

### 7.3 _dp_gather_via_all_gather（L498–515，MAX_LEN 路径）

比 all_reduce 版多一层结构，因为它要同时完成"attn-TP 求和 + DP 拼接"两个目标：

```python
if get_attention_tp_size() == 1:                     # L504–506
    get_tp_group().all_gather_into_tensor(global_tokens, local_tokens)
    return                                          # 无 attn-TP，一步到位
if not is_partial:
    if get_attention_tp_rank() != 0:
        local_tokens.fill_(0)                        # L508–510 replicate 清零防重复
scattered = local_tokens.tensor_split(get_attention_tp_size())[get_attention_tp_rank()]
get_attention_tp_group().reduce_scatter_tensor(scattered, local_tokens)  # L514
get_tp_group().all_gather_into_tensor(global_tokens, scattered)          # L515
```

通信结构是 **reduce-scatter(attn-TP) → all-gather(全 TP)**：

- reduce-scatter 在 attn-TP 组内把 partial 和**以及** replicate 的清零策略统一处理（sum 语义下非 0 rank 写 0 等价于只留 rank 0 的值），并把结果散射到等长块——**这一步同时完成了"求和"与"pad 到 max_len 块"**；
- all-gather 沿全 TP 组（= 所有 DP rank × attn-tp）把各 rank 的块拼成全局缓冲。

这就是 MAX_LEN 模式必须 pad 的根本原因：`tensor_split(attn_tp_size)` 与 `all_gather_into_tensor` 都假设**等长块**。两步总通信量 ≈ 全局缓冲的 1.5 倍，通常优于 all_reduce 的 2 倍，且能吃 symmetric memory。

**形状流转图**（沿用 §3 的 8 卡 dp=4、attn_tp=2 例子，设 max_len=L、hidden=H，gather 后全局缓冲 4L×H）：

```
                rank 2 (DP1, attn_tp0)            rank 3 (DP1, attn_tp1)
  partial:   local_tokens (L,H) 部分和①      local_tokens (L,H) 部分和②
                         │                            │
                         └──────── reduce-scatter(attn-TP 组 {2,3}) ────────┘
                                        │  (①+② 求和后散射到等长两半)
                                        ▼
                        scattered (L/2, H)   ← 每个 attn-tp rank 持有一半
                                        │
                                        │ all-gather(全 TP 组 {0..7})
                                        ▼
                global_tokens (4L, H)：[DP0 段 | DP1 段 | DP2 段 | DP3 段]
                                        │
                                     MoE (EP)
```

replicate 模式只有一处不同：非 rank0 先 `fill_(0)`（L508–510），后续 sum 语义自动"只留 rank 0 的真值"。

### 7.4 dp_scatter（L550–569）

MoE 之后的逆操作：`local_tokens.fill_(0)`（L559，CUDA Graph 下缓冲必须保持确定性）→ 从全局缓冲把本 rank 段 memcpy 出来（L567–569，`offset_src=True` 表示偏移作用在源端）。docstring（L555–556）提醒：`local_num_tokens` ≠ `local_tokens.shape[0]`（后者可能是图 padding 过的），拷贝长度必须用前者。

### 7.5 memcpy_triton：为什么要手写拷贝 kernel（L422–460）

gather/scatter 的数据搬运不是 `tensor.copy_` 或切片赋值，而是手写 triton kernel（L422–445），三个理由藏在参数里：

1. **偏移在 GPU 张量上**：`offset_ptr/sz_ptr` 是 device 张量（`local_start_pos` 来自 GPU cumsum，L392–397）——若用 torch 切片 `global[start:start+n]`，索引必须是 Python int/slice，会强制 D2H 同步，击穿 CUDA Graph（§9）；triton kernel 里 `tl.load(offset_ptr)`（L433）在 device 上读偏移，全程零同步；
2. **int64 截距防护**：`pid.to(tl.int64)` 与 `offset.to(tl.int64)`（L432–434）——全局缓冲可达数十万 token × hidden 数千，int32 乘积会溢出；
3. **双向复用**：`offset_src: tl.constexpr`（L439）编译期分派"偏移在源端（scatter，L444–445）还是在目标端（gather，L441–442）"，一个 kernel 服务两个方向。`chunk_size = prod(src.shape[1:])`（L456）把 (N, H) 展平成一维按元素块拷贝，`BLOCK_SIZE=8192`（L457）配合 `mask` 处理非整块尾部。

### 7.6 通信原语总表

| 函数 | 行号 | 方向 | 语义 |
|---|---|---|---|
| `dp_gather_partial` | L534 | local→global | partial 和聚合（MoE 前，attn 输出未 reduce） |
| `dp_gather_replicate` | L542 | local→global | replicate 聚合（如 input_ids 嵌入） |
| `dp_scatter` | L550 | global→local | MoE 后取回本 rank 段 |
| `dp_reduce_scatter_tensor` | L572 | global→local | MoE TP 输出的 reduce-scatter（§8） |

---

## 8. MoE 侧通信包装

- **`dp_reduce_scatter_tensor`**（L572–580）：MoE（TP 或 EP）算完后全局缓冲是 TP 部分和，需要 reduce 回各 DP rank。两分支：`tp_size == attn_dp_size`（即 attn_tp_size=1）时全 TP 组一步 reduce-scatter；否则先全 TP 组 reduce-scatter 到 1/attn_tp_size 大小的段，再沿 attn-TP 组 all-gather 恢复各 attn-tp rank 的副本（L576–580）——与 §7.3 的两步结构互为镜像；
- **attn 组包装**（L583–600）：`attn_tp_reduce_scatter_tensor` / `attn_tp_all_reduce` / `attn_tp_all_gather_into_tensor` / `attn_cp_reduce_scatter_tensor` / `attn_cp_all_gather_into_tensor`，把"本次通信只应发生在我的 attention TP/CP 伙伴间"显式化，防止模型代码误用全 TP 组；
- **moe_cp 家族**（L603–625）：`get_moe_cp_group/rank/size` + `moe_cp_all_gather_into_tensor`——`is_enable_moe_cp_allgather()`（L616–621）为 True（`attn_cp_size > moe_dp_size`）时，MoE 前沿 moe_dp 组补一次 all-gather，把 CP 切片的序列还原成完整 token 流；
- `attn_tp_all_gather`（L628）：list 版 all-gather，DSA（原 NSA，见提交 8131641bc 的重命名）attention 的配置/元信息同步用。

---

## 9. CUDA Graph 适配

CUDA Graph 要求静态形状，DP attention 的应对：

1. **图内固定 MAX_LEN 模式**（§5.2，L88–95），pad 长度 = `cuda_graph_batch`（捕获时的桶大小）；
2. **rank-padded 布局**：`get_dp_local_slice_cpu`（L405–419）——图运行时本 rank 段起始 = `dp_rank × cuda_graph_batch`（L416），而非按真实 token cumsum。**返回 Python int**（L411 注释强调 no D2H sync）——图内任何 GPU→CPU 同步都会破坏捕获；
3. **零填充保持确定性**：`dp_scatter` 的 `fill_(0)`（L559）保证图回放时缓冲内容与捕获时一致；
4. `get_dp_local_info`（L387–402）把 cumsum 结果缓存进 `forward_batch.dp_local_start_pos`（L399–400）——同一 forward 的几十个 MoE 层共享一次计算，且 `global_num_tokens_gpu` 是 GPU 张量、cumsum 在 device 上完成（避免逐层同步）。

---

## 10. `_RUN_DP_CTX` 考据

**本 commit（ec075d8bc）不存在 `_RUN_DP_CTX`**——全仓 grep 无匹配，`git log -S` 在可达历史中亦无痕迹。它是 SGLang 早期版本（2025 年 v0.4.x 时代）的设计：模块级布尔 `_RUN_DP_CTX` + `run_dp_attention` contextmanager，在前向进入"DP attention 段"时置位，退出时复位，供 `get_attention_tp_group()` 等**运行期动态**返回不同通信组。

现行架构用三个静态机制取代了它：

1. **`_ENABLE_DP_ATTENTION_FLAG`**（L47，初始化于 L285）+ 模块级 rank/size 全局量：启动时一次算清，运行期只读；
2. **parallel_state 的独立组注册**（`parallel_state.py` L1758+）：attn-TP/CP/MoE-DP 组在 `initialize_model_parallel` 阶段创建为独立对象，模型代码通过 `get_attention_tp_group()`（L322）等**静态查询**拿组，不再依赖"当前上下文在哪一段"；
3. **`is_allocation_symmetric()`**（L318–319）接过了原上下文标志的一个关键消费者：把"是否处于 DP attention 均匀 pad 状态"暴露给内存分配层（topk.py L98 反向 import，决定 topk 输出与 DP gather 缓冲的 symmetric memory 资格）。

唯一幸存的"运行期切换"是 `disable_dp_size`（L366–384）——服务于投机解码 draft 模型的特殊 TP 度，它就是旧上下文方案的微缩遗迹。若你读到引用 `_RUN_DP_CTX` 的旧文章/旧代码，对应到本版本时应映射为"`initialize_dp_attention` 静态初始化 + parallel_state 组注册"。

---

## 11. 与 MoE EP 的配合

DeepSeek V3 的经典部署命令 `python -m sglang.launch_server --enable-dp-attention --tp-size 8 --ep-size 8`（SGLang DeepSeek 官方文档的 DP+EP 配置）在本文件视角下逐层走读：

**初始化期**：`dp_size=8` → `attn_dp_size=8`、`attn_tp_size=8//8=1`（L243–245）。每个 GPU 即一个 DP rank，attention 单卡跑全量头；`initialize_model_parallel` 同时注册 EP=8 的专家组。

**每层前向**（模型侧代码如 `deepseek_v2.py` 调用本文件原语）：

1. **attention（DP）**：各 rank 只算自己请求的 attention，零集合通信；输出在 attn_tp_size=1 下天然完整（无 partial 问题）；
2. **`dp_gather_partial/replicate`**（L534/L542）：8 个 rank 的 token 拼成全局 batch。MAX_LEN 模式下走 reduce-scatter+all-gather（L498–515；attn_tp_size=1 时一步 all-gather，L504–506）；
3. **TopK 路由**：`topk.py` 在全局 batch 上选专家，输出缓冲因 `is_allocation_symmetric()`（topk.py L443–445）可能走对称内存；EPLB/DeepEP 的重映射把 token 指到 8 个 EP rank；
4. **MoE（EP）**：全局 token 流入 8 个 rank 的本地专家——**EP 的负载均衡恰好受益于全局 batch**（每专家见的 token ×8），这是 DP attention 与 EP 的共生关系；
5. **`dp_scatter`**（L550）：各 rank 从全局缓冲取回自己的 token 段，进入下一层 attention。

**收益账**：attention 省掉 TP all-reduce（每层 2 次），代价是 gather/scatter（每层 2 次，且 gather 的量 = 全局 batch）。长序列、attention 占比高的场景净赚；token 分布倾斜时 SUM_LEN 模式（§5.2）控制浪费。

**CP 变体**：`--attn-cp-size N` 启用 ring/DSA context parallel 后，`moe_cp_*` 家族（L603–625）负责 MoE 前把 CP 切片聚合回完整序列（`is_enable_moe_cp_allgather` L616–621 的判据 `attn_cp_size > moe_dp_size`），attn CP 组（L334–343）承载 ring 通信——组体系在 §4 表格中的三层（attn-TP/CP、MoE-DP）正是为这类组合爆炸预留的坐标。

---

## 12. 与其他模块的交互

| 模块 | 交互点 | 行号 |
|---|---|---|
| `srt/distributed/parallel_state.py` | 组的创建方；本文件是查询门面（`get_attn_tp_group`/`get_attn_cp_group`/`get_moe_dp_group`） | L13–28, L603–605 |
| `srt/distributed/device_communicators/pynccl_allocator` | `use_symmetric_memory`：gather 缓冲与 scatter 的对称内存 | L29–31, L130, L140 |
| `layers/communicator.py` | 本文件原语的最大消费者：层间 scatter/gather 编排 | — |
| `layers/moe/topk.py` | 反向 import `is_allocation_symmetric` 决定 topk 输出缓冲内存策略 | topk.py L98/443 |
| `models/deepseek_v4(_nextn).py` | 直接调用 `dp_gather/dp_scatter` 的模型实现 | — |
| `model_executor/forward_batch_info.py` | `dp_padding_mode` / `global_num_tokens_gpu` / 缓存字段 `dp_local_start_pos` | L387–402 |
| `managers/scheduler.py` + cuda_graph_runner | 每步 `set_dp_buffer_len` 刷新缓冲长度；图捕获用 `get_dp_local_slice_cpu` | L185–193, L405–419 |
| `server_args` | `enable_dp_attention/dp_size/moe_dense_tp_size/attn_cp_size/moe_dp_size` 配置源 | L280–283, L618–621 |

---

## 13. 关键设计决策

1. **MAX_LEN/SUM_LEN 双模式 + 显式成本模型**（L76–86）：把"pad 浪费 vs all_reduce 通信量"折算成可比代价（`2×sum_len` vs `max_len×dp_size`），打平优先 MAX_LEN 以换 symmetric memory 与静态图——性能决策不靠拍脑袋，且 extend 与 decode 的负载差异被 `is_extend_in_batch` 分支显式建模。
2. **reduce-scatter+all-gather 的两段式 gather**（L498–515）：用等长块的 reduce-scatter 同时完成"attn-TP 部分和归约"与"pad 到均匀块"，再 all-gather 拼全局——一次结构解决两个并行度的问题，避免了先 all-reduce 再单独 pad 的冗余拷贝。
3. **元数据与缓冲分离的 `_DpGatheredBufferWrapper`**（L98–182）：类属性单例集中管理每步变化的缓冲长度，配一层模块级函数门面（L185–237）——scheduler 算一次、几十个 MoE 层共享，cumsum 结果再缓存进 forward_batch（L399–400），把每步的记账成本压到一次。
4. **静态初始化取代运行期上下文标志**（§10）：`_RUN_DP_CTX` 式动态切换被启动期组注册 + 只读全局量取代，唯一例外（`disable_dp_size` L366–384）被限制在投机解码 draft 场景——分布式状态越静态，race 与误用越少。
5. **同步纪律：CPU 侧布局计算零 D2H**（L405–419）：图内的 rank-padded 起始偏移用 `global_num_tokens_cpu` 算 Python int，device 侧 cumsum 走 GPU 张量——任何一处隐式同步都会击穿 CUDA Graph 捕获，这是 DP attention 与图兼容的隐形契约。

---

## 14. 阅读建议

1. **先读 §3 rank 代数再读一切**：拿 8 卡、dp=4、tp=8 手排一遍 L240–254 的公式，写出 8 个 rank 的 (attn_dp, attn_tp) 坐标——后面所有 gather/scatter 的 `tensor_split`/偏移都建立在这张坐标表上，排不出来就必然读不懂 §7。
2. **用两个极端 case 验证通信原语**：① attn_tp_size=1（DeepSeek DP+EP 配置）：`_dp_gather_via_all_gather` 走 L504–506 快路径，一步 all-gather；② attn_tp_size=2 且 partial：走 L508–515 两步，对照画张量形状变化图（local (L,H) → scattered (L/2,H) → global (4L,H)）。两例吃透，任何组合都是插值。
3. **追踪 `dp_padding_mode` 的一生**：在 `forward_batch_info.py` 里找它的赋值处（scheduler 依据本步 token 分布调用 L66–86 的决策），再看它在 L518–531 如何分流通信路径、在 L318–319 如何影响 symmetric memory——它是本文件所有机制的"状态变量"，串起来就是调度器↔通信层的完整接口。
4. **对照 topk.py 篇读 §10–11**：`is_allocation_symmetric` 是两文件的唯一 import 交汇（topk.py L98），从它出发看"DP attention 的 pad 模式如何决定 MoE 路由输出的内存属性"，能体会 SGLang 中 attention 并行与 MoE 并行的耦合深度。
5. **实测观察**：起一个 2 卡 DP attention 服务（`--enable-dp-attention --tp 2 --dp 2`），用不同长度请求打流量，开 `SGLANG_LOG_LEVEL=debug` 观察 gather 缓冲长度变化；再对比 `--enable-dp-attention` 开关前后的 torch profiler trace，找到 reduce-scatter+all-gather 的位置——通信结构从抽象符号变成时间线上的两个 kernel 后，§7 的每个 assert 都会变得具体。
