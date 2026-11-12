# NVMesh v3.5.0 Module Params Guide

<!--
SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
SPDX-License-Identifier: Apache-2.0
-->

## Table of Contents

- [NVMesh v3.5.0 Module Params Guide](#nvmesh-v350-module-params-guide)
  - [Table of Contents](#table-of-contents)
- [Copyright and Trademark Information](#copyright-and-trademark-information)
- [Preface](#preface)
- [Acronyms and Terms](#acronyms-and-terms)
- [Module Parameters](#module-parameters)
  - [Tracer Severities](#tracer-severities)
  - [nvmeiba](#nvmeiba)
  - [nvmeibc](#nvmeibc)
  - [nvmeib\_common](#nvmeib_common)
  - [nvmeib\_common\_public](#nvmeib_common_public)
  - [nvmeibs](#nvmeibs)
  - [siw](#siw)

# Copyright and Trademark Information

© 2026 NVIDIA All rights reserved.

Specifications are subject to change without notice.

NVMesh® is a registered trademark of NVIDIA.

All other brands or products are trademarks or registered trademarks of their respective holders and should be treated as such.

# Preface

**<u>Audience</u>**

The primary audience for this document is intended to be storage and/or application administration personnel responsible for installing and deploying NVMesh.

**<u>Feedback</u>**

We continually try to improve the quality and usefulness of documentation. If you have any corrections, feedback, or requests for additional documentation, send an e-mail message to <nvmesh-documentation@nvidia.com>.

# Acronyms and Terms

| Acronym | Description |
| --- | --- |
| Recoverer volume | A recoverer volume is attached to a client only so the storage system can perform recovery operations on it. <br>It is not exposed to user space as a `/dev` device. |
| NVLustre | Lustre-over-NVMesh. |
| RDMA IO | This is IO executed using RoCE or Infiniband for communication. |
| SIW | SoftiWarp, which provides an RDMA API, but performs communication over TCP without RDMA. <br>Often referred to as TCP in module parameter names. |
| SIW IO | This is IO executed using SIW for communication, in contrast to RDMA IO. |

# Module Parameters

For any module, it is possible to obtain a description of the module’s parameters using:

modinfo &lt;module name&gt;

## Tracer Severities

Tracer severities are defined by these values:

- 1 = Error

- 2 = Warn

- 3 = Info

- 4 = Trace

- 5 = Debug

- 6 = Fine

## nvmeiba

| Name | Description | Type | Permissions | Defaults |
|---|---|---|---|---|
| `verbose_debug` | Defines logging level. For production environments, it is recommended to set explicitly to false, in case a non-production compiled version is used. | `bool` | writable (`0644`) | `!NVMESH_IS_PRODUCTION_COMPILATION` |

## nvmeibc

| Name | Description | Type | Permissions | Defaults |
|---|---|---|---|---|
| `bio_noexec` | This is for debugging. When set to true, BIOs (kernel block IOs) are ignored instead of being executed. | `bool` | writable (`0644`) | `false` |
| `cfg_id` | Client configuration profile ID | `charp` | writable (`0644`) | `"DefaultID"` |
| `cfg_name` | Client configuration profile name | `charp` | writable (`0644`) | `"DefaultName"` |
| `cfg_version` | Client configuration profile version | `uint` | writable (`0644`) | `0` |
| `cli_attach_check_if_already_attached` | Debug only: use to simulate and test race conditions of cli attach | `bool` | writable (`0644`) | `true` |
| `debug_fail_uj_encode` | ... | `bool` | writable (`0644`) | `false` |
| `debug_level` | Enables debug logging (to the system log not NVMesh tracer) if set above 1. Deprecated. | `int` | writable (`0644`) | `1` |
| `default_dir_lsblk` | Defines the directory within /dev in which block devices will be generated. Can be left empty to use /dev. Default value: nvmesh | `string` | writable (`0644`) | `"nvmesh"` |
| `disk_coremask_support` | Set to true to enable disk coremask support. Creates "disk_max_coremask_nrch" NRCHs per coremask added via block CLI. Updated on rediscover | `bool` | writable (`0644`) | `false` |
| `disk_local_defer_block_cb` | Determines whether to defer local IO block cb to non-interrupt context. | `bool` | writable (`0644`) | `false` |
| `disk_local_use_system_pcpu_wq` | Determines whether local IO uses the system per-cpu workqueue for requests. | `bool` | writable (`0644`) | `false` |
| `disk_locks_ch_overflow_threshold` | Outstanding-op count on the address-sharded lock channel above which selection spills to the least-loaded channel. <=0 always spills (least-loaded), INT_MAX never spills (pure sharding). | `int` | writable (`0644`) | `32` |
| `disk_locks_fast_reuse` | Reuse a disk lock (disk-lock opr) before calling the callback from releasing the lock (ulp cb). This is a boolean. This is a potential optimization. | `bool` | writable (`0644`) | `false` |
| `disk_locks_use_system_pcpu_wq` | Defines whether disk locks use the system per-cpu workqueues for requests completion handling. | `bool` | read-only (`0444`) | `false` |
| `disk_max_coremask_nrch` | Determines the maximum number of channels per coremask. Updated on rediscover. | `uint` | writable (`0644`) | `2` |
| `disk_nrch_defer_block_cb` | Defines whether to defer the IO callbacks until after reenabling interrupts. | `bool` | writable (`0644`) | `false` |
| `disk_pause_at_first_discover` | Defines whether to set the disk as paused for the first discovery to make attach operations faster. False simulates pre-2.6 behavior. | `bool` | writable (`0644`) | `true` |
| `disk_pcpu_nrch_poll_proc` | Allow polling of per-cpu IO channels through a proc file, which is useful for running kernel IO from SPDK. Useful for initial SNAP versions that did some IO from the kernel. | `bool` | read-only (`0444`) | `false` |
| `disk_prio_pending` | Defines whether to prioritize IO in the pending IO queue, which hold both locks and journal entries. This was added to improve the performance of EC rebuilds. | `bool` | writable (`0644`) | `true` |
| `disk_use_coremask_pending` | Determines whether to maintain a pending command list for the coremask. If false, any IOs that cannot be immediately processed by the coremask will be submitted to the any-core channels. | `bool` | writable (`0644`) | `true` |
| `dma_pools_max_free_list_reqs` | Maximum number of requests to keep in the free list | `int` | writable (`0644`) | `32` |
| `dma_pools_max_free_reqs_per_work` | Maximum number of requests to free per work | `uint` | writable (`0644`) | `16` |
| `dma_pools_max_jiffies_free_list` | Maximum number of jiffies to keep requests in the free list | `int` | writable (`0644`) | `5` |
| `ec_reuse_req` | Enable reusing feature for requests (EC). This parameter was added to facilitate disabling this reuse as a potential optimization for NVMesh in DPU mode. | `bool` | writable (`0644`) | `true` |
| `force_reconf_reboot` | Force all block device configuration changes to be done via device reboot, i.e. restarting the block device. | `bool` | writable (`0644`) | `true` |
| `goodpath_debug_level` | This determines the level of tracing for the regular data path. Only traces with this level or lower will be issued, see tracer severities above. | `int` | writable (`0644`) | `if defined(NVMESH_IS_PRODUCTION_COMPILATION) && (NVMESH_IS_PRODUCTION_COMPILATION==1) then 0; otherwise 2` |
| `goodpath_locks_debug_level` | This determines the level of tracing for the regular data path locks. Only traces with this level or lower will be issued, see tracer severities above. | `int` | writable (`0644`) | `if defined(NVMESH_IS_PRODUCTION_COMPILATION) && (NVMESH_IS_PRODUCTION_COMPILATION==1) then 0; otherwise 3` |
| `goodpath_syncs_debug_level` | This determines the level of tracing for data path syncs. Only traces with this level or lower will be issued, see tracer severities above. | `int` | writable (`0644`) | `if defined(NVMESH_IS_PRODUCTION_COMPILATION) && (NVMESH_IS_PRODUCTION_COMPILATION==1) then 0; otherwise 4` |
| `goodpath_transport_debug_level` | This determines the level of tracing for the regular data path networking. Only traces with this level or lower will be issued, see tracer severities above. | `int` | writable (`0644`) | `1` |
| `guids` | Used for port filtering functionality. Typically populated from nvmesh.conf parameters. | `string` | writable (`0644`) | `""` |
| `ib_net_complete_iocmd_use_pcpu_wq` | Determines whether IB net complete iocmd use per-cpu workqueues for request handling. | `bool` | read-only (`0444`) | `false` |
| `io_max_retry_encrypted_secs` | Encrypted volume max time to try and execute IO before failing it to OS [sec], if 0, use system's default | `uint` | writable (`0644`) | `300` |
| `io_max_retry_secs` | Max time to try and execute IO before failing it to OS [sec], if 0, use system's default | `uint` | writable (`0644`) | `0` |
| `io_throttle_metrics_trace_mask` | Bitmask of IO throttle metric traces to emit: bit0=event_count, bit1=latency_highres_histogram, bit2=reserved, bit3=number_of_throttled_ios. 0 disables all. | `uint` | writable (`0644`) | `11` |
| `ioch_drained_timeout_sec` | The timeout in seconds for the IOCH drained event before disconnecting disk | `uint` | writable (`0644`) | `10` |
| `ioch_ka_only_no_rdda` | Use only IO channels for IO keep alive messages, requires disk discovery to take effect. | `bool` | writable (`0644`) | `1` |
| `iommu_enabled` | Informs the internal NVMesh NVMe driver that the IOMMU is enabled on the node. | `bool` | read-only (`0444`) | `false` |
| `iterations` | Number of test loop iterations | `uint` | writable (`0644`) | `50000` |
| `jam_log_metrics_period` | Defines the journal manager's periodic metrics logging period in seconds. | `ulong` | writable (`0644`) | `if DEBUG_JAM && defined(NVMESH_IS_PRODUCTION_COMPILATION) && (NVMESH_IS_PRODUCTION_COMPILATION==1) then 0; if DEBUG_JAM && else(defined(NVMESH_IS_PRODUCTION_COMPILATION) && (NVMESH_IS_PRODUCTION_COMPILATION==1)) then 2` |
| `jam_max_used_entries` | Sets the maximum journal entries to be used by the JAM (journal allocation manager). | `uint` | writable (`0644`) | `0` |
| `jam_non_free_entry_timeout` | JAM timeout for having a journal entry in a non-free state in seconds. | `ulong` | writable (`0644`) | `300` |
| `jam_pending_enb` | Controls whether to enable or allow pending allocations on the JAM. | `bool` | writable (`0644`) | `true` |
| `jam_pending_req_timeout_jif` | JAM timeout for pending allocation request in jiffies. If set to 0, use system default. | `ulong` | writable (`0644`) | `if defined(BLKDEV_SIMULATOR) && (BLKDEV_SIMULATOR==1) then (HZ / 100); otherwise (HZ / 5)` |
| `jam_use_system_pcpu_wq` | Determines whether the journal manager uses the system per-cpu workqueue for pending requests. | `bool` | read-only (`0444`) | `false` |
| `local_io_use_md_dma_pool` | When a local IO request is made without providing space for the metadata buffer and the drive has metadata enabled, then this determines whether to use a preallocated pool of memory or to dynamically allocate memory per IO. | `bool` | writable (`0644`) | `true` |
| `local_io_use_prpl` | Determines whether local IO requests use PRPLs instead of SGLs (see the NVMe standard for more information). PRPLs are needed for environments with the IOMMU enabled. | `bool` | writable (`0644`) | `true` |
| `local_io_use_rd_md_pool` | Determines whether to use a preallocated pool or to dynamically allocate memory for metadata read operations, as the NVMe standard forces reading the block data with the metadata. | `bool` | writable (`0644`) | `true` |
| `local_write_use_data_copy` | Copy write data to a DMA pool buffer before submitting to the drive. Prevents CRC mismatches when application modifies buffers during DMA. Automatically enabled for fake_4kpi drives. | `bool` | writable (`0644`) | `false` |
| `lock_ch_2nd_ch_coremask` | Enable, disable or set whether to use secondary channels as coremasks channels. Possible values: 0 - Disabled, > 0 - Max number of channels per mask to connect,All other IOs use primary channel. | `uint` | writable (`0644`) | `0` |
| `lock_ch_2nd_ch_pcpu` | Enable, disable or set the number of secondary lock channels as per-cpu lock channels. Offline CPUs within the configured CPUs range are not compensated for. Possible values: 0 = disabled, 1 = use max possible channels (min(num-cpus, 128)), Other value (when lock_ch_pcpu_cpus="") = cpu [0, i) use a per-cpu secondary-channel [0, i). Other cpus share the primary lock channel. | `uint` | writable (`0644`) | `0` |
| `lock_ch_2nd_ch_pcpu_lockless` | Determines whether the per-CPU storage-level lock channels are run lockless compared to other threads and CPUs. This reduces contention and increases performance. NOTE: There must be a pcpu channel for all submission cores or it will fallback to the shared channels with locking. | `bool` | writable (`0644`) | `true` |
| `lock_ch_get_method` | Determines the method for choosing the lock channel for RDMA communication. Possible values: 0 = LRU - tie break by sharding, 1 = BY_CPU, 2 = SHARDING by destination address | `int` | writable (`0644`) | `0` |
| `lock_ch_get_method_tcp` | Determines the method for choosing the lock channel for TCP communication, same values as for RDMA, see above. | `int` | writable (`0644`) | `1` |
| `lock_ch_pcpu_cpus` | A list of CPUs on which to pin the secondary per-cpu lock channels. The format is a hex-mask list where each entry is 32-bits, e.g., 1f,ff for CPUS 0-7, 32-36. If the list is empty, use all cores. | `charp` | writable (`0644`) | `NULL` |
| `lock_ch_scq_offload_thread` | Use a thread for offload processing for RDMA shared completion queue handling. | `bool` | writable (`0644`) | `true` |
| `lock_ch_scq_offload_thread_tcp` | Use a thread for offload processing for SIW shared completion queue handling. | `bool` | writable (`0644`) | `true` |
| `lock_ch_scq_use_kwq` | Determines whether to use kernel workqueue instead of kthread for SCQ offload processing. | `bool` | writable (`0644`) | `false` |
| `lock_channel_metrics_mask` | Bitwise mask controlling which lock channel metrics to dump in periodic traces: bit 0 (0x01): lock_opr_count - lock operation count bit 1 (0x02): lock_opr_latency - lock operation latency histogram bit 2 (0x04): lock_opr_deferred_queue_length_max - max deferred queue length bit 3 (0x08): lock_opr_deferred_latency - deferred operation latency histogram Note: Proc file always shows all metrics regardless of this mask. Default: 0x0F (all metrics enabled) | `uint` | writable (`0644`) | `(LOCK_CH_METRIC_COUNT \| LOCK_CH_METRIC_LATENCY \| LOCK_CH_METRIC_DEFERRED_QUEUE_MAX \| LOCK_CH_METRIC_DEFERRED_LATENCY)` |
| `lock_channel_periodic_timer_interval` | Interval in milliseconds for periodic lock channel usage metrics tracing per disk | `ulong` | writable (`0644`) | `10000` |
| `lock_retry_delay_multiplier` | Lock retry timeout in microseconds when failing to obtain a lock. The retry timeout undergoes exponential backoff. | `uint` | writable (`0644`) | `(5000)` |
| `lock_shard_type` | Lock shard type: 0) HASH_MODULO, 1) LOCKSET_MODULO | `uint` | writable (`0644`) | `0` |
| `locks_scq_wq_unbound` | Determines whether to use an unbound kernel workqueue for nvmeibc_locks_scq (true) or a bound one (false). | `bool` | read-only (`0444`) | `false` |
| `main_cpu` | CPU to pin main thread to | `int` | writable (`0644`) | `0` |
| `management_report_frequency` | Report frequency for management, in seconds | `int` | writable (`0644`) | `5` |
| `map_each_sg_entry` | IB DMA map each SG-entry separately. | `bool` | writable (`0644`) | `false` |
| `map_sg_mode` | Defines the mode for mapping data SG lists: 0 = Combined, use global key when able to collapse all sg-entries to one, otherwise map-mr (map WR and rdma-write WR). 1 = Use only map-mr (IB_WR_REG_MR, IB_WR_FAST_REG_MR). 2 = Use only the global dma key, which means that multiple rdma-write WRs from clnt/srv in wr/rd, respectively, may be needed. The target must have enough WRs to write the data back for read operations. 3 = Combined, but use ib_map_mr_sg when mapping MR. 4 = Use only map-mr, but use ib_map_mr_sg() for the mapping | `uint` | writable (`0644`) | `3` |
| `map_sg_result_trace` | Defines how to trace the result of mapping the data SG list: 0 = Disabled, 1 = One-shot (edge), 2 = Continuous (level) | `uint` | writable (`0644`) | `0` |
| `max_ioch_path_fail` | Number of failures allowed per path in a connection cycle. | `int` | writable (`0644`) | `(1)` |
| `max_ioch_rm_works` | Max concurrent IO communication channel removal operations. | `int` | writable (`0644`) | `0` |
| `max_ios_per_cpu` | Maximum number of concurrent IO operations handled per core. Can be used to prevent IO flooding. In other words, the upper limit on the number of outstanding IOs to issue via the block driver per CPU core. Some file systems and applications queue or perform read-ahead very aggressively, likely to overcome problems with legacy storage solutions. With NVMesh, large numbers of outstanding read requests may lead to network congestion especially when target bandwidth exceeds client bandwidth. Throttling the number of outstanding requests using this parameter can reduce this congestion and improve overall quality of service. Limiting this value often ends up improving performance for the Client and others on the network. If in doubt, start with a value of 8. This setting can be applied dynamically to the kernel module without restarting services. | `uint` | writable (`0644`) | `default 64; default 16` |
| `max_lock_channels` | The maximum number of lock channels for non-TCP transports per disk. | `uint` | writable (`0644`) | `5` |
| `max_lock_channels_tcp` | The maximum number of lock channels for TCP transports per disk. | `uint` | writable (`0644`) | `16` |
| `max_nic_srqs` | Maximum number of shared receive queues per NIC. | `int` | read-only (`0444`) | `16` |
| `max_notify_cq_iterations` | Defines the maximum number of iterations to ARM completion queues. | `uint` | writable (`0644`) | `10` |
| `max_num_partitions_on_vol` | Defines the maximum number of external partitions reserved as minors range. | `uint` | read-only (`0444`) | `256` |
| `max_trim_size_mirrored` | Maximum size of a single NVMesh internal TRIM operation for mirrored volumes. The value is for multiples of 128 KB. | `uint` | writable (`0644`) | `128` |
| `max_trim_size_non_mirrored` | Maximum size of a single NVMesh internal TRIM operation for non-mirrored volumes. | `uint` | writable (`0644`) | `16384` |
| `memmgr_metrics_info_dump_each_cpu_separately` | Dump memmgr metrics info per cpu | `bool` | writable (`0644`) | `false` |
| `min_rediscover_timeout_ms` | Minimum time between rediscovery attempts in milliseconds | `uint` | writable (`0644`) | `1000` |
| `mini_elevator` | Enable mini-elevator which combines writes to erasure coded volumes to fill stripes. This functionality was experimental (and promising), but did not reach production quality. | `bool` | writable (`0644`) | `false` |
| `mini_elevator_jiffies` | Defines the maximum number of jiffies an IO may reside in the mini-elevator. | `ulong` | writable (`0644`) | `100` |
| `nic_io_stats_block_size` | Block-size to use for NIC iostats.json | `uint` | read-only (`0444`) | `4096` |
| `no_part_scan` | Disable partition scan on nvmesh block devices. | `bool` | writable (`0644`) | `false` |
| `nordda_wq_unbound` | Determines whether to use an unbound kernel workqueue for nvmeibc_nordda (true) or a bound one (false). Relevant only if nr_defer_recv_comps_use_kwq is set to true | `bool` | read-only (`0444`) | `false` |
| `nr_defer_recv_comps` | Defer processing of IO completions for RDMA transports. | `bool` | writable (`0644`) | `true` |
| `nr_defer_recv_comps_tcp` | Defer processing of IO completions for SIW transports. | `bool` | writable (`0644`) | `false` |
| `nr_defer_recv_comps_use_kwq` | Determines whether to use a kernel workqueue for deferred receive completions on nordda channels. | `bool` | writable (`0644`) | `false` |
| `nr_get_by_cpu_index` | Get nrch based on CPU-index: 0 - False, 1 - True, Other (>=2) - True and allow fallback to other select schemes | `uint` | writable (`0644`) | `0` |
| `nr_get_by_cpu_index_tcp` | Get nrch based on CPU-index (for TCP): 0 - False, 1 - True, Other (>=2) - True and allow fallback to other select schemes | `uint` | writable (`0644`) | `0` |
| `nr_get_by_numa_node` | Get nrch based on NUMA-node: 0 - False, 1 - True and allow fallback to other select schemes | `uint` | writable (`0644`) | `1` |
| `nr_get_by_numa_node_tcp` | Get nrch based on NUMA-node (for TCP): 0 - False, 1 - True and allow fallback to other select schemes | `uint` | writable (`0644`) | `1` |
| `nr_get_least_used` | Get least used nrch (preceded by nr_get_by_cpu_index) | `bool` | writable (`0644`) | `false` |
| `nr_max_channels_per_disk` | Maximum number of RDMA IO channels per disk. | `uint` | writable (`0644`) | `(64)` |
| `nr_max_channels_per_path` | Maximum number of RDMA IO channels per disk per networking path. | `uint` | writable (`0644`) | `4` |
| `nr_max_channels_per_path_iommu` | Maximum number of RDMA IO channels per disk per networking path when the IOMMU is enabled. | `uint` | writable (`0644`) | `4` |
| `nr_max_channels_per_path_tcp` | Maximum number of SIW IO channels per disk per networking path. | `uint` | writable (`0644`) | `16` |
| `nr_max_used_reqs_per_channel` | Maximum number of requests issued simultaneously on a channel. | `uint` | writable (`0644`) | `64` |
| `nr_max_wrs_per_req` | The maximum number of WRs (RDMA work requests) per IO channel request, used for a write operation. For 0, use system's default. | `uint` | writable (`0644`) | `0` |
| `nr_pcpu_ch_ll_cpus` | A list of CPU cores for lockless per-cpu IO RDMA channels. The format is as a hex-mask list of cores, where each entry is 32-bits. | `charp` | writable (`0644`) | `NULL` |
| `nr_pcpu_ch_lockless` | Per-cpu RDMA IO channels are lockless. This reduces contention and increases performance, but requires a lot more channels typically. | `bool` | writable (`0644`) | `false` |
| `nr_pcpu_channels_per_disk` | Connect per-cpu RDMA IO channels (up to 128) in addition to the nr_max_channels_per_disk any-cpu channels. The total number of channels between a client and a target's disk is limited by the lower of nr_max_channels_per_path on the Client and the Target. Typically set to true for kernel-based DPU usage. | `uint` | writable (`0644`) | `0` |
| `nr_rotate_in_pending` | Rotate nrch list when reusing channel for pending cmds | `bool` | writable (`0644`) | `false` |
| `nr_shared_cq` | Use a shared completion queue (SCQ) for RDMA IO. | `bool` | writable (`0644`) | `true` |
| `nr_shared_cq_tcp` | Use a shared completion queue (SCQ) for SIW IO. | `bool` | writable (`0644`) | `false` |
| `nr_skip_rdma_write` | This is an unsafe debug mode. RDMA IOs skip the RDMA write for write operations. This will always work on Legacy volumes and on EC when CRC check is off and block size is equal to the slice length of the volumes, but it will not store the right data! Used for performance testing only. | `bool` | writable (`0644`) | `false` |
| `nr_store_fr` | Enables a workaround for RDMA resource usage to avoid rare RDMA protection errors in EC writes where target-side buffers from journal writes are reused for data writes. | `bool` | writable (`0644`) | `true` |
| `nr_use_srq` | Use a shared receive queue (RCQ) for RDMA IO. | `bool` | writable (`0644`) | `true` |
| `nr_use_srq_tcp` | Use a shared receive queue (RCQ) for SIW IO. | `bool` | writable (`0644`) | `true` |
| `nr_wd_long_timeout` | IO watchdog timeout in jiffies. | `ulong` | writable (`0644`) | `0` |
| `nr_wd_rescue_timeout` | IO watchdog rescue timeout in jiffies. An IO watchdog rescue is an attempt to handle any missed receive interrupts even though there was no interrupt. This functionality was an escape and is considered unnecessary. A value under 1 second disables this functionality. | `ulong` | writable (`0644`) | `0` |
| `nvmeibc_copy_bio_buffers` | Copy bio buffers in writes. Should be on except for specific file systems that never write into a buffer during IO. | `bool` | writable (`0644`) | `true` |
| `nvmeibc_debug_ram_binfo` | Enforce detection of topological data corruptions in RAM. | `bool` | writable (`0644`) | `true` |
| `nvmeibc_debug_ram_unknown_dbits` | Enforce detection of too much unknown dbits relative to degraded mode | `bool` | writable (`0644`) | `true` |
| `nvmeibc_default_debug_di` | Upon volume attach, enable "debug di" mode. | `bool` | writable (`0644`) | `false` |
| `nvmeibc_dp_alloc_allow_io` | Do not use GFP_NOIO for data path memory allocations | `bool` | writable (`0644`) | `false` |
| `nvmeibc_io_pet_buffer_size` | IO per-entity trace buffer size. | `uint` | writable (`0644`) | `4096` |
| `nvmeibc_io_pet_disable` | A non-zero value will disable IO per-entity trace functionality. | `uint` | writable (`0644`) | `1` |
| `nvmeibc_io_pet_max_traced_ops_per_cpu` | Maximum concurrently traced IO PET operations per CPU. 0 = unlimited. | `uint` | writable (`0644`) | `256` |
| `nvmeibc_io_pet_minimal_severity` | Defines the minimal severity for IO per-entity trace buffers to be written. | `uint` | writable (`0644`) | `2` |
| `nvmeibc_io_pet_verbose` | A non-zero value will allow IO per-entity trace buffers to provide even more information such as the first 8 bytes and metadata for every block. This may hurt performance and the buffer size should be taken into account. | `uint` | writable (`0644`) | `0` |
| `nvmeibc_jentry_num_blocks` | Length of erasure coding journal, in blocks. For erasure coding volumes, increasing this means fewer parallel write IO operations, but more efficient large writes. It is highly recommended to increase for use cases with large writes. Range is 1 to 16. | `uint` | writable (`0644`) | `16` |
| `nvmeibc_jmd_wr_version` | Version of JMD (journal metadata) to use to facilitate backwards compatibility: 0 = packed, 1 = unpacked. | `uint` | writable (`0644`) | `(1)` |
| `nvmeibc_should_sync_reuse_memory` | Reuse pages across syncs (internal storage recovery operations) to reduce the number of page allocations and deallocations. | `bool` | writable (`0644`) | `true` |
| `nvmeibc_sync_full_lockset_probability_factor` | Defines the probability of sync'ing full 128K blocks instead of the current IO requested. It is used to avoid very slow IO during recovery, while avoiding wasteful repeat synchronizations. If the entire block is not synchronized, this will still need to be done by the regular recovery mechanism. The probability is computed by multiplying the number of blocks in the IO x param value / 3200. Range is 0 to 3200. 0 = never synchronize the full block. 3200 = always. | `uint` | writable (`0644`) | `100` |
| `nvmeibc_sync_max_operations_per_dev` | Maximum number of outstanding sync (recovery) operations per volume. Maximum is 6144. | `uint` | writable (`0644`) | `(384)` |
| `nvmeibc_target_nics_query_min_fail_secs` | Minimum number of seconds of discovery failures before sending a Target NICs query to management, for the whole target | `uint` | writable (`0644`) | `10` |
| `nvmeibc_trace_stats_period_sec` | (no MODULE_PARM_DESC found) | `uint` | writable (`0644`) | `10` |
| `nvmeibc_warn_on_edic_verification_failure` | Issue kernel warning upon CRC-based read block verification failure. Useful for detecting data that has been correct on drives. | `bool` | writable (`0644`) | `true` |
| `pages_max_alloc` | Maximum (kernel) order of page allocations allowed. | `int` | writable (`0644`) | `(sizeof(unsigned int) * 8 - 1)` |
| `panic_on_core_dbgdi` | In "debug di" mode, panic on detection of an issue, on both client and target. This is an internal debugging facility. | `bool` | writable (`0644`) | `false` |
| `pcpu_cq_poll_proc` | Create /proc files for polling the nvmeibs shared completion queues from SPDK. This requires pcpu_cq_all_cpus=Y for nvmeib_common. | `bool` | read-only (`0444`) | `false` |
| `per_cpu_lock_transfer_num` | The number of lock transfer candidates or slots per CPU. Lock transfers are used to optimize serial writes and transfer lock ownership from one IO to another to avoid having to wait for it to be released and then acquired again. For production clusters, it is often recommended to set to 32. | `uint` | read-only (`0444`) | `8` |
| `ports` | Used for port filtering functionality. This is typically set by service startup based on nvmesh.conf information. If empty, no filter is used otherwise the format is either: <hca_id> - use this nic and all its ports or <hca_id>:<port id> or a net-device name. For example: mlx4_0:1,mlx_4:2,mlx4_1:1 - will use three ports of two nics | `string` | writable (`0644`) | `""` |
| `prefix_priority_masks_rediscover_on_new` | Determines whether to rediscover when a new common prefix priority is found. | `bool` | writable (`0644`) | `false` |
| `profiling_enabled` | Enable statistics gathering, should be turned off if the clocksource is not tsc. | `bool` | writable (`0644`) | `true` |
| `qa_ec_stress_debug` | For QA only! Stresses the EC datapath. | `bool` | writable (`0644`) | `false` |
| `rdda_pois_bb` | Poison RDDA remote buffer before read | `bool` | writable (`0644`) | `true` |
| `recovery_debug_level` | This determines the level of tracing for recovery operations for this module. Only traces with this level or lower will be issued, see tracer severities above. | `int` | writable (`0644`) | `if defined(NVMESH_IS_PRODUCTION_COMPILATION) && (NVMESH_IS_PRODUCTION_COMPILATION==1) then 3; otherwise 4` |
| `recovery_iterator_cooldown` | Recovery iterator timeout to wait after completing full recovery cycle in jiffies. Increasing this trades recovery load vs. recovery time. | `ulong` | writable (`0644`) | `1` |
| `reject_all_volume_attaches` | Autofail all volume attaches, prevent kernel crashes on wrong MCS/mgmt messages | `uint` | writable (`0644`) | `0` |
| `restart_io_timeout_secs` | Time in seconds to wait between full cycles of IO channels reconnection. Upon a disconnection, reconnection attempts will be more often and exponentially backoff as needed up to this value. | `uint` | writable (`0644`) | `(30)` |
| `resub_awake_throttle_sleep_ms` | Resubmit thread's sleep time for throttling, in milliseconds. Should be in the order of scheduler process switching. | `ulong` | writable (`0644`) | `(10)` |
| `resub_awake_throttle_threshold_ms` | Resubmit thread's threshold for throttling, in milliseconds. The thread will yield after running for this amount of time. | `ulong` | writable (`0644`) | `(1000)` |
| `self_recovery_detach_idle_time_sec` | Time-out for idle recoverer volume (after recovery finished) until self detached [sec] | `uint` | writable (`0644`) | `60` |
| `self_recovery_detach_initial_time_sec` | Time-out for just attached idle recoverer volume until self detached [sec] | `uint` | writable (`0644`) | `5` |
| `skip_disk_iocmds_flags` | This is an unsafe debug mode. Skip disk access (remote and local): 0 = Disabled, 1 = Skip read operations, 2 = Skip write operations, 3 = Skip read & write operations, 4 = Skip journal write operations or any combination using this operation, 5 = Skip all IO operations including those not mentioned above. Used for performance tuning and debugging. | `uint` | writable (`0644`) | `0` |
| `skip_lock_cmds_flags` | This is an unsafe debug mode. Skip locking operations for non-EC volumes (remote and local): 0 = Disabled, Bit-0 = skip cmp_exchange (regular locks), Bit-1 = skip active table locking, Bit-2 = skip read locks, Bit-3 = skip writing block-info. Used for performance tuning and debugging. | `uint` | writable (`0644`) | `0` |
| `sm_th` | Maximum number of concurrent Infiniband subnet manager requests. Used for throttling subnet manager access. | `uint` | writable (`0644`) | `32` |
| `tcp_mode` | Activate the SIW communicate mode exclusively, i.e., filter out any RoCE devices. Usually set by service startup from nvmesh.conf information. | `uint` | read-only (`0444`) | `0` |
| `tgt_nics_query_min_fail_secs` | Minimum number of seconds of discovery failures before sending a Target NICs query to management | `uint` | writable (`0644`) | `10` |
| `tgt_nics_query_min_n_fail` | The minimum number of discovery failures before sending a Target NICs query to management. | `uint` | writable (`0644`) | `UINT_MAX` |
| `tgt_nics_query_min_secs` | The minimum amount of time allowed between Target NICs query to management. | `uint` | writable (`0644`) | `2` |
| `timer_cpu` | CPU to run timer on (-1=same as main, >=0 explicit) | `int` | writable (`0644`) | `1` |
| `timer_fire_us` | Timer fire interval in us (RDMA high-load: 50-200) | `uint` | writable (`0644`) | `100` |
| `topology_debug_level` | This determines the level of tracing for topology operations, i.e. changes to volume health and layout, for this module. Only traces with this level or lower will be issued, see tracer severities above. | `int` | writable (`0644`) | `if defined(NVMESH_IS_PRODUCTION_COMPILATION) && (NVMESH_IS_PRODUCTION_COMPILATION==1) then 3; otherwise 4` |
| `tracer_debug_level` | This determines the level of tracing for this module. Only traces with this level or lower will be issued, see tracer severities above. | `int` | writable (`0644`) | `if defined(NVMESH_IS_PRODUCTION_COMPILATION) && (NVMESH_IS_PRODUCTION_COMPILATION==1) then 3; otherwise 4` |
| `unprotected_write_period_seconds` | Deprecated. Timeout in seconds for an unprotected volume until it becomes read-only. | `ulong` | writable (`0644`) | `jfs2secs(((nvmeibc_jiffies_t)~0UL))` |
| `use_async_subscribe` | Determines whether to run "subscribe" operations asynchronously. Subscribe operations are used for clients to subscribe to TOMA for instructions regarding a volume's disk segment. | `bool` | writable (`0644`) | `true` |
| `use_block_external_major` | Determines whether to use a dedicated block external major for the NVMesh block devices. This is rarely required. | `bool` | read-only (`0444`) | `false` |
| `use_ctr` | 1=use recv_comp_work_ctr pattern, 0=cancel_work_sync only | `int` | read-only (`0444`) | `0` |
| `use_local_bypass` | Access local drives directly and not via a NIC, i.e. over the network. Setting to false is mainly used for debugging local disk access. | `bool` | writable (`0644`) | `true` |
| `use_norrda_for_io` | Allow using non-RDDA operations for IO. As RDDA is deprecated, this should always be true. | `bool` | writable (`0644`) | `true` |
| `use_only_norrda_for_io` | Use only non-RDDA operations for IO. As RDDA is deprecated, this is meaningless. | `bool` | writable (`0644`) | `false` |
| `use_pcpu_cq` | Use a per-cpu shared completion queue (SCQ) and shared receive queue (SRQ). | `bool` | read-only (`0444`) | `false` |
| `use_rdda` | Allow using RDDA operations for IO. As RDDA is deprecated, this should always be false. | `bool` | read-only (`0444`) | `false` |
| `warn_if_lock_held_more_than_n_msec` | Defines the time in milli-seconds a lock is held before issuing a warning to the log. | `uint` | writable (`0644`) | `5000` |
| `warn_if_lock_took_more_than_n_msec` | If lock acquisition takes more than this value in milliseconds, issue a warning to the log. | `uint` | writable (`0644`) | `20000` |

## nvmeib_common

| Name | Description | Type | Permissions | Defaults |
|---|---|---|---|---|
| `cm_ephemeral_debug_level` | CM Ephemeral Tracing Debug Level [0..6] | `int` | writable (`0644`) | `4` |
| `completion_noise_enabled` | Enable completion noise statistics collection | `bool` | read-only (`0444`) | `false` |
| `completion_noise_measurement_interval_ms` | Measurement interval in milliseconds for noise statistics | `uint` | read-only (`0444`) | `55` |
| `cq_vec_flags` | CQ (completion queue) completion-vector selection flags, as follows: Bit 0: Reserve vec 0 for userspace. Bit 1: Index based, set by CQ creator. Bit 2: Use the same vector for SCQ/RCQ. | `uint` | writable (`0644`) | `0` |
| `cq_vec_flags_tcp` | Same as cq_vec_flags for TCP (SIW) completion queues. | `uint` | writable (`0644`) | `4` |
| `cq_vec_snd_rcv_delta` | If cq_vec_flags (see above) is set to use index-based selection for the vector, then this value will be the delta between the send and receive queue's vector. | `uint` | writable (`0644`) | `0` |
| `cq_vec_snd_rcv_delta_tcp` | Same as cq_vec_snd_rcv_delta for TCP (SIW) completion queues. | `uint` | writable (`0644`) | `0` |
| `debug_level` | Enables debug logging (to the system log not NVMesh tracer) if set above 1. | `int` | writable (`0644`) | `(int)1` |
| `fr_pool_percpu_cache` | Enable per-cpu cache for fast registration pool | `bool` | read-only (`0444`) | `true` |
| `fr_pool_percpu_high` | Spill threshold for per-cpu cache for fast registration pool | `uint` | read-only (`0444`) | `128` |
| `fr_pool_percpu_idle_timeout_ms` | Idle timeout for per-cpu cache for fast registration pool in milliseconds | `uint` | read-only (`0444`) | `1000` |
| `fr_pool_percpu_low` | Refill target for per-cpu cache for fast registration pool | `uint` | read-only (`0444`) | `64` |
| `fr_pool_percpu_rebalance_min_interval_ms` | Rebalance per-cpu cache minimum interval in milliseconds | `uint` | read-only (`0444`) | `1000` |
| `ib_cross_subnet` | Enable cross subnet, IB transport | `bool` | writable (`0644`) | `false` |
| `intr_shaper_max_burst` | Defines the maximum number of recv completions to handle in an interrupt before entering poll mode. | `uint` | writable (`0644`) | `(64)` |
| `intr_shaper_max_irq_time_usecs` | Defines the maximum time to spend in an interrupt before entering poll mode. | `uint` | writable (`0644`) | `(2000)` |
| `intr_shaper_max_pct_cpu` | Defines the maximum percentage of CPU time to spend processing completions in an interrupt before entering poll mode. | `uint` | writable (`0644`) | `(20)` |
| `ipv6_mode` | IPv6 Mode: 0 - No IPv6, 1 - IPv6 enabled, prefer IPv4 addresses, 2 - IPv6 enabled and preferred, 3 - IPv6 Only | `uint` | writable (`0644`) | `1` |
| `iwarp_cm_inv_time_sec` | Timeout for iWARP CM Invalidate (in seconds | `uint` | writable (`0644`) | `30` |
| `iwarp_find_path_sock` | Use a socket for iwarp_find_path. Reduces load on siw_cm_wq | `bool` | writable (`0644`) | `true` |
| `iwarp_find_path_sock_port` | listener port for find path socket listener | `int` | read-only (`0444`) | `8915` |
| `json_iostats_fixed_size` | Pad I/O statistics in JSON representation to a fixed size | `bool` | writable (`0644`) | `false` |
| `num_warnings` | The number of warnings the module has triggered. Contact support if this is not 0 | `uint` | writable (`0644`) | `0` |
| `numa_alloc_granularity` | Number of pages on the same node | `uint` | writable (`0644`) | `64` |
| `numa_alloc_policy` | NUMA node choice policy in case of large allocations: 0 : Default 1 : Round robin on all nodes 2 : Round robin on nodes within the same socket as an appropriate device | `uint` | writable (`0644`) | `if defined(CONFIG_NUMA) && defined(__x86_64__) then 2; otherwise 0` |
| `nvmeib_completion_noise_threshold_percentages` | Noise thresholds as CPU percentage (default: 1,5,10,20,50) | `int[]` | read-only (`0444`) | `{1, 5, 10, 20, 50}` |
| `pcpu_cq2srq_size_margin` | When employing a per CPU shared completion and receive queue, this determines how much bigger the SCQ is than the SRQ. Margin = CQ-size - SRQ-size. | `int` | read-only (`0444`) | `1024` |
| `pcpu_cq_all_cpus` | Allocated CQ per online-cpus (per the Linux kernel) per device, which always process completions in a thread context, i.e. on the ipoller. | `bool` | read-only (`0444`) | `false` |
| `pcpu_cq_comp_vecs_per_dev` | Y = use first N comp-vectors of device where N='max num of pcpu-cqs per device'. N = use all comp-vectors spread globally between all devices, which is usually not recommended. | `bool` | read-only (`0444`) | `true` |
| `pcpu_cq_flush_del_qps` | percpu cqs flush QPs pending for deletion (bool). Do not change with consulting support. | `bool` | writable (`0644`) | `false` |
| `pcpu_cq_intr_budget` | The per-cpu CQs interrupt-mode's budget. This is the maximum number of completions to handle in a single interrupt. | `uint` | writable (`0644`) | `4` |
| `pcpu_cq_max_cqs_per_dev` | Maximum number of percpu cqs per device. If set to 0, use system default. | `uint` | read-only (`0444`) | `0` |
| `pcpu_cq_poll_budget` | The per-cpu CQs polling-mode's budget, which is the maximum number of CQ entries to be processed in an interrupt before offloading to ipoller thread. | `uint` | writable (`0644`) | `256` |
| `pcpu_cq_size` | The length or size of the shared completion queue when employing a per CPU shared completion and receive queue. | `int` | read-only (`0444`) | `4096` |
| `pcpu_cq_user_poll_budget` | The per-cpu CQs user-mode polling budget. This is the maximum number of CQ entries to process for each user-mode poll. | `uint` | writable (`0644`) | `64` |
| `pcpu_cq_user_poll_timeout_msecs` | Timeout to switch from user polling, i.e., polling from a user-space application thread context ,e.g. SPDK, back to ipoller for a CQ. | `uint` | writable (`0644`) | `100` |
| `pcpu_process_cq_retry_usecs` | The time window in micro-seconds to keep polling after last completion before rearming interrupts (0: disabled). | `uint` | writable (`0644`) | `0` |
| `pcpu_wq_debug_level` | Set trace level for nvmeib_pcpu_wq | `int` | writable (`0644`) | `4` |
| `qp_retry_cnt` | QP retry count | `uint` | writable (`0644`) | `7` |
| `qp_timeout` | QP timeout (4.096 x 2^N) us | `uint` | writable (`0644`) | `14` |
| `relax_timeouts` | Multiplier for default control path timeouts (0 - unset) | `uint` | writable (`0644`) | `0` |
| `tcp_base_port_id` | The first (base) port ID for secondary SIW (iWARP) listeners. | `uint` | read-only (`0444`) | `7915` |
| `tcp_num_ports` | TCP: Secondary iWARP listeners number of TCP ports (0 = number of RX Queues or number of online CPUs) | `uint` | read-only (`0444`) | `0` |
| `tracer_debug_level` | This determines the level of tracing for this module. Only traces with this level or lower will be issued, see tracer severities above. | `int` | writable (`0644`) | `3` |

## nvmeib_common_public

| Name | Description | Type | Permissions | Defaults |
|---|---|---|---|---|
| `config` | This parameter can be used to alter the binary tracer engine configuration. This string can be up to 4 kbytes. The tracer's configuration defines the resources consumed by the tracer, its performance, and aspects of its ephemeral behaviour. | `string` | writable (`0644`) | `""` |
| `do_kasan_test` | When set, run a test KASAN on module load. Results will be found in the system log, i.e., via dmesg. | `bool` | read-only (`0444`) | `false` |
| `hide_warnings_stack` | Hide warnings from dmesg, the kernel log, while keeping them in the binary traces. | `bool` | writable (`0644`) | `NVMESH_IS_PRODUCTION_COMPILATION` |
| `ib_odp_info` | Defines whether On-Demand-Paging is enabled for RDMA usage and NVMesh should use it. 1 = Enabled, 0 = Disabled, -1 = Auto. On-demand-paging enables using RDMA on non-pinned memory pages. | `int` | writable (`0644`) | `-1` |
| `ipoller_poll_duration_jif` | ipoller poll duration till reschedule, 0=default (uint). This is used for RDMA completion queue handling, albeit it can be used for other purposes as a generic NVMesh infrastructure component. | `uint` | writable (`0644`) | `0` |
| `tracer_dbg_level` | Tracer debug level, internal | `ulong` | writable (`0644`) | `4` |
| `tracer_dbg_mask` | Tracer debug injections mask, internal | `ulong` | writable (`0644`) | `0` |
| `tracer_debug_level` | This determines the level of tracing for this module. Only traces with this level or lower will be issued, see tracer severities above. | `int` | writable (`0644`) | `3` |
| `tracer_wq_debug_level` | This determines the level of tracing for work queues for this module. Only traces with this level or lower will be issued, see tracer severities above. | `int` | writable (`0644`) | `4` |
| `wq_max_processing_time` | The maximum wq (workqueue) processing time before the workqueue reschedules itself in jiffies. | `ulong` | writable (`0644`) | `(3 * HZ)` |

## nvmeibs

| Name | Description | Type | Permissions | Defaults |
|---|---|---|---|---|
| `cap_transfer_size` | Cap all disks' max-transfer-size to 128 KB, even if the drive supports larger transfers. | `bool` | read-only (`0444`) | `true` |
| `debug_level` | Enables debug logging (to the system log not NVMesh tracer) if set above 1. Deprecated. | `int` | writable (`0644`) | `1` |
| `defer_process_io_cq` | Defer all IO completions to a per completion queue thread, so it is not done in the interrupt context. | `bool` | writable (`0644`) | `false` |
| `defer_recv_comps` | Defer handling of IO receive completions, so it is not done in the interrupt context. | `bool` | writable (`0644`) | `true` |
| `defer_recv_comps_tcp` | Same as defer_recv_comps, but applied for TCP/SIW NICs. | `bool` | writable (`0644`) | `false` |
| `disk_collect_stats` | Enable collecting statistics for disk operations. Can be used for performance optimization. | `bool` | writable (`0644`) | `true` |
| `distr_intr_program` | Path to the interrupt distribution program | `string` | writable (`0600`) | `"/opt/nvmesh/common-repo/scripts/" "/nvmesh_set_irq_affinity"` |
| `dummy_id` | Serial ID to be used for drives on drive-less targets. Dummy drives are rarely needed, only for an arbiter on a 2-node system. | `charp` | read-only (`0444`) | `NULL` |
| `emulate_4kpi` | Dev only. Emulate 4096+8 format on 512b-only drives by mapping each 4K+8 LBA to 9x512b LBAs. | `bool` | read-only (`0444`) | `false` |
| `fake4kpi_integrity` | Integrity check for fake4kpi sectors: none, crc32c, crc32, xxhash, xor (default: crc32) | `charp` | read-only (`0444`) | `"crc32"` |
| `fake4kpi_md_size` | Metadata size in bytes for fake4kpi (8, 16, 32, 64; default: 8) | `int` | read-only (`0444`) | `8` |
| `fake4kpi_ring_size` | Per-queue bounce buffer ring size for fake4kpi (0 = auto-size to queue depth) | `int` | read-only (`0444`) | `0` |
| `fake_large_disk_size_lba` | Do not use for production systems. The size of fake large disks, in 4k units. | `ullong` | read-only (`0444`) | `((uint64_t)1 << ((32) + 1))` |
| `fake_large_disks` | Do not use for production systems. Fake the system having larger disks by overriding their size. This is used for developing support for larger drives. | `bool` | read-only (`0444`) | `false` |
| `fake_serial` | Do not use for production systems. Fake serial number for a fake NVMe drive, which should be machine specific. | `charp` | read-only (`0444`) | `NULL` |
| `force_fake4kpi` | Dev only. Force fake4kpi on drives that support native 4k+8 but are currently formatted to 512b+0. | `bool` | read-only (`0444`) | `false` |
| `format_timeout_seconds_seconds_try` | (no MODULE_PARM_DESC found) | `int` | writable (`0644`) | `3600` |
| `gcp_drives_to_uuid_list` | Related to GCP mode, i.e., specifically for GCP virtual NVMe drives. This provides a list of UUIDs of drives to be used. This should be provided on module invocation, i.e., during Target service startup. | `charp[]` | read-only (`0444`) | `(no explicit initializer)` |
| `gcp_mode` | Use only drives that are specified in gcp_drives_to_uuid_list. | `bool` | writable (`0644`) | `false` |
| `goodpath_debug_level` | This determines the level of tracing for the regular data path. Only traces with this level or lower will be issued, see tracer severities above. | `int` | writable (`0644`) | `2` |
| `guids` | Used for port filtering functionality. Typically populated from nvmesh.conf parameters. | `string` | writable (`0644`) | `""` |
| `ib_port_prio` | Defines the priority of Infiniband. Enables overriding the form of network transportation to prefer. See roce_port_prio and tcp_port_prio also. | `uint` | writable (`0644`) | `0` |
| `ignore_disks` | Comma separated list of PCI IDs of NVMe drives to ignore. For example, "0000:03:00.0,0000:12:01.0". | `string` | writable (`0600`) | `(no explicit initializer)` |
| `ignore_disks_serials` | Comma separated list of serial IDs of NVMe drives to ignore. For example, "S23YNAAH201234,S23YNAAH202345". | `string` | writable (`0600`) | `(no explicit initializer)` |
| `ioka_timeout_sec` | Keepalive timeout failure for an IO channel, in seconds. | `int` | writable (`0644`) | `8` |
| `iommu_enabled` | Informs the internal NVMesh NVMe driver that the IOMMU is enabled on the node. | `bool` | read-only (`0444`) | `false` |
| `jgc_avail_ent_low_wm_div` | Triggers JGC (journal garbage collection) if the available range of entries falls below the low watermark of total-range-entries * mult / div. | `uint` | writable (`0644`) | `8` |
| `jgc_avail_ent_low_wm_mult` | Triggers JGC (journal garbage collection) if the available range of entries falls below the low watermark of total-range-entries * mult / div. | `uint` | writable (`0644`) | `8` |
| `local_skip_disk_access` | Unsafe debug mode. Skip local disk access, i.e., complete disk operations immediately instead of performing them. Used for debugging and performance optimization. | `bool` | writable (`0644`) | `false` |
| `max_client_rsrc` | RDDA is deprecated. Maximum number of RDDA connections per client. | `uint` | writable (`0644`) | `if !defined(NVMEIB_SHARED_H) && !defined(LOW_MEM) then (128); if !defined(NVMEIB_SHARED_H) && else(!defined(LOW_MEM)) then (1)` |
| `max_completions` | Maximum number of networking completions to handle per interrupt. | `int` | writable (`0644`) | `64` |
| `max_local_nvmeqs` | Maximum NVMe queues for local operation. A value of 0 sets the actual maximum to the lower of the number of CPUs, drive queues, doorbells and MSI-X interrupts available. The value is replaced by the actual number calculated. | `int` | read-only (`0444`) | `0` |
| `max_nic_srqs` | Maximum number of shared receive queues to define per NIC. | `int` | read-only (`0444`) | `16` |
| `max_outstanding_cm_work_items` | Max outstanding CM (connection manager) work items. Important for larger environments using RDMA. | `uint` | writable (`0644`) | `8` |
| `max_req_size` | Maximum size of client-target messages. | `int` | read-only (`0444`) | `roundup_pow_of_two(C_MSGS_MAX(NVMEIBC_MAX_ADMIN_CLIENT_REQ_SIZE, NVMEIBC_RSP_SIZE))` |
| `min_local_nvmeqs` | Minimum number of NVMe queues per drive to reserve for non-RDDA usage. As RDDA is deprecated, this is obsolete. | `int` | writable (`0644`) | `1` |
| `mostly_idle_ch` | Defines whether to use the first shared CQ for "mostly" idle channels. | `bool` | writable (`0644`) | `false` |
| `nic_io_stats_block_size` | Defines the block-size to use for NIC iostats.json. | `uint` | read-only (`0444`) | `4096` |
| `nordda_kernel_wq_unbound` | Determines whether to use an unbound kernel workqueue (true) or a bound one (false). | `bool` | read-only (`0444`) | `false` |
| `nordda_use_kernel_wq` | Determines whether to use a kernel workqueue for nordda deferred IO commands (reduces IRQ latency). | `bool` | read-only (`0444`) | `true` |
| `nr_max_channels_per_path` | The maximum number of RDMA IO channels per network path. | `uint` | writable (`0644`) | `0` |
| `nr_max_channels_per_path_tcp` | The maximum number of SIW IO channels per network path. | `uint` | writable (`0644`) | `16` |
| `nr_max_wrs_per_req` | The maximum number of WRs (RDMA work requests) per IO channel request, used in response to a read request. For 0, use system's default. | `int` | writable (`0644`) | `0` |
| `nr_post_recv_on_send_comp` | In per-cpu CQ and SRQ mode, post a receive buffer on send completion of an IO response. | `bool` | read-only (`0444`) | `false` |
| `nr_skip_disk_access` | Unsafe debug mode. Skip local disk access, i.e., complete disk operations immediately instead of performing them for remote IO operations. Used for debugging and performance optimization. | `bool` | writable (`0644`) | `false` |
| `nr_skip_rdma_write_back` | Unsafe debug mode. Skip performing the RDMA write-back usually done for disk read operations for remote IO operations. Used for debugging and performance optimization. | `bool` | writable (`0644`) | `false` |
| `nr_wq_set_cpu_affinity` | Set CPU affinity of IO communication work queues, based on channel index. | `bool` | writable (`0644`) | `false` |
| `nvme_disk_periodic_timer_interval` | Interval in milliseconds for periodic timer per disk | `callback` | writable (`0644`) | `(not found)` |
| `nvme_doorbell_batch` | Determines whether to batch NVMe doorbell requests. | `bool` | writable (`0644`) | `true` |
| `nvme_number_offset` | Offset for /dev/nvme%d device names. | `int` | read-only (`0444`) | `1000` |
| `nvme_wq_unbound` | Determines whether to use an unbound kernel workqueue for nvmeibs_nvme (true) or a bound one (false), relevant only if use_nvme_kwq = true. | `bool` | read-only (`0444`) | `false` |
| `nvmeibs_jrange_num_blocks` | Total number of journal blocks in journal range, typically allocated to a single client. Should be set to a power of 2, between 64 and 16384. | `uint` | read-only (`0444`) | `(1 << NVMEIB_EC_JOURNAL_MAX_BLKS_PER_RANGE_V1_3_SHIFT)` |
| `nvmeibs_nordda_io_req_num` | Number of IO requests per IO channel. More can increase throughput, but may hurt caching. Less reduces memory consumption. | `int` | writable (`0644`) | `if !defined(NVMEIB_SHARED_H) && !defined(LOW_MEM) then (96); if !defined(NVMEIB_SHARED_H) && else(!defined(LOW_MEM)) then (4)` |
| `pcpu_cq_poll_proc` | Create /proc files for polling the nvmeibs shared completion queues from SPDK. This requires pcpu_cq_all_cpus=Y for nvmeib_common. | `bool` | read-only (`0444`) | `false` |
| `ports` | Used for port filtering functionality. This is typically set by service startup based on nvmesh.conf information. | `string` | writable (`0644`) | `""` |
| `qid_hint` | Send data on a channel per the CPU id, mainly relevant for SIW. | `bool` | writable (`0644`) | `false` |
| `roce_ipv4_only` | Deprecated. Use IPv4 only for RoCE, which was needed for CX-3. | `bool` | read-only (`0444`) | `false` |
| `roce_port_prio` | Defines the priority of ROCE. Enables overriding the form of network transportation to prefer. See ib_port_prio and tcp_port_prio also. | `uint` | writable (`0644`) | `10` |
| `serjio_fail_next_gpt_init` | SERJIO - Fail the next GPT init (for testing). | `bool` | writable (`0644`) | `false` |
| `serjio_fail_next_gpt_update` | SERJIO - Fail the next GPT update (for testing). | `bool` | writable (`0644`) | `false` |
| `serjio_init_db_interrupt_range` | Interrupt Init DB when it gets to this range. Warning: This is for debug only, used for testing SERJIO init failures. | `uint` | writable (`0644`) | `~(unsigned)0` |
| `serjio_invalid_jris_exist_on_disk` | Allocate (but quarantine) invalid JRIs (0,1,2) on disk. | `bool` | read-only (`0444`) | `true` |
| `serjio_next_free_alloc_quarantined` | SERJIO - Allocate a quarantined range index for the next allocation (for testing). | `bool` | writable (`0644`) | `false` |
| `serjio_next_free_alloc_quarantined_idx` | Quarantined range index for next invalid allocation. Relevant only if next_free_alloc_quarantined is set to true. | `int` | writable (`0644`) | `-1` |
| `serjio_resched_work_wait_max` | Amount of time in seconds to wait for a rescheduled SERJIO work item to run. SERJIO work items are related to garbage collection and cleaning up of journal entries. Works are rescheduled if SERJIO is in a busy state, e.g., due to a GPT update, and cannot process normal work. | `uint` | writable (`0644`) | `10` |
| `service_guid` | Override cm_listen_id with this value. | `callback` | writable (`S_IRUGO \| S_IWUSR`) | `(not found)` |
| `shared_rq_size` | Networking shared receive queue (SRQ) size. | `int` | writable (`0644`) | `(128 * 16 * NVMEIB_MAX_NORDDA_IO_REQ) >> 2` |
| `simulate_timeout` | Set to 1 to simulate a timeout on the next outstanding command (auto-clears) | `bool` | writable (`0644`) | `false` |
| `stamp_free_jrnl_entries` | Stamp free journal entries for debugging purposes. | `bool` | read-only (`0444`) | `true` |
| `submit_wait_timeout` | Timeout for NVMe admin operations such as drive formatting. Does not affect a second format attempt after a failure, as some drives take a long time to format, especially larger ones. Value in milliseconds. | `ulong` | writable (`0644`) | `15000000` |
| `tcp_mode` | Activate the SIW communicate mode exclusively, i.e., filter out any RoCE devices. Usually set by service startup from nvmesh.conf information. | `uint` | read-only (`0444`) | `0` |
| `tcp_port_prio` | Defines the priority of SIW. Enables overriding the form of network transportation to prefer. See ib_port_prio and roce_port_prio also. | `uint` | writable (`0644`) | `20` |
| `tracer_debug_level` | This determines the level of tracing for this module. Only traces with this level or lower will be issued, see tracer severities above. | `int` | writable (`0644`) | `4` |
| `use_intr_shaper` | Determines whether to use an interrupt shaper for NVMe completions. | `bool` | writable (`0644`) | `true` |
| `use_nvme_kwq` | Determines whether to use a kernel workqueue instead of a wakeup thread for processing completion queues. | `bool` | read-only (`0444`) | `false` |
| `use_pcpu_cq` | Use a per-cpu shared completion queue (SCQ) and shared receive queue (SRQ). | `bool` | read-only (`0444`) | `false` |

## siw

| Name | Description | Type | Permissions | Defaults |
|---|---|---|---|---|
| `ack_signal_wr` | Request responder to ack signaled writes (bool). | `bool` | writable (`0644`) | `true` |
| `comp_vector_cpu0` | (no MODULE_PARM_DESC found) | `int` | writable (`0644`) | `0` |
| `connect_non_block` | Perform non-block TCP connects (bool). | `bool` | writable (`0644`) | `true` |
| `cq_notify_tasklet` | Use tasklet (instead of WQ) for CQ notify (bool). | `bool` | read-only (`0444`) | `true` |
| `debug_level` | Enables debug logging (to the system log not NVMesh tracer) if set above 1. Deprecated. | `int` | writable (`0644`) | `1` |
| `iface_list` | Interface list SIW attaches to if present (array of characters). | `charp[]` | read-only (`0444`) | `(no explicit initializer)` |
| `loopback_enabled` | Enable loopback (bool). | `bool` | writable (`0644`) | `true` |
| `low_delay_tx` | Run tight transmit thread loop if activated (bool). | `bool` | writable (`0644`) | `true` |
| `low_delay_tx_cpu_set` | bitmap of tx-cpus thread in tight loop (ulong). | `ulong` | writable (`0644`) | `-1` |
| `mpa_crc_required` | MPA CRC required (bool). | `bool` | writable (`0644`) | `(no explicit initializer)` |
| `mpa_crc_strict` | MPA CRC off enforced (bool). | `bool` | writable (`0644`) | `true` |
| `mr_min_page_4k` | Advertise 4 KiB as the minimum MR page size in page_size_cap, even when the kernel PAGE_SIZE is larger (bool, default true). | `bool` | writable (`0644`) | `true` |
| `notify_on_wq` | Notify CQ on Workqueue (bool). | `bool` | writable (`0644`) | `true` |
| `panic_on_rx_err` | Panic on RX Error (bool). | `bool` | writable (`0644`) | `false` |
| `panic_remote_on_rx_err` | Panic remote on RX Error (bool) using TCP OOB. | `bool` | writable (`0644`) | `false` |
| `relax_timeouts` | Multiplier for default timeouts (0 - unset) | `uint` | writable (`0644`) | `0` |
| `siw_cm_err_inj` | SIW CM error injection bits via FOREACH_SIW_CM_ERR_INJ(SIW_CM_ERR_INJ_BIT_MODPARAM_DESC). Not for production use! | `ulong` | writable (`0644`) | `0` |
| `sock_buff_sz` | Socket buffers size in bytes. | `int` | writable (`0644`) | `65536` |
| `tcp_nodelay` | Set TCP NODELAY (bool). | `bool` | writable (`0644`) | `true` |
| `tcp_quickack` | Set TCP QUICKACK (bool). | `bool` | writable (`0644`) | `true` |
| `tx_cpu_list` | List of CPUs siw TX thread shall be bound to (format: comma separated no spaces) | `string` | read-only (`0444`) | `""` |
| `tx_cpus` | TX CPU selection: 0=tx_cpu_list, 1=all CPUs, 2=NUMA local to NIC when choosing TX thread | `int` | read-only (`0444`) | `1` |
| `tx_flags_from_upstream` | Tx flags from upstream... | `bool` | writable (`0644`) | `false` |
| `tx_flags_use_eor` | Tx flags from upstream use EOR... | `bool` | writable (`0644`) | `false` |
| `tx_one_ht_per_core` | Use only one hyperthread per physical core for TX threads | `bool` | read-only (`0444`) | `false` |
| `tx_thread_high_prio_bmp` | A bitmap of CPU Tx Threads to set to high priority. | `ulong` | writable (`0644`) | `0` |
| `use_so_incoming_cpu` | Set the RX CPU of socket to RCQ's comp-vector index (after connect/accept). | `bool` | writable (`0644`) | `true` |
| `wait_rqe_delay_ms` | Delay to wait on empty S(RQ) (in ms) (int). | `int` | writable (`0644`) | `10` |
| `wait_rqe_max_retries` | Number of retries on empty S(RQ) (int). | `int` | writable (`0644`) | `10` |
| `zcopy_tx` | Zero copy user data transmit if possible (bool). | `bool` | writable (`0644`) | `true` |
| `zero_delay_tx` | Run tight transmit thread loop always (bool). | `bool` | writable (`0644`) | `true` |

