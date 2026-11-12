# 01 · gpt-5-4-prompting：把提示词当 API 契约写的内部指南

## 角色定位

`plugins/codex/skills/gpt-5-4-prompting/` 是插件里唯一一组"教 Claude 如何给 Codex 写 prompt"的知识资产。SKILL.md 开宗明义（`plugins/codex/skills/gpt-5-4-prompting/SKILL.md:7` 标题，`:9` 触发条件是 codex-rescue 子代理需向 Codex 求助时）。它 frontmatter 里 `user-invocable: false`——用户敲不出来，只有挂载它的 codex-rescue 子代理（`plugins/codex/agents/codex-rescue.md:6-8` 的 skills 列表）在转发任务前加载，用来把用户的原始请求收紧成更好的 Codex prompt。一句话定位：**子代理的提示词编译器前端**，产出不进任何运行时代码，只改变发往 `codex-companion.mjs task` 那一个 Bash 调用里的文本质量（该契约见 `plugins/codex/skills/codex-cli-runtime/SKILL.md:14`：prompt 改写是唯一被允许的 Claude 侧工作）。

## 内部结构

一主三辅四份 markdown：

- **SKILL.md（54 行）**：方法论主体。四条核心规则在 `plugins/codex/skills/gpt-5-4-prompting/SKILL.md:14-17`——一次一个明确任务、显式定义"完成"、防瞎猜要加 grounding/verification、优先改契约而非升推理档位。默认配方五块（`plugins/codex/skills/gpt-5-4-prompting/SKILL.md:20-25`）：task / structured 或 compact_output_contract / default_follow_through_policy / verification 或 completeness / grounding 或 citation。"何时加块"矩阵在 `:27-31`：编码调试加 completeness+verification+missing_context_gating；评审加 grounding+structured+dig_deeper；研究加 research_mode+citation；可写任务加 action_safety。
- **references/prompt-blocks.md（172 行 21 节）**：块字典，六大组——Core Wrapper（`plugins/codex/skills/gpt-5-4-prompting/references/prompt-blocks.md:6`，task 块 `:8`）、Output and Format（`:18`，structured_output_contract `:20`、compact `:32`）、Follow-through（`:43`，default_follow_through_policy `:45`、completeness_contract `:56`、verification_loop `:68`）、Grounding（`:79`，missing_context_gating `:81`、grounding_rules `:92`、citation_rules `:104`）、Safety（`:115`，action_safety `:117`）、Task-Specific（`:140`，research_mode `:142`、dig_deeper_nudge `:153`）。每节是一段可直接复制的规范英文文本。
- **references/codex-prompt-recipes.md（150 行）**：五套端到端模板——Diagnosis（`plugins/codex/skills/gpt-5-4-prompting/references/codex-prompt-recipes.md:7`，root cause/evidence/smallest safe next step 三段契约）、Narrow Fix（`:37`，"最小安全修复+完成前不许停"）、Root-Cause Review（`:72`）、Research or Recommendation（`:101`）、Prompt-Patching（`:127`，续线程只发 delta 指令）。
- **references/codex-prompt-antipatterns.md（100 行）**：七类反模式，每类 Bad 原文 vs Better 的 XML 改写。

## 外部连接

上游唯一消费者是 codex-rescue 子代理：`plugins/codex/agents/codex-rescue.md:22` 允许"仅用它收紧 prompt，不得借此自己读库解题"。下游对接两处真实 prompt 管道：一是对抗评审模板 `plugins/codex/prompts/adversarial-review.md`——本身就是这套块语法的满配示范（role/task/operating_stance/attack_surface `:19`/finding_bar/structured_output_contract `:48`/grounding_rules/calibration_rules/final_check 十块齐发）；二是停机门模板 `plugins/codex/prompts/stop-review-gate.md`（task+compact_output_contract+default_follow_through_policy+grounding_rules+dig_deeper_nudge 五块）。SKILL.md 结尾交叉引用（`plugins/codex/skills/gpt-5-4-prompting/SKILL.md:52-54`）把三个 references 各自用途（块字典/配方/反模式）钉死。

## 数据流

用户请求 → /codex:rescue 命令（`plugins/codex/commands/rescue.md:26` 先跑 task-resume-candidate 判断续/新线程）→ codex-rescue 子代理加载本技能 → 按 `plugins/codex/skills/gpt-5-4-prompting/SKILL.md:45-51` 的组装清单选最小契约：定 task 范围 → 挑最小够用的输出契约 → 决定默认跟进还是停下问 → 按需加 verification/grounding/safety → 删冗余。产出的 XML 块 prompt 作为参数传给 `codex-companion.mjs task`，最终在 `plugins/codex/scripts/lib/codex.mjs:1095` runAppServerTurn 里经 buildTurnInput（`plugins/codex/scripts/lib/codex.mjs:86-88`）包成 text 消息发给 codex app-server 的 turn/start。这套指南的全部价值都沉淀在那一条 text 里。

## 设计决策

- **契约优先于算力**：`plugins/codex/skills/gpt-5-4-prompting/SKILL.md:41` "Do not raise reasoning or complexity first"——与"加思考预算"路线明确决裂；effort 六档（`plugins/codex/scripts/codex-companion.mjs:71`）默认不设，用户点名才传。
- **XML 而非自然语言分隔**：块名即接口名，Claude 可机械组装、Codex 可稳定识别——本质是把 prompt 结构化成可组合 DSL。
- **Bad/Better 对照教学法**：`plugins/codex/skills/gpt-5-4-prompting/references/codex-prompt-antipatterns.md:9` 先给真实坏例（"Take a look at this..."）再给改写，比抽象原则可执行。
- **反模式与块的对称性**：antipatterns 的"缺输出契约"（`plugins/codex/skills/gpt-5-4-prompting/references/codex-prompt-antipatterns.md:21`）对应 blocks 的 output_contract 组，"无跟进默认"（`:40`）对应 follow_through 组——清单是块的负空间。
- **Prompt-Patching 承认对话性**：续线程只发增量（`plugins/codex/skills/gpt-5-4-prompting/references/codex-prompt-recipes.md:127`），配合 task --resume-last 的 DEFAULT_CONTINUE_PROMPT（`plugins/codex/scripts/lib/codex.mjs:49-50`）形成低成本追问闭环。

## 新人提示

阅读顺序 blocks → antipatterns → recipes → SKILL.md：先建词汇再看反例最后看组装。两个坑：一是这套块语法只在 Codex/GPT-5.4 目标下成立，别照搬到别的模型；二是 prompt 改写是子代理被允许的**唯一**智力活动——`plugins/codex/agents/codex-rescue.md:23-27` 明令不得借机自己读文件、解题、加分析，越界的"好心帮忙"会破坏 verbatim 返回契约。想看满配实战，精读 `plugins/codex/prompts/adversarial-review.md`（84 行十块全展开），它是这套方法论最完整的样品。
