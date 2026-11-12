# vllm/snapshot/ — 进程检查点子系统：CRIU 冻结引擎、canary oracle 验收与事务式 create/restore

> 源码：`vllm/snapshot/`（5 文件 2019 行，主力 runtime.py 1318 行）｜CLI 入口 `vllm/entrypoints/cli/snapshot.py`｜vLLM 2026-10-28 @06e172b5cf

## ① 角色定位

vLLM 冷启动的大头不在推理，而在 import、权重加载、CUDA context 与编译缓存预热。`snapshot/` 冲这一段来：把**已完成初始化的引擎进程树**用 CRIU 整棵冻结成磁盘工件，同一主机原样复活，跳过全部初始化。它不进 serving 热路径，唯一入口是 CLI 三动作 `vllm snapshot create|inspect|restore`（vllm/entrypoints/cli/snapshot.py:91），落到 `create_snapshot`（vllm/snapshot/controller.py:58）与 `restore_snapshot`（:96）。

五文件：controller.py（132 行）=事务编排；runtime.py（1318 行）=主力，`LocalSnapshotTools`（vllm/snapshot/runtime.py:186）封装 CRIU/cuda-checkpoint/nvidia-smi、/proc 盘点与 pidfd 管理；server.py（252 行）=**被冻结的子进程本体**（`python -m vllm.snapshot.server`）；manifest.py（276 行）=pydantic 严格 schema+路径安全契约；types.py（37 行）只有 Oracle 值对象。边界收得很紧：单卡（TP/PP/DP/PCP 全 1）+不可变远端模型 40 位 revision+单实例明文 HTTP+禁投机解码（vllm/entrypoints/cli/snapshot.py:22-67）+Linux x86_64（:68）。

## ② 内部结构

**runtime.py 三段**：进程/系统盘点（:118-484）、CRIU 执行与 link-remap 管理（:486-741）、恢复期 pin/清理（:742-1318）。`__init__`（:189）定位三个外部二进制、CRIU CUDA 插件目录（:193）与超时（:196，默认 900s）；`preflight`（:219）查 Linux x86_64、pidfd（:222）、`cuda_plugin.so`（:232）、`sudo -n` 免密（:234）。CRIU 统一走 `_criu`（:486）：sudo env 透传 ignored-FD 映射表，固定五选项 --shell-job/--ext-unix-sk/--tcp-established/--link-remap/--file-locks（:58），失败截尾打日志（:516）。

**server.py 是"可重放"的 API server**：`run_vllm_snapshot_child`（vllm/snapshot/server.py:198）状态机=canary→睡眠→彩排→再睡眠→冻结点等待→恢复服务；`parse_vllm_args`（:178）拒绝 grpc/headless（:189）。

**manifest.py 的 schema 防线**：`SnapshotRuntimeIdentity`（vllm/snapshot/manifest.py:37）12 字段 frozen+strict+extra=forbid；`SnapshotManifest`（:54）加 `boundary: Literal["post-engine-init-reloadable-state-released"]`（:56）——这个字符串就是快照的定义：冻结点=引擎初始化完成且可重载状态已释放。

## ③ 外部连接

- **外部二进制**：criu、cuda-checkpoint、nvidia-smi（vllm/snapshot/runtime.py:227-229）+CRIU CUDA 插件——CUDA context 不在 CRIU 原生能力内，靠插件协同转储，preflight 因此硬查插件（:232-233）。
- **与 EngineCore 生命周期的关系**：子进程不另造暂停机制，直接复用 sleep 家族——`_release_reloadable_state` 就是 `engine.sleep(level=2)`（vllm/snapshot/server.py:92；level 语义见 vllm/v1/engine/core.py:1023-1027，level 2=丢弃全部 GPU 显存）；恢复侧 `_restore_reloadable_state`（:97）=`wake_up(tags=["weights"])`→`collective_rpc("reload_weights")`→`wake_up(tags=["kv_cache"])`（AsyncLLM 层 vllm/v1/engine/async_llm.py:1198/:1213）。
- **被依赖**：仅 CLI（vllm/entrypoints/cli/snapshot.py:74/:86 惰性 import）；`inspect_snapshot`（vllm/snapshot/manifest.py:275）供 inspect 打印。
- **环境契约**：子进程默认补 `VLLM_WORKER_MULTIPROC_METHOD=spawn` 与 `NCCL_IB_DISABLE=1`（vllm/snapshot/runtime.py:260-261）——CRIU 转储不了 RDMA 状态，持 IB 描述符直接拒绝创建（:365）。

## ④ 数据流

