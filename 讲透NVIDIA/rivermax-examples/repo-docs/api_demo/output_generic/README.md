# Rivermax Output Generic API Demo Applications

## Description

This directory contains a set of demo applications that demonstrate the usage of
[Rivermax](https://developer.nvidia.com/networking/rivermax) Output Generic API. The most basic
application is `generic_send` which demonstrates how to send a generic stream to the network
using Rivermax Output Generic API. All other applications are built on top of this basic application 
and demonstrate more advanced features.

The `RmxOutputGenericApiBase` class provides basic (non Rivermax specific) functionality
for sending generic streams to the network.

## Structure

```
api_demo/output_generic      # Rivermax Output Generic API demo applications directory
├── CMakeLists.txt           # CMake rules for this subdirectory
├── README.md                # This file
├── output_generic_base.cpp  # Rivermax Output Generic API base class implementation
├── output_generic_base.h    # Rivermax Output Generic API base class header
└── generic_send/            # Rivermax Output Generic API basic send demo application
```
