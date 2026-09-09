# DeepSeek-Prover-V1.5 论文精读

> 论文：*DeepSeek-Prover-V1.5: Harnessing Proof Assistant Feedback for Reinforcement Learning and Monte-Carlo Tree Search*
> arXiv:2408.08152（2024-08-15，Huajian Xin 等 17 人，DeepSeek-AI）
> 本地仓：`~/ai/explore/deepseek-ai/DeepSeek-Prover-V1.5`（含 paper.pdf 与完整推理代码）

---

## 1. 一句话定位

DeepSeek-Prover-V1.5 是一个 7B 开源 Lean 4 定理证明模型，在 DeepSeek-Prover-V1 的"单次整证明生成"范式上，通过**训练侧（SFT + 强化学习 RLPAF）与推理侧（RMaxTS 蒙特卡洛树搜索）双线改造**，把 miniF2F-test 从 50.0% 推到 63.5%、ProofNet 从 ~13.8%（此前 SOTA ReProver）推到 25.3%，双榜 SOTA（2024-08 时点）。它是 DeepSeek 从 V1（合成数据）走向 V2（子目标分解 RL）的关键中继站，也是"证明助手反馈当免费验证器"这一思想的完整落地。

**团队背景**：一作 Huajian Xin 即 DeepSeek-Prover V1 的核心作者，团队同人为 DeepSeekMath（GRPO 算法）班底——所以本文的 RL 组件直接复用 GRPO，搜索组件则向 AlphaZero 式"训练×搜索"闭环靠拢。

## 2. 动机与痛点

形式化定理证明（Lean 4）此前有两条路线，各有硬伤：

| 路线 | 代表 | 优点 | 痛点 |
|---|---|---|---|
| **proof-step 生成** | GPT-f、Thor、ReProver、HTPS | 每步 tactic 都能拿到证明状态反馈，可接树搜索 | 模型与验证器通信频繁、上下文工程复杂 |
| **whole-proof 生成** | DSP、LEGO-Prover、DeepSeek-Prover-V1 | 一次出整段证明，计算高效 | **长程预测看不到中间 tactic state**：后续 tactic 依赖前面 tactic 的隐藏结果，自回归模型对中间状态会产生错误信念，一步走错步步错（compounding error） |

V1 用 whole-proof 拿了 Lean 4 SOTA（miniF2F-test 50.0%），但天花板明显。V1.5 的核心问题意识：**能否让 whole-proof 模型也"看见"中间状态？** 答案是 truncate-and-resume——先当 whole-proof 生成，错了就从第一个错误处截断，把已验证部分当新 prompt 续写，再把这套机制嵌进 MCTS。这样单模型同时覆盖两种范式，训练目标几乎不变。

## 3. 核心方法

### 3.1 训练管线：Base → SFT → RL 三级火箭

**（a）继续预训练**：以 DeepSeekMath-Base 7B 为底座，在高质量代码+自然语言数学语料上继续预训练，重点是 Lean / Isabelle / Metamath 等形式语言 → `V1.5-Base`。

**（b）SFT：两类数据增强**（这是把 V1 数据盘活的关键）：

- **Thought-augmented proof generation**：用 DeepSeek-Coder-V2 236B 给 V1 的证明代码**注入自然语言 CoT 注释**——proof 块开头插完整解题思路，每个 tactic 前插对应的步骤规划（类似 Lean-STaR，但 CoT 直接内嵌代码注释）。训练数据用两套引导 prompt 区分 CoT / non-CoT 双模式。
- **Tactic state 注释**：增强 Lean REPL（借 LeanDojo 的数据提取），抽每个 tactic 的三元组（位置、执行前状态、执行后状态），在合法证明的每个 tactic 后插入 `/- tactic state: … -/` 注释。训练时该注释之后的 token 全部算 loss（含一个**预测 tactic state 的辅助任务**），之前是 prompt。这个辅助任务就是为 MCTS 的 resume 机制铺路——模型必须学会"读状态、续证明"。
- 数据规模：expert iteration（生成→验证→回训→再生成）滚动，最终 **9,645k 序列**；训练 9B tokens，batch 2048，lr 1e-4，ctx 4096。

