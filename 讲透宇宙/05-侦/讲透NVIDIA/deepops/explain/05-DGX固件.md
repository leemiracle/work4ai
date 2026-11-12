# 05 · DGX 固件升级：12 任务流水线与人工断电环

## 角色定位

roles/nvidia-dgx-firmware 是全仓唯一"承认自动化有边界"的角色：固件写入是高危运维，它把可自动化的部分（诊断、容器加载、停服卸驱动、升级、日志回收）组织成 12 个 task 文件的流水线，把 SBIOS/BMC 级的底盘断电明确交还给人工。入口 playbooks/nvidia-dgx/nvidia-dgx-fw-update.yml 以 `connection: paramiko_ssh` 强制连接插件（`:4-6` 注释：固件容器要交互式 -t 需 TTY，auto 模式的 ansible ssh 会 flake；固件/BMC 升级会重启 sshd，paramiko 独立会话也更稳），并开启 `run_diagnostics: true / update_firmware: true`（:15-17）。

## 内部结构

12 个 tasks 文件构成全流程：main（编排）、check-firmware（版本比对）、run-diagnostics（pre/post 体检，逐项 ignore_errors:8-16）、get-health/get-ib/get-data/get-time（信息采集）、load-image（固件容器装载）、update-firmware（写入）、verify-firmware（复核）、transfer-logs（日志回传）、clean（清理）。main.yml 的 block 是标准高危模板：pre-flight 诊断（`:22-27`）→ 容器加载（:30-31）→ `systemd stopped` 停 nvsm/persistenced/fabricmanager/nv_peer_mem/dcgm/docker 六服务（:34-40，defaults/main.yml:56-62）→ `modprobe absent` 卸载 nv_peer_mem/nvidia_uvm/nvidia_drm/nvidia_modeset/nvidia 五模块（:42-47，defaults:64-70）→ 升级（:50-51）→ post 诊断（:54-57）→ `always` 块无条件 transfer-logs（:59-60，注释明言失败也要把已捕获的日志拉回来）。机型强校验在姊妹角色 roles/nvidia-dgx：`tasks/main.yml:2-5` 直接 fail——`ansible_product_name is not search("DGX")` 即 "Role supports DGX systems only"，防止误跑到普通服务器。

## 外部连接

升级载体是厂商固件容器 `nvfw-dgxa100:21.11.2`（defaults/main.yml:20-26），tar 包从 inventory 的 containers/dgx-firmware 目录分发；update-firmware.yml:22-23 以 `docker run --rm -ti --privileged -v /:/hostfs` 挂根文件系统执行 `set_flags AUTO=1 update_fw {{ target_fw }}`，target_fw 默认 all（defaults:43-45，注释列出 CEC SBIOS BMC VBIOS FPGA SSD SWITCH CPLD 八类目标）。输出 JSON 交 parse_manifest.py 解析（:25-30，files/parse_manifest.py 是脚本式 CLI）。

## 数据流

check-firmware.yml 先 `show_fw_manifest` 与 `show_version`（`:11-17`），grep 过滤 Inactive/standby 组件后（:29-32）以输出中是否含 "no" 判定 `firmware_needs_upgrade`（:34-38，TODO 注释承认该字符串判定待 JSON 化）。update-firmware.yml 解析回执：`RebootRequired==true` 置 reboot_required（`:31-34`）→ `sleep 2 && shutdown -r now` 以 `async:1 poll:0` 发射（:39-44）→ `wait_for_connection delay=15 timeout={{ reboot_timeout }}` 等节点回来（:57-60，defaults:53-54 给 1200s——注释说明 SBIOS 升级比常规重启久）→ verify-firmware 复核（:66-69）。

## 设计决策

① 人工断电环是点睛之笔：当回执 `FirmwareLoadAction == "DC Power Cycle"`（update-firmware.yml:48-51），置 `nv_fw_power_cycle_needed` 后 main.yml:66-71 与 update-firmware.yml:52-55 两处 debug 明确指挥操作员——"用 BMC 或 ipmitool 断电、通知数据中心、先 clean shutdown 再下电"，宁可打断自动化也不模拟断电；`:46` 的 TODO 补充说明 ipmitool 底盘级断电仍未自动化。② 停服+卸模块是写固件的安全前提（main.yml:33-47），驱动占着设备时写 VBIOS/FPGA 是灾难。③ always 回收日志让失败现场可审计。④ 诊断 stress 测试（dcgm_stress）默认关闭（defaults:15-17）——"可以压很久且伤硬件"。

## 新人提示

跑之前确认 inventory 的 containers/dgx-firmware 里有对应机型的固件 tar（repo/tag 与机型必须配套，DGX A100 的容器对 DGX-2 无效）；pre/post 两轮诊断日志会覆盖部分 pre-flight 结果（main.yml:60 注释）；reboot_timeout 按目标组件调（SBIOS 给 1200s 以上）；升级后看到 power cycle 提示不要试图重跑 playbook 跳过它——那是设计上留给人的步骤。
