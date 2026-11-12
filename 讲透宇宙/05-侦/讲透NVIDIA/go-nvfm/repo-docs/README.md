# go-nvfm

Go Bindings for the NVIDIA Fabric Manager SDK (NVFM)

## Table of Contents

- [Overview](#overview)
- [Fabric Manager SDK Package](#fabric-manager-sdk-package)
- [Quick Start](#quick-start)
- [Examples](#examples)
- [How the bindings are generated](#how-the-bindings-are-generated)
- [Code Structure](#code-structure)
  - [Code defining the NVFM API](#code-defining-the-nvfm-api)
  - [Code to load `libnvfm.so`](#code-to-load-libnvfmso)
  - [Code to bridge the auto-generated and manual bindings](#code-to-bridge-the-auto-generated-and-manual-bindings)
  - [Manual wrappers around the auto-generated bindings from `c-for-go`](#manual-wrappers-around-the-auto-generated-bindings-from-c-for-go)
  - [Test code](#test-code)
- [Building and Testing](#building-and-testing)
- [Updating the Code](#updating-the-code)
  - [Update the Fabric Manager SDK headers](#update-the-fabric-manager-sdk-headers)
  - [Regenerate bindings](#regenerate-bindings)
  - [Add manual wrappers](#add-manual-wrappers)
- [Releasing](#releasing)
- [Contributing](#contributing)

## Overview

This repository provides Go bindings for the NVIDIA Fabric Manager SDK (NVFM).

At present, these bindings are only supported on **Linux**.

These bindings are not a reimplementation of Fabric Manager in Go, but rather a
set of wrappers around the C API provided by `libnvfm.so`. Fabric Manager itself
runs as a daemon/service. Applications using these bindings initialize the local
client library with `nvfm.Init()`, then connect to the running Fabric Manager
daemon with `nvfm.Connect()` before using connection-oriented APIs.

**Note:** A working Fabric Manager installation with `libnvfm.so` is not
required to compile code that imports these bindings. However, you will get a
runtime error if `libnvfm.so` is not available in your library path at runtime.
Connection-oriented APIs also require a running Fabric Manager service.

The vendored SDK headers in `gen/nvfm` come from the latest available CUDA
repository package and will need to be periodically refreshed.

The SDK headers retain the notices provided in NVIDIA's development package.

## Fabric Manager SDK Package

`libnvfm.so`, `nv_fm_agent.h`, and `nv_fm_types.h` are shipped in the Fabric
Manager SDK/development package, not necessarily in the core Fabric Manager
daemon package. NVIDIA documents the SDK as a separate RPM/Debian development
package for compiling Fabric Manager API clients. See the
[NVIDIA Fabric Manager User Guide](https://docs.nvidia.com/hgx-platforms/fabric-manager-user-guide/index.html).

Use the package that matches the installed driver/Fabric Manager branch and
version.

| Linux family | Package name to look for | NVIDIA CUDA repo path pattern |
| --- | --- | --- |
| Ubuntu/Debian | `nvidia-fabricmanager-dev` or `nvidia-fabricmanager-dev-<driver-branch>` | `https://developer.download.nvidia.com/compute/cuda/repos/<ubuntu-distro>/<arch>/` |
| RHEL/CentOS/Rocky/Alma/Amazon/Fedora | `nvidia-fabricmanager-devel` or `nvidia-fabric-manager-devel` | `https://developer.download.nvidia.com/compute/cuda/repos/<rpm-distro>/<arch>/` |

Examples of repo path components are `ubuntu2204/x86_64`, `ubuntu2404/x86_64`,
`rhel8/x86_64`, `rhel9/x86_64`, and `rhel10/sbsa`.

On Debian/Ubuntu-based systems:

```bash
apt-cache search nvidia-fabricmanager-dev
apt-cache policy nvidia-fabricmanager-dev nvidia-fabricmanager-dev-<driver-branch>
sudo apt-get install nvidia-fabricmanager-dev
```

On RPM-based systems:

```bash
dnf repoquery 'nvidia-fabric*manager*devel*'
sudo dnf install nvidia-fabricmanager-devel
# If your configured repo uses the dashed package name:
sudo dnf install nvidia-fabric-manager-devel
```

## Quick Start

The code below shows an example of initializing the local NVFM client library,
connecting to Fabric Manager over a Unix domain socket, and querying the number
of supported fabric partitions.

```go
package main

import (
	"fmt"
	"log"

	"github.com/NVIDIA/go-nvfm/pkg/nvfm"
)

func main() {
	ret := nvfm.Init()
	if ret != nvfm.SUCCESS {
		log.Fatalf("unable to initialize NVFM: %v", nvfm.ErrorString(ret))
	}
	defer nvfm.Shutdown()

	handle, ret := nvfm.Connect(nvfm.WithUnixSocket("/run/nvidia-fabricmanager/socket"))
	if ret != nvfm.SUCCESS {
		log.Fatalf("unable to connect to Fabric Manager: %v", nvfm.ErrorString(ret))
	}
	defer handle.Disconnect()

	partitions, ret := handle.GetSupportedFabricPartitions()
	if ret != nvfm.SUCCESS {
		log.Fatalf("unable to query partitions: %v", nvfm.ErrorString(ret))
	}

	fmt.Printf("Supported partitions: %d\n", partitions.NumPartitions)
}
```

Sample output:
```
$ go run main.go
Supported partitions: 15
```

Note: Use `nvfm.WithAddress(address)` instead of `nvfm.WithUnixSocket(path)` to
connect over TCP.

## Examples

The [`examples`](examples) directory contains standalone programs that
demonstrate how to list, activate, and deactivate Fabric Manager partitions:

- [`list-partitions`](examples/list-partitions)
- [`activate-partition`](examples/activate-partition)
- [`deactivate-partition`](examples/deactivate-partition)

Build all examples with:

```bash
make examples
```

## How the bindings are generated

This project leverages two core technologies:

1. Go's builtin support for `cgo` (<https://go.dev/cmd/cgo/>)
1. A third-party tool called `c-for-go` (<https://c.for-go.com/>)

Using these tools, we generate Go bindings for NVFM from the Fabric Manager SDK
headers:

- `nv_fm_agent.h`
- `nv_fm_types.h`

Most of the process to generate these bindings is automated, but manual code is
still used to make the generated bindings more useful from an end user's
perspective. The basic flow to generate the bindings is therefore to:

1. Copy the desired Fabric Manager SDK headers into `gen/nvfm`
1. Run `c-for-go` using `gen/nvfm/nvfm.yml`
1. Run `go tool cgo -godefs` to produce Go struct layouts in `types_gen.go`
1. Generate package and handle interfaces with `gen/nvfm/generateapi.go`
1. Keep manual wrappers around the raw generated calls in `pkg/nvfm`

As an example, consider the generated binding for
`fmGetSupportedFabricPartitions()`:

Original API in `nv_fm_agent.h`:

```c
fmReturn_t fmGetSupportedFabricPartitions(fmHandle_t pFmHandle, fmFabricPartitionList_t *pFmFabricPartition);
```

Auto-generated Go binding from `c-for-go`:

```go
func fmGetSupportedFabricPartitions(PFmHandle *nvfmHandle, PFmFabricPartition *FabricPartitionList) Return {
	cPFmHandle, cPFmHandleAllocMap := (C.fmHandle_t)(unsafe.Pointer(PFmHandle)), cgoAllocsUnknown
	cPFmFabricPartition, cPFmFabricPartitionAllocMap := (*C.fmFabricPartitionList_t)(unsafe.Pointer(PFmFabricPartition)), cgoAllocsUnknown
	__ret := C.fmGetSupportedFabricPartitions(cPFmHandle, cPFmFabricPartition)
	runtime.KeepAlive(cPFmFabricPartitionAllocMap)
	runtime.KeepAlive(cPFmHandleAllocMap)
	__v := (Return)(__ret)
	return __v
}
```

Manual wrapper around the generated binding:

```go
func (fm *fabricManager) GetSupportedFabricPartitions() (FabricPartitionList, Return) {
	var partitions FabricPartitionList
	partitions.Version = FabricPartitionListVersion
	ret := fmGetSupportedFabricPartitionsFunc(fm.handle, &partitions)
	return partitions, ret
}
```

The manual wrapper initializes the versioned C structure and returns the result
as a Go value. It is used through the connected handle returned by `Connect()`:

```go
partitions, ret := handle.GetSupportedFabricPartitions()
```

## Code Structure

There are two top-level directories in this repository:

- `/gen`
- `/pkg`

The `/gen` directory houses the Fabric Manager SDK headers, `c-for-go`
configuration, and small helper programs used while generating bindings. The
`/pkg` directory houses the dynamic loader package and the final NVFM Go
bindings.

In general, the code can be broken into five logical parts:

1. Code defining the NVFM API and how generated bindings should be produced
1. Code responsible for dynamically loading `libnvfm.so`
1. Code bridging auto-generated bindings and manual wrappers
1. Manual wrappers that expose the package API
1. Test code

Each of these parts is discussed below.

### Code defining the NVFM API

The following files aid in defining the NVFM API and how generated bindings
should be produced from it.

- `gen/nvfm/nv_fm_agent.h`
- `gen/nvfm/nv_fm_types.h`
- `gen/nvfm/nvfm.yml`
- `gen/nvfm/generateapi.go`

The header files are copies of the headers from the Fabric Manager SDK
development package. `nvfm.yml` is the input file to `c-for-go` that tells it
how to parse the headers and generate bindings. `generateapi.go` creates the
package-level API aliases and Go interfaces from the manual wrapper methods.

### Code to load `libnvfm.so`

The code under `pkg/dl` is responsible for dynamically loading `libnvfm.so`
from the runtime system. This happens under the hood whenever a user calls
`nvfm.Init()`.

By default, the bindings look for:

```text
libnvfm.so
```

Use `nvfm.SetLibraryOptions()` before `nvfm.Init()` to load a non-standard
library path:

```go
err := nvfm.SetLibraryOptions(nvfm.WithLibraryPath("/path/to/libnvfm.so"))
if err != nil {
	return err
}
```

### Code to bridge the auto-generated and manual bindings

The files below define glue between the generated bindings and the manual
wrappers.

- `pkg/nvfm/bindings.go`
- `pkg/nvfm/cgo_helpers_static.go`
- `pkg/nvfm/const_static.go`
- `pkg/nvfm/return.go`
- `pkg/nvfm/zz_generated.api.go`

`bindings.go` stores generated function variables so tests can replace raw C
calls with stubs. `cgo_helpers_static.go` contains helper functions for C-style
strings and cgo allocation markers. `return.go` makes the generated `Return`
type implement useful string/error behavior. `zz_generated.api.go` exposes the
package-level methods and interfaces derived from the manual wrappers.

### Manual wrappers around the auto-generated bindings from `c-for-go`

The following files add manual wrappers around the generated bindings.

- `pkg/nvfm/api.go`
- `pkg/nvfm/connect.go`
- `pkg/nvfm/handle.go`
- `pkg/nvfm/init.go`
- `pkg/nvfm/lib.go`

These wrappers handle dynamic library lifecycle, connection options, Fabric
Manager handles, versioned parameter structs, and friendlier slice-based
arguments.

For example, `ActivateFabricPartitionWithVFs()` validates the VF list length
and passes the correct pointer/count pair to the generated C binding:

```go
func (fm *fabricManager) ActivateFabricPartitionWithVFs(id FabricPartitionId, vfs []PciDevice) Return {
	if len(vfs) > MAX_NUM_GPUS {
		return BADPARAM
	}
	if len(vfs) == 0 {
		return fmActivateFabricPartitionWithVFsFunc(fm.handle, id, nil, 0)
	}
	return fmActivateFabricPartitionWithVFsFunc(fm.handle, id, &vfs[0], uint32(len(vfs)))
}
```

### Test code

Unit tests live next to the packages they test:

- `pkg/nvfm/*_test.go`

The unit tests do not require `libnvfm.so`. Integration smoke tests are skipped
automatically when `libnvfm.so` is not available in the runtime library path.

## Building and Testing

Building and testing the bindings is straightforward. The only prerequisite for
regenerating bindings is a working installation of `c-for-go`.

```bash
make bindings
make build
make test
```

## Updating the Code

The general steps to update the bindings to a newer Fabric Manager SDK are as
follows.

### Update the Fabric Manager SDK headers

Install or download the desired Fabric Manager SDK/development package, then
copy the updated headers into `gen/nvfm`:

```text
gen/nvfm/nv_fm_agent.h
gen/nvfm/nv_fm_types.h
```

The currently vendored headers came from:

```text
nvidia-fabric-manager-devel-610.43.02-1.el9.x86_64.rpm
```

After replacing the headers, inspect the diff for new or changed API calls:

```bash
git diff -w gen/nvfm/nv_fm_agent.h gen/nvfm/nv_fm_types.h
```

### Regenerate bindings

Run:

```bash
make bindings
```

This copies the headers into `pkg/nvfm`, runs `c-for-go`, regenerates Go struct
layouts with `go tool cgo -godefs`, regenerates `zz_generated.api.go`, and
formats the updated packages.

### Add manual wrappers

If the updated SDK adds new functions that should be part of the public Go API,
add manual wrappers under `pkg/nvfm` and rerun:

```bash
make bindings
make test
```

The interface generator will include exported methods on the `library` and
`fabricManager` types in `zz_generated.api.go`.

## Releasing

Once the code in `gen/` has been updated and the generated code in `pkg/` has
been refreshed, create a release by committing both the source header changes
and generated binding changes.

A typical flow is:

```bash
make bindings
make test
git add gen/ pkg/
git commit -m "Add bindings for Fabric Manager SDK <version>"
VERSION=v<version> # Eg: v1.0
git tag $VERSION
git push origin HEAD $VERSION
```

If a fix needs to be made against a previous release, append a revision suffix
`-<revision>` number to the tag. For example:

```bash
git checkout v1.0
git checkout -b bug-fixes-for-v1.0
... fix bugs and commit
git tag v1.0-1
git push v1.0-1
```

## Contributing

Please see the file [CONTRIBUTING.md](CONTRIBUTING.md) for details on how to contribute to this project.
