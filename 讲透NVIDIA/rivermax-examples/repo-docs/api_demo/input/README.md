# Rivermax Input API Demo Applications

## Description

This directory contains a set of demo applications that demonstrate the usage of
[Rivermax](https://developer.nvidia.com/networking/rivermax) Input API. The most basic
application is `receive` which demonstrates how to receive a stream from
the network using Rivermax Input API. All other applications are built on top of it
and demonstrate more advanced API features.

The `RmxInputApiBase` class provides basic (non Rivermax specific) functionality for receiving streams from the network.

## Structure

```
api_demo/input                    # Rivermax Input API demo applications directory
├── CMakeLists.txt                # CMake rules for this subdirectory
├── README.md                     # This file
├── input_base.cpp                # Rivermax Input API base class implementation
├── input_base.h                  # Rivermax Input API base class header
├── receive/                      # Rivermax Input API basic receive demo application
├── memory_allocation_receive/    # Rivermax Input API memory allocation receive demo application
├── memory_registration_receive/  # Rivermax Input API memory registration receive demo application
├── hds_receive/                  # Rivermax Input API header-data split receive demo application
├── multi_source_receive/         # Rivermax Input API multi source receive demo application
└── drain_detached_flow_receive/  # Rivermax Input API drain detached flow demo application
```
