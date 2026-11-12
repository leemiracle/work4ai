# PINA 新人上手文档（ONBOARDING）

> 依据 PINA 仓库知识图谱（1326 节点 / 2581 边 / 15 层 / 16 步导览，commit `60ea474a`，validator 0 issues）与源码逐条核实编写。文中所有 `文件:行号` 锚均已用 grep 对当前 commit 验证；core 四件套统一写作 `core/xxx.py`，指 `pina/_src/core/` 下的实现文件（与 `pina/` 顶层同名转发 shim 区分）。

## 1. 一句话定位

PINA（Physics-Informed Neural networks for Advanced modeling，见 JOSS 论文标题 joss/paper.md:2）是意大利 mathlab 团队（SISSA）维护的科学机器学习库：在 PyTorch 生态里用物理信息神经网络（PINN）与神经算子**声明式地**求解微分方程，同时覆盖监督拟合与参数反演。所谓物理信息，是指训练信号不来自标注数据，而来自把 PDE 残差（方程两端之差）与边界条件当作损失函数，在网络输出上用自动微分现场求导——于是"解方程"被转化成"最小化物理残差"。PyPI 包名是 `pina-mathlab` 而非 `pina`（pyproject.toml:2），安装即 `pip install pina-mathlab`。底层只依赖三件套 torch / lightning / torch_geometric（pyproject.toml:17-19），Python 版本下限 3.10（pyproject.toml:22）。README 给出两条最小示例线：数据驱动的监督回归（README.md:226-244，从 `from pina import Trainer` 到 `trainer = Trainer(solver, max_epochs=1000, accelerator="gpu")`）与物理信息求解，正好对应库的两大用法支柱。

新人最常问的定位问题：与 DeepXDE 等同类库相比，PINA 的差异化在于**工程化程度**——基于 Lightning 的训练循环（分布式、混合精度、日志开箱即用）、统一的 LabelTensor 数据载体、以及从问题定义到神经算子的一条龙抽象，而不是单一的 PINN 实现。

## 2. 核心架构总览：15 层依赖金字塔

知识图谱把全仓 1326 个节点划成 15 层。剥开来看，这座金字塔只有三种角色：**顶部门面、塔基基元、扇出的子系统**。理解依赖方向（永远单向向下、向 core 汇聚）比记住任何单个类都重要。

- **门面层（fan-in 611 边，全仓之最）**。`pina/__init__.py` 只聚合导出五个符号：`LabelTensor / Trainer / Condition / DataModule / Graph`（pina/__init__.py:7-13），实现全部从 `pina/_src/` 各子系统 import（pina/__init__.py:15-19）。全部测试与教程几乎都经 `import pina` 进入，因此门面就是公共 API 契约本身。模型、求解器、条件、问题等各有自己的桶文件（如 pina/model/__init__.py:3-22 列出 18 个模型）。**门面只做转发、不做实现**——这是阅读本仓的第一把钥匙：在 `pina/` 顶层看到任何类，都要立刻意识到真正代码在 `_src` 里。
- **核心基础层 `_src/core`（塔基）**。被 model（30 边）、equation（22）、condition（18）、domain（16）、problem（11）、callback（9）、solver（8）等全部子系统单向依赖，自身不依赖任何其他子系统——这是"金字塔"含义的由来。四个支柱文件：core/utils.py（fan-in 95，全库第二高）、core/label_tensor.py、core/operator.py、core/trainer.py。
- **七大功能子系统**，全部只向 core 汇聚、经门面暴露：problem 把方程/条件/几何装配成问题对象（_src 内最大消费方：→equation 21 边、→condition 11、→domain 9）；equation 是数学内核；domain 管几何采样；model + adaptive_function 提供函数逼近器（内部密度全 _src 最高，高度内聚）；solver 加九个 mixin 负责训练组装，其中 solver→condition 26 边是全仓最大的子系统间依赖；callback 是训练循环的运行时插件；weighting / loss / optim 构成训练目标三组件；data 管外部数据集的批次化，与 domain（采样生成）互补。
- **四个外围资产层**：tests（126 个测试文件，两组镜像覆盖）、tutorials（24 个 notebook 加 24 个 CI 导出的同名 .py 双轨）、docs（211 个文件，其中 172 个 API 页由 apidoc 从代码树自动生成——文档结构是代码结构的派生物）、工程配置层（6 条 GitHub Actions、14 份治理文档、三套 AI 技能目录）。

