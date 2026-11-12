# TorchSurv 新人上手指南（ONBOARDING）

> 基于仓库知识图谱（236 节点/452 边/11 层/13 步导览，commit `a28dac5e`）生成；全部行号锚经源码逐条核实。

## 1. 一句话定位与项目背景

TorchSurv 是一个**无参数化约束的纯 PyTorch 深度生存分析（survival analysis）工具箱**：你用任意神经网络输出 log hazard 或 log 参数，它负责提供可微损失与删失校正的时间依赖评估指标。项目由 Novartis × Paris Dauphine × FDA 合作出品，已加入 PyTorch Ecosystem，并被 FDA 监管科学工具目录收录，学术侧以 JOSE（JOSS 姊妹刊）论文形式发表（`paper/paper.md`）。安装支持 uv/PyPI/conda 三渠道（根 `README.md`），核心运行依赖只有五个包（见第 6 节），轻量到可以直接进任何训练管线。

与 R/Python 竞品（survival、pec、sksurv、pycox 等）的本质差异写在根 `README.md` 的竞品对比表里：传统库把模型形式（Cox 线性、Weibull 参数化）写死在公式里，TorchSurv 只约束"损失吃 log hazard、吐标量"的接口契约（`README.md` 中 Cox/Weibull 两个十行伪代码示例即此契约的展示），骨干网络完全自由。包当前版本 v0.2.0（`src/torchsurv/__init__.py:17`），`__all__` 共导出 15 个公共 API 符号加版本号（`src/torchsurv/__init__.py:19-35`）——整个用户可见面就这么大，一天可以全部摸一遍。

生存分析三概念是读懂本仓的前提：**event**（事件是否发生的 bool）、**time**（事件或删失时间）、**censoring**（删失：随访结束仍未见事件）。删失是生存分析区别于普通回归/分类的根本难点——你只知道患者的存活时间"至少是多久"，却不知道确切终点，直接丢掉删失样本会带来偏倚，当作事件处理更错。TorchSurv 的全部设计都围绕"如何在有删失的情况下学风险、评 discrimination 与 calibration"展开：训练侧用偏似然或 IPCW 加权绕开删失，评估侧用 KM 删失分布估计校正指标。理解了这一点，四族损失与三件套指标的每个公式就都有了共同的动机。

新人还值得一读 `docs/notebooks/loss.md`：它从 T_i=min(X_i,D_i)（事件时间与删失时间的较小者）这一观测模型出发，完整推导 Cox 与 Weibull 两族损失的数学形式，是把"删失"翻译成可微目标的最好教材。

## 2. 核心架构总览：11 层依赖梯度

图谱 11 层自上而下是一条清晰的依赖梯度，建议按此顺序建立心智地图。核心规律只有一条：**箭头永远向下**——门面引损失/指标，损失/指标引 stats 与校验，测试与文档引 src，构建与治理在最外围消费一切。新人找代码时反向走：从任何函数出发，顺着 import 向下最多三跳必到 validators 或 KM，这就是全仓复杂度的天花板。

| 层 | 内容 | 代表文件 |
|---|---|---|
| L0 公共 API 门面 | 5 个 `__init__.py` barrel，纯 re-export 零实现 | `src/torchsurv/__init__.py` |
| L1 损失函数 | 四族可微损失 + 推断函数 | `src/torchsurv/loss/cox.py` 等 4 文件 |
| L2 评估指标 | Auc / ConcordanceIndex / BrierScore | `src/torchsurv/metrics/` 3 文件 |
| L3 统计估计与校验基础 | KM、IPCW、validators | `src/torchsurv/stats/` + `tools/` |
| L4-L5 测试与 R 基准 | 14 个 test_*.py + 7 个 R 脚本 + 10 个基准 JSON | `tests/` |
| L6-L7 文档站与教程 | Sphinx 站 + 4 篇 notebook + 3 篇数学推导 | `docs/` |
| L8-L10 CI / 构建 / 治理 | 6 条 workflow、pyproject 单一配置源、治理四件套 | `.github/`、根目录 |

两条结构性事实值得新人第一时间记住：

