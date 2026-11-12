# RESUME-0826.md —— 讲透Graph 断点续传【已全部完成，转完成档案】

> 建单元 2026-08-26，**同日收官**（用户指令"一次性全部做完"）。
> 00-12 章 + E1-E6 全部完成，6 实验可复现。

## ✅ 完成清单

- [x] 前沿调研：34 天术语战争全时间线（papers.md §五）
- [x] 一手核实：arXiv 2608.21156 + Awesome-GE + Graphiti/Zep + LangChain + Neo4j + SurrealDB + GEM 2026
- [x] README（篇目表已物理链接化——Ch10 自我治理示范）/ papers.md / 00-12 章全部落盘
- [x] E1 类型边 vs 相似度 ✅（5/5 vs 0/5；ADR-006 see_also 与 ADR-007 supersedes 主题标签相同=相似度死穴）
- [x] E2 拓扑成本 ✅（线性 13.2K vs 并行 6.7K tok 省 49% 轮次 6→2；验证门 +40%=可靠性税；6分支×0.85 一次全过仅 37.7%）
- [x] E3 bi-temporal ✅（覆盖式 6/8 失史、追加式 4/8 生伪、bi-temporal 8/8；溯源演示 Adidas→Nike validity window）
- [x] E4 图税 ✅（构建 6×/增量 7.2×；输出 token 5× 单价 + 社区摘要层是结构性原因）
- [x] E5 每跳乘法灾难 ✅（p=0.9 十跳 34.9%；交叉点算术：q=0.90,k=5 需每跳 ≥0.979，5×0.98=0.904 打平）
- [x] E6 仓库健康度 ✅（3058 节点/7321 边/自产孤儿率 31.5%；E6b 分类：A 章节伪影 136/B 工作流 9/C 真孤儿 831；治理债排行：讲透Agent 240、实例 217、top-math 146；断链 2155）
- [x] 挂网：主 README 表 + 前沿 108 专题 + Context/Loop/Harness 三姊妹互链 + 本 README 篇目表物理链接

## 🔮 后续期权（非债，按需取用）

1. **还治理债**：实例/ 217 真孤儿 + 断链 2155 分批清理（Ch10 毕业练习：graph_lint.py）
2. **capability graphs 深读卡**：综述 §6 的能力图（typed nodes + authorization/cost/reliability 边）值得单独成卡，挂 top-math-courses 或讲透Agent
3. **季度复查**：Awesome-Graph-Engineering 仓库跟踪新收录；术语战争续集（ontology engineering 会不会是下一个 X 热词）
4. **真 LLM 复验**：E1/E3 可升级为本地 Qwen + 真抽取的版本（当前规则模拟是特性：干净隔离变量，讲透Loop 的 0.5B 教训）

## 断点细节（供后续续写者）

- GEM 2026 全文在搜索缓存 /home/lwz/.local/share/opencode/tool-output/tool_03bc52*.txt
- E6b 脚本在 /tmp/opencode/e6b_orphan_taxonomy.py（结果已存 experiments/E6b_orphan_taxonomy.json；脚本如要长期保留应迁入 experiments/）
- 综述 HTML 版全文也可 webfetch arxiv.org/html/2608.21156 拿三支柱细读
