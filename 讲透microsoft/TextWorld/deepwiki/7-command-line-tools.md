<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/TextWorld · page 7 Command Line Tools · fetched 2026-10-26 -->

# Command Line Tools

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/pep8.yml](.github/workflows/pep8.yml)
- [scripts/tw-extract](scripts/tw-extract)
- [scripts/tw-make](scripts/tw-make)
- [scripts/tw-play](scripts/tw-play)
- [tests/test_make_game.py](tests/test_make_game.py)
- [tests/test_tw-extract.py](tests/test_tw-extract.py)
- [tests/test_tw-play.py](tests/test_tw-play.py)
- [textworld/agents/human.py](textworld/agents/human.py)
- [textworld/envs/wrappers/__init__.py](textworld/envs/wrappers/__init__.py)
- [textworld/envs/wrappers/recorder.py](textworld/envs/wrappers/recorder.py)
- [textworld/envs/wrappers/tests/test_viewer.py](textworld/envs/wrappers/tests/test_viewer.py)
- [textworld/generator/__init__.py](textworld/generator/__init__.py)
- [textworld/generator/chaining.py](textworld/generator/chaining.py)
- [textworld/generator/tests/test_chaining.py](textworld/generator/tests/test_chaining.py)
- [textworld/generator/tests/test_logger.py](textworld/generator/tests/test_logger.py)
- [textworld/generator/tests/test_making_a_game.py](textworld/generator/tests/test_making_a_game.py)
- [textworld/text_utils.py](textworld/text_utils.py)
- [tox.ini](tox.ini)

</details>



TextWorld provides several command-line utilities that serve as the primary interface for generating, playing, and analyzing text-based games. These tools abstract the underlying TextWorld API into convenient command-line interfaces suitable for scripting, experimentation, and automated workflows.

