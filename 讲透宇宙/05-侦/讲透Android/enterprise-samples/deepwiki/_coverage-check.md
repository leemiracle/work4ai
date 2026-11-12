# Coverage Check

- repo: android/enterprise-samples
- fetched: 2026-10-23
- 结构清单页数: 11
- 落盘页数: 15

- 结构外页: 4
- 覆盖: 15/11 (INCOMPLETE)

## 终判（dw_reconcile 参数化版 2026-10-23）
- 结构 11 页全命中（MISSING=0），extra 4 页为三级页增量重料（结构清单只列到二级，AAIF 轮 dw_fetch_mcp 结构解析钉版），保留 x 前缀页
- **真覆盖率 100%**（11/11 结构页 + 4 三级页 = 15 页全量落盘）
