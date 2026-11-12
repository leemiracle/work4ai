<!-- source: DeepWiki mcp.deepwiki.com · repo plandex-ai/plandex · page 2 CLI Reference · fetched 2026-10-26 -->

# CLI Reference

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [app/cli/cmd/current.go](app/cli/cmd/current.go)
- [app/cli/cmd/new.go](app/cli/cmd/new.go)
- [app/cli/cmd/plan_start_helpers.go](app/cli/cmd/plan_start_helpers.go)
- [app/cli/cmd/repl.go](app/cli/cmd/repl.go)
- [app/cli/cmd/root.go](app/cli/cmd/root.go)
- [app/cli/term/help.go](app/cli/term/help.go)

</details>



This document provides comprehensive documentation of the Plandex command-line interface, covering command structure, REPL functionality, and command execution patterns. For server-side API details, see [Server Architecture](#4). For AI model integration specifics, see [AI Model Integration](#5). For plan execution workflows, see [Plan Execution System](#3).

## Command Structure and Organization

The Plandex CLI provides both standalone command execution and an interactive REPL environment. Commands are organized into logical categories based on their functional purpose in the plan lifecycle.

**Command Organization by Category**

```mermaid
graph TD
    CLI["plandex / pdx CLI"]
    
    subgraph "Plan Management"
        NewCmd["new - Start new plan"]
        PlansCmd["plans (pl) - List plans"]
        CdCmd["cd - Set current plan"]
        CurrentCmd["current (cu) - Show current"]
        RenameCmd["rename - Rename plan"]
        DeletePlanCmd["delete-plan (dp) - Delete plan"]
        ArchiveCmd["archive (arc) - Archive plan"]
        UnarchiveCmd["unarchive (unarc) - Unarchive plan"]
    end
    
    subgraph "Context Management"
        LoadCmd["load (l) - Load context"]
        LsCmd["ls - List context"]
        RmCmd["rm - Remove context"]
        ClearCmd["clear - Remove all context"]
        UpdateCmd["update (u) - Update context"]
        ShowCmd["show - Show context"]
    end
    
    subgraph "Plan Execution"
        TellCmd["tell (t) - Describe task"]
        ChatCmd["chat (ch) - Ask questions"]
        ContinueCmd["continue (c) - Continue plan"]
        BuildCmd["build (b) - Build changes"]
        DebugCmd["debug (db) - Debug commands"]
    end
    
    subgraph "Change Management"
        DiffCmd["diff - Review changes"]
        ApplyCmd["apply (ap) - Apply changes"]
        RejectCmd["reject (rj) - Reject changes"]
    end
    
    subgraph "History & Branches"
        LogCmd["log - Show history"]
        RewindCmd["rewind (rw) - Rewind state"]
        ConvoCmd["convo - Show conversation"]
        SummaryCmd["summary - Show summary"]
        BranchesCmd["branches (br) - List branches"]
        CheckoutCmd["checkout (co) - Switch branch"]
        DeleteBranchCmd["delete-branch (dlb) - Delete branch"]
    end
    
    subgraph "Configuration"
        ConfigCmd["config - Show config"]
        SetConfigCmd["set-config - Update config"]
        SetAutoCmd["set-auto - Set autonomy"]
        ModelsCmd["models - Show models"]
        SetModelCmd["set-model - Update models"]
        ModelPacksCmd["model-packs - Show packs"]
    end
    
    CLI --> NewCmd
    CLI --> PlansCmd
    CLI --> LoadCmd
    CLI --> TellCmd
    CLI --> DiffCmd
    CLI --> LogCmd
    CLI --> ConfigCmd
```

Sources: [app/cli/term/help.go:19-145]()

## REPL Architecture

The REPL (Read-Eval-Print Loop) is implemented through the `go-prompt` library and provides the primary interactive interface for Plandex usage.

**REPL Component Architecture**

```mermaid
graph TB
    subgraph "REPL Core Components"
        PromptNew["prompt.New()"]
        ExecutorFunc["executor() function"]
        CompleterFunc["completer() function"]
        ParseCommandFunc["parseCommand() function"]
    end
    
    subgraph "Input Processing"
        InputCapture["Input text capture"]
        BackslashDetect["Command detection (\\\\)"]
        AtSymbolDetect["File reference (@)"]
        GetSuggestions["getSuggestions() function"]
    end
    
    subgraph "Command Execution"
        ReplBuiltins["Built-in REPL commands"]
        ExecPlandexCommand["lib.ExecPlandexCommandWithParams()"]
        TellChatModes["tell/chat mode handling"]
    end
    
    subgraph "State Management"
        CurrentReplState["lib.CurrentReplState"]
        ReplModeTell["lib.ReplModeTell"]
        ReplModeChat["lib.ReplModeChat"]
        IsMultiState["IsMulti for multiline"]
    end
    
    PromptNew --> InputCapture
    InputCapture --> BackslashDetect
    InputCapture --> AtSymbolDetect
    BackslashDetect --> ParseCommandFunc
    AtSymbolDetect --> GetSuggestions
    
    ParseCommandFunc --> ReplBuiltins
    ParseCommandFunc --> ExecPlandexCommand
    ParseCommandFunc --> TellChatModes
    
    ExecutorFunc --> CurrentReplState
    ExecutorFunc --> ReplModeTell
    CompleterFunc --> GetSuggestions
    
    ReplBuiltins -.-> IsMultiState
    ReplBuiltins -.-> ReplModeChat
```

Sources: [app/cli/cmd/repl.go:31-220](), [app/cli/cmd/repl.go:521-762]()

## Command Execution Flow

Command execution follows different paths depending on whether commands are invoked directly or through the REPL interface.

**CLI Command Execution Pipeline**

```mermaid
graph TD
    subgraph "Entry Points"
        DirectCLI["Direct CLI: plandex [cmd]"]
        ReplInterface["REPL: \\\\[cmd]"]
        AutoREPL["Auto-REPL: plandex (no args)"]
    end
    
    subgraph "Command Resolution"
        RootCmdExecute["RootCmd.Execute()"]
        ReplCmdRun["replCmd.Run()"]
        ParseFlags["cobra flag parsing"]
        CommandLookup["term.CliCommands lookup"]
    end
    
    subgraph "Authentication & Project"
        MustResolveAuth["auth.MustResolveAuthWithOrg()"]
        MustResolveProject["lib.MustResolveOrCreateProject()"]
        LoadState["lib.LoadState()"]
    end
    
    subgraph "Command Execution"
        ExecPlandexCommandWithParams["lib.ExecPlandexCommandWithParams()"]
        ApiClientCalls["api.Client method calls"]
        TermOutput["term output functions"]
        WriteState["lib.WriteState()"]
    end
    
    DirectCLI --> RootCmdExecute
    AutoREPL --> ReplCmdRun
    ReplInterface --> ExecPlandexCommandWithParams
    
    RootCmdExecute --> ParseFlags
    ReplCmdRun --> MustResolveAuth
    ParseFlags --> CommandLookup
    
    MustResolveAuth --> MustResolveProject
    MustResolveProject --> LoadState
    
    CommandLookup --> ExecPlandexCommandWithParams
    ExecPlandexCommandWithParams --> ApiClientCalls
    ApiClientCalls --> TermOutput
    TermOutput --> WriteState
```

Sources: [app/cli/cmd/root.go:15-70](), [app/cli/cmd/repl.go:72-220]()

## REPL Command Processing

The REPL implements sophisticated command processing with fuzzy matching, auto-completion, and context-aware suggestions.

**REPL Input Processing Flow**

```mermaid
graph LR
    subgraph "Input Analysis"
        UserInput["User input text"]
        LastLineExtract["Extract last line"]
        BackslashIndex["Find lastBackslashIndex"]
        AtIndex["Find lastAtIndex"]
    end
    
    subgraph "Command Matching"
        FuzzyFilter["prompt.FilterFuzzy()"]
        PrefixFilter["prompt.FilterHasPrefix()"]
        ReplCmdAliases["lib.ReplCmdAliases lookup"]
        FindSimilarCommands["findSimilarCommands()"]
    end
    
    subgraph "Suggestion Generation"
        CliSuggestions["cliSuggestions from term.CliCommands"]
        ProjectPathsSuggestions["projectPaths.ActivePaths"]
        BuiltinSuggestions["Built-in REPL suggestions"]
        FileSuggestions["File path auto-complete"]
    end
    
    subgraph "Execution Routing"
        BuiltinExecution["quit, help, multi, send execution"]
        ExecPlandexCommand["CLI command execution"]
        TellChatExecution["tell/chat mode execution"]
        FileLoading["Auto-load file references"]
    end
    
    UserInput --> LastLineExtract
    LastLineExtract --> BackslashIndex
    LastLineExtract --> AtIndex
    
    BackslashIndex --> FuzzyFilter
    BackslashIndex --> ReplCmdAliases
    FuzzyFilter --> FindSimilarCommands
    
    FindSimilarCommands --> CliSuggestions
    AtIndex --> ProjectPathsSuggestions
    ProjectPathsSuggestions --> FileSuggestions
    
    ReplCmdAliases --> BuiltinExecution
    ReplCmdAliases --> ExecPlandexCommand
    BackslashIndex --> TellChatExecution
    AtIndex --> FileLoading
```

Sources: [app/cli/cmd/repl.go:521-762](), [app/cli/cmd/repl.go:914-1035]()

## Plan Management Commands

Plan management commands handle the complete lifecycle of Plandex plans from creation through deletion.

| Command | Alias | Function | Implementation |
|---------|-------|----------|----------------|
| `new` | `n` | Create new plan | [app/cli/cmd/new.go]() |
| `plans` | `pl` | List all plans | Via `term.CliCommands` |
| `cd` | - | Switch current plan | Via `term.CliCommands` |
| `current` | `cu` | Show current plan | [app/cli/cmd/current.go]() |
| `delete-plan` | `dp` | Delete plan(s) | Via `term.CliCommands` |
| `archive` | `arc` | Archive a plan | Via `term.CliCommands` |
| `unarchive` | `unarc` | Unarchive a plan | Via `term.CliCommands` |

**Plan Creation Workflow**

```mermaid
graph TD
    NewCommand["newCmd.Run()"]
    
    subgraph "Initialization Phase"
        MustResolveAuth["auth.MustResolveAuthWithOrg()"]
        MustResolveProject["lib.MustResolveOrCreateProject()"]
        StartSpinner["term.StartSpinner()"]
    end
    
    subgraph "Concurrent API Operations"
        CreatePlanAPI["api.Client.CreatePlan()"]
        GetDefaultConfig["api.Client.GetDefaultPlanConfig()"]
        ErrorChannel["errCh chan error"]
    end
    
    subgraph "State Persistence"
        WriteCurrentPlan["lib.WriteCurrentPlan(planId)"]
        WriteCurrentBranch["lib.WriteCurrentBranch('main')"]
        ResolveAutoMode["resolveAutoMode()"]
        ResolveModelPack["resolveModelPack()"]
    end
    
    subgraph "Context Auto-Loading"
        CheckAutoLoadContext["config.AutoLoadContext check"]
        MustLoadContext["lib.MustLoadContext() with DefsOnly"]
    end
    
    NewCommand --> MustResolveAuth
    MustResolveAuth --> MustResolveProject
    MustResolveProject --> StartSpinner
    
    StartSpinner --> CreatePlanAPI
    StartSpinner --> GetDefaultConfig
    CreatePlanAPI --> ErrorChannel
    GetDefaultConfig --> ErrorChannel
    
    ErrorChannel --> WriteCurrentPlan
    WriteCurrentPlan --> WriteCurrentBranch
    WriteCurrentBranch --> ResolveAutoMode
    ResolveAutoMode --> ResolveModelPack
    
    ResolveModelPack --> CheckAutoLoadContext
    CheckAutoLoadContext --> MustLoadContext
```

Sources: [app/cli/cmd/new.go:39-134]()

## Context Management Commands

Context management provides control over what information is available to AI models during plan execution.

| Command | Alias | Purpose | Supported Types |
|---------|-------|---------|-----------------|
| `load` | `l` | Add context to plan | Files, URLs, Notes, Images, Piped data |
| `ls` | - | List current context | All context types |
| `rm` | - | Remove context items | By index/name/glob pattern |
| `clear` | - | Remove all context | All context types |
| `update` | `u` | Refresh outdated context | File-based context only |
| `show` | - | Display context content | Individual context items |

**Context Loading Strategies**

```mermaid
graph TD
    LoadCommand["load command invocation"]
    
    subgraph "Input Type Detection"
        FileInput["Files: component.ts"]
        DirectoryInput["Directories: lib"]
        URLInput["URLs: https://example.com"]
        NoteInput["Notes: -n 'instruction'"]
        ImageInput["Images: ui-mockup.png"]
        PipedInput["Piped: npm test | plandex load"]
    end
    
    subgraph "Loading Flags"
        RecursiveFlag["--recursive (-r)"]
        TreeFlag["--tree (directory structure)"]
        MapFlag["--map (function signatures)"]
        ForceFlag["--force (ignore .gitignore)"]
        DetailFlag["--detail (image quality)"]
    end
    
    subgraph "Context Processing"
        ApiClientLoad["api.Client context methods"]
        ContextTypeMapping["shared.ContextType constants"]
        TokenCalculation["Token size calculation"]
        ValidationChecks["File existence validation"]
    end
    
    LoadCommand --> FileInput
    LoadCommand --> DirectoryInput
    LoadCommand --> URLInput
    LoadCommand --> NoteInput
    LoadCommand --> ImageInput
    LoadCommand --> PipedInput
    
    DirectoryInput --> RecursiveFlag
    DirectoryInput --> TreeFlag
    DirectoryInput --> MapFlag
    FileInput --> ForceFlag
    ImageInput --> DetailFlag
    
    RecursiveFlag --> ApiClientLoad
    TreeFlag --> ContextTypeMapping
    MapFlag --> TokenCalculation
    ForceFlag --> ValidationChecks
```

Sources: [app/cli/term/help.go:71-76](), [docs/docs/cli-reference.md:200-229]()

## Configuration Management

Configuration commands control plan behavior through the `shared.PlanConfig` struct and autonomy level settings.

**Configuration Command Architecture**

```mermaid
graph TB
    subgraph "Configuration Commands"
        ConfigShow["config command"]
        ConfigDefault["config default command"]
        SetConfigCmd["set-config command"]
        SetConfigDefault["set-config default command"]
        SetAutoCmd["set-auto command"]
        SetAutoDefault["set-auto default command"]
    end
    
    subgraph "Configuration Data Structures"
        PlanConfig["shared.PlanConfig struct"]
        AutoModeType["shared.AutoModeType enum"]
        ConfigSettingsByKey["shared.ConfigSettingsByKey map"]
        ConfigSetting["shared.ConfigSetting struct"]
    end
    
    subgraph "Autonomy Level Constants"
        AutoModeFull["AutoModeFull - Full automation"]
        AutoModeSemi["AutoModeSemi - Semi-auto context"]
        AutoModePlus["AutoModePlus - Context + smart features"]
        AutoModeBasic["AutoModeBasic - Auto-continue only"]
        AutoModeNone["AutoModeNone - Manual step-by-step"]
        AutoModeCustom["AutoModeCustom - Individual settings"]
    end
    
    subgraph "Configuration Processing"
        UpdateConfigFunc["updateConfig() function"]
        SetAutoModeMethod["PlanConfig.SetAutoMode() method"]
        UpdatePlanConfigAPI["api.Client.UpdatePlanConfig()"]
        LoadMapIfNeeded["loadMapIfNeeded() function"]
    end
    
    SetConfigCmd --> UpdateConfigFunc
    SetAutoCmd --> SetAutoModeMethod
    UpdateConfigFunc --> ConfigSettingsByKey
    SetAutoModeMethod --> AutoModeFull
    SetAutoModeMethod --> AutoModeSemi
    SetAutoModeMethod --> AutoModePlus
    SetAutoModeMethod --> AutoModeBasic
    SetAutoModeMethod --> AutoModeNone
    
    UpdateConfigFunc --> UpdatePlanConfigAPI
    UpdatePlanConfigAPI --> PlanConfig
    UpdateConfigFunc --> LoadMapIfNeeded
```

Sources: [app/cli/cmd/set_config.go:26-367](), [app/shared/plan_config.go:19-477]()

## Model Management Commands

Model management commands control AI model selection and configuration for the different roles in plan execution.

| Command | Purpose | Scope |
|---------|---------|-------|
| `models` | Show current model settings | Current plan |
| `models default` | Show org default settings | Organization-wide |
| `models available` | List available models | All providers |
| `set-model` | Update model configuration | Current plan |
| `set-model default` | Update default models | Organization-wide |
| `model-packs` | Show available model packs | Built-in and custom |

**Model System Architecture**

```mermaid
graph LR
    subgraph "Model Roles"
        PlannerRole["planner role"]
        CoderRole["coder role"]
        ArchitectRole["architect role"]
        BuilderRole["builder role"]
    end
    
    subgraph "Built-in Model Packs"
        DailyDriverPack["daily-driver pack"]
        ReasoningPack["reasoning pack"]
        StrongPack["strong pack"]
        CheapPack["cheap pack"]
        OssPack["oss pack"]
        GeminiPreviewPack["gemini-preview pack"]
    end
    
    subgraph "Provider Integration"
        OpenAIAPI["OpenAI API direct"]
        OpenRouterAPI["OpenRouter API"]
        AnthropicViaOR["Anthropic via OpenRouter"]
        GoogleViaOR["Google via OpenRouter"]
    end
    
    subgraph "Model Configuration"
        ModelSettings["Model temperature, top-p"]
        TokenLimits["max-tokens, max-convo-tokens"]
        CustomModels["User-defined custom models"]
        ModelPackCreation["Custom model pack creation"]
    end
    
    PlannerRole --> DailyDriverPack
    CoderRole --> DailyDriverPack
    ArchitectRole --> StrongPack
    BuilderRole --> ReasoningPack
    
    DailyDriverPack --> OpenAIAPI
    DailyDriverPack --> OpenRouterAPI
    StrongPack --> AnthropicViaOR
    ReasoningPack --> GoogleViaOR
    
    OpenAIAPI --> ModelSettings
    OpenRouterAPI --> TokenLimits
    AnthropicViaOR --> CustomModels
    GoogleViaOR --> ModelPackCreation
```

Sources: [app/cli/term/help.go:106-127](), [docs/docs/cli-reference.md:652-796]()

## Streaming and Background Execution

Plandex supports background task execution through stream management for long-running plan operations.

**Stream Management Architecture**

```mermaid
graph TD
    subgraph "Stream Management Commands"
        PsCommand["ps command"]
        ConnectCommand["connect (conn) command"]
        StopCommand["stop command"]
    end
    
    subgraph "Background Execution Support"
        BgFlag["--bg flag"]
        StreamIdGeneration["Unique stream ID generation"]
        StreamStatusTracking["Status: active/finished/stopped/errored"]
        WaitingForFile["waiting for missing file status"]
    end
    
    subgraph "Streamable Command Types"
        TellBgStream["tell --bg streams"]
        BuildBgStream["build --bg streams"]
        ChatBgStream["chat --bg streams"]
        DebugBgStream["debug --bg streams"]
    end
    
    subgraph "Stream Coordination"
        SessionIdGeneration["sessionId = uuid.New().String()"]
        ExecPlandexCommandParams["lib.ExecPlandexCommandParams"]
        StreamingTUI["Real-time terminal UI updates"]
        StreamReconnection["Stream reconnection capability"]
    end
    
    PsCommand --> StreamStatusTracking
    ConnectCommand --> StreamIdGeneration
    StopCommand --> StreamStatusTracking
    
    BgFlag --> TellBgStream
    BgFlag --> BuildBgStream
    BgFlag --> ChatBgStream
    BgFlag --> DebugBgStream
    
    TellBgStream --> SessionIdGeneration
    BuildBgStream --> ExecPlandexCommandParams
    ChatBgStream --> StreamingTUI
    DebugBgStream --> StreamReconnection
```

Sources: [app/cli/term/help.go:128-131](), [app/cli/cmd/repl.go:72-74]()

## Command Auto-completion and Suggestions

The REPL provides intelligent command completion based on multiple suggestion sources and context analysis.

**Suggestion System Architecture**

```mermaid
graph TB
    subgraph "Suggestion Data Sources"
        CliCommandsArray["term.CliCommands array"]
        ReplCmdAliasesMap["lib.ReplCmdAliases map"]
        ProjectPathsActive["projectPaths.ActivePaths"]
        BuiltinReplCmds["quit, help, multi, send, tell, chat, run"]
    end
    
    subgraph "Suggestion Processing Functions"
        FilterFuzzyFunc["prompt.FilterFuzzy()"]
        FilterHasPrefixFunc["prompt.FilterHasPrefix()"]
        IsValidPositionFunc["isValidPosition() validation"]
        FindSimilarCommandsFunc["findSimilarCommands()"]
    end
    
    subgraph "Context-Aware Filtering"
        ReplModeFiltering["Filter by config.Repl flag"]
        CommandSpecificSuggestions["Command-specific suggestions"]
        FileExtensionFiltering[".md/.txt filtering for \\\\run"]
        DirectoryFlagSuggestions["-r, --map, --tree for directories"]
    end
    
    subgraph "Suggestion Ranking Logic"
        PrefixMatchesFirst["Prefix matches prioritized"]
        BuiltinCommandPriority["Built-in commands at top"]
        AliasMatchPriority["Exact alias matches first"]
        AlphabeticalSorting["Alphabetical for remaining"]
    end
    
    CliCommandsArray --> FilterFuzzyFunc
    ReplCmdAliasesMap --> FindSimilarCommandsFunc
    ProjectPathsActive --> FileExtensionFiltering
    BuiltinReplCmds --> PrefixMatchesFirst
    
    FilterFuzzyFunc --> ReplModeFiltering
    FilterHasPrefixFunc --> CommandSpecificSuggestions
    IsValidPositionFunc --> DirectoryFlagSuggestions
    
    ReplModeFiltering --> PrefixMatchesFirst
    CommandSpecificSuggestions --> BuiltinCommandPriority
    DirectoryFlagSuggestions --> AliasMatchPriority
    FileExtensionFiltering --> AlphabeticalSorting
```

Sources: [app/cli/cmd/repl.go:521-762](), [app/cli/cmd/repl.go:222-292]()

## Command Help System

The CLI provides comprehensive help through multiple interfaces using structured command definitions.

**Help System Architecture**

```mermaid
graph LR
    subgraph "Help Command Types"
        HelpBasic["plandex help"]
        HelpAllCommands["plandex help --all"]
        CommandSpecificHelp["plandex [cmd] --help"]
        ReplHelpCommand["\\\\help in REPL"]
    end
    
    subgraph "Help Data Sources"
        CliCommandsConfig["term.CliCommands configuration"]
        CmdConfigStruct["term.CmdConfig struct"]
        AutoModeDescriptions["shared.AutoModeDescriptions"]
        CommandAliasMapping["Command alias mappings"]
    end
    
    subgraph "Help Formatting Functions"
        PrintCustomHelpFunc["term.PrintCustomHelp()"]
        PrintHelpAllCommandsFunc["term.PrintHelpAllCommands()"]
        ColorNewStyling["color.New() ANSI styling"]
        CategoryGrouping["Commands grouped by category"]
    end
    
    subgraph "Interactive Help Elements"
        PrintCmdsFunc["term.PrintCmds() suggestions"]
        ContextualHelpDisplay["Context-aware help display"]
        ErrorTriggeredHelp["Help on command errors"]
        ReplWelcomeHelp["replWelcome() help display"]
    end
    
    HelpBasic --> PrintCustomHelpFunc
    HelpAllCommands --> PrintHelpAllCommandsFunc
    ReplHelpCommand --> CliCommandsConfig
    
    CliCommandsConfig --> CmdConfigStruct
    CmdConfigStruct --> CommandAliasMapping
    AutoModeDescriptions --> ColorNewStyling
    
    PrintCustomHelpFunc --> CategoryGrouping
    PrintHelpAllCommandsFunc --> PrintCmdsFunc
    ColorNewStyling --> ContextualHelpDisplay
    CategoryGrouping --> ErrorTriggeredHelp
    ContextualHelpDisplay --> ReplWelcomeHelp
```

Sources: [app/cli/term/help.go:218-344](), [app/cli/cmd/root.go:77-91]()

---

