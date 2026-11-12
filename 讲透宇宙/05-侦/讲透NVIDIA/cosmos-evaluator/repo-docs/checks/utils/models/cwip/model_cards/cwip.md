# CWIP Overview

## Description:  
CWIP (Contrastive World-Image Pre-training) projects a camera frame and a world-model frame into a joint embedding space to score camera-to-world consistency and emit per-patch object-presence and object-type classifications. It was developed by NVIDIA as part of Cosmos Evaluator for automated quality scoring of generative world foundation models.  

This model is ready for commercial or non-commercial use.  


### License/Terms of Use:
[OpenMDW-1.1](https://openmdw.ai/license/1-1)
### Deployment Geography:  
Global

### Use Case:  
Developers and researchers building, evaluating, or auditing generative world foundation models for autonomous driving, including users of NVIDIA Cosmos and the open-source Cosmos Evaluator suite. Specific applications include per-frame embeddings, alignment scoring, per-patch defect detection, object-type classification, and automated quality scoring of driving-video generations.  
  

### Release Date:
**GitHub:** 07/07/2026 via https://github.com/NVIDIA/cosmos-evaluator  
**NGC:** 07/07/2026 via https://catalog.ngc.nvidia.com/orgs/nvidia/cosmos/models/cwip  
**HuggingFace:** 07/07/2026 via https://huggingface.co/nvidia/CWIP-1.0  

## Reference(s):
[Perception Encoder: The best visual embeddings are not at the output of the network](https://arxiv.org/abs/2504.13181)  
[Learning Transferable Visual Models From Natural Language Supervision](https://arxiv.org/abs/2103.00020)  
[Deformable DETR: Deformable Transformers for End-to-End Object Detection](https://arxiv.org/abs/2010.04159)  
[Sigmoid Loss for Language Image Pre-Training](https://arxiv.org/abs/2303.15343)  

## Model Architecture:   
**Architecture Type:** Transformer   
**Network Architecture:**
A custom dual-encoder architecture that encodes a pair of world-model control frame and camera frame, and outputs global embeddings for each frame and two segmentation masks for consistency and object-type prediction respectively. [PE-Spatial-B16-512](https://huggingface.co/facebook/PE-Spatial-B16-512) is used as the frozen image encoder in v1.0; only the alignment layers and patch classifier are trained, on 1280x720 frame pairs.

Model is trained and tested with BF16 precision. The inference code supports a camera-only mode that skips world-model input and processing.  

![CWIP v1.0 architecture](assets/cwip_arch.png)

**This model was developed based on PE-Spatial-B16-512 (used frozen).**  
**Number of model parameters:** 0.3B (0.3*10^9)  
  
 
## Input:  
**Input Type(s):** Image  
**Input Format(s):** RGB (Red, Green, Blue)  
**Input Parameters:** Three-Dimensional (3D)  
**Other Properties Related to Input:** The model accepts a paired camera frame and world-model frame as input, where world-model frames are visual representations of autonomous-driving-relevant scene elements. The pair is encoded into per-frame embeddings used for camera-to-world consistency scoring, per-patch defect detection, and object-type classification. Camera and world frames must share spatial dimensions (the camera frame is resized to match the world frame if they differ). Trainable layers were trained and evaluated at 1280x720 frame pairs; other resolutions are supported via RoPE2D and bilinear interpolation of the encoder's absolute position embedding. The inference code also supports a camera-only mode where only the camera frame is required and the world encoder is skipped.  
  

## Output:  
**Output Type(s):** Embeddings, Segmentation Masks  
**Output Format:** Tensor, Tensor  
**Output Parameters:** One-Dimensional (1D), Three-Dimensional (3D)  
**Other Properties Related to Output:** The model outputs per-frame L2-normalized 1024-dimensional global embedding vectors for world-model frame and camera frame, per-patch defect classifications (MATCH, EXTRA, MISSING, WRONG, DONT_CARE) and object-type classifications over an 18-class taxonomy. These outputs are used for automated quality scoring of driving-video generations. Defect classification masks (MATCH+EXTRA+WRONG) may be used to filter object-type classification to improve precision. In camera-only mode, only camera embeddings and object-type classifications are produced.  
   
Our AI models are designed and/or optimized to run on NVIDIA GPU-accelerated systems. By leveraging NVIDIA's hardware (e.g. GPU cores) and software frameworks (e.g., CUDA libraries), the model achieves faster training and inference times compared to CPU-only solutions.

## Software Integration:
**Runtime Engine(s):** 
* PyTorch
* Transformers (optional)    

**Supported Hardware Microarchitecture Compatibility:**
* NVIDIA Ampere
* NVIDIA Hopper
* NVIDIA Lovelace

**Supported Operating System(s):** Linux  

The integration of foundation and fine-tuned models into AI systems requires additional testing using use-case-specific data to ensure safe and effective deployment. Following the V-model methodology, iterative testing and validation at both unit and system levels are essential to mitigate risks, meet technical and functional requirements, and ensure compliance with safety and ethical standards before deployment.  


## Model Version(s): 
CWIP v1.0  

Model weights are stored in HuggingFace safetensors format. PyTorch is required for inference. See [Cosmos Evaluator](https://github.com/NVIDIA/cosmos-evaluator/tree/main/checks/utils/models/cwip) repo for reference usage.  
 
## Training and Evaluation Datasets:  


## Training Dataset:

**Data Modality:** Video  

**Video Training Data Size:** Less than 10,000 Hours  
**Data Collection Method by dataset:** Automated  
**Labeling Method by dataset:** Automated  
**Properties (Quantity, Dataset Descriptions, Sensor(s)):** Approximately 136,000 camera and world-model video pairs of driving scenes. Each video is approximately 20 seconds long.

### Evaluation Dataset:

**Data Collection Method by dataset:** Hybrid: Automated/Synthetic  
**Labeling Method by dataset:** Hybrid: Automated/Manually-Labeled/Synthetic  
**Properties (Quantity, Dataset Descriptions, Sensor(s)):** Approximately 7K camera and world-model video pairs of real driving scenes. Each video is ~20 seconds long. Positive and negative frame pairs are sampled from these videos for evaluation. Evaluates Precision, Recall, F1, and IoU, and visual qualitative check.

Approximately 1.2K camera and world-model video pairs of synthetic driving scenes with human labels. Each video is ~10 seconds long. Evaluates missing objects and hallucinations, and visual qualitative check.


## Inference:
**Acceleration Engine:** PyTorch  
**Test Hardware:**  NVIDIA Hopper (H100)

## Ethical Considerations:
NVIDIA believes Trustworthy AI is a shared responsibility and we have established policies and practices to enable development for a wide array of AI applications. Developers should work with their internal model team to ensure this model meets requirements for the relevant industry and use case and addresses unforeseen product misuse.

Please make sure you have proper rights and permissions for all input image and video content; if image or video includes people, personal health information, or intellectual property, the image or video generated will not blur or maintain proportions of image subjects included.

For more detailed information on ethical considerations for this model, please see the Model Card++ Explainability, Bias, Safety & Security, and Privacy Subcards.  
  
Please report model quality, risk, security vulnerabilities or NVIDIA AI Concerns [here](https://app.intigriti.com/programs/nvidia/nvidiavdp/detail).