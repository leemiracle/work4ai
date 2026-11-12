# mHC: Manifold-Constrained Hyper-Connections — 论文 × TileKernels 实现对照精读

> 论文：arXiv 2512.24880（v1 2025-12-31，v2 2026-01-05），DeepSeek-AI。一手实现：TileKernels `tile_kernels/mhc/`（29 文件 4359 行，v2.0.0）+ `tile_kernels/torch/mhc.py`（参考实现）+ `tests/mhc/`。实现锚均为本机源码行号实证（2026-11-04）。

## ① 主张与发表信息

**主张**：HC 加宽残差流收益显著但丢失恒等映射性质——多层复合连接矩阵无界增长，27B 训练复合增益冲到 ~3000 并伴随 loss 尖峰；mHC 把 $\mathcal{H}^{\mathrm{res}}$ 投影到**双随机矩阵流形**（Birkhoff polytope），恢复范数守恒，增益全程有界（~1.6），配合 kernel 融合，n=4 下仅 +6.7% 时间。

**机构甄别**：作者 20 位（abs 页"Zhenda Xie and 19 other authors"；HTML 版自述 21 人，含三位 core contributor，通讯 Zhenda Xie）。**HTML 正文作者栏只有 DeepSeek-AI，全页无 Peking University**——任务预设的"PKU×DeepSeek"不成立（勿与 Engram 论文的 PKU×DS 双机构混淆）。无 comments 字段（截至 v2 未见会议标注）。

**前作谱系**：HC = Zhu et al., arXiv:2409.19606（**ByteDance，ICLR 2025**）。mHC 保留"加宽+动态连接"骨架，把参数化从 `α·tanh(θx̃ᵀ)+b`（tanh 无界）换成 **sigmoid / Sinkhorn 流形投影**（值域受控），并补上系统层设计（融合 kernel、选择性重算、DualPipe 扩展）。第三方 Frac-Connections（arXiv 2503.14125）从分数阶角度扩展 HC，与 mHC 正交。

## ② 数学核心

### 2.1 从残差到 HC：残差流加宽

标准残差（Eq.1）：$x_{l+1} = x_l + F(x_l, W_l)$。HC 把特征维从 $C$ 扩到 $nC$（$n$ 为扩展率），每层传播（Eq.3）：

$$x_{l+1} = \mathcal{H}_l^{\mathrm{res}} x_l + \mathcal{H}_l^{\mathrm{post}\top} F(\mathcal{H}_l^{\mathrm{pre}} x_l,\ W_l)$$

三个映射各司其职：

| 映射 | 形状 | 语义 |
|---|---|---|
| $\mathcal{H}_l^{\mathrm{pre}} \in \mathbb{R}^{1\times n}$ | 行向量 | 从 $n$ 条流聚合出子层输入（读） |
| $\mathcal{H}_l^{\mathrm{res}} \in \mathbb{R}^{n\times n}$ | 方阵 | 流间混合（残差主体） |
| $\mathcal{H}_l^{\mathrm{post}} \in \mathbb{R}^{1\times n}$ | 行向量 | 把子层输出写回流（写） |

HC 每个映射为动态+静态两部分（Eq.5）：$\mathcal{H}_l = \alpha_l\cdot\tanh(\theta_l \tilde{x}_l^\top) + b_l$，$\tilde{x}_l = \mathrm{RMSNorm}(x_l)$。多层复合（Eq.4）$\prod_{i}\mathcal{H}^{\mathrm{res}}_{l+i}$ **无任何约束**——不稳定根源。

> 记号勘误：论文记"$C \to nC$，$n{=}4$"，blog26 记"加宽 4 倍"，V4 部署记法 $R{=}4r$（单流宽 $r$）——同一事实，本篇从论文记号。

### 2.2 流形约束：Birkhoff polytope + Sinkhorn-Knopp

mHC 的核心一步是把 $\mathcal{H}^{\mathrm{res}}$ 投影到双随机矩阵集合（Eq.6）：

$$\mathcal{P}_{\mathcal{M}^{\mathrm{res}}} := \{H \in \mathbb{R}^{n\times n} \mid H\mathbf{1}_n = \mathbf{1}_n,\ \mathbf{1}_n^\top H = \mathbf{1}_n^\top,\ H \geqslant 0\}$$

参数化（Eq.7-8）：输入展平 $\vec{x}_l = \mathrm{vec}(x_l) \in \mathbb{R}^{1\times nC}$，投影矩阵 $\varphi_l^{\mathrm{res}} \in \mathbb{R}^{nC \times n^2}$（φ 矩阵小初始化），然后：

