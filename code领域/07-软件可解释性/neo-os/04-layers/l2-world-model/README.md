# Neo-OS · L2 System World Model Layer

> **核心创新层**——从软件历史（commits/crashes/specs）蒸馏领域世界模型。7B 蒸馏小模型，本机常驻，<100ms。
>
> 权威 spec：[`00-constitution/DESIGN.md`](../../00-constitution/DESIGN.md) §一 L2 节

---

## 状态：🟢 C1 命门已达标（Phase 0 完成 → Phase 1 待接入）

L2 的"数据地基"是 commit 蒸馏（命门 V25/C1）。三域已达标：

| 域 | N | root_cause 抽取率 | 完整三元组 | precision | 报告 |
|---|---|---|---|---|---|
| sglang (Python) | 100 | 62% | — | — | [`data/commit_extraction_report.md`](./data/commit_extraction_report.md) |
| etcd/Raft (Go) | 89 | **97%** | 39% | 73-93% | [`data/raft_extraction_report.md`](./data/raft_extraction_report.md) |
| **kernel (C)** | 145 | **100%** | 57.9% | **100%** (15 样本) | [`data/c1_final_report.md`](./data/c1_final_report.md) |

**结论**：council C1 全绿。kernel C commit **能**蒸馏（中性预期 ~58% 已远超，Fixes: 子集 precision 100%）。

---

## 当前实现（prototype）

### [`c1_pipeline/`](./c1_pipeline/) — commit 蒸馏 pipeline

| 文件 | 作用 | 状态 |
|---|---|---|
| `c1_pipeline.py` | 主 pipeline：L1 被动抽取 + L2 agent 增强（ZHIPU GLM API）| ✅ |
| `l2_distill.py` | L2 autoformalize 闭环（48 蒸馏规则）| ✅ |
| `l2_audit.py` | L2 语义审计（量化 R5§6 命门：编译通过≠语义正确）| ✅ |
| `fetch_kernel_commits.py` | kernel commit 抓取（绕过 kernel.org 限速）| ✅ |
| `sample_commits.sh` | Fixes: 标签 commit 抽样 | ✅ |

### [`data/`](./data/) — 抽取结果 + 蒸馏规则

- `*_results.jsonl` — 三域抽取结果（sglang/etcd/kernel）
- `l2_distilled_rules*.lean` — 48 蒸馏规则的 Lean4 形式（→ L2.5）
- `*_report.md` — 三域抽取报告

---

## 与上下游的契约

| 方向 | 契约 |
|---|---|
| **上游输入** | Linux/etcd/sglang git history → c1_pipeline 抽取 (symptom, root_cause, fix) 三元组 |
| **下游输出** | 蒸馏规则 `.lean` → [`l2_5-formal-rules/`](../l2_5-formal-rules/) 形式化验证；解释能力 → [`l3-explain/`](../l3-explain/) |

---

## Phase 1 升级路线（DESIGN.md L2 节）

### 模型（待训练）
- 基座：Qwen2.5-Coder-7B（代码理解强 + 中文友好 + 开源）
- 训练目标三层：主因果/干预式 + 辅预测式 next-event + 界面生成式解释
- 蒸馏方法：QLoRA（NF4 4bit）+ 每域 LoRA adapter + LIMA 式 1000 条精挑 + DPO 对齐
- 部署：本机 GPU 7B（vLLM/SGLang）+ INT4 量化 + 云端 fallback

### 训练语料构成（DESIGN.md L2 节）
- Linux commits 60%（Tier 1/2/3 分层）
- Crash reports 20%（kernel oops, syzkaller）
- 合成数据 15%（注入 bug → trace → 已知原因）
- 教科书 5%（OSTEP, Red Book）

---

## 引用

- work4ai 理论弹药：[`03-methodology/from-work4ai.md`](../../03-methodology/from-work4ai.md) §B/D（讲透基础模型/世界模型/微调/RAG）
- 形式化下游：[`l2_5-formal-rules/`](../l2_5-formal-rules/)
- 命门报告：[`02-research/deep/SYNTHESIS.md`](../../02-research/deep/SYNTHESIS.md)
