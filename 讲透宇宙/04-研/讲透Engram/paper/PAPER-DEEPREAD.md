# Engram 精读：Conditional Memory via Scalable Lookup

> 论文：*Conditional Memory via Scalable Lookup: A New Axis of Sparsity for Large Language Models*，arXiv:2601.07372（v1 2026-01-12；v2 2026-07-12；ACL 2026 long.226）
> 作者：Xin Cheng*、Rui Tian*、Wangding Zeng、Damai Dai、Zhenda Xie、梁文锋（Wenfeng Liang）、Huishuai Zhang、赵东岩（Dongyan Zhao） 等（北京大学 × DeepSeek-AI，*共一；梁文锋/张牧涵/赵东岩为 PKU 侧公开中文名，其余保留拼音）
> 本地仓：`~/ai/explore/deepseek-ai/Engram`（含 `Engram_paper.pdf` 原文 + `engram_demo_v1.py` 参考实现）

## 0. 定位澄清（任务调研结论，推翻原预设）

任务原预设"DeepSeek 的记忆项目？与 Mem0 关系"。经 websearch + 仓内 PDF 核实，**两者都不是**：

1. **Engram 不是 agent 记忆层/记忆管理项目**，而是 DeepSeek 与北大合著的**模型架构研究论文**——给 Transformer 增加一个可训练的"N-gram 查表记忆模块"。"memory"指模型内部的**参数化静态记忆**（embedding 表），不是对话记忆/用户记忆。
2. **与 Mem0 零关联**：Mem0 是独立的 agent 记忆基础设施公司；唯一生态交集是 Mem0 后来给 DeepSeek 的 agent 框架（Cordis/DeepSeek-Harness）发布过一个插件——与本文完全无关。社区将其解读为"DeepSeek V4 架构预告"（新浪报道：梁文锋署名、V4 更细节了），因为它明确以"下一代稀疏模型的建模原语"自我定位（与 V3.2 的 DSA 稀疏注意力同一谱系：一个砍注意力的计算，一个补知识的查表）。
3. **有论文**（仓内 PDF 即正文，arXiv 2601.07372 为网络版），故本报告走论文精读结构；版本注记：ACL camera-ready 摘要中模块曾用名 **DSE（Deep Sparse Embedding）**，arXiv v2 恢复并统一为 **Engram**，两名为同一物。

## 1. 一句话定位

把经典 N-gram 嵌入"现代化"成一个 O(1) 查表的**条件记忆（conditional memory）模块**：语言中大量命名实体与固定搭配是局部、静态、高度刻板的，没必要用深层注意力去"算"，直接查表取回静态嵌入并用上下文门控融合进隐状态；论文进一步形式化"稀疏预算在 MoE（条件计算）与 Engram（条件记忆）之间怎么分"的 **Sparsity Allocation** 问题，发现 U 形分配律，据此训出等参数等 FLOPs 下全面胜过 MoE-27B 的 Engram-27B。

## 2. 动机与痛点

- **语言建模的二象性**：组合推理（需要深而动态的计算）与知识检索（局部、静态、刻板——N-gram 时代的强项）混在同一种稠密计算里。
- **Transformer 缺原生查找原语**：识别一个多 token 实体（论文引 PatchScope 的 Diana, Princess of Wales 案例）要耗掉前若干层的 attention+FFN 逐步拼装特征——本质是**用运行时计算昂贵地重建一张静态查找表**，浪费顺序深度。
- **MoE 只解决了"算"的稀疏**（条件计算），"查"的稀疏缺一个对偶原语。生物神经系统同样稀疏（引用 Olshausen & Field）。

## 3. 核心方法

### 3.1 总体数据流

位置 t 两阶段：**检索**（压缩后缀 N-gram → 确定性哈希 → 查多张质数大小的嵌入表 → 拼接）→ **融合**（隐状态作 Query、检索向量作 K/V 的门控 + 短卷积）→ 残差写回 `H ← H + Y`，之后照常走该层 Attention 与 MoE。模块**只挂在特定层**（27B 版：第 2、15 层），输入输出 embedding/un-embedding 不动。

### 3.2 Tokenizer Compression

子词 tokenizer 为无损重建设计，语义等价词形（Apple vs ␣apple）拿到不同 ID，浪费表容量。做法：预计算满射投影 P: V→V′，按规范化文本等价类（NFKC、去音标、小写、空白归一）折叠 ID，128k 词表**有效大小降 23%**。后缀 N-gram 在压缩 ID 上构成：g_{t,n} = (x'_{t-n+1},…,x'_t)。

