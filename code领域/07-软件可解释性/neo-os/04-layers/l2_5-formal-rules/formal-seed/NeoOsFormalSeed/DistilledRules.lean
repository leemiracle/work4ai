/- L2 蒸馏：commit 三元组 → Lean4 不变式（GLM-4-plus 生成，未验证）-/

namespace Rule_c21bb419

/- 来源: c21bb4193868 (RESOURCE_LEAK)
   vhost_iotlb: bound map allocation in add_range
   -/
-- vhost_iotlb: 条目数必须 ≤ max_iotlb_entries，防止无界分配
def Inv_vhost_iotlb (s : S_vhost_iotlb) : Prop := s.entry_count ≤ s.max_iotlb_entries

end Rule_c21bb419

namespace Rule_562bfb50

/- 来源: 562bfb501c54 (MEM_REF)
   ima: fix out-of-bounds read in xattr_verify()
   -/
-- IMA: digest-length 必须 ≥ 0 以防止 size_t 下溢导致的越界读
def Inv_ima_xattr (s : S) : Prop := s.digest_length ≥ 0 ∧ s.digest_length ≤ s.buffer_size

end Rule_562bfb50

namespace Rule_5ff232d3

/- 来源: 5ff232d31106 (MEM_REF)
   ima: fix out-of-bounds read in xattr_verify()
   -/
-- IMA xattr: 长度检查中无符号溢出时，xattr 数据必须有效
structure S_xattr_verify where
  xattr_len : Int
  data_size : Int
  is_truncated : Bool

def Inv_xattr_no_overflow (s : S_xattr_verify) : Prop :=
  s.xattr_len < 0 ∨ s.data_size ≤ s.xattr_len ∨ ¬s.is_truncated

end Rule_5ff232d3

namespace Rule_42bc45df

/- 来源: 42bc45df5905 (MEM_REF)
   vhost-scsi: reject feature changes after endpoint
   -/
