"""采集器测试脚本 - 带超时逐个测试"""
import logging
import sys
import threading
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
logging.basicConfig(level=logging.ERROR, format="%(message)s")

from src.config import Config
Config.reload()
Config.sources()["collection"]["default_delay_seconds"] = 0.3
Config.sources()["collection"]["timeout_seconds"] = 8
Config.sources()["collection"]["max_retries"] = 1

from src.collectors.factory import create_collector

SOURCES = [
    "infoq", "juejin", "v2ex", "hackernews", "devto",
    "segmentfault", "oschina", "cnblogs", "meituan_tech",
    "jiqizhixin", "qbitai", "kr36", "geekpark",
]


def test_source(name: str, results: dict, timeout: int = 25):
    try:
        c = create_collector(name)
        articles = c.collect()
        results[name] = {"ok": True, "count": len(articles),
                         "sample": articles[0].title[:40] if articles else "-"}
    except Exception as e:
        results[name] = {"ok": False, "error": f"{type(e).__name__}: {str(e)[:70]}"}


def run_with_timeout(name: str, timeout: int = 25) -> dict:
    results: dict = {}
    t = threading.Thread(target=test_source, args=(name, results), daemon=True)
    t.start()
    t.join(timeout=timeout)
    if name not in results:
        return {"ok": False, "error": "TIMEOUT"}
    return results[name]


def main():
    print(f"测试 {len(SOURCES)} 个数据源...\n")
    ok_count = 0
    for s in SOURCES:
        r = run_with_timeout(s, timeout=25)
        if r["ok"]:
            ok_count += 1
            print(f"  {s:15s} OK   {r['count']:3d}篇  {r['sample']}")
        else:
            print(f"  {s:15s} ERR  {r['error']}")
    print(f"\n结果: {ok_count}/{len(SOURCES)} 数据源可用")


if __name__ == "__main__":
    main()
