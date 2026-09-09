#!/usr/bin/env python3
"""TechInsight 入口脚本

用法:
  python run.py collect                  # 采集全部源
  python run.py collect --source infoq   # 仅采集 InfoQ
  python run.py collect --priority 2     # 采集优先级<=2的源
  python run.py analyze                  # 运行分析管道（知识图谱+趋势+架构+机会+报告）
  python run.py full                     # 完整管道（采集+分析）
  python run.py web                      # 启动 Web 仪表盘
  python run.py rag "你的问题"           # RAG 问答
  python run.py stats                    # 查看数据统计
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.config import Config


def setup_logging():
    Config.ensure_dirs()
    settings = Config.settings()
    log_cfg = settings.get("logging", {})
    level = getattr(logging, log_cfg.get("level", "INFO"))
    handlers = [logging.StreamHandler(sys.stdout)]
    log_file = Config.base_dir() / log_cfg.get("file", "data/processed/app.log")
    if log_file:
        handlers.append(logging.FileHandler(str(log_file), encoding="utf-8"))
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=handlers,
    )


def cmd_collect(args):
    from src.pipeline import run_collection
    result = run_collection(source=args.source, priority=args.priority)
    print(f"\n采集结果: {result}")


def cmd_analyze(args):
    from src.pipeline import run_analysis_pipeline
    result = run_analysis_pipeline(max_articles=args.max_articles)
    if "error" in result:
        print(result["error"])
        return
    print(f"\n分析完成!")
    print(f"  报告: {result['reports']}")
    print(f"  统计: {result['stats']}")


def cmd_full(args):
    from src.pipeline import run_full_pipeline
    result = run_full_pipeline(source=args.source, max_articles=args.max_articles)
    print(f"\n完整管道完成: {result}")


def cmd_web(args):
    import uvicorn
    from src.web.server import app
    web_cfg = Config.settings().get("web", {})
    host = web_cfg.get("host", "127.0.0.1")
    port = web_cfg.get("port", 8765)
    print(f"启动 Web 仪表盘: http://{host}:{port}")
    uvicorn.run(app, host=host, port=port)


def cmd_rag(args):
    from src.rag.qa import RAGEngine
    engine = RAGEngine()
    result = engine.answer(args.question)
    print(f"\n问: {args.question}")
    print(f"\n答: {result['answer']}")
    if result.get("sources"):
        print(f"\n参考来源 ({len(result['sources'])} 条):")
        for i, s in enumerate(result["sources"]):
            print(f"  [{i+1}] (相关度:{s['score']:.2f}) {s['text'][:100]}...")


def cmd_stats(args):
    from src.storage.database import get_stats, init_db
    init_db()
    stats = get_stats()
    print(f"\n数据统计:")
    print(f"  文章总数: {stats['total_articles']}")
    print(f"  已分析: {stats['analyzed_articles']}")
    print(f"  知识实体: {stats['entities']}")
    print(f"  实体关系: {stats['relations']}")
    print(f"\n各源采集量:")
    for source, count in stats["by_source"].items():
        print(f"  {source}: {count}")


def cmd_sources(args):
    sources = Config.sources()["sources"]
    print(f"\n配置的数据源 ({len(sources)} 个):")
    for key, cfg in sorted(sources.items(), key=lambda x: x[1].get("priority", 5)):
        feeds = cfg.get("feeds", [])
        feed_type = " / ".join(set(f.get("endpoint", "") for f in feeds))[:60]
        print(f"  [P{cfg.get('priority', '?')}] {key} ({cfg.get('name', '')})")
        print(f"        type: {cfg.get('type')}, feeds: {len(feeds)}")
        print(f"        tags: {', '.join(cfg.get('tags', [])[:5])}")


def main():
    parser = argparse.ArgumentParser(description="TechInsight 技术媒体洞察平台")
    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    p_collect = subparsers.add_parser("collect", help="采集数据")
    p_collect.add_argument("--source", type=str, help="指定数据源 (如 infoq)")
    p_collect.add_argument("--priority", type=int, help="采集优先级 <= N 的源")
    p_collect.set_defaults(func=cmd_collect)

    p_analyze = subparsers.add_parser("analyze", help="运行分析管道")
    p_analyze.add_argument("--max-articles", type=int, default=300)
    p_analyze.set_defaults(func=cmd_analyze)

    p_full = subparsers.add_parser("full", help="完整管道（采集+分析）")
    p_full.add_argument("--source", type=str, default=None)
    p_full.add_argument("--max-articles", type=int, default=300)
    p_full.set_defaults(func=cmd_full)

    p_web = subparsers.add_parser("web", help="启动 Web 仪表盘")
    p_web.set_defaults(func=cmd_web)

    p_rag = subparsers.add_parser("rag", help="RAG 问答")
    p_rag.add_argument("question", type=str, help="问题")
    p_rag.set_defaults(func=cmd_rag)

    p_stats = subparsers.add_parser("stats", help="数据统计")
    p_stats.set_defaults(func=cmd_stats)

    p_sources = subparsers.add_parser("sources", help="列出数据源")
    p_sources.set_defaults(func=cmd_sources)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return

    setup_logging()
    args.func(args)


if __name__ == "__main__":
    main()