一页纸速览看 API_scheme.md 的 mermaid 图（API_scheme.md:7），画了 11 个子模块的依赖关系（注意其中一处笔误，见第 8 节）。

这套分层带来两个直接可验证的推论，读代码时可当定位技巧用：其一，`pina/` 顶层的同名文件（pina/trainer.py、pina/utils.py 等）都只是几行到几十行的转发 shim，真正实现必须下到 `_src`；其二，任何跨子系统的 import 都是坏味道——比如 equation 里需要微分就 import core 的 operator（poisson_equation.py:5），而不会去碰 model；当你发现某个文件同时 import 两个子系统，它多半属于 solver 或 problem 这类"装配者"。

## 3. 关键模块深读

### 3.1 problem：声明式问题抽象

PINA 的核心心智模型是**问题 = 变量 + 域 + 条件**，三者都在一个 Python 类里以类属性/方法声明，没有配置文件、没有 DSL。基类 `BaseProblem`（core 之上的 problem/base_problem.py:19）在构造时做一件关键事：把 `conditions` 字典里每个条件对象反向绑定回所属问题——`self.conditions[name].problem = self`（base_problem.py:39-42），后续采样与残差计算都靠这条回链；`input_variables` 是抽象属性（base_problem.py:241），`discretised_domains` 与 `are_all_domains_discretised`（base_problem.py:263、276）支撑 Trainer 判断就绪状态。空间问题 `SpatialProblem` 用 `@abstractmethod` 强制子类给 `spatial_domain`（spatial_problem.py:34-35），时间问题同理要求 `temporal_domain`（time_dependent_problem.py:34）；`ParametricProblem` 与 `InverseProblem` 面向参数化与反演场景，六个问题类型统一从 pina/problem/__init__.py:12-17 导出。

zoo 预置问题里最值得精读的是 `Poisson2DSquareProblem`（poisson_problem.py:27）——一个类读通即掌握全部声明式语法：`output_variables = ["u"]`（L69）声明输出变量；`spatial_domain = CartesianDomain({"x": [0, 1], "y": [0, 1]})`（L70）声明单位方域；`domains` 字典把内部域 `"D"` 与边界 `"boundary": spatial_domain.partial()` 区分开（L72-75）；`conditions` 字典把 Dirichlet 边界 `Condition(domain="boundary", equation=FixedValue(0.0))` 与 Poisson 方程 `Condition(domain="D", equation=PoissonEquation(...))` 分别绑域（L77-82）；再附一个解析解方法 `solution` 供对拍。同目录还有 Burgers（burgers_problem.py:26）、Helmholtz、Advection、AllenCahn、AcousticWave、DiffusionReaction、反演用的 `InversePoisson2DSquareProblem(SpatialProblem, InverseProblem)`（inverse_poisson_problem.py:75）与最朴素的 `SupervisedProblem(BaseProblem)`（supervised_problem.py:7），统一经 pina/problem/zoo.py:15-25 转发。

采样入口是 `BaseProblem.discretise_domain(n=None, mode="random", domains=None, sample_rules=None)`（base_problem.py:74-75）。四种模式：`"random"` 均匀随机、`"latin"`/`"lh"` 拉丁超立方、`"chebyshev"` 切比雪夫点、`"grid"` 网格（base_problem.py:84-86）；但要警惕几何限制——只有 random 在所有几何上通用，grid/chebyshev/lh 仅部分几何支持（base_problem.py:111-115）。采样算法的底层实现就在塔基：拉丁超立方 core/utils.py:182 的 `torch_lhs`、切比雪夫根 utils.py:235 的 `chebyshev_roots`、多域点合并 utils.py:135 的 `merge_tensors`。

### 3.2 condition：六类训练契约

