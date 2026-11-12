# `src/torchsurv/__init__.py`：15 个符号定义的整个用户世界

## 一、角色定位

一句话：这是 TorchSurv 包的**公共 API 门面**——35 行纯 re-export，把四大子包的 15 个公共符号聚合成 `import torchsurv` 一次可见的全部用户世界。在 11 层架构中它位于最顶层 **L0 公共 API 门面层**（与 `loss/__init__.py`、`metrics/__init__.py`、`stats/__init__.py`、`tools/__init__.py` 四个同类 barrel 并列），是依赖图的 BFS 起点：图谱中它的 9 条出边全部指向 L1/L2/L3 的实现文件，自身零实现。

## 二、内部结构

文件只有 35 行，结构一眼见底：

- **模块 docstring**（`src/torchsurv/__init__.py:1-3`）：声明这是 TorchSurv 主模块，包含用 PyTorch 做生存分析的核心类与函数。
- **9 条 import**（`src/torchsurv/__init__.py:7-15`）：Cox 三函数（L7）、`Momentum`（L8）、灵活模型两函数（L9）、Weibull 三函数（L10）、`Auc`（L11）、`BrierScore`（L12）、`ConcordanceIndex`（L13）、`get_ipcw`（L14）、`KaplanMeierEstimator`（L15）。每行一个来源文件，顺序为 loss→metrics→stats，与层序一致。
- **版本号**（`src/torchsurv/__init__.py:17`）：`__version__ = "0.2.0"`。
- **`__all__` 导出清单**（`src/torchsurv/__init__.py:19-35`）：共 16 项 = 15 个公共 API 符号 + `__version__`。注意文献里"15 个符号"的说法不含版本项（口径坑）。清单刻意按字母排序，3 个损失函数族、3 个推断用的 survival function、3 个指标类、2 个 stats 件、再加 `Momentum` 与 `log_hazard`。

15 个符号按功能分四组：**训练损失 4 个**（`neg_partial_log_likelihood`/`neg_log_likelihood_weibull`/`neg_log_likelihood`/`Momentum`）、**推断函数 5 个**（`baseline_survival_function`、`survival_function_cox`/`_weibull`/无后缀版、`log_hazard`）、**指标 3 个类**（`Auc`/`BrierScore`/`ConcordanceIndex`）、**统计基础 2 个**（`get_ipcw`/`KaplanMeierEstimator`）。

## 三、外部连接

图谱口径下本文件的邻居：

- **出边（9 条，全为 imports）**：直接依赖 `loss/cox.py`、`loss/momentum.py`、`loss/survival.py`、`loss/weibull.py`、`metrics/auc.py`、`metrics/brier_score.py`、`metrics/cindex.py`、`stats/ipcw.py`、`stats/kaplan_meier.py`——恰好是 src 内除 validators 与四个子包 barrel 之外的全部实现文件。validators 不出现在门面，因为它是纯内部设施，用户无需感知。
- **入边（9 条）**：`pyproject.toml`（L7 `dynamic = ["version"]` + L79 `[tool.hatch.version]`，hatchling 构建时从本文件读版本号——**版本号的唯一真源在此，不在构建配置里**）；`MANIFEST.in` 与 `dev/environment.yml`（打包/环境清单引用）；`docs/conf.py`（Sphinx 文档站从这里取版本）；`paper/paper.md` 与 `communications/blog_pytorch_foundation.md`（论文与官方博客引用 API 面）；`.pre-commit-config.yaml` 与 autosummary 两个模板。
- **子包 barrel 分工**：`loss/__init__.py` 同样 re-export 9 个符号（含 `Momentum`），`metrics/__init__.py` 只导出 3 个指标类，两者让 `from torchsurv.loss import cox` 与 `from torchsurv import cox` 两种用法都成立。

## 四、数据流

典型调用链从这扇门开始：

1. 用户 `import torchsurv`，Python 执行本文件 9 条 import，把 15 个符号挂到包命名空间——此时四大子包的模块代码全部加载，validators 的 pydantic 模型随依赖链就位。
2. 训练侧：用户网络前向输出 log hazard → `torchsurv.neg_partial_log_likelihood(log_hz, event, time)`（实为 `loss/cox.py:248` 的函数）→ 校验、张量运算、返回标量损失 → `backward()`。
3. 评估侧：`auc = torchsurv.Auc()` → `auc(estimate, event, time)` → 内部走 `stats/ipcw.py:17` 的 `get_ipcw` 拿删失校正权重。
4. 发布侧：CI 的 build-release job 触发 hatchling，`pyproject.toml:79` 的 `[tool.hatch.version]` 指回本文件 L17 抓 `0.2.0` 写进发行物元数据。

全链没有一处逻辑落在本文件——它只做名字搬运，这正是它能 35 行管住整个 API 面的原因。

## 五、设计决策

**为什么用扁平门面而不是只靠子包？** `import torchsurv; torchsurv.Auc` 比 `from torchsurv.metrics.auc import Auc` 短一半，对 Notebook 用户（本仓主要受众之一，四篇教程 notebook 都这么写）更友好。同时保留子包 barrel，两条路径等价，属于低成本的接口冗余。

**为什么 `__all__` 显式列出而不是 `import *` 自动收集？** 显式清单即 API 契约：私有函数（如 `cox.py` 的 `_partial_likelihood_efron`，见 `src/torchsurv/loss/cox.py:13-20` 中被注释掉的私有项）天然排除；未来加符号必须改这里，等于强制作者做一次"这算不算公共 API"的决策。文档站的 autosummary 也以 `__all__` 为准生成 API 页。

**批判视角**：门面把 metrics 类与 loss 函数混在一个扁平命名空间，15 个符号尚可，若未来涨到 30+ 个（比如再加 auc 的变体、更多参数族），扁平面会开始拥挤；届时子包路径（`torchsurv.metrics.Auc`）会成为主入口，门面退化为兼容层。另一面，版本号嵌在源码而非 git tag/CHANGELOG 单独维护，好处是"装了什么版本"import 即知，代价是发版要同时改两处（`__version__` 与 `docs/CHANGELOG.md`），CI 的 check-changelog 工作流就是为对冲这个漂移风险设的。

## 六、新人提示

- **上手顺序**：先读本文件的 `__all__`（L19-35）当 API 目录，再按"损失→指标→stats"顺序进入各实现文件；从任何符号出发顺 import 向下最多三跳必到 `tools/validators.py` 或 KM，这是全仓复杂度天花板。
- **坑 1**：`from torchsurv import *` 拿不到 `KaplanMeierEstimator` 之外的 stats 私有工具；想改输入校验行为要去 `tools/validators.py`，门面里找不到。
- **坑 2**：改版本号只改 `__version__` 不够，CHANGELOG 必须同步更新，否则 PR 会被 `check-changelog.yml` 拦下。
- **坑 3**：不要往本文件加任何实现——一旦门面有了逻辑，`dynamic version` 抓取、autosummary 扫描、pre-commit 钩子的隐式假设都可能被打破。35 行是刻意维持的不变量。
