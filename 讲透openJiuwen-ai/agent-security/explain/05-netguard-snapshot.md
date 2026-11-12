# 05 · netguard 快照校验架构：零网络调用的出站防护

> 定位：`tool_permission/netguard/` 自称 "W3 出站判定"（`netguard/__init__.py:3`）。它解决的问题是 SSRF/出站管控的经典难题——**权限引擎自己绝不做 DNS 解析**，而是校验宿主执行器提供的 DNS 快照。url_safety.py 做纯 URL 解析（"No DNS resolution"，`url_safety.py:3`），address_policy.py 校验快照地址分类（"without making network calls"，`address_policy.py:3`），net_urls.py 编译 URL 规则，component.py 聚合成 engine 第 9 号组件。`tests/netguard/test_audit_regressions.py` 的 17 个测试是四参考分支 W3 审计留下的绕过回归资产。

## 一、角色定位

传统出站防护有两条死路：权限引擎自己解析 DNS——TOCTOU 竞态（判定后、连接前 DNS 可换答案）+ 引擎被拖进网络 IO；只看 URL 主机名——`evil.com` 可以解析到 `169.254.169.254`（云元数据）。netguard 的答案是**快照模型**：执行器在真正连接前，把 `resolved_addresses`（DNS 全部答案）与 `connect_address`（实际要连的地址）作为参数递给权限引擎，引擎只做**一致性校验 + 地址分类**，全程零网络调用。

这个分工把 TOCTOU 窗口压到执行器内部，权限引擎保持纯函数性质——可单测、可离线审计、无超时无重试。代价是协议契约变重：调用方必须传快照，缺快照（`resolved_addresses` 非法）直接 ValueError（`address_policy.py:296-299`），这是 fail-closed——出站判定不允许"没数据就放行"。

NetGuardComponent 在 engine 里的克制姿态：**非网络工具一律弃权**（`netguard/component.py:135-138`，注释明说"abstain so bash is not raised to ASK by the network defaults fallback"——bash 命令里的 URL 提取明确不在本期路由范围）。`network_connect` 是特例：它跳过工具基线，只吃 URL/地址策略结果（L140-141）——连接类工具的语义就是"这次连哪"，工具级 ALLOW/ASK 无意义。

## 二、内部结构

### address_policy.py：65536 项 /16 查表

模块用一张 64KB 表把 IPv4 分类做成 O(1) 查表（L129-147）：`_build_v4_hi` 建 `bytearray(65536)`——每个 /16 前缀一个字节，取值 public/blocked/loopback/private/mixed（L104-109）；`/16` 及更短的前缀（10/8、172.16/12、192.168/16、127/8 及整段非公开段）直接"刷漆"（`_fill_v4_hi` L112-121）；更长前缀只把所在 /16 标 **mixed**（`_mark_v4_mixed` L123-126），命中 mixed 才走慢路径 `_v4_class_fine` 逐前缀判定（L185-202）。

为什么不用 `ipaddress.is_global`？L70-74 注释：不同 Python 版本的 special-purpose 注册表漂移会让同一配置判定不同，所以仓里**手工钉死注册表**：`_NON_PUBLIC_V4` 八段（0/8、100.64/10 CGNAT、169.254/16、192.0.2/24、198.18/15、198.51.100/24、203.0.113/24、224/3，L74-83）、IPv6 过渡段（2002::/16 6to4、2001::/32 Teredo、64:ff9b::/96 与 /48 NAT64，L50-55）、废弃 6to4 中继 192.88.99.0/24（L63）、特殊段 192.0.0.0/24 但保留 192.0.0.9/10 选播（L58-62），并标注 IANA 审查日期 2026-10-19（L57）——注册表是要人工对齐 IANA 演进的活资产。