**其一，`src/torchsurv/tools/validators.py` 是全仓代码依赖的汇聚点。** 它以 11 条 imports 边成为 src 内代码扇入最高的文件（图谱实测；其余被引多的是 documents 文档边加成，如 `cox.py` 总扇入 15 中仅 8 条是 imports）。全部损失与指标入口共用这里的 pydantic v2 模型做输入定型：`SurvivalInputs` 强制 event 为 bool 且至少一个事件（全删失报错，`src/torchsurv/tools/validators.py:127-128`）、time 非负（`src/torchsurv/tools/validators.py:131-137`）、model_validator 校验 event/time/strata 三者等长且 strata 缺省补全 1（`src/torchsurv/tools/validators.py:148-157`）；`ModelInputs` 按 cox/weibull/survival 三种模型约定检查 log_params 形状（详见第 3 节）。**改输入格式只动这一个文件**，这是本仓最重要的单一修改点。

**其二，metrics 层对 stats 层有一条共享依赖边：删失校正权重全部来自 IPCW。** 三个指标（cindex/auc/brier_score）的删失逆概率加权统一由 `src/torchsurv/stats/ipcw.py:17` 的 `get_ipcw` 提供，而它内部又依赖 KaplanMeierEstimator 估计删失分布（`src/torchsurv/stats/ipcw.py:76-77`）。这条 loss/metrics → stats → validators 的单向依赖（无反向边）是全仓架构的骨架。

## 3. 关键模块深读

### 3.1 损失四族（`src/torchsurv/loss/`）

**Cox 偏部分似然**（`cox.py`，756 行，全仓被引最广）：`neg_partial_log_likelihood`（`src/torchsurv/loss/cox.py:248`）支持 Efron/Breslow 两种并列时间（ties）处理、分层 strata 与扩展时变协变量三选项。并列时间指多个受试者同一时刻发生事件——Breslow 法把并列组当作整体处理，计算快但在 ties 多时偏保守；Efron 法在风险集内对并列组做加权拆分，更精确。两者在此处以并列参数切换，R 基准对拍各生成一套参照（见第 5 节）。训练后 `baseline_survival_function`（`src/torchsurv/loss/cox.py:488`）用 Breslow 估计求基线生存函数，`survival_function_cox`（`src/torchsurv/loss/cox.py:632`）由基线外推新个体生存概率 S_i(t)=S_0(t)^λ_i。这是半参数路线：不对基线形状做任何假设，模型容量全部留给神经网络学 λ_i。

**Weibull AFT**（`weibull.py`）：全参数化路线。累积风险（`src/torchsurv/loss/weibull.py:16`）、log_hazard（`src/torchsurv/loss/weibull.py:76`）、生存函数（`src/torchsurv/loss/weibull.py:139`）与负对数似然（`src/torchsurv/loss/weibull.py:181`）全部闭式。约定 log_params 两列分别为 log scale 与 log shape；只给一列时由校验层补 0（即 shape=1，退化为指数分布，见 `src/torchsurv/tools/validators.py:239-240` 的 `impute_missing_log_shape` 调用，归一检查在 `src/torchsurv/tools/validators.py:230-240`）。

**survival 灵活模型**（`survival.py`）：折中路线——神经网络在离散评估时间网格上逐点直出连续 log hazard，`neg_log_likelihood`（`src/torchsurv/loss/survival.py:70`）用梯形法近似累积风险（`_cumulative_hazard_trapezoid` 定义于 `src/torchsurv/loss/survival.py:16`，`torch.trapezoid` 调用在 `src/torchsurv/loss/survival.py:62` 与 `src/torchsurv/loss/survival.py:65` 两个分支）；`survival_function`（`src/torchsurv/loss/survival.py:199`）对新个体同样走梯形积分后取 `exp(-H)`（`src/torchsurv/loss/survival.py:252`）。这是四族中唯一需要数值积分的损失，也因此**唯一原生支持时变协变量**——参数模型（如 Weibull）的 hazard 形式已被参数锁死（`docs/notebooks/time_varying_covariates.md` 有完整论证）。校验层对应要求 log_hz 为 2-D 且列数与 eval_times 严格递增等长（`src/torchsurv/tools/validators.py:360-361`、`src/torchsurv/tools/validators.py:362-366`、`src/torchsurv/tools/validators.py:367-368`），模型形状约定在 `src/torchsurv/tools/validators.py:246-248`。

