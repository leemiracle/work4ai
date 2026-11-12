# Calibro Node Profile

## Scope

This document defines Calibro's public, scheduler-neutral profile for a host
node: a physical or virtual machine that supplies the environment for a
benchmark or experiment. It describes the observable hardware and host software
facts needed to compare results, reproduce an environment, and diagnose
unexpected behavior.

This is a documentation profile, not source code or a complete schema
reference. It includes host inventory and SBOM evidence, but excludes
scheduler-specific node context, microbenchmarks, runtime telemetry, collector
implementation, test fixtures, and command output.

## Collection and handling rules

- The collection command shown for each field is guidance for obtaining a value;
  it is not a requirement to use a particular collector.
- Collectors must preserve the declared unit and must not guess inaccessible
  values. Follow the field note when it specifies `unknown`, an empty value, or
  omission.
- Treat host names, serial numbers, IP addresses, environment variables, and
  process snapshots as potentially sensitive. Apply the applicable redaction
  policy before a result leaves the host.
- Node identity is captured when the node is selected for execution. SBOM
  evidence is collected before the workload runs. All other fields are captured
  at the environment-snapshot phase unless this document states otherwise.

## Host identity and baseboard

Node identity scopes the rest of the inventory to one observed host. Baseboard
facts distinguish otherwise similar CPU and accelerator configurations.

| Field | Type / unit | Required | Collection source | Command / method | Notes |
| --- | --- | --- | --- | --- | --- |
| `node_id` | string | Yes | Collector | Stable local node identifier scoped to the result | Capture when the node is selected for execution. Use a stable identifier that is meaningful only within the result. |
| `hostname` | string | No | Host OS | `hostname --fqdn` or `hostname` | Capture when the node is selected for execution. Redact or pseudonymize when host names are sensitive. |
| `system_vendor` | string | Yes | SMBIOS/DMI | `dmidecode -s system-manufacturer` | Requires root on many hosts; use `unknown` if unavailable. |
| `system_product_name` | string | Yes | SMBIOS/DMI | `dmidecode -s system-product-name` | Captures OEM/platform model. |
| `system_version` | string | No | SMBIOS/DMI | `dmidecode -s system-version` | May be empty on some platforms. |
| `baseboard_manufacturer` | string | Yes | SMBIOS/DMI | `dmidecode -s baseboard-manufacturer` | Use `unknown` if unavailable. |
| `baseboard_product_name` | string | Yes | SMBIOS/DMI | `dmidecode -s baseboard-product-name` | Use `unknown` if unavailable. |
| `baseboard_version` | string | No | SMBIOS/DMI | `dmidecode -s baseboard-version` | Board revision when exposed. |
| `chassis_type` | string | No | SMBIOS/DMI | `dmidecode -s chassis-type` | Chassis category when exposed. |

## CPU and memory

Represent CPU facts per package when socket topology is available; a
single-socket or lower-fidelity collector may emit one aggregate CPU record.

