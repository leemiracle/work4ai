<!-- source: DeepWiki mcp.deepwiki.com · repo google-deepmind/perception_test · page 3 Tasks · fetched 2026-10-26 -->

# Tasks

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)

</details>



## Purpose and Scope

This page documents the six perceptual and reasoning tasks that comprise the Perception Test benchmark. Each task is designed to evaluate specific capabilities of multimodal video models across visual, audio, and textual modalities. This document covers task definitions, input/output specifications, and performance metrics for each task. For information about the dataset structure and organization, see [Dataset](#2). For evaluation details and metrics computation, see [Evaluation](#4).

## Overview of Tasks

The Perception Test benchmark consists of six distinct tasks organized into three categories: tracking tasks, localization tasks, and question-answering tasks. Each task evaluates different perceptual and reasoning capabilities.

```mermaid
graph TD
    A["Perception Test Tasks"] --> B["Tracking Tasks"]
    A --> C["Localization Tasks"]
    A --> D["Question-Answering Tasks"]
    
    B --> B1["Object Tracking"]
    B --> B2["Point Tracking"]
    
    C --> C1["Action Localization"]
    C --> C2["Sound Localization"]
    
    D --> D1["Multiple-Choice Video QA"]
    D --> D2["Grounded Video QA"]
    
    subgraph "Memory & Physics"
    B1
    B2
    end
    
    subgraph "Event Understanding"
    C1
    C2
    end
    
    subgraph "Multimodal Reasoning"
    D1
    D2
    end
```

Sources: [README.md:139-147]()

## Task Categories and Relationships

Each task evaluates specific capabilities of multimodal video models and uses defined evaluation metrics to measure performance. The table below summarizes the tasks and their associated metrics:

| Task Category | Task Name | Primary Skill | Evaluation Metric |
|--------------|-----------|---------------|-------------------|
| Tracking     | Object Tracking | Visual tracking, occlusion reasoning | Average IoU |
| Tracking     | Point Tracking | Motion understanding, fine-grained tracking | Average Jaccard |
| Localization | Action Localization | Action recognition, temporal segmentation | Mean Average Precision |
| Localization | Sound Localization | Audio-visual correlation | Mean Average Precision |
| QA           | Multiple-Choice Video QA | Reasoning across modalities | Top-1 Accuracy |
| QA           | Grounded Video QA | Referential understanding | HOTA |

Sources: [README.md:155-162]()

## Tracking Tasks

Tracking tasks evaluate a model's ability to continuously locate and follow objects or points across video frames, testing spatial reasoning and memory capabilities.

### Single Object Tracking

Single Object Tracking requires models to track the position of a specified object throughout a video sequence.

```mermaid
flowchart LR
    A["Input Video"] --> B["Initial Object Bounding Box"]
    B --> C["Tracking Model"]
    C --> D["Predicted Bounding Boxes"]
    D --> E["Evaluation: Average IoU"]
    
    subgraph "Data Format"
    F["object_tracks.id"]
    G["object_tracks.bounding_boxes"]
    H["object_tracks.initial_tracking_box"]
    end
    
    F -.-> B
    G -.-> E
    H -.-> B
```

**Task Definition**: Given a video and the initial bounding box of an object in the first frame, predict the bounding box coordinates of the same object in all subsequent frames.

**Input**:
- Video sequence
- Initial object bounding box coordinates [x1, y1, x2, y2]

**Output**:
- Bounding box coordinates for all frames

**Evaluation Metric**: Average Intersection over Union (IoU) between predicted and ground-truth bounding boxes.

**Baseline**: Static baseline that keeps the initial bounding box constant throughout the video.

Sources: [README.md:76-83](), [README.md:142-142](), [README.md:157-157](), [README.md:197-210]()

### Single Point Tracking

Single Point Tracking requires models to track specific points on objects throughout a video sequence.

```mermaid
flowchart LR
    A["Input Video"] --> B["Initial Point Coordinates"]
    B --> C["Tracking Model"]
    C --> D["Predicted Point Coordinates"]
    D --> E["Evaluation: Average Jaccard"]
    
    subgraph "Data Format"
    F["point_tracks.id"]
    G["point_tracks.points"]
    H["point_tracks.parent_objects"]
    end
    
    F -.-> B
    G -.-> E
    H -.-> B
```

**Task Definition**: Given a video and the initial coordinates of a point in the first frame, predict the coordinates of the same point in all subsequent frames.

**Input**:
- Video sequence
- Initial point coordinates [y, x]

**Output**:
- Point coordinates for all frames

**Evaluation Metric**: Average Jaccard similarity between predicted and ground-truth points.

**Baseline**: Static baseline that keeps the initial point location constant throughout the video.

Sources: [README.md:86-93](), [README.md:143-143](), [README.md:158-158](), [README.md:212-221]()

## Localization Tasks

Localization tasks evaluate a model's ability to identify when specific events occur in videos, testing temporal reasoning and multimodal understanding.

### Temporal Action Localization

Temporal Action Localization requires models to identify when specific actions occur within a video.

```mermaid
flowchart LR
    A["Input Video"] --> B["Feature Extraction"]
    B --> C["Action Localization Model"]
    C --> D["Predicted Action Segments"]
    D --> E["Evaluation: Mean Average Precision"]
    
    subgraph "Data Format"
    F["action_segments.id"]
    G["action_segments.label"]
    H["action_segments.timestamps"]
    end
    
    F -.-> D
    G -.-> C
    H -.-> E
```

**Task Definition**: Given a video, identify all action segments and classify them according to predefined action categories.

**Input**:
- Video sequence
- Optional pre-computed TSP video features

**Output**:
- List of detected action segments with start/end timestamps and class labels

**Evaluation Metric**: Mean Average Precision (mAP) at various temporal IoU thresholds.

**Baseline**: ActionFormer model fine-tuned on Perception Test data.

Sources: [README.md:96-103](), [README.md:144-144](), [README.md:159-159](), [README.md:222-232]()

### Temporal Sound Localization

Temporal Sound Localization requires models to identify when specific sounds occur within a video's audio track.

```mermaid
flowchart LR
    A["Input Video + Audio"] --> B["Feature Extraction"]
    B --> C["Sound Localization Model"]
    C --> D["Predicted Sound Segments"]
    D --> E["Evaluation: Mean Average Precision"]
    
    subgraph "Data Format"
    F["sound_segments.id"]
    G["sound_segments.label"]
    H["sound_segments.timestamps"]
    I["sound_segments.is_visible"]
    end
    
    F -.-> D
    G -.-> C
    H -.-> E
    I -.-> C
```

**Task Definition**: Given a video with audio, identify all sound segments and classify them according to predefined sound categories.

**Input**:
- Video sequence with audio
- Optional pre-computed MMV audio features

**Output**:
- List of detected sound segments with start/end timestamps and class labels

**Evaluation Metric**: Mean Average Precision (mAP) at various temporal IoU thresholds.

**Baseline**: ActionFormer model fine-tuned on Perception Test data.

Sources: [README.md:107-114](), [README.md:145-145](), [README.md:160-160](), [README.md:235-246]()

## Question-Answering Tasks

Question-Answering tasks evaluate a model's ability to reason about video content and answer natural language questions, testing high-level understanding and integration of multiple modalities.

### Multiple-Choice Video QA

Multiple-Choice Video QA requires models to answer questions about video content by selecting from provided options.

```mermaid
flowchart LR
    A["Input Video + Audio"] --> C["QA Model"]
    B["Question + Options"] --> C
    C --> D["Predicted Answer"]
    D --> E["Evaluation: Top-1 Accuracy"]
    
    subgraph "Data Format"
    F["mc_question.id"]
    G["mc_question.question"]
    H["mc_question.options"]
    I["mc_question.answer_id"]
    J["mc_question.area"]
    K["mc_question.reasoning"]
    end
    
    F -.-> B
    G -.-> B
    H -.-> B
    I -.-> E
    J -.-> C
    K -.-> C
```

**Task Definition**: Given a video and a question with multiple-choice options, select the correct answer from the options.

**Input**:
- Video sequence with audio
- Question text
- Answer options (3 choices)

**Output**:
- Selected answer option ID

**Evaluation Metric**: Top-1 Accuracy.

**Baseline**: Frequency baseline using statistics from training question/answer pairs.

Sources: [README.md:117-124](), [README.md:146-146](), [README.md:161-161](), [README.md:249-260]()

### Grounded Video QA

Grounded Video QA requires models to answer questions about video content by identifying specific objects in the video.

```mermaid
flowchart LR
    A["Input Video + Audio"] --> C["Grounded QA Model"]
    B["Question"] --> C
    C --> D["Predicted Object IDs"]
    D --> E["Evaluation: HOTA"]
    
    subgraph "Data Format"
    F["grounded_question.id"]
    G["grounded_question.question"]
    H["grounded_question.answers"]
    I["grounded_question.area"]
    J["grounded_question.reasoning"]
    K["object_tracks.id"]
    end
    
    F -.-> B
    G -.-> B
    H -.-> E
    I -.-> C
    J -.-> C
    K -.-> D
```

**Task Definition**: Given a video and a question, identify the object(s) in the video that correctly answer the question.

**Input**:
- Video sequence with audio
- Question text

**Output**:
- List of object IDs that answer the question

**Evaluation Metric**: Higher Order Tracking Accuracy (HOTA) between predicted and ground-truth object references.

**Baseline**: MDETR for open-vocabulary object detection combined with static tracking.

Sources: [README.md:126-133](), [README.md:147-147](), [README.md:162-162](), [README.md:263-272]()

## Task Implementation and Code Organization

The following diagram shows how the task definitions relate to their baseline implementations in the codebase:

```mermaid
flowchart TD
    A["Perception Test Tasks"] --> B["Task Definitions"]
    B --> C["Baseline Implementations"]
    
    subgraph "Notebook Implementations"
    C1["single_object_tracking.ipynb"]
    C2["single_point_tracking.ipynb"]
    C3["temporal_action_localisation.ipynb"]
    C4["temporal_sound_localisation.ipynb"]
    C5["mc_vqa.ipynb"]
    C6["grounded_vqa.ipynb"]
    end
    
    C --> C1
    C --> C2
    C --> C3
    C --> C4
    C --> C5
    C --> C6
    
    subgraph "Baseline Models"
    D1["Static"]
    D2["Static"]
    D3["ActionFormer"]
    D4["ActionFormer"]
    D5["Frequency"]
    D6["MDETR + static"]
    end
    
    C1 --> D1
    C2 --> D2
    C3 --> D3
    C4 --> D4
    C5 --> D5
    C6 --> D6
```

The implementation of each task is provided in separate Jupyter notebooks, which serve as examples for loading data, implementing baseline models, and evaluating performance.

Sources: [README.md:137-147](), [README.md:155-162]()

## Skill Areas and Reasoning Types

Each task in the Perception Test is designed to evaluate specific skill areas and reasoning types:

| Skill Area | Description | Related Tasks |
|------------|-------------|---------------|
| Memory | Ability to track and recall events | Object Tracking, Point Tracking, Multiple-Choice QA, Grounded QA |
| Abstraction | Understanding patterns and generalizations | Multiple-Choice QA, Grounded QA |
| Physics | Understanding physical interactions | Object Tracking, Point Tracking, Action Localization, Multiple-Choice QA, Grounded QA |
| Semantics | Understanding meaning and relationships | Action Localization, Sound Localization, Multiple-Choice QA, Grounded QA |

| Reasoning Type | Description | Related Tasks |
|----------------|-------------|---------------|
| Descriptive | What is happening | Multiple-Choice QA, Grounded QA |
| Explanatory | Why something happened | Multiple-Choice QA, Grounded QA |
| Predictive | What will happen next | Multiple-Choice QA, Grounded QA |
| Counterfactual | What would happen if | Multiple-Choice QA, Grounded QA |

These skill areas and reasoning types are explicitly annotated for the question-answering tasks and implicitly tested in the tracking and localization tasks.

Sources: [README.md:249-260](), [README.md:263-272]()

---

