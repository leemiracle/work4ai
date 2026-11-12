# DSpark 深度精读：半自回归生成 + 置信度调度验证的投机解码

> 论文：**DSpark: Confidence-Scheduled Speculative Decoding with Semi-Autoregressive Generation**
> arXiv 2607.05147v1 [cs.AI，cross-list cs.CL]，2026-07-06 提交，376KB，CC BY 4.0
> 作者 33 人：Xin Cheng（北大）领衔，梁文锋、胡师帅等 DeepSeek-AI 全班底——北大×DeepSeek 联合工作（与 Engram/DSE 同款合作模式）
> 锚约定：论文内论断标 §节/Eq式/Table表/Fig图；本地仓论断标 `文件:行号`

---

## ① 一句话主张与发表信息

**一句话主张**：DSpark 把并行起草（parallel drafting）的"快"与串行依赖建模的"准"缝合在一起——用一个**并行骨干 + 轻量串行头**的半自回归架构治好并行 drafter 的"尾部衰减"病，再用**逐请求置信度调度的验证长度**治好"大块验证在高并发下浪费 batch 容量"病，最终在 DeepSeek-V4 生产流量上以同吞吐换取**每用户 60–85% 提速**（§5，vs MTP-1 基线），把 serving 系统的 Pareto 前沿整体外推。

这不是一篇单纯的算法论文，而是**算法（架构+损失）× 系统（调度器+kernel）× 生产部署（V4 全量流量）**三位一体的工作——三个弱点各对应一根支柱：架构治 acceptance 衰减（§3.1）、调度治容量浪费（§3.2）、部署给出真实 SLO 约束下的收益（§5）。作者明言部署在 DeepSeek-V4-Flash 与 V4-Pro preview 的在线 serving 系统（§5 开篇），且 DSpark 在 V4-preview 发布两周后替换了 MTP-1 基线（§5.2）。

## ② 动机：并行起草快，但块内依赖建模弱

投机解码的每 token 延迟目标函数是全文的公理起点（§3, Eq. 1）：**L = (T_draft + T_verify)/τ**——τ 为每周期接受 token 数。两个流派分别卡在这条式的两端：

- **串行 drafter（Eagle/Eagle3、MTP）**：token 逐个生成，块内依赖建模强，但 γ 个 draft token 要跑 γ 次串行前向，T_draft 随块长线性涨，且推理 batch 维度天然闲置——起草不并行就是浪费算力；
- **并行 drafter（Medusa、DFlash 等）**：一次前向吐出整块 draft，T_draft 低且吃满 batch，但所有位置**条件独立**——第 k 个 draft token 看不到前 k−1 个 draft token，块越长猜得越飘。

论文用逐位置条件接受率把这个病量化了（§4.3.1, Fig. 2，Qwen3-4B）：并行 drafter DFlash 在位置 1 很强（Math 0.88 vs Eagle3 的 0.81；Chat 0.72 vs 0.53），但随位置衰减（Code 0.87→0.78，Chat 0.72→0.63）；Eagle3 反向爬升（Chat 0.53→0.74）。**这就是"suffix decay"（尾部衰减）**：并行 drafter 赢在开头、输在结尾。DSpark 起点即 0.93（Math）且全程稳定（Fig. 2）。

第二个动机在系统侧：静态验证长度在高并发下是毒药。验证 γ 个 token 占用的 batch 容量是 γ+1 个槽位，接受率低时这些槽位白白烧掉——论文明确指出 oversized blocks "waste batch capacity under high concurrency"（Abstract），并记录静态多 token 变体（MTP-3/5）在高并发下吞吐退化（§6 baseline 段）。所以第二根支柱是**按前缀存活概率逐请求决定验证长度**（§3.2）。

**与三代投机解码路线的对比表**（综合 §2/§6 论述）：

