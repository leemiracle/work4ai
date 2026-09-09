# PRACTICE_LAB：AI↔Math 双向实践操作手册（怎么做版）

> card_id: practice-lab
> universe: top-math-courses
> burke: 场景=零基础数学学习者要在 AI×Math 交叉处动手；主体=你+DCU服务器+本地CPU；行动=五级AI4Math阶梯+五个Math4AI最小实验；目的=从"读过"到"跑过"；张力=工具链庞杂vs每周只有10-20h；弧线=每级都有晋级标准，不达标不升级
> status: v1.0（2026-08-25）
> refs: AI_FOR_MATH_TOOLS.md（用什么）/ 讲透Agent/实战案例-Prover数学Agent（已有资产）/ REBUILD.md（服务器复活）
> updated: 2026-08-25

**与 AI_FOR_MATH_TOOLS.md 的分工**：那份讲"用什么"（工具分层地图）；本份讲"怎么做"（命令+实验+验证标准）。每级/每个实验都给出**晋级标准**——不达标不升级，避免收藏夹式学习。

---

## A. AI for Math 实践：五级阶梯

### L0 环境与基本功（1-2 周，可与讲透Lean4数学并线）

**装（准确命令）**：
```bash
# 1. elan（Lean 版本管理器，类似 rustup）
curl https://elan.lean-lang.org/elan-init.sh -sSf | sh
elan default stable

# 2. 新 Mathlib 项目（预编译缓存，不必本地编 2 小时）
lake new mymath math
cd mymath
lake exe cache get   # 下载 Mathlib 预编译 oleans（数 GB，一次到位）
lake build           # 首次 ~10 分钟

# 3. VSCode：装 lean4 扩展 → 打开项目即语言服务器
```

**跑**：把讲透Lean4数学/01 NNG 的练习在新项目里重做 10 题。

**晋级标准**：① `lake build` 零错误；② 不看答案写出 `induction n` + `simp_all` 组合证 3 题；③ 能解释 infoview 里 goal/ctx 两栏各是什么。
**避坑**：Mathlib 版本漂移——tactic 报错先 `lake update`；服务器上用 `/work/lean-4.21.0-linux`（x86）不是 `/work/lean4`（aarch64）。

### L1 人机协作证明（立即开始，零训练成本）

**装**：
```lean
-- lakefile.toml 加：
[[require]]
name = "LeanCopilot"
git = "https://github.com/lean-dojo/LeanCopilot"
rev = "v0.6"   -- 以官方 README 当前 rev 为准
-- 然后 lake exe cache get && lake build
```

**用（VSCode 内）**：
- 光标停在 tactic 处 → `/Suggest`（AI 补全下一步）
- `/Premises`（推荐可用引理）
- `/Tactic`（找 tactic 名）

**对拍实验**：同一批 10 题，三个通道各跑一遍并记录通过率/耗时：
1. 纯手写（L0 能力基线）
2. LeanCopilot /Suggest
3. opencode + `oprover-math` skill（glm-5.3，走 API）

产出一张 3×10 通过率表——这就是你自己的第一个"人机协作消融实验"，直接写进讲透Agent 案例。

**晋级标准**：AI 辅助通道比纯手写通过率高 ≥30%，且你能指出 AI 建议里至少 3 次错误（会拒收才算会用）。

### L2 本地 Prover 推理栈（你的独有资产，服务器恢复后 1 周）

**已有**（讲透Agent/实战案例-Prover数学Agent）：REBUILD.md 8 步复活 → vLLM :8177 卡1 → distill_pipeline.py。

**新实验 L2-E1：miniF2F 子集 pass rate**（论文口径的最小复现）：
```bash
# 服务器恢复后（REBUILD.md §二 步 6-7）
# 下载 miniF2F test 集（github.com/openai/miniF2F，75 题）
# 取前 20 题，non-CoT 模式每题 4 采样（temp 0/0.7），Lean 验证
# 记录 pass@1 / pass@4，对照论文 DeepSeek-Prover-V2-7B miniF2F-test ~30%+ 量级
```

**晋级标准**：跑通 20 题并得到自己的 pass@k 数字（高低无所谓，重要的是**你有自己的可复现基线**，之后一切训练都以它为对照）。

### L3 训练实操（2-4 周）

三步，全部已有脚本，按序：

