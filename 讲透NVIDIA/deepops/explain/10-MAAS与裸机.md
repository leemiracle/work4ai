# 10 MAAS 与裸机：maas_deploy 的 OAuth 直调、paramiko 固件升级与 common.sh 运行时锚定

## 一、角色定位

横跨图谱 L05（DGX 固件硬件）与 L12（运维脚本）：scripts/maas_deploy.sh+maas_inventory.py 负责"从裸金属到可装机"（MAAS 纳管/部署/打标/释放），playbooks/nvidia-dgx/nvidia-dgx-fw-update.yml+roles/nvidia-dgx-firmware 负责固件升级（BMC/SBIOS），scripts/common.sh 是全脚本运行时锚。配套 roles/maas-controller、docs/pxe/maas.md（347 行）、skills/provision-with-maas/SKILL.md（252 行）。

## 二、内部结构

**maas_deploy.sh（540 行，21 函数）是 bash+python3 混合实现**：骨架 load_config(:49)/parse_args(:118)/maas_auth_header(:163)/maas_get(:173)/maas_post(:178)/get_system_id(:184)/wait_for_ssh(:269)/do_apply_profile(:323)/do_release(:406)/do_deploy(:438)/main(:527)，另有 10 个辅助。两个设计点：其一**不依赖 maas CLI**，curl 裸调 MAAS REST API，鉴权头是 OAuth 1.0 PLAINTEXT 手工拼接（:165-171，nonce 由 python3 -c 生成）；其二**JSON 解析全部内嵌 python3 -c**——get_system_id 从 `/machines/?hostname=` 取 system_id（:186-194）。wait_for_ssh 5 秒轮询上限 120 秒（:271-293）支持 ProxyCommand。do_deploy 状态机：Step1 释放已部署机器（:452-466）→等 Ready→部署→等 SSH→收尾。

**maas_inventory.py（287 行）是 Python 姊妹**：build_oauth1_header(:66)/load_config(:85)/maas_api_get(:147)/get_preferred_ip(:168)/build_inventory(:180)——读 maas-inventory.yml 清单与网段偏好，从 MAAS 拉事实生成 Ansible inventory，"MAAS 是唯一事实源"。

**固件线选 paramiko 是刻意的**：playbook 注释说明原因——固件容器交互 `-it` 要 tty、Ansible ssh auto 模式翻车、且升级 BMC 会重启 sshd 打断多路复用（nvidia-dgx-fw-update.yml:4-7），故 `connection: paramiko_ssh`（:10）。角色 main.yml（71 行）：拷 parse_manifest.py 到节点（:15-16），pre 诊断（:22）→停服务（:34）→modprobe 卸载 nvidia/nvidia_uvm（:42）→update-firmware（:50）→post 诊断（:54），**always 块回收日志**（:59-60，注释直言成功时 pre-flight 可能被覆盖）；SBIOS/BMC 类升级最后提示**人工下电**（:68-71）而非自动化。

## 三、外部连接

- common.sh 是运行时锚：BASH_SOURCE 定位自身推 ROOT_DIR（scripts/common.sh:10-11），DEEPOPS_CONFIG_DIR 可覆盖且缺配置只警告（:12-16），DEEPOPS_VERSION 默认 `git describe` 运行时派生（:24-25）。
- maas_deploy 产物→maas_inventory 生成 inventory→交给 slurm/k8s playbook；skills/provision-with-maas 把同一流程写成 agent 可执行程序。
- DGX 固件角色与 L04 驱动线互斥：写固件前必须停服卸驱动。

## 四、数据流

裸机上电→MAAS（maas-controller 装）enlist→maas_deploy release/apply-profile/deploy（OAuth 直调）→wait_for_ssh 证 OS 就绪→maas_inventory 生成 inventory→（可选）固件线：诊断→停服卸驱动→fw-update→always 拉日志→人工下电提示→常规部署。

## 五、设计决策与甄别

1. **curl+OAuth 而非 maas CLI**：少一层依赖，代价是签名与 JSON 处理自己扛——bash 内嵌 python3 -c 的混合范式正为此而生。
2. **paramiko 只用在"会杀死连接的任务"**：全仓仅固件 playbook 用它，其余默认 ssh——按风险选连接插件。
3. **高危操作外置给人类**：机架级下电不自动化（main.yml:68-71），与 epilog"破坏性操作先判后执行"哲学一致。
4. 甄别：skills/provision-with-maas 是 2026 年新写的 agent skill 层，docs/pxe/maas.md 是面向人的老文档——两代并存。

## 六、新人提示

1. MAAS API key 形如 `key:token:secret` 三段冒号分隔（:167 IFS 拆分），配错时签名必错。
2. 固件升级永远先跑 pre-check；失败时 transfer-logs 拉回的日志在控制机。
3. common.sh 被所有 scripts/ 脚本 source，改它等于改全部脚本。
4. 多网卡机器的 maas-inventory.yml 必配 network_filter，否则 get_preferred_ip（:168）选错网卡。
