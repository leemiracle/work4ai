# `docs/notebooks/loss.md`：四族损失的数学总纲

## 一、角色定位

一句话：以观测模型 T_i=min(X_i,D_i) 出发，把 TorchSurv 四族损失（Cox/Weibull/Exponential/Flexible）的数学形式、假设清单与选型 FAQ 完整推导一遍的 **MyST 数学文档**——src 里三族损失 docstring 的"上游教科书"。位于 **L7 教程 Notebook 与数学文档层**（与四篇 notebook、`metrics.md`、`time_varying_covariates.md` 同层），是图谱里唯一同时挂 `cox.py`/`weibull.py`/`survival.py` 三个 documents 边的文件——"一篇文档统领三族实现"的知识中枢。

## 二、内部结构

216 行、六段式：

- **Introduction**（`docs/notebooks/loss.md:6-23`）：观测模型三件套——T_i=min(X_i,D_i)（L13）、事件指示 δ_i=1(X_i≤D_i)（L19）、协变量 x_i 可高维（L23，"an image or a vector of clinical features"点明深度学习场景）。这三行是全仓所有 docstring 里 δ_i/T_i 记号的定义源。
- **Cox Model**（L26-61）：hazard 分解 h_i(t)=λ_0(t)·λ_i（L37）→ TorchSurv 的改写 log λ_i = f_θ(x_i)（L46，**基线不参数化、相对风险神经网络化**的接口契约）→ 偏似然损失公式（L53）→ 假设三条：比例风险、独立删失、协变量效应正确设定（L59-61）。
- **Weibull model**（L65-106）：标准 hazard（L76）→ 网络输出 log ρ_i 与 log λ_i 双头（L86）→ 负对数似然（L92）与闭式累积风险 H_i(t)=(t/λ_i)^{ρ_i}（L98）→ 假设含"网络能吸收对 Weibull 形式的偏离"（L104）。
- **Exponential Model**（L108-122）：ρ_i≡1 的特例、hazard 常数 1/λ_i（L116-119），损失与 Weibull 完全同路——"免费的第三个模型"，对应实现侧 `log_params` 补零列退化（`weibull.py` 的 `impute_missing_log_shape`）。
- **Flexible Survival model**（L125-159）：唯一无参数形式的一族——log h_i(t) = f_θ(x_i, t)（L138，**时间进网络**）；损失含积分项 ∫h（L145）；关键论证在 L150-151：累积风险无闭式，TorchSurv 用梯形法数值近似，"这是本库唯一需要近似似然的损失"；L153 给出等价性保证：若网络输出的 hazard 恰为 Weibull/指数形式，本模型精确复原它们的对数似然——这也是无 R 基准时数值正确性的验证原理；假设四条（L156-159）多了一条"数值积分精度依赖时间离散化"。
- **FAQ 与 Summary Table**（L162-216）：四个"When should I use"问答（Cox L164、Weibull L175、Exponential L185、Flexible L195）各配"Use if/Avoid if"双清单；收尾对照表（L211-216）四行五列——hazard 形式、时变风险支持（只有 Flexible 打勾）、闭式似然（只有 Flexible 打叉）、适用场景。

## 三、外部连接

- **documents 出边 3 条**（图谱）：指向 `loss/cox.py`、`loss/weibull.py`、`loss/survival.py`——文档与实现的映射按节对应：第 1 节↔`neg_partial_log_likelihood`（`cox.py:248`）、第 2/3 节↔`neg_log_likelihood_weibull`（`weibull.py:181`）、第 4 节↔`neg_log_likelihood`（`survival.py:70`）。
- **入边**：`docs/index.rst` 的 toctree 收编——它随 Sphinx 站发布，myst_parser 渲染 LaTeX。
- **横向同层**：`metrics.md`（指标的数学）、`time_varying_covariates.md`（时变协变量的深入论证，与本文第 4 节互为详略）构成"数学三文档"；四篇 ipynb 是它们的可执行版。
- **写作身份**：L4 署名 Mélodie Monod（第一作者），`paper/paper.md` 的方法节与本文同源——学术侧与文档侧共享一套推导。

