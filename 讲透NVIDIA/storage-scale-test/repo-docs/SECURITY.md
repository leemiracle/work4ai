<!--
SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
SPDX-License-Identifier: Apache-2.0

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
-->

# Security Policy

NVIDIA is committed to the security of its open source software. This policy
explains how to report potential vulnerabilities in `storage-scale-test` and
documents the security boundaries assumed by the project.

## Reporting a Vulnerability

If you believe you have found a security vulnerability in this project, report
it privately. **Do not open a public GitHub issue, pull request, or
discussion for security matters.**

- **NVIDIA Vulnerability Disclosure Program:**
  https://www.nvidia.com/en-us/security/
- **Email:** [psirt@nvidia.com](mailto:psirt@nvidia.com). For sensitive
  details, use the NVIDIA PSIRT PGP key:
  https://www.nvidia.com/en-us/security/pgp-key
- **Repository private reporting:** when available, use this repository's
  **Security** tab, then **Report a vulnerability**.

Please include:

- Project name, affected version, branch, or commit SHA.
- Vulnerability type and affected component or file path.
- Step-by-step reproduction instructions.
- Proof-of-concept code or commands, if available.
- Expected impact and any relevant deployment assumptions.

NVIDIA PSIRT will acknowledge the report, validate the vulnerability, assess
severity, coordinate fixes, and publish security guidance as appropriate.

## Security Architecture & Context

`storage-scale-test` is shell and Python tooling for exercising storage systems
and reporting benchmark results. It runs filesystem, object-storage, and network
benchmarks across a fleet of client nodes through passwordless SSH or Slurm;
filesystem tests can also run as Kubernetes workloads through `kubectl`. It
parses benchmark output into CSV, Markdown, tables, and plots.

The repository is an open source CLI and reporting tool. It is not a hosted
service, daemon, library linked into production applications, or security
boundary component. The project orchestrates third-party benchmark programs such
as elbencho and Warp as separate processes. Those programs are not vendored
into this repository; operators obtain or build them separately.

This tool is designed for trusted infrastructure that is actively under storage
testing. It is intended to be used with dedicated test paths and empty test
buckets where no production, sensitive, or valuable data is present. The code
can warn and validate some inputs, but it cannot enforce where users run it or
what data they choose to point it at.

**Repository Exposure Classification:** Public.
Basis: the project is intended for publication as a public open source
repository; this document is written for public consumption.

**Service Exposure Classification:** External / Regulated (high confidence).
Basis: publicly distributed, source-only CLI tooling. The project does not
operate a hosted service or distribute compiled artifacts. Benchmark runs can
create temporary inbound listeners on worker nodes and object-storage tests use
credentials supplied and controlled by the operator. This classification
reflects public distribution, not regulated-data processing by the project.

**Primary security responsibility.** The tool's responsibility is to make its
operator-visible trust boundaries clear, keep credentials and generated outputs
out of source control, and avoid surprising behavior outside the test targets
chosen by the operator. Operators remain responsible for selecting isolated
test infrastructure, disposable data locations, scoped credentials, and network
controls appropriate for their environment.

**Key boundaries and interfaces.**

- Configuration and secret sourcing: `env.sh`, filesystem `--target` and
  `--env-override` files, and the object-auth file selected by `$OBJ_AUTH_FILE`
  are operator-controlled inputs sourced as Bash. `lib/env_base.sh` sources the
  object-auth file and exports S3-compatible credential variables for Warp and
  helper tools.
- Remote fleet execution: `lib/env_functions.sh` builds and runs commands on
  configured SSH hosts or Slurm allocations. The `storage-tests/**/ssh` and
  `storage-tests/**/sbatch` scriptlets execute benchmark commands on worker
  nodes.
- Kubernetes execution: the launcher uses the operator's current `kubectl`
  context to create Jobs, Pods, DaemonSets, NetworkPolicies, and one Lease per
  claim in the namespaces the `TEST_DIRS` keys name, using the operator's
  existing claims and images. Pods run as the configured non-root UID/GID with
  no added capabilities and no privilege escalation; Elbencho Pods request
  `Unconfined` seccomp for Linux AIO. No Pod has an API token, except that a
  batch spanning namespaces adds a sequencer Pod whose ServiceAccount, Role,
  and RoleBinding (created by the launcher) allow only reading and starting
  that attempt's Jobs. A sweep's control bundle and run state live on a claim
  and are executed by the coordinator Pod.