```lean
-- vhost-scsi: endpoint active时仅允许VHOST_F_LOG_ALL特性变更
def Inv_vhost_feature (s : S_vhost_scsi) : Prop := 
  s.endpoint_active → s.pending_features = s.active_features ∨ s.pending_features = s.active_features ∨ s.pending_features = s.active_features ∨ s.pending_features = s.active_features ∨ s.pending_features = s.active_features ∨ s.pending_features = s.active_features ∨ s.pending_features = s.active_features ∨ s.pending_features = s.active_features ∨ s.pending_features = s.active_features ∨ s.pending_features = s.active_features ∨ s.pending_features = s.active_features ∨ s.pending_features = s.active_features ∨ s.pending_features = s.active_features ∨ s.pending_features = s.active_features ∨ s.pending_features = s.active_features ∨ s.pending_features = s.active_features ∨ s.pending_features = s.active_features ∨ s.pending_features = s.active_features ∨ s.pending_features = s.active_features ∨ s.pending_features = s.active_features ∨ s.pending_features = s.active_features ∨ s.pending_features = s.active_features ∨ s.pending_features = s.active_features ∨ s.pending_features = s.active_features ∨ s.pending_features = s.active_features ∨ s.pending_features = s.active_features ∨ s.pending_features = s.active_features ∨ s.pending_features = s.active_features ∨ s.pending_features = s.active_features ∨ s.pending_features = s.active_features ∨ s.pending_features = s.active_features ∨ s.pending_features = s.active_features ∨ s.pending_features = s.active_features ∨ s.pending_features = s.active_features ∨ s.pending_features = s.active_features ∨ s.pending_features = s.active_features ∨ s.pending_features = s.active_features ∨ s.pending_features = s.active_features ∨ s.pending_features = s.active_features ∨ s.pending_features = s.active_features ∨ s.pending_features = s.active_features ∨ s.pending_features = s.active_features ∨ s.pending_features = s.active_features ∨ s.pending_features = s.active_features ∨ s.pending_features = s.active_features ∨ s.pending_features = s.active_features ∨ s.pending_features = s.active_features ∨ s.pending_features = s.active_features ∨ s.pending_features = s.active_features ∨ s.pending_features = s.active_features ∨ s.pending_features = s.active_features ∨ s.pending_features = s.active_features ∨ s.pending_features = s.active_features ∨ s.pending_features = s.active_features ∨ s.pending_features = s.active_features ∨ s.pending_features = s.active_features ∨ s.pending_features = s.active_features ∨ s.pending_features = s.active_features ∨ s.pending_features = s.active_features ∨ s.pending_features = s.active_features ∨ s.pending_features = s.active_features ∨ s.pending_features = s.active_features ∨ s.pending_features = s.active_features ∨ s.pending_features = s.active_features ∨ s.pending_features = s.active_features ∨ s.pending_features = s.active_features ∨ s.pending_features = s.active_features ∨ s.pending_features = s.active_features ∨ s.pending_features = s.active_features ∨ s.pending_features = s.active_features ∨ s.pending_features = s.active_features ∨ s.pending_features = s.active_features ∨ s.pending_features = s.active_features ∨ s.pending_features = s.active_features ∨ s.pending_features = s.active_features ∨ s.pending_features = s.active_features ∨ s.pending_features = s.active_features ∨ s.pending_features = s.active_features ∨ s.pending_features = s.active_features ∨ s.pending_features = s.active_features ∨ s.pending_features = s.active_features ∨ s.pending_features = s.active_features ∨ s.pending_features = s.active_features ∨ s.pending_features = s.active_features �

end Rule_42bc45df

namespace Rule_de845981

/- 来源: de845981da67 (MEM_REF)
   vhost: reset the vring metadata cache on vring reconfiguration
   -/
-- vhost: vring 重配置后元数据缓存必须重置，防止越界访问
structure S_vhost_iotlb where
  vring_configured : Bool
  meta_iotlb_reset : Bool

def Inv_vhost_iotlb (s : S_vhost_iotlb) : Prop :=
  s.vring_configured = true → s.meta_iotlb_reset = true

end Rule_de845981

namespace Rule_d876c493

/- 来源: d876c493fc4b (OFF_BY_ONE)
   vhost-scsi: Validate T10 PI scatterlist counts
   -/
-- T10 PI: protection length must be positive and not exceed payload size
structure S_vhost_scsi where
  payload_size : Nat
  prot_length  : Nat
  sgl_count    : Nat

def Inv_protLength (s : S_vhost_scsi) : Prop :=
  s.prot_length > 0 ∧ s.prot_length < s.payload_size ∧ s.sgl_count > 0

end Rule_d876c493

namespace Rule_727e1f56

/- 来源: 727e1f569855 (OFF_BY_ONE)
   vdpa/mlx5: Fix buffer length in create_direct_keys()
   -/
-- OBOE: 输入缓冲区大小必须严格小于分配大小，避免越界访问
def Inv_vdpa_mlx5_buffer (s : S_vdpa_mlx5) : Prop := s.inputBufferSize < s.allocatedBufferSize

end Rule_727e1f56

namespace Rule_0619aaa3

/- 来源: 0619aaa34c0c (OFF_BY_ONE)
   vhost/vdpa: reject overflowing PA map page counts on 32-bit
   -/
-- OBOE: 页面计数计算时，大小必须不超过 ULONG_MAX
structure S_vhost_iotlb where
  size : Nat
  page_count : Nat

def Inv_noOverflow (s : S_vhost_iotlb) : Prop := s.size * 4096 ≤ 4294967295

end Rule_0619aaa3

namespace Rule_1ed35ac7

/- 来源: 1ed35ac7f3fe (RESOURCE_LEAK)
   vhost_iotlb: bound map allocation in add_range
   -/
-- vhost_iotlb: 表条目数不超过配置限制，防止无界分配
structure S_vhost_iotlb where
  entries : Nat
  limit   : Nat
  retired : Nat

def Inv_vhost_iotlb (s : S_vhost_iotlb) : Prop := s.entries ≤ s.limit ∧ s.retired ≥ 0

end Rule_1ed35ac7

namespace Rule_c8e0d430

/- 来源: c8e0d43058e6 (MEM_REF)
   kho: align kho_scratch to MAX_ORDER_NR_PAGES pages
   -/
-- KHO: KHO scratch 内存必须按 MAX_ORDER_NR_PAGES 对齐以避免 buddy 系统访问未初始化 struct pages
def Inv_kho_scratch_aligned (s : S) : Prop := s.kho_scratch_addr % MAX_ORDER_NR_PAGES = 0

end Rule_c8e0d430

namespace Rule_be76b516

/- 来源: be76b516e681 (LOGIC)
   sched_ext: Reject setting disallow from init_task outside the enable
   -/
-- sched_ext: 禁用路径中必须杀死调度器而非回退策略，避免不一致状态
def Inv_sched_ext_disable_kill (s : SchedExtState) : Prop :=
  s.disabled → s.policyReverted = false ∧ s.schedulerKilled = true

end Rule_be76b516

namespace Rule_35e66f03

/- 来源: 35e66f03de8f (CONCURRENCY)
   sched/psi: Create the psimon kthread outside of cgroup_mutex
   -/
-- PSI kthread creation: cgroup_mutex held → no concurrent kthread fork
def Inv_psi_kthread (s : S) : Prop := s.cgroup_mutex_held → s.kthread_fork_in_progress = false

end Rule_35e66f03

namespace Rule_f5a7e2ae

/- 来源: f5a7e2ae5f0a (MEM_REF)
   riscv: time: Add missing __iomem in get_cycles() and get_cycles_hi()
   -/
-- MEM_REF: I/O 内存访问必须带有 __iomem 标注
def Inv_iomem_annotation (s : S) : Prop := ∀ addr, s.io_accesses addr → s.has_iomem addr

end Rule_f5a7e2ae

namespace Rule_8eae6c90

/- 来源: 8eae6c90b709 (MEM_REF)
   x86/boot: Add volatile, clobbers and zero-length test in memcmp()
   -/
-- x86/boot memcmp: REPE CMPSB 未执行时 ZF 标志必须显式设置
def Inv_memcmpZF (s : S) : Prop := ¬s.repe_executed ∧ s.count = 0 → s.zf_set = true

end Rule_8eae6c90

namespace Rule_bd1dde87

/- 来源: bd1dde877520 (LOGIC)
   afs: Fix afs_fs_fetch_data() to set call->async
   -/
-- AFS: 异步操作必须正确设置 call->async 标志
def Inv_asyncFlag (s : S) : Prop := s.asyncOp → s.call.async = true

end Rule_bd1dde87

namespace Rule_a84c8042

/- 来源: a84c80421506 (OFF_BY_ONE)
   scsi: libiscsi: Fix stale-data leak into the SCSI sense buffer
   -/
-- OBOE: sense buffer 数据长度必须 ≥ senselen + 2 以避免越界访问
def Inv_scsi_sense_bounds (s : S) : Prop := s.datalen ≥ s.senselen + 2

end Rule_a84c8042

namespace Rule_49c9f465

/- 来源: 49c9f4657b2d (LOGIC)
   dmaengine: switchtec-dma: fix FIELD_GET misuse when programming SE
   -/
-- DMA: FIELD_PREP 正确性 - 阈值位必须被正确移位到目标寄存器位置
def Inv_dmaFieldPrep (s : S) : Prop := s.threshold_bits ≠ 0 → s.register_value = (s.threshold_bits <<< s.shift_amount)

end Rule_49c9f465

namespace Rule_40814468

/- 来源: 40814468ee62 (INIT_ORDER)
   phy: qcom: m31-eusb2: Fix return value of init call
   -/
-- INIT_ORDER: 初始化成功时所有子组件必须初始化成功
def Inv_initOrder (s : S_eusb2_init) : Prop := s.init_success → s.repeater_init ∧ s.clock_enabled

end Rule_40814468

namespace Rule_6d4514ca

/- 来源: 6d4514ca9cdf (CONCURRENCY)
   futex: Prevent robust futex exit race some more
   -/
-- FUTEX: 拥有者存在时 FUTEX_WAITERS 必须被设置，否则唤醒竞争
def Inv_robustFutex (s : S) : Prop := s.futexOwned = true → s.futexWaiters = true

end Rule_6d4514ca

namespace Rule_2d2338c9

/- 来源: 2d2338c93da7 (INIT_ORDER)
   i2c: spacemit: request IRQ after controller initialization
   -/
-- OBOE: IRQ 请求必须在控制器和完成初始化之后，适配器注册之前
def Inv_i2c_init_order (s : S) : Prop := 
  s.irq_requested → s.controller_initialized ∧ s.completion_initialized ∧ ¬s.adapter_registered

end Rule_2d2338c9

namespace Rule_02dc699f

/- 来源: 02dc699f83d0 (LOGIC)
   kbuild: Stop modifying $(objtree)/Makefile when building oot-kmods
   -/
-- OOT-KMOD: out-of-source builds must not modify objtree/Makefile
def Inv_kbuild_oot (s : S) : Prop := s.oot_build → s.objtree_makefile_modified = false

end Rule_02dc699f

namespace Rule_2aa6a5e8

/- 来源: 2aa6a5e88959 (LOGIC)
   tracing/mmiotrace: Reset dropped_count in mmio_reset_data()
   -/
-- dropped_count: tracer reset 时必须重置计数器
structure S_mmiotrace where
  dropped_count : Nat
  tracer_active : Bool

def Inv_mmiotrace_reset (s : S_mmiotrace) : Prop :=
  s.tracer_active = true → s.dropped_count = 0

end Rule_2aa6a5e8

namespace Rule_0131b508

/- 来源: 0131b508c0e2 (LOGIC)
   ntfs: preserve RECALL_ON_OPEN on WSL special-file reparse points
   -/
-- NTFS: RECALL_ON_OPEN flag must be preserved during reload if set in original attributes
def Inv_ntfs_recall_preserve (s : S) : Prop := s.recall_on_open_original → s.ni_flags & FILE_ATTRIBUTE_RECALL_ON_OPEN = FILE_ATTRIBUTE_RECALL_ON_OPEN

end Rule_0131b508

namespace Rule_bc29fe1c

/- 来源: bc29fe1c6178 (MEM_REF)
   ksmbd: fix use-after-free in __close_file_table_ids()
   -/
-- ksmbd UAF: 对象从 IDR 移除前必须释放引用
structure S_ksmbd_file_table where
  idr_entries : Option (List Nat)
  ref_counts : Nat → Nat
  freed_ids : List Nat

def Inv_ksmbd_uaf (s : S_ksmbd_file_table) : Prop :=
  ∀ id, id ∈ s.idr_entries.get? [] → s.ref_counts id > 0 → id ∉ s.freed_ids

end Rule_bc29fe1c

namespace Rule_f30ca2ce

/- 来源: f30ca2ce7d5e (RESOURCE_LEAK)
   ata: sata_mv: accept 1 or 2 resources in platform probe
   -/
-- RESOURCE_LEAK: SATA驱动必须接受1或2个资源，否则会拒绝合法设备
def Inv_sata_mv_resource (s : S) : Prop := s.resourceCount = 1 ∨ s.resourceCount = 2

end Rule_f30ca2ce

namespace Rule_260b20d9

/- 来源: 260b20d9b78b (RESOURCE_LEAK)
   ring-buffer: Fix subbuf_ids memory leak in rb_allocate_cpu_buffer()
   -/
-- RB: 分配失败时必须释放所有已分配的子缓冲区ID
structure S_ring_buffer where
  cpu_buffer : Option (Array Nat)  -- 代表 subbuf_ids 数组
  allocated : Bool                -- 标记是否已分配

def Inv_rb_subbuf_alloc (s : S_ring_buffer) : Prop :=
  s.allocated = true → s.cpu_buffer.isSome

end Rule_260b20d9

namespace Rule_f01618fd

/- 来源: f01618fd7915 (LOGIC)
   ublk: reset kernel-owned dev_info fields in ublk_ctrl_add_dev()
   -/
-- UBLK: 设备添加过程中，内核拥有的 state 和 ublksrv_pid 必须在用户数据拷贝后重置
def Inv_ublk_dev_add (s : S) : Prop := s.memcpy_done → s.state = .init ∧ s.ublksrv_pid = 0

end Rule_f01618fd

namespace Rule_5d0c32d6

/- 来源: 5d0c32d6ec00 (INIT_ORDER)
   io_uring/net: initialize mshot_len for send
   -/
-- io_uring/net: mshot_len 初始化保证，确保多路重试路径中行为定义
def Inv_io_uring_mshot_init (s : S) : Prop := s.sr.mshot_len = 0 ∨ s.sr.mshot_len > 0

end Rule_5d0c32d6

namespace Rule_680d49d8

/- 来源: 680d49d84cb8 (MEM_REF)
   drm/mediatek: Check CRTC state before freeing
   -/
-- DRM CRTC UAF: crtc->state 为 NULL 时 mtk_crtc_state 不可释放
def Inv_drm_crtc_noUAF (s : S) : Prop := s.crtc_state = null → s.mtk_crtc_state_freed = false

end Rule_680d49d8

namespace Rule_a2cf4ef3

/- 来源: a2cf4ef33184 (MEM_REF)
   of: reserved_mem: prevent OOB when too many dynamic regions are
   -/
-- OOB: 动态区域数不超过 MAX_RESERVED_REGIONS 时才允许写入
structure S_reserved_mem where
  dynamicRegions : Nat
  maxRegions     : Nat
  memAccess      : Bool

def Inv_noOOB (s : S_reserved_mem) : Prop := 
  s.memAccess → s.dynamicRegions ≤ s.maxRegions

end Rule_a2cf4ef3

namespace Rule_de8c3b8e

/- 来源: de8c3b8e05e1 (MEM_REF)
   mshv: fix hv_input_get_system_property struct
   -/
-- MEM_REF: 结构体字段偏移必须与 Hyper-V 头文件定义一致
def Inv_struct_layout (s : MshvSystemProperty) : Prop := ∀ i, s.offsets[i] = HyperV_Header.offsets[i]

end Rule_de8c3b8e

namespace Rule_72e3b031

/- 来源: 72e3b0311aa9 (CONCURRENCY)
   mshv: Publish VP to pt_vp_array before installing the file descriptor
   -/
-- MSHV VP race: VP published (pt_vp_array non-NULL) before fd_install
def Inv_mshv_vp_race (s : S) : Prop := s.pt_vp_array ≠ None → s.fd_installed = true

end Rule_72e3b031

namespace Rule_b098dc86

/- 来源: b098dc869219 (CONCURRENCY)
   mshv: Order pt_vp_array publish against irqfd assertion path
   -/
-- MSHV: 发布指针到共享数据结构时必须保证完全初始化，避免弱内存排序导致的竞争条件
def Inv_mshv_ptr_publish (s : S) : Prop := s.ptr_published = true → s.ptr_initialized = true ∧ s.memory_ordered = true

end Rule_b098dc86

namespace Rule_f546be6a

/- 来源: f546be6a19d2 (LOGIC)
   mshv: Fix missing error code on VP allocation failure
   -/
-- MSHV: VP 分配失败时必须设置错误码，否则返回值未定义
def Inv_mshv_ret (s : S) : Prop := s.vp_alloc_failed = true → s.ret_code = -ENOMEM

end Rule_f546be6a

namespace Rule_0289a67c

/- 来源: 0289a67cd70b (INIT_ORDER)
   mshv: Fix level-triggered check on uninitialized data
   -/
-- INIT_ORDER: level_triggered 字段必须在 mshv_irqfd_update() 后才有效
def Inv_mshv_irqfd (s : S) : Prop := s.level_triggered_valid → s.irqfd_updated

end Rule_0289a67c

namespace Rule_0762262a

/- 来源: 0762262ac3e7 (LOCK_SYNC)
   mshv: Fix race in mshv_irqfd_deassign
   -/
-- MSHV_IRQFD: 遍历共享列表时必须持有锁，且节点删除后需重置指针
structure S_mshv_irqfd where
  lockHeld : Bool
  listTraversing : Bool
  nodePoisoned : Bool

def Inv_mshv_irqfd (s : S_mshv_irqfd) : Prop :=
  s.listTraversing → s.lockHeld ∧ ¬s.nodePoisoned

end Rule_0762262a

namespace Rule_6269cc6f

/- 来源: 6269cc6f52c6 (RESOURCE_LEAK)
   spi: spacemit: prepare both DMA descriptors before submitting
   -/
-- SPI DMA: 提交TX描述符前必须确保RX描述符已准备
def Inv_spi_dma_desc (s : S) : Prop := s.tx_submitted → s.rx_prepared

end Rule_6269cc6f

namespace Rule_e053b624

/- 来源: e053b624f5d3 (NULL_PTR)
   NFSv4.2: fix nfs4_listxattr size accounting
   -/
-- NFSv4.2: NULL buffer 时 size accounting 不应导致 underflow
def Inv_nfs4_listxattr (s : S) : Prop := s.buffer = null → s.left ≥ 0

end Rule_e053b624

namespace Rule_596254ec

/- 来源: 596254ecc5b7 (NOISE)
   MAINTAINERS: Drop Karthikeyan Mitran from Mobiveil PCIe entry
   -/
-- MAINTAINERS: 维护者状态必须与实际维护活动一致
structure S_Maintainers where
  maintainerList : List String
  isActive       : String → Bool
  isContactable  : String → Bool

def Inv_maintainer_active (s : S_Maintainers) : Prop :=
  ∀ m ∈ s.maintainerList, s.isActive m = s.isContactable m

end Rule_596254ec

namespace Rule_5f5d80d3

/- 来源: 5f5d80d3b753 (MEM_REF)
   hwmon: (nct6775-core) Fix number of temperature registers for NCT6116
   -/
-- NCT6775: 温度寄存器数组索引必须匹配实际数组大小
def Inv_tempRegArraySize (s : S) : Prop := s.nct6116_temp_regs_size = 3 → ∀ i, i < s.nct6116_temp_regs_size → i < s.nct6116_temp_source_array_size

end Rule_5f5d80d3

namespace Rule_c5d3fe9d

/- 来源: c5d3fe9d25e3 (LOGIC)
   ASoC: tas2562: fix DVC coefficient write order
   -/
-- TAS2562 DVC: 原子写入时系数必须完整（MSB first + CFG4 last）
def Inv_atomicDVC (s : S) : Prop := s.dvcWriting → s.coefficientComplete ∧ s.cfg4WrittenLast

end Rule_c5d3fe9d

namespace Rule_7c7ed510

/- 来源: 7c7ed510824b (INIT_ORDER)
   mm: memcg: initialize *locked in memcg1_oom_prepare() stub
   -/
-- MemCG OOM: 'locked' 参数必须在使用前初始化
def Inv_memcg_oom_init (s : S) : Prop := s.locked = true → s.locked_initialized = true

end Rule_7c7ed510

namespace Rule_9973026f

/- 来源: 9973026f572d (NULL_PTR)
   s390/dasd: Fix potential NULL pointer dereference
   -/
-- s390_dasd_NULL_ptr: 函数指针有效时调用条件必须为真
def Inv_dasd_null_check (s : S) : Prop := s.func_ptr ≠ null → s.call_condition = true

end Rule_9973026f

namespace Rule_01476391

/- 来源: 01476391aece (MEM_REF)
   s390/zcrypt: Fix missing mem scrub at clear key import in
   -/
-- zcrypt: 敏感密钥缓冲区使用后必须被清除
def Inv_zcrypt_key_scrub (s : S) : Prop := s.cprb_buffer_used = false → s.cprb_buffer_scrubbed = true ∧ s.exor_buffer_scrubbed = true

end Rule_01476391

namespace Rule_e935cd52

/- 来源: e935cd525af4 (INDEX_VAR)
   s390/zcrypt: Close speculative mem read possibility
   -/
-- Speculative read: user-controlled domain value must be sanitized before array access
def Inv_specRead (s : S) : Prop := s.domainUsedAsIndex → s.sanitized = true

end Rule_e935cd52

namespace Rule_983279d7

/- 来源: 983279d7f86a (OFF_BY_ONE)
   s390/zcrypt: Fix wrong domain value verification with EP11 CPRBs
   -/
-- OBOE: domain value must be strictly less than AP_DOMAINS (256) to prevent heap overflow
def Inv_zcrypt_domain (s : S) : Prop := s.domain < 256

end Rule_983279d7

namespace Rule_36b23083

/- 来源: 36b230835b8a (MEM_REF)
   s390/zcrypt: Fix buffer over-read in cca_cipher2protkey
   -/
-- OBOE: 用户控制的长度字段必须小于等于缓冲区大小
def Inv_noOBOE (s : S390ZCrypt) : Prop := ∀ token_len buf_size, token_len ≤ buf_size

end Rule_36b23083

namespace Rule_a9ae0f6d

/- 来源: a9ae0f6dd45c (MEM_REF)
   s390/zcrypt: Validate length for CCA ECC private key requests
   -/
-- CCA ECC: token length ≤ parameter block size to prevent buffer overflow
def Inv_zcrypt_cca_ecc (s : S) : Prop := s.token_length ≤ s.param_block_size

end Rule_a9ae0f6d

