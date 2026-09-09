> 来源: [https://deepwiki.com/deepseek-ai/DualPipe/8-glossary](https://deepwiki.com/deepseek-ai/DualPipe/8-glossary)
> DeepWiki deepseek-ai/DualPipe

# Glossary

  Relevant source files 
 - [README.md](https://github.com/deepseek-ai/DualPipe/blob/030ce432/README.md?plain=1)
 - [dualpipe/comm.py](https://github.com/deepseek-ai/DualPipe/blob/030ce432/dualpipe/comm.py)
 - [dualpipe/dualpipe.py](https://github.com/deepseek-ai/DualPipe/blob/030ce432/dualpipe/dualpipe.py)
 - [dualpipe/dualpipev.py](https://github.com/deepseek-ai/DualPipe/blob/030ce432/dualpipe/dualpipev.py)
 - [dualpipe/utils.py](https://github.com/deepseek-ai/DualPipe/blob/030ce432/dualpipe/utils.py)
 - [examples/example_dualpipe.py](https://github.com/deepseek-ai/DualPipe/blob/030ce432/examples/example_dualpipe.py)
 - [examples/example_dualpipev.py](https://github.com/deepseek-ai/DualPipe/blob/030ce432/examples/example_dualpipev.py)
 
  This page provides definitions for the specialized terminology, architectural concepts, and internal code abstractions used in the DualPipe library. It serves as a reference for engineers to understand the mapping between pipeline parallelism theory and the implementation details found in the codebase.

 
## Pipeline Scheduling Terminology

 
### F, B, and W Phases

 In the context of DualPipe, computation is broken down into three distinct phases for each micro-batch.

 
 - **F (Forward)**: The forward pass computation [README.md34](https://github.com/deepseek-ai/DualPipe/blob/030ce432/README.md?plain=1#L34-L34)
 - **B (Backward for Input)**: The backward pass to calculate gradients with respect to the inputs (activation gradients) [README.md34](https://github.com/deepseek-ai/DualPipe/blob/030ce432/README.md?plain=1#L34-L34)
 - **W (Backward for Weights)**: The backward pass to calculate gradients with respect to the model parameters (weight gradients) [README.md35](https://github.com/deepseek-ai/DualPipe/blob/030ce432/README.md?plain=1#L35-L35)
 
 In traditional schedules like 1F1B, B and W are often combined into a single backward step. DualPipe separates them to enable the **ZB1P** (Zero Bubble 1 Pipe) style optimization where W is deferred to overlap with other F/B chunks [README.md29-30](https://github.com/deepseek-ai/DualPipe/blob/030ce432/README.md?plain=1#L29-L30)

 
### Pipeline Bubble

 The idle time on a device where no useful computation is occurring, typically at the start (warm-up) or end (cool-down) of a pipeline execution [README.md3-4](https://github.com/deepseek-ai/DualPipe/blob/030ce432/README.md?plain=1#L3-L4) DualPipe significantly reduces this bubble compared to 1F1B by using bidirectional scheduling and F/B overlap [README.md26-31](https://github.com/deepseek-ai/DualPipe/blob/030ce432/README.md?plain=1#L26-L31)

 
### Bidirectional Scheduling

 A scheduling strategy where micro-batches are processed in two symmetric directions simultaneously (forward and reverse). In `DualPipe`, this is implemented by assigning two modules to each rank and managing two symmetric "phases" of computation [dualpipe/dualpipe.py11-22](https://github.com/deepseek-ai/DualPipe/blob/030ce432/dualpipe/dualpipe.py#L11-L22)

 **Sources:** [README.md26-36](https://github.com/deepseek-ai/DualPipe/blob/030ce432/README.md?plain=1#L26-L36) [dualpipe/dualpipe.py11-22](https://github.com/deepseek-ai/DualPipe/blob/030ce432/dualpipe/dualpipe.py#L11-L22)

 
---

 
## Code Abstractions and Entities

 
### DualPipe vs. DualPipeV

 
 - **DualPipe**: The original bidirectional algorithm. It requires $PP$ physical devices for $PP$ stages [README.md30](https://github.com/deepseek-ai/DualPipe/blob/030ce432/README.md?plain=1#L30-L30)
 - **DualPipeV**: A V-shape variant that executes $PP$ stages on $PP/2$ physical devices by folding the pipeline [README.md31](https://github.com/deepseek-ai/DualPipe/blob/030ce432/README.md?plain=1#L31-L31) In the code, this is reflected by `DualPipeV` managing a V-shape rank topology [dualpipe/dualpipev.py36-41](https://github.com/deepseek-ai/DualPipe/blob/030ce432/dualpipe/dualpipev.py#L36-L41)
 
 
### Overlapped Forward-Backward (`overlapped_forward_backward`)

 A specialized execution mode where a forward chunk and a backward chunk are executed concurrently to hide communication latency.

 
 - **Logic**: Users must implement this in their `PipelineStage` class [examples/example_dualpipe.py55-83](https://github.com/deepseek-ai/DualPipe/blob/030ce432/examples/example_dualpipe.py#L55-L83)
 - **Internal Call**: The library triggers this via `_forward_backward_compute_chunk` [dualpipe/dualpipe.py121-169](https://github.com/deepseek-ai/DualPipe/blob/030ce432/dualpipe/dualpipe.py#L121-L169)
 
 
### WeightGradStore

 A global utility class used to manage the separation of weight gradient computation ($W$) from input gradient computation ($B$).

 
 - **`enabled`**: A flag that, when `True`, redirects weight gradient calculations into a cache rather than executing them immediately [dualpipe/utils.py10](https://github.com/deepseek-ai/DualPipe/blob/030ce432/dualpipe/utils.py#L10-L10) [examples/example_dualpipe.py29-32](https://github.com/deepseek-ai/DualPipe/blob/030ce432/examples/example_dualpipe.py#L29-L32)
 - **`put`**: Stores a gradient calculation function (closure) [dualpipe/utils.py15-16](https://github.com/deepseek-ai/DualPipe/blob/030ce432/dualpipe/utils.py#L15-L16)
 - **`flush` / `pop`**: Used to commit cached functions to a queue and execute them during the pipeline's "bubble" or overlapped sections [dualpipe/utils.py19-29](https://github.com/deepseek-ai/DualPipe/blob/030ce432/dualpipe/utils.py#L19-L29)
 
 **Sources:** [dualpipe/dualpipe.py121-169](https://github.com/deepseek-ai/DualPipe/blob/030ce432/dualpipe/dualpipe.py#L121-L169) [dualpipe/utils.py8-35](https://github.com/deepseek-ai/DualPipe/blob/030ce432/dualpipe/utils.py#L8-L35) [examples/example_dualpipe.py55-83](https://github.com/deepseek-ai/DualPipe/blob/030ce432/examples/example_dualpipe.py#L55-L83)

 
---

 
## System Mapping Diagrams

 
### Concept to Code Entity Mapping

 The following diagram maps high-level pipeline concepts to the specific classes and functions that implement them in the `DualPipe` repository.

 **Diagram: Architectural Mapping**

 
```

```

 **Sources:** [dualpipe/dualpipe.py11-22](https://github.com/deepseek-ai/DualPipe/blob/030ce432/dualpipe/dualpipe.py#L11-L22) [dualpipe/dualpipev.py11-22](https://github.com/deepseek-ai/DualPipe/blob/030ce432/dualpipe/dualpipev.py#L11-L22) [dualpipe/comm.py1-38](https://github.com/deepseek-ai/DualPipe/blob/030ce432/dualpipe/comm.py#L1-L38) [dualpipe/utils.py8-12](https://github.com/deepseek-ai/DualPipe/blob/030ce432/dualpipe/utils.py#L8-L12) [dualpipe/utils.py62-80](https://github.com/deepseek-ai/DualPipe/blob/030ce432/dualpipe/utils.py#L62-L80)

 
### Computation Phase Data Flow

 This diagram illustrates how the `WeightGradStore` intercepts the standard PyTorch backward flow to implement the $B$ and $W$ separation required for DualPipe's efficiency.

 **Diagram: Gradient Management Flow**

 
```

```

 **Sources:** [dualpipe/utils.py8-35](https://github.com/deepseek-ai/DualPipe/blob/030ce432/dualpipe/utils.py#L8-L35) [examples/example_dualpipe.py13-35](https://github.com/deepseek-ai/DualPipe/blob/030ce432/examples/example_dualpipe.py#L13-L35)

 
---

 
## Technical Jargon and Abbreviations

 
| Term | Definition | Code Pointer |
|---|---|---|
| PP Rank | The logical position of a process in the pipeline (0 to N-1). | self.rank in dualpipe/dualpipe.py36 |
| Phase | Refers to one of the two symmetric directions in the bidirectional schedule (Phase 0 or Phase 1). | phase arg in dualpipe/dualpipe.py67 |
| Chunk ID | The index of a micro-batch within the total num_chunks. | chunk_id in dualpipe/dualpipe.py69 |
| P2POp | A point-to-point communication operation (send or receive) managed by NCCL. | dist.P2POp in dualpipe/comm.py30 |
| ZB | Zero Bubble. Refers to the optimization where weight gradients are calculated during communication/forward phases. | enable_zb in dualpipe/dualpipe.py87 |
| Rank Mapping | The translation between a process's global MPI/NCCL rank and its position in the pipeline. | rank_mapping in dualpipe/dualpipe.py28-36 |

 **Sources:** [dualpipe/dualpipe.py28-87](https://github.com/deepseek-ai/DualPipe/blob/030ce432/dualpipe/dualpipe.py#L28-L87) [dualpipe/comm.py25-38](https://github.com/deepseek-ai/DualPipe/blob/030ce432/dualpipe/comm.py#L25-L38) [dualpipe/utils.py8-35](https://github.com/deepseek-ai/DualPipe/blob/030ce432/dualpipe/utils.py#L8-L35)
