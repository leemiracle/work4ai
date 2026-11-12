# Coverage Check

- repo: android/location-samples
- fetched: 2026-10-23
- 结构清单页数: 15
- 落盘页数: 18

- 结构外页: 3
- 覆盖: 18/15 (INCOMPLETE)

## 终判（dw_reconcile 参数化版 2026-10-23）
- 结构 15 页全命中（MISSING=0），extra 3 页为三级页增量重料（结构清单只列到二级，AAIF 轮 dw_fetch_mcp 结构解析钉版），保留 x 前缀页
- **真覆盖率 100%**（15/15 结构页 + 3 三级页 = 18 页全量落盘）
