# explain-06 · 联邦学习用例全景：examples 与 job_templates

## 一、角色定位

如果说 `nvflare/` 包是引擎，那么 `examples/` 与 `job_templates/` 就是 NVFlare 面向用户的整个驾驶舱。NVFlare 自我定位是"domain-agnostic 的联邦学习 SDK，支持横向与纵向 FL、内置 FedAvg/FedProx/FedOpt/Scaffold/Ditto，以及差分隐私、同态加密、PSI"（`CLAUDE.md:7`、`CLAUDE.md:9`），全部在这两个目录兑现为可运行代码。`examples/` 按 hello-world → advanced → devops → tutorials 分层，是**教学与算法演示**层；`job_templates/` 是 28 个**配置模板**，供 `nvflare job create` 复制改造，是生产入口。

任务书提到 hello-world 下有 hello_ml/hello_shap，实际不存在——现有 15 个示例覆盖框架广度（pt/numpy/tf/jax/lightning/huggingface/flower 等）而非 ML 任务广度。

## 二、内部结构

**hello-world 层**：每个示例一个 `job.py + client.py + README` 最小闭环。hello-pt 是范式样板：`job.py` 用 25 行构造 `FedAvgRecipe`（`examples/hello-world/hello-pt/job.py:56`），模型可传实例也可传 `class_path` 字典（`job.py:61-62` 注释），`add_final_global_evaluation` 保证最终模型必被验证（`job.py:70`）。`client.py` 是 Client API 完整教学：`flare.init()`（`client.py:107`）→ `while flare.is_running()` 里 `flare.receive()` 收全局模型（`client.py:135-137`）→ 本地训练 → `flare.send(FLModel(...))` 回传（`client.py:205`）；`is_submit_model`/`is_evaluate` 分支演示 cross-site evaluation 语义（`client.py:143`、`client.py:159`）。

**advanced 层**（40+ 用例域）按算法主题聚类：

- **cifar10**：经典横向 FL 基准，pt 侧有五算法变体。`cifar10-sim/cifar10_fedavg/job.py` 用 Dirichlet `--alpha` 控制数据异构度（`job.py:44-49`），`aggregator_data_kind=DataKind.WEIGHT_DIFF` 走增量聚合（`job.py:84`）；`cifar10-real-world/` 则走 secure provisioning 生产路径。
- **federated-statistics**：不训练模型只算统计。`df_stats/job.py` 声明式配置 count/mean/histogram/quantile（`job.py:38-45`），交给 `FedStatsRecipe`（`job.py:18`），并带 `min_noise_level/max_noise_level` 噪声保护（`job.py:57-59`）。
- **LLM/生医用例**：medgemma 是联邦 LoRA 微调集大成者——每 site 可指定不同 LoRA rank（`examples/advanced/medgemma/job.py:108-115`），naive 与 HLoRA 两种自定义聚合器可选（`job.py:274-278`）。bionemo/evo2 基因大模型同样走 `FedAvgRecipe`（`examples/advanced/bionemo/evo2/job.py:377`）；qwen3-vl 在 `--lora` 时只交换 adapter 权重（`examples/advanced/qwen3-vl/job.py:196`）。
- **纵向联邦一线**（详见 explain-09）：横向 `XGBHorizontalRecipe`（`examples/advanced/xgboost/fedxgb/job.py:86`）、纵向需先跑 PSI 对齐样本再训练（`fedxgb/job_vertical.py:53-54` 两步制）；cifar10-splitnn 用 `CollabRecipe` 把 server/client Python 对象直接打包成 job（`examples/advanced/vertical_federated_learning/cifar10-splitnn/job.py:66`）。
- **job_api**：FedJob API 裸用法对照。`job_api/pt/fedavg_script_runner_cifar10.py` 手工装配：controller `job.to(controller, "server")`（`:38`）、`PTModel(Net())` 初始模型（`:42`）、每 client 一个 `ScriptRunner`（`:48-53`）、`simulator_run` 直跑（`:56`）。

