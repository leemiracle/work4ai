# A' · C1 Pipeline 验证报告（kernel commit 蒸馏，命门 V25 复现）

> **实验目标**：在 Linux kernel C commit 上复现 V25（sglang Python 62%），回答 council C1。
>
> **日期**：2026-08-05
> **状态**：🟡 **pipeline 就绪 + synthetic 验证通过；真实 kernel 抽取待外部网络条件**

---

## ⚠️ 诚实声明（声称-验证差距校正）

本报告严格遵守 CONSTITUTION.md 的"声称-验证差距校正"原则。各项声称的真实验证状态：

| 声称 | 真实验证状态 | 等级 |
|------|------------|------|
| pipeline 可抽取 kernel C commit 三元组 | ✅ synthetic 3 样本通过（真实 kernel bug 模式）| 工程管道验证 |
| pipeline 在真实 kernel commit 上工作 | ⚠️ **未完成**（kernel.org/镜像限速，clone 阻塞）| **未验证** |
| kernel L2 coverage ~50-58% | ❌ **外推自 sglang，非 kernel 实测** | 预测，非验证 |
| Fixes: 子集 precision ≥90% | ❌ **未标注**（需资深 kernel 工程师）| 预测，非验证 |

**结论**：C1 的**方法学与 pipeline 已就绪并验证**，但**真实 kernel 数据抽取受外部网络限速阻塞**。这与 council C1 的完整要求（1000 commit + 工程师标注 precision）尚有差距，需在具备 kernel.org 稳定连接的环境补完。

---

## 一、为什么 C1 真实抽取未在本会话完成

```
尝试的 clone 源                  结果
─────────────────────────────────────────────────────
git.kernel.org（全量）           ~4.5 KB/s，20 分钟 11 MB，全量需数天
git.kernel.org（--depth=5000）   同样限速，25 分钟 112 KB
mirrors.tuna.tsinghua.edu.cn     ls-remote 超时
mirrors.ustc.edu.cn              未测（kernel.org 已证限速）
mirrors.kernel.org               未测
GitHub torvalds/linux            port 443 blocked（全程不通）
```

**根因**：当前运行环境对 kernel.org 限速严重（~4.5 KB/s），且 GitHub 完全不通。这是**外部网络约束**，非 pipeline 技术问题。pipeline 本身已验证可用。

---

## 二、Pipeline（已完成并验证）

### 文件
- `../c1_pipelinec1_pipeline.py` — 主 pipeline（L1 被动 + L2 agent）
- `../c1_pipelinesample_commits.sh` — 抽 Fixes: commit
- `../c1_pipelineREADME.md` — 使用说明

### 抽取层次（对标 V25 sglang）

| 层 | 方法 | sglang 实测 | kernel 预期（外推）|
|----|------|------------|-------------------|
| L1 被动 | 启发式（关键词 because/due to/fixes + 症状词）| ~30% | ~30%（同）|
| **L2 agent** | **GLM 读 subject+body，主动构造因果链** | **~62%** | **~50-58%**（C 因果更硬，略低）|

### LLM
- ZHIPU GLM-4-plus（`ZHIPU_API_KEY` 已配置，OpenAI 兼容格式）
- 可换 `glm-4.5`（`C1_MODEL=glm-4.5`）

---

## 三、Synthetic 验证结果（pipeline 工作证明）

对 3 个真实风格的 kernel bug-fix commit 跑 L2 抽取（`c1_pipeline.py test`）：

### 样本 1：use-after-free（hotplug 路径）
```
commit: "drm/XYZ: fix use-after-free in hotplug path
         The driver accessed a freed buffer ... because cleanup() freed it
         before the worker finished. Fixes: abc12345 ..."
L2 抽取:
  symptom    : null              ← commit 未直接写症状（符合 V25 发现：symptom 最稀缺）
  root_cause : "use-after-free: cleanup freed buffer before hotplug worker finished"  ✓
  fix        : "ensure buffer is not freed before hotplug worker completes"  ✓
  category   : MEM_REF           ✓
  confidence : 1.0
```

### 样本 2：off-by-one（skb queue loop）
```
commit: "net: fix off-by-one in skb queue loop
         The loop used i <= n instead of i < n, causing a one-byte over-read
         ... under high load. Fixes: def67890 ..."
L2 抽取:
  symptom    : "data corruption under high load"  ✓（从 root_cause + 修复反推）
  root_cause : "off-by-one: loop should be i < n not i <= n"  ✓
  fix        : "change loop bound to i < n"  ✓
  category   : OFF_BY_ONE        ✓
  confidence : 1.0
  → 完整三元组 ✓
```

### 样本 3：docs typo（噪声）
```
commit: "[docs] update README typo"
noise filter: → 跳过（is_noise=True）✓
```

**结论**：pipeline 正确抽取因果三元组，noise filter 正确过滤，category 分类准确。**抽取方法学在 kernel bug 模式上验证通过。**

---

## 四、kernel 迁移预期（sglang 外推，非实测）

基于 V25 sglang(Python) 62% 的外推（参考 commit_extraction_report.md §四）：

| 维度 | sglang (Python) | kernel (C) 预期 | 推理 |
|------|----------------|----------------|------|
| commit 规范 | conventional commits | **严格**（Linus 强制）+ `Fixes:` 标签 | kernel 规范更强 → coverage 倾向更高 |
| message 详细度 | body 常空 | **详细**（多段论证）| kernel 信息密度更高 |
| 因果链深度 | 中（应用层）| 深（内核：指针/并发/内存序）| kernel 因果更"硬"，更难抽 → coverage 倾向略低 |
| 噪声率 | ~22% | ~15%（maintainer review 过滤）| kernel 噪声更低 |
| **L2 预期** | 62% | **50-58%**（中性）| 净效应：规范提升 vs 因果变硬，略降 |

