# 02 · dm-verity fail-closed 与供应链对账（guest_extension_image.rs / hash.rs / lockdown.rs / release.yaml）

## 角色定位

这一组文件回答机密计算的立身问题："客户机里的每一块代码，凭什么可信？"guest_extension_image.rs（512 行）在启动早期把冷插镜像扩展逐个 dm-verity 验证后挂载；hash.rs 给运行中的二进制打自证摘要；lockdown.rs 提供 panic 断电与模块禁载两道闸；release.yaml/reproducible.yaml 在仓外保证"发布出来的那个二进制"与"你手里这份数据"可对账。

## 内部结构

- guest_extension_image.rs 的不变量只有三行（guest_extension_image.rs:15-17）：device+params→verify and mount；device 无 params→panic（verity 被剥）；params 无 device→panic（对不上）。`plan_mounts()`（guest_extension_image.rs:65-90）双向对账实现它，**没有未度量 raw-mount 回退**。
- VerityParams 五字段全必填、数值字段还非零（guest_extension_image.rs:151-166）；`veritysetup open` 显式 `--no-superblock --hash sha256`（guest_extension_image.rs:176-195）。
- 挂载 flags `MS_RDONLY|MS_NOSUID|MS_NODEV` 刻意不带 NOEXEC——扩展要出货可执行文件如 attestation-agent（guest_extension_image.rs:102-103）。
- 扩展名 charset 白名单（字母数字+`_-`+`.`，拒绝全点号），堵 `extension-../evil` traversal（guest_extension_image.rs:209-215，测试 :400-416）。
- hash.rs：`self_exe()`（hash.rs:32-34）对 `/proc/self/exe` 做 SHA-256（hash.rs:49-51），拼 `NVRC version=... sha256=...` 行；GIT_REV 开发戳含 `-dirty` 后缀（hash.rs:24-30）。
- lockdown.rs：panic hook 写 `/dev/kmsg`→`sync()`→`reboot(RB_POWER_OFF)`（lockdown.rs:40-50）；`disable_modules_loading` 写 modules_disabled=1 单向生效，对 NotFound 容忍（内核未编 CONFIG_MODULES）、其他错误照旧 panic（lockdown.rs:62-70）。

## 外部连接

- 上游：被度量的内核命令行提供 `kata.extension.<name>.verity_params`（guest_extension_image.rs:40-41）；`/sys/block` 提供 serial 设备发现（guest_extension_image.rs:199-223）与分区号（data=1/hash=2，:227-251）。
- 下游：挂载点 `/run/kata-extensions/<name>`（MOUNT_BASE，guest_extension_image.rs:32）是 gpu_extension.rs 消费 `ROOT`（gpu_extension.rs:20）的事实来源。
- 仓外：release.yaml 出 SPDX SBOM 并 cosign keyless 双签 binary+SBOM（release.yaml:105-134）；reproducible.yaml 从不同目录构建两次、强制 sha256 相等（reproducible.yaml:49-62）；时序上 mount_all 必须先于 disable_modules_loading（main.rs:83-84 注释：dm-verity/erofs 模块还没载入）。

## 数据流

virtio-blk 扩展盘（serial `extension-<name>`）→ sysfs 发现 → 与 cmdline 参数 1:1 对账 → veritysetup open 建 mapper → EROFS 挂载 → gpu_extension::setup 消费。hash 线独立：self exe → SHA-256 → dmesg →（人工）与 Rekor 证据比对。

## 设计决策

1. **fail-closed 而非 downgrade**：普通系统遇到验证不过会降级继续跑，机密 VM 直接关机——这是 guest_extension_image.rs 头注释（:11-13）明说的取舍。
2. **hash.rs 自认"非安全原语"**（hash.rs:9-13）：被入侵的 NVRC 能谎报哈希；真正的完整性由块层 dm-verity、文件层 fs-verity、IPE 在 execve 前强制，可信摘要在 Rekor 不在 dmesg。这一段的自我批判是理解"自证不可信"的教科书。
3. **panic=断电**：机密 VM 里 undefined state 可能泄密，宁可干净终止（lockdown.rs:22-26）。
4. 分区号从 sysfs 的 `partition` 属性读而非拼名字（:226-227），兼容 `vdb1` 与 `nvme0n1p1`。

## 新人提示

对照测试读实现最快：guest_extension_image.rs:259-516 的 rstest 矩阵几乎逐分支镜像实现；想复现供应链对账走 VERIFY.md；别把 hash.rs 当完整性机制引用；lockdown.rs:81 的 `#[ignore]` 测试注释警告模块禁载会永久弄脏 runner，只能在专用机 `--include-ignored` 跑。
