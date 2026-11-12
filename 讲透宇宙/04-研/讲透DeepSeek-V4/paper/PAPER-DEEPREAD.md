# DeepSeek-V4 论文精读（PAPER-DEEPREAD）

> 论文：*DeepSeek-V4: Towards Highly Efficient Million-Token Context Intelligence*，arXiv 2606.19348v1 [cs.CL]，DeepSeek-AI 集体署名（abs 页列名 319 位作者，report number 001），v1 钤记 2026-04-26。权重：`huggingface.co/collections/deepseek-ai/deepseek-v4`。官方"开源实现"脚注指向 HF checkpoint 仓 `DeepSeek-V4-Pro/tree/main/inference`，**无独立 GitHub 代码仓**（全文唯一 GitHub 引用=DeepGEMM PR #304，§3.1）。
> 对照素材：TRT-LLM blog26《DeepSeek-V4 on NVIDIA Blackwell》（本地 `/usr-data/data2/repos/agent-repos/NVIDIA/TensorRT-LLM/docs/source/blogs/tech_blog/blog26_*.md`，下称 blog26，按行号引用）；前传 blog15（V3.2）/blog17（sparse attention framework）。

---

## ① 一句话主张

**用"先压缩再稀疏"的 CSA/HCA 混合注意力把百万 token 上下文成本打掉一个数量级——1M 设定下 Pro 相对 V3.2 只需 27% 单 token 推理 FLOPs 与 10% KV cache（Flash 10%/7%）——以 mHC 残差流改造与 Muon 优化器为配套，代价是架构复杂度，以 preview 版发布 Pro 1.6T-A49B / Flash 284B-A13B 两个 MoE 模型**（Abstract, §1）。定位不是刷榜（推理追平 GPT-5.2/Gemini-3.0-Pro、落后 GPT-5.4/Gemini-3.1-Pro 约 3–6 个月，§5.3.2），而是把 1M 上下文从"能跑"变成"能 routinely 服务"，为 test-time scaling 与 long-horizon agent 铺路（§1）。

## ② 与 V3 / V3.2 的架构差异总表

| 维度 | V3（2024） | V3.2（2025） | **V4（2026）** |
| :--- | :--- | :--- | :--- |
| 注意力 | MLA 稠密，YaRN 扩 128K | DSA 单模式：Indexer 打分 + TopK **2048**（token 级） | **三模式逐层混排** SWA/CSA/HCA，由 checkpoint 的 per-layer compression-ratio 列表驱动（§2.3, §4.2.1；blog26 L82：Flash `[0,0,4,128,…]`、Pro `[128,128,4,128,…]`，0=纯 SWA 层） |
| 稀疏对象 | — | 原始 token 上选 top-2048 | 先把每 m token 压成 1 entry 再在**压缩条目**上选：CSA TopK=512(Flash)/1024(Pro)（§4.2.1） |
| 局部性 | 无 | 无 | CSA/HCA 层均附加 **128-token 滑窗分支**（`n_win=128`，§2.3.3）补压缩盲区 |
| 残差 | 标量残差流 | 同 V3 | **mHC**：残差流×4+双随机矩阵混合（§2.2） |
| MoE | 前 3 层 dense FFN+254 路由专家，8 激活 | 同 V3 | **全层 MoE**；前 3 层 **hash 路由**（token-ID 哈希表）；Sigmoid→**Sqrt(Softplus)**；去掉路由目标节点数限制（§2.1） |
| 优化器 | AdamW | AdamW | **Muon 为主**（embedding/pred head/RMSNorm 仍 AdamW，§2.4） |
| 精度 | FP8 训练 | FP8+indexer FP8 | MoE 梯度随机舍入 BF16；发布 **routed experts MXFP4**+indexer QK FP4 QAT（§5.2.1） |
| 上下文 | 128K | 128K | **原生 1M**（4K→16K→64K→1M，§4.2.2） |
| 规模 | 671B-A37B，61 层 | 同 V3 权重系 | **Flash 43 层 d=4096 284B-A13B；Pro 61 层 d=7168 1.6T-A49B**（§4.2.1） |

