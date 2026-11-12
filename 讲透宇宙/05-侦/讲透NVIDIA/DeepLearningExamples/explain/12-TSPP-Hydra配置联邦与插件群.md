# 12 · TSPP 的 Hydra 配置联邦与 vendored 插件群

## 角色定位

如果说 launch_training.py（见 11 篇）是 TSPP 的引擎，`conf/` 联邦 + `hydra_plugins/` 四个 vendored 插件就是它的方向盘与变速箱。这一层的使命：让"模型×数据集×训练器"的组合爆炸保持可组合、可复现、可搜索——组合配方（model_dataset/）、调参历史（overrides/best_N）、搜索空间（overrides/hp_search）全部 YAML 化，而超参搜索与并行/分布式执行能力**不是自研框架而是四个从 Facebook hydra 生态 vendored 进来的插件**（optuna sweeper 与 joblib/multiprocessing/torchrun launcher）。这与 FastSpeech 自研 parent_yaml（08 篇）相反：扩展点外包给成熟插件的 namespace package 机制。理解本层是跑通 examples/hp_search.sh 的前提。

## 内部结构

装配总锚是 `conf/train_config.yaml` 的 defaults 链（:4-12），注释直言"The order in this list matters a lot!"——前者只能被后者改。关键装配：`model: ???`（:5 必选）、`dataset: electricity`（:6）、evaluator 行（:7）嵌套两层 resolver 三路选择 `${if:${cmp:${oc.select:trainer, ctltrainer}, xgbtrainer}, xgbevaluator, ...}`——按 trainer 类型自动换评估器；`optional model_dataset@_global_: ${model}_${dataset}`（:8）是**组合配方注入总锚**：运行时插值出 `dcrnn_pems_bay` 这类组名，optional 让无配方组合静默跳过；`optional overrides@_global_`（:11）注入调参覆盖。resolver 注册源是 `conf/conf_utils.py`：`OmegaConf.register_new_resolver` 在 import 时全局注册 and/add/if/sum/cmp/feature.selector 等（conf_utils.py:20-37），launch_training.py:29 的 `import conf.conf_utils  # loads resolvers` 挑明这个副作用模块。

配方库两层：`conf/model_dataset/` 24 份组合配置（图谱钉版多组逐字段同构——GNN 系共享 PEMS-BAY 配方）；`conf/overrides/<dataset>/<model>/` 下 hp_search.yaml（搜索空间）与 best_N.yaml（收敛快照）。**@_global_ 扁平注入机理**是本层最微妙的设计：dcrnn_pems_bay.yaml 的内容是 `trainer.config.batch_size: 64`/`dataset.config.binarized: False` 的**从根写起的全路径**——`@_global_` 把组内容平铺合并进最终配置树的根（而非塞进 model_dataset 子节点），而 Hydra 1.1 的组选项文件不能自带 defaults 再引用别的组，组合配置只能全路径内联固化。overrides 里 `+trainer.config.ema_decay` 同理：+ 前缀向 ctltrainer.yaml 基座**追加不存在的新键**。

## 外部连接

四个 vendored 插件（版权头均为 Facebook, Inc.，联邦仓特征）：①`hydra_optuna_sweeper/`——核心 `_impl.py` 把 Hydra override 语法翻译成 Optuna 分布：`override.is_choice_sweep()`（_impl.py:88）→ CategoricalDistribution，`is_interval_sweep()`（:118）→ 均匀/离散分布，`"log" in value.tags`（:122）→ Log 系分布——choice()/interval()/tag(log,...) 三个语法实体就是这三条分支；config.py 定义 6 个采样器配置类（TPE/Grid/Random/CmaEs/NSGAII/MOTPE）并注册为 hydra/sweeper 组。②`hydra_joblib_launcher/`——joblib_launcher.py:43 `from . import _core` 放在 launch() 方法体内，与 _core.py 顶层"导入 JoblibLauncher 做类型注解"构成**刻意的循环依赖打破模式**；_core.py:110 用海象运算符 `(v := joblib_cfg['n_jobs'])`，backend 硬编码 loky（注释言明 threading backend 与 Hydra 不兼容）。③`hydra_multiprocessing_launcher/`——原生 mp.Process 版（_core.py:79 `_proxy_fn_call` 代理+结果队列、:161 `mp_context.Process`），注册名 multiprocessing（config.py:18）。④torchrun 启动器**双拷贝并存**：`hydra_torchrun_launcher/`（2024 版权，带 tests/README 完整包）与 `distributed_launcher/hydra_plugins/hydra_torchrun_launcher/`（2022 旧版）各一份 _core.py（diff 65 行：新版增 rdzv_configs={"rank": 0} 与 redirects/tee），**两份 config.py 都注册 `group="hydra/launcher", name="torchrun"`**（:40 与旧侧 :42）——Dockerfile:70 只装新拷贝，旧拷贝是遗留死资产。两个 `_core.py` 都把 `start_method` 固定 fork（spawn/forkserver 需 pickle，包装函数不适用）。另有顶层孤儿 `hydra_plugins/optuna_sweeper.py`：从 Hydra 源码 vendored 的 Sweeper 抽象接口，`from .launcher import Launcher` 的目标文件仓内不存在（不可独立导入）——但 Dockerfile:71 用 `cp optuna_sweeper.py .../hydra/plugins/sweeper.py` **覆写已安装 Hydra 的插件接口**，注入 ExperimentSequence 迭代协议与 validate_batch_is_legal 预检。

