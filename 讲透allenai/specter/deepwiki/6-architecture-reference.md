<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/specter · page 6 Architecture Reference · fetched 2026-10-26 -->

# Architecture Reference

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [specter/__init__.py](specter/__init__.py)
- [specter/model.py](specter/model.py)

</details>



This document provides technical details about SPECTER's internal architecture and code components. It covers the core model implementation, loss functions, data processing pipeline, and prediction infrastructure at the code level.

For information about using SPECTER's interfaces, see [User Guide](#4). For training procedures, see [Training Models](#4.2). For data format specifications, see [Data Formats](#5).

## Core Architecture Overview

SPECTER's architecture consists of several key components implemented as Python classes that work together to create document embeddings from academic papers.

### Main Architecture Diagram

```mermaid
graph TB
    subgraph "Core Classes"
        Specter["Specter<br/>(specter.model.Specter)"]
        SpecterPredictor["SpecterPredictor<br/>(specter.predictor.SpecterPredictor)"]
        DataReader["DataReader<br/>(specter.data.DataReader)"]
        DataReaderFromPickled["DataReaderFromPickled<br/>(specter.data.DataReaderFromPickled)"]
    end
    
    subgraph "Loss Functions"
        TripletLoss["TripletLoss<br/>(specter.model.TripletLoss)"]
        BinaryLoss["BinaryLoss<br/>(specter.model.BinaryLoss)"]
        TripletMarginLoss["TripletMarginLoss<br/>(torch.nn.TripletMarginLoss)"]
    end
    
    subgraph "AllenNLP Components"
        TextFieldEmbedder["TextFieldEmbedder<br/>(text_field_embedder)"]
        Seq2VecEncoder["Seq2VecEncoder<br/>(title_encoder, abstract_encoder, venue_encoder)"]
        FeedForward["FeedForward<br/>(feedforward)"]
        Vocabulary["Vocabulary<br/>(vocab)"]
    end
    
    subgraph "Training Infrastructure"
        Model["Model<br/>(allennlp.models.model.Model)"]
        InitializerApplicator["InitializerApplicator<br/>(initializer)"]
        RegularizerApplicator["RegularizerApplicator<br/>(regularizer)"]
    end
    
    DataReader --> Specter
    DataReaderFromPickled --> Specter
    Specter --> SpecterPredictor
    
    Specter --> TripletLoss
    Specter --> BinaryLoss
    Specter --> TripletMarginLoss
    
    Specter --> TextFieldEmbedder
    Specter --> Seq2VecEncoder
    Specter --> FeedForward
    Specter --> Vocabulary
    
    Model --> Specter
    InitializerApplicator --> Specter
    RegularizerApplicator --> Specter
```

Sources: [specter/__init__.py:1-3](), [specter/model.py:111-142]()

## Model Components Architecture

The `Specter` class inherits from AllenNLP's `Model` class and implements the core paper embedding functionality through several specialized components.

### Specter Class Component Diagram

```mermaid
graph TB
    subgraph "Specter Class Components"
        Specter["Specter"]
        
        subgraph "Text Processing"
            text_field_embedder["text_field_embedder<br/>(TextFieldEmbedder)"]
            venue_field_embedder["venue_field_embedder<br/>(TextFieldEmbedder)"]
            author_text_embedder["author_text_embedder<br/>(TextFieldEmbedder)"]
        end
        
        subgraph "Encoders"
            title_encoder["title_encoder<br/>(Seq2VecEncoder)"]
            abstract_encoder["abstract_encoder<br/>(Seq2VecEncoder)"]
            venue_encoder["venue_encoder<br/>(Seq2VecEncoder)"]
            body_encoder["body_encoder<br/>(Seq2VecEncoder)"]
            author_text_encoder["author_text_encoder<br/>(Seq2VecEncoder)"]
        end
        
        subgraph "Author Processing"
            author_id_embedder["author_id_embedder<br/>(TextFieldEmbedder)"]
            author_position_embedder["author_position_embedder<br/>(TextFieldEmbedder)"]
            author_time_dist_ff["author_time_dist_ff<br/>(TimeDistributed)"]
        end
        
        subgraph "Output Processing"
            feedforward["feedforward<br/>(FeedForward)"]
            layer_norm["layer_norm<br/>(LayerNorm)"]
            dropout["dropout<br/>(Dropout)"]
        end
        
        subgraph "Loss Functions"
            loss["loss<br/>(TripletLoss|BinaryLoss|TripletMarginLoss)"]
        end
    end
    
    Specter --> text_field_embedder
    Specter --> venue_field_embedder
    Specter --> author_text_embedder
    
    text_field_embedder --> title_encoder
    text_field_embedder --> abstract_encoder
    venue_field_embedder --> venue_encoder
    text_field_embedder --> body_encoder
    author_text_embedder --> author_text_encoder
    
    title_encoder --> feedforward
    venue_encoder --> feedforward
    
    feedforward --> layer_norm
    layer_norm --> dropout
    
    author_id_embedder --> author_time_dist_ff
    author_position_embedder --> author_time_dist_ff
    
    Specter --> loss
```

