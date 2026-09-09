#!/usr/bin/env python3
"""Extract full text from EPUB and MOBI files.

EPUBs are ZIP files containing XHTML. MOBI requires custom binary parsing.
Output: JSON files with {filename, total_chars, pages, full_text} format.
"""

import zipfile
import os
import re
import json
import hashlib
import struct
from pathlib import Path
from bs4 import BeautifulSoup

SOURCE_DIR = "/mnt/c/Users/mirac/Documents/个人/写书/政治"
OUTPUT_DIR = "/mnt/c/workspace/essence/data/political-books-extracted"
OUTPUT_DIR = Path(OUTPUT_DIR)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ─── EPUB extraction ───────────────────────────────────────────────────────────

def get_spine_order(zf: zipfile.ZipFile):
    """Parse OPF to get correct reading order (spine) of HTML files."""
    opf_files = [n for n in zf.namelist() if n.endswith('.opf')]
    if not opf_files:
        return None

    ordered_files = []
    for opf_path in opf_files:
        try:
            opf_content = zf.read(opf_path).decode('utf-8', errors='ignore')
            soup = BeautifulSoup(opf_content, 'xml')

            # Build id->href map from manifest
            id_to_href = {}
            for item in soup.find_all('item'):
                item_id = item.get('id', '')
                href = item.get('href', '')
                media_type = item.get('media-type', '')
                if href and ('html' in media_type or 'xml' in media_type or
                             href.endswith(('.html', '.xhtml', '.htm'))):
                    id_to_href[item_id] = href

            # Get spine order
            spine = soup.find('spine')
            if spine:
                opf_dir = os.path.dirname(opf_path)
                for itemref in spine.find_all('itemref'):
                    idref = itemref.get('idref', '')
                    if idref in id_to_href:
                        href = id_to_href[idref]
                        # Resolve relative to OPF location
                        full_path = os.path.normpath(os.path.join(opf_dir, href)) if opf_dir else href
                        ordered_files.append(full_path)
        except Exception as e:
            print(f"  Warning parsing OPF {opf_path}: {e}")

    return ordered_files if ordered_files else None


def extract_metadata(zf: zipfile.ZipFile):
    """Extract title and author from OPF metadata."""
    title = author = ''
    opf_files = [n for n in zf.namelist() if n.endswith('.opf')]
    for opf_path in opf_files:
        try:
            opf_content = zf.read(opf_path).decode('utf-8', errors='ignore')
            soup = BeautifulSoup(opf_content, 'xml')
            dc_title = soup.find('dc:title')
            dc_creator = soup.find('dc:creator')
            if dc_title and not title:
                title = dc_title.get_text(strip=True)
            if dc_creator and not author:
                author = dc_creator.get_text(strip=True)
            if title and author:
                break
        except Exception:
            pass
    return title, author


def clean_html_to_text(html_content: str) -> str:
    """Convert HTML to clean text, preserving paragraph breaks."""
    soup = BeautifulSoup(html_content, 'lxml')

    # Remove script and style
    for tag in soup.find_all(['script', 'style']):
        tag.decompose()

    # Insert newlines for block elements
    for tag in soup.find_all(['p', 'div', 'br', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
                               'li', 'tr', 'blockquote', 'section', 'article']):
        tag.append('\n')

    text = soup.get_text(separator='')
    # Clean up whitespace
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = text.strip()
    return text


