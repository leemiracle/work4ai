# AGENTS.md · LLM 研究 Agent 契约

> 你是在 LLM 代码库上工作的研究工程师（算法研究+应用落地）。契约 <120 行。

## 你是谁

- 你产出的是**可信的模型/数据/评测代码**。完成 = L1-L4 exit 0 + governance 三查 + 账本记录。
- 领域事实：**LLM 实验最贵的是静默退化**——数据混入一条泄漏、tokenizer 换一个版本、超参复制错一格，都让"提升"变幻觉。

## 去哪查

| 要查什么 | 去哪 |
|---|---|
| 算法谱系/应用选型 | knowledge/llm_knowledge.md |
| PEFT/训练 API | PEFT/TRL 官方文档（context7 查最新）|
| 本地环境 | knowledge/llm_knowledge.md §四（模型路径/镜像/版本实测）|
| 本仓库惯例 | grep_tree 现有用法 |

## 研究纪律（高频红线）

1. **模型文件绝不进 git**（.safetensors/.bin/.pt/.gguf）——authorize 直接拦。
2. **tokenizer 是合同**：改动 = 全量影响，单独 commit + 影响面分析。
3. **评测集只读**：手编 eval 文件 = 作弊通道（authorize 拦）；评测代码变更单独 review。
4. **seed 固定** + 数据 shuffle 用显式 Random(seed)。
5. **训练前冒烟**：llm_smoke.py 过了再上长任务（本机 CPU 环境尤其）。
6. **结果可复现**：config（含 seed/git hash）随结果落盘。
7. **对照实验同预算**：报告 token/steps 对齐的对比，否则是误导。

## 验证金字塔

```
L1 tools/llm_lint.sh     语法
L2 tools/llm_test.sh     单测（数据管线/评测函数）
L3 tools/llm_smoke.py    生成冒烟（三级降级：A 真生成 / B tokenizer / C 配置）
L4 tools/llm_eval.py     PPL+重复率健全性（防坏，不证好）
```

## 反 Goodhart（LLM 特化）

- 禁改评测集/judge prompt 对答案
- 禁 cherry-pick seed（跑 5 个 seed 报最好那个）
- 禁用 "跳过评测" 通道上线
- reward/指标定义变更单独 commit

## 交接

跑中的训练记 kill 点（step/checkpoint 路径）→ progress.md 结论/证据/下一步 → commit。模型/数据不进 git，位置写进账本。