Sources: [specter/model.py:114-141](), [specter/model.py:147-202]()

### Key Methods and Data Flow

The `Specter` class implements several critical methods that define the data processing pipeline:

| Method | Purpose | Input | Output |
|--------|---------|-------|--------|
| `get_embedding_and_mask()` | Extract embeddings and masks from text fields | `text_field`, `embedder_type` | `embedded_`, `mask_` |
| `_embed_paper()` | Generate paper embeddings from components | `title`, `abstract`, `venue`, etc. | `paper_embedding` |
| `forward()` | Main forward pass for training/inference | All paper fields for source, positive, negative | `loss` or `embedding` |
| `decode()` | Post-process model output | `output_dict` | `output_dict` |

Sources: [specter/model.py:204-214](), [specter/model.py:216-244](), [specter/model.py:248-330](), [specter/model.py:332-334]()

## Loss Functions Architecture

SPECTER implements three different loss functions for training, each with specific distance metrics and use cases.

### Loss Function Class Hierarchy

```mermaid
graph TB
    subgraph "Loss Function Classes"
        nn_Module["nn.Module<br/>(torch.nn.Module)"]
        
        TripletLoss["TripletLoss<br/>(specter.model.TripletLoss)"]
        BinaryLoss["BinaryLoss<br/>(specter.model.BinaryLoss)"]
        TripletMarginLoss["TripletMarginLoss<br/>(torch.nn.TripletMarginLoss)"]
        
        subgraph "TripletLoss Distance Options"
            l2_norm["l2-norm<br/>(F.pairwise_distance)"]
            cosine["cosine<br/>(F.cosine_similarity)"]
            dot["dot<br/>(torch.bmm)"]
        end
        
        subgraph "BinaryLoss Components"
            contrastive_pos["Positive Distance<br/>(F.pairwise_distance)"]
            contrastive_neg["Negative Distance<br/>(F.pairwise_distance)"]
        end
    end
    
    nn_Module --> TripletLoss
    nn_Module --> BinaryLoss
    nn_Module --> TripletMarginLoss
    
    TripletLoss --> l2_norm
    TripletLoss --> cosine
    TripletLoss --> dot
    
    BinaryLoss --> contrastive_pos
    BinaryLoss --> contrastive_neg
```

Sources: [specter/model.py:30-84](), [specter/model.py:86-108](), [specter/model.py:158-163]()

### Loss Function Selection Logic

The loss function is selected in the `Specter` constructor based on the `loss_distance` parameter:

| loss_distance | Loss Class | Implementation |
|---------------|------------|----------------|
| `'l2-norm'` | `torch.nn.TripletMarginLoss` | PyTorch built-in with L2 distance |
| `'binary'` | `BinaryLoss` | Custom contrastive loss implementation |
| `'cosine'` | `TripletLoss` | Custom triplet loss with cosine similarity |
| `'dot'` | `TripletLoss` | Custom triplet loss with dot product |

Sources: [specter/model.py:158-163]()

## Data Processing Pipeline

The data processing pipeline transforms raw paper metadata into model-ready tensors through several specialized components.

### Data Reader Architecture

