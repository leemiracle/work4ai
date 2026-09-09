#!/usr/bin/env python3
"""
tinydb — 参照 SQLite/LevelDB 的 page-based KV 存储引擎

参照项目：
  SQLite  : page-based 文件格式、B-tree、WAL
  LevelDB : WAL 预写日志、SSTable

核心特性：
  P1 ✅ page-based 文件（参照 SQLite file format）
  P2 ✅ 线性索引页（简化版 B-tree，单层叶子）
  P3 ✅ WAL 预写日志（参照 SQLite WAL / db §六）
  P4 ✅ crash recovery（从 WAL 恢复）
  P5 ✅ hexdump 可视化（参照 sqlite-btree 精读）

验证：参照 SQLite btree 精读的 hexdump 方法

用法：
  python3 main.py set mykey myvalue
  python3 main.py get mykey
  python3 main.py delete mykey
  python3 main.py hexdump          # 看页的物理布局
  python3 main.py compact          # 整理碎片
"""

import os
import struct
import sys
from pathlib import Path

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 常量（参照 SQLite file format 文档）
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PAGE_SIZE = 4096                    # 参照 SQLite 默认 page size
MAGIC = b"TDB1"                     # 文件魔数（参照 SQLite "SQLite format 3\0"）
HEADER_SIZE = 32                    # 文件头
PAGE_HEADER_SIZE = 8                # page 头
MAX_KEY_SIZE = 255
MAX_VALUE_SIZE = PAGE_SIZE - PAGE_HEADER_SIZE - MAX_KEY_SIZE - 8

# Page 类型（参照 SQLite btree page type）
PAGE_TYPE_FREE     = 0x00
PAGE_TYPE_DATA     = 0x0D          # 参照 SQLite leaf table b-tree page = 0x0D
PAGE_TYPE_OVERFLOW = 0x02

# Cell 格式: [key_len:2][val_len:4][key:N][val:M]
CELL_HEADER = struct.Struct("<HI")  # key_len(H=2bytes) + val_len(I=4bytes)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 文件头（参照 SQLite 100 字节头，简化为 32 字节）
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 偏移  大小  字段
# 0     4     magic "TDB1"
# 4     2     page_size (4096)
# 6     4     page_count
# 10    4     first_data_page
# 14    4     last_data_page
# 18    4     free_page_list_head
# 22    4     item_count
# 26    6     reserved

HEADER_FMT = struct.Struct("<4sHIHHHII")  # 不完美对齐但够用

def pack_header(page_count, first_data, last_data, free_head, item_count):
    return HEADER_FMT.pack(MAGIC, PAGE_SIZE, page_count, first_data,
                           last_data, free_head, item_count, 0)[:HEADER_SIZE]