`Condition` 是问题定义与求解器之间的数据契约，也是本仓最精巧的一个类：它没有自己的 `__init__` 逻辑，而是在 `__new__` 里按传入关键字组合分派（condition.py:127 起），传位置参数直接 ValueError。分派依据是内部 `_SPECS` 表（condition.py:106-122），列出六种具体条件：`InputTargetCondition`（input+target 监督数据对，支持 Tensor/LabelTensor/PyG Data）、`InputEquationCondition`（固定输入点+方程，替代随机采样算残差）、`DomainEquationCondition`（domain+equation，域上采样施加物理残差——PINN 的核心条件）、`DataCondition`（仅 input 的非监督条件）、`TimeSeriesCondition` 与 `GraphTimeSeriesCondition`（滑动窗口时间序列，必传 `n_windows` 与 `unroll_length`）。公共桶 pina/condition/__init__.py:11-21 一共导出 9 个符号。每种条件的损失语义由 solver 侧解释，condition 自己只负责装载数据与方程。选型口径：正向求解 PDE 用 domain+equation 在内部域与边界各建一个条件；边界条件也可换成 FixedValue 系方程类挂到边界域上（poisson_problem.py:78 的写法）；有仿真快照或实验数据时用 input+target 做监督条件、甚至与物理条件混用（半物理训练）；反演问题则把未知参数声明进 problem 的 unknown_parameters，数据条件驱动参数收敛。一个 problem 挂多少个条件都合法，多条件的配平交给 weighting 层——这是 PINN 工程里最影响收敛质量的旋钮之一。

### 3.3 equation 与 domain：数学内核与几何来源

方程层的统一接口很薄：`Equation(BaseEquation)`（equation.py:7）包装一个 residual 可调用对象，`residual()` 委托基类求值（equation.py:40）。zoo 侧 12 个方程类经 pina/equation/zoo.py:18-30 转发——七个 PDE（Poisson/Burgers/Advection/AllenCahn/Helmholtz/AcousticWave/DiffusionReaction）加边界条件 `FixedValue / FixedGradient / FixedFlux / FixedLaplacian` 与 `Laplace`。以 `PoissonEquation`（poisson_equation.py:9）为例：构造时接收 forcing_term，residual 就是 `Δu − f`，其中 laplacian 直接 import 自 core/operator.py（poisson_equation.py:5）——方程层自己不做微分，全靠塔基算子。`FixedValue(0.0)`（fixed_value.py:7）编码 Dirichlet 型边界。

几何域层 12 个文件三种基本几何：`CartesianDomain`（cartesian_domain.py:10，轴对齐盒）、`EllipsoidDomain`（ellipsoid_domain.py:10，椭球/Sphere 特例）、`SimplexDomain`（单纯形族），加 Union/Intersection/Difference/Exclusion 四种集合运算拼复杂几何。域层只依赖 core、内部互引 12 边高内聚，采样结果以 LabelTensor 上交。

### 3.4 model 族：从 MLP 到神经算子

`pina.model` 桶导出 18 个模型类（pina/model/__init__.py:3-22），按逼近对象分四线。选型直觉：解单个 PDE 用 FeedForward 起步；学"函数到函数"的算子映射（一族右端项到一族解）用 DeepONet/FNO；输入是点云或网格图用 GNO 系；追求表达能力上限再试 KAN 与 PirateNet（专为 PINN 设计的深层稳定架构，pirate_network.py:9）：

- **MLP 主线**：`FeedForward`（feed_forward.py:9）是最常用入口，支持层宽列表、激活列表与任意前置 batch 维度；`ResidualFeedForward`（feed_forward.py:116）按 Wang et al. 2021 引入残差结构，专门缓解 PINN 训练的梯度流病理。
- **神经算子线**：`FNO` 继承 `KernelNeuralOperator`，谱卷积核 `FourierIntegralKernel`（fourier_neural_operator.py:16、261）做 FFT 截断模态卷积；`DeepONet` 是分支-干结构，但**它与 MIONet 同住一个文件且是继承关系**（deeponet.py:9 定义 `MIONet`、L324 `class DeepONet(MIONet)`），两者由 pina/model/__init__.py:29 一行同时导出；另有 AveragingNeuralOperator、LowRankNeuralOperator、面向图输入的 GraphNeuralOperator 与 EquivariantGraphNeuralOperator。
- **可学习激活线**：`KolmogorovArnoldNetwork`（kolmogorov_arnold_network.py:6）用可学习样条激活替代固定激活函数；adaptive_function 家族（12 个 Adaptive* 文件）把激活的 α/β 做成可学习参数以加速 PINN 收敛，基类 `BaseAdaptiveFunction(torch.nn.Module, AdaptiveFunctionInterface)` 双继承统一参数管理（base_adaptive_function.py:10）。
- **组合块线**：`_src/model/block/` 目录 18 个 py 文件（含 message_passing/ 子包），经 pina.model.block 桶统一导出。代表块：`FourierBlock1D/2D/3D`（fourier_block.py:14、88、162）谱卷积积木、`KANBlock`（kan_block.py:8）可学习样条单层、`RBFBlock`（rbf_block.py:122）径向基、`PeriodicBoundaryEmbedding` 与 `FourierFeatureEmbedding`（embedding.py:7、181）缓解谱偏差；图输入走 message_passing 子包的 Interaction Network、Radial Field 等五个 GNN 块。

