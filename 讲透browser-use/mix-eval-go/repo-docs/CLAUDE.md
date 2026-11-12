# Mix Eval Go

Go-based evaluation orchestrator for running Mix Eval tasks using browser automation agents.

## Development Commands

<bash_commands>
task dev                 # Development hot reload (rebuilds on file changes)
task build               # Build the binary
task test                # Run tests with race detection
task tail-dev-log        # View unified dev server logs (last 100 lines)
task clean               # Clean build artifacts and log files
task lint                # Run linters
task fmt                 # Format code
task install             # Install dependencies
task --list-all          # Show all available tasks
</bash_commands>

- Do NOT stop the dev server. It stays running and auto-reloads, logging to `dev.log`.
- Run `task` from the project's top-level directory.
- You MUST check the tail-dev-log after finishing each task.
- All tests include race detection (`-race` flag) to catch concurrency issues

## Testing

### Test Naming Conventions

- `*_test.go` - Unit tests (no external dependencies)
- `*_e2e_test.go` - End-to-end tests (requires Mix Agent, real browser, zero mocking)
- `*_bench_test.go` - Benchmark tests

E2E tests use `//go:build e2e` tag and skip by default. Run with `-tags=e2e`.

### Running Tests

Run all tests:

```bash
task test
```

Run tests for specific packages:

```bash
# Test a specific package
go test -v ./pkg/orchestrator

# Test with race detection (recommended)
go test -v -race ./pkg/providers

# Run specific test by name
go test -v ./pkg/orchestrator -run TestFetchTasks

# Skip integration/e2e tests
SKIP_INTEGRATION_TESTS=1 go test -v ./...
```

## Architecture

```
mix-eval-go/
├── cmd/
│   └── main.go                # Main entry point
├── pkg/
│   ├── orchestrator/          # Task orchestration & coordination
│   ├── providers/             # Browser provider implementations
│   └── convex/                # Convex database client
├── test/
│   └── e2e/                   # End-to-end tests
└── bin/                       # Built binaries (runtime)
```

## Code Style & Key Patterns

Go Conventions:

- Use `gofmt` for formatting (tabs, not spaces)
- Run tests with `-race` flag to detect race conditions
- Follow [Effective Go](https://go.dev/doc/effective_go) guidelines
- Keep packages focused and cohesive
- Prefer table-driven tests

Project-Specific Patterns:

- Context Everywhere: All async operations take `context.Context` as first parameter for cancellation and timeouts.
- Error Handling: Always handle errors explicitly. Use `fmt.Errorf("...: %w", err)` for error wrapping.
- Typed Structures: Never use `map[string]interface{}` for structured data with known fields. Define typed structs in appropriate packages (orchestrator, providers).
- Structured Errors: Use custom error types for domain-specific errors. Never return errors as maps or parse error strings.
- Named Constants: Define constants for magic strings (URLs, timeouts) and magic numbers. Never hardcode these values.
- Parallel Execution: Use goroutines with proper synchronization (WaitGroup, channels) for concurrent task execution.
- Configuration via Environment: Load all configuration from environment variables with sensible defaults.
- Graceful Shutdown: Always handle SIGINT/SIGTERM for clean resource cleanup.
