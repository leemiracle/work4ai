# Neo-OS · C1 Pipeline（kernel commit 蒸馏）

> 命门 V25 在 Linux kernel C commit 上的复现（council C1）。
> 对标：V25 sglang(Python) 100 样本 L2 ≈ 62%。

## 文件

| 文件 | 作用 |
|------|------|
| `c1_pipeline.py` | 主 pipeline：L1 被动 + L2 agent（ZHIPU GLM API）抽取 (symptom, root_cause, fix) |
| `sample_commits.sh` | 从 kernel git 抽 N 个 Fixes: bug-fix commit |

## 环境

- `ZHIPU_API_KEY` 环境变量（已设）
- Python 3.10+（仅标准库，无第三方依赖）
- kernel git 浅克隆：`../datalinux`（`--depth=5000 --filter=blob:none --no-checkout`）

## 用法

### 1. synthetic 自测（验证 API + prompt）

```bash
python3 .c1_pipeline.py test
```

预期：3 个 synthetic commit（use-after-free / off-by-one / docs-typo）正确抽取，noise filter 跳过 docs。

### 2. 抽 kernel commit

```bash
./.sample_commits.sh ../datalinux 1000 \
    ../data/kernel_fixes_commits.txt
```

### 3. 跑小样本（对标 V25 的 100 样本）

```bash
python3 .c1_pipeline.py run \
    ../data/kernel_fixes_commits.txt --n 100 \
    --out ../datac1_results.jsonl
```

### 4. 统计 coverage（命门对照）

```bash
python3 .c1_pipeline.py stats ../datac1_results.jsonl
```

## 抽取层次（对标 V25）

| 层 | 方法 | 预期（kernel C）|
|----|------|----------------|
| L1 被动 | 启发式（关键词 because/due to/fixes + 症状词）| ~30%（同 sglang）|
| **L2 agent** | **GLM 读 subject+body，主动构造因果链** | **~50-58%**（略低于 Python，但 Fixes: precision ≥90%）|

## 命门对照

| 阈值 | 区间 |
|------|------|
| <10% | 🔴 悲观（转降级）|
| 40-70% | 🟡-🟢 现实-乐观（推进）|
| >70% | 🟢 乐观（全力）|

## precision 标注（council C1 要求 ≥0.7）

L2 抽取的 root_cause 需人工标注 precision。标注工具与方案见 `kernel_extraction_report.md`。
Neo-OS 的 Raft 域（见 `../../../01-decisions/FIRST_DOMAIN_DECISION.md`）有 Jepsen+dsyme 双 ground truth，
kernel 域靠资深 kernel 工程师标注（本 pipeline 提供 100 样本供标注）。

## 局限

1. **kernel clone 慢**：kernel.org 不支持 partial clone filter（warning: filtering not recognized），
   用 `--depth=5000` shallow 限制对象数。全量 clone 需数小时。
2. **L2 用 GLM-4-plus**：非 GPT-4 级，抽取质量可能略低。可换 `glm-4.5`（`C1_MODEL=glm-4.5`）。
3. **未跑 diff-level 抽取**：当前仅 subject+body。Phase 1 加 diff（+ 上下文代码）提升 coverage。
4. **precision 标注需人**：本 pipeline 不含自动 precision 评估。
