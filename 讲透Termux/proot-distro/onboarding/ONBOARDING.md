# proot-distro 入驻文档（ONBOARDING）

> 基于知识图谱（commit `737306f5`，1800 节点/3670 边/14 层/16 步导览/197 文件）与源码核实撰写，行号锚均已验证。

## 1. 一句话定位与治理

proot-distro 是 Termux 官方的 Linux 发行版安装管理器：纯 Python（最低 3.9，`pyproject.toml:10`）借助 proot 的 ptrace 仿真，在 Android 上无需 root 运行完整 Linux 容器——既可从 Docker registry 拉镜像装容器，也能把 Dockerfile 在容器里"解释执行"成 OCI 镜像。本仓为 Python 3.9+ 重构版：零运行时第三方依赖（`pyproject.toml:12` `dependencies = []`）。

治理三文档：README.md 用户参考；STRUCTURE.md 贡献者地图——逐模块职责表、数据布局（STRUCTURE.md:117）、五大关键流程（STRUCTURE.md:145）、贯穿性设计规则（STRUCTURE.md:187）、测试矩阵（STRUCTURE.md:215）；AGENTS.md 项目宪法（零依赖、安全优先、TLS 默认）。各模块开头 `# Architecture:` 注释记录塑造代码的攻击或 bug——先读头注释是硬习惯。

## 2. 仓库全景

```
proot-distro.py        零逻辑启动脚本（proot-distro.py:21 仅 import cli.main）
proot_distro/
  constants/paths/names/message/progress   小共享件（fan-in 63/50/45）
  dirfd/statedir/atomic/locking           安全文件系统层
  guestfile/l2s/shm/sysdata/session/arch  容器运行时与架构探测
  commands/            每命令一个模块，各暴露 command_<name>(args)
    login/ help/       login 子包 8 模块；help 以 pages+render 分离
  helpers/
    docker/            纯 Python OCI/Docker registry 客户端 8 模块
    build_engine/      Dockerfile 解释器 10 模块
    dockerfile/layer_diff/oci_writer/rootfs/tar_extract/download 等
  completions/         bash/zsh/fish 补全
tests/                 unit(36)/integration(17)/security(41)/live(3)+conftest 等
```

命令面：`_COMMAND_HANDLERS`（cli.py:64）注册 18 处理器——install/remove/rename/reset/login/list/backup/restore/clear-cache/copy/sync/run/build/push/ps/kill/search/help。包根 `proot_distro/__init__.py` 为全库 fan-in 之最（72）的纯文档 barrel；`pyproject.toml:22-24` 暴露 `proot-distro`/`pd` 双控制台脚本。

## 3. 架构分层速览（14 层自底向上）

- **L01 基础层**：constants（导入期绑定 XDG 布局）、paths（容器路径中枢）、names（容器名正则唯一事实源）、message/progress、安全三件套 locking/statedir/dirfd、session（`<pid>.json` 注册表）。fan-in 全库最高。
- **L02 运行时支持层**：guestfile 按 chroot 语义走读容器内文件；l2s/shm/sysdata 抹平 proot/Android 差异；arch 解析 ELF 选架构与 QEMU。
- **L03 通用 helpers 层**：download 共享网络策略、rootfs/tar_extract 安装解包、dockerfile/layer_diff/oci_writer/build_cache 构建构件。
- **L04 Registry 客户端层**：8 模块（transport/refs/cache/layers/pull/push 等），barrel re-export（fan-in 29）。
- **L05 build_engine 层**：Dockerfile 解释器（engine/stage/handlers/copy_step/run_step 等）。
- **L06 login 子包层**：login 全量实现，fan-out 命令模块之最。
- **L07/L08 命令层与 CLI 入口**：18 处理器；parser.py 选项与别名、help 子包。
- **L09-L12 测试四层**：conftest 沙箱/_builders/_registry 地基 → unit → security（41 件最大）→ integration。
- **L13/L14 文档补全与 CI**：三 shell 补全为包数据（`pyproject.toml:33-35`）；tests.yml 质量门、publish.yml。

## 4. 核心数据流：install → login 全链

**install**（install.py:138）按引用形态三路分派（install.py:163-164）：本地路径走 `install_from_local_file`（plain tar 用 strip 启发式；OCI tar 走 index.json 信任链逐步 digest 校验）；URL 走共享下载层；Docker 引用走 `helpers.docker.pull`——查 manifest/层双缓存（`oci_manifests/`+`oci_layers/`，cache.py:24）命中且重哈希全过则完全离线，未命中认证拉取、逐层流式验证+原子晋升。殊途同归：容器排它锁内经 `extract_tar_to_rootfs`（tar_extract.py:105，`strip` 与 `handle_whiteouts` 区分普通 rootfs 与 Docker 层）落盘，写 `manifest.json`、rootfs.py 集成修正、sysdata 桩；失败自清。

**login** 是终点：持可跨 exec 存活的共享容器锁，`open_container_pair`（paths.py:147）以 O_NOFOLLOW fd 钉住 container/rootfs 目录对（login/`__init__.py:324`）→ passwd 经 guestfile 走读容器内 `/etc/passwd` → env/bindings 合成环境 → `build_proot_args` 组装 argv → `os.fchdir(rootfs_fd)`（login/`__init__.py:663`）后 exec proot；`run` 读 Entrypoint/Cmd 后完全委托 login。

## 5. 关键机制深潜

**dirfd openat 安全模型**（fan-in 48）。威胁模型一句话："guest 可写目录里的一切名字都不可信"。一切操作以 `(dir_fd, name)` 寻址并逐级 O_NOFOLLOW，绝不把名字交给内核路径解析。三条易错规则制度化：chmod 只经 `_chmod_fd`（dirfd.py:444）；端点 open 加 O_NONBLOCK 拒 FIFO（dirfd.py:162）；写一律 O_EXCL 造新 inode（dirfd.py:188）。`Levels`（dirfd.py:801）停放浅层 fd，使 fd 数与树深无关。

