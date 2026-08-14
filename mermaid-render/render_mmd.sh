#!/usr/bin/env bash
# render_mmd.sh — 把 markdown 里的 ```mermaid 块批量渲染成 PNG 图片。
#
# 用法:
#   bash render_mmd.sh <md文件>              # 输出到 md 同级的 assets/
#   bash render_mmd.sh <md文件> <输出目录>
#   bash render_mmd.sh <目录>                # 递归处理目录下所有 .md
#   bash render_mmd.sh <目录> <输出目录>     # 全部图集中到一个目录
#
# 一次性安装 (仅首次):
#   cd <本目录> && npm install @mermaid-js/mermaid-cli
#
# 前提:
#   - Node.js >= 18, Python 3
#   - 系统装了 chromium-browser (本机: /usr/bin/chromium-browser, aarch64)
#     路径不同就改本目录的 puppeteerConfig.json
#
# 设计:
#   - 每个 mermaid 块 → 独立 PNG; 语法错的块会打印错误 + 源码, 方便定位
#   - 输出命名: <md文件名>-<两位序号>.png (如 02-architecture-03.png)
#   - 渲染参数: 白底, 宽 1800px
#   - 已知陷阱: graph 节点 label 里的裸 ( 会被误判为 [(...)] 圆柱节点语法;
#     含 ( ) : ; 等特殊字符的 label 必须加双引号, 如 A["foo(bar)"]
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MMDC="$SCRIPT_DIR/node_modules/.bin/mmdc"
CFG="$SCRIPT_DIR/puppeteerConfig.json"
EXTRACT="$SCRIPT_DIR/extract_mermaid.py"

[ -x "$MMDC" ] || { echo "✗ 未找到 mermaid-cli。请运行: cd \"$SCRIPT_DIR\" && npm install @mermaid-js/mermaid-cli"; exit 1; }
[ -f "$CFG" ]  || { echo "✗ 缺少 $CFG"; exit 1; }
[ $# -ge 1 ]   || { echo "用法: bash $0 <md文件或目录> [输出目录]"; exit 1; }

TARGET="$1"
OUT_DIR="${2:-}"

render_one() {
    local md="$1" od="$2" tmp stem f base out ok fail
    tmp="$(mktemp -d)"; stem="$(basename "$md" .md)"
    python3 "$EXTRACT" "$md" "$tmp" 2>/dev/null || { echo "✗ 提取失败: $md"; rm -rf "$tmp"; return; }
    mkdir -p "$od"; ok=0; fail=0
    for f in "$tmp"/*.mmd; do
        [ -e "$f" ] || continue
        base="$(basename "$f" .mmd)"; out="$od/${base}.png"
        if timeout 120 "$MMDC" -i "$f" -o "$out" -b white -w 1800 \
             --puppeteerConfigFile "$CFG" >/tmp/rmmd.$$.log 2>&1; then
            echo "  ✓ ${base} -> $(du -h "$out" | cut -f1)"
            ok=$((ok+1))
        else
            echo "  ✗ ${base} FAILED:"; sed -n '1,6p' /tmp/rmmd.$$.log
            echo "    --- mermaid 源码 ---"; sed 's/^/    /' "$f"
            fail=$((fail+1))
        fi
    done
    rm -rf "$tmp" /tmp/rmmd.$$.log
    echo "  [$md] 成功 $ok / 失败 $fail -> $od"
}

if [ -d "$TARGET" ]; then
    mapfile -t MDS < <(find "$TARGET" -name '*.md' | sort)
else
    MDS=("$TARGET")
fi

for md in "${MDS[@]}"; do
    [ -f "$md" ] || { echo "✗ 不是文件: $md"; continue; }
    od="${OUT_DIR:-$(dirname "$md")/assets}"
    render_one "$md" "$od"
done
