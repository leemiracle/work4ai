# Rivermax API Demo Applications

## Description

This directory contains a set of demo applications that demonstrate the usage of
[Rivermax](https://developer.nvidia.com/networking/rivermax) API.
The applications are provided as source code and can serve as references when developing your own applications.

The applications are simple, API-centric examples, each self-contained and easy to follow.
They all inherit from the common base class RmxApiBaseDemoApp,
which provides infrastructure unrelated to Rivermax so the demos can focus on the Rivermax API.
Each application overrides the operator() method in the base class to implement the Rivermax-specific functionality it is designed to demonstrate.

> The code is provided "As Is" and any express or implied warranties, including,
> but not limited to, the implied warranties of merchantability and fitness for a particular
> purpose are disclaimed.

## Structure

```
api_demo             # Root directory
├── CMakeLists.txt   # CMake rules for this subdirectory
├── README.md        # This file
├── api_base.cpp     # Base demo application
├── api_base.h       # Base demo application header
├── input/           # Rivermax Input API demo applications
├── output_generic/  # Rivermax Output Generic API demo applications
└── output_media/    # Rivermax Output Media API demo applications
```
