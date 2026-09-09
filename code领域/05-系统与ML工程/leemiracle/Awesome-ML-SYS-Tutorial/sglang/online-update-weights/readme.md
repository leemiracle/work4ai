# Online Update Weights

如 [code-walk-through](../code-walk-through/readme.md) 所述，为了实现 SGLang 和 OpenRLHF 的集成，
我们需要在 SGLang 中添加一个 `online_update_weights` 的接口，区别于先前的 `update_weights`。先前的 `update_weights` 是从磁盘上读新的权重，而 `online_update_weights` 是从训练 engine 中直接通过 nccl 广播新的权重。

## 现有的 `update_weights`

要在现在每个有 `update_weights` 的地方添加同样的 `online_update_weights` 的接口。所以这里读取几个重要的 `update_weights` 接口。

### `ModelRunner`

`update_weights` in `sglang/srt/model_excutor/model_runner.py`，这个函数如下：

<details>
<summary>Code</summary>

```python
    def update_weights(self, model_path: str, load_format: str):
        """Update weights in-place."""
        from vllm.model_executor.model_loader.loader import (
            DefaultModelLoader,
            device_loading_context,
            get_model_loader,
        )
        from vllm.model_executor.model_loader.utils import set_default_torch_dtype

        logger.info(
            f"Update weights begin. "
            f"avail mem={get_available_gpu_memory(self.device, self.gpu_id):.2f} GB"
        )

        target_device = torch.device(self.device)

        try:
            # TODO: Use a better method to check this
            vllm_model_config = VllmModelConfig(
                model=model_path,
                quantization=self.server_args.quantization,
                tokenizer=None,
                tokenizer_mode=None,
                trust_remote_code=self.server_args.trust_remote_code,
                dtype=self.server_args.dtype,
                seed=self.server_args.random_seed,
                skip_tokenizer_init=True,
            )
        except Exception as e:
            message = f"Failed to load model config: {e}."
            return False, message

        load_config = LoadConfig(load_format=load_format)

        # Only support vllm DefaultModelLoader for now
        loader = get_model_loader(load_config)
        if not isinstance(loader, DefaultModelLoader):
            message = f"Failed to get model loader: {loader}."
            return False, message

        def get_weight_iter(config):
            iter = loader._get_weights_iterator(
                DefaultModelLoader.Source(
                    config.model,
                    revision=config.revision,
                    fall_back_to_pt=getattr(
                        self.model, "fall_back_to_pt_during_load", True
                    ),
                )
            )
            return iter

        def model_load_weights(model, iter):
            model.load_weights(iter)
            for _, module in self.model.named_modules():
                quant_method = getattr(module, "quant_method", None)
                if quant_method is not None:
                    with device_loading_context(module, target_device):
                        quant_method.process_weights_after_loading(module)
            return model

        with set_default_torch_dtype(vllm_model_config.dtype):
            try:
                iter = get_weight_iter(vllm_model_config)
            except Exception as e:
                message = f"Failed to get weights iterator: {e}."
                return False, message
            try:
                model = model_load_weights(self.model, iter)
            except Exception as e:
                message = (
                    f"Failed to update weights: {e}.\nRolling back to original weights."
                )
                del iter
                gc.collect()
                iter = get_weight_iter(self.vllm_model_config)
                self.model = model_load_weights(self.model, iter)
                return False, message

        self.model = model
        self.server_args.model_path = model_path
        self.server_args.load_format = load_format
        self.vllm_model_config = vllm_model_config
        self.load_config = load_config
        self.model_config.path = model_path

        logger.info("Update weights end.")
        return True, "Succeeded to update model weights."
```
</details>

其实就做了两件事情：

- **权重加载**：使用 vllm 的 `DefaultModelLoader` 从指定的 `model_path` 加载新的模型权重

- **配置更新**：更新相关的模型配置信息，包括 `server_args`、`model_config`

1. 创建 `VllmModelConfig` 配置
2. 获取 `ModelLoader`
3. 通过 `get_weight_iter` 获取权重迭代器
4. 使用 `model_load_weights` 加载权重
5. 更新相关配置

### `TpModelWorker`

其实 `TpModelWorker` 的 `update_weights` 代表了很大一类的 `update_weights` 接口，就是层层往下调用，直到 `ModelRunner` 的 `update_weights`。值得一提的是，在 [code-walk-through](../code-walk-through/readme.md#tpmodelworker) 中，我们就提到过 SGLang 的 `TpModelWorker` 和 `ModelRunner` 共同负责了 vllm 的 `Worker` 功能。也即：

- `TpModelWorker`：负责初始化模型和分布式环境、管理内存池、执行模型的前向传播、分类处理 embedding 和生成任务。
- `ModelRunner`：负责实际上执行模型推理，并提供接口给 `TpModelWorker` 调用。

所以，OpenRLHF 在 vllm 的 `Worker` 基础上，添加两个有关 `update_weights` 的接口：

<details>
<summary>Code</summary>

```python
import importlib
import inspect

import torch
from vllm.worker.worker import Worker

from openrlhf.utils.distributed_util import init_process_group
from openrlhf.utils.logging_utils import init_logger

logger = init_logger(__name__)


class WorkerWrap(Worker):
    def init_process_group(self, master_address, master_port, rank_offset, world_size, group_name, backend="nccl"):
        """Init torch process group for model weights update"""
        assert torch.distributed.is_initialized(), f"default torch process group must be initialized"
        assert group_name != "", f"group name must not be empty"

        rank = torch.distributed.get_rank() + rank_offset
        self._model_update_group = init_process_group(
            backend=backend,
            init_method=f"tcp://{master_address}:{master_port}",
            world_size=world_size,
            rank=rank,
            group_name=group_name,
        )
        print(
            f"init_process_group: master_address={master_address}, master_port={master_port}, ",
            f"rank={rank}, world_size={world_size}, group_name={group_name}",
        )

    def update_weight(self, name, dtype, shape, empty_cache=False):
        """Broadcast weight to all vllm workers from source rank 0 (actor model)"""
        if torch.distributed.get_rank() == 0:
            print(f"update weight: {name}, dtype: {dtype}, shape: {shape}")

        assert dtype == self.model_config.dtype, f"mismatch dtype: src {dtype}, dst {self.model_config.dtype}"
        weight = torch.empty(shape, dtype=dtype, device="cuda")
        torch.distributed.broadcast(weight, 0, group=self._model_update_group)

        self.model_runner.model.load_weights(weights=[(name, weight)])

        del weight
        # TODO: should we empty cache if all weights have updated?
        # if empty_cache:
        #     torch.cuda.empty_cache()`
```

对应也需要在 `ModelRunner` 中添加 `online_update_weights`。

</details>

### `Runtime`

具体是指 `sglang/srt/server.py` 中的 `Runtime` 类，这里直接 link 到之前的解析 [../code-walk-through/readme.md](../code-walk-through/readme.md#runtime) 中的 `Runtime` 部分。


这里捋清楚 `app` 的 `update_weights` 请求会层层向下，先发给 `TokenizerManager`，然后向下调用实际的 `ModelRunner` 的 `update_weights`。

