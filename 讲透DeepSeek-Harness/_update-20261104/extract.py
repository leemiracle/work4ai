#!/usr/bin/env python3
"""Structural extraction for understand pipeline batches 21-30 (deepseek-harness increment).
Read-only on the source repo. Outputs extracted.json (machine) + digest.md (condensed view)."""
import json, os, re, sys

ROOT = '/usr-data/data2/repos/deepseek-ai/deepseek-harness'
BASE = '/data/usershare/ai/work4ai/讲透DeepSeek-Harness/_update-20261104'
PKG_MAP = json.load(open(os.path.join(BASE, 'packages-map.json')))

def strip_comments_keep_lines(src: str, blank_strings: bool = False) -> str:
    """Replace comments with spaces (newlines preserved) so line numbers stay valid.
    blank_strings=True additionally blanks string/template literal contents so brace
    matching and symbol scanning ignore braces inside string interpolations."""
    out = []
    i, n = 0, len(src)
    while i < n:
        c = src[i]
        if c == '/' and i + 1 < n and src[i+1] == '/':
            j = i
            while j < n and src[j] != '\n':
                j += 1
            out.append(' ' * (j - i)); i = j
        elif c == '/' and i + 1 < n and src[i+1] == '*':
            j = src.find('*/', i + 2)
            j = n if j == -1 else j + 2
            seg = src[i:j]
            out.append(re.sub(r'[^\n]', ' ', seg)); i = j
        elif c in ('"', "'", '`'):
            j = i + 1
            while j < n:
                if src[j] == '\\': j += 2; continue
                if src[j] == c: break
                if c != '`' and src[j] == '\n': break  # unterminated normal string
                j += 1
            j = min(j + 1, n)
            seg = src[i:j]
            if blank_strings:
                out.append(re.sub(r'[^\n]', ' ', seg))
            else:
                out.append(seg)
            i = j
        else:
            out.append(c); i = 1 + i
    return ''.join(out)

IMPORT_RE = re.compile(
    r'(?:^|(?<=[;\s]))import\s+(?:type\s+)?[\w$*\s{},]+from\s+[\'"]([^\'"]+)[\'"]|'
    r'(?:^|(?<=[;\s]))import\s+[\'"]([^\'"]+)[\'"]|'
    r'(?:^|(?<=[;\s]))export\s+(?:type\s+)?[\w$*\s{},*]+\s+from\s+[\'"]([^\'"]+)[\'"]|'
    r'import\(\s*[\'"]([^\'"]+)[\'"]\s*\)', re.S | re.M)

def collect_imports(code: str):
    specs = []
    for m in IMPORT_RE.finditer(code):
        s = next(g for g in m.groups() if g)
        specs.append(s)
    # dedupe, keep order
    seen, out = set(), []
    for s in specs:
        if s not in seen:
            seen.add(s); out.append(s)
    return out

def resolve(spec: str, cur_file: str):
    """Resolve an import spec to a project-relative path or None (external)."""
    def exists(p): return os.path.exists(os.path.join(ROOT, p))
    def try_pkg_sub(dirpath, sub):
        # sub like 'src/brand' or 'lib/index'
        cands = [sub + '.ts', sub + '.tsx', sub, sub + '.json']
        if sub.endswith('.js'):  # .js -> .ts
            cands.insert(0, sub[:-3] + '.ts')
        for c in cands:
            if exists(os.path.join(dirpath, c)): return os.path.join(dirpath, c)
        return None
    if spec.startswith('@/'):  # alias if any
        return None
    if spec.startswith('.'):
        d = os.path.dirname(cur_file)
        p = os.path.normpath(os.path.join(d, spec))
        cands = []
        if spec.endswith('.js'): cands.append(p[:-3] + '.ts')
        cands += [p + '.ts', p + '.tsx', p + '.json', p, os.path.join(p, 'index.ts'), os.path.join(p, 'index.tsx')]
        for c in cands:
            if exists(c): return c
        return 'UNRESOLVED:' + spec
    m = re.match(r'^(@deepseek-ai/dsh-[a-z0-9-]+)(?:/(.*))?$', spec)
    if m:
        pkg, sub = m.group(1), m.group(2)
        if pkg not in PKG_MAP: return 'UNRESOLVED:' + spec
        d = PKG_MAP[pkg]
        if not sub:
            for c in ['src/index.ts', 'src/index.tsx', 'index.ts']:
                if exists(os.path.join(d, c)): return os.path.join(d, c)
            return 'UNRESOLVED:' + spec
        return try_pkg_sub(d, 'src/' + sub) or try_pkg_sub(d, sub) or ('UNRESOLVED:' + spec)
    return None  # external package

