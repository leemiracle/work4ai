# 10 · trainer 训练系统：TrainingArguments、回调体系与优化器工厂

## ① 角色定位

训练体系由三根柱子撑起：`src/transformers/trainer.py`（4642 行，Trainer 巨类 L261 起）、`src/transformers/training_args.py`（2920 行，TrainingArguments 数据类 L180 起）与 `src/transformers/trainer_callback.py`（回调九件套）。Trainer 的自我定位是"单进程/分布式通吃的训练循环托管"：dataloader 组装、优化器与调度器工厂、accelerate/DeepSpeed/FSDP 集成、评估与 checkpoint 全部内包，子类只覆写钩子。`trainer_seq2seq.py`（392 行）是最薄的一层示范——生成式任务如何以最小侵入扩展 Trainer。

## ② 内部结构

**TrainingArguments** 是一个 112 个 `field()` 的巨型 dataclass，按域分节：批大小/梯度累积、优化器（OptimizerNames 显式枚举 L113 起）、调度器、混合精度、分布式（deepspeed/fsdp/tp）、日志、保存与 hub 推送，`__post_init__` 做交叉校验。ParallelMode 枚举单独放在文件尾部（L2899）——文件内部也有层次。**Trainer** 的工厂方法群：`create_optimizer_and_scheduler`（L1235）编排两步，`create_optimizer`（L1246）内聚优化器构建，L1354 经 `from .optimization import GreedyLR, get_scheduler`（trainer.py:82）拿调度器——GreedyLR（optimization.py:621）是按训练表现自适应调学习率的新调度器（arXiv 2512.14527），静态工厂 `get_optimizer_cls_and_kwargs`（L1365）负责把 `--optim` 字符串解析成 (类, kwargs) 二元组。**回调体系**（trainer_callback.py）自底向上：TrainerState 训练状态快照（L35）→ TrainerControl 控制流（L234，should_training_stop）→ TrainerCallback 抽象基类（L295，16 个事件钩子）→ CallbackHandler 分发器（L429）→ 四个内置实现：DefaultFlowCallback 流控（L563）、ProgressCallback 进度条（L624）、PrinterCallback 打印（L698）、EarlyStoppingCallback 早停（L711）。TrainerState/TrainerControl/EarlyStoppingCallback 还实现 ExportableState（L189）——断点恢复时状态可序列化导出。

## ③ 外部连接

Trainer 向上接 datasets/DataCollator，向下经 integrations 接 accelerate（.integrations.accelerate）与 DeepSpeed（HfDeepSpeedConfig 全家，integrations/deepspeed.py）；hyperparameter_search.py 挂 optuna/ray。**Seq2SeqTrainer 的 TYPE_CHECKING 块是"重运行时轻依赖"的范本**：trainer_seq2seq.py:38-48 恰好 9 条静态 import——IterableDataset/DataCollator/FeatureExtractionMixin/BaseImageProcessor/PreTrainedModel/ProcessorMixin/PreTrainedTokenizerBase/TrainerCallback/EvalPrediction 与 PredictionOutput——全部只服务类型注解，运行时零导入成本；真正的运行时依赖只有 torch、Trainer 本体与 fsdp/deepspeed 两个条件导入（L25-28,32-36）。

## ④ 数据流

`train()` 一轮：回调 on_train_begin → dataloader 取批 → model(**inputs) 算 loss →（梯度累积边界内）accelerator.backward → optimizer.step/scheduler.step → 回调 on_step_end（EarlyStopping 在此查 metrics 决定 control.should_training_stop）→ 周期性 evaluate → on_save/on_log → 结束 on_train_end。优化器链路是惰性两段式：Trainer.__init__ 不建优化器，首次进入训练循环才 `create_optimizer_and_scheduler`（子类可整段覆写或只覆写 create_optimizer——L686,708 的报错信息明确指出这两条覆写路径）。生成式评估的分叉在 Seq2SeqTrainer.prediction_step（L259）：`predict_with_generate` 为真且非 loss_only（L290）时，labels 生成 decoder_input_ids 后被逐出（L311 注释："evict the former, so that the model can freely generate"），`generated_tokens = self.model.generate(**generation_inputs, **gen_kwargs)`（L329）接管，再走统一 metrics。

## ⑤ 设计决策与勘误

- **TrainingArguments 独立成文件**（不在 trainer.py 里）不是审美问题：2920 行 dataclass 与 4642 行循环解耦后，Trainer 子类化与参数序列化（TrainingArguments 可直接 to_dict 进 trainer_state.json）互不拖累。
- **勘误一**：网传"trainer_seq2seq 大量 import 各模态处理类"——运行时并不导入，那 9 条全在 TYPE_CHECKING 下（L38-48），装 transformers 不装 torchvision 也能跑文本 Seq2Seq。
- **勘误二**："Seq2SeqTrainer 重写 evaluate"不准确——它重的是 prediction_step 这个原子操作，evaluate/循环全部继承复用；generate 的 max_length/num_beams 等 kwargs 经 `gen_kwargs`（docstring L166-171）在构造期声明。
- **优化器工厂是静态方法**（L1365 挂 @staticmethod 语义）：无 self，纯 (args, model)→(cls, kwargs) 函数，第三方（如 TRL）可以脱离 Trainer 实例直接复用——这是被低估的公共 API。
- 回调无优先级队列：CallbackHandler 按注册顺序同步遍历，EarlyStopping 的 stop 信号要等本轮全部回调跑完才生效，写回调别假设短路语义。

## ⑥ 新人提示

排训练问题先看 TrainerState（日志里可打印的 ground truth）再看代码。自定义训练行为优先级：传 optimizers 参数 → 覆写 create_optimizer → 覆写 compute_loss → 最后才覆写 training_step；越往右回归风险越大。写自定义回调继承 TrainerCallback 时，所有钩子签名都有 args/state/control/model 四件套，**必须**透传 control 才能不破坏其他回调的停止信号。迁移旧代码注意 OptimizerNames 枚举在持续扩容（adamw_torch_fused 系/galore 系等），字符串硬编码会漂移。
