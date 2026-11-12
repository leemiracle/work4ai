<!-- source: DeepWiki mcp.deepwiki.com · repo fishaudio/Bert-VITS2 · page 4 Multi-Language Text Processing · fetched 2026-10-29 -->

# Multi-Language Text Processing

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [bert/bert-base-japanese-v3/README.md](bert/bert-base-japanese-v3/README.md)
- [bert/bert-base-japanese-v3/config.json](bert/bert-base-japanese-v3/config.json)
- [bert/bert-base-japanese-v3/vocab.txt](bert/bert-base-japanese-v3/vocab.txt)
- [bert/bert-large-japanese-v2/tokenizer_config.json](bert/bert-large-japanese-v2/tokenizer_config.json)
- [text/bert_utils.py](text/bert_utils.py)
- [text/cleaner.py](text/cleaner.py)
- [text/english_bert_mock.py](text/english_bert_mock.py)
- [text/symbols.py](text/symbols.py)
- [tools/classify_language.py](tools/classify_language.py)
- [tools/sentence.py](tools/sentence.py)

</details>



## Purpose and Scope

This document explains the multi-language text processing pipeline within Bert-VITS2, a text-to-speech synthesis system that supports multiple languages. It covers the language detection, text normalization, phoneme conversion, and BERT feature extraction processes that occur before audio synthesis.