def brace_match(code: str, start: int):
    """start = index of '{'. Returns index of matching '}' or len-1."""
    depth = 0; i = start; n = len(code)
    while i < n:
        c = code[i]
        if c == '{': depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0: return i
        i += 1
    return n - 1

def line_of(code, idx): return code.count('\n', 0, idx) + 1

TOPLEVEL_CLOSE = re.compile(r'(?m)^\}')

def end_line_of_body(scan: str, from_idx: int, fallback: int) -> int:
    """End line = first column-0 '}' after the body starts (prettier-style top-level close).
    Falls back to brace matching when no such line exists nearby."""
    m = TOPLEVEL_CLOSE.search(scan, from_idx)
    if m is not None:
        ln = line_of(scan, m.start())
        if ln - line_of(scan, from_idx) < 400:
            return ln
    return fallback

CLASS_RE = re.compile(r'(?m)^(?:export\s+)?(?:default\s+)?(?:abstract\s+)?class\s+(\w+)(?:<[^{>]*>)?(\s+extends\s+[\w$.,\s]+?)?(\s+implements\s+[\w$.,\s]+?)?\s*\{')
FUNC_RE = re.compile(r'(?m)^(?:export\s+)?(?:default\s+)?(?:async\s+)?function\s*\*?\s*(\w+)\s*(?:<[^>]*>)?\s*\(')
CONST_FN_RE = re.compile(r'(?m)^(?:export\s+)?(?:const|let)\s+(\w+)\s*(?::\s*[^=;]+?)?=\s*(?:async\s+)?(?:function\b|\([^)]*\)\s*(?::\s*[^=;]+?)?=>|\w+\s*=>)')

CORDIS_SIGNALS = [
    (r'\bextends\s+Service\b', 'extends Service'),
    (r'\bdefine\s*\(', 'define()'),
    (r'\bctx\.effect\s*\(', 'ctx.effect'),
    (r'\bctx\.on\s*\(', 'ctx.on'),
    (r'@action\b', '@action decorator'),
]

