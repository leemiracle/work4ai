# 02 · diagnostic-policy.ts：40+ 诊断工具的逐 argv 白名单引擎

> 文件：`helm/mosaic-stack/files/openclaw-seed/extensions/diagnostic-policy.ts`（97 行）
> 消费方：automation-context、remote-ssh 插件；文档锚：`docs/security_model.md:46`

## 一、角色定位

AFOA 允许 agent 在 View 模式下对远端主机跑诊断命令，但"只读"二字必须落在代码上而不是提示词上。`diagnostic-policy.ts` 就是这把尺子：它为每一个允许的诊断工具**逐个定义 argv 校验规则**，任何一个参数不合法即整体拒绝。97 行里没有一行执行逻辑——它是纯函数校验器，职责边界清晰到极致：**"能不能跑"在这里判，"怎么跑"在 runner**。

它服务两个关键决策点：

1. **动态工具分级**：`run_remote_ssh` 是全仓唯一按 argv 动态分级的工具（`automation-context.ts:213-218`）——`isAllowedDiagnosticArgv` 返回 true 则 read、否则 edit。白名单引擎的判定结果直接决定一次调用走"免审批直跑"还是"Edit+HITL 审批"。
2. **View 模式的远程诊断放行**：remote-ssh 插件的策略层以它为闸（`remote-ssh/index.ts:69`），执行层再独立复查一次（`remote-ssh/index.ts:125`）——同一判据两处使用，防线不因单点遗漏而失守。

## 二、内部结构

### 出口守卫 isAllowedDiagnosticArgv

整个文件只有一个导出（`diagnostic-policy.ts:91-97`），类型谓词 `value is string[]`，四道整体边界先于逐工具校验：

1. 数组、非空、**≤64 元**（`diagnostic-policy.ts:92`）；
2. 每参是字符串、非空、**≤1024 字节**、且过 `ARGUMENT` 字符集正则（`diagnostic-policy.ts:93`，正则定义在 `:5`：`^[A-Za-z0-9_./:=,+%@-]+$`）——这个字符集是第一道命门：**空格、引号、分号、管道、`$`、反引号、换行全部不在白名单里**，shell 元字符在字符集层就被歼灭，任何拼接注入都无从谈起；
3. 程序名过 `PROGRAM` 正则（`diagnostic-policy.ts:94`，`:4`：`^[A-Za-z0-9][A-Za-z0-9_-]*$`）——**禁路径**（不许 `/usr/bin/x` 绕别名）、禁 `-` 开头（不许把参数伪装成程序名）；
4. 程序名小写查 `RULES` 表（`diagnostic-policy.ts:96`）——查无此程序返回 undefined，`=== true` 才放行。**fail closed**：表里没有的工具一律拒绝，不存在"默认放行"分支。

### 三种（半）校验形态

任务简报概括为 exact/flags/pairs 三形态，源码里恰好是三个工厂函数加两个专用状态机：

**exact——全等命令表**（`diagnostic-policy.ts:7-8`）：闭包吃一组字符串数组，参数序列必须与某条白名单**逐项全等**。适合封闭式只读命令：`ipmitool` 只准 7 条固定命令（`mc info`/`fru print`/`sensor list`/`sdr list`/`sdr elist`/`sel list`/`chassis status`，`diagnostic-policy.ts:58`）；`rdma` 只准 5 条 `link/dev/resource/system/statistic show`（`diagnostic-policy.ts:71`）；`ip` 只准 9 条 show 形态（`diagnostic-policy.ts:72`，含 `-s link show`、`-br address show` 变体）。**这是最严的形态：连参数值都不许变**。

**flags——正则全参匹配**（`diagnostic-policy.ts:10`）：每个参数独立过同一个正则。适合"flag 组合自由但值封闭"的工具：`uname`（`diagnostic-policy.ts:54`）允许 `-a -s -n` 等短旗与 `--kernel-name` 等长旗任意组合，但正则穷尽了全部合法词形——`--option=value` 形态也钉死值域（如 `df` 的 `--output=[A-Za-z0-9_,+-]+`，`diagnostic-policy.ts:62`）。`hostname`（`:53`）、`uptime`（`:55`）、`nproc`（`:56`）、`lscpu`（`:59`）、`lsblk`（`:60`）、`free`（`:61`）、`vmstat`（`:63`）、`iostat`（`:64`）、`dmesg`（`:76`）、`sensors`（`:79`）皆此形态。

