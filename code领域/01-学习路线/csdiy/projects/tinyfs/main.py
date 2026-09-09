#!/usr/bin/env python3
"""
tinyfs — 参照 xv6 fs.c 的内存文件系统

参照：xv6 fs.c / littlefs / FUSE
csdiy 对应：os §四(page cache/fsync) + xv6 lab

核心：inode + data block + 目录树 + 文件操作
"""
import time

class Inode:
    def __init__(self, inum, type="file"):
        self.inum = inum; self.type = type
        self.data = b"" if type == "file" else {}
        self.links = 0
        self.created = time.time()

class TinyFS:
    """
    内存文件系统（参照 xv6 的 fs.c + log.c）

    xv6 文件系统层次：
      inode → 数据块 / 目录条目
      log → WAL（保证 crash 安全）

    本实现用 dict 模拟（简化但概念完整）。
    """
    def __init__(self):
        self.inodes = {}
        self.next_inum = 1
        # 创建根目录
        root = self._alloc_inode("dir")
        self.root = root.inum

    def _alloc_inode(self, type):
        inum = self.next_inum; self.next_inum += 1
        inode = Inode(inum, type); inode.links = 1
        self.inodes[inum] = inode
        return inode

    def _resolve(self, path):
        """路径 → inode（参照 xv6 namei）"""
        if path == "/": return self.inodes[self.root]
        parts = [p for p in path.strip("/").split("/") if p]
        cur = self.inodes[self.root]
        for part in parts:
            if cur.type != "dir" or part not in cur.data:
                return None
            cur = self.inodes[cur.data[part]]
        return cur

    def _parent(self, path):
        """获取父目录 inode + 文件名"""
        parts = [p for p in path.strip("/").split("/") if p]
        name = parts[-1]
        parent_path = "/" + "/".join(parts[:-1])
        return self._resolve(parent_path), name

    def create(self, path, type="file"):
        """创建文件/目录（参照 xv6 create）"""
        parent, name = self._parent(path)
        if not parent or parent.type != "dir":
            return None
        if name in parent.data:
            return None  # 已存在
        inode = self._alloc_inode(type)
        parent.data[name] = inode.inum
        return inode

    def read(self, path):
        """读文件（参照 xv6 readi）"""
        inode = self._resolve(path)
        if not inode or inode.type != "file":
            return None
        return inode.data

    def write(self, path, data):
        """写文件（参照 xv6 writei）"""
        inode = self._resolve(path)
        if not inode:
            inode = self.create(path)
            if not inode: return False
        if inode.type != "file": return False
        inode.data = data if isinstance(data, bytes) else data.encode()
        return True

    def list(self, path="/"):
        """列目录（参照 xv6 dirlookup）"""
        inode = self._resolve(path)
        if not inode or inode.type != "dir": return []
        result = []
        for name, inum in inode.data.items():
            child = self.inodes[inum]
            prefix = "d" if child.type == "dir" else "f"
            size = len(child.data) if isinstance(child.data, bytes) else len(child.data)
            result.append(f"{prefix} {name:20s} {size:>8}B")
        return result

    def delete(self, path):
        """删除（参照 xv6 unlink）"""
        parent, name = self._parent(path)
        if not parent or name not in parent.data: return False
        inum = parent.data[name]
        del parent.data[name]
        if inum in self.inodes: del self.inodes[inum]
        return True

    def stat(self):
        files = sum(1 for i in self.inodes.values() if i.type == "file")
        dirs = sum(1 for i in self.inodes.values() if i.type == "dir")
        total = sum(len(i.data) for i in self.inodes.values() if isinstance(i.data, bytes))
        return {"files": files, "dirs": dirs, "total_bytes": total, "inodes": len(self.inodes)}

def main():
    fs = TinyFS()
    print("tinyfs — 内存文件系统（参照 xv6 fs.c）\n")

    # 创建目录和文件
    fs.create("/docs", "dir")
    fs.create("/docs/readme", "file")
    fs.write("/docs/readme", "Hello from tinyfs!")
    fs.write("/tmp.log", "application log data\n" * 10)
    fs.create("/src", "dir")
    fs.write("/src/main.py", "print('hello world')")

    # 列目录
    print("/ (root):")
    for item in fs.list("/"): print(f"  {item}")
    print("\n/docs:")
    for item in fs.list("/docs"): print(f"  {item}")
    print("\n/src:")
    for item in fs.list("/src"): print(f"  {item}")

    # 读文件
    print(f"\nread('/docs/readme'): {fs.read('/docs/readme')}")
    print(f"read('/src/main.py'): {fs.read('/src/main.py')}")

    # 删除
    fs.delete("/tmp.log")
    print(f"\n删除 /tmp.log 后:")
    for item in fs.list("/"): print(f"  {item}")

    print(f"\nstat: {fs.stat()}")

if __name__ == "__main__": main()