def extract_file(rel: str):
    p = os.path.join(ROOT, rel)
    src = open(p, encoding='utf-8', errors='replace').read()
    nlines = src.count('\n')
    code = strip_comments_keep_lines(src)
    scan = strip_comments_keep_lines(src, blank_strings=True)  # structure scanning view
    imports = []
    for spec in collect_imports(code):
        r = resolve(spec, rel)
        imports.append({'spec': spec, 'resolved': r})
    classes = []
    for m in CLASS_RE.finditer(scan):
        name = m.group(1)
        ext = (m.group(2) or '').strip()
        impl = (m.group(3) or '').strip()
        start = scan.find('{', m.end() - 1)
        end = brace_match(scan, start) if start != -1 else m.end()
        endLn = end_line_of_body(scan, start + 1 if start != -1 else m.end(), line_of(scan, end)) if start != -1 else line_of(scan, end)
        classes.append({'name': name, 'startLine': line_of(scan, m.start()),
                        'endLine': endLn, 'extends': ext.replace('\n',' '), 'implements': impl.replace('\n',' ')})
    funcs = []
    for m in FUNC_RE.finditer(scan):
        # m.end() sits just after the '(' the regex consumed; start depth at 1
        j = m.end() - 1; depth = 0; started = False; n = len(scan)
        while j < n:
            c = scan[j]
            if c == '(': depth += 1
            elif c == ')': depth -= 1
            elif c == '{' and depth == 0:
                started = True; break
            elif c == ';' and depth == 0: break
            j += 1
        if started:
            endLine = end_line_of_body(scan, j + 1, line_of(scan, brace_match(scan, j)))
        else:
            endLine = line_of(scan, m.end())
        exported = bool(re.match(r'^export\b', m.group(0)))
        funcs.append({'name': m.group(1), 'startLine': line_of(scan, m.start()), 'endLine': endLine, 'exported': exported, 'kind': 'function'})
    for m in CONST_FN_RE.finditer(scan):
        name = m.group(1)
        seg_start = m.start()
        exported = bool(re.match(r'^export\b', m.group(0)))
        brace = scan.find('{', m.start())
        semi = None
        j = m.end(); n = len(scan); depth = 0
        while j < n:
            c = scan[j]
            if c in '([{': depth += 1
            elif c in ')]}': depth -= 1
            elif c == ';' and depth <= 0: semi = j; break
            elif c == '\n' and depth <= 0 and scan[j-1] not in ',({[+':
                semi = j; break
            j += 1
        endIdx = semi if semi is not None else m.end()
        if brace != -1 and brace < endIdx and re.match(r'^\s*(async\s+)?function', scan[m.end():brace+1]):
            endIdx = brace_match(scan, brace)
        funcs.append({'name': name, 'startLine': line_of(scan, seg_start), 'endLine': line_of(scan, endIdx), 'exported': exported, 'kind': 'arrow/const'})
    # dedupe funcs by name+start
    seen = set(); f2 = []
    for f in sorted(funcs, key=lambda x: x['startLine']):
        k = (f['name'], f['startLine'])
        if k in seen: continue
        seen.add(k); f2.append(f)
    signals = []
    for pat, label in CORDIS_SIGNALS:
        if re.search(pat, code): signals.append(label)
    return {'path': rel, 'lines': nlines, 'imports': imports, 'classes': classes, 'functions': f2, 'signals': signals}

def main():
    all_results = {}
    digest = []
    for bi in range(21, 31):
        b = json.load(open(os.path.join(BASE, f'batches/batch-{bi:03d}.json')))
        for rel in b['files']:
            p = os.path.join(ROOT, rel)
            if not os.path.exists(p):
                all_results[rel] = {'path': rel, 'missing': True}; continue
            if rel.endswith(('.ts', '.tsx', '.mts', '.cts')):
                all_results[rel] = extract_file(rel)
            else:
                src = open(p, encoding='utf-8', errors='replace').read()
                all_results[rel] = {'path': rel, 'lines': src.count('\n'), 'nonTs': True,
                                    'imports': [], 'classes': [], 'functions': [], 'signals': []}
    json.dump(all_results, open(os.path.join(BASE, 'extracted.json'), 'w'), indent=1, ensure_ascii=False)
    # digest
    for rel, r in all_results.items():
        digest.append(f"===== {rel} ({r.get('lines','?')} lines) =====")
        if r.get('missing'):
            digest.append('  [MISSING ON DISK]'); continue
        for imp in r['imports']:
            t = imp['resolved'] if imp['resolved'] is not None else '(external)'
            digest.append(f"  import {imp['spec']} -> {t}")
        if r['signals']:
            digest.append(f"  signals: {', '.join(r['signals'])}")
        for c in r['classes']:
            extra = ' ' + c['extends'] if c['extends'] else ''
            extra += ' ' + c['implements'] if c['implements'] else ''
            digest.append(f"  class {c['name']} [{c['startLine']}-{c['endLine']}]{extra}")
        for f in r['functions']:
            digest.append(f"  fn {f['name']} [{f['startLine']}-{f['endLine']}] ({f['kind']}{', exported' if f['exported'] else ''})")
        digest.append('')
    open(os.path.join(BASE, 'digest.md'), 'w').write('\n'.join(digest))
    # quick unresolved report
    unres = set()
    imp_total = 0
    for rel, r in all_results.items():
        for imp in r['imports']:
            imp_total += 1
            if isinstance(imp['resolved'], str) and imp['resolved'].startswith('UNRESOLVED:'):
                unres.add(f"{rel}: {imp['spec']}")
    print(f"files: {len(all_results)}, import specs: {imp_total}, unresolved: {len(unres)}")
    for u in sorted(unres): print('  UNRES', u)

if __name__ == '__main__':
    main()
