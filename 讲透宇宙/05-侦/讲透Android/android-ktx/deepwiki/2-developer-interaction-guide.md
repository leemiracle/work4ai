<!-- source: DeepWiki mcp.deepwiki.com · repo android/android-ktx · page 2 Developer Interaction Guide · fetched 2026-10-23 -->

# Developer Interaction Guide

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)

</details>



## Purpose and Scope

This guide outlines the procedures and channels for developers to interact with Android KTX libraries following the transition to the Android Open Source Project (AOSP). It covers how to report issues, request features, contribute code, and effectively engage with the Android KTX ecosystem now that the original repository has been deprecated.

For historical information about the Android KTX project before its transition, see [Project History and Versioning](#3). For specific details on reporting issues and contributing code, see [Reporting Issues and Feature Requests](#2.1) and [Contributing Code](#2.2).

Sources: [README.md:4-13]()

## Repository Transition Overview

The Android KTX repository has undergone a significant transition. Originally developed as a standalone repository, all development activities have now moved to the Android Open Source Project (AOSP). This means that the original repository is no longer accepting pull requests or issues, and all development work takes place within AOSP.

```mermaid
flowchart TD
    subgraph "Previous Structure"
        OrigRepo["android/android-ktx Repository"]
        OrigIssues["GitHub Issues"]
        OrigPRs["GitHub Pull Requests"]
    end
    
    subgraph "Current Structure"
        AOSP["Android Open Source Project"]
        IssueTracker["Google Issue Tracker<br>(component=396204)"]
        AOSPContrib["AOSP Contribution Process"]
    end
    
    OrigRepo -->|"Transition"| AOSP
    OrigIssues -->|"Migrated to"| IssueTracker
    OrigPRs -->|"Migrated to"| AOSPContrib
    
    AOSP -->|"Contains"| CoreKTX["core-ktx"]
    AOSP -->|"Contains"| OtherKTX["Other KTX Libraries"]
```

*Diagram: Android KTX Repository Transition*

Sources: [README.md:4-13]()

## Current Developer Interaction Workflow

Developers now interact with Android KTX through AOSP channels rather than the original GitHub repository. This ensures standardized development processes and better integration with other Android components.

```mermaid
flowchart LR
    Dev["Developer"]
    
    subgraph "Developer Actions"
        ReportIssue["Report Bug/Feature"]
        Contribute["Contribute Code"]
        UseLibraries["Use KTX Libraries"]
    end
    
    subgraph "AOSP Ecosystem"
        IssueTracker["Google Issue Tracker<br>(component=396204)"]
        AOSPRepo["AOSP Repository<br>(platform/frameworks/support)"]
        Libraries["KTX Libraries<br>(core-ktx, etc.)"]
    end
    
    Dev --> ReportIssue
    Dev --> Contribute
    Dev --> UseLibraries
    
    ReportIssue -->|"Submit to"| IssueTracker
    Contribute -->|"Submit to"| AOSPRepo
    UseLibraries -->|"Import from"| Libraries
```

*Diagram: Developer Interaction Workflow*

Sources: [README.md:4-13]()

## Reporting Issues and Feature Requests

All bug reports, feature suggestions, and other issue tracking for Android KTX libraries are now handled through Google's Issue Tracker rather than GitHub Issues.

### Process for Issue Reporting

1. Navigate to Google's Issue Tracker at https://issuetracker.google.com/issues/new
2. Select component ID: 396204 (specific to Android KTX libraries)
3. Provide detailed information about the issue or feature request
4. Submit the issue

| Category | Platform | Link |
|----------|----------|------|
| Bug Reports | Google Issue Tracker | Component ID: 396204 |
| Feature Requests | Google Issue Tracker | Component ID: 396204 |
| General Queries | Google Issue Tracker | Component ID: 396204 |

```mermaid
sequenceDiagram
    actor Dev as Developer
    participant IT as Google Issue Tracker
    participant AOSP as AOSP Team
    
    Dev->>IT: Create new issue with component=396204
    Note over Dev,IT: Include device, OS version, library version
    Note over Dev,IT: Provide reproduction steps
    IT->>AOSP: Route issue to appropriate team
    AOSP->>IT: Update issue status/respond
    IT->>Dev: Notification of updates
```

*Diagram: Issue Reporting Process*

Sources: [README.md:7-8]()

## Contributing Code

Code contributions to Android KTX libraries must now follow the AOSP contribution process. The original repository no longer accepts pull requests.

### Contribution Process

1. Set up AOSP development environment
2. Navigate to the platform/frameworks/support repository
3. Follow the contribution guidelines in the repository's README
4. Submit code changes through the AOSP gerrit system

```mermaid
flowchart TD
    Dev["Developer"]
    AOSPSetup["Set up AOSP Environment"]
    FindRepo["Navigate to platform/frameworks/support"]
    ReadDocs["Read Contribution Guidelines"]
    MakeChanges["Make Code Changes"]
    RunTests["Run Tests"]
    SubmitChange["Submit through Gerrit"]
    CodeReview["Code Review Process"]
    Merge["Changes Merged"]
    
    Dev --> AOSPSetup
    AOSPSetup --> FindRepo
    FindRepo --> ReadDocs
    ReadDocs --> MakeChanges
    MakeChanges --> RunTests
    RunTests -->|"Tests pass"| SubmitChange
    RunTests -->|"Tests fail"| MakeChanges
    SubmitChange --> CodeReview
    CodeReview -->|"Approved"| Merge
    CodeReview -->|"Needs revision"| MakeChanges
```

*Diagram: Code Contribution Process*

Sources: [README.md:10-11]()

## KTX Libraries Structure in AOSP

The Android KTX libraries are now organized within the AOSP structure, primarily in the platform/frameworks/support repository.

```mermaid
flowchart TD
    AOSP["Android Open Source Project"]
    FrameworksSupport["platform/frameworks/support"]
    
    AOSP --> FrameworksSupport
    
    FrameworksSupport --> CoreKTX["core-ktx"]
    FrameworksSupport --> FragmentKTX["fragment-ktx"]
    FrameworksSupport --> PaletteKTX["palette-ktx"]
    FrameworksSupport --> CollectionKTX["collection-ktx"]
    FrameworksSupport --> SqliteKTX["sqlite-ktx"]
    FrameworksSupport --> OtherKTX["Other KTX libraries"]
```

*Diagram: KTX Libraries in AOSP Structure*

Sources: [README.md:10-11]()

## Communication Channels

As part of the transition to AOSP, the communication channels for Android KTX have changed. Developers should be aware of the current channels for effective interaction.

| Channel Type | Previous | Current |
|--------------|----------|---------|
| Issue Tracking | GitHub Issues | Google Issue Tracker (component=396204) |
| Code Contributions | GitHub Pull Requests | AOSP Gerrit |
| Documentation | GitHub Wiki | AOSP Documentation |

```mermaid
sequenceDiagram
    actor Dev as Developer
    participant AOSP as AOSP Community
    participant IT as Issue Tracker
    participant Gerrit as AOSP Gerrit
    
    Note over Dev,Gerrit: Key Communication Channels
    
    Dev->>IT: Report bugs/request features
    IT->>Dev: Issue updates
    
    Dev->>Gerrit: Submit code changes
    Gerrit->>Dev: Code review feedback
    
    Dev->>AOSP: Questions and discussions
    AOSP->>Dev: Community support
```

*Diagram: Communication Channels*

Sources: [README.md:4-13]()

## Summary

The migration of Android KTX to AOSP represents a significant change in how developers interact with these libraries. By following the guidelines in this document, developers can effectively:

1. Report issues and request features through Google's Issue Tracker
2. Contribute code through the AOSP contribution process
3. Access the latest KTX libraries through the AOSP ecosystem

This transition aligns Android KTX development with the broader Android development process, providing a more integrated experience for developers.

Sources: [README.md:4-13]()

---