### 3.3 Multi-Head Hashing

所有可能 N-gram 直接参数化不可行（组合爆炸），用哈希撞大表：对每阶 n 配 K 个头，第 k 头以确定性 multiplicative-XOR 哈希 φ_{n,k} 映到质数大小 M_{n,k} 的表 E_{n,k}：

$$z_{t,n,k} = \varphi_{n,k}(g_{t,n}), \quad \mathbf{e}_{t,n,k} = \mathbf{E}_{n,k}[z_{t,n,k}], \quad \mathbf{e}_t = \Big\|_{n=2}^{N}\Big\|_{k=1}^{K}\mathbf{e}_{t,n,k}$$

多独立头把单头碰撞噪声变成可学习消解的冗余（配合下述门控）。

### 3.4 Context-aware Gating（消歧的关键）

检索向量是无上下文先验，会因碰撞/多义有噪声。用当前隐状态 h_t（已聚合全局上下文）作 Query，检索向量 e_t 出 K/V：

$$\alpha_t = \sigma\!\left(\frac{\mathrm{RMSNorm}(\mathbf{h}_t)^\top\,\mathrm{RMSNorm}(\mathbf{k}_t)}{\sqrt{d}}\right),\qquad \tilde{\mathbf{v}}_t = \alpha_t\cdot\mathbf{v}_t$$

语义不对路时门趋零、噪声被压制（RMSNorm 稳梯度）。再过一支 depthwise 因果卷积（kernel=4、dilation=max N=3、SiLU、残差）扩大感受野补非线性：

$$\mathbf{Y} = \mathrm{SiLU}(\mathrm{Conv1D}(\mathrm{RMSNorm}(\tilde{\mathbf{V}}))) + \tilde{\mathbf{V}}$$

### 3.5 多分支（mHC）集成与参数共享

主干用 Manifold-Constrained Hyper-Connections（M=4 分支）。Engram 适配：**嵌入表与 W_V 全分支共享，M 个独立 W_K^(m) 给出分支特异门控** α_t^(m)，W_V 与各 W_K 拼成单个稠密 FP8 GEMM 吃满 GPU。分支门控：

$$\alpha_t^{(m)} = \sigma\!\left(\frac{\mathrm{RMSNorm}(\mathbf{h}_t^{(m)})^\top\,\mathrm{RMSNorm}(\mathbf{W}_K^{(m)}\mathbf{e}_t)}{\sqrt{d}}\right)$$

### 3.6 Sparsity Allocation：U 形分配律（理论核心）

固定总参 P_tot 与激活参 P_act（等参等 FLOPs），把稀疏预算 P_sparse = P_tot − P_act 在 MoE 专家（占比 ρ）与 Engram 表（1−ρ）间划分。两档算力（5.7B/568M 激活，sparsity≈10；9.9B/993M）扫 ρ：

- **纯 MoE（ρ=100%）是次优的**：把 20–25% 稀疏预算换记忆最好（10B 档验证 loss 1.7248→1.7109，Δ=0.0139）；
- 最优点稳定在 **ρ≈75–80%**（Engram-27B 取 ρ=74.3%：72 个路由专家砍到 55，腾出 5.7B 参数做记忆）；
- MoE 砍到 ρ≈40% 时性能才追平纯 MoE——"白拿"约一半稀疏预算；
- 两端都差：ρ→1 缺记忆原语被迫用深度重建静态知识；ρ→0 失去条件计算，动态推理受损——**记忆替代不了计算**。

**无限记忆 regime**：固定 3B/568M 骨干训 100B tokens，表 slots 从 2.58×10⁵ 扫到 10⁷（追加约 13B 参数）：验证 loss 随 slots 严格幂律下降（log-空间线性）——一个**不增 FLOPs 的可预测扩容旋钮**，且同预算下扩表效率显著优于 OverEncoding 的平均式融合。

### 3.7 系统效率：计算与存储解耦

与 MoE 依赖隐状态动态路由不同，Engram 寻址**只由输入 token ID 决定（确定性）**：训练时表按 GPU 分片 + All-to-All 收集激活行/分发梯度；推理时表可卸载到 host 内存，前向开始前即知索引 → 异步 PCIe 预取，用前置层的计算掩盖传输（模块挂层位置要同时满足"建模要早插入"与"留足预取窗口"的双约束）；N-gram 的 Zipf 分布进一步支撑多级缓存（HBM/DRAM/NVMe）。实测 **100B 参数表 offload 到 host 开销 <3%**——绕开 HBM 容量约束激进扩参。

