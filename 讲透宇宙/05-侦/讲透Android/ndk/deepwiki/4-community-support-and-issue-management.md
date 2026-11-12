<!-- source: DeepWiki mcp.deepwiki.com · repo android/ndk · page 4 Community Support and Issue Management · fetched 2026-10-23 -->

# Community Support and Issue Management

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/ISSUE_TEMPLATE/config.yml](.github/ISSUE_TEMPLATE/config.yml)

</details>



## Purpose and Scope

This document provides an overview of the comprehensive issue management system and community support channels for the Android NDK. It explains how user-submitted issues are automatically routed to appropriate teams and support channels through a sophisticated GitHub configuration system.

For detailed information about the technical implementation of issue routing, see [Issue Routing System](#4.1). For specific bug reporting processes and templates, see [Bug Reporting Process](#4.2). For feature request and documentation workflows, see [Feature Requests and Documentation Issues](#4.3).

## Issue Management Architecture

The NDK project implements a sophisticated issue management system that automatically routes user inquiries to the most appropriate support channels. This system prevents misdirected issues and ensures users receive help from the correct teams.

### GitHub Issue Routing Configuration

The core of the issue management system is implemented through GitHub's issue template configuration, which disables blank issue creation and provides structured routing options.

```mermaid
flowchart TD
    User["User Creates Issue"]
    ConfigYml["config.yml Configuration"]
    BlankDisabled["blank_issues_enabled: false"]
    
    subgraph "Contact Links Routing"
        StudioLink["Android Studio and Gradle issues"]
        OSLink["Android OS issues, new NDK API requests"]
        QuestionsLink["Questions"]
    end
    
    subgraph "External Destinations"
        StudioTracker["developer.android.com/studio/report-bugs"]
        AOSPTracker["source.android.com/setup/contribute/report-bugs"]
        Discussions["github.com/android/ndk/discussions"]
    end
    
    subgraph "Issue Templates"
        BugTemplate["Bug Report Template"]
        FeatureTemplate["Feature Request Template"]
        DocTemplate["Documentation Bug Template"]
        LLVMTemplate["LLVM Bug Template"]
    end
    
    User --> ConfigYml
    ConfigYml --> BlankDisabled
    ConfigYml --> StudioLink
    ConfigYml --> OSLink
    ConfigYml --> QuestionsLink
    
    StudioLink --> StudioTracker
    OSLink --> AOSPTracker
    QuestionsLink --> Discussions
    
    ConfigYml --> BugTemplate
    ConfigYml --> FeatureTemplate
    ConfigYml --> DocTemplate
    ConfigYml --> LLVMTemplate
```

**Issue Routing System Configuration**

Sources: [.github/ISSUE_TEMPLATE/config.yml:1-31]()

The routing system is configured through three main contact links defined in the `config.yml` file:

| Route | URL | Purpose |
|-------|-----|---------|
| Android Studio and Gradle issues | `https://developer.android.com/studio/report-bugs` | Redirects IDE and build plugin issues to Android Studio team |
| Android OS issues, new NDK API requests | `https://source.android.com/setup/contribute/report-bugs` | Routes platform-level issues to AOSP Framework component |
| Questions | `https://github.com/android/ndk/discussions` | Directs general questions to GitHub Discussions forum |

## Issue Classification and Routing Logic

The system automatically classifies and routes issues based on their nature, preventing the NDK team from handling issues outside their scope.

```mermaid
flowchart LR
    subgraph "Issue Classification"
        UserIssue["User Issue"]
        Classification{"Issue Type Classification"}
    end
    
    subgraph "NDK Team Scope"
        NDKBugs["NDK Runtime Bugs"]
        NDKFeatures["NDK Feature Requests"]
        NDKDocs["NDK Documentation Issues"]
        LLVMIssues["LLVM/Clang Issues"]
    end
    
    subgraph "External Team Scope"
        StudioIssues["Android Studio Issues"]
        AGPIssues["Android Gradle Plugin Issues"]
        OSIssues["Android OS Framework Issues"]
        APIRequests["New Platform API Requests"]
    end
    
    subgraph "Community Support"
        GeneralQuestions["General NDK Questions"]
        UsageHelp["Usage Help"]
        BestPractices["Best Practices"]
    end
    
    UserIssue --> Classification
    
    Classification --> NDKBugs
    Classification --> NDKFeatures
    Classification --> NDKDocs
    Classification --> LLVMIssues
    
    Classification --> StudioIssues
    Classification --> AGPIssues
    Classification --> OSIssues
    Classification --> APIRequests
    
    Classification --> GeneralQuestions
    Classification --> UsageHelp
    Classification --> BestPractices
```

**Issue Classification Matrix**

Sources: [.github/ISSUE_TEMPLATE/config.yml:4-10](), [.github/ISSUE_TEMPLATE/config.yml:11-20](), [.github/ISSUE_TEMPLATE/config.yml:21-30]()

### Android Studio and Gradle Issues

Issues related to Android Studio IDE or Android Gradle Plugin are automatically redirected because they are maintained by separate teams. The configuration explicitly states that such issues "are not handled by this team and must be filed against the Android Studio team."

**Key characteristics of redirected issues:**
- IDE functionality problems
- Build system integration issues
- Gradle plugin configuration problems
- Android Studio-specific debugging issues

### Android OS and Framework Issues

Device and OS-level issues typically cannot be fixed in the NDK itself. These are routed to the AOSP Framework component with specific guidance to avoid using the NDK component in the bug tracker.

**Routing guidance from config.yml:**
- "Do not use the NDK component. That will just bring you back here"
- Users should select the "Framework component for this type of bug"
- NDK team may add workarounds, but core fixes must come from OS team

### Community Questions and Discussions

General questions and usage inquiries are directed to GitHub Discussions to maintain separation between bug reports and community support.

## Integration with Android Development Ecosystem

The NDK issue management system integrates with the broader Android development support infrastructure, ensuring users receive appropriate help regardless of their issue's scope.

```mermaid
graph TB
    subgraph "User Entry Point"
        NDKRepo["android/ndk GitHub Repository"]
        IssueCreation["Create New Issue"]
    end
    
    subgraph "Routing Configuration"
        ConfigSystem["config.yml Routing System"]
        BlankIssuesDisabled["blank_issues_enabled: false"]
        ContactLinks["contact_links Array"]
    end
    
    subgraph "Android Development Support Ecosystem"
        StudioSupport["Android Studio Bug Tracker"]
        AOSPSupport["AOSP Issue Tracker"]
        NDKDiscussions["GitHub Discussions"]
        NDKIssueTemplates["NDK Issue Templates"]
    end
    
    subgraph "Team Responsibilities"
        StudioTeam["Android Studio Team"]
        FrameworkTeam["Android Framework Team"]
        NDKTeam["NDK Team"]
        Community["Developer Community"]
    end
    
    NDKRepo --> IssueCreation
    IssueCreation --> ConfigSystem
    ConfigSystem --> BlankIssuesDisabled
    ConfigSystem --> ContactLinks
    
    ContactLinks --> StudioSupport
    ContactLinks --> AOSPSupport
    ContactLinks --> NDKDiscussions
    ContactLinks --> NDKIssueTemplates
    
    StudioSupport --> StudioTeam
    AOSPSupport --> FrameworkTeam
    NDKDiscussions --> Community
    NDKIssueTemplates --> NDKTeam
```

**Ecosystem Integration Points**

Sources: [.github/ISSUE_TEMPLATE/config.yml:1-31]()

The issue management system serves as a critical routing hub that connects users with the appropriate support resources across the Android development ecosystem. This prevents issue duplication and ensures efficient resource utilization across different Android development teams.

## Community Support Channels

The NDK project provides multiple support channels tailored to different types of user needs:

### GitHub Discussions Forum
Primary venue for questions, usage help, and community interaction. The forum handles:
- General NDK usage questions
- Best practices discussions
- Community-driven troubleshooting
- Feature discussion and feedback

### Structured Issue Templates
For confirmed bugs and feature requests, users can access specialized templates that gather necessary technical information for effective triage and resolution.

### Documentation and Guides
Comprehensive documentation resources help users find answers to common questions without requiring direct support interaction.

The routing system's effectiveness relies on clear communication about scope boundaries and appropriate escalation paths, ensuring users receive timely and relevant assistance from the most qualified support resources.

Sources: [.github/ISSUE_TEMPLATE/config.yml:1-31]()

---