## 四、数据流

读者动线走读：新人从 `docs/notebooks/introduction.ipynb` 入门后，被 README 指到本文补数学 → 顺 Introduction 的三个定义往下，按自己的数据特征在 FAQ 找到候选模型族 → Summary Table 一眼比对四族 → 回到 src 找对应函数落地——文档的消费终点是 `import torchsurv` 的那行代码。

维护动线走读（对本仓贡献者）：改损失公式必须同步三处——本文件对应节、src 函数 docstring 的 Note 数学块（如 `cox.py:282-358` 五组公式）、R 基准脚本；本文没有 doctest 可执行兜底，它的"正确性"由下游实现的 R 对拍间接背书——这是数学文档与代码文档的验证链差异。

## 五、设计决策

**为什么单独成文而不是全塞进 docstring？** 四族共享观测模型与记号体系，docstring 里每个函数重复 δ_i/T_i 定义会漂移；本文一次定义、三处引用，docstring 只放本族公式。集中推导还让"族间对比"（FAQ 与表格）成为可能——分散的 docstring 里长不出对照表。

**Exponential 独立成节而非脚注**：ρ=1 特例数学上三行就完（L116-119），但选型视角它是"常数风险"这个独立假设——独立成节让 FAQ 的四个问答对称完整，也把"缺 shape 列=选了指数模型"这个接口行为显式化（L122 明说"omit it altogether"）。

**Flexible 节把"近似"写进身份**（L151）：不掩饰梯形法是近似、直接断言唯一性——配合 L153 的等价性保证（输出参数族形式则精确复原），读者获得的不是"这族更灵活所以更好"的营销话术，而是"灵活性=数值近似误差+网格超参"的诚实交换条件。

**批判视角**：① 假设清单覆盖了独立删失、形式设定，但**没讨论删失机制相关性**（IPCW 一致性的真正命门）与左右删失（本仓只支持右删失）——假设的"清单完整性"以本仓实现边界为限；② Summary Table 的"Time-varying Risk ✗/✓"一列把 Cox 的扩展模型（`(N,N)` 时变矩阵，`cox.py:350-358` 有完整公式）隐性归入 ✗——表格粒度服务于快速选型，细读者会在 cox.py docstring 发现扩展 Cox 这个"半时变"中间态，两处口径有粒度差；③ FAQ 是定性指南，没有给"如何检验比例风险假设"（如 Schoenfeld 残差）的操作路径——从"怀疑非比例"到"选 Flexible"之间缺一环工具链，得去 R 生态补。

## 六、新人提示

- **上手顺序**：先通读 Introduction 与 Summary Table 建立四族坐标，再按自己项目候选的 1-2 族精读对应节，最后带着公式进 src 对照 docstring 的 Note 块读实现——"文档公式 → docstring 公式 → 代码行"三级映射是最快的深读路径。
- **坑 1**：本文公式用 ρ/λ 记 shape/scale，代码参数是 log_params 两列的 log_scale/log_shape——中间隔着 exp 与列序约定（scale 在第 1 列），对拍时先固定映射。
- **坑 2**：第 4 节的"τ_1 应为观测起点"提醒（对应 `survival.py` docstring L123-124）在本文 L150 一带只隐含在"discretized time grid"里——网格起点选错损失系统性偏小，两处文档都要读到才能避开。
- **坑 3**：修改本文不会触发任何测试失败（无 doctest、无对拍）——公式改错的唯一防线是 review；改公式时把 src docstring 与之逐条 diff 是本仓不成文的纪律。
- **坑 4**：Sphinx 构建时本文经 myst_parser 渲染，LaTeX 块写错只影响文档站不挡 CI 的文档构建 job（警告不升级为错误）——本地 `dev/build-docs.sh` 预览确认渲染是唯一保险。
