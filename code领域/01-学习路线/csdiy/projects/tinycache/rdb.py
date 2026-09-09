#!/usr/bin/env python3
"""
tinycache/rdb.py — 参照 Redis RDB 的持久化模块

参照：Redis rdb.c (BGSAVE) + PostgreSQL COPY
csdiy 对应：os §三(fork/COW) + db §六(WAL/checkpoint)

核心：fork + 序列化 → 磁盘快照
  1. fork() 子进程（COW 机制，不阻塞主进程）
  2. 遍历所有 key-value → 序列化为二进制格式
  3. 写入 .rdb 文件
  4. crash 后可从 .rdb 恢复

和 tinydb 的 WAL 互补：
  WAL = 增量日志（crash 安全）
  RDB = 全量快照（快速恢复）
  Redis = WAL + RDB 混合
"""
import os, struct, time, pickle, threading
from pathlib import Path
from typing import Optional

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# RDB 文件格式（参照 Redis rdb.c，简化版）
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

RDB_MAGIC = b"TCDB"           # 参照 Redis "REDIS"
RDB_VERSION = 1
RDB_EOF = 0xFF                 # 参照 Redis RDB_OPCODE_EOF
RDB_SELECTDB = 0xFE           # 参照 Redis RDB_OPCODE_SELECTDB
RDB_EXPIRETIME_MS = 0xFC      # 参照 Redis RDB_OPCODE_EXPIRETIME_MS
RDB_TYPE_STRING = 0x00        # 参照 Redis RDB_TYPE_STRING

class RDBEncoder:
    """
    RDB 编码器（参照 Redis rdb.c: rdbSaveRio）

    格式：
      [MAGIC 4B][VERSION 1B]
      [SELECTDB][db_id]
      [key_count 4B]
      for each key:
        [EXPIRETIME_MS 1B][timestamp 8B]  (如果有 TTL)
        [TYPE 1B][key_len 4B][key][val_len 4B][val]
      [EOF 1B][CRC32 4B]
    """

    @staticmethod
    def encode(data: dict[str, tuple[bytes, float]]) -> bytes:
        """
        data: {key: (value, expire_at)}  expire_at=0 表示永不过期
        """
        buf = bytearray()

        # 先过滤已过期的数据（修复 key_count 不匹配 bug）
        now = time.time()
        valid = {k: v for k, v in data.items() if not (v[1] > 0 and v[1] <= now)}

        # Header
        buf.extend(RDB_MAGIC)
        buf.append(RDB_VERSION)
        buf.append(RDB_SELECTDB)
        buf.append(0)  # db 0

        # Key count（用过滤后的数量）
        buf.extend(struct.pack(">I", len(valid)))

        # Entries
        for key, (value, expire_at) in valid.items():
            key_bytes = key if isinstance(key, bytes) else key.encode()
            val_bytes = value if isinstance(value, bytes) else value.encode()

            # 过期时间（只保存未过期的）
            if expire_at > 0 and expire_at > now:
                buf.append(RDB_EXPIRETIME_MS)
                buf.extend(struct.pack(">Q", int(expire_at * 1000)))
            elif expire_at > 0:
                continue  # 已过期，跳过

            # Type + key + value
            buf.append(RDB_TYPE_STRING)
            buf.extend(struct.pack(">I", len(key_bytes)))
            buf.extend(key_bytes)
            buf.extend(struct.pack(">I", len(val_bytes)))
            buf.extend(val_bytes)

        # EOF + CRC
        buf.append(RDB_EOF)
        import binascii
        crc = binascii.crc32(buf) & 0xFFFFFFFF
        buf.extend(struct.pack(">I", crc))

        return bytes(buf)

