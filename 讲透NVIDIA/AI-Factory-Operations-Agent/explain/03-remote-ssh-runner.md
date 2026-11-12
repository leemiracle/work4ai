# 03 · remote-ssh/runner：钉死 20 项连接参数的加固执行器

> 文件：`helm/mosaic-stack/files/openclaw-seed/extensions/remote-ssh/runner.ts`（96 行）
> 协同：`remote-ssh/policy.ts`（81 行）、`remote-ssh/index.ts`（176 行）；对照件 `kubernetes/runner.ts`（88 行）

## 一、角色定位

如果说 diagnostic-policy 决定"什么命令能跑"，runner 决定"命令在一条什么样的 SSH 通道上跑"。AFOA 的 agent 跑在 Kubernetes Pod 里，要诊断的是集群外的裸金属节点——中间这条 SSH 通道是整个系统里唯一离开集群边界的执行路径，所以它被加固到"参数全部钉死、模型没有任何自由度"的程度：`buildSshArgs`（`remote-ssh/runner.ts:15-43`）生成的连接参数里，模型能影响的只有**目标主机别名**（还必须是装机时注册的）和**远端命令字符串**（policy 层已转义）两项。

三个文件各司一职：`policy.ts` 是启动期与请求期的校验层（主机表、argv 边界、POSIX 引号转义）；`runner.ts` 是进程执行层（spawn、限额、超时、脱敏）；`index.ts` 是 OpenClaw 插件层（注册 `run_remote_ssh` 工具与 `remote-ssh-access` 可信策略，串起审批与幂等台账）。

## 二、内部结构

### buildSshArgs：一份逐项可审计的加固清单

`remote-ssh/runner.ts:15-43` 拼出最终 ssh 命令行。**19 个 `-o` 选项**（`:20-38`）加 `-F /dev/null`、`-i`、`-p` 三个直接参数（`:17-19`），按防御目标分组读：

**掐断凭据旁路（6 项）**——`BatchMode=yes`（`:20`，禁止任何交互式提示）、`IdentitiesOnly=yes`（`:21`，只用 `-i` 指定的这一把 key）、`IdentityAgent=none`（`:22`，禁 ssh-agent——Pod 里若有别的 agent 也不许用）、`PasswordAuthentication=no`（`:23`）、`KbdInteractiveAuthentication=no`（`:24`）、`PreferredAuthentications=publickey`（`:25`，认证方法白名单只剩公钥）。加上 `NumberOfPasswordPrompts=0`（`:35`），密码/键盘交互路径被三重封死。

**钉死主机信任（3 项）**——`StrictHostKeyChecking=yes`（`:26`，禁 TOFU：陌生主机指纹直接失败而不是询问后接受）、`UserKnownHostsFile=<装机路径>`（`:27`，只信 Helm 灌入的 known_hosts）、`GlobalKnownHostsFile=/dev/null`（`:28`，连系统级全局hosts 也不认）。三者合起来：**SSH 层的主机身份完全由装机者定义**，运行期不可协商。

**封掉网络与转发隧道（5 项）**——`ProxyCommand=none`（`:29`）、`ProxyJump=none`（`:30`，禁跳板——没有这两项，攻击者可用 ProxyCommand 让"受限主机"变成任意目标的跳板，经典 SSRF 变种）、`ForwardAgent=no`（`:31`）、`ClearAllForwardings=yes`（`:32`，端口/X11/agent 转发全清）、`RequestTTY=no`（`:34`，不给远端 TTY，交互式提权工具无从起）。

**禁本地命令与配置（2 项+1 参数）**——`-F /dev/null`（`:17`，**完全忽略** `~/.ssh/config`——用户级配置里的 LocalCommand/ProxyJump/IdentityFile 全部失效，这是防"配置文件后门"的根治手段）、`PermitLocalCommand=no`（`:33`，即便配置残留也禁执行）。

**生命周期（3 项）**——`ConnectTimeout` 由工具超时换算并钳在 1-30 秒（`:36`），`ServerAliveInterval` 钳 1-30 秒（`:37`）、`ServerAliveCountMax=2`（`:38`）——两条保活合计保证僵尸连接在 timeoutMs 量级内被杀掉，不会挂死进程。

最后 `--` 终结符（`:39`）+ `user@address`（`:40`）+ 远端命令（`:41`）：`--` 之后的一切不再是 ssh 的选项——**即使远端命令里混进 `-oSomething` 也会被当作命令的一部分传给远端 shell**，而不是改写本地 ssh 行为。

### runSsh：最小环境的受控 spawn

`remote-ssh/runner.ts:52-96` 的执行纪律：