For details on BERT feature generation, see [BERT Feature Generation](#3.2). For language-specific text processing implementations, see the related pages for [Chinese Text Processing](#4.1), [Japanese Text Processing](#4.2), and [English Text Processing](#4.3).

## Overview of Multi-Language Support

Bert-VITS2 supports multiple languages through a modular architecture that handles language detection, text normalization, phoneme conversion, and BERT feature extraction in a language-specific manner. The system currently supports Chinese (ZH), Japanese (JP), and English (EN) as the primary languages.

### Multi-Language Processing Architecture

```mermaid
flowchart TB
    InputText["Input Text"] --> LanguageDetection["Language Detection\nclassify_language()"]
    LanguageDetection --> SingleLang["Single Language Track"]
    LanguageDetection --> MixedLang["Mixed Language Track"]
    
    SingleLang --> LanguageNorm["Language-Specific Normalization\ntext_normalize()"]
    MixedLang --> LanguageMarkup["Language Markup\nmarkup_language()"]
    LanguageMarkup --> SegmentProcessing["Process Individual Language Segments"]
    
    LanguageNorm --> Phonemes["Phoneme Conversion\ng2p()"]
    SegmentProcessing --> Phonemes
    
    Phonemes --> BertFeatures["BERT Feature Extraction\nget_bert_feature()"]
    
    BertFeatures --> PhonemeAlignment["Phoneme-BERT Alignment\nvia word2ph"]
    
    PhonemeAlignment --> OutputFeatures["Processed Text Features"]
    
    subgraph "Language Module Selection"
        LanguageModuleMap["language_module_map\nZH → chinese\nJP → japanese\nEN → english"]
    end
    
    LanguageNorm -.-> LanguageModuleMap
    Phonemes -.-> LanguageModuleMap
    BertFeatures -.-> LanguageModuleMap
```

Sources: [text/cleaner.py](), [tools/sentence.py](), [tools/classify_language.py]()

## Language Detection and Classification

The system uses language detection libraries to determine the language of input text. This detection enables proper text processing and feature extraction for each language.

### Language Detection System

```mermaid
flowchart LR
    subgraph "Language Identification Libraries"
        direction TB
        LangId["langid\nDefault option"]
        FastLid["fastlid/fasttext\nAlternative option"]
    end
    
    InputText["Input Text"] --> ConfigCheck["Check language_identification_library\nin config"]
    ConfigCheck --> LangLibrary["Select Language Library"]
    LangLibrary --> LangId
    LangLibrary --> FastLid
    
    LangId --> FilterLanguages["Filter Target Languages"]
    FastLid --> FilterLanguages
    FilterLanguages --> Classifier["Classify Text\nclassify_language()"]
    
    Classifier --> OutputLang["Detected Language\n(zh, ja, en, etc.)"]
    
    subgraph "Special Case: Chinese vs Japanese"
        ZhJaInput["Chinese/Japanese Text"] --> UnicodeCheck["Check Unicode Ranges\nclassify_zh_ja()"]
        UnicodeCheck --> JapaneseChars["Check for Japanese-specific characters\n0x3040-0x309F, 0x30A0-0x30FF"]
        JapaneseChars --> LangOutput["Output 'ja' or 'zh'"]
    end
```

Sources: [tools/classify_language.py]()

### Language Support Table

The system defines language-specific symbols and mappings:

| Language | Code | ID | Symbols Count | Tones | Example Symbols |
|----------|------|----|--------------|----|-----------------|
| Chinese  | ZH   | 0  | 72           | 6  | a, ai, an, ang, ao, b, c, ch... |
| Japanese | JP   | 1  | 57           | 2  | N, a, a:, b, by, ch, d, dy... |
| English  | EN   | 2  | 42           | 4  | aa, ae, ah, ao, aw, ay, b, ch... |

Sources: [text/symbols.py]()

## Text Segmentation and Mixed Language Processing

For mixed-language text, the system segments the input into language-specific chunks and processes each separately.

### Mixed Language Processing Workflow

```mermaid
flowchart TB
    InputText["Mixed Language Text"] --> PatternSplit["Split by Punctuation\nre.split(pattern, text)"]
    PatternSplit --> CheckTargetLangs["Check Target Languages"]
    
    CheckTargetLangs --> AlphaSegmentation{"Is target [en, zh] or [en, ja]\nor [en, ja, zh]?"}
    AlphaSegmentation -->|Yes| SplitAlphaNonAlpha["Split Alpha/Non-Alpha\nsplit_alpha_nonalpha()"]
    AlphaSegmentation -->|No| SkipSplit["Use Original Segments"]
    
    SplitAlphaNonAlpha --> ProcessSegments["Process Each Segment"]
    SkipSplit --> ProcessSegments
    
    ProcessSegments --> DetectLanguage["Detect Language\nclassify_language()"]
    DetectLanguage --> AddMarkup["Add Language Markup\n[ZH], [JP], [EN]"]
    
    AddMarkup --> OutputMarkupText["Marked-up Text\nwith Language Tags"]
    
    subgraph "Example"
        ExInput["Input: 'Hello, 你好, こんにちは'"]
        ExSplit["Split: ['Hello', '你好', 'こんにちは']"]
        ExDetect["Detect: ['en', 'zh', 'ja']"]
        ExMarkup["Output: '[EN]Hello[EN][ZH]你好[ZH][JP]こんにちは[JP]'"]
        
        ExInput --> ExSplit --> ExDetect --> ExMarkup
    end
```

Sources: [tools/sentence.py](), [tools/classify_language.py]()

## Text Cleaning and Normalization Process

The system uses a modular approach for text cleaning, with separate modules for each supported language.

### Text Cleaning Pipeline

```mermaid
flowchart TB
    InputText["Input Text"] --> LanguageSelection["Select Language Module\nlanguage_module_map"]
    
    LanguageSelection -->|"ZH"| ChineseModule["chinese module"]
    LanguageSelection -->|"JP"| JapaneseModule["japanese module"]
    LanguageSelection -->|"EN"| EnglishModule["english module"]
    
    ChineseModule --> ChineseNorm["Chinese Normalization\ntext_normalize()"]
    JapaneseModule --> JapaneseNorm["Japanese Normalization\ntext_normalize()"]
    EnglishModule --> EnglishNorm["English Normalization\ntext_normalize()"]
    
    ChineseNorm --> ChineseG2P["Chinese G2P\ng2p()"]
    JapaneseNorm --> JapaneseG2P["Japanese G2P\ng2p()"]
    EnglishNorm --> EnglishG2P["English G2P\ng2p()"]
    
    ChineseG2P --> OutputPhoneTone["Phones, Tones, Word2ph"]
    JapaneseG2P --> OutputPhoneTone
    EnglishG2P --> OutputPhoneTone
    
    subgraph "BERT Feature Extraction (Optional)"
        OutputPhoneTone --> BertExtraction["Get BERT Features\nget_bert_feature()"]
        BertExtraction --> OutputBert["BERT Features"]
    end
```

Sources: [text/cleaner.py]()

## BERT Feature Integration

The system extracts BERT features for each language using language-specific BERT models. These features enhance the prosody and naturalness of generated speech.

### BERT Feature Extraction System

```mermaid
flowchart TB
    InputText["Normalized Text"] --> LanguageModule["Language Module"]
    LanguageModule --> BertFeature["get_bert_feature()"]
    
    subgraph "BERT Models by Language"
        ZhBert["Chinese BERT Model"]
        JpBert["Japanese BERT Model\nbert-base-japanese-v3"]
        EnBert["English BERT Model\ndeberta-v3-large"]
    end
    
    BertFeature -->|"ZH"| ZhBert
    BertFeature -->|"JP"| JpBert
    BertFeature -->|"EN"| EnBert
    
    ZhBert --> BertEmbeddings["BERT Embeddings"]
    JpBert --> BertEmbeddings
    EnBert --> BertEmbeddings
    
    Word2ph["word2ph Mapping"] --> PhonemeAlignment["Phoneme-level Alignment"]
    BertEmbeddings --> PhonemeAlignment
    
    PhonemeAlignment --> RepeatFeatures["Repeat Word Embeddings\nfor Each Phoneme"]
    RepeatFeatures --> OutputFeatures["Phone-level BERT Features"]
```

Sources: [text/cleaner.py](), [text/english_bert_mock.py](), [bert/bert-base-japanese-v3/README.md]()

## Symbol System and Phoneme Representation

The system uses a unified set of phoneme symbols across all supported languages, while maintaining language-specific subsets.

### Symbol System Architecture

```mermaid
flowchart TB
    subgraph "Language-Specific Symbols"
        ZhSymbols["zh_symbols\n72 phonemes"]
        JaSymbols["ja_symbols\n57 phonemes"]
        EnSymbols["en_symbols\n42 phonemes"]
    end
    
    ZhSymbols --> CombineSymbols["normal_symbols\n(sorted unique set)"]
    JaSymbols --> CombineSymbols
    EnSymbols --> CombineSymbols
    
    CombineSymbols --> AddSpecial["Add Special Symbols\n(pad, punctuation, etc.)"]
    AddSpecial --> FinalSymbols["symbols\nFull Symbol Set"]
    
    subgraph "Tone System"
        ZhTones["num_zh_tones: 6"]
        JaTones["num_ja_tones: 2"]
        EnTones["num_en_tones: 4"]
        
        ZhTones --> CombineTones["num_tones\nTotal: 12"]
        JaTones --> CombineTones
        EnTones --> CombineTones
    end
    
    subgraph "Language ID System"
        LangMap["language_id_map\nZH: 0, JP: 1, EN: 2"]
        ToneStartMap["language_tone_start_map\nZH: 0, JP: 6, EN: 8"]
    end
```

Sources: [text/symbols.py]()

## Language Processing Workflow

The following diagram illustrates the complete workflow from raw text input to processed features ready for the TTS model:

```mermaid
flowchart TB
    subgraph "Input Processing"
        InputText["Raw Text Input"] --> InputMode{"Processing Mode"}
        InputMode -->|"Single Language"| SpecifyLang["Specify Language\n(ZH, JP, EN)"]
        InputMode -->|"Auto Detect"| DetectLanguage["Detect Language\nclassify_language()"]
        InputMode -->|"Mixed Language"| MarkupLanguage["Markup with Language Tags\nmarkup_language()"]
    end
    
    SpecifyLang --> CleanText["clean_text()\ntext_cleaner.py"]
    DetectLanguage --> CleanText
    MarkupLanguage --> SplitByLanguage["Split by Language\nsplit_by_language()"]
    SplitByLanguage --> ProcessEachSegment["Process Each Segment"]
    ProcessEachSegment --> CleanText
    
    CleanText --> NormalizedText["Normalized Text"]
    CleanText --> Phonemes["Phoneme Sequence"]
    CleanText --> Tones["Tone Sequence"]
    CleanText --> Word2ph["Word-to-Phoneme Mapping"]
    
    NormalizedText --> BertFeatureExtraction["BERT Feature Extraction\nclean_text_bert()"]
    Word2ph --> BertFeatureExtraction
    
    Phonemes --> TextToSequence["text_to_sequence()\nConvert to IDs"]
    Tones --> TextToSequence
    
    BertFeatureExtraction --> PhoneBertFeature["Phone-level BERT Features"]
    TextToSequence --> PhoneIDs["Phone ID Sequence"]
    
    PhoneBertFeature --> FinalOutput["Processed Features for TTS Model"]
    PhoneIDs --> FinalOutput
```

Sources: [text/cleaner.py](), [tools/sentence.py](), [tools/classify_language.py]()

## Conclusion

The multi-language text processing system in Bert-VITS2 provides a flexible framework for handling text in different languages. By using language-specific processing modules and BERT models, it accurately converts text into phonetic and linguistic features that can be used by the TTS model to generate natural-sounding speech in multiple languages. The system handles both single-language input and mixed-language text, making it versatile for various use cases.

---

