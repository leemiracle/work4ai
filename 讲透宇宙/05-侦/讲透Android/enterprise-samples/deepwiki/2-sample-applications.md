<!-- source: DeepWiki mcp.deepwiki.com · repo android/enterprise-samples · page 2 Sample Applications · fetched 2026-10-23 -->

# Sample Applications

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [ManagedConfigurations/app/src/main/java/com/example/android/managedconfigurations/MainActivity.kt](ManagedConfigurations/app/src/main/java/com/example/android/managedconfigurations/MainActivity.kt)
- [ManagedConfigurations/app/src/main/java/com/example/android/managedconfigurations/ManagedConfigurationsFragment.kt](ManagedConfigurations/app/src/main/java/com/example/android/managedconfigurations/ManagedConfigurationsFragment.kt)
- [ManagedConfigurations/app/src/main/res/values/styles.xml](ManagedConfigurations/app/src/main/res/values/styles.xml)
- [ManagedConfigurations/build.gradle.kts](ManagedConfigurations/build.gradle.kts)
- [ManagedConfigurations/gradle.properties](ManagedConfigurations/gradle.properties)
- [Work-profile-codelab/app-finished/src/main/java/com/example/workprofile/MainActivity.kt](Work-profile-codelab/app-finished/src/main/java/com/example/workprofile/MainActivity.kt)
- [Work-profile-codelab/app-finished/src/main/res/values/styles.xml](Work-profile-codelab/app-finished/src/main/res/values/styles.xml)

</details>



This document provides an overview of the two main sample applications in the Android Enterprise Samples repository that demonstrate different enterprise capabilities. These applications serve as practical examples and learning resources for developers implementing Android Enterprise features.