### 3.5 solver 族与 mixin 重构

`BaseSolver`（base_solver.py:17，全文件 434 行）承担所有求解器的公共样板：条件注册、DataModule 装配、train/validation/test 三步路由（base_solver.py:235、254）。v0.3 架构重构的关键词是 **mixin**：`_src/solver/mixin/` 下九个混入类（SingleModel/MultiModel/PhysicsInformed/ConditionAggregator/Ensemble/Autoregressive/GradientEnhanced/ResidualBasedAttention/ManualOptimization）自由组合出全部求解器。标准 PINN 就是 `class PhysicsInformedSingleModelSolver(PhysicsInformedMixin, SingleModelSolver)`（physics_informed_single_model_solver.py:12），目标函数为域内残差与边界残差的加权和（其 docstring 的数学定义在同文件 L20-40）。`PhysicsInformedMixin` 的全部秘密是一行装饰器——用 `@torch.enable_grad()` 包住 `validation_step` 与 `test_step`（physics_informed_mixin.py:16-17），因为 Lightning 默认在验证期关梯度，而物理残差必须求导。其余同理：监督拟合 `SupervisedSingleModelSolver`（supervised_single_model_solver.py:7）、逐点可学习权重的 `SelfAdaptivePhysicsInformedSolver`（self_adaptive_physics_informed_solver.py:14，继承 MultiModelSolver）、causal/competitive/gradient/RBA 四个 PINN 变体、autoregressive 与 ensemble 系列，共 16 个导出（pina/solver/__init__.py:4-19）。

### 3.6 callback：R3 refinement 与运行时插件

回调分三簇（pina/callback/__init__.py:8-16）。`optim/` 的 `SwitchOptimizer(new_optimizers, epoch_switch)`（switch_optimizer.py:8、31）在指定 epoch 换优化器——"先 Adam 后 LBFGS"的 PINN 经典配方；`refinement/` 的 `R3Refinement`（r3_refinement.py:10）按 Retain-Resample-Release 三步自适应细化配点：保留高残差点、全域重采样、释放低残差点（r3_refinement.py:12-14），算法出处是 Daw et al. 2023（r3_refinement.py:27），构造参数 `sample_every` 控制细化周期；`processing/` 的 `MetricTracker`（metric_tracker.py:9）在 `on_train_epoch_end` 钩子收集日志指标（metric_tracker.py:73），训练后可导出 DataFrame 做分析。回调层只依赖 core，是观察"训练过程如何被外部塑造"的最佳窗口。

## 4. 数据流与典型调用链

五步主链路，quickstart（docs/source/_quickstart.rst:8，"5 分钟解 Poisson"）与 tutorial1 是两条实证：

1. **定义问题**：继承 SpatialProblem 声明变量与 conditions（_quickstart.rst:37；tutorial1/tutorial.py:32-36 导入 `Trainer, Condition` 与 `PhysicsInformedSingleModelSolver`、`FeedForward`）。
2. **域上配点**：`problem.discretise_domain(n=100, mode="grid", domains=["domain", "boundary"])`（_quickstart.rst:54）。domain 层的采样算法全部来自塔基（torch_lhs/chebyshev_roots），结果装进 LabelTensor。
3. **选模型**：`FeedForward(input_dimensions=..., output_dimensions=..., layers=[64, 64])`（_quickstart.rst:63-65；README.md:238）。
4. **组装 solver**：`PhysicsInformedSingleModelSolver(problem, model)` 把问题、模型、损失、加权方案装配成 Lightning 可训练对象（_quickstart.rst:75；tutorial1/tutorial.py:187）。此处 optimizer/scheduler/loss/weighting 不传则全走默认值。
5. **Trainer 训练**：`Trainer` 是 `lightning.pytorch.Trainer` 的薄扩展（core/trainer.py:20），`Trainer(solver=solver, max_epochs=1000, accelerator="cpu")` 后调 `.train()`（_quickstart.rst:80-83；tutorial1/tutorial.py:201-202）。Trainer 内部会调 `move_discretisation_into_conditions()`（base_problem.py:216）把离散化域搬进条件——**用户脚本不要手动调它**。

