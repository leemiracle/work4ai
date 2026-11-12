<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/cluster-readiness-engine · page 8 Testing Infrastructure · fetched 2026-10-26 -->

# Testing Infrastructure

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.claude/skills/cre-test/SKILL.md](.claude/skills/cre-test/SKILL.md)
- [.claude/skills/managing-openvex/SKILL.md](.claude/skills/managing-openvex/SKILL.md)
- [.github/workflows/attest-selftest.yml](.github/workflows/attest-selftest.yml)
- [AGENTS.md](AGENTS.md)
- [CLAUDE.md](CLAUDE.md)
- [CONTRIBUTING.md](CONTRIBUTING.md)
- [cmd/integration/testdata/reconcile/bandwidth-measurement/expected.json](cmd/integration/testdata/reconcile/bandwidth-measurement/expected.json)
- [cmd/integration/testdata/reconcile/goodput-measurement/expected.json](cmd/integration/testdata/reconcile/goodput-measurement/expected.json)
- [cmd/integration/testdata/reconcile/goodput-measurement/input_config.yaml](cmd/integration/testdata/reconcile/goodput-measurement/input_config.yaml)
- [cmd/integration/testdata/reconcile/job/expected.json](cmd/integration/testdata/reconcile/job/expected.json)
- [cmd/integration/testdata/reconcile/workflow-topology-metrics-all-failed/expected.json](cmd/integration/testdata/reconcile/workflow-topology-metrics-all-failed/expected.json)
- [cmd/integration/testdata/reconcile/workflow-topology-metrics/expected.json](cmd/integration/testdata/reconcile/workflow-topology-metrics/expected.json)
- [docs/cli-reference/overview.md](docs/cli-reference/overview.md)
- [docs/getting-started/first-certification.md](docs/getting-started/first-certification.md)
- [docs/getting-started/install.md](docs/getting-started/install.md)
- [pkg/controller/metrics.go](pkg/controller/metrics.go)
- [pkg/controller/metrics_cleanup_test.go](pkg/controller/metrics_cleanup_test.go)

</details>



The NVIDIA Cluster Readiness Engine (NVCRE) employs a robust test pyramid designed to ensure the correctness of its controllers, CLI commands, catalog entries, and deployment artifacts without always requiring a live GPU cluster. The infrastructure spans package-level golden-file unit tests, controller-runtime `envtest` integration suites, Kind and KWOK-simulated User Acceptance Tests (UAT), and static policy guards.

```mermaid
graph TD
    TestPyramid["Test Pyramid"] --> Unit["Golden-File Unit Tests\npkg/testutil.TestCaseParser"]
    TestPyramid --> Integration["Integration Tests\ncmd/integration (envtest)"]
    TestPyramid --> UAT["User Acceptance Tests\ntest/uat (Kind + KWOK)"]
    TestPyramid --> Policy["Policy & Doc Guards\ntest/releasepolicy & test/docspolicy"]

    Unit --> CodePkg["pkg/* packages\n(.yaml input -> .json expected)"]
    Integration --> ReconcileEngine["cmd/integration/testdata/reconcile/\ninput_client_objects.yaml"]
    UAT --> KWOKSim["test/uat/testdata/\nexpected_pods.yaml"]
    Policy --> PolicyFiles["test/releasepolicy/\nWorkflow YAML checks"]

    subclassDef default stroke:#000,stroke-width:1px,fill:none;
```

Sources: [.claude/skills/cre-test/SKILL.md:15-24](), [CLAUDE.md:107-114]()

---

## 8.1 Golden-File Unit Tests and `testutil.TestCaseParser`

NVCRE standardizes structured output verification across core packages using `testutil.TestCaseParser` defined in `[pkg/testutil/]()`. Rather than maintaining inline test assertions or hand-written result tables, test suites define cases as directories containing `input.yaml` (or `input_*.yaml`) and snapshot the expected output into an `expected.json` or `expected.txt` golden file (`[.claude/skills/cre-test/SKILL.md:27-37]`). 

Packages implementing this pattern include `[pkg/catalog/]`, `[pkg/certification/]`, `[pkg/controller/]`, `[pkg/goodput/]`, `[pkg/orchestration/]`, `[pkg/platform/]`, `[pkg/render/]`, `[pkg/report/]`, and `[pkg/workload/]` (`[CLAUDE.md:111-114]()`). Developers can regenerate golden files intentionally using environment variables like `TESTUTIL_UPDATE_EXPECTED=true` (`[CLAUDE.md:31-33]()`).

For full details on authoring test cases, structure conventions, and updating goldens, see [Golden-File Unit Tests and testutil.TestCaseParser](#8.1).

Sources: [.claude/skills/cre-test/SKILL.md:15-56](), [CLAUDE.md:107-114]()

---

## 8.2 Integration Tests (`envtest`)

Integration tests validate the Kubernetes controller reconcilers against a lightweight, real `kube-apiserver` and `etcd` instance provided by controller-runtime's `envtest` harness (`[cmd/integration/]()`) (`[CONTRIBUTING.md:130-132]()`). These suites exercise complex control loops—such as job checkpoint restarts, condition transitions, and metric cardinalities—without needing a physical Kubernetes cluster.

Each integration test case resides in a dedicated directory under `[cmd/integration/testdata/reconcile/]` containing `input_client_objects.yaml`, `input_config.yaml`, and `expected.json` (`[.claude/skills/cre-test/SKILL.md:97-105]()`). The harness supports deterministic pod log injection via the `PodLogFetcher` interface (`[CLAUDE.md:109]()`) using `input_logs_*.txt` files to test log parsers and goodput calculators.

For comprehensive coverage of test execution, harness setup, and memory/garbage collection management across large data corpora, see [Integration Tests (envtest)](#8.2).

Sources: [CLAUDE.md:107-110](), [.claude/skills/cre-test/SKILL.md:97-128]()

---

## 8.3 UAT, Helm and Policy Test Suites

User Acceptance Testing (UAT) and higher-level validation suites ensure that fully rendered manifests and deployment configurations behave correctly in end-to-end environments. UAT tests (`[test/uat/]`) spin up a transient Kind cluster combined with KWOK (Kubernetes WithOut Kubelet) to simulate GPU node pools, validating actual rendered controller output against golden expectations (`[CLAUDE.md:35-64]()`).

Additionally, chart rendering correctness is verified via test/helm suites, while `[test/releasepolicy/]` and `[test/docspolicy/]` guard against drift in release definitions, workflow YAML scripts, and documentation pipelines (`[.claude/skills/cre-test/SKILL.md:23]()`).

```mermaid
graph LR
    MakeTarget["make test-uat"] --> KindCluster["Kind Cluster\n(nvcre-test-uat)"]
    KindCluster --> KWOKSim["KWOK Node Simulator\n(GPU Node Custom Resources)"]
    KWOKSim --> ControllerDeploy["Controller Manager\n(Deployed via Tiltfile)"]
    ControllerDeploy --> UATSuite["test/uat/ Suite\nTestAWSGB200NCCL"]

    subclassDef default stroke:#000,stroke-width:1px,fill:none;
```

Sources: [CLAUDE.md:35-64](), [.claude/skills/cre-test/SKILL.md:23]()

For details on running UAT pipelines, Tilt workflows, Helm chart rendering checks, and policy guards, see [UAT, Helm and Policy Test Suites](#8.3).

---

