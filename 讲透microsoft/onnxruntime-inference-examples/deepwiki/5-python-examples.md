<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/onnxruntime-inference-examples · page 5 Python Examples · fetched 2026-10-26 -->

# Python Examples

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [c_sharp/OpenVINO_EP/yolov3_object_detection/README.md](c_sharp/OpenVINO_EP/yolov3_object_detection/README.md)
- [python/OpenVINO_EP/tiny_yolo_v2_object_detection/README.md](python/OpenVINO_EP/tiny_yolo_v2_object_detection/README.md)
- [python/OpenVINO_EP/tiny_yolo_v2_object_detection/requirements.txt](python/OpenVINO_EP/tiny_yolo_v2_object_detection/requirements.txt)
- [python/OpenVINO_EP/tiny_yolo_v2_object_detection/tiny_yolov2_obj_detection_sample.py](python/OpenVINO_EP/tiny_yolo_v2_object_detection/tiny_yolov2_obj_detection_sample.py)
- [python/OpenVINO_EP/yolov4_object_detection/README.md](python/OpenVINO_EP/yolov4_object_detection/README.md)
- [python/OpenVINO_EP/yolov4_object_detection/requirements.txt](python/OpenVINO_EP/yolov4_object_detection/requirements.txt)
- [python/OpenVINO_EP/yolov4_object_detection/yolov4.py](python/OpenVINO_EP/yolov4_object_detection/yolov4.py)
- [python/models/llama/LLaMA-2 E2E Notebook.ipynb](python/models/llama/LLaMA-2 E2E Notebook.ipynb)
- [python/models/llama/README.md](python/models/llama/README.md)

</details>



## Purpose and Scope

This section covers Python examples in the ONNX Runtime inference examples repository, demonstrating inference workflows across computer vision and natural language processing tasks. The examples showcase two primary categories: OpenVINO Execution Provider integration for Intel hardware acceleration, and large language model inference with LLaMA-2.

For C# examples using similar execution providers, see [C# Examples](#4). For JavaScript browser implementations, see [JavaScript Examples](#6).

## OpenVINO Execution Provider Examples

The Python OpenVINO examples demonstrate computer vision inference using Intel's OpenVINO execution provider for hardware acceleration. These examples support CPU, GPU, and specialized Intel hardware targets.

### Object Detection Examples

#### YOLOv4 Object Detection

The YOLOv4 implementation supports real-time object detection with 80 COCO dataset classes across multiple input modalities.

```mermaid
graph TD
    subgraph "Input Sources"
        A["Image Files"]
        B["Video Files"]  
        C["Live Camera"]
    end
    
    subgraph "yolov4.py Core Functions"
        D["image_preprocess()"]
        E["postprocess_bbbox()"]
        F["postprocess_boxes()"]
        G["nms()"]
        H["draw_bbox()"]
    end
    
    subgraph "ONNX Runtime Integration"
        I["rt.InferenceSession"]
        J["OpenVINOExecutionProvider"]
        K["sess.run()"]
    end
    
    subgraph "Output Processing"
        L["bboxes_iou()"]
        M["cv2.rectangle()"]
        N["Video/Image Output"]
    end
    
    A --> D
    B --> D
    C --> D
    D --> I
    I --> J
    J --> K
    K --> E
    E --> F
    F --> G
    G --> H
    H --> L
    L --> M
    M --> N
```

Sources: [python/OpenVINO_EP/yolov4_object_detection/yolov4.py:1-343](), [python/OpenVINO_EP/yolov4_object_detection/README.md:1-99]()

#### TinyYOLOv2 Object Detection

The TinyYOLOv2 implementation provides a lightweight alternative for resource-constrained environments, detecting 20 object classes.

```mermaid
graph TD
    subgraph "Core Processing Pipeline"
        A["tiny_yolov2_obj_detection_sample.py"]
        B["image_preprocess()"]
        C["sigmoid()"]
        D["softmax()"]
        E["postprocess_output()"]
    end
    
    subgraph "Model Configuration"
        F["anchors = [1.08, 1.19, ...]"]
        G["label = ['aeroplane', 'bicycle', ...]"]
        H["clut color lookup"]
    end
    
    subgraph "OpenVINO EP Setup"
        I["rt.InferenceSession"]
        J["device_type options"]
        K["CPU_FP32/GPU_FP32/GPU_FP16"]
    end
    
    A --> B
    B --> I
    I --> J
    J --> K
    K --> E
    E --> C
    E --> D
    F --> E
    G --> E
    H --> E
```

Sources: [python/OpenVINO_EP/tiny_yolo_v2_object_detection/tiny_yolov2_obj_detection_sample.py:1-222](), [python/OpenVINO_EP/tiny_yolo_v2_object_detection/README.md:1-68]()

### Device Support and Configuration

| Device Type | Precision | Use Case |
|-------------|-----------|----------|
| `CPU_FP32` | Float32 | General CPU inference |
| `GPU_FP32` | Float32 | Intel GPU acceleration |
| `GPU_FP16` | Float16 | Optimized GPU inference |
| `MYRIAD_FP16` | Float16 | Intel Neural Compute Stick |

Sources: [python/OpenVINO_EP/yolov4_object_detection/README.md:60-61](), [python/OpenVINO_EP/tiny_yolo_v2_object_detection/README.md:32]()

## LLaMA-2 Large Language Model Examples

The LLaMA-2 examples demonstrate end-to-end large language model workflows including export, optimization, quantization, and inference using ONNX Runtime.

### Model Export and Optimization Pipeline