- Temporary benchmark listeners: filesystem and network tests start
  `elbencho --service` on port 1611 or `$NETBENCH_PORT`. Multi-node Warp object
  tests start clients listening on `0.0.0.0:7761`. Kubernetes worker Pods listen
  on TCP 1611 on their Pod IP; an attempt-scoped NetworkPolicy admits only that
  attempt's coordinator where the CNI enforces policy.
- Resume and replay: `storage-tests/fs/nv-elbencho-sweep.sh` and
  `storage-tests/fs/sbatch/_nv-elbencho-coordinator.sh` source a generated
  `env_used.sh` sidecar from a results directory when resuming a sweep.
- Object connectivity helper: `utils/build/s3-test.c` performs AWS SigV4
  signing with credentials from the environment or object-auth file and uses
  TLS certificate and hostname verification for S3-compatible endpoints.
- Third-party benchmark supply chain: `utils/build/*.sh` and
  `utils/build_tarball.sh` help operators gather or build benchmark binaries,
  but they do not make this repository a binary distribution channel or a
  supply-chain guarantee for those upstream projects.

Secrets are not intended to be committed. `env.sh`, `.obj_auth`, generated
virtual environments, benchmark binaries, and release tarballs are ignored by
Git.

## Threat Model

The following scenarios are the primary security concerns for this project.
They are derived from the actual code paths and the intended deployment model.

1. **Destructive benchmark configuration:** The filesystem and object-storage
   tests intentionally create, overwrite, and delete data in the configured test
   paths and buckets. If `TEST_DIRS`, object bucket settings, or delete-only
   paths are pointed at real data, the result can be data loss. The intended
   mitigation is operational: use only dedicated test paths and empty buckets.

2. **Object-storage credential exposure:** `lib/env_base.sh` sources the
   object-auth file and exports `WARP_ACCESS_KEY`, `WARP_SECRET_KEY`, and mapped
   `AWS_*` variables. Object tests propagate those variables into benchmark
   processes and remote scriptlets. Operators should use scoped credentials for
   disposable test buckets and rotate them after shared or untrusted runs.

3. **Remote command execution across the test fleet:** SSH, Slurm, and
   Kubernetes execution are core features of this tool. A malicious `env.sh`,
   `--target` or `--env-override` file, host list, benchmark binary or image, or
   generated scriptlet can execute commands on the configured worker fleet as
   the invoking user or workload UID. Operators must treat those inputs as
   trusted and protect them with normal host filesystem permissions.

4. **Temporary listener exposure during benchmark runs:** elbencho service mode
   and multi-node Warp client mode open temporary listeners on worker nodes. If
   the benchmark network is reachable by untrusted systems, those listeners may
   expose benchmark control or traffic surfaces that this repository does not
   authenticate. Run benchmarks on isolated test networks or restrict access to
   the relevant ports.

5. **Resume sidecar sourcing:** `--resume` restores prior sweep settings by
   sourcing `env_used.sh` from a results directory. If an attacker can write to
   a results directory that also satisfies the expected layout, resuming that
   directory can execute attacker-controlled shell code. Only resume from
   results produced by this tool in trusted locations.

6. **Downloaded elbencho archive integrity:** `utils/build_tarball.sh` can
   download pinned upstream elbencho release archives. It verifies each archive
   against the architecture-specific SHA-256 value recorded in the repository
   before extraction. Maintainers must review and update both the pinned release
   and its hashes together.

7. **Kubernetes workload and claim state:** The launcher acts with the
   operator's Kubernetes credentials, and the coordinator Pod executes the
   control bundle and run state stored on a claim. Digest checks detect
   corruption, not a malicious writer: anyone who can write that claim path or
   create Pods in the namespace can change what the sweep runs. Use dedicated
   namespaces and claims, least-privilege RBAC, and digest-pinned images (the
   elbencho image and, for batches spanning namespaces, the sequencer image)
   from a trusted registry.

### Accepted Risks and Usage Assumptions

The following behaviors are intentional parts of the project's trust model.
Using the corresponding feature means that the operator accepts the residual
risk and is responsible for meeting the stated conditions.

