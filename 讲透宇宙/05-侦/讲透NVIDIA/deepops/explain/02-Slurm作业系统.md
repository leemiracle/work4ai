# 02 · Slurm 作业系统：PAM、prolog/epilog 与 PATH drop-in

## 角色定位

roles/slurm 是全仓最重的角色（17 个 task 文件，从源码 build 到节点配置），把一台普通 Linux 机器改造成"没有作业就 SSH 不进去"的调度节点。它的三件防御性设计——pam_slurm_adopt 门禁、编号化 prolog/epilog 清理链、slurmd PATH drop-in——是 DGX 类共享集群长期运维踩坑的沉淀，每个都带长注释记录事故现场。

## 内部结构

compute.yml 负责节点侧：grub cgroup 参数（`compute.yml:20-24`）、pmix 环境块（:72-83）、prolog/epilog 引入（:96-98）。PAM 段是精髓：`:161-166` 注释钉死踩坑链——slurm_pam_lib_dir 随架构派生，build.yml 因版本匹配跳过重编时，模块可能不在本轮回选目录，"a wrong -account line in /etc/pam.d/sshd locks operators out of the node"。因此 `:167-174` 先 stat 探测模块真实存在，`:176-191` 不存在即 fail 并在报错里点名 `slurm_force_rebuild=true` 或手工指定 lib 目录；`:193-206` 才写入三行 PAM 栈（adopt sufficient → localusers 白名单 sufficient → adopt required）。`:222-242` 把 Ubuntu/RHEL 的 pam_systemd.so 注释掉——它与 adopt 语义冲突（官方文档背书）。service-files.yml 的 PATH 段（`service-files.yml:25-30` 注释）解释了另一个事故：slurmd 继承 systemd 最小 PATH，Enroot 的 slurm-pmi hook 调 scontrol 报 "Command not found"，导致 Pyxis 容器全部拒启；解法是 `:40-49` 写 `/etc/systemd/system/slurmd.service.d/10-slurm-path.conf` drop-in 把 `slurm_install_prefix/bin` 前置进 PATH，配合 compute.yml:143-148 的无条件重启每次收敛都生效。

## 外部连接

slurm.conf 模板声明 `Prolog={{ slurm_config_dir }}/prolog.sh`、`Epilog=.../epilog.sh`（slurm.conf:62-63），PrologFlags=Alloc,Serial,Contain（:57）。prolog.sh/epilog.sh（各 6 行）只做 logger 打点加调用 `shared/bin/run-parts.sh`（epilog.sh:5）。run-parts.sh 是自实现版：`run-parts.sh:76-78` 注释说明因 CentOS 的 run-parts 是无 flag 的简版 bash 才重造轮子，按文件名序遍历 `epilog.d/*`；`:88` 判定同用户还有作业在跑则跳过 last-user-job 类脚本——这是"最后一个作业才清理"语义的判定守卫。pyxis/enroot、nhc（HealthCheckProgram，slurm.conf:72）都挂在这条链上。

## 数据流

epilog 执行序即文件名编号：`40-lastuserjob-processes`（杀用户残余进程）→ `41-lastuserjob-ssh`（`41-lastuserjob-ssh:8` 用 `sed -i` 把用户从 /etc/localusers 除名，收回 SSH 权）→ `42-lastuserjob-cleanup`（清 /tmp 与 /dev/shm）→ 50+/60/80 排他资源清理。40 号脚本的防御最典型：`:22-37` 把 grep 退出码三态化（0=白名单命中不杀、1=确定不在名单可杀、>1=查找失败不许杀），`|| lookup_rc=$?` 防 set -e 吞状态；42 号 `:43-47` 先 `id -u` 解析用户名，解析失败宁可跳过也不在残缺列表上执行 rm；`:52` 起的 -xdev 注释解释为何要阻止 find 越过挂载点删掉别的节点正在用的文件。prolog_epilog.yml:16-39 会在收敛时先删除 prolog.sh/prolog.d 等旧布局文件再铺新文件，防历史残留双跑。

## 设计决策

① PAM 白名单双写：compute.yml:150-157 同时写 `/etc/localusers`（运行时 SSH 门禁）与 `localusers.backup`（epilog 豁免名单）——40/41/42 三兄弟全部先查 backup 再动手，运维账号在计算节点提交作业不会被断线。② 守卫与执行分离：run-parts.sh 只判定"要不要 reap"，杀进程在编号脚本里做，tests/slurm-epilog/run-tests.sh 因此能零依赖回归。③ 拒绝静默半配置：所有清理脚本宁可 logger 告警退出 0 也不在证据不足时执行破坏动作。

## 新人提示

排障顺序记牢：Pyxis 容器起不来先查 slurmd PATH drop-in；SSH 被锁在节点外先看 pam.d/sshd 的 ANSIBLE MANAGED BLOCK 与 `/etc/localusers`；作业结束后用户文件丢失，看 epilog.d 各脚本的豁免日志（logger -t slurm-epilog）。改 epilog 脚本必须走 template（Jinja 变量 `{{ slurm_config_dir }}` 渲染后落盘），且新脚本按编号插入正确执行段位。
