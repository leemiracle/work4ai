<!-- source: DeepWiki mcp.deepwiki.com · repo rohitg00/ai-engineering-from-scratch · page 9 Phase 4 & 5: Computer Vision & NLP · fetched 2026-10-30 -->

# Phase 4 & 5: Computer Vision & NLP

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [phases/04-computer-vision/06-object-detection-yolo/code/main.py](phases/04-computer-vision/06-object-detection-yolo/code/main.py)
- [phases/04-computer-vision/06-object-detection-yolo/docs/en.md](phases/04-computer-vision/06-object-detection-yolo/docs/en.md)
- [phases/04-computer-vision/06-object-detection-yolo/outputs/prompt-detection-metric-reader.md](phases/04-computer-vision/06-object-detection-yolo/outputs/prompt-detection-metric-reader.md)
- [phases/04-computer-vision/06-object-detection-yolo/outputs/skill-anchor-designer.md](phases/04-computer-vision/06-object-detection-yolo/outputs/skill-anchor-designer.md)
- [phases/04-computer-vision/06-object-detection-yolo/quiz.json](phases/04-computer-vision/06-object-detection-yolo/quiz.json)
- [phases/05-nlp-foundations-to-advanced/01-text-processing/assets/pipeline.svg](phases/05-nlp-foundations-to-advanced/01-text-processing/assets/pipeline.svg)
- [phases/05-nlp-foundations-to-advanced/01-text-processing/docs/en.md](phases/05-nlp-foundations-to-advanced/01-text-processing/docs/en.md)
- [phases/05-nlp-foundations-to-advanced/02-bag-of-words-tfidf/docs/en.md](phases/05-nlp-foundations-to-advanced/02-bag-of-words-tfidf/docs/en.md)
- [phases/05-nlp-foundations-to-advanced/03-word-embeddings-word2vec/docs/en.md](phases/05-nlp-foundations-to-advanced/03-word-embeddings-word2vec/docs/en.md)
- [phases/05-nlp-foundations-to-advanced/05-sentiment-analysis/docs/en.md](phases/05-nlp-foundations-to-advanced/05-sentiment-analysis/docs/en.md)
- [phases/05-nlp-foundations-to-advanced/06-named-entity-recognition/docs/en.md](phases/05-nlp-foundations-to-advanced/06-named-entity-recognition/docs/en.md)
- [phases/05-nlp-foundations-to-advanced/07-pos-tagging-parsing/docs/en.md](phases/05-nlp-foundations-to-advanced/07-pos-tagging-parsing/docs/en.md)
- [phases/05-nlp-foundations-to-advanced/09-sequence-to-sequence/docs/en.md](phases/05-nlp-foundations-to-advanced/09-sequence-to-sequence/docs/en.md)
- [phases/05-nlp-foundations-to-advanced/17-chatbots-rule-to-neural/docs/en.md](phases/05-nlp-foundations-to-advanced/17-chatbots-rule-to-neural/docs/en.md)

</details>



This phase transitions from general deep learning foundations into the two primary domains of modern AI: **Computer Vision (CV)** and **Natural Language Processing (NLP)**. Across 57 lessons, the curriculum covers the evolution from classical feature engineering (Porter stemmers, HOG features) to state-of-the-art architectures like Vision Transformers (ViT) and Retrieval-Augmented Generation (RAG).

The goal is to move from "Language/Images are continuous" to "Models are discrete" by building the bridges—preprocessing pipelines, convolutional filters, and embedding spaces—from scratch.

## Computer Vision: CNNs, Detection & Generation

The Computer Vision phase (Phase 4) covers the spatial reasoning capabilities of AI. It begins with image fundamentals and progresses through the lineage of Convolutional Neural Networks (CNNs), moving from simple classification to complex tasks like object detection and image synthesis.

Key implementations include:
*   **Architectures:** From LeNet and ResNet to Vision Transformers (ViT).
*   **Object Detection:** Implementing the `YOLOHead` [phases/04-computer-vision/06-object-detection-yolo/code/main.py:69-81]() and `yolo_loss` [phases/04-computer-vision/06-object-detection-yolo/code/main.py:121-152]() to understand grid-based spatial prediction.
*   **Segmentation:** U-Net for semantic segmentation and Mask R-CNN for instance-level detail.
*   **Generative Models:** GANs and the math behind Diffusion models.

