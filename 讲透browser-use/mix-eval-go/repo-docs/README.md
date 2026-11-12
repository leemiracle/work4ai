# Mix Eval Go

Go-based evaluation orchestrator for running Mix Eval tasks using browser automation agents.

Mix-Eval-Go orchestrates agent evaluations by:
1. Fetching tasks from Convex evaluation platform
2. Creating browser sessions with cloud providers (optional)
3. Executing tasks via Mix Agent with SSE streaming
4. Collecting tool calls and execution history
5. Evaluating results with Claude judge
6. Submitting results back to Convex

## Quick Start

### Prerequisites

- **Mix Agent** running at `http://localhost:8088` (see [Mix Agent Setup](https://github.com/recreate-run/mix))
- **Convex Database** with evaluation API (deployment URL + secret key)
- **(Optional)** Cloud browser provider API keys (Browserbase, Brightdata, Hyperbrowser, Anchor)

### Installation

```bash
# Install dependencies
task install

# Install CLI globally
task install-cli
```

### Configuration

Create `.env` file (auto-loads on startup):

```bash
cp .env.example .env
```

Required variables:
- `CONVEX_URL` - Convex deployment URL
- `CONVEX_SECRET_KEY` - Convex API secret key

Optional:
- `MIX_AGENT_URL` - Mix Agent URL (default: `http://localhost:8088`)
- `BROWSERBASE_API_KEY`, `BRIGHTDATA_USER`, etc. - Cloud browser credentials

### Running Evaluations

```bash
# Run single task by ID
mix-eval-go --dataset PostHog_Cleaned_020226 --task-id 93046

# Run task range by index
mix-eval-go --dataset PostHog_Cleaned_020226 --start-index 0 --end-index 9 --parallel 3

# Run with cloud browser provider
mix-eval-go --dataset PostHog_Cleaned_020226 --task-id 93046 --browser-provider browserbase
```

**Options:**
- `--dataset` - Dataset name (required)
- `--task-id` - Run specific task by ID
- `--start-index`, `--end-index` - Run task range
- `--parallel` - Number of parallel tasks (default: 3)
- `--browser-provider` - Cloud browser (browserbase, brightdata, hyperbrowser, anchor)
- `--run-id` - Custom run identifier
- `--model` - Override LLM model
- `--max-steps` - Maximum steps per task

## Development

### Commands

```bash
task dev                 # Development hot reload
task build               # Build the binary
task install-cli         # Install CLI to ~/go/bin
task test                # Run tests with race detection
task test-e2e            # Run end-to-end tests (requires Mix Agent)
task tail-dev-log        # View dev server logs
task clean               # Clean build artifacts
task lint                # Run linters
task fmt                 # Format code
task --list-all          # Show all available tasks
```

### Development Workflow

During development, use the auto-built local binary instead of reinstalling globally:

```bash
# task dev auto-rebuilds bin/mix-eval-go on file changes
./bin/mix-eval-go --dataset foo --task-id 123

# Optional: Create alias for convenience
alias mix-eval-go="./bin/mix-eval-go"
```

Only use `task install-cli` when deploying or using the CLI outside this project. The dev server (`task dev`) hot-reloads changes automatically to `bin/mix-eval-go`.

### Project Structure

```
mix-eval-go/
├── cmd/mix-eval-go/           # CLI entry point
├── pkg/
│   ├── orchestrator/          # Task orchestration & SSE streaming
│   ├── convex/                # Convex database client
│   └── providers/             # Browser provider implementations
└── test/e2e/                  # End-to-end tests
```

### Testing

E2E tests require Mix Agent running at `localhost:8088`:

```bash
# Run all tests
task test-all

# Run only e2e tests
task test-e2e
```

Tests use `//go:build e2e` tag and verify the complete workflow with zero mocking.

## Architecture

### Evaluation Flow

1. Fetch tasks from Convex
2. Create browser session (if cloud provider specified)
3. Create Mix Agent session
4. Stream SSE events in background (manual HTTP due to SDK bug)
5. Send task to Mix Agent
6. Collect tool calls and screenshots
7. Extract execution history
8. Judge evaluates completion
9. Upload screenshots to Convex
10. Submit results to Convex

### Browser Providers

- **Browserbase** - High-quality managed browsers
- **Brightdata** - Global proxy network with browsers
- **Hyperbrowser** - Stealth browsing capabilities
- **Anchor Browser** - Mobile and desktop with captcha solving

## Ecosystem

Mix-Eval-Go is part of a unified evaluation platform with multiple runners:

- **evaluation-platform** - Shared Convex backend + UI for all runners
- **manus-eval** (Python) - Evaluates Manus agent (tool-based execution)
- **mix-eval-go** (Go) - This repository, evaluates Mix Agent
- **evaluations-internal** (Python) - Original framework for browser-use agent

All runners share task definitions and submit results to the same platform for comparison.

See `docs/` for detailed documentation on authentication, GitHub Actions integration, and architecture.

## Dependencies

- `github.com/recreate-run/mix-go-sdk v0.2.1` - Mix SDK client
- `github.com/joho/godotenv v1.5.1` - Environment variable loading
- Go standard library

## License

Proprietary
