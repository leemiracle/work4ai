# Prompt 工程工具链（六仓蓝图 → opencode）· 案例笔记

> 一句话定位：**把 LLM 域 09/11 类的六个高星仓合成一条"素材→优化→测试→评估→监控→编排"的 prompt 工具链，零依赖映射进 opencode（1 agent + 3 commands + 2 资产目录），与自成长改造共用 `.agent/` 基建。**
>
> 蓝图六仓（[`透视GitHub-LLM高星仓库全景.md`](../../透视GitHub-LLM高星仓库全景.md) 09/11 类，用例卡见 E24/E28/E30/E31/E34）：

| 仓库 | ★ | 生态位 | 取其思想 |
|---|---:|---|---|
| linshenkx/prompt-optimizer | 33.1K | prompt 优化器 | 五步优化环 + 变体对照 |
| promptfoo/promptfoo | 24.2K | prompt/Agent/RAG 测试 + 红队 | 测试矩阵（典型×边界×对抗）+ 可判定断言 |
| comet-ml/opik | 21.4K | LLM 调试/评估/监控 | 评估可追溯（tracing 思想 → evals/ 目录） |
| vibrantlabsai/ragas | 15.3K | RAG 无参考评估 | 四指标：忠实度/相关性/上下文精确率/召回率 |
| microsoft/promptflow | 11.2K | LLM 应用 DAG + 变体批量评估 | prompt 是版本化资产（血缘 + 生命周期门禁） |
| asgeirtj/system_prompts_leaks | 62.9K | 一流系统提示词提取集 | 模式素材：角色+契约+边界+few-shot 的"参考答案" |

## 为什么是这六个（闭环论证）

单独的优化器只会越改越花——**没有测试的优化是装饰，没有资产化的优化是重来**。六仓合起来才成环：

```
素材(leaks: 好prompt长什么样)
  → 优化(optimizer: 五步改写出变体)
    → 测试(promptfoo: 变体过不过矩阵)
      → 评估(ragas: RAG质量四指标)
        → 监控(opik: 评估记录可追溯)
          → 编排(promptflow: 变体血缘+生命周期)
            → 最优版回流为素材 ↑
```

## 落地映射（opencode 扩展点）

| 层 | 文件 | 对应蓝图 |
|---|---|---|
| Agent | `~/.config/opencode/agent/promptsmith.md` | 六合一提示词工程师（三流程内置于方法库） |
| 命令 | `/optimize <prompt>` | prompt-optimizer 五步环 |
| 命令 | `/ptest <prompt或变体名>` | promptfoo 测试矩阵 |
| 命令 | `/evalrag <三元组>` | ragas 四指标 |
| 资产 | `<project>/.agent/prompts/` | promptflow 变体管理（draft→testing→production 血缘门禁） |
| 资产 | `<project>/.agent/evals/` | opik 追溯（评估记录 ⇄ prompt 资产 ⇄ 日志三向链） |

与 [`opencode自成长改造`](../opencode自成长改造/README.md) 的关系：本链是**飞轮的"技能精化"支线**——/retro 发现的 prompt 模式进孵化器，/optimize 产出的变体进 prompts/，两套 `.agent/` 基建互通。

## 与讲透Prompt 的理论锚接

| 工具链环节 | 讲透Prompt 理论 |
|---|---|
| /optimize 变体对照 | 00：prompt=P(输出\|输入) 的条件——改 prompt = 改输出分布 |
| /ptest 断言四类 | 04：LLM-as-Judge 的可判定化 |
| /ptest 对抗样本 | 08-Prompt安全 + 欺骗动力学-检测Prompt库 |
| /evalrag 忠实度 | 04：上下文工程（lost-in-middle / 信息密度） |
| prompts/ 血缘 | 01：few-shot 即 prompt 资产的最早形态 |

## 使用速查

```powershell
# 优化一段 prompt（变体落盘 .agent/prompts/）
/optimize 你是一个代码审查员，请检查以下代码...

# 测试某变体（矩阵落盘 .agent/evals/）
/ptest .agent/prompts/code-reviewer-v2.md

# RAG 评估（上下文+问题+答案 三元组）
/evalrag <context>...<question>...<answer>...

# 生命周期：draft→testing→production 门禁见 .agent/prompts/README.md
```

## 审计命令

```powershell
Get-ChildItem C:\Users\mirac\.config\opencode\command\optimize.md, C:\Users\mirac\.config\opencode\command\ptest.md, C:\Users\mirac\.config\opencode\command\evalrag.md, C:\Users\mirac\.config\opencode\agent\promptsmith.md | Select-Object Name
Get-ChildItem C:\workspace\work4ai\.agent\prompts, C:\workspace\work4ai\.agent\evals | Select-Object Name
```

## 红线

- 对抗样本仅用于防御性检查（写明"应被拒绝"）——/ptest 不是越狱教程（system_prompts_leaks/L1B3RT4S 的攻防边界见 欺骗动力学）
- 优化不换题：每版变体必须可追溯到原始意图（降熵不熵增）
- 2026-08-15 建链，与用例库 E24/E28/E30/E31/E34 卡互为索引