**Momentum 动量训练**（`momentum.py`）：单文件单类（`src/torchsurv/loss/momentum.py:18`），借 MoCo 思想（源码自注 "inspired from MoCo"，引 He et al. 2019，`src/torchsurv/loss/momentum.py:52`）：在线网络 q 与目标网络 k 并行、目标网络 EMA 更新（默认 rate=0.999，`src/torchsurv/loss/momentum.py:74`）、log hazard 记忆库虚拟扩大批规模，专治小批量下 Cox 损失不稳定的问题。背景动机：Cox 偏似然的分母（风险集求和）在批内样本量小时方差极大——批里只有几个人可比，排序信号近乎噪声。动量框架把"批内样本量"与"有效训练样本量"解耦：目标网络的历史输出存进记忆库，当前在线网络的输出与整个记忆库比较，等价于在远大于批规模的样本集合上算风险集。这是全仓唯一引入训练机制的模块，其余三族都是纯函数式损失。

### 3.2 指标三件套（`src/torchsurv/metrics/`）

三者共享同一接口语法：`compute`/`__call__` 点估计、`integral` 积分、`confidence_interval`/`p_value` 统计推断、`compare` 两模型比较。这套统一接口是刻意设计：时间依赖指标天然要回答"在哪个时刻、以何种加权、和谁比"四个问题，接口语法把四个问题映射到四个方法族，学一个等于学三个。共同点还包括：全部接受 IPCW 删失校正权重、全部走 validators 校验、全部支持 jit 脚本化。

**Auc**（`auc.py`，1221 行，全仓最大文件）：实现 cumulative/dynamic 与 incident/dynamic 两种时间依赖 AUC，case/control 定义在 `src/torchsurv/metrics/auc.py:235-239`（incident 要求 T_i=t，cumulative 只要 T_i≤t），ROC 上梯形积分在 `src/torchsurv/metrics/auc.py:274`；`integral`（`src/torchsurv/metrics/auc.py:296`）以事件密度加权。推断侧双引擎：Blanche 影响函数法（标准误 `src/torchsurv/metrics/auc.py:818`、影响函数 `src/torchsurv/metrics/auc.py:950`）与 bootstrap（`src/torchsurv/metrics/auc.py:982`）；p 值走 t 分布 CDF（`src/torchsurv/metrics/auc.py:787`）；`_update_*` 输入预处理静态方法组从 `src/torchsurv/metrics/auc.py:1149` 起。`docs/notebooks/metrics.md` 给出 C-index 与 AUC^I/D 积分关系的完整证明，值得精读。

**ConcordanceIndex**（`cindex.py`）：可调用对象模式，`__call__`（`src/torchsurv/metrics/cindex.py:60`）算 Harrell 估计量（IPCW 加权即 Uno 版），风险分同值容差由 `tied_tol` 控制（默认 1e-8，`src/torchsurv/metrics/cindex.py:21`，tie 判定在 `src/torchsurv/metrics/cindex.py:229`）；置信区间默认 noether，另有 conservative/bootstrap 两法（`src/torchsurv/metrics/cindex.py:260`、`src/torchsurv/metrics/cindex.py:262`、`src/torchsurv/metrics/cindex.py:278`）。

**BrierScore**（`brier_score.py`）：`__call__`（`src/torchsurv/metrics/brier_score.py:51`）实现 Graf(1999) 估计量（引用见 `src/torchsurv/metrics/brier_score.py:101`），`integral`（`src/torchsurv/metrics/brier_score.py:217`）梯形积分得 IBS；支持 torch.jit 脚本化（判断在 `src/torchsurv/metrics/brier_score.py:183`）。

### 3.3 stats 基础（`src/torchsurv/stats/`）