- **环境变量白名单只有三个**：`HOME`/`LANG`/`PATH`（`:55-59`）——ssh 客户端在此环境里几乎读不到任何可能改变行为的变量（配合 `-F /dev/null`，连 `SSH_AUTH_SOCK` 之类的注入面都被清空）；
- `shell: false`（`:60`）——参数数组直达 execve，无中间 shell；
- `stdio: ["ignore","pipe","pipe"]`（`:61`）——**stdin 直接 ignore**：这条通道天生不给远端喂任何输入，交互式命令（sudo 密码、分页器）只能失败；
- 输出限额：stdout+stderr 合计计数，超 `maxOutputBytes`（默认 65536，`remote-ssh/index.ts:37`）立即 SIGKILL 并报错（`:79-86`）——防 `yes` 死循环或大文件 cat 撑爆上下文；
- 超时定时器 SIGKILL（`:91-94`）；`settled` 单次收口旗（`:66-78`）保证 error/close/timeout 三路事件只结算一次；
- **redactSshOutput**（`:45-50`）：出站前把私钥路径、known_hosts 路径、整个 `/var/run/mosaic-ssh` 凭据目录替换成占位符——错误信息里最常见的"泄漏源"（路径回显）被 preemptively 抹掉。

### policy.ts：请求的最后一道形态校验

`normalizeHosts`（`remote-ssh/policy.ts:24-46`）在**启动期**校验主机表：alias/address/user 三正则（`:11-13`）、端口 1-65535 整数（`:39`）、别名查重（`:42`）——任一非法直接抛错，插件起不来（fail fast，装错配置比带病运行好）。

`classifySshRequest`（`remote-ssh/policy.ts:52-81`）在**请求期**把关：只认 `host`/`argv` 两键，多余键直接拒（`:55-56`）；主机必须在注册表内（`:58-59`）；argv 1-64 参、每参 ≤1024 字节、禁 NUL/CR/LF（`:60-69`）；**程序名不得以 `-` 开头**（`:70`，防参数伪装成程序名）；basename 查 `FORBIDDEN_PROGRAMS = {ssh, scp, sftp}`（`:14,71-72`，禁嵌套 SSH——不许把受限跳板当垫脚石再往外跳）；全命令 ≤8192 字节（`:73-75`）。

`quoteRemoteArg`（`remote-ssh/policy.ts:48-50`）是 POSIX 单引号转义的标准写法 `'` → `'"'"'`——argv 逐字拼接成远端命令串时**不引入任何 shell 元字符**。注意这里存在一个结构性的语义边界：远端命令最终仍由远端 shell 解释，单引号转义保证的是"参数不被二次切分/展开"，与 `ARGUMENT` 字符集白名单（`diagnostic-policy.ts:5`）叠加后才构成完整防线——前者管拼接安全，后者管内容安全。

### index.ts：策略层如何用 runner

可信策略 `remote-ssh-access`（`remote-ssh/index.ts:56-97`）：自动化会话无条件 block（`:61-66`）；`classifySshRequest` 抛错转 block（`:90-95`）；白名单命中 / `hitl=false` / Auto 模式三者其一放行（`:69`）；否则构造审批卡片（title 带 host 别名、description 带完整 argv 与 `user@address:port`，`:70-77`），先试 Slack 身份审批再落通用 `requireApproval`，超时行为 deny（`:78-89`）。

执行侧双通道（`remote-ssh/index.ts:122-173`）：诊断命令直跑（`:126-136`）；其余走 `runMutationOnce` 幂等通道，终态由 exitCode 决定（`:137-143`），重放返回 `replayed/previousStatus` 而不重复执行（`:144-152`）。异常路径统一返回 `blocked: true, executed: false` 的结构化结果（`:162-172`）——**拒绝也是一等返回值**，不是崩溃。

## 三、外部连接

- **上游**：`remote-ssh/index.ts:5-14` 导入 automation-context（会话/审批判定）、diagnostic-policy（白名单）、mutation-ledger（幂等）、本目录 policy/runner——remote-ssh 是把前两篇主角全部串起来的集成点。
- **对照件 kubernetes/runner.ts**：同构的 spawn 纪律（限额收集+SIGKILL+超时，`kubernetes/runner.ts:55-72`），但 stdin 语义相反——kubectl 的 stdin 是一等公民（`stdio[0]` 按需 pipe，`:34`；`child.stdin?.end(stdin)`，`:66`），SSH 的 stdin 恒 ignore。这个差异是下一篇的重点之一。
- **凭据来源**：keyPath/knownHostsPath 默认 `/var/run/mosaic-ssh/`（`remote-ssh/index.ts:31-32`），由 Helm chart 的 Secret 挂载灌入——runner 从文件系统读，从不过问 Secret 内容。
- **测试**：`helm/mosaic-stack/tests/remote-ssh-policy.test.mjs` 6 用例（主机解析与 POSIX 引号保真、未知主机拒绝、畸形 argv、嵌套 SSH 拒绝）；`tests/remote-ssh-kind-e2e.sh` 现场生成 ed25519 密钥对灌成 Secret 的端到端验证；`tests/setup-kind-session-access-targets.sh` 搭靶机。
- **文档锚**：`docs/security_model.md:50-55` 逐条对应"主机是装机定义的别名、用户/端口/密钥来自 Helm、不接受选项与身份覆盖、命令以受验 argv 传输"。

