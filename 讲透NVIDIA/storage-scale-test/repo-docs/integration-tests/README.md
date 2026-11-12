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

# Single-host integration environment

`bin/integration-test.py` provisions the lightweight, three-node kind fixture
used to exercise Kubernetes, SSH, and Slurm storage substrates on one Linux
server. The control-plane node is also the Slinky login node and negative
control for the storage-worker label. The two worker nodes run storage clients.

Prerequisites: Ubuntu 24.04 on x86-64 or ARM64, at least two CPUs, 8 GiB total
and 6 GiB available RAM, 20 GiB free on the selected backend's filesystem,
Python 3.12 with `requirements.txt` installed, and an accessible rootful Docker
daemon. The driver installs other host packages and pinned client tools as
needed, and builds small derived Slinky and SSH images carrying the workload
account.

Run setup (or its synonym, `start`) as the ordinary test user. The NFS profile
uses passwordless `sudo` only for packages and its export, loop-device,
firewall, and systemd operations:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
source .venv/bin/activate
sudo -v
integration-tests/bin/integration-test.py setup
```

## Storage backends

- **`nfs`**: a loop-backed NFSv4 export with NFS CSI, using kind's pinned
  Kindnet.
- **`sbx-shared`** (Docker SBX only): one repository-backed directory mounted
  into every kind node, with static RWX claims bound to separate test-data and
  shared-home subdirectories.

Both satisfy the same contract (cross-node and host read/write visibility,
shared homes, successful SSH and Slurm sweeps); they differ in environmental
fidelity, not feature coverage. NFS and CSI provisioning themselves are out of
this repository's test scope.

Both backends also provide a second storage target for multi-target Kubernetes
scenarios: a namespace named `<namespace>-target-2` holding its own
`storage-test-rwx` claim. On NFS the StorageClass `subDir`
(`<namespace>/<claim>`) gives it a distinct directory; on SBX a second static PV
(`storage-scale-sbx-data-2`) binds it to its own `storage-test-2` directory.
A third claim, `storage-test-rwx-2`, sits beside the primary one in the primary
namespace for the aggregate scenario (on SBX it is bound to
`storage-scale-sbx-data-3` and its own `storage-test-3` directory). Scenario
roots name their claim (`storage-test-rwx:<root>`, or
`<namespace>/storage-test-rwx:<root>` for the second namespace), and every Pod
the product creates mounts each claim at `/mnt/storage-scale-test/<claim>`. The
harness's own utility Pods mount claims the same way, so a path the product
recorded is valid there unchanged.
Teardown removes them with the kind cluster and the backend's data. The
Kubernetes prerequisite probe stays in the primary namespace only: it checks
cluster-wide CNI and policy behavior, the namespaces carry no Pod Security
labels, and every attempt creates its own NetworkPolicies per target namespace.

The default, `--storage-backend auto`, selects `nfs` when the host has the
loop, mount, systemd, and kernel NFS facilities, and `sbx-shared` only when a
recognized capability that NFS needs is absent. An explicit backend never falls
back. Setup records the selection; changing it requires teardown. Other
download, image, Kubernetes, storage-visibility, SSH, and Slurm failures are
fatal.

Select Docker SBX explicitly with:

```bash
integration-tests/bin/integration-test.py \
  --storage-backend sbx-shared setup
