# Coverage Check

- repo: agentgateway/agentgateway
- fetched: 2026-10-21
- 结构清单页数: 107
- 落盘页数: 109

- 结构外页: 2
- 覆盖: 109/107 (INCOMPLETE)

## 甄别结论（2026-10-22 手写覆盖脚本判定）

- 全层级对账（含三级页）：结构 109 页 = 落盘 109 页，命中 109，**MISSING=0，结构外=0**
- 脚本判 INCOMPLETE 系口径问题：结构解析只数到二级（107 页），2 个三级页被漏出匹配集（PII Detection and Redaction / Streaming Guardrails），恰等于"结构外 2 页"，已按 x1-x2 前缀落盘
- x 页内容抽验：10.7K/15.8K bytes，真页确认
- **最终覆盖：109/109 = 100%**
