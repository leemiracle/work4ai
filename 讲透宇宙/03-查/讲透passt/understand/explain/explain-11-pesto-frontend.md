# explain-11 · pesto.c：运行时转发规则配置前端

## 1. 角色定位

`pesto.c`（521 行）是独立的小前端二进制：连上运行中 passt/pasta 的配置 socket（`--config` 传入的 UNIX socket，服务端在 conf.c，见 explain-10），在线查看/增删/替换端口转发表。使用场景是容器/虚拟机的端口映射随业务动态变化——以前要重启 passt（断所有连接），现在 `pesto /tmp/passt.sock.config -t 8080:80` 一步到位。文件头（`pesto.c:3-9`）有个可爱的自我吐槽：全称 "Programmable Extensible Socket Translation Orchestrator"，紧跟着一行 "*(it's not actually extensible)*"——PESTO 与 PASST/PASTA 一样是递归缩写梗，但作者不想让你当真。它是纯客户端：没有事件循环、没有转发逻辑，一次连接完成"握手→全量读规则→本地改→全量回写"的同步事务。

## 2. 内部结构

**安全自锁先行**：`main()`（`pesto.c:298`）第一件事 `PR_SET_DUMPABLE=0`（`pesto.c:326`）+ 装构建期生成的 `filter_pesto` seccomp（`pesto.c:331-333`）；紧接着一个精心注释的细节——`setvbuf(stdout, stdout_buf, _IOFBF, ...)`（`pesto.c:338-339`）：**不预分配 stdout 缓冲，第一次 printf 会让 glibc malloc，直接打穿 seccomp 白名单**。静态 `stdout_buf[BUFSIZ]` 解决。这类"seccomp 与 libc 的暗坑"处理贯穿全仓。

**选项模型**（`usage()`，`pesto.c:53-102`， SPEC 语法文档极详尽）：三个模式开关 `-A/--add`、`-D/--delete`、`-C/--clear PIF`；四个规则选项 `-t/-u`（HOST 方向 TCP/UDP）与 `-T/-U`（SPLICE 方向）；`-s/--show` 前后对照打印。SPEC 语法是 fwd_rule.c 的 `PORTS` DSL：`all`、`auto`（只转发目标命名空间已绑定的端口）、逗号列表、`22-80` 区间、`22:23` 换端口、`192.0.2.1/5` 绑定地址限定、`~10-20` 排除（`pesto.c:63-90` 的示例全覆盖）。**两遍 getopt 模式**再现（与 conf.c 同款思路）：第一遍只记 update/show 标志（`pesto.c:343-377`），连上服务端读完全量规则后 `optind=0` 重扫第二遍做真正的规则修改（`pesto.c:449+`）——因为 `-t` 的语义是"改我从服务端拿到的表"，必须先有表。

**协议交互**：connect 后读 `pesto_hello`（`pesto.c:399-430`）：校验 magic（PESTO_SERVER_MAGIC）、版本（服务端版本只能 ≤ 客户端已知 PESTO_PROTOCOL_VERSION；版本 0 是实验协议，客户端也必须是 0 才继续，`pesto.c:408-418`）、两个尺寸字段 `pif_name_size`==PIF_NAME_SIZE、`ifnamsiz`==IFNAMSIZ（`pesto.c:420-430`，ABI 对齐检查——两边编译期常量不一致直接拒绝，防止结构体错位解析）。随后 `read_pif_conf()`（`pesto.c:163`）循环读每个 pif 的 `pesto_pif_info`（名称/能力位/规则计数）+规则数组，直到 PIF_NONE 结束符；服务端推送的表进 `struct configuration`（`pesto.c:113-116`，MAX_PIFS=3：HOST/SPLICE/+1）。

