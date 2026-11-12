# 11 · TSPP 平台核心：launch_training 三态分派、trainer 三层与数据工厂

## 角色定位

`Tools/PyTorch/TimeSeriesPredictionPlatform/`（TSPP）是本仓唯一"平台级"框架：不是单模型示例，而是把时序预测做成了**可插拔模型×数据集×训练范式的矩阵**——14 个模型（TFT/LSTM/NBeats/NHiTS/DeepAR 两代/DCRNN/MTGNN/GNN/统计模型/XGBoost/集成/可解释/平凡模型）、四大数据集（electricity/traffic/M5/pems_bay）、三种训练范式（深度学习 CTL/统计 Stat/梯度提升 XGB）经 Hydra 配置联邦自由组合。核心四件：`launch_training.py`（139 行总入口）、`training/`（trainer 三层）、`criterion.py`（损失家族）、`data/`（数据集工厂与下载脚本）。谱系上它继承 Google Research TFT 的预处理代码（data_utils.py 与 script_download_data.py 头部保留 Google Apache-2.0 双版权声明），NVIDIA 在其上长出整个平台。

## 内部结构

**入口的三态字符串分支**是全平台的调度枢纽：launch_training.py:32 `@hydra.main(config_path="conf", config_name="train_config")` 挂载，:34 `trainer_type = config.trainer._target_` 取 trainer 的实例化目标字符串，随后不做任何 import 检查、直接 `if 'CTLTrainer' in trainer_type`（:44）/`elif 'XGBTrainer'`（:96）/`elif "StatTrainer"`（:115）三段分派，落空抛 AttributeError（:135）。三态前的公共装配五行：`set_seed`（:36）→ `model = hydra.utils.instantiate(config.model)`（:37）→ `train, valid, test = hydra.utils.call(config.dataset)`（:39）→ evaluator instantiate（:40）→ `logger = hydra.utils.call(config.logger)`（:41）。**模型层零静态消费**：launch_training.py 全文无一行 import models——conf/model/tft.yaml 的 `_target_: models.tft.InterpretableTFT` 经 instantiate 按字符串定位类，模型清单增删只动 conf 目录。

**trainer 三层**（training/trainer.py）：`Trainer(ABC)`（:42）只约定 `train()` 模板方法；`CTLTrainer`（:47，深度线核心）装配 callbacks 容器、world_size/local_rank 环境读取（:68-69）、train/valid sampler、AMP 开关，`train()`（:190）是 callbacks 钩子环绕的 epoch 循环——`optimizer.zero_grad()`→`prep_data`→`model(batch)`→`criterion(preds, labels, weights=weights)`→`losses.sum()`→amp.scale_loss 或裸 backward（:203-210）→gradient_norm 裁剪；`StatTrainer`（:266）没有优化器循环，`train()` 直接返回预测字典（统计模型拟合即推理）；`XGBTrainer`（:327）把 valid_dataset 交给 xgboost 早停。外围 training/ 还有三件：checkpoint_utils.py 的 `maybe_restore_checkpoint`（:51）/`maybe_continue_run`（:128）断点续跑（内含 `detect_duplicated_run`（:92）防 optuna 并行作业互踩、:150-153 atexit 钩子注销重注册）；ema.py:41 `ModelEmaV2` 权重滑动平均；utils.py:50 `get_optimization_objectives` 把评测指标折成 optuna 单/多目标返回值。

## 外部连接

**criterion 家族**（criterion.py）四类：`TSPP_criterion_wrapper`（:21）统一各损失的 forward 签名——按 `criterion.forward.__code__.co_varnames`（:26）运行时内省参数集自动匹配；课程学习双参 `cl_start_horizon/cl_update` 必须同时置空或同时设置（:31 assert），渐进扩展预测地平线。三个具体损失：`QuantileLoss`（:71，pinball 分位数）、`GaussianLogLikelihood`（:86，均值+方差的概率预测）、`TweedieLoss`（:104，p=1.1 零膨胀计数目标）。**数据集工厂**（data/datasets.py，920 行全平台最大文件）：`DatasetFactory`（:139）按 (type/layout/entity/target) **四维枚举键**注册——DatasetType（:69，DL/STAT/XGB）×布局×实体结构×目标任务，`register` 装饰器（:143）+`construct_dataset`（:160）查表构造（configuration_args 逐个从 config 抽值，required 缺失即抛），顶层入口 `create_datasets`（:825）产出 train/valid/test 三件套，`get_collate_fn`（:867）按模型类型选 collate（TFT 张量/DGL 图/多目标变体）。数据管线前段在 data_utils.py：DataTypes/InputTypes/FeatureSpec 三件套特征规格 + Log1pScaler/CompositeScaler 缩放器 + `Preprocessor` 17 方法（切分/类别映射/填补/划分）。

