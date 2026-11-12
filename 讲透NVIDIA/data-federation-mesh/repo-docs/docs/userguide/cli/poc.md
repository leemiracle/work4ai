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

# POC Mode

DFM Proof of Concept (POC) mode allows for "mimicking" a full federation deployment on your computer. It runs each DFM site as a separate process and directly uses [NVIDIA Flare POC mode](https://nvflare.readthedocs.io/en/main/user_guide/nvflare_cli/poc_command.html#poc-command).

The `poc` command group manages the POC environment:

## Starting POC Mode

```bash
# Start with specific federation
dfm poc start --federation my_federation

# Start in debug mode
dfm poc start --debug

# Prepare workspace only
dfm poc start --prepare-only
```

It is important to highlight, that DFM POC mode always simulates some federation. By default, the CLI command starts DFM POC with the provided [example federation](https://github.com/NVIDIA/data-federation-mesh/tree/main/tutorials/example-fed). It is assumed that users will directly specify their configured federation upon using this tool. See [Configuration Management](./federation.md#configuration-management) to learn more about configuring federations with DFM CLI.

## Monitoring POC mode

Display aggregated logs when DFM is running in POC mode:

```bash
dfm poc logs
```

Check the current state of the POC environment:

```bash
dfm poc status --federation my_federation
```

## Managing the POC Environment

Other useful POC commands:

```bash
# Wait for POC to be ready
dfm poc wait

# Stop POC environment
dfm poc stop

# Restart POC environment
dfm poc restart

# Clean up POC workspace
dfm poc cleanup
```
