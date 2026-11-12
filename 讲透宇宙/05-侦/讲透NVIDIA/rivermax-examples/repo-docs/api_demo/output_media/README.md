# Rivermax Output Media API Demo Applications

## Description

This directory contains a set of demo applications that demonstrate the usage of
[Rivermax](https://developer.nvidia.com/networking/rivermax) Output Media API. The most basic
application is `media_send` which demonstrates how to send a media stream to the network
using Rivermax Output Media API. All other applications are built on top of this basic application
and demonstrate more advanced features.

The `RmxOutputMediaApiBase` class provides basic (non Rivermax specific) functionality
for sending media streams to the network.

## Structure

```
api_demo/output_media                # Rivermax Output Media API demo applications directory
├── CMakeLists.txt                   # CMake rules for this subdirectory
├── README.md                        # This file
├── output_media_base.cpp            # Rivermax Output Media API base class implementation
├── output_media_base.h              # Rivermax Output Media API base class header
├── media_send/                      # Rivermax Output Media API basic send demo application
├── memory_allocation_media_send/    # Rivermax Output Media API memory allocation send demo application
├── memory_registration_media_send/  # Rivermax Output Media API memory registration send demo application
├── hds_media_send/                  # Rivermax Output Media API header-data split send demo application
└── dynamic_media_send/              # Rivermax Output Media API dynamic ancillary send demo application
```