| Field | Type / unit | Required | Collection source | Command / method | Notes |
| --- | --- | --- | --- | --- | --- |
| `cpu_id` | string | Yes | `/proc/cpuinfo` / sysfs | `lscpu --json or /sys/devices/system/cpu topology` | Stable CPU package identifier scoped to the node. |
| `socket_index` | int | No | `/proc/cpuinfo` / sysfs | `lscpu --json or /sys/devices/system/cpu topology` | Physical socket/package index when exposed. |
| `numa_node_ids` | array of int | No | sysfs | `ls /sys/devices/system/node/node*/cpulist` | NUMA nodes associated with this CPU package. |
| `cpu_model` | string | Yes | `/proc/cpuinfo` | `lscpu \| grep 'Model name'` | Full model name. |
| `cpu_architecture` | string | Yes | `/proc/cpuinfo` | `lscpu \| grep 'Architecture'` | Architecture such as x86_64 or aarch64. |
| `cpu_vendor` | string | Yes | `/proc/cpuinfo` / lscpu | `lscpu \| grep 'Vendor ID'` or `cat /proc/cpuinfo \| grep vendor_id \| head -1` | Use `unknown` if not exposed. |
| `cpu_cpuid_signature` | string | If x86 | CPUID | `cpuid -1 -r \| grep '0x00000001'` → EAX | Normalize as an 8-character uppercase hexadecimal string without `0x`. |
| `cpu_family` | int | If x86 | `/proc/cpuinfo` / lscpu | `lscpu \| grep 'CPU family'` or `cat /proc/cpuinfo \| grep 'cpu family' \| head -1` | x86/x86_64 only. |
| `cpu_model_id` | int | If x86 | `/proc/cpuinfo` / lscpu | `lscpu \| grep '^Model:'` or `cat /proc/cpuinfo \| grep '^model[[:space:]]*:' \| head -1` | Numeric CPUID model, not model name. |
| `cpu_stepping` | int | If x86 | `/proc/cpuinfo` / lscpu | `lscpu \| grep 'Stepping'` or `cat /proc/cpuinfo \| grep stepping \| head -1` | x86/x86_64 only. |
| `cpu_silicon_revision` | string | No | SMBIOS/DMI / vendor tools | `dmidecode -t processor \| grep -E 'Signature:\|Version:'` | Optional vendor-specific revision string. |
| `cpu_sockets` | int | No | `/proc/cpuinfo` | `lscpu \| grep 'Socket(s)'` | Number of physical sockets represented by this record. |
| `cpu_cores_per_socket` | int | Yes | `/proc/cpuinfo` | `lscpu \| grep 'Core(s) per socket'` | Physical cores per socket. |
| `cpu_threads_per_core` | int | Yes | `/proc/cpuinfo` | `lscpu \| grep 'Thread(s) per core'` | Hardware-threading factor. |
| `cpu_vcpu_total` | int | Yes | `/proc/cpuinfo` | `nproc --all` | Sockets × cores per socket × threads per core. |
| `cpu_cores_allocated` | int | Yes | Scheduler / cgroup / OS | `SLURM_CPUS_PER_TASK * SLURM_NTASKS` (Slurm), K8s resource requests, cgroup `cpu.max`/`cpuset.cpus`, or `nproc` | Cores visible to or allocated for the execution. |
| `cpu_max_frequency` | float / MHz | No | `/proc/cpuinfo` | `lscpu \| grep 'CPU max MHz'` | Maximum CPU frequency. |
| `cpu_numa_nodes` | int | No | `/proc/cpuinfo` | `lscpu \| grep 'NUMA node(s)'` | Number of NUMA nodes. |
| `cpu_numa_nodes_allocated` | array of int | If `cpu_sockets` > 1 | cgroup, sysfs | `numactl --show \| grep 'nodebind'` (works in both Slurm and K8s — reads cgroup CPU affinity); K8s: parse `/sys/fs/cgroup/cpuset/cpuset.cpus` and map to NUMA nodes via `/sys/devices/system/node/nodeN/cpulist`; Slurm: same via `taskset -p $$` or `SLURM_CPU_BIND` | Deduplicated NUMA node IDs for allocated cores. |
| `cpu_cache_l1d` | int / KiB | No | `/proc/cpuinfo` | `lscpu \| grep 'L1d cache'` | L1 data cache per core. |
| `cpu_cache_l1i` | int / KiB | No | `/proc/cpuinfo` | `lscpu \| grep 'L1i cache'` | L1 instruction cache per core. |
| `cpu_cache_l2` | int / KiB | No | `/proc/cpuinfo` | `lscpu \| grep 'L2 cache'` | L2 cache per core. |
| `cpu_cache_l3` | int / MiB | Yes | `/proc/cpuinfo` | `lscpu \| grep 'L3 cache'` | Shared L3 cache. |
| `cpu_tdp` | int / W | No | Vendor power/TDP source | Vendor-specific tools or platform inventory that reports thermal design power in watts | Do **not** derive from `dmidecode` `Max Speed`; that is frequency, not TDP. |
| `cpu_flags` | string | No | `/proc/cpuinfo` | `lscpu \| grep 'Flags'` or `cat /proc/cpuinfo \| grep flags \| head -1` | CPU feature flags. |
| `cpu_microcode` | string | No | `/proc/cpuinfo` | `cat /proc/cpuinfo \| grep microcode \| head -1` | Microcode revision. |
| `cpu_scaling_driver` | string | Yes | sysfs | `cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_driver` | Per-policy on heterogeneous systems; use `unknown` if not exposed. |
| `cpu_scaling_governor` | string | Yes | sysfs | `cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor` | Repeat per policy if needed. |
| `cpu_turbo_enabled` | bool | Yes | sysfs / firmware | Intel: `/sys/devices/system/cpu/intel_pstate/no_turbo` (0=on); AMD: `amd_pstate` attributes; Arm: platform-specific | `false` if boost is disabled or unknown. |
| `cpu_max_frequency_by_core_group_mhz` | string (JSON) | No | `/sys/devices/system/cpu`, `lscpu` | Parse per-CPU `cpufreq/cpuinfo_max_freq` grouped by core type, or tool-specific topology report | JSON array or map; omit or use `[]` when `cpu_max_frequency` is sufficient. |
| `cpu_frequency_policy_attributes` | string (JSON) | No | sysfs | Dump relevant files under `/sys/devices/system/cpu/cpufreq/policy*` (e.g. `energy_performance_preference`, `energy_perf_bias`) | JSON object; keys vary by driver. |
| `cpu_idle_state_config` | string (JSON) | No | sysfs | `ls /sys/devices/system/cpu/cpu0/cpuidle/state*` → `name`, `disable` per state | JSON array of state names and enabled status. |
| `cpu_hardware_prefetcher_config` | string (JSON) | No | MSR / vendor tools | e.g. `msr-tools`, vendor tuning CLIs where permitted | Often requires root; may be empty. |
| `cpu_cve_mitigation_status` | map<string, string> | Yes | sysfs | `cat /sys/devices/system/cpu/vulnerabilities/*` | Use an empty map when no vulnerability interface is exposed. |
| `ram_total` | int / MiB | Yes | `/proc/meminfo` | `cat /proc/meminfo \| grep MemTotal` | Convert to MiB. |
| `ram_allocated` | int / MiB | Yes | Scheduler / cgroup / OS | K8s resource requests/limits, Slurm `--mem`, cgroup `memory.max`, or `/proc/meminfo` | Memory visible to or allocated for the execution. |
| `ram_type` | string | Yes | dmidecode | `dmidecode -t memory \| grep Type:` | Requires root. |
| `ram_frequency` | int / MHz | Yes | dmidecode | `dmidecode -t memory \| grep Speed:` | Requires root. |
| `ram_channels` | int | No | dmidecode | `dmidecode -t memory` → count populated DIMMs by locator | Requires root. |
| `ram_dimms_per_channel` | int | No | dmidecode | `dmidecode -t memory` → DIMMs per channel from locator topology | Requires root. |
| `hugepages_total` | int | No | `/proc/meminfo` | `cat /proc/meminfo \| grep HugePages_Total` | Configured hugepages. |
| `hugepage_size` | int / KiB | No | `/proc/meminfo` | `cat /proc/meminfo \| grep Hugepagesize` | Convert to KiB. |
| `ram_transparent_hugepages_mode` | string | Yes | sysfs | `cat /sys/kernel/mm/transparent_hugepage/enabled` | Parse `[never]`, `[madvise]`, or `[always]`; use `unknown` if unreadable. |
| `ram_automatic_numa_balancing_enabled` | bool | Yes | sysctl | `sysctl -n kernel.numa_balancing` → `0`/`1` | Most relevant when there is more than one NUMA node. |
| `ram_dimms` | string (JSON) | Yes | dmidecode | `dmidecode -t memory` → JSON array of DIMM records (Type, Speed, Size, Manufacturer, Part Number, Serial Number, Locator, Bank Locator, etc.); normalize capacity to `size_mib` and preserve original DMI text as `size_raw` | Requires root; redact serial if policy requires. |
| `ram_channel_topology` | string (JSON) | No | dmidecode / collector | Derive channel map from DMI locators, bank locator channel strings, or NUMA distance tables | Omit when DMI exposes only generic slot names. |