## 4. 实验与结果

**27B 级（262B tokens、30 block、hidden 2560、MLA 32 头、mHC×4、Muon 优化器、DeepSeek-V3 tokenizer；嵌入 lr×5 无 weight decay、卷积零初始化保恒等起步）：**

| | Dense-4B | MoE-27B | Engram-27B | Engram-40B |
|---|---|---|---|---|
| 总参/激活 | 4.1B/3.8B | 26.7B/3.8B | 26.7B/3.8B | 39.5B/3.8B |
| Pile loss | – | 2.091 | 1.960 | 1.942 |
| MMLU | 48.6 | 57.4 | 60.4 (+3.0) | 60.6 |
| CMMLU | 47.9 | 57.9 | 61.9 (+4.0) | 63.4 |
| BBH | 42.8 | 50.9 | 55.9 (**+5.0**) | 57.5 |
| ARC-Challenge | 59.3 | 70.1 | 73.8 (+3.7) | 76.4 |
| HumanEval | 26.8 | 37.8 | 40.8 (+3.0) | 38.4 |
| GSM8K / MATH | 35.5/15.2 | 58.4/28.3 | 60.6/30.7 | 62.6/30.6 |
| CCPM | 72.2 | 79.6 | 87.1 (**+7.5**) | 87.7 |

亮点：**推理类收益（BBH +5.0）大于知识类（MMLU +3.0）**——与"记忆只帮知识"的直觉相反，机制分析（§5）解释了原因。Engram-40B 训练 loss 差距到训练尾段仍在拉大（欠训练，容量未饱和）。

**长上下文（YaRN 扩 32K：s=10, α=1, β=32, f=0.707，5000 步/30B tokens）**：Engram-27B 只用 82% 预训练 FLOPs（41k 步）即追平 MoE-50k 的 LongPPL；等 loss（46k）与等 FLOPs（50k）设定下 RULER 全面碾压——Multi-Query NIAH **84.2→97.0**、Variable Tracking 77.0→89.0、CWE 4.5→99.3、FWE 34.5→44.0。解释：局部依赖交给查表后，注意力容量被解放给全局上下文。

## 5. 机制分析（为什么推理也变强）

- **LogitLens 预测收敛**：中间层隐状态过 LM Head 与最终分布的 KL——Engram 各层系统性更小、前几块差距最大（更早完成特征组装、更早"预测就绪"）。
- **CKA 有效深度**：以 Few-NERD 实体末 token 表示算层间 CKA 相似度矩阵，定义软对齐指数 a_j（top-5 相似 MoE 层的加权质心）：**Engram 第 5 层 ≈ MoE 第 12 层**，全程 a_j > j——早层静态重建被查表接管后，网络"等效变深"，省下的深度用于复杂推理。这是"推理也涨分"的直接证据，也回应了 §6.2 消融：**Engram 插得越早越好**（layer 2 最优，越深越差——与系统侧"挂深一点好藏预取延迟"相矛盾，最终 2+15 双层是折中）。
- **Gating 可视化**：门在"局部静态模式完成处"精确点亮——英文多 token 实体（Alexander the Great、the Milky Way）与公式化短语（By the way），中文成语与历史实体（四大发明、张仲景），跨语言成立。消融确认 multi-branch 集成、tokenizer compression、context-aware gating 三件均不可少。

## 6. 局限与后续

论文自认/可见：① demo 代码明确标注是**数据流演示**（Attention/MoE/mHC 全 mock），生产化需定制 CUDA kernel 与分布式训练——本仓没有训练代码；② Engram-40B 未严格支配 27B（欠训练），记忆容量的饱和点未知；③ 只在 ≤40B/262B tokens 规模验证，百倍放大后 U 形最优 ρ 是否仍稳定待验；④ 与 RAG/kNN-LM 的边界（表是训练出来的静态参数，不能在线更新知识）。后续：论文结语自陈"条件记忆是下一代稀疏模型不可或缺的建模原语"——与 DSA（算的稀疏）合流即是社区对 V4 架构的预期方向（DSA 长上下文 + Engram 查表 + MoE 三稀疏轴并存）。

## 7. 与代码的对照（`engram_demo_v1.py`，423 行单文件）

