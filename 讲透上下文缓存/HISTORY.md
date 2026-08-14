# 讲透上下文缓存 · 思想史

> **一句话定位**：上下文缓存是一条 65 年的思想弧线——"如何避免重复计算我们已经知道的东西"——从 Wilkes 的"从属存储器"（1965）到 Atlas 虚拟内存（1961），到 Redis（2009），到 vLLM 的 PagedAttention（2023），再到 Anthropic 把 prompt caching 定价成 90% off 的产品功能（2024）。每一次范式转移，**被缓存的"东西"变了**：原始字节（1960s-2000s）→ 计算结果（2000s-2020s）→ 神经中间表示（2023-）。
>
> **与 KV Cache 系列的互补关系**：[`讲透KV Cache/`](../讲透KV Cache/) 偏**底层**——KV Cache 的数学、显存账、PagedAttention/MLA/量化的架构深挖；本篇偏**应用层与思想史**——缓存概念怎么从 OS 流入 LLM，怎么从引擎技巧变成 API 定价。两者交叉点在 vLLM PagedAttention 和 SGLang RadixAttention。

---

## 0. 方法论：为什么上下文缓存需要思想史

### 0.1 年代史陷阱

如果你搜索"LLM prompt caching"，你会得到一条时间线：

```
2023.06  vLLM 发布，PagedAttention
2023.12  SGLang arXiv，RadixAttention
2024.08  Anthropic Prompt Caching 上线
2024.10  OpenAI Prompt Caching（自动）
2024.05  Gemini Context Caching 预告
2024.??  DeepSeek Context Cache
2025     Augment Context Engine / 模块化缓存
```

**这种讲法的问题**：它告诉你"发生了什么"，不告诉你**为什么此时发生**。为什么 prompt prefix caching 直到 2023 年才出现，而不是 2017 年 Transformer 论文发表时？为什么是 API 厂商（Anthropic/OpenAI）而非推理引擎（vLLM/TGI）最终把它推向大众？为什么 90% off——而不是 50% off 或 95% off？

### 0.2 思想史问的问题

本篇追问：

| 问题 | 思想史答法 |
|---|---|
| 为什么 2023 才有 LLM prefix caching？ | 2022 ChatGPT 之后 API 经济爆发，重复 prefix 成了肉眼可见的成本黑洞 |
| 为什么 PagedAttention 照搬 1961 年虚拟内存？ | 因为 KV Cache 在显存里面临的问题和 1961 年物理内存完全同构——碎片化、共享、按需分配 |
| 为什么是 LMSYS（Chatbot Arena 的人）发明了 RadixAttention？ | 因为做竞技场服务的人最先观察到"多请求共享前缀"这一模式 |
| 为什么 Anthropic 敢给 90% off？ | 因为 KV 计算的成本确实低——90% off 仍有利润，且是定价策略（锁用户） |

### 0.3 核心分析框架：WHAT 被缓存

贯穿全篇的主轴：**缓存技术的每一次范式转移，本质是"被缓存的计算产物"的抽象层级跃迁**。

```
1960s-2000s：缓存原始数据（字节/内存页/磁盘块）
              → 同一地址永远返回同一内容（确定性）

2000s-2020s：缓存计算结果（HTTP 响应 / Redis KV / CDN 内容）
              → 同一 key 永远返回同一 value（确定性 + 显式 key）

2023-：缓存神经中间表示（KV 张量）
              → 同一 prefix token 序列在同一模型同一权重下返回同一 K/V
              → 确定性 + 架构耦合 + 权重耦合

2025-：缓存语义模块（composable / semantic cache）
              → 相似但不相同的 prefix → 近似 K/V 复用
              → 非确定性！赌正确性
```

**越往下，缓存的"确定性"越弱，"正确性风险"越高。** 这正是本系列五幕的核心张力（见 [`04-不足-缓存失败模式.md`](./04-不足-缓存失败模式.md)）。

> 🎯 **博士级训练**：每个"突破"都问"被缓存的东西变了什么"——这比问"什么时候"深刻得多。

---

## 1. 前夜：OS / CPU / Redis 的缓存传统

### 1.1 缓存概念的诞生（1965）

**Maurice Wilkes**（剑桥，EDSAC 设计者）在 1965 年的论文中首次描述了一种"从属存储器"（slave memory）的概念：在主存和寄存器之间放一个小而快的存储层，存最近用过的数据。他后来回忆，灵感来自观察程序的行为模式——**同一块数据会被反复访问**。

"cache"一词来源法语 *cacher*（隐藏），暗示缓存对程序员是"隐藏的"——它不改变计算结果，只改变速度。**这个"不改变结果"的特性是传统缓存的灵魂**，也是 2024 年 prompt caching 敢于承诺"不改变输出质量"的理论基础。

### 1.2 虚拟内存：Atlas（1961）

比 Wilkes 的 cache 概念更早的是**曼彻斯特大学 Atlas 计算机**（1961，Tom Kilburn 团队）的**虚拟内存/分页机制**——这是计算史上最重要的缓存思想之一。

Atlas 解决的问题：程序需要的内存超过物理内存。方案——把物理内存分成固定大小的页（512 字），用一个"页表"把虚拟地址映射到物理地址，用不上时换到磁鼓（drum）上。

**这就是分页（paging）的诞生。** 62 年后，vLLM 的 PagedAttention 把同样的思想搬到了 GPU 显存上——把 KV Cache 空间分成 block，用 block table 映射逻辑序列。这不是类比，是**字面意义上的思想移植**。

### 1.3 CPU Cache 层级演化（1969-2010s）

