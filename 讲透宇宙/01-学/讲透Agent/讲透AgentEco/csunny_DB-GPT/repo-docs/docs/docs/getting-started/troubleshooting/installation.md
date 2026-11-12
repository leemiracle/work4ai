---
sidebar_position: 1
title: Installation Issues
---

# Installation Issues

Common problems during DB-GPT installation and how to fix them.

## Python version errors

**Symptom:** `Python 3.10+ required` or version mismatch errors.

**Fix:**

```bash
python --version
# Must be 3.10 or newer
```

If you have multiple Python versions, specify the version explicitly:

```bash
uv python pin 3.11
uv sync --all-packages ...
```

## uv not found

**Symptom:** `command not found: uv`

**Fix:**

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Verify
uv --version
```

If installed but not found, ensure it's on your PATH:

```bash
export PATH="$HOME/.local/bin:$PATH"
```

## Dependency resolution failures

**Symptom:** `uv sync` fails with dependency conflict errors.

**Fix:**

1. Make sure you're using the latest uv:

```bash
uv self update
```

2. Clean the cache and retry:

```bash
uv cache clean
uv sync --all-packages --extra "base" ...
```

3. If using China mirrors, set the index URL:

```bash
UV_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple uv sync --all-packages ...
```

## Build failures for native extensions

**Symptom:** Compilation errors during `uv sync`, especially for packages like `tokenizers`, `grpcio`, or `psutil`.

**Fix:**

Install build tools:

```bash
# Ubuntu/Debian
sudo apt-get install build-essential python3-dev

# macOS
xcode-select --install

# CentOS/RHEL
sudo yum groupinstall "Development Tools"
```

For Rust-dependent packages (e.g., `tokenizers`):

```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
source $HOME/.cargo/env
```

## CUDA / GPU issues

**Symptom:** `CUDA not available` or GPU not detected.

**Fix:**

1. Verify CUDA installation:

```bash
nvidia-smi
# Should show your GPU and CUDA version
```

2. Install the matching CUDA extra:

```bash
# For CUDA 12.1
uv sync --all-packages --extra "cuda121" ...

# For CUDA 12.4
uv sync --all-packages --extra "cuda124" ...
```

3. Verify PyTorch sees the GPU:

```bash
uv run python -c "import torch; print(torch.cuda.is_available())"
```

## Port conflicts

**Symptom:** `Address already in use` on port 5670.

**Fix:**

```bash
# Find what's using the port
lsof -i :5670

# Kill the process
kill -9 <PID>
```

Or start on a different port:

```bash
uv run dbgpt start webserver --config configs/your-config.toml --port 5671
```

## Docker-specific issues

### Permission denied

**Symptom:** `permission denied` when running Docker commands.

**Fix:**

```bash
# Add your user to the docker group
sudo usermod -aG docker $USER
# Log out and back in
```

### NVIDIA runtime not found

**Symptom:** `docker: Error response from daemon: could not select device driver`

**Fix:** Install the NVIDIA Container Toolkit:

```bash
# Ubuntu
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/libnvidia-container/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/libnvidia-container/$distribution/libnvidia-container.list | sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
sudo apt-get update && sudo apt-get install -y nvidia-container-toolkit
sudo systemctl restart docker
```

## Database issues

### MySQL connection refused

**Symptom:** `Can't connect to MySQL server` during startup.

**Fix:**

1. Verify MySQL is running:

```bash
mysql -h127.0.0.1 -uroot -p -e "SELECT 1"
```

2. Check config values match your MySQL instance:

```toml
[service.web.database]
type = "mysql"
host = "127.0.0.1"    # Not 'localhost' — use IP
port = 3306
user = "root"
database = "dbgpt"
password = "your-password"
```

3. Create the database if it doesn't exist:

```bash
mysql -h127.0.0.1 -uroot -p < ./assets/schema/dbgpt.sql
```

## Still stuck?

- Check the detailed [FAQ](/docs/faq/install) for more solutions
- Search [GitHub Issues](https://github.com/eosphoros-ai/DB-GPT/issues)
- Ask in [GitHub Discussions](https://github.com/orgs/eosphoros-ai/discussions)
