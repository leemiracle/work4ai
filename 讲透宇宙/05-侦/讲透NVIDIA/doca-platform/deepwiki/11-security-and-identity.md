<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/doca-platform · page 11 Security and Identity · fetched 2026-10-26 -->

# Security and Identity

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/public/advanced-configuration/per-dpu-bmc-credentials.md](docs/public/advanced-configuration/per-dpu-bmc-credentials.md)
- [internal/operator/controllers/spiffe_validation_test.go](internal/operator/controllers/spiffe_validation_test.go)
- [internal/provisioning/controllers/dpu/state/prepare_bfb_subject_test.go](internal/provisioning/controllers/dpu/state/prepare_bfb_subject_test.go)
- [internal/provisioning/controllers/dpu/state/rebooting_test.go](internal/provisioning/controllers/dpu/state/rebooting_test.go)
- [internal/provisioning/controllers/dpu/state/redfish/client/client.go](internal/provisioning/controllers/dpu/state/redfish/client/client.go)
- [internal/provisioning/controllers/dpu/state/redfish/diag/diag.go](internal/provisioning/controllers/dpu/state/redfish/diag/diag.go)
- [internal/provisioning/controllers/dpu/state/redfish/diag/diag_test.go](internal/provisioning/controllers/dpu/state/redfish/diag/diag_test.go)
- [internal/provisioning/controllers/dpu/state/redfish/firmware_update.go](internal/provisioning/controllers/dpu/state/redfish/firmware_update.go)
- [internal/provisioning/controllers/dpu/state/redfish/firmware_update_test.go](internal/provisioning/controllers/dpu/state/redfish/firmware_update_test.go)
- [internal/provisioning/controllers/dpu/state/redfish/installing.go](internal/provisioning/controllers/dpu/state/redfish/installing.go)
- [internal/provisioning/controllers/dpu/state/redfish/installing_test.go](internal/provisioning/controllers/dpu/state/redfish/installing_test.go)
- [internal/provisioning/controllers/dpu/state/redfish/mock/redfish.go](internal/provisioning/controllers/dpu/state/redfish/mock/redfish.go)
- [internal/provisioning/controllers/dpu/state/redfish/mock/redfish_test.go](internal/provisioning/controllers/dpu/state/redfish/mock/redfish_test.go)
- [internal/provisioning/controllers/dpu/util/reboot_helpers.go](internal/provisioning/controllers/dpu/util/reboot_helpers.go)
- [internal/provisioning/controllers/dpudevice/dpudevice_controller.go](internal/provisioning/controllers/dpudevice/dpudevice_controller.go)
- [internal/provisioning/controllers/dpudevice/dpudevice_controller_test.go](internal/provisioning/controllers/dpudevice/dpudevice_controller_test.go)
- [internal/provisioning/controllers/dpudevice/dpudevice_spiffe_envtest_test.go](internal/provisioning/controllers/dpudevice/dpudevice_spiffe_envtest_test.go)
- [internal/provisioning/controllers/dpudevice/spiffe_entry.go](internal/provisioning/controllers/dpudevice/spiffe_entry.go)
- [internal/provisioning/controllers/dpudevice/spiffe_entry_test.go](internal/provisioning/controllers/dpudevice/spiffe_entry_test.go)

</details>



The DOCA Platform Framework (DPF) implements a robust security architecture designed to support both host-trusted and zero-trust deployment models. This architecture ensures that DPU agents are cryptographically identified, BMC communications are secured via mTLS and unique credentials, and diagnostic tools provide secure visibility into the fleet.

## SPIFFE/SPIRE Identity Framework

DPF leverages the SPIFFE (Secure Production Identity Framework for Everyone) standard to provide automated, rotation-capable identities to DPU agents. This framework ensures that only authenticated DPUs can communicate with the management cluster and participate in service orchestration.

*   **Workload Identity**: Each DPU agent receives a SPIFFE ID based on its hardware identity (e.g., serial number).
*   **Trust Domain**: The system manages a SPIRE server that issues SVIDs (SPIFFE Verifiable Identity Documents) to DPU workloads.
*   **Identity Lifecycle**: The `DPUDeviceReconciler` manages the lifecycle of `ClusterStaticEntry` resources, ensuring identities are provisioned during onboarding and deregistered during deletion `[internal/provisioning/controllers/dpudevice/dpudevice_controller.go:146-155]()`.