For detailed documentation of each individual sample application, see [ManagedConfigurations Sample](#2.1) and [Work Profile Codelab](#2.2). For information about the build system and CI/CD infrastructure that supports these applications, see [Build System](#3).

## Repository Structure and Sample Applications

The repository contains two distinct sample applications that demonstrate different aspects of Android Enterprise functionality:

```mermaid
graph TB
    subgraph "Android Enterprise Samples Repository"
        subgraph "ManagedConfigurations"
            MC_MA["MainActivity"]
            MC_MF["ManagedConfigurationsFragment"]
            MC_RM["RestrictionsManager"]
            MC_BR["BroadcastReceiver"]
        end
        
        subgraph "Work-profile-codelab"
            WP_S["app-starter"]
            WP_F["app-finished"]
            WP_MA["MainActivity"]
            WP_CPA["CrossProfileApps"]
            WP_CC["ContactsContract"]
        end
        
        subgraph "Enterprise Systems"
            EMM["EMM System"]
            DPC["Device Policy Controller"]
            WP["Work Profile"]
        end
    end
    
    EMM --> MC_RM
    DPC --> MC_RM
    MC_RM --> MC_MF
    MC_MF --> MC_MA
    MC_BR --> MC_MF
    
    WP --> WP_CPA
    WP_CPA --> WP_MA
    WP_CC --> WP_MA
    WP_S --> WP_F
```

**Sample Applications Architecture Overview**

Sources: [ManagedConfigurations/app/src/main/java/com/example/android/managedconfigurations/MainActivity.kt:1-117](), [Work-profile-codelab/app-finished/src/main/java/com/example/workprofile/MainActivity.kt:1-156](), [ManagedConfigurations/app/src/main/java/com/example/android/managedconfigurations/ManagedConfigurationsFragment.kt:1-255]()

## Sample Applications Overview

| Sample Application | Primary Purpose | Key Components | Target Use Case |
|-------------------|----------------|----------------|-----------------|
| ManagedConfigurations | Demonstrates app restrictions and managed configurations | `RestrictionsManager`, `BroadcastReceiver`, `RestrictionEntry` | Enterprise app configuration management |
| Work-profile-codelab | Teaches work profile implementation with starter and finished versions | `CrossProfileApps`, `ContactsContract`, profile switching | Cross-profile application development |

## ManagedConfigurations Sample

The ManagedConfigurations sample demonstrates how applications can receive and respond to restrictions set by enterprise administrators through EMM systems or Device Policy Controllers.

```mermaid
graph TB
    subgraph "ManagedConfigurations Application Flow"
        MA["MainActivity"]
        MCF["ManagedConfigurationsFragment"]
        RM["RestrictionsManager"]
        BR["BroadcastReceiver"]
        RE["RestrictionEntry"]
        
        subgraph "Restriction Types"
            BOOL["Boolean: can_say_hello"]
            STR["String: message"]
            INT["Integer: number"]
            RANK["Choice: rank"]
            ARRAY["String Array: approvals"]
            BUNDLE["Bundle Array: items"]
        end
        
        subgraph "UI Components"
            BTN["sayHello Button"]
            NUM["yourNumber TextView"]
            RNK["yourRank TextView"]
            APP["approvalsYouHave TextView"]
            ITM["yourItems TextView"]
        end
    end
    
    MA --> MCF
    MCF --> RM
    RM --> RE
    BR --> MCF
    
    RE --> BOOL
    RE --> STR
    RE --> INT
    RE --> RANK
    RE --> ARRAY
    RE --> BUNDLE
    
    BOOL --> BTN
    INT --> NUM
    RANK --> RNK
    ARRAY --> APP
    BUNDLE --> ITM
```

**ManagedConfigurations Component Architecture**

The sample handles six different types of restrictions defined in [ManagedConfigurations/app/src/main/java/com/example/android/managedconfigurations/ManagedConfigurationsFragment.kt:245-252]():

- `KEY_CAN_SAY_HELLO`: Boolean restriction controlling button enablement
- `KEY_MESSAGE`: String restriction for toast message content  
- `KEY_NUMBER`: Integer restriction displayed in UI
- `KEY_RANK`: Choice restriction from predefined options
- `KEY_APPROVALS`: String array restriction for multiple selections
- `KEY_ITEMS`: Bundle array restriction for complex data structures

Sources: [ManagedConfigurations/app/src/main/java/com/example/android/managedconfigurations/ManagedConfigurationsFragment.kt:101-133](), [ManagedConfigurations/app/src/main/java/com/example/android/managedconfigurations/MainActivity.kt:56-61]()

## Work Profile Codelab

The Work Profile Codelab provides both starter and finished implementations to teach developers how to build applications that work seamlessly across personal and work profiles.

```mermaid
graph TB
    subgraph "Work Profile Codelab Structure"
        subgraph "app-starter"
            AS_MA["MainActivity (Basic)"]
            AS_UI["Basic UI Setup"]
        end
        
        subgraph "app-finished"
            AF_MA["MainActivity (Complete)"]
            AF_CPA["CrossProfileApps"]
            AF_CC["ContactsContract"]
            AF_LL["LoaderManager"]
            AF_CA["ContactsAdapter"]
        end
        
        subgraph "Profile Functionality"
            PS["Profile Switching"]
            PC["Personal Contacts"]
            WC["Work Contacts"]
            CPL["Cross-Profile Launch"]
        end
        
        subgraph "Permissions"
            RCP["READ_CONTACTS Permission"]
            PRM["Permission Request Flow"]
        end
    end
    
    AS_MA --> AF_MA
    AF_MA --> AF_CPA
    AF_MA --> AF_CC
    AF_MA --> AF_LL
    AF_LL --> AF_CA
    
    AF_CPA --> PS
    AF_CPA --> CPL
    AF_CC --> PC
    AF_CC --> WC
    
    RCP --> PRM
    PRM --> AF_CC
```

**Work Profile Codelab Learning Progression**

The finished implementation in [Work-profile-codelab/app-finished/src/main/java/com/example/workprofile/MainActivity.kt:75-86]() demonstrates key cross-profile functionality:

- Profile detection using `CrossProfileApps.targetUserProfiles`
- Profile switching with `CrossProfileApps.startMainActivity()`
- Dual contact loading from personal and enterprise directories
- Permission handling for cross-profile contact access

The application loads contacts from both profiles using different `ContactsContract` URIs:
- Personal contacts: `ContactsContract.Contacts.CONTENT_URI`
- Work contacts: `ContactsContract.Contacts.ENTERPRISE_CONTENT_FILTER_URI`

Sources: [Work-profile-codelab/app-finished/src/main/java/com/example/workprofile/MainActivity.kt:108-136](), [Work-profile-codelab/app-finished/src/main/java/com/example/workprofile/MainActivity.kt:75-86](), [Work-profile-codelab/app-finished/src/main/java/com/example/workprofile/MainActivity.kt:65-73]()

## Enterprise Integration Points

Both sample applications demonstrate different aspects of Android Enterprise integration:

| Integration Area | ManagedConfigurations | Work Profile Codelab |
|-----------------|---------------------|-------------------|
| **EMM Communication** | `RestrictionsManager.applicationRestrictions` | `CrossProfileApps.targetUserProfiles` |
| **Runtime Updates** | `Intent.ACTION_APPLICATION_RESTRICTIONS_CHANGED` | Profile state changes |
| **Data Access** | Restriction values and types | Cross-profile contacts |
| **User Experience** | Dynamically configured UI | Seamless profile switching |

The ManagedConfigurations sample uses [ManagedConfigurations/app/src/main/java/com/example/android/managedconfigurations/ManagedConfigurationsFragment.kt:82-85]() to register for restriction changes, while the Work Profile Codelab demonstrates cross-profile capabilities through [Work-profile-codelab/app-finished/src/main/java/com/example/workprofile/MainActivity.kt:75-86]().

Sources: [ManagedConfigurations/app/src/main/java/com/example/android/managedconfigurations/ManagedConfigurationsFragment.kt:77-85](), [Work-profile-codelab/app-finished/src/main/java/com/example/workprofile/MainActivity.kt:42-87]()

---