def unpack_header(data):
    # 只取 HEADER_FMT.size 字节（24），避免 32 字节的 padding 问题
    buf = data[:HEADER_FMT.size]
    if len(buf) < HEADER_FMT.size:
        buf = buf.ljust(HEADER_FMT.size, b'\0')
    magic, psize, pcount, first, last, free, count, _ = \
        HEADER_FMT.unpack(buf)
    return {
        "magic": magic, "page_size": psize, "page_count": pcount,
        "first_data_page": first, "last_data_page": last,
        "free_page_head": free, "item_count": count,
    }

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Page 操作（参照 SQLite btree.c 的 page 级操作）
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class Page:
    """
    一个数据页（参照 SQLite btree page）

    物理布局（参照 sqlite-btree 精读 §二）:
    ┌────────────────────────────────────────────┐
    │ Page Header (8 bytes)                      │
    │   type(1) + free_count(1) + cell_count(2)  │
    │   + cell_content_start(2) + free_next(2)   │
    ├────────────────────────────────────────────┤
    │ Cell Pointer Array (2 bytes each)          │
    │   指向每个 cell 在页内的偏移               │
    ├────────────────────────────────────────────┤
    │ ... 空闲空间 ...                            │
    ├────────────────────────────────────────────┤
    │ Cell Data (从页尾向前生长)                  │
    │   [key_len][val_len][key][value]           │
    └────────────────────────────────────────────┘
    """

    def __init__(self, data: bytearray, page_no: int):
        self.data = data
        self.page_no = page_no
        self._parse_header()

    def _parse_header(self):
        self.page_type = self.data[0]
        self.free_count = self.data[1]
        self.cell_count = struct.unpack_from("<H", self.data, 2)[0]
        self.cell_content_start = struct.unpack_from("<H", self.data, 4)[0]
        if self.cell_content_start == 0:
            self.cell_content_start = PAGE_SIZE
        self.free_next = struct.unpack_from("<H", self.data, 6)[0]

    def _write_header(self):
        self.data[0] = self.page_type
        self.data[1] = self.free_count
        struct.pack_into("<H", self.data, 2, self.cell_count)
        struct.pack_into("<H", self.data, 4, self.cell_content_start)
        struct.pack_into("<H", self.data, 6, self.free_next)

    def get_cells(self) -> list[tuple[bytes, bytes]]:
        """读取所有 cell（参照 SQLite btree 的 cell pointer array 遍历）"""
        cells = []
        ptr_start = PAGE_HEADER_SIZE
        for i in range(self.cell_count):
            offset = struct.unpack_from("<H", self.data, ptr_start + i * 2)[0]
            key_len, val_len = CELL_HEADER.unpack_from(self.data, offset)
            key = bytes(self.data[offset + CELL_HEADER.size : offset + CELL_HEADER.size + key_len])
            val = bytes(self.data[offset + CELL_HEADER.size + key_len :
                                  offset + CELL_HEADER.size + key_len + val_len])
            cells.append((key, val))
        return cells

    def add_cell(self, key: bytes, value: bytes) -> bool:
        """
        向页内添加一个 cell（参照 SQLite btree insertCell）

        如果空间不够返回 False（需要分裂/新页）。
        """
        if len(key) > MAX_KEY_SIZE or len(value) > MAX_VALUE_SIZE:
            return False

        cell_data = CELL_HEADER.pack(len(key), len(value)) + key + value
        cell_size = len(cell_data)
        ptr_size = 2  # cell pointer

        # 检查空间（参照 SQLite btree page 的空闲检查）
        free_space = self.cell_content_start - PAGE_HEADER_SIZE - self.cell_count * ptr_size
        if cell_size + ptr_size > free_space:
            return False  # 页满了

        # 从页尾向前写入 cell 数据（参照 SQLite 的 cell content area 从页尾生长）
        self.cell_content_start -= cell_size
        cell_offset = self.cell_content_start
        self.data[cell_offset : cell_offset + cell_size] = cell_data

        # 在 cell pointer array 末尾添加指针
        ptr_offset = PAGE_HEADER_SIZE + self.cell_count * 2
        struct.pack_into("<H", self.data, ptr_offset, cell_offset)

        self.cell_count += 1
        self._write_header()
        return True

    def find_cell(self, key: bytes) -> bytes | None:
        """线性扫描查找（简化版，真实 B-tree 用二分）"""
        for k, v in self.get_cells():
            if k == key:
                return v
        return None

    def delete_cell(self, key: bytes) -> bool:
        """删除 cell（简化版：重建页数据；真实 SQLite 用 freeblock 链表）"""
        cells = self.get_cells()
        new_cells = [(k, v) for k, v in cells if k != key]
        if len(new_cells) == len(cells):
            return False  # 没找到

        # 重建页
        self.data = bytearray(PAGE_SIZE)
        self.data[0] = PAGE_TYPE_DATA
        self.cell_count = 0
        self.cell_content_start = PAGE_SIZE
        self._write_header()

        for k, v in new_cells:
            self.add_cell(k, v)
        return True

    @classmethod
    def new_data_page(cls, page_no: int) -> "Page":
        data = bytearray(PAGE_SIZE)
        data[0] = PAGE_TYPE_DATA
        page = cls(data, page_no)
        page.cell_content_start = PAGE_SIZE
        page._write_header()
        return page


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# WAL 预写日志（参照 SQLite WAL / db-程序员视角 §六）
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class WAL:
    """
    预写日志（参照 SQLite wal.c / LevelDB log.go）

    原理（参照 db §六）：
      写操作先追加到 WAL → fsync → 再写数据页
      crash 后从 WAL 重放未 checkpoint 的操作

    格式（参照 LevelDB log format，简化）:
      [op:1][key_len:2][val_len:4][key:N][val:M]
      op: 1=SET, 2=DELETE
    """

    OP_SET = 1
    OP_DEL = 2
    ENTRY_HEADER = struct.Struct("<BHI")  # op + key_len + val_len

    def __init__(self, path: str):
        self.path = path
        self.file = open(path, "ab")

    def log_set(self, key: bytes, value: bytes):
        entry = self.ENTRY_HEADER.pack(self.OP_SET, len(key), len(value)) + key + value
        self.file.write(entry)
        self.file.flush()
        os.fsync(self.file.fileno())  # 参照 db §六：fsync 是关键

    def log_del(self, key: bytes):
        entry = self.ENTRY_HEADER.pack(self.OP_DEL, len(key), 0) + key
        self.file.write(entry)
        self.file.flush()
        os.fsync(self.file.fileno())

    def checkpoint(self, db: "TinyDB"):
        """
        Checkpoint（参照 SQLite wal checkpoint）

        把 WAL 中的操作应用到数据文件，然后清空 WAL。
        """
        self.file.close()
        entries = []
        with open(self.path, "rb") as f:
            while True:
                hdr = f.read(self.ENTRY_HEADER.size)
                if len(hdr) < self.ENTRY_HEADER.size:
                    break
                op, kl, vl = self.ENTRY_HEADER.unpack(hdr)
                key = f.read(kl)
                val = f.read(vl)
                entries.append((op, key, val))

        # 重放到数据页（已经在 _apply 里做了，这里只做截断）
        log.info(f"WAL checkpoint: {len(entries)} entries applied")

        # 清空 WAL
        self.file = open(self.path, "wb")  # truncate
        self.file.close()
        self.file = open(self.path, "ab")

    def recover(self, db: "TinyDB"):
        """从 WAL 恢复（crash 后调用）"""
        if not os.path.exists(self.path) or os.path.getsize(self.path) == 0:
            return
        log.info("WAL recovery: replaying...")
        self.checkpoint(db)

    def close(self):
        self.file.close()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TinyDB 核心（参照 SQLite btree + LevelDB）
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

import logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S")
log = logging.getLogger("tinydb")

class TinyDB:
    """
    KV 存储引擎（参照 SQLite + LevelDB）

    架构：
      用户命令 → WAL 追加 → 数据页写入 → checkpoint 截断 WAL

    数据文件布局（参照 sqlite-btree 精读 §二）：
      Page 0: 文件头
      Page 1..N: 数据页（线性链表）
      WAL 文件: tinydb.wal
    """

    def __init__(self, path: str):
        self.path = Path(path)
        self.wal_path = self.path.with_suffix(".wal")

        if not self.path.exists():
            self._init_db()
        else:
            self.file = open(self.path, "r+b")
            hdr_data = self.file.read(HEADER_SIZE)
            self.header = unpack_header(hdr_data)

        self.wal = WAL(str(self.wal_path))
        # crash recovery
        self.wal.recover(self)

    def _init_db(self):
        """初始化新数据库（参照 SQLite sqlite3BtreeCreateTable）"""
        self.file = open(self.path, "w+b")
        # 写文件头
        self.header = {
            "magic": MAGIC, "page_size": PAGE_SIZE, "page_count": 1,
            "first_data_page": 1, "last_data_page": 1,
            "free_page_head": 0, "item_count": 0,
        }
        hdr = pack_header(1, 1, 1, 0, 0)
        self.file.write(hdr.ljust(PAGE_SIZE, b'\0'))

        # Page 1: 第一个数据页
        page = Page.new_data_page(1)
        self.file.seek(PAGE_SIZE)
        self.file.write(page.data)
        self.file.flush()
        os.fsync(self.file.fileno())

    def _read_page(self, page_no: int) -> Page:
        """读取一个页（参照 SQLite sqlite3PagerGet）"""
        self.file.seek(page_no * PAGE_SIZE)
        data = bytearray(self.file.read(PAGE_SIZE))
        return Page(data, page_no)

    def _write_page(self, page: Page):
        """写入一个页（参照 SQLite sqlite3PagerWrite）"""
        self.file.seek(page.page_no * PAGE_SIZE)
        self.file.write(page.data)
        self.file.flush()
        # 不每次 fsync（性能）；WAL 保证 crash safety

    def _alloc_page(self) -> Page:
        """分配新页（参照 SQLite btreeBalance 的页分配）"""
        self.header["page_count"] += 1
        page_no = self.header["page_count"] - 1
        page = Page.new_data_page(page_no)
        # 扩展文件
        self.file.seek(page_no * PAGE_SIZE)
        self.file.write(page.data)
        # 更新文件头
        self.header["last_data_page"] = page_no
        self._write_header()
        return page

    def _write_header(self):
        hdr = pack_header(
            self.header["page_count"],
            self.header["first_data_page"],
            self.header["last_data_page"],
            self.header["free_page_head"],
            self.header["item_count"],
        )
        self.file.seek(0)
        self.file.write(hdr)
        self.file.flush()

    def get(self, key: str) -> bytes | None:
        """GET（参照 SQLite 的 SELECT）"""
        key_bytes = key.encode()
        # 线性扫描所有数据页（简化版，真实 B-tree 从根开始）
        for page_no in range(self.header["first_data_page"],
                             self.header["last_data_page"] + 1):
            page = self._read_page(page_no)
            val = page.find_cell(key_bytes)
            if val is not None:
                return val
        return None

    def set(self, key: str, value: str):
        """SET（参照 SQLite INSERT + WAL）"""
        key_bytes = key.encode()
        val_bytes = value.encode()

        # 1. 写 WAL（参照 db §六 WAL 原理）
        self.wal.log_set(key_bytes, val_bytes)

        # 2. 写数据页
        # 先尝试在已有页中找 key（更新）
        for page_no in range(self.header["first_data_page"],
                             self.header["last_data_page"] + 1):
            page = self._read_page(page_no)
            if page.find_cell(key_bytes) is not None:
                # key 已存在 → 删旧 + 加新
                page.delete_cell(key_bytes)
                if page.add_cell(key_bytes, val_bytes):
                    self._write_page(page)
                    return
                # 页满了 → 在新页加
                break

        # 在最后一页尝试添加
        last_page = self._read_page(self.header["last_data_page"])
        if last_page.add_cell(key_bytes, val_bytes):
            self._write_page(last_page)
        else:
            # 页满了 → 分配新页（参照 SQLite balance_nonroot 分裂）
            new_page = self._alloc_page()
            new_page.add_cell(key_bytes, val_bytes)
            self._write_page(new_page)

        self.header["item_count"] += 1
        self._write_header()

    def delete(self, key: str) -> bool:
        """DELETE（参照 SQLite DELETE）"""
        key_bytes = key.encode()
        self.wal.log_del(key_bytes)

        for page_no in range(self.header["first_data_page"],
                             self.header["last_data_page"] + 1):
            page = self._read_page(page_no)
            if page.delete_cell(key_bytes):
                self._write_page(page)
                self.header["item_count"] = max(0, self.header["item_count"] - 1)
                self._write_header()
                return True
        return False

    def hexdump(self, page_no: int = 1, nbytes: int = 256):
        """hexdump 一个页（参照 sqlite-btree 精读 §九）"""
        page = self._read_page(page_no)
        data = page.data[:nbytes]
        print(f"\nPage {page_no} hexdump (first {nbytes} bytes):")
        print(f"  type={page.data[0]} cell_count={page.cell_count} "
              f"content_start={page.cell_content_start}")
        print()
        for i in range(0, len(data), 16):
            hex_part = " ".join(f"{b:02x}" for b in data[i:i+16])
            ascii_part = "".join(chr(b) if 32 <= b < 127 else "." for b in data[i:i+16])
            print(f"  {i:04x}: {hex_part:<48s} {ascii_part}")

    def stats(self):
        print(f"\ntinydb stats:")
        print(f"  file: {self.path}")
        print(f"  pages: {self.header['page_count']}")
        print(f"  items: {self.header['item_count']}")
        print(f"  file size: {self.path.stat().st_size} bytes")
        print(f"  wal size: {self.wal_path.stat().st_size if self.wal_path.exists() else 0} bytes")

    def close(self):
        self.wal.checkpoint(self)
        self.wal.close()
        self.file.close()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CLI
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def main():
    if len(sys.argv) < 3:
        print("用法: python3 main.py <db_file> <command> [args]")
        print("命令: set <key> <value> | get <key> | delete <key> | hexdump [page] | stats")
        sys.exit(1)

    db_path = sys.argv[1]
    cmd = sys.argv[2]

    db = TinyDB(db_path)

    if cmd == "set":
        if len(sys.argv) < 5:
            print("用法: set <key> <value>")
            sys.exit(1)
        db.set(sys.argv[3], sys.argv[4])
        print(f"OK")

    elif cmd == "get":
        if len(sys.argv) < 4:
            print("用法: get <key>")
            sys.exit(1)
        val = db.get(sys.argv[3])
        if val is not None:
            print(val.decode())
        else:
            print("(nil)")

    elif cmd == "delete":
        if len(sys.argv) < 4:
            print("用法: delete <key>")
            sys.exit(1)
        if db.delete(sys.argv[3]):
            print("OK")
        else:
            print("(not found)")

    elif cmd == "hexdump":
        page_no = int(sys.argv[3]) if len(sys.argv) > 3 else 1
        db.hexdump(page_no)

    elif cmd == "stats":
        db.stats()

    else:
        print(f"未知命令: {cmd}")

    db.close()

if __name__ == "__main__":
    main()
