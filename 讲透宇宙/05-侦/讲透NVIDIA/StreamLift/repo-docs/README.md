# StreamLift
Real-time super-resolution for interactively streamed media.

# Overview
StreamLift is a collection of AI-optimized algorithms to achieve one or more domain-dependent goals:
* Reduce encoder (H.264/265) latency or improve throughput at the server
  * e.g. maximize simultaneous streams per streaming node
* Reduce decoder latency at the client
  * e.g. enable high-refresh rates, resolution or both
* Maximize streaming efficiency:
  * preserve static elements like UI/text/crosshair
  * improve streaming quality at low bandwidth

## Architecture
![](docs/streamlift_arch.png)

The SDK does not include video encoding and decoding capabilities; instead, it relies on the host application to interface with appropriate encoding (NvEnc) and decoding (any comaptible decoding) libraries. 

# Requirements
- Server API:
  - OS: Windows or Linux 64bit
  - GPU: Nvidia Turing+ GPU
    - Optional: NvEnc (H.264/265) capable GPU
  - Arch: x86_64 or Aarch64
  - API: CUDA 12.1+ 
- Client D3D11 API:
  - OS: Windows 64bit
  - GPU: Any D3D11 Capable GPU
    - Optional: Video decode (H.264/265) capability 
  - Arch: x86_64
  - API: DirectX11 (SM 5.0+)
- Client CUDA API:
  - OS/Arch: Windows or Linux 64bit
  - GPU: Nvidia Turing+ GPU
    - Optional: NvDec (H.264/265) capable GPU 
  - Arch: x86_64 or Aarch64
  - API: CUDA 12.1+

# Getting Started
The host application must have a server and client component. The server component is based on CUDA. The client component may choose between CUDA or D3D11 APIs.
* Server (CUDA only):
  * Include: `streamlift_server.h"`
  * Link:
    * Windows: `streamlift_server.lib`
    * Linux/Debian: `libstreamlift_server.so` 
* Client (CUDA):
  * Include: `streamlift_client_cuda.h`
  * Link:
    * Windows: `streamlift_client_cuda.lib`
    * Linux/Debian: `libstreamlift_client_cuda.so`
* Client (D3D11):
  * Include: `streamlift_client_d3d11.h`
  * Link:
    * Windows-only: `streamlift_client_d3d11.lib` 

# Basic Usage
```bash
#include "streamlift_*.h"

Streamlift_*_Init(...)

for(;;)
    Streamlift_*_ProcessFrame(...)

Streamlift_*_DeInit(...)
```

## Security
- Vulnerability disclosure: `SECURITY.md`
- Do not file public issues for security reports.

## Support
- Level: Experimental.
- How to get help: Comment on github-issues.

# License
See the LICENSE.md file for details.

