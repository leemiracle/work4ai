<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/ib-traffic-monitor · page 3 Architecture · fetched 2026-10-26 -->

# Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [ib-traffic-monitor.c](ib-traffic-monitor.c)
- [infiniband.c](infiniband.c)

</details>



This document describes the high-level architecture of `ib-traffic-monitor`, including its component organization, layering strategy, design patterns, and execution model. For detailed information about individual modules and their implementations, see [Core Components](#4). For specifics on how data flows through the system from hardware to display, see [Data Flow](#3.2).

## Overview

`ib-traffic-monitor` follows a **layered architecture** pattern with clear separation between application orchestration, domain logic, presentation, and utilities. The application is a single-threaded, polling-based monitoring tool that reads InfiniBand metrics from the Linux sysfs filesystem and displays them in a terminal UI using ncurses.

The system consists of four source modules compiled into a single executable:

| Module | Purpose | Primary Files |
|--------|---------|---------------|
| Application Layer | Event loop, initialization, signal handling | `ib-traffic-monitor.c` |
| Domain Layer | InfiniBand device discovery and metrics collection | `infiniband.c`, `infiniband.h` |
| Presentation Layer | Terminal UI layout and rendering | `ncurses_utils.c`, `ncurses_utils.h` |
| Utility Layer | OS detection and file I/O helpers | `utils.c`, `utils.h` |

**Sources:** [README.md:1-111](), [ib-traffic-monitor.c:1-345]()

## Layered Architecture

```mermaid
graph TB
    subgraph CLI["Command-Line Interface"]
        ARGS["main() argument parsing<br/>[ib-traffic-monitor.c:52-112]"]
    end
    
    subgraph APP["Application Layer"]
        MAIN["main() event loop<br/>[ib-traffic-monitor.c:203-330]"]
        SIGNAL["sigint_handler()<br/>[ib-traffic-monitor.c:46-50]"]
        INIT["Initialization logic<br/>[ib-traffic-monitor.c:137-201]"]
    end
    
    subgraph DOMAIN["Domain Layer"]
        GETMETRICS["get_infiniband_metrics()<br/>[infiniband.c:28-355]"]
        STRUCTS["struct infiniband_metrics<br/>struct interface<br/>[infiniband.h]"]
    end
    
    subgraph PRESENT["Presentation Layer"]
        LAYOUT["construct_window_layout()<br/>[ncurses_utils.c]"]
        DELIM["print_delimiter()<br/>[ncurses_utils.c]"]
        NCWIN["WINDOW main_window<br/>[ib-traffic-monitor.c:178]"]
    end
    
    subgraph UTIL["Utility Layer"]
        OSCHECK["is_linux()<br/>[utils.c]"]
        FILEIO["read_file_char()<br/>read_file_long_int()<br/>[utils.c]"]
    end
    
    subgraph EXTERNAL["External Systems"]
        SYSFS["/sys/class/infiniband/*<br/>Linux sysfs"]
        NCURSES["libncurses"]
    end
    
    ARGS --> MAIN
    MAIN --> SIGNAL
    MAIN --> GETMETRICS
    MAIN --> LAYOUT
    MAIN --> DELIM
    MAIN --> NCWIN
    MAIN --> OSCHECK
    
    GETMETRICS --> STRUCTS
    GETMETRICS --> FILEIO
    GETMETRICS --> SYSFS
    
    LAYOUT --> NCURSES
    DELIM --> NCURSES
    NCWIN --> NCURSES
    
    FILEIO --> SYSFS
```

**Layering Principles:**

- **Application Layer** (`ib-traffic-monitor.c`) orchestrates the entire program lifecycle, including initialization, event loop management, signal handling, and cleanup. It depends on all other internal layers.
- **Domain Layer** (`infiniband.c`, `infiniband.h`) encapsulates InfiniBand-specific knowledge, including device discovery, port enumeration, and metric reading. It depends only on the utility layer.
- **Presentation Layer** (`ncurses_utils.c`, `ncurses_utils.h`) handles terminal UI concerns, including window layout construction and delimiter printing. It depends only on ncurses.
- **Utility Layer** (`utils.c`, `utils.h`) provides reusable, domain-agnostic helpers. It has no internal dependencies.

**Sources:** [ib-traffic-monitor.c:1-345](), [infiniband.c:1-355](), [infiniband.h]()

## Component Organization

```mermaid
graph LR
    subgraph MODULES["Source Modules"]
        MAIN_C["ib-traffic-monitor.c<br/>main()<br/>sigint_handler()<br/>usage()"]
        IB_C["infiniband.c<br/>get_infiniband_metrics()"]
        NC_C["ncurses_utils.c<br/>construct_window_layout()<br/>print_delimiter()"]
        UTIL_C["utils.c<br/>is_linux()<br/>read_file_char()<br/>read_file_long_int()"]
    end
    
    subgraph HEADERS["Header Interfaces"]
        IB_H["infiniband.h<br/>struct infiniband_metrics<br/>struct interface<br/>INTERFACE_COUNT"]
        NC_H["ncurses_utils.h<br/>Function declarations"]
        UTIL_H["utils.h<br/>Function declarations"]
    end
    
    subgraph BUILD["Build Artifacts"]
        OBJ_MAIN["ib-traffic-monitor.o"]
        OBJ_IB["infiniband.o"]
        OBJ_NC["ncurses_utils.o"]
        OBJ_UTIL["utils.o"]
        EXE["ib-traffic-monitor<br/>executable"]
    end
    
    MAIN_C -.includes.-> IB_H
    MAIN_C -.includes.-> NC_H
    MAIN_C -.includes.-> UTIL_H
    IB_C -.includes.-> IB_H
    IB_C -.includes.-> UTIL_H
    NC_C -.includes.-> NC_H
    UTIL_C -.includes.-> UTIL_H
    
    MAIN_C --> OBJ_MAIN
    IB_C --> OBJ_IB
    NC_C --> OBJ_NC
    UTIL_C --> OBJ_UTIL
    
    OBJ_MAIN --> EXE
    OBJ_IB --> EXE
    OBJ_NC --> EXE
    OBJ_UTIL --> EXE
```

**Dependency Rules:**

- No circular dependencies exist between modules
- The main application (`ib-traffic-monitor.c`) is the only module that includes all three subsystem headers
- Domain logic (`infiniband.c`) depends only on utilities, ensuring reusability
- Presentation logic (`ncurses_utils.c`) is self-contained except for ncurses library

**Sources:** [Makefile](), [README.md:43-52]()

## Key Design Patterns

### Polling Architecture

The application uses a **polling model** with configurable refresh intervals. The main event loop at [ib-traffic-monitor.c:203-330]() repeatedly:

1. Collects current metrics via `get_infiniband_metrics()`
2. Calculates rates by comparing with previous iteration's data
3. Renders metrics to the ncurses window
4. Blocks for the refresh interval using `pselect()`

```mermaid
stateDiagram-v2
    [*] --> Initialize
    Initialize --> CollectMetrics: "get_infiniband_metrics()"
    CollectMetrics --> CalcRates: "prev_data_flag > 0"
    CollectMetrics --> DisplayStatic: "first iteration"
    DisplayStatic --> WaitRefresh
    CalcRates --> DisplayAll: "compare current & previous"
    DisplayAll --> WaitRefresh: "wrefresh(main_window)"
    WaitRefresh --> CheckInput: "pselect() timeout"
    CheckInput --> CollectMetrics: "no input"
    CheckInput --> Cleanup: "Q pressed or SIGINT"
    Cleanup --> [*]
```

The refresh interval defaults to 5 seconds but can be configured via the `-r` command-line flag [ib-traffic-monitor.c:81-95]().

**Sources:** [ib-traffic-monitor.c:203-330](), [ib-traffic-monitor.c:62]()

### Data Structure Lifecycle

The application maintains two instances of `struct infiniband_metrics`:

- `cur_infiniband_metrics`: Current iteration's metrics [ib-traffic-monitor.c:121]()
- `prev_infiniband_metrics`: Previous iteration's metrics [ib-traffic-monitor.c:122]()

At the end of each loop iteration, current metrics are copied to previous [ib-traffic-monitor.c:325-326](), enabling delta calculations for rate-based metrics (packets/second, MB/second). A flag `prev_data_flag` tracks whether previous data exists [ib-traffic-monitor.c:131]().

**Sources:** [ib-traffic-monitor.c:121-122](), [ib-traffic-monitor.c:325-329]()

### Interface Matching Strategy

Since InfiniBand interfaces can be added or removed between iterations, the application matches interfaces by name. For rate calculations, it performs a nested loop [ib-traffic-monitor.c:274-293]():

```c
for (int i = 0; i < ret_get_infiniband_metrics; ++i) {
    for (int j = 0; j < prev_ret_get_infiniband_metrics; ++j) {
        if (strcmp(cur_infiniband_metrics.infiniband[i].interface_name,
                   prev_infiniband_metrics.infiniband[j].interface_name) == 0) {
            // Calculate and display rates
        }
    }
}
```

This ensures rate metrics are only displayed for interfaces present in both iterations.

**Sources:** [ib-traffic-monitor.c:272-295]()

## Execution Model

```mermaid
graph TD
    START["Program Start"] --> PARSEARGS["Parse CLI Arguments<br/>[ib-traffic-monitor.c:73-112]"]
    PARSEARGS --> OSCHECK["is_linux() validation<br/>[ib-traffic-monitor.c:115-118]"]
    OSCHECK --> SIGSETUP["Signal Setup<br/>block SIGINT, install handler<br/>[ib-traffic-monitor.c:137-175]"]
    SIGSETUP --> NCINIT["ncurses Initialization<br/>initscr(), cbreak(), curs_set(0)<br/>[ib-traffic-monitor.c:182-188]"]
    NCINIT --> WINCREAT["Create main_window<br/>newwin(), nodelay()<br/>[ib-traffic-monitor.c:191-200]"]
    
    WINCREAT --> LOOP["Main Event Loop<br/>[ib-traffic-monitor.c:203-330]"]
    
    LOOP --> DISCOVER["get_infiniband_metrics()<br/>[ib-traffic-monitor.c:221]"]
    DISCOVER --> VALIDATE{"Devices found?"}
    VALIDATE -->|"No"| ERROR["Set error_flag<br/>break loop"]
    VALIDATE -->|"Yes"| CONSTRUCT["construct_window_layout()<br/>[ib-traffic-monitor.c:235]"]
    CONSTRUCT --> DISPLAY["Display metrics<br/>[ib-traffic-monitor.c:240-295]"]
    DISPLAY --> REFRESH["wrefresh(main_window)<br/>[ib-traffic-monitor.c:297]"]
    REFRESH --> WAIT["pselect() with timeout<br/>[ib-traffic-monitor.c:307]"]
    WAIT --> INPUT{"Input/Signal?"}
    INPUT -->|"Q or SIGINT"| CLEANUP
    INPUT -->|"Timeout"| COPY["Copy current to previous<br/>[ib-traffic-monitor.c:325-329]"]
    COPY --> LOOP
    
    ERROR --> CLEANUP["Cleanup<br/>delwin(), endwin()<br/>[ib-traffic-monitor.c:333-335]"]
    CLEANUP --> EXIT["Exit with status<br/>[ib-traffic-monitor.c:343]"]
```

### Signal Handling

The application handles SIGINT (Ctrl+C) gracefully using a combination of signal masking and `pselect()`:

1. SIGINT is blocked during normal operation [ib-traffic-monitor.c:158-161]()
2. A signal handler sets `break_flag` when SIGINT arrives [ib-traffic-monitor.c:46-50]()
3. `pselect()` atomically unblocks SIGINT during sleep [ib-traffic-monitor.c:307]()
4. After `pselect()` returns with EINTR, the main loop checks `break_flag` and exits [ib-traffic-monitor.c:318-322]()

This ensures clean ncurses cleanup occurs even when interrupted.

**Sources:** [ib-traffic-monitor.c:137-175](), [ib-traffic-monitor.c:307](), [ib-traffic-monitor.c:318-322]()

### Non-Blocking Input

User input ('Q' to quit) is handled non-blockingly:

1. `nodelay(main_window, TRUE)` enables non-blocking reads [ib-traffic-monitor.c:200]()
2. `pselect()` monitors stdin with a timeout [ib-traffic-monitor.c:307]()
3. If input is available, a single character is read and checked [ib-traffic-monitor.c:310-314]()

This allows the application to respond immediately to user input without polling.

**Sources:** [ib-traffic-monitor.c:200](), [ib-traffic-monitor.c:299-315]()

## External Dependencies

### Linux sysfs

The application reads metrics from `/sys/class/infiniband/` and its subdirectories:

| Path Pattern | Content |
|--------------|---------|
| `/sys/class/infiniband/` | Device discovery |
| `/sys/class/infiniband/{device}/ports/` | Port enumeration |
| `/sys/class/infiniband/{device}/ports/{port}/` | Port status (state, phys_state, rate, lid, link_layer) |
| `/sys/class/infiniband/{device}/ports/{port}/counters/` | Counter metrics |

The application validates sysfs accessibility using `opendir()` [infiniband.c:45-49]() and gracefully handles missing files.

**Sources:** [infiniband.c:28-355](), [README.md:108]()

### ncurses Library

The application links against `libncurses` [README.md:51]() and uses these primary functions:

| Function | Purpose | Usage |
|----------|---------|-------|
| `initscr()` | Initialize ncurses | [ib-traffic-monitor.c:182]() |
| `newwin()` | Create window | [ib-traffic-monitor.c:191]() |
| `mvwprintw()` | Print formatted text at position | [ib-traffic-monitor.c:243-268]() |
| `wrefresh()` | Update display | [ib-traffic-monitor.c:297]() |
| `endwin()` | Cleanup ncurses | [ib-traffic-monitor.c:335]() |

The application uses `cbreak()` to disable line buffering [ib-traffic-monitor.c:185]() and `curs_set(0)` to hide the cursor [ib-traffic-monitor.c:188]().

**Sources:** [ib-traffic-monitor.c:182-200](), [ib-traffic-monitor.c:333-335](), [README.md:5]()

## Compilation and Linking

The build process compiles four source files into object files with strict compiler flags, then links them with ncurses:

```
gcc [flags] -c -o ib-traffic-monitor.o ib-traffic-monitor.c
gcc [flags] -c -o infiniband.o infiniband.c
gcc [flags] -c -o utils.o utils.c
gcc [flags] -c -o ncurses_utils.o ncurses_utils.c
gcc [flags] -o ib-traffic-monitor *.o -lncurses
```

Compiler flags include `-Wall -Wextra -Wpedantic -fsanitize=undefined` for robust error detection during development.

**Sources:** [README.md:43-52]()

---

