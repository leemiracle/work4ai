"""ProseMirror 文档 -> Markdown / 纯文本 转换器。

InfoQ 的 content.json 形如：
    {"type":"doc","content":[{"type":"paragraph","content":[{"type":"text","text":"..."}]}, ...]}
节点类型覆盖：paragraph/text/heading/bullet_list/ordered_list/list_item/
image/code_block/blockquote/hard_break/hard_break/hr/embed/table 等。
对未知节点做容错降级（取 text 子串）。
"""
from __future__ import annotations
from typing import Any

Node = dict[str, Any]


def _marks(node: Node) -> set[str]:
    return {m.get("type") for m in (node.get("marks") or [])}


def _inline(nodes: list[Node] | None) -> str:
    """把行内节点序列渲染成 markdown 文本。"""
    if not nodes:
        return ""
    parts: list[str] = []
    for n in nodes:
        t = n.get("type")
        if t == "text":
            txt = n.get("text", "")
            marks = _marks(n)
            if "code" in marks:
                parts.append(f"`{txt}`")
            else:
                if "bold" in marks and "italic" in marks:
                    parts.append(f"***{txt}***")
                elif "bold" in marks:
                    parts.append(f"**{txt}**")
                elif "italic" in marks:
                    parts.append(f"*{txt}*")
                else:
                    parts.append(txt)
        elif t == "hard_break":
            parts.append("\n")
        elif t in ("image",):
            src = (n.get("attrs") or {}).get("src", "")
            parts.append(f"\n![图片]({src})\n")
        elif t == "mention":
            parts.append((n.get("attrs") or {}).get("label", "") or "")
        else:
            # 未知行内节点：尝试取 text
            if n.get("text"):
                parts.append(n["text"])
            elif n.get("content"):
                parts.append(_inline(n["content"]))
    return "".join(parts)


def _block(node: Node, depth: int = 0) -> str:
    t = node.get("type")
    attrs = node.get("attrs") or {}
    inner = node.get("content")

    if t == "paragraph":
        return _inline(inner) + "\n"
    if t == "heading":
        level = attrs.get("level") or 2
        level = max(1, min(6, int(level)))
        return ("#" * level) + " " + _inline(inner) + "\n"
    if t == "bullet_list":
        return _list(inner, ordered=False, depth=depth)
    if t == "ordered_list":
        return _list(inner, ordered=True, depth=depth)
    if t == "list_item":
        return _inline(inner) + "\n"
    if t == "code_block":
        code = _inline(inner)
        lang = attrs.get("language") or ""
        return f"\n```{lang}\n{code}\n```\n"
    if t == "blockquote":
        sub = "".join(_block(c, depth) for c in (inner or []))
        return "".join("> " + ln for ln in sub.splitlines(keepends=True)) + "\n"
    if t == "image":
        src = attrs.get("src", "")
        alt = attrs.get("alt") or attrs.get("title") or "图片"
        return f"\n![{alt}]({src})\n"
    if t == "hr":
        return "\n---\n"
    if t == "hard_break":
        return "\n"
    if t == "table":
        # 简化表格：逐行提取文本
        rows = []
        for row in (inner or []):
            cells = []
            for cell in (row.get("content") or []):
                cells.append(_inline(cell.get("content")).strip())
            rows.append("| " + " | ".join(cells) + " |")
        if rows:
            header = rows[0]
            sep = "| " + " | ".join(["---"] * (header.count("|") - 1)) + " |"
            return "\n".join([header, sep] + rows[1:]) + "\n"
        return ""
    if t in ("embed", "video", "audio"):
        src = attrs.get("src") or attrs.get("url") or ""
        return f"\n[嵌入媒体 {t}]({src})\n"
    if t == "doc":
        return _render_blocks(inner, depth)
    # 未知块：递归取内容
    if inner:
        return _render_blocks(inner, depth)
    return _inline(inner) + "\n"


def _list(nodes: list[Node] | None, ordered: bool, depth: int) -> str:
    if not nodes:
        return ""
    out: list[str] = []
    indent = "  " * depth
    for i, item in enumerate(nodes, 1):
        # list_item 的 content 通常是若干 block
        body = "".join(_block(c, depth + 1) for c in (item.get("content") or []))
        marker = f"{i}." if ordered else "-"
        first, _, rest = body.partition("\n")
        out.append(f"{indent}{marker} {first}")
        if rest.strip():
            out.append(rest.rstrip())
    return "\n".join(out) + "\n"


def _render_blocks(nodes: list[Node] | None, depth: int = 0) -> str:
    if not nodes:
        return ""
    return "".join(_block(n, depth) for n in nodes)


def to_markdown(doc: Any) -> str:
    """把 ProseMirror doc（dict 或已是字符串）转成 markdown。"""
    if doc is None:
        return ""
    if isinstance(doc, str):
        return doc
    if isinstance(doc, dict) and doc.get("type") == "doc":
        md = _block(doc)
    elif isinstance(doc, dict):
        md = _block(doc)
    else:
        md = str(doc)
    # 折叠多余空行
    lines = [ln.rstrip() for ln in md.splitlines()]
    cleaned: list[str] = []
    blank = 0
    for ln in lines:
        if ln == "":
            blank += 1
            if blank <= 1:
                cleaned.append(ln)
        else:
            blank = 0
            cleaned.append(ln)
    return "\n".join(cleaned).strip() + "\n"


def to_plain(doc: Any) -> str:
    """最朴素的纯文本：去掉所有 markdown 标记，仅保留文字与换行。"""
    md = to_markdown(doc)
    import re
    md = re.sub(r"!\[[^\]]*\]\([^)]+\)", "", md)          # 图片
    md = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", md)      # 链接
    md = re.sub(r"^```.*$|^```$", "", md, flags=re.M)      # 代码围栏
    md = re.sub(r"^[#>\-\d\.\s|]+", "", md, flags=re.M)    # 标题/引用/列表/表格
    md = re.sub(r"\*+|`+", "", md)                          # 强调/代码
    md = re.sub(r"\n{3,}", "\n\n", md)
    return md.strip()
