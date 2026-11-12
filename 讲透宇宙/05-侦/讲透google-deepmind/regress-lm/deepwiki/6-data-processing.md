<!-- source: DeepWiki mcp.deepwiki.com · repo google-deepmind/regress-lm · page 6 Data Processing · fetched 2026-10-26 -->

# Data Processing

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [regress_lm/tokenizers.py](regress_lm/tokenizers.py)
- [regress_lm/vocabs.py](regress_lm/vocabs.py)

</details>



## Purpose and Scope

The data processing system in RegressLM handles the conversion of raw text and numerical data into tokenized representations suitable for neural network training and inference. This system provides two main capabilities: text tokenization for the encoder input and specialized numerical tokenization for the decoder output.

For detailed information about the abstract model interfaces that consume these processed tokens, see [Model Abstractions](#5.1). For the neural architecture that processes these tokens, see [Neural Architecture](#5.3).

## System Architecture

The data processing system consists of two parallel tokenization pipelines that work together to handle the text-to-number regression task:

```mermaid
graph TB
    subgraph "Input Processing"
        RawText["Raw Text Input<br/>'The temperature is high'"]
        RawFloat["Target Float<br/>98.6"]
    end
    
    subgraph "Text Tokenization Pipeline"
        EncoderVocab["EncoderVocab<br/>(Abstract Base)"]
        BasicEnglishVocab["BasicEnglishVocab"]
        SentencePieceVocab["SentencePieceVocab"]
        EncoderTokens["Encoder Token IDs<br/>[101, 1996, 4860, 2003, 2152, 102]"]
        
        EncoderVocab --> BasicEnglishVocab
        EncoderVocab --> SentencePieceVocab
    end
    
    subgraph "Numerical Tokenization Pipeline"
        DecoderVocab["DecoderVocab"]
        DecoderTokenizer["DecoderTokenizer<br/>(Abstract Base)"]
        P10Tokenizer["P10Tokenizer<br/>s * m * 10^e"]
        IEEEFloatTokenizer["IEEEFloatTokenizer<br/>s * b^e * m"]
        DecoderTokens["Decoder Token IDs<br/>[1, 2, 9, 8, 6, 10]"]
        
        DecoderVocab --> DecoderTokenizer
        DecoderTokenizer --> P10Tokenizer
        DecoderTokenizer --> IEEEFloatTokenizer
    end
    
    subgraph "External Libraries"
        TorchText["torchtext.vocab.Vocab"]
        SentencePiece["sentencepiece_processor"]
    end
    
    RawText --> EncoderVocab
    RawFloat --> DecoderVocab
    
    EncoderVocab --> EncoderTokens
    DecoderVocab --> DecoderTokens
    
    BasicEnglishVocab --> TorchText
    SentencePieceVocab --> SentencePiece
    DecoderVocab --> TorchText
```

Sources: [regress_lm/vocabs.py:27-144](), [regress_lm/tokenizers.py:50-262]()

## Text Processing Pipeline

The encoder side handles text input through a vocabulary abstraction that supports multiple tokenization strategies:

| Vocabulary Class | Purpose | Tokenization Method | Use Case |
|------------------|---------|-------------------|----------|
| `BasicEnglishVocab` | Simple word-level tokenization | TorchText basic_english | Testing and development |
| `SentencePieceVocab` | Subword tokenization | SentencePiece model | Production use with pretrained models |

Both vocabulary classes inherit from `EncoderVocab` and implement the `to_token_ids` method to convert raw text into integer token sequences. The `pad_id` property provides the padding token for batch processing.

Sources: [regress_lm/vocabs.py:39-49](), [regress_lm/vocabs.py:91-144]()

## Numerical Processing Pipeline

The decoder side uses a two-layer architecture for numerical tokenization:

```mermaid
graph TD
    subgraph "Tokenizer Layer"
        DecoderTokenizer["DecoderTokenizer[ObjectT]<br/>Abstract Base Class"]
        P10["P10Tokenizer<br/>Scientific notation"]
        IEEE["IEEEFloatTokenizer<br/>IEEE-like format"]
        
        DecoderTokenizer --> P10
        DecoderTokenizer --> IEEE
    end
    
    subgraph "Vocabulary Layer"
        DecoderVocab["DecoderVocab[ObjectT]<br/>Manages token-to-ID mapping"]
        TTVocab["torchtext.vocab.Vocab<br/>Underlying vocabulary"]
        
        DecoderVocab --> TTVocab
    end
    
    subgraph "Token Format Examples"
        P10Example["98.6 → [<+>, <9>, <8>, <6>, <0>, <E-1>]"]
        IEEEExample["98.6 → [<+>, <+>, <0>, <9>, <8>, <6>, <0>]"]
    end
    
    DecoderTokenizer --> DecoderVocab
    P10 --> P10Example
    IEEE --> IEEEExample
```

The `DecoderTokenizer` abstract class defines the interface for converting floats to token sequences, while `DecoderVocab` manages the mapping from token strings to integer IDs using TorchText's vocabulary system.

Sources: [regress_lm/tokenizers.py:50-76](), [regress_lm/vocabs.py:51-89]()

## Tokenization Methods

### P10 Tokenization

The `P10Tokenizer` implements the P10 method from research literature, representing floats as `s * m * 10^e`:

- **Sign token**: `<+>` or `<->`
- **Mantissa digits**: `<0>` through `<9>` (configurable length)
- **Exponent token**: `<E-10>` through `<E10>` (configurable range)

The tokenizer handles rounding and range constraints automatically through the `_round_float` method.

### IEEE-like Tokenization

The `IEEEFloatTokenizer` uses a format similar to IEEE floating-point standards, representing floats as `s * b^e * m`:

- **Sign token**: `<+>` or `<->`
- **Exponent sign**: `<+>` or `<->`
- **Exponent digits**: Base-b representation (configurable base and digit count)
- **Mantissa digits**: Base-b representation (configurable digit count)

Sources: [regress_lm/tokenizers.py:78-171](), [regress_lm/tokenizers.py:173-262]()

## Integration with Model System

The processed tokens flow into the model system through standardized interfaces:

```mermaid
graph LR
    subgraph "Data Processing Output"
        EncTokens["Encoder Token IDs<br/>list[int]"]
        DecTokens["Decoder Token IDs<br/>list[int]"]
    end
    
    subgraph "Model Input Processing"
        ConvertInputs["convert_inputs()<br/>ExampleInput → tensors"]
        ConvertExamples["convert_examples()<br/>Example → tensors"]
    end
    
    subgraph "Neural Architecture"
        EncoderDecoder["EncoderDecoder<br/>Neural Network"]
    end
    
    EncTokens --> ConvertInputs
    DecTokens --> ConvertExamples
    ConvertInputs --> EncoderDecoder
    ConvertExamples --> EncoderDecoder
```

The vocabulary classes provide metadata needed for model configuration, including vocabulary sizes (`__len__`), padding tokens (`pad_id`, `bos_pad_id`), and sequence lengths (`decode_len`).

Sources: [regress_lm/vocabs.py:63-88]()

## Detailed Documentation

For implementation details of the vocabulary management system, see [Vocabulary Management](#6.1).

For in-depth coverage of the numerical tokenization algorithms and their mathematical foundations, see [Numerical Tokenization](#6.2).

---