| 方案 | 起草方式 | 块内依赖 | 起草延迟 | 精确无损 | 短板 |
|---|---|---|---|---|---|
| MTP（V3/R1，串行链） | 逐 token 串行，链式模块 | 强（自回归） | 高（γ 次前向） | ✓ | T_draft 线性涨；生产只敢开浅（V4 用 MTP-1/3） |
| Eagle/Eagle3（自回归头） | 逐 token 串行，特征级输入 | 强 | 高，但 TTT 训练学得准 | ✓ | 同上；首位置反而弱于并行 drafter（Fig. 2） |
| Medusa/DFlash（并行） | 一次前向整块 | **无**（条件独立） | **低** | ✓（逐位置重采样） | suffix decay；DFlash 靠 KV 注入已是最强并行，仍被 DSpark 反超 16–18%（Table 1） |
| CRF-NAT / CTC drafter | 非自回归整块 | 全局归一化建模 | 低 | **✗**（§6：给不出精确逐 token 概率，全局归一/边缘化破坏无损拒绝采样） | 不可用于严格无损场景 |
| **DSpark** | 并行骨干+串行头 | **强**（Eq. 4 逐位置条件分解） | 低（骨干 1 次前向，串行头开销 0.2–1.3%，§4.3.2） | ✓（局部 softmax，§6） | 固定整块起草算力不可回收（§5.4，见⑥） |

定位一句话：DSpark = DFlash 的并行骨架 + Eagle 的依赖建模语义 + Medusa 时代不敢想的系统级调度——三者都不新，缝在正确的位置才新。

## ③ 方法核心：并行骨干 + 串行头，公式主线

### 3.1 半自回归架构（§3.1）

**并行骨干**直接建在 DFlash 上（§3.1）：DFlash 的输入是"锚点 + γ−1 个 mask token"，只在锚点位置出一个预测（§2.2）；DSpark 的手术只有一处——**把锚点位置改为第一个预测位**，于是 γ 个输入 token（1 锚 + γ−1 mask）一次前向产出 γ 个 draft logit 向量 U₁…U_γ。骨干的 KV 注入沿用 DFlash（§2.2, Eq. 2–3）：上下文隐状态经 RMSNorm 投影拼接进 drafter 每层的 K/V——这就是"目标模型知识"进入 drafter 的通道，也是起草质量不塌的底座。

**串行头**是本文的核心公式（§3.1, Eq. 4）：把整块联合分布改写为自回归分解

$$P(X \mid x_0) = \prod_{k=1}^{\gamma} p_k(x_k \mid x_0, x_{<k}), \quad p_k(v) = \frac{\exp(U_k(v) + B_k(x_0, x_{<k}, v))}{\sum_{u \in \mathcal{V}} \exp(U_k(u) + B_k(x_0, x_{<k}, u))}$$

其中 x₀ 是上一验证周期幸存的锚 token。妙处在于**分工**：U_k（骨干并行产出）承担"这个位置大概是什么"的语义先验；B_k（串行头递归产出）承担"给定前面 draft token 选了什么，这里该修正成什么"的转移偏置。两者相加进同一 softmax，**局部归一化保住了精确逐 token 概率**——这是 §6 强调与 CRF-NAT/CTC 的本质区别，无损拒绝采样的前提。

串行头两档配置（复杂度递增）：

- **Markov 头**（Eq. 5）：一阶转移 B(x_{k−1},·) = W₁[x_{k−1}]W₂，低秩分解 W₁∈ℝ^{V×r}（embedding 查表）+ W₂∈ℝ^{r×V}（logit 投影），默认秩 r=256。两个矩阵乘法级别的小操作，生产部署用的就是它（§5：V4 上 γ=5 的 "DSpark-5" 配 Markov 头）。
- **RNN 头**（Eq. 6）：输入拼接 z_k = [s_{k−1}; W₁[x_{k−1}]; h_k] ∈ ℝ^{2r+d}（上一步状态 + 当前 token embedding + 骨干隐状态），门控更新 s_k = σ(W_g z_k)⊙s_{k−1} + (1−σ(W_g z_k))⊙tanh(W_c z_k)，偏置 B_k = W₂^T tanh(W_o z_k)。三个投影矩阵从同一个线性层切分，s₀=0。

Draft 模型与目标模型**共享 embedding 层与 LM head，且都冻结**（§3.1/§3.3）——参数经济性拉满，串行头本体只有 r=256 秩的几个小矩阵。

### 3.2 置信度调度验证（§3.2）

**置信度头**（§3.2.1, Eq. 7）：c_k = σ(w^T[h_k; W₁[x_{k−1}]])——串行头的中间量顺手估计"**给定前缀全部被接受**，第 k 个 draft token 幸存验证的条件概率"。训练标签不是拍脑袋的 0/1，而是**全变差距离的解析接受率**（Eq. 8）：c_k* = 1 − ½‖p_k^d − p_k^t‖₁（draft 分布与目标分布的 TV 距离补数）——这个标签在贪心验证下就是接受概率的解析式，理论干净。