$$\mathcal{H}^{\mathrm{pre}} = \sigma(\tilde{\mathcal{H}}^{\mathrm{pre}}),\qquad \mathcal{H}^{\mathrm{post}} = 2\sigma(\tilde{\mathcal{H}}^{\mathrm{post}}),\qquad \mathcal{H}^{\mathrm{res}} = \mathrm{SK}(\tilde{\mathcal{H}}^{\mathrm{res}})$$

Sinkhorn-Knopp：先取指数保证正性 $M^{(0)} = \exp(\tilde{\mathcal{H}}^{\mathrm{res}})$，再交替行列归一化 $M^{(t)} = \mathcal{T}_r(\mathcal{T}_c(M^{(t-1)}))$，实验取 $t_{\max}=20$。**注意约束只施加在 $\mathcal{H}^{\mathrm{res}}$ 上**；pre/post 只用 sigmoid 保证元素非负（论文也把这框定为流形投影：非负矩阵流形），pre 的行和不必为 1，post 是 $2\sigma\in(0,2)$（均值≈1，近似保幅）。

### 2.3 恒等映射为何被恢复（四条性质）

1. **凸组合**：$\mathcal{H}^{\mathrm{res}} x$ 是各流特征的凸组合——均值守恒、范数受严格正则；
2. **非扩张**：$\|\mathcal{H}^{\mathrm{res}}\|_2 \leqslant 1$，梯度不爆（对比 tanh 复合放大 ~3000 倍）；
3. **乘法封闭**：任意深度复合 $\prod_i \mathcal{H}^{\mathrm{res}}$ 仍双随机，守恒性全深度保持；
4. **退化恢复**：$n{=}1$ 时约束坍缩为标量 1，**精确退化为标准残差**（HC 的 n=1 因 tanh 参数化并非恒等）。

几何直觉：Birkhoff polytope 是置换矩阵的凸包，$\mathcal{H}^{\mathrm{res}}$ = "置换的凸组合"，随训练从近似恒等滑向任意混合。SK 收敛性：正矩阵（exp 保证）下 Sinkhorn 定理保证交替归一化收敛到唯一双随机极限；有限 $t{=}20$ 时梯度增益略偏离 1（论文明示的 practical limitation）。

## ③ 实验数字

**设置**：DeepSeek-V3 风格 MoE，$n{=}4$：3B/39.3B tokens/30k 步、9B/105B/50k、27B/262B/50k（27.0B 总参/4.14B 激活），另有 3B@1.05T（100k 步）长训。

**27B 下游（Table 4，baseline→HC→mHC）**：

| 基准 | baseline | HC | mHC |
|---|---|---|---|
| BBH (EM) | 43.8 | 48.9 | **51.0** |
| DROP (F1) | 47.0 | 51.6 | **53.9** |
| GSM8K (EM) | 46.7 | 53.2 | **53.8** |
| HellaSwag | 73.7 | 74.3 | **74.7** |
| MATH (EM) | 22.0 | **26.4** | 26.0 |
| MMLU | 59.0 | 63.0 | **63.4** |
| PIQA | 78.5 | 79.9 | **80.5** |
| TriviaQA (EM) | 54.3 | 56.3 | **57.6** |

mHC 8 项中 7 项胜 HC（MATH 略输）；最终 loss 比 baseline 低 0.021，比 HC 高 +2.1 BBH / +2.3 DROP。**稳定性对照最有说服力**：HC 27B 在 ~12k 步 loss 尖峰+梯度范数不稳，复合增益峰值 ~3000；mHC 全程稳定 ≤1.6（三个数量级压制）。组件消融（Table 1，loss gap）：仅 $\mathcal{H}^{\mathrm{res}}$ → −0.022，+$\mathcal{H}^{\mathrm{pre}}$ → −0.025，全开 → −0.027——残差混合贡献大头。

**开销**：n=4 仅 +6.7% 时间。I/O 账（Table 2，每 token 前向）：标准残差读 $2C$ 写 $C$；HC 读 $(5n{+}1)C{+}n^2{+}2n$ 写 $(3n{+}1)C{+}n^2{+}2n$；融合后读 $(n{+}1)C$、写 $nC$。显存：选择性重算只留每 $L_r$ 层块输入，$L_r^* \approx \sqrt{nL/(n{+}2)}$。基础设施三件套：TileLang 三融合 kernel、RMSNorm 除法后置重排、融合 SK kernel 带 on-chip 重算反向；DualPipe 扩展调度+高优先级计算流。

