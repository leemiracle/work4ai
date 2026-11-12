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

# Federation Management

A federation consists of distributed services, resources, and applications that execute user-created pipelines. Each federation is one self-contained instance, meaning that two separate federations do not communicate and do not know anything about their internal operations and pipelines. Each federation is an independent entity, containing its own configuration, code, certificates, etc. that can be distributed and deployed. Services that are part of *federation A* cannot communicate with services from *federation B*. Each federation needs to be configured, tested, and deployed separately. 

DFM CLI provides tools for:
 - federation setup and configuration
 - generation of API and runtime code
 - generation of deployment files, such as Dockerfiles and Helm charts.

## Configuration Management

Each federation requires configuration file (.dfm.yaml) that lists all the sites and operations available within that federation. 
If DFM is run in *flare* mode (that is deployed on a Kubernetes cluster or executed in POC mode), then an additional configuration file for NVFlare is required (`project.yaml` ). 

All the provisioning files required for running federation are located in `workspace` directory. 

The following commands facilitate federation configuration management:

```bash
# List all configured federations
dfm fed config list-all

# Add or modify federation configuration
dfm fed config set my_federation --federation-dir /path/to/fed --config-path /path/to/config

# Show federation configuration
dfm fed config show my_federation

# Delete federation configuration
dfm fed config delete my_federation
```

## Code Generation

The following commands facilitate and manage code generation within a given federation:

```bash
# Generate API and runtime code
dfm fed gen code my_federation --output-dir /path/to/output

# Generate only runtime code
dfm fed gen code my_federation --no-api

# Generate code for specific sites
dfm fed gen code my_federation --runtime-site site1 --runtime-site site2
```

## Docker Files Generation

These CLI tools facilitate federation deployment by generating Docker-specific files (including `Dockerfile`), and various other scripts, including runtime scripts, that are essential for containerization and deployment of a federation.

```bash
# Generate Docker files for a federation
dfm fed gen docker my_federation

# Force regeneration even if files already exist
dfm fed gen docker my_federation --force

# Generate with custom patch file
dfm fed gen docker my_federation --patch /path/to/custom-patch.yaml
```

**Requirements:**
- The federation configuration must include a `provision.docker` section specifying:
  - `dockerfile`: Path (relative to federation directory) where the Dockerfile should be generated
  - `image`: Docker image name
  - `tag`: Docker image tag
  - `build.engine`: Build engine (`docker` or `podman`)
  - `build.arch`: Target architecture (`amd64` or `arm64`)
  - `build.context`: Build context directory

:::{warning}
Generated files are intended as starting placeholders and are not production-ready. Review and adapt them for your environment before deploying.
:::

## Helm Charts Generation

The following CLI tools generate tentative Helm chart for Kubernetes deployment of DFM federations. This includes complete Helm chart templates, deployment configurations, and deployment scripts for easy federation management in Kubernetes environments.

```bash
# Generate Helm chart for a federation
dfm fed gen helm my_federation

# Force regeneration even if chart already exists
dfm fed gen helm my_federation --force

# Generate with custom patch file
dfm fed gen helm my_federation --patch /path/to/custom-patch.yaml
```

**Requirements:**
- The federation configuration must include a `provision.helm` section specifying:
  - `path`: Path (relative to federation directory) where the Helm chart should be generated
  - `name`: Name of the Helm chart
  - `chartVersion`: Version of the Helm chart (optional, defaults to federation version)
  - `appVersion`: Application version (optional, defaults to federation version)
  - `startup_package_source`: Package source mode (`env` or `workspace`)
- Federation must have exactly one server site and one client site (multiple sites not yet supported)

:::{warning}
Generated files are intended as starting placeholders and are not production-ready. Review and adapt them to your environment before deploying.
:::

## Provisioning

Once the federation is configured and its code is generated, the federation administrator has to provision federation. Provisioning produces the Flare workspace that includes startup packages for each site that are then distributed to site administrators.

```bash
# Provision a federation
dfm fed gen provision my_federation

# Clean the workspace before provisioning
dfm fed gen provision my_federation --clean
```

The `--clean` flag removes any previously generated provisioning artifacts before running, useful when re-provisioning after configuration changes.

## Job Submission

The jobs can be submitted to the federation when it is fully configured and running.

There are two execution targets for a pipeline:
- `local` - runs within the context of user's application process (does not need a running federation),
- `flare` - runs within federation deployment based on NVIDIA Flare.

There are two main ways to submit a job using DFM CLI:
- directly submit a Python script, or
- submit a script starting user's application that runs a DFM pipeline and collects results

Submitting a pipeline is a simplification for submitting a full job script. In this case, DFM CLI takes care of creating a DFM session, running the pipeline, and collecting the results. User is only required to provide a path to a Python script that must contain `get_pipeline` function that returns DFM `Pipeline` object, and `get_pipeline_parameters` that returns a dictionary with pipeline parameters.

A simple pipeline that runs within the DFM example federation [`examplefed`](../../tutorials/example-fed):

```python
import argparse

from examplefed.apps.concierge import GreetMe, Yield
from dfm.api import Pipeline

def get_pipeline(args: list[str] | None = None):
    with Pipeline() as pipeline:
        greet = GreetMe(site="reception", name="World")
        Yield(value=greet)
    return pipeline

def get_pipeline_parameters(args: list[str] | None = None):
    return {}
```

Submit jobs to federations using the `fed submit` command:

```bash
# Submit job to federation (flare target, default)
dfm fed submit my_federation --target flare script /path/to/user_script.sh --timeout 3600 -- [job_args...]

# Submit job to federation (flare target, POC mode)
dfm fed submit my_federation --target flare --poc script /path/to/user_script.sh --timeout 3600 -- [job_args...]

# Submit to local target
dfm fed submit my_federation script /path/to/user_script.sh --target local -- [job_args...]
```

:::{tip}
The `submit` tool will pass all arguments provided after `--` to the submitted script/pipeline as local parameters. It will also automatically assign `DFM_FEDERATION_WORKSPACE_PATH` variable that points to files required for execution of a DFM user application. This can be used in user's scripts to connect to the federation. 
:::
