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

# Shell Completion

DFM CLI supports tab completion for bash, zsh, and fish. The `completion` command group manages completion setup.

## Quick Setup

The easiest way to enable completion is to let DFM auto-detect your shell and configure it:

```bash
# Auto-detect shell and configure completion
dfm completion setup

# Configure for a specific shell
dfm completion setup --shell zsh

# Force setup even if completion is already configured
dfm completion setup --force
```

After running setup, restart your shell or "source" your `*rc` file to activate completion:

```bash
source ~/.zshrc   # zsh
source ~/.bashrc  # bash
```

## Manual Setup

If you prefer to manage the completion script yourself:

```bash
# Generate and save a completion script
dfm completion generate --shell zsh --output ~/.dfm-complete.zsh

# Then add to your shell config:
echo "source ~/.dfm-complete.zsh" >> ~/.zshrc
```

## Checking Completion Status

```bash
# Check status for all supported shells
dfm completion status

# Check status for a specific shell
dfm completion status --shell zsh

# Show detailed information about completion support
dfm completion info
```
