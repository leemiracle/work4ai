<!-- source: DeepWiki mcp.deepwiki.com · repo mit-han-lab/proxylessnas · page 4 Evaluation Framework · fetched 2026-10-30 -->

# Evaluation Framework

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [eval.py](eval.py)
- [eval_tf.py](eval_tf.py)

</details>



The Evaluation Framework provides a standardized system for testing the performance of ProxylessNAS pre-trained models on common computer vision datasets. This framework supports both PyTorch and TensorFlow implementations, enabling researchers and practitioners to validate model accuracy on ImageNet and CIFAR-10 datasets.

For information about the available pre-trained models themselves, see [Model Zoo](#3). For documented performance results from training logs, see [Performance Results](#4.3).

## System Overview

The evaluation framework consists of two main evaluation scripts that provide standardized testing procedures for different deep learning frameworks. Both scripts implement similar evaluation workflows but are optimized for their respective framework ecosystems.

**Evaluation Framework Architecture**
```mermaid
graph TD
    subgraph "Input Sources"
        A["ImageNet Dataset"] --> C["eval.py"]
        B["CIFAR-10 Dataset"] --> C
        A --> D["eval_tf.py"]
    end
    
    subgraph "PyTorch Evaluation Path"
        C --> E["model_zoo.__dict__"]
        E --> F["proxyless_cpu"]
        E --> G["proxyless_gpu"] 
        E --> H["proxyless_mobile"]
        E --> I["proxyless_mobile_14"]
        E --> J["proxyless_cifar"]
    end
    
    subgraph "TensorFlow Evaluation Path"
        D --> K["tf_model_zoo.__dict__"]
        K --> L["proxyless_cpu (TF)"]
        K --> M["proxyless_gpu (TF)"]
        K --> N["proxyless_mobile (TF)"]
        K --> O["proxyless_mobile_14 (TF)"]
    end
    
    subgraph "Evaluation Metrics"
        P["AverageMeter"]
        Q["accuracy function"]
        R["CrossEntropyLoss"]
    end
    
    F --> P
    G --> P
    H --> P
    I --> P
    J --> P
    L --> P
    M --> P
    N --> P
    O --> P
    
    P --> S["Top-1 Accuracy"]
    P --> T["Top-5 Accuracy"]
    P --> U["Average Loss"]
```

Sources: [eval.py:15-19](), [eval_tf.py:13-15](), [README.md:93-97]()

## PyTorch Evaluation System

The PyTorch evaluation system is implemented in `eval.py` and provides comprehensive model testing capabilities for both ImageNet and CIFAR-10 datasets.

**PyTorch Evaluation Pipeline**
```mermaid
graph LR
    subgraph "Command Line Interface"
        A["argparse.ArgumentParser"] --> B["args.arch"]
        A --> C["args.dataset"] 
        A --> D["args.path"]
        A --> E["args.batch_size"]
    end
    
    subgraph "Model Loading"
        B --> F["model_zoo.__dict__[args.arch]"]
        F --> G["pretrained=True"]
    end
    
    subgraph "Dataset Selection"
        C --> H["imagenet branch"]
        C --> I["cifar10 branch"]
        H --> J["datasets.ImageFolder"]
        I --> K["datasets.CIFAR10"]
    end
    
    subgraph "Data Processing"
        J --> L["transforms.Compose"]
        K --> L
        L --> M["transforms.Resize(256)"]
        L --> N["transforms.CenterCrop(224)"]
        L --> O["transforms.Normalize"]
    end
    
    subgraph "Evaluation Loop"
        P["torch.no_grad()"] --> Q["data_loader"]
        Q --> R["net(_input)"]
        R --> S["criterion(output, target)"]
        S --> T["accuracy(output.data, target)"]
    end
```

Sources: [eval.py:21-63](), [eval.py:72-76](), [eval.py:82-123](), [eval.py:137-160]()

### Model Architecture Selection

The evaluation script supports all available ProxylessNAS model variants through the `model_zoo` module. The architecture selection is controlled by the `--arch` parameter:

| Parameter Value | Model Variant | Target Platform |
|-----------------|---------------|-----------------|
| `proxyless_cpu` | CPU-optimized | Intel CPU |
| `proxyless_gpu` | GPU-optimized | NVIDIA GPU |
| `proxyless_mobile` | Mobile-optimized | ARM mobile devices |
| `proxyless_mobile_14` | Mobile v1.4 | ARM mobile devices |
| `proxyless_cifar` | CIFAR-optimized | Research/CIFAR-10 |

Sources: [eval.py:47-54](), [eval.py:72-75]()

### Dataset Configuration

The evaluation system automatically configures dataset-specific preprocessing based on the `--dataset` parameter:

**ImageNet Configuration:**
- Input resolution: 224×224 (center crop from 256×256 resize)
- Normalization: ImageNet standard (mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
- Data path: `{args.path}/val` directory structure

**CIFAR-10 Configuration:**
- Input resolution: 32×32 (native CIFAR-10 size)
- Normalization: CIFAR-10 standard (mean=[125.3, 123.0, 113.9]/255, std=[63.0, 62.1, 66.7]/255)
- Automatic download: Enabled via `download=True`

Sources: [eval.py:81-107](), [eval.py:108-123]()

## TensorFlow Evaluation System

The TensorFlow evaluation system in `eval_tf.py` provides ImageNet validation for TensorFlow model variants using the TensorFlow session-based execution model.

**TensorFlow Evaluation Workflow**
```mermaid
graph TD
    subgraph "Model Initialization"
        A["tf_model_zoo.__dict__[args.arch]"] --> B["pretrained=True"]
        B --> C["net.sess (TensorFlow Session)"]
    end
    
    subgraph "Data Pipeline"
        D["datasets.ImageFolder"] --> E["transforms.Compose"]
        E --> F["torch.utils.data.DataLoader"]
        F --> G["_input.numpy()"]
        G --> H["np.transpose(images, [0,2,3,1])"]
    end
    
    subgraph "TensorFlow Execution"
        H --> I["feed_dict"]
        I --> J["net.images"]
        I --> K["net.labels"]
        I --> L["net.is_training: False"]
        M["net.cross_entropy"] --> N["net.sess.run(fetches)"]
        O["net.accuracy"] --> N
    end
    
    subgraph "Metrics Collection"
        N --> P["losses.update()"]
        N --> Q["top1.update()"]
    end
```

Sources: [eval_tf.py:48](), [eval_tf.py:50-75](), [eval_tf.py:79-96]()

### TensorFlow-Specific Implementation Details

The TensorFlow evaluation differs from PyTorch in several key aspects:

1. **Data Format Conversion:** Images are transposed from PyTorch format `[N,C,H,W]` to TensorFlow format `[N,H,W,C]` using `np.transpose(images, axes=[0, 2, 3, 1])`

2. **Label Processing:** Labels are converted to one-hot encoding using `net.labels_to_one_hot(1000, target.numpy())`

3. **Session-Based Execution:** Model inference uses TensorFlow session execution with feed dictionaries containing `net.images`, `net.labels`, and `net.is_training`

4. **Limited Dataset Support:** Only supports ImageNet evaluation (no CIFAR-10 support)

Sources: [eval_tf.py:80-82](), [eval_tf.py:84-90]()

## Evaluation Metrics and Utilities

Both evaluation scripts utilize the `AverageMeter` utility class for tracking running averages of loss and accuracy metrics throughout the evaluation process.

**Metrics Calculation Pipeline**
```mermaid
graph LR
    subgraph "PyTorch Metrics"
        A["accuracy(output.data, target, topk=(1,5))"] --> B["acc1, acc5"]
        B --> C["top1.update(acc1[0].item())"]
        B --> D["top5.update(acc5[0].item())"]
    end
    
    subgraph "TensorFlow Metrics"
        E["net.accuracy"] --> F["accuracy * 100"]
        F --> G["top1.update()"]
    end
    
    subgraph "Loss Tracking"
        H["criterion(output, target)"] --> I["losses.update(loss.item())"]
        J["net.cross_entropy"] --> K["losses.update(loss)"]
    end
    
    subgraph "Output Reporting"
        C --> L["Final Top-1 Average"]
        D --> M["Final Top-5 Average"]
        G --> L
        I --> N["Final Loss Average"]
        K --> N
    end
```

Sources: [eval.py:148-151](), [eval_tf.py:92-96](), [proxyless_nas/utils.py (referenced)]()

### Usage Examples

The evaluation framework supports flexible configuration through command-line arguments:

**ImageNet Evaluation (PyTorch):**
```bash
python eval.py --path '/path/to/imagenet' --arch proxyless_cpu --batch-size 32 --gpu all
```

**CIFAR-10 Evaluation (PyTorch):**
```bash
python eval.py --dataset cifar10 --arch proxyless_cifar
```

**ImageNet Evaluation (TensorFlow):**
```bash
python eval_tf.py --path '/path/to/imagenet' --arch proxyless_mobile_14 --batch-size 64
```

Sources: [README.md:93-97](), [eval.py:21-63](), [eval_tf.py:17-46]()

---

