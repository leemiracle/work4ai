# skill_agent（v3）：skill 库为一等公民的 RL agent —— skills 全技术 × RL 自进化

> **定位**：[rl_agent.py](./rl_agent.py)（v2，原子工具）的升级版——动作空间从"固定 4 工具"变为"**原子工具 + 动态 skill 库**"，并让 agent 自己进化 skill 库。
> **融合蓝本**：[deepseek-harness 插件机制全景](../Agent框架案例/deepseek-harness插件化框架/notes/02-capability-seams/02-插件机制全景.md) + deer-flow 渐进披露 + opencode SKILL.md 机制 + SkillWeaver（agent 自己造工具 ← 讲透Agent/05 What 轴）。

---

## 一、skills 技术融合映射（六要素全覆盖）

| 插件机制要素（harness 笔记） | skill_agent 落点 | 代码锚点 |
|---|---|---|
| **Plugin 形态**（cordis.yml）| skill = JSON（name/description/triggers/body/meta）——语义对齐 opencode SKILL.md | `new_skill()` |
| **Loader / HMR**（热重载）| `SkillStore.scan()` 每任务前重扫，新 skill 落盘即生效 | `SkillStore.scan` |
| **渐进披露**（deer-flow）| 决策只看 name+description（`+0.05/词` 语义先验），body 执行时才展开 | `desc_match_bonus` / `execute_skill` |
| **scope** | `triggers` 限定激活状态（concept/experiment/paper/mixed/any） | `active_for()` |
| **自修改**（preset 之上）| `evolve_skills()`：🧬 生成（教训聚类→新 skill）/ 🔁 变异（低成功率→改 body）/ 🗑️ 归档（持续失败）| `evolve_skills` |
| **preset + hook** | 种子 8 个 RL 专属 skill；execute 前后 hook（meta 谱系统计=进化压力源） | `seed_skills` / `skill_success_hook` |

**专属 RL 领域 8 技**（preset）：q_learning_tutor / grpo_group_lab / bandit_playground / dqn_replay_guide / paper_wh_locator / rlvr_reward_consult / pomdp_explainer / **meta_prompt_tuner**（meta-skill：调 agent 自身 APO 接口——skill 迭代自身的入口）。

## 二、RL 融合（v2 → v3 核心升级）

```
动作空间 = 原子工具 + scope 内 skills（动态 N+3）
π(a|s)   = ε-greedy over [ Q(s,a) + 0.05×desc语义匹配 ]      ← Q 学习值逐渐盖过语义先验
reward   = RLVR + 相关性闸门：罐头 kb_keys 命中≠证据（证据行必须含任务词 bigram；
           实验只对 experiment 态充分——概念题跑实验不算回答）
进化环   = 失败教训聚类 → 🧬 生成；usage≥2 且成功率<0.5 → 🔁 变异；usage≥3 且<0.3 → 🗑️ 归档
```

## 三、demo 实测弧线（2026-08-17，纯本地）

```
场景1 concept 题 → desc 语义选型首选 q_learning_tutor ✅（非字母序）
场景2 GRPO 实验  → grpo_group_lab 一击命中（21seed bandit 降方差实测）✅
场景3 冷门措辞   → 探索/利用 bigram 命中 KB 真证据（合法成功）✅
场景4 乱码真缺口 → 全链失败 → 教训落盘 ❌
场景5 再失败     → 教训聚类≥2 → 触发自修改 ❌
场景6 三战       → 🧬 adaptive_mixed_9 诞生（kb_keys=['qqwwzzpp']）→ 优先被探索 → 诚实仍败 ❌
                  （教学点：进化造检索结构，不造知识——能力边界=KB 覆盖）
战报 3/6：KB 覆盖的题全胜；缺口诚实失败 ×3
```

## 四、开发中抓到并修复的 3 个 reward hacking 活体（连续第三轮）

| # | 问题 | 修复 |
|---|---|---|
| 1 | **罐头词作弊**：skill 罐头 kb_keys（"What/进化"）命中与任务无关行 → 虚假 3/3 成功 | 相关性闸门：证据行必须含任务词 |
| 2 | **无关实验充数**：概念题跑 DQN 实验也算"证据" | 实验仅对 experiment 态充分 |
| 3 | **中文分词失灵**：空格分词下整句成巨词，闸门/选型/查询三处连锁失效 | `_zh_words` bigram 启发式统一三处 |

加上 v2 的 2 起（paper_locate 未匹配计成功 / 乱码跑默认实验），本案例已累计 **5 起 reward hacking 活体**——每个都在"验证即证据"下当场闭环。

## 五、快速开始

```bash
python3 skill_agent.py demo        # 六场景弧线（含进化环）
python3 skill_agent.py --task "什么是 RLVR 的可验证奖励？"
python3 skill_agent.py chat        # 交互（skill 库持久，跨会话成长）
python3 skill_agent.py evolve      # 手动触发一次 skill 库自修改
# skill 文件：memory/skills/*.json（运行产物不进 git）
```

## 六、与 harness 工程手册 Phase 4（共进化）的对位

手册 01 章"Phase 4 Co-evolution：模型-harness 共同进化（agent-native 训练 + 可学习 harness）"——skill_agent 是其**零训练版最小实现**：harness 的可学习部分（skill 库）由 RL 信号（Q 表 + 谱系统计）驱动进化，模型侧不动权重。升级路线：skill body 从"配方"升级为"可执行片段"（Voyager 技能库方向）→ 真正的 Phase 4。

---
立项：2026-08-17 · v3.0.1（3 轮验证即证据迭代）· 依赖：rl_agent.py（复用其原子工具与安全件）
