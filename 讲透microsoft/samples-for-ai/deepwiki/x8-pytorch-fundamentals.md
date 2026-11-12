<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/samples-for-ai · extra page PyTorch Fundamentals · fetched 2026-10-26 -->

# PyTorch Fundamentals

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [examples/pytorch/PyTorchExamples.sln](examples/pytorch/PyTorchExamples.sln)
- [examples/pytorch/cifar10/cifar10.py](examples/pytorch/cifar10/cifar10.py)
- [examples/pytorch/cifar10/cifar10.pyproj](examples/pytorch/cifar10/cifar10.pyproj)
- [examples/pytorch/mnist/mnist.py](examples/pytorch/mnist/mnist.py)
- [examples/pytorch/mnist/mnist.pyproj](examples/pytorch/mnist/mnist.pyproj)
- [examples/pytorch/sentiment_analysis/sentiment_analysis.py](examples/pytorch/sentiment_analysis/sentiment_analysis.py)
- [examples/pytorch/sentiment_analysis/sentiment_analysis.pyproj](examples/pytorch/sentiment_analysis/sentiment_analysis.pyproj)
- [examples/pytorch/transfer_learning/transfer_learning.py](examples/pytorch/transfer_learning/transfer_learning.py)
- [examples/pytorch/transfer_learning/transfer_learning.pyproj](examples/pytorch/transfer_learning/transfer_learning.pyproj)

</details>



This document covers the fundamental PyTorch examples that demonstrate core deep learning concepts including image classification (MNIST, CIFAR-10), transfer learning, and natural language processing (sentiment analysis). These examples provide a foundation for understanding PyTorch's programming model, training workflows, and neural network architectures.

