> 来源: [https://deepwiki.com/catalyst-team/catalyst/5-data-processing](https://deepwiki.com/catalyst-team/catalyst/5-data-processing)
> DeepWiki catalyst-team/catalyst | Last indexed: 21 April 2025 (e99f90

# Data Processing

  Relevant source files 
 - [catalyst/contrib/data/collate_fn.py](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/contrib/data/collate_fn.py)
 - [catalyst/data/__init__.py](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/data/__init__.py)
 - [catalyst/data/dataset.py](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/data/dataset.py)
 - [catalyst/data/sampler.py](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/data/sampler.py)
 - [catalyst/utils/__init__.py](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/utils/__init__.py)
 - [catalyst/utils/config.py](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/utils/config.py)
 - [catalyst/utils/misc.py](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/utils/misc.py)
 - [catalyst/utils/torch.py](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/utils/torch.py)
 - [docs/api/data.rst](https://github.com/catalyst-team/catalyst/blob/e99f9065/docs/api/data.rst)
 
  This document covers Catalyst's data handling components, which provide tools for efficiently processing, sampling, and augmenting data during model training. These components build upon PyTorch's data loading ecosystem while adding specialized functionality for addressing class imbalance, self-supervised learning, and distributed training scenarios.

 For information about metrics computation, see [Metrics System](https://deepwiki.com/catalyst-team/catalyst/6-metrics-system). For details on the actual training implementation, see [Runner System](https://deepwiki.com/catalyst-team/catalyst/2-runner-system).

 
## Overview

 The data processing subsystem in Catalyst consists of several key components:

 
 - **Samplers** - Specialized sampling strategies to handle class imbalance and distributed training
 - **Dataset Wrappers** - Dataset implementations for specific use cases like self-supervised learning
 - **Collation Functions** - Custom batch collation logic for flexible data handling
 
 These components integrate with PyTorch's data loading pipeline and feed into Catalyst's Runner system, which orchestrates the training process.

 
```

```

 *Data Processing Components and their Integration with PyTorch*

 Sources: [catalyst/data/__init__.py](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/data/__init__.py) [catalyst/data/sampler.py](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/data/sampler.py) [catalyst/data/dataset.py](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/data/dataset.py) [catalyst/contrib/data/collate_fn.py](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/contrib/data/collate_fn.py)

 
## Samplers

 Samplers in Catalyst extend PyTorch's `Sampler` class to provide specialized sampling strategies. These samplers generate indices for accessing elements from datasets in specific orders or distributions.

 
```

```

 *Catalyst Sampler Hierarchy*

 Sources: [catalyst/data/sampler.py](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/data/sampler.py)

 
### BalanceClassSampler

 `BalanceClassSampler` addresses class imbalance by creating stratified samples. It supports two modes:

 
 - **downsampling**: Limits all classes to the size of the smallest class
 - **upsampling**: Increases all classes to the size of the largest class (with replacement)
 
 This sampler is particularly useful for classification tasks with uneven class distributions.

 
```

```

 Sources: [catalyst/data/sampler.py17-113](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/data/sampler.py#L17-L113)

 
### BatchBalanceClassSampler

 `BatchBalanceClassSampler` creates balanced batches by selecting a fixed number of classes and a fixed number of samples per class for each batch. This is particularly useful for:

 
 - Metric learning tasks
 - Training with triplet losses
 - Forming positive/negative pairs within a batch
 
 Unlike `BalanceClassSampler`, this sampler operates at the batch level rather than the dataset level.

 
```

```

 Sources: [catalyst/data/sampler.py116-255](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/data/sampler.py#L116-L255)

 
### DynamicBalanceClassSampler

 `DynamicBalanceClassSampler` provides a smooth transition from the original class distribution to a balanced one during training. It uses an exponential scheduler to gradually change the sampling distribution over epochs.

 This sampler is useful for:

 
 - Training on highly imbalanced datasets
 - Transitioning from exploration of the original data distribution to exploitation of a balanced distribution
 
 Sources: [catalyst/data/sampler.py258-397](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/data/sampler.py#L258-L397)

 
### MiniEpochSampler

 `MiniEpochSampler` creates smaller "mini-epochs" from a dataset, allowing for more frequent validation and model updates. This is particularly useful for:

 
 - Large datasets where full epochs take too long
 - Rapid experimentation with different hyperparameters
 - Implementing curriculum learning strategies
 
 Sources: [catalyst/data/sampler.py400-496](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/data/sampler.py#L400-L496)

 
### DistributedSamplerWrapper

 `DistributedSamplerWrapper` wraps any sampler to make it compatible with distributed training. It ensures that each process receives a unique subset of the data when using multi-GPU training with `DistributedDataParallel`.

 
```

```

 Sources: [catalyst/data/sampler.py499-550](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/data/sampler.py#L499-L550)

 
## Dataset Wrappers

 Catalyst provides specialized dataset wrappers that extend PyTorch's `Dataset` class to support specific use cases.

 
```

```

 *Catalyst Dataset Wrapper Hierarchy*

 Sources: [catalyst/data/dataset.py](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/data/dataset.py)

 
### DatasetFromSampler

 `DatasetFromSampler` creates a dataset from a sampler's indices. This is primarily used internally by the `DistributedSamplerWrapper` to create subsampled datasets for distributed training.

 Sources: [catalyst/data/dataset.py6-37](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/data/dataset.py#L6-L37)

 
### SelfSupervisedDatasetWrapper

 `SelfSupervisedDatasetWrapper` implements contrastive learning logic by creating multiple augmented views of the same sample. This wrapper is essential for self-supervised learning approaches like SimCLR, where the model learns by comparing different views of the same data point.

 The wrapper can be configured with:

 
 - A single transform applied to both views
 - Separate transforms for each view
 - An optional transform for the original sample
 
 
```

```

 Sources: [catalyst/data/dataset.py39-158](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/data/dataset.py#L39-L158)

 
## Collation Functions

 Collation functions customize how individual samples are combined into batches when using PyTorch's `DataLoader`.

 
### FilteringCollateFn

 `FilteringCollateFn` extends PyTorch's default collation by selectively preventing certain keys in batch items from being converted to tensors. This is useful for handling complex data types or metadata that should remain in their original format.

 
```

```

 Sources: [catalyst/contrib/data/collate_fn.py6-42](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/contrib/data/collate_fn.py#L6-L42)

 
## Integration with PyTorch's Data Pipeline

 The following diagram illustrates how Catalyst's data processing components integrate with PyTorch's data loading pipeline and the Catalyst training loop:

 
```

```

 *Data Flow in Catalyst Training Pipeline*

 Sources: [catalyst/data/__init__.py](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/data/__init__.py) [catalyst/data/sampler.py](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/data/sampler.py) [catalyst/data/dataset.py](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/data/dataset.py)

 
## Usage Examples

 Below are common patterns for using Catalyst's data processing components:

 
### Handling Class Imbalance

 
```

```

 
### Self-Supervised Learning Setup

 
```

```

 
### Distributed Training with Custom Sampling

 
```

```

 
## Conclusion

 Catalyst's data processing components provide a flexible and powerful extension to PyTorch's data loading ecosystem. These tools help address common challenges in deep learning such as class imbalance, multi-GPU training, and specialized training paradigms like self-supervised learning.

 By leveraging these components, users can implement advanced data handling strategies while maintaining compatibility with PyTorch's familiar data loading patterns.

 Sources: [catalyst/data/__init__.py](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/data/__init__.py) [catalyst/data/sampler.py](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/data/sampler.py) [catalyst/data/dataset.py](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/data/dataset.py) [catalyst/contrib/data/collate_fn.py](https://github.com/catalyst-team/catalyst/blob/e99f9065/catalyst/contrib/data/collate_fn.py)
