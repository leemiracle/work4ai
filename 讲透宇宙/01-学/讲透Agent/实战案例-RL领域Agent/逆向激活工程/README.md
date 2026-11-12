# 逆向激活工程（RAE）· 总纲

> 项目代号 **rae**（Reverse Activation Engineering）· 隶属 `实战案例-RL领域Agent/`
> 引擎：**glm-5.3**（zhipu-ai-coding-plan，`thinking:{type:enabled, level:max}`，2026-08-19 实测档案见 §5）

---

## 0 · 两条观察规律（项目公理）

**规律 1（约束链）**：LLM 应用 = 从人类自然语言出发、经层层约束，最终为了**激活超大规模参数中的特定参数子集**。

**规律 2（层谱 trade-off）**：越接近自然语言的层——越易解释、随机性越大、调整越便宜；越接近参数的层——越易精确激活、确定性越强、但越难解释、调整成本越高。

### 形式化：激活层谱（Activation Stack）

```
层 5  自然语言 Prompt     ── 解释性 █████████ / 确定性 ▓░░░░ / 成本 ~0        / 迭代 秒
层 4  Skills（SKILL.md）  ── 解释性 ████████  / 确定性 ▓▓░░░ / 成本 低       / 迭代 分钟   ← 程序性知识+工具
层 3  Context（RAG/记忆） ── 解释性 ██████    / 确定性 ▓▓▓░░ / 成本 中       / 迭代 小时   ← 检索即约束
层 2  Adapter（LoRA）     ── 解释性 ██        / 确定性 ▓▓▓▓░ / 成本 GPU时    / 迭代 天     ← 权重增量 ΔW=BA
层 1  参数（Base/RLHF）   ── 解释性 ▓         / 确定性 ▓▓▓▓▓ / 成本 集群月   / 迭代 季     ← 能力的物质基座
```

正向工程（社区主流）：Prompt→Context→Skills→LoRA，**从软到硬逐层下探**，每层不达标才降一层。
**本项目逆向**：从硬往软走——**以已有的参数层工件为"能力参照物"，逆向生成等效的软层工件**，换取可解释性/可移植性/零训练成本。

## 1 · 逆向生成的定义

> **逆向激活生成（Reverse Generation）**：给定目标能力 C 的参数态实现（如多模态 LoRA），在软层（skill/context/prompt）搜索程序态实现 C'，使得行为等价度 BehaviorDist(C, C') ≤ ε 且成本-解释性占优。

这是一个**搜索问题**，映射空间巨大（skill 结构 × 工具组合 × prompt 表述 × 工作流顺序），**用 RL/bandit 搜索**（继承本目录 rl_agent v4 的 UCB1 + cascade 组件），奖励 = 行为等价度 − λ·token 成本。

### 旗舰案例：多模态 LoRA → Skill（用户例子的形式化）

```
路线 A（参数态）  ：LLM + 多模态LoRA      图片 ──ViT+ΔW──→ 模型"直接看见"   解释性差/不可移植/需GPU
路线 B（程序态）  ：裸LLM + 视觉skill      图片 ──工具脚本──→ 结构化描述 ──→ 模型"读报告理解"
  skill 内容 = { 视觉后端调用法（caption/检测/OCR 脚本）,
                 查询策略（何时查/查什么/查多细）,
                 图像任务工作流（描述→分解→推理） }
逆向生成目标 = 从路线A的行为自动搜索出路线B的skill配置
```

**真实世界对应物**：Claude Code 给无视觉模型配 vision skill/MCP 就是路线 B 的手工版；本项目做的是**自动化版**——RL 搜出最优 skill 结构。学术血统：soft→hard prompt 蒸馏（PEZ, Wen et al.）、tool learning、知识管理理论 Polanyi 隐性→显性转化。

## 2 · 四层逆向生成器矩阵（Roadmap）