三个**显式封禁端点**（L45-49）：`100.100.100.200`、`168.63.129.16`、`fd00:ec2::254`。注释解释为什么不并入私有段："Keep the Xiaoyi inference proxy's special-target exclusions explicit"——小艺推理代理的特殊目标要显式列出，不依赖 Python 版本相关的 is_global/is_reserved。

快照校验快慢双路径：`_fast_ipv4_classes`（L254-288）在**全部答案是严格点分十进制 IPv4** 时走整数快路径（`_strict_ipv4` L214-230 手写解析器，复刻 `IPv4Address` 语义——四位、无前导零、≤255）；任何 IPv6/映射地址/怪文本回落 `normalize_address` 通用路径（L171-182，IPv4-mapped IPv6 归一成 IPv4）。

### url_safety.py：拒绝歧义而不是猜测

`parse_url`（L148-198）的设计哲学浓缩在 docstring："Parse without silently discarding whitespace, credentials or bad ports"。客户端生态对 URL 规范化各有分歧，netguard 对所有歧义输入**一律 ValueError 落 defaults**，不猜执行器最终会请求哪个资源：歧义字符（控制字符、反斜杠、空白）拒（L111-116，ASCII 快速路径用 bytes translate 免正则扫 8192 字符，L17-19）；百分号转义解码遇控制字符或编码后的路径分隔符（`%2F` 等）拒（L121-137）；路径 `.`/`..` 段拒（L136-137，"Reject those inputs rather than guessing the executed path"）；userinfo、非 http(s)、端口 0/尾随冒号拒（L172-175）；IPv6 主机必须方括号+合法字面量（L179-190）。

**IDNA2003 拒绝**是最微妙的一条（`normalize_host` L92-97）：Python stdlib 的 `encodings.idna` 是 IDNA2003，HTTP 客户端可能走 IDNA2008——两者对 `ß`（→ss）等映射不同，"规则里写的域名"与"客户端实际请求的域名"可能是两个 DNS 名。处置：`ToUnicode(ToASCII(label)) != NFC(label)` 即拒（L95-98）——**有损映射的 Unicode 主机直接拒绝**，稳定 Unicode 与显式 punycode A-label 照常用。配套拒：非规范数字主机（`127.1`、`0x7f000001`，L82-83）、Unicode 主机混 wildcard（L88-89）。

**机密查询防护**：`has_secret_query` 只看 key 名不看值（L201-208，docstring "never return credentials or query values"）——token/apikey/signature 等 13 个词 + 9 个复合词命中即给 warning `network_secret_query`；`rule_label` 把带机密查询的规则 label 截断成 `?<redacted>`（L211-217），保证日志与 matched_rule 不泄漏凭据。

### net_urls.py：glob 编译与前缀/后缀索引

规则编译（`compile_rule` L67-75）：主机部分含 `*?` 编译成 host_glob，路径/查询同样；`compile_glob` 用 `fnmatch.translate` 而不是手写 `.*` 正则——注释点明 fnmatch 的原子化翻译能避免朴素 `.*` 重复的指数回溯（L28-31），`[` 转义防字符类注入（L30）。`NetUrlRule.matches`（L44-64）的语义分层：host 全等或 glob 全配 → scheme+port 全等 → 路径（无查询的规则做前缀匹配、带查询的做全等）→ 查询 glob/全等。

component.configure 的索引构建（L102-112）：无 glob 的规则进 `exact_hosts[host]`；有 glob 的规则取 glob 的**必然字面前缀/后缀**（`*` 最早出现位置之前 / 最晚出现位置之后），把较长的一侧作为 key 进 prefix/suffix 索引。运行时 `_check_rules`（L53-74）按目标 host 的所有前缀和后缀查候选——"Every glob has a necessary literal prefix/suffix. Indexing the longer one; checking all host substrings here also preserves globs within DNS labels"（L57-59）。匹配数从 O(规则数) 降到 O(host 长度×桶大小)，且**跨 DNS label 边界的 glob 语义不被索引破坏**（对应回归测试 `test_host_glob_index_preserves_character_and_dns_label_boundaries`）。