**（c）RLPAF（RL from Proof Assistant Feedback）**：

- 算法：**GRPO**（组相对策略优化，免去 critic 模型）。每条定理采一组 32 个候选证明，按组内相对奖励优化。
- 奖励：Lean 验证器给出**二值奖励**——证明编译通过 =1，否则 =0。形式验证的天然优势：不需要训练 reward model，反馈零噪声。
- 稀疏性缓解：**prompt 筛选**——只保留 SFT 模型多次尝试中"部分成功"的定理（约 4.5k 条），保证组内有对有错，GRPO 的组内对比才有梯度。
- 超参：lr 5e-6，KL 惩罚系数 0.02（SFT 模型兼作参考模型），max len 2048，batch 512。

### 3.2 RMaxTS：截断-恢复式树搜索

**（a）Tactic 级树抽象（truncate-and-resume）**

- **Truncate**：把整段生成交给 Lean 解析成 tactic 序列，在**最早验证错误处截断**，错误之后的代码丢弃；成功部分的每个 tactic（含其 CoT 注释）变成一条树边（一个 tactic state 转移）。
- **Resume**：Lean 里不同 tactic 可达同一状态，所以每个节点存一组**等价 tactic 代码**，扩展时随机选一个作为 prompt 结尾，再拼上 Lean 返回的最新 tactic state 注释，让模型续写。
- 与 proof-step 搜索的本质区别：whole-proof 模型一次 rollout 就是一整段证明，**一次扩展可以插入一条节点链**（而非博弈树的一层子节点）。

**（b）MCTS 三步（simulation 并入 expansion）**

- **Selection**：树策略 $TreePolicy(s)=\arg\max_{a\in Children(s)\cup\{\oslash\}} Q_{UCB}(s,a)$。$\oslash$ 是"扩展当前节点"的虚拟动作（virtual node 技巧，来自 DT-solver），使**非叶节点也能被持续扩展**——因为生成模型的输出空间不受固定分支数约束。$Q_{UCB}=\underbrace{Q(s,a)}_{exploitation}+\underbrace{UCB(s,a)}_{exploration}$。
- **Expansion**：从选中节点 resume 生成，Lean 验证；全对则终止，否则截断成节点链并入树。
- **Backpropagation**：沿选择轨迹更新 $Q_{UCB}$。

**（c）RMax 内在奖励（本文最优雅的一笔）**

证明搜索的外在奖励极度稀疏（只有完整证出才有 1），属于典型的 hard-exploration 问题。RMaxTS 借经典 RMax 算法（2002）的"乐观探索"思想：**到达未见状态就给自己发最大奖励**，且完全弃用外在奖励（同 ZeroRMax）：

$$R_{\text{intrinsic}}(\tau)=\mathbb{I}[\text{本轮扩展至少给树加入了一个新节点}]$$

直觉：优先扩展"能产生多样化 tactic state"的节点；多种 Lean 代码若导致相同状态转移，该奖励自动抑制冗余生成，提升样本效率。

**（d）DUCB：非平稳奖励的折扣 UCB**

内在奖励天然非平稳——树越大，发现新节点越难，旧记录的期望值持续衰减。标准 UCB1 会高估老节点。解法是折扣上置信界（DUCB，2011）：

$$Q_{DUCB}(s,a)=\frac{W_\gamma(s,a)}{N_\gamma(s,a)}+\sqrt{\frac{2\ln\sum_{a'}N_\gamma(s,a')}{N_\gamma(s,a)}},\quad W_\gamma=\sum_{t=1}^{N(s,a)}\gamma^{N(s,a)-t}R(\tau_t),\quad N_\gamma=\sum_{t=0}^{N(s,a)-1}\gamma^t$$

新反馈权重高、旧反馈按 $\gamma$ 衰减，实验取 $\gamma=0.99$。注意：这里的折扣作用在**搜索迭代维度**而非轨迹内步数维度。

**（e）并行化（工程关键）**