| 年代 | 事件 | 意义 |
|---|---|---|
| 1965 | Wilkes "slave memory" | cache 概念诞生 |
| 1968 | **Peter Denning** "working set" model | 局部性原理的数学化（时间局部性 + 空间局部性）|
| 1969 | **IBM System/360 Model 85** | 首台商用 L1 cache（16-32KB）|
| 1980s | L2 cache 出现（板载）| 多级缓存层次确立 |
| 1995 | **Pentium Pro** 片上 L2 | L2 从板载移到芯片内 |
| 2000s | L3 cache 出现（AMD K6-III / Intel Core）| 三级层次：L1→L2→L3→DRAM |
| 2003 | **ARC**（IBM Megiddo & Modha）| 自适应替换算法，融合 LRU+LFU |

**局部性原理**（Denning 1968）是整个缓存大厦的地基：**程序倾向于反复访问最近用过的数据（时间局部性），以及访问空间上相邻的数据（空间局部性）。** 没有局部性，缓存就没意义。

**对 LLM 的启示**：LLM 推理有没有局部性？有——**system prompt / few-shot / 文档前缀是"时间局部性"**（多请求反复用同一前缀），**因果注意力的递推性是"空间局部性"**（前缀 token 的 K/V 只依赖更早的 token，可以增量缓存）。vLLM 和 SGLang 的全部有效性建立在这两点上。

### 1.4 Belady 1966：理论最优替换

Laszlo Belady 1966 年提出：**如果你知道未来访问序列，最优替换策略是淘汰"未来最远才用到的"那个页。** 这就是 OPT/MIN，理论天花板，现实中无法实现（不能预知未来）。

但它提供了两个洞察：
1. **所有实际策略（LRU/LFU/ARC）都是对 Belady 的近似**——它们用历史模式预测未来
2. **LLM 场景可以部分预知未来**——同一个 system prompt 的高频复用模式是可观测的。这给了 prompt caching 比传统 OS cache 更高的命中率潜力

### 1.5 Redis：应用层缓存的王者（2009）

2009 年，意大利程序员 **Salvatore Sanfilippo**（网名 antirez）为自己的实时网站分析工具 LLOOGG 需要一个高性能数据结构服务器，写了 Redis。最初的想法很简单：**把数据库查询结果存在内存里，加上 TTL 和 LRU 淘汰，避免重复查库。**

Redis 的核心创新不是速度（memcached 更早），而是**丰富的数据结构 + 持久化 + 发布订阅**。它让"缓存"从"key→value 字符串"进化到"key→复杂结构可原子操作"。

**Redis 与 prompt caching 的类比**：

| Redis | Prompt Caching |
|---|---|
| key = 查询条件 | prefix = token 序列 |
| value = 查询结果 | value = KV 张量 |
| TTL = 过期自动删除 | TTL = 5 分钟自动失效 |
| LRU = 满了淘汰最旧 | LRU = 显存满了淘汰最旧 |
| 写入 = 一次查库 | 写入 = 一次前向传播 |
| 命中 = 跳过查库 | 命中 = 跳过前向传播 |

**几乎完全同构。** 这不是巧合——prompt caching 就是"把 Redis 的模式搬到 Transformer 推理上"。区别在于：Redis 缓存的是数据库的确定输出，prompt caching 缓存的是神经网络前向传播的中间态（KV）。

> 🎯 **思想史洞察**：从 Wilkes（1965）到 antirez（2009），缓存技术的对象始终是**确定性数据**——同 key 永远返回同 value。2023 年的范式转移打破了这个前提：LLM 缓存的对象是**架构耦合的神经表示**——同 prefix 在同模型同权重下才返回同 K/V。

---

## 2. CDN 与 Web 缓存：从"缓存数据"到"缓存计算结果"

### 2.1 Akamai（1998）：地理缓存的诞生

1998 年，MIT 数学家 **Tom Leighton** 和研究生 Danny Lewin 创立 Akamai。他们的核心洞察：**互联网最大的延迟不是计算，是距离。** 如果在用户附近放一份网页副本，就不必每次都从源站拉。

这就是 CDN（Content Delivery Network）——**地理维度上的缓存**。它缓存的不再是"字节"或"内存页"，而是**整个 HTTP 响应——一次计算的完整输出**。

这是一个微妙的但重要的转变：**缓存的抽象层级上移了。** CPU cache 对程序员透明（硬件管）；Redis 对业务透明（中间件管）；CDN 对源站透明（网络层管）。每上移一层，缓存的对象离"用户的真实需求"更近。

### 2.2 HTTP 缓存协议

HTTP 的设计者（Roy Fielding 等）为缓存设计了精巧的协议层：

- **Expires / Cache-Control**：声明内容何时过期（TTL 的鼻祖）
- **ETag**：内容的指纹，用于条件 GET（"内容变了吗？"）
- **304 Not Modified**：内容没变，不传 body（cache hit 的协议化）

**这套机制深刻影响了 prompt caching 的设计**：
- Anthropic 的 `cache_control: {type: "ephemeral"}` 就是 HTTP 的 `Cache-Control`
- 5 分钟 TTL 就是 HTTP 的 `max-age=300`
- 前缀严格匹配就是 HTTP 的 ETag 精确匹配
- cache miss → 写入 → 下次命中，和 HTTP 完全一致

### 2.3 Varnish / Squid / Nginx：缓存即基础设施

2000s-2010s，Varnish（2006）、Squid（1996）、Nginx（2004 缓存功能）把 HTTP 缓存变成了基础设施。所有高流量网站都在用"源站 + CDN + 边缘缓存 + 应用缓存（Redis）+ 数据库缓存"的**多层缓存层次**——和 CPU 的 L1→L2→L3→DRAM 层次结构惊人地同构。

