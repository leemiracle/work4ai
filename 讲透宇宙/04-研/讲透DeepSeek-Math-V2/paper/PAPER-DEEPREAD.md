# DeepSeekMath-V2: Towards Self-Verifiable Mathematical Reasoning — 论文精读

> arXiv:2511.22570（2025-11-27 提交，v1）· Zhihong Shao*, Yuxiang Luo*, Chengda Lu*, Z.Z. Ren* 等 10 人 · DeepSeek-AI
> 代码/权重：github.com/deepseek-ai/DeepSeek-Math-V2（本仓即本地对照对象）
> 本文是一手 arXiv HTML 全文精读 + 本仓 inference 代码对照。
>
> **两点核实说明**：① 本仓 README 未附 arXiv 链接，ID 经 web 检索核实为 **2511.22570**，摘要与 README 逐句吻合；② 任务预期描述为"迭代扩展 RL+工具集成路线"——实际论文是**"迭代扩展 RL + 自验证（self-verification）"路线：verifier 作为 reward model 的 GRPO 迭代，全程无工具集成（无代码执行器/符号工具/搜索引擎）**。迭代扩展 RL 的判断正确，工具集成为预期偏差，特此勘误。

---

## 1. 一句话定位

**把数学 RL 的奖励从"最终答案对不对"升级为"verifier 给证明打的分数"，并让生成器显式知道自己的奖励函数、通过自我审查最大化它**：训练出首个开源的自然语言定理证明模型族，以 64+64 候选池 × 16 轮验证引导搜索拿下 IMO 2025 金牌线（83.3%）、CMO 2024 金牌线（73.8%）、Putnam 2024 **118/120**（人类最高分 90）。一作 Zhihong Shao 是 DeepSeekMath（GRPO 提出者，2402.03300）一作——本文是 GRPO 路线对"答案可验证性"这一根本约束的正面回应，基座为 DeepSeek-V3.2-Exp-Base。

## 2. 动机与痛点

**范式级痛点**：过去一年，"RL + 最终答案奖励"让推理模型饱和了 AIME/HMMT 这类量化竞赛，但该奖励机制有两个根本缺陷：
1. **答案正确 ≠ 推理正确**——模型可以靠有缺陷的逻辑或幸运的错误得到正确答案（reward 是推理正确性的不可靠代理）；
2. **定理证明不适用**——证明题往往没有数值终答，严格推导本身才是目标，final-answer reward 根本无从定义。

后果：这类模型产出的自然语言证明频繁包含数学无效或逻辑不一致的步骤；且**不具备验证证明的能力**——高假阳性，对有明显逻辑漏洞的证明也宣称有效。换言之，自然语言定理证明领域**缺乏 generation-verification gap**（生成比验证强，验证跟不上就无从筛选与改进）。

**三个关键观察**（方法的地基）：
- 人类**没有参考答案也能挑出证明的问题**——攻克 open problem 的必备能力；
- 一个证明若在**放大的验证努力下仍找不到 issue**，则更可能是对的；
- **识别出有效 issue 所需的努力程度**可作为证明质量的代理 → 可用来优化生成。

由此勾出的飞轮：验证反馈优化生成 → 放大验证算力自动标注"新一代难验证证明"→ 新数据再强化 verifier → 循环。

## 3. 核心方法

### 3.1 训练 Verifier：识别 issue 并给证明打分（创新 #1）

打分规则模仿数学专家评审：给问题 $X$ 与证明 $Y$，verifier $\pi_\varphi(\cdot|X,Y,\mathcal{I}_v)$ 产出 proof analysis（先总结识别到的 issue，再打分）——**1 = 完全严格（所有逻辑步清晰论证）；0.5 = 整体正确但有细节遗漏/小错；0 = 有致命逻辑错误或关键缺口**。

