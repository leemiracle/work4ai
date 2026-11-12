# systemd understand 图谱 · 全链产物

> systemd/systemd @ca78951b（每日跟踪中）· 产物 2026-11-08 · 真源本目录 · **史上最大图谱**

## 状态

| 产物 | 规模 | 状态 |
|---|---|---|
| knowledge-graph.json | **23980 节点 / 56339 边 / 16 层 / 16 步 tour**（18.7MB） | ✅ validator 双验 0 issues 0 warnings |
| fingerprints 基线 | 3618 文件 @ca78951b | ✅ 支持增量 |
| ONBOARDING.md | 7717 字 8 节 46 行号锚 | ✅ 抽验 3/3 |
| explain/ | 12 篇 43373 字符 | ✅ 216 锚 0 坏（写作中自纠 3 处） |

## 裁剪口径（.understandignore 钉版）

src/test（291）+ man/po/docs/factory/mkosi/shell-completion/coccinelle/rules.d 等全裁 → 3618 文件入图（src/ 主体 + 根配置）。

## 批分析实录（170 批 / 3618 文件，历时 ~20 小时跨 3 个 1308 窗口）

- 手扫补 imports 合计 **~7000 条**（C 仓 scanner 只认同目录 include 的系统性盲区在 systemd 上最严重——meson 的 -I 目录链 shared→libsystemd/sd-*→basic→fundamental→systemd 全靠各批工人源码重扫）
- tree-sitter 大文件盲区全谱实证：TEST() 宏全解析为同名节点（一文件 80 个 ID 冲突）、#if 条件编译块整体漏提取、`Type* func(` 星号紧贴返回类型全漏、4000 行级文件后半段漏函数、varlink IDL 宏零提取
- 悬空边 29 条（多为跨批函数级 calls 符号未建节点）按 merge 安全网丢弃属预期
- 深度甄别：本仓 origin=github.com/systemd/systemd（无 Kylin 私有 diff）；udevd/udevadm、networkctl/networkd 均为同二进制 busybox 式双面目；D-Bus→Varlink 迁移进行时（51 个 varlink IDL）；include/override 的 libc shim 四层覆盖链（libc→override→uapi→系统头）

## 16 层速览

构建配置(83) → 公共 API 头+libc 兼容层(256) → fundamental/basic(313) → libsystemd(205) → libsystemd-network(110) → shared I/II(626) → core PID1(220) → network(301) → resolve(113) → udev(124) → boot EFI(161) → 日志会话(256) → 虚拟化镜像(303) → 安全度量(241) → CLI 生成器 fuzz(306)

## 使用

- 新人：ONBOARDING.md → tour 16 步 → explain/ 12 篇
- agent：knowledge-graph.json（23980n）+ knowledge/systemd-network.md 消化文档
- 增量：代码变更后重跑 prepare（fingerprints 跳过未变）