这种多层结构反映了一个深层规律：**缓存的本质是用"便宜但有限的存储层"吸收"昂贵计算的重复请求"，层次越多，说明计算与存储之间的价格落差越大。** CPU 的 L1 比 DRAM 快 100 倍但小 1000 倍；CDN 边缘节点比源站近 10 个路由跳但存储有限；Redis 比数据库快 10000 倍但内存贵 10 倍。

**这正是 2023 年 LLM 推理系统走的路**：GPU KV Cache（L1）→ CPU KV offload（L2）→ SSD 分层（L3）→ 远端模型重算（DRAM/源站）。vLLM 和 SGLang 的"分层 KV Cache"研究方向（见 [`讲透KV Cache/06-分层KV Cache`](../讲透KV Cache/)），本质是在 LLM 上重建 CPU 的多级缓存层次。GPU HBM 带宽远高于 CPU DRAM，但容量极小（80GB vs 1TB）——这种极端的带宽-容量落差让 KV Cache 的分层管理比传统场景更紧迫，也更有收益空间。

> 🎯 **范式转移预兆**：CDN/HTTP 缓存已经开始缓存"计算结果"而非原始数据。但 HTTP 响应仍是确定性输入→确定性输出的简单映射。**下一步——缓存神经网络的中间态——需要先等神经网络本身成为主流计算范式。** 这一等就是 15 年。

---

## 3. 第一次范式转移：LLM prompt prefix caching（2023）

### 3.1 旧范式的反常累积

到 2022 年底 ChatGPT 爆发，LLM 推理服务面临一个"旧范式解释不了"的反常：

**同一个 system prompt 被数百万请求反复传入，每次都要重新跑一遍前向传播。** 这在传统 web 服务里是不可思议的——你不会每次查同一个 SQL 都重新编译查询计划。但 Transformer 推理没有"查询计划缓存"这一层。

反常的三重来源：
1. **经济反常**：成本结构不可持续——API 调用中 80%+ 的 token 是重复的 system prompt / few-shot
2. **延迟反常**：首 token 延迟（TTFT）高得离谱，因为每次都要重算整个前缀
3. **显存反常**：每个请求各自存一份完整 KV Cache，相同前缀被存了 N 份

### 3.2 vLLM PagedAttention：OS 虚拟内存的复活（SOSP 2023）

**2023 年 10 月**，UC Berkeley 的 **Woosuk Kwon** 等人在 SOSP（Symposium on Operating Systems Principles）发表 *Efficient Memory Management for Large Language Model Serving with PagedAttention*（vLLM）。

**核心突破**：把 Atlas 1961 年的分页虚拟内存思想**完整搬到了 GPU 显存管理**。

具体做法（详见 [`讲透KV Cache/02-PagedAttention深挖`](../讲透KV Cache/02-PagedAttention深挖.md)）：
1. 把 KV Cache 空间分成固定大小 block（如 16 token/block）
2. 用 block table 把逻辑序列映射到物理 block（= OS 的页表）
3. 相同前缀物理共享（= OS 的 copy-on-write 共享内存）

结果：**吞吐量提升 2-4 倍**。这不是算法创新——是**把 62 年前的 OS 思想第一次正确地用在了神经计算上**。

**为什么是 Berkeley？为什么是 SOSP？**

这不是巧合。Berkeley 有 Ion Stoica、Joseph Gonzalez——他们同时是 **Ray**（分布式计算）和 **Databricks** 的创始人。SOSP 是操作系统顶会。vLLM 的核心团队来自 Sky Computing Lab，他们的世界观是"用 OS 思想解决 ML 系统问题"。**如果这个团队来自纯 ML 背景，可能不会有 PagedAttention——他们不会想到把虚拟内存搬过来。**

> 🎯 **路径依赖**：PagedAttention 的诞生依赖一个特定的思想杂交——OS 体系结构思维 × ML 推理。少了任何一端，这个突破可能推迟数年。

### 3.3 为什么这是范式转移（而非渐进改进）

按 Kuhn 的判据：
1. ✅ **旧范式反常累积**：成本/延迟/显存三重不可持续
2. ✅ **新范式解释反常**：PagedAttention 一次性解决了碎片化 + 前缀共享 + 显存利用率
3. ✅ **不可通约性**：PagedAttention 之前的推理引擎（HuggingFace Transformers、TGI）的 KV 管理范式与 PagedAttention 根本不同——不是"改参数"，是"换管理哲学"

**WHAT 被缓存的跃迁**：从"数据"到"神经中间表示"。CPU cache 存的是原始数据；Redis 存的是确定输出；**vLLM 存的是 Transformer 前向传播的 K/V 张量**——一种**架构耦合、权重耦合**的计算产物。换个模型或换个权重，同一 prefix 的 K/V 完全不同。

这是思想史意义上的新物种。

---

## 4. SGLang RadixAttention：从单请求到跨请求的 KV 复用

### 4.1 单请求缓存不够

PagedAttention 解决了"一个请求内的 KV 管理"，但还有一个维度没碰：**跨请求的 KV 共享**。

如果你的 API 网关收到 1000 个请求，它们都带同一个 system prompt（"你是一个有帮助的助手"），朴素做法是每个请求各自算一遍前缀的 K/V。PagedAttention 虽然支持 copy-on-write 共享，但需要显式管理。

**能不能自动做？**

### 4.2 RadixAttention：基数树管理一切（2023.12）

