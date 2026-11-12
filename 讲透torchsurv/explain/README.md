# TorchSurv 重要文件精讲（explain 系列，12 篇）

> 基于 torchsurv 知识图谱（236 节点/452 边/11 层/13 步 tour，commit `a28dac5e`）与源码逐行核实撰写，2026-10-21。
> 每篇六节钉版结构：①角色定位（一句话+11 层架构位置）②内部结构（类/函数地图+行号）③外部连接（imports/tested_by 邻居）④数据流（典型调用链走读）⑤设计决策（为什么+批判视角）⑥新人提示（上手顺序+坑）。
> **字数口径：单篇 2500-4800 不计空格字符**（中文字符与英文非空白字符同权计数），系列合计 48006。

## 篇目索引

| # | 文件 | 一句话摘要 | 字数 |
|---|------|-----------|------|
| 01 | `src/torchsurv/__init__.py` | 35 行纯 re-export 门面：9 条 import 聚合 15 个公共符号 + 版本号真源（hatchling dynamic version 指回 L17），`__all__` 即 API 契约 | 3545 |
| 02 | `src/torchsurv/loss/cox.py` | Cox 偏部分似然全家桶：Efron 向量化核（scatter_add+reverse_cumsum）、Breslow 基线、分层/时变/并列三选项，全仓被引最广 | 4443 |
| 03 | `src/torchsurv/loss/weibull.py` | Weibull AFT 闭式似然族：log 参数空间 + expm1 稳定技巧 + 三层 clamp 防爆，CDF 外包 torch.distributions | 4188 |
| 04 | `src/torchsurv/loss/survival.py` | 灵活生存模型：唯一需要梯形法数值积分、唯一原生支持时变协变量的损失，EvalTimeInputs 网格契约 | 3780 |
| 05 | `src/torchsurv/metrics/auc.py` | 时间依赖 AUC 双定义（cumulative/incident）+ Blanche 影响函数与 bootstrap 双引擎推断，1221 行全仓最大 | 4304 |
| 06 | `src/torchsurv/metrics/cindex.py` | Harrell/Uno 一体的 C-index：可比对字典 + 计数分项留存供 Noether SE，tmax 截断与 tied_tol 细节 | 4450 |
| 07 | `src/torchsurv/metrics/brier_score.py` | Graf 删失校正 Brier 分：case/control 双权重残差核 + IBS 梯形归一，parametric/bootstrap 推断 | 4173 |
| 08 | `src/torchsurv/stats/ipcw.py` | IPCW 权重枢纽：KM 删失分布取倒数，0 处置 0 的 mask 策略；含死代码+文案漂移勘误（L112 vs L115-116） | 3347 |
| 09 | `src/torchsurv/stats/kaplan_meier.py` | KM 双分布引擎：censoring_dist 三行角色互换一物两用，predict 的 -inf/1.0 前缀与左极限语义 | 3876 |
| 10 | `src/torchsurv/tools/validators.py` | pydantic v2 输入定型：5 模型 + 2 助手，src 内 imports 扇入最高（11 条），"改输入格式只动这一个文件" | 4509 |
| 11 | `tests/strategies.py` | hypothesis 属性测试策略库：约束感知生成（与 validators 三对镜像约束）；实证发现 conftest 夹具零消费、策略值域被测试体丢弃 | 3809 |
| 12 | `docs/notebooks/loss.md` | 四族损失数学总纲：T_i=min(X_i,D_i) 观测模型出发的完整推导 + 选型 FAQ + 对照表，三族实现 docstring 的上游教科书 | 3582 |

## 质量口径

- **行号锚**：全部锚（`path:N` 式与 `L N` 式合计 492 处，篇内去重；另有 13 处"11 层架构"层号引用不计）经源码 grep/read 逐条核实，写作后又跑了一轮自动化抽取比对，修正过 10 处初稿锚（auc.py 单行签名 L19、auc_type 默认 L64、配对检查 L1133、auc_type 检查 L1137、训练集提醒 L162-163、survival.py τ_1 提醒 L123-124 等）与 7 处跨文件锚消歧（"本文件 L11"/"auc.py:10" 式改写）。
- **源码只读**：全程未改动 torchsurv 仓任何文件。
- **批判视角内容均为源码实证**：ipcw 死代码、conftest 夹具零消费（grep 全 tests/ 无引用）、test_hypothesis 丢弃策略值改用 randn（tests/test_hypothesis.py:26-27）、BrierScore 与 Auc 的 `_find_torch_unique_indices` 重复实现（brier_score.py:760 / auc.py:1104）。

## 阅读路线建议

- **按依赖梯度**（推荐新人）：01 门面 → 10 validators（全汇点）→ 09 KM → 08 IPCW → 02/03/04 损失三族 → 06/07/05 指标三件套（先 cindex/brier 后 auc）→ 11 测试 → 12 数学总纲收束。
- **按 tour 步**：对应图谱 13 步导览的 Step 3（01）、Step 4-5（02/03/04）、Step 6（05/06/07）、Step 7（08/09/10）、Step 8（11）、Step 10（12）。
- 与 `../onboarding/ONBOARDING.md`（113 处锚的全局导览）互为详略：onboarding 给地图，本系列给每栋楼的剖面图。