| 生成器 | 输入（参数态参照物） | 输出（软态工件） | 状态 |
|---|---|---|---|
| `generators/lora2skill/` | 多模态/领域 LoRA 的行为规格 | SKILL.md + 工具调用脚本 + 查询策略 | **旗舰，exp2 实证中** |
| `generators/lora2context/` | 领域 LoRA | 检索库（LoRA 训练知识的 context 化） | 规划 |
| `generators/context2skill/` | 长期上下文/RAG 管线 | 可复用 SKILL.md（工作流外化） | 规划 |
| `generators/prompt_distill/` | 系统 prompt 集群 | 精简 prompt（soft→hard 蒸馏，接 09 章 McNemar 方法） | 规划 |

### 📌 断点待办（2026-08-20 会话从这继续）

1. **UCB1 闭环**：把 exp3 的"多候选→KL 选择"自动化（候选生成=臂，KL 降幅=奖励，替代人工看表选 prompt2）——即 `prompt_distill` 生成器的 RL 内核；
2. **真多模态 LoRA**：用 LLaVA 系（或 Qwen2.5-VL-3B 量级）替换格式行为，测逆向在"视觉能力"这类不可完全言说行为上的边界；
3. **v2 严格化**：全序列 KL（不只 answer 首 token）+ 输出分布对比 + 多 seed 方差。
   环境已就绪：本机 torch2.10cpu+peft0.20+transformers5.10dev，模型库 `~/ai/models/`（Qwen2.5-0.5B-Instruct 已在），下载须 `HF_ENDPOINT=hf-mirror.com`，长任务 `setsid nohup` 防 wrapper 组杀；远端海光机仅侦察不跑（红线）。exp3 三段式可复跑：`python3 experiments/exp3_lora2text_real.py {train|reverse|eval}`（adapter 已在 artifacts/exp3_lora/，勿重训）。

层选择元问题（逆向到哪层停）也由 RL 决策：行为等价度阈值 + 成本预算 → 输出 Pareto 前沿上的最优层。

## 3 · 目录结构

```
逆向激活工程/
├── README.md                 # 本文件（总纲）
├── generators/               # 四层生成器（按层分目录）
├── experiments/
│   ├── exp1_layer_tradeoff.py    # 层谱 trade-off 定律 toy 验证（零 API，纯本地）
│   └── exp2_multimodal_skill_rev.py  # 旗舰：LoRA→skill 逆向（glm-5.3 实跑）
├── artifacts/                # 实验输出（json/png，绝不进 git）
└── （后续）01-理论.md / 02-旗舰案例.md / 实验报告.md
```

## 4 · 与项目内资产的接线

- RL 组件复用：`../harness_rl/`（UCB1/cascade/账本）、`../rl_agent.py` 血统
- 层谱 taxonomy ↔ `../../Agent框架案例/Topics全链路全景/`（十层 topics 的谱系学表亲：那边是生态观测，这边是能力工程）
- skill 规范 ↔ `../../Agent框架案例/Skills生态全景/notes/02`（SKILL.md 解剖）
- prompt 蒸馏方法 ↔ `../../../工程化手册库/`（若存在 prompt 手册 09/12 章方法）

## 5 · 引擎实测档案（2026-08-19，本会话一手）

| 项 | 值 |
|---|---|
| 端点 | `https://open.bigmodel.cn/api/paas/v4/chat/completions`（zhipuai-coding-plan 凭证，读 `~/.local/share/opencode/auth.json`，绝不硬编码） |
| 模型 | `glm-5.3`（旧"1220 无权限"已过时，现套餐内可用） |
| thinking | **必须 enabled**（always-thinking 模型，不支持 disabled）；强度用 `{type:enabled, level:max}` 或 `reasoning_effort:max` |
| 实测注意 | `level` 被接受但 low/max 的 rt 无显著差（358-429t 同题）——端点疑似静默忽略强度档；以 max 为准 |
| 延迟/消耗 | 简单题 rt≈78-95t；数学题 rt≈350-430t；每次调用 3-15s |
| 继承坑 | coding 端点 vs paas 端点行为不同（09 章教训）；temperature 0.1 仍带方差 → 判分必须规则可判（RLVR） |

## 6 · 论文档案（四篇全部实测核实，2026-08-19 webfetch/search 一手）

