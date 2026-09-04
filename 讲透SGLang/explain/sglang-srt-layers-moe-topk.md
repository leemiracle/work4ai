# 深度解析：`python/sglang/srt/layers/moe/topk.py`

> 源码: `python/sglang/srt/layers/moe/topk.py` @ commit `ec075d8bc`（全文 1606 行）

本文是 SGLang MoE 路由层的核心解析。该文件实现了 MoE（Mixture of Experts）的 **Top-K 门控路由全家族**：从最朴素的 softmax/sigmoid TopK，到 DeepSeek 系的 grouped TopK 与 biased grouped TopK，再到 Kimi K2 专用路径与多家硬件（CUDA/ROCm/CPU/NPU/XPU/MUSA）的 kernel 分发。它同时承担三项"路由后处理"职责：EPLB 专家位置重映射（logical→physical）、DeepEP 交错布局重映射、以及 shared experts 融合列的追加。最终产出统一的 `topk_weights` / `topk_ids` 张量，供下游 `fused_moe` triton kernel（或其他 MoE runner backend）按专家分组执行 GEMM。整个文件是"模型路由语义"与"底层通信/ kernel 资源"之间的契约层。

---

## 目录

1. [全景：文件结构与三层架构](#1-全景)
2. [输出协议体系：TopKOutput 三形态](#2-输出协议体系)
3. [TopKConfig 与 TopK 主类：MultiPlatformOp 多平台分发](#3-topk-主类)
4. [select_experts：路由家族选择总决策树](#4-select_experts-决策树)
5. [标准 TopK 家族逐个拆解](#5-标准-topk-家族)
6. [grouped_topk 与 biased_grouped_topk：DeepSeek 路由双雄](#6-grouped-topk-双雄)
7. [biased_grouped_topk_gpu：六层 kernel 阶梯](#7-六层-kernel-阶梯)
8. [renormalize 与 routed_scaling_factor 语义](#8-renormalize-与-scaling)
9. [Shared Experts 融合：topk 列追加语义](#9-shared-experts-融合)
10. [EPLB 专家位置重映射](#10-eplb-专家位置重映射)
11. [DeepEP 交错布局重映射与 waterfill](#11-deepep-重映射与-waterfill)
12. [topk_ids / topk_weights 输出语义规范](#12-输出语义规范)
13. [与 fused_moe triton kernel 的衔接](#13-与-fused_moe-的衔接)
14. [Noisy Router 考据（本版本不含）](#14-noisy-router-考据)
15. [与其他模块的交互](#15-与其他模块的交互)
16. [关键设计决策](#16-关键设计决策)
17. [阅读建议](#17-阅读建议)

---

## 1. 全景

文件按注释分隔线自上而下分为四大块：

| 行区间 | 内容 |
|---|---|
| L34–193 | **可选 kernel 导入区**：`triton_kernels`（`routing()` 函数 L39–77）、`sgl_kernel`（`moe_fused_gate` L132、`topk_softmax` L175、`topk_sigmoid` L178）、flashinfer（`fused_topk_deepseek` L135–167）、`kimi_k2_moe_fused_gate`（L170）、aiter/ROCm（L181–186）、musa（L187–193）。全部用 try/except 包裹，缺失则优雅降级 |
| L195–301 | **配置与输出类型**：`TopKConfig`（L198–213）、`TopKOutputFormat` 枚举（L236–239）、`TopKOutput` Protocol（L242–249）及三个实现 |
| L305–539 | **TopK 主类**（`MultiPlatformOp` 子类），按平台分发到 `forward_cuda/cpu/npu/xpu` |
| L542–1606 | **实现层**：十几个自由函数（各路由算法的 native/torch/专用 kernel 版本）、平台别名绑定（L1265–1273）、后处理 `_post_process_topk_ids`（L1323–1395）、总入口 `select_experts`（L1398–1560）、torch.compile fake 注册（L1563–1606） |

三层架构清晰：**TopK 类（配置+平台分发）→ select_experts（算法决策树）→ 各 *_impl / kernel 函数（具体计算）**。

值得注意的第一处细节：L98 直接 `from sglang.srt.layers.dp_attention import is_allocation_symmetric`——TopK 模块反向依赖 DP Attention 模块，用于决定 `topk_weights`/`topk_ids` 输出缓冲是否可分配为 symmetric memory（详见 §13），这是 MoE 与 DP Attention 两条线在代码里的显式交汇点。

---

## 2. 输出协议体系

### 2.1 为什么需要三种输出格式

不同 MoE runner backend 对路由结果的消费方式不同：

- **Triton fused_moe / DeepEP / cutlass** 等：需要显式的 `topk_weights` + `topk_ids` 张量（"我告诉你每个 token 选了哪些专家、权重多少"）；
- **triton_kernels（matmul_ogs）**：路由被进一步物化为 ragged tensor 元数据 + gather/scatter 索引，供其特有的 grouped GEMM 直接消费；
- **flashinfer trtllm / mxfp4**：路由在 MoE kernel 内部完成，TopK 层只需"透传"原始 logits。

因此 L236–239 定义 `TopKOutputFormat` 三值枚举，L242–249 用 `runtime_checkable Protocol` 约束共同接口 `format` 属性。

### 2.2 StandardTopKOutput（L252–261）

```python
class StandardTopKOutput(NamedTuple):
    topk_weights: torch.Tensor   # (num_tokens, top_k) float32
    topk_ids: torch.Tensor       # (num_tokens, top_k) int32
    router_logits: torch.Tensor  # (num_tokens, num_experts) 变换后的 logits
```

三个字段的语义在 §12 详述。注意 `router_logits` 返回的是**经过 EPLB 输入变换之后**的 logits（见 §10），而非模型原始输出——下游某些 kernel（如 DeepEP 的 dispatch 权重计算）还会再用到它。

### 2.3 TritonKernelTopKOutput（L264–273）

直接封装 `triton_kernels.matmul_ogs` 的 `RoutingData / GatherIndx / ScatterIndx` 三件套。这些对象由 L39–77 的 `routing()` 函数构造：先可选 softmax（`sm_first`，L52–53），再调 `triton_kernels_topk`（L55–61），从结果的 `mask_metadata` 提取 row/col 排序索引并构造 ragged 元数据（L62–76）。这是 MoE 论文里 "expert-parallel token permutation" 的完全物化形式。注意 L47–50：triton_kernels 3.6.0 不支持 `simulated_ep`。

### 2.4 BypassedTopKOutput（L276–299）

一个"惰性包"：只装 `hidden_states`、`router_logits`、`topk_config` 等原料，不做任何计算。当某个 backend（flashinfer_trtllm、flashinfer_mxfp4 的部分路径，见 L418–421）自己做路由时，TopK 层返回它直接跳过。关键是 `to_standard()` 方法（L289–299）：需要显式路由张量的 kernel 可以在后续任意时刻调用它，内部递归调用 `select_experts` 把路由"物化"出来——**惰性求值模式**，避免双重计算。

### 2.5 TopKOutputChecker（L219–233）

三个静态方法 + `TypeGuard`，让下游代码（如 `moe_runner`）能用 `if TopKOutputChecker.format_is_standard(x):` 的形式在 type checker 眼皮底下安全 narrowing。这是纯类型工程，零运行时开销。

---

## 3. TopK 主类

### 3.1 构造参数与 TopKConfig（L198–213, L314–373）

`TopK.__init__` 接收的参数基本一一对应 `TopKConfig` 字段：

- `top_k`：**含 fused shared experts 的总选择数**（docstring L308 明确说 "including the fused shared expert(s)"）；
- `use_grouped_topk / topk_group / num_expert_group`：DeepSeek 式分组路由三件套，L338–339 断言后两者必须同时给出；
- `renormalize`：选完后是否对权重归一化（默认 True）；
- `correction_bias`：DeepSeek e_score_correction_bias，推理时参与**选择**但不参与**计分**（见 §6.2）；
- `routed_scaling_factor` / `apply_routed_scaling_factor_on_output`：DeepSeek 输出缩放的两种施加方式（§8）；
- `num_fused_shared_experts`：融合共享专家数（§9）；
- `custom_routing_function`：模型自带路由函数的逃生口（如 DBRX）；
- `scoring_func`：`"softmax"` / `"sigmoid"` / `"sqrtsoftplus"` 三种打分函数。

注意 L334–335 的注释：`scoring_func` 当前未真正用于所有路径，保留是为了未来扩展（链接 PR #4505）。

### 3.2 DeepEP waterfill 预处理（L344–354, L375–385）

若启用 `enable_deepep_waterfill` 且有 fused shared experts，构造期做一个关键改写（L352–354）：`top_k -= num_fused_shared_experts`、`num_fused_shared_experts = 0`、强制 `output_format = STANDARD`——即 waterfill 模式下**放弃 shared experts 融合**，由 `deepep_waterfill_balancer`（由 ModelRunner 注入，L378–381 断言必须先 prepare）在 `expand_topk`（L385）中事后扩展 topk 列。TODO 注释（L351）表明共享专家融合与 routed TopK 融合的耦合是已知的待重构债。

### 3.3 forward_cuda 的输出格式决策（L406–454）

```python
if self.topk_config.output_format is not None:      # 显式指定优先
    output_format = self.topk_config.output_format
elif get_moe_runner_backend().is_triton_kernels():  # backend 推断
    output_format = TopKOutputFormat.TRITON_KERNEL
elif ... is_flashinfer_trtllm() or (is_flashinfer_mxfp4() and not self.is_fp4_experts):
    output_format = TopKOutputFormat.BYPASSED
else:
    output_format = TopKOutputFormat.STANDARD
```

三分支后各走各路：TRITON_KERNEL → `routing()`（L425–432，注意 `sm_first=not renormalize` 的等价改写，L426 注释）；BYPASSED → 打包 `BypassedTopKOutput`（L433–440）；STANDARD → 进入 `select_experts`，但包在一层 **symmetric memory 上下文**里（L443–445）：

```python
with use_symmetric_memory(get_tp_group(), disabled=not is_allocation_symmetric()):
    topk_output = select_experts(...)
```

这是因为 `topk_weights`/`topk_ids` 会被 TP 组内的 NCCL 集合通信消费（DeepEP dispatch 等），对称内存可以让通信走 NVLink 零拷贝；但 DP attention 非均匀 pad 时缓冲不对称，必须禁用（`is_allocation_symmetric` 语义见 dp_attention 篇 §7）。

### 3.4 其他平台 forward

- `forward_native`（L387–404）：置 `torch_native=True` 走纯 torch 实现，用于正确性对照与无 kernel 环境；
- `forward_cpu`（L456–472）：与 native 相同入口（内部由 L1265–1273 的别名绑定决定具体函数）；
- `forward_npu`（L474–492）：转投 `fused_topk_npu`；
- `forward_xpu`（L516–539）：能力探测式降级——仅当 `top_k <= 8 且 experts <= 256`（L528–530）才用 `topk_softmax/topk_sigmoid` kernel，否则 torch native；
- `empty_topk_output`（L494–514）：为 CUDA Graph 空批次准备的零行输出工厂，注意 L504–513 对 DeepEP + fused shared experts 的形状补偿（topk 列额外加 n）。

---

## 4. select_experts 决策树

`select_experts`（L1398–1560）是所有路由的**总入口**，决策顺序如下：

```
select_experts(hidden_states, router_logits, topk_config)
│
├─ ① EPLB 输入变换（L1423–1430）
│     router_logits, correction_bias = transform_select_experts_inputs(...)
│     （重排 logits 列到物理专家布局，见 §10）
│
├─ ② use_grouped_topk?
│   ├─ 无 correction_bias → grouped_topk（L1439–1449）      # DeepSeek V2 朴素版
│   └─ 有 correction_bias → biased_grouped_topk（L1451–1462）# DeepSeek V3/R1
│
├─ ③ torch_native 且无 custom fn → fused_topk_native（L1463–1476）
│     （断言：不支持 num_token_non_padded / EPLB / output scaling，L1464–1468）
│
├─ ④ 无 custom fn，按 scoring_func 分流（L1477–1522）
│   ├─ "sqrtsoftplus" → biased_topk(_jit_kernel)_impl（L1481–1500）
│   │     * JIT 开关：envs.SGLANG_OPT_USE_JIT_KERNEL_FUSED_TOPK（L1484）
│   ├─ flashinfer_trtllm_routed + softmax + 无 bias
│   │     → fused_topk_softmax_torch_raw_logits（L1501–1512）# 对 raw logits topk
│   └─ 否则 → fused_topk（L1513–1522）                       # Qwen3MoE 等主流路径
│
├─ ⑤ custom_routing_function → 直接调用（L1523–1534）
│     （同样断言不支持 padding / EPLB / output scaling）
│
├─ ⑥ benchmark 专用：SGLANG_SIMULATE_UNIFORM_EXPERTS（L1536–1546）
│     覆盖为 round-robin 均匀路由，消灭 dummy 权重的专家倾斜
│
└─ ⑦ 统一后处理 _post_process_topk_ids（L1548–1556）
      + expert distribution recorder 钩子（L1558）
      → StandardTopKOutput（L1560）
```

三个反复出现的约束值得记住：**native 路径与 custom 路径都不支持 `num_token_non_padded`（DP attention 的 pad 语义）和 EPLB dispatch**——只有 fused kernel 路径（④的前两支）和 grouped 家族完整支持这两项生产特性。

另外注意 `_use_aiter` 下的参数微调：`topk=num_routed_topk if _use_aiter else top_k`（L1442/1455/1472 等）——aiter 的 kernel 自己会追加 shared experts 列，所以只传 routed 部分；CUDA kernel 则拿全量 top_k 并在 kernel 内/后处理时追加（§9）。

---

## 5. 标准 TopK 家族

### 5.1 fused_topk_torch_native（L545–583）

纯 torch 参考实现，两种模式：

- **有 correction_bias**（L561–568）：`scores = softmax/sigmoid(logits)`；**选择**用 `scores + bias`，**权重**取原始 `scores.gather` —— "bias 只影响选择、不影响打分"是 biased 路由的普适不变量；
- **无 bias**（L569–579）：直接 `torch.topk(scoring_func_impl(logits))`。

最后 `renormalize` 则按行归一（L581–582）。

### 5.2 fused_topk_softmax_torch_raw_logits（L586–602）

trtllm_routed 专用变体：**跳过整行 softmax**，直接对 raw logits 取 topk（L596），只对**被选中的 k 个 logits** 做 softmax（L598–600）。数学上等价（softmax 的 topk 集合不变，分母只差一个常数，且选中子集的 softmax = 全局 softmax 后再 renormalize），但计算量从 O(E) 降到 O(k)，还规避了大 E 下 softmax 的数值开销。这是与 trtllm Gen 决策树 kernel 行为对齐的必要条件。

### 5.3 fused_topk（L649–707）：kernel 版标准路径

按 `scoring_func` 二分：

- `"softmax"`：aiter（L667–677）或 `sgl_kernel.topk_softmax`（L679–684）；
- `"sigmoid"`：aiter+bias 走 `aiter_biased_grouped_topk`（L686–695，借 grouped 接口、`num_expert_group=1` 退化为普通 biased topk）；否则 `topk_sigmoid`（L697–703，原生支持 correction_bias 参数）。

输出预分配为 `(M, topk)` 的 float32 weights + int32 ids（L661–664）。这是 **Qwen3MoE / GLM-4.5 / Mistral 等大批模型**的默认路径（L1514 注释点名 Qwen3MOE）。

### 5.4 CPU 路径（L605–646）

`fused_topk_cpu`：无 bias 且 softmax 时走 C++ kernel `topk_softmax_cpu`（L627–632），否则回退 torch native（L617–625，注释点名 MiniMax 同时用 bias+sigmoid）。`apply_topk_weights_cpu`（L636–646）是 CPU MoE 的特殊两段式：权重先行乘到输入上、`topk_weights` 清 1，为的是让后续 `fused_experts_cpu` kernel 少一路索引。

---

## 6. grouped TopK 双雄

### 6.1 grouped_topk_gpu（L710–773）——DeepSeek V2 朴素分组路由

无 bias 版本，算法五步（与 DeepSeek V2 论文的 sigmoid+group 结构对应，但此处打分是 softmax，L725）：

1. `scores = softmax(gating_output)`（L725）；
2. **组代表分**：`group_scores = scores.view(n, n_group, -1).max(dim=-1)`（L728–730）——每组内最大专家分作为该组的代表；
3. **组选择**：`group_idx = topk(group_scores, k=topk_group)`（L731–733）——选出 topk_group 个组；
4. **掩码过滤**：组掩码扩展成专家掩码，组外专家分数置 0（L734–7741）；
5. **专家选择**：掩码后再 `torch.topk(tmp_scores, k=topk)`（L742–747）。

DeepSeek V3 的 256 专家 / 8 组 / topk_group=4 / topk=8 语义在此完全落地。整个函数被 `@torch.compile(dynamic=True)` 包裹（L711），mask+topk 这种访存密集模式恰好是 inductor 的甜点。

### 6.2 biased_grouped_topk_impl（L957–1027）——DeepSeek V3/R1 参考实现

与 6.1 的三点差异：

1. **打分 sigmoid**（L972）而非 softmax；
2. **组代表分不同**：`group_scores = (scores + bias).view(n, n_group, -1).topk(2).sum(-1)`（L976–980）——组内 **top-2 之和**而非 max。这是 DeepSeek V3 官方 `e_score_correction_bias` 路由的定义：bias 加法只发生在"选择链路"（组代表分 + 最终选择 L975/L994），**最终权重仍是原始 sigmoid 分**（L1000 `scores.gather`）；
3. 掩码填充值 `-inf`（L991–993）而非 0——sigmoid 分数恒正，0 无法扮演"排除"角色。

### 6.3 kimi_k2_biased_topk_impl（L802–837）

Kimi K2 的 `num_expert_group=1`（384 专家无分组）特化：直接 `sigmoid + bias → topk`（L824–827），省掉全部组掩码开销。docstring（L812–816）明确假设 `num_fused_shared_experts=0`。对应的专用 kernel 见 §7 第 5 档。

### 6.4 biased_topk_impl / biased_topk_jit_kernel_impl（L840–954）

无分组 biased 路由：支持 `sigmoid` 与 `sqrtsoftplus`（`softplus(x).sqrt()`，L858–859，豆包/ERNIE 类模型）两种打分。JIT 版本（L900–954）在 aiter+sqrtsoftplus 时走 `topk_gating`（L915–936），否则走 sglang 自家 JIT kernel `moe_fused_gate`（L938–950）。两者由 L1482–1486 的环境开关切换。

---

## 7. 六层 kernel 阶梯

`biased_grouped_topk_gpu`（L1057–1234）是全文件最"考古"的函数——一串 elif 按约束从快到慢逐档降级：

| 档 | 行号 | kernel | 触发约束 |
|---|---|---|---|
| 1 | L1078–1130 | flashinfer `fused_topk_deepseek` | CUDA + kernel 可用 + `is_power_of_two(num_experts)`（L1081）+ `topk_routed<=8`（L1083）+ `topk_group<=num_expert_group` 且 `topk_group*num_expert_group>=topk_routed`（L1084–1085）+ 组内专家≤32 且 `每组专家×topk_group≤128`（多组时，L1086–1090）或总专家≤384（单组时） |
| 2 | L1132–1149 | `sgl_kernel.moe_fused_gate` | CUDA + `experts_per_group<=32`（L1135，注释：kernel MAX_VPT=32）+ power of two |
| 3 | L1151–1170 | aiter `biased_grouped_topk` | ROCm + SGLANG_USE_AITER |
| 4 | L1171–1185 | musa `moe_fused_gate` | MUSA + 组内≤32 或单组 {160,256,384}（L1172–1174） |
| 5 | L1187–1221 | `kimi_k2_moe_fused_gate` / JIT `grouped_topk` | CUDA 特化：384 专家单组走 Kimi 专用 kernel（L1189–1197）；单组+topk_group=1+无融合共享专家+专家≤512+topk≤8 走 JIT（L1198–1221） |
| 6 | L1222–1234 | `biased_grouped_topk_impl` | 兜底 torch.compile 参考实现 |

几个精妙点：

- **档 1 的 shared experts 处理**（L1118–1128）：flashinfer 只算 routed 部分（`topk_routed = topk - num_fused_shared_experts`，L1077），出来后 `F.pad` 追加 shared 列（L1122–1123），shared 权重 = `sum(routed) / routed_scaling_factor`（L124–128）——与参考实现严格一致（L1119–1121 注释）。scaling_factor 参数的"内施/外施"换算在 L1100–1103：flashinfer 总是在内部乘 scaling，所以外部模式时传 1.0、输出模式时传真实值；
- **档 5 的 scaling 换算**（L1208–1212）：JIT kernel 同样内乘 scaling，`apply_routed_scaling_factor_on_output=False` 时强制传 1.0；
- **平台别名绑定**（L1265–1273）：CPU+AMX 可用时四个入口全绑 CPU kernel，否则绑 GPU/native 版本——模块加载时一次性决策，运行期零判断。

---

## 8. renormalize 与 scaling

**renormalize**（默认 True）：选中 k 个专家后权重归一 `w / w.sum()`。出现在所有 impl 的尾部（如 L761–767、L830–834、L1015–1021），规律一致：

- 有 fused shared experts 时，**归一化分母只含 routed 列**（`topk_weights[:, :-1].sum()`，L765/890/1019），shared 列的权重单独由公式生成（§9）；
- **renormalize=False 仅在 sigmoid 打分家族合法**（sigmoid 分数有界、天然可比；softmax 分数不归一则整体尺度飘）。

**routed_scaling_factor** 的两种施加位置：

- `apply_routed_scaling_factor_on_output=False`（默认，DeepSeek V3 训练即如此）：归一化后**不再乘** scaling，输出纯归一权重，由 MoE 输出端统一乘 `routed_scaling_factor`；
- `=True`：归一化后直接 `topk_weights *= routed_scaling_factor`（L768–769/833–834/1022–1023），MoE 输出端不再补乘。

两种模式不能共存，L1478–1479 对非 sqrtsoftplus 路径断言 `not apply_routed_scaling_factor_on_output`——因为 fused kernel 路径的输出端补乘逻辑写死在 runner 里。

---

## 9. Shared Experts 融合

DeepSeek V3 的 shared expert（每 token 必激活）可以不单独算，而是**当作第 k+1 个"伪专家"塞进 topk_ids 尾列**，与 routed experts 在同一个 fused kernel 里计算。语义约定：

1. **ID 段**：shared experts 占 `[num_experts, num_experts + num_fused_shared_experts)` 的 ID 空间。torch 路径用 `torch.randint` 随机填一个 shared 槽位（L749–755/874–880/1003–1009，随机是为了多副本 shared expert 的负载分摊）；flashinfer 路径固定 pad `value=num_experts`（L1122）；aiter 路径在 `_post_process_topk_ids` 里由 `fused_append_shared_experts` 统一追加（L1358–1377，base id = N，L1376）；
2. **权重公式**：`w_shared = sum(routed_weights未归一) / routed_scaling_factor`（L756–759/881–884/1110–1113）。数学动机：DeepSeek 输出为 `routed_scaling * Σ routed + shared`，把输出端统一乘上 `routed_scaling` 后，shared 列需贡献 1.0×shared，即 `w_shared = 1/routed_scaling × (归一化后Σrouted=1)`；
3. **sorted 标志**：有 fused shared experts 时 topk 必须 `sorted=True`（L746/869/998）——保证最高分在首列、**尾列腾给 shared**，`[:, -1]` 的覆盖才安全。

---

## 10. EPLB 专家位置重映射

EPLB（Expert Parallelism Load Balancer）运行时会**复制热点专家、迁移专家位置**，于是产生 logical expert id（模型权重的原始编号）与 physical expert id（EP rank 上的实际槽位）两套坐标系。本文件中重映射发生在**两个位置**：

### 10.1 输入侧：transform_select_experts_inputs（L1423–1430）

`select_experts` 入口处，把 `router_logits` 的**列**（和 `correction_bias`）按当前层的 logical→physical 映射重排。此后一切选择都发生在物理坐标系——好处是 kernel 无需感知 EPLB 存在。

### 10.2 输出侧：topk_ids_logical_to_physical（L1052）

`_biased_grouped_topk_postprocess`（L1048–1054）对输出 `topk_ids` 再做一次 logical→physical 查表，紧随其后调用 `_mask_topk_ids_padded_region`（L1034–1045）：DP attention 的 pad 区（行号 ≥ `num_token_non_padded` 的 token 行）的 ids 整行置 **-1**（CUDA int32 走 `mask_topk_ids` JIT kernel L1042，否则 torch 版 L1044–1045）。-1 语义见 §12——下游 kernel 一票否决 pad 行，防止幽灵 token 参与专家计算与通信。

两处合起来的完整链路在 `_post_process_topk_ids`（L1323–1395）：

1. routed 专家捕获钩子（L1336–1340，`get_global_experts_capturer`，服务 constrained generation 的专家约束）；
2. **DeepEP + fused shared experts 的特殊拆分**（L1346–1352）：EPLB 查表只作用于 routed 列——shared 列的值（=num_experts）会越界（L1342–1345 注释），所以先 `torch.cat` 拆合；
3. aiter 的 shared 列追加（§9.3）；
4. DeepEP 交错重映射（§11）。

---

## 11. DeepEP 重映射与 waterfill

### 11.1 _remap_topk_for_deepep（L1276–1320）

DeepEP dispatch 要求"每个 rank 的 shared expert 拥有全局唯一 ID"，于是物理专家表被排成**交错布局**（docstring L1283–1292）：

```
[routed_0..L-1, shared, routed_L..2L-1, shared, ...]   # L = num_local_routed
```

重映射公式：

- routed：`e -> e + e // num_local_routed`（L1305–1306，单 fused 算子完成"每 L 个插一个空位"）；
- shared：`ep_rank * num_local_experts + num_local_routed + arange(n)`（L1309–1313，路由到**本 rank** 的 shared 槽）；
- shared 权重覆写为 `1.0 / routed_scaling_factor`（L1315–1318）——净贡献恰为 1.0，补偿 MoE 输出端的统一 scaling（与 §9.2 呼应）。

注意 L1299–1301 的细节：入口处 routed ids **已经是物理 id**（§10 已做过 EPLB），所以除法用 `num_physical_routed_experts`（L1381–1386 计算并传入），静态 EPLB 的冗余副本 expert 不会破坏布局。

### 11.2 waterfill（L344–385）

DeepEP waterfill（水填式负载均衡）模式下放弃 shared 融合（§3.2），由外部 balancer 事后 `expand_topk`。`empty_topk_output`（L494–514）同样对 DeepEP 空批次做形状补偿，保证 CUDA Graph 捕获时形状一致。

---

## 12. 输出语义规范

综合全文，`StandardTopKOutput` 的契约：

| 字段 | 形状 | dtype | 语义 |
|---|---|---|---|
| `topk_weights` | `(M, top_k)` | **float32**（所有 impl 尾部 `.to(torch.float32)`，L771/836/896/1025） | 行归一权重（或含 scaling）；shared 列 = sum(routed)/rsf 或 1/rsf |
| `topk_ids` | `(M, top_k)` | **int32** | 物理 expert id；**pad 行 = -1**；shared 列 ∈ [E, E+n) 或 DeepEP 交错槽位 |
| `router_logits` | `(M, E')` | 同输入 | **EPLB 变换后**的 logits（E' 可大于 E） |

排序约定：无 fused shared experts 时 `sorted=False`（不保证列序）；有时 `sorted=True` 且尾列为 shared。`-1` 是显式契约：`empty_topk_output` 的 `torch.full(..., -1)`（L500）、`_mask_topk_ids_padded_region` 的整行 -1（L1045）、下游 triton kernel 以 `topk_ids >= 0` 作为有效 token 判据。

---

## 13. 与 fused_moe 的衔接

三路输出各自对接：

1. **STANDARD**：`moe_runner/triton.py` 的 runner input 直接装 `topk_weights/topk_ids`（其 L31–32、L209–225）；triton kernel 按 `topk_ids` 做 expert-major 排序（segment id = expert id），把同一专家的 token 聚成连续块做批量 GEMM，再用 `topk_weights` 加权散射回去。`-1` 行天然落在所有 segment 之外被跳过；
2. **TRITON_KERNEL**：`routing()` 已产出 expert-sorted 的 `RoutingData`（L62–76），matmul_ogs 直接按 ragged 元数据开工，省掉 runner 侧再排序；
3. **BYPASSED**：flashinfer kernel 拿 `BypassedTopKOutput.router_logits` 自行路由；若某层忽然需要显式路由（混合 backend），`to_standard()`（L289–299）惰性物化。

`get_global_expert_distribution_recorder().on_select_experts(topk_ids)`（L1558）是 EPLB 统计的统一挂点——**物理坐标系下的最终选择**才计入分布，热力图因此与真实负载一致。

---

## 14. Noisy Router 考据

**本 commit 的 topk.py 不含 Noisy Router / 噪声注入逻辑**（全仓 grep `noisy|noisy_topk` 无路由相关命中；`git log -S noisy` 在本文件历史中亦无痕迹）。这不是遗漏：

- Noisy gating（Mixtral 的训练期 jitter noise、Shazeer 2017 的可学习噪声）是**训练期负载均衡技术**，推理时 router 权重已冻结，注入噪声只会破坏确定性输出；
- SGLang 是纯推理框架，路由家族里所有"随机性"都是工程语义而非训练语义：`torch.randint` 填 shared 槽（§9）是多副本负载分摊，`SGLANG_SIMULATE_UNIFORM_EXPERTS`（L1536–1546，注释明言 "Benchmark-only... Do NOT use in production"）是 benchmark 去倾斜开关，EPLB 的 `random` dispatch 算法（`ExpertLocationDispatchInfo.ep_dispatch_algorithm`，见 `eplb/expert_location_dispatch.py`）是冗余副本的运行期分流。

若你在旧版笔记/其他框架（vLLM 的 `NoisyTopk`、Megablocks 训练管线）看到 noisy router，那属于训练侧代码；本文件的对应"扰动机制"即上述三者。

---

## 15. 与其他模块的交互

| 模块 | 交互点 | 行号 |
|---|---|---|
| `sgl_kernel` / flashinfer / aiter / mate | 路由 kernel 提供方 | L131–193 |
| `sglang.jit_kernel.*` | `mask_topk_ids`（dsv4）、`moe_fused_gate`、`grouped_topk` JIT kernel | L82, L939, L1206 |
| `sglang.srt.eplb.expert_location_dispatch` | 输入/输出双向 logical↔physical 重映射 | L92–97, L1423–1430, L1052 |
| `sglang.srt.eplb.expert_distribution` | `on_select_experts` 负载统计钩子 | L93, L1558 |
| `sglang.srt.state_capturer.routed_experts` | constrained generation 专家捕获 | L102, L1336–1340 |
| `sglang.srt.layers.dp_attention` | `is_allocation_symmetric` 决定 symmetric memory | L98, L443–445, L496–498 |
| `sglang.srt.layers.moe`（get_moe_runner_backend） | 输出格式推断（triton_kernels/flashinfer） | L99, L416–421 |
| `sglang.srt.layers.moe.utils`（is_deepep_class_backend） | DeepEP 布局重映射触发 | L100, L1346, L1381 |
| `moe_runner/triton_utils`（fused_append_shared_experts） | aiter shared 列追加 | L1366–1377 |
| 模型层（deepseek_v2/qwen2_moe/glm4_moe/dbrx 等 20+ 模型文件） | `TopK` 实例化方 | — |
| `sglang.srt.server_args` | waterfill / 全局参数查询 | L342–347 |

---

## 16. 关键设计决策

1. **协议先行的输出体系**：`TopKOutput` Protocol + 三格式 + `TypeGuard` narrowing，让 TopK 层与 MoE runner 解耦——新增 backend 只需声明格式，不动路由算法；BYPASSED 的 `to_standard()` 惰性物化是"零成本抽象"的范本。
2. **"选择用 bias、计分不用 bias" 的严格分离**：所有 biased impl 中 correction_bias 只进 topk 的比较键（L564–567/864/975/1024），权重永远取原始 sigmoid/softmax 分。这保证与训练期路由分布一致的同时不污染输出数值。
3. **EPLB 双点重映射（输入重排 + 输出查表）**：把"物理坐标系"完全封装在 select_experts 内部，kernel 与模型层零感知；shared 列与 -1 pad 行的两个特判（L1346–1352、L1034–1045）是封装的代价，也是边界清晰的地标。
4. **六层 kernel 阶梯而非单一 kernel**：flashinfer/sgl_kernel/aiter/musa/kimi/jit 各有约束（power-of-two、VPT≤32、topk≤8…），用条件链从最快降到最通用， correctness 由参考 impl 兜底——性能与可移植性分治。
5. **`torch.compile(dynamic=True)` 常驻**：mask+gather+topk 的组合在 inductor 下生成少 kernel 融合代码，`dynamic=True` 适应变长 batch；同时用 `register_fake`（L1563–1606）为自定义 kernel 补 meta 实现，保证 compile 图完整。

---

## 17. 阅读建议

1. **入口顺序**：先读 `TopKOutput` 三兄弟（L236–299）建立输出心智模型 → 跳到 `select_experts` 决策树（L1398–1560）→ 再挑一条自己模型对应的 impl 精读（Qwen3MoE 走 `fused_topk`，DeepSeek 走 `biased_grouped_topk_gpu`）。
2. **对照 DeepSeek V3 论文 §2.1 的路由公式**读 `biased_grouped_topk_impl`（L957–1027）：sigmoid 打分、bias 加法、组 top-2 求和选组、组内选专家——四步与论文完全同构，是最好的"论文↔代码"对照样本。
3. **拿 DeepSeek V3 的 256/8/4/8 参数**手算一遍 L1057–1234 的条件链：256 是 2 的幂、topk_routed=8≤8、每组 32 专家×topk_group 4=128——恰好命中第 1 档 flashinfer；换成 384 专家的 Kimi K2 则落到第 5 档。这条链是理解"为什么我的模型没走上快 kernel"的排查地图。
4. **画一张 topk_ids 的"坐标系旅行图"**：原始 logits 列（EPLB 输入重排）→ 物理 routed id（输出查表）→ DeepEP 交错 id（+e//L 平移 + shared 槽覆盖）。三段变换分布在 L1423/L1052/L1305，串起来才算真正读懂 -1 与 shared 列的语义。
5. **交叉阅读**：本文 §10–11 的重映射与 `eplb/expert_location_dispatch.py`、DeepEP 的 `dispatcher.py` 强耦合；§3.3 的 symmetric memory 与 `dp_attention.py` 的 `is_allocation_symmetric` 对偶——建议与本系列 dp_attention 篇对照读，两文共享同一处代码交汇（topk.py L98）。