**pairs——单参/带值/前缀式三集配对**（`diagnostic-policy.ts:29-37`）：`single` 集合的参数独立成参；`valued` 集合的参数必须吞噬下一参（且下一参存在）；`prefixes` 正则命中的 `--key=value` 形态免验。`journalctl` 是教科书案例（`diagnostic-policy.ts:39-46`）：`--no-pager`/`-r`/`-k` 等 11 个单参（`:42`）、`-u`/`-n`/`-p`/`-o` 等 7 个带值参（`:43`）、`--unit=`/`--since=`/`SYSLOG_IDENTIFIER=` 等 5 类前缀式（`:44`）三集各司其职。注意带值参的**值本身不经 `ARGUMENT` 之外的二次校验**——但出口守卫的字符集已经把值域压到无害字符内。

**两个专用状态机**补在三种形态之外：

- `nvidiaSmi`（`diagnostic-policy.ts:12-27`）：`needsId` 单步状态机——遇到 `-i`/`--id` 后下一参必须匹配 GPU id 正则 `^[A-Za-z0-9_.:-]+$`（`:16`），收尾时若仍悬着未消费的 needsId 直接 false（`:26`，防 `-i` 落单）。白名单值覆盖 `-L`/`-q`/`--display=COMPUTE` 等枚举与 `--query-(gpu|compute-apps)=` 带字段列表的形态（`:20-24`）。这是全表最精细的一条规则。
- 复用工厂 `nvidiaToolArgs`（`diagnostic-policy.ts:48-50`）被 `ibstat`/`ibstatus`/`ibv_devinfo`/`ibv_devices` 四个 InfiniBand 工具共享（`:67-70`）——只准短旗与 `--key=value` 形态。

另有四条内联 lambda 值得点名：`ethtool` 只准 0/1 参或 7 个只读子命令旗之一（`diagnostic-policy.ts:73`）；`systemctl` 首词必须是 `status`/`is-active`/`is-failed`/`list-units`/`list-unit-files` 五个只读动词，其余参数过词形正则（`:74`）——**`systemctl restart` 在首词就被拒**；`ss` 参数过宽松的 `ARGUMENT` 但**显式拉黑 `-K`/`--kill`**（`:81`）——这是"读参数集宽松但抠掉杀伤性 flag"的代表；Slurm 全家 `sacct`/`squeue`/`sinfo`/`sstat`/`sdiag`/`sreport` 只做字符集校验（`:82-87`），`scontrol` 则首词限 `show`/`ping`（`:88`）。

### RULES 表全景

`RULES`（`diagnostic-policy.ts:52-89`）实际收录 **36 个程序**：主机/内核 4（hostname/uname/uptime/nproc）、GPU 1（nvidia-smi）、BMC 1（ipmitool）、硬件拓扑 9（lscpu/lsblk/free/df/vmstat/iostat/mpstat/lspci/dmidecode/numactl/sensors——见对应行）、InfiniBand/RDMA 5（ibstat/ibstatus/ibv_devinfo/ibv_devices/rdma）、网络 3（ip/ethtool/ss）、系统服务 3（systemctl/journalctl/dmesg）、进程 1（ps）、Slurm 7（sacct/squeue/sinfo/sstat/sdiag/sreport/scontrol）。

## 三、外部连接

- **automation-context.ts:4** 的 import 是全仓唯一业务依赖方向的起点：`toolAccess` 在 `automation-context.ts:217` 调用 `isAllowedDiagnosticArgv` 完成 run_remote_ssh 的动态分级。
- **remote-ssh/index.ts:11** 导入它，策略层白名单命中即免审批放行（`remote-ssh/index.ts:69`），执行层再独立判定决定走只读直跑还是 mutation-ledger 幂等通道（`remote-ssh/index.ts:125-143`）。
- **docs/security_model.md:46** 直接点名"policy in `diagnostic-policy.ts` validates the executable and every argument"，并列举 nvidia-smi/ipmitool/journalctl/squeue/scontrol 为代表命令——文档、代码、策略三层口径一致。
- 测试 `helm/mosaic-stack/tests/diagnostic-policy.test.mjs` 两组用例钉死边界：有界只读 argv 放行；变更 flag、任意程序、路径、shell 语法全部拒绝。
- AGENTS.md 的行为侧呼应：`workspace/AGENTS.md:27` 直接给出三条白名单内的推荐 argv（GPU 固件 `["nvidia-smi","--query-gpu=name,driver_version,vbios_version","--format=csv"]`、BMC `["ipmitool","mc","info"]`、Slurm 守护 `["journalctl","-u","slurmd","-n","100","--no-pager"]`）——提示词示例全部选白名单内的形态，模型抄作业也不会抄出界。

