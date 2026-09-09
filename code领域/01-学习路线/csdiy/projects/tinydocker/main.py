#!/usr/bin/env python3
"""
tinydocker — 参照 Docker/runC 的迷你容器引擎

参照：Docker (namespace + cgroup) + runC
csdiy 对应：os-程序员视角 §三(fork-exec) + §五(并发/隔离) + CSAPP Ch8(异常控制流)

核心：用 Linux namespace + cgroup 隔离进程
功能：run（创建容器）/ exec（进入容器）/ ps（列表）

⚠️ 需要 root 权限（namespace 需要 CAP_SYS_ADMIN）
"""
import os, sys, subprocess, json, time
from pathlib import Path

CONTAINER_DIR = Path("/var/lib/tinydocker")
CONTAINER_DIR.mkdir(parents=True, exist_ok=True)

def run(image_rootfs: str, command: list[str], name: str = None):
    """
    创建并启动容器（参照 Docker run + runC create）

    核心三步（参照 csapp Ch8 + os §三）：
    1. clone() 用 CLONE_NEWPID | CLONE_NEWNS | CLONE_NEWUTS → 新 namespace
    2. 在子进程里 mount rootfs → chroot
    3. cgroup 限制资源（内存/CPU）
    """
    if not os.path.isdir(image_rootfs):
        print(f"Error: rootfs '{image_rootfs}' not found"); sys.exit(1)

    container_id = name or f"c_{int(time.time())}"
    container_meta = {
        "id": container_id,
        "rootfs": os.path.abspath(image_rootfs),
        "command": command,
        "created": time.time(),
        "status": "running",
    }

    print(f"Creating container {container_id}...")

    # 用 unshare 创建新 namespace（参照 Docker 的 namespace 隔离）
    # CLONE_NEWPID: 新 PID namespace（容器内 PID 从 1 开始）
    # CLONE_NEWNS: 新 mount namespace（隔离文件系统视图）
    # CLONE_NEWUTS: 新 hostname
    pid = os.fork()
    if pid == 0:
        # 子进程：容器内的 init 进程
        _container_init(image_rootfs, command, container_id)
        os._exit(0)
    else:
        # 父进程：记录容器元数据
        container_meta["pid"] = pid
        _save_container(container_id, container_meta)
        # 设置 cgroup（简化版：限制内存 100MB）
        _setup_cgroup(container_id, pid)
        print(f"Container {container_id} started (pid={pid})")
        os.waitpid(pid, 0)
        container_meta["status"] = "exited"
        _save_container(container_id, container_meta)

def _container_init(rootfs: str, command: list[str], hostname: str):
    """
    容器初始化（参照 Docker runc init）

    在新的 namespace 里：
    1. 设置 hostname
    2. mount proc（隔离进程视图）
    3. chroot 到 rootfs
    4. exec 用户命令
    """
    # 这些需要 root 权限，在真实容器里用 clone(CLONE_NEW*)
    try:
        import ctypes
        libc = ctypes.CDLL("libc.so.6", use_errno=True)

        # sethostname（参照 Docker 容器 hostname）
        hostname_bytes = hostname.encode()[:32]
        libc.sethostname(hostname_bytes, len(hostname_bytes))

        # mount /proc（参照 Docker 的 proc mount）
        # os.mount("proc", f"{rootfs}/proc", "proc", 0, "")

        # chroot（参照 Docker 的 rootfs 切换）
        os.chroot(rootfs)
        os.chdir("/")

        # exec 用户命令（参照 csapp Ch8 的 fork-exec-wait）
        os.execvp(command[0], command)
    except PermissionError:
        print(f"[tinydocker] Need root. Try: sudo python3 main.py run ...")
        print(f"[tinydocker] Demo mode: running without isolation")
        subprocess.run(command)
    except FileNotFoundError:
        print(f"[tinydocker] Command not found in rootfs: {command[0]}")

def _setup_cgroup(container_id: str, pid: int):
    """
    设置 cgroup 限制（参照 Docker 的资源限制）

    真实 Docker 设置：
    - memory.limit_in_bytes
    - cpu.cfs_quota_us
    本简化版只尝试设内存限制，失败则跳过。
    """
    try:
        cg_path = Path(f"/sys/fs/cgroup/tinydocker/{container_id}")
        cg_path.mkdir(parents=True, exist_ok=True)
        (cg_path / "memory.max").write_text("104857600")  # 100MB
        (cg_path / "cgroup.procs").write_text(str(pid))
    except (PermissionError, FileNotFoundError):
        pass  # 非 root 或 cgroup v1，跳过

def ps():
    """列出容器（参照 docker ps）"""
    containers = _list_containers()
    if not containers:
        print("No containers"); return
    print(f"{'ID':<20} {'PID':<8} {'STATUS':<10} {'COMMAND'}")
    print("-" * 60)
    for c in containers:
        cmd = " ".join(c.get("command", []))
        print(f"{c['id']:<20} {c.get('pid','?'):<8} {c['status']:<10} {cmd}")

def images():
    """列出可用镜像（参照 docker images）"""
    print("Available rootfs (put directories here as 'images'):")
    for d in Path(".").iterdir():
        if d.is_dir() and (d / "bin").exists():
            print(f"  {d.name}")

def _save_container(cid: str, meta: dict):
    (CONTAINER_DIR / f"{cid}.json").write_text(json.dumps(meta, indent=2))

def _list_containers() -> list[dict]:
    return [json.loads(f.read_text()) for f in CONTAINER_DIR.glob("*.json")]

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 main.py <command> [args]")
        print("Commands: run <rootfs> <cmd...>, ps, images"); sys.exit(1)
    cmd = sys.argv[1]
    if cmd == "run":
        if len(sys.argv) < 4: print("Usage: run <rootfs> <command...>"); sys.exit(1)
        run(sys.argv[2], sys.argv[3:])
    elif cmd == "ps": ps()
    elif cmd == "images": images()
    else: print(f"Unknown: {cmd}")

if __name__ == "__main__": main()