一次 `trainer.train()` 内部的数据流：problem 的 conditions 被 `DataModule`（data_module.py:16，继承 LightningDataModule）按条件独立划分 train/val/test；`_DataManager` 工厂按数据形态分派——普通张量走 `_TensorDataManager` 按批切片，图数据走 `_GraphDataManager` 用 `LabelBatch` 组批（data_manager.py:10-20），对外只经 pina/data/manager.py:3-16 暴露。每个 batch 是"条件名 + 点集"的元组列表，solver 按 CLAUDE.md 之外的正式约定逐条件前向、算残差（残差微分靠 core/operator.py 的 `grad`/`div`/`laplacian`/`advection`，operator.py:316、405，低内存场景换 `fast_grad`/`fast_laplacian`，operator.py:124、198），再由 weighting 方案配平——如按梯度范数取逆的 `NeuralTangentKernelWeighting`（ntk_weighting.py:8）——最后聚合反向。全链路数据载体是 `LabelTensor`（core/label_tensor.py:8）：torch.Tensor 子类加命名列，`extract(["x","y"])` 按标签取列（core/label_tensor.py:216），方程残差里按变量名取导数分量全靠它。图数据侧对应 `Graph` 扩展 PyG Data，`RadiusGraph/KNNGraph` 从点云建图（core/graph.py:11、314、370）。优化器统一延迟实例化：`TorchOptimizer` 构造时只存类与超参（torch_optimizer.py:42-44），到 `hook(parameters)` 才真正构造实例（torch_optimizer.py:55-56）——这是 SwitchOptimizer 能运行时换优化器的前提；调度器同理（torch_scheduler.py:9）。

把链路串成一个具象例子（即 tutorial1 的实际内容）：求解一维 Burgers 方程时，先在 problem 里声明 `spatial_domain = CartesianDomain({"x": [-1, 1]})` 与初始/边界两个 Condition；`discretise_domain` 分别对内部与边界采样（tutorial1/tutorial.py:100-101 用 `"lh"` 模式）；模型吃进带标签的 x 列、吐出带标签的 u 列；solver 对每个 batch 先前向得 u，再用 operator 对 u 求 u_x、u_xx，组装 `u_t + u·u_x − ν·u_xx` 残差；weighting 把初始条件残差与内部残差配平后求和反向；Trainer 的 Lightning 循环负责设备搬运、进度显示与日志。理解了这个闭环，PINA 的每个子系统都能对号入座。

## 5. 测试与质量体系

tests/ 共 126 个 py 文件，图谱将其分两组镜像覆盖。**训练主链路上半段六套件 61 文件**：test_model(16)、test_block(11)、test_messagepassing(5)、test_adaptive_function(12)、test_solver(11)、test_callback(6)。**组件层 13 套件 65 文件**：condition(6)、equation(2)+equation_zoo(11)、problem(5)+problem_zoo(9)、domain(7)、data(7)、loss(3)、optim(2)、weighting(4)、label_tensor(2)，加上根部的 conftest 与 trainer/label_tensor/operator/type_checker/package/utils/graph 单文件测试。三条风格特征：其一，导入几乎全部走 `import pina` 门面（test_solver 对门面 55 边），测试即公共 API 契约的活文档——读不懂某 API 用法时，先去对应 test 文件找最小用例，往往比文档更快更准；其二，唯一共享装置是 conftest.py 的 `clean_tmp_dir` 夹具（tests/conftest.py:6-17），整个测试体系显式、无状态、每个文件可独立阅读；其三，test_package.py 整个文件只有一行 `import pina`（test_package.py:1-2），验证发行版可装可导。test_solver 的十一个文件与十一个求解器实现一一对应（如 test_physics_informed_single_model_solver.py），普遍按"构造、训练、验证、测试、存取恢复"五段式组织，直接可当求解器用法样例抄。zoo 对拍是质量底线：test_problem_zoo 九个文件逐一验证预置问题的采样与解析解，test_equation_zoo 十一个文件对拍 12 个预置方程（pina/equation/zoo.py:18-30）的残差表达——改方程实现后跑这两套件是最低验证标准。