- **Root parallelization**：每节点 256 个 MCTS runner，每 GPU 一个模型、batch 512；Lean 验证走 REPL 跑在数千 CPU 核的集群上，每个验证任务独立沙箱进程，生成与验证全部异步。
- **Tree parallelization**：每棵树 32 个线程 worker 并行跑"选点→生成→验证→回传"循环。
- **Virtual loss**：进行中的迭代暂时回传 $R=0$，逼并发 worker 选不同节点。

## 4. 实验与结果

**miniF2F-test（244 题高中竞赛级，Lean 4.9.0）主榜**：

| 方法 | 预算 | pass |
|---|---|---|
| TheoremLlama | 128 | 33.6% |
| GPT-f | 64×8×512 | 36.6% |
| Hypertree Proof Search | 64×5000 | 41.0% |
| Lean-STaR | 64×1×50 | 46.3% |
| DeepSeek-Prover-V1 | 16×4096 | 50.0% |
| InternLM2-StepProver | 64×32×100 | 54.5% |
| V1.5-Base（3-shot） | 6400 | 42.2% |
| V1.5-SFT | 16×6400 | 57.4% |
| V1.5-RL（单次生成 CoT） | 16×6400 | **60.2%** |
| V1.5-RL + RMaxTS（CoT） | 16×6400 | 62.7% |
| V1.5-RL + RMaxTS（CoT/non-CoT 混合） | 32×6400 | **63.5%** |

亮点：V1.5-RL 只用 **3200 次采样就达 54.9%**，反超 InternLM2-StepProver 用 64×3200 次树搜索才到的 54.5%——搜索效率高一个数量级。ProofNet（本科级 371 题）：V1.5-RL+RMaxTS 全集 25.3%（valid 25.4%），碾压 ReProver 13.8%、InternLM2-StepProver 18.1%。

**训练阶段消融（pass@128，miniF2F-test / ProofNet-test）**：Base 29.7%/9.7% → SFT(CoT) 50.4%/15.9% → RL(CoT) 51.6%/18.2%。重要发现：与 DeepSeekMath 在自然语言数学上"RL 只提升 TopK 采样"不同，这里 **RL 在小预算到大预算全区间稳定提升**——是真实能力增强，且与 RMaxTS 的增益正交可叠加。

**CoT vs non-CoT**：CoT 优势随样本预算放大（大预算下 CoT 60.2% vs non-CoT 57.4%）；但两模式互补——CoT 擅长系统性数学思考，non-CoT 擅长用 Lean 高层 tactic 自动化解决计算型问题。**混合策略**（预算对半分）再涨到 63.5%。

**RMaxTS 组件消融（miniF2F-test，16×6400，RL+CoT）**：完整 RMaxTS 62.7% > 去 tactic state 61.1% ≈ UCT（去内在奖励）61.1% ≈ DUCB→UCB1 60.7%。结论：①无内在奖励时树搜索退化到接近单次采样；②tactic state 注释是树搜索发挥威力的必要条件。

## 5. 局限与后续（含 V2 展望）

论文自认局限与未来方向：①本文只做了 RL 的**探索侧**（RMaxTS 多样化证明路径），**利用侧**（证明搜索的剪枝）未触及——最有前景的方向是训练 **partial-proof critic 模型**评估不完整证明并剪枝搜索分支，这实质是 temporal credit assignment 问题；②下一个战场是 file-level 证明（miniCTX 方向），当前模型已隐约理解文件级上下文但未专门优化。

