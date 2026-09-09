# Decision Records · 决策记录

> 这个目录归档"项目内容增强的决策过程"——为什么选这个方案、对比了什么、增量在哪。
>
> 不属于正文（模块 01-14），但记录"正文的某些章节是怎么演化出来的"，供未来回溯。

## 当前记录

| 日期 | 文件 | 触发 | 决策 |
|---|---|---|---|
| 2026-07-23 | `2026-07-23-transformers-v5-enrichment-plan.md` | 用户提供 `/data/usershare/ai/transformers` (v5.6.0.dev0) + attention 创新点 | **方案 C**（最小动作）：给模块 12-05 部署章节加新 §十二「工程深挖：推测解码、KV Cache 与量化矩阵」（317 行 + 1 实验）。CHANGELOG v2.0.1 |
| 2026-07-23 | `2026-07-23-lean4ai-innovation-analysis.md` | 用户提供 `/data/usershare/ai/lean4ai`（19 开源项目 + 300 万字字典 + 飞腾 D3000 + Lean4 注释） | **方案 D**（A+B 组合）：A 线模块 14 §05 加飞腾 D3000 / B 线模块 13 加形式化验证 / B 线次模块 12 §01 加 Certigrad4。CHANGELOG v2.0.2 |

## 风格

- 每份记录包含：触发 / 三方案对比 / 选定方案 / 增量章节 / 与项目铁律衔接
- 中间产物（草稿、bash 输出、score.py 等脚本）不归档，只归档"决策本身"
- 与 `CHANGELOG.md` 互补：CHANGELOG 记"做了什么"，decision-records 记"为什么这么做"
