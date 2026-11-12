# go-harnessless

A Go rewrite of [browser-use/harnessless](https://github.com/browser-use/harnessless) — a daemon-based Chrome DevTools Protocol bridge designed for LLM-driven browser automation.

Same three-process model as the Python original, rewritten with Go-native concurrency primitives.

```
Chrome (CDP WebSocket)
    ↕
harnessless-daemon   (long-running, holds Chrome connection)
    ↕ Unix socket /tmp/harnessless.sock
harnessless-client   (ephemeral, sends one command at a time)
```

---

## Why Go instead of Python

| Concern | Python | Go |
|---|---|---|
| Concurrency | `asyncio` event loop (single-threaded) | Goroutines — true OS-thread parallelism |
| Tab isolation | Global session lock | `sync.RWMutex` per tab: reads on different tabs are fully parallel |
| Chrome back-pressure | Unlimited concurrent CDP calls possible | Worker pool (`WorkerCount=4`) caps concurrency |
| Response routing | `asyncio.Future` per request | Buffered `chan *CDPResponse` per request — zero-allocation fast path |
| Memory model | GIL-protected | Race-detector clean; `go test -race` supported |
| Binary distribution | Requires Python + uv | Single static binary, zero runtime dependencies |
| Startup latency | ~300 ms (Python import) | ~5 ms (Go startup) |

### Concurrency architecture

```
 Chrome WS
    │
    ▼
readPump goroutine          ← sole reader, no lock needed on ws.ReadMessage
    │
    ├─▶ pending map [id]→chan   ← non-blocking channel delivery per request
    └─▶ event ring buffer       ← sync.RWMutex-guarded, max 500 events

client goroutine (1 per Unix connection)
    │
    ▼
workerCh  (buffered channel)
    │
    ├─▶ worker-0  ─┐
    ├─▶ worker-1  ─┤  each acquires Tab.RLock (read) or Tab.Lock (write)
    ├─▶ worker-2  ─┤  before calling sendCDP → response channel → reply
    └─▶ worker-3  ─┘

TabManager
    ├─ manager-level  sync.RWMutex  (guards the map of tabs)
    └─ per-Tab        sync.RWMutex  (guards tab fields + Chrome round-trip)
         ├─ RLock for: captureScreenshot, evaluate, getTargets, getTargetInfo
         └─  Lock for: navigate, click, type, scroll, attachToTarget, …
```

---

## Prerequisites

1. **Chrome 144+** running (any profile, any window).
2. Remote debugging enabled:
   - Open `chrome://inspect/#remote-debugging`
   - Tick **"Discover network targets"** (the checkbox that enables `DevToolsActivePort`)
3. **Go 1.21+** to build.

---

## Quick start

```bash
# Build both binaries
go build -o harnessless-daemon ./cmd/daemon
go build -o harnessless-client ./cmd/client

# Start the daemon (keeps your Chrome session + cookies)
./harnessless-daemon &

# Use the client
./harnessless-client goto https://github.com
./harnessless-client info
./harnessless-client shot /tmp/github.png
./harnessless-client js "document.title"
./harnessless-client click 760 400
./harnessless-client type "hello world"
./harnessless-client key Enter
./harnessless-client tabs
./harnessless-client shutdown
```

---

## Client commands

```
NAVIGATION
  goto   <url>                Navigate to url and wait for load
  info                        Print URL / title / viewport / scroll as JSON

MOUSE
  click  <x> <y>              Left-click at (x, y)
  dclick <x> <y>              Double-click
  rclick <x> <y>              Right-click
  scroll <x> <y> [dy] [dx]   Scroll wheel; dy<0 = scroll up (default −300)

KEYBOARD
  type   <text>               Insert text into the focused element
  key    <key> [modifiers]    Named key press (1=Alt 2=Ctrl 4=Meta 8=Shift)
                              e.g.  key Enter   key a 2  (Ctrl+A)

VISUAL
  shot   [path] [full]        PNG screenshot → path (default /tmp/shot.png)
                              full=true captures beyond the viewport

JAVASCRIPT
  js     <expr>               Evaluate JS, print result as JSON

TABS
  tabs                        List open page targets as JSON
  tab    <targetId>           Switch to a tab by target ID
  newtab [url]                Open a new tab

EVENTS
  events                      Drain and print buffered CDP events as JSON

RAW CDP
  cdp    <Method> [json]      Pass-through: e.g.  cdp Page.reload '{}'

DAEMON
  alive                       Exit 0 if daemon alive, 1 otherwise
  shutdown                    Graceful daemon exit
```

---

## Use as a Go library

```go
import harnessless "github.com/browser-use/go-harnessless"

func main() {
    c := harnessless.NewClient()

    // Start daemon if not already running
    if err := c.EnsureDaemon(0); err != nil {
        log.Fatal(err)
    }

    h := harnessless.NewHelpers(c)

    h.Goto("https://example.com")

    info, _ := h.PageInfo()
    fmt.Printf("%s — %dx%d\n", info.Title, int(info.W), int(info.H))

    h.Screenshot("/tmp/shot.png", false)

    h.Click(400, 300, "left", 1)
    h.TypeText("hello")
    h.PressKey("Enter", 0)

    // Raw CDP
    result, _ := c.CDP("Page.reload", "", map[string]interface{}{"ignoreCache": true})
    _ = result

    // Concurrent operations on different tabs proceed in parallel
    tabs, _ := h.ListTabs(false)
    var wg sync.WaitGroup
    for _, tab := range tabs {
        wg.Add(1)
        go func(targetID string) {
            defer wg.Done()
            // Each goroutine holds its own tab's RLock — no contention
            h.JS("document.title", targetID)
        }(tab.TargetID)
    }
    wg.Wait()
}
```

---

## File structure

```
go-harnessless/
├── types.go          CDP wire types, Unix-socket protocol, PageInfo, constants
├── tab_manager.go    Tab (per-tab sync.RWMutex) + TabManager (registry)
├── daemon.go         WebSocket read pump, worker pool, Unix socket server
├── client.go         Unix socket client: Send / CDP / session / lifecycle
├── helpers.go        High-level browser helpers: Goto, Click, Screenshot, …
├── cmd/
│   ├── daemon/main.go    harnessless-daemon binary entry point
│   └── client/main.go    harnessless-client CLI entry point
├── go.mod
└── go.sum
```

---

## Environment variables

| Variable | Default | Purpose |
|---|---|---|
| `HARNESSLESS_DAEMON` | `harnessless-daemon` on PATH | Path to the daemon binary used by `EnsureDaemon` |
| `CHROME_PROFILE_DIR` | OS default | Override Chrome profile directory for DevToolsActivePort lookup |

---

## Differences from the Python version

- **No `uv` or Python required** — a single static binary for the daemon and client.
- **Per-tab RWMutex** — concurrent screenshot + page_info on the same tab; parallel read operations across different tabs.
- **Worker pool** — `WorkerCount` (default 4) goroutines cap Chrome concurrency; configurable at compile time.
- **Channel-delivered responses** — each in-flight CDP request has its own buffered channel; readPump delivers responses without a global lock.
- **30-second CDP timeout** per request (Python version hangs forever).
- **Typed response structs** — `PageInfo`, `Target`, `Event` are proper Go types, not raw dicts.
- **CLI client** — `harnessless-client` provides shell-scriptable access to every helper function.

The Unix-socket protocol (`{method, params, session_id}` / `{result}` / `{error}`) is intentionally wire-compatible with the Python daemon so mixed-language setups are possible.
