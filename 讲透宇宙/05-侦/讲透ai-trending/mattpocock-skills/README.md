# 讲透 mattpocock-skills（mattpocock/skills，306.7k star）

Matt Pocock 的 AI agent skills 库全链知识基座：图谱+ONBOARDING+explain 4 篇（2026-11-02）。

| 链路 | 终态 |
|---|---|
| 图谱 | **76n/137e/13层/16步tour**，validator 0 issues 0 warnings，fingerprints 74 文件@e3d8b735 |
| onboarding | ONBOARDING.md 6759 字 8 节 |
| explain | 4 篇（域语言双旗舰/质量反馈双环/issue 生命周期管线/productivity 与自举），304 锚（独立终验 67 path:line 全好+worker 语义抽验 70 处） |
| NOTES-DIGEST | 22 条批阶段甄别笔记 |
| 图谱位置 | 仓内 `.understand-anything/knowledge-graph.json`（/usr-data/data2/repos/ai-trending/skills） |

## 核心发现

**三层自举实证**：仓库用自己的 CONTEXT.md 术语表+ADR-0001 硬软依赖分级+.out-of-scope/ 拒绝知识库治理自己。README 19 出边=最大治理 hub；setup 5 入边=被引用最多技能。

## 勘误精选（8 条全清单见 ONBOARDING）

- plugin.json 实际仅 15 条目（eng 10+prod 5），misc 4 skill 缺席，与 CLAUDE.md:10 自述规则矛盾
- write-a-skill 宣称 SKILL.md<100 行（L113）但库内 5 个超限（含其自身 117）——指导非存量门槛
- link-skills.sh 排除 deprecated 但不排除 personal/in-progress，与 plugin.json 15 条两套口径并存；list-skills.sh 连 deprecated 也不排除
- deprecated/qa:26 仍引用已被 CONTEXT.md 机制取代的 UBIQUITOUS_LANGUAGE.md——术语机制演进文字化石