**statedir 状态树**：RUNTIME_DIR 与 BASE_CACHE_DIR 两个信任根按名打开一次（statedir.py:62），其下组件逐级 O_NOFOLLOW 下行——guest 植入的符号链接无处把读写引向宿主；`read_state_file` 限 16MiB（statedir.py:77,82）。

**session 注册表**：每会话一个 `<pid>.json`（session.py:145），存活判定靠"清掉 O_CLOEXEC 的独占 flock 跨 exec 继承"（session.py:171,182）——锁 fd 活着即会话活着；只认十进制 `<pid>.json` 规范名，伪造记录不算会话。kill 按 TERM→QUIT 升级。

**registry 认证与层缓存**：`AuthStrippingRedirectHandler`（transport.py:157）跨 origin（scheme/host/port 严格比较）重定向时剥 Authorization；`PD_DOCKER_AUTH` 唯一凭证契约（transport.py:39）。cache.py 读取全走 statedir 安全步行，blob 消费前重哈希验 digest——`open_verified_layer` 驱逐坏层（cache.py:515）、`open_required_layer` 拒绝（cache.py:561）。

**build_engine 编排**：`BuildEngine` 遍历指令分派 handler，每个 FROM 对应一个 Stage（层序列+作用域），每条指令追加一条 OCI history。COPY/ADD 每条产出一个 OCI 层；RUN 是唯一真正执行用户代码的指令——run_step.py:106 先算 recipe hash 查 build_cache，命中回放层跳过 proot，未命中则 snapshot → proot 执行 → 再 snapshot，layer_diff 以 `(size, mtime_ns, mode, crc32)` 指纹产出增量层。错误归一到唯一异常 `BuildError`。

**tar_extract 防穿越**：成员路径先经 `safe_resolve_parts` 钳制——`..` 与空分量丢弃、绝对符号链接在 rootfs 重锚、尾部穿越拒绝（tar_extract.py:36-47），再以 O_NOFOLLOW 逐跳重走父链落盘；whiteout（`.wh.<name>`）删除后继名且不逃出解包根。

## 6. 构建与测试

`python proot-distro.py` 直接跑；测试 `pip install -e .[test]` + `pytest`。四类分工（tests/README.md）：**unit 36 件**逐模块覆盖；**integration 17 件**跨模块走通主流程（含零网络的 build 端到端）；**security 41 件**实证威胁模型——tar 穿越、容器目录符号链接逃逸（test_container_dir_escape.py 覆盖八命令）、缓存投毒重哈希拒绝、copy pin TOCTOU 竞态重现器、login `--rootfs=.` 钉住形态；**live 3 件**经 `RUN_LIVE_TESTS=1` 门控（conftest.py:99-100）走真实网络与 proot。

关键时序：constants 导入期绑定 XDG，conftest.py 须在生产模块导入前把 XDG_*/HOME 指进一次性沙箱（conftest.py:22-23）。`_builders.py` 构造 tarfile 高层 API 拒造的敌意成员；`_registry.py` 进程内三服务器（/v2/、token、CDN）让 pull/push 无网络跑通。CI（tests.yml）：proot job 从 termux/proot 固定 commit 自建二进制（tests.yml:29，不用发行版包）；test job 按 Python 3.9/3.12/3.15（tests.yml:69-73）跑四类 pytest（tests.yml:126,129,132）。

## 7. 新人上手路径（16 步 tour 精简为 9 里程碑）

1. **全景**：README 架构与存储两节 + STRUCTURE.md 全文（图谱 fan-out 最高的导航文档）。
2. **入口链**：proot-distro.py → cli.py:main（SIGQUIT cli.py:258/拒嵌套 proot cli.py:90/引导装 proot cli.py:149）→ `_COMMAND_HANDLERS`（cli.py:64）。
3. **基础层**：constants（IS_TERMUX 至少两个特征才认，constants.py:56,68）/paths/names/message/progress。
4. **安全模型**：dirfd.py 头注释 + statedir.py + locking.py + session.py，配 security/test_container_dir_escape.py——本仓灵魂，其余模块皆其应用。
5. **install 流水线**：install.py → pull/cache/layers 或 install_local.py → tar_extract.py → rootfs.py。
6. **build 引擎**：build.py → dockerfile.py（纯解析）→ engine.py+stage.py → copy_step/run_step → layer_diff/oci_writer。
7. **login 会话**：login/`__init__.py` → proot_cmd.py（`--rootfs=.`：proot_cmd.py:107 与 login/`__init__.py:541-546` 注释讲透防换名符号链接劫持）→ bindings/env/passwd/detach。
8. **生命周期命令**：backup/restore、copy/sync、remove/rename/reset、list/ps/kill——全站在 dirfd+锁+session 地基上。
9. **跑测试**：`pytest tests/unit tests/integration tests/security` 全绿即就绪；改代码前先读对应 security 测试。

## 8. 延伸阅读

- **知识图谱**：`proot-distro/.understand-anything/knowledge-graph.json`（validator 0 issues）。
- **仓内文档**：STRUCTURE.md（含贯穿性设计规则全表）、README.md、tests/README.md、各模块 `# Architecture:` 头注释。
- **上游**：github.com/termux/proot-distro 与姐妹项目 termux/proot；OCI image-spec 与 Docker distribution/reference（refs.py 规范依据）。
- **姊妹篇**：`讲透Termux/` 其余仓的 deepwiki 与图谱产物。