1. **LoRA SFT**：`finetune_lora.py --data distill.jsonl`（24 题全量蒸馏跑完后）。看 loss 曲线 + 样本过拟合情况（样本 <100 条时以"跑通流程"为目标，不期待指标提升——诚实边界）。
2. **专家迭代（R5）**：wins.jsonl 积累 → 每攒 50 条重训一次 → holdout pass rate 对比。这是 AlphaProof/Gauss 数据飞轮的个人最小版。
3. **LeanDojo 复现（可选，进 Research 生态）**：
```bash
pip install lean-dojo
# 官方 quickstart：从 Trace/Isabelle… 用其 Dojo 交互环境逐步证明
# ReProver 模型 HF: kaiyuyue/ReProver-7B（检索增强 premise selection）
```
对应论文 ReProver（ICLR'24 spotlight）——premise selection 是比整证明更便宜的可训练任务。

**晋级标准**：完成 1+2（训练循环闭合）；3 可选。

### L4 研究级实操（选做，面向社区存在感）

- **给 Mathlib 提 PR**：找 `good first issue` 或 doc 改进；从 L3 的 wins 库里挑一条 Mathlib 没有的初等引理形式化提交。第一个 merged PR = 进入 600 人贡献者网络。
- **Equational Theories 式微项目**：挑一个 20 条等式的小代数结构，写暴力 prover（枚举重写）+ 让 7B 补 hardest case——复刻 2024 社区项目的 1/1000 规模。
- **Gauss 式 autoformalization agent**：把 prompts.py 的 DECOMPOSE 模板改成"逐定理依赖序翻译"（Herald 思路：按 import DAG 拓扑序，先译前置概念）。

---

## B. Math for AI 实践：五个最小实验（本地 CPU 可跑，torch 已装）

> 设计原则：每个实验回答一个"理论说 X，我亲眼看一次 X"。都放进 `讲透数学实验/` 或对应讲透单元 experiments/。

### E1 手写 Muon：Newton-Schulz 正交化优化器（1 天）

**要看的理论**：Muon = 动量矩阵 → 正交化（UV^T）→ 更新；实践中用 5 步 Newton-Schulz 多项式逼近而非 SVD（2025-26 已有收敛证明：误差随步数双指数衰减）。

**最小实验**（~100 行纯 torch）：
```python
# 核心：Newton-Schulz 5 步（实用系数，来自实践社区）
def zeropower_via_newtonschulz5(G, steps=5):
    X = G.bfloat16() / (G.norm() + 1e-7)
    a, b, c = 3.4445, -4.7750, 2.0315
    for _ in range(steps):
        A = X @ X.T
        B = b * A + c * A @ A
        X = a * X + B @ X
    return X
# Muon step：对 2D 参数 momentum→NS5→更新；1D 参数走 AdamW
```
在 2 层小 transformer（讲透KV Cache 的 Qwen 太大；用 nanoGPT-shakespeare 级别，CPU 一晚）上对比 AdamW vs Muon 的 loss 曲线。

**验证标准**：Muon 的 loss 下降更快或持平（小模型小数据下可能持平——如实记录）；你能回答"为什么正交化等于把所有奇异值拉平，这为何有益"。
**预期坑**：bfloat16 CPU 支持不稳 → float32 也行；学习率要重调（Muon 最佳 lr 通常比 AdamW 大 ~3×）。

### E2 Chinchilla scaling law 亲手拟合（2 天）

**理论**：L(N,D) = E + A/N^α + B/D^β（Chinchilla，2022）。

**最小实验**：本地 CPU 训 15-20 个小模型（参数 1e4~1e6，字符级 LM，各 10-30 分钟），网格覆盖 N×D；`scipy.optimize.curve_fit` 拟合 α,β,E；画 iso-loss 等高线，找自己的 compute-optimal 边界 C∝ND 与 Chinchilla 的 N∝D^(2/3)（近似）对照。

**验证标准**：拟合 R²>0.95；你的最优 N/D 比值量级与论文一致（不苛求数值相同，量级相同即成功——参数少 6 个数量级还能外推趋势，这本身就是 scaling law 的震撼点）。
**进阶**：加精度维度 P，复现 "Scaling Laws for Precision"（arXiv:2411.04330）的 effective parameter count 思想：N_eff = N(1-e^(-P/γ))。

### E3 NTK：宽网络在训练中"冻结"（半天）

**理论**：Neural Tangent Kernel——足够宽的初始化网络，训练中 kernel 几乎不变，学习退化为 kernel regression。