**校准（STS）**：前缀存活概率是连乘 a_{r,j} = ∏_{i≤j} c_{r,i}，原始头 ROC-AUC 0.81–0.90 但 ECE 3–8%，连乘会放大偏差；**Sequential Temperature Scaling** 自左向右逐位置做一维网格搜索，最小化累积乘积的 ECE，校准后平均 ECE ≈1%（§4.3.3, Fig. 5），且保序（排名不乱，调度只看排名）。

**调度器**（§3.2.2, Algorithm 1）：把验证长度选择形式化为最大化 **Θ = τ·SPS(B)**——τ = Σ_r(1 + Σ_{j≤ℓ_r} a_{r,j}) 是批期望接受数，SPS(B) 是**初始化时一次性 profile 的引擎 steps-per-second 曲线**（成本表），B = Σ_r(1+ℓ_r) 是批大小。贪心解法：所有 (请求, 位置) 对按 a_{r,j} 降序排，逐个准入更新 Θ，Θ 回落即早停（早停全局最优当且仅当 Θ 单峰）。**关键纪律是非前瞻性（non-anticipating）**：调度只准用置信度，不准偷看目标模型对本轮 draft 的验证结果——Appendix A 给了反例，回溯式选择会泄漏 x_{r,k} 使选择偏差破坏无损性。

**训练**（§3.3, Eq. 9–12）：目标模型冻结，随机采样锚点构造 γ-token 块；三路损失按位置权重 w_k = exp(−(k−1)/γ)（前重后轻）加权——交叉熵（Eq. 9，α_ce=0.1）+ **TV 分布匹配**（Eq. 10，α_tv=0.9，直接最大化期望接受率的解析量）+ 置信头 BCE（Eq. 11，α_conf=1.0）。TV 损失权重 9 倍于 CE，再次印证"接受率才是第一性目标"。

## ④ 实验数字：离线基准与生产部署

**离线设置**（§4.1）：目标模型 Qwen3-4B/8B/14B + Gemma4-12B；块长 γ=7 统一；Eagle3（1 层，TTT horizon 7）与 DFlash（5 层）同框架同数据重训保证公平；数据 Open-PerfectBlend 1.3M 样本（chat 17.6% / math 39.4% / code 38.9% / IF 4.1%），非思考模式温度 1.0 重生成回复，10 epochs。离线实验关闭调度器（纯比 drafter 质量）。

**接受长度 τ**（Table 1，含 bonus token）——数字模式高度一致：**math/code 强（GSM8K 6.05–6.21、HumanEval 5.38–5.64，γ=7 意味着理论上限 8），开放对话弱**（MT-Bench 3.49–3.72、Arena-Hard 2.92–3.29）——确定性强的域并行起草最受益。宏平均增益：**vs Eagle3：+30.9%（4B）/ +26.7%（8B）/ +30.0%（14B）；vs DFlash：+16.3% / +18.4% / +18.3%**——对最强并行 drafter 还有近两成增益，串行头确实补到了实处。

**消融**（§4.3.2）：(a) **2 层 DSpark 全面胜 5 层 DFlash**——依赖建模的价值可以折算回骨干层数；(b) 块长扩展收益加速：γ=7 时 vs DFlash +16%（math）/+15%（code）/+18%（chat），**γ=15 时 +30%/+26%/+22%**——suffix decay 被治好后，更长块的红利才兑现（这正是并行 drafter 此前不敢开长块的原因）；(c) 串行头延迟开销仅占整轮延迟 **0.2%–1.3%**（batch 128，上下文 512–4096）——近三成接受率提升的代价百分之一出头。

**置信度质量**（§4.3.3, Fig. 5）：按置信度分层后实测接受率 Chat 45.7%→95.7%、Math 76.9%→92.5%、Code 67.6%→92.0% 单调爬升——置信度确实是接受率的可靠代理，这是调度器可用的经验证据。

