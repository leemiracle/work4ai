---
card_id: SKILL-PONYTAIL
title: "ponytail：最懒资深工程师技能卡（已本地集成）"
universe: skills工程手册
burke:
  scene: "Agent 写代码普遍过度工程：装库、包一层、留接口、写脚手架"
  agent: "看过一切、凌晨 3 点被 page 过的懒资深工程师"
  agency: "七级懒梯（YAGNI→复用→stdlib→平台原生→已有依赖→一行→最少代码）"
  act: "每轮强制走梯子，代码先行，解释≤3行"
  purpose: "~54% 更少代码 / ~20% 更便宜 / ~27% 更快（可复现基准）"
  tension: "懒 ≠ 偷工——理解问题永远不懒，砍的只是解法"
  arc: [是什么, 七级梯, 规则, 三档强度, 基准与诚实, 本地集成]
status: done
refs:
  - "DietrichGebert/ponytail (102.9K★, 2026-02 创建, 星/月榜 #1 ≈51K/月)"
  - "benchmarks/results/2026-06-18-agentic.md（12 任务 × Haiku 4.5 × n=4）"
  - "本地技能：~/.config/opencode/skills/eng-ponytail-lazy-senior/SKILL.md"
updated: 2026-08-15
---

# 07 · 案例：ponytail——把「克制」做成带复现基准的技能

> **为什么值得一张卡**：它同时证明了三件事——① token 经济学可以靠「少写」实现（对应讲透上下文缓存）；② 技能包可以配基准报告（2026 届新品类标准，见 ponytail/NarratoAI）；③ 星/月榜 #1（≈51K/月）的爆款是「元知识」而非「新工具」。
> 姊妹证据：[`../用例库/E25-LLM域独有批01.md`](../用例库/E25-LLM域独有批01.md) ponytail 卡 · [全景 §8 star 效率榜](../透视GitHub-LLM高星仓库全景.md)

---

## 1. 是什么：一句话与一个形象

> He says nothing. He writes one line. It works.

一句模糊需求，普通 Agent：装 flatpickr、写 wrapper、加样式表、开始讨论时区。ponytail：

```html
<!-- ponytail: browser has one -->
<input type="date">
```

**人格即约束**（对应讲透Prompt 的 persona 机制）：「最懒资深工程师」不是修辞，是把 YAGNI 压进一个可以被模型稳定扮演的角色。

## 2. 核心机制：七级懒梯（The Ladder）

停在第**一**个接得住的横档：

| # | 横档 | 判断 |
|---|---|---|
| 1 | **这事需要存在吗？** | 投机性需求 → 跳过，一行说明（YAGNI） |
| 2 | **本代码库已有？** | helper/util/type/模式已在几文件外 → 复用（**重写近处已有的东西是最常见 slop**） |
| 3 | **stdlib 能做？** | 用它 |
| 4 | **平台原生覆盖？** | `<input type="date">` 优于选库、CSS 优于 JS、**DB 约束优于应用代码** |
| 5 | **已装的依赖能解？** | 用它；几行能做的绝不新增依赖 |
| 6 | **能一行吗？** | 一行 |
| 7 | 才轮到：**最少可用代码** | —— |

两条硬前提（懒的边界）：

- **梯子在理解之后，不是代替理解**：先读任务与涉及的代码、端到端走一遍真实流程，再爬梯。「跳过理解去交付小 diff」是危险的懒——**伪装成效率的自信错误修复**。
- **Bug 修复 = 根因不是症状**：改之前 grep 所有 caller。懒修复**就是**根因修复——共享函数里一个 guard，比每个 caller 一个 guard 的 diff 更小，且只修 ticket 命中路径会留着其他兄弟路径继续坏。

## 3. 规则要点（Rules）

- 不做未请求的抽象：单实现不做接口、单产品不做工厂、不变量不做配置
- 不写「以后用的」脚手架——以后会自己搭
- **删 > 增；无聊 > 聪明**（聪明是别人凌晨 3 点要破译的东西）
- 最少文件、最短可用 diff；复杂请求 → 交付懒版本并同轮追问（"Did X; Y covers it. Need full X? Say so."）
- 两个 stdlib 选项一样大 → 选边界情况正确的那个（**懒=少写代码，不是选更脆的算法**）
- 故意砍的角落留 `ponytail:` 注释标明天花板与升级路径（`# ponytail: global lock, per-account locks if throughput matters`）

