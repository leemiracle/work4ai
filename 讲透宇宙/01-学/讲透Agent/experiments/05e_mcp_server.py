"""
05e_mcp_server.py — L3 补缺配套: 最小真 MCP server (FastMCP 3.x, stdio 传输)
对应: 自进化2.0-整体叠加.md §7 L3 行 · 由 [05e_toolmaker](./05e_toolmaker.py) 进程内拉起做真协议回路验证
注: 官方 mcp SDK 新版已把 FastMCP 拆为独立包 fastmcp (本文件开发实录: 先踩 mcp.server.fastmcp
ModuleNotFoundError, pip install fastmcp 后通) — 正是"查最新 API 不凭记忆"的活例子
注册进 opencode 的三行配置 (手动步骤, 重启 opencode 生效):
  { "mcp": { "servers": { "toolmaker-demo": {
      "command": "python3", "args": ["讲透Agent/experiments/05e_mcp_server.py"] } } } }
"""
from fastmcp import FastMCP

mcp = FastMCP("toolmaker-demo")

@mcp.tool()
def multiply(a: float, b: float) -> float:
    """两数相乘 (与 05e_toolmaker 注册表同源工具, 走真 MCP 协议)"""
    return a * b

@mcp.tool()
def sqrt(x: float) -> float:
    """平方根"""
    return x ** 0.5

@mcp.tool()
def sort_list(xs: str) -> str:
    """逗号分隔数字排序, 返回逗号分隔字符串"""
    return ",".join(str(v) for v in sorted(float(v) for v in xs.split(",")))

if __name__ == "__main__":
    mcp.run()   # stdio