**DeepSeek-V4 生产部署**（§5）：
- 配置：DSpark-5（γ=5）+ Markov 头；骨干 3 层 MoE（mHC + 128 滑窗注意力）；基线是生产中的 MTP-1（静态单 token）。
- **V4-Flash**：80 tok/s/user SLA 下聚合吞吐 +51%；120 tok/s/user 名义吞吐高 661%（作者自己注明这是前沿外推口径——MTP-1 在该区段已退化为低并发形态）；**同吞吐下每用户提速 60–85%**。
- **V4-Pro**：35 tok/s/user 下 +52%，50 tok/s/user 名义 +406%（同上口径）；**每用户提速 57–78%**。
- **负载自适应预算**（Fig. 8）：轻并发（Flash<200 / Pro<150 并发请求）时验证预算自动扩到 **4–6 token**（MTP-1 静态才 2），重载下平滑收缩——调度器真的在流量里做决策，不是离线摆设。
- 工程代价可控：kernel 改动限于 index-attention 与 compress kernel（变长路由经 marker tensor 进稀疏注意力，§5 末）。
- 生产训练（HAI-LLM，§5.1）两招：(a) 隐状态通信——跨 worker 只传 pre-LM-head 激活，每 token 通信量 O(d)，LM head 投影在 draft worker 本地算；(b) 锚点有界序列打包 + token 级注意力索引实现无 padding 的精确因果掩码。

## ⑤ 与 V4 MTP 的关系：MTP-3 是 TRT-LLM 默认，DSpark 是 tuning 中的替代路径

DSpark 论文内部把 MTP-1 称为"production baseline"（§5），但**DeepSeek 自家 serving 与 NVIDIA TRT-LLM 栈的现状不同**，两条线要分开看：

1. **DeepSeek 官方线上**：DSpark 在 V4-preview 发布两周后直接替换 MTP-1（§5.2）——官方路径已完成切换。
2. **TensorRT-LLM（blog26）**：V4 checkpoint 的 MTP 层走 **Eagle 式 one-model 路径**（每个 MTP 模块吃目标模型/上一 MTP 模块的扩展残差态 + 下一 token embedding，跑同款 mHC 包裹的注意力+MoE 结构，注意力用 SWA；TRT-LLM 重映射 MTP 权重、与目标模型共享 embedding/LM head）——`blog26:124`。该 blog 的性能数据全部用此 MTP 路径；且 **MTP-3 是多数延迟/中前沿点的默认配置，最高并发点退到 MTP-1**（`blog26:289` 扫描配置原话："MTP-3 for most latency and mid-frontier points and MTP-1 at the highest-concurrency points"；生产配置同样 MTP-3，`blog26:447`）——这与论文 §6 "静态 MTP-3/5 高并发吞吐退化"的论断互为印证：静态长度两头不讨好，DSpark 的动态调度正是解此题。同段确认 DeepSeek 已发布 V4 专属 DSpark checkpoint，"DSpark adds a lightweight sequential head to a parallel draft backbone to model dependencies within a draft block, **while performance tuning for this path remains in progress**"（`blog26:124`）——DSpark 在 TRT-LLM 是**替代路径且调优进行中**；Future Work 明列 "Add DeepSeek-V4 DSpark support"，剩余工作=测接受行为、调运行时配置、量化端到端收益（`blog26:482`）。
3. **TensorRT-Edge-LLM（端侧）**：DSpark 已实际落地非 DeepSeek 模型——0.10.0（2026/08）为 **Nemotron-3.5 Lightning** 加 DSpark（`README.md:22`），且 "Added DSpark speculative decoding with **DDTree drafting**"（`CHANGELOG.md:71`，0.10.0 段）；后续 "Expanded Nemotron and Gemma speculative decoding with DSpark, greedy trees, reduced-vocabulary chain MTP, and quantized drafts"（`CHANGELOG.md:16`）、Qwen3.8-27B DSpark hybrid-base 导出（`CHANGELOG.md:43`）、修 DSpark paged KV metadata（`CHANGELOG.md:57`）；能力总表与 EAGLE3/MTP/DFlash 并列（`docs/source/overview.md:70`）。**端侧反而比数据中心栈更快用上 DSpark**——侧面说明其串行头之轻（r=256 低秩）适配边缘算力。

演进线收束：**V3/R1 MTP（串行链、逐 token）→ Eagle 式（TRT-LLM 把 V4 MTP 层跑成 Eagle one-model 路径，`blog26:124`）→ DSpark（并行骨干+串行头+动态调度，DeepSeek 线上已切换、TRT-LLM 调优中、TRT-Edge-LLM 已跨模型落地）**。一条"从串行到并行、从静态到动态"的完整演化弧。