**KaplanMeierEstimator**（`kaplan_meier.py`）：`__call__`（`src/torchsurv/stats/kaplan_meier.py:31`）以 `censoring_dist` 旗标切换生存/删失双分布估计（默认 False，`src/torchsurv/stats/kaplan_meier.py:35`；估删失分布时把删失当事件处理，`src/torchsurv/stats/kaplan_meier.py:85-87`），核心连乘 1-d/N 在 `src/torchsurv/stats/kaplan_meier.py:90-98`（`torch.cumprod`）；`predict`（`src/torchsurv/stats/kaplan_meier.py:136`）用 `searchsorted` 左极限取新时刻值（`src/torchsurv/stats/kaplan_meier.py:178`），越随访上限时冻结最后估计；另有 `get_survival_table`（`src/torchsurv/stats/kaplan_meier.py:189`）输出生存表与 `_compute_counts`（`src/torchsurv/stats/kaplan_meier.py:209`）统计事件数/风险集数。

**get_ipcw**（`ipcw.py`）：权重 = KM 删失分布估计的倒数。入口 `src/torchsurv/stats/ipcw.py:17`；设备不齐时告警并对齐（`src/torchsurv/stats/ipcw.py:63-69`）；拟合删失分布 KM 后在 new_time 上预测（`src/torchsurv/stats/ipcw.py:80`），删失分布为 0 的时刻权重置 0（mask 逻辑 `src/torchsurv/stats/ipcw.py:83-85`）。直觉：一个在时刻 t 仍被观测（未删失）的样本，代表的是 1/G(t) 个同类样本（G 为删失分布）——被删失概率越高的时点，幸存观测的"代表性权重"越大。指标层用它做无偏校正。取倒数的辅助函数在 `src/torchsurv/stats/ipcw.py:108-116`（此处有死代码，见第 8 节）。

## 4. 数据流与典型调用链

**训练侧**：用户 `import torchsurv`（触发 L0 门面 9 条 re-export）→ 自定义网络前向输出 log_hz/log_params → 调 `loss.cox.neg_partial_log_likelihood(log_hz, event, time)` → 函数入口首先经 validators 定型校验（输入错误在此统一抛 ValueError，报错信息带具体维度，方便定位）→ 张量运算返回标量损失 → backward。四族损失可无痛互换：Weibull 换成 `neg_log_likelihood_weibull`，网格模型换成 `survival.neg_log_likelihood`，接口形状契约不变——这正是"无参数化约束"承诺的落点：换损失不动骨干网络，换骨干不动损失。推断侧同理：`survival_function_cox(baseline_survival, new_log_hz, new_time)` 一类函数吃校验后的张量直出存活概率，eval_time/new_time 的排序唯一性由 `NewTimeInputs` 保证（升序 `src/torchsurv/tools/validators.py:305-307`、无重复 `src/torchsurv/tools/validators.py:308-309`、默认还须落在随访窗 `[min(time), max(time))` 内 `src/torchsurv/tools/validators.py:310-314`）。

**评估侧**：三个指标对象先 `__call__(estimate, event, time, new_time)`（内部经 `get_ipcw` → `KaplanMeierEstimator(censoring_dist=True)` 拿删失校正权重），结果存入实例状态，后续 `integral`/`confidence_interval`/`p_value`/`compare` 复用该状态——这是典型的"可调用对象 + 惰性推断"模式，BrierScore 与 ConcordanceIndex 均如此（BrierScore 的实例状态设计见其类结构，`src/torchsurv/metrics/brier_score.py:51` 起）。`compare` 的典型用法：两个模型各自算完指标后互相比较，返回差值置信区间与 p 值，论文里"模型 A 显著优于 B"的表述即来源于此。整个评估链没有隐式全局状态，同一个指标对象重新 `__call__` 即重置，可以在训练循环的每个 epoch 末尾安全复用。

**测试侧的训练封装**在 `tests/utils.py`（637 行）：`LitSurvival`（`tests/utils.py:24`）是 lightning.LightningModule 封装，`training_step` 前向后调损失并记日志（`tests/utils.py:37`），`setup` 按数据名加载生存数据集（`tests/utils.py:56`）；孪生网络版 `LitSurvivalTwins`（`tests/utils.py:68`）内嵌 Momentum 实例（rate=0.999，`tests/utils.py:73-78`）；`SurvivalDataGenerator`（`tests/utils.py:157`）可按 16 个边界条件旗标生成模拟生存数据；`DataBatchContainer`（`tests/utils.py:559`）做批容器。

