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

# Tutorials

This folder contains the following tutorials and examples:

| Directory | Description |
|-----------|-------------|
| [zero-to-thirty](zero-to-thirty/) | Start here. Introduces essential DFM concepts and walks you through developing adapters and setting up a simple federation. |
| [weather-fed](weather-fed/) | Jupyter notebooks demonstrating pipelines built with `nv-dfm-lib-weather` adapters for distributed weather data processing. |
| [example-fed](example-fed/) | A small reference federation with multiple sites that imitates hotel reception greetings. |
| [startup-fed](startup-fed/) | A `cookiecutter` template for scaffolding your own federation project. |

For setup instructions, see the [DFM documentation](https://nvidia.github.io/data-federation-mesh/tutorials.html) or the README in each tutorial directory.

## Cookiecutter Startup Template

After you are familiar with DFM (for example, after completing the Zero to Thirty tutorials), you can use the startup template to scaffold a new federation project with the minimum setup needed to develop adapters and deploy in POC mode. The template uses [`cookiecutter`](https://github.com/cookiecutter/cookiecutter) to generate and customise the project directory.

1. Install `cookiecutter` following the [installation instructions](https://github.com/cookiecutter/cookiecutter).
2. `cd` to the folder where you want to create your project.
3. Run `cookiecutter https://github.com/NVIDIA/data-federation-mesh --directory tutorials/startup-fed`

The command will prompt you for project details and then generate a directory with the following structure:

```
your_project/
├── your_package/
│   ├── apps/
│   │   └── your_app.py              # Application that creates DFM pipelines
│   ├── configs/
│   │   ├── federation.dfm.yaml      # Federation and site configuration
│   │   └── project.yaml             # NVIDIA Flare project config
│   └── lib/
│       └── __init__.py              # Your adapter implementations
├── concierge_example/               # Toy example of adapters and DFM setup
├── .dfm-cli.conf.yaml               # CLI config
├── .gitignore
├── federation.yaml                  # List of configured federations
├── pyproject.toml
└── README.md
```

Follow the `README.md` in the generated folder to proceed with installation and development.