For details on anchors, YOLO, and vision transformers, see **[Computer Vision: CNNs, Detection & Generation](#9.1)**.

### Vision System to Code Entity Mapping

The following diagram bridges the conceptual "Detection Pipeline" to the specific code entities implemented in the YOLO lesson.

```mermaid
graph TD
    subgraph "Image Space"
        ["Input Image"] --> ["Grid Cells"]
    end

    subgraph "Code Entity Space (YOLO Implementation)"
        ["Grid Cells"] --> ["assign_targets()"]
        ["assign_targets()"] -- "Anchors" --> ["YOLOHead"]
        ["YOLOHead"] -- "Logits" --> ["yolo_loss()"]
        ["yolo_loss()"] -- "MSE/BCE" --> ["Total Loss"]
        
        ["YOLOHead"] -- "Inference" --> ["postprocess()"]
        ["postprocess()"] --> ["nms()"]
        ["nms()"] -- "IOU Threshold" --> ["Final Detections"]
    end

    style ["assign_targets()"] stroke-dasharray: 5 5
    style ["YOLOHead"] stroke-width: 2px
```
**Sources:** [phases/04-computer-vision/06-object-detection-yolo/code/main.py:69-184](), [phases/04-computer-vision/06-object-detection-yolo/docs/en.md]()

---

## NLP Foundations: Text Processing to Seq2Seq

Phase 5 (Lessons 01–10) focuses on the transition from raw strings to mathematical representations. It covers the "classical" stack that remains the bedrock of production NLP: tokenization, stemming, lemmatization, and vectorization.

*   **Preprocessing:** Building a regex `tokenize` function [phases/05-nlp-foundations-to-advanced/01-text-processing/docs/en.md:41-43]() and a Porter `stem_step_1a` [phases/05-nlp-foundations-to-advanced/01-text-processing/docs/en.md:59-69]().
*   **Representation:** Implementing `bag_of_words` [phases/05-nlp-foundations-to-advanced/02-bag-of-words-tfidf/docs/en.md:54-61]() and `tfidf` [phases/05-nlp-foundations-to-advanced/02-bag-of-words-tfidf/docs/en.md:100-110]().
*   **Sequence Modeling:** The `Encoder` [phases/05-nlp-foundations-to-advanced/09-sequence-to-sequence/docs/en.md:41-51]() and `Decoder` [phases/05-nlp-foundations-to-advanced/09-sequence-to-sequence/docs/en.md:58-70]() pattern that defines the Seq2Seq era.

For details on the NLP pipeline and early sequence models, see **[NLP Foundations: Text Processing to Seq2Seq](#9.2)**.

### NLP Pipeline Visualization

```mermaid
graph LR
    ["Raw Text"] -- "re.findall" --> ["Tokens"]
    ["Tokens"] -- "Porter Stemmer" --> ["Stems"]
    ["Tokens"] -- "Lookup Table" --> ["Lemmas"]
    ["Lemmas"] -- "Counter()" --> ["BoW Vector"]
    ["BoW Vector"] -- "log(N/df)" --> ["TF-IDF Matrix"]
```
**Sources:** [phases/05-nlp-foundations-to-advanced/01-text-processing/docs/en.md:20-129](), [phases/05-nlp-foundations-to-advanced/02-bag-of-words-tfidf/docs/en.md:20-110]()

---

## Advanced NLP: IR, QA, Summarization & Multilingual

The latter half of Phase 5 (Lessons 11–29) moves into high-level tasks that define modern AI engineering. This section covers how models interact with external knowledge and generate complex outputs.

*   **Information Retrieval (IR):** Moving from BM25 to dense retrieval and hybrid search.
*   **Question Answering & RAG:** Building systems that ground generation in retrieved documents.
*   **Chatbot Evolution:** Transitioning from `rule_based_respond` [phases/05-nlp-foundations-to-advanced/17-chatbots-rule-to-neural/docs/en.md:54-60]() to an `agent_loop` [phases/05-nlp-foundations-to-advanced/17-chatbots-rule-to-neural/docs/en.md:114-137]() that uses tools.
*   **Multilingual NLP:** Handling the "tokenization tax" and zero-shot cross-lingual transfer.

For details on RAG, agent loops, and multilingual strategies, see **[Advanced NLP: IR, QA, Summarization & Multilingual](#9.3)**.

### Chatbot Architecture Evolution

The curriculum tracks the evolution of conversational agents from simple pattern matching to tool-using loops.

| Paradigm | Core Logic | Code Entity Example |
| :--- | :--- | :--- |
| **Rule-Based** | Regex Matching | `RulePattern` [phases/05-nlp-foundations-to-advanced/17-chatbots-rule-to-neural/docs/en.md:40-44]() |
| **Retrieval** | Vector Similarity | `faq_respond` [phases/05-nlp-foundations-to-advanced/17-chatbots-rule-to-neural/docs/en.md:85-92]() |
| **Neural** | Seq2Seq Generation | `Encoder` / `Decoder` [phases/05-nlp-foundations-to-advanced/09-sequence-to-sequence/docs/en.md:41-70]() |
| **Agentic** | Tool-Use Loop | `agent_loop` [phases/05-nlp-foundations-to-advanced/17-chatbots-rule-to-neural/docs/en.md:114-137]() |

**Sources:** [phases/05-nlp-foundations-to-advanced/17-chatbots-rule-to-neural/docs/en.md:18-30](), [phases/05-nlp-foundations-to-advanced/09-sequence-to-sequence/docs/en.md:18-31]()

---

## Toolkit Artifacts

These phases produce several critical reusable artifacts in the `outputs/` directory:

*   `skill-anchor-designer`: A utility for calculating dataset-specific YOLO anchors using K-Means [phases/04-computer-vision/06-object-detection-yolo/outputs/skill-anchor-designer.md:1-8]().
*   `prompt-detection-metric-reader`: A diagnostic tool for interpreting `mAP` and `precision/recall` trade-offs [phases/04-computer-vision/06-object-detection-yolo/outputs/prompt-detection-metric-reader.md:1-6]().
*   `skill-noise-schedule-designer`: For configuring diffusion model training.
*   `agent_loop`: The standard interface for tool-calling LLMs [phases/05-nlp-foundations-to-advanced/17-chatbots-rule-to-neural/docs/en.md:114]().

**Sources:** [phases/04-computer-vision/06-object-detection-yolo/outputs/skill-anchor-designer.md](), [phases/04-computer-vision/06-object-detection-yolo/outputs/prompt-detection-metric-reader.md](), [phases/05-nlp-foundations-to-advanced/17-chatbots-rule-to-neural/docs/en.md]()

---

