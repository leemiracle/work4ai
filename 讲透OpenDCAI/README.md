# 讲透 OpenDCAI（2026-11-02）

GitHub org [OpenDCAI](https://github.com/OpenDCAI)（数据为中心 AI：DataFlow 数据清洗流水线家族 + 评测 + 数据合成）。用户令：①org 仓确认克隆并走 deepwiki 流水线；②**>100★ 才处理**（15/46 仓入选，31 仓 ≤100★ 仅存档清单 `manifest-dc.txt`）。

## 状态表（15/15 收官）

| repo | ★ | deepwiki | repo-docs | 状态 |
|---|---|---|---|---|
| DataFlow | 8409 | 102 页 2.4MB | — | ✅ TRUE_100 + ✅ **understand 全链**（图谱 1252n/3743e/14 层/15 步 tour，双校验 0 issues，fingerprints 462@7d7ff715；ONBOARDING 8 节+explain 12 篇 61,065 字符 288 锚终验归零） |
| DataFlex | 3364 | 27 页 0.4MB | — | ✅ TRUE_100 + ✅ **understand 全链**（358n/916e/16 层/15 步@d9625e4c；ONBOARDING 5131 字 37 锚+explain 6 篇 16,506 字 159 锚；⚠️ 发现 19+8 YAML 明文凭据应轮换） |
| Paper2Any | 2821 | 75 页 1.6MB | — | ✅ TRUE_100 + ✅ **understand 全链**（**2327n/5173e/16 层/16 步@b538531e 本 campaign 最大图**；ONBOARDING 5998 字 65 锚+explain 12 篇 74,360 字 562 锚；⚠️ text.py api_key 明文日志） |
| GameFactory-3A | 990 | 38 页 0.8MB | — | ✅ TRUE_100（exit1 已终判回写） |
| OpenWorldLib | 889 | 30 页 0.6MB | — | ✅ TRUE_100 |
| DataMind | 456 | — | 33 md | ⛔ NOT_INDEXED + ✅ **understand 全链**（868n/1818e/16 层/15 步@36e189d6；ONBOARDING 5753 字 65 锚+explain 12 篇 46,362 字） |
| OpenPrism | 388 | 48 页 2.2MB | — | ✅ TRUE_100 + ✅ **understand 全链**（285n/671e/14 层/15 步@d383c044；ONBOARDING 5994 字 65 锚+explain 6 篇 14,684 字 195 锚） |
| DataFlow-WebUI | 254 | 54 页 1.1MB | — | ✅ TRUE_100 + ✅ **understand 全链**（840n/1532e/15 层/15 步@2e95d40a；ONBOARDING 5986 字 57 锚+explain 12 篇 47,394 字 374 锚） |
| Data-Preparation-Bench | 241 | — | 11 md | ⛔ NOT_INDEXED + ✅ **understand 全链**（274n/544e/12 层/15 步@2508319e；ONBOARDING 5984 字 90 锚+explain 6 篇） |
| RARE | 185 | — | 1 md | ⛔ NOT_INDEXED + ✅ **understand 全链**（102n/169e/11 层/12 步@0f6d7064；ONBOARDING 5999 字 63 锚+explain 6 篇 14,938 字 192 锚） |
| One-Eval | 163 | 28 页 0.5MB | — | ✅ TRUE_100 + ✅ **understand 全链**（636n/1307e/16 层/16 步@8aba20ad；ONBOARDING 5978 字 36 锚+explain 12 篇 42,063 字 467 锚） |
| AgentFlow | 143 | 49 页 1.4MB | — | ✅ TRUE_100 + ✅ **understand 全链**（909n/1857e/16 层/16 步@23aa36a5；ONBOARDING 5984 字 46 锚+explain 12 篇 73,213 字 539 锚；⚠️ osworld-settings 明文凭据应轮换） |
| gugu | 134 | — | 94 md | ⛔ NOT_INDEXED → repo-docs 兜底（**本地克隆曾中断为空壳，已重克隆 @ee7a276a**） |
| Mycel | 113 | 45 页 2.1MB | — | ✅ TRUE_100 + ✅ **understand 全链**（**3168n/6913e/15 层/15 步@4ec5a4d5 第二大图**；ONBOARDING 5998 字 56 锚+explain 12 篇 59,933 字 363 锚） |
| Awesome_MLLMs_Reasoning | 111 | — | 1 md | ⛔ NOT_INDEXED → repo-docs 兜底 |

**汇总**：deepwiki 10/15 TRUE_100（496 内容页 ≈13MB，全含 wiki_full.md + INDEX + _coverage-check）；NOT_INDEXED 5/15 → repo-docs 共 140 md（放弃清单 `opendcai/deepwiki-batch/放弃清单-no-deepwiki.txt`）。

## 台账与产物

- 台账：`/usr-data/data2/repos/opendcai/deepwiki-batch/PROGRESS.md`（manifest-dc.txt 全量 46 / manifest-dc100.txt 入选 15 / status/ 15 终态）
- 克隆：`/usr-data/data2/repos/opendcai/`（15 仓；gugu 二波中断已修复）
- 产物：本目录 `{repo}/deepwiki/`（10）+ `{repo}/repo-docs/`（5）+ `_docs-index-repodocs.md`

understand：**DataFlow 已全链完成**（2026-11-02，24 批/1252n/3743e；onboarding/ + explain/ 12 篇在 `讲透OpenDCAI/DataFlow/`）；其余 14 仓待裁决。字数口径=不计空格总字符（explain 均值 ~5.1K、ONBOARDING 8995，符合系列 norm）。
