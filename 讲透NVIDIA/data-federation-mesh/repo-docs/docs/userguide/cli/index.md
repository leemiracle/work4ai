<!--
SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
SPDX-License-Identifier: Apache-2.0

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
-->

# Command Line Interface (CLI)

**Data Federation Mesh CLI** is a command line tool that simplifies
interaction with DFM and NVIDIA Flare backend within DFM, and provides a convenient
way to perform many DFM-related tasks, such as code development (both DFM core and adapters),
testing, running DFM in POC (simulation) mode, deploying and packaging. Each command
has a comprehensive help guide:

```bash
# Display main DFM CLI help
dfm --help

# Display help for POC command group
dfm poc --help

# Display help for a particular command in POC group
dfm poc start --help
```

## Installation

When installing DFM from an installable `wheel` package, the DFM CLI is installed automatically.

## Commands

- [Shell Completion](completion.md)
- [Federation Management](federation.md)
- [POC Mode](poc.md)
