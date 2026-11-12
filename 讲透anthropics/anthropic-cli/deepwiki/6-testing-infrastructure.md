<!-- source: DeepWiki mcp.deepwiki.com · repo anthropics/anthropic-cli · page 6 Testing Infrastructure · fetched 2026-10-26 -->

# Testing Infrastructure

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.stats.yml](.stats.yml)
- [internal/binaryparam/binary_param.go](internal/binaryparam/binary_param.go)
- [internal/binaryparam/binary_param_test.go](internal/binaryparam/binary_param_test.go)
- [internal/mocktest/mocktest.go](internal/mocktest/mocktest.go)
- [scripts/mock](scripts/mock)
- [scripts/test](scripts/test)

</details>



The Anthropic CLI testing infrastructure is designed to ensure reliability across a wide range of API commands and edge cases. The suite combines unit tests for internal logic with high-fidelity integration tests that execute the CLI against a mock server. This approach validates the entire request-response lifecycle, including flag parsing, file embedding, and output rendering.

## High-Level Testing Strategy

The testing architecture is built on three primary pillars:

1.  **Integration Tests with Steady**: The CLI uses a mock server (Steady) that runs against the same OpenAPI specification used to generate the CLI's request structures. This ensures the CLI is always tested against the expected API contract.
2.  **Network Isolation**: Tests are executed in a restricted environment where network access is blocked for all hosts except the local mock server.
3.  **Cross-Platform Validation**: The test suite includes specific checks for Windows compatibility by attempting to compile test binaries for `GOOS=windows`.

### Testing Lifecycle Diagram

The following diagram illustrates how a test case interacts with the CLI binary and the mock server environment.

**CLI Integration Test Flow**
```mermaid
graph TD
    subgraph "Go Test Runner"
        A["TestRunMockTestWithFlags"] --> B["blockNetworkExceptMockServer()"]
        B --> C["exec.Command('go run ./cmd/ant')"]
    end

    subgraph "CLI Process (ant)"
        C --> D["Flag Parsing"]
        D --> E["internal/requestflag"]
        E --> F["HTTP Client"]
    end

    subgraph "Mock Environment"
        F --> G["Steady Mock Server (Port 4010)"]
        G -- "OpenAPI Responses" --> F
    end

    F -- "Blocked if not 4010" --> H["External Internet"]

    Sources: [internal/mocktest/mocktest.go:60-94](), [scripts/test:15-56]()
```

## Mock Server Integration

The integration suite relies on the **Steady** mock server. Before running tests, the `scripts/test` runner checks for a running instance of Steady or starts one automatically using `scripts/mock`.

*   **Endpoint Validation**: Steady validates that the CLI sends correctly formatted query parameters, headers, and body objects according to the OpenAPI spec.
*   **Base URL Override**: While the default is `http://localhost:4010`, the `TEST_API_BASE_URL` environment variable can be used to point the test suite at a different target, such as a staging environment.
*   **Daemon Mode**: The `scripts/mock` script can start the server as a background process, waiting for the `/_x-steady/health` endpoint to return success before proceeding.

For details on the helper functions used to invoke these tests, see [Mock Server Test Helpers](#6.1).

**Sources:** [scripts/test:15-37](), [scripts/mock:23-47](), [.stats.yml:1-4]()

## Network Isolation and Security

To prevent accidental real API calls during testing, the `internal/mocktest` package implements a custom dialer. The `OnlyMockServerDialer` intercepts all connection attempts and blocks any that do not target the `mockServerURL`.

| Component | Responsibility |
| :--- | :--- |
| `OnlyMockServerDialer` | Checks if `address == mockServerURL.Host`. Returns error if not. |
| `blockNetworkExceptMockServer` | Replaces `http.DefaultTransport` with the restricted dialer. |
| `restoreNetwork` | Reverts the global HTTP transport to its original state. |

**Sources:** [internal/mocktest/mocktest.go:33-56]()

## Unit Testing Patterns

In addition to integration tests, the codebase contains standard Go unit tests for internal utilities. These focus on logic that does not require a full API round-trip, such as:

*   **Path Handling**: Validating that `-` or `/dev/stdin` correctly maps to standard input.
*   **JSON Transformation**: Testing the GJSON `--transform` logic in `cmdutil`.
*   **Flag Merging**: Ensuring that file contents are correctly embedded into JSON request bodies.

For details on per-command test files and utility tests, see [Command-Level Tests](#6.2).

**Code Entity Mapping**
```mermaid
graph LR
    subgraph "Code Entity Space"
        BP["internal/binaryparam"]
        MT["internal/mocktest"]
        ST["scripts/test"]
    end

    subgraph "Natural Language Space"
        BP -- "implements" --> "Stdin vs File logic"
        MT -- "implements" --> "Network Isolation"
        ST -- "implements" --> "Test Runner & Mock Lifecycle"
    end

    Sources: [internal/binaryparam/binary_param.go:1-30](), [internal/mocktest/mocktest.go:1-102](), [scripts/test:1-65]()
```

## Developer Workflow

Developers typically run the full suite using the provided bash script:

```bash
./scripts/test
```

This script performs the following sequence:
1.  Sets `GOPRIVATE` to ensure internal SDKs are handled correctly.
2.  Ensures the Steady mock server is running on port 4010.
3.  Executes `go test ./...`.
4.  Cross-compiles tests for Windows (`GOOS=windows`) to catch platform-specific compilation errors.

**Sources:** [scripts/test:1-65]()

---

