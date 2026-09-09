#!/usr/bin/env python3
"""
tinygit — 参照 git 的迷你版本控制系统

参照：git (Linus Torvalds)
csdiy 对应：csapp(文件/哈希) + os(page cache)

核心概念：blob(tree(commit)) 对象模型 + SHA1 内容寻址
功能：init / add / commit / log / diff / checkout
"""
import hashlib, os, json, time, zlib, sys
from pathlib import Path

TINYGIT_DIR = ".tinygit"

def init():
    if Path(TINYGIT_DIR).exists():
        print("Already a tinygit repository"); return
    for d in [TINYGIT_DIR, f"{TINYGIT_DIR}/objects", f"{TINYGIT_DIR}/refs"]:
        os.makedirs(d, exist_ok=True)
    _write(f"{TINYGIT_DIR}/HEAD", "ref: refs/main")
    _write(f"{TINYGIT_DIR}/index", json.dumps([]))
    print(f"Initialized empty tinygit repository in {TINYGIT_DIR}/")

def hash_object(data: bytes, obj_type="blob") -> str:
    """内容寻址存储（参照 git 的 SHA1 + zlib 压缩）"""
    header = f"{obj_type} {len(data)}\0".encode()
    full = header + data
    oid = hashlib.sha1(full).hexdigest()
    path = f"{TINYGIT_DIR}/objects/{oid[:2]}/{oid[2:]}"
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as f:
            f.write(zlib.compress(full))  # 参照 git 的 zlib 压缩
    return oid

def get_object(oid: str, expected=None) -> bytes:
    """读取对象（参照 git cat-file）"""
    path = f"{TINYGIT_DIR}/objects/{oid[:2]}/{oid[2:]}"
    if not os.path.exists(path):
        raise FileNotFoundError(f"Object {oid} not found")
    with open(path, "rb") as f:
        full = zlib.decompress(f.read())
    null_idx = full.index(b"\0")
    header = full[:null_idx].decode()
    obj_type, _ = header.split()
    if expected and obj_type != expected:
        raise ValueError(f"Expected {expected}, got {obj_type}")
    return full[null_idx + 1:]

def add(files: list[str]):
    """添加到暂存区（参照 git add）"""
    index = json.loads(_read(f"{TINYGIT_DIR}/index"))
    for fpath in files:
        if not os.path.isfile(fpath): continue
        data = open(fpath, "rb").read()
        oid = hash_object(data, "blob")
        entry = {"path": fpath, "oid": oid}
        # 去重更新
        index = [e for e in index if e["path"] != fpath] + [entry]
        print(f"  added: {fpath} ({oid[:8]})")
    _write(f"{TINYGIT_DIR}/index", json.dumps(index))

def commit(message: str) -> str:
    """创建提交（参照 git commit：tree + parent + msg）"""
    index = json.loads(_read(f"{TINYGIT_DIR}/index"))

    # 构建 tree 对象（参照 git tree：路径 + blob oid 列表）
    tree_data = json.dumps(index).encode()
    tree_oid = hash_object(tree_data, "tree")

    # 获取 parent
    head_ref = _read(f"{TINYGIT_DIR}/HEAD").strip()
    parent = None
    if head_ref.startswith("ref: "):
        ref_path = f"{TINYGIT_DIR}/{head_ref[5:]}"
        if os.path.exists(ref_path):
            parent = _read(ref_path).strip()

    # commit 对象（参照 git commit：tree + parent + timestamp + msg）
    commit_data = json.dumps({
        "tree": tree_oid,
        "parent": parent,
        "timestamp": time.time(),
        "message": message,
    }).encode()
    commit_oid = hash_object(commit_data, "commit")

    # 更新 ref
    if head_ref.startswith("ref: "):
        _write(f"{TINYGIT_DIR}/{head_ref[5:]}", commit_oid)
    print(f"[{ _current_branch()} {commit_oid[:8]}] {message}")
    return commit_oid

def log():
    """提交历史（参照 git log）"""
    head = _get_head_commit()
    while head:
        data = json.loads(get_object(head, "commit"))
        ts = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(data["timestamp"]))
        print(f"\033[33mcommit {head}\033[0m")
        print(f"Date: {ts}")
        print(f"\n    {data['message']}\n")
        head = data.get("parent")

def checkout(branch_or_oid: str):
    """切换分支/版本（参照 git checkout）"""
    ref_path = f"{TINYGIT_DIR}/refs/{branch_or_oid}"
    if os.path.exists(ref_path):
        commit_oid = _read(ref_path).strip()
        _write(f"{TINYGIT_DIR}/HEAD", f"ref: refs/{branch_or_oid}")
    else:
        commit_oid = branch_or_oid

    # 恢复文件（参照 git checkout 的文件更新）
    data = json.loads(get_object(commit_oid, "commit"))
    tree_data = json.loads(get_object(data["tree"], "tree"))
    for entry in tree_data:
        content = get_object(entry["oid"], "blob")
        os.makedirs(os.path.dirname(entry["path"]) or ".", exist_ok=True)
        with open(entry["path"], "wb") as f:
            f.write(content)
    print(f"Switched to {branch_or_oid}")

def diff():
    """显示未提交的变更（参照 git diff）"""
    index = json.loads(_read(f"{TINYGIT_DIR}/index"))
    print("Unstaged changes:")
    for entry in index:
        fpath = entry["path"]
        if not os.path.exists(fpath):
            print(f"  \033[31mdeleted: {fpath}\033[0m")
            continue
        current = open(fpath, "rb").read()
        if hash_object(current, "blob") != entry["oid"]:
            print(f"  \033[33mmodified: {fpath}\033[0m")

def _write(path, data): open(path, "w").write(data)
def _read(path): return open(path).read()
def _current_branch(): return _read(f"{TINYGIT_DIR}/HEAD").replace("ref: refs/", "").strip()
def _get_head_commit():
    head = _read(f"{TINYGIT_DIR}/HEAD").strip()
    if head.startswith("ref: "):
        ref = f"{TINYGIT_DIR}/{head[5:]}"
        return _read(ref).strip() if os.path.exists(ref) else None
    return head

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 main.py <command> [args]")
        print("Commands: init, add, commit, log, diff, checkout"); sys.exit(1)
    cmd = sys.argv[1]
    if cmd == "init": init()
    elif cmd == "add": add(sys.argv[2:])
    elif cmd == "commit": commit(" ".join(sys.argv[2:]) or "no message")
    elif cmd == "log": log()
    elif cmd == "diff": diff()
    elif cmd == "checkout": checkout(sys.argv[2])
    else: print(f"Unknown: {cmd}")

if __name__ == "__main__": main()
