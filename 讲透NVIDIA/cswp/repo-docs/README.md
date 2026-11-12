<!-- SPDX-FileCopyrightText: Copyright (c) 2024-2026 NVidia Corporation. All rights reserved. -->
<!-- SPDX-License-Identifier: BSD-3-Clause -->

# NVidia's CSWP Client library
This repository contains Nvidia's implementation of the client side of the
CoreSight Wire Protocol specification.

# Overview
The NVidia's CSWP Client library can be used to communicate with NVidia's
Tegra SOCs CSWP server in order to access internal debug facilities of the
following SOCs:
-Vera

For a description of the CSWP protocol this software is based on see [https://github.com/ARM-software/coresight-wire-protocol/blob/master/cswp/doc/CSWP%20Protocol%20Specification.pdf]

# Origin of this derivative work
The code is based on the public CSWP client implementation from ARM:
[https://github.com/ARM-software/coresight-wire-protocol]
using following steps:
```bash
wget https://github.com/ARM-software/coresight-wire-protocol/archive/refs/heads/master.zip          // Get archive of latest version (07/30/2024) of repo
sha256sum master.zip                                                                                // 712ec2cf2e83dd2527d7f3a3507ce24ebca757f23283ecb82fbe055457e9d28f
unzip master.zip                                                                                    // Extracts zip file to coresight-wire-protocol-master
mv coresight-wire-protocol-master coresight-wire-protocol                                           // Rename to remove master from the name
rm ./.gitignore ./cswp/.gitignore ./rddi_streaming_trace/.gitignore ./target/cswp_server/.gitignore // Remove .gitignore files
```
# Getting Started
You will need cmake version 3.31.3
```bash
mkdir build
cd build
cmake .. -DCMAKE_INSTALL_PREFIX=<install_path>
make -j8 install
```
# Requirements
Building client for x86_64 Linux host only
Supported OS: Ubuntu 18.04+, CentOS 7 and OpenBMC.

# Reporting an issue
Please report any issue or feature request [here](https://github.com/NVIDIA/cswp/issues/new/choose)

# Community
Please email swteg-debug-help@nvidia.com if you have any question or feedback.

# License
This project is licensed under the BSD3 License - see the LICENSE.md file for details