## ④ TileKernels 实现对照表（论文公式 ↔ 文件:行号）

实现分三层：`*_kernel.py`（API/后端分派）→ `*_cuda.py`（TileLang CUDA）→ `*_asc.py`（昇腾 SIMD）；`torch/mhc.py` 为 PyTorch 参考（测试裁判）。全部 op 双后端实现且带 `use_pdl`（分派例 `mhc/sinkhorn_kernel.py:7-12`；昇腾 SIMD `mhc/sinkhorn_asc.py:1-40`）。数据流：`expand → [GEMM(φ)→reduce+RMSNorm→split→Sinkhorn→apply] → 子层 F → post → … → head`。

| 论文概念/公式 | TileKernels 实现 | 关键锚 |
|---|---|---|
| 残差流加宽 $C \to nC$ | `expand_to_mhc`：hidden 复制 n 份 | 参考 `torch/mhc.py:4-5`；fwd `mhc/expand_cuda.py:5-27`（L20-25 复制），bwd 对 n 流梯度求和 `expand_cuda.py:45-50` |
| RMSNorm 后投影 $\varphi$（Eq.7 的 $\tilde{H}=\varphi\vec{x}$） | φ 矩阵（代码 `fn`，(n²+2n, nC)）× residual 展平——**GEMM 本体在 DeepGEMM**，库内做 normw 折叠与 split-K 归约 | 增益折叠 `mhc/norm_fn_cuda.py:11-29`；参考 `torch/mhc.py:66-85` |
| **RMSNorm 除法后置**（"数学等价重排"） | GEMM 出 split-K partials（未归一化乘积+平方和），归约时才乘 $rsqrt$ | `mhc/norm_fn_cuda.py:66-111`（rsqrt L102，mixes L103-107）；参考 `torch/mhc.py:88-111` |
| $\mathcal{H}^{\mathrm{pre}}=\sigma(\cdot)$，$\mathcal{H}^{\mathrm{post}}=2\sigma(\cdot)$，$\tilde{\mathcal{H}}^{\mathrm{res}}$ logits（Eq.7-8）+ 动静态分解（Eq.5 后继） | `mhc_pre_split_mixes`：GEMM 输出 (tokens, 2n+n²=24) 劈三份，各自 `input·scale+base`（scale(3,)/base(24,) 即论文 α/b 静态部）后不同变换 | `mhc/pre_split_mixes_cuda.py:54-60`（pre=σ+eps）、`:61-62`（post=σ·mult）、`:63-64`（logits）；参考 `torch/mhc.py:27-49` |
| $\mathcal{H}^{\mathrm{res}} = \mathrm{SK}(\tilde{H})$（Eq.8） | `mhc_sinkhorn`：softmax+eps 起步，交替行/列归一化 `repeat-1` 轮 | fwd `mhc/sinkhorn_cuda.py:33-39,41-43,45-52`；参考 `torch/mhc.py:8-14`；API `mhc/sinkhorn_kernel.py:6-12` |
| **SK 反向（on-chip 重算）** | 反向 kernel 重跑前向并把全部中间态存 shared memory（`xs[repeat*2]`/`sums`），逆序手推链式法则 | `mhc/sinkhorn_cuda.py:91-92`（中间态）、`:124-144`（逆序行/列）、`:146-151`（softmax 反向 $(g-\sum g\odot x)\odot x$） |
| pre 读出 $=\mathcal{H}^{\mathrm{pre}} x$ | `mhc_pre_apply_mix`：$o=\sum_m \mathrm{mix}_m x_m$（fp32 累加 bf16 出） | `mhc/pre_apply_mix_cuda.py:46-48`；参考 `torch/mhc.py:52-53`；bwd `:83-110` |
| post+res 写回（Eq.3 右两项） | `mhc_post`：`x_new[m]=post[m]·d + Σ_n comb[n,m]·res[n]` | `mhc/post_cuda.py:53-58`；参考 `torch/mhc.py:56-63`；bwd 四路梯度 `post_cuda.py:128-152`；dtype 约束 `mhc/post_kernel.py:19-22`（bf16 残差/fp32 混合） |
| **三融合 kernel**（"mostly in TileLang"） | `mhc_pre_big_fuse`：单 kernel = 归约+RMSNorm→劈 post/comb→**片上 4×4 Sinkhorn**→pre 劈分+apply；96 线程 warp 分工 | `mhc/pre_big_fuse_cuda.py:49-63,65-72,74-106,108-134`；GEMM 移交 DeepGEMM 证据 `tests/mhc/test_pre_big_fuse.py:62-68,233` |
| HC head（n→1 坍缩进 LM head） | `mhc_head_compute_mix`：σ(mix·scale+base)+pre_eps | `mhc/head_compute_mix_cuda.py:33`；参考 `torch/mhc.py:17-24` |
| 选择性重算 | `mhc_multilayer_recompute`：指针数组一次 launch 重放 L 层链，双缓冲 async 预取，层间 bf16 round-trip | `mhc/multilayer_recompute_cuda.py:13-36`（ptr）、`:94-99`（pre-apply）、`:104-107`（post）、`:111-112`（bf16 回写=位级一致前提）、`:114-125`（尾部 pre-only） |

