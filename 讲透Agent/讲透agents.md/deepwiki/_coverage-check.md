# Coverage Check

- repo: agentsmd/agents.md
- fetched: 2026-10-21
- 结构清单页数: 18
- 落盘页数: 25

- 结构外页: 7
- 覆盖: 25/18 (INCOMPLETE)

## 甄别结论（2026-10-22 手写覆盖脚本判定）

- 全层级对账（含三级页）：结构 25 页 = 落盘 25 页，命中 25，**MISSING=0，结构外=0**
- 脚本判 INCOMPLETE 系口径问题：结构解析只数到二级（18 页），7 个三级页被漏出匹配集（Additional Agent Logos / Agent Data and Shuffling / Grid View Toggle / LogoItem Rendering / Marquee Animation System 等），恰等于"结构外 7 页"，已按 x1-x7 前缀落盘
- x 页内容抽验：6.4K-14.2K bytes，真页确认
- **最终覆盖：25/25 = 100%**