## 四、数据流

一次 Edit 模式的非白名单命令（如重启服务）：

```
run_remote_ssh {host:"gpu-03", argv:["systemctl","restart","nvidia-fabricmanager"]}
  → classifySshRequest：host 查表 ✓、argv 边界 ✓、basename∉{ssh,scp,sftp} ✓
  → isAllowedDiagnosticArgv(argv) = false（systemctl 只允许 5 个只读动词）
  → 非 Auto + hitl → 审批卡片（argv 全文 + user@address:port）
  → 批准 → runMutationOnce 领号（fingerprint 入账）
  → runSsh：
      spawn("/tools/ssh", ["-F","/dev/null","-i",key,...19 个 -o,"--","user@addr",
                           "'systemctl' 'restart' 'nvidia-fabricmanager'"],
            {env:{HOME,LANG,PATH}, shell:false, stdio:["ignore","pipe","pipe"]})
  → 限额/超时看护 → redactSshOutput → {code, stdout, stderr} → 台账终态回写
```

关键点：**审批卡片上的命令与实际执行的命令由同一份 argv 派生**（policy.ts:74 的 JSON.stringify 与 runner.ts:41 的 remoteCommand 同源），人批的就是机器跑的，不存在"展示一个、执行另一个"的缝隙。

## 五、设计决策

1. **加固参数写死在代码而不是配置**。`buildSshArgs` 没有一个可调项（除 timeout 换算出的两个数）——加固清单若可配置，就存在被配置放松的可能。`-F /dev/null` 是典范：不是"忽略危险指令"，而是整个配置文件宇宙都不存在。
2. **stdin 的两种哲学**。SSH 通道 stdin 恒 ignore（`runner.ts:61`）是因为诊断命令天然无输入、且交互面即提权面；kubectl 通道 stdin 开放（`kubernetes/runner.ts:34,66`）是因为 `exec ... -- bash -s` 喂脚本是合法刚需。于是 stdin 的前置校验被放在 kubectl 的**策略层**而非执行层：`kubernetes/policy.ts:102-108` 规定 exec 且带 stdin 时，`-i`/`--stdin` 必须出现在 `--` 之前——错误消息明说 "no command was executed"（`:106`），即**策略层在执行前就拦截**，避免"命令跑了但 stdin 没接上"的半执行状态。AGENTS.md 把这条写进了工具描述（`kubernetes/index.ts:209`："For scripts, use exec with -i before -- and send the script through stdin to bash -s"）。
3. **环境变量白名单而非黑名单**（`runner.ts:55-59`）：新变量默认不进来——与 diagnostic-policy 的字符集白名单同一哲学。
4. **kill 用 SIGKILL 不用 SIGTERM**（`:82,92`）：超限/超时的子进程没有"优雅退出"的资格，给 SIGTERM 留窗口就是给恶意命令留收尾动作（删日志、起反弹）的时间。
5. **输出脱敏在收口处统一做**（`:75-76`）：不是每个可能泄漏的点各自防，而是 stdout/stderr 汇总后过一遍 redact——单点覆盖，无遗漏路径。

## 六、新人提示

- 改 `buildSshArgs` 时先问"这个改动会不会让装机者失去对主机身份或凭据的控制"——19 个 `-o` 里的大部分存在的意义就是**否定 ssh 的默认协商行为**，删任何一个都要给出等价补偿。
- `ConnectTimeout` 的钳制区间 1-30 秒（`runner.ts:36`）与 `ServerAliveInterval` 的 1-30（`:37`）是刻意的小值：SSH 通道的失败要快，agent 还有别的主机可试（AGENTS.md:27 明确"If the command or target is unavailable, report that evidence source as unavailable and continue"）。
- `/tools/ssh` 与 `/tools/kubectl`（`remote-ssh/index.ts:30`、`kubernetes/index.ts:36`）是包装命令路径，不是系统 ssh——chart 可以在这层再套一层 wrapper（如日志/审计），代码不必感知。
- ⚠️ 甄别记录：任务简报称"20+ ssh -o 加固项"——源码核实 `-o` 选项为 **19 个**（`runner.ts:20-38` 逐项清点），加 `-F /dev/null` 合计 20 个连接加固参数；"exec 的 -i/--stdin 前置校验在策略层"已核实（`kubernetes/policy.ts:102-108`），但属 kubernetes 域而非本文件，本文已按对照关系讲清。图谱 summary 与源码无冲突。

（行号锚基于当前工作树源码逐条核实。）