```mermaid
graph LR
    subgraph "HuggingFace Model"
        A["meta-llama/Llama-2-7b-hf"]
        B["LlamaConfig.from_pretrained()"]
        C["LlamaTokenizer.from_pretrained()"]
    end
    
    subgraph "ONNX Conversion"
        D["convert_to_onnx.py"]
        E["--precision fp16/int4"]
        F["--use_gqa"]
        G["--quantization_method blockwise"]
    end
    
    subgraph "Optimized ONNX Output"
        H["rank_0_Llama-2-7b-hf_decoder_merged_model_fp16.onnx"]
        I["GroupQueryAttention"]
        J["Optimized Graph"]
    end
    
    A --> B
    A --> C
    B --> D
    C --> D
    D --> E
    D --> F
    D --> G
    E --> H
    F --> I
    G --> J
```

Sources: [python/models/llama/LLaMA-2 E2E Notebook.ipynb:547-628](), [python/models/llama/README.md:1-4]()

### Inference Architecture

The LLaMA-2 inference implementation demonstrates advanced ONNX Runtime features including IO binding and KV cache management.

```mermaid
graph TD
    subgraph "Input Preparation"
        A["tokenizer.batch_encode_plus()"]
        B["get_initial_inputs_and_outputs()"]
        C["torch.tensor() device allocation"]
    end
    
    subgraph "ONNX Runtime Session"
        D["ort.InferenceSession()"]
        E["CUDAExecutionProvider"]
        F["apply_io_binding()"]
        G["io_binding.bind_input()"]
        H["io_binding.bind_output()"]
    end
    
    subgraph "Generation Loop"
        I["model.run_with_iobinding()"]
        J["torch.argmax() token sampling"]
        K["KV cache buffer sharing"]
        L["attention_mask updates"]
    end
    
    subgraph "Output Processing"
        M["tokenizer.batch_decode()"]
        N["Generated Text"]
    end
    
    A --> B
    B --> C
    C --> D
    D --> E
    E --> F
    F --> G
    G --> H
    H --> I
    I --> J
    J --> K
    K --> L
    L --> I
    I --> M
    M --> N
```

Sources: [python/models/llama/LLaMA-2 E2E Notebook.ipynb:1305-1351](), [python/models/llama/LLaMA-2 E2E Notebook.ipynb:1403-1463](), [python/models/llama/LLaMA-2 E2E Notebook.ipynb:1501-1557]()

### Performance Benchmarks

The LLaMA-2 examples include comprehensive performance benchmarks across different model sizes and hardware configurations.

| Model | Batch Size | Prompt Length | Throughput (tps) | Latency (ms) |
|-------|------------|---------------|------------------|--------------|
| LLaMA-2 7B FP16 | 1 | 16 | 95.01 | 10.52 |
| LLaMA-2 7B FP16 | 4 | 16 | 366.29 | 10.92 |
| LLaMA-2 7B FP16 | 16 | 16 | 1385.42 | 11.55 |

Sources: [python/models/llama/README.md:7-26]()

### Advanced Features

#### IO Binding and Memory Management

The LLaMA-2 implementation demonstrates advanced ONNX Runtime features for optimal GPU memory utilization.

```python
# Key functions from the implementation
def get_initial_inputs_and_outputs(config, tokenizer, prompt, device, use_fp16, use_buffer_share)
def apply_io_binding(model, inputs, outputs, use_fp16, use_buffer_share)
```

#### GroupQueryAttention Buffer Sharing

When `use_buffer_share=True`, the implementation enables memory sharing between present and past KV cache tensors, reducing memory overhead.

Sources: [python/models/llama/LLaMA-2 E2E Notebook.ipynb:1608-1649](), [python/models/llama/LLaMA-2 E2E Notebook.ipynb:1651-1706]()

## Common Dependencies and Requirements

### OpenVINO Examples Dependencies

The OpenVINO examples share common Python dependencies managed through `requirements.txt` files:

- `onnx` - ONNX model format support
- `opencv-python` - Computer vision operations
- `scipy` - Scientific computing functions
- `Pillow` - Image processing
- `protobuf==3.20.2` - Protocol buffer serialization

Sources: [python/OpenVINO_EP/yolov4_object_detection/requirements.txt:1-9](), [python/OpenVINO_EP/tiny_yolo_v2_object_detection/requirements.txt:1-9]()

### LLaMA-2 Dependencies

The LLaMA-2 examples require additional packages for transformer model handling:

- `transformers>=4.33.2` - Hugging Face transformers
- `torch>=2.2.0.dev` - PyTorch framework
- `onnxruntime-gpu>=1.16.2` - ONNX Runtime with CUDA support
- `datasets>=2.8.0` - Dataset handling utilities

Sources: [python/models/llama/LLaMA-2 E2E Notebook.ipynb:118-326]()

## Integration Patterns

### Execution Provider Selection

Both example categories demonstrate consistent patterns for execution provider configuration:

```python
# CPU execution
sess = rt.InferenceSession(model_path, providers=['CPUExecutionProvider'])

# OpenVINO execution  
sess = rt.InferenceSession(model_path, providers=['OpenVINOExecutionProvider'], 
                          provider_options=[{'device_type': device}])

# CUDA execution
sess = rt.InferenceSession(model_path, providers=['CUDAExecutionProvider'])
```

Sources: [python/OpenVINO_EP/yolov4_object_detection/yolov4.py:280-287](), [python/models/llama/LLaMA-2 E2E Notebook.ipynb:1385-1387]()

---

