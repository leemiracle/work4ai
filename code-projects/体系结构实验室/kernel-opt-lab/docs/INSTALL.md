# 安装指南 — Perfetto + 系统配置

> 适用于：飞腾 D3000 (FTC862) + 银河麒麟 V10 SP1 (aarch64, kernel 5.4.18)
> 已在 2026-06-29 验证通过

---

## 0. 前置依赖

```bash
# 验证关键组件
arch                        # 应为 aarch64
cat /proc/cpuinfo | head -5 # 应见 Phytium D3000
which perf gcc make         # 应全部存在
sudo -n true && echo OK     # sudo 免密（见下）
```

---

## 1. 系统级配置（一次性，永久生效）

### 1.1 解锁 perf_event + kptr

```bash
# 临时（重启失效）
echo 1 | sudo tee /proc/sys/kernel/perf_event_paranoid
echo 0 | sudo tee /proc/sys/kernel/kptr_restrict

# 永久（推荐）
sudo tee /etc/sysctl.d/99-perf-gator.conf > /dev/null <<EOF
kernel.perf_event_paranoid = 1
kernel.kptr_restrict = 0
kernel.perf_event_max_sample_rate = 100000
kernel.perf_event_mlock_kb = 516
EOF
sudo sysctl -p /etc/sysctl.d/99-perf-gator.conf
```

### 1.2 配置 sudo 免密（可选但强烈推荐）

```bash
# 先 visudo 校验，再写入
TMP=$(mktemp)
echo "lwz ALL=(ALL) NOPASSWD: ALL" > $TMP
sudo visudo -c -f $TMP   # 必须 "parsed OK" 才继续

sudo install -m 440 -o root -g root $TMP /etc/sudoers.d/lwz-nopasswd
sudo visudo -c            # 全局再校验一次
rm $TMP

# 验证
sudo -n true && echo "✅ 免密 sudo 生效"
```

> ⚠️ **安全提示**：仅适用于单用户工作站；多用户机器请用 `NOPASSWD: /usr/bin/perf, /usr/bin/perf record` 限定命令。

---

## 2. 安装 Perfetto v56.1（aarch64）

### 2.1 下载

```bash
# 最新版查询
LATEST=$(curl -sL https://api.github.com/repos/google/perfetto/releases/latest \
         | grep -m1 tag_name | cut -d\" -f4)
echo "最新版本: $LATEST"  # 2026-06 时为 v56.1

# 下载 aarch64 Linux 包（约 12MB）
curl -L -o /tmp/perfetto-arm64.zip \
  https://github.com/google/perfetto/releases/download/${LATEST}/linux-arm64.zip
```

### 2.2 安装

```bash
INSTALL_DIR="/opt/perfetto-${LATEST}"
sudo mkdir -p "$INSTALL_DIR"
sudo chown -R "$USER":"$USER" "$INSTALL_DIR"

unzip -o /tmp/perfetto-arm64.zip -d "$INSTALL_DIR"
# 解压会有 linux-arm64/ 子目录，提到顶层
sudo mv "$INSTALL_DIR/linux-arm64"/* "$INSTALL_DIR/"
sudo rmdir "$INSTALL_DIR/linux-arm64"
sudo chmod +x "$INSTALL_DIR"/*

# 软链
sudo ln -sfn "$INSTALL_DIR" /opt/perfetto
for cmd in perfetto tracebox traceconv trace_processor_shell traced traced_probes; do
    sudo ln -sf "/opt/perfetto/$cmd" "/usr/local/bin/$cmd"
done

# 验证
perfetto --version
tracebox --version
```

### 2.3 验证 PMU 端到端

```bash
sudo perf stat -a -e cycles,instructions,branch-misses -- sleep 2
# 应看到 cycles 在涨（GHz 级），IPC > 0
```

---

## 3. 浏览器连接配置（Chrome）

Perfetto UI 是 https 页面，要连本地 http://localhost:9001，默认被 Chrome 拦截。

```
1. 地址栏输入: chrome://flags/#unsafely-treat-insecure-origin-as-secure
2. 顶部输入框加: http://localhost:9001
3. 右侧下拉选 "Enabled"
4. 点 "Relaunch" 重启 Chrome
```

Firefox 无此限制。

---

## 4. 已知限制（麒麟 5.4.18 内核）

| 项 | 状态 | 替代方案 |
|---|---|---|
| `CONFIG_FUNCTION_TRACER` | **not set** ❌ | 无法采 sched_switch / syscall tracepoint |
| `CONFIG_FTRACE_SYSCALLS` | **not set** ❌ | 同上 |
| `CONFIG_HW_PERF_EVENTS` | ✅ y | PMU 全可用 |
| `/sys/kernel/tracing` | 不存在 | 不需要，PMU 走 `/dev/perf_event` |
| `tracebox --ftrace` | 不可用 | 用 `perf record -g` + `trace_processor_shell` 绕开 |

→ **结论**：Perfetto 的 PMU / 火焰图 / 进程统计全可用，仅 ftrace tracepoint 受限。

---

## 5. 卸载

```bash
# 停服务
sudo systemctl stop tp-http.service 2>/dev/null
sudo systemctl reset-failed tp-http.service 2>/dev/null

# 删 Perfetto
sudo rm -rf /opt/perfetto /opt/perfetto-*
sudo rm -f /usr/local/bin/{perfetto,tracebox,traceconv,trace_processor_shell,traced,traced_probes}

# 删系统配置
sudo rm -f /etc/sysctl.d/99-perf-gator.conf
sudo rm -f /etc/sudoers.d/lwz-nopasswd

# 重新加载
sudo sysctl --system
```

---

## 6. 故障排查

| 症状 | 原因 | 解决 |
|---|---|---|
| `perf stat` 全 0 | `perf_event_paranoid` 过严 | 设为 1（见 §1.1）|
| `gatord` / `tracebox` 报 ENOTSUP | 内核缺 PMU 支持 | 检查 `CONFIG_HW_PERF_EVENTS=y` |
| Chrome 连不上 localhost:9001 | mixed content 拦截 | 见 §3 |
| trace_processor 启动卡死 | systemd-run 子进程被杀 | 不要用 `nohup &`，必须 `systemd-run --unit=...` |
| perf.data 加载报 "Import errors" | 多事件 multiplexing | 单事件分次跑，或忽略（不影响主分析）|
