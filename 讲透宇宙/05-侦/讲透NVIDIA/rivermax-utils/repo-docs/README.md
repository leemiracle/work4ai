# Rivermax Utils

[![GitHub license](https://img.shields.io/github/license/NVIDIA/nvidia-docker?style=flat-square)](https://github.com/nvidia/rivermax-utils/blob/main/License.md)

This repository contains utility scripts and tools for NVIDIA Rivermax SDK, providing essential tools for system optimization, performance tuning, and various utilities across different platforms.

## Overview

NVIDIA Rivermax Utils provides a comprehensive set of tools designed to enhance the Rivermax experience by offering system tuning capabilities, performance optimization scripts, and other utility functions to improve your Rivermax development and deployment workflow.

## Repository Structure

### Linux Tools
- **[`rmx_perf/linux/`](./rmx_perf/linux)** - Advanced performance tool
  - Discover NVIDIA network devices
  - Tune system, network, CPU, GRUB
  - Query current system state
  - Monitor PTP/PHC synchronization
  - Manage PTP services
- **[`media_converter/`](./media_converter)** - MP4 to SMPTE ST 2110-20 raw media format converter

### Windows Tools
- **[`windows_tuning/`](./windows_tuning)** - Tuning scripts
  - System optimization and network interface tuning
  - Available functionality: check, set and restore system tuning

## Getting Started

Clone the repository:
```sh
git clone https://github.com/nvidia/rivermax-utils.git
```

Navigate to the specific tool directory for detailed usage instructions.

## Issues and Contribution

We welcome contributions to the Rivermax Utils repository:  
* To contribute and make pull requests, please follow the guidelines outlined in the [Contributing](CONTRIBUTING.md) document.
* Please let us know about any bugs or issues by [filing a new issue](https://github.com/NVIDIA/rivermax-utils/issues/new).

## License

This project is licensed under the same terms as the Rivermax SDK. See the [License](License.md) file for details.