## 四、数据流

一次 View 模式的远程诊断调用，判据流如下：

```
模型发起 run_remote_ssh {host, argv}
  → remote-ssh 策略层 classifySshRequest 先做请求形态校验（remote-ssh/policy.ts:52）
  → isAllowedDiagnosticArgv(argv)（remote-ssh/index.ts:69）
      ├─ 命中 → 放行，无审批
      └─ 未命中 → HITL 且非 Auto → 审批卡片 / 否则 block
  → execute 再次判定（remote-ssh/index.ts:125）
      ├─ diagnostic=true → runSsh 直跑（:127）
      └─ false → runMutationOnce 幂等通道（:137-143）
```

同一 argv 在一次调用中被判定两次（策略层 + 执行层）。这不是冗余：策略层的结果影响审批 UI 展示，执行层的结果决定幂等记账路径——两处共享同一纯函数，结论必然一致，但各自服务不同的下游机制。

## 五、设计决策

1. **字符集白名单先于工具白名单**。`ARGUMENT` 正则（`diagnostic-policy.ts:5`）在程序规则之前就把 shell 元字符全部排除——即便某条工具规则写得宽松（如 Slurm 全家的纯字符集校验），注入面也已被整体边界封死。这是纵深防御的最内层。
2. **逐工具逐参数而非通用正则**。36 条规则每条单独手写，看似笨重，实则把"什么算只读"的领域知识显式化：`systemctl` 的五个只读动词、`ss` 的 kill 拉黑、`ipmitool` 的七条命令——每条规则都是一次对工具语义的人工审读。通用方案（如"禁写路径的 mount 点"）做不到这种精度。
3. **fail closed 的查表尾巴**（`diagnostic-policy.ts:96`）：`RULES[program]?.(args) === true`——查无程序返回 undefined，严格等比较才放行。新增诊断工具必须显式写规则，"忘了配"默认是拒绝而非放行。
4. **大小写归一只在程序名**（`:96` toLowerCase）：`NVIDIA-SMI` 与 `nvidia-smi` 同判，但参数区分大小写——`-L` 与 `-l` 在 nvidia-smi 里语义不同，归一反而会开洞。
5. **上限常量全线对齐**：64 元/1024 字节与 remote-ssh 策略层的 `MAX_ARGS`/`MAX_ARG_BYTES`（`remote-ssh/policy.ts:15-16`）同值，与 kubernetes 策略的 64 上限（`kubernetes/policy.ts:55`）同值——同一套量纲横跨三个执行域，评审时只需记一组数。

## 六、新人提示

- **加一个诊断工具 = 加一条 RULES**。先决定形态：封闭命令选 exact、flag 组合选 flags、键值对选 pairs、有顺序依赖就写状态机。写完务必补 `tests/diagnostic-policy.test.mjs` 的正反用例。
- **不要**试图在这里放行任何写操作——本文件的语义锚是 `docs/security_model.md:46-48`："View mode can run a bounded set of read-only diagnostic commands"。写操作属于 Edit/Auto 通道，走审批与台账，与白名单引擎职责不同。
- `ps` 的规则（`diagnostic-policy.ts:80`）允许任意无元字符参数（含 `-e -f -o` 组合）——它是全表最宽松的一条，若未来发现滥用，收紧点在 `ARGUMENT` 允许的 `:=` 等字符。
- 调试技巧：`isAllowedDiagnosticArgv(["journalctl","-u","slurmd","-n","100","--no-pager"])` 可直接在 node 里跑——纯函数零依赖，不需要起任何服务。
- ⚠️ 甄别记录：任务简报与图谱 summary 称"40+ 诊断工具"，源码核实 `RULES` 表实为 **36 个程序**（`diagnostic-policy.ts:52-89` 逐键清点）；三形态框架成立，另有 nvidiaSmi/nvidiaToolArgs 两个共用/专用校验器与四条内联 lambda。本文按源码 36 个口径撰写。

（行号锚基于当前工作树源码逐条核实。）