**2023 年 12 月**，LMSYS 的 **Lianmin Zheng** 和 **Ying Sheng** 等人在 arXiv 发表 *Efficiently Programming Large Language Models using SGLang*（arXiv:2312.07104），2024 年 1 月 17 日发布正式博客。

**RadixAttention 的核心**：用**基数树（radix tree）**自动管理所有活跃请求的 KV Cache。

基数树是一种空间高效的 trie 变体——边可以标注任意长度的序列，而非单个元素。SGLang 用它管理一个映射：**token 序列（键）→ KV 张量（值）**。

工作机制（摘自 SGLang 博客）：
1. 每个请求来时，runtime 自动做前缀匹配——找到树中最长的公共前缀
2. 命中部分直接复用 KV，只算新的部分
3. 用完的 KV 不丢弃，插入树中（LRU 淘汰）
4. 树结构存在 CPU 上，维护开销极小

**关键数据**：在 MMLU、HellaSwag、ReAct Agent、Tree-of-Thought 等基准上，SGLang 比 vLLM/Guidance/TGI **快最高 5 倍**。

### 4.3 为什么是 LMSYS

LMSYS 是做 **Chatbot Arena**（大模型竞技场）的组织。竞技场是一个**天然的多请求共享前缀**场景：成千上万用户问不同问题，但都带相同的 evaluation prompt 模板。

**正是因为运营竞技场，LMSYS 团队第一个大规模观察到"KV cache reuse patterns"**——他们博文中列出了四种模式：few-shot 共享、self-consistency 多采样共享、多轮对话历史共享、tree-of-thought 搜索路径共享。

> 🎯 **思想史洞察**：RadixAttention 不是在实验室里想出来的——是从运营真实 LLM 服务中"长出来的"。**应用场景塑造技术**，这和 Anthropic 从做 Claude 产品中发现 prompt caching 的需求是同一逻辑。

### 4.4 从"被动缓存"到"主动调度"

RadixAttention 还做了一个 OS 级的跃迁：**cache-aware scheduling**。不只是"来了请求就查缓存"，而是"根据缓存命中概率**调度请求执行顺序**"——优先执行能命中缓存的请求，提高整体命中率。

这回到了 Belady 1966 的精神：**如果能部分预知未来访问模式，就能做比 LRU 更好的调度。** SGLang 的 cache-aware scheduler 正是这一思想的工程化。

---

## 5. 第二次范式转移：API 级 prompt caching（Anthropic/OpenAI 2024）

### 5.1 从引擎技巧到定价功能

PagedAttention（vLLM）和 RadixAttention（SGLang）是**引擎层**的技术——只有自部署的人受益。对 95% 使用 API（Anthropic/OpenAI/Google）的开发者来说，这些技术完全不可见。

**2024 年发生的事情，是把这个技术从引擎层"上提"到 API 产品层——变成一个开发者可见、可计费、可定价的功能。** 这是范式转移：缓存不再是"实现细节"，而是"产品特性 + 定价策略"。

### 5.2 Anthropic Prompt Caching（2024.08.14）

**2024 年 8 月 14 日**，Anthropic 发布 Prompt Caching（beta）。这是**第一家主流 LLM API 厂商**把前缀缓存做成产品功能。

定价设计（摘自 Anthropic 官方文档，以当前模型为例）：

| 计费项 | 相对于 base input 的倍数 | 含义 |
|---|---|---|
| Base Input Tokens | 1.0× | 正常输入价格 |
| 5m Cache Write | **1.25×** | 首次写入贵 25% |
| 1h Cache Write | 2.0× | 1 小时 TTL 更贵 |
| Cache Read（命中）| **0.1×** | 命中只付 10% |
| Output | 正常 | 不受影响 |

**5 分钟 TTL**：默认缓存生命周期。每次命中会刷新 TTL（免费）。

**核心限制**：前缀必须**严格字节级相同**（包括图片）。改一个 token → 哈希不匹配 → 全部 miss。

**最小可缓存长度**：512-4096 token（因模型而异）。短于这个长度的前缀无法缓存。

**2024-2025 的演化**：
- 自动缓存（automatic caching）：加一个顶层 `cache_control`，系统自动管理断点
- 1 小时 TTL：解决"5 分钟太短"的问题
- 4 个断点：支持不同变更频率的多段缓存
- Pre-warming：`max_tokens=0` 预热缓存，消除首个请求的 miss 延迟

### 5.3 OpenAI Prompt Caching（2024.10）

**2024 年 10 月**，OpenAI 跟进。与 Anthropic 的关键差异：

| 维度 | Anthropic | OpenAI |
|---|---|---|
| 触发方式 | 显式 `cache_control` | **自动**（>1024 token 自动启用）|
| 折扣 | 命中 90% off | 命中 **50% off** |
| 写入溢价 | 25% 贵 | **无溢价**（正常 input 价格）|
| TTL | 5 分钟（可选 1 小时）| 约 5-10 分钟（未公开精确值）|

**OpenAI 的策略哲学**：零配置、零溢价、但折扣更少。它赌的是"自动化 > 深度优化"——大多数用户懒得手动管理断点，自动启用覆盖面更广，50% off 足够吸引人。

**Anthropic 的策略哲学**：给高级用户最大收益（90% off），但要求主动配置。它赌的是"重度用户愿意优化"——客服系统、coding agent 等高频场景，90% off 的收益碾压配置成本。

> 🎯 **思想史洞察**：同样的底层技术（prefix KV reuse），两家厂商的产品化哲学完全不同——OpenAI 偏"苹果式零配置"，Anthropic 偏"Linux 式高控制力"。这不是技术选择，是**产品哲学选择**。

