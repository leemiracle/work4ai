# 09 tuner 智能体调优：配置前端与 Trinity-RFT 桥

> **勘误（以源码为准）**：①顶层 `agentscope.tune` 已废弃且**不是软提示**——`tune/__init__.py:4` 直接 `raise ImportError` 指引改用 `agentscope.tuner`，import 即抛异常；②任务来源所述 "agent learning" 不是文件，是 `tuner/__init__.py:2` docstring 的措辞（"The learning module of AgentScope, including RL and SFT"）；实际文件为 `_tune/_config/_workflow/_judge/_dataset/_algorithm/_model` 七件。（锚相对 `src/agentscope/`）

## 1. 角色定位

tuner 是 agent 学习（RL/SFT）的**配置前端**而非训练引擎：`tune()` 做三件事——校验用户函数签名、把 Python 参数翻译成 Trinity-RFT 配置、拉起训练。真正的采样/奖励/优化循环全部在外部 Trinity-RFT 里。这决定了包形态：七文件全是 pydantic 配置类加一个入口函数，零训练代码。

## 2. 内部结构

**入口**：`tune()`（`tuner/_tune.py:16`）全 keyword-only 参数（workflow/judge/模型/数据集/算法/监控）。Trinity 懒导入，缺失时报带安装指引的 ImportError（`tuner/_tune.py:65`）；随后校验 workflow/judge 函数签名（`tuner/_tune.py:70`），`_to_trinity_config` 翻译配置，最终 `run_stage` 拉起（`tuner/_tune.py:91`）；环境变量 `USE_ALIYUN_PAI_DLC` 可切阿里云 PAI 的 ray 集群（`tuner/_tune.py:87`）。

**翻译核心**：`_to_trinity_config`（`tuner/_config.py:20`）把 agentscope 概念逐一映射：workflow 函数注册名为 `agentscope_workflow_adapter_v1`（`tuner/_config.py:53`），**函数对象本身**经 `workflow_args` 塞进 Trinity 的 taskset 配置（`tuner/_config.py:72`）；`AlgorithmConfig` 五键映射到 Trinity 的 optimizer/buffer/trainer/explorer（`tuner/_config.py:114`）。

**契约类型**：`WorkflowOutput`（`tuner/_workflow.py:9`）三通道 reward/response/metrics——reward 直填或 response 交给 judge；`WorkflowType` 签名 `(task, model, auxiliary_models, logger)`（`tuner/_workflow.py:33`）。`JudgeOutput`（`tuner/_judge.py:9`）= reward+metrics，`JudgeType` 收 `(task, response, ...)`（`tuner/_judge.py:22`）。签名校验按**参数名**做鸭子检查：workflow 必须有 task/model（`tuner/_config.py:192`），judge 必须有 task/response，且禁 `*args`/`**kwargs`（`tuner/_config.py:241`）。

**模型侧**：`TunerModelConfig`（`tuner/_model.py:8`）是 vLLM 推理引擎视角的配置（tool_call_parser 默认 hermes、Qwen3 预设）；`TinkerConfig`（`tuner/_model.py:96`）描述 LoRA 服务化训练（rank/train_mlp/train_unembed）。`DatasetConfig` 兼容 HF datasets 格式并带 streaming preview 抽查。

## 3. 外部连接

唯一重依赖是 pip 包 trinity-rft（`run_stage`/`setup_ray_cluster`）；监控后端 tensorboard/wandb/mlflow/swanlab 四选一由 Trinity 承接。`ChatModelBase` 类型从 model 子包借入（workflow/judge 的模型注解）；examples/tuner/react_agent 提供带 reward 曲线的端到端样例。与 ReActAgent 的关系是间接的：workflow 函数内部通常包一个 agent，但 tuner 只认函数边界。

## 4. 数据流

用户视角的单环：写 `workflow_func(task, model, auxiliary_models, logger)` → 内部跑 agent 逻辑 → 返回 `WorkflowOutput`。若有 `judge_func`，response 进入 judge 得 `JudgeOutput.reward`；否则直接用 workflow 自报 reward。Trinity 按 `group_size` 并发采样同 task 的多条 rollout，组内奖励归一化后由 multi_step_grpo 更新 `model_path` 指向的权重；vLLM rollout 引擎与训练器在同一 config 内协同（explorer/rollout_model 字段）。

## 5. 设计决策

①**纯前端设计**：训练复杂度整体外置，agentscope 只保契约稳定——Trinity 升级不传染本包 API。②**函数即配置**：workflow/judge 以函数对象穿透 config 传递，依赖 ray 同进程对象传输，换取零样板代码。③**按参数名校验而非继承**：不强制基类，`inspect.signature` 白名单检查，容错默认参数、拒变长参数。④**双奖励通道**：reward 直填与 LLM-as-judge 二选一，覆盖"环境可评分"与"只能模型评"两类任务。

## 6. 新人提示

- 坑 1：`agentscope.tune` 的废弃是**硬失败**（`tune/__init__.py:4` raise ImportError），老代码迁移没有任何兼容层。
- 坑 2：trinity-rft **不在 pyproject 任何 extra 里**（全文件 grep 零命中）——装齐 agentscope 全家桶也跑不了 tune，须手动 `pip install trinity-rft`，运行期才在 `tuner/_tune.py:65` 报错。
- 坑 3：workflow/judge 函数参数必须**按名**命名 task/model（或 task/response），位置参数风格直接 ValueError；auxiliary_models/logger 可省。
- 坑 4：auxiliary_models 只当环境/裁判，**不参与训练**（`tuner/_workflow.py:48` docstring 明示），别指望它被微调。
- 坑 5：默认算法 multi_step_grpo 学习率 1e-6，对 agent 场景是保守值，调参从 group_size 入手更有效。
