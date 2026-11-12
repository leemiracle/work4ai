# nora_lib interfaces

Contains interfaces for agents to report cost, report progress, and record state.

Includes some no-op and file-based implementations.

Publishes the `nora_lib` package

# Development

This project has no python code of its own. It only publishes a subset of code from the `impl` sub-project,
i.e. excluding anything in the `nora_lib/impl` module.

Add all tests to `impl`. This project's only testing is to run `mypy`, to verify that there are no missing dependencies or broken imports.