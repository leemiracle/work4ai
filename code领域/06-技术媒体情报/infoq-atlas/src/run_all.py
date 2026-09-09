"""一键完整流水线（全量版）。阶段可单独跳过。

A. InfoQ 深度:  crawl → normalize → enrich → analyze → kg → content_intel
B. 多经典站:    harvest_sites → harvest_deep → site_intel
C. 知识抽取:    kb_prep → (大模型批次) → kb_auto → kb_report
D. 主题演化:    cluster_evolve
E. 产出:        report_gen → dashboard → panorama
"""
from __future__ import annotations
import argparse
import time
import sys


def run(name, fn, *a, **k):
    print(f"\n{'='*64}\n>>> {name}\n{'='*64}", flush=True)
    t = time.time()
    fn(*a, **k)
    print(f"<<< {name} ({time.time()-t:.0f}s)", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-crawl", action="store_true", help="不爬，基于已有数据")
    ap.add_argument("--only", default="", help="只跑某阶段: infoq/sites/kb/themes/output")
    args = ap.parse_args()
    only = args.only

    def want(stage):
        return only == "" or only == stage

    if want("infoq"):
        from . import normalize, enrich, analyze, kg, content_intel
        if not args.no_crawl:
            from . import crawl_topics, crawl_catalog, crawl_content
            run("InfoQ topic树", crawl_topics.main)
            run("InfoQ 目录", crawl_catalog.main)
            run("InfoQ 全文", crawl_content.main)
        run("规范化入库", normalize.build)
        run("作者富化", enrich.main)
        run("多维统计", analyze.main)
        run("知识图谱", kg.build)
        run("内容情报", content_intel.main)

    if want("sites"):
        from . import harvest_sites, harvest_deep, site_intel
        run("多经典站采集", harvest_sites.harvest_all)
        run("经典站深爬", harvest_deep.main)
        run("跨站情报", site_intel.main)

    if want("kb"):
        import subprocess
        from . import kb_prep, kb_report, kb_catalog_nlp
        run("知识抽取-选样打包", kb_prep.main, 3, 1600)
        # GLM-5.1 全文/站点抽取（需 Z_AI_API_KEY）
        subprocess.run([sys.executable, "-m", "src.kb_llm", "0", "10"], check=False)
        subprocess.run([sys.executable, "-m", "src.kb_llm_sites", "8"], check=False)
        run("知识抽取-目录NLP全量", kb_catalog_nlp.main)
        run("知识库报告+入库", kb_report.main)

    if want("themes"):
        from . import cluster_evolve
        run("主题聚类与演化", cluster_evolve.main)

    if want("output"):
        from . import report_gen, dashboard, panorama, neo4j_export
        run("报告生成", report_gen.main)
        run("仪表盘", dashboard.build)
        run("全景主报告", panorama.build)
        run("Neo4j图谱导出", neo4j_export.main)
    print("\n✅ 流水线完成")


if __name__ == "__main__":
    main()