**修改逻辑**（`pesto.c:449-514`）：按名字找 `inbound`（HOST）/`outbound`（SPLICE）两张表；`-C` 直接 `fwd_rule_clear`；`-t` 在 MODE_CLEAR（默认）下**先清空再 parse**（替换语义，`pesto.c:480-484` 的 `inbound_cleared` 守卫保证只清一次），`-A` 后切 MODE_ADD（追加语义），`-D` 删指定项。修改全在本地副本上做，最后 `send_conf()`（`pesto.c:241`）把整个 configuration 序列化回写，服务端 `conf_recv_rules` 收进 pending 表并 `fwd_listen_switch()` 原子切换。`-s` 把"Previous configuration"与"Updated configuration"前后都打出来（`pesto.c:441-443, 509-511`），纯只读时打一份（`pesto.c:435-439`）。

## 3. 外部连接

依赖 `pesto.h`（协议结构：pesto_hello/pesto_pif_info/PESTO_* 常量）、`serialise.c`（read_u8/read_all_buf/write_all_buf 二进制原语）、`fwd_rule.c`（fwd_rule_parse/clear/read/write——**与服务端共用同一套规则解析与序列化代码**，这是协议一致性的根本保证）、`fwd.c` 的 `fwd_probe_ephemeral()`（`pesto.c:341`，探测临时端口范围，`auto`/`all` 语义需要它）、`log.h`（debug 宏）。被依赖：无（终端工具）。对端是 conf.c 的 conf_accept/conf_handler（EPOLL_TYPE_CONF*）。`slirp4netns.sh` 是生态另一半：把 slirp4netns 的 --mtu/--port-range 等选项翻译成 pasta 命令行，帮 Podman 用户零成本换引擎（tour t14 的另一半，shell 脚本不在本篇展开）。

## 4. 数据流

一次"给运行中的 pasta 加端口映射"：`pesto /run/pasta.sock.config -A -t 8080:80` → connect → 服务端 conf_accept 发 hello+HOST/SPLICE 两张表全量 → 客户端校验 ABI → `-A` 置 MODE_ADD（不清表）→ `fwd_rule_parse('t', del=false, "8080:80", &inbound->fwd)` 追加规则 → send_conf 全量回写 → 服务端 conf_handler 收进 fwd_pending → `fwd_listen_switch()`：关旧监听 socket、按新表开 8080 监听 → 客户端 shutdown/close 退出。此后 host:8080 的连接被转发到 namespace:80。现有连接不受影响——切换只动监听 socket 与规则表，流表照旧。

## 5. 设计决策

**全量同步而非增量指令**：客户端拿整表、改整表、还整表，服务端整体切换。没有"add one rule"这种细粒度命令——事务边界清晰、无部分失败状态、协议消息只有 hello/info/rule-array 三种。代价是规则多时多传几个字节，端口转发表撑死几百条，不值一提。**与服务端共享解析器**：SPEC 语法只在 fwd_rule.c 一处实现，CLI 字符串→规则的语义在两端绝对一致，杜绝"客户端能解析服务端不认"的漂移。**hello 里协商编译期常量**（PIF_NAME_SIZE/IFNAMSIZ）：这俩来自系统头文件，不同发行版/架构可能不同，握手期发现不匹配就死，好过静默错位解析结构体。**seccomp 极简白名单+静态缓冲**：客户端跑在可能是特权上下文的环境（root 执行 pesto），被攻破面要压到最小。

## 6. 新人提示

用法速查：只看 `pesto SOCK -s`；替换 HOST 表 `pesto SOCK -t 22 -t 8080:80`；追加 `pesto SOCK -A -t 443`；删单条 `pesto SOCK -D -t 443`；清空某方向 `pesto SOCK -C HOST`。注意 `-t` 默认是**替换**语义（先清后加），想保留旧规则必须加 `-A`——这是最容易踩的坑。服务端同步事务的已知限制（conf.c FIXME）：客户端中途死掉可能卡住服务端主循环，脚本里务必给 pesto 加超时。开发新规则字段时三处联动：fwd_rule.h 结构、fwd_rule_read/write 序列化、pesto.h 的 hello 不用动但版本号该 bump。调试用 `-d`：每条收发与解析决策都有 debug 输出；`--show` 的前后对照本身就是最好的验证手段。