## 6. 构建发布与 CI

六条 Actions（.github/workflows/）：`tester.yml` 是 PR 门卫，在 windows/macos/ubuntu 三平台 × Python 3.10-3.14 五版本矩阵上全量回归（tester.yml:16-17）；`master_cleaner.yml` 用 black 守护主分支代码风格（master_cleaner.yml:10）；`deployer.yml` 由任意 tag 触发，`pip install .[doc]` 后构建 Sphinx 文档（deployer.yml:18-19），用 peaceiris/actions-gh-pages 部署文档站（deployer.yml:23），随后发 GitHub release；`tutorial_exporter.yml` 安装 `.[tutorial]` 与 `black[jupyter]` 把 notebook 导出为 py（tutorial_exporter.yml:31）——24 对双轨文件由此保持同步；`monthly-tagger.yml` 每月 1 日 cron `20 2 1 * *` 自动打月度 tag（monthly-tagger.yml:5）；`create-tag.yml` 手动触发建指定 tag。贡献契约（CONTRIBUTING.md）：提交前跑 pytest（CONTRIBUTING.md:69）并 `bash code_formatter.sh`（CONTRIBUTING.md:73）。学术侧 joss/paper.md 是 JOSS 论文全文，附 pinn_base/pinn_feat/pinn_learn 三张架构图。

本仓的独特资产是**三套 AI 技能目录**：.opencode/skills、.claude/skills、.agents/skills 各维护 9-10 个 PINA 工作流技能（pina-workflow、create-problem、define-domains、define-equations、condition-setup、select-model、select-solver、select-trainer、create-skill），由 utils/check_skill_sync.py（main 入口 check_skill_sync.py:265）强制三处同步——这是一个"为 AI 协作原生设计"的仓库：技能目录本身就是给编码代理的操作手册，三个目录对应三种主流代理工具。全局规则钉在 .opencode/skills/RULES.md，七条硬规则都值得新人背下来：禁止修改源码、技能只读（L5-7）；微分算子不缓存，须一次计算多分量再 extract 而非逐分量反复调——六次单独 `grad` 就是六次 backward，合并成一次再逐列提取是六倍速差（L16-20）；推理必须走 `solver(input)` 而非裸 `model(input)`，solver 内部处理标签传播与后处理（L46-49）；域定点变量必须传 float——`CartesianDomain({"t": 0})` 会造出 int64 张量导致无法求导（L59-63）；LabelTensor 转 NumPy 前必须 `.detach()`，否则 matplotlib 直接抛错（L77-82）；`move_discretisation_into_conditions` 由 Trainer 内部调用、用户勿动（L94-97）；交付训练代码前先跑少 epoch 冒烟测试（L99-102）。治理面还有 14 份根级文档（GOVERNANCE.md、STEERING-COMMITTEE.md、SECURITY.md 等），社区规范程度在同类科研库里相当少见。

## 7. 新人路线图（16 步 tour 前 5 步）

1. **项目概览**：从 README 双示例线入手建立"问题→模型→求解器→Trainer"四段式直觉，API_scheme.md 的 mermaid 图看模块分层，joss/paper.md 看学术定位。
2. **安装与工程约定**：pyproject 四组 extras——doc(sphinx 系)/test(pytest+scipy)/dev(black)/tutorial(jupyter+smithers)（pyproject.toml:24-45）；改码前先知道 tester 矩阵与 black 契约。
3. **pina 门面**：全库 fan-in 之王。只导五个符号（pina/__init__.py:7-13），尾部还有 v0.2 弃用名映射（pina/__init__.py:24-27）；模型与求解器桶文件分别是 18 与 16 个导出。任务是建立"门面只转发"的条件反射。
4. **core 塔基**：精读四件套——`check_consistency` 类型校验（core/utils.py:30）、`merge_tensors`（utils.py:135）、`torch_lhs`（utils.py:182）、`chebyshev_roots`（utils.py:235）；LabelTensor 的标签机制；operator 的 grad/laplacian 与 fast_* 变体差异；Trainer 对 Lightning 的扩展点。此层读透，上层全是组合艺术。
5. **问题抽象**：BaseProblem 的条件回绑 → 两个抽象域属性 → 精读 Poisson2DSquareProblem 收束语法 → 跑一遍 `discretise_domain` 四种模式体会几何限制。