**实现完整度：论文公式侧 100% 覆盖**——三映射、SK 前向/反向、融合、重算、head 全落地且有逐公式参考；不在库内的只有 φ GEMM 本体（DeepGEMM 承接）与训练编排（DualPipe 属训练框架）。

## ⑤ 测试揭示的边界（数值容差 / 形状约束）

**数值容差分层**（fp32 元素级 → bf16 访存级 → 位级相等，三档）：

| 档位 | 测试 | 容差 | 锚 |
|---|---|---|---|
| 位级 | pre_big_fuse 融合 vs 未融合链；multilayer_recompute vs 逐层 kernel | `torch.equal`（bit-exact） | `test_pre_big_fuse.py:203-205`、`test_multilayer_recompute.py:121-127` |
| 紧 fp32 | sinkhorn、pre_split_mixes | 默认 close；大 logit 用 rtol=1e-5/atol=1e-6；split 用 rtol=1e-5/atol=2e-5 | `test_sinkhorn.py:58-59,101-102`、`test_pre_split_mixes.py:165-170` |
| 松 bf16 | pre_apply_mix（沿 nC 维 bf16 累加）；norm_fn mixes | atol=1e-2/rtol=1e-3；atol/rtol=1e-3 | `test_pre_apply_mix.py:59-61`、`test_norm_fn.py:167` |
| 相对差范数 | norm_fn 的 GEMM 邻接算子（防 `1-sim` 灾难性消去） | `_calc_diff` < 1e-8 | `test_norm_fn.py:75-89` |
| 小矩阵梯度单独放宽 | post 的 dc/da（4×4/4 维小张量） | atol/rtol=1e-4 | `test_post.py:70-81` |

位级相等是最硬的发现：融合 kernel 与未融合链采用**完全相同的浮点操作序**（归约顺序、eps 位置逐位复刻，`pre_big_fuse_cuda.py:74-106` 对 `sinkhorn_cuda.py:33-52` 逐行等价），故 `torch.equal` 可作断言——融合优化"零数值代价"有测试背书。

**数值稳定性专项**：`test_sinkhorn_large_same_sign_logits`（`test_sinkhorn.py:62-102`）用 ±100 偏移大 logit 验证 max 减法稳定性（`exp(x - row_max)`，`sinkhorn_cuda.py:33-36`——论文只写 $\exp(\tilde{H})$ 未提 max 减，实现补齐；数学上 max 平移被首个行归一化精确抵消，纯数值动机）。eps 语义**不对称**：首轮行归一化 `/row_sum + eps`（softmax 后加，`sinkhorn_cuda.py:39`），后续 `/(sum + eps)`（`:48,52`）——与参考 `torch/mhc.py:9-13` 逐位一致，位级断言成立的前提。