时变协变量的输入形态值得单独记：`(start, stop]` 长表 + heart.csv（Stanford 心脏移植 172 条间隔记录）示例见 `docs/notebooks/regression_time_varying.ipynb`，校验层会用向量化方式找并列时刻并逐列 allclose 防错位（`src/torchsurv/tools/validators.py:425`、`src/torchsurv/tools/validators.py:426-432`）。

## 5. 测试与质量体系

测试体系分三层防线：

**第一层 值对拍**：`tests/conftest.py` 提供固定种子夹具（n_samples 默认 64 在 `tests/conftest.py:12`、seed 在 `tests/conftest.py:17`、`survival_data` 固定 seed=42 生成在 `tests/conftest.py:22` 与 `tests/conftest.py:24`、带 3 层 strata 版本在 `tests/conftest.py:31`）与基准 JSON 会话级加载器。以 `tests/test_cox.py` 为范本：模块级加载 4 个 R 基准 JSON（`tests/test_cox.py:14-21`），15 个用例覆盖无结/含结/时变对数似然与 R 逐值对拍、lung/gbsg 真实数据集与 lifelines 对拍、分层基线外推。测试文件命名约定是 `test_$FUNCTIONALITY.py`（`tests/README.md` 阐明），覆盖值对照/输出格式/错误处理三类维度。

**第二层 R 基准对拍资产**：`tests/benchmark_script/` 下 7 个 R 脚本（test_cox.R 用 survival::coxph、test_auc.R 用 survAUC/timeROC/riskRegression、test_ipcw.R 用 pec 等）在模拟数据上算参照值 `write_json` 落盘到 `tests/benchmark_data/` 的 10 个 JSON——含结/无结 Cox 各带 Breslow/Efron 两套参照、extended Cox 两个、KM/IPCW/Weibull/cindex/auc/brier_score 各一。这构成"R → JSON → pytest"的可复现数值证据链，是 TorchSurv"与 R 包数值一致"承诺的根基。方法论上这是"黄金主对照"（golden master）测试的教科书实践：R 生态二十余年打磨的生存分析实现当作真值源，Python 侧任何重构只要对拍通过即等价。改数值算法时先跑 R 脚本再生成新基准，再回归 pytest，三步缺一不可。

**第三层 属性测试与集成冒烟**：`tests/test_hypothesis.py` 用 `tests/strategies.py` 的组合策略随机生成输入，验证 Cox/Weibull 损失有限性、指标落在 [0,1]、KM 估计量单调性等普适性质（`@given` + `max_examples=50`，如 `tests/test_hypothesis.py:21-22`、`tests/test_hypothesis.py:32-33`、`tests/test_hypothesis.py:43-44`）——固定样本单测覆盖不到的输入空间由随机化补位，这正是 CHANGELOG 里 hypothesis 属性测试被单列为版本特性的原因；`test_mnist.py`/`test_train.py` 是 Lightning 驱动的端到端训练冒烟（MNIST 数字"首次分类正确所需 epoch"当生存时间，佐证生存分析不限于医学），`test_torch_jit.py` 验证 torch.compile/jit 兼容——保证库在编译加速场景下不炸。全仓共 14 个 `test_*.py`。

**质量门禁**：pytest addopts 内嵌 `--cov=torchsurv`（`pyproject.toml:177`）与 `--cov-fail-under=80`（`pyproject.toml:180`）——80% 覆盖率是硬门禁，含 R 对拍、属性测试、集成冒烟三类，本地与 CI 同一条命令，不会出现"本地绿远端红"的口径分裂。本地跑测入口 `dev/run-unittests.sh`（PYTHONPATH=src + pytest）。

## 6. 构建发布与 CI

**单一配置源**：`pyproject.toml` 用 hatchling 后端（dynamic version 取自包根 `__init__.py`），运行依赖 torch>=2.8 + scipy/numpy/torchmetrics/pydantic>=2.0（`pyproject.toml:35`），requires-python >=3.10（`pyproject.toml:36`），dev/publish/docs 三依赖组（`pyproject.toml:38`）；ruff（line-length 120，`pyproject.toml:151`）+ mypy strict（`pyproject.toml:135`）+ codespell 全部内嵌，无 setup.cfg/tox.ini 等散落配置——本仓是"单一配置源"工程范本，找任何工具配置先来 `pyproject.toml`。`dev/environment.yml` 是已弃用的 conda 遗留（首行即声明 DEPRECATED—use uv instead，`dev/environment.yml:1`）。本地质检用 `dev/codeqc.sh`：ruff format → ruff check → mypy src/（`dev/codeqc.sh:14-20`），与 CI 的 codeqc job 保持本地/远端一致。

