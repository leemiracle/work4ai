# explain-07 · src/resolve/resolved-dns-scope.c — DnsScope：查询路由与多协议解析面

## 一、角色定位

systemd-resolved 是系统级 DNS/DNSSEC/LLMNR/mDNS 解析器，`DnsScope` 是它的核心路由单元：一个 scope = "某个来源（网卡/委派/全局）× 某个协议（DNS/LLMNR/mDNS）× 某个地址族"的查询通道（`dns_scope_new()`，resolved-dns-scope.c:48，origin 分 LINK/DELEGATE/全局三档，断言见 64-65）。查询进来后，resolved 的第一件事就是拿问题问每个 scope"这域名归你管吗"——`dns_scope_good_domain()`（676）；命中后事务（dns-transaction.c）在该 scope 的服务器/socket 上跑。本文件因此承载三块逻辑：scope 路由裁决、组播协议（LLMNR/mDNS）的收发/应答/冲突仲裁/宣告，以及 DNS socket 的选路与服务器轮换。

## 二、内部结构

scope 创建时做三件要事：为组播协议初始化限速（MULTICAST_RATELIMIT，resolved-dns-scope.c:82）与重发超时（78）；DNS 协议下从 link 或 manager 拷贝 DNSSEC/DoT 模式——注释言明只在创建时拷贝、此后不再跟随配置变化（85-90）；立即加入 LLMNR/mDNS 组播组（107-108，membership 实现在 947-1010）。`DnsScope` 内嵌自己的 `DnsCache`（resolved-dns-scope.h:46）与 transaction 链表，销毁时 `dns_scope_abort_transactions`（121）用 `block_gc++` 防止边遍历边释放的经典手法逐个中止。socket 工厂 `dns_scope_socket()`（398）统一处理"粘住同一服务器"（保证 DNSSEC 连贯性）与路由标记（保证包从对应接口出）；发送走 `dns_scope_emit_udp`（373），RTT 反馈回服务器选择：`dns_scope_packet_received/lost`（223/233）。

## 三、外部连接

上游：resolved-manager.c 按 link 配置创建/销毁 scope；dns-query.c 调 dns_scope_good_domain 做多 scope 竞争；dns-transaction.c 是真正的状态机（超时/重传/DNSSEC 验证），本文件只提供环境。内部：dns-server.c（服务器池，`dns_scope_next_dns_server` 轮换，206）、dns-zone.c（本地区域数据，LLMNR 应答查它）、dns-sd（DNS-SD 服务注册，1750/1788）。对外：组播 socket 挂进 manager 事件循环；`dns_scope_to_json`（1879）是 varlink introspection 的输出面。与 nss-resolve 的契约：单标签名/搜索域/路由域的优先级全部在 good_domain 里定，改这里会直接改变全网机器的解析行为。

## 四、数据流

查询路由（最值得精读的函数）`dns_scope_good_domain()`（resolved-dns-scope.c:676）返回五档信号：NO / LAST_RESORT / MAYBE / YES_BASE+n（n=匹配的后缀标签数）——函数头注释（686-696）就是这个"最长后缀优先、MAYBE 兜底"算法的规范。硬性拒绝清单按序：指定 ifindex 不匹配（715）、协议/族不在请求 flags 里（718）、localhost 与 127.in-addr.arpa（723-726，永远本地合成）、RFC6303/6761 保留域（729）、特殊用途域（733）、`_gateway`/`_outbound`/`_localdnsstub` 等合成名（737-741）、自己的主机名（744）、LLMNR 不收 SOA/NS/DNSSEC 请求（747-748）。DNS 分支里数搜索域后缀标签取最长匹配（782-797），单标签名在有搜索域的 scope 上直接 YES_BASE+1（802-803，与 LLMNR 平权竞争）。

应答方向（LLMNR responder）`dns_scope_process_query()`（1095）：只处理 LLMNR（1099）；UDP 查询必须发给组播地址（RFC 4795 §2.5，1104-1111）；C 位冲突触发 `dns_scope_verify_conflicts`（1129）；单 question 查 `s->zone`（1136）组装应答（make_reply_packet:1019）。冲突仲裁链：notify_conflict（1322）→ 防抖 timer（1291）→ 比较 IP 后决定让步或顶回（check_conflicts:1359）。默认路由裁决 `dns_scope_is_default_route()`（1849）：显式配置优先（DefaultRoute=），否则用启发式——有 route-only 域（~. 风格，VPN 特征）的接口不当默认路由（1834-1846 的 "~. 压倒一切"注释），delegate 默认不当，全局 scope 永远当。

## 五、设计决策

1. **返回值编码优先级**：good_domain 用枚举区间 DNS_SCOPE_YES_BASE+n（resolved-dns-scope.h:17）把"匹配强度"编码进返回值，调用方一次遍历即可选出最佳 scope——比回调或排序都轻。
2. **安全短路前置**：localhost/保留域/合成名的拒绝全在协议分支之前（721-750），保证任何协议都不可能把这些名字泄到网络——防 DNS 侧信道（如用 localhost 解析探测内网）。
3. **scope 与配置解耦快照**（85-90 注释）：DNSSEC 模式创建时拷贝，避免 scope 生命周期内配置翻转导致验证链断裂；代价是 reload 后需重建 scope。
4. **VPN 感知的默认路由启发式**（1849）：route-only 域检测让 resolved 默认不把 VPN 接口当通用出口，同时留显式配置覆盖（1862-1864）——启发式可预测且可推翻。
5. **组播限速内建**（82）：LLMNR/mDNS 的洪泛风险在 scope 层就压住，不依赖上层。

## 六、新人提示

排解析问题先分清"路由错了"还是"事务错了"：`resolvectl query` 会显示用了哪个 scope/协议，对不上预期就读 good_domain 的五档逻辑（686-696）手推一遍——九成怪现象（VPN 域名走错出口、单标签名被 LLMNR 抢答、~. 未生效）都能在那 200 行里找到解释。改路由规则必须同步更新 686 的注释与 man resolved.conf，行为即文档。组播调试用 `resolvectl llmnr-status`/`mdns-status`；冲突仲裁窗口内（timer 未触发）日志会出现 tentative 应答，属协议正常行为。Kylin 工作区提示：国产 VPN/多网卡环境的路由域配置经常互相打架，is_default_route 的三级优先（显式配置 > route-only 启发式 > 全局兜底）是排查框架；若麒麟安全策略要求禁 mDNS，在 link 配置层面关（MulticastDNS=no 会走到 1001-1010 的 membership 撤销），不要动本文件。