## GPUs and topology

GPU facts are per visible or allocated accelerator. Topology describes the
interconnect among those accelerators and their relation to host NUMA nodes.

| Field | Type / unit | Required | Collection source | Command / method | Notes |
| --- | --- | --- | --- | --- | --- |
| `gpu_model` | string | Yes | nvidia-smi | `nvidia-smi -q -x` → `<product_name>` | Single XML query provides most GPU fields. |
| `gpu_count` | int | Yes | nvidia-smi | `nvidia-smi -q -x` → count of `<gpu>` elements | Or `CUDA_VISIBLE_DEVICES` length. |
| `gpu_memory_total` | int / MiB | Yes | nvidia-smi | `nvidia-smi -q -x` → `<fb_memory_usage><total>` |  |
| `gpu_uuid` | string | Yes | nvidia-smi | `nvidia-smi -q -x` → `<uuid>` | Treat as an identifier. |
| `gpu_serial` | string | No | nvidia-smi | `nvidia-smi -q -x` → `<serial>` | May require root; treat as sensitive. |
| `gpu_pci_bus_id` | string | No | nvidia-smi | `nvidia-smi -q -x` → `<pci><pci_bus_id>` |  |
| `gpu_tgp` | int / W | Yes | nvidia-smi | `nvidia-smi -q -x` → `<power_readings><max_power_limit>` | Board power limit. |
| `gpu_clock_max_sm` | int / MHz | Yes | nvidia-smi | `nvidia-smi -q -x` → `<max_clocks><graphics_clock>` |  |
| `gpu_clock_max_mem` | int / MHz | Yes | nvidia-smi | `nvidia-smi -q -x` → `<max_clocks><mem_clock>` |  |
| `gpu_ecc_mode` | bool | Yes | nvidia-smi | `nvidia-smi -q -x` → `<ecc_mode><current_ecc>` | Enabled → `true`. |
| `gpu_mig_mode` | string | No | nvidia-smi | `nvidia-smi -q -x` → `<mig_mode><current_mig>` | Partitioning state. |
| `gpu_persistence_mode` | string | No | nvidia-smi | `nvidia-smi -q -x` → `<persistence_mode>` |  |
| `gpu_compute_mode` | string | No | nvidia-smi | `nvidia-smi -q -x` → `<compute_mode>` |  |
| `gpu_vbios_version` | string | No | nvidia-smi | `nvidia-smi -q -x` → `<vbios_version>` |  |
| `gpu_topology_matrix` | string (JSON) | Yes | nvidia-smi | `nvidia-smi topo -m` | Parse matrix output to JSON. |
| `nvlink_version` | int | Yes | nvidia-smi | `nvidia-smi nvlink -s` → NVLink version |  |
| `nvlink_link_count` | int | Yes | nvidia-smi | `nvidia-smi nvlink -s` → count active links per GPU |  |
| `nvswitch_present` | bool | Yes | nvidia-smi | `nvidia-smi topo -m` → check for NVSwitch in topology |  |
| `pcie_generation` | int | Yes | nvidia-smi / lspci | `nvidia-smi -q -x` → `<pci><pci_gpu_link_info><link_gen>` or `lspci -vvv` |  |
| `pcie_width` | int / lanes | Yes | nvidia-smi / lspci | `nvidia-smi -q -x` → `<pci><pci_gpu_link_info><link_width>` |  |
| `gpu_numa_node` | int | If `cpu_sockets` > 1 | nvidia-smi / sysfs | `nvidia-smi topo -m` → NUMA Affinity column, or `cat /sys/bus/pci/devices/<pci_bus_id>/numa_node` | `-1` means no affinity. |