### 5.4 Google Gemini Context Caching（2024）

Google 的 Gemini 走了第三条路：**显式缓存对象**。

用户可以调用 API **创建一个 cache 对象**（`cached_content`），指定内容和 TTL，然后用这个 cache 对象引用来发请求。TTL 可设为小时级甚至天级。

这比 Anthropic 的 5 分钟 TTL 灵活得多，适合需要**长期持有大上下文**的场景（如把整本书/整个代码库缓存数天）。

### 5.5 DeepSeek Context Cache（2024）

DeepSeek 作为开源/低成本 API 代表，也内置了 context cache——**命中自动复用，无需配置**。结合其 MLA（Multi-head Latent Attention，见 [`讲透KV Cache/04-MLA深挖`](../讲透KV Cache/04-MLA深挖.md)）把 KV 压缩 10-90 倍，成本极低。

### 5.6 为什么是范式转移

这次范式转移的标志不是技术突破（底层 KV reuse 2023 年已有），而是：

1. **市场验证**：90% off 的定价意味着厂商确认"前缀计算确实占了 90% 的边际成本"——**价格即真理**
2. **开发者心智改变**：从"每次请求都重新算"变成"重复 prefix 应该缓存"成为默认假设
3. **应用层重构**：coding agent、RAG 系统、客服系统的架构开始围绕"缓存友好"重新设计（固定前缀在前、动态内容在后）

---

## 6. 第三次范式转移：模块化 / 可组合缓存（2025-）

### 6.1 从前缀匹配到语义匹配

prompt caching 的根本局限：**只认字面前缀**。"怎么退款"和"如何退钱"字面不同 → 无法复用 KV。

2025 年的前沿方向试图打破这一限制：

**语义缓存（Semantic Caching）**：把 query 转 embedding，在缓存库中找 cosine 相似度 > 阈值的历史 query，命中则直接复用答案（不是复用 KV，是复用最终输出）。

这是**认知复杂度的跳跃**（见 [`01-直觉`](./01-直觉-缓存即预计算的回忆.md) 的阶梯图）：从"确定性复用"（prefix KV）到"概率性复用"（embedding 相似度）。它赌的是"相似问题有相似答案"——但这个赌注有时是错的（"退款金额" vs "退款流程"，embedding 近但答案异）。

### 6.2 Augment Context Engine：60 万 token 的魔法（2025）

2025 年 coding agent 公司 Augment 推出 Context Engine，号称**真实可用 60 万 token**——远超一般模型的有效范围。

秘密不是窗口大，而是**大规模语义索引 + 智能检索 + 多层缓存**：
1. 整个代码库语义索引（embedding + 倒排）
2. 用户提问时实时检索最相关片段
3. 配合 prompt caching 让常用上下文不重算

**这其实是 RAG + 缓存的深度工程组合**，但工程做到极致，让"60 万可用"不是营销词。

**思想史意义**：Augment 代表了"缓存不再是单一技术，而是 context 管理栈的核心组件"。未来的竞争力不在窗口大小，在**context 编排能力**——缓存、检索、压缩、记忆的协同。

### 6.3 模块化推理：KV 的可组合性

更前沿的方向：**把 KV Cache 按"语义模块"拆分**，不同模块独立缓存、跨请求自由组合。

设想：
- system prompt 的 KV 是一个模块
- 工具定义的 KV 是另一个模块
- 用户消息的 KV 是第三个模块
- 不同请求按需拼接模块的 KV，而非每次重算

这类似 OS 的**动态链接库（DLL/so）**——共享代码段而非复制。但 Transformer 的因果注意力让"中间插入"很困难（前缀变了后面全失效），所以当前实现仍局限于前缀拼接。

**DeepSeek MLA**（Multi-head Latent Attention）从另一个角度解决：不缓存完整 KV，而是缓存**压缩后的潜在向量**，按需解压——把 10-90 倍的 KV 压缩成一个小向量。这更接近"信息蒸馏"而非传统缓存。

### 6.4 这个范式转移成熟了吗？

**还没。** 2025-2026 的状态是"前缀缓存已成熟，语义/模块化缓存仍在探索"。真正成熟的标志会是：
- 语义缓存的假命中率降到可接受水平（< 0.1%）
- 跨请求模块组合有标准协议
- 长期知识从"缓存"迁移到"记忆层"（见 [`讲透记忆/`](../讲透记忆/)）

值得注意的是，这个方向面临一个根本性的认识论困难：**语义缓存要求系统"理解"两段文本是否真正等价，而这恰恰是 LLM 本身的能力。** 用 LLM 判断"是否可以复用缓存"再用 LLM 生成——这个判断本身也要花钱算。如果判断成本接近生成成本，缓存就失去了意义。所以语义缓存的可行边界，取决于"判断相似性"能否比"重新生成"便宜得多——这又回到了 embedding 模型的质量与速度问题。当前 embedding 判断比完整生成便宜约 100-1000 倍，所以经济上是可行的；但精度问题（假命中）才是真正的瓶颈。

---

## 7. 长上下文 LLM 与缓存的张力

### 7.1 一个反直觉的矛盾

直觉上，长上下文（1M token window）和缓存是盟友——窗口越大，能缓存的越多。**但实际是张力关系：**

| 维度 | 长上下文 | 缓存 |
|---|---|---|
| 成本 | 线性增长（每 token 都贵）| 命中后几乎免费 |
| 延迟 | 首 token 延迟随长度上升 | 命中降低首 token 延迟 |
| 显存 | KV Cache 随长度线性膨胀 | 共享缓解膨胀 |
| 有效注意力 | "needle in haystack"——越长越容易忽略中间 | 缓存不解决注意力衰减 |

