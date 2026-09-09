# code领域 —— 16 源收编总宇宙

> **定位**：把散落在 C:\workspace 的 16 个项目/知识库/克隆仓收编为 work4ai 的 code 领域总宇宙——
> 一站式覆盖 CS 学习路线、编译器、论文OS、数学基础、系统与 ML 工程、技术媒体情报、软件可解释性、世界本质、投资与经济。
> **收编日期**：2026-09-09/10 · **车道**：feature/code-universe · **设计**：[specs/2026-09-09-code-universe-consolidation-design.md](../docs/superpowers/specs/2026-09-09-code-universe-consolidation-design.md)

## 九区导航

| 子区 | 定位 | 来源与规模 |
|---|---|---|
| [`01-学习路线/`](./01-学习路线/csdiy/) | CS 自学路线 + tiny* 逆向工程 26 项目 + 双环学习反思 | csdiy 整仓自有层+索引层，885 文件/937M |
| [`02-编译器与LLVM/`](./02-编译器与LLVM/) | LLVM Expert_01-13 专家笔记 + llvm_experiments + IT学习平台 | 45+37+154 文件 + 头文件 patch |
| [`03-论文OS/`](./03-论文OS/) | AI 论文学习 OS：学习路径/实践项目/知识图谱 + 15 个上游实现参考 | paper-os 22,345 文件 |
| [`04-数学基础/`](./04-数学基础/) | 数学专家库 + awesome-math + Lean4 全家（lean4ai/mathlib4…） | math 9,523 + math-expert-pro 2,803 |
| [`05-系统与ML工程/`](./05-系统与ML工程/) | ML 系统教程/调试/个人站 + ML 面试 + deepseek-harness 官方源 | 252+51+7,416 文件 |
| [`06-技术媒体情报/`](./06-技术媒体情报/) | InfoQ 十维分析 + 全站知识图谱（14 topic/2.5万篇） | infoq-analysis 1,605 + infoq-atlas 1,003 |
| [`07-软件可解释性/`](./07-软件可解释性/neo-os/) | neo-os：事件本体+commit 蒸馏+Lean4 规则→可证明解释 | 87 文件（桥梁：根级 `neo-os知识桥梁.md`） |
| [`08-世界本质/`](./08-世界本质/essence/) | 跨学科"世界运行本质"知识库（哲学→智能→世俗权力） | essence 436 文件 |
| [`09-投资与经济/`](./09-投资与经济/) | 段永平投资理念索引 + 经济五域调研残留 | fastisslow 索引卡 + economy 两文件 |

## 对账总表（源计数 = 目标计数）

| 源 | 基线 | 入库 | 不迁（豁免决策） |
|---|---|---|---|
| csdiy | 48,630 | 885 | github-repos 47,341/21G（[克隆索引卡](./01-学习路线/csdiy/github-repos克隆索引卡.md)）+ books 404/102M（[书单](./01-学习路线/csdiy/books书单索引.md)） |
| deepseek-harness | 7,416 | 7,416 | — |
| economy | 3 | 2 | .opencode 缓存 1 |
| essence | 436 | 436 | — |
| fastisslow | 16 | 0（索引卡） | 11 PDF+附属（版权，[索引](./09-投资与经济/fastisslow索引.md)） |
| infoq-analysis | 1,605 | 1,605 | — |
| infoq-atlas | 1,003 | 1,003 | — |
| leemiracle | 252 | 252 | — |
| llvm-project（自有层） | 37+154+2补丁 | 37+154+2 | monorepo 156,484/2.14GiB（[克隆索引卡](./02-编译器与LLVM/LLVM-monorepo克隆索引.md)） |
| LLVM项目研究 | 45 | 45 | — |
| Machine-Learning-Interviews | 51 | 51 | — |
| math | 9,523 | 9,523 | — |
| math-expert-pro | 2,803 | 2,803 | — |
| neo-os | 87 | 87 | — |
| paper-os | 22,345 | 22,345 | — |
| **合计** | — | **~46,000 文件入库** | ~204,000 文件按 4 张用户决策豁免 |

## 迁移说明

- **上游参考库**（03区 15 个克隆、05区 deepseek-harness 等、04区 awesome-math/mathlib4 等）为第三方开源项目副本，仅作本地学习参考；其内部链接自成体系，**不纳入本仓链检范围**
- 各源迁移脚本与对账工具在车道提交历史中（`git log --grep=code领域`）；一次性工具 `.mig-*.py/sh` 已清理
- 原文件夹处置记录：2026-09-10 终批删除（见 `迁移完成报告.md`）

## 来源处置记录（不可逆动作留痕）

2026-09-10 00:28-00:30，对账全平后删除 15 个原目录（16 源；llvm/ 含 llvm-project）：
`csdiy · deepseek-harness · economy · essence · fastisslow · infoq-analysis · infoq-atlas · leemiracle · llvm(含llvm-project) · LLVM项目研究 · Machine-Learning-Interviews · math · math-expert-pro · neo-os · paper-os`
每源删除条件 = 基线对账相等 或 用户书面豁免（github-repos/books/fastisslow-PDF/LLVM-monorepo/economy缓存）。删除日志存车道提交历史。