```

The SBX profile:

- requires Docker's private engine to bind-mount the checked-out repository,
  plus preinstalled host packages; it never invokes `sudo`;
- uses the tested kind v0.30.0/Kubernetes v1.34.0 profile, mapping `/dev/null`
  to `/dev/kmsg` only when that device is missing;
- replaces Kindnet, whose nftables policy path the nested SBX kernel cannot
  run, with checksum-verified Calico on digest-pinned images preloaded through
  host Docker;
- installs Docker SBX's proxy CA, when exposed, in the disposable kind nodes;
- keeps data under `tmp/integration-sbx-shared` (override with
  `--sbx-shared-root`, which must stay below the repository's `tmp/`). Its
  four marker-owned, disposable backing directories (test data, the second
  target's data, the primary namespace's second claim's data, and shared homes)
  are deliberately non-sticky `0777`, because SBX can map the host caller and
  UID 2000 workloads to different owners and both must create and remove
  scenario data.

### NFS headroom and kernel isolation

The NFS fixture raises the server to at least 32 workers
(`INTEGRATION_NFS_THREADS`, 1-256) without lowering a larger pool or
restarting the server, and restores the recorded original count at teardown.
Tuning is skipped when that count cannot be recorded, and tuning or restoration
failures are logged rather than fatal. The `sbx-shared` backend owns no NFS
server and skips tuning.

Containers share the host kernel, so the loop-backed NFS fixture can stall when
server writes wait on commits that need the same worker pool. At each command
timeout the driver logs bounded pressure, NFS counters, blocked-task stacks,
and kernel warnings before cleanup touches the PVC; blocked server workers
double the pool, up to 256. This mitigates the stall but is not isolation,
which needs a separate NFS server VM or host. Local NFS hosts should carry the
upstream `nfs_release_folio()` reclaim fix
(`cce0be6eb4971456b703aaeafd571650d314bcca`); the harness never upgrades or
reboots a shared host.

## Setup, identities, and state

Setup preloads the pinned upstream Elbencho image, and the product's default
sequencer image (`alpine/kubectl` 1.37.0 by index digest, on both profiles; the
multi-target sequencer's `kubectl` and `sh`), under
fixture-private node references and runs a temporary Kubernetes prerequisite probe: one non-root
service Pod per worker, direct Pod-IPv4 access from a coordinator, denial from
an unrelated Pod, and bidirectional PVC visibility. Elbencho service Pods
request the workload's `Unconfined` seccomp profile; other probe Pods keep
`RuntimeDefault`. The probe uses no Service, host networking, host ports,
service-account token, or external pull from kind nodes, and removes its
objects and storage afterward.

Every lifecycle action refuses root. Kubeconfig, keys, downloaded clients,
cached deployments, rendered manifests, logs, and test runs are created
user-owned under `tmp/integration-state` (setup never recursively chowns it),
and setup confirms the caller can use Docker, kind, kubectl, and that directory.
The generated host SSH key, strict known-hosts file, and worker addresses live
there too; re-running setup reconciles and validates the environment without
replacing them or retained backend data.

The in-cluster workload account is independent of the host account: LoginSet
coordination, Slurm jobs, SSH workers, and shared-storage staging run as
`tester` (UID/GID 2000), verified on the coordinator and both real `srun`
tasks. This matches the NFS export's anonymous mapping, so clients create data
directly with a restrictive umask and never chown through the all-squashed
mount.

SSH workers normally have separate `emptyDir` homes. A scenario needing the
RWX shared-home claim owns a bounded StatefulSet transition and restores
separate homes afterward; setup and SSH test preflight recover an interrupted
transition first. The kind and Slurm fixtures keep running throughout.

## Running tests

After setup succeeds, run the bounded filesystem regression cases with:

```bash
integration-tests/bin/integration-test.py test
integration-tests/bin/integration-test.py test --substrate ssh
integration-tests/bin/integration-test.py test --scenario baseline
integration-tests/bin/integration-test.py test --scenario mdtest-sweep
integration-tests/bin/integration-test.py test --list-scenarios
```

With no options, `test` runs every scenario on each applicable substrate.
`--substrate` accepts `all`, `ssh`, `slurm`, or `kubectl`; `--scenario` is
repeatable. `--list-scenarios` prints each scenario's name, substrates, and
purpose, and needs no setup state or privileges. Real tests refuse root,
require the saved non-root identity, validate the live topology, generate
environments from the packaged `env.sh.template`, and run `validate_env.sh`
once per configuration it treats differently (one root; two worker-directory
roots; per substrate, the multi-claim, single-big-file, weighted-root,
shared-home, and allocation-option cases), not before every sweep.

Scenarios fall into common cases that run on all three substrates (baseline,
direct I/O, failure/resume, mdtest sweep, mixed prepared batch, live capture)
and focused cases for a subset (for example, retained data on SSH and Slurm,
Slurm scheduling, SSH shared homes, and Kubernetes cancellation, coordinator
loss, endpoint drift, and multi-target runs). Workloads are deliberately small.
Assertions check execution coordinates, state transitions, workload evidence, dataset totals,
required native flags, scheduling evidence, and semantic report rows and plot
families, never incidental output or performance values. Structure-only
direct-I/O scenarios use 256 KiB files because synced direct I/O to the NFS
export is slow; scenarios whose sizes or active intervals matter keep 16 MiB.
Failure-injection staging publishes files through digest-verified temporary
copies with remote deadlines and transient retries, and cleanup restores the
wrapper from the verified local binary, never from a remote delegate.

The kubectl cases exercise the asynchronous submit/status/collect/cancel/resume
lifecycle specified in
[KUBERNETES_ELBENCHO_LIFECYCLE.md](../docs/KUBERNETES_ELBENCHO_LIFECYCLE.md)
and described for users in
[FILESYSTEM_TESTING.md](../docs/FILESYSTEM_TESTING.md#kubernetes-run-inspect-and-collect).
The local fixture proves that lifecycle and its networking contract (ordinary
Pod networking with an attempt-scoped NetworkPolicy; no host networking, host
ports, or Service) on its supported kind profile. An external cluster still
needs its own acceptance run for CNI, Pod-to-Pod policy, storage behavior, and
credential lifetime.

The Kubernetes multi-target cases pass their targets as `--target` files, never
as `--env-override` files: what to test comes from `env.sh` or `--target`, and
how to test from `env.sh` or `--env-override`. Every scenario's `env.sh` names
roots as `storage-test-rwx:<root>` (the claim, then the path inside it) with
`KUBECTL_NAMESPACE` set to the primary namespace and `KUBECTL_SEQUENCER_IMAGE`
set to the preloaded sequencer image's fixture-private digest alias (so
`validate_env.sh`'s default image check passes under the `Never` pull policy);
no scenario sets `KUBECTL_PVC`, `KUBECTL_PV`, or `KUBECTL_STORAGE_TARGETS`.

The `kubectl-multi-target` case writes two target files, `a.env`
(`<namespace-1>/storage-test-rwx:<root>`) and `b.env`
(`<namespace-2>/storage-test-rwx:<root>`) and prepares a default time-limited IO
`--batch --target a.env --target b.env` and an `--append`ed mdtest with the same
two `--target` flags. That gives four groups: IO on `a` then `b`, then mdtest on
`a` then `b`, each named `<namespace>/storage-test-rwx:<root>`. It runs
`validate_env.sh --sequencer` once with that environment, the real sequencer
probe included (`env.sh` names one namespace, so the probe runs there only). It
then runs `validate_env.sh --sequencer` once more as a temporary ServiceAccount
that may run Jobs and hold Leases but may not create or delete ServiceAccounts,
Roles, or RoleBindings, and requires it to fail, naming each missing permission
and the fallback (the temporary objects are always deleted). After
`--start` it does not call `--status`, because `--status` itself starts the next
suspended coordinator Job when the sequencer is lost: it waits with `kubectl`
for the sequencer Job to be Complete and requires the sequencer Pod's log to
show each segment (a namespace) starting and completing in order, then all
segments complete (on failure the error carries the sequencer log and the Job
and Pod states). Only then does it poll `--status` for `NEXT_ACTION=COLLECT` and
collect. It asserts each submission's printed `_GROUPS` and
`GROUP_<gid>_TARGET` keys (and no `_CLAIM` key); each group's recorded
namespace, target name, target file, and Pod-mapped roots (and no PV or claim);
the `GROUP_<NNNN>_KIND`, `GROUP_<NNNN>_TARGET`, and `SEGMENT_COUNT`,
`SEGMENT_<i>_NAMESPACE` (`<i>` counts from 0), and `SEGMENT_<i>_STATE` status
keys (and no `TARGET_<i>_*` keys); one Lease per claim
and one coordinator Job per namespace; successful cells with result files; run
trees on both claims before collection and none after; the report index's Target
column; and no tool-owned Lease, Job, DaemonSet, NetworkPolicy, Pod,
ServiceAccount, Role, or RoleBinding left in either namespace. The scenario sets
`KUBECTL_SEQUENCER_POLL_SECONDS=2` so the sequencer hands off promptly.
`kubectl-multi-target-unbound` renders `b.env` with a scenario-owned claim that
can never bind and requires `--start` to fail while leaving no owned object or
run tree behind.

`kubectl-same-namespace-targets` tests an aggregate target beside a separate
target, all in the primary namespace and with no sequencer image. `agg.env`
weights `storage-test-rwx:<root-a>` 2 and `storage-test-rwx-2:<root-b>` 1;
`single.env` holds `storage-test-rwx-2:<root-c>`. `env.sh` carries the aggregate
map too, so `validate_env.sh` checks both claims. The case prepares one small 4K
cell per group with
`--batch --target agg.env --target single.env --run-to-completion --nodes 1`,
starts it, and requires one attempt with exactly one plain coordinator Job (no
init containers) and one worker DaemonSet, each mounting both claims at
`/mnt/storage-scale-test/<claim>`, and no sequencer Job, ServiceAccount, Role, or
RoleBinding. With no sequencer to prove, it polls `--status` until
`NEXT_ACTION=COLLECT` and requires no `SEGMENT_*` keys, since segments are
reported for several namespaces only. After collection it requires every cell to
succeed and, from the aggregate group's recorded
`ELBENCHO_RUN_GENERATED_TEST_DIRS_CSV` (no cluster call), a 2:1 split of generated
directories between the two claims. It also requires the run tree to have been on
the control root's claim (the claim of the lexically first root, here
`storage-test-rwx-2`) and gone after collection, and every generated directory
and tool-owned object on both claims to be gone.

`mixed-batch` also exercises storage-target provenance on every substrate: its
appended metadata group passes a `--target` file (an explicit
`STORAGE_TARGET_NAME` and a distinct `TEST_DIRS` root, claim-qualified on
Kubernetes) and a workload-only `--env-override` recipe. The test requires each
submission to print `GROUP_<gid>_TARGET` and the legacy `GROUP_TARGET` (and no
`_GROUPS` list or `_CLAIM` key), the prepared batch's `--status` to print
`GROUP_<NNNN>_KIND` and `GROUP_<NNNN>_TARGET` for every group (the other two
groups carry the derived name), each group's `env_used.yaml` to record its name,
its `target_file` (path, SHA-256 of the file, and the variables it set; `null`
for groups without one) and the workload override files in order, and the report
index's Target column to name each group's target. The report step also runs
`extract-filesystem.py --to-json` and requires `results.json` to show a complete
batch: one group per identity, every execution `success`/`complete`, and
elbencho first/last rates on each IO execution.

Tests run a real deployment archive: the harness snapshots the tracked source
once, builds it with the zero-argument `utils/build_tarball.sh`, and caches the
validated archive by snapshot manifest, architecture, integration recipe, and
seeded Elbencho/runtime identity. Each scenario extracts it into an isolated
workspace, adds only its own environment and inputs, and cleans its remote data
afterward. SSH cases launch `validate_env.sh` and `nv-elbencho-sweep.sh` on the
host and reach the two worker pods over SSH; Slurm cases stream the archive to
the LoginSet, extract it in shared storage, and launch both there. The NFS
profile gets Elbencho from a size-limited, checksum-verified upstream archive;
on Docker SBX, where GitHub release assets may be unreachable, the binary and
runtime libraries are extracted from the digest-pinned
`docker.io/breuner/elbencho:v3.2-1` image into the generated test deployment
only.

Beyond each scenario's own checks, every test requires successful execution
records, exact workload totals, ordered worker selection, nonempty benchmark
output, environment snapshots, and cleanup of generated data directories, and
runs `utils/extract-elbencho.py` on host-side result copies. Host-side results
and diagnostics stay under the state directory, with timestamped build and step
logs below its `test-runs/`.

## Stopping and tearing down

Delete the disposable kind cluster and, for the NFS backend when owned
exclusively by the harness, stop NFS with:

```bash
integration-tests/bin/integration-test.py stop
```

Stop deletes kind containers, Kubernetes objects, and MariaDB's node-local
volume, and preserves packages, downloaded charts, Docker images, generated
keys and passwords, rendered state, logs, and backend data. A later `start`
therefore creates and validates a fresh cluster, which takes longer than an
idempotent setup against a running one.

Where retained fixture data is not wanted (for example, CI workers), run:

```bash
integration-tests/bin/integration-test.py teardown
```

Teardown is idempotent. It performs the stop, then deletes the fixture's
generated data, keys, logs, and locally built image tags, restoring the exact
prior image ID where a tag existed before setup. Harness-downloaded client
copies go with the state tree; OS packages, pre-existing client tools, and
reusable upstream image layers stay. It refuses destructive cleanup when
ownership and path checks do not match the fixture.

- **NFS**: removes the dedicated export and configuration and any
  harness-owned UFW rule, unmounts the verified loop-backed filesystem, and
  disables and stops `nfs-server` only if setup started it and no unrelated
  exports remain.
- **Docker SBX**: removes only the marker-owned shared root; it never invokes
  NFS, systemd, firewall, loop, or mount operations.

## Logs, caches, and retries

Pass `--verbose` before the action (`integration-test.py --verbose <action>`)
for command-level logging. On failure, the driver captures host, Docker,
backend, Kubernetes node, Pod, and event diagnostics without
printing Kubernetes Secrets.

Image pulls reuse digest- and architecture-verified host Docker caches. Slinky
charts are downloaded and validated before any release is installed, then
cached with source, version, and checksum records. Recognized transient pull
failures get up to four attempts per registry reference, with exponential
backoff and jitter within a shared four-minute deadline per acquisition;
setup logs keep sanitized errors and retry history. Authentication errors,
corrupt artifacts, and unknown errors fail immediately, and retries cannot
overcome a persistent registry outage.

## Bootstrapping prerequisites in a constrained sandbox

An agent preparing a fresh, network-constrained sandbox for this suite
(for example, a Docker SBX environment) should prefer these sources, which
are reliably reachable even when arbitrary internet hosts are not:

- Install `kind` (pin the version this repository tests, currently v0.30.0),
  `file`, and `python3-venv` from the distribution's own `apt` repositories
  instead of downloading GitHub release binaries.
- Fetch `kubectl` from `dl.k8s.io` and Helm via its official
  `get.helm.sh` install script; verify the published checksums. These
  endpoints are commonly allowed even where generic GitHub release downloads
  are not.
- Run ShellCheck from the `shellcheck-py` PyPI package inside the repository's
  `.venv-ci`, rather than fetching a standalone ShellCheck release archive.
- Let the harness pull container images (including the pinned Elbencho image)
  through the host Docker daemon, whose registry path and proxy/CA
  configuration is usually the most reliable, and import them into kind; don't
  rely on kind nodes reaching registries directly. Pulled images stay cached
  for later runs.
- Give the Docker data root (commonly `/var/lib/docker`) the ~50 GiB this
  suite's images, kind nodes, and build artifacts need; request a larger
  volume up front rather than after `no space left on device`.

If a required tool is unavailable through these channels, install it into the
repository's own state (a local venv, `tmp/`, or similar) rather than assuming
it is preinstalled; see "Checks (run before committing)" in
[AGENTS.md](../AGENTS.md) for the CI-tooling equivalent.

## On-demand CI

The `Filesystem integration` GitHub Actions workflow runs only on demand, never
on pull-request, push, or default-branch events. To run it, open **Actions**,
choose **Filesystem integration**, select **Run workflow**, pick the workflow
ref, and optionally enter a different source branch, tag, or commit SHA to test
(empty tests the workflow ref). **Re-run jobs** repeats an existing run.

It runs six concurrent jobs, one per architecture (amd64, arm64) and substrate
(SSH, Slurm, Kubernetes), each on its own runner and NFS fixture; scenarios
within a job run one at a time. Three fixtures per architecture cost more
runner time than one but cut wall time. Each job installs
`requirements.txt` in an isolated venv, smoke-tests driver startup, runs setup,
proves root lifecycle execution is rejected, runs `test --substrate
<substrate>` as the ordinary runner account, and tears down twice. The fixture
lifecycle does not depend on the substrate, so only the SSH jobs (the
shortest, so they absorb the extra time best) and an unsharded `all` run also
repeat setup and stop and restart the fixture before testing. Run the same
lifecycle locally with:

```bash
integration-tests/bin/ci-integration.sh <amd64|arm64> [nfs|sbx-shared] [all|ssh|slurm|kubectl]
```

The substrate defaults to `all`. Every job tests one source commit, resolved
once from the requested ref, and writes a manifest (commit, architecture,
backend, substrate, boot ID, lifecycle step durations, and planned versus
passed work items). The final status job requires every job to pass and the six
manifests to cover the unsharded scenario plan exactly once per architecture
(`integration-tests/lib/shard_manifest.py verify`).

Separately, the regular (pull-request, default-branch, weekly) CI pytest job
sets `CI_REQUIRE_DOCKER=1`, making the Docker BuildKit fixture-build tests
mandatory rather than skippable; see
[Running repository checks](../docs/CODING_STANDARDS.md#running-repository-checks).

### Package mirrors for fixture image builds

The package-cache action rewrites only the runner's own APT sources, so the
SSH and Slinky login image builds (the only ones that install packages) get
mirrors through `lib/apt-build.sh`:

- **Interface**: the workflow exports `INTEGRATION_APT_ARCHIVE_MIRROR`,
  `INTEGRATION_APT_SECURITY_MIRROR`, `INTEGRATION_APT_PORTS_MIRROR`, and
  `INTEGRATION_APT_CA_BUNDLE`, which the driver forwards to those builds.
  Mirror URLs must be plain `http(s)` without credentials; HTTPS needs the CA
  bundle. With none set (the local default), builds keep the base image's
  public repositories.
- **Rewrite**: only the URI of the image's own Ubuntu sources changes (amd64
  archive/security, arm64 ports); suites, components, and signing keys are
  kept.
- **Coverage and failure**: once any mirror is set, every public Ubuntu URI the
  image uses must be covered, checked per URI even when a deb822 `URIs:` field
  lists several; a mirror is needed only for hosts the image uses (an amd64
  image needs no ports mirror). Because `apt-get update` exits 0 when a source
  fails, the script inspects its output: a failed index from an Ubuntu source
  (public archive/security/ports.ubuntu.com or a configured mirror) fails and
  is retried, while failures of non-Ubuntu sources in the base image (such as
  the Slinky login image's Kubernetes repository) are tolerated, as with bare
  `apt-get`. A mirror that cannot be applied or reached fails the build; it
  never falls back to the public repositories.
- **CA trust**: the bundle is mounted as the `apt_ca` BuildKit secret with mode
  0444 (APT downloads as `_apt`; the script fails early if `_apt` cannot read
  it) and passed to APT on the command line, so it is never stored in the
  image.
- **Time budget**: there is no per-attempt cap. APT's own finite timeouts (30 s,
  with two internal retries) bound each stall, the script retries only
  when APT fails or a failed Ubuntu index appears, and `APT_BUDGET_SECONDS`
  (default 540) ends the whole build, so slow but progressing downloads are
  never killed and restarted. The driver logs each image build's start and
  elapsed time at INFO.