**冷启动数据**：① 从 AoPS 竞赛集爬 2010 年后明确要求证明的题，共 **17,503 道**（$\mathcal{D}_p$）；② 用 DeepSeek-V3.2-Exp-Thinking 变体生成候选证明（该模型未针对证明优化、输出简洁但易错，prompt 其多轮自我精炼以提升完备性）；③ 专家分层抽样评分 → $\mathcal{D}_v=\{(X_i,Y_i,s_i)\},\ s_i\in\{0,0.5,1\}$。

**RL 目标**（基于 V3.2-Exp-SFT 数学/代码推理版，GRPO 训练）：

$$\max_{\pi_\varphi}\ \mathbb{E}\left[R_{\text{format}}(V_i')\cdot R_{\text{score}}(s_i',s_i)\right],\qquad R_{\text{score}}(s_i',s_i)=1-|s_i'-s_i|$$

$R_{\text{format}}$ 检查输出含规定短语（"Here is my evaluation of the solution:" + "Based on my evaluation, the final overall score should be: `\boxed{...}`"）；$R_{\text{score}}$ 奖励预测分与专家分接近。

### 3.2 Meta-Verification：审查 proof analysis 本身（创新 #2，忠实性关键）

**漏洞**：上述目标只监督分数，不管 issue 真假——verifier 可以**猜对分数的同时幻觉出根本不存在的 issue** 拿满分，摧毁可信度。

**解法**：训一个 meta-verifier $\pi_\eta(\cdot|X,Y,V,\mathcal{I}_{mv})$ 评估"verifier 的分析是否合理"（issue 是否真实存在、论证是否支持所给分数），专家按 $\mathcal{I}_{mv}$ 对 verifier 输出打质量分 $\in\{0,0.5,1\}$ 构造 $\mathcal{D}_{mv}$，RL 结构同上。然后把 meta 反馈乘进 verifier 奖励：

$$R_V = R_{\text{format}}\cdot R_{\text{score}}\cdot R_{\text{meta}}$$

效果：verifier 分析的平均质量分（由 meta-verifier 评）**0.85 → 0.96**，分数预测精度不降。最终模型身兼 proof verification 与 meta-verification 双任务。

### 3.3 训练 Generator：verifier 作生成式 reward model（创新 #3）

$$\max_{\pi_\theta}\ \mathbb{E}_{X_i\sim\mathcal{D}_p,\ Y_i\sim\pi_\theta(\cdot|X_i)}\left[R_Y\right]$$

$R_Y$ 即 verifier $\pi_\varphi$ 给生成的证明打的分。纯 verifier-reward 版本。

### 3.4 Self-Verification：让生成器内化验证能力（创新 #4，本文灵魂）

**观察到的关键失败模式**：一次性 prompt 生成器"边写边自评"，它倾向于**宣称自己正确**——即便外部 verifier 轻易就能挑出错。即：生成器能基于外部反馈改证明，却不能用同等严格度审视自己。

**训练时改为产出 证明 $Y$ + 自分析 $Z$**（$Z$ 与 verifier 同格式同 rubric，预测分记 $s'$），用 verifier 双重评估——$Y$ 得分 $R_Y=s$，$Z$ 经 meta-verification 得 $R_{\text{meta}}(Z)=ms$：

$$R = R_{\text{format}}(Y,Z)\cdot\left(\alpha\cdot R_Y + \beta\cdot R_Z\right),\qquad R_Z = R_{\text{score}}(s',s)\cdot R_{\text{meta}}(Z)$$

**$\alpha=0.76,\ \beta=0.24$**。该结构制造的激励（原文三条，值得逐条品味）：
- **诚实认错比谎报正确的收益高**；
- 最高奖励 = 证明真对 + 准确认识到自己的严格性；
- 拿高reward的好策略是**在定稿前尽可能多地发现并解决自己证明中的 issue**。

一句话概括本文哲学：**让模型显式知道自己的奖励函数，用深思熟虑（deliberate reasoning）而非盲目试错去最大化它**。

### 3.5 验证-生成协同与全自动标注（创新 #5，可扩展性关键）

verifier 提升 generator → generator 产出"verifier 单次尝试挑不出错"的新证明 → 这些难例成为 verifier 的新训练数据。标注新证明的自动化管线（替代人工）：
1. 每个证明生成 $n$ 份独立验证分析；
2. 对报 issue（0 或 0.5 分）的分析各生成 $m$ 份 meta-verification 投票，多数确认才算有效；
3. 取最低分档分析，若 ≥$k$ 份被确认有效则打该最低分标签；所有验证都没发现合法 issue → 打 1 分；否则丢弃或转人工。

可行性依据：验证采样越多越可能抓到真 issue；而"审查已识别的 issue"（=meta-verification）比"从头找 issue"容易且样本效率高。**最后两轮训练迭代完全用此自动管线替代了人工标注**，质量检查与专家判断对齐良好。

**迭代训练**（GRPO）：每轮先优化验证，generator 从 verifier checkpoint 初始化再优化生成；第 2 轮起 verifier 从"用 rejection fine-tuning 合并了上轮双能力"的 checkpoint 初始化。

## 4. 实验与结果

**基准**：in-house CNML 难度 91 题（代数 13/几何 24/数论 19/组合 24/不等式 11）；IMO 2025（6 题）、CMO 2024（6 题）、Putnam 2024（12 题）、ISL 2024（31 题）；**IMO-ProofBench**（DeepMind DeepThink IMO-Gold 团队出品，Basic 30 题 pre-IMO~IMO-Medium + Advanced 30 题 IMO-Hard）。

- **One-shot**（每题 8 样本，8 份验证分析多数投票判对错）：CNML 全类别稳定超过 **GPT-5-Thinking-High 与 Gemini 2.5-Pro**（Figure 1）。
- **Sequential refinement**（ISL 2024，32 线程，128K 上限内多轮自验证精炼）：Pass@1 随最大精炼轮数（1→8）显著上升；**Best@32（按自评分选优）显著高于线程均值**——证明生成器的自我评估能可靠区分证明质量（Figure 2）。
- **High-compute search**（核心战报）：候选池每题 64 证明 × 64 验证分析；每轮按平均验证分选 64 强，各配 8 份分析（优先报 issue 的）精炼，最多 16 轮或"通过全部 64 次验证"提前停。全程单模型（最终 generator）兼任生成与验证：

| 竞赛 | 得分 | 说明 |
|---|---|---|
| IMO 2025 | **83.3%**（P1/P2/P4/P5 全解 + P3 partial） | 金牌线 |
| CMO 2024 | **73.8%**（P1/P2/P4/P5/P6） | 金牌线 |
| Putnam 2024 | **98.3% = 118/120**（11/12 全解 + 1 题小错） | 人类最高 90 |

- **IMO-ProofBench**（Figure 3，专家按官方指南评分）：**Basic 集超过 DeepMind DeepThink（IMO Gold）**，Advanced 集保持竞争力，其余所有 baseline 大幅领先。未全解的题上生成器通常能指出自己证明中的真实 issue，全解题则通过全部 64 次验证——verifier 确实学会了评"以前被认为无法自动评判"的证明。

## 5. 局限与后续（论文自认 + 评论）

- **自认局限**：最难 IMO 级问题仍未解决（Advanced 集与 DeepThink 有差距）；"much work remains" 反复出现——self-verifiable reasoning 只证明了可行性，不是完成时。
- **方法论层面的开放风险**（我的评论，非论文原文）：评测对错由自家 verifier 多数投票判定，存在**自我认证循环**风险（论文用专家抽检缓解，Figure 3 亦请专家按 DeepMind 指南独立评分）；128K 上下文限制了一次性精炼的深度（论文明确以此论证 sequential refinement 的必要性）；框架面向"有客观正误的数学"，对真正的 open problem（无 ground truth、验证本身可能无解）尚未验证。
- **生态位**：与 DeepSeek-Prover-V2（2504.21801，形式化 Lean 路线）互补——非形式化自验证 vs 形式化编译保证。论文明确将两者视为未来"informal insight + formal guarantee"可靠数学系统的两翼。社区评价普遍将其视为开源阵营对 Gemini DeepThink 的首次正面回应（IMO-ProofBench 同源可比）。

## 6. 与代码的对照（论文概念 → 本仓实现）

本仓是推理/复现仓（模型基于 V3.2-Exp-Base，训练框架不在仓内），对照点集中在 prompt 体系与搜索循环：

| 论文概念 | 本仓位置（DeepSeek-Math-V2/） |
|---|---|
| Appendix A.2 Proof Verification Prompt | `inference/math_templates.py` `"proof_verification"`：逐字实现——"Here is my evaluation of the solution:"、"Based on my evaluation, the final overal score should be: `\boxed{...}`"（注意模板里 "overal" 拼写与论文一致）、1/0.5/0 三档规则、"referencing anything from any paper does not save the need to prove the reference" |
| Appendix A.3 Meta-Verification Prompt | `math_templates.py` `"meta_verification"`：Step Restatement / Defect Analysis / Expression Analysis / Score Analysis 四维审查 + "defect analysis 优先于一切"的裁决规则，与论文 §2.1.2 完全对应 |
| Appendix A.1 Proof Generation Prompt（含内嵌评价指令） | `math_templates.py` `"proof_generation"`：`## Solution` + `## Self Evaluation` 双节格式；"You CAN'T cheat! If you cheat, we will know, and you will be penalized!"——§3.4 的激励设计直接写进 prompt |
| Appendix A.4 Proof Refinement Prompt | `math_templates.py` `"proof_refinement"`：候选证明+评估配对精炼 |
| 高算力搜索（64×64 池、多轮 R） | `inference/main.py`：`--n_verification_per_proof`（默认 4）、`proof_verification_R{R}/meta_verification_R{R}` 按轮落盘、`prepare_proof_refinement` 读取 **R-1 轮**的 verification+meta_verification 输出构造下一轮输入、`--skip_meta_verification` 开关、320 进程并发、验证温度 1.0、64K max_len |
| IMO/CMO/Putnam 题目与模型输出 | `inputs/*.json`（含 CMO2025）+ `outputs/*.jsonl`（5 个基准的完整预测，README 声明即论文 Table 1/Figure 3 的数据源） |

与 DeepWiki（work4ai/讲透DeepSeek-Math-V2/deepwiki/，含 `2.3-self-verification-mechanism.md` 等页）的机制描述一致，可交叉阅读。

## 7. 学习路径

1. **前置**：DeepSeekMath（2402.03300，GRPO 原始论文——本文优化器与命名直接继承）→ DeepSeek-R1（Nature 2025，final-answer RL 范式的巅峰，也是本文批判的起点）→ LLM-as-judge / self-verification 文献（Dekoninck et al. 2025、Luong et al. 2025 是论文自引的直接先驱）。
2. **精读顺序**：§1 三个关键观察（全文逻辑的种子）→ §2.1.2 meta-verification（理解"为什么分数监督不够"）→ §2.2.2 的激励三条（本文价值观）→ §2.3 自动标注管线（可扩展性核心）→ Figure 2/3 与 Table 1。公式只有 6 个且无高等数学，难点全在训练流程的闭环设计。
3. **复现建议**：模型权重开源（V3.2-Exp-Base 底座，需 vLLM 栈），本仓 `inference/run.sh` 可直接对 `inputs/` 跑四模板管线；最划算的入门实验是把 `n_verification_per_proof` 从 4 调到 64 观察"验证算力→判分稳定度"曲线（即 §2.3 观察 1 的直接验证）；研究向可复现 sequential refinement 的 Pass@1/Best@32 曲线（32 线程即可）。
4. **延伸阅读**：DeepSeek-Prover-V2（形式化对照）、Seed-Prover（IMO 2025 5/6 的形式化方案）、AlphaProof 系列；本精读姊妹篇（讲透DeepSeek-Prover-V1.5/paper/）已覆盖该线前史。

---

*写于 2026-09-05；一手来源 arXiv HTML v1（ID 经 websearch 核实）+ 本仓 inference 代码逐行对照。*