For advanced PyTorch implementations including ScreenerNet curriculum learning, see [ScreenerNet Implementation](#3.2.2). For neural image captioning systems, see [Image Captioning](#3.2.3).

## Project Structure

The PyTorch fundamentals are organized as a Visual Studio solution containing four core example projects that demonstrate different aspects of deep learning with PyTorch.

```mermaid
graph TB
    subgraph "PyTorchExamples.sln"
        MNIST["mnist.pyproj<br/>MNIST Digit Classification"]
        CIFAR10["cifar10.pyproj<br/>CIFAR-10 Image Classification"]
        TRANSFER["transfer_learning.pyproj<br/>ResNet34 Transfer Learning"]
        SENTIMENT["sentiment_analysis.pyproj<br/>IMDB Sentiment Analysis"]
    end
    
    subgraph "Computer Vision"
        MNIST_DATA["MNIST Dataset<br/>28x28 Grayscale Images"]
        CIFAR_DATA["CIFAR-10 Dataset<br/>32x32 Color Images"]
        IMAGENET["ImageNet Pretrained<br/>ResNet34 Weights"]
    end
    
    subgraph "Natural Language Processing"
        IMDB_DATA["IMDB Dataset<br/>Movie Reviews"]
        TORCHTEXT["torchtext.datasets<br/>Text Processing"]
    end
    
    MNIST --> MNIST_DATA
    CIFAR10 --> CIFAR_DATA
    TRANSFER --> CIFAR_DATA
    TRANSFER --> IMAGENET
    SENTIMENT --> IMDB_DATA
    SENTIMENT --> TORCHTEXT
```

Sources: [examples/pytorch/PyTorchExamples.sln:1-39]()

## Training Pipeline Architecture

All fundamental examples follow a consistent training pipeline pattern with standardized function signatures and workflow components.

```mermaid
graph TD
    subgraph "Common Functions"
        GET_DATA["get_data_loader(args, train, shuffle)"]
        VALIDATE_FUNC["validate(model, device, val_loader, criterion)"]
        SAVE_MODEL["save_model(args, model, filename)"]
        TRAIN_FUNC["train(args)"]
    end
    
    subgraph "Training Loop Components"
        DEVICE["torch.device('cuda' if available else 'cpu')"]
        MODEL_INIT["Model().to(device)"]
        CRITERION["nn.CrossEntropyLoss() / nn.BCELoss()"]
        OPTIMIZER["optim.Adam() / optim.SGD()"]
    end
    
    subgraph "Training Process"
        FORWARD["model(inputs)"]
        LOSS_CALC["criterion(output, labels)"]
        BACKWARD["loss.backward()"]
        STEP["optimizer.step()"]
    end
    
    GET_DATA --> TRAIN_FUNC
    VALIDATE_FUNC --> TRAIN_FUNC
    SAVE_MODEL --> TRAIN_FUNC
    
    TRAIN_FUNC --> DEVICE
    TRAIN_FUNC --> MODEL_INIT
    TRAIN_FUNC --> CRITERION
    TRAIN_FUNC --> OPTIMIZER
    
    MODEL_INIT --> FORWARD
    CRITERION --> LOSS_CALC
    LOSS_CALC --> BACKWARD
    BACKWARD --> STEP
```

Sources: [examples/pytorch/mnist/mnist.py:82-124](), [examples/pytorch/cifar10/cifar10.py:94-136](), [examples/pytorch/transfer_learning/transfer_learning.py:68-110]()

## Computer Vision Examples

### MNIST Digit Classification

The MNIST example demonstrates basic convolutional neural network architecture for grayscale image classification using the `Model` class with two convolutional layers followed by fully connected layers.

| Component | Implementation | Details |
|-----------|---------------|---------|
| Model Architecture | `Model(nn.Module)` | Conv2D → BatchNorm → LeakyReLU → MaxPool |
| Input Processing | `transforms.Normalize((0.13,), (0.31,))` | Grayscale normalization |
| Optimizer | `optim.SGD(lr=0.01, momentum=0.6)` | Stochastic gradient descent |
| Loss Function | `nn.CrossEntropyLoss()` | Multi-class classification |

```mermaid
graph LR
    subgraph "Model Architecture"
        INPUT["Input<br/>1x28x28"]
        CONV1["conv1<br/>nn.Conv2d(1,32,3,padding=1)"]
        BN1["bn1<br/>nn.BatchNorm2d(32)"]
        POOL1["MaxPool2d(2)<br/>32x14x14"]
        CONV2["conv2<br/>nn.Conv2d(32,16,3,padding=1)"]
        BN2["bn2<br/>nn.BatchNorm2d(16)"]
        POOL2["MaxPool2d(2)<br/>16x7x7"]
        FC1["fc1<br/>nn.Linear(784,100)"]
        FC2["fc2<br/>nn.Linear(100,10)"]
        OUTPUT["Output<br/>10 classes"]
    end
    
    INPUT --> CONV1
    CONV1 --> BN1
    BN1 --> POOL1
    POOL1 --> CONV2
    CONV2 --> BN2
    BN2 --> POOL2
    POOL2 --> FC1
    FC1 --> FC2
    FC2 --> OUTPUT
```

Sources: [examples/pytorch/mnist/mnist.py:30-47]()

### CIFAR-10 Image Classification

The CIFAR-10 example implements a deeper convolutional network for color image classification using the `make_conv_block` function to create modular convolutional blocks.

```mermaid
graph TB
    subgraph "Model Components"
        MAKE_CONV["make_conv_block(in_channels, out_channels)"]
        CONV_SEQ["Conv2d → ReLU → BatchNorm2d → Conv2d → ReLU → BatchNorm2d → MaxPool2d"]
    end
    
    subgraph "Architecture Flow"
        INPUT_32["Input 3x32x32"]
        BLOCK1["make_conv_block(3, 32)"]
        BLOCK2["make_conv_block(32, 64)"]
        BLOCK3["make_conv_block(64, 128)"]
        DROPOUT["Dropout2d(0.5)"]
        FC_LAYERS["Linear(2048,100) → Linear(100,10)"]
        OUTPUT_10["Output 10 classes"]
    end
    
    MAKE_CONV --> CONV_SEQ
    
    INPUT_32 --> BLOCK1
    BLOCK1 --> BLOCK2
    BLOCK2 --> BLOCK3
    BLOCK3 --> DROPOUT
    DROPOUT --> FC_LAYERS
    FC_LAYERS --> OUTPUT_10
```

Sources: [examples/pytorch/cifar10/cifar10.py:28-59]()

## Transfer Learning Implementation

The transfer learning example demonstrates how to adapt pre-trained models using `models.resnet34(pretrained=True)` with custom classification heads via the `create_resnet` function.

| Component | Implementation | Purpose |
|-----------|---------------|---------|
| Base Model | `models.resnet34(pretrained=True)` | ImageNet pre-trained features |
| Custom Head | `model.fc = nn.Linear(model.fc.in_features, 10)` | CIFAR-10 classification |
| Input Resize | `transforms.Resize((200, 200))` | Match ImageNet input size |
| Optimizer | `optim.Adam(lr=0.001)` | Lower learning rate for fine-tuning |

```mermaid
graph LR
    subgraph "Transfer Learning Pipeline"
        PRETRAINED["models.resnet34(pretrained=True)"]
        FROZEN["Frozen Feature Extractor<br/>ImageNet Weights"]
        CUSTOM_FC["model.fc = nn.Linear(in_features, 10)"]
        CIFAR_CLASSES["CIFAR-10 Classes"]
    end
    
    subgraph "Data Processing"
        RESIZE["transforms.Resize((200,200))"]
        NORMALIZE["transforms.Normalize((0.5,0.5,0.5), (0.5,0.5,0.5))"]
    end
    
    PRETRAINED --> FROZEN
    FROZEN --> CUSTOM_FC
    CUSTOM_FC --> CIFAR_CLASSES
    
    RESIZE --> NORMALIZE
```

Sources: [examples/pytorch/transfer_learning/transfer_learning.py:34-39](), [examples/pytorch/transfer_learning/transfer_learning.py:44-47]()

## Natural Language Processing

### Sentiment Analysis with Attention

The sentiment analysis example implements a bidirectional GRU with attention mechanism for binary classification of movie reviews using the `Model` class with embedding, recurrent, and attention layers.

| Component | Implementation | Details |
|-----------|---------------|---------|
| Embeddings | `nn.Embedding(vocab_size, idim, padding_idx=1)` | Word vector representations |
| Recurrent Layer | `nn.GRU(bidirectional=True, dropout=0.5)` | Bidirectional sequence processing |
| Attention | `nn.Linear(hdim * ndirections + idim, 1)` | Attention weight computation |
| Classification | `nn.Linear(hdim * ndirections, 100)` | Binary sentiment prediction |

```mermaid
graph TD
    subgraph "NLP Pipeline Components"
        TOKENIZE["tokenize_line_en(line)"]
        PREPROCESS["preprocessing(x)"]
        VOCAB_BUILD["TEXT.build_vocab(train)"]
        BUCKET_ITER["data.BucketIterator.splits()"]
    end
    
    subgraph "Model Architecture"
        EMBEDS["embeds<br/>nn.Embedding(vocab_size, 20)"]
        GRU["gru<br/>nn.GRU(bidirectional=True)"]
        ATT["att<br/>Attention Mechanism"]
        FC_ATT["fc_att<br/>Binary Classification"]
    end
    
    subgraph "Data Flow"
        IMDB["IMDB Dataset"]
        TOKENS["Tokenized Text"]
        SEQUENCES["Padded Sequences"]
        PREDICTIONS["Sentiment Predictions"]
    end
    
    IMDB --> TOKENIZE
    TOKENIZE --> PREPROCESS
    PREPROCESS --> VOCAB_BUILD
    VOCAB_BUILD --> BUCKET_ITER
    
    BUCKET_ITER --> EMBEDS
    EMBEDS --> GRU
    GRU --> ATT
    ATT --> FC_ATT
    FC_ATT --> PREDICTIONS
```

Sources: [examples/pytorch/sentiment_analysis/sentiment_analysis.py:33-61](), [examples/pytorch/sentiment_analysis/sentiment_analysis.py:78-91]()

## Common Design Patterns

### Argument Parsing and Configuration

All examples use consistent argument parsing patterns with `argparse.ArgumentParser()` for hyperparameter configuration:

| Parameter | MNIST Default | CIFAR-10 Default | Transfer Learning | Sentiment Analysis |
|-----------|---------------|------------------|-------------------|-------------------|
| Learning Rate | 0.01 | 0.01 | 0.001 | 0.002 |
| Batch Size | 1000 | 256 | 128 | 128 |
| Epochs | 20 | 20 | 20 | 20 |
| Data Directory | 'data' | 'data' | 'data' | 'data' |
| Model Directory | 'model' | 'model' | 'model' | 'model' |

Sources: [examples/pytorch/mnist/mnist.py:114-122](), [examples/pytorch/cifar10/cifar10.py:127-133](), [examples/pytorch/transfer_learning/transfer_learning.py:100-107](), [examples/pytorch/sentiment_analysis/sentiment_analysis.py:173-181]()

### Model Validation and Checkpointing

The `validate` function implements consistent evaluation logic across all examples using `model.eval()` and `torch.no_grad()` context managers. Best model checkpointing uses the `save_model` function with `torch.save(model.state_dict())` for state persistence.

```mermaid
graph LR
    subgraph "Validation Pattern"
        MODEL_EVAL["model.eval()"]
        NO_GRAD["torch.no_grad()"]
        COMPUTE_LOSS["criterion(output, label)"]
        COMPUTE_ACC["preds.eq(label).sum()"]
    end
    
    subgraph "Checkpointing Pattern"
        BEST_CHECK["if corrects > best_corrects"]
        SAVE_CALL["save_model(args, model, filename)"]
        TORCH_SAVE["torch.save(model.state_dict())"]
    end
    
    MODEL_EVAL --> NO_GRAD
    NO_GRAD --> COMPUTE_LOSS
    COMPUTE_LOSS --> COMPUTE_ACC
    
    COMPUTE_ACC --> BEST_CHECK
    BEST_CHECK --> SAVE_CALL
    SAVE_CALL --> TORCH_SAVE
```

Sources: [examples/pytorch/mnist/mnist.py:69-80](), [examples/pytorch/cifar10/cifar10.py:81-92](), [examples/pytorch/sentiment_analysis/sentiment_analysis.py:98-112]()

---

