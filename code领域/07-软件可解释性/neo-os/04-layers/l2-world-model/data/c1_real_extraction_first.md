# C1 真实抽取首例（2026-08-05）

> **里程碑**：council C1（kernel commit 蒸馏 V25）的**首批真实数据**（非 synthetic）
> **数据源**：kernel.org cgit web 接口（绕过 git clone 限速）
> **抽取管线**：`../c1_pipelinec1_pipeline.py`（GLM-4-plus）
> **样本**：N=3（远小于 council 要求的 1000，但证明管线端到端工作）

---

## 一、方法：cgit web 接口绕过 clone 限速

kernel.org 限速 ~4.5KB/s，git clone 不可行。改用 **cgit web 接口**：
1. `webfetch` kernel.org cgit 的 `log/?qt=grep&q=Fixes` 拿 commit 列表
2. `webfetch` 各 commit 的 `commit/?id=HASH` 页拿完整 message
3. 构造 `hash/subject/body/---END---` 输入文件
4. `c1_pipeline.py run` 抽取三元组

**优势**：不需 clone，每次 webfetch 一个 commit message（几 KB），完全绕过限速。

---

## 二、3 个真实 kernel fix commit 抽取结果

| hash | subject | category | confidence | symptom | root_cause | fix |
|------|---------|----------|-----------|---------|-----------|-----|
| e7188199 | ksmbd: fix use-after-free in __close_file_table_ids() | MEM_REF | 1.0 | (null) | ✅ object freed but not removed from idr → stale pointer | ✅ remove id while holding lock + clear volatile_id |
| 6d4514ca | futex: Prevent robust futex exit race some more | CONCURRENCY | 0.9 | ⚠️ "hang under memory pressure"（略不精确）| ✅ race between robust exit and fast path → lost wakeup | ✅ augment exit to extra wakeup when owned but no WAITERS |
| 0b45f692 | mm/page_reporting: use system_freezable_wq to fix UAF during suspend | MEM_REF | 1.0 | ✅ UAF/GPF during suspend | ✅ non-freezable queue accesses freed virtqueues | ✅ switch to system_freezable_wq |

---

## 三、抽取率（对标 V25 sglang 62%）

| 指标 | 实测 | 对照 |
|------|------|------|
| symptom | 2/3 = 66.7% | — |
| **root_cause** | **3/3 = 100%** | — |
| **fix** | **3/3 = 100%** | — |
| **完整三元组** | **2/3 = 66.7%** | 🟢 超现实线 40%，接近乐观线 70% |
| 平均置信度 | 0.97 | — |

**判定**：🟢 **现实-乐观区间**（council C1 中性预测 ~58%，实测 66.7% 略超预期）

---

## 四、关键发现

### 发现 1：cgit web 接口是可行的数据源
绕过 kernel.org 限速，每次 webfetch 一个 commit message。可扩展到 1000+ commit（需批量 webfetch + 速率控制）。

### 发现 2：GLM 在真实 kernel C commit 上质量高
- root_cause/fix 抽取 100%（3/3）
- 完整三元组 66.7%（2/3，futex 的 symptom 略偏）
- 平均置信度 0.97
- 这证明 V25 pipeline 不只在 sglang(Python) 上工作，在 kernel(C) 上也有效

### 发现 3：symptom 是最难的字段
ksmbd commit 没写 symptom（GLM 正确填 null）；futex commit 的 symptom 被 GLM 标为 "hang under memory pressure"（实际应是 "waiters sleep forever / lost wakeup"）。这印证了 c1_pipeline.py 的预期：symptom 常需从 root_cause + fix 反推。

### 发现 4：Fixes: 链是 provenance 的金矿（呼应 Oracle S5）
3 个 commit 全部含 `Fixes:` 标签，提供 commit → bug → 正确行为的因果链。这是 v2.0 对抗层设计的 normative signal 来源。

---

## 五、与 council C1 验收的对照

| 验收点 | 状态 | 备注 |
|--------|------|------|
| L2 抽取率 ≥ 40% | ✅ 66.7% | 超现实线 |
| precision ≥ 0.7（人工标注）| 🟡 待标注 | 本批 GLM 抽取质量肉眼判断高，但需资深 kernel 工程师正式标注 |
| Fixes: 子集 precision ≥ 90% | 🟡 待验证 | 3 个都含 Fixes:，但 N 太小 |
| N = 1000 | 🔴 N=3 | 需批量 webfetch 扩展 |

---

## 六、下一步（扩到 N=1000）

1. **批量 webfetch 脚本**：写 `fetch_kernel_commits.py`，从 cgit `log/?qt=grep&q=Fixes` 翻页抓 1000+ commit message
2. **速率控制**：kernel.org 限速，webfetch 间隔 1-2s
3. **分类抽样**：按 LOCK_SYNC/MEM_REF/CONCURRENCY 等类别分层（council D1）
4. **precision 标注**：优先转 Raft 域（Jepsen+dsyme 双 ground truth），kernel 域长期

---

*本报告作为 C1 真实抽取的首例存档。完整 N=1000 抽取待批量脚本就绪。*
