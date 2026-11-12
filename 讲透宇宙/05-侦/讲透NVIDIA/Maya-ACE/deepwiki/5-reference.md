<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/Maya-ACE · page 5 Reference · fetched 2026-10-26 -->

# Reference

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/additionals.md](docs/additionals.md)
- [docs/reallusionsample.md](docs/reallusionsample.md)

</details>



This section provides technical reference materials, specifications, and additional resources for Maya-ACE development and usage. It serves as a comprehensive guide to system constraints, file format requirements, sample projects, and compatibility information.

For step-by-step development instructions, see [Development Guide](#4). For architectural details, see [Architecture](#3).

## Overview

The reference materials are organized into the following categories:

| Category | Description | Section |
|----------|-------------|---------|
| Audio Specifications | Technical requirements for audio files, supported formats, and Maya compatibility constraints | [Audio Specifications](#5.1) |
| Sample Projects | Documentation of provided sample projects and setup instructions | [Sample Projects](#5.2) |

## Technical Specifications Summary

Maya-ACE integrates multiple technical systems with specific requirements and constraints. The following diagram illustrates the key technical specifications and their relationships:

**Maya-ACE Technical Specification Overview**

```mermaid
graph TB
    subgraph "Audio Processing Layer"
        AudioFile["AudioFile Library"]
        WAV_Support["WAV Format Support"]
        AIFF_Support["AIFF Format Support"]
        PCM_Constraint["PCM Format Constraint"]
    end
    
    subgraph "Maya Integration Layer"
        Maya2024["Maya 2024 Support"]
        Maya2025["Maya 2025 Support"]
        Timeline_Import["Timeline Audio Import"]
        Format_Validation["Maya Format Validation"]
    end
    
    subgraph "Recommended Specifications"
        WAV_16bit["WAV 16-bit PCM"]
        SampleRates["16kHz/32kHz/48kHz"]
        MonoChannel["Mono Channel"]
        OptimalSpecs["Optimal Performance Specs"]
    end
    
    subgraph "Sample Resources"
        ReallusionSample["Reallusion Character Sample"]
        CamilaCharacter["Camila Character (CC4)"]
        ArnoldMaterials["Arnold Render Materials"]
    end
    
    AudioFile --> WAV_Support
    AudioFile --> AIFF_Support
    Maya2025 --> PCM_Constraint
    Timeline_Import --> Format_Validation
    
    WAV_16bit --> OptimalSpecs
    SampleRates --> OptimalSpecs
    MonoChannel --> OptimalSpecs
    
    ReallusionSample --> CamilaCharacter
    CamilaCharacter --> ArnoldMaterials
    
    PCM_Constraint --> WAV_16bit
    Format_Validation --> OptimalSpecs
```

Sources: [docs/additionals.md:1-21](), [docs/reallusionsample.md:1-13]()

## Audio System Integration

The following diagram shows how audio specifications relate to specific code components and libraries:

**Audio Processing Code Entity Relationships**

```mermaid
graph LR
    subgraph "External Dependencies"
        AudioFileLib["adamstark/AudioFile"]
        MayaAudioAPI["Maya Audio Import API"]
    end
    
    subgraph "File Format Handlers"
        WAVHandler["WAV File Handler"]
        AIFFHandler["AIFF File Handler"]
        PCMValidator["PCM Format Validator"]
    end
    
    subgraph "Maya Version Constraints"
        Maya2024Compat["Maya 2024 Compatibility"]
        Maya2025PCM["Maya 2025 PCM-Only"]
    end
    
    subgraph "Specification Compliance"
        SixteenBitPCM["16-bit PCM"]
        SampleRateSupport["16kHz|32kHz|48kHz"]
        MonoChannelSupport["Single Channel"]
    end
    
    AudioFileLib --> WAVHandler
    AudioFileLib --> AIFFHandler
    
    WAVHandler --> PCMValidator
    AIFFHandler --> PCMValidator
    
    PCMValidator --> Maya2024Compat
    PCMValidator --> Maya2025PCM
    
    Maya2025PCM --> SixteenBitPCM
    SixteenBitPCM --> SampleRateSupport
    SampleRateSupport --> MonoChannelSupport
    
    MayaAudioAPI --> Maya2024Compat
    MayaAudioAPI --> Maya2025PCM
```

Sources: [docs/additionals.md:4-9](), [docs/additionals.md:15-20]()

## Compatibility Matrix

The following table summarizes the compatibility requirements across different Maya versions:

| Component | Maya 2024 | Maya 2025 | Notes |
|-----------|-----------|-----------|--------|
| Audio File Library | AudioFile library | AudioFile library | External dependency |
| WAV Support | Full WAV support | PCM WAV only | Format constraint |
| AIFF Support | Full AIFF support | PCM AIFF only | Format constraint |
| Bit Depth | Variable | 16-bit PCM recommended | Performance optimization |
| Sample Rate | Variable | 16/32/48 kHz recommended | Maya timeline compatibility |
| Channel Count | Multi-channel | Mono recommended | Processing efficiency |

Sources: [docs/additionals.md:7-9](), [docs/additionals.md:15-20]()

## Sample Resource Specifications

Maya-ACE includes access to professional-grade sample content for testing and demonstration purposes:

**Sample Project Structure**

```mermaid
graph TB
    subgraph "Reallusion Sample Package"
        ZipArchive["Reallusion_Character_Camila.zip"]
        ReadmeFile["README.txt"]
        MayaProject["Maya Project Files"]
    end
    
    subgraph "Character Content"
        CamilaCharacter["Camila Character Model"]
        CC4Generated["Character Creator 4 Generated"]
        BlendshapeTargets["ARKit Blendshape Targets"]
    end
    
    subgraph "Rendering Assets"
        ArnoldMaterials["Arnold Render Materials"]
        TextureMaps["Texture Maps"]
        ShaderNetwork["Shader Network"]
    end
    
    subgraph "Technical Specifications"
        FileSize["2.1GB Package Size"]
        LicenseAgreement["Reallusion License"]
        SetupInstructions["Setup Instructions"]
    end
    
    ZipArchive --> ReadmeFile
    ZipArchive --> MayaProject
    
    MayaProject --> CamilaCharacter
    CamilaCharacter --> CC4Generated
    CC4Generated --> BlendshapeTargets
    
    CamilaCharacter --> ArnoldMaterials
    ArnoldMaterials --> TextureMaps
    TextureMaps --> ShaderNetwork
    
    ReadmeFile --> SetupInstructions
    ZipArchive --> FileSize
    ZipArchive --> LicenseAgreement
```

Sources: [docs/reallusionsample.md:3-10]()

## Resource Locations

| Resource Type | Location | Size | Description |
|---------------|----------|------|-------------|
| Sample Character | Reallusion Download | ~2.1GB | Complete Maya project with Camila character |
| Documentation | README.txt | - | Setup instructions included in sample |
| License Agreement | Sample archive | - | Reallusion license terms |
| Character Assets | Maya project files | - | CC4-generated character with materials |

## External References

- [AudioFile Library Documentation](https://github.com/adamstark/AudioFile)
- [Maya Audio File Format Support](https://help.autodesk.com/view/MAYAUL/2024/ENU/?guid=GUID-CF2B0358-6946-4C9D-9F8C-A783921CAECC)
- [Reallusion Character Creator](https://www.reallusion.com)

Sources: [docs/additionals.md:4-5](), [docs/reallusionsample.md:3]()

---