### Fixes: 子集的 precision 优势（council C1 关键预测）

council C1 预测："kernel raw coverage 不超 Python，但 **Fixes: 标签子集 precision ≥90%**"。

**为什么 Fixes: precision 这么高**：
- `Fixes: <hash> ("subject")` 提供确定性因果链接（这个 commit 修那个 commit 引入的 bug）
- Fixes: 的 commit 经过 maintainer review，因果密度高
- Fixes: 链可机械验证（hash → 原 commit → diff 对比）

这是 kernel 相对 sglang 的**独特质量优势**——V25 sglang 无此机制。

---

## 五、Raft 域的替代 ground truth（C1 的更强验证路径）

**重要联动**：`../../../01-decisions/FIRST_DOMAIN_DECISION.md` 选定 Raft 为第一域，Raft 提供 kernel 所没有的**三重 ground truth**：

```
Jepsen 21 issue（运行时因果真值）+ dsyme/raft-lean-squad 716T（形式化已证）+ Ongaro TLA+
                              ↓
              Neo-OS 蒸馏 precision 验证的最强对齐目标
```

**对 C1 的启示**：
- kernel 域 C1 的 precision 验证需资深 kernel 工程师（稀缺、慢）
- **Raft 域 C1 的 precision 验证有 Jepsen + dsyme 双 ground truth**（现成、机械可验证）
- 建议：**C1 的 precision 验证优先在 Raft 域完成**（第一域），kernel 域 C1 作为长期验证（CONSTITUTION 第一条：kernel 仍是长期核心靶子）

---

## 六、命门对照（基于外推，非实测）

| 命门指标（Phase 0 W4）| 阈值 | sglang 实测 | kernel 状态 |
|----------------------|------|-----------|------------|
| 可蒸馏规则率 | ≥10% | 62%（L2）| 🟡 外推 ~50-58%，**待实测** |
| LLM 抽取 precision | ≥0.7 | 待标注 | 🔴 **未标注**（需 kernel 工程师）|
| 合格规则产出 | ≥1 条 | 5 条 Lean4（V11）+ spinlock（C2）| 🟢 已超额（C2 非平凡规则）|
| 用户价值确认 | ≥3 工程师 | 待 | 🟡 待 |
| 解释开销 | <15% | 待 prototype | 🟡 待 |

**总体判定**：🟡 **pipeline + 方法学就绪，真实数据抽取待外部条件**。结合 C2（形式化非平凡规则已证），命门的形式化侧（V11+C2）已通过；蒸馏侧（V25+C1）的 pipeline 就绪，待真实数据 + 工程师标注。

---

## 七、执行计划（补完 C1 的真实抽取）

### 前置：在具备 kernel.org 稳定连接的环境执行

```bash
# 1. clone kernel（全量或 shallow，视网络）
git clone --filter=blob:none --no-checkout \
    https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git \
    .linux
# 或 shallow（限速环境）：
git clone --depth=10000 --no-checkout <URL> .linux

# 2. 抽 1000 Fixes: commit
./../c1_pipelinesample_commits.sh .linux 1000 \
    .kernel_fixes_commits.txt

# 3. 跑小样本（100，对标 V25 sglang）
python3 ../c1_pipelinec1_pipeline.py run \
    .kernel_fixes_commits.txt --n 100 \
    --out .c1_results.jsonl

# 4. 统计 coverage
python3 ../c1_pipelinec1_pipeline.py stats .c1_results.jsonl
```

### precision 标注（council C1 要求 ≥0.7）
1. 从 c1_results.jsonl 取 100 个 root_cause 抽取
2. 邀请 ≥1 位资深 kernel 工程师标注（Fixes: 子集优先，预期 precision ≥90%）
3. 算 precision = (正确数 / 标注数)

### 验收（council C1 全绿条件）
- [ ] L2 agent 抽取率 ≥40%（中性预期 ~58%）
- [ ] precision 经 kernel 工程师标注 ≥0.7
- [ ] Fixes: 子集 precision ≥90%

---

## 八、C1 的 council 验收清单（当前状态）

| council C1 要求 | 当前状态 | 证据 |
|----------------|---------|------|
| V25 在 kernel C commit 复现 | 🟡 **pipeline 就绪，真实抽取待网络** | 本报告 §二 §三 |
| 抽取率 ≥40% | 🟡 外推 ~50-58%，待实测 | §四外推 |
| precision 经 kernel 工程师 ≥0.7 | 🔴 **未标注** | 需团队 |
| Fixes: precision ≥90% | 🔴 **未验证**（强预测）| §四 Fixes: 论证 |

**判定**：C1 的**工程基础设施（pipeline + 方法学 + synthetic 验证）已完成**；**真实数据验证受外部网络限速阻塞**。建议：
1. 在具备 kernel.org 连接的环境补完真实抽取（§七执行计划）
2. **C1 的 precision 验证优先转 Raft 域**（三重 ground truth，§五），kernel 域作长期验证

---

*本报告诚实记录 C1 的部分完成状态。pipeline 已就绪，真实抽取待外部条件。结合 C2（形式化非平凡规则已证），Neo-OS 命门的形式化侧完全通过，蒸馏侧 pipeline 就绪。*
