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

# Key Concepts

The Data Federation Mesh (DFM) is built upon a set of core ideas and terminology that defines its architecture and operational model. 

## Federation

A collection of heterogeneous resources (for example, data sources, computational resources, services) distributed across multiple sites that collaboratively implement common functionality.

A federation is a closed, independent entity with:

- Its own configurations, executable code, and certificates
- Services distinct from other federations
- Separate configuration, testing, and deployment

## Site

A group of services and resources deployed together in one location, maintained by the same *site administrator*. Multiple sites communicating in a peer-to-peer way form a federation. Primary site types include:

- *homesite* — accepts connections from DFM clients, manages requests, and holds results for clients to poll
- *controller site* (NVFlare server) — submits pipelines for execution and distributes jobs across computation sites; required by NVFlare design
- *worker sites* (NVFlare workers) — host adapters and perform computation

## Site Administrator

A role that maintains the site. Responsibilities include:

- Setting up site configuration and deploying services
- Ensuring site functionality and security
- Controlling resources provided and used by the site
- Configuring the operations API exposed to DFM users (mapping operations to adapters, setting public parameters)

## Federation Administrator

A role responsible for the overall federation. Duties include:

- Monitoring federation health
- Combining individual site configurations
- Generating startup kits

## Federation Configuration

YAML files that specify operations API and sites with their respective providers and interfaces. This configuration is critical for generating various assets during a provisioning phase. Configuration files must:

- Use a `.dfm.yaml` extension
- Include the DFM configuration format version
- Include the API version
- Include the Python package name for the generated code

The system supports referencing single objects or merging dictionaries from external files or URLs using JSON Pointers.

## DFM Client (Apps)

A UI or API used by an end-user application to communicate with a federation. The DFM client allows for:

- Connecting with the homesite
- Creating a DFM session
- Submitting pipelines and discovery requests
- Polling results
- Cancelling requests

While a federation, as a collection of multiple sites, provides a single coherent set of operations that can be used to assemble pipelines, a single federation may be used by multiple DFM clients or Apps.

## Operation (API)

Defines the signature of a function that consists of a name, typed input parameters, expected output types, and an implicit agreement on its general semantics. Operations are defined within the API section of the federation's YAML configuration. This is a public API exposed to a DFM user. Operations are used to build a pipeline and make up nodes of the pipeline graph. During provisioning, language-specific APIs are generated from the YAML definitions.

## Adapter

Plugin-like components that implement specific DFM functionalities. DFM users never interact with adapters directly. Instead, they call the [*Operations API*](#operation-api) within their pipelines. Adapters implement the abstract signatures defined by operations.

The site administrator defines which adapter implements each operation at each site, and reflects this in the DFM configuration. DFM includes example adapters as a starting point, but users are expected to write their own adapters tailored to their federation's needs.

## Providers

Groups of related interface operations that share common functionality or implementation details. They help organize and manage sets of operations that work together and can be used for overloading the same operation with variations in functionality.

## Bindings

Define how an [*adapter*](#adapter) is associated with an [*operation*](#operation-api) within a site's or provider's interface. Bindings map adapter parameters to:

- The operation's parameters
- A constant value
- A secret (from a secret vault)

**Example:** An adapter with parameters `(p1: str, p2: str, p3: int)` can be bound to an operation with `(i1: int, i2: str)` so that `p1` maps to `i2`, `p3` to `i1`, and `p2` to a constant or secret. Site administrators define adapter-operation bindings.

## Pipeline

JSON-serialized graphs submitted by a user for execution. Nodes correspond to operations defined in the federation's API; edges are data flows between operations. Special built-in nodes need not be specified in the API.

Pipelines run at one of two *targets*:

- *`local`* — execution on a single machine using multiprocessing, no deployed federation required
- *`flare`* — execution within a DFM deployment based on NVIDIA Flare

For distributed execution, pipelines are translated into a Petri-net-like format:

- *Places* — buffers for tokens (individual data items)
- *Transitions* — functions that consume tokens from input places and produce tokens into output places
- *Activations* — checks before a transition to ensure correct tokens are available

## Startup Kit

Packages of code, credentials, and configuration produced by the [NVFlare provisioning tool](https://nvflare.readthedocs.io/en/2.6.2/real_world_fl/overview.html) for each federation site. Site admins receive startup kits, verify consistency with their configuration, and use them to deploy the site.

## DFM CLI

A command-line interface that mediates interaction with DFM and NVIDIA Flare. It supports:

- Code development and generation
- Testing
- Running in Proof of Concept (POC) mode

