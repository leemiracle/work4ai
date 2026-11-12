# 讲透 KNighter

> KNighter: Transforming Static Analysis with LLM-Synthesized Checkers（arXiv:2503.09002v3，SOSP'25，UIUC ise-uiuc）
> 上游仓库 clone：/usr-data/data2/aios/KNighter（基准 f4e834b3，原仓零改动）· 生成于 2026-10-15/16

| 资产 | 说明 | 状态 |
|---|---|---|
| [KNighter-论文与源码全解.md](KNighter-论文与源码全解.md) | 13 节源码级全解（论文×代码映射/五阶段走读/16 模板/勘误 30 条），四角色审查修订版 | ✅ |
| [KNighter-研究态势与代码级机会.md](KNighter-研究态势与代码级机会.md) | 四路深度调研：引用网络×竞品谱系×CSA 生态位×代码级研究机会 11 条 | ✅ 2026-10-16 |
| [code-annotated/](code-annotated/) | 41 文件逐行中文注释镜像，保真终验 41/41（Python AST+token / C++ gcc 剥离 / YAML 剥离） | ✅ |

读法建议：全解 §1-§2 建立框架 → 研究态势看生态 → 需要抠代码时进 code-annotated/（每文件头四段式导航）。