```mermaid
graph LR
    subgraph "Input Sources"
        raw_papers["Raw Papers<br/>(JSON/JSONL)"]
        pickled_data["Pickled Data<br/>(.pkl files)"]
        citation_graph["Citation Graph<br/>(relationships)"]
    end
    
    subgraph "Data Readers"
        DataReader["DataReader<br/>(specter.data.DataReader)"]
        DataReaderFromPickled["DataReaderFromPickled<br/>(specter.data.DataReaderFromPickled)"]
    end
    
    subgraph "Processing Steps"
        text_to_instance["text_to_instance()<br/>(method)"]
        tokenization["Tokenization<br/>(BERT tokenizer)"]
        field_creation["Field Creation<br/>(TextField, MetadataField)"]
    end
    
    subgraph "Output"
        instance["Instance<br/>(AllenNLP Instance)"]
        batch["Batch<br/>(Dict[str, torch.Tensor])"]
    end
    
    raw_papers --> DataReader
    pickled_data --> DataReaderFromPickled
    citation_graph --> DataReader
    
    DataReader --> text_to_instance
    DataReaderFromPickled --> text_to_instance
    
    text_to_instance --> tokenization
    tokenization --> field_creation
    field_creation --> instance
    instance --> batch
```

Sources: [specter/__init__.py:1-2](), [specter/data.py]()

### Paper Embedding Generation Flow

The `_embed_paper()` method processes individual papers through the following pipeline:

```mermaid
graph TD
    subgraph "Paper Embedding Pipeline"
        input_fields["Input Fields<br/>(title, abstract, venue, etc.)"]
        
        get_embedding_and_mask["get_embedding_and_mask()<br/>(method)"]
        
        subgraph "Field Processing"
            title_processing["Title Processing<br/>(title_encoder)"]
            venue_processing["Venue Processing<br/>(venue_encoder)"]
            dropout_layer["Dropout<br/>(dropout)"]
        end
        
        subgraph "Combination Logic"
            include_venue_check["include_venue<br/>(boolean flag)"]
            concatenation["torch.cat()<br/>(encoded_title, encoded_venue)"]
            title_only["encoded_title<br/>(title only)"]
        end
        
        paper_embedding["paper_embedding<br/>(torch.Tensor)"]
    end
    
    input_fields --> get_embedding_and_mask
    get_embedding_and_mask --> title_processing
    get_embedding_and_mask --> venue_processing
    
    title_processing --> dropout_layer
    venue_processing --> dropout_layer
    
    dropout_layer --> include_venue_check
    include_venue_check --> concatenation
    include_venue_check --> title_only
    
    concatenation --> paper_embedding
    title_only --> paper_embedding
```

Sources: [specter/model.py:216-244]()

## Training vs Inference Mode Architecture

The `Specter` model operates in two distinct modes with different data flows and outputs.

### Mode Selection and Data Flow

```mermaid
graph TB
    subgraph "Model Input"
        forward_method["forward()<br/>(method)"]
        predict_mode_flag["predict_mode<br/>(boolean)"]
        input_validation["Input Validation<br/>(pos_title, neg_title checks)"]
    end
    
    subgraph "Training Mode Flow"
        training_mode["Training Mode<br/>(predict_mode=False)"]
        embed_source["_embed_paper()<br/>(source paper)"]
        embed_positive["_embed_paper()<br/>(positive paper)"]
        embed_negative["_embed_paper()<br/>(negative paper)"]
        loss_computation["Loss Computation<br/>(self.loss)"]
        loss_weighting["Loss Weighting<br/>(mixing_ratio)"]
        training_output["Output: {'loss': loss}"]
    end
    
    subgraph "Inference Mode Flow"
        inference_mode["Inference Mode<br/>(predict_mode=True)"]
        embed_source_only["_embed_paper()<br/>(source paper only)"]
        inference_output["Output: {'embedding': src_paper}"]
    end
    
    forward_method --> predict_mode_flag
    forward_method --> input_validation
    
    predict_mode_flag --> training_mode
    predict_mode_flag --> inference_mode
    
    training_mode --> embed_source
    training_mode --> embed_positive
    training_mode --> embed_negative
    embed_source --> loss_computation
    embed_positive --> loss_computation
    embed_negative --> loss_computation
    loss_computation --> loss_weighting
    loss_weighting --> training_output
    
    inference_mode --> embed_source_only
    embed_source_only --> inference_output
```

Sources: [specter/model.py:248-330](), [specter/model.py:298-301](), [specter/model.py:304-325](), [specter/model.py:327-328]()

This architecture enables SPECTER to seamlessly switch between training (which requires positive and negative examples) and inference (which only processes single papers) modes while maintaining the same underlying embedding generation logic.

---