**六条 GitHub Actions**（`.github/workflows/`）：①`codeqc.yml` 质量总闸（lint + 80% 覆盖测试 + 文档构建三并行 job）；②`torch-compatibility.yml` 跑 3 Python（3.10/3.11/3.12）× 2 torch（2.12.1/2.13.0）兼容矩阵（`.github/workflows/torch-compatibility.yml:11-12`），`dev/sync-badges.py` 据此同步 README 徽章；③`docs.yml` 把 Sphinx 文档强推 gh-pages；④`check-changelog.yml` 强制每个 PR 更新 CHANGELOG；⑤`build-release.yml` PyPI 构建冒烟；⑥`draft-pdf.yml` 编译 JOSE 论文 PDF。`.github/CODEOWNERS` 让四位作者的 PR 自动请对应审查人。

**Sphinx 文档站**（`docs/`）：`index.rst` 用 4 个 toctree 组织 API/Tutorials/Under the hood/Other 四大板块（`docs/index.rst:7`、`docs/index.rst:16`、`docs/index.rst:26`、`docs/index.rst:34`）；`conf.py` 注册 myst_parser/autosummary/nbsphinx/sphinxcontrib-bibtex 四扩展并从 torchsurv 包读版本号；`Makefile` 构建前把根治理文档拷入 docs/ 并 sed 重写资源路径；API 参考页靠 autosummary + Jinja 模板（`docs/_templates/autosummary/module.rst`）从 docstring 自动生成，`docs/loss.rst`/`docs/metrics.rst`/`docs/stats.rst` 各列对应子模块。注意 docstring 质量直接决定文档站质量——写新函数时 docstring 里的 doctest 也会被 `dev/run-doctests.sh` 链路执行。本地预览 `dev/build-docs.sh`，线上由 CI 发布 gh-pages。

**学术侧**：`paper/paper.md` 是 JOSE 投稿手稿（Statement of need + 基准对拍结果），`paper/paper.bib` 独立文献库，`communications/blog_pytorch_foundation.md` 是 PyTorch 基金会官方博客推广文。

## 7. 新人路线图（对应图谱 13 步导览前 5 步）

- **Step 1 项目概览**：读 `README.md`（定位 + Cox/Weibull 伪代码 + 竞品对比表）→ `docs/package_overview.md`（一张 mermaid 图看 loss/metrics/stats 三模块全景）→ `docs/CHANGELOG.md`（v0.1.0→v0.2.0 共 8 个版本的演进脉络：pydantic 校验、uv 迁移、hypothesis 属性测试）。半小时建立全局感。
- **Step 2 环境上手**：`pyproject.toml` 看依赖与工具链；按 `CONTRIBUTING.md` 三步走（uv sync --group dev + pre-commit install + pytest）；`docs/devnotes.md` 是 11 节开发者指南（含 PyPI 发布 10 步清单），配 `.pre-commit-config.yaml` 与 `MANIFEST.in`（管 sdist 打包清单）。
- **Step 3 API 门面**：从 `src/torchsurv/__init__.py:19-35` 的 `__all__` 出发，确认 15 个符号与四个子包 barrel（loss/metrics/stats/tools 各自的 `__init__.py`）的 re-export 关系——这是依赖图的 BFS 起点。门面层零实现，全部是转发。
- **Step 4 损失（上）**：精读 `src/torchsurv/loss/cox.py`（先看 `src/torchsurv/loss/cox.py:248` 主函数，再看 `src/torchsurv/loss/cox.py:488` 基线与 `src/torchsurv/loss/cox.py:632` 外推）与 `src/torchsurv/loss/weibull.py`（从 `src/torchsurv/loss/weibull.py:181` 的负对数似然切入），对照 `docs/notebooks/loss.md` 从 T_i=min(X_i,D_i) 出发的完整数学推导逐节读。
- **Step 5 损失（下）**：`src/torchsurv/loss/survival.py`（梯形法，重点 `src/torchsurv/loss/survival.py:70` 与 `src/torchsurv/loss/survival.py:199`）与 `src/torchsurv/loss/momentum.py`（重点 `src/torchsurv/loss/momentum.py:18` 类定义与 `src/torchsurv/loss/momentum.py:52` 设计动机注释），配合 `docs/notebooks/time_varying_covariates.md` 理解为何参数模型不能时变。

