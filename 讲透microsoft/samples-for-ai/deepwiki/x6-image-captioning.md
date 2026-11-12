<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/samples-for-ai · extra page Image Captioning · fetched 2026-10-26 -->

# Image Captioning

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [examples/keras/Image_Captioning/Image_Captioning.py](examples/keras/Image_Captioning/Image_Captioning.py)
- [examples/keras/Image_Captioning/Image_Captioning.pyproj](examples/keras/Image_Captioning/Image_Captioning.pyproj)
- [examples/keras/Image_Captioning/README.md](examples/keras/Image_Captioning/README.md)
- [examples/pytorch/ScreenerNet/ScreenerNet.pyproj](examples/pytorch/ScreenerNet/ScreenerNet.pyproj)

</details>



This document covers the neural image captioning system implementation that combines CNN-based image feature extraction with LSTM-based sequence generation to automatically generate natural language descriptions of images. The system uses InceptionV3 for visual encoding and bidirectional LSTM networks for caption generation, trained on the Flickr8k dataset.

For other PyTorch examples including ScreenerNet, see [ScreenerNet Implementation](#3.2.2). For Keras generative models, see [Generative Adversarial Networks](#3.3.1).

## Overview

The image captioning system implements an encoder-decoder architecture where images are encoded using a pre-trained InceptionV3 CNN and captions are generated using LSTM networks. The system supports both greedy decoding and beam search for caption generation.

```mermaid
graph TB
    subgraph "Input Processing"
        IMG["Input Image<br/>(299x299x3)"]
        CAPTIONS["Training Captions<br/>Flickr8k Dataset"]
    end
    
    subgraph "Feature Extraction"
        INCEPTION["InceptionV3<br/>model_new"]
        FEATURES["Image Features<br/>(2048-dim)"]
    end
    
    subgraph "Text Processing"
        TOKENIZER["word2idx/idx2word<br/>Vocabulary Mapping"]
        SEQUENCES["Padded Sequences<br/>max_len=40"]
    end
    
    subgraph "Model Architecture"
        IMAGE_MODEL["image_model<br/>Dense(300) + RepeatVector"]
        CAPTION_MODEL["caption_model<br/>Embedding + LSTM(256)"]
        MERGE["Merge Layer<br/>concat_axis=1"]
        BILSTM["Bidirectional LSTM<br/>(256 units)"]
        OUTPUT["Dense(vocab_size)<br/>+ Softmax"]
    end
    
    IMG --> INCEPTION
    INCEPTION --> FEATURES
    FEATURES --> IMAGE_MODEL
    
    CAPTIONS --> TOKENIZER
    TOKENIZER --> SEQUENCES
    SEQUENCES --> CAPTION_MODEL
    
    IMAGE_MODEL --> MERGE
    CAPTION_MODEL --> MERGE
    MERGE --> BILSTM
    BILSTM --> OUTPUT
```

Sources: [examples/keras/Image_Captioning/Image_Captioning.py:1-487]()

## Dataset and Preprocessing

The system uses the Flickr8k dataset, which contains 8,000 images with 5 captions each. The dataset is split into training, validation, and test sets using predefined file lists.

### Dataset Structure

| Component | File Path | Purpose |
|-----------|-----------|---------|
| Images | `./input/Flicker8k_Dataset/` | 8k JPEG images |
| Captions | `./input/Flickr8k_text/Flickr8k.token.txt` | Image-caption mappings |
| Train Split | `./input/Flickr8k_text/Flickr_8k.trainImages.txt` | Training image list |
| Validation Split | `./input/Flickr8k_text/Flickr_8k.devImages.txt` | Validation image list |
| Test Split | `./input/Flickr8k_text/Flickr_8k.testImages.txt` | Test image list |

### Image Preprocessing Pipeline

```mermaid
graph LR
    subgraph "Image Processing Functions"
        LOAD["image.load_img<br/>(299, 299)"]
        ARRAY["image.img_to_array"]
        EXPAND["np.expand_dims<br/>(axis=0)"]
        PREPROCESS["preprocess_input<br/>(normalize)"]
    end
    
    subgraph "Feature Encoding"
        ENCODE_FUNC["encode() function"]
        INCEPTION_PRED["model_new.predict"]
        RESHAPE["np.reshape<br/>(2048,)"]
    end
    
    subgraph "Caching System"
        TRAIN_CACHE["encoded_images_inceptionV3.p"]
        VAL_CACHE["encoded_images_val_inceptionV3.p"]
        TEST_CACHE["encoded_images_test_inceptionV3.p"]
    end
    
    LOAD --> ARRAY
    ARRAY --> EXPAND
    EXPAND --> PREPROCESS
    PREPROCESS --> ENCODE_FUNC
    
    ENCODE_FUNC --> INCEPTION_PRED
    INCEPTION_PRED --> RESHAPE
    
    RESHAPE --> TRAIN_CACHE
    RESHAPE --> VAL_CACHE
    RESHAPE --> TEST_CACHE
```

The `preprocess_input` function [examples/keras/Image_Captioning/Image_Captioning.py:82-86]() normalizes pixel values to the range [-1, 1], and the `encode` function [examples/keras/Image_Captioning/Image_Captioning.py:114-118]() generates 2048-dimensional feature vectors using InceptionV3.

Sources: [examples/keras/Image_Captioning/Image_Captioning.py:32-151](), [examples/keras/Image_Captioning/README.md:1-17]()

## Model Architecture

The system implements a multimodal encoder-decoder architecture combining visual and textual information processing.

### Component Models

#### Image Feature Processing
- **Input**: 2048-dimensional InceptionV3 features
- **Architecture**: `Dense(300, activation='relu')` followed by `RepeatVector(max_len)`
- **Purpose**: Projects image features to embedding space and replicates across sequence length

#### Caption Processing  
- **Input**: Tokenized word sequences (max_len=40)
- **Architecture**: `Embedding(vocab_size, 300)` → `LSTM(256, return_sequences=True)` → `TimeDistributed(Dense(300))`
- **Purpose**: Encodes partial captions into contextual representations

#### Final Model
```mermaid
graph TB
    subgraph "Input Layers"
        IMG_INPUT["Image Features<br/>(batch, 2048)"]
        TEXT_INPUT["Partial Caption<br/>(batch, max_len)"]
    end
    
    subgraph "Processing Layers"
        IMG_DENSE["Dense(300)<br/>+ RepeatVector(40)"]
        TEXT_EMB["Embedding(vocab_size, 300)"]
        TEXT_LSTM["LSTM(256)<br/>return_sequences=True"]
        TEXT_TD["TimeDistributed<br/>Dense(300)"]
    end
    
    subgraph "Fusion and Output"
        MERGE_LAYER["Merge Layer<br/>mode='concat'"]
        BI_LSTM["Bidirectional LSTM<br/>(256 units)"]
        DENSE_OUT["Dense(vocab_size)"]
        SOFTMAX["Activation('softmax')"]
    end
    
    IMG_INPUT --> IMG_DENSE
    TEXT_INPUT --> TEXT_EMB
    TEXT_EMB --> TEXT_LSTM
    TEXT_LSTM --> TEXT_TD
    
    IMG_DENSE --> MERGE_LAYER
    TEXT_TD --> MERGE_LAYER
    
    MERGE_LAYER --> BI_LSTM
    BI_LSTM --> DENSE_OUT
    DENSE_OUT --> SOFTMAX
```

The model is compiled with `categorical_crossentropy` loss and `RMSprop` optimizer [examples/keras/Image_Captioning/Image_Captioning.py:415]().

Sources: [examples/keras/Image_Captioning/Image_Captioning.py:393-417]()

## Training Pipeline

### Data Generation Strategy

The training uses custom data generators that create training samples by:
1. Loading image encodings from cached pickle files
2. Creating partial caption sequences and corresponding next-word targets
3. Padding sequences to uniform length using `sequence.pad_sequences`

```mermaid
graph TB
    subgraph "Training Data Generator"
        DF_TRAIN["flickr8k_training_dataset.txt<br/>pandas.read_csv"]
        SHUFFLE["df.sample(frac=1)<br/>Data Shuffling"]
        ITER["df.iterrows()<br/>Row Iterator"]
    end
    
    subgraph "Batch Processing"
        PARTIAL_CAPS["partial_caps[]<br/>Sequence prefixes"]
        NEXT_WORDS["next_words[]<br/>One-hot targets"]
        IMAGES_BATCH["images[]<br/>Cached encodings"]
    end
    
    subgraph "Output Generation"
        PAD_SEQ["sequence.pad_sequences<br/>maxlen=40"]
        YIELD["yield [[images, partial_caps], next_words]"]
    end
    
    DF_TRAIN --> SHUFFLE
    SHUFFLE --> ITER
    ITER --> PARTIAL_CAPS
    ITER --> NEXT_WORDS
    ITER --> IMAGES_BATCH
    
    PARTIAL_CAPS --> PAD_SEQ
    NEXT_WORDS --> YIELD
    IMAGES_BATCH --> YIELD
    PAD_SEQ --> YIELD
```

### Training Configuration

| Parameter | Value | Description |
|-----------|-------|-------------|
| Batch Size | 512 | Training batch size |
| Steps per Epoch | 748 | Calculated from dataset size |
| Validation Steps | 125 | Validation batches per epoch |
| Epochs | 57 | Total training epochs |
| Workers | 4 | Multiprocessing workers |

The `PlotLosses` callback [examples/keras/Image_Captioning/Image_Captioning.py:371-390]() logs training metrics to text files for monitoring.

Sources: [examples/keras/Image_Captioning/Image_Captioning.py:267-425]()

## Inference and Caption Generation

The system provides two inference modes for generating captions from images.

### Greedy Decoding

The `predict_captions` function [examples/keras/Image_Captioning/Image_Captioning.py:429-443]() implements simple greedy decoding:

```mermaid
graph LR
    subgraph "Greedy Generation Process"
        START["start_word = ['<start>']"]
        ENCODE["Get image encoding<br/>encoding_test[image]"]
        PREDICT["final_model.predict<br/>([image_enc, partial_caps])"]
        ARGMAX["np.argmax(preds[0])<br/>Select best word"]
        APPEND["start_word.append<br/>(word_pred)"]
        CHECK["word_pred == '<end>'<br/>or len > max_len"]
    end
    
    START --> ENCODE
    ENCODE --> PREDICT
    PREDICT --> ARGMAX
    ARGMAX --> APPEND
    APPEND --> CHECK
    CHECK -->|Continue| PREDICT
    CHECK -->|Stop| END["return joined caption"]
```

### Beam Search Decoding

The `beam_search_predictions` function [examples/keras/Image_Captioning/Image_Captioning.py:446-487]() implements beam search with configurable beam width:

```mermaid
graph TB
    subgraph "Beam Search Algorithm"
        INIT["start_word = [[start_token], 0.0]<br/>beam_index=3"]
        EXPAND["For each beam candidate"]
        PREDICT_BS["Get model predictions<br/>final_model.predict"]
        TOP_K["np.argsort(preds[0])[-beam_index:]<br/>Top-k words"]
        UPDATE["Update candidates with<br/>cumulative probabilities"]
        SORT["Sort by probability<br/>Keep top beam_index"]
        LENGTH_CHECK["len(sequence) < max_len"]
    end
    
    subgraph "Output Processing"
        BEST["Select best sequence<br/>start_word[-1][0]"]
        DECODE["idx2word mapping<br/>intermediate_caption"]
        FILTER["Remove <end> tokens<br/>final_caption"]
    end
    
    INIT --> EXPAND
    EXPAND --> PREDICT_BS
    PREDICT_BS --> TOP_K
    TOP_K --> UPDATE
    UPDATE --> SORT
    SORT --> LENGTH_CHECK
    LENGTH_CHECK -->|Continue| EXPAND
    LENGTH_CHECK -->|Stop| BEST
    
    BEST --> DECODE
    DECODE --> FILTER
```

The beam search maintains multiple candidate sequences and selects the one with highest cumulative probability.

Sources: [examples/keras/Image_Captioning/Image_Captioning.py:429-487]()

## Key Implementation Details

### Vocabulary Management
- **Word-to-Index Mapping**: `word2idx` dictionary for token encoding
- **Index-to-Word Mapping**: `idx2word` dictionary for decoding
- **Special Tokens**: `<start>` and `<end>` tokens mark sequence boundaries
- **Vocabulary Size**: Calculated as `len(unique)` from all caption words

### Caching Strategy
The system implements efficient caching of image encodings:
- Training encodings: `encoded_images_inceptionV3.p`
- Validation encodings: `encoded_images_val_inceptionV3.p`  
- Test encodings: `encoded_images_test_inceptionV3.p`

This prevents recomputing InceptionV3 features during training.

### Visual Studio Integration
The project includes a `.pyproj` file [examples/keras/Image_Captioning/Image_Captioning.pyproj:1-41]() for Visual Studio integration with the following configuration:
- **Startup File**: `Image_Captioning.py`
- **Project Type**: Python project with Jupyter support
- **Debug Configuration**: Standard Python launcher

Sources: [examples/keras/Image_Captioning/Image_Captioning.py:194-208](), [examples/keras/Image_Captioning/Image_Captioning.py:121-150](), [examples/keras/Image_Captioning/Image_Captioning.pyproj:1-41]()

---