def extract_epub(path: str) -> dict:
    """Extract full text from an EPUB file."""
    filename = os.path.basename(path)
    print(f"\n{'='*60}")
    print(f"Extracting EPUB: {filename}")
    print(f"{'='*60}")

    with zipfile.ZipFile(path) as z:
        # Metadata
        title, author = extract_metadata(z)
        print(f"  Title: {title}")
        print(f"  Author: {author}")

        # Get reading order
        ordered = get_spine_order(z)
        all_html_files = sorted([f for f in z.namelist()
                                 if f.endswith(('.html', '.xhtml', '.htm'))])

        if ordered:
            # Filter to files that actually exist in the zip
            namelist = set(z.namelist())
            ordered = [f for f in ordered if f in namelist]
            # Add any HTML files not in spine (append at end)
            ordered_set = set(ordered)
            for f in all_html_files:
                if f not in ordered_set:
                    ordered.append(f)
            file_list = ordered
            print(f"  Using spine order: {len(file_list)} files")
        else:
            file_list = all_html_files
            print(f"  No spine found, using sorted order: {len(file_list)} files")

        full_text_parts = []
        for hf in file_list:
            try:
                raw = z.read(hf).decode('utf-8', errors='ignore')
                text = clean_html_to_text(raw)
                if len(text) > 30:  # skip near-empty files
                    full_text_parts.append({
                        'file': hf,
                        'text': text
                    })
            except Exception as e:
                print(f"  Warning reading {hf}: {e}")

        total_chars = sum(len(p['text']) for p in full_text_parts)

        # MD5 of source file
        with open(path, 'rb') as f:
            md5 = hashlib.md5(f.read()).hexdigest()

        result = {
            'filename': filename,
            'title': title,
            'author': author,
            'format': 'epub',
            'md5': md5,
            'total_chars': total_chars,
            'pages': len(full_text_parts),
            'full_text': full_text_parts,
        }

        outpath = OUTPUT_DIR / f"epub_{md5}.json"
        with open(outpath, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        print(f"  Total chars: {total_chars:,}")
        print(f"  Pages (HTML files): {len(full_text_parts)}")
        print(f"  Saved to: {outpath}")

        return result


# ─── MOBI extraction ───────────────────────────────────────────────────────────

def extract_mobi(path: str) -> dict:
    """Extract text from MOBI file using the mobi library for proper decompression."""
    filename = os.path.basename(path)
    print(f"\n{'='*60}")
    print(f"Extracting MOBI: {filename}")
    print(f"{'='*60}")

    import mobi
    import tempfile
    import shutil

    # Use mobi library to properly decompress
    tempdir, filepath = mobi.extract(path)
    print(f"  Extracted to temp dir via mobi library")

    try:
        # The main content is in book.html
        html_path = os.path.join(tempdir, 'mobi7', 'book.html')
        if not os.path.exists(html_path):
            # Try to find the HTML file
            for root, dirs, files in os.walk(tempdir):
                for f in files:
                    if f.endswith('.html') or f.endswith('.htm'):
                        html_path = os.path.join(root, f)
                        break

        with open(html_path, 'rb') as f:
            html_content = f.read().decode('utf-8', errors='ignore')

        print(f"  HTML size: {len(html_content):,} chars")

        # Clean HTML to text
        text = clean_html_to_text(html_content)
        print(f"  Cleaned text: {len(text):,} chars")

        # Split into pages (chunks of ~5000 chars)
        pages = []
        chunk_size = 5000
        for i in range(0, len(text), chunk_size):
            chunk = text[i:i + chunk_size]
            if len(chunk.strip()) > 30:
                pages.append({
                    'file': f'chunk_{i//chunk_size:04d}',
                    'text': chunk.strip()
                })

        total_chars = sum(len(p['text']) for p in pages)

        # MD5 of source file
        with open(path, 'rb') as f:
            md5 = hashlib.md5(f.read()).hexdigest()

        result = {
            'filename': filename,
            'title': '人类简史',
            'author': '尤瓦尔·赫拉利',
            'format': 'mobi',
            'md5': md5,
            'total_chars': total_chars,
            'pages': len(pages),
            'full_text': pages,
        }

        outpath = OUTPUT_DIR / f"mobi_{md5}.json"
        with open(outpath, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        print(f"  Total chars: {total_chars:,}")
        print(f"  Pages: {len(pages)}")
        print(f"  Saved to: {outpath}")

        return result

    finally:
        # Clean up temp directory
        shutil.rmtree(tempdir, ignore_errors=True)


def palmdoc_decompress(data: bytes) -> bytes:
    """Decompress PalmDOC LZ77 compressed data.

    Format:
      c=0:       literal 0x00
      c=1..8:    copy next c bytes literally
      c=9..127:  literal byte
      c=128..191: back-reference (c, c2 form 16-bit value)
                   distance = (V >> 3), length = (V & 7) + 3
                   copy from: pos = len(output) - distance
      c=192..255: space + (c ^ 0x80)
    """
    result = bytearray()
    i = 0
    n = len(data)
    while i < n:
        c = data[i]
        i += 1

        if c == 0:
            # Literal null byte
            result.append(0)
        elif c <= 8:
            # Copy next c bytes literally
            for _ in range(c):
                if i < n:
                    result.append(data[i])
                    i += 1
        elif c <= 0x7F:
            # Literal byte (0x09-0x7F)
            result.append(c)
        elif c <= 0xBF:
            # Back-reference
            if i < n:
                c2 = data[i]
                i += 1
            else:
                c2 = 0
            # 16-bit value V = (c << 8) | c2
            V = (c << 8) | c2
            window_dist = V >> 3       # distance back from current position
            length = (V & 0x07) + 3    # bytes to copy

            # Copy from earlier in output
            src = len(result) - window_dist
            if src < 0:
                src = 0
            for j in range(length):
                if src + j < len(result):
                    result.append(result[src + j])
                else:
                    result.append(0x20)  # space padding
        else:
            # c >= 0xC0: space + (c XOR 0x80)
            result.append(0x20)  # space
            result.append(c ^ 0x80)

    return bytes(result)


# ─── Main ──────────────────────────────────────────────────────────────────────

EPUB_FILES = [
    '万历十五年.epub',
    '中国社会学经典文库（金翼 美好社会与美美与共 社会变革与婚姻家庭变动 陆学艺文萃 乡村治理的社会基础 组织社会学与决策分析 中国的单位组织... (Z-Library).epub',
    '人地之间：中国增长模式下的城乡土地改革 (陶然) (Z-Library).epub',
    '毛泽东文集（全集，共八卷） (中共中央文献研究室) (Z-Library).epub',
    '鄧小平文選 (鄧小平) (Z-Library).epub',
    '置身事内.epub',
]

MOBI_FILES = [
    '人类简史_尤瓦尔·赫拉利.mobi',
]


def main():
    results = []

    for epub_name in EPUB_FILES:
        path = os.path.join(SOURCE_DIR, epub_name)
        if not os.path.exists(path):
            print(f"NOT FOUND: {epub_name}")
            continue
        try:
            result = extract_epub(path)
            results.append(result)
        except Exception as e:
            print(f"ERROR extracting {epub_name}: {e}")
            import traceback
            traceback.print_exc()

    for mobi_name in MOBI_FILES:
        path = os.path.join(SOURCE_DIR, mobi_name)
        if not os.path.exists(path):
            print(f"NOT FOUND: {mobi_name}")
            continue
        try:
            result = extract_mobi(path)
            results.append(result)
        except Exception as e:
            print(f"ERROR extracting {mobi_name}: {e}")
            import traceback
            traceback.print_exc()

    # Summary
    print(f"\n{'='*60}")
    print("EXTRACTION SUMMARY")
    print(f"{'='*60}")
    print(f"{'File':<45} {'Chars':>12} {'Pages':>8}")
    print('-' * 67)
    for r in results:
        print(f"{r['filename'][:44]:<45} {r['total_chars']:>12,} {r['pages']:>8}")
    total = sum(r['total_chars'] for r in results)
    print('-' * 67)
    print(f"{'TOTAL':<45} {total:>12,}")

    # Save summary
    summary_path = OUTPUT_DIR / '_extraction_summary.json'
    with open(summary_path, 'w', encoding='utf-8') as f:
        json.dump({
            'results': [{k: v for k, v in r.items() if k != 'full_text'} for r in results],
            'total_chars': total,
        }, f, ensure_ascii=False, indent=2)
    print(f"\nSummary saved to: {summary_path}")


if __name__ == '__main__':
    main()
