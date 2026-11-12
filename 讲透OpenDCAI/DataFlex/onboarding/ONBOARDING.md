# DataFlex ONBOARDING

图谱基线 commit d9625e4c（358 节点/916 边/16 层/15 步 tour），文中行号锚均从该基线源码核实。

## 1. 一句话定位

DataFlex 是以数据为中心的 LLM 训练框架：跑在 LLaMA-Factory 之上，在训练循环内动态调度数据——Selection（选样本）/Mixture（域配比）/Reweighting（样本加权）/Reordering（训练顺序）四族算法组件经 Registry 装配进五种动态训练器。NeurIPS 2026 Datasets & Benchmarks Track 录用（README.md:28）。与同 org 的 DataFlow（数据清洗）是姊妹项目但非同族抽象：DataFlow 用 OperatorABC 体系，DataFlex 只有 Selector/Mixer/Weighter/Reorder 四个 ABC 加 Registry 装饰器，不共享代码。

## 2. 心智模型

- **Registry**（core/registry.py:4-33）：`kind→name→class` 两级字典加全局单例；四个装饰器工厂 `@register_selector/mixer/weighter/reorder`（registry.py:30-33），模块 import 即注册——selector/__init__.py 等 barrel 的唯一使命就是触发副作用导入。`REGISTRY.build`（registry.py:20-27）合并 cfg 与 runtime 依赖（runtime 优先）再按 `__init__` 签名过滤喂参。
- **components.yaml**（configs/components.yaml）：五族 41 预设（selectors 15/mixers 5/weighters 7/reorders 10/pipelines 4）。训练 YAML 里 `component_name: less` 即从此查表；load_component.py:35-55 读桶、替换 `${var}` 占位符、回退废弃别名 `reorderers:`（load_component.py:10-12）。
- **hooks 三接缝**（train/hooks.py:15-39）：曾三次 vendor `Trainer._inner_training_loop`（每次 transformers 发版重 diff），如今只用三覆写拿「下一步吃什么、跑多少步、步内损失」：`get_batch_samples`（hooks.py:156，每优化器步调 `dataflex_next_indices` 换数据源）、`train()` 把步预算写进 `args.max_steps`（hooks.py:134-150，保 LR 调度诚实）、`compute_loss/training_step`（子类自覆写）。v4/v5 通用。
- **launcher monkey-patch**：入口在运行时把 LlamaFactory 的 hparams/get_dataset/CustomSeq2SeqTrainer 换成 DataFlex 版，按 train_type 六值分发。

## 3. 代码地图（16 层）

L1 门面（pyproject.toml、test.yml、双语 README）→ L2 core Registry → L3 utils 横切（logging、loss_utils 全仓唯一 per-sample loss 定义、selector_io）→ L4 Selector 15 实现 → L5 offline_selector 离线预选（near/tsds/presel/record 四件）→ L6 Mixer 5 → L7 Weighter 7 → L8 Reorder（patterns.py 七种纯函数排序模式）→ L9 数据层（loader.py:201 三条 get_dataset 路径、mixed_proportion_manager）→ L10 五 Trainer+hooks.py → L11 lego 组合（pipeline/stages/plan/scoreboard/context）→ L12 入口（cli.py+launcher.py）→ L13 LoRA 配方（train_lora/{selectors,mixers,weighters}/）→ L14 全参/分布式/合并/冒烟+components.yaml → L15 演示数据（dataset_info.json 114 条目）→ L16 skills 文档（how_to_use.md 25 节、how_to_add_algorithm.md 19 节）。

## 4. 核心链路走读：一次 dataflex-cli train 的旅程

1. cli.py:238 `main()` 分发 train/presel/version（pyproject.toml:37）；多卡时 cli.py:275-291 用 torchrun 以 launcher.py 为入口重派。
2. `read_args`（cli.py:206-216）OmegaConf 读 YAML 并合并 CLI 覆盖。
3. cli.py:41-48 换 FinetuningArguments/DataArguments 为扩展子类后 uncache 清缓存。
4. cli.py:50-101 按 train_type∈{static,dynamic_select/mix/weight/reorder/lego}（cli.py:58）选 Trainer，五点替换 sft/pt 两工作流符号（cli.py:80-99）。
5. dynamic_mix/reorder/lego 再 patch get_dataset（cli.py:255-260）；reorder 仅 static+apply_at=raw 真换（launcher.py:127-176），dynamic 分数来自当前模型必须走索引。
6. 组件装配：如 WeightTrainer（weight_trainer.py:38-53）load_component 查表、REGISTRY.build 注入 dataset/accelerator 等 runtime 依赖。
7. 每优化器步 hooks.py:156 `get_batch_samples`→`dataflex_next_indices`→selector.select()/mixer.mix()→`_dataflex_open_stage`（hooks.py:178-184）换 Stage 迭代器。刻意无视上游 epoch_iterator、复用 super() 的 num_items_in_batch 计数（防梯度累积缩放隐性 bug）。
8. SelectTrainer 三段调度「warmup 抽样→每 update_step 重选→阶段滚动」（select_trainer.py:92-190）；mixture 路径返回 WHOLE_DATASET 哨兵（hooks.py:49）整库换集而非收窄索引。

## 5. 运行与调试

- **环境**：Python>=3.11（pyproject.toml:13）；`pip install -e .`，LESS 另装 `[less]`（TRAK），DeepSpeed 用 `[deepspeed]` extra。CI 权威序列是 uv（test.yml:50-61）。
- **冒烟四件**：examples/test/{test_select,test_weight,test_mix,test_static_mix}.yaml，alpaca_en_demo+delta_loss 微调度，单卡几分钟跑通。
- **ZeRO**：examples/deepspeed/ 五档 z0/z2/z2+offload/z3/z3+双卸载；2026-03-17 起梯度计算支持 ZeRO-3，LESS/TRAK 系在 z3 下可用。
- **DoReMi 三步链**（how_to_use.md:286-303）：Step1 static 均匀训参考模型→Step2 dynamic doremi 学域权→Step3 static 用优化权重训终模（step3 yaml:54-58，train_type 仍 dynamic_mix、component_name: static）；三 YAML 的 ref_model 路径手工串。
- **离线预选**：`dataflex-cli presel`（cli.py:244）reference→extract→score→select 四阶段。

## 6. 已知坑（先读再跑）

1. **密钥明文泄露（应立即轮换）**：19 个 examples YAML 注释残留真实 swanlab_api_key（less.yaml:38 等），8 个残留 swanlab_lark_secret（doremi_step2_dynamic_qwen_pt_lora.yaml:44）——注释也被 git 历史固化，clone 者可读。
2. **multimodal_fullsft 引用未注册键**：multimodal_fullsft.yaml:13 `dataset: mmfinereason_sft`、:44 eval_dataset 同坑——dataset_info.json 只注册 *_demo 变体，原样跑必报数据集不存在。
3. **CI pytest 停用**：test.yml:81-84 pytest 步整体注释，只剩 version/import 冒烟，绿勾≠测试通过。
4. **尾注释复制残留**：cluster_less.yaml:74 运行命令误指 less.yaml。
5. **IDE 跳转失灵的阅读法**：cli/launcher 全延迟 import 且两文件近乎全量重复，静态分析追不到符号——按 launcher.py 单文件读逻辑，找定义用 `grep -rn "def patch_" src/`，YAML 字段查 how_to_use.md:47 起双层字段表。
6. **注释漂移**：YAML 注释写 train_type 可选 "static_full"，代码真值是 "static"（launcher.py:55）。

## 7. 上游与生态

- **llamafactory>=0.9.5 依赖底座**（requirements.txt:30）：数据加载/模板/训练循环/CLI 骨架全复用，DataFlex 只做数据策略层——升级 llamafactory 必回归冒烟。
- **reorder patterns 移植自 microsoft/data-efficacy**（七种排序模式工程化复刻）；record_presel_selector.py 是上游 PreSel（MIT）LLaVA 记录选择核心原样移植；LESS/TracIn/ICONS 共享 TRAK 投影基建（less_selector.py `_trak_projectors`）；adapt_weighter（ICLR2026）/loss_weighter（ICLR2025）为论文实现。
- **OpenDCAI org**：DataFlow=训练前清洗，DataFlex=训练中调度，互补两线；文档站 OpenDCAI.github.io/DataFlex-Doc，DeepWiki 已收录。

## 8. 学习路径

**15 步 tour=依赖序**：T1 门面→T2 Registry（全仓钥匙）→T3-T9 四族「契约→实现」（T3/T4 影响函数系、T5 多模态轻量信号、T6 离线预选、T7 Mixer、T8 Weighter、T9 Reorder）→T10 数据层→T11 hooks/Trainer→T12 lego→T13 入口→T14 配置→T15 数据/文档。读完 T13 才闭环「一次 train 的旅程」。

**explain 6 篇配读**：registry 篇配 T2，selector 族配 T3-T6，mixer/weighter 配 T7-T8，reorder 配 T9，hooks/trainer 配 T10-T11，launcher 配 T13——先 tour 拿骨架，再 explain 拿行号细节。

**上手序列（一个下午）**：①README+how_to_use.md 前 110 行（三命令+双层字段）；②跑 examples/test/test_select.yaml 验 import 链；③换 component_name: loss 再跑，体会换件即换算法；④精读 registry.py（34 行）+hooks.py docstring，两文件懂一半架构；⑤照 how_to_add_algorithm.md「注册装饰器→继承 ABC→实现 select()」三步写第一个自定义选择器。