**核心矛盾**：长上下文让"可以缓存的东西"变多，但让"必须重新计算的东西"也变多（因为用户消息在变）。如果 1M token 中 99 万是固定的 system prompt，缓存收益巨大；但如果每条消息都在变，缓存命中率反而低。

### 7.2 Gemini 1M / Claude 扩展上下文

Google Gemini 1.5 Pro 宣称 1M token（后 2M）。Claude 从 100k 扩展到 200k（部分模型支持 1M+）。

**但"宣称窗口"≠"有效窗口"**。多项研究（如 Needle In A Haystack 压力测试）表明：大多数模型在超过 32k-64k 后，注意力质量显著下降。这意味着**长上下文的前半部分可能被"忽略"**——你缓存了它，但模型用不好它。

这催生了一个悖论：**缓存让长前缀"便宜"，但不让长前缀"有用"。** 成本和质量的解耦。

### 7.3 KV 压缩：缓存的减法哲学

既然长上下文的 KV 太大，一个方向是**压缩 KV 本身**：
- **GQA / MQA**（分组/多查询注意力）：减少 KV 的头数
- **MLA**（DeepSeek）：KV 压到潜在空间，10-90 倍压缩
- **KV 量化**：FP8/INT4/1.58-bit，精度换空间
- **KV 剪枝**：丢弃不重要的 KV 条目

详见 [`讲透KV Cache/04-MLA深挖`](../讲透KV Cache/04-MLA深挖.md) 和 [`讲透KV Cache/05-KVCache量化`](../讲透KV Cache/05-KVCache量化.md)。

**思想史意义**：这些技术是缓存哲学的"减法"——**不是存更多，而是存得更精简。** 它和道家"无为而无不为"（去掉冗余反而增强）高度同构。

从思想史角度看，KV 压缩代表了缓存演化的一个新分支：**不是在"缓存什么"的维度上创新（那是前三节的故事），而是在"缓存多少"的维度上做文章。** 传统缓存的命中率优化是"存对的东西"，KV 压缩是"用更少的空间存同样的东西"。这两条线在 2025 年开始交叉——MLA 压缩后的 KV 仍可被 prefix caching 复用，SGLang 的 RadixAttention 也兼容量化后的 block。最终极的目标是：在有限 GPU 显存内，同时实现"高命中率"（多存）和"低显存占用"（少存每份）——这是两个看似矛盾的方向的辩证统一。

---

## 8. 思想史反思：5 个反常识

### 8.1 PagedAttention 是 1961 年 Atlas 分页的转世

vLLM 的 PagedAttention 不是新发明——它是 Tom Kilburn 1961 年在 Atlas 上实现的**虚拟内存分页机制**的字面移植。block table = page table；copy-on-write prefix 共享 = shared memory pages；按需分配 block = demand paging。

**62 年的思想延迟。** 为什么这么久？因为中间 62 年没有"神经中间表示需要内存管理"这个问题域。Transformer 2017 才诞生，KV Cache 的显存问题 2022 年 ChatGPT 后才爆发。**思想等了合适的载体 62 年。**

### 8.2 90% off 是定价决策，不是技术突破

Anthropic 的 90% off 不是因为他们的缓存算法比 vLLM 好 9 倍。**是因为他们选择把节省的绝大部分让利给用户。** 这和当年 AWS 对 Spot Instance 降价 90% 的逻辑一样——**定价是锁用户的武器**。一旦你的系统围绕 Anthropic prompt caching 设计了（前缀结构、断点位置），迁移到 OpenAI（50% off）意味着重构。

> 🎯 **警惕"技术折扣"的营销**：90% off 是真实的技术基础 + 精明的定价策略。不要把定价当作技术实力的唯一指标。

### 8.3 SGLang 来自 Chatbot Arena，不是系统实验室

RadixAttention 来自 LMSYS——做**大模型竞技场**的组织。这不是一个传统的系统研究组（如 OSDI/SOSP 常见的 CMU/MIT 系统 lab）。它来自**运营真实 LLM 服务时的观察**。

**教训**：有时最好的系统创新来自"做应用的人被性能问题逼出来的方案"，而非"做系统的人找应用场景"。这和 Redis 来自一个网站分析工具（LLOOGG）的需求是同一逻辑——**应用驱动 > 技术驱动**。

### 8.4 长上下文与缓存是张力，不是协同

表面上看"窗口大→缓存多"，实际上**窗口大让有效缓存更难**：注意力衰减、KV 显存爆炸、命中率波动。真正让长上下文经济的不是更大的窗口，而是**更好的 context 管理**（缓存 + 检索 + 压缩 + 记忆的协同）。Augment 的 60 万 token 靠的不是大窗口，是 context 编排。

### 8.5 "Cache"是一个做了过度工作的隐喻

传统 cache（CPU/Redis/CDN）缓存的是**确定性产物**——同 key 永远返回同 value。LLM prompt cache 缓存的是**架构耦合的神经表示**——同 prefix 在同模型同权重同精度下才返回同 K/V。换模型、换权重、换量化精度，全部失效。

**这个区别被"cache"这个词掩盖了。** 当有人说"LLM 也有缓存"，你可能以为它和 Redis 一样通用。实际上它远更脆弱——**它是"特定计算图在特定参数下的中间态快照"**，不是"通用数据的快速副本"。

> 🎯 **博士级警示**：术语借用是双刃剑——它帮助直觉迁移，但也掩盖本质差异。"上下文缓存"借了"缓存"的壳，内核是一个全新的计算范式。

---

## 9. 关键人物 / 机构谱系