（tour 后 11 步依次为：几何域 → 方程与 zoo → Condition 契约 → 模型族 → 组合块与自适应激活 → 求解器族 → 训练回调 → 加权/损失/optim → 数据管理 → 测试体系 → 教程与文档收官。）

给新人的三条实操建议：**改任何 `_src` 代码前先跑对应测试套件建立基线**（tester 矩阵含五版本 Python，本地至少跑 3.10 一档）；**上手第一个实验直接抄 tutorial1**（tutorials/tutorial1/tutorial.py），它是 Problem→模型→求解器→Trainer 全链路的母版；**写方程时对照 equation/zoo 里最接近的现成类改**，残差函数的标签命名约定（如导数列名 dudx）从 zoo 实例里学最快，比读接口文档直观。

## 8. 已知坑与勘误（图谱实证）

1. **API_scheme.md "pina.block" 笔误**：L22 写 `pina.block`，但仓内不存在顶层 pina/block，真实路径是 `pina.model.block`（目录结构实证）。照图索骥会 import 失败。
2. **rbf_block.rst "Radias" 拼写错误**：docs/source/_rst/model/block/rbf_block.rst:5 的标题 "Radias Basis Function Block" 应为 "Radial"。
3. **MIONet 与 DeepONet 同文件且为继承关系**：deeponet.py:9 定义 `MIONet`、L324 `class DeepONet(MIONet)`。按文件名找 DeepONet 实现会扑空；pina/model/__init__.py:29 一行导出两者。
4. **弃用别名经 `__getattr__` 映射，文档仍在用旧名**：`pina.solver.PINN`、`CausalPINN`、`RBAPINN` 等 12 个旧名可用但触发 DeprecationWarning——映射表 `_DEPRECATED_IMPORTS`（pina/solver/__init__.py:63-75，`"PINN": "PhysicsInformedSingleModelSolver"` 在 L69）；GAROM、ReducedOrderModelSolver、PINNInterface 等已彻底移除、导入即 ImportError（L78-92，GAROM 在 L90）。根包的 `PinaDataModule → DataModule` 同理（pina/__init__.py:24）。**写新代码一律用新名**——仓内 CLAUDE.md 的示例用的还是旧别名 PINN 系列。
5. **格式化工具口径不一**：CLAUDE.md Commands 写 `ruff check .`，但 pyproject 的 dev extras 只有 black（pyproject.toml:38）、CI 守护的也是 black（master_cleaner.yml:10）。以 black 为准。
6. **采样模式几何限制**：仅 random 全几何通用，grid/chebyshev/lh 有几何限制（base_problem.py:111-115）；tutorial1 混用 `"lh"`（tutorial1/tutorial.py:100）与 `"latin"`（L115）是合法同义词（base_problem.py:84）。
7. **图谱枢纽描述的行号漂移**：图谱对 RULES.md 的摘要引用了 L114-118，但该文件实际仅 102 行——AI 生成元数据的行号必须以源码为准；本文全部行号已按 commit `60ea474a` 重新核实。

## 附：架构数据速查

| 指标 | 值 |
|---|---|
| 图谱 | 1326 节点 / 2581 边 / 15 层 / 16 步 tour，validator 0 issues |
| 门面 fan-in | 611 边（全仓最高）；core/utils.py 95（第二） |
| 最大子系统间依赖 | solver → condition 26 边 |
| 测试 | 126 文件（上半段 61 + 组件层 65） |
| 教程 | 24 notebook + 24 CI 导出 py 双轨 |
| 文档 | docs/ 211 文件，172 个 apidoc 自动生成 API 页 |
| 技能目录 | .opencode/.claude/.agents 三套 9-10 个 skill，check_skill_sync 强制同步 |

---
*字数统计（双口径）：中文汉字 4,109 字；不计空格总字符 16,013（行号锚密度推高了后者）。事实锚共 121 处引用、111 个唯一 `文件:行号` 锚，全部经 grep 对 commit `60ea474a` 核实，零坏锚。*
