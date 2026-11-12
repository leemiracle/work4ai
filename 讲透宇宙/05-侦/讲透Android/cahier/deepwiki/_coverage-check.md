# Coverage Check

- repo: android/cahier
- fetched: 2026-10-23
- 结构清单页数: 32
- 落盘页数: 37

- 结构外页: 5
- 覆盖: 37/32 (INCOMPLETE)

## 终判（dw_reconcile 参数化版 2026-10-23）
- 结构 32 页全命中（MISSING=0），extra 5 页为三级页增量重料（结构清单只列到二级，AAIF 轮 dw_fetch_mcp 结构解析钉版），保留 x 前缀页
- **真覆盖率 100%**（32/32 结构页 + 5 三级页 = 37 页全量落盘）
