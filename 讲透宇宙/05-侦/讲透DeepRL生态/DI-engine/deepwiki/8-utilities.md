> 来源: [https://deepwiki.com/opendilab/DI-engine/8-utilities](https://deepwiki.com/opendilab/DI-engine/8-utilities)
> DeepWiki opendilab/DI-engine | Last indexed: 20 April 2025 (c290a6

# Utilities

  Relevant source files 
 - [ding/torch_utils/__init__.py](https://github.com/opendilab/DI-engine/blob/c290a673/ding/torch_utils/__init__.py)
 - [ding/torch_utils/data_helper.py](https://github.com/opendilab/DI-engine/blob/c290a673/ding/torch_utils/data_helper.py)
 - [ding/torch_utils/tests/test_data_helper.py](https://github.com/opendilab/DI-engine/blob/c290a673/ding/torch_utils/tests/test_data_helper.py)
 
  The DI-engine framework provides a comprehensive suite of utility functions and helper classes to facilitate common operations in reinforcement learning development. These utilities handle data conversion, tensor manipulation, device management, and other technical tasks that simplify implementation across the codebase. This page provides an overview of these utilities and their primary use cases.

 For specific PyTorch utilities, see [PyTorch Utilities](https://deepwiki.com/opendilab/DI-engine/8.1-pytorch-utilities). For reinforcement learning specific utilities, see [Reinforcement Learning Utilities](https://deepwiki.com/opendilab/DI-engine/8.2-reinforcement-learning-utilities).

 
## Utility Categories

 DI-engine's utilities are organized into several categories to support different aspects of the framework:

 
```

```

 Sources: [ding/torch_utils/__init__.py1-14](https://github.com/opendilab/DI-engine/blob/c290a673/ding/torch_utils/__init__.py#L1-L14)

 
## Data Conversion Utilities

 DI-engine provides a set of functions for seamless conversion between different data types commonly used in deep learning:

 
```

```

 Sources: [ding/torch_utils/data_helper.py120-213](https://github.com/opendilab/DI-engine/blob/c290a673/ding/torch_utils/data_helper.py#L120-L213) [ding/torch_utils/data_helper.py216-287](https://github.com/opendilab/DI-engine/blob/c290a673/ding/torch_utils/data_helper.py#L216-L287) [ding/torch_utils/data_helper.py291-332](https://github.com/opendilab/DI-engine/blob/c290a673/ding/torch_utils/data_helper.py#L291-L332) [ding/torch_utils/data_helper.py335-382](https://github.com/opendilab/DI-engine/blob/c290a673/ding/torch_utils/data_helper.py#L335-L382) [ding/torch_utils/data_helper.py385-440](https://github.com/opendilab/DI-engine/blob/c290a673/ding/torch_utils/data_helper.py#L385-L440)

 
### to_tensor

 Converts `numpy.ndarray` objects to `torch.Tensor` objects. It can process individual arrays, lists, tuples, or dictionaries containing arrays.

 
```

```

 Sources: [ding/torch_utils/data_helper.py120-213](https://github.com/opendilab/DI-engine/blob/c290a673/ding/torch_utils/data_helper.py#L120-L213)

 
### to_ndarray

 Converts `torch.Tensor` objects to `numpy.ndarray` objects. Like `to_tensor`, it can process nested data structures.

 
```

```

 Sources: [ding/torch_utils/data_helper.py216-287](https://github.com/opendilab/DI-engine/blob/c290a673/ding/torch_utils/data_helper.py#L216-L287)

 
### to_list and tensor_to_list

 Convert `torch.Tensor` or `numpy.ndarray` objects to Python lists. The `to_list` function works with both tensor and array types, while `tensor_to_list` specifically handles tensors.

 
```

```

 Sources: [ding/torch_utils/data_helper.py291-332](https://github.com/opendilab/DI-engine/blob/c290a673/ding/torch_utils/data_helper.py#L291-L332) [ding/torch_utils/data_helper.py335-382](https://github.com/opendilab/DI-engine/blob/c290a673/ding/torch_utils/data_helper.py#L335-L382)

 
### to_item

 Converts data to Python native scalars. This is particularly useful for extracting single values from tensors or arrays.

 
```

```

 Sources: [ding/torch_utils/data_helper.py385-440](https://github.com/opendilab/DI-engine/blob/c290a673/ding/torch_utils/data_helper.py#L385-L440)

 
### to_dtype

 Changes data to a specified dtype. Works with `torch.Tensor` objects and containers of tensors.

 
```

```

 Sources: [ding/torch_utils/data_helper.py82-117](https://github.com/opendilab/DI-engine/blob/c290a673/ding/torch_utils/data_helper.py#L82-L117)

 
## Device Management

 
### to_device

 Transfers data to a specified device (CPU or GPU). Handles various data types including tensors, modules, and nested containers.

 
```

```

 Sources: [ding/torch_utils/data_helper.py16-79](https://github.com/opendilab/DI-engine/blob/c290a673/ding/torch_utils/data_helper.py#L16-L79)

 
### CudaFetcher

 A utility class for asynchronous data fetching and device transfer. It helps optimize the pipeline by pre-loading data to the GPU while the model is processing the current batch.

 
```

```

 Sources: [ding/torch_utils/data_helper.py523-593](https://github.com/opendilab/DI-engine/blob/c290a673/ding/torch_utils/data_helper.py#L523-L593)

 
## Shape Manipulation

 DI-engine provides several utilities for manipulating tensor shapes:

 
### squeeze and unsqueeze

 Add or remove dimensions from tensor data, including handling of nested data structures.

 
```

```

 Sources: [ding/torch_utils/data_helper.py626-658](https://github.com/opendilab/DI-engine/blob/c290a673/ding/torch_utils/data_helper.py#L626-L658) [ding/torch_utils/data_helper.py661-693](https://github.com/opendilab/DI-engine/blob/c290a673/ding/torch_utils/data_helper.py#L661-L693)

 
### zeros_like

 Creates zero tensors with the same shape as input data. Works with tensors and nested containers.

 
```

```

 Sources: [ding/torch_utils/data_helper.py722-756](https://github.com/opendilab/DI-engine/blob/c290a673/ding/torch_utils/data_helper.py#L722-L756)

 
### same_shape

 Checks if all data elements in a list have the same shapes.

 
```

```

 Sources: [ding/torch_utils/data_helper.py443-460](https://github.com/opendilab/DI-engine/blob/c290a673/ding/torch_utils/data_helper.py#L443-L460)

 
## Helper Classes

 
### LogDict

 A specialized dictionary class that automatically converts `torch.Tensor` objects to lists for convenient logging.

 
```

```

 Sources: [ding/torch_utils/data_helper.py463-503](https://github.com/opendilab/DI-engine/blob/c290a673/ding/torch_utils/data_helper.py#L463-L503)

 
### Additional Utilities

 The LogDict can be created using the `build_log_buffer()` function:

 
```

```

 Sources: [ding/torch_utils/data_helper.py506-520](https://github.com/opendilab/DI-engine/blob/c290a673/ding/torch_utils/data_helper.py#L506-L520)

 
## Other Utility Functions

 
### get_tensor_data

 Gets tensor data without disturbing the gradient computation graph.

 
```

```

 Sources: [ding/torch_utils/data_helper.py595-623](https://github.com/opendilab/DI-engine/blob/c290a673/ding/torch_utils/data_helper.py#L595-L623)

 
### get_null_data

 Creates null data based on a template, useful for padding sequences or creating placeholder entries.

 
```

```

 Sources: [ding/torch_utils/data_helper.py696-719](https://github.com/opendilab/DI-engine/blob/c290a673/ding/torch_utils/data_helper.py#L696-L719)

 
## Usage Patterns

 The utilities in DI-engine are designed to facilitate common operations across the framework. The following table shows typical usage patterns for these utilities:

 
| Scenario | Utility Function | Example Use |
|---|---|---|
| Transferring model to GPU | to_device | model = to_device(model, 'cuda:0') |
| Converting numpy observation to tensor | to_tensor | obs_tensor = to_tensor(obs_array) |
| Extracting scalar value from tensor | to_item | reward_value = to_item(reward_tensor) |
| Creating a log-friendly dict | build_log_buffer | log = build_log_buffer() |
| Batch dimension manipulation | unsqueeze/squeeze | batch_obs = unsqueeze(obs, dim=0) |
| Asynchronous data loading | CudaFetcher | fetcher = CudaFetcher(dataloader, 'cuda') |

 
## Integration with DI-engine Components

 The utility functions described here are used throughout the DI-engine framework to facilitate operations between different components:

 
```

```

 These utilities handle the data transformation pipeline, ensuring seamless conversion between different formats used by various components of the system.

 Sources: [ding/torch_utils/data_helper.py16-756](https://github.com/opendilab/DI-engine/blob/c290a673/ding/torch_utils/data_helper.py#L16-L756)