configure 的最后一行注释值得抄进任何配置加载代码："No state is mutated until every field and rule has been validated"（L113）——与第 01 篇 `_install` 同款原子性。

### 四条内置 deny 与工具基线

`builtin_rules.py` 的 `_BUILTIN_NET_URLS`（L10-15）：`169.254.169.254`、`metadata.google.internal`、`localhost`、`127.0.0.1` 全 deny——云元数据端点与本地回环的默认封禁；`package_rules_enabled` 缺省启用（L17-20）。工具基线由 `tool_policy.py` 单独编译（`NetworkToolPolicy` L26-47），与 URL 策略在 evaluate 里取最严合并（component L149-157）。

## 三、外部连接

- **engine**：NetGuardComponent 是第 9 号组件；`evaluate_url_policy` 公开方法供组件外调用方单独查 URL 策略（L164-171）。
- **执行器契约**：`network_connect` 工具的调用参数必须含 `url` + `resolved_addresses`(1..64) + `connect_address`——这是快照模型的协议面，缺省即 ValueError。
- **url_safety 的复用**：`UrlTarget`/`normalize_host`/`parse_url` 被 net_urls 与 address_policy 共用；`iptext.py` 是测试友好的 IP 文本构造小工具（`ipv4(127,0,0,1)`），生产代码也用它构造常量表（`address_policy.py:14`）。
- **W3 审计回归**：`tests/netguard/test_audit_regressions.py` 标题即 "Security regressions from the four-reference-branch W3 audit"（L6），**17 个测试函数**（与任务书"17 用例"核对一致）：覆盖 faß/ς/全角/零宽连接符/短格式 IP 不能授权别的目标主机、点段与百分号编码、查询分隔符非通配、mapped IPv6 不能绕过等价 IPv4 规则、元数据主机限制在 URL 覆盖后仍存活、64 上限在 trim/hash 前生效、特殊地址不能用 private/loopback 例外、glob 与查询约束藏不住独立 deny、索引匹配与全量枚举一致（随机种子对拍）。

## 四、数据流

`network_connect` 一次完整判定（component `_evaluate_url_policy` L173-217 + address_policy `connection_rejection_reason` L291-316）：

1. URL 长度 >8192 → DENY `net_guard:url_too_long`（L190-193；`extract_fetch_url` 特意保留超长原串以产生这个 DENY，L46-48）；
2. URL 缺失/非法 → **defaults**（L194-204）——URL 都没有时没有"最严"可取，按缺省策略走；
3. `parse_url` 产出 `UrlTarget`（歧义即 ValueError → defaults）；
4. `_check_rules` 规则匹配（exact/前缀/后缀三索引取并集，多条命中取最严并合并 label，L53-74）；未命中 → `net_guard:defaults`；
5. `connection_rejection_reason` 快照校验：
   - `resolved_addresses` 必须 list、1..64（L296-299）；
   - 快路径全 IPv4 或通用路径归一后，**connect_address ∈ 快照集合**否则 ValueError "Connection address is not in the DNS snapshot"（L276-277 / L306-308）——防执行器"判定用 A 地址、连接用 B 地址"；
   - URL 主机是 IP 字面量时，快照必须恰为该字面量（L278-287 / L309-314）——防 URL 写公网 IP、快照塞别的；
   - 分类集合 classes = 所有答案的 {public/private/loopback/blocked}；
6. `_class_decision`（L319-332）依序：`metadata.google.internal`（含子域）→ `metadata_host_not_allowed`（L320-323）；http 且未 allow_http → `http_not_allowed`；classes=={public} → 放行；{loopback}+allow_loopback → 放行；{private}+allow_private_network → 放行；**其余一律 address_not_allowed**——混合分类（一个 public 一个 private）不享受任何例外，这是防 DNS rebinding 的关键：多条答案里只要有一条不干净整组拒绝。
7. 结果合并 warnings（secret query）返回；ValueError 沿组件协议向上抛（`netguard/component.py` 文件头 noqa TRY004 注释即为此契约）。