## ⑥ 局限与批判

论文自己认的（§5.4 + §5.2/§5.3）：

1. **固定整块起草算力不可回收**（§5.4）：并行骨干每次都要算完整 γ-token 块，低接受率查询（如 Arena-Hard 类开放对话，τ≈3 vs 上限 8）这部分算力白烧。作者给的 future fix 是 drafter 内部 difficulty-aware early exiting——即起草侧也需要自己的"调度"，目前只有验证侧有。
2. **调度最优性依赖 Θ 单峰假设**（§3.2.2）：真实 SPS 曲线锯齿状非单峰，生产版被迫砍掉早停（§5.2），贪心退化为近似——理论保证（附录 A 的无损性）在工程妥协后只剩经验有效性。
3. **异步近似的时间偏差**（§5.2）：截断长度 K 用两步前的置信度（动态 top-K、保序），容量估计有滞后——流量突变时的调度质量未量化。
4. **动态变长验证 kernel 门槛**（§5.3）：与标准定长 decode kernel 不兼容，需定制 kernel（marker tensor 变长路由）——这解释了为何 TRT-LLM 集成仍在"tuning in progress"（`blog26:124/482`），也是复现者最大的工程障碍。

我的补充批判（推断，非论文自认）：

5. **开放域收益腰斩但成本不减**：Table 1 里 chat 域 τ≈3.2–3.7 vs math 6+，而 §4.3.3 显示 chat 置信度分层两端 45.7%–95.7% 方差最大——正是调度器最该发力的地方，但论文未单列 chat 域的调度收益分解（离线关调度器、生产只报聚合数），"调度治开放域"的完整证据链缺一环。
6. **基线公平性存疑点**：Eagle3 只给 1 层、DSpark/DFlash 5 层（§4.1 设置）。虽然 §4.3.2 证明 2 层 DSpark 已胜 5 层 DFlash（间接回应了层数质疑），但"Eagle3 加层/加 TTT horizon 会怎样"未报——Eagle3 原文的多层配置未在同等预算下对齐。
7. **60–85% 的口径**：是"同吞吐下每用户提速"（§5），非 E2E 延迟直接砍半；且 661%/406% 两个名义吞吐数字作者自己标注为退化解读（MTP-1 在该区段已崩）——引用时务必带上"at matched throughput"限定。

---

## 锚清单（复核实引）

- 论文：arXiv 2607.05147v1（2026-07-06；abstract 页 33 作者/北大×DeepSeek）。核心锚：Eq. 1（延迟目标）、§2.2 Eq. 2–3（DFlash KV 注入）、Eq. 4（串行分解）、Eq. 5（Markov 头 r=256）、Eq. 6（RNN 头）、Eq. 7–8（置信头/TV 标签）、Algorithm 1 + 附录 A（非前瞻性）、Eq. 9–12（三损失 α=0.1/0.9/1.0）、Table 1（τ 九基准四模型）、Fig. 2（逐位置接受率）、§4.3.2（消融/0.2–1.3% 开销）、Fig. 5（置信分层 45.7–95.7%）、§5（V4 部署 60–85%/57–78%、Fig. 8 预算 4–6）、§5.4（局限）、§6（CRF-NAT/CTC 不可无损；Domino/DFlare 并行工作）。
- 本地仓：`/usr-data/data2/repos/agent-repos/NVIDIA/TensorRT-LLM/docs/source/blogs/tech_blog/blog26_DeepSeek_V4_on_NVIDIA_Blackwell_Model_Specific_and_Agentic_Workload_Optimizations_in_TensorRT-LLM.md` L124（Eagle 式 MTP 路径+DSpark 描述+tuning in progress）、L180（MTP-1/MTP-3 定义）、L289（MTP-3 默认/MTP-1 高并发）、L447（生产配置 MTP-3）、L482（Future Work：DSpark 集成中）。
- `/usr-data/data2/repos/agent-repos/NVIDIA/TensorRT-Edge-LLM/`：README.md L22（0.10.0 Nemotron-3.5 DSpark）、CHANGELOG.md L16/L43/L57/L71（DDTree drafting、Gemma/Nemotron 扩展、Qwen3.8 导出、paged KV 修复）、docs/source/overview.md L70（能力总表）。
