<!--Copyright 2022 The HuggingFace Team. All rights reserved.

Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
the License. You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the

⚠️ Note that this file is in Markdown but contain specific syntax for our doc-builder (similar to MDX) that may not be
rendered properly in your Markdown viewer.

-->

# 使用Trainer API进行超参数搜索

🤗 Transformers库提供了一个优化过的[`Trainer`]类，用于训练🤗 Transformers模型，相比于手动编写自己的训练循环，这更容易开始训练。[`Trainer`]提供了超参数搜索的API。本文档展示了如何在示例中启用它。


## 超参数搜索后端

[`Trainer`] 目前支持四种超参数搜索后端：[optuna](https://optuna.org)，[raytune](https://docs.ray.io/en/latest/tune/index.html)，[wandb](https://wandb.ai/site/sweeps)

在使用它们之前，您应该先安装它们作为超参数搜索后端。

```bash
pip install optuna/wandb/ray[tune]
```

## 如何在示例中启用超参数搜索

定义超参数搜索空间，不同的后端需要不同的格式。

对于optuna，请参阅optuna [object_parameter](https://optuna.readthedocs.io/en/stable/tutorial/10_key_features/002_configurations.html#sphx-glr-tutorial-10-key-features-002-configurations-py)，它类似于以下内容：

```py
>>> def optuna_hp_space(trial):
...     return {
...         "learning_rate": trial.suggest_float("learning_rate", 1e-6, 1e-4, log=True),
...         "per_device_train_batch_size": trial.suggest_categorical("per_device_train_batch_size", [16, 32, 64, 128]),
...     }
```

Optuna提供了多目标HPO。您可以在`hyperparameter_search`中传递`direction`参数，并定义自己的`compute_objective`以返回多个目标值。在`hyperparameter_search`中将返回Pareto Front（`list[BestRun]`），您应该参考[test_trainer](https://github.com/huggingface/transformers/blob/main/tests/trainer/test_trainer.py)中的测试用例`TrainerHyperParameterMultiObjectOptunaIntegrationTest`。它类似于以下内容：

```py
>>> best_trials = trainer.hyperparameter_search(
...     direction=["minimize", "maximize"],
...     backend="optuna",
...     hp_space=optuna_hp_space,
...     n_trials=20,
...     compute_objective=compute_objective,
... )
```

对于raytune，可以参考raytune的[object_parameter](https://docs.ray.io/en/latest/tune/api/search_space.html)，它类似于以下内容：

```py
>>> def ray_hp_space(trial):
...     return {
...         "learning_rate": tune.loguniform(1e-6, 1e-4),
...         "per_device_train_batch_size": tune.choice([16, 32, 64, 128]),
...     }
```

对于wandb，可以参考wandb的[object_parameter](https://docs.wandb.ai/guides/sweeps/configuration)，它类似于以下内容：

```py
>>> def wandb_hp_space(trial):
...     return {
...         "method": "random",
...         "metric": {"name": "objective", "goal": "minimize"},
...         "parameters": {
...             "learning_rate": {"distribution": "uniform", "min": 1e-6, "max": 1e-4},
...             "per_device_train_batch_size": {"values": [16, 32, 64, 128]},
...         },
...     }
```

定义一个`model_init`函数并将其传递给[Trainer]，作为示例：

```py
>>> def model_init(trial):
...     return AutoModelForSequenceClassification.from_pretrained(
...         model_args.model_name_or_path,
...         config=config,
...         cache_dir=model_args.cache_dir,
...         revision=model_args.model_revision,
...     )
```

使用你的`model_init`函数、训练参数、训练和测试数据集以及评估函数创建一个[`Trainer`]。

```py
>>> trainer = Trainer(
...     model=None,
...     args=training_args,
...     train_dataset=small_train_dataset,
...     eval_dataset=small_eval_dataset,
...     compute_metrics=compute_metrics,
...     processing_class=tokenizer,
...     model_init=model_init,
...     data_collator=data_collator,
... )
```

调用超参数搜索，获取最佳试验参数，后端可以是`"optuna"`/`"wandb"`/`"ray"`。方向可以是`"minimize"`或`"maximize"`，表示是否优化更大或更低的目标。

您可以定义自己的compute_objective函数，如果没有定义，将调用默认的compute_objective，并将评估指标（如f1）之和作为目标值返回。

```py
>>> best_trial = trainer.hyperparameter_search(
...     direction="maximize",
...     backend="optuna",
...     hp_space=optuna_hp_space,
...     n_trials=20,
...     compute_objective=compute_objective,
... )
```

## 针对DDP微调的超参数搜索
目前，Optuna已启用针对DDP的超参数搜索。只有rank-zero进程会进行超参数搜索并将参数传递给其他进程。
