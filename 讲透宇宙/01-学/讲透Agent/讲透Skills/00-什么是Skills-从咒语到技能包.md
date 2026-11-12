# 00 — 什么是 Skills：从咒语到技能包

> 「讲透 Skills」第一篇。回答一个根本问题：**prompt 工程已经存在了，为什么还需要 skills？** 答案藏在三个 prompt 天生解决不了的问题里。

---

## 1. 直觉：prompt 的三个先天缺陷

你写了一个绝妙的 prompt——教 Claude 按公司品牌规范生成 PPT。三天后你想再用一次，发现：

```
缺陷1【每次重讲】prompt 活在对话里，对话结束就消失。下次任务要全文复述一遍。
缺陷2【不可版本控制】你改进了 prompt，但旧版新版散落在不同聊天记录里，
       没有 diff、没有 release、没有回滚。
缺陷3【不可共享】同事想用你的方法？截图发给他，他再手抄一遍，抄错一处。
```

Skills 的定义（anthropics/skills README 原文）：

> "Skills are **folders** of instructions, scripts, and resources that Claude **loads dynamically** to improve performance on specialized tasks."

翻译成工程语言：**skill = 把 prompt 从"对话里的咒语"变成"文件系统里的资产"**。

```
prompt（咒语形态）              skill（资产形态）
─────────────────              ─────────────────
活在聊天记录里          →       活在文件夹里（可 git 管理）
每次重打一遍            →       按需自动加载（progressive disclosure）
单体大文本              →       SKILL.md + scripts/ + references/ + assets/
一个人用                →       团队共享、marketplace 分发、跨 40+ 工具携带
写完就完                →       有版本、有 evals、有优化工具链
```

## 2. 一个最小 skill 长什么样

```markdown
---
name: pdf-processing
description: Extracts text and tables from PDF files, fills PDF forms, and
  merges multiple PDFs. Use when working with PDF documents or when the user
  mentions PDFs, forms, or document extraction.
---

# PDF 处理

## 步骤
1. 先用 scripts/extract.py 抽取文本（不要用 LLM 硬读）
2. 表格用 scripts/parse_tables.py
3. 表单填充见 references/FORMS.md 的模板

## 边界情况
- 扫描件（无文本层）→ 走 OCR 流程，见 references/ocr.md
```

就这么简单：**一个文件夹 + 一个 SKILL.md（YAML 头 + Markdown 正文）**。YAML 头只有 `name` 和 `description` 两个必填字段——这是整个规范的核心极简主义：入门门槛低到 5 分钟，所以生态能在一年内膨胀到 11,492 仓。

## 3. 演化时间线（一年走完 prompt 十年的路）

```
2025-09-22  anthropics/skills 仓库创建（最早的可考时间）
2025-10-16  Anthropic 发布 Agent Skills（Claude 私有功能）
2025-12-18  开放标准发布（agentskills.io）——规范与实现分离
2025-12-20  微软、OpenAI 48 小时内跟进（openai/skills、microsoft/skills）
2026-03     32+ 工具兼容（Claude Code/Codex/Cursor/OpenCode/Gemini CLI...）
2026-06     40+ 工具；企业 registry/治理萌芽
2026-08     GitHub topic:skills 11,492 仓（本项目实测快照）
```

> 详见姊妹篇 [`Skills生态全景/notes/02-规范演进`](../Agent框架案例/Skills生态全景/notes/02-规范演进与SKILL.md解剖.md)。

**为什么这么快？** 因为规范只有两个必填字段，而所有 Agent 工具都面临同一个痛点：用户想让 agent 记住"我们公司是怎么做事的"。谁支持 skills，谁的用户就能把 skills 从别的工具直接搬来——**标准即护城河的反面：标准即入场券**。

## 4. Skills 与相邻概念的精确分界

| 概念 | 一句话 | 与 skills 的关系 |
|---|---|---|
| **Prompt** | 一次对话内的指令文本 | skills 是 prompt 的**打包+分层加载**形态 |
| **System prompt** | 常驻的指令前缀 | skill 元数据（name+description）常驻，正文按需——比 system prompt 更省 |
| **MCP** | 工具/数据接入协议（插座） | MCP 给 agent 接**能力**，skills 教 agent **怎么用能力**（手册）|
| **Plugin** | 宿主特定的扩展包 | plugin 绑定工具（如 Claude Code plugin），skill 跨工具（开放标准）|
| **Subagent** | 独立上下文的分身 | skills 可以教 subagent 怎么做事；subagent 可以加载不同 skills |
| **Fine-tuning** | 改权重学技能 | skills 改上下文（0 训练成本、0 部署成本、即时生效、随时删除）|

最常混淆的是 **MCP vs Skills**。用厨房比喻：MCP 是给厨房装新电器（烤箱/料理机 = 工具），skills 是菜谱（怎么用这些电器做出菜）。官方 mcp-builder skill 甚至就是"教你怎么造新插座"的菜谱——两者是协作不是竞争。

## 5. 为什么"文件夹+Markdown"这个形态赢了对模型上下文的适配

三个深层原因（后面各章展开）：

1. **注意力经济**（→ [02](02-渐进披露与上下文经济学.md)）：上下文不是免费的，attention 会随长度稀释（lost in the middle）。skills 的三层渐进披露把"常驻成本"压到每个 skill ~100 token。
2. **检索即路由**（→ [03](03-路由与触发-description即检索键.md)）：agent 面对任务时，在 skill 元数据列表里做检索——description 的质量决定 skill 是否被用。这让"写 skill"的核心技巧变成"写好一条 1024 字符以内的检索键"。
3. **代码优于文本**（→ [01](01-规范精读-SKILL.md解剖.md) scripts/）：确定性任务交给 scripts/ 里的真代码跑，不耗上下文、不靠 LLM 模拟。官方 pdf/xlsx skill 的杀器就是 Python 脚本。

## 6. 本站怎么读

- 想动手写第一个 skill → [01](01-规范精读-SKILL.md解剖.md) + [03](03-路由与触发-description即检索键.md)
- 想理解为什么这么设计 → [02](02-渐进披露与上下文经济学.md)
- 想装现成的 → [04](04-生态全景-七赛道与工具链.md)
- 想验证/优化 → [05](05-实验矩阵-知识点×可验证实验.md) + [07](07-自动优化-从skill-creator到MCE.md)

## ✍️ 练习

1. 把你最近一段"教 AI 做事的对话"改写成一个最小 skill（只需 name + description + 3 步指令）。写完问自己：description 里有没有"什么时候该用"？
2. 观察 `~/.config/opencode/skills/` 下任意一个 skill（或本站姊妹篇的仓卡），指出它哪些部分属于"元数据层/正文层/资源层"。
3. （思考）你工作流里哪部分适合做成 skill，哪部分更适合 MCP 工具？判断依据是什么？（提示：程序性知识 vs 能力接入）

---

**下一篇**：[01 — 规范精读：SKILL.md 解剖](01-规范精读-SKILL.md解剖.md)