| 论文概念（公式号） | 代码位置 |
|---|---|
| Tokenizer Compression（§2.2） | `CompressedTokenizer`：`normalizers.Sequence(NFKC→NFD→StripAccents→Lowercase→空白归一→哨兵保护纯空格 token)`，`_build_lookup_table` 建满射 old2new 表；乱码 token 回退原 ID |
| Multi-Head Hashing（式 1-2） | `NgramHashMapping`：`_get_ngram_hashes`——`mix = Σ tokens[k]*multipliers[k]`（XOR 累积，即 multiplicative-XOR）；`find_next_prime` 为每阶每头生成**互异质数表大小**（`engram_vocab_size=[129280*5]*2`，pad_id=2）；每层乘子由 `seed + 10007×layer_id` 派生（层间解耦） |
| 嵌入表拼接（式 2） | `MultiHeadEmbedding`：`offsets` 把各头各阶的质数表拼进一个大 `nn.Embedding`，`forward` 里 `ids+offsets` 一次查表 |
| Context-aware Gating（式 4/6） | `Engram.forward`：`key_projs[m]`（M=4 分支特异 W_K）+ `value_proj`（共享 W_V）；`gate = (normed_key*normed_query).sum(-1)/sqrt(d)`，随后 `abs().clamp_min(1e-6).sqrt()*sign()` 的**数值稳定化整形**（保号平方根压缩幅值）再 sigmoid——论文正文只写 σ(内积)，这是 demo 实现里的稳定技巧，读代码时勿疑公式对不上 |
| 短卷积（式 5） | `ShortConv`：`nn.Conv1d(groups=hidden*hc_mult)`（depthwise）、kernel=4、dilation=max_ngram_size=3、`[..., :T]` 截尾保因果、SiLU，外接残差 `value + short_conv(value)` |
| 残差集成与挂层 | `TransformerBlock.forward`：`engram(...) + hidden` 先于 attn/moe；`EngramConfig.layer_ids=[1,15]`（0 起数，对应论文 layers 2 & 15） |
| 配置 | `EngramConfig`：max_ngram_size=3、n_head_per_ngram=8、n_embed_per_ngram=512、tokenizer=DeepSeek-V3（vocab 129280）——与论文附录 A 的 27B 配置同构（表规模按 demo 缩小） |
| mock 部分 | `attn = lambda x: x`、`moe = lambda x: x`、超连接用 `unsqueeze(2).expand(...)` 模拟——README ⚠️ 所述"只为讲清 Engram 数据流" |

主程序用论文案例句 "Only Alexander the Great could tame the horse Bucephalus." 跑通前向，与论文 Figure 7 的 gating 可视化同一句——设计上的呼应，方便对照读。

## 8. 学习路径

1. **前置**：NN-gram 语言模型史（Bengio 2003 → Brants 2007 大规模 N-gram）、推荐系统高基数类别嵌入的哈希技巧（ROBE 等碰撞嵌入，§7.2 的对话对象）、DeepSeekMoE/稀疏激活、mHC（Xie et al. 2025，多分支残差）、Muon 优化器。
2. **精读顺序**：§1 二象性动机与 Diana 案例 → §2 架构四件套（compression/hashing/gating/conv）→ `engram_demo_v1.py` 全文对照（半日可全懂）→ §3 U 形分配律 → §4 主表 → §6 机制分析（LogitLens/CKA 是可复用的分析工具）→ §2.5 系统设计。
3. **复现建议**：
   - demo 单卡 CPU 即可跑（`pip install torch numpy transformers sympy`，需联网拉 DeepSeek-V3 tokenizer）；建议扩展：打印每 token 的 gate 值，在自己选的中英文句子上复现"gating 点亮实体/成语"现象（论文 Fig.7 的家庭版）；
   - 小规模重演 U 形：用 4 个 100M 级 MoE（不同专家数）+ 对应 Engram 表，固定 token 预算扫 ρ，画验证 loss 曲线（单机数天）；
   - 对照阅读 OverEncoding（Huang et al. 2025）与 SCONE（Yu et al. 2025）：同为大规模 N-gram 嵌入，一个走平均融合、一个推理侧 f-gram——理解 Engram 的差异化主张在"训练时一等公民 + 门控消歧 + 等算力对照"；
   - 与 DSA 精读（讲透DeepSeek-V3.2-Exp）连读：DSA=注意力轴稀疏、Engram=容量轴稀疏、MoE=计算轴稀疏，三者正交性是判断"V4 会长什么样"的思维框架。

（完）
