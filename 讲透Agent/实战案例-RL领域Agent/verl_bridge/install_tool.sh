#!/bin/bash
# install_tool.sh —— 把 rl_agent tool symlink 安装进 verl_tool（可撤销，不污染上游 git）
# 前置：verl-tool 在 ~/ai/verl-tool（或环境变量 VERL_TOOL_DIR）
set -e
VERL_TOOL_DIR=${VERL_TOOL_DIR:-~/ai/verl-tool}
SRC="$(cd "$(dirname "$0")" && pwd)/rl_agent_tool.py"
DST="$VERL_TOOL_DIR/verl_tool/servers/tools/rl_agent.py"
ln -sf "$SRC" "$DST"
echo "✅ installed: $DST -> $SRC"
python3 -c "
import sys; sys.path.insert(0, '$VERL_TOOL_DIR')
from verl_tool.servers.tools.base import get_tool_cls
cls = get_tool_cls('rl_agent')
print('✅ 注册验证: get_tool_cls(\"rl_agent\") =', cls.__name__)"
