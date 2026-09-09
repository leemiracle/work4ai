/- L2 蒸馏：commit 三元组 → Lean4 不变式（GLM-4-plus 生成，未验证）-/

namespace NeoOs.DistilledRules

/- 来源: c21bb4193868 (RESOURCE_LEAK)
   vhost_iotlb: bound map allocation in add_range
   -/
-- RESOURCE_LEAK: vhost_iotlb 条目数不超过最大限制，且分配节点可重用
structure VhostIotlbState where
  entries : Nat
  maxEntries : Nat
  retiredNodes : List (Option α) -- 可重用的节点池
  tableFull : Bool -- 标记表是否已满

def Inv_vhost_iotlb (s : VhostIotlbState) : Prop :=
  s.entries ≤ s.maxEntries ∧ (s.tableFull ↔ s.entries = s.maxEntries) ∧
  ∀ node ∈ s.retiredNodes, node = none -- 重用池中节点必须为空（可重用状态）

/- 来源: 562bfb501c54 (MEM_REF)
   ima: fix out-of-bounds read in xattr_verify()
   -/
-- OBOE: digest-length 必须 ≤ xattr_size 且 ≥ 0，防止 size_t 转换下溢
structure S where
  digest_len : Int
  xattr_size : Int

def Inv_noOBOE (s : S) : Prop := 0 ≤ s.digest_len ∧ s.digest_len ≤ s.xattr_size

/- 来源: 5ff232d31106 (MEM_REF)
   ima: fix out-of-bounds read in xattr_verify()
   -/
-- OBOE: xattr 长度检查时，确保 signed int 运算避免溢出导致下界错误
structure S where
  xattr_len : Int
  xattr_max : Int
  truncated : Bool

def Inv_noOBOE (s : S) : Prop := 
  s.truncated = true → s.xattr_len ≥ 0 ∧ s.xattr_len ≤ s.xattr_max

/- 来源: 42bc45df5905 (MEM_REF)
   vhost-scsi: reject feature changes after endpoint
   -/
-- vhost-scsi: feature negotiation state must be stable when endpoint is active
structure VhostSCSIState where
  features : Nat
  endpointActive : Bool
  protSgl : Bool

def Inv_featureStability (s : VhostSCSIState) : Prop :=
  s.endpointActive → s.protSgl = (s.features && VHOST_F_LOG_ALL)

/- 来源: de845981da67 (MEM_REF)
   vhost: reset the vring metadata cache on vring reconfiguration
   -/
-- MEM_REF: vring 重配置后元数据缓存必须重置，防止越界访问
structure VringState where
  meta_iotlb : Option (Array Nat)
  vring_addr_updated : Bool
  vring_num_updated : Bool

def Inv_vring_mem_safe (s : VringState) : Prop :=
  (s.vring_addr_updated ∨ s.vring_num_updated) → s.meta_iotlb = none

end NeoOs.DistilledRules