第一个动手练习建议：跑通 `docs/notebooks/introduction.ipynb`（GBSG2 乳腺癌数据全流程），再打开 `tests/test_cox.py` 看 R 对拍怎么写——两者对照，"用户怎么用"与"正确性怎么证"一次看全。

之后按导览顺序自然延伸：Step 6 指标三件套 → Step 7 stats 基础 → Step 8 测试体系 → Step 9 R 基准链 → Step 10 教程 notebook（GBSG2 入门/MNIST 动量/时变回归）→ Step 11 文档站 → Step 12 六条 CI → Step 13 治理与论文。完整 13 步定义见图谱 tour。

## 8. 已知坑与勘误（源码实证）

以下六条全部由本次图谱分析与源码抽查实证，前两条已被源码逐行核对。遇到诡异行为先对照本清单，能省去大量定位时间：

1. **ipcw.py 死代码**：`src/torchsurv/stats/ipcw.py:115` 的 `weight = 1.0 / ct` 被下一行 `src/torchsurv/stats/ipcw.py:116` 的 `weight = torch.ones_like(ct) / ct` 立即覆盖，是死赋值。且 `src/torchsurv/stats/ipcw.py:108-114` 的 warning 文案宣称 "Returning ones as weight"，但 if 块内并无提前 return——实际仍会执行 1/ct（ct=0 处得 inf），**告警文案与行为不符**，读代码或调试权重异常时勿被该文案误导。
2. **run-doctests.sh 注释失真**：`dev/run-doctests.sh:2` 注释写 "Run all unit tests"，实际行为是 L12 用 find+grep 扫描 src/ 下含 `if __name__ == "__main__"` 块的文件（共 9 个核心模块），L14-17 sed 转点分模块名后逐个 `python -m` 运行模块级 doctest——跑单测应使用 `dev/run-unittests.sh`。
3. **R 脚本硬编码绝对路径**：`tests/benchmark_script/test_weibull.R:107` 的 write_json 目标写作 `/Users/Monod/git/torchsurv/tests/benchmark_data/benchmark_weibull.json`，离开原作者机器无法直接重生成基准，复现基准链前需先改此行。
4. **fan-in 口径需分清**：说"validators.py 扇入 11 全仓最高"仅指 **imports 代码边**口径（图谱实测 `src/torchsurv/tools/validators.py` 纯 11 条 imports）；若把 documents（文档引用）边计入，`src/torchsurv/loss/cox.py` 总扇入 15（8 imports + 5 documents + 2 其他）才是被引最广的文件。两个说法都对，口径不同。
5. **environment.yml 已弃用**：`dev/environment.yml:1` 明示 "DEPRECATED — use uv instead"，权威依赖在 `pyproject.toml` 的 dependency-groups，新人勿按 conda 流程配环境。
6. **__all__ 计数口径**：`src/torchsurv/__init__.py:19-35` 的 `__all__` 实际 16 项 = 15 个公共 API 符号 + `__version__`，文献里"15 个符号"的说法不含版本项。

这些坑的共同形态是"注释/文案与代码漂移"——这正是有 R 对拍资产护体的仓库最不怕的事：即使有人误改文案，数值正确性由基准链兜底。新人提 PR 前建议自查三件：doctest 是否通过（`dev/run-doctests.sh`）、覆盖率是否守住 80%（`pyproject.toml:180`）、CHANGELOG 是否更新（CI 的 check-changelog 会拦）。若要修第 1 条死代码，注意同时核对告警文案语义，避免只删行不修文案留下新的漂移。

---

*生成于 2026-10-21，基于 torchsurv 知识图谱（commit `a28dac5e`）与源码逐行核实；行号锚 113 处（去重 99 个），全部经 grep/sed 对源码验证，零坏锚。正文纯汉字 4017、不计空格字符 15014。*