关键代际判断：V3.2 的 DSA 是"**在 token 级 KV 上做选择**"，V4 换成"**先压缩成 entry 再选择**"——选择坐标从 token 空间变成 1/m 压缩空间（blog26 L211 的 4× compressed coordinate space），且论文明说选了更小 top-k 以兼顾中短文本效率（§2.3.4）。首层配置：Flash 前两层纯 SWA、Pro 前两层 HCA，之后 CSA/HCA 交错（§4.2.1）——与 blog26 压缩比列表逐值吻合（双源互验）。

## ③ Compressor 数学：softmax-gated pooling 与双压缩流

Compressor 是 token 级、在线增量的"KV 池化器"，CSA 与 HCA 各有一套参数化（§2.3.1 式 9–12；§2.3.2 式 20–23）：

- **CSA（m=4，重叠感受野 2m）**：每个 token 经两个投影分支产出两套 KV 候选与打分 $C^a=HW^a_{KV},\ Z^a=HW^a_Z$ 与 $C^b=HW^b_{KV},\ Z^b=HW^b_Z$；对第 i 个输出，把**当前组**（$[mi,\ m(i{+}1)-1]$，a 分支）与**前一组**（$[m(i{-}1),\ mi-1]$，b 分支）共 **2m 个打分**加上可学习位置偏置 $B^a,B^b\in\mathbb{R}^{m\times c}$ 后做行 softmax：$S=\mathrm{Softmax}_{row}([Z^a_{mi:m(i+1)-1}+B^a;\ Z^b_{m(i-1):mi-1}+B^b])$，再加权求和 $C^{Comp}_i=\sum_j S^a_j\odot C^a_j+\sum_j S^b_j\odot C^b_j$。相邻输出共用一半原始 token → 相邻条目重叠 m 个位置，**有效感受野 2m=8**（blog26 L107 的工程表述："Consecutive outputs overlap by m raw-token positions through separate projection branches"）。直觉：相邻压缩块共享信息，缓解 4× 有损压缩的边界断裂。
- **HCA（m′=128，不相交窗）**：单分支 $C=HW_{KV},\ Z=HW_Z$，$S=\mathrm{Softmax}_{row}(Z+B)$（m′ 个元素），同样加权求和（式 20–23）。不做重叠压缩（§2.3.2），128× 极限压缩下重叠的冗余不划算，靠稠密attend全量条目兜底。
- **Indexer（CSA 专属）**：低秩 indexer query（式 13–14），得分 $I_{t,s}=\sum_h w^I_{t,h}\cdot\mathrm{ReLU}(q^I_{t,h}\cdot K^{IComp}_s)$（式 16，ReLU 打分），Top-K 选择器保留压缩 KV 子集（式 17）。**CSA 层因此维护双压缩流**：注意力 KV entry 流 + Indexer key 流（同一压缩算子在 Indexer 内再跑一遍产 K；blog26 L107/L137：两条流各自 dtype 与缓存布局不同）。
- **配套细节**（§2.3.3）：query/KV 双 RMSNorm 防 logits 爆炸（故无需 QK-Clip，§2.4）；部分 RoPE 只施最后 64 维，输出 $o_{t,i}$ 施位置 $-i$ 的 RoPE 得相对位置；attention sink——每头可学习 sink logit $\mathrm{Exp}(z'_h)$ 加进 softmax 分母（式 27）。工程侧（blog26 L109/L233）：FP32 状态缓冲暂存未闭合窗口的投影，窗口闭合在线 finalize，保"整序列一次压缩"语义，吸收 chunk 边界错位。

## ④ mHC 摘要（详读留给 2512.24880 专门篇）

mHC（Manifold-Constrained Hyper-Connections，§2.2；专门论文 arXiv 2512.24880）把残差流加宽 $n_{hc}=4$ 倍，每个子层边界经三段动态映射：**pre-mapping** $A_l=\sigma(\tilde A_l)$ 读子层输入；**residual-mixing** $B_l$；**post-mapping** $C_l=2\sigma(\tilde C_l)$ 写回。Sigmoid 约束保证 A/C 非负有界（式 6–7）。核心在 $B_l$：投影到**双随机矩阵流形**（Birkhoff polytope，式 2）——谱范数 $\|B_l\|_2\le 1$（非扩张）且对乘法封闭，深层堆叠不放大扰动。实现用 Sinkhorn-Knopp：$M^{(0)}=\exp(\tilde B_l)$ 后迭代行列归一化，$t_{max}=20$（式 8）。动态参数化（式 3–5）：映射参数=动态分量（RMSNorm 后 $\hat X_l$ 乘 W）+静态偏置 S，再乘门控 α。

工程代价：融合 kernel+选择性重计算+改造 DualPipe 1F1B 后，训练 wall-time 开销压到 **6.7%**（§3.4.2）；输出维仅 24 的矩阵乘走确定性 split-k（§3.3）。推理侧（blog26 L113/L239-241）：每层两个 mHC 模块+LM head 前 **HC head** 折叠回单流；相邻 post/pre 融合并吃掉下层 RMSNorm，小 M 用 FMA、大 M 用 MMA 自动调优——与 6.7% 是训练/推理两个语境（见勘误 7）。

## ⑤ MoE：Flash 256 / Pro 384 专家、6+1 激活、前三层 hash 路由

- **配置**（§4.2.1）：Flash 每层 1 共享+256 路由专家（中间维 2048），Pro 1 共享+384（3072），每 token 激活 6 路由+1 共享。全部 Transformer block 皆 MoE——V3 的"前 3 层 dense FFN"改为 **MoE+hash 路由**：路由目标由 checkpoint 内置 token-ID→专家哈希表决定（§2.1；blog26 L115）。论文未给动机；合理推断是浅层表示未分化、学习型路由噪声大易失衡，hash 免学习且按 token-ID 均匀散列天然负载均衡（推断，非论文论断）。
- **路由亲和度**：Sigmoid 换成 **Sqrt(Softplus(·))**（§2.1）；沿用 auxiliary-loss-free 负载均衡（bias 更新速度 0.001）+ 序列级平衡损失（权重 1e-4，§4.2.2）；**移除了路由目标节点数限制**并重设计 EP 并行策略。
- **后层学习型路由**（blog26 L115）：Sqrt-Softplus 打分 + score-correction bias（即 aux-loss-free 的 bias 修正项）+ Top-6 选择。
- **训练侧配套**（§4.2.3）：**Anticipatory Routing**——骨干网用当前参数 $\theta_t$ 算特征、路由索引用历史参数 $\theta_{t-\Delta t}$ 预计算缓存，解耦两者的同步更新显著改善稳定性；常开 wall 开销约 20%，靠"loss spike 自动检测→短暂回滚→仅尖峰期启用→恢复"把总体开销压到可忽略。**SwiGLU Clamping**——线性分量夹到 [−10,10]、gate 上限 10（引 OpenAI 2025），消除 outlier 稳住训练。
- **通信**（§3.1）：细粒度 EP 把专家切 wave 调度，wave 内通信完即开算，计算/token 传输/结果回传三路流水；带宽-算力平衡点 $C/B\le 2d=6144$ FLOPs/Byte。开源落点 DeepGEMM PR #304（MegaMoE），通用推理 1.50–1.73×、RL rollout/agent 延迟敏感场景最高 1.96×（§3.1）。

## ⑥ 训练与规模：Flash 284B-A13B / Pro 1.6T-A49B、FP8 训 FP4 发

- **模型超参**（§4.2.1）：Flash 43 层 / d=4096 / query heads 64 / head dim 512 / $d_c$=1024 / 输出投影组 g=8；Pro 61 层 / d=7168 / heads 128 / $d_c$=1536 / g=16；两者 CSA indexer 均 64 头×128 维、MTP depth=1、mHC 4×/SK 20。
- **数据与调度**（§4.1, §4.2.2）：语料 >32T token（数学/代码/网页/长文档）；Flash 32T、Pro 33T；batch 升到 Flash 75.5M / Pro 94.4M 保持；LR Flash 2.7e-4→2.7e-5、Pro 2.0e-4→2.0e-5 余弦退火；序列 4K→16K→64K→1M；**前 1T token 稠密注意力 warmup，64K 阶段引入稀疏并保持**（indexer 先短阶段单独 warmup，两段式）；sample-level attention masking 替代 V3 的 packing 截断；MTP loss 0.3，LR 退火后降 0.1。
- **Muon**（§2.4, §3.4.1）：动量 0.95、wd 0.1、更新矩阵 RMS rescale 0.18 以复用 AdamW 学习率量级；Newton-Schulz 共 10 次迭代混合系数——前 8 次 (3.4445, −4.7750, 2.0315)、后 2 次 (2, −1.5, 0.5)；NS 迭代 BF16 稳定计算（QK RMSNorm 防爆后无需 QK-Clip）；MoE 梯度随机舍入到 BF16。embedding/预测头/mHC 静态偏置与门控/RMSNorm 权重走 AdamW。
- **发布精度**（§1, §5.2.1）：post-training 做 **FP4(MXFP4) QAT**，覆盖 MoE 专家权重（显存大头）与 CSA indexer QK 路径（激活全 FP4 缓存/加载/乘法），index 分数 FP32→BF16。论文指出 FP4×FP8 当前硬件峰值与 FP8×FP8 相同，收益在带宽与显存，未来硬件理论再快 1/3。blog26 L77-80 精度口径：Base 模型 FP8 mixed，Instruct 模型 FP4+FP8 mixed。
- **后训练管线**（§5.1）：两阶段——先按域（数学/代码/agent/指令遵循）独立训专家模型（SFT+RL，含 Generative Reward Model、Tool-Call Schema 特殊 token），再多教师 **On-Policy Distillation** 统一合并（full-vocabulary OPD，教师可无限多，§5.1.2）。推理档位 Non-think/High/Max（Table 2/3）：RL 各配长度惩罚与上下文窗（8K/128K/384K），Max 档加专用系统 prompt。**Interleaved Thinking 升级**（§5.1.1）：不同于 V3.2 在新 user turn 丢弃推理痕迹，V4 全程保留跨轮 reasoning 历史，靠 1M 窗口吃下累积思维。**Quick Instruction**：附加专用特殊 token 复用已算 KV 并行执行辅助任务（搜索 query 生成等），砍掉独立小模型的冗余 prefill 降 TTFT（Table 5）。

## ⑦ 实验关键数字

**效率（论文核心卖点，Abstract/§1/§2.3.4）**
- 1M 上下文 vs V3.2：Pro 单 token 推理 FLOPs **27%**、KV cache **10%**；Flash **10%**/**7%**。
- KV cache ≈ BF16 GQA8（head dim 128）基线的 **2%**（§2.3.4）。
- infra：MegaMoE 细粒度 EP 通用 1.50–1.73×、agent/RL rollout 最高 **1.96×**（§3.1）；TileLang host codegen 把 CPU 校验从几十/上百 µs 压到 **<1µs**（§3.2）；top-k 选择器优化 2× 加速且保持 99%+ 一致性（§3.4）。

**能力（§4.3 base / §5.3 post / §5.4 真实任务）**
- 知识：Pro-Max 在 SimpleQA/Chinese-SimpleQA 显著领先开源；MMLU-Pro/HLE/GPQA 小幅领先开源，仍落后 Gemini-3.1-Pro（§5.3.2）。
- 推理：Pro-Max 超 GPT-5.2 与 Gemini-3.0-Pro，落后 GPT-5.4/Gemini-3.1-Pro 约 **3–6 个月**；Flash-Max 代码/数学超此前最佳开源 K2.6-Thinking（§5.3.2）。
- Agent：Pro 与 K2.6/GLM-5.1 相当，开源整体落后闭源；Pro 在 MCPAtlas、Toolathlon（跨工具泛化集）突出；Flash 明显弱于 Pro（Terminal Bench 2.0 尤甚）；§1 自述内部评测超 Sonnet 4.5、接近 Opus 4.5。
- 1M 长上下文：MRCR+CorpusQA 上 Pro 超 Gemini-3.1-Pro（Abstract/§5.3.2，Figure 9）。
- 档位效应：Max（更长上下文+更低长度惩罚）在最难任务上超 High；HLE 上 Pro 比 V3.2 token 效率更高（Figure 10）。
- 真实任务（§5.4）：中文写作强在 Task Completion/Content Quality、主动预判隐含意图，偶漏细节指令；Agentic Search 平均 16.2 次并行工具调用（Table 10）；内部 V4 vs V3.2 搜索问答 V4 胜率 50–72%（Table 11）；开发者调查 52% 愿以 Pro 为默认主力编码模型、39% 倾向愿意、<9% 拒绝。

## ⑧ 系统落地视角（blog26 对照，NVIDIA Blackwell/GB300）

**Day-0 栈**：TRT-LLM 以 PyTorch 后端 `DeepseekV4ForCausalLM`+专用 sparse-attention 后端+`DeepseekV4CacheManager` 支持 SM100+（L71）；注意力布局从 checkpoint 元数据读取而非硬编码（L82）。

**KV 双池缓存**（L134-150）：V4 把"KV cache"拆成生命周期不同的状态族——滑窗池（SWA KV+Compressor KV/score 短命状态；HCA 128、CSA 8 个原始位置窗口，L144）与持久压缩池（4×/128× 压缩条目+CSA 压缩 Indexer-K，随序列长度增长）。页分配保持**原始 token 坐标**，压缩缓冲按 `tokens_per_block/r` 存条目，前缀复用/容量核算共用一套页模型（L146）；`pool_ratio` 分层组配比+beta rebalancer（默认关）；SWA scratch reuse 让长 prefill 各 SWA 层复用同一物理 scratch（L261）。

**双池 MLA kernel 与热路径**（L101-103, L199-217）：统一 dual-pool 算子先滑窗再压缩流、一次 online-softmax 归约；per-query `topk_lens` 适配变长负载。B200 FMHA 优化后 1.31×（CSA prefill）/1.21×（HCA decode）；Q RMSNorm+RoPE+FP8 量化融进 producer；逆 RoPE+FP8 量化 standalone 1.6–2.3×、并入 FMHA epilogue 后 1.62×/1.34%；Top-K device-aware（K=512、196608 列、bsz148：384µs→112µs）+ **GVR**（相邻 decode 步选择重叠，blog21 引入）扩到 4× 压缩坐标空间，kernel-only 1.40–2.17×，Flash 8×B300 65K 输入端到端 +6.4%；三流注意力调度+Indexer 嵌套并行。

**Compressor/mHC/MoE kernel**（L225-251）：`wkv_gate` 单投影出 KV+打分；压缩/状态更新/后处理各融一刀；mHC 相邻 post+pre 融合并吃掉下层 RMSNorm；MoE router GEMM 1–16 行 8µs→3µs；**MXFP8×MXFP4 DeepGEMM MegaMoE** 融合通信路径 500 请求实测吞吐 +15.3%/延迟 −12.7%；NVFP4 MegaMoE WIP。

**精度配方**（L166-178）：FP8 Base / MXFP4 Instruct / NVFP4 requant 三配方表；indexer weights 投影与 Compressor KV/score 线性层全程 BF16；Compressor 状态 FP32；Indexer-K 缓存默认 MXFP4（FP4 约省一半载荷）。精度验证 GPQA-Diamond：Flash 88.8 / Pro 89.08 / Pro 分离部署 89.39 / Pro-NVFP4 89.39（MTP-3、FP8 KV，L182-188）——NVFP4 requant 无精度损失。

**GB300 性能演化**（L276-317）：Pro 8K/1K 固定形状、MXFP4、分离部署 Pareto 扫描，四个里程碑 984→1167→1505→**1618 tok/s/GPU**（+64.5%）：4/28 基线（功能性）→5/8（Top-K+Compressor，+18.6%）→5/18（MegaMoE+EPLB+mHC 融合，+29.0%）→5/28（注意力 overlap+逆 RoPE/PDL，+7.5%）。此后更新未计入。

**Agentic 工作负载**（Part II, L322-458）：AA-AgentPerf 闭环多轮 agent 回放；两级路由（orchestrator 选 CTX 实例+ADP router 选 rank，conversation-aware 或 KV-cache-aware，L367-399）；滑窗缓存 `per_request` 生命周期+pool_ratio 手调（L407-409）；host 路径去 Python 化（按 block 哈希、C++ 哈希器、msgspec、CTX 回传 token ID 免 GEN 重复分词，L421-431）。终局：GB300 NVL72 上 **SLO20（≥20 tok/s、P95 TTFT≤10s）57.5 CPG**（1840 并发/32 GPU，6×CTX DEP4+1×GEN DEP8）、**SLO60（≥60 tok/s、≤5s）19.2 CPG**（768/40，DEP16），Artificial Analysis 复测验证（L451-456）。

## ⑨ 局限与批评

1. **preview 定位 + 架构复杂度自认**（§6）：自述"bold architectural design…retained many preliminarily validated components and tricks…made the architecture relatively complex"，未来要蒸馏到最简必要设计；Anticipatory Routing 与 SwiGLU Clamping 有效但"underlying principles remain insufficiently understood"——万亿 MoE 训练稳定性仍是黑箱止痛。
2. **前沿差距仍在**（§5.3.2）：知识榜落后 Gemini-3.1-Pro；推理落后 GPT-5.4/Gemini-3.1-Pro 约 3–6 个月；agent 开源阵营整体落后闭源；Flash 与 Pro 知识面差距大、agent 能力（尤其 Terminal Bench 2.0）明显弱于 Pro。
3. **评测卫生瑕疵**：GPT-5.4 因 API 无响应缺席 1M 重评（§5.3.1）——头对头长上下文对比实际只剩 Gemini-3.1-Pro 与 Claude Opus 4.6；K2.6/GLM-5.1 部分 agent 条目因 API 繁忙留空；Terminal Bench 2.0 已知环境问题仍按原始集报告（§5.3.1）。
4. **效率红利的系统代价**：SWA KV 未压缩且每层都有，体积约为压缩条目 **8 倍**（§3.5.2），磁盘缓存三策略在存储与重算间取舍；mHC 训练 6.7%、AR 常开 20%；hash 路由动机论文未解释（见 ⑤）。
5. **部署侧未竟事项**（blog26 L251, L470-484）：NVFP4 MegaMoE WIP；Hopper 待扩展；KV Cache Manager V2 热路径仍 Python；DSPark 集成验证中。
6. **host offloading 负结果**（blog26 L411）：V4 每 token KV 足迹小到 host KV 卸载与增量 CTX→GEN 传输**都无有意义的端到端收益**——架构级压缩预先吃掉了系统层优化空间；该负结果不可外推到重 KV 模型。
7. **真实用户反馈**（§5.4）：trivial mistakes、模糊 prompt 误读、偶发 over-thinking、偶漏格式指令。

## ⑩ 与本地资产关系

- **无 GitHub 代码仓（钉版）**：论文脚注 1 的 open-source implementation = HF checkpoint 仓 `DeepSeek-V4-Pro/tree/main/inference`（HTML href 实证）；全文唯一 GitHub 引用=DeepGEMM PR #304（§3.1）。读官方实现去 HF 仓 inference/ 目录。
- **TileKernels 有 mHC 算子**（钉版）：DeepSeek 开源 infra 家族的 TileKernels 仓含 mHC 实现，对应论文 §3.4.2 融合 kernel 叙事，是 mHC 代码对照入口。
- **TRT-LLM day-0 支持**：本地 `/usr-data/data2/repos/agent-repos/NVIDIA/TensorRT-LLM`（blog15/17/26 在 `docs/source/blogs/tech_blog/`）；V4 sparse attention 后端长在 blog17 的通用稀疏注意力框架上（选择逻辑与后端解耦，blog26 L86），DSA→V4 是同一框架两代实例。
- **前传档案**：`~/ai/work4ai/讲透DeepSeek-V3.2-Exp/paper/PAPER-DEEPREAD.md`（V3.2=DSA、TopK 2048）；blog15 是 V3.2 Blackwell 优化实录（Top-K 确定性/radix-select 源头）。

## ⑪ 勘误与口径差（论文 vs blog26 / 元数据）

1. **SWA 的"三分框架"是部署侧表述**：论文 §2.3.3 把滑窗定义为 CSA/HCA 的**附加分支**（非独立层型）；blog26 L88-92 把 ratio=0 的层升格为独立 attention mode "SWA"。数值一致（Flash 前两层 `[0,0]` = 论文"first two layers pure SWA"，§4.2.1），语义框架不同——引用时注意论文口径里"纯 SWA 层"是"只有分支没有主干"的退化情形。
2. **Pro 首两层交叉验证通过**：论文 §4.2.1 "For the first two layers, we use HCA" ↔ blog26 L82 Pro 列表 `[128,128,4,128,…]`（128=HCA 压缩比）。非矛盾，是双源印证。
3. **训练 token 口径**：摘要/§1 "more than 32T"（统一口径）vs §4.2.2 精确值 Flash **32T** / Pro **33T**。引精确数字以正文为准。
4. **DSPark 是 checkpoint 生态，不在论文内**：blog26 L124 提 DeepSeek 另发 DSpark 投机解码 checkpoint（arXiv 2607.05147）；论文全文零提 DSpark（grep 实证），论文侧只有 MTP depth=1（§4.2.1）。两者的投机解码叙事不可混引。
5. **NVFP4 非官方发布口径**：论文只讲 MXFP4 QAT（§5.2.1）；blog26 L178 的 NVFP4 是 NVIDIA requantized checkpoint（`nvidia/DeepSeek-V4-Pro-NVFP4`，MTP 子树保留 Instruct 配方）。"V4 发布 FP4"应表述为"Instruct 模型 routed experts MXFP4"。
6. **GB300/Blackwell 字样论文零出现**（grep 实证）：1618 tok/s/GPU、57.5/19.2 CPG 等系统数字全在 blog26；论文效率主张止于 FLOPs/KV 百分比与 2% 基线。
7. **mHC 开销数字不同语境**：论文 6.7%（§3.4.2）=训练侧 overlapped 1F1B 流水阶段；blog26 L239-241 =推理侧 kernel 融合。不可互引。
8. **arXiv 元数据错位**：编号 2606.19348 落 2026 年 6 月编号段，而 abs 页与 HTML 钤记均为 **2026-04-26 v1**（唯一版本）。引用以 v1 钤记日期为准并注明错位。
9. **hash 路由"前三层"计数对象不同**：论文 §4.2.1 "first 3 **MoE layers**"（全块 MoE 时等价于前 3 层）vs blog26 L115 "first three layers"。对比 V3 时注意其对象是"前 3 层 dense FFN"。

---

*方法记录：arXiv abs+HTML 双通道（WebFetch + curl 拉 918KB HTML 转 191K 文本锚点提取）；blog26 全文直读。论断锚=论文节号/式号，系统锚=blog26 行号。2026-11-04 成稿。*