## Network and storage

Network fields are per interface and storage fields are per volume. Focus on
interfaces and volumes relevant to the workload; do not publish IP addresses or
device identifiers where policy forbids it.

| Field | Type / unit | Required | Collection source | Command / method | Notes |
| --- | --- | --- | --- | --- | --- |
| `nic_name` | string | Yes | System | `ip link show` or `ls /sys/class/net/` | Per-interface. |
| `nic_model` | string | Yes | lspci | `lspci \| grep -i ethernet` or `lspci \| grep -i infiniband` |  |
| `nic_firmware` | string | No | ethtool | `ethtool -i <iface> \| grep firmware` |  |
| `nic_speed` | int / Gb/s | Yes | ethtool | `ethtool <iface> \| grep Speed` | Parse a numeric value in Gb/s. |
| `nic_mtu` | int / bytes | Yes | ip / sysfs | `ip link show <iface>` → mtu field, or `cat /sys/class/net/<iface>/mtu` |  |
| `nic_queue_length` | int | No | sysfs | `cat /sys/class/net/<iface>/tx_queue_len` |  |
| `nic_bond_mode` | string | No | `/proc/net/bonding` | `cat /proc/net/bonding/<bond>` → Bonding Mode | Only for bonded interfaces. |
| `nic_bond_members` | array of string | No | `/proc/net/bonding` | `cat /proc/net/bonding/<bond>` → Slave Interface lines |  |
| `rdma_available` | bool | Yes | ibstat / rdma | `ibstat` or `rdma link show` | `true` if any InfiniBand or RoCE device is present. |
| `ib_port_state` | string | If RDMA | ibstat | `ibstat \| grep State` |  |
| `ib_link_layer` | string | If RDMA | ibstat | `ibstat \| grep 'Link layer'` | InfiniBand or Ethernet (RoCE). |
| `gdr_support` | bool | Yes | nvidia-peermem | `lsmod \| grep nvidia_peermem` | Module present → `true`. |
| `nccl_net_plugin` | string | No | NCCL env / runtime | `NCCL_NET` env var or NCCL debug output |  |
| `nic_irq_cpu_affinity` | string | Yes | proc / irqbalance | `/proc/interrupts` + `grep <iface> /proc/irq/*/smp_affinity_list` or irqbalance debug | Per-interface CPU affinity. |
| `nic_receive_packet_steering_cpumask` | string | Yes | sysfs | `cat /sys/class/net/<iface>/queues/rx-*/rps_cpus` | Hex mask per queue; aggregate in JSON if needed. |
| `nic_transmit_packet_steering_cpumask` | string | Yes | sysfs | `cat /sys/class/net/<iface>/queues/tx-*/xps_cpus` | Same. |
| `nic_numa_node` | int | If `cpu_sockets` > 1 | sysfs | `cat /sys/class/net/<iface>/device/numa_node` | `-1` means no affinity. |
| `nic_ip_addresses` | array of string / CIDR | No | ip | `ip -j addr show <iface>` → `addr_info[].local/prefixlen` for `inet` and `inet6` | Treat captured addresses as sensitive. |
| `storage_mount_path` | string | If storage used | df / mount | `df -h` or `mount \| grep <path>` | Per-volume mount point. |
| `filesystem_type` | string | No | df | `df -T <path>` |  |
| `storage_device_type` | string | If storage used | lsblk | `lsblk -d -o NAME,ROTA,TRAN` |  |
| `storage_device_model` | string | No | lsblk / sysfs | `lsblk -d -o NAME,MODEL` or `cat /sys/block/<dev>/device/model` | Local storage only. |
| `storage_capacity` | int / GiB | No | df | `df -BG <path> \| awk 'NR==2{print $4}'` | Available capacity. |
| `storage_pcie_link_generation` | int | If storage used | lspci / sysfs | `lspci -vv -s <bdf>` → LnkSta / LnkCap; or `nvme id-ctrl` / `smartctl` for NVMe link speed | Map GT/s to generation if needed. |
| `storage_pcie_link_width_lanes` | int / lanes | If storage used | lspci / sysfs | `lspci -vv -s <bdf>` → Width x4 etc. |  |
| `storage_pcie_max_link_generation` | int | If storage used | lspci | `lspci -vv -s <bdf>` → LnkCap max speed |  |
| `storage_pcie_max_link_width_lanes` | int / lanes | If storage used | lspci | `LnkCap` width |  |
| `storage_device_queue_depth` | int | If storage used | sysfs | `cat /sys/block/<dev>/queue/nr_requests` or NVMe `queue_count` / sysfs | Transport-dependent. |

