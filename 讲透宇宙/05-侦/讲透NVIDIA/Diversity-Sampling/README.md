# 讲透 Diversity-Sampling

NVIDIA/Dependency-Patterns 集群微仓之一：主动学习**多样性采样**（coreset 最远点贪心）的 GPU 参考实现。Python 微仓（8 文件：核心 193 行单类 + 演示 notebook + 三测试 + CI 配置）。

## 全链状态表

| 阶段 | 状态 | 产物与指标 |
|---|---|---|
| 批分析 | ✅ | 3 批（CI workflow / 文档 / notebook+src+tests），21 节点 34 边，imports 1:1 对账（scanner 唯一内部边 tests→coreset.py 已发）+ notebook sys.path 运行时依赖 5 条手扫边 |
| 终验 | ✅ | json.load 全过 / ID 唯一 21/21 / 文件覆盖 8/8 / 零悬空零自环 |
| merge | ✅ | assembled-graph 21n/34e，tested_by 补链 1 节点打 "tested" 标签 |
| layers/tour | ✅ | 7 层（微仓下限达标）/12 步 tour，python 自检全覆盖 21/21 |
| finalize | ✅ | validator 0 issues 0 warnings；fingerprints 8 文件基线 @6e5352b2 |
| onboard | ✅ | `onboarding/ONBOARDING.md`（8 节，锚 30+） |
| explain | ✅ | 3 篇（coreset.py / plot.py / Demo_wiki.ipynb），行号锚+cell 锚全核实 |
| 图谱位置 | — | 仓内 `.understand-anything/knowledge-graph.json`（21n/34e/7层/12步） |

## 一句话架构

`CoresetSampler`（`src/coreset.py:24`）= DBScan 每簇一点初始化 + torch 增量 min 距离贪心 argmax；`plot.py` 三函数做 t-SNE 可视化；notebook 在 Wikipedia 子集上量化证明 coreset 优于随机采样（多样性占比 + KL 散度双指标）。

## 甄别清单（源码级实证）

1. **CI 是从未生效的死配置**（GitHub API 实证 actions/runs total_count=0，2026-11-07 查询）：`python-app.yml:8` 触发分支写死 `"master"`，上游默认且唯一分支是 `main`——push/PR 永不触发。
2. **三测试只能在 GPU 机器通过**：测试构造 `CoresetSampler` 均未传 device（默认 "cuda"，`src/coreset.py:51`），无 GPU runner 上 `.to("cuda")`（`src/coreset.py:164`）必抛错——与坑 1 叠加互相掩埋（CI 若真跑过就会暴露）。
3. **notebook 对比实验的 coreset 臂是 `initialization=""` 的纯贪心**（cell 28 实证）：DBScan 初始化的卖点**没有**进入量化对比曲线——对比只测最远点贪心本身的收益，属干净的消融设计（引用 README+notebook 结论时注意口径）。
4. **README 结构树与实际不符**：`README.md:80` 的 `src/input/` 不存在，数据实际放根下 `input/`（`README.md:52`）；快速上手的 `from coreset import ...`（L58）只在 notebook sys.path 环境成立，库式用法应为 `from src.coreset import ...`。
5. **min_distances 两段式初始化**：种子预计算段用 `ids[:-1]`（`src/coreset.py:173`）刻意排除最后一个种子，循环首轮补上——非漏算。
6. **notebook 对 cuml 硬失败 vs 库内静默降级**：cell 4 `raise ImportError`，与 `src/coreset.py:79` 的 try/except 降级策略相反。
7. notebook cell 29 注释 "3 -> 1 for faster execution" 系作者提速改动痕迹，正式复现建议恢复多次取均值。

## 相关产物

- 图谱：`/usr-data/data2/repos/agent-repos/NVIDIA/Diversity-Sampling/.understand-anything/knowledge-graph.json`
- 精讲：`explain/src-coreset.py.md`（核心采样器）/ `explain/src-plot.py.md`（可视化三件套）/ `explain/notebooks-Demo_wiki.ipynb.md`（端到端演示与量化对比）

*2026-11-07 全链收官（understand 流水线，微仓口径 3 批/7 层/12 步/3 篇 explain）。字数双口径钉版：onboard 不计空格 5532（汉字 1452）、explain 三篇 2154-2834——行号锚密度所致非空格字符偏高，验收口径=不计空格总字符。*
