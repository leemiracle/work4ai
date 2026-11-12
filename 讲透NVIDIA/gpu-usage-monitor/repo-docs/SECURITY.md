# Security Policy: GPU Usage Monitor

## Reporting a Vulnerability

NVIDIA is dedicated to the security and trust of our software products and services, including all source code repositories managed through our organization.

If you discover a potential security vulnerability, please **do not open a public issue or pull request.** If a potential security issue is inadvertently reported through a public channel, NVIDIA maintainers may limit public discussion and redirect the reporter to the appropriate private disclosure channels.

To report a potential security vulnerability in any NVIDIA product:

- **Web (preferred):** [NVIDIA Vulnerability Disclosure Program](https://www.nvidia.com/en-us/security/) — [Security Vulnerability Submission Form](https://www.nvidia.com/object/submit-security-vulnerability.html)
- **E-Mail:** [psirt@nvidia.com](mailto:psirt@nvidia.com)
  - We encourage you to use the following PGP key for secure email communication: [NVIDIA public PGP Key for communication](https://www.nvidia.com/en-us/security/pgp-key)
- **GitHub:** Use the **Security** tab > **Report a vulnerability** to submit a private report directly on this repository

Please include the following information:

- Product/project name and the chart version or branch that contains the vulnerability
- Type of vulnerability (code execution, denial of service, information disclosure, privilege escalation, etc.)
- Step-by-step instructions to reproduce the vulnerability
- Proof-of-concept or exploit code, if available
- Potential impact of the vulnerability, including how an attacker could exploit it

**Detailed reports help NVIDIA evaluate and address issues faster.**

NVIDIA's PSIRT team will acknowledge receipt, validate severity, develop fixes, and publish security bulletins as appropriate. While NVIDIA currently does not have a bug bounty program, we do offer acknowledgement when an externally reported security issue is addressed under our coordinated vulnerability disclosure policy. Please visit our [Product Security Incident Response Team (PSIRT)](https://www.nvidia.com/en-us/security/psirt-policies/) policies page for more information.

## NVIDIA Product Security

For all security-related concerns, please visit NVIDIA's Product Security portal at https://www.nvidia.com/en-us/security

## Security Architecture & Context

GPU Usage Monitor is a **Helm chart** that deploys a self-contained observability stack for NVIDIA GPU utilization in a Kubernetes cluster. It contains no first-party application code or container images. The repository consists of chart metadata (`Chart.yaml`), operator-facing configuration defaults (`values.yaml`), a single template that publishes two Grafana dashboard definitions as a ConfigMap (`templates/grafana/configmap.yaml`, `dashboards/*.json`), and a release workflow that packages and publishes the chart (`.github/workflows/on-release.yaml`).

This software operates at the **deployment/configuration (Helm chart)** level. Its primary security responsibility is the **security posture of the configuration it hands to the upstream Prometheus and Grafana community subcharts** — specifically the Grafana authentication settings, the Prometheus datasource definition, and the dashboard provisioning configuration. It does not itself process untrusted input at runtime; the runtime attack surface it creates belongs to the components it configures.

**Repository Exposure Classification:** Public.
Basis: origin remote is github.com and the project is Apache-2.0 open source; SECURITY.md written to public-safe detail.

**Service Exposure Classification:** External / Regulated (high confidence).
Basis: externally distributed artifact — the chart is packaged and pushed to a public OCI registry (`ghcr.io/nvidia/gpu-usage-monitor`) by the release workflow, is publicly documented for third-party installation, and is deployed by external consumers as a live in-cluster service.

### Trust Boundaries

- **Chart consumer → chart defaults.** Operators install with `helm install` and inherit `values.yaml` unless they override it. Every default in that file is a security decision made on the consumer's behalf.
- **Client → Grafana.** Grafana is the only user-facing interface. The chart enables anonymous access with the `Viewer` role and sets a GPU dashboard as the default home dashboard. The chart defines no Ingress, so exposure depends entirely on how the operator reaches the Service (`kubectl port-forward` in the documented flow).
- **Grafana → Prometheus.** The provisioned datasource uses `access: proxy`, so Grafana's server-side identity performs metric queries. The target is either the in-chart Prometheus Service or an operator-supplied URL (`global.prometheusUrl`).
- **Prometheus → metric sources.** Prometheus scrapes DCGM Exporter and kube-state-metrics. Both are **external to this chart** — DCGM Exporter is expected from the GPU Operator, and `kube-state-metrics` is disabled by default. Their metric output (pod names, namespaces, node and GPU inventory) is treated as authoritative.
- **Release pipeline → public registry.** The release workflow resolves the Prometheus and Grafana subcharts from upstream chart repositories at build time and publishes the resulting package to a public container registry using the workflow's scoped token.

## Threat Model

The following scenarios represent the primary security concerns for this chart, ordered by severity and likelihood. Each derives from configuration present in this repository.

1. **Published Default Grafana Administrator Credentials:** `values.yaml` ships `grafana.adminUser: admin` and `grafana.adminPassword: admin`, and the README documents the same pair. Any deployment installed without an explicit override runs a Grafana administrator whose credentials are publicly known from this repository.

   Because anonymous access is also enabled by default (threat 2), the two defaults compose into a privilege escalation: a client that reaches the Grafana Service starts as an unauthenticated `Viewer` and can elevate to full `Admin` using the published credentials, with no prior access to the cluster. Administrator capability in Grafana is substantially broader than dashboard access — it includes **creating new datasources pointing at arbitrary internal endpoints**, which turns the server-side datasource proxy into an attacker-controlled request primitive against services the client cannot reach directly (a stronger path than the operator-misconfiguration case in threat 4); **installing plugins**, which introduces attacker-supplied code into the Grafana pod; and modifying or deleting the provisioned dashboards (threat 7).

   Reachability of the Grafana Service is determined by the operator, not by this chart: the documented access path is `kubectl port-forward`, and this chart ships no Ingress and no LoadBalancer Service. Operators who add an Ingress, change the Service type, or run workloads that can reach the Service over the cluster network extend this exposure accordingly.

2. **Unauthenticated Read Access to Cluster Metrics:** `grafana.ini` sets `auth.anonymous.enabled: true` with `org_role: Viewer` and `hide_version: true`. Anyone able to reach the Grafana Service — for example through a Service type change, an operator-added Ingress, or lateral movement from another pod — reads GPU and pod dashboards without authenticating. The dashboards surface cluster inventory such as namespaces, pod names, and GPU model names derived from `kube_pod_info` and `DCGM_FI_DEV_*` series.

3. **Metric Query Reach Beyond the Curated Dashboards:** The Prometheus datasource is provisioned with `access: proxy` and `isDefault: true`. Queries are executed by the Grafana pod rather than the browser, so a client that reaches Grafana can obtain data from a Prometheus instance it has no direct network path to. Combined with anonymous access, the disclosure surface is the full metric set retained by Prometheus, not only the panels shipped in `dashboards/`.

4. **Operator-Supplied Datasource URL Rendered Without Validation:** `global.prometheusUrl` is interpolated verbatim into the datasource `url` field in `values.yaml`. The chart performs no scheme or host validation, so a mistaken or attacker-influenced value directs the Grafana proxy at an arbitrary in-cluster or external endpoint. This turns dashboard rendering into server-side requests toward that endpoint and can redirect the query stream — including cluster topology implied by the queries themselves — off-cluster.

5. **No Transport Security or Network Segmentation Shipped:** The chart defines no TLS configuration, no Ingress, and no NetworkPolicy. Client-to-Grafana traffic (including the administrator login form) and Grafana-to-Prometheus traffic are plain HTTP over the cluster network, and nothing in the chart constrains which workloads may reach the Prometheus or Grafana Services.

6. **Release Pipeline and Subchart Supply Chain:** `.github/workflows/on-release.yaml` runs `helm dependency build` at release time, resolving the Prometheus and Grafana subcharts from upstream community chart repositories, then publishes the package to a public OCI registry. No dependency lock file is committed to the repository, the workflow does not verify subchart provenance, and the published chart is not signed or accompanied by a provenance attestation. Compromise or content drift at an upstream chart repository would be carried into the published artifact, and consumers have no signature to verify what they pull. The package version is taken directly from the release ref without validation.

7. **Mutable Provisioned Dashboards:** The dashboard provider is configured with `editable: true` and `disableDeletion: false`. An authenticated Grafana user with sufficient role — reachable via the default administrator credentials in threat 1 — can modify or delete the provisioned GPU dashboards, or introduce panels that alter what subsequent viewers see and which endpoints the Grafana proxy contacts.

## Critical Security Assumptions

This chart delegates the following to the deploying operator and the surrounding platform. Each is something the chart does **not** enforce:

- **Assumes the operator replaces the default Grafana credentials before any exposure.** The chart neither generates a random administrator password nor fails installation when the shipped defaults are left in place.
- **Assumes access to the Grafana Service is restricted by the cluster.** The documented access path is `kubectl port-forward`, so the chart relies on Kubernetes RBAC governing that verb; it ships no Ingress, no authentication proxy, and no NetworkPolicy.
- **Assumes the cluster network is trusted.** There is no TLS configuration between components and no expectation of a service mesh, so confidentiality of dashboard traffic and administrator credentials in transit is assumed to be provided by the platform or by the port-forward tunnel.
- **Assumes GPU and pod metadata is not sensitive in the deploying environment.** Anonymous `Viewer` access is enabled by default, which is only appropriate where namespace names, pod names, node inventory, and GPU model information are acceptable to disclose to anyone who can reach the service.
- **Assumes Kubernetes Secret access is appropriately restricted.** The Grafana administrator password supplied through chart values is rendered into a Kubernetes Secret and is readable by any principal with secret-read permission in the release namespace.
- **Assumes DCGM Exporter and kube-state-metrics are correctly deployed and trustworthy.** Neither is installed by this chart; DCGM Exporter is expected from the GPU Operator and `kube-state-metrics` is disabled by default. Their metric output is consumed as authoritative and is not validated.
- **Assumes the upstream Prometheus and Grafana community charts and their referenced container images are trustworthy and kept patched.** Subchart versions are pinned in `Chart.yaml`, and this repository performs no automated dependency update or vulnerability scanning; consumers are responsible for tracking advisories in the bundled components.
- **Assumes Kubernetes enforces pod and namespace isolation.** The chart sets no pod- or container-level security context beyond upstream subchart defaults and relies on the platform's admission and isolation controls.

## Hardening Recommendations for Operators

Deployments reachable beyond a local `port-forward` should at minimum:

- Override `grafana.adminUser` and `grafana.adminPassword`, or supply an existing Secret through the Grafana subchart's `admin.existingSecret` value.
- Disable anonymous access unless unauthenticated read is an accepted decision for the environment:

  ```yaml
  grafana:
    grafana.ini:
      auth.anonymous:
        enabled: false
  ```

- Terminate TLS in front of Grafana and restrict reachability with a NetworkPolicy scoped to the release namespace.
- Set `global.prometheusUrl` only to a known in-cluster Prometheus endpoint.
- Track security advisories for the pinned Prometheus and Grafana subchart versions and update deliberately.

## Scope

**In scope:** the chart templates, default values, dashboard definitions, and the release workflow contained in this repository.

**Out of scope:** vulnerabilities in the upstream Prometheus and Grafana charts or their container images (report those to their respective projects), in NVIDIA DCGM Exporter (see the [dcgm-exporter](https://github.com/NVIDIA/dcgm-exporter) repository), in kube-state-metrics, or in Kubernetes itself. Misconfiguration introduced by an operator's own values overrides is also out of scope, though reports of insecure defaults shipped by this chart are welcome.
