# Contributing to the bundled Exgentic component

This directory contains a locally adapted snapshot of
[Exgentic](https://github.com/Exgentic/exgentic) used by AgentStream. Changes
specific to this bundled copy are contributed through the
[Sico repository](https://github.com/microsoft/Sico), not through the upstream
Exgentic repository.

## Contribution process

Follow Sico's root [contribution guide](../../../CONTRIBUTING.md) for the fork,
branch, commit, pull-request, review, code-of-conduct, and security-reporting
processes. For local setup and component-specific checks, see
[DEVELOPMENT.md](./DEVELOPMENT.md).

If a change applies to the original Exgentic project rather than this
AgentStream-specific copy, contribute it to the
[upstream repository](https://github.com/Exgentic/exgentic) separately.

## License

The contents of `labs/AgentStream`, including this bundled component, are
licensed under the Apache License 2.0; see [LICENSE](./LICENSE) and the
[AgentStream license](../LICENSE). This is an exception to Sico's root MIT
license.

New source files in this directory must include the following SPDX identifier
using the appropriate comment syntax:

```text
SPDX-License-Identifier: Apache-2.0
```
