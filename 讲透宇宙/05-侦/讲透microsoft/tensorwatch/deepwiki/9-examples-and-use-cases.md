<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/tensorwatch · page 9 Examples and Use Cases · fetched 2026-10-26 -->

# Examples and Use Cases

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitignore](.gitignore)
- [docs/images/teaser.gif](docs/images/teaser.gif)
- [notebooks/data_exploration.ipynb](notebooks/data_exploration.ipynb)
- [notebooks/fruits_analysis.ipynb](notebooks/fruits_analysis.ipynb)
- [notebooks/mnist.ipynb](notebooks/mnist.ipynb)
- [notebooks/network_arch.ipynb](notebooks/network_arch.ipynb)
- [tensorwatch/embeddings/tsne_utils.py](tensorwatch/embeddings/tsne_utils.py)
- [tensorwatch/model_graph/torchstat/README.md](tensorwatch/model_graph/torchstat/README.md)
- [tensorwatch/model_graph/torchstat/__init__.py](tensorwatch/model_graph/torchstat/__init__.py)
- [tensorwatch/model_graph/torchstat/reporter.py](tensorwatch/model_graph/torchstat/reporter.py)
- [tensorwatch/model_graph/torchstat/stat_tree.py](tensorwatch/model_graph/torchstat/stat_tree.py)
- [tensorwatch/zmq_wrapper.py](tensorwatch/zmq_wrapper.py)
- [test/pre_train/draw_model.py](test/pre_train/draw_model.py)
- [test/pre_train/model_stats.py](test/pre_train/model_stats.py)

</details>



This page provides practical examples and use cases for TensorWatch, demonstrating its capabilities in model analysis, real-time monitoring, data exploration, and visualization. TensorWatch's flexibility allows it to be used across a wide range of deep learning workflows. For information about the core architecture, see [Core Architecture](#3).

## Table of Key Examples

| Example Type | Description | Primary Classes Used |
| ------------ | ----------- | -------------------- |
| Model Statistics | Analyze model parameters, FLOPs, and memory usage | `ModelStats` |
| Lazy Logging | Real-time monitoring of training metrics | `Watcher`, `WatcherClient` |
| Data Exploration | Visualize high-dimensional data with t-SNE | `get_tsne_components`, `ArrayStream` |
| Network Visualization | Generate model architecture diagrams | `draw_model` |

## Model Statistics Analysis

TensorWatch provides tools to analyze PyTorch models, calculating statistics like:
- Parameter counts
- Floating-point operations (FLOPs)
- Memory requirements
- Layer-by-layer metrics

### Example: Analyzing Common CNN Architectures

```python
import tensorwatch as tw
import torchvision.models

model = torchvision.models.resnet18()
model_stats = tw.ModelStats(model, [1, 3, 224, 224], clone_model=False)
print(f'FLOPs: {model_stats.Flops}, parameters: {model_stats.parameters}, memory: {model_stats.inference_memory}')
```

The `ModelStats` class analyzes model architectures before training, giving insights into computational requirements and memory usage.

Sources: [test/pre_train/model_stats.py:1-9]()

### Model Analysis Flow

```mermaid
flowchart TD
    A["PyTorch Model"] --> B["ModelStats"]
    C["Input Shape"] --> B
    B --> D["Analyzer"]
    D --> E["Forward/Backward\nHooks"]
    E --> F["Compute Statistics"]
    F --> G["FLOPs"]
    F --> H["Parameters"]
    F --> I["Memory Usage"]
    F --> J["MAdd Operations"]
    K["StatTree"] --> L["Pandas DataFrame"]
    F --> K
    L --> M["Human-readable Report"]
```

Sources: [tensorwatch/model_graph/torchstat/stat_tree.py](), [tensorwatch/model_graph/torchstat/reporter.py]()

## Real-Time Training Monitoring

TensorWatch enables real-time monitoring of neural network training through its "lazy logging" system, which allows querying variables without pre-defined logging statements.

### Lazy Logging Architecture

```mermaid
sequenceDiagram
    participant NB as "Jupyter Notebook"
    participant WC as "WatcherClient"
    participant W as "Watcher"
    participant TP as "Training Process"
    participant V as "Visualizer"
    
    NB->>WC: create WatcherClient()
    TP->>W: create Watcher()
    TP->>W: observe(var1=value1, var2=value2)
    NB->>WC: create_stream(expr="lambda d: d.var1 + d.var2")
    WC->>W: Send stream creation request
    W->>W: Create Evaler with lambda
    TP->>W: observe() with new values
    W->>W: Evaluate expression
    W->>WC: Send StreamItem with result
    NB->>V: Create Visualizer(stream)
    WC->>V: StreamItem data
    V->>NB: Update visualization
```

### Example: Monitoring MNIST Training

The following workflow demonstrates how to monitor an MNIST training run in real-time:

1. Start the training script in a separate process
2. Create `WatcherClient` instances in a Jupyter notebook
3. Request specific metrics using lambda expressions
4. Visualize the metrics as they're produced

```python
import tensorwatch as tw

# Connect to training process
train = tw.WatcherClient(port=0)
test = tw.WatcherClient(port=1)

# Request batch loss vs epoch data
batch_loss_stream = train.create_stream(
    lambda data: (data.epochf, data.batch_loss)
)

# Visualize with line plot
vis = tw.Visualizer(batch_loss_stream, vis_type='line')
vis.show()
```

Sources: [notebooks/mnist.ipynb:32-104](), [notebooks/fruits_analysis.ipynb:41-107]()

### ZMQ Communication Flow