**job_templates 层**：28 个模板各含四件套 `config_fed_client.conf`/`config_fed_server.conf`/`meta.conf`/`info.md`（`job_templates/readme.md:9-13`），HOCON 允许注释省引号（`readme.md:20`）。以 fedopt_pt 为例：`meta.conf` 声明 `min_clients = 2` 与 `deploy_map` 全站分发（`job_templates/fedopt_pt/meta.conf:4-5`）；server 侧 `workflows` 数组挂 FedOpt controller，连 optimizer/lr_scheduler 都用 class path 配置（`fedopt_pt/config_fed_server.conf:19-22`），`PTFileModelPersistor` 负责模型落盘（`config_fed_server.conf:55-56`）；client 侧 `ClientAPIExecutor` 声明处理 train/validate/submit_model 三种任务、`params_transfer_type: DIFF` 增量传输（`fedopt_pt/config_fed_client.conf:13`、`:18`）。模板覆盖 fedopt/sag/cyclic/swarm 四类控制流 × pt/tf/np/sklearn/gnn/nemo 后端，外加 psi_csv、vertical_xgb 等专用模板。

## 三、外部连接

examples 是核心 API 的最大消费者：`nvflare.recipe` 包导出 `SimEnv/PocEnv/ProdEnv/FedAvgRecipe/set_per_site_config` 等（`nvflare/recipe/__init__.py:17-27`），同一 `recipe.execute(env)` 从仿真切到生产只换 env——medgemma `job.py:312-317` 的 SimEnv 多线程+GPU 配置即为例证。job_templates 被 `nvflare job` CLI 消费：`list-templates` 命令（`nvflare/tool/job/job_cli.py:83`）、`build_job_template_indices` 索引全部模板（`job_cli.py:155`）。hello-collab/splitnn 一线还依赖 `nvflare.collab.CollabRecipe` 新 API。

## 四、数据流

标准生命周期：**job.py（Recipe 或 FedJob）→ export → job 目录（meta + config 三件套 + 自定义代码）→ simulator 或 provision 到生产**。以 hello-pt 为例：`recipe.execute(SimEnv)` 本地起 server+clients 仿真，server 端 persistor 初始化模型并广播，client 端 `ClientAPIExecutor` 拉起 `client.py`，模型经 FLModel 在 `flare.receive()/flare.send()` 间往返（`hello-pt/client.py:137-205`），训练指标经 SummaryWriter 上报（`client.py:183`）。`--export` 可只导出 job 目录不运行（`hello-pt/job.py:26-29`），导出结构与模板一致，可直接 `nvflare job submit`——**Recipe 是生成器，模板是生成结果的静态样本**。

## 五、设计决策

1. **三代接口并存是负债也是资产**。config 三件套（模板代）→ FedJob API（job_config 代）→ Recipe API（当前代）同时在 examples 里活着。Recipe 明显在收敛，仅 job_api/ 保留 FedJob 裸用法作对照；但 CLI 工作流仍依赖模板，用户要学两套心智模型。
2. **client.py 用"侵入式 API + 原生训练循环"而非回调**。训练代码保留纯 PyTorch 写法，只在上报点插 `flare.receive/send`（`hello-pt/client.py:135`），学习成本最低，但任务分支漏写即挂——`client.py:143-148` 对 submit-before-train 的防御性报错说明这是已知坑。
3. **模板用 class path 字符串配置一切**（连 optimizer 都是 `"torch.optim.SGD"`，`fedopt_pt/config_fed_server.conf:29`），换来零代码改配置的灵活，代价是配置错误只在运行时爆炸。
4. **用例按框架维度而非行业维度组织**。medgemma/qwen3-vl/bionemo 共同点是 LoRA/QLoRA + FedAvg——LLM 时代 NVFlare 的主打卖点实为"参数高效微调使联邦可行"（可交换参数量骤减）。

## 六、新人提示

- 入门顺序：hello-pt → hello-numpy → cifar10-sim（异构数据）→ job_api（理解 config 生成原理）→ `nvflare job list-templates` 后挑模板改造。
- 读示例先读 `job.py` 再读 `client.py`：前者定义拓扑，后者定义本地计算，两者之间只有 FLModel 契约。
- 改聚合算法看 medgemma 的 `custom_aggregators.py`——自定义 aggregator 经 Recipe 的 `aggregator=` 注入（`medgemma/job.py:274`），是官方示范扩展点。
- main 分支的 requirements.txt 会钉住"下一个未发布版本"（`AGENTS.md:19-21`），示例装不上依赖先查 pin 是否超前于 PyPI。
- cifar10-real-world 与 cifar10-sim 共享 client 代码但部署路径完全不同：sim 用 SimEnv，real-world 需 provision 出的 secure project。
