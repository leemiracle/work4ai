<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/audio-flamingo · page 3 Technical Architecture · fetched 2026-10-26 -->

# Technical Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)

</details>



This document provides a comprehensive technical overview of the architectures, components, and design decisions across the Audio Flamingo series. It covers the evolution from the Flamingo-based architecture (Audio Flamingo 1) to the LLaVA-based architecture (Audio Flamingo 3 and Music Flamingo), the progression of language model backbones and audio encoders, and the development of specialized components for reasoning and interaction.

For information about specific model variants and their capabilities, see [Model Variants](#2). For training methodologies and datasets, see [Training Data and Strategies](#4). For model usage and deployment, see [Getting Started](#6).

---

## Architectural Evolution Overview

The Audio Flamingo series demonstrates a systematic architectural evolution across five model variants, with each iteration introducing significant technical improvements in backbone models, audio encoders, and specialized components.

### Architecture Timeline and Scaling

```mermaid
graph TB
    subgraph AF1["Audio Flamingo 1 (1.3B)"]
        AF1_Arch["Flamingo Architecture"]
        AF1_LM["OPT-IML 1.3B"]
        AF1_Enc["Generic Audio Encoder"]
        AF1_Data["5.9M Training Pairs"]
    end
    
    subgraph AF2["Audio Flamingo 2 (3B)"]
        AF2_Arch["Flamingo Architecture<br/>(Enhanced)"]
        AF2_LM["Qwen-2.5 3B"]
        AF2_Enc["Improved CLAP Encoder"]
        AF2_Data["10M Training Pairs"]
        AF2_Stage["3-Stage Training Strategy"]
    end
    
    subgraph CoT["Sound-CoT (3B)"]
        CoT_Base["AF2 Base Architecture"]
        CoT_Reasoning["Chain-of-Thought<br/>Reasoning System"]
        CoT_Data["1M CoT Traces"]
    end
    
    subgraph AF3["Audio Flamingo 3 (7B)"]
        AF3_Arch["LLaVA Architecture"]
        AF3_LM["Qwen-2.5 7B"]
        AF3_Enc["AF-Whisper Encoder<br/>(Unified)"]
        AF3_Data["50M Training Pairs"]
        AF3_TTS["AF3-Chat TTS Module"]
    end
    
    subgraph MF["Music Flamingo (7B)"]
        MF_Base["AF3 Base Architecture"]
        MF_CoT["Chain-of-Thought<br/>Integration"]
        MF_RL["Reinforcement Learning<br/>with Custom Rewards"]
        MF_Music["Music Specialization<br/>Components"]
    end
    
    AF1 --> AF2
    AF2 --> CoT
    AF2 --> AF3
    AF3 --> MF
    
    AF1_Arch --> AF1_LM
    AF1_LM --> AF1_Enc
    AF1_Enc --> AF1_Data
    
    AF2_Arch --> AF2_LM
    AF2_LM --> AF2_Enc
    AF2_Enc --> AF2_Data
    AF2_Data --> AF2_Stage
    
    CoT_Base --> CoT_Reasoning
    CoT_Reasoning --> CoT_Data
    
    AF3_Arch --> AF3_LM
    AF3_LM --> AF3_Enc
    AF3_Enc --> AF3_Data
    AF3_Data --> AF3_TTS
    
    MF_Base --> MF_CoT
    MF_CoT --> MF_RL
    MF_RL --> MF_Music
```

**Sources:** [README.md:14-18](), [README.md:107](), [README.md:172](), [README.md:239-240]()

### Key Architectural Transitions

The series exhibits three major architectural transitions:

| Aspect | Audio Flamingo 1 | Audio Flamingo 2 | Audio Flamingo 3 |
|--------|------------------|------------------|------------------|
| **Base Architecture** | Flamingo | Enhanced Flamingo | LLaVA |
| **Language Model** | OPT-IML 1.3B | Qwen-2.5 3B | Qwen-2.5 7B |
| **Audio Encoder** | Generic | Improved CLAP | AF-Whisper (unified) |
| **Audio Modalities** | Sound, Music | Sound, Music | Sound, Music, Speech |
| **Training Scale** | 5.9M pairs | 10M pairs | 50M pairs |
| **Max Audio Length** | Not specified | 5 minutes | 10 minutes |
| **Training Strategy** | Standard | 3-stage pipeline | Multi-stage with specialization |

**Sources:** [README.md:14-18](), [README.md:107](), [README.md:172](), [README.md:204]()

---

## Architectural Foundations

### Flamingo Architecture (AF1, AF2)

Audio Flamingo 1 and 2 are built on the Flamingo architecture, originally designed for vision-language tasks. This architecture emphasizes in-context learning and few-shot capabilities.

```mermaid
graph LR
    subgraph "Flamingo-based Architecture"
        Audio["Audio Input<br/>(Waveform)"]
        Encoder["Audio Encoder"]
        Features["Audio Features"]
        Perceiver["Perceiver Resampler<br/>(Cross-attention)"]
        LM["Language Model<br/>(Frozen/Adapted)"]
        Output["Text Output"]
        
        Audio --> Encoder
        Encoder --> Features
        Features --> Perceiver
        Perceiver --> LM
        LM --> Output
    end
    
    subgraph "Key Characteristics"
        FSL["Few-Shot Learning<br/>via In-Context"]
        Dialogue["Multi-Turn<br/>Dialogue Support"]
        Interleaved["Interleaved<br/>Audio-Text Input"]
    end
```

The Flamingo architecture provides:
- **Cross-attention mechanisms** between audio features and language model layers
- **Perceiver resampler** for efficient feature compression and alignment
- **In-context learning** through interleaved audio-text examples
- **Multi-turn dialogue** capabilities through conversational context management

**Sources:** [README.md:15](), [README.md:204]()

### LLaVA Architecture (AF3, Music Flamingo)

Audio Flamingo 3 and Music Flamingo transition to the LLaVA architecture, enabling more efficient multimodal fusion and better scaling properties.

```mermaid
graph LR
    subgraph "LLaVA-based Architecture"
        AudioIn["Audio Input<br/>(Up to 10 min)"]
        AFWhisper["AF-Whisper Encoder<br/>(Unified)"]
        Projector["Multimodal Projector<br/>(Linear/MLP)"]
        QwenLM["Qwen-2.5 LM<br/>(7B parameters)"]
        TextOut["Text Output"]
        
        AudioIn --> AFWhisper
        AFWhisper --> Projector
        Projector --> QwenLM
        QwenLM --> TextOut
    end
    
    subgraph "Architecture Benefits"
        Unified["Unified encoder for<br/>sound/music/speech"]
        Efficient["More efficient<br/>feature fusion"]
        Scalable["Better scaling to<br/>large datasets"]
        LongAudio["Extended audio<br/>context (10 min)"]
    end
```

The LLaVA architecture offers:
- **Simplified projection** from audio to language model space via linear/MLP layers
- **Unified encoder** (AF-Whisper) handling all three audio modalities
- **Improved training efficiency** enabling scaling to 50M training pairs
- **Extended context** supporting up to 10 minutes of audio input

**Sources:** [README.md:107](), [README.md:109]()

### Architecture Comparison

```mermaid
graph TB
    subgraph Comparison["Architectural Design Patterns"]
        
        subgraph Flamingo["Flamingo Pattern (AF1, AF2)"]
            F1["Cross-attention between<br/>frozen LM layers"]
            F2["Perceiver resampler for<br/>feature compression"]
            F3["Emphasis on few-shot<br/>in-context learning"]
            F4["Modular audio encoder<br/>replacement"]
        end
        
        subgraph LLaVA["LLaVA Pattern (AF3, MF)"]
            L1["Direct projection to<br/>LM token space"]
            L2["Simple linear/MLP<br/>projection layer"]
            L3["Emphasis on large-scale<br/>supervised training"]
            L4["Unified multimodal<br/>encoder design"]
        end
        
    end
    
    Transition["Architectural Transition<br/>Rationale"]
    R1["Scalability: Better handling<br/>of 50M training pairs"]
    R2["Efficiency: Reduced<br/>computational overhead"]
    R3["Unification: Single encoder<br/>for all modalities"]
    R4["Context: Extended audio<br/>length support"]
    
    Flamingo --> Transition
    LLaVA --> Transition
    Transition --> R1
    Transition --> R2
    Transition --> R3
    Transition --> R4
```

**Sources:** [README.md:107](), [README.md:204]()

---

## Language Model Backbones

### OPT-IML Foundation (AF1)

Audio Flamingo 1 uses OPT-IML as its language model backbone, providing foundational language understanding capabilities.

| Component | Specification |
|-----------|--------------|
| **Model Name** | OPT-IML |
| **Parameters** | 1.3B |
| **License** | OPT-IML License (see [License and Attribution](#7)) |
| **Key Features** | Instruction-following, multi-task capabilities |
| **Training Objective** | Instruction-tuned OPT model |

The OPT-IML backbone provides:
- Instruction-following capabilities for audio understanding tasks
- Multi-task performance across captioning, classification, and QA
- Foundation for few-shot learning through in-context examples
- Multi-turn dialogue support when combined with dialogue training data

**Sources:** [README.md:204](), [README.md:239]()

### Qwen-2.5 Foundation (AF2, AF3, Variants)

Audio Flamingo 2, Audio Flamingo 3, Sound-CoT, and Music Flamingo transition to the Qwen-2.5 series of language models.

```mermaid
graph TB
    subgraph Qwen["Qwen-2.5 Language Model Family"]
        Q05["Qwen-2.5 0.5B"]
        Q15["Qwen-2.5 1.5B"]
        Q3["Qwen-2.5 3B"]
        Q7["Qwen-2.5 7B"]
    end
    
    subgraph Models["Model Mappings"]
        AF2_05["AF2-0.5B"]
        AF2_15["AF2-1.5B"]
        AF2_3["AF2-3B"]
        CoT["Sound-CoT 3B"]
        AF3_Main["AF3-7B"]
        AF3_Chat["AF3-Chat-7B"]
        MF_Main["Music Flamingo-7B"]
    end
    
    Q05 --> AF2_05
    Q15 --> AF2_15
    Q3 --> AF2_3
    Q3 --> CoT
    Q7 --> AF3_Main
    Q7 --> AF3_Chat
    Q7 --> MF_Main
```

| Model Variant | LM Backbone | Parameters | Primary Use Case |
|---------------|-------------|------------|------------------|
| AF2-0.5B | Qwen-2.5 0.5B | 0.5B | Resource-constrained deployment |
| AF2-1.5B | Qwen-2.5 1.5B | 1.5B | Balanced performance/efficiency |
| AF2-3B | Qwen-2.5 3B | 3B | Full AF2 capabilities |
| Sound-CoT | Qwen-2.5 3B | 3B | Reasoning-focused tasks |
| AF3 | Qwen-2.5 7B | 7B | State-of-the-art performance |
| Music Flamingo | Qwen-2.5 7B | 7B | Music understanding specialization |

The Qwen-2.5 backbone provides:
- **Enhanced language understanding** compared to OPT-IML
- **Multi-size variants** (0.5B, 1.5B, 3B, 7B) for different deployment scenarios
- **Stronger instruction-following** capabilities
- **Better reasoning** foundations for chain-of-thought tasks
- **License**: Qwen RESEARCH LICENSE AGREEMENT (see [License and Attribution](#7))

**Sources:** [README.md:165-167](), [README.md:172](), [README.md:240]()

---

## Audio Encoders

### Generic Audio Encoder (AF1)

Audio Flamingo 1 uses a generic audio encoder without specific details disclosed in the main repository documentation. This encoder processes audio waveforms into feature representations compatible with the Flamingo architecture's cross-attention mechanisms.

**Sources:** [README.md:204]()

### Improved CLAP Encoder (AF2)

Audio Flamingo 2 introduces a re-trained CLAP (Contrastive Language-Audio Pretraining) encoder with enhanced text understanding capabilities.

```mermaid
graph LR
    subgraph CLAP["CLAP Encoder Architecture"]
        AudioInput["Audio Waveform"]
        AudioFrontend["Audio Frontend<br/>(Spectrogram)"]
        AudioBackbone["Audio Backbone<br/>Network"]
        AudioProj["Audio Projection<br/>Head"]
        TextInput["Text Input"]
        TextEncoder["Text Encoder"]
        TextProj["Text Projection<br/>Head"]
        
        AudioInput --> AudioFrontend
        AudioFrontend --> AudioBackbone
        AudioBackbone --> AudioProj
        
        TextInput --> TextEncoder
        TextEncoder --> TextProj
        
        AudioProj -.->|"Contrastive<br/>Learning"| SharedSpace["Shared<br/>Embedding<br/>Space"]
        TextProj -.->|"Contrastive<br/>Learning"| SharedSpace
    end
```

CLAP encoder improvements in AF2:
- **Re-trained from scratch** with stronger text understanding objectives
- **Enhanced audio-text alignment** through improved contrastive learning
- **Better zero-shot performance** on classification and retrieval tasks
- **Foundation for AudioSkills** dataset learning

**Sources:** [README.md:172]()

### AF-Whisper Unified Encoder (AF3, Music Flamingo)

Audio Flamingo 3 introduces AF-Whisper, a unified audio encoder based on Whisper architecture but trained to handle understanding tasks beyond speech recognition.

```mermaid
graph TB
    subgraph AFWhisper["AF-Whisper Unified Encoder"]
        Input["Audio Input<br/>(Up to 10 min)"]
        
        subgraph Processing["Processing Pipeline"]
            Segment["Audio Segmentation"]
            Whisper["Whisper-based<br/>Encoder Backbone"]
            Adaptation["Understanding<br/>Adaptation Layer"]
        end
        
        subgraph Modalities["Supported Modalities"]
            Sound["Sound<br/>Understanding"]
            Music["Music<br/>Understanding"]
            Speech["Speech<br/>Understanding"]
        end
        
        Output["Unified Audio<br/>Representations"]
        
        Input --> Segment
        Segment --> Whisper
        Whisper --> Adaptation
        Adaptation --> Output
        
        Output --> Sound
        Output --> Music
        Output --> Speech
    end
```

AF-Whisper key features:
- **Whisper-based foundation**: Leverages Whisper architecture trained on 680k hours of speech
- **Extended training**: Adapted for sound and music understanding beyond speech recognition
- **Unified representation**: Single encoder handles all three audio modalities
- **Long-audio support**: Processes up to 10 minutes of audio through segmentation
- **Efficient integration**: Direct projection into LLaVA architecture token space

Technical specifications:
- Base architecture derived from Whisper encoder
- Trained on 50M audio-text pairs covering sound, music, and speech
- Produces fixed-dimensional embeddings compatible with Qwen-2.5 token space
- Supports variable-length audio through chunking and temporal aggregation

**Sources:** [README.md:107](), [README.md:109]()

### Encoder Evolution Comparison

| Feature | Generic (AF1) | CLAP (AF2) | AF-Whisper (AF3) |
|---------|--------------|------------|------------------|
| **Modalities** | Sound, Music | Sound, Music | Sound, Music, Speech |
| **Training Focus** | General audio | Audio-text alignment | Unified understanding |
| **Text Understanding** | Limited | Improved | Integrated |
| **Max Audio Length** | Not specified | 5 minutes | 10 minutes |
| **Architecture** | Unspecified | Contrastive learning | Whisper-based |

**Sources:** [README.md:107](), [README.md:172](), [README.md:204]()

---

## Specialized Components

### AF3-Chat Streaming TTS Module

Audio Flamingo 3 includes AF3-Chat, a streaming text-to-speech module that enables voice output capabilities.

```mermaid
graph LR
    subgraph AF3Chat["AF3-Chat TTS System"]
        TextGen["Text Generation<br/>from AF3"]
        TTSModule["Streaming TTS<br/>Module"]
        AudioOut["Voice Output<br/>(Audio Stream)"]
        
        TextGen --> TTSModule
        TTSModule --> AudioOut
    end
    
    subgraph Features["TTS Features"]
        Streaming["Real-time<br/>Streaming"]
        Integration["Seamless AF3<br/>Integration"]
        Quality["High-quality<br/>Voice Synthesis"]
    end
    
    AF3Chat --> Features
```

AF3-Chat capabilities:
- **Streaming synthesis**: Real-time voice generation as text is produced
- **Integrated deployment**: Available as AF3-Chat checkpoint variant
- **Multi-turn support**: Enables voice-based dialogue interactions
- **HuggingFace availability**: Deployed at `nvidia/audio-flamingo-3-chat`

**Sources:** [README.md:82-83](), [README.md:109]()

### Chain-of-Thought Reasoning System (Sound-CoT, Music Flamingo)

The chain-of-thought reasoning system enables step-by-step reasoning for complex audio understanding tasks.

```mermaid
graph TB
    subgraph CoTSystem["Chain-of-Thought System"]
        AudioQ["Audio + Question<br/>Input"]
        
        subgraph Reasoning["Reasoning Process"]
            Step1["Step 1:<br/>Audio Analysis"]
            Step2["Step 2:<br/>Evidence Gathering"]
            Step3["Step 3:<br/>Logical Inference"]
            StepN["Step N:<br/>Conclusion"]
        end
        
        FinalAnswer["Final Answer<br/>with Reasoning Trace"]
        
        AudioQ --> Step1
        Step1 --> Step2
        Step2 --> Step3
        Step3 --> StepN
        StepN --> FinalAnswer
    end
    
    subgraph Training["CoT Training Data"]
        AFCoTTrain["AF-CoT-Train<br/>(1M traces)"]
        AFThink["AF-Think Dataset"]
        
        AFCoTTrain --> CoTSystem
        AFThink --> CoTSystem
    end
    
    subgraph Evaluation["CoT Evaluation"]
        AFReasoningEval["AF-Reasoning-Eval<br/>Benchmark"]
    end
```

Chain-of-Thought implementation:
- **Training data**: 1M reasoning traces in AF-CoT-Train dataset
- **Sound-CoT model**: 3B parameter model based on AF2 architecture
- **Music Flamingo integration**: CoT reasoning for deep music analysis
- **Evaluation framework**: AF-Reasoning-Eval benchmark for reasoning assessment

CoT capabilities:
- **Common-sense reasoning**: Logical inference about sound sources and contexts
- **Discriminative reasoning**: Distinguishing between closely related audio concepts
- **Step-by-step explanation**: Transparent reasoning process for interpretability
- **Music theory reasoning**: Understanding harmony, structure, and cultural context

**Sources:** [README.md:46](), [README.md:148](), [README.md:150]()

### Reinforcement Learning with Custom Rewards (Music Flamingo)

Music Flamingo employs reinforcement learning with custom reward functions to improve music understanding quality.

```mermaid
graph TB
    subgraph RLSystem["RL Training System"]
        BaseModel["AF3 Base Model<br/>+ CoT"]
        
        subgraph RLLoop["RL Training Loop"]
            AudioInput["Audio Input"]
            Generation["Response Generation"]
            Rewards["Custom Reward<br/>Functions"]
            PolicyUpdate["Policy Update"]
        end
        
        MFModel["Music Flamingo<br/>Optimized Model"]
        
        BaseModel --> AudioInput
        AudioInput --> Generation
        Generation --> Rewards
        Rewards --> PolicyUpdate
        PolicyUpdate --> MFModel
    end
    
    subgraph RewardComponents["Custom Reward Design"]
        Accuracy["Answer Accuracy"]
        Detail["Detail Richness"]
        Theory["Theory Correctness"]
        Coherence["Reasoning Coherence"]
        Cultural["Cultural Context"]
        
        Accuracy --> Rewards
        Detail --> Rewards
        Theory --> Rewards
        Coherence --> Rewards
        Cultural --> Rewards
    end
```

RL with custom rewards features:
- **Multi-aspect rewards**: Evaluation across accuracy, detail, theory, coherence, and cultural context
- **Music-specific objectives**: Rewards designed for music understanding quality
- **CoT integration**: Rewards applied to both answers and reasoning traces
- **Performance optimization**: Achieves SOTA on 10+ music benchmarks

Custom reward functions target:
- **Harmony analysis accuracy**: Correct identification of chords and progressions
- **Structural understanding**: Accurate description of song sections and form
- **Timbre description**: Precise characterization of instrumental qualities
- **Lyrical interpretation**: Meaningful analysis of song lyrics and themes
- **Cultural context**: Appropriate recognition of genre and cultural influences

**Sources:** [README.md:42-49]()

---

## Component Integration Architecture

### End-to-End Processing Pipeline

```mermaid
graph TB
    subgraph Input["Input Processing"]
        AudioFile["Audio File<br/>(WAV/MP3/etc.)"]
        TextPrompt["Text Prompt/<br/>Question"]
    end
    
    subgraph AudioPath["Audio Processing Path"]
        Waveform["Waveform<br/>Loading"]
        Encoder["Audio Encoder<br/>(CLAP/AF-Whisper)"]
        AudioEmbed["Audio<br/>Embeddings"]
    end
    
    subgraph Fusion["Multimodal Fusion"]
        Projector["Multimodal<br/>Projector"]
        TokenSpace["LM Token<br/>Space"]
        
        AudioEmbed --> Projector
        Projector --> TokenSpace
    end
    
    subgraph LMProcessing["Language Model Processing"]
        TextEmbed["Text<br/>Embeddings"]
        QwenLM["Qwen-2.5 LM"]
        
        TextPrompt --> TextEmbed
        TokenSpace --> QwenLM
        TextEmbed --> QwenLM
    end
    
    subgraph Output["Output Generation"]
        TextGen["Text Generation"]
        CoTReasoning["CoT Reasoning<br/>(Optional)"]
        TTSOutput["TTS Voice<br/>(AF3-Chat)"]
        
        QwenLM --> TextGen
        TextGen --> CoTReasoning
        TextGen --> TTSOutput
    end
    
    AudioFile --> Waveform
    Waveform --> Encoder
```

**Sources:** [README.md:107](), [README.md:172]()

### Model-Specific Component Stacks

```mermaid
graph LR
    subgraph AF1Stack["AF1 Component Stack"]
        AF1E["Generic<br/>Encoder"]
        AF1P["Perceiver<br/>Resampler"]
        AF1L["OPT-IML<br/>1.3B"]
        
        AF1E --> AF1P
        AF1P --> AF1L
    end
    
    subgraph AF2Stack["AF2 Component Stack"]
        AF2E["CLAP<br/>Encoder"]
        AF2P["Perceiver<br/>Resampler"]
        AF2L["Qwen-2.5<br/>3B"]
        AF2S["3-Stage<br/>Training"]
        
        AF2E --> AF2P
        AF2P --> AF2L
        AF2L --> AF2S
    end
    
    subgraph CoTStack["Sound-CoT Stack"]
        CoTE["CLAP<br/>Encoder"]
        CoTP["Perceiver<br/>Resampler"]
        CoTL["Qwen-2.5<br/>3B"]
        CoTR["CoT<br/>Reasoning"]
        
        CoTE --> CoTP
        CoTP --> CoTL
        CoTL --> CoTR
    end
    
    subgraph AF3Stack["AF3 Component Stack"]
        AF3E["AF-Whisper<br/>Encoder"]
        AF3Proj["Linear/MLP<br/>Projector"]
        AF3L["Qwen-2.5<br/>7B"]
        AF3T["AF3-Chat<br/>TTS"]
        
        AF3E --> AF3Proj
        AF3Proj --> AF3L
        AF3L --> AF3T
    end
    
    subgraph MFStack["Music Flamingo Stack"]
        MFE["AF-Whisper<br/>Encoder"]
        MFProj["Linear/MLP<br/>Projector"]
        MFL["Qwen-2.5<br/>7B"]
        MFCoT["CoT<br/>Integration"]
        MFRL["RL Custom<br/>Rewards"]
        
        MFE --> MFProj
        MFProj --> MFL
        MFL --> MFCoT
        MFCoT --> MFRL
    end
```

**Sources:** [README.md:14-18](), [README.md:42-49](), [README.md:107](), [README.md:172](), [README.md:204]()

---

## Architecture Summary

The Audio Flamingo series demonstrates systematic architectural evolution:

**Core Architecture Transition:**
- AF1/AF2: Flamingo architecture with cross-attention and perceiver resampler
- AF3/Music Flamingo: LLaVA architecture with direct projection and simplified fusion

**Language Model Progression:**
- AF1: OPT-IML 1.3B (instruction-tuned)
- AF2: Qwen-2.5 3B (with 0.5B, 1.5B variants)
- Sound-CoT: Qwen-2.5 3B (reasoning-optimized)
- AF3/Music Flamingo: Qwen-2.5 7B (state-of-the-art scale)

**Audio Encoder Evolution:**
- AF1: Generic audio encoder
- AF2: Improved CLAP with enhanced text understanding
- AF3/Music Flamingo: AF-Whisper unified encoder for sound/music/speech

**Specialized Components:**
- AF3-Chat: Streaming TTS for voice output
- Sound-CoT: Chain-of-thought reasoning system with 1M training traces
- Music Flamingo: Reinforcement learning with custom music-specific rewards

This architectural progression enables scaling from 5.9M to 50M training pairs, extending audio context from unspecified lengths to 10 minutes, and expanding from two modalities (sound, music) to three (adding speech), while maintaining full backward compatibility through the branch structure.

**Sources:** [README.md:14-18](), [README.md:42-49](), [README.md:107-109](), [README.md:172](), [README.md:204](), [README.md:239-240]()

---