- **User-built Warp supply chain:** `utils/build/build_warp_from_source.sh`
  clones an operator-selected upstream repository and source ref, then builds a
  Warp binary in the operator's environment. The helper accepts an installed Go
  toolchain at or above its minimum version; if none is available, it can use a
  tagged Docker image or download the minimum Go release from `go.dev`.
  `storage-scale-test` intentionally does not prescribe one Go archive or
  checksum because operators may need a newer patched Go release to avoid
  toolchain CVEs, and it does not build, release, or distribute Warp binaries.
  Users accept the residual supply-chain risk for the selected Warp source,
  resolved dependencies, Go toolchain or container image, build platform and
  settings, and resulting binary. They are responsible for selecting a trusted
  upstream repository and immutable commit, using a currently supported and
  patched Go toolchain, applying the checksum, signature, image-digest, or other
  provenance controls required by their environment, and recording hashes for
  their own artifacts when required. — *Accepted (2026-08-03): Warp is built
  from a separate open source repository with an operator-selected toolchain;
  source, toolchain, and artifact provenance are end-user build and deployment
  responsibilities.*

- **Operator-controlled S3 credentials:** The object connectivity helper assumes
  provider-issued secret keys of conventional length. Unusually long,
  nonstandard credentials may not be handled safely. Credential files and
  environment variables are trusted operator configuration; users must protect
  and validate them before use.
- **Ephemeral SSH host identity:** SSH mode does not retain or verify host keys
  because it is designed for unattended fan-out across operator-selected,
  frequently reprovisioned benchmark nodes. Enabling SSH mode accepts the
  residual risk of connecting to an impersonated host. Operators must use a
  trusted host list, isolated network, and least-privilege SSH account; where
  those conditions cannot be met, use Slurm mode or enforce host verification
  outside this tool.
- **Trusted resume state:** The `--resume` workflow sources generated shell state
  and per-execution definitions from the selected results directory. Resuming a
  run treats that directory as executable configuration. Only resume results
  created by this tool and writable solely by the trusted operator.

## Critical Security Assumptions

- The operator runs the tool on trusted, isolated test infrastructure rather
  than on production systems or shared systems with untrusted users.
- The configured filesystem paths and object buckets contain no production,
  sensitive, or valuable data.
- `env.sh`, `--target` and `--env-override` files, object-auth files, SSH host
  lists, generated execution scripts, and results directories are writable only
  by trusted users.
- In Kubernetes mode, the namespaces and the claim paths used for test roots and
  sweep state are writable only by trusted users, and the cluster's CNI enforces
  NetworkPolicy or the Pod network is otherwise isolated.
- Object-storage credentials are scoped to disposable test buckets and can be
  rotated after use.
- Worker nodes are allowed to execute benchmark commands as the invoking user,
  and the invoking user is not privileged unless the operator has deliberately
  accepted that risk.
- Benchmark listeners are reachable only from trusted benchmark clients or are
  otherwise restricted by network policy or host firewall rules.
- Pinned elbencho archives remain available at their reviewed upstream release
  URLs and match the SHA-256 values recorded in `utils/build_tarball.sh`.
- Warp source repositories, refs, dependencies, toolchains, and build
  environments selected by operators are trusted, currently security-supported,
  and reviewed before the locally built binaries are used. Operators apply any
  required provenance controls to their chosen Go distribution or image.
- Users are responsible for applying these assumptions to their own
  environments. This repository cannot enforce their network, data-handling, or
  credential-scoping choices.

## Scope

This policy covers the `storage-scale-test` repository contents. Third-party
benchmark tools downloaded, built, or invoked at runtime are governed by their
own upstream projects and licenses. Vulnerabilities in those tools should be
reported to their respective maintainers. This project does not distribute Warp
binaries; users obtain or build them from a separate open source repository and
own the provenance and integrity verification of the resulting artifacts.

Expected behavior that is in scope for documentation but not necessarily a
code vulnerability includes:

- Deleting data in configured benchmark paths or buckets.
- Running commands on explicitly configured SSH or Slurm worker nodes, or as
  Kubernetes workloads in the configured namespaces.
- Opening temporary benchmark listeners during active test runs.
- Requiring operators to supply, scope, protect, and rotate object-storage
  credentials used for their own test buckets.
