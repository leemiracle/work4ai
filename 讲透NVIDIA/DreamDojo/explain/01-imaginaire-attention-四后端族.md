# ① imaginaire/attention：统一注意力前端与四后端族

## 角色定位

`cosmos_predict2/_src/imaginaire/attention/`（41 文件）是 Imaginaire4 训练基建的"算子适配层"：把 FlashAttention-2/3、cuDNN SDPA、NATTEN 四家注意力实现统一到一个前端 API 下，让上层 DiT（`networks/minimal_v4_dit.py:58` 的 `from ...imaginaire.attention import attention`）完全不感知硬件与库差异。它解决的核心矛盾：不同 SM 架构上最优后端不同（Hopper=flash3、Blackwell=cuDNN、Ampere=flash2），且各家对 GQA/varlen/因果掩码/dtype 的支持矩阵互相错位。所有后端遵守统一张量布局 `[batch, seqlen, heads, head_dim]`（heads-last）。

## 内部结构

**前端三 API**（`frontend.py`）：`attention()`（55 行，一维序列）、`multi_dimensional_attention()`（277 行，1-3 维 token 布局的邻域注意力，window_size/stride/dilation 三参直通 GNA/DiNAT 语义）、`spatio_temporal_attention()`（507 行，6-D `[B,T,H,W,H,D]` 特例，硬编码 `is_causal=(True,False,False)` 于 583 行——时间因果、空间全连）。

**分发核心**：`frontend.py:43-52` 两张表——`BACKEND_MAP`（四后端函数）与 `MULTI_DIM_BACKEND_MAP`（仅 natten，因为多维邻域注意力只有 NATTEN 会做）。`backends.py:107-148` `get_backend_list(arch_tag)` 按性能排序返回候选：SM90 → `[flash3, cudnn, natten, flash2]`（125-131）；SM100/103（Blackwell 含 B300 的 103）→ `[cudnn, natten, flash2]`（133-139，注释里还有被注释掉的 `"flash4"`）；SM80+ → `[flash2, cudnn, natten]`（141-146）；SM75 只有 `[natten]`；SM<75 返回空。`choose_backend`（151）逐个试 `is_backend_compatible`，第一个过检的即中选。

**四后端四件套**：每后端一个目录，checks（能力探测）/functions（算子入口）/meta（dtype·架构表）/stubs（可选依赖懒加载）：
- flash2（`flash2/functions.py:31` `flash2_attention`，包 `flash_attn`）；
- flash3（`flash3/functions.py:37`，包 `flash_attn_3`）——`functions.py:31` 用 `inspect.signature` 探测 `return_attn_probs` 参数是否存在（版本无 commit 哈希反射的兜底），119-120 无条件传 `return_attn_probs=True`；`meta.py:41` `arch_tag != 90` 即返回空 dtype 表——**flash3 是 Hopper 专属**；`checks.py:81-86` 还拒绝 torch.compile 区域；
- cudnn（`cudnn/functions.py:167` `cudnn_attention` → `CudnnAttentionAutogradFn`，48 行 torch.autograd.Function 手写正反传）：forward 里现场生成 cuDNN 计算图（102 行 `cudnn_sdpa_fwd_generate_op`），图按 shape/dtype/stride 键 `@lru_cache(maxsize=64)` 缓存（`cudnn_forward.py:37,196`）；`functions.py:45` `CUDNN_PADDING_REQUIRED=False` 关闭了 256 对齐 padding 的 workaround（69-71 行注释留档"2025-11-12 修不了 bug 但保留备用"）；245 行 `assert not is_varlen`——cuDNN 后端不支持变长序列打包；
- natten（`natten/functions.py:45` `natten_attention`、163 `natten_multi_dim_attention`）：唯一同时覆盖一维与多维的后端，127-142 行还有二段选择——backend_kwargs 未指定时按形状调 `choose_natten_backend` 选 NATTEN 内部 kernel，并默认 `backward_use_pt_reduction=True` 用 PyTorch 归约换精度（136-141）。

**公共件**：`masks.py:26` `CausalType` 三值枚举（TopLeft=CUTLASS/NATTEN 默认对角、BottomRight=FlashAttention 默认、DontCare=方阵时等价），31-56 行 ASCII 图画清两种对角差异——跨后端因果语义对齐的关键抽象；`varlen.py:29` `generate_varlen_parameters` 把 seqlens 转 cumsum+max（104-110 手动拼前导 0），42-48 明确**禁止在 torch.compile 区域调用**（.item() 断图）；`checks.py` 500 行承载全部校验（35 `_universal_tensor_checks`、155 `attention_tensor_checks`、202 `varlen_tensor_checks`）；`utils/__init__.py:31` `get_arch_tag` 探 SM 版本、54-63 dtype 判定、66-71 `is_hopper/is_blackwell_dc`。