## 数据流

冷启动数据流：`script_download_data.py --dataset electricity` → `main`（:528）从 `DOWNLOAD_FUNCTIONS` 分发表（:539，字典定义在 :551）取下载器。四条下载线各有专属清洗逻辑：electricity（:110）从 UCI 拉电负荷重采样小时级、截取 2014-01-01~09-08 学术对齐区间并派生 hour/day_of_week 特征；traffic（:175）解析 PEMS 自定义文本格式、randperm 逆置乱还原传感器-日顺序；download_m5（:338）按 28 天评测窗拼接 melt 长表 join 日历售价、缺售价填 -1 且权重置零（对齐 M5 竞赛指南语义）；download_PEMS_BAY（:408）按站点提示推断表头、过滤湾区 325 传感器、前向插值，并按经纬度高斯核 exp(-d²) 0.8 阈值截断建 DGL 图 pickle 为 graph.bin 供 DCRNN/MTGNN 消费。训练数据流：launch_training 的 CTL 分支先 `init_parallel()`/`init_distributed()`（:45-46，distributed_utils.py:114/:139，torchrun 环境变量驱动），训练后主进程 `torch.load("best_checkpoint.zip")`（:74）载最优权重复跑 evaluator.predict→unpack_predictions→evaluate（:75-79），最后为 joblib 并行残留做五连清理（:87-93 del+gc.collect+empty_cache+ipc_collect——注释自述 joblib loky 后端复用进程阻碍 PyTorch 自清理）。异常面：CUDNN_STATUS_NOT_INITIALIZED 打印 "This happens sometimes. IDK why. Sorry..."（:60-63）、CUDA OOM 打印 Job 号后优雅退出（:65-70）——两条都是"多作业 sweep 场景下一个作业死不能拖垮整个 optuna sweep"的防御。

## 设计决策

四个决策值得咀嚼。①**字符串子串匹配做分派**（`'CTLTrainer' in trainer_type`）而非 isinstance/多态：因为 trainer 是 Hydra instantiate 的产物、且子类配置（如 CTLTrainer 的派生 yaml）会改 `_target_` 全名字符串——子串匹配天然兼容目标名的命名空间变化，代价是拼错类名会静默落进 AttributeError 分支。②**四维数据集工厂**用注册表而非继承树分派：DL/STAT/XGB 三线对"数据集"的语义差（张量窗口/统计特征化/展平特征矩阵）太大，四维正交键让 10 余种 TSBaseDataset 变体各占一格，新增布局不动旧代码。③**同名类双定义的真实源码事实**（datasets.py:338 与 :602 两个 `TSMemoryMappedDataset`，前者继承 TSDataset 属 DL 线、后者继承 StatDataset 属统计线）：Python 模块属性只留 :602 版本，但两个 @DatasetFactory.register 在定义时已各自完成注册——调用方经工厂拿到的是各自注册版本，直接 import 类名只能拿统计线版本。这是"注册器模式 vs import 语义"分叉的活教材。④**criterion 用 co_varnames 内省统一签名**：不要求各损失继承基类，而是运行时读函数对象的参数名集合自动喂参——松耦合到极致，但 IDE 完全失去静态检查。

## 新人提示

入手顺序：先读 conf/train_config.yaml 与 12 篇（配置联邦）再看 launch_training.py:33-44 这十行——理解 `_target_` 字符串如何同时驱动模型/数据/评估/训练器四类实例化；然后 training/trainer.py 的 CTLTrainer.train() 循环；最后 datasets.py 的 DatasetFactory.register 装饰器。三个坑：① 改 trainer 类名（哪怕只是重命名）会同时破坏三态字符串分派与全部 conf/trainer/*.yaml 的 _target_——必须 grep 双侧；② 引用 TSMemoryMappedDataset 类时先想清楚要哪条线，直接 import 拿到的是 :602 统计线版本，DL 线版本只能经工厂四维键取；③ 断点续跑/重复运行检测依赖 checkpoint_utils 的 run 目录探测，optuna 并行 sweep 时 job 的工作目录由 Hydra 自动编号，手工重跑旧作业要先清 outputs/ 或靠 detect_duplicated_run 的警告判断。数据侧 script_download_data 与仓内模块零耦合（import 全是外部包），可独立拷走复用。