## 五、设计决策与权衡

**快照模型 vs 引擎自解析。** 自解析的判定一致性最好但引入网络依赖与 TOCTOU；快照模型把信任边界划在"执行器如实上报"上，用两条一致性断言（connect∈snapshot、literal==snapshot）把执行器的作弊空间压到"整套 DNS 假答案"，而整套假答案意味着执行器已被攻陷——那不是权限层能救的场景。

**65536 查表 vs 逐条 ip_network 判断。** 64 地址×每次连接的判定频度下，`ipaddress` 对象网络的逐成员判断（每个 answer × 每条前缀）开销不可控；查表把公共情形压成两次移位取字节。代价是**注册表固化**：IANA 未来新增特殊段需要改代码发版，而 is_global 方案"免费"跟进——设计者明确选择了确定性 over 免费跟进（L70-74）。

**拒绝歧义 vs 规范化猜测。** URL 解析器（L119-137）每一个 ValueError 都对应某个客户端生态的现实分歧。安全判定层的立场：猜错的代价（放行了另一个资源）远大于拒绝的代价（该 URL 落 defaults 可能 ASK）。defaults 本身可配置，所以"拒"的最终效果由部署者兜底——引擎只保证"不静默改写语义"。

**IDNA 往返校验 vs 升级 IDNA2008 库。** 引第三方 idna 库最彻底，但给安全核心加依赖；往返校验（ToUnicode∘ToASCII == NFC）用 stdlib 就能把**有损映射**全部拒掉，稳定 Unicode 不受影响。取舍：少数往返不稳的合法域名被误拒——可用 punycode A-label 显式写进规则（回归测试 L40-52 验证了这条路）。

**机密查询只告警不拦截。** `has_secret_query` 产出 warning 不是 DENY（L211-216）——token in query 是大量合法 API 的现实，拦截会全打死；warning 给上层留消费位。"旁路信号不阻断主业务"的又一实例。

## 六、新人提示与坑

1. **改 `_NON_PUBLIC_V4` 等注册表常量必须同步想 `_build_v4_hi`**：表是启动时从常量构建的（L147 模块级执行），新加 /16 以细的前缀只会标 mixed（慢路径兜住），但删前缀会静默放行——动表前跑 `tests/netguard/test_address_policy.py` 全量。
2. **`net_guard.enabled` 缺省是 False**（component L94）——与 file_guard 的"有 external_directory 即启用"推断不同，netguard 必须显式开。测试里忘开会得到"全弃权"假绿。
3. **快照校验抛的是 ValueError 不是返回 DENY**：netguard 的错误契约（`net_urls.py:5` "W3's ValueError contract"）是"配置/输入非法 → 异常"，"合法但不允许 → DENY 结果"。宿主 catch 层要区分：前者是 bug 要修，后者是策略要批。
4. **URL 规则的路径语义随查询存在与否改变**：无查询的规则做**前缀**匹配（`/api` 盖住 `/api/anything`），带查询的规则做全等（L54-59）——想"前缀 + 忽略查询"就写 `https://host/api?*`。
5. **max 64 条 DNS 答案、1 万条 URL 规则、8192 字符 URL** 三个上限（`address_policy.py:17`、`net_urls.py:19`、`url_safety.py:14`）都在**构造/入口期**检查——`test_limits_apply_before_trimming_or_hashing_snapshot_strings`（回归 L151）专门守住"先验限制再做任何规范化"的顺序，防规范化后绕过。
6. **debug 判定差异先查 mixed**：某 /16 内同时有公开与非公开段（如 192.0.0.0/24 里的 .9/.10）时行为在慢路径，与直觉的"整段 blocked"不同——`_SPECIAL_PUBLIC_V4`（L59-62）就是为保住 .9/.10 两个公开地址而存在。