## 外部连接

上游消费者：`predict2/networks/minimal_v4_dit.py:375` `i4_attention_op`（整流流 DiT 的 `backend="i4"` 路径）、`predict2/modules/neighborhood_attn.py`（DiT 的 NATTEN 稀疏注意力分支）、`interactive` 线的因果 DiT。下游依赖：可选包 `flash_attn`/`flash_attn_3`/`natten` 与 cuDNN 前端（`pyproject.toml` extras 控制），torch/FlexAttention 不经此层（minimal_v4_dit 自带 `flex_attention_op`，`minimal_v4_dit.py:292`）。测试四份：`tests/sdpa_test.py`（对拍 torch SDPA）、`varlen_test.py`、`multi_dim_test.py`、`torch_compile_test.py`。

## 数据流

以一次 varlen 注意力为例：用户在模型 forward 外预算 `generate_varlen_parameters(q,k,v,seqlens_Q,seqlens_KV)` 得 `(cumsum_Q, cumsum_KV, max_Q, max_KV)` → `attention(q,k,v,cumulative_seqlen_Q=...)` → 前端先过 `attention_tensor_checks`（164）与 `attention_param_checks`（166）→ `varlen_tensor_checks`（179）归一化两种传参 → `choose_backend`（201）按 arch_tag 排序试检 → GQA/MQA 不兼容时走图变换兜底：`frontend.py:217` 判定 `heads>heads_kv` 后用 `torch.repeat_interleave`（229-230）把 K/V 头复制到与 Q 等头再递归重试 → 命中后端函数（261 `BACKEND_MAP[compatible_backend](...)`）。flash3 的 varlen 路径（`flash3/functions.py:122-153`）把 batch=1 的 packed 序列 squeeze 成 3-D 喂 `flash_attn_varlen_func`，输出 lse 统一 `permute` 回 heads-last（179）。

## 设计决策

1. **按性能排序的探测式选择**而非静态绑定——同一份代码在 H100/B200/A100 上自动换最优 kernel，代价是每次调用都跑一遍 checks（用 debug log 解释淘汰原因，`frontend.py:252` 提示"开 debug 日志看原因"）。
2. **checks 与 functions 分离**：能力探测纯函数化，使 `choose_backend` 能廉价轮询；每个后端 checks 内部先查 meta 的 dtype 表再查形状约束（如 flash3 MLA 头维组合 108-118 行）。
3. **varlen 双传参设计**：seqlens 便捷但每次重算 cumsum+max（含 host 同步），cumsum+max 高效但要求用户在编译区外预算——用 RuntimeError 强制（`varlen.py:42-48`）。
4. **graph transformation 兜底**：GQA 通过 repeat_interleave 物化展开（`frontend.py:222-247`），牺牲带宽换兼容性，注释明言 MLA/varlen 也可如此但暂不做（214-215）。
5. **multi-dim 降维化简**：token 布局含 1 的维度直接 reshape 去掉（408-441）、窗口=全形的自注意力退回一维 `attention()` 快路径（452-475）——少碰 NATTEN 就少一份开销。

## 新人提示

- 排查"选了错误后端"：设 `ATTENTION` 相关 debug 日志（`utils/safe_log.py`），每条淘汰原因都会打出来；`is_backend_compatible`（`backends.py:48`）可单测。
- **勘误（源码实证）**：`frontend.py:421` `value_t = key.reshape(value.shape[0], ...)`——multi-dim 降 1 维路径把 **key** 的数据 reshape 成 value 的形状（应为 `value.reshape(...)`）；当前所有调用方 K/V 同形所以未触发，但写自定义 head_dim_v≠head_dim 的算子会静默拿到错误数据。同函数 419-421 行注释也仅声明 "assumes QKV token layouts match"，属上游未爆雷。
- flash3 在 torch.compile 里不可用（`flash3/checks.py:81`）、cuDNN 不支持 varlen（`cudnn/functions.py:245`）——组合这些特性时前端会自动降级到 flash2/natten，不必自己写分支。
- 新增后端：复制一个四件套目录 + 在 `backends.py:36-45` 两张表注册 + 写 `tests/sdpa_test.py` 对拍即可，前端零改动。
