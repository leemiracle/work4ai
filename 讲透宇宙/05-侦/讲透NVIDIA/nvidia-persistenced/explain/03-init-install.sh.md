# 讲透 init/install.sh（init 三系安装器，813 行）

## 角色定位
把守护装进 systemd / SysV / Upstart 三种 init 系统的参考安装器（自述"sample"，install.sh:33-36 声明可能不适配所有发行版）。它同时是仓内唯一带**事务回滚语义**的脚本：任何一步失败，已执行步骤逆序撤销。

## 内部结构
- 基础设施：`nvpdError`（:99，触发回滚链）+ `nvpdCommand`（:126，执行命令并把第 3 参的回滚命令**前插**进 cleanup_cmd 链 :136-142，保证逆序撤销）+ `isNvpdRunning`（:167，读 /var/run PID 文件判活）。
- 公共检查/安装：`checkCommon`（:190，sed/useradd/userdel/id 四件套）+ `installCommon`（:246，useradd -s /sbin/nologin -d '/' -r 建系统用户 :254-256；用户已存在则校验属组 :259-265）。
- 三系对称九函数：create/check/install/uninstall × SysV（:292/:314/:348/:385）、systemd（:407/:429/:462/:500）、Upstart（:522/:544/:575/:610）。
- 主流程：getopt 解析（:627）→ checkCommon → 无 -r 则先 sed 填 __USER__ 生成三套样本（:697-700）→ targets 探测循环（:706 起始序 "systemd upstart sysv"，与 usage :77-78 一致）→ 分发 install/uninstall。

## 外部连接
模板三件：systemd（Type=forking，ExecStopPost 直接 rm -rf /var/run/nvidia-persistenced，init/systemd/nvidia-persistenced.service.template:34）、SysV（nvidia-persistenced.template，chkconfig 风格，NVPD_USER=__USER__ :49）、Upstart（expect fork + post-stop rm -rf）。依赖外部命令 systemctl/initctl/chkconfig 做探测（:442/:555/:328）。

## 数据流
install：模板 sed 注入用户名 → 目标系探测（checkInstallPath 试 /etc/init.d→/etc/rc.d/init.d→/etc/rc.d，:322-324）→ 建用户 → 安装（SysV 路径：杀旧进程 kill -9 :358-360→备份旧脚本为 .bk :365-367→cp+chkconfig --level 2345 :373-375→start）→ 每步回滚命令入栈。uninstall（-r）：stop → disable → rm 脚本 → userdel（-d 可保留用户）。

## 设计决策
① 回滚用 shell 字符串拼接的"命令栈"而非 trap 临时文件——零外部依赖的 POSIX sh 事务；② 三系全生成样本但只装探测到的第一个（:727-745 循环 break），其余留档给管理员手工迁移；③ systemd 装过则 `systemctl reenable`（:489）而非 restart，保住开机自启语义；④ SysV 安装前 isNvpdRunning 判活并优先用旧 init 脚本优雅停（:350-361）。

## 新人提示
最大陷阱是 -d 与 -u 的顺序耦合：-d 把 nvpd_user 清空（:683-685），其后的 -u 因 `if [ "$nvpd_user" != "" ]` 判断被静默吞掉（:650-657）——卸载想保用户必须 `-d -u <user>` 且 -d 在前。另外回滚链只在"安装中失败"生效，uninstall 分支失败只提示"may be incomplete"（:113-115）不回滚。
