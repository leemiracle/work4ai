<!--
SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
SPDX-License-Identifier: Apache-2.0
-->

# Media Function Operator Kit

Media Function Operator Kit provides reusable Kubernetes API types for media
function operators, plus an example operator that shows how to use them. It is
intended for teams building Kubernetes operators for media functions that need a
common shape for control, transport, format, resource, and status fields.

## Overview

The root module exposes reusable media-function API types:

```go
import mfov1alpha1 "github.com/NVIDIA/media-function-operator-kit/api/v1alpha1"
```

The example operator lives under `examples/reference-operator` and currently
contains:

- `ColorPatternMediaFunction`: generates a video test pattern.
- `SrtGatewayMediaFunction`: receives media and forwards it as SRT.

The example CRDs use the `example.com/v1alpha1` API group. The runtime path
is MXL video transport with NMOS or static MXL flow IDs. The shared
API still includes the RTP transport option for compatibility and future
controller implementations.

## Getting Started

[docs/getting-started.md](docs/getting-started.md) covers the main workflows:

- Create another operator that imports the shared kit API.
- Work on the included example operator.
- Apply the included samples in `config/samples`.

Implementation review is mostly in `api/v1alpha1` for reusable kit API types
and `examples/reference-operator` for the example operator, manifests, charts,
and samples. The example operator has its own Operator SDK project metadata and
Makefile; the root Makefile delegates to it and adds shared API generation.

Add the kit to another Go operator:

```sh
go get github.com/NVIDIA/media-function-operator-kit@<version>
```

## Development

Generate manifests and deepcopy code:

```sh
make manifests generate
```

Run the non-e2e test suite:

```sh
go test $(go list ./... | grep -v /e2e)
```

Build the example operator manager image (`examples/reference-operator`):

```sh
make docker-build IMG=<registry>/reference-media-functions-operator:<tag>
```

Release automation can publish that manager image to the project container
registry. Use the same image reference when installing the example operator.

## Requirements

- Go 1.24 for local builds and tests.
- Kubernetes cluster access for deployment and end-to-end tests.
- Docker or a compatible container tool for image builds.
- `kubectl` and Helm 3 for installing the example operator.
- MXL samples require a separate media-function image (`<registry>/<mxl-media-function>:<tag>`),
  distinct from the example operator manager image. See
  [Runtime Contracts](docs/getting-started.md#runtime-contracts) in getting-started.

## Usage

Create a normal Operator SDK project in your own repository, add this module as
a dependency, and import the shared API package in your CRD types. The included
example operator can be built and deployed from the repository root:

```sh
make docker-build IMG=<registry>/reference-media-functions-operator:<tag>
make docker-push IMG=<registry>/reference-media-functions-operator:<tag>
make deploy IMG=<registry>/reference-media-functions-operator:<tag>
```

The example operator Helm chart (`reference-media-functions-operator`) can also
be installed directly:

```sh
helm upgrade --install reference-media-functions-operator \
  ./examples/reference-operator/charts/reference-media-functions-operator \
  -n reference-media-functions-operator --create-namespace \
  --set image.repository=<registry>/reference-media-functions-operator \
  --set image.tag=<tag>
```

More examples and runtime details are in
[docs/getting-started.md](docs/getting-started.md).

## Releases & Roadmap

Release tags are expected to build and publish the example operator manager
image (`reference-media-functions-operator`) to the project container registry.
The Helm chart is maintained under
`examples/reference-operator/charts/reference-media-functions-operator`.

## Contribution Guidelines

Start with [CONTRIBUTING.md](CONTRIBUTING.md). Contributions require a
Developer Certificate of Origin sign-off:

```sh
git commit -s
```

Development quickstart:

```sh
make manifests generate
make test
```

## Governance & Maintainers

This project is maintained by NVIDIA. Project changes are reviewed through pull
requests, with reusable kit API changes kept separate from example operator
implementation changes where practical.

## Security

Do not file public issues for security reports. Use NVIDIA's vulnerability
disclosure process in [SECURITY.md](SECURITY.md) for security issues.

## Support

Support level: experimental. Use repository issues and pull requests for
questions, bugs, and proposed improvements once the repository is publicly
available.

## Community

Community discussion happens through repository issues and pull requests.

## References

- [Getting Started](docs/getting-started.md)
- [Example Operator](examples/reference-operator)
- [Apache License 2.0](LICENSE)

## License

This project is licensed under the Apache License 2.0. See [LICENSE](LICENSE)
for details.
