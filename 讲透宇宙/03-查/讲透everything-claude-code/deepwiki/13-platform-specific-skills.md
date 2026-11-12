<!-- source: DeepWiki mcp.deepwiki.com · repo affaan-m/everything-claude-code · page 13 Platform-Specific Skills · fetched 2026-10-26 -->

# Platform-Specific Skills

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [skills/foundation-models-on-device/SKILL.md](skills/foundation-models-on-device/SKILL.md)
- [skills/liquid-glass-design/SKILL.md](skills/liquid-glass-design/SKILL.md)
- [skills/swift-concurrency-6-2/SKILL.md](skills/swift-concurrency-6-2/SKILL.md)

</details>



## Purpose and Scope

This section documents skills that target specific platform features, language versions, or vendor-specific APIs. Platform-specific skills provide workflow patterns for capabilities that are not cross-platform and require specialized knowledge of a particular ecosystem.

These skills differ from general framework skills (see [Skills Reference](#5.2)) in that they address:
- Version-specific language features (e.g., Swift 6.2 concurrency model changes).
- Vendor-specific frameworks (e.g., Apple's FoundationModels for on-device LLM).
- Platform design systems (e.g., iOS 26 Liquid Glass material).
- Language-specific testing and build workflows.

Currently, platform-specific skills target Swift/iOS and Kotlin/JVM ecosystems. For general-purpose skills that work across platforms, see [Skills Reference](#5.2).

---

## Platform-Specific Skills Architecture

The following diagram shows how platform-specific skills integrate with the broader ECC skill system, bridging natural language requirements to code-level implementations.

### ECC Platform Skill Integration
```mermaid
graph TB
    subgraph "General_Skills_System"
        [SkillRef] --> [Framework]
        [SkillRef] --> [Language]
    end
    
    subgraph "Platform-Specific_Skills_13"
        [Swift62]
        [FndModels]
        [LiquidGlass]
    end
    
    subgraph "Activation_Triggers"
        [ProjectDetect]
        [VersionCheck]
        [PlatformCheck]
    end
    
    subgraph "Skill_Storage"
        [SkillMD] --> [Frontmatter]
        [SkillMD] --> [Content]
    end
    
    [SkillRef] -.-> [Swift62]
    [SkillRef] -.-> [FndModels]
    [SkillRef] -.-> [LiquidGlass]
    
    [ProjectDetect] --> [Swift62]
    [VersionCheck] --> [Swift62]
    [VersionCheck] --> [FndModels]
    [PlatformCheck] --> [FndModels]
    
    [Swift62] --> [SkillMD]
    [FndModels] --> [SkillMD]
    [LiquidGlass] --> [SkillMD]
```

**Sources:** [skills/swift-concurrency-6-2/SKILL.md:1-4](), [skills/foundation-models-on-device/SKILL.md:1-4](), [skills/liquid-glass-design/SKILL.md:1-4]()

---

## Swift 6.2 Approachable Concurrency

### Overview

The `swift-concurrency-6-2` skill documents Swift 6.2's fundamental shift in concurrency semantics: async functions now stay on the calling actor by default instead of implicitly offloading to background threads [skills/swift-concurrency-6-2/SKILL.md:38-51](). This eliminates a major class of data-race errors. For details, see [Swift 6.2 Concurrency](#13.1).

| Aspect | Details |
|--------|---------|
| **Skill Name** | `swift-concurrency-6-2` |
| **File Location** | [skills/swift-concurrency-6-2/SKILL.md]() |
| **Target Platform** | Swift 6.2+, Xcode 26+ |
| **Key Proposals** | SE-0466 (MainActor isolation), SE-0461 (NonisolatedNonsendingByDefault) |

**Sources:** [skills/swift-concurrency-6-2/SKILL.md:1-17](), [skills/swift-concurrency-6-2/SKILL.md:139-139]()

### Key Code Patterns

#### Isolated Conformances
MainActor types can conform to non-isolated protocols safely using `@MainActor` extensions [skills/swift-concurrency-6-2/SKILL.md:64-68]().

#### Explicit Background Offloading
Actual parallelism is achieved via the `@concurrent` attribute on functions, requiring the containing type to be `nonisolated` [skills/swift-concurrency-6-2/SKILL.md:142-158]().

---

## FoundationModels: On-Device LLM

### Overview

The `foundation-models-on-device` skill documents Apple's FoundationModels framework for integrating on-device language models into iOS 26+ apps. All processing happens on-device for privacy and offline support [skills/foundation-models-on-device/SKILL.md:6-8](). For details, see [FoundationModels (On-Device LLM)](#13.2).

| Aspect | Details |
|--------|---------|
| **Skill Name** | `foundation-models-on-device` |
| **File Location** | [skills/foundation-models-on-device/SKILL.md]() |
| **Target Platform** | iOS 26+, requires Apple Intelligence-capable device |
| **Core API** | `SystemLanguageModel`, `LanguageModelSession` |

**Sources:** [skills/foundation-models-on-device/SKILL.md:1-18](), [skills/foundation-models-on-device/SKILL.md:25-25](), [skills/foundation-models-on-device/SKILL.md:48-48]()

### Core API Patterns

#### Guided Generation with @Generable
The `@Generable` macro allows generating structured Swift types instead of raw strings [skills/foundation-models-on-device/SKILL.md:76-86]().

#### Tool Protocol
Custom code can be invoked by the model through the `Tool` protocol, using `@Generable` for argument schema [skills/foundation-models-on-device/SKILL.md:115-133]().

---

## Liquid Glass Design System

### Overview

The `liquid-glass-design` skill documents iOS 26's Liquid Glass material — a dynamic effect that blurs background content, reflects surrounding colors, and reacts to touch interactions [skills/liquid-glass-design/SKILL.md:6-8](). For details, see [Liquid Glass Design System](#13.3).

| Aspect | Details |
|--------|---------|
| **Skill Name** | `liquid-glass-design` |
| **File Location** | [skills/liquid-glass-design/SKILL.md]() |
| **Target Platform** | iOS 26+ |
| **Key Components** | `.glassEffect()`, `GlassEffectContainer`, `UIGlassEffect` |

**Sources:** [skills/liquid-glass-design/SKILL.md:1-17](), [skills/liquid-glass-design/SKILL.md:28-29](), [skills/liquid-glass-design/SKILL.md:61-61](), [skills/liquid-glass-design/SKILL.md:136-136]()

### SwiftUI Patterns

#### GlassEffectContainer
Multiple glass elements should be wrapped in a `GlassEffectContainer` to control merge distance via the `spacing` parameter [skills/liquid-glass-design/SKILL.md:61-76]().

#### Morphing Transitions
Using `.glassEffectID(_:in:)` with a `@Namespace` enables smooth morphing when elements appear or disappear [skills/liquid-glass-design/SKILL.md:102-117]().

---

## Platform-Specific Entity Mapping

This diagram bridges natural language platform concepts to the specific code entities documented in these skills.

### Concept to Code Mapping
```mermaid
graph LR
    subgraph "Natural_Language_Concept"
        [Concur]
        [LLM]
        [Glass]
    end

    subgraph "Code_Entity_Space"
        [SE0466]
        [SE0461]
        
        [SysLM]
        [GenMacro]
        
        [GlassMod]
        [GlassCont]
    end

    [Concur] --> [SE0466]
    [Concur] --> [SE0461]
    [LLM] --> [SysLM]
    [LLM] --> [GenMacro]
    [Glass] --> [GlassMod]
    [Glass] --> [GlassCont]
```

**Sources:** [skills/swift-concurrency-6-2/SKILL.md:42](), [skills/swift-concurrency-6-2/SKILL.md:156](), [skills/foundation-models-on-device/SKILL.md:25](), [skills/foundation-models-on-device/SKILL.md:76](), [skills/liquid-glass-design/SKILL.md:28](), [skills/liquid-glass-design/SKILL.md:61]()

---

## Best Practices Summary

### Implementation Priority
1. **Check Availability**: For on-device LLM, always check `SystemLanguageModel.default.availability` [skills/foundation-models-on-device/SKILL.md:25-42]().
2. **Prefer MainActor**: In Swift 6.2, start on the `MainActor` and only offload CPU-intensive work using `@concurrent` [skills/swift-concurrency-6-2/SKILL.md:193-195]().
3. **Containerize UI**: Use `GlassEffectContainer` for performance when using multiple glass elements [skills/liquid-glass-design/SKILL.md:61-76]().
4. **Use Isolated Conformances**: Prefer `@MainActor` protocol extensions over `nonisolated` workarounds [skills/swift-concurrency-6-2/SKILL.md:64-68]().
5. **Snapshot Streaming**: Use `LanguageModelSession.streamResponse` for real-time structured UI updates [skills/foundation-models-on-device/SKILL.md:166-175]().

**Sources:** [skills/swift-concurrency-6-2/SKILL.md:191-199](), [skills/foundation-models-on-device/SKILL.md:217-226](), [skills/liquid-glass-design/SKILL.md:61-76]()

---