用户提供的"LoRA→Text 逆向"技术报告及其自我澄清（自称 arXiv 编号是编造的）经逐篇实测：**四篇论文与编号全部为真**——那份自我澄清本身不可靠。元教训：**连模型的自我检讨都不可信，只有实测可信**（铁律 ⑧ 的强化版）。

| arXiv ID（核实为真） | 论文 | 在本项目的角色 |
|---|---|---|
| 2605.27642 | Learning to Translate from Soft to Hard LLM Prompts（2026-05-26，Kongsomjit/Goyal/Whitehill） | exp3 方法 C 的直接血统：训练翻译器把 soft prompt verbalize 为自然语言；官方仓库 macmacmacmac/softprompt_translator |
| 2602.15902 | Doc-to-LoRA: Learning to Instantly Internalize Contexts（Sakana AI，ICML 2026） | 正向超网络 H: doc→LoRA；本项目的逆向目标即 H⁻¹ 的行为版（官方仓库 SakanaAI/doc-to-lora，5.9k★） |
| 2506.11516 | Brewing Knowledge in Context: Distillation Perspectives on ICL（2025-06-13） | 统一理论基础：ICL=隐式蒸馏，attention≈隐式梯度步——"LoRA 显式更新 vs prompt 隐式更新"等价性的理论根据；MMD 界给出好 prompt 判据 |
| 2307.06865 | Effective Prompt Extraction from Language Models（Zhang/Carlini/Ippolito，USENIX Security 2024） | 黑盒逆向路径：翻译攻击提取 system prompt——exp3 reverse 阶段的攻击面参照 |

## 6.5 · exp3 战报（2026-08-19，全本地真链路）

真训 LoRA（Qwen2.5-0.5B，trainable 1.08M/0.22%，150 步/31 分钟/8 核 CPU，loss 5.78→0.0006，注入格式行为 `RAE-7X:`）→ glm-5.3 黑盒 verbalization（12 对样本→3 候选）→ answer 首 token 真 KL 评估（24 held-out）：

| 变体 | 前缀命中 | KL(P_lora‖P_var) | 相对 base 降幅 |
|---|---|---|---|
| base 裸模型 | 0/24 | 20.85 | — |
| +prompt1 | 3/24 | 8.36 | 59.9% |
| **+prompt2（最优）** | **13/24** | **2.27** | **89.1%** |
| +prompt3 | 5/24 | 7.19 | 65.5% |

**结论**：① `Base + Hard Prompt ≈ Base + LoRA` 量化成立——60 字中文 prompt 恢复 LoRA 行为偏移的 89%（KL 口径）；② 不完全等价（13/24≠24/24）——prompt 表达力与 0.5B 指令跟随的边界，与 ICL-蒸馏理论（2506.11516 MMD 界不为零）一致；③ 候选质量方差大（59.9% vs 89.1%）→ verbalization 需多候选+选择机制（RL 接入点）；④ glm-5.3 连训练数据隐含的"极简风格"都逆向出来了（行为考古学）；⑤ 已知瑕疵：lora_hits 检测器 tokenizer 粒度误判（显示 0/24，但 reverse 阶段生成侧实见 12/12 前缀，KL 为硬指标不受影响）。

## 7 · 诚实边界

1. exp2 的"LoRA"是**模拟**（合成场景直通=参数态理想化），非真训练 adapter——**exp3 已修正此局限**：本地 CPU（8 核飞腾，~17s/步）真训 Qwen2.5-0.5B LoRA（trainable 1.08M/0.22%），glm-5.3 逆向生成 prompt，answer 首 token 位置真 KL 散度评估——"写的太假"的批评由此回应；
2. exp3 的 KL 只在 answer 首位置（next-token 分布），非全序列分布 KL（留 v2）；
3. 层谱 trade-off 的"解释性"是定性评分（规则可读性），主观成分已标注；
4. 远程服务器（内网GPU服务器，vllm Qwen3-32B）仅侦察不使用——用户红线，项目全本地跑。

*updated: 2026-08-19*
