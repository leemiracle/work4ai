# 实战案例 · Prover 数学 Agent（DeepSeek-Prover-V2 逆向蒸馏）

> **任务源**：逆向蒸馏 DeepSeek-Prover-V2-7B 关于数学发现的规律 → 生成 skill/harness/prompt → 融合到现有 math 相关 agent。
> **一手来源**：论文 arXiv:2504.21801（2025-04-30）+ [官方 repo](https://github.com/deepseek-ai/DeepSeek-Prover-V2) + [Damek Davis 独立解析](https://damek.github.io/random/deepseek-prover-v2-overview/)（2026-08-24 检索核实）。
> **执行环境**：内网 DCU 服务器（2× 内网GPU 64G，工作容器 容器：模型 /work/models/DeepSeek-Prover-V2-7B 13G + transformers 5.12 + Lean 4.21.0 x86 于 /work/lean-4.21.0-linux/）。
> **战绩背景**：MiniF2F-test 88.9%（Pass@8192，SOTA）、PutnamBench 49/658、AIME 15 题解 6（vs V3 informal 8——形式与非形式差距显著缩小）。
> **外部印证（2026-08-25 核实）**：ZIB 的 The Agentic Researcher（arXiv:2603.15914，ICML 2026 Workshop Oral）同样把科学方法论写成"十条戒律"注入 CLI agents——与本单元"逆向蒸馏十条规律"是同一哲学的独立实现，两边对读见 top-math-courses/AI_FOR_MATH_TOOLS.md §14.2。

---

## 一、逆向蒸馏：十条可操作规律

### R1 递归子目标分解——难度的来源是"跨度"而非"深度" ★核心
大模型（V3 671B）做**分解+形式化**：把定理拆成高层证明草图并同步形式化为 Lean 4 的 `have` 骨架（子目标留 `sorry`）；小模型（7B）做**局部证明**：逐个替换 sorry。关键机制：子目标从 have 语句提取替换原目标，**前面的子目标作为 premises 传给后续子目标**——"促进局部化依赖结构，发展更简单的引理"。
**规律**：7B 端到端证不出的定理，拆成跨度小的子目标后就能证出。**难度在跨度（一步要跨多远）不在深度（要跨多少步）**。

### R2 冷启动数据 = {NL 计划, 已验证 Lean 证明} 配对——非形式引导形式
数据筛选条件极其讲究：**只收"7B 端到端失败、但所有分解子目标都被解决"的问题**——拼起来的完整形式证明 + V3 的自然语言分解计划缝合为一条训练数据。
**规律**：这是教科书级的**最近发展区（ZPD）策展**——太简单学不到东西，太难学不动，"跳一跳够得着"的才进训练集。且 informal CoT 与 formal proof 是**引导关系不是竞争关系**。

### R3 一致性奖励——binary reward 会让模型绕过计划走捷径
RL 早期观察：生成证明的结构经常偏离 CoT 给出的引理分解 → 加入 consistency reward，显式强制最终证明包含所有分解的 have 引理，惩罚结构错位——对复杂多步定理提升尤其明显。
**规律**：**只看结果（编译通过）时模型会无视过程结构；结构对齐本身值得奖励**。（perfagent 单元的"verdict 与纯作弊收益两维度分开测"同构——结果对≠过程对。）

### R4 课程学习——子目标再生成"猜想定理"，难度渐进爬坡
分解出的子目标直接作为训练任务（两种形态：独立证 / 带前序子目标作 premises 证——后者训练上下文推理=真实证明中的引理使用）。
**规律**：**分解不仅是为了解原题，还是题目生成器**——子目标天然构成难度低于原题的课程序列。

### R5 专家迭代——验证器是免费的完美裁判
当前最优策略对上一轮未解决问题生成尝试 → Lean 验证 → 成功的进 SFT 集 → 训练更强模型 → 循环。
**规律**：**自举循环的把关者必须是确定性验证器**（binary +1/0，零标注、不可欺骗——除 sorry 之外）。与性能优化单元"LLM 当工程师，代码当守门员"、KernelBench 裁判哲学完全同构。

### R6 GRPO + prompt 策展——又是 ZPD
组相对策略优化（每定理采样一组候选，组内相对奖励，无 critic）；训练 prompt 只留"足够挑战但 SFT 模型可解"的问题。
**规律**：RL 阶段的数据策展与冷启动阶段同一条规律（R2 的 ZPD）在两个阶段重复出现——**"难度匹配"贯穿全程**。

### R7 skill 发现——小模型的冷门技能枝
7B non-CoT 模式解出 671B 漏掉的 13 道 PutnamBench 题，用的是 `Cardinal.toNat` / `Cardinal.natCast_inj` 这类**类型鸿沟处的冷门转换 tactic**（Lean 严格区分 Cardinal/Nat，标准算术 tactic 不会自动桥接）。
**规律**：**小模型 + RL 会长出大模型没有的技能枝**；大采样（Pass@8192）的尾部是多样性富矿——这也是"为什么还留着 non-CoT 小模型"的答案。

### R8 prompt 双模式——官方模板朴素得惊人
- **CoT 模式**（复杂定理）："Complete the following Lean 4 code … Before producing the Lean 4 code, provide a detailed proof plan…"
- **non-CoT 模式**（简单定理/专家迭代）：直接补全代码块，无计划要求。
**规律**：**没有魔法 prompt，只有"代码补全框架 + 可选计划要求"**；威力的来源在训练（冷启动数据教会它"计划→have 骨架→填 sorry"的节奏），不在 prompt 措辞。

### R9 尺寸分工——大模型当建筑师，小模型当瓦工
分解/形式化用 671B（需要通用数学知识+形式化能力），子目标证明搜索用 7B（局部问题+量大+便宜）。
**规律**：与性能优化单元"LLM 提议、guard 裁决"、 Ruflo"Agent=Model+Harness" 同构——**能力分层外包，贵的能力只用在刀刃（分解）上**。

### R10 诚实边界（Damek Davis 指出）
premises 结构（前序子目标作为上下文）的益处论文**未单独消融**；数据严格过滤"全子目标解决才保留"（部分成功丢弃，宁缺毋滥）。
**规律**：读论文要区分"验证过的机制"与"合理但未消融的设计"。

### 规律总表（一条主线串起来）

```
ZPD 策展（R2/R6）──贯穿冷启动与 RL
   ↓
分解降跨度（R1/R4）──大模型建筑师（R9）
   ↓
验证器把关（R5）+ 结构对齐奖励（R3）
   ↓
双模式 prompt（R8）+ 尾部 skill 富矿（R7）
```

## 二、三个 Deliverable

| 物 | 位置 | 对应规律 |
|---|---|---|
| **skill：`oprover-math`** | `~/.config/opencode/skills/oprover-math/SKILL.md`（全局，任意 LLM 的证明行为规范） | R1/R2/R8/R5 |
| **harness：`prover_harness.py`** | [./prover_harness.py](./prover_harness.py)（递归子目标闭环，可跑） | R1/R4/R5/R9 |
| **prompt：`prompts.py`** | [./prompts.py](./prompts.py)（官方双模式逐字保真 + 分解 prompt 重构版） | R8/R1 |
| **蒸馏流水线** | [experiments/distill_pipeline.py](./experiments/distill_pipeline.py)（420 行：e2e→分解→逐 sorry→ZPD 入库，断点续跑）+ [finetune_lora.py](./experiments/finetune_lora.py) + [eval_holdout.py](./experiments/eval_holdout.py) + 题库 24 core + 12 holdout | R1/R2/R4/R5 全链 |
| **Needle 2 融合笔记** | [./needle2-fusion.md](./needle2-fusion.md)（窄域/QAT/KV有界/语法约束四映射 + 批判性边界） | 借法 |
| **语法约束解码实验** | [experiments/prover_grammar_decoding.py](./experiments/prover_grammar_decoding.py)（H1 轻约束收益 / H2 强约束反伤——量化"约束收益∝空间封闭度"） | Needle2 借法 |

（冒烟实测见 §四；融合挂网见 §五）

## 三、harness 架构（六层映射，复用本项目的 guard 哲学）

```
decompose（建筑师：API 大模型/glm-5.3 或本地）
   → 输出 have 骨架（子目标留 sorry）          ← R1/R9
   → 逐子目标 prove（瓦工：Prover-V2-7B @DCU / 任意小模型）
      · 前序子目标已证结果作为 premises 注入    ← R1
      · 失败→子目标再分解（深度+1）或换模式      ← R4
   → 合成完整证明 → lean 单文件验证（无 sorry 才算过）← R5 守门员
   → 成功入 win 库（expert iteration 数据积攒）/ 失败子目标入 trap 库
```

关键工程决策：
- **验证器独立于生成器**（lean 子进程，二值判定）——R5 的工程化
- **架构-二进制匹配坑**：工作容器 是 x86_64，`/work/lean4`（aarch64）不可用，必须用 `/work/lean-4.21.0-linux/`——踩坑实录
- **单文件 lean 无 mathlib**：冒烟用核心库定理；正式 harness 需 lake 项目 + mathlib 缓存（下一步）
- sorry 显式拒绝：lean 对 sorry 只出 warning 仍 exit 0，验证器必须查 stderr——**"能编译"≠"证完了"**（R10 式诚实边界在工程上的对应物）

## 四、冒烟实测（2× 内网GPU DCU，2026-08-24）

**三轮降级实录**（对复现者是高价值情报）：

| 尝试 | 栈 | 结果 |
|---|---|---|
| 1 | transformers 5.12 + device_map | ❌ 需装 accelerate → 装后 `apply_chat_template` 返回 BatchEncoding（5.12 已知坑）→ 修后 **DynamicCache 在 DTK 上崩**（KV cat 维度错） |
| 2 | vLLM 0.23.1 rocm633 **offline LLM 类** | ✅ 66s 加载、6/6 生成成功、内容正确（`norm_num`/`induction n <;> simp_all`）——但 **detokenize 损坏**（Ġ/Ċ 未还原+空格吞失，token_ids 同污染） |
| 3 | vLLM **server 模式**（`vllm serve` :8177 + HTTP） | ✅ **2026-08-25 验证通过**：HTTP content 正常（detokenize 坑仅限 offline 类）；e2e 冒烟 **5/6 SOLVED**（e2 CoT 92s；e3-e6 non-CoT ~18s；e1 分解阶段败） |

**2026-08-25 全量蒸馏启动**（`distill_pipeline.py`，24 题，断点续跑设计：api 断连绝不落死标记，等 server 复活重试）。排障三坑（对复现者是高价值情报）：
- **DCU 选卡**：容器内 `HIP_VISIBLE_DEVICES=1` 无效（hipErrorNoDevice）；DTK 正统是 **`ROC_VISIBLE_DEVICES=1`**（实测 torch count=1 + 显存分配落卡1）
- **numpy 2.x ABI 事故**：numpy 被并行环境升到 2.4.6 → DCU 定制 torch（1.x ABI）下 vLLM EngineCore 死于 `buffer_utils.py:49 "Numpy is not available"`。修复 `pip install -i 清华源 numpy==1.26.4`。**教训：环境被并行改动后先查 site-packages 时间戳**
- **pkill 自杀坑**：`pkill -9 -f vllm` 会匹配自身 bash -c 命令行杀死 shell → 必须 `pkill -9 -f "[v]llm serve"`

**生成侧已验证的行为事实**（offline 模式，6/6）：

| 定理 | CoT 模式 | non-CoT 模式 |
|---|---|---|
| t1-rfl | 581tok：先"Detailed Proof and Analysis"再证明 | **22tok：`theorem smoke_add : 2+2=4 := by norm_num` 一次过（正确）** |
| t2-have | 704tok：结构化分析（Problem/Proof 分节） | 256tok：重复骨架（该题对 non-CoT 偏难） |
| t3-lemma | 825tok：分析 `Nat.succ` 语义 | 45tok：`induction n <;> simp_all [...]`（结构正确） |

行为观察与论文 R8 一致：**non-CoT 短平快（22-45tok）适合简单题，CoT 长分析（581-825tok）适合复杂题**；t2 对 7B 都不容易——恰好是分解路线（R1）该接手的场景。

**环境备忘**（工作容器 容器）：宿主 `/root/工作容器` ↔ 容器 `/work`；Lean 用 `/work/lean-4.21.0-linux/`（x86，**`/work/lean4` 是 aarch64 不可用**）；vLLM server 恢复命令（**卡1**）：`docker exec -d 工作容器 bash -lc "ROC_VISIBLE_DEVICES=1 nohup vllm serve /work/models/DeepSeek-Prover-V2-7B --served-model-name prover --max-model-len 8192 --port 8177 > /work/prover-smoke/vllm_server_gpu1.log 2>&1 &"`；蒸馏流水线：`docker exec -d 工作容器 bash -lc "cd /work/distill && nohup python3 distill_pipeline.py > run_full.log 2>&1 &"`。服务器网络间歇中断（08-24/08-25 两次入方向 100% 丢包，出方向正常）——**所有长任务必须 nohup + docker exec -d 保活**。

## 五、融合挂网

- [讲透Lean4数学/README](../../讲透数学/讲透Lean4数学/README.md)：加"Prover 数学 Agent 实战"条目（NNG 学习者 → Prover 工具使用者 → harness 造物主三级跳）
- [top-math-courses/AI_FOR_MATH_TOOLS.md](../../top-math-courses/AI_FOR_MATH_TOOLS.md)：AlphaProof/LeanCopilot 条目旁加 DeepSeek-Prover-V2 条目（十条规律+本地部署）
- skill `oprover-math` 全局可用（opencode 自动加载）
- 方法论互链：与 [实战案例-性能优化Agent](../实战案例-性能优化Agent/README.md) 的 guard/裁判哲学互认（R3/R5 与双测协议同构）

---

生成：2026-08-24 · 上级 [讲透Agent/README](../README.md)
