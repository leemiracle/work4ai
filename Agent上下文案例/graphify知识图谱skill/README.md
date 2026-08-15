# Graphify 知识图谱 Skill · 案例笔记

> 一句话定位：**`/graphify` 一条命令把整个项目（代码+文档+PDF+图片+视频）映射成可查询的知识图谱——代码走本地确定性 tree-sitter AST（零 LLM），非代码走 LLM 语义 pass；每条边带 `EXTRACTED/INFERRED/AMBIGUOUS` 置信标签；不是向量库，是真图。**
>
> 上游：https://github.com/Graphify-Labs/graphify （Apache-2.0 + MIT 双许可文件，106k★，10.3k forks，1,418 commits，开发分支 `v8`，YC S26）
> PyPI 包：**`graphifyy`（双 y，官方包；CLI 命令是 `graphify`）**——本地验证 2026-08-14，最新 0.9.42
> 商业面：[app.graphify.com](https://app.graphify.com)（always-on 平台早期访问）+ Enterprise（代码/文档/会议全上下文记忆层）
>
> 本案例组织方式参照 [`codegraph代码知识图谱`](../codegraph代码知识图谱/README.md)；领域全景见上级 [`Agent上下文案例/README.md`](../README.md)。

## 为什么值得深读

1. **Skill 优先交付**（vs codegraph 的 MCP 优先）：不常驻后台，`/graphify .` 按需构建，产物是**三个可提交进 git 的文件**（`graph.html` 交互图 / `GRAPH_REPORT.md` 报告 / `graph.json` 全图）——团队工作流是"一人建图，全员查询"。
2. **置信标签一等公民**：每条边标 `EXTRACTED`（源码显式）/ `INFERRED`（推导）/ `AMBIGUOUS`（待人审）——与 codegraph 的 `provenance:'heuristic'` 同一哲学：**推测必须自称推测**。
3. **超代码语料**：docs/PDF/Office/Google Workspace/图片/视频/YouTube/arXiv 全进同一张图；`# NOTE:/# WHY:` 注释和 ADR 成为一等节点——"为什么"与"是什么"同图。
4. **图分析即产品**：Leiden 社区检测（LLM-free 标签）、god nodes（枢纽概念）、surprising connections（跨模块意外连接）、`path A B`（两概念间最短路）、工作记忆闭环（`save-result` → `reflect` → `LESSONS.md`）。
5. **20+ 平台接线矩阵**：hook 平台（Claude Code/Gemini）用 PreToolUse 拦截"直接 grep"并导向图；指令文件平台（Codex/OpenCode/Cursor）写 AGENTS.md/rules；还有 **strict mode**（阻断会话首次裸读源码）。平台适配的工程量本身是"skill 分发"的教科书。

## 阅读顺序

| # | 笔记 | 回答的问题 |
|---|---|---|
| 1 | [01-管线架构与置信标签](notes/01-管线架构与置信标签.md) | detect→extract→build→cluster→analyze→report→export 七段管线、schema、安全模型 |
| 2 | [02-skill交付面与平台策略](notes/02-skill交付面与平台策略.md) | `/graphify` 怎么跑、20+ 平台怎么接、团队工作流、MCP/HTTP 服务、工作记忆 |
| 3 | [03-基准对比与领域定位](notes/03-基准对比与领域定位.md) | LOCOMO/LongMemEval 数字与裁判方法学、vs codegraph 正面对比、诚实度评估 |

## 审计总命令

```bash
# 证据 A: PyPI 包存在且版本活跃（2026-08-14 实测输出，节选）
$ pip index versions graphifyy
graphifyy (0.9.42)
Available versions: 0.9.42, 0.9.41, ..., 0.1.1   # 200+ 版本，0.4.x 起要求 Python >=3.10,<3.14

# 证据 B: 官方包名是 graphifyy（双 y），README 明确警告其他 graphify* 包无关联
# uv tool install graphifyy && graphify install && /graphify .

# 证据 C: 仓库规模（上游 GitHub，2026-08-14）
#   106k stars / 10.3k forks / 1418 commits / 分支 v8
#   根目录双许可: LICENSE (Apache-2.0) + LICENSE-MIT + NOTICE——README 未解释二者关系
#   ARCHITECTURE.md 有测试锚: tests/test_architecture_doc.py 导入文中每个符号，文档不许漂移
```

> 注：与 codegraph 案例同级为**文档级审计**（README/ARCHITECTURE.md/BENCHMARKS.md/PyPI 元数据逐条核对），未做源码 clone。ARCHITECTURE.md 自称"签名是真实的，测试导入文中每个符号"——文档-代码一致性由 CI 强制，这是其可信度的加分项。

## 项目内交叉引用

- 领域全景（六路线 + 速查表）：[`../README.md`](../README.md)
- 直接对照案例：[`codegraph代码知识图谱`](../codegraph代码知识图谱/README.md)（MCP 常驻 vs skill 按需；纯代码图 vs 多模态语料；Rust vs Python）
- 知识图谱手册接口：[`工程化手册库/知识图谱工程手册`](../../工程化手册库/知识图谱工程手册/README.md)——graphify 可导出 Obsidian vault（`to_obsidian`），正是该手册"个人知识图谱"工作流的外部供给端
- 记忆层对照：[`Agent记忆系统案例/mem0开源记忆层`](../../Agent记忆系统案例/mem0开源记忆层/)——graphify 的 LOCOMO 基准直接以 mem0 为对照系，`save-result/reflect` 是会话内工作记忆的另一种实现
- 欺骗动力学接口：置信标签（EXTRACTED/INFERRED）是"证据分级"的工业实现，见 [`欺骗动力学-AI纪实验包.md`](../../欺骗动力学-AI纪实验包.md) D1 验证维度