```
CREATE（vllm/snapshot/controller.py:58）：
  preflight @vllm/snapshot/runtime.py:219 → 0700 目录+路径安全校验（vllm/snapshot/manifest.py:157-194）
  launch_child @vllm/snapshot/runtime.py:241 → python -m vllm.snapshot.server
    （start_new_session @:269，输出→child.log）
  子进程：canary @vllm/snapshot/server.py:124（prompt="The capital of France is"
    @:19；temperature=0/单 token/seed=0）→ sleep(2)→唤醒重载→彩排比对
    @:213 → 再 sleep(2) → detach 输出流 @:146 → 写 ready.json →
    wait_for_release_marker @:158 阻塞＝冻结点
  控制器：wait_ready @vllm/snapshot/runtime.py:274 → inventory @:442（进程树/CUDA
    持有者/唯一 GPU UUID/io_uring 禁入 @:451/外部 TCP 禁入 @:159/JIT
    缓存指纹 @:413）→ dump @:704（+link_remap 收编 @:583）→ verify_dead
    @:742 → make_manifest @:832（argv 脱敏）→ publish @:891（manifest
    原子落盘＝工件"完整"唯一标志）
RESTORE（vllm/snapshot/controller.py:96）：
  read_manifest → validate_identity @vllm/snapshot/manifest.py:122（12 字段全等）
  → restore @vllm/snapshot/runtime.py:1126（PID 占用探测→缓存复核 @:1098→child.log
    截断 @:679→link_remap 预放 @:622→CRIU restore --restore-detached→
    pidfd 钉进程树 @:969）
  → release @:1179（bind 探测后写 release.json{host,port}）
  → 子进程在冻结点醒来：恢复权重/KV → setup_server（vllm/entrypoints/launchers/launcher.py:366）
    → build_and_serve
  → wait_listener @:1206 → request_oracle @:1222（HTTP /v1/completions
    同款 canary）→ oracles_match（vllm/snapshot/types.py:27，容差 1e-3 @:35）→
    complete_restore @:1300；失败走 cleanup @:1262（TERM→KILL→poll）
```

## ⑤ 设计决策

1. **先证可重置、再冻结**：冻结前完整跑一遍 sleep(2)→唤醒→重载→彩排 canary，要求与首次输出全等（vllm/snapshot/server.py:210-215）。GPU 权重/KV 留在磁盘是设计而非妥协：镜像只保 CPU 侧，彩排证明"释放-重建"闭环保真。
2. **canary oracle 是唯一验收标准**：单 token、贪心、固定种子、取 sampled logprob（vllm/snapshot/server.py:128-134），恢复后经真实 HTTP 前端复测（vllm/snapshot/runtime.py:1222-1252），容差 1e-3（vllm/snapshot/types.py:35）；CLI 侧禁 raw_logits/processed_logits 模式（vllm/entrypoints/cli/snapshot.py:61）。
3. **manifest.json 即发布动作**：工件完整=manifest 原子存在（vllm/snapshot/manifest.py:235；O_EXCL+O_NOFOLLOW+fsync :213-232）；失败路径 finally rmtree（vllm/snapshot/controller.py:90-93），半成品永远读不到。身份闸门严于"版本号相同"：torch version.py AST 解析 cuda runtime（:776-800，不 import torch）、cuda-checkpoint sha256（:906）、machine-id、GPU UUID、环境哈希（:817-830）。
4. **按"主机上有敌对邻居"设防**：路径链逐级查 symlink/属主/组写、工件目录 0700（vllm/snapshot/manifest.py:157）；恢复后 pidfd 钉整棵树，根必须是 session+pgid leader 且 cmdline 含 `--release-file` 原路径（vllm/snapshot/runtime.py:996-1012）——防 PID 复用把清理信号发给别人的进程。
5. **CRIU 能力边界清单化**：io_uring（:451）/IB-RDMA（:365）/外部已建立 TCP（:159）三项禁入；/dev/shm link_remap 收编进工件（:583）；JIT 缓存（triton/flashinfer/inductor，:78-104）恢复前逐一 sha256 复核（:1098）。
## ⑥ 新人提示

- 读法：先 controller.py 两函数（:58/:96）拿骨架 → vllm/snapshot/server.py:198 子进程状态机 → runtime.py 按数据流段号跳读。
- 调试第一现场是工件目录：child.log、images/dump.log、ignored-nvidia-fds.tsv；restore 会把 child.log 截断回捕获尺寸（:679），别指望它保留恢复期日志。
- 冻结点在 `wait_for_release_marker`（vllm/snapshot/server.py:158）——被恢复进程从这里醒来，之后才恢复权重并起 HTTP；失败先查 release.json 与 bind 探测（vllm/snapshot/runtime.py:1183）。
- `--enable-sleep-mode` 由控制器强制追加（vllm/snapshot/controller.py:53-54），argv 里的 --snapshot-dir 会被剥掉（:48，前缀匹配连缩写都认）。
- 单卡/同主机/同环境是硬边界：validate_create_args（vllm/entrypoints/cli/snapshot.py:19）与 validate_identity（vllm/snapshot/manifest.py:122）都直接 raise；扩多卡先读 `_pin_restored_tree`（vllm/snapshot/runtime.py:1018）。
- 与 sleep mode 区分：线上 sleep(1)/wake_up 是省显存换驻留（vllm/v1/engine/core.py:1019），snapshot 是把"sleep(2) 后的裸进程镜像"搬上磁盘做冷启动储备——同一家族，两种产物。