**形状约束**：
- $n{=}4$：CUDA 侧参数化 `mhc_mult` 但测试矩阵只覆盖 4；**昇腾侧 assert mHC4-only**（`mhc/head_compute_mix_kernel.py:11,37,77`）——与论文"n 固定 4、无消融"互证。
- hidden 对齐：`h_blk = gcd(h,1024)` 且 `%128==0`（`mhc/post_kernel.py:51-53`）；测试覆盖 1280~8192 含 (4096+64) 非整除路径（`test_expand.py:35`、`test_pre_big_fuse.py:182-183`）。
- 奇数 token（1001/509/1021）靠 guard `if i < num_tokens`（`head_compute_mix_cuda.py:32`）；head 测试到 24576 token（`test_head_compute_mix.py:81`）。
- 重算链最长 10 层×8192 token，L 与 L_post 允许差一（`test_multilayer_recompute.py:10-28`）。
- **初始化口径**（论文"小初始化门控"）：φ `randn×1e-4`（`test_norm_fn.py:53-57`）、`mhc_scale/base×0.1`（`test_pre_big_fuse.py:44-45`）、normw `×0.1+1.0`（近 1，`test_norm_fn.py:59-60`）。
- 超参缺省值：`mhc_post_mult_value=2.0`（= 论文 $2\sigma$；`test_pre_split_mixes.py:33`）、`mhc_pre_eps=1e-2`、`sinkhorn eps=1e-6`、测试 `repeat=10`（论文/blog 生产值 20，kernel 由 `repeat` 参数承接）。

## ⑥ 部署融合视角（TensorRT-LLM blog26，V4 on Blackwell）

V4 生产架构：**每层两个 mHC 模块**（包住 attention 与 MoE）+ **HC head**（LM head 前坍缩回单流）+ 20 次 SK 迭代；MTP draft 层复用 mHC 结构消费扩展残差态。优化四板斧：

1. **post+pre 融合**：上一子层 post 与下一子层 pre 融合成形状特化 kernel（attention→MoE 边界首选，可跨层全融）；**下一子层 RMSNorm 折进融合 epilogue**——省一次 launch + 一次 HBM 往返；mHC 拥有残差连接后 MoE 路径不再单独做残差。
2. **FMA/MMA 双路径按 M 选**：小 token 数走 FMA、大 M 走高吞吐 MMA，各有 two-kernel / all-in-one 战术、多 tile 配置与 Split-K；autotuner 按 M 区间剪枝并缓存战术。
3. **PDL**：消费方 grid 提前 launch、显式依赖点等待，用于 fused mHC 缩短相邻边界（TileKernels 同款：全部 mhc kernel 带 `use_pdl`）。
4. **收益实测**：May 18 里程碑（MegaMoE+EPLB+**fused mHC+RMSNorm**+多流 attention）阶段 +29.0%、对基线 +53.0%；全链 Pareto 984→1618 tokens/s/GPU（+64.5%）。

训练侧（TileKernels）与部署侧（TRT-LLM）是同一数学的两种融合切法：前者保 autograd（融合限 pre 侧前向链+重算），后者无梯度约束可 post+pre+RMSNorm 全融；共享论文 I/O 账本结论（读 $(3n{+}1)C{\to}(n{+}1)C$、写 $3nC{\to}nC$）。

## ⑦ 局限

1. **有限 SK 迭代的梯度偏差**：$t{=}20$ 下反向梯度增益略偏离 1，复合偏差上浮 ~1.6（有界非 1）；无迭代数消融，精度-开销权衡无系统刻画。
2. **扩展率未消融**：$n{=}4$ 固定，无 n=2/6/8 对照；HC 前作消融结论不能直接平移（约束改变容量-稳定性权衡）。
3. **额外参数与显存**：φ 投影每层 $(2n{+}n^2){\times}nC$（n=4 时 ≈96C/层，小但非零）；残差流驻留显存 ×4（选择性重算缓解），推理侧 KV/激活管理复杂度同步上升。
4. **稳定性收益 ≠ 收益上限**：MATH 上 mHC（26.0）低于 HC（26.4）——流形约束压制不稳定的同时截断部分表达自由度（plasticity-stability，论文自认未来方向）；约束单一（Birkhoff），定制流形是开放问题。
5. **实验面窄**：仅自家 V3 风格 MoE，无 dense/外部模型族/微调验证；3B@1.05T 长训 scaling 未展开。
6. **实现侧边界**：n=4 硬编码（昇腾 assert）、hidden 128 对齐、φ GEMM 依赖 DeepGEMM split-K partials 接口（`test_pre_big_fuse.py:62-68`）——跨 n 泛化须重写 tile 布局。

## 参考

- 论文：arXiv 2512.24880（v2 2026-01-05）；HC 前作：Zhu et al., arXiv:2409.19606（ByteDance, ICLR 2025；[arXiv](https://arxiv.org/abs/2409.19606) / [OpenReview](https://openreview.net/forum?id=9FqARW7dwB)）
- 实现：`/usr-data/data2/repos/deepseek-ai/TileKernels`（v2.0.0, 828cc15）；部署：TensorRT-LLM blog26（DeepSeek-V4 on Blackwell）