## Operating system, platform, and drivers

These fields capture the host software and firmware state that can change the
behavior of the same workload on otherwise identical hardware.

| Field | Type / unit | Required | Collection source | Command / method | Notes |
| --- | --- | --- | --- | --- | --- |
| `os_name` | string | Yes | `/etc/os-release` | `grep '^NAME=' /etc/os-release` | Distribution name. |
| `os_version` | string | Yes | `/etc/os-release` | `grep '^VERSION_ID=' /etc/os-release` | Distribution version. |
| `kernel_version` | string | Yes | uname | `uname -r` |  |
| `kernel_cmdline` | string | No | `/proc/cmdline` | `cat /proc/cmdline` | May include IOMMU, hugepage, and NUMA settings. |
| `kernel_sysctl_net` | map<string, string> | Yes | sysctl | `sysctl -a` filtered to `net.` prefix, or explicit keys (e.g. `net.core.rmem_max`, `net.ipv4.tcp_rmem`) | Key is the dotted name; value is a string. |
| `bios_version` | string | No | dmidecode | `dmidecode -s bios-version` | Requires root. |
| `bmc_firmware_version` | string | No | ipmitool | `ipmitool mc info \| grep 'Firmware Revision'` | Requires IPMI access. |
| `bios_settings` | map<string, string> | No | dmidecode / vendor tools | Vendor-specific (e.g., `syscfg` for Supermicro, `sum` for Intel) | Requires root; use an empty map when unavailable. |
| `platform_irq_balance_enabled` | bool | Yes | systemd / ps | `systemctl is-active irqbalance` or `ps -C irqbalance` | `false` if inactive. |
| `platform_process_snapshot` | string (JSON) | No | ps / proc | `ps aux --sort=-%cpu \| head -n 20` parsed to JSON | Snapshot only; redact command lines and PIDs as needed. |
| `nvidia_driver_version` | string | Yes | nvidia-smi | `nvidia-smi -q -x` → `<driver_version>` |  |
| `cuda_version` | string | Yes | nvidia-smi | `nvidia-smi -q -x` → `<cuda_version>` | Runtime version. |
| `cuda_toolkit_version` | string | No | nvcc | `nvcc --version` | Build/toolkit version. |
| `cudnn_version` | string | No | Library inspection | `python -c "import torch; print(torch.backends.cudnn.version())"` or inspect library headers |  |
| `nccl_version` | string | Yes | Library inspection | `python -c "import torch; print(torch.cuda.nccl.version())"` or NCCL debug output |  |
| `nvidia_fabricmanager_version` | string | No | systemctl / nv-fabricmanager | `nv-fabricmanager --version` or `systemctl status nvidia-fabricmanager` | Only with NVSwitch. |
| `nvidia_peermem_loaded` | bool | No | lsmod | `lsmod \| grep nvidia_peermem` | Module present → `true`. |
| `nvidia_container_toolkit_version` | string | No | nvidia-ctk | `nvidia-ctk --version` |  |

