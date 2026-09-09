"""把 content_intel.json 压缩成精读输入：每 topic 一段紧凑文本，
含头部实体、子主题、代表性文章真实摘要。供 LLM 据此写深度综合。"""
import json
from . import config as C

def main():
    d = json.loads((C.PROCESSED / "content_intel.json").read_text("utf-8"))
    out = []
    for t in d["topic_digests"]:
        s = [f"### TOPIC {t['topic_id']} :: {t['name']}  (全文{t['n_fulltext']}篇)\n"]
        ents = []
        for cat, items in sorted(t["top_entities_by_cat"].items(),
                                 key=lambda x: -sum(c for _, c in x[1]))[:6]:
            ents.append(cat + ": " + ", ".join(f"{n}({c})" for n, c in items[:8]))
        s.append("实体: " + " | ".join(ents) + "\n")
        s.append("子主题: " + " / ".join(x["theme"] for x in t["subthemes"][:8]) + "\n")
        s.append("关键短语: " + " / ".join(k for k, _ in t["top_keyphrases"][:15]) + "\n")
        s.append("代表文章摘要:")
        for a in t["representative"][:6]:
            summ = " ".join(a.get("summary", [])) if isinstance(a.get("summary"), list) else str(a.get("summary",""))
            s.append(f"  - 《{a['title']}》(阅读{a.get('views',0)}): {summ[:280]}")
        out.append("\n".join(s))
    text = "\n\n" + "="*60 + "\n\n".join(out)
    p = C.NOTES / "synth_input.txt"
    p.write_text(text, encoding="utf-8")
    print(f"wrote {p} ({p.stat().st_size//1024}KB), {len(out)} topics")

if __name__ == "__main__":
    main()