For details, see [SPIFFE/SPIRE Identity Framework](#11.1).

## BMC Credential Management and DPU Discovery

Secure management of Baseboard Management Controller (BMC) access is critical for out-of-band DPU lifecycle operations like OS installation and firmware updates.

*   **Credential Resolution**: DPF supports both a global shared password (`bmc-shared-password`) and per-device BMC credentials stored as Kubernetes Secrets `[internal/provisioning/controllers/dpu/state/redfish/client/client.go:126-128]()`.
*   **Per-DPU Credentials**: The `DPUDevice` spec allows referencing a unique secret via `spec.bmcCredentialSecretName`, which DPF uses for all managed accounts including `root` (BF3), `admin` (BF4), and the `service` account `[docs/public/advanced-configuration/per-dpu-bmc-credentials.md:7-32]()`.
*   **mTLS Communication**: Redfish communication with the BMC is secured using mTLS. DPF manages the CA and client certificates through `cert-manager`, including automated rotation of BMC server certificates `[internal/provisioning/controllers/dpudevice/dpudevice_controller.go:78-90]()`.
*   **DPUDiscovery Crawler**: An automated component that crawls the network to discover DPU devices and register them as `DPUDevice` resources in the management cluster.

For details, see [BMC Credential Management and DPU Discovery](#11.2).

### BMC Security Context and Identity Flow

The following diagram illustrates how the `DPU` controller and `DPUDevice` controller interact with security entities to establish secure communication.

| Diagram: BMC Security Context |
| :--- |
| ```mermaid
graph TD
    subgraph "K8s_Management_Cluster"
        [DPU_CR]
        [DPUDevice_CR]
        [Secret_dpf-ca-trust-bundle]
        [Secret_dpf-provisioning-redfish-client-secret]
        [Secret_bmc-shared-password]
    end

    subgraph "Provisioning_Controller"
        NewTLSClient["rc.NewTLSClient()"]
        DPUDeviceReconciler["DPUDeviceReconciler"]
        CertManager["cert-manager.io/v1 CertificateRequest"]
    end

    subgraph "DPU_Hardware"
        BMC["BMC (Redfish API)"]
    end

    [DPU_CR] -->|Ref| [DPUDevice_CR]
    [DPUDevice_CR] -->|Address| NewTLSClient
    [Secret_dpf-ca-trust-bundle] -->|Trust_Bundle| NewTLSClient
    [Secret_dpf-provisioning-redfish-client-secret] -->|Client_Cert| NewTLSClient
    [Secret_bmc-shared-password] -->|Fallback_Auth| NewTLSClient
    
    DPUDeviceReconciler -->|Rotates_Cert| CertManager
    CertManager -->|Issues| BMC
    NewTLSClient -->|mTLS_HTTPS| BMC
``` |
**Sources:** `[internal/provisioning/controllers/dpu/state/redfish/client/client.go:88-118]()`, `[internal/provisioning/controllers/dpudevice/dpudevice_controller.go:102-120]()`, `[docs/public/advanced-configuration/per-dpu-bmc-credentials.md:12-22]()`

## Zero-Trust Authentication

In zero-trust mode, the framework assumes the host environment is potentially compromised. Security is enforced through:

*   **Host Isolation**: Disabling host-side RShim interfaces via Redfish to prevent the host from interfering with the DPU's internal management.
*   **Restricted Privileges**: For BlueField-4 devices, the controller sets host privileges to `Restricted` via the `APIHostPrivilegeConfigSettings` endpoint to limit host access to DPU hardware resources `[internal/provisioning/controllers/dpu/state/redfish/client/client.go:103-104]()`.
*   **Agent-Side Enforcement**: The DPU agent operates independently of the host, reporting status and receiving configuration only after successful SPIFFE-based authentication.

### Hardware Hardening Logic

This diagram shows the code entities involved in hardening a DPU during the provisioning lifecycle.

| Diagram: Hardware Hardening Logic |
| :--- |
| ```mermaid
graph LR
    subgraph "Provisioning_Logic"
        Installing["Installing()"]
        FirmwareUpdate["FirmwareUpdate()"]
    end

    subgraph "Redfish_Operations"
        APIHostPrivilege["APIHostPrivilegeConfigSettings"]
        APIDisableHostRshim["APIDisableHostRshim"]
        APISecureBoot["APISecureBoot"]
    end

    Installing -->|Check_Type| DPUType{DPUType}
    DPUType -- "BF4" --> APIHostPrivilege
    DPUType -- "BF3" --> APIDisableHostRshim
    
    FirmwareUpdate -->|Verify_Versions| CheckVersions["checkFirmwareVersions()"]
    CheckVersions -->|mTLS| BMC["BMC_FirmwareInventory"]
``` |
**Sources:** `[internal/provisioning/controllers/dpu/state/redfish/installing.go:88-98]()`, `[internal/provisioning/controllers/dpu/state/redfish/firmware_update.go:108-140]()`, `[internal/provisioning/controllers/dpu/state/redfish/client/client.go:74-92]()`

## dpfctl Diagnostic Tooling

`dpfctl` is the primary CLI tool for diagnosing the health and security state of the DPU fleet. It provides visibility into the complex relationship between physical hardware, Kubernetes resources, and security conditions.

*   **Describe**: Provides a tree-view of resources, showing how a `DPUSet` relates to individual `DPU` and `DPUDevice` objects.
*   **SOS Report**: Collects comprehensive logs and state information from both the management cluster and the DPU clusters for troubleshooting.
*   **Condition Reporting**: Aggregates security and operational conditions (e.g., `OSInstalled`, `FwBundleUpdated`, `Rebooted`) into a human-readable format `[internal/provisioning/controllers/dpu/state/redfish/installing.go:126-132]()`, `[internal/provisioning/controllers/dpu/state/redfish/firmware_update.go:147-148]()`.

For details, see [dpfctl Diagnostic Tooling](#11.3).

## Summary Table: Security Components

| Component | Responsibility | Relevant Code / CRDs |
| :--- | :--- | :--- |
| **Redfish Client** | Secure out-of-band management via BMC mTLS | `rc.Client`, `DPUDevice` |
| **SPIFFE Entry** | Cryptographic identity for DPU agents | `ClusterStaticEntry`, `DPUDevice` |
| **Firmware Controller** | Enforcement of secure firmware versions | `FirmwareUpdate()`, `BlueFieldSoftware` |
| **Reboot Handler** | Secure power-cycling of DPUs via HostAgent or Redfish | `StartRebooting()`, `DPUNode` |
| **Credential Manager** | Per-DPU BMC password rotation and storage | `BMCCredentialsReady`, `Secret` |

**Sources:** `[internal/provisioning/controllers/dpu/state/redfish/client/client.go:88-118]()`, `[internal/provisioning/controllers/dpudevice/dpudevice_controller.go:146-166]()`, `[internal/provisioning/controllers/dpu/state/redfish/firmware_update.go:45-73]()`, `[internal/provisioning/controllers/dpu/util/reboot_helpers.go:35-60]()`, `[docs/public/advanced-configuration/per-dpu-bmc-credentials.md:144-155]()`

---