## 数据流

一次 hp_search 的完整装配流（examples/hp_search.sh）：按 DISTRIBUTED 开关选 launcher——单机 `hydra.launcher=multiprocessing + n_jobs=8`，分布式 `hydra/launcher=torchrun`（hp_search.sh:32）→ 命令行 `overrides=${DATASET}/${MODEL}/hp_search` 经 train_config.yaml:11 的 optional 总锚注入搜索空间 → `hydra/sweeper=optuna` 启用 vendored sweeper → TSPPOptunaExperimentSequence（hydra_utils.py:49，平台自研子类）实现 ask/tell 异步调度：先产出实验批交 launcher 并行执行，再用 `update_sequence`（:102）回收 launch_training 返回的 objectives（MAE/RMSE）喂回 Optuna study 推进下一轮。搜索期普遍降档提速：train_samples 10 万、15 epoch、log_interval=-1、`~trainer.callbacks.save_checkpoint` 删存盘回调；best_N 快照升回 100 万样本 30 epoch 全量复训——搜索/复训两套预算全部编码在 overrides 文件里。

## 设计决策

四条决策值得咀嚼。①**optional@_global_ vs defaults 组嵌套**：组合配方不做组树而是全路径内联，牺牲"配方自动继承组默认值"，换来"任意组合覆盖任意子树叶子"的自由度——24 份 model_dataset 极薄（多份同构）、新增组合零代码。②**vendored 插件而非框架化**：四个插件原样拷贝上游（连 NEWS.md/tests 一起），平台只写 TSPPOptunaExperimentSequence 一个胶水类；代价是 torchrun 双拷贝漂移无人清理，且 Dockerfile:71 覆写 hydra 安装文件的侵入式 patch 把接口锁死在 hydra-core==1.1.1。③**PyYAML 双 merge key 的跨世代对照**（根因）：TSPP 自己不用 merge key，但同仓 Transformer-XL 的 wt103_large.yaml:35-36 同一 map 连写 `<<: *wt103` + `<<: *train`——YAML 1.1 对重复 merge key 属未定义行为，严格 core schema 解析器报重复键，而真实消费端 train.py:72 的 `yaml.load(f, Loader=yaml.FullLoader)` 按顺序覆盖语义正常加载（第一重冗余但无害）；"能跑但工具链报错"的**根因是 PyYAML 宽容实现与规范严格性的历史缝**，也正是 TSPP 改用 Hydra/OmegaConf 的动机——FastSpeech 的 parent_yaml（08 篇）是中间世代。④**override 语法统一表意**：`trainer/criterion: choice(L1,MSE)` 把"选哪个 criterion 组文件"本身变成搜索维度——配置组合学与超参搜索在同一套语法里统一。

## 新人提示

入手顺序：先读 train_config.yaml 十四行+conf_utils.py 的 resolver 注册表，再对照读 dcrnn_pems_bay.yaml（最薄配方）与 overrides/M5/nhits/hp_search.yaml（最厚搜索空间），最后跟 examples/hp_search.sh 走一遍 -m 多运行链路。四个坑：① 改 trainer/dataset/evaluator 的 yaml 键名必须 grep conf/overrides 与 conf/model_dataset 两处——全路径内联意味着配方文件直接引用你的内部路径，Hydra 不给结构性破坏报错；② torchrun 插件两份注册同名，调试 launcher 先确认 Dockerfile 装的是哪份（新拷贝），本地把 distributed_launcher 也装进包路径会出现"改码不生效"幽灵现象；③ `+` 前缀只在基座无该键时合法，写 overrides 想清楚是覆盖还是追加；④ 升级 hydra-core 后 Dockerfile:71 的 sweeper.py 覆写可能失效，sweep 行为异常先查这行 patch。搜索空间语法的权威定义在 vendored _impl.py:88-126 三条分支，文档不如源码准。
