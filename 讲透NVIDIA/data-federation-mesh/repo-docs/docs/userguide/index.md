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

# User Guide

Welcome to the Data Federation Mesh (DFM) user guide. This guide documents the package and its design.

## Quick Start

### Install

Install the core DFM package:
```bash
pip install nv-dfm-core
```

### Verify Installation

```bash
dfm --version
dfm --help
```

To follow the rest of this quick-start guide, clone the repository and install from source:
```bash
git clone https://github.com/NVIDIA/data-federation-mesh.git
cd data-federation-mesh
uv sync --package nv-dfm-core
```

```{tip}
For detailed installation options — including installing individual packages, tutorial extras, and weather adapter dependencies — see the [Installation](about/installation.md) page.
```

### Run the Example (Local Target)

From `tutorials/example-fed`:
```bash
# Activate the virtual environment
source .venv/bin/activate

# Install the example federation package in editable mode
uv pip install -e tutorials/example-fed

# Run the example application
python tutorials/example-fed/examplefed/apps/concierge.py --target local --name 'DFM-Test' --greetme-from app --message 'Hello, User!'
```

You should expect the following output:
```
Executing the GreetMe that's specialized on the concierge homesite with custom message
Received greeting from concierge for place 'yield', frame token='@dfm-control-token' frame=[0]:
  Hello, User!
Received stop of call frame [0]
Received overall pipeline stop frame
Job (hopefully) finished with status FINISHED: JobStatus.FINISHED
The concierge app says goodbye!
```

### Run the Example (Distributed POC Mode)

Run the same example with a local distributed deployment:
```bash
# Start the simulated distributed environment (POC mode); make sure the virtual environment is activated
dfm poc start --federation examplefed

python tutorials/example-fed/examplefed/apps/concierge.py --target flare --name 'DFM-Test' --greetme-from reception --federation-path workspace/examplefed_poc/examplefed/
```

You should expect the following output:
```
Executing the general GreetMe on site reception
Site info for reception doesn't have send cost info to site 'concierge'. Using suboptimal default info.
Site info for reception doesn't have send cost info to site 'concierge'. Using suboptimal default info.
Received greeting from reception for place 'yield':
  Welcome to the reception desk at examplefed, DFM-Test. Today is Thursday, 2025-04-17 and it is 10 o'clock. We hope you are having a good experience.
Received stop of call frame [0]
Received overall pipeline stop frame
Job (hopefully) finished with status FINISHED: JobStatus.FINISHED
The concierge app says goodbye!
```

To stop the local distributed deployment:
```bash
dfm poc stop
```

```{tip}
To learn more, continue with the [Zero to Thirty](../tutorials-zero-to-thirty/00-introduction.md) tutorial.
```

## About

- [Introduction](about/introduction.md)
- [Key Concepts](about/key_concepts.md)
- [Installation](about/installation.md)

## Development

- [DFM Workflow](development/workflow.md)
- [Adapters and Operations](development/adapters.md)
- [Configuration Files](development/federation_configuration.md)
- [Site Customization](development/site-customization.md)

## CLI
- [Command Line Interface (CLI)](cli/index.md)

```{toctree}
:caption: About
:maxdepth: 1
:hidden:

about/introduction
about/key_concepts
about/installation
```

```{toctree}
:caption: Development
:maxdepth: 1
:hidden:

development/workflow
development/adapters
development/federation_configuration
development/site-customization
```

```{toctree}
:caption: CLI
:maxdepth: 1
:hidden:

cli/index
cli/completion
cli/federation
cli/poc
```