**最小实验**（~60 行）：两个不同 seed 初始化的宽 MLP（width 512→4096 递增），采样 NTK：K(x,x') = ⟨∇f(x), ∇f(x')⟩；对比训练 0 step vs 500 step 后 K 的相对变化；画 width↑ → ΔK/K↓ 曲线。

**验证标准**：亲眼看到 width 4096 时 kernel 变化 <1%，width 512 时 >10%——"无限宽极限"从口号变成你跑出来的数字。

### E4 QAT vs PTQ：亲手复现"2-bit 崩溃、4-bit 存活"（1-2 天，呼应 Needle 2）

**理论**：PTQ 在 ≤2-bit 基准崩溃（Needle 2 文档同款论断）；QAT 让量化噪声进梯度。

**最小实验**：字符级小 LM（同 E2 底座），三组：fp32 基线 / 4-bit PTQ（`torch.ao.quantization` 或手写 round-to-nearest + scale）/ 4-bit QAT（forward 伪量化，STE 反传）；比较测试 loss。

**验证标准**：得到"PTQ 掉 X、QAT 只掉 X/5"的自己的数字；顺手做 2-bit PTQ 看 collapse（模型输出乱码即"崩溃"的直观体验）。
**连接**：这正是服务器上 distill 模型未来做 INT8 部署（DCU int8 路径）的前置演习——Needle 2 的 CQ2-bit 思路"训练即量化"的本地最小版。

### E5 长度泛化：APE vs NoPE（1 天）

**理论**：ICLR 2025 formal framework——绝对位置编码下，长度泛化能力由任务是否属于 Limit Transformer 可表达类决定。

**最小实验**：字符级复制/反转任务，训练长度 ≤16，测试长度 32/64；对比 APE / NoPE / RoPE 三种位置方案的成功率断崖。

**验证标准**：得到一个"任务×编码"的成败矩阵——理论预测（periodic+local 任务可泛化）与你的矩阵一致性 ≥70%。

---

## C. 双向闭环：把 A 和 B 焊在一起（本季度主线）

```
A 侧（服务器）                          B 侧（本地 CPU）
distill_pipeline 24题 → distill.jsonl
        ↓
finetune_lora (LoRA SFT, 卡1)
        ↓                                    ↑
eval_holdout: base vs LoRA pass rate    E4 的 QAT 经验
        ↓                                    ↓
QAT-INT8（DCU）→ 部署 = "训练的模型=部署的模型"   ← Needle 2 路线个人复刻
```

这就是"应用数学研究型工程师"的最小完整闭环：**生成（A）→ 训练（A/B）→ 压缩（B）→ 部署（A）**，每一步都有自己的数字。

## D. 每周节奏（10-20h 参考）

| 周 | 主线（A，服务器/网络依赖） | 副线（B，本地随时可跑） |
|---|---|---|
| 1 | L0 环境恢复+NNG 重做 | E3 NTK（半天级，先尝甜头） |
| 2 | L1 三通道对拍实验 | E1 Muon |
| 3-4 | L2 miniF2F 基线 + L3 SFT | E2 scaling law |
| 5+ | L3 专家迭代循环 | E4/E5 + C 闭环 |

**网络中断预案**：服务器任务全部 nohup/detached（已验证）；断网窗口切 B 线——B 线零网络依赖，这就是双线设计的意义。

---

## 附：快速命令卡（贴墙）

```bash
# Lean 项目
lake exe cache get && lake build       # 预编译缓存+构建
# vLLM (DCU 卡1)
docker exec -d csmath bash -lc "ROC_VISIBLE_DEVICES=1 nohup vllm serve /work/models/DeepSeek-Prover-V2-7B --served-model-name prover --max-model-len 8192 --port 8177 > /work/prover-smoke/vllm_server_gpu1.log 2>&1 &"
# 蒸馏断点续跑
docker exec -d csmath bash -lc "cd /work/distill && nohup python3 distill_pipeline.py > run_full.log 2>&1 &"
# 杀 vLLM（防自杀正则）
pkill -9 -f "[v]llm serve"
```

生成：2026-08-25 · 上级 [MATHEMATICIAN_MASTER_INDEX.md](MATHEMATICIAN_MASTER_INDEX.md) · 姊妹篇 [AI_FOR_MATH_TOOLS.md](AI_FOR_MATH_TOOLS.md)
