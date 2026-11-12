# Rivermax Examples

[![GitHub license](https://img.shields.io/github/license/NVIDIA/nvidia-docker?style=flat-square)](https://github.com/nvidia/rivermax-examples/blob/main/License.md)

This repository contains example applications and demonstrations for NVIDIA Rivermax SDK, 
showcasing high-performance media and data streaming capabilities over standard IP networks.

## Overview

NVIDIA Rivermax is an SDK that enables direct data flows from the NIC to the GPU, 
delivering best-in-class throughput and latency for streaming workloads. 
This repository provides practical examples demonstrating how to leverage Rivermax for various streaming applications.

## Repository Structure

- [api_demo/](./api_demo/) - Simple straightforward applications demonstrating the direct usage of Rivermax API
- [legacy/](./legacy/) - Legacy applications demonstrating more complex Rivermax capabilities

## Development Kit Integration

This repository relies on [rivermax-dev-kit (RDK)](https://github.com/NVIDIA/rivermax-dev-kit) as a provider of infrastructure services.
However, all the Rivermax related logic and all the calls to Rivermax API, 
are explicitly invoked by the code within the examples.

## Getting Started

### Prerequisites

Please follow the guidelines provided in [README of rivermax-dev-kit](https://github.com/NVIDIA/rivermax-dev-kit?tab=readme-ov-file#prerequisites)

> For a smoother start, it is better to follow the installation guidelines of the 
> [Rivermax SDK](https://developer.nvidia.com/networking/rivermax-getting-started).

### Building

#### Building Rivermax Examples

The repository relies on [CMake](https://cmake.org/) to build binaries, and it can be built both on Linux and Windows.  
On how to build these examples using CMake, please follow the guidelines provided in
[README of rivermax-dev-kit](https://github.com/NVIDIA/rivermax-dev-kit?tab=readme-ov-file#building) 

#### Building Specific Categories

One can filter out categories of applications completely, 
by selecting only the needed ones during the configuration command line e.g.,:

```sh
cmake -B <build-dir> -DRMAX_APP_LISTS="api_demo"
```

>[!NOTE]
>By default, if `RMAX_APP_LISTS` is not specified, all apps are configured to be built.

#### Building Specific Applications

To build individual applications using target names:

```sh
cmake --build <build-dir> --target=<app_name>
```

>[!NOTE]
>By default, if a target is not explicitly specified, all targets are built.

#### CUDA Support

Enable GPU acceleration for supported applications:

```sh
cmake -B <build-dir> -DRMAX_CUDA=ON
```

## Usage

Each example code provides its own usage instructions.

## Issues and Contribution

We welcome contributions to the Rivermax Examples repository:  
* To contribute and make pull requests, please follow the guidelines outlined in the [Contributing](CONTRIBUTING.md) document.
* Please let us know about any bugs or issues by [filing a new issue](https://github.com/NVIDIA/rivermax-examples/issues/new).
