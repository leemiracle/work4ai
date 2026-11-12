# 讲透 NVIDIA/spdm（spdmcpp）

DMTF SPDM 规范（DSP0274）的 C++ Requester 实现栈：libspdmcpp 协议库 + spdmd openBMC 守护 + spdmutil CLI + fuzzer/负向注入/合规/压测工具族。本目录是"讲透"产物总索引。

## 产物状态

| 产物 | 状态 | 规模 |
|---|---|---|
| deepwiki/ | ✅ 2026-10-26 | 28 结构页 + 15 增补页 = 43 页，796,741 字符（INDEX.md/_coverage-check.md） |
| onboarding/ONBOARDING.md | ✅ 8 节 | ≥3500 字（不计空格），行号锚逐条核实 |
| explain/ | ✅ 3 篇 | connection 状态机 / spdmd 发现引擎 / libmctppacketcorrupt 注入 |
| 图谱 | ✅ | 1069 节点 / 1484 边 / 10 层 / 11 步 tour，fingerprints 246 文件 @ 2c5e6d28 |

- 仓：/usr-data/data2/repos/agent-repos/NVIDIA/spdm（commit 2c5e6d28，2026-10-24）
- 图谱在仓内 `.understand-anything/knowledge-graph.json`；onboard 输入 `onboard-input.json`
- 依赖子项目共 6 个 wrap：mbedtls / sdbusplus / phosphor-dbus-interfaces / sdeventplus / CLI11 / nlohmann（`subprojects/` 目录实证）

## 已核实勘误（vs README/文档/直觉说法）

以下每条均以源码 file:line 实证（commit 2c5e6d28）：

1. **README 的构建说明指向不存在的目标**：`README.md:21`/`:28` 让用户运行 `./spdmcpp_emu/spdmcpp_requester_emu`，但仓内没有任何 meson.build 定义该目标，也不存在 spdmcpp_emu/ 目录（全树 grep 仅这两处 README 引用）；`meson_options.txt:9` 的 `emu` 选项（"Build spdmcpp_emu for testing"，默认还 enabled）是没有消费者的死开关。DeepWiki 6.1 页（`deepwiki/6.1-build-options-and-compilation.md:415` "Builds spdmcpp_emu test binary"）同错。实际可构建产物只有 spdmd / spdmutil / fuzzer / libmctppacketcorrupt / 测试（`meson.build:104-109`）。
2. **"连接状态机 FlowClass" 是死代码**：`libspdmcpp/headers_public/spdmcpp/connection.hpp:43-79` 的 FlowClass/QueryFlowClass（含 STATE_GOT_VERSION→STATE_END 状态枚举）整段躺在 `/* ... */` 注释里，全仓零引用。grep 到它容易误以为是活的握手状态机；真正的状态推进是 `libspdmcpp/connection.cpp` 的事务方法链（tryGetVersion `:365` → tryGetCapabilities `:478` → tryNegotiateAlgorithms `:548` → tryGetDigest `:676` → tryGetCertificate `:917` → tryGetMeasurements `:935`）。
3. **报文结构头是 21 个，不是 23/25 个**：`libspdmcpp/headers_public/spdmcpp/internal/` 根 6 个 hpp + request/ 8 个 + response/ 7 个 = 21；`packet.hpp` 的 packet 系 include 也是 21 条（`:104`-`:136`，总 #include 34 条含标准库）。"23 头/25 include" 的口径把非报文头也数进去了。
4. **压力测试数据规模**：`tools/stress-test/` 实有 **47** 个请求 JSON（fpga 11 + hmc 11 + indices 12 + parallel 13，find 实证），非 57；`tools/stress-test-bash/` 实有 **32** 张请求 CSV（2022-11-04 批 19 + parallel 批 13），非 33。
5. **packetcorrupt 自述拦截的 syscall 名不副实**：`tools/libmctppacketcorrupt/readme.md:5` 称 "intercept the system calls read and write"，实际包装的是 **send/recv/connect/close**（`syscalls_wrap.c:112` `_iosys_recv`、`:148` `_iosys_send`、`:69` connect、`:186` close，且用 `.symver recv@GLIBC_2.4` 钉版本 `:145`）。另 `readme.md:16` 的 zerolen 模式描述串 "zerjjkko" 是原文打字错误。
6. **MCTP "tag=1" 与 "type=5" 是两个维度**：README `:49` 说 "5 is reserved for SPDM"（MCTP 控制守护的消息类型参数），代码里 `MCTP_TYPE_SPDM = 5`（`mctp_support.hpp:44`）对应它；而 `MCTP_TAG_SPDM = 1`（`mctp_support.hpp:42`）是 MCTP 头部的 tag 位，两者常被混读。
7. **spdmd 的 "Responder" 不是协议角色**：spdmd 是纯 Requester 侧实现；`spdmd/dbus_impl_responder.cpp` 里的 Responder 是 D-Bus 呈现对象——把远端设备的 SPDM 结果同步到 openBMC 属性（version `:111` / measurementsHash `:245` / measurementsSignature `:257`），本地不实现 Responder 协议行为（伪造 Responder 只在 fuzzer）。
8. **spdmd_conf.json 只管可见性**：`spdmd/conf_files/spdmd_conf.json` 的 endpoints（eid/name/visible/description）只影响 D-Bus 对象的呈现（无 inventory 时给名字/描述、控制 visible），不参与发现决策——发现由 MCTP+inventory UUID 驱动（`spdmd/mctp_endpoint_discovery.cpp:491`/`:897`）。

## 图谱管线补扫说明

批阶段两条钉版：`libspdmcpp/headers_public/spdmcpp/packet.hpp` 是典型 include-aggregator，各报文头反向依赖它形成守卫环（SPDMCPP_PACKET_HPP 宏控制）；`tools/libmctppacketcorrupt/syscalls_wrap.c` 通过包装 POSIX socket 调用实现透明注入。tree-sitter 对该仓 Allman 风格纯 C/C++ 声明存在盲区，113 个 struct 域由人工手扫补齐入图（手扫器已按 Allman 风格修复）。

## 阅读顺序建议

新手：README（忽略勘误 #1 的 emu 段）→ onboarding/ONBOARDING.md → explain/01（协议核心）→ explain/02（部署形态）→ explain/03（负向测试）。需要协议细节再进 deepwiki/ 2.x 系列；需要构建/选项事实以源码 meson_options.txt 为准（deepwiki 6.1 含 emu 错误描述）。