### 9.1 传统缓存谱系

| 人物 | 贡献 | 时代 |
|---|---|---|
| **Maurice Wilkes**（剑桥） | cache 概念（"slave memory"）| 1965 |
| **Tom Kilburn**（曼彻斯特） | Atlas 虚拟内存/分页 | 1961 |
| **Peter Denning**（Purdue） | working set / 局部性原理 | 1968 |
| **Laszlo Belady**（IBM） | OPT 最优替换算法 | 1966 |
| **Tom Leighton**（MIT → Akamai） | CDN / 地理缓存 | 1998 |
| **Salvatore Sanfilippo**（antirez） | Redis | 2009 |

### 9.2 LLM 缓存谱系

| 人物/团队 | 贡献 | 时代 |
|---|---|---|
| **Woosuk Kwon** 等（UC Berkeley） | vLLM / PagedAttention | 2023 |
| **Lianmin Zheng / Ying Sheng**（LMSYS） | SGLang / RadixAttention | 2023-2024 |
| **Ion Stoica / Joseph Gonzalez**（Berkeley → Databricks） | 背后的系统思维（Ray/Sky Lab）| 贯穿 |
| **Anthropic 工程团队** | 首个 API 级 prompt caching | 2024 |
| **DeepSeek** | MLA + context cache | 2024 |

### 9.3 师承与思想流动

```
Wilkes (1965 cache) → Denning (1968 locality)
                         ↓
                    OS cache hierarchy (L1/L2/L3)
                         ↓
Kilburn (1961 paging) → Atlas VM
                         ↓
                    vLLM PagedAttention (2023) ← Berkeley OS × ML 交叉
                         ↓
                    SGLang RadixAttention (2023) ← LMSYS 应用驱动
                         ↓
                    Anthropic/OpenAI/Gemini API caching (2024) ← 产品化
```

**关键杂交点**：Berkeley 的 Sky Computing Lab 是 OS 思想 × ML 推理的杂交地。没有这个特定的学术环境，PagedAttention 可能不会在 2023 年出现。

---

## 10. 失败方向与教训

### 10.1 任意位置缓存（非前缀）

**想法**：不只缓存前缀，缓存任意子串的 KV。

**为什么失败**：Transformer 的因果注意力决定了——token t 的 K/V 只依赖 t 之前的 token。所以只有"前缀"能安全复用。中间插入一段缓存的 KV，会破坏因果链。

**教训**：缓存的可行性受架构约束。换一种架构（如非因果/双向 attention），可能解锁任意位置缓存——但那不再是标准 LLM。

### 10.2 跨模型 / 跨版本 KV 复用

**想法**：模型 A 的 KV Cache 给模型 B 用。

**为什么失败**：KV 是**架构耦合 + 权重耦合**的。不同模型的隐藏维度、注意力头数、权重矩阵完全不同。A 的 KV 对 B 是噪声。

**教训**：神经中间表示不像 HTTP 响应那样可移植。这是 LLM 缓存与传统缓存的本质区别。

### 10.3 语义缓存的假命中

**想法**：用 embedding 相似度缓存"相似问题"的答案。

**现实**：精度不够。"退款金额"和"退款流程"embedding 很近，但答案完全不同。假命中比 miss 更危险——直接返回错答案。

**教训**：**确定性边界不能随意跨越。** 从 prefix 匹配到 embedding 匹配，是从"100% 确定"到"概率确定"的范式跳跃。生产系统的铁律是"宁可 miss 不要假命中"（见 [`04-不足`](./04-不足-缓存失败模式.md)）。

### 10.4 过度依赖 TTL

**问题**：Anthropic 5 分钟 TTL 对客服够（会话内），对长期知识不够。开发者把长期知识塞进 prompt cache，TTL 过期后命中率暴跌。

**教训**：**缓存解决"重复"，不解决"记忆"。** 长期知识属于记忆层（[`讲透记忆/`](../讲透记忆/)），不是缓存层。把两者混淆会导致架构混乱。

---

## 11. 路径依赖与偶然性

### 11.1 如果 Berkeley 没有 OS × ML 交叉环境

PagedAttention 需要同时懂 OS 虚拟内存和 ML 推理的人。如果 vLLM 团队来自纯 ML 背景（不会想到分页），或纯 OS 背景（不懂 Transformer），这个突破可能推迟数年。

**反事实**：如果 PagedAttention 推迟到 2025 年才出现，开源 LLM 服务生态会落后多少？SGLang 可能也不会那么快出现（RadixAttention 部分灵感来自 PagedAttention 的 prefix sharing）。

### 11.2 如果 LMSYS 没做 Chatbot Arena

RadixAttention 的四种 KV 复用模式（few-shot / self-consistency / 多轮对话 / tree-of-thought）全部来自运营竞技场的真实观察。如果 LMSYS 只做学术研究不做线上服务，可能不会发现这些模式。

**偶然性**：Chatbot Arena 本意是做模型评测，副产品是催生了 SGLang。**重大技术有时诞生于"顺便"。**

### 11.3 如果 Anthropic 不是第一个

如果 OpenAI 先发布 prompt caching（50% off），Anthropic 的 90% off 可能不会有同样的市场冲击力。**先发者定锚**——第一个公开 90% off 让所有人意识到"前缀计算占了 90% 成本"。如果先听到的是 50% off，行业对成本结构的认知会不同。

### 11.4 "缓存"这个词的路径依赖

如果 2023 年不用"cache"这个词，而是叫"KV reuse"或"prefix memoization"，开发者可能更早理解它的局限性（架构耦合、权重耦合）。**"cache"这个词带来了直觉（Redis 经验），但也掩盖了差异。** 这是术语路径依赖的典型——一旦叫开了，很难改。