```mermaid
flowchart TD
    A["Training Process"] -->|"observe()"| B["Watcher"]
    C["Jupyter Notebook"] -->|"create"| D["WatcherClient"]
    D -->|"create_stream(lambda)"| B
    B -->|"ZMQ Socket\nCommunication"| D
    D -->|"stream data"| E["Visualizer"]
    E -->|"render"| F["Plot/Chart"]
```

Sources: [tensorwatch/zmq_wrapper.py:14-290]()

## Data Exploration and Visualization

TensorWatch offers tools for exploring high-dimensional data through dimensionality reduction techniques like t-SNE.

### Example: Visualizing MNIST with t-SNE

The following process visualizes MNIST digit clusters using t-SNE:

1. Load the MNIST dataset
2. Sample a subset of images for each digit class
3. Apply t-SNE to reduce dimensionality to 3D
4. Visualize the resulting components in an interactive plot

```python
import tensorwatch as tw

# Get t-SNE components from dataset
components = tw.get_tsne_components((inputs, labels))

# Create stream and visualize
comp_stream = tw.ArrayStream(components)
vis = tw.Visualizer(comp_stream, vis_type='tsne', 
                    hover_images=inputs, hover_image_reshape=(28,28))
vis.show()
```

Sources: [notebooks/data_exploration.ipynb:38-130](), [tensorwatch/embeddings/tsne_utils.py:1-42]()

### t-SNE Visualization Workflow

```mermaid
flowchart TD
    A["Input Data\n(High Dimension)"] --> B["get_tsne_components()"]
    B --> C["3D Components"]
    C --> D["ArrayStream"]
    D --> E["Visualizer(vis_type='tsne')"]
    E --> F["Interactive 3D Plot"]
    G["Original Images"] --> E
    E -->|"hover shows"| H["Image Preview"]
```

Sources: [tensorwatch/embeddings/tsne_utils.py:23-38]()

## Network Architecture Visualization

TensorWatch can generate visual representations of neural network architectures, helping to understand model structure.

### Example: Visualizing VGG16 Architecture

```python
import tensorwatch as tw
import torchvision.models

vgg16_model = torchvision.models.vgg16()
drawing = tw.draw_model(vgg16_model, [1, 3, 224, 224])
drawing.save('model_architecture.png')
```

Sources: [test/pre_train/draw_model.py:1-10](), [notebooks/network_arch.ipynb:1-13]()

### Network Visualization Pipeline

```mermaid
flowchart TD
    A["PyTorch Model"] --> B["tw.draw_model()"]
    C["Input Shape"] --> B
    B --> D["Model Graph Generation"]
    D --> E["Layer Information\nExtraction"]
    E --> F["Graph Rendering\n(PyDot)"]
    F --> G["SVG/PNG Output"]
```

Sources: [notebooks/network_arch.ipynb:1-13](), [test/pre_train/draw_model.py:1-10]()

## Integrated Workflow Example

The following diagram illustrates a complete deep learning workflow using TensorWatch for monitoring, analysis, and visualization:

```mermaid
flowchart TD
    subgraph "Pre-Training Analysis"
        A1["Model Definition"] --> A2["tw.ModelStats"]
        A2 --> A3["FLOPs/Memory Analysis"]
        A1 --> A4["tw.draw_model"]
        A4 --> A5["Architecture Visualization"]
    end
    
    subgraph "Training Monitoring"
        B1["Training Script"] --> B2["tw.Watcher"]
        B2 -->|"observe()"| B3["Variables & Metrics"]
        B4["Jupyter Notebook"] --> B5["tw.WatcherClient"]
        B5 -->|"lambda queries"| B2
        B5 --> B6["tw.Visualizer"]
        B6 --> B7["Real-time Plots"]
    end
    
    subgraph "Post-Training Analysis"
        C1["Training Data"] --> C2["tw.get_tsne_components"]
        C2 --> C3["Dimensionality Reduction"]
        C3 --> C4["tw.Visualizer(vis_type='tsne')"]
        C4 --> C5["Interactive Data Visualization"]
    end
    
    A3 --> B1
    A5 --> B1
    B7 --> C1
```

Sources: [notebooks/mnist.ipynb](), [notebooks/fruits_analysis.ipynb](), [notebooks/data_exploration.ipynb](), [test/pre_train/model_stats.py](), [test/pre_train/draw_model.py]()

## Common Use Cases

### 1. Model Development and Debugging

Use TensorWatch to:
- Analyze model complexity before training
- Visualize architecture to verify design
- Monitor training in real-time to identify problems early
- Compare parameter counts and computational demands between model variants

### 2. Training Optimization

Use TensorWatch to:
- Monitor batch-level metrics to fine-tune hyperparameters
- Identify computational bottlenecks in model architecture
- Compare training behavior across different optimization strategies
- Track resource usage during training

### 3. Data Understanding

Use TensorWatch to:
- Visualize high-dimensional data using t-SNE
- Explore relationships between data points
- Identify clusters and patterns in training data
- Examine model's internal representations

### 4. Educational and Research Applications

Use TensorWatch to:
- Visualize neural network architectures for teaching
- Compare different model designs side-by-side
- Demonstrate training dynamics in real-time
- Explore model behavior interactively

## Additional Resources

For comprehensive examples of these use cases, refer to the Jupyter notebooks in the repository:
- MNIST training monitoring: `notebooks/mnist.ipynb`
- Fruits dataset analysis: `notebooks/fruits_analysis.ipynb`
- Data exploration: `notebooks/data_exploration.ipynb`
- Network architecture visualization: `notebooks/network_arch.ipynb`

For information about the Lazy Logging system, see [Lazy Logging](#3.3).