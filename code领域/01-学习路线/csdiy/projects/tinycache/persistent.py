#!/usr/bin/env python3
"""
tinycache with persistence — 集成 RDB 持久化的缓存服务器

把 tinycache/main.py 和 tinycache/rdb.py 连起来：
  启动时从 RDB 恢复数据
  定期 BGSAVE 保存快照
  SIGTERM 时最后保存一次

架构：
  Client → tinycache → [Dict（内存）]
                      ↓ BGSAVE（定期/退出时）
                    [RDB 文件（磁盘）]
                      ↑ Load（启动时）
"""
import asyncio, signal, time, logging, os, sys
from pathlib import Path

# 导入主模块和 RDB 模块
sys.path.insert(0, str(Path(__file__).resolve().parent))
from main import TinyCache, CacheDict, RESPParser
from rdb import RDBPersistence

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S")
log = logging.getLogger("tinycache+persistence")

PERSISTENT_CACHE = TinyCache()

class PersistentTinyCache:
    """带 RDB 持久化的 TinyCache"""

    def __init__(self, rdb_path: str = "/tmp/tinycache.rdb", save_interval: int = 60):
        self.rdb = RDBPersistence(rdb_path)
        self.save_interval = save_interval
        self._save_task = None

    def load_from_rdb(self):
        """启动时从 RDB 恢复"""
        loaded = self.rdb.load()
        if loaded:
            for key, (value, expire_at) in loaded.items():
                key_str = key.decode() if isinstance(key, bytes) else key
                val_str = value.decode() if isinstance(value, bytes) else value
                PERSISTENT_CACHE.data.set(
                    key_str.encode(), val_str.encode(),
                    expire_at=expire_at if expire_at > 0 else 0
                )
            log.info(f"📦 从 RDB 恢复 {len(loaded)} 个 key")
        else:
            log.info("📦 RDB 文件为空，从零开始")

    def _snapshot_provider(self):
        """获取当前数据快照（供 BGSAVE）"""
        result = {}
        now = time.time()
        for entry in PERSISTENT_CACHE.data.table:
            while entry:
                if entry.expire_at == 0 or now <= entry.expire_at:
                    result[entry.key] = (entry.value, entry.expire_at)
                entry = entry.next
        return result

    async def start_save_loop(self):
        """定期 BGSAVE"""
        while True:
            await asyncio.sleep(self.save_interval)
            if PERSISTENT_CACHE.data.used > 0:
                self.rdb.bgsave(self._snapshot_provider)
                info = self.rdb.info()
                log.info(f"💾 自动 BGSAVE: {info['rdb_size']}B, {info['last_save_duration_ms']}ms")

    def save_now(self):
        """同步保存（退出时用）"""
        if PERSISTENT_CACHE.data.used > 0:
            snapshot = self._snapshot_provider()
            duration = self.rdb.save(snapshot)
            log.info(f"💾 退出保存: {len(snapshot)} keys, {duration*1000:.1f}ms")

async def main_async():
    import argparse
    parser = argparse.ArgumentParser(description="tinycache with RDB persistence")
    parser.add_argument("-p", "--port", type=int, default=6395)
    parser.add_argument("--rdb", default="/tmp/tinycache.rdb", help="RDB 文件路径")
    parser.add_argument("--save-interval", type=int, default=60, help="自动保存间隔(秒)")
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # 初始化持久化
    persistent = PersistentTinyCache(rdb_path=args.rdb, save_interval=args.save_interval)
    persistent.load_from_rdb()

    # 启动服务器
    server = await asyncio.start_server(
        PERSISTENT_CACHE.handle_client, "0.0.0.0", args.port, reuse_address=True
    )
    addr = server.sockets[0].getsockname()
    log.info(f"tinycache+persistence on {addr[0]}:{addr[1]}")
    log.info(f"  RDB: {args.rdb}")
    log.info(f"  auto-save: every {args.save_interval}s")
    log.info(f"  keys: {PERSISTENT_CACHE.data.used}")

    # 启动定期保存 + 定期过期
    asyncio.create_task(persistent.start_save_loop())
    asyncio.create_task(PERSISTENT_CACHE.active_expire_loop())

    # 优雅退出
    stop_event = asyncio.Event()
    loop = asyncio.get_event_loop()
    def _shutdown():
        log.info("收到退出信号，正在保存...")
        persistent.save_now()
        stop_event.set()
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, _shutdown)
        except NotImplementedError:
            pass

    async with server:
        await stop_event.wait()

    log.info(f"tinycache 停止。最后状态: {PERSISTENT_CACHE.data.used} keys")

if __name__ == "__main__":
    asyncio.run(main_async())
