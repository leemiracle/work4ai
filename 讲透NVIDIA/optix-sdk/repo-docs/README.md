# OptiX SDK

OptiX is an application framework for achieving optimal ray tracing
performance on the GPU. It provides a simple, recursive, and flexible
pipeline for accelerating ray tracing algorithms. 

This repository contains the OptiX SDK, which includes the header files
necessary for building an application with OptiX support, including access to
the OptiX functions provided by the NVIDIA display driver. This SDK also
contains sample applications that demonstrate the use of the OptiX API, and
some third party code to support the sample applications.

The [OptiX SDK](https://developer.nvidia.com/rtx/ray-tracing/optix) is
alternatively available as a downloadable, installable package on the NVIDIA
Developer web site.

A small minimal version of the SDK that includes only OptiX headers, but no
sample applications is available in the 
[optix-dev repository](https://github.com/NVIDIA/optix-dev). 
The optix-dev repository can be used
instead of the complete SDK for CI/CD workflows, automated installations, and
container-based development environments.

Visit the [OptiX home page](https://developer.nvidia.com/rtx/ray-tracing/optix) 
for an in-depth
introduction to OptiX and to find online OptiX documentation.

For bug reports, comments, or questions, please visit the 
[OptiX Forum](https://forums.developer.nvidia.com/c/gaming-and-visualization-technologies/visualization/optix/167)
