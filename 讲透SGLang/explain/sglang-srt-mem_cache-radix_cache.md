# 深度解析：`python/sglang/srt/mem_cache/radix_cache.py`

> 源码: python/sglang/srt/mem_cache/radix_cache.py @ commit ec075d8bc

## 目录

- [一、这个文件做什么](#一这个文件做什么)
- [二、核心类与函数总览](#二核心类与函数总览)
- [三、`RadixKey`：树的边标签](#三radixkey树的边标签)
- [四、`TreeNode`：树节点](#四treenode树节点)
- [五、`RadixCache` 本体](#五radixcache-本体)
- [六、树的生命周期：一个逐步演化的例子](#六树的生命周期一个逐步演化的例子)
- [七、与 memory_pool 的协同：三方契约](#七与-memory_pool-的协同三方契约)
- [八、与其他模块的交互](#八与其他模块的交互)
- [九、端到端时序：一个多轮对话请求的一生](#九端到端时序一个多轮对话请求的一生)
- [十、关键设计决策](#十关键设计决策)
- [十一、常见问题与误区](#十一常见问题与误区)
- [十二、阅读建议](#十二阅读建议)

---

## 一、这个文件做什么

`radix_cache.py` 是 SGLang 招牌技术 **RadixAttention** 的核心数据结构实现（模块 docstring，L20-22："The radix tree data structure for managing the KV cache"）。

一句话概括职责：

> **把所有请求的 token 序列作为 key、KV cache 的物理槽位索引作为 value，存进一棵 radix 树（基数树/压缩前缀树）；新请求到来时沿树做最长前缀匹配，命中部分直接复用已算好的 KV cache，跳过对应的 prefill 计算；同时以"叶子节点 + LRU（或其他策略）"为单位管理淘汰，把显存里最没用的前缀 KV 释放掉。**

### 1.1 它解决的经济学问题

LLM 推理最贵的是 prefill 的 KV 计算，而实际负载里大量请求共享前缀——few-shot 模板、system prompt、多轮对话历史、同一文档的反复提问。RadixAttention 让**任何两个请求的公共前缀在显存里只存一份**，且这个共享是自动、细粒度（token 级）、增量进行的：

- 与 vLLM 早期的 block table + 精确哈希前缀匹配相比，radix 树支持**部分匹配**：请求与已缓存序列前 900 个 token 相同、第 901 个不同，照样复用那 900 个（哈希方案要求边界完全对齐才能命中）；
- 与完全无缓存相比，多轮对话第二轮起只需 prefill 新增的几个 token，TTFT（首 token 延迟）可下降一个数量级。

### 1.2 三个主角

- `RadixKey`（L66）：树的"边标签"——token 序列的轻量视图，支持 page 对齐和 EAGLE bigram 视图；
- `TreeNode`（L208）：树节点——key 边 + value（KV 槽位索引张量）+ 锁/时间戳/优先级等簿记；
- `RadixCache`（L270）：树本体——匹配 `match_prefix`、写入 `insert`/`cache_unfinished_req`/`cache_finished_req`、淘汰 `evict`、引用计数 `inc_lock_ref`/`dec_lock_ref`。

### 1.3 一个必须先建立的认知：目录与仓库分离

**这棵树只存"逻辑 token → 物理 KV 槽位"的映射，不存 KV 数据本身**。KV 张量在 `token_to_kv_pool_allocator` 管理的显存池里；树节点 `value` 是 `torch.Tensor`（int64 槽位号）。树是"目录"，池是"仓库"。

```
   RadixCache（目录）                token_to_kv_pool（仓库）
   root ── [A B C] ── [D E]          slot 17: K_A V_A   ← 物理显存
            │                         slot 18: K_B V_B
            └── [F G]                 slot 19: K_C V_C
   节点.value = tensor([17,18,19])    ...
```

这个分离是一系列设计的前提：树的分裂/合并是纯元数据操作、淘汰退化为一次 `allocator.free`、被淘汰节点可以保留 key 骨架等待 HiCache 从 host 恢复。

---

## 二、核心类与函数总览

| 组件 | 行号 | 职责 |
|---|---|---|
| `RadixKey` | L66-206 | token 序列 key：bigram 视图、page 对齐、前缀匹配、子节点哈希键、页哈希 |
| `TreeNode` | L208-267 | 树节点：children/parent、key/value、lock_ref、LRU 时间戳、host_value（HiCache）、hash_value（事件） |
| `RadixCache.__init__` | L271-316 | 读配置、选 7 种淘汰策略之一、`evictable_leaves` 集合 |
| `RadixCache.reset` | L338-359 | 建根节点（永久锁定）、复用空匹配结果 |
| `match_prefix` | L361-419 | **读路径**：最长前缀匹配 |
| `insert` | L421-439 | **写路径**底层：插入 key/value 对 |
| `cache_finished_req` | L441-486 | 请求结束时把全部 KV 存树、释放多余槽位与锁 |
| `cache_unfinished_req` | L488-552 | chunked prefill 中途把已算 KV 存树、迁移锁、回写 req_to_token |
| `evict` | L561-588 | 按策略淘汰可淘汰叶子，释放显存 |
| `inc_lock_ref` / `dec_lock_ref` | L590-624 | 引用计数：在用前缀的防淘汰保护 |
| `_match_prefix_helper` | L646-670 | 匹配的下降循环（含节点分裂） |
| `_split_node` | L672-692 | 把一个节点按前缀长度劈成两半 |
| `_insert_helper` | L702-754 | 插入的下降/分裂/建叶循环 |
| `_update_leaf_status` / `_delete_leaf` | L774-797 | 可淘汰叶子集合的增量维护 |

主链路鸟瞰：

```
[Prefill 准入]  Scheduler → match_prefix (L361)
                     └─ _match_prefix_helper (L646) ──命中中途── _split_node (L672)
                     └─ 返回 device_indices + last_device_node
                     └─ req.last_node ← last_node; inc_lock_ref (L590)

[Chunked prefill 中途 / 请求被逐出]
   maybe_cache_unfinished_req (common.py:46)
                     └─ cache_unfinished_req (L488)
                          ├─ insert (L421) → _insert_helper (L702)
                          ├─ free 重复槽位 → re-match → 回写 req_to_token
                          ├─ dec 旧锁 / inc 新锁
                          └─ req.prefix_indices = 树内索引 + 私有尾巴

[请求完结]      release_kv_cache (common.py:567)
                     └─ cache_finished_req (L441)
                          ├─ insert → free 重复段/零头段
                          └─ dec_lock_ref (L605)

[显存不足]      alloc_token_slots → evict_from_tree_cache (common.py:330)
                     └─ evict (L561): 叶子堆 → allocator.free → _delete_leaf → 父晋升
```

---

## 三、`RadixKey`：树的边标签（L66-206）

### 3.1 基本形态与 bigram 视图

`RadixKey` 用 `__slots__`（L69）持三样东西：`token_ids`（`array("q")` 的原始 token 序列）、`extra_key`（可选命名空间标签，如 lora_id / cache_salt）、`is_bigram`（L71-82）。

`extra_key` 是个精巧的隔离机制——`match_prefix` 的 docstring（L362-373）专门解释：相同 token 前缀但 `extra_key` 不同的条目**故意不共享**，用于 LoRA 隔离、不同采样盐/缓存版本的隔离（不同 adapter 对同一 prompt 算出的 KV 不同，绝不能混用）。`child_key`（L180-190）生成子节点字典键时会把 `extra_key` 编进去（`(extra_key, plain)`），`_check_compatible`（L141-146）在 match 前校验两侧 extra_key 相同，不匹配直接抛 `ValueError`。

`is_bigram` 服务 EAGLE 类推测解码：draft 模型的 KV 以**相邻 token 对**（bigram）为逻辑单位（因为 EAGLE draft attention 每步消费一对 token）。妙处在于它不物化 bigram 列表，而是**同一段 token_ids 的另一种视图**：

- `__len__` 返回 `n-1`（L84-88，N+1 个 raw token 表示 N 个 bigram）；
- `__iter__` yield 相邻对 `(t[i], t[i+1])`（L91-97）；
- `maybe_to_bigram_view` O(1) 翻转标志（L128-139，注释"flip the bigram flag instead of materializing a tuple list"），配对的 value 截到 bigram 数；
- 切片语义（`__getitem__`，L99-116）：bigram 的 `[start, stop)` 对应原始 token 的 `[start, stop+1)`——相邻 bigram 共享一个边界 token（L67 docstring），空切片给空序列而非"悬空边界 token"（L111-115 注释）。

### 3.2 匹配与子键

- `match(other, page_size)`（L149-178）：返回与 `other` 的公共前缀长度（逻辑单位，page 对齐向下取整）。三种情形分支：bigram 模式下 L 个相同 token 意味着 L-1 个相同 bigram（L154-162）；page_size=1 时逐 token 比较（L164-170）；page_size>1 时按页比较整页是否相等（L172-178），保证匹配长度是页的倍数。两处 TODO 注释（L90, L148）坦承瓶颈：逐元素 Python 循环有 PyLong boxing 开销，待 numpy 向量化。
- `page_aligned(page_size)`（L122-126）：把 key 截到页大小整数倍——paged KV 布局（如 FlashInfer/HydraGraph 的 page table）要求 KV 复用必须按页对齐。
- `child_key(page_size)`（L180-190）：**树下降用的哈希键**——取头一页的逻辑单位（单 token 或 token 二元组元组），加 extra_key 命名空间。children 字典的键就是它，所以"找下一个孩子"是一次 O(1) 哈希查找而非线性扫描兄弟节点。这等价于把 trie 的"每 token 一层"压缩成"每页一层哈希 + 边内线性确认"。
- `hash_page(start, end, prior_hash)`（L192-205）：对 `[start, end)` 的逻辑单位做 SHA256，支持链式（`prior_hash` 先混入，形成前缀哈希链）。这是给 KV cache 事件（`KVCacheEventMixin`）和 PD 分布式预填充用的——页级内容指纹，让 prefill 调度器能跨节点识别"这段 KV 我有/他要"。

---

## 四、`TreeNode`：树节点（L208-267）

字段分四组（L212-233）：

**结构组**：

| 字段 | 说明 |
|---|---|
| `children` | `defaultdict(TreeNode)`——child_key → 子节点 |
| `parent` | 父指针（锁/哈希都要沿它上行） |
| `key: RadixKey` | 从父到本节点的边标签（这段 token） |
| `value: Optional[torch.Tensor]` | 这段前缀对应的 KV 槽位索引；`evicted` property（L235-237）就是 `value is None` |

**淘汰簿记组**：

| 字段 | 用途 |
|---|---|
| `lock_ref` | 被在跑请求引用的计数，>0 则不可淘汰 |
| `last_access_time` | `time.monotonic()`，LRU 依据；`__lt__` 按它比较（L266-267），使节点可直接进 `heapq` |
| `creation_time` / `hit_count` | FIFO / LFU 依据 |
| `priority` | priority 策略用，插入时沿路径取 max 传播（L716/L733/L737） |

**HiCache 组**：`host_ref_counter`（L224，"incremented when the node is referenced by a storage operation"——层级缓存做 host↔device 搬运时的防淘汰锁，与 `lock_ref` 独立计数）+ `host_value`（host 端 KV 索引）。`protect_host`/`release_host`（L243-252）成对操作，减到负数直接抛 `RuntimeError`。`backuped` property（L239-241）= `host_value is not None`。

**事件组**：`hash_value: List[str]`（每页指纹，惰性计算——`_insert_helper` L752 注释"Hash will be computed lazily during event emission"）；`get_last_hash_value`（L254-258）与 `get_prefix_hash_values`（L260-264，沿父链递归拼接出从根到本节点的完整指纹序列）供事件导出。

类级 `counter`（L210）给每节点发唯一自增 id（L232-233），用于调试与事件追踪。

一个重要的结构性质：**`evicted` 节点（value=None）的 key 骨架仍留在树上**。这不是惰性清理的疏忽，而是有意的——保留路径信息意味着 HiCache 场景下从 host 恢复 KV 时只需把 value 填回去，树形与指纹链都还在（`_update_leaf_status` L785 也据此把 evicted 节点排除在可淘汰叶子之外）。

---

## 五、`RadixCache` 本体

### 5.1 构造与 reset（L271-359）

`__init__` 从 `CacheInitParams` 读配置：`disable`（关掉前缀缓存）、`req_to_token_pool`、`token_to_kv_pool_allocator`、`page_size`、`is_eagle`、`disable_finished_insert`、`eviction_policy`（L272-279）。淘汰策略是**策略对象**（`evict_policy.py` 的 `EvictionStrategy` 体系）：

```python
if self.eviction_policy == "lru":   self.eviction_strategy = LRUStrategy()
elif self.eviction_policy == "lfu": ...
# fifo / mru / filo / priority / slru 同理（L295-308）
else: raise ValueError(...)          # L310-313，报错列出全部支持项
```

七种策略只实现 `get_priority(node) -> 可比较值`，淘汰循环本身在 `RadixCache.evict`——**排序维度与淘汰机制解耦**，新增策略只需加一个类。

`reset`（L338-359）建根节点，四个细节：`priority=-sys.maxsize`（注释："Initialize root with minimum priority so any real priority overrides it"，保证根不干扰 priority 传播）；`lock_ref = 1`（**根永久锁定，永不被淘汰**，也使空树的 inc/dec 循环有自然终点）；`evictable_size_`/`protected_size_` 清零；L349-358 预构造 `_empty_match_result`（空索引张量 + root 为三个 node 字段）——`match_prefix` 的所有"提前返回"路径都复用这一个对象，省掉反复分配空张量（高频路径上的微优化）。

`create_simulated`（L318-334）提供无内存池的模拟构造（`mock_allocator`），测试和仿真用（文件尾 L812-826 的 `__main__` demo 就靠它跑）。

### 5.2 读路径：`match_prefix`（L361-419 + `_match_prefix_helper` L646-670）

公开接口先做三道闸（L398-407）：`disable` 或空 key 返回空结果；`maybe_to_bigram_view`（EAGLE 视角翻转）；`page_aligned` 截齐页，截完为空也返回空结果。然后进入核心的 `_match_prefix_helper(root, key)`。

下降循环的骨架（L646-670）：

```python
child_key = key.child_key(self.page_size)          # 取查询 key 的头一页
while len(key) > 0 and child_key in node.children:
    child = node.children[child_key]
    prefix_len = child.key.match(key, page_size=self.page_size)
    if prefix_len < len(child.key):                # 查询在 child 边的中途分岔
        new_node = self._split_node(child.key, child, prefix_len)
        value.append(new_node.value); node = new_node; break
    else:                                          # 整条 child 边都匹配上了
        value.append(child.value); node = child
        key = key[prefix_len:]                      # 剩余部分继续往下找
        if len(key): child_key = key.child_key(...)
```

三个语义要点：

1. **匹配即刷新时间戳**：进入函数就更新 `node.last_access_time`，循环中每个路过的 child 也刷（L647-648, L655）——被查询过的前缀自动"变热"，LRU 的"最近使用"由读路径顺手维护，不需要额外 pass。
2. **匹配中的分裂（结构变异）**：查询在 child 边的中途结束时，**当场把 child 劈成两截**（`_split_node`）。docstring（L391-396）解释动机："this structural refinement improves subsequent match efficiency and does not duplicate data"——分裂让"部分匹配"这个事实在树结构上显式化，下次匹配直接命中新节点，不必每次重新比较半条边。这是 radix 树的经典"路径压缩 + 惰性分裂"：边可以存长序列（压缩，省内存省指针），分岔时才真正切开。
3. **value 的收集**：`value` 是各段 `child.value` 的列表，出口处 `torch.cat`（L410-411）成一条完整索引张量。返回 `MatchResult(device_indices, last_device_node, last_host_node, best_match_node)`（L414-419）——后三个节点字段是**整条匹配路径的末端节点**，调用方（Scheduler）会把它记在 `req.last_node` 上并 `inc_lock_ref`，这正是"匹配到的前缀在请求运行期间不可淘汰"的实现钩子。

### 5.3 `_split_node`：一次干净的外科手术（L672-692）

把 `child`（边长 `len(child.key)`）按 `split_len` 劈成 `new_node`（前缀部分）+ 修正后的 `child`（后缀部分）：

```python
def _split_node(self, key, child, split_len):
    # new_node -> child
    new_node = TreeNode(priority=child.priority)       # 继承：代表共享前缀
    new_node.hit_count = child.hit_count                # 继承命中计数
    new_node.children = {key[split_len:].child_key(...): child}
    new_node.parent = child.parent
    new_node.lock_ref = child.lock_ref                  # 关键：锁随前缀段继承
    new_node.key = child.key[:split_len]
    new_node.value = child.value[:split_len].clone()    # clone：独立存储
    child.parent = new_node
    child.key = child.key[split_len:]
    child.value = child.value[split_len:].clone()
    new_node.parent.children[key.child_key(...)] = new_node
    new_node.hash_value, child.hash_value = split_node_hash_value(...)
    return new_node
```

四个语义细节：

- **`lock_ref` 整体搬给 new_node 而不是拆分**（L679）：正在被引用的 child 被切开时，引用方（请求）持有的是 `last_node` 句柄，分裂后这个语义必须体现在前缀段上；后缀段锁不锁取决于是否另有请求挂在更深处。严格说这是把"整段锁"归到前缀段的保守近似，简单且安全。
- **value 各自 `clone()`**（L681, L684）：`Tensor[:n]` 是视图，树节点必须持有独立存储——淘汰时 `free(x.value)` 才不会误伤别人。
- **父节点字典重挂**（L685）：`new_node.parent.children[child的头一页键] = new_node`，原 child 从祖父的字典里被顶替。
- **`hash_value` 若已算过则按 split_len/page_size 同步切分**（L687-690，`split_node_hash_value` 工具函数），没算过留 None（惰性）。

注意 `lock_ref` 继承但**不重算 evictable/protected 计数**——因为锁住的总量没变（child 原来锁 N 个 token，现在 new_node+child 合起来还是锁 N 个），树只是形状变了。这个不变量值得停下来体会一次。

### 5.4 写路径底层：`insert` 与 `_insert_helper`（L421-439 / L702-754）

公开 `insert` 做规整：bigram 视图、page 对齐、value 截到 key 长度；value 为 None 时用 token id 本身当 value（L434-436 注释标明"Debug/test fallback"，`__main__` demo 用的就是它）。

`_insert_helper` 是匹配的镜像操作，同样沿树下降（L723-740）：命中的部分推进 `total_prefix_length` 并裁掉 key/value 的已存前缀；在边中途分岔就 `_split_node`（L731-735）。路径上的维护（L713-738）：每路过一个节点刷时间戳、`priority` 沿路取 max 传播（高优先级请求"抬高"整条路径，L716/L733/L737 三处）、`_inc_hit_count`（L694-700）——**chunked 请求跳过计数**，注释说明是防"自己给自己上一 chunk 建的节点刷 hit_count"的自我膨胀。

不同点在于**走完已存路径后还剩 key 时要建新叶**（L742-753）：

```python
if len(key):
    new_node = TreeNode(priority=priority)
    new_node.parent = node; new_node.key = key; new_node.value = value.clone()
    self._inc_hit_count(new_node, chunked)
    node.children[child_key] = new_node
    self.evictable_size_ += len(key)                # 新增 token 全部计入可淘汰
    self._update_leaf_status(node)                  # 父节点从此不再是叶子
    self._update_leaf_status(new_node)              # 新节点成为可淘汰叶子
    self._record_store_event(new_node)              # KV 事件（惰性哈希）
```

返回值 `total_prefix_length` 即"树里原本已有多少前缀"，调用方靠它知道哪些槽位是重复的、要释放（见 5.6）。

### 5.5 `cache_finished_req`：请求完结的入库（L441-486）

请求正常结束时（由 `mem_cache/common.py` 的 `release_kv_cache` 统一调进来，common.py L567-581），做五件事：

1. **确定性模式闸**（L444-445）：`disable_finished_insert`（服务确定性输出需求）时把 `is_insert` 强制置 False——只释放不写入，保证行为可复现。
2. **取已提交长度**（L447）：`kv_committed_len = req.pop_committed_kv_cache()`。这个长度 ≤ 请求全长：overlap 调度下请求可能还在被上一轮 batch 引用，只有"安全提交线"以内的 KV 才允许入库。`disable` 分支（L448-453）直接按它 free 槽位返回。
3. **组装 key/value**（L455-464）：

```python
token_ids = (req.origin_input_ids + req.output_ids)[:kv_committed_len]
kv_indices = self.req_to_token_pool.req_to_token[req.req_pool_idx, :len(token_ids)]
radix_key = RadixKey(token_ids, req.extra_key, is_bigram=self.is_eagle).page_aligned(...)
key_len = len(radix_key)
values = kv_indices[:key_len].to(dtype=torch.int64, copy=True)
```

   key = prompt + 已生成 token（截到提交线）；value 从 req_to_token 映射表读出这串 token 各自的物理 KV 槽位。
4. **入库 + 去重**（L467-482）：`is_insert=True` 时调 `insert`，拿到 `result.prefix_len`（树里原有的重复前缀长度），然后：

```python
self.token_to_kv_pool_allocator.free(kv_indices[req.cache_protected_len : result.prefix_len])
```

   这段槽位的内容和树里已有的完全重复，物理上留一份就够，多出来的还给分配器。`cache_protected_len` 是"该请求此前已被锁保护的长度"（见 5.6），这之前的部分**不能 free**（上一次 `cache_unfinished_req` 已经 free 过/转移过所有权）。不插入时 free 整个未保护段（L476-479）。最后 free 页对齐的零头尾巴（L482）。
5. **解锁**（L485-486）：`dec_lock_ref(req.last_node)`——请求死了，它对匹配前缀的引用归零，这些节点回到"可淘汰"状态。

注意所有权语义（L466 注释"Radix Cache takes one ref in memory pool"）：insert 后，这段 KV 的所有权从请求移交给了树；树成为这些槽位的持有者，直到某次 `evict` 把它们释放。

### 5.6 `cache_unfinished_req`：chunked prefill 的中途入库（L488-552）

比 finished 版本复杂得多，因为它要**换锁不换血**——请求还活着，继续跑：

1. **取数据**（L493-501）：key 用 `req.fill_ids`（已填充的完整前缀：prompt + 此前 chunk 已算部分），value 同样从 req_to_token 读。
2. **插入并释放重复**（L504-516）：同 5.5 第 4 步，free `cache_protected_len` 到新 `prefix_len` 之间的重复段。
3. **重新匹配**（L519-526）：insert 后再 `match_prefix` 一次拿规范化的 `new_indices`/`new_last_node`。为什么插入后还要匹配？因为 insert 可能把请求的 key 并入了已有的更长的边（或触发分裂），**树视角下"这个请求的前缀"的末端节点可能与插入路径不同**；assert（L524-526）确认新索引长度等于 key 长度。
4. **回写 req_to_token**（L528-531）：

```python
self.req_to_token_pool.write(
    (req.req_pool_idx, slice(req.cache_protected_len, len(new_indices))),
    new_indices[req.cache_protected_len :],
)
```

   **关键协同点**：请求后续的 attention 仍通过 req_to_token 找 KV 槽位，而树刚把其中一部分槽位去重换成了"树里的那份"，所以映射表必须同步改成树里的槽位号。free 掉的重复槽位从此与该请求无关。
5. **`cache_protected_len` 的语义**（L533-537，一段浓缩了 page 语义的注释）：`cache_protected_len` **不等于** `len(req.prefix_indices)`——page_size>1 时，请求 prefix 末尾不满一页的部分会留在 `prefix_indices` 里继续用，但**没进树**（未对齐）。这个尾巴要在下一次 `cache_unfinished_req` / 最终 `cache_finished_req` 里才能安全释放，`cache_protected_len` 就是记录"已经入树并转移所有权的边界"。EAGLE bigram 同理（L544 注释：bigram key 只缓存 len-1 个索引）。
6. **锁迁移**（L539-540）：`dec_lock_ref(req.last_node)`（旧的、可能已被分裂改写的末端）→ `inc_lock_ref(new_last_node)`。新锁沿 new_last_node 到根整条路径生效。
7. **拼 prefix_indices**（L542-550）：若 `len(new_indices) < len(kv_indices)`（页尾/bigram 尾巴），`req.prefix_indices = cat([new_indices, kv_indices[len(new_indices):]])`——树内规范化索引 + 请求私有的尾巴。注释点明这个字段稍后会被 `PrefillAdder::add_chunked_req` 用。
8. **更新 `req.last_node`**（L552）。

调用方有两处（见第八节）：Scheduler 处理 chunked prefill 的 chunk 边界（`scheduler.py:2310`，带 `chunked=True` 抑制 hit_count），以及 batch result processor 在请求被 retraction/preemption 时兜底缓存（`batch_result_processor.py:238/322`）。入口统一包在 `maybe_cache_unfinished_req`（`common.py:46-50`）里，检查 `req.skip_radix_cache_insert` 标志。

### 5.7 淘汰：`evict`（L561-588）

分配器显存不够时，`common.py` 的 `alloc_token_slots` → `evict_from_tree_cache`（common.py:330-353）调到这里，要 `num_tokens` 个槽位：

```python
leaves = list(self.evictable_leaves)                       # 候选集（增量维护的集合）
eviction_heap = [(self.eviction_strategy.get_priority(node), node) for node in leaves]
heapq.heapify(eviction_heap)                               # 现场建堆
num_evicted = 0
while num_evicted < num_tokens and len(eviction_heap):
    _priority, x = heapq.heappop(eviction_heap)
    self.token_to_kv_pool_allocator.free(x.value)          # 还显存
    num_evicted += len(x.value)
    self._delete_leaf(x)                                   # 摘节点
    if len(x.parent.children) == 0 and x.parent.lock_ref == 0:
        eviction_heap.push((strategy.get_priority(x.parent), x.parent))  # 父晋升
    self._record_remove_event(x)
```

设计上三个亮点：

- **只淘汰叶子**。内部节点被多个后代表示的前缀共享，删它等于同时砍掉所有分支的 KV。叶子被删后父节点若变空且无锁，则**晋升入堆**成为新叶子候选（L581-583）——淘汰是自底向上的塌缩过程，一条无人引用的链会逐级化掉。
- **`evictable_leaves` 集合 + evict 时现场建堆**。集合由 `_update_leaf_status`（L784-797）增量维护，节点"可淘汰"⇔未 evicted、无锁（L785）、且**没有任何未淘汰的子节点**（L790-794——有活孩子的节点不是叶子）。而"按策略排序"延迟到真正 evict 时做（L568-571），淘汰是低频操作（显存压力时才发生），平时插入/解锁不值得维护全局有序结构。这是典型的摊销设计。
- **`free` 的对象是 `x.value`（槽位张量）**，`_delete_leaf`（L774-782）负责树形摘除：从父字典 pop（带 assert 校验键值一致，L776-777）、`evictable_size_` 减、叶子集合摘除、父节点状态重算。

注意 evict 循环里 pop 出的节点一定无锁（因为带锁的压根不在 `evictable_leaves` 里），这就是引用计数体系要保证的不变量。`evict` 可能超额完成（`num_evicted` 略超 `num_tokens`，因为按叶子粒度整删），调用方按需重新 alloc 即可。

### 5.8 引用计数：`inc_lock_ref` / `dec_lock_ref`（L590-624）

```python
def inc_lock_ref(self, node):
    while node != self.root_node:
        if node.lock_ref == 0:                       # 从 0→1：跨越可淘汰边界
            self.evictable_size_ -= len(node.key)
            self.protected_size_ += len(node.key)
            delta -= len(node.key)
        node.lock_ref += 1
        self._update_leaf_status(node)               # 带锁节点必须移出叶子集合
        node = node.parent
```

沿节点到根的整条路径 +1；`dec_lock_ref` 对称（1→0 时记账反向迁移，L613-616）。两个不变量：**(a) 锁的是路径不是点**——匹配到一个深叶节点，它全部祖先边（即整个前缀）都在保护范围内，因为淘汰一个内部节点同样会毁掉这段前缀（子节点全没了）；**(b) 计数迁移只在 0↔1 边界发生**——多一个请求共享同前缀时不改变可淘汰性，记账零成本。L619-622 的 assert（"This request holds the node from another tree"）防跨树操作——SWA/Mamba 变体有多棵树时 dec 到 parent 为 None 的孤儿会在这里被抓住。

对外暴露 `evictable_size()`/`protected_size()`（L626-631），调度器的准入控制（还能不能再放请求进来）就看这两个数加上分配器的空闲量。

---

## 六、树的生命周期：一个逐步演化的例子

用文件尾 demo 的 token 序列（L815-819）走一遍树的演化（page_size=1、LRU）。初始空树只有 root：

**Step 1：insert [1,2,3]**（无公共前缀）→ 建一个叶子：

```
root ── [1 2 3]                    evictable_size_=3
          (value=槽位[17,18,19])
```

**Step 2：再次 insert [1,2,3]**（完全重复）→ `_insert_helper` 沿边走完，key 剩空，不建节点；`total_prefix_length=3`，调用方据此 free 重复的 3 个槽位。树形不变。

**Step 3：insert [1,2,4,5]** → 下降：child_key=1 命中 `[1 2 3]`，`match([1,2,4,5])=2 < 3`，触发**分裂**：

```
root ── [1 2] ── [3]               ← _split_node 产物（继承 lock_ref/hit_count）
          └──── [4 5]              ← 新建的叶子
```

原边 `[1 2 3]` 被劈成 `[1 2]` + `[3]`，value 也切成 `[17,18]` 和 `[19]`（各自 clone）。新 key 剩余 `[4 5]` 挂到 `[1 2]` 下。此后若来查询 `[1,2,9,9]`，直接命中 `[1 2]` 节点返回两个槽位——分裂的收益兑现。

**Step 4：insert [1,2,4,5,6,7]** → 沿 `[1 2]` → `[4 5]` 走完，剩 `[6 7]` 建叶：

```
root ── [1 2] ── [3]
          └──── [4 5] ── [6 7]
```

**Step 5：insert [8,9,10,11,12]** → 无公共前缀，root 下另起一枝：

```
root ── [1 2] ── [3]
   │      └──── [4 5] ── [6 7]
   └── [8 9 10 11 12]
```

**Step 6：match [1,2,4,5,99]** → 下降 `[1 2]`→`[4 5]`，child_key=99 不在 children → 停在 `[4 5]`，返回 `cat([[17,18],[22,23]])` 与 `[4 5]` 节点；Scheduler 记 `req.last_node=[4 5]` 并 `inc_lock_ref` → `[4 5]` 和 `[1 2]` 的 lock_ref 变 1，`protected_size_=4`，两个节点移出 `evictable_leaves`。

**Step 7：显存吃紧，evict(num_tokens=5)** → 堆里候选是 `[3]`（和 `[6 7]`，取决于时间戳）。pop `[3]`：free 槽位 `[19]`，`_delete_leaf` 摘除；父 `[1 2]` 有别的孩子 `[4 5]`，不晋升。若 `[4 5]` 也可淘汰且被 pop，则 `[1 2]` 删完孩子后无锁晋升入堆，继续被淘汰——链式塌缩。

这个例子覆盖了全部核心操作：建叶、重复插入的去重语义、match 触发的分裂、锁的路径保护、evict 的叶子塌缩。`pretty_print`（L554-556，实现 L756-772）打印的就是这个形状，还带 child_key 一致性 assert（L770-772）。

---

## 七、与 memory_pool 的协同：三方契约

RadixAttention 的运行时正确性建立在一套三方契约上，radix_cache.py 是签约方之一：

1. **`req_to_token_pool`（请求↔槽位映射表）**：二维表 `req_to_token[req_pool_idx, :seq_len]` 记录"该请求第 i 个 token 的 KV 在哪个物理槽"。读侧：两个 cache_req 都从这里取 KV 槽位序列（L449, L456, L494）；写侧：`cache_unfinished_req` 去重后必须 `write` 回改写过的映射（L528-531）。**树视图与映射表视图必须逐 token 一致**，否则后续 attention 会读到已 free 的槽位（use-after-free 显存错误）。
2. **`token_to_kv_pool_allocator`（槽位分配器）**：树的"仓库"。`free(indices)` 是唯一的归还接口（L452, L473-482, L514-516, L577）——每次 free 的区间都精确到"重复段/零头段/淘汰段"，绝不多还（多还=双 free 崩溃）也绝不漏还（漏还=显存泄漏，`cache_protected_len` 的整套设计就是防这个，L533-537）。插入时不调 alloc——**槽位是 prefill 时就分好的，树只是接管所有权**（L466 注释"Radix Cache takes one ref in memory pool"）。
3. **`Req`（schedule_batch.py）上的四个桥字段**：`last_node`（当前锁住的树末端，匹配/入库时更新）、`cache_protected_len`（所有权已移交树的边界）、`prefix_indices`（含未对齐尾巴的完整前缀槽位）、`extra_key`/`priority`（透传给 RadixKey）。这些字段是树与调度器之间的全部状态通道——Scheduler 不了解树内部，只搬运这几个句柄。

`lock_ref`/`host_ref_counter` 双锁体系则对应两级保护：`lock_ref` 保护"正在被运行的请求使用的前缀"（5.8），`host_ref_counter` 保护"正在被 host↔device 存储搬运的节点"（L243-252）——HiCache 分层缓存的异步搬运会与淘汰并发，必须独立计数。

时序上还要注意：所有树操作发生在 Scheduler 的单线程事件循环内（或持有相应锁的组件里），因此树内部无需自己的并发控制；`evict` 由分配路径同步触发（common.py 的"先 evict 后 alloc"循环），不存在"淘汰进行到一半被匹配"的中间态。

---

## 八、与其他模块的交互

- **`base_prefix_cache.py`**：抽象基类与**参数对象协议**（`MatchPrefixParams`/`InsertParams`/`EvictParams`/`DecLockRefParams` + `MatchResult`/`InsertResult`/`EvictResult`/`IncLockRefResult`/`DecLockRefResult`）。所有公共 API 都走参数对象而非位置参数——这是为 SWA、Mamba、ChunkCache 等变体族保持接口稳定。`zero_match_result`（base L188-193）等工具也在这里。
- **`mem_cache/common.py`**：调度侧粘合层。`maybe_cache_unfinished_req`（L46-50，含 `skip_radix_cache_insert` 闸）、`release_kv_cache`（L567-581，请求完结 → mamba 池处理 → `cache_finished_req` → req pool free）、`alloc_token_slots` → `evict_from_tree_cache`（L330-353，分配不足时触发 `evict`）。
- **`managers/scheduler.py` 与 `managers/scheduler_components/batch_result_processor.py`**：上层调用点。chunked prefill 的 chunk 边界（scheduler.py:2310，`chunked=True`）、请求被逐出 running batch 时（batch_result_processor.py:238/322）。
- **`schedule_batch.py` 的 `Req`**：桥字段生产方（第七节第 3 点）；prefill 时 `init_next_round_input` 系列用 `match_prefix` 的结果裁剪要重算的 token。
- **`evict_policy.py`**：七种 `EvictionStrategy`，只提供 `get_priority(node)`。
- **`events.py` 的 `KVCacheEventMixin`**：`_record_store_event`/`_record_remove_event`/`_record_all_cleared_event` 钩子 + `kv_event_queue`（L281）+ `init_metrics_collector`（L283-284）；页指纹（`hash_value`/`hash_page`）为 PD 分离部署的 KV 事件导出服务。
- **`mem_cache/utils.py` 的 `split_node_hash_value`**（L60）：分裂时同步切分页指纹。
- **`registry.py` 的 `create_tree_cache`**（L157）：按模型/配置选用 RadixCache 或变体。
- **变体家族**：`swa_radix_cache.py`（混合 SWA 模型，full/SWA 双池，自带 sanity_check）、`mamba_radix_cache.py`（Mamba 线性注意力状态缓存，full/mamba 双 LRU 链）、`chunk_cache.py`（按 chunk 边界缓存，`is_chunk_cache()` 分支见 base L189/`common.py:334`）。它们都复用本文件的 RadixKey/TreeNode（或其子类）与整体骨架。
- **`kv_cache_builder.py`**（L21-256）：离线/分层构建场景组装 tree cache 与 host 池。
- **HiCache 体系**（`hierarchical_cache/`）：消费 `host_value`/`host_ref_counter`/`backuped` 这组字段做 host 端 KV 备份与恢复。

---

## 九、端到端时序：一个多轮对话请求的一生

设 system prompt 为 S（200 token），用户三轮提问 U1/U2/U3（各 10 token），page_size=1、LRU：

**第 1 轮（prefill [S,U1]）**：

```
1. Scheduler: req.prefix_indices = match_prefix([S,U1]) → 空（首次）
   req.last_node = root; inc_lock_ref(root) → 无操作（root 即终点）
2. Prefill 全量计算 210 token 的 KV，槽位从 allocator 现分，
   写 req_to_token[req_idx, :210]
3. 请求完成后 release_kv_cache → cache_finished_req:
   insert([S,U1], 槽位[0..209]) → 树: root ── [S U1(210 tokens)]
   free(空区间)（无重复）
   dec_lock_ref(root) → 无操作
```

**第 2 轮（prefill [S,U1,A1,U2]，A1 为第一轮回答 20 token）**：

```
1. match_prefix → 命中 [S,U1] 整条边（210/230）
   返回槽位[0..209]，last_node = [S U1] 节点
   req.last_node = 该节点; inc_lock_ref → lock_ref=1, protected_size_=210
   → PrefillAdder 只排 20 个新 token（A1）的 prefill！TTFT 大降
2. 新 token KV 写入新槽位 [300..319]
3. 完成 → cache_finished_req:
   insert([S,U1,A1,U2]) → 沿 [S U1] 边走完，剩 [A1,U2] 建叶:
       root ── [S U1] ── [A1 U2]
   free(kv[0:210 的重复段]) —— 本请求这次没用旧槽位（match 来的），
     若 req_to_token 里这段与其插入 value 重复则精确释放
   dec_lock_ref([S U1]) → lock_ref=0，回到 evictable
```

**第 3 轮（prefill [S,U1,A1,U2,A2,U3]）**：match 命中 230 token，只 prefill U3 的 10 个；完成后树变成三层链。**每一轮的增量 prefill 都只有新增部分**——这就是 RadixAttention 在多轮对话里的复利。

**显存压力时刻**：新请求潮水般涌入，allocator 空闲不足 → `alloc_token_slots` 循环 evict：堆顶是最久未访问的叶子（比如某条冷门分支），free 它的槽位、摘节点、父链塌缩。而正在对话中的 `[S U1] ...` 路径因有请求挂着（lock_ref>0）被完整保护。请求被逐出 running batch 时（retraction），`batch_result_processor` 调 `cache_unfinished_req` 把已算部分入库并迁移锁——被逐出 ≠ 缓存丢失，回来时还能命中。

---

## 十、关键设计决策

1. **radix 树而非哈希表**。哈希前缀缓存（vLLM 早期自动前缀缓存的思路）只能整段精确命中，要求请求前缀与缓存条目边界完全对齐；radix 树的边是**任意长 token 段**，匹配可在任意位置分岔（`_split_node` 惰性分裂），于是**任意长度的公共前缀都能复用**，且共享是自动的：两个请求只要前缀有交集，树上就走同一条路径、value 指向同一批槽位。配套地，`child_key`（L180-190）把"找下一层"做成 O(1) 哈希查找，避免了朴素 trie 每 token 一层的深递归。代价是树操作比哈希查询贵，但相比省下的 prefill FLOPs 完全可忽略——这正是 RadixAttention 作为 SGLang 招牌技术的立身之本。
2. **"目录与仓库分离"：树存索引、池存数据**。`value` 是 int64 槽位张量而非 KV 数据，使树的分裂/合并/淘汰都是纯元数据操作（分裂只 clone 索引张量，L681-684），不触碰显存里的大 KV 张量；同时让淘汰语义退化为一次 `allocator.free(x.value)`（L577），与分配器的 buddy/paged 实现完全解耦。`evicted` 节点保留 key 骨架（L235-237）也源于此——目录条目可以比库存活得久，为 HiCache 的 host 备份恢复留下路径信息。
3. **锁是"路径引用计数"而非全局位图**。`inc_lock_ref` 沿匹配末端到根整条链 +1（L590-603），配合"只淘汰叶子 + 父节点塌缩晋升"（L581-583），从结构上排除了"删掉在用前缀"的可能：任何在用前缀的末端有锁→沿路全有锁→全不可淘汰。`evictable_size_`/`protected_size_` 只在 0↔1 边界记账（L596-599），共享前缀的多请求几乎零额外成本。这是无锁并发缓存里最朴素也最稳的方案（本类本身单线程使用——Scheduler 事件循环内调用，无并发问题）。
4. **页对齐内建于 key 层**。`page_aligned`/`match(page_size)`/`child_key(page_size)` 把 paged KV 布局的约束（复用必须整页）压进 RadixKey 语义里（L122-126, L149-178, L180-190），于是上层 `insert`/`match_prefix` 的代码几乎看不到 page_size 的特判——只在 `cache_protected_len` 的所有权边界处理上露出一点复杂度（L533-537）。同理，EAGLE bigram 也压进 key 视图（`maybe_to_bigram_view` O(1) 翻转，L128-139），避免了整套独立的 bigram 树实现。**"把变体压进 key 抽象"是这个文件最值得学的重构手法**。
5. **摊销式淘汰维护**。读路径刷时间戳（顺手）、`_update_leaf_status` 增量维护叶子集合（O(度)）、排序延迟到 `evict` 现场建堆（L568-571）——热路径（每次匹配/插入）保持近乎零簿记，冷路径（显存吃紧才发生的淘汰）一次性付清排序成本。对每秒数千次匹配的服务负载，这个成本分布是唯一合理的形态。

---

## 十一、常见问题与误区

**Q1：为什么不用 LRU 链表（双链表+哈希）而用堆 + 集合？**
`evictable_leaves` 是 set，evict 时现场 `heapify`（L567-571）。看似每次 evict O(n log n)，但 evict 是低频事件；而 LRU 链表需要在**每次** match/insert/lock 变化时维护全局顺序，热路径成本更高。且淘汰策略可插拔（LFU/FIFO/...），链表方案只对 LRU 自然。摊销思路下集合+现场堆是更通用的选择。

**Q2：匹配到的 KV 槽位会不会中途被 evict？**
不会。Scheduler 拿到 `MatchResult` 后立刻 `inc_lock_ref(last_device_node)`（在 `cache_unfinished_req` L540 与调度流程中），槽位在锁路径上；evict 只从 `evictable_leaves` 取候选，带锁节点早被 `_update_leaf_status` 移出（L785-787）。风险窗口只在"match 返回与 inc 之间"，而这两步在同一个调度循环内同步完成。

**Q3：`_split_node` 时 lock_ref 全给了前缀段，后缀段岂不是丢了保护？**
若原 child 有锁，分裂后 new_node.lock_ref = child.lock_ref（L679），child（后缀段）的锁清零。挂在这个节点上的请求 `req.last_node` 仍指向**原对象**（现在是后缀段 child），它 dec 时沿 child→new_node→...上行，语义仍正确（后缀段+前缀段路径）。这是"句柄不变、路径重组"的自然结果，不是缺陷——但值得意识到分裂会改变"哪个节点对象代表哪段前缀"。

**Q4：insert 时为什么不调 allocator.alloc？**
槽位在 prefill 阶段已由 `alloc_token_slots`（common.py:459-468）分配并写进 req_to_token；树只接管已有槽位的所有权。树与分配器之间唯一的反向接口是 `free`。若 insert 需要 alloc，就会出现在调度关键路径上同步等显存的局面，破坏"分配在前缀缓存决策之前完成"的分层。

**Q5：`evicted=True` 的节点为什么还留在树上？**
value=None 的节点保留 key/骨架（L235-237），`_match_prefix_helper` 匹配时照样会路过它（value 也在收集列表里，`torch.cat` 时空张量无害）。这样设计让 (a) HiCache 可以从 host 恢复 value；(b) 子孙若还有 value，路径仍然可达；(c) 事件系统的 hash 链不断。代价是树会缓慢积累空骨架，由 `_delete_leaf` 的父链塌缩在淘汰时逐步清理。

**Q6：`disable_finished_insert`（L444-445）和 `disable`（L448-453）有什么区别？**
`disable` 彻底关闭前缀缓存：不匹配（L401-402 返回空）、不插入、请求完结直接 free 全部槽位。`disable_finished_insert` 只关闭"完结入库"：运行中请求仍可互相通过 `cache_unfinished_req` 共享（那是调度正确性的一部分），但完结的 KV 不长期留存——用于确定性输出等特殊需求，是更细粒度的开关。

**Q7：这个类线程安全吗？**
类内部无锁。它运行在 Scheduler 的单线程 asyncio 事件循环里（TPOT 关键路径上的调用都是同步的），唯一并发来源是 HiCache 的异步搬运，那由独立的 `host_ref_counter` 保护（L243-252）。把 RadixCache 挪到多线程环境需要自己加大锁或改造成分片树。

---

## 十二、阅读建议

1. **先跑文件尾的 demo**（L812-826）：`python radix_cache.py` 直接执行，5 次 insert + 1 次 match_prefix 后 `pretty_print()` 打印树形。对着第六节的逐步演化理解"边压缩"与匹配分裂，十分钟建立直觉。
2. **按"一个请求的一生"读调用链**：`match_prefix`（prefill 准入，Scheduler 里裁剪 extend 输入）→ `cache_unfinished_req`（chunk 边界/被逐出时，注意锁迁移与 req_to_token 回写）→ `cache_finished_req`（完结，注意 `cache_protected_len` 到 `prefix_len` 的 free 区间）。每一站都问三个问题：哪些槽位转移了所有权？锁挂在哪个节点？req_to_token 是否同步？
3. **把不变量当 checklist**：(a) `evictable_size_ + protected_size_ ==` 树上未淘汰 token 总数；(b) 带锁节点不在 `evictable_leaves`；(c) 任一时刻，运行中请求的 `prefix_indices` 指向的槽位要么被其 `last_node` 路径锁住、要么属于请求私有尾巴。读懂代码后可以试着在 `pretty_print`/`sanity_check`（变体里有现成实现，如 swa_radix_cache.py L291）里验证这些不变量。
4. **对照 `base_prefix_cache.py` 读接口演进**：参数对象（`InsertParams` 等）看似啰嗦，实为变体族（SWA/Mamba/Chunk）预留的稳定协议——猜测每个字段"哪个变体会用"，是理解整个 mem_cache 目录结构的捷径。
5. **延伸阅读顺序**：`memory_pool.py`（token_to_kv_pool 分配器的 alloc/free 语义）→ `common.py`（调度侧粘合：alloc_token_slots 的"先 evict 后 alloc"循环）→ `swa_radix_cache.py`（看双池变体如何复用本文件骨架）→ RadixAttention 原始论文（*RadixAttention: Efficient Context Reuse for Multi-Turn LLM Serving*，SGLang 团队，2024）对照"aware prefix cache"的动机与收益数据（多轮对话场景命中率与吞吐提升）。
6. **性能视角**：注意两处 TODO（L90, L148 的 PyLong boxing）指向的纯 Python 匹配开销；以及 `value.append(child.value)` + `torch.cat`（L410-411）每次匹配都拼接新张量——超长前缀场景这是热点。可以思考：如果换成 C++/Rust 扩展树 + 预分配输出缓冲，哪些接口语义必须保留？（提示：参数对象协议和 MatchResult 的节点句柄是外部世界的全部依赖。）
