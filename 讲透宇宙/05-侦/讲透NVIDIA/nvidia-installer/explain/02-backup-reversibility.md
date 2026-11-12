# 02 · backup.c + crc.c — 备份日志与卸载可逆线

## 一、角色定位

`backup.c`（1786 行）实现安装器的**可逆性承诺**：安装时每个被覆盖/删除的既有文件都被搬进备份目录并逐条记账，卸载时纯按账本逆向回滚——不依赖包管理器。它与 `files.c` 的落盘动作、`command-list.c` 的 BACKUP_CMD 生成、`crc.c` 的校验和共同闭环。`crc.c`（135 行）提供查表 CRC32（`compute_crc_from_buffer`，`crc.c:72`；文件版 `compute_crc`，`crc.c:94`）。

## 二、内部结构

**1) 目录与账本布局。** 三条宏定义一切：`BACKUP_DIRECTORY "/var/lib/nvidia"`（`backup.c:46`）、账本 `BACKUP_LOG "/var/lib/nvidia/log"`（`:47`）、目录账 `BACKUP_MKDIR_LOG "/var/lib/nvidia/dirs"`（`:48`）。备份文件以递增整数命名（`snprintf(tmp, len, "%s/%d", BACKUP_DIRECTORY, backup_file_number)`，`backup.c:247`）。

**2) 账本格式=两行一条。** 普通文件：`fprintf(log, "%d: %s\n", backup_file_number, filename)`（`:250`）记"编号: 原路径"，紧接 `fprintf(log, "%u %04o %d %d\n", crc, mode, uid, gid)`（`:254`）记四元属性；符号链接只记目标串。新装文件（非备份）另走 `log_install_file`（`:302`，`:320` 只写一行 CRC）供卸载直接删除。

**3) 三阶段生命周期。** 安装前 `init_backup`（`backup.c:137`）开账本——用 `umask(~BACKUP_LOG_PERMS)` 技巧保证日志权限恰为 0600（`:167`，`:80` 定义）；执行期 `do_backup`（`:208`）对每个冲突文件 stat→`compute_crc`（`:240`）→`nvrename`（`:244`）搬入备份目录→记账；卸载期 `do_uninstall`（`:631`）：`access(BACKUP_DIRECTORY)` 探目录（`:651`）→`read_backup_log_file`（`:656`，解析器 `:899`）→`check_backup_log_entries`（`:658`，逐条核对 `:1108`）→按 `conflicting_kernel_modules[]` 序 rmmod（`:833`，数组在 `conflicting-kernel-modules.c:29`）→恢复/删除→depmod/ldconfig 收尾。

**4) 两套核对策略。** `check_backup_log_entries`（卸载用，容忍并告警）与 `sanity_check_backup_log_entries`（`:1620`，`uninstall_existing_driver` 在 `:1569` 调用）差异在错误处理姿态——账本对不上时前者继续尽力卸载，后者更严格。

## 三、外部连接

- **上游**：`install-from-cwd.c:324` 先 `run_existing_uninstaller`（`backup.c:1460`，找系统里的 `nvidia-uninstall`（`:1462`）先跑旧卸载器再回退本仓逻辑）；`install-from-cwd.c:327` `init_backup`。
- **消费方**：`command-list.c` 把 BACKUP_CMD 排进命令链；`files.c:1607` `nvrename` 是物理搬移执行者；`misc.c:1202` `verify_crc` 用同一 CRC 复核安装产物。
- `uninstall_existing_driver`（`backup.c:1393`）是 `--uninstall` 模式入口，被 `nvidia-installer.c:732` 派发。

## 四、数据流

安装：冲突文件 →(nvrename) `/var/lib/nvidia/<N>` + 账本两行；新装文件 → 账本一行 CRC。卸载：账本 → BackupInfo 结构 → 反向遍历：有备份号的恢复回原路径（含 mode/uid/gid 还原），纯安装记录的直接删除；目录账 `dirs` 反序 rmdir。CRC 全程扮演"文件是否被动过"的指纹：恢复前不匹配则告警 `existing_installation_is_borked`（`backup.c:641` 文案）。

## 五、设计决策

- **为什么不复制而要 rename**：原子且零空间放大；代价是跨文件系统会失败，故备份目录固定在 `/var/lib`。
- **账本人读可写**（`%d: %s` 明文路径）而非二进制：现场排障可直接 cat；解析器 `parse_crc_mode_uid_gid`（`backup.c:428`）用行对读取。
- **0600 权限锁定**：账本含全路径信息，防非 root 篡改（`umask` 技巧 `:167` 正是为绕过继承 mask）。
- 局限：卸载"尽力而为"——账本损坏时仅告警继续（`do_uninstall` 的 warn 分支），不提供事务回滚。

## 六、新人提示

1. 读 `backup.c:208` do_backup 与 `backup.c:631` do_uninstall 对着看，账本格式一眼即懂。
2. 排查"卸载不干净"先 `cat /var/lib/nvidia/log`：编号断档/路径消失就是 check_backup_log_entries 告警源。
3. CRC 与 zlib 无关，是仓内自带查表实现（`crc.c:72`），改算法会破坏老账本兼容。
4. rmmod 顺序别乱调——数组序就是反依赖序（`conflicting-kernel-modules.c:29` 注释明示）。

---
字数 2532（非空白字符）/锚 17