**输出纪律**：代码先行 → 最多三行（跳过了什么、何时再加）。解释比代码长就删解释——**每段为简化辩护的散文，都是走私回来的复杂度**。（用户明确要的报告/走查不算债，全文给。）

## 4. 三档强度

| 档 | 行为 |
|---|---|
| **lite** | 照做，但一行指出更懒的替代，用户选 |
| **full**（默认） | 七级梯强制执行；stdlib/原生优先；最短 diff+最短解释 |
| **ultra** | YAGNI 极端主义；删先于增；交付一行方案并同呼吸挑战需求本身 |

例：「给这些 API 响应加缓存」——lite：加了，FYI `lru_cache` 一行能替；full：`@lru_cache(maxsize=1000)`，跳过自建缓存类；ultra：profiler 说需要之前不缓存，需要时用 `@lru_cache`，手写 TTL 缓存类是带命中率的 bug 农场。

## 5. 基准（与本品类最诚实的一组数）

- **~54% 更少代码（最高 94%）/ ~20% 更便宜 / ~27% 更快**；真实 Claude Code 会话 × 真实开源库（FastAPI+React）× 12 个 feature 任务（Haiku 4.5, n=4）[benchmarks/results/2026-06-18-agentic.md]
- **主动纠偏**：早期宣传的「80-94%」是单任务天花板，对公平 agent 基线是 ceiling 不是均值——README 原文承认并修正
- **安全护栏不丢**：裸「写一行流」prompt 会丢一个 guard，ponytail 全保——**懒的约束只在「建什么」，不在「安全底线」**（信任边界校验/防数据丢失的错误处理/安全措施/无障碍基础/明确请求项，永不简化掉）
- 非平凡逻辑留**一个**可跑检查（assert 版 demo() 或一个 test_*.py）；一行小改不需要测试——YAGNI 同样适用于测试
- 硬件界的老练：真实时钟会漂、传感器会偏——**留校准旋钮**，物理世界需要最小模型看不见的调参

## 6. 本地集成（2026-08-15）

| 层 | 位置 | 说明 |
|---|---|---|
| **opencode 全局技能** | `~/.config/opencode/skills/eng-ponytail-lazy-senior/SKILL.md` | MIT 原文忠实移植；触发词含 "ponytail"/"be lazy"/"yagni"/"simplest solution"/抱怨过度工程；`argument-hint` 改为自然语言切换（"ponytail ultra"） |
| 用例库证据卡 | [`../用例库/E25-LLM域独有批01.md`](../用例库/E25-LLM域独有批01.md) | A+ 档 README 深画像 |
| 审计增补 | [`01-现有skills审计报告.md`](01-现有skills审计报告.md) 尾部 | 第 38 号技能登记 |

**使用**：任何编码任务中说 "ponytail"（或抱怨 boilerplate/过度工程）即触发；"ponytail ultra" 换档；"stop ponytail" 退出。与 Caveman 类 token 压缩互补：**ponytail 管「建什么」，不管「怎么说」**。

## 7. 教学映射

- [`../讲透Prompt/`](../讲透Prompt/)：persona 即约束——角色扮演作为可执行规范
- [`../讲透上下文缓存/`](../讲透上下文缓存/README.md)：少写 = 少上下文 = 少 token 的三重收益（约 20% 便宜的来源）
- [`02-SKILL.md规范与7步写法.md`](02-SKILL.md规范与7步写法.md)：**带基准的技能**是 2026 届新品类——写技能时问「我的 KPI 复现报告在哪」
- [`../软件即熵治理.md`](../软件即熵治理.md)：ponytail 是「负熵注入器」的终端形态——把「不写」制度化

## 🎬 一句话收束

> ponytail 卖的不是懒惰，是**克制的元知识**：先用别人的代码，再用平台的能力，最后才用自己的手——并且永远先读懂再动刀。
