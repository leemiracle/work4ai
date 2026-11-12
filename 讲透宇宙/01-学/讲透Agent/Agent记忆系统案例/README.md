# Agent 记忆系统案例 · 索引

| 案例库 | 内容 | 状态 |
|---|---|---|
| **mem0开源记忆层/** | mem0 源码精读专档（11 个子目录：V3 七阶段管线/评分融合/图谱/评测） | 已完成，2026-08 核对：三个月内算法零变化，结论有效期长（见 topics-memory-3Kplus/A01-mem0.md 增量核对） |
| **topics-memory-3Kplus/** | GitHub `topic:memory & stars>3K` **全量 44 仓**深读（2026-08-15）：`00-总览与横向综合.md`（九族形态谱系/六条收敛共识/基准反虚荣审计/B 层跨域迁移）+ A 层 29 篇 + B 层 12 篇 + C 层 3 篇，全部行号钉版 | 已完成 |
| **blog-AgentMemory设计谱系.md** | 三源码对读 blog（2026-08-21）：ClaudeCode 极简派 vs openclaw 治理派 vs mem0/Letta 服务派——"四个起点收敛成同一形状"；反直觉四则（ADD-only 是进步/0.72vs0.65/记忆可能是负债） | 已完成 |
| **OpenViking上下文数据库/** | volcengine/OpenViking 源码深读专档（2026-08-25）：`notes/` 7 目录 24 篇 3300+ 行全行号钉版（四层栈架构/L0L1L2/检索与会话管线/ov compile/三语言 SDK/九家编辑器集成/部署安全/VikingBot/评测）+ `deepwiki-raw/` 74 页 876KB 档案 + 06-deepwiki-cross-reference（74 页 vs HEAD 262 commits 差异全景，时效三档分层） | 已完成（基准 HEAD=c66b9155，2026-08-24；⚠️ 该仓库 30 天 262 commits 高速迭代，使用前先 git log 核对增量） |

## 速查：什么问题查哪里

- **选型决策** → `../讲透记忆/05-应用-记忆架构选型.md`（决策树已接入 44 仓实测修正）
- **九族形态谱系 / 收敛共识 / 基准乱象** → `topics-memory-3Kplus/00-总览与横向综合.md`
- **某个具体仓库的机制细节** → `topics-memory-3Kplus/_清单与分层.md` 找编号 → 对应 A/B/C 笔记
- **FSRS 遗忘数学（Agent 记忆 decay 的现成方案）** → `topics-memory-3Kplus/B03-fsrs4anki.md`
- **mem0 内部实现** → `mem0开源记忆层/`
- **OpenViking 内部实现 / viking:// 文件系统记忆路线** → `OpenViking上下文数据库/notes/README.md`（速通路径 2-3 小时；与 mem0 的"记忆层 vs 上下文库"路线对照表在其结尾）