---

## 12. 开放问题

1. **长上下文会杀死缓存吗？** 如果未来 100M token 窗口免费且无注意力衰减，还需要 prefix caching 吗？（不会——因为计算成本不消失，只转移）

2. **跨模型 KV 复用可能吗？** 如果有一个"通用 KV 表示"层（类似 IR 在编译器中的作用），不同模型共享 KV？（当前无解，但 MLA 的压缩思路可能是起点）

3. **语义缓存何时成熟？** 假命中率需要降到什么水平才"生产可用"？是否需要 LLM-as-judge 做二次确认？（参考 [`04-不足`](./04-不足-缓存失败模式.md)）

4. **缓存的"民主化"会到什么程度？** 当所有 API 都内置 caching，开发者还需要理解它吗？还是它完全隐形成基础设施？

5. **记忆层 vs 缓存层的边界在哪？** 5 分钟 TTL 是缓存，永久存储是记忆。中间地带（小时/天级）属于谁？

6. **模块化 KV 会成为标准吗？** "system prompt KV + tool KV + context KV" 分模块缓存、跨请求组合——这需要新的系统抽象和标准协议。

---

## 13. 配套资源

### 13.1 必读论文

| 论文 | 年份 | 核心 |
|---|---|---|
| Wilkes, "Slave Memories and Dynamic Storage Allocation" | 1965 | cache 概念诞生 |
| Denning, "The Working Set Model for Program Behavior" | 1968 | 局部性原理 |
| Belady, "A Study of Replacement Algorithms for Virtual-Storage Computer" | 1966 | OPT 最优替换 |
| Kwon et al., "Efficient Memory Management for LLM Serving with PagedAttention" (vLLM) | SOSP 2023 | OS 虚拟内存→KV Cache |
| Zheng et al., "Efficiently Programming Large Language Models using SGLang" | arXiv 2023.12 | RadixAttention |

### 13.2 关键文档

- [Anthropic Prompt Caching 官方文档](https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching)
- [SGLang 博客（RadixAttention 原始介绍）](https://lmsys.org/blog/2024-01-17-sglang/)
- [OpenAI Prompt Caching 文档](https://platform.openai.com/docs/guides/prompt-caching)

### 13.3 配套系列

- [`讲透KV Cache/`](../讲透KV Cache/)——底层深挖：数学、显存账、PagedAttention/MLA/量化
- [`讲透记忆/`](../讲透记忆/)——长期知识的归宿（缓存 vs 记忆的边界）
- [`讲透AI历史/`](../讲透AI历史/)——思想史方法论
- [`讲透代码生成/`](../讲透代码生成/)——coding agent 的 context 管理实践

### 13.4 关键代码库

- [vLLM](https://github.com/vllm-project/vllm)——PagedAttention 实现
- [SGLang](https://github.com/sgl-project/sglang)——RadixAttention 实现

---

## 14. 费曼回炉（L2 自检）

- **F2 卡壳点**：最初把"上下文缓存"当成一个单一技术（prompt caching），没有看到它背后 65 年的思想弧线。重读 Wilkes 1965 和 Atlas 1961 后才意识到——prompt caching 是"缓存神经中间表示"这一新范式的产品化，而它的方法论祖先（分页、LRU、TTL、局部性）全部来自 OS/CPU 时代。另一个误区是把"长上下文"和"缓存"当盟友——实际上它们是张力关系：窗口越大，有效缓存越难。
- **F3 术语翻译**：
  - "prompt prefix caching" → 不是"缓存提示词"，而是"缓存 Transformer 对提示词前缀做前向传播后的中间结果（K/V 张量）"——缓存的是**计算的副产物**，不是文本本身
  - "RadixAttention" → 用基数树（一种压缩前缀树）自动管理所有请求的 KV，让公共前缀自动共享——相当于"智能的、跨请求的 KV 复用调度器"
  - "cache hit" → 在 LLM 场景不是"数据找到了"，而是"同一段 token 序列在同模型同权重下的前向传播中间态还在"——一个远比 Redis hit 更脆弱的命中
- **F4 回炉**：v1 把演进写成"vLLM → SGLang → Anthropic"的线性技术升级。v2 改成三次**范式转移**的框架——每次转移"WHAT 被缓存"变了（数据→计算结果→神经中间表示→语义模块）。diff 是从"技术编年"升级为"思想史分析"：不只讲发生了什么，更讲"为什么此时"和"被缓存的东西本质变了什么"。

---

## 🎭 欺骗动力学视角

> 承接 [`欺骗动力学-社会进步的隐秘引擎.md`](../欺骗动力学-社会进步的隐秘引擎.md)。

### 三问

1. **讲透上下文缓存 思想史 防的是什么欺骗？** → 把"prompt caching"当成 2024 年横空出世的新技术，忽视它 65 年的 OS/CPU/Redis 血统。
2. **被什么攻破？** → 胜利者叙事（只讲 vLLM/SGLang/Anthropic，不讲 Wilkes/Kilburn/Denning）+ 术语膨胀（"cache"掩盖了架构耦合的本质差异）。
3. **沉淀进哪条主链？** → 验证主链——思想史方法揭示"被缓存的 WHAT"的层级跃迁，是对"新瓶装旧酒 vs 真新物种"的判断装置。

### 一句话

> "cache"这个词最大的欺骗在于让你以为 LLM 缓存和 Redis 缓存是一回事——其实它缓存的是架构耦合的神经中间表示，是一个全新的计算范式借了旧名字。