class RDBDecoder:
    """RDB 解码器（参照 Redis rdb.c: rdbLoadRio）"""

    @staticmethod
    def decode(data: bytes) -> dict[bytes, tuple[bytes, float]]:
        """返回 {key: (value, expire_at)}"""
        if len(data) < 6 or data[:4] != RDB_MAGIC:
            raise ValueError("Invalid RDB file")

        pos = 4  # skip magic
        version = data[pos]; pos += 1

        if data[pos] != RDB_SELECTDB: raise ValueError("Expected SELECTDB")
        pos += 1
        db_id = data[pos]; pos += 1

        key_count = struct.unpack_from(">I", data, pos)[0]; pos += 4

        result = {}
        for _ in range(key_count):
            expire_at = 0

            if data[pos] == RDB_EXPIRETIME_MS:
                pos += 1
                ms = struct.unpack_from(">Q", data, pos)[0]; pos += 8
                expire_at = ms / 1000.0

            if data[pos] != RDB_TYPE_STRING:
                raise ValueError(f"Unknown type: {data[pos]}")
            pos += 1

            key_len = struct.unpack_from(">I", data, pos)[0]; pos += 4
            key = data[pos:pos+key_len]; pos += key_len

            val_len = struct.unpack_from(">I", data, pos)[0]; pos += 4
            val = data[pos:pos+val_len]; pos += val_len

            result[key] = (val, expire_at)

        return result

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# RDB 持久化管理器（参照 Redis BGSAVE）
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class RDBPersistence:
    """
    RDB 持久化（参照 Redis BGSAVE）

    Redis BGSAVE 流程：
    1. fork() → 子进程（COW，不影响主进程）
    2. 子进程遍历所有 key → 写 RDB 文件
    3. 写完 → 通知主进程
    4. 主进程继续服务

    本实现用线程（简化版）：
    1. 快照当前 data（浅拷贝 key 列表）
    2. 后台线程序列化+写文件
    3. 主进程继续服务
    """

    def __init__(self, rdb_path: str):
        self.rdb_path = Path(rdb_path)
        self.last_save_time = 0
        self.last_save_duration = 0
        self.is_saving = False

    def save(self, data: dict[str, tuple[bytes, float]]) -> float:
        """同步保存（参照 Redis SAVE，会阻塞）"""
        start = time.time()
        encoded = RDBEncoder.encode(data)
        tmp_path = self.rdb_path.with_suffix(".rdb.tmp")
        tmp_path.write_bytes(encoded)
        # 原子重命名（参照 Redis 的 rename 保证 crash 安全）
        tmp_path.rename(self.rdb_path)
        self.last_save_time = time.time()
        self.last_save_duration = self.last_save_time - start
        return self.last_save_duration

    def bgsave(self, data_provider) -> threading.Thread:
        """
        后台保存（参照 Redis BGSAVE）

        data_provider: 一个返回当前数据的 callable（避免传大 dict）
        """
        if self.is_saving:
            return None

        self.is_saving = True

        def _save():
            try:
                snapshot = data_provider()
                self.save(snapshot)
            finally:
                self.is_saving = False

        thread = threading.Thread(target=_save, daemon=True)
        thread.start()
        return thread

    def load(self) -> dict[bytes, tuple[bytes, float]]:
        """加载 RDB（参照 Redis 启动时的 rdbLoad）"""
        if not self.rdb_path.exists():
            return {}
        data = self.rdb_path.read_bytes()
        return RDBDecoder.decode(data)

    def info(self) -> dict:
        """状态信息（参照 Redis INFO persistence）"""
        file_size = self.rdb_path.stat().st_size if self.rdb_path.exists() else 0
        return {
            "rdb_file": str(self.rdb_path),
            "rdb_size": file_size,
            "last_save": self.last_save_time,
            "last_save_duration_ms": round(self.last_save_duration * 1000, 1),
            "is_saving": self.is_saving,
        }

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 测试
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def main():
    print("tinycache/rdb.py — RDB 持久化（参照 Redis BGSAVE）\n")

    rdb = RDBPersistence("/tmp/tinycache_test.rdb")

    # 准备数据
    data = {}
    for i in range(100):
        key = f"key_{i:03d}".encode()
        val = f"value_{i}_{ 'x' * 20 }".encode()
        expire = time.time() + 3600 if i % 10 == 0 else 0  # 10% 有 TTL
        data[key] = (val, expire)
    print(f"准备数据: {len(data)} 个 key")

    # SAVE（同步）
    print("\n── SAVE（同步）──")
    duration = rdb.save(data)
    info = rdb.info()
    print(f"  耗时: {info['last_save_duration_ms']}ms")
    print(f"  文件: {info['rdb_size']} bytes")
    print(f"  每条记录: {info['rdb_size']//len(data)} bytes")

    # LOAD（恢复）
    print("\n── LOAD（恢复）──")
    loaded = rdb.load()
    print(f"  恢复: {len(loaded)} 个 key")

    # 验证
    ok = 0
    for key, (val, expire) in data.items():
        if key in loaded and loaded[key][0] == val:
            ok += 1
    print(f"  校验: {ok}/{len(data)} ✅")

    # BGSAVE（后台）
    print("\n── BGSAVE（后台线程）──")
    rdb.is_saving = False  # reset
    thread = rdb.bgsave(lambda: data)
    if thread:
        thread.join(timeout=5)
        print(f"  BGSAVE 完成: {rdb.info()['last_save_duration_ms']}ms")
        print(f"  is_saving: {rdb.info()['is_saving']}")

    # Crash 恢复模拟
    print("\n── Crash 恢复模拟 ──")
    new_rdb = RDBPersistence("/tmp/tinycache_test.rdb")
    recovered = new_rdb.load()
    print(f"  新实例恢复: {len(recovered)} 个 key")
    print(f"  数据一致: {'✅' if len(recovered) == len(data) else '❌'}")

    # 过期数据验证
    print("\n── 过期数据验证 ──")
    expired_data = {
        b"active": (b"data1", time.time() + 3600),    # 未过期
        b"expired": (b"data2", time.time() - 100),      # 已过期
        b"permanent": (b"data3", 0),                     # 永久
    }
    rdb.save(expired_data)
    loaded = rdb.load()
    print(f"  写入 3 个 key（1 活跃 + 1 过期 + 1 永久）")
    print(f"  恢复 {len(loaded)} 个 key（过期的不保存）")
    has_active = b"active" in loaded
    has_expired = b"expired" in loaded
    has_perm = b"permanent" in loaded
    print(f"  active: {'✅' if has_active else '❌'}")
    print(f"  expired (应该不存在): {'✅ 跳过' if not has_expired else '❌ 存在'}")
    print(f"  permanent: {'✅' if has_perm else '❌'}")

    print(f"\n{'='*50}")
    print(f"  RDB 持久化验证完成")
    print(f"{'='*50}")

if __name__ == "__main__":
    main()