**→ DeepSeek-Prover-V2 展望（arXiv:2504.21801，已核实）**：V2 论文标题 *Advancing Formal Mathematical Reasoning via Reinforcement Learning for Subgoal Decomposition*（2025-04-30）。它恰好把 V1.5 留下的两个坑都填了：①**子目标分解取代 MCTS**——用 DeepSeek-V3 把难题分解成 `have ... sorry` 链（证明草图），由 7B 小模型递归求解各子目标，全部解出后把逐步形式证明与 V3 的 CoT 配对成**冷启动推理数据**，再上 RL（binary reward）；②模型从 7B dense 换成 DeepSeek-V3 底座的 **671B MoE**。战果：miniF2F-test **88.9%**（pass@8192；pass@32 即 82.4%）、ProofNet-test 37.1%（pass@1024）、PutnamBench 49/658（论文 v2 修订为 47）、自建 ProverBench 325 题中 15 道 AIME 题 24-25 解出 6 道（对比 DeepSeek-V3 多数投票解 8 道——形式与非形式推理的差距已大幅收窄）。V1.5 的 RMaxTS 是"推理时暴力探索"，V2 转向"训练时把分解能力内化"，这条演进线与 AlphaProof 的思路殊途同归。

## 6. 与代码的对照（论文 → 本仓文件）

| 论文概念 | 仓内位置 | 说明 |
|---|---|---|
| RMaxTS 算法 | `prover/algorithms/rmax_tree_search.py` | `TreeNode` 持有 `_discounted_rewards/_discounted_visitation/_subtree_*` 四组折扣统计——正是 Eq.(7)-(9) DUCB 的增量实现；`update_reward()` 回传、`start_new_job()/complete_job()` 即 virtual loss |
| 截断-恢复机制 | `prover/lean/verifier.py`、`proof.py`、`ast_parser.py` | Lean REPL 验证 + 首错截断 + tactic 解析（论文 §3.1） |
| 搜索/树/生成 worker 并行 | `prover/workers/{search,scheduler,generator,data_loader}.py` | 论文 §3.4 root/tree parallelization |
| 单次整证明采样 | `prover/algorithms/sampling.py`、`configs/sampling.py` | single-pass 基线 |
| 论文全部搜索超参 | `configs/RMaxTS.py` | `gamma=0.99`、`sample_num=6400`、`concurrent_num=32`（每树 32 worker）、`n_search_procs=256`（runner 数）、`tactic_state_comment=True`、`batch_size=512`、`mode='cot'`、temperature=1/top_p=0.95/max_tokens=2048、lean_timeout=300——与论文逐字对应 |
| 入口与汇总 | `prover/launch.py`、`prover/summarize.py` | README 快速开始两条命令 |
| Mathlib4 依赖 | `mathlib4/`（submodule） | 验证环境需 `lake build` |
| 纯推理示例 | `quick_start.py`（70 行） | transformers 直接加载 RL 模型出证明 |

一个值得注意的实现细节：PyTorch 的冻结在这里不是 `requires_grad=False`，而是把参数注册成 buffer（见 ESFT 仓同款技巧），说明 DeepSeek 系仓库共享一套训练工程习惯。

## 7. 学习路径

**前置**：①Lean 4 tactic mode 基本语法（Mathlib 常用 tactic：`nlinarith`/`rw`/`have`）；②DeepSeekMath 论文（GRPO 原始定义）；③MCTS 基础（UCT、virtual loss、RMax 算法与 count-based exploration）。

**精读顺序**：Figure 2 总框架 → §2.2 两类数据增强（理解"为什么 SFT 要学 tactic state"）→ §3.1 truncate-resume 图（Figure 4）→ §3.3 RMax+DUCB 公式 → §4 Table 3（CoT/mixture 消融是最常被忽略的增量）→ 附录 A 的 CoT/non-CoT prompt 实例。

**复现建议**：①门槛最低：`quick_start.py` 单卡出证明（需先 `lake build` mathlib4，约 30-90 分钟）；②进阶：跑 `configs/sampling.py` 复现 pass@k 曲线；③完整 RMaxTS 需要 GPU 节点 + 大量 CPU 跑 Lean REPL（`n_search_procs=256` 是集群配置，单机可把 `concurrent_num/sample_num` 调小验证流程）；④读 `rmax_tree_search.py` 时对照 Eq.(7)-(9) 手推一遍折扣增量的代数，是理解 DUCB 落地的最好练习。

**延伸阅读**：Lean-STaR（CoT 前身）、HTPS（树搜索前作）、DeepSeek-Prover-V1（数据合成）、DeepSeek-Prover-V2（子目标分解 + RL 终局形态）。