## Host-wide environment

`Node.environment` records only variables that are declared to apply across
workload processes on the host. It is separate from container image, scheduler,
and entrypoint environment layers.

| Field | Type / unit | Required | Collection source | Command / method | Notes |
| --- | --- | --- | --- | --- | --- |
| `Node.environment` | map<string, string> | No | Declared host-wide node environment | `env` or `printenv` from the collector process when it was launched from the declared node-wide environment; otherwise `tr '\0' '\n' < /proc/<pid>/environ` for the host process that represents the node-wide launch/session environment | Redact values before storage. Do not store image-baked, scheduler-injected, or entrypoint-set component variables here. |

## Software bill of materials

SBOM evidence is captured before the workload runs. The reference or hash
identifies the full artifact; package lists provide an inline summary when
appropriate. Do not publish private registry locations or package information
that policy classifies as sensitive.

| Field | Type / unit | Required | Collection source | Command / method | Notes |
| --- | --- | --- | --- | --- | --- |
| `sbom_ref` | string (URI) | One of `sbom_ref` or `sbom_hash` | SBOM store / build pipeline | URI to CycloneDX SBOM produced at image build time | Preferred when an SBOM store exists. |
| `sbom_hash` | string | One of `sbom_ref` or `sbom_hash` | Image artifact | `syft <image> -o cyclonedx-json \| sha256sum` | Compute at build or collection time. |
| `python_packages` | array of {name, version} | Yes | Image inspection | `syft <image> -o json` → filter Python packages, or `pip list --format=json` inside image | Syft is preferred for non-invasive collection. |
| `os_packages` | array of {name, version} | No | Image inspection | `syft <image> -o json` → filter OS packages |  |
| `python_version` | string | Yes | Image inspection | `crane config <image>` → inspect entrypoint/env, or `syft` metadata |  |
| `pip_version` | string | No | Image inspection | Included in Syft SBOM output |  |
| `conda_packages` | array of {name, version} | No | Image inspection | `syft <image> -o json` → filter Conda packages | Only when a conda environment is present. |
| `source_mode` | string | No | — | — | Distinguishes an image scan from a best-effort local inventory. |
| `external_ref_id` | string | No | — | — | Reference to the complete SBOM artifact when the inline package lists are only a summary. |

## Explicit exclusions

The following are deliberately outside this public Node profile:

- Kubernetes and Slurm node context, labels, taints, and scheduler metadata.
- Per-instance placement, allocation, rank, and device-binding information.
- Generic Node labels and typed metadata.
- Microbenchmark results and commands.
- Runtime telemetry and application metrics.
- Collector source code, schemas, generated SDKs, fixtures, and command output.