For information about the underlying game generation system, see [Game Generation](#4). For details about environment execution and agent interfaces, see [Game Environments](#5) and [Agent Interface](#6).

## Architecture Overview

The command-line tools form a bridge between user workflows and TextWorld's core systems. Each tool focuses on a specific aspect of the TextWorld ecosystem: game creation, game execution, and data extraction.

```mermaid
graph TB
    subgraph "Command Line Interface Layer"
        twmake["tw-make<br/>Game Generation CLI"]
        twplay["tw-play<br/>Game Execution CLI"]  
        twextract["tw-extract<br/>Data Extraction CLI"]
    end
    
    subgraph "Core TextWorld Systems"
        gamemaker["GameMaker<br/>World Construction"]
        challenges["Challenges<br/>Built-in Scenarios"]
        compiler["Inform7 Compiler<br/>Game Compilation"]
        environments["Environment System<br/>Game Execution"]
        agents["Agent System<br/>Player Implementations"]
        textutils["Text Utilities<br/>Data Processing"]
    end
    
    subgraph "Output Artifacts"
        z8files[".z8/.ulx Files<br/>Compiled Games"]
        jsonfiles[".json Files<br/>Game Metadata"]
        datafiles[".txt Files<br/>Extracted Data"]
    end
    
    twmake --> gamemaker
    twmake --> challenges
    twmake --> compiler
    twplay --> environments
    twplay --> agents
    twextract --> textutils
    
    gamemaker --> z8files
    compiler --> z8files
    gamemaker --> jsonfiles
    textutils --> datafiles
    
    z8files --> twplay
    jsonfiles --> twextract
```

Sources: [scripts/tw-make:1-246](), [scripts/tw-play:1-84](), [scripts/tw-extract:1-172]()

## Command Line Tool Integration Flow

The following diagram shows how command-line arguments flow through the TextWorld system to produce outputs:

```mermaid
graph LR
    subgraph "User Input"
        args["Command Line Arguments"]
        configs["Configuration Files"]
        thirdparty["Third-party Modules"]
    end
    
    subgraph "Argument Processing"
        argparse["argparse.ArgumentParser<br/>Argument Validation"]
        options["GameOptions<br/>Configuration Object"]
        chainingopts["ChainingOptions<br/>Quest Parameters"]
    end
    
    subgraph "Core Execution"
        textworld_make["textworld.make()<br/>Game Generation"]
        textworld_start["textworld.start()<br/>Environment Creation"]
        game_load["Game.load()<br/>Metadata Loading"]
    end
    
    subgraph "Output Generation"
        compilation["compile_game()<br/>Inform7 Compilation"]
        agents_act["Agent.act()<br/>Game Interaction"]
        data_extract["extract_vocab_from_gamefiles()<br/>Data Processing"]
    end
    
    args --> argparse
    configs --> argparse
    thirdparty --> argparse
    
    argparse --> options
    argparse --> chainingopts
    
    options --> textworld_make
    options --> textworld_start
    options --> game_load
    
    textworld_make --> compilation
    textworld_start --> agents_act
    game_load --> data_extract
```

Sources: [scripts/tw-make:148-246](), [scripts/tw-play:37-83](), [scripts/tw-extract:68-169]()

## tw-make: Game Generation Tool

The `tw-make` command generates TextWorld games with customizable parameters. It supports both custom game creation and built-in challenge scenarios.

### Command Structure

```mermaid
graph TB
    subgraph "tw-make Command Structure"
        main["tw-make"]
        custom["custom<br/>Custom Game Generation"]
        challenges["Challenge Subcommands<br/>coin_collector, treasure_hunter, etc."]
        thirdparty["--third-party<br/>External Module Loading"]
    end
    
    subgraph "Custom Game Options"
        worldsize["--world-size<br/>Number of Rooms"]
        nbobjects["--nb-objects<br/>Object Count"]
        questlen["--quest-length<br/>Action Sequence Length"]
        theme["--theme<br/>Grammar Theme"]
        output["--output<br/>File Path"]
        format["--format<br/>z8 or ulx"]
    end
    
    subgraph "Processing Pipeline"
        parser["build_parser()<br/>Argument Setup"]
        options_create["GameOptions()<br/>Configuration"]
        make_call["textworld.make()<br/>Generation"]
        compile_call["compile_game()<br/>Output"]
    end
    
    main --> custom
    main --> challenges
    main --> thirdparty
    
    custom --> worldsize
    custom --> nbobjects
    custom --> questlen
    custom --> theme
    custom --> output
    custom --> format
    
    worldsize --> parser
    nbobjects --> parser
    questlen --> parser
    theme --> parser
    output --> parser
    format --> parser
    
    parser --> options_create
    options_create --> make_call
    make_call --> compile_call
```

Sources: [scripts/tw-make:46-146](), [scripts/tw-make:163-217]()

### Key Implementation Details

The tool implements sophisticated argument parsing through the `build_parser()` function at [scripts/tw-make:46-146](). It creates separate subparsers for custom games and each registered challenge:

- **Custom games**: Configured through `GameOptions` and `ChainingOptions` objects
- **Challenge games**: Use challenge-specific make functions from `textworld.challenges.CHALLENGES`
- **Third-party support**: Dynamic module loading via `_maybe_load_third_party_module()` at [scripts/tw-make:31-44]()

The generation process handles error cases like `QuestGenerationError` and `MissingTextGrammar` with informative error messages at [scripts/tw-make:200-210]().

## tw-play: Game Execution Tool

The `tw-play` command provides an interface for playing TextWorld games using different agent implementations.

### Agent Mode Architecture

```mermaid
graph TB
    subgraph "tw-play Agent Modes"
        human["human<br/>HumanAgent Interactive"]
        random["random<br/>NaiveAgent Exploration"]
        randomcmd["random-cmd<br/>RandomCommandAgent"]
        walkthrough["walkthrough<br/>WalkthroughAgent Oracle"]
    end
    
    subgraph "Environment Setup"
        start["textworld.start()<br/>Environment Creation"]
        seed["env.seed()<br/>Randomization"]
        viewer["HtmlViewer<br/>Web Interface"]
        reset["env.reset()<br/>Game Initialization"]
    end
    
    subgraph "Game Loop"
        act["agent.act()<br/>Action Selection"]
        step["env.step()<br/>Action Execution"]
        render["env.render()<br/>Output Display"]
        done["Game Completion Check"]
    end
    
    human --> start
    random --> start
    randomcmd --> start
    walkthrough --> start
    
    start --> seed
    seed --> viewer
    viewer --> reset
    
    reset --> act
    act --> step
    step --> render
    render --> done
    done --> act
```

Sources: [scripts/tw-play:42-79](), [scripts/tw-play:14-34]()

### Agent Implementation Details

Each agent mode corresponds to a specific class from `textworld.agents`:

- `HumanAgent`: Interactive play with optional oracle hints at [scripts/tw-play:50]()
- `NaiveAgent`: Random action selection at [scripts/tw-play:46]()
- `RandomCommandAgent`: Random command generation at [scripts/tw-play:48]()  
- `WalkthroughAgent`: Optimal action sequence execution at [scripts/tw-play:52]()

The tool supports optional web visualization through `HtmlViewer` wrapper at [scripts/tw-play:56-57]().

## tw-extract: Data Extraction Tool

The `tw-extract` command extracts various types of information from TextWorld games for analysis and dataset creation.

### Extraction Pipeline

```mermaid
graph TB
    subgraph "Extraction Subcommands"
        vocab["vocab<br/>Word Extraction"]
        entities["entities<br/>Object Names"]
        walkthroughs["walkthroughs<br/>Solution Paths"]
        commands["commands<br/>Valid Actions"]
    end
    
    subgraph "Data Sources"
        gamefiles["Game Files<br/>.z8/.ulx inputs"]
        jsonfiles["JSON Metadata<br/>Game.load()"]
        grammar["Grammar Themes<br/>Text Generation"]
        jericho["Jericho Dictionary<br/>Z-machine vocab"]
    end
    
    subgraph "Processing Functions"
        extract_vocab["extract_vocab_from_gamefiles()<br/>Word Processing"]
        game_load["Game.load()<br/>Metadata Parsing"]
        grammar_vocab["Grammar.get_vocabulary()<br/>Theme Words"]
        regex_proc["Regex Processing<br/>Template Expansion"]
    end
    
    subgraph "Output Processing"
        merge["--merge<br/>Combine with Existing"]
        force["--force<br/>Overwrite Files"]
        output_files[".txt Output Files<br/>Structured Data"]
    end
    
    vocab --> gamefiles
    entities --> jsonfiles
    walkthroughs --> jsonfiles
    commands --> jsonfiles
    
    gamefiles --> extract_vocab
    jsonfiles --> game_load
    grammar --> grammar_vocab
    
    extract_vocab --> merge
    game_load --> merge
    grammar_vocab --> merge
    regex_proc --> merge
    
    merge --> force
    force --> output_files
```

Sources: [scripts/tw-extract:68-169](), [scripts/tw-extract:18-65]()

### Extraction Implementation

Each subcommand implements specific extraction logic:

- **Vocabulary**: Uses `extract_vocab_from_gamefiles()` from `textworld.text_utils` at [scripts/tw-extract:92]()
- **Entities**: Extracts `game.objects_names` from loaded JSON metadata at [scripts/tw-extract:86]()
- **Walkthroughs**: Retrieves solution sequences from `game.metadata["walkthrough"]` at [scripts/tw-extract:111]()
- **Commands**: Expands command templates using object type hierarchies at [scripts/tw-extract:131-141]()

The tool supports merging new extractions with existing files and provides verbose output for analysis workflows.

## Usage Patterns and Workflows

### Typical Game Development Workflow

```mermaid
graph LR
    subgraph "Development Cycle"
        generate["tw-make custom<br/>--world-size 5<br/>--quest-length 3"]
        test["tw-play game.z8<br/>--mode walkthrough"]
        analyze["tw-extract vocab<br/>game.z8"]
        iterate["Refine Parameters<br/>Repeat Cycle"]
    end
    
    subgraph "Batch Processing"
        script["Shell Scripts<br/>Automated Generation"]
        parallel["Parallel Execution<br/>Multiple Games"]
        dataset["Dataset Creation<br/>Research Workflows"]
    end
    
    generate --> test
    test --> analyze
    analyze --> iterate
    iterate --> generate
    
    generate --> script
    test --> parallel
    analyze --> dataset
```

### Integration with TextWorld API

The command-line tools serve as high-level interfaces to the core TextWorld API, providing convenient access to functionality that can also be accessed programmatically. Each tool corresponds to specific API entry points:

| Tool | Primary API | Configuration | Output |
|------|-------------|---------------|---------|
| `tw-make` | `textworld.make()` | `GameOptions` | `.z8/.ulx + .json` |
| `tw-play` | `textworld.start()` | Agent classes | Interactive session |
| `tw-extract` | `Game.load()` | Extraction type | `.txt` data files |

Sources: [scripts/tw-make:199](), [scripts/tw-play:42](), [scripts/tw-extract:85](), [textworld/text_utils.py:57-62]()

---

