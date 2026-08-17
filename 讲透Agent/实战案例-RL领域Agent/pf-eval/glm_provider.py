"""promptfoo 自定义 provider：智谱 GLM（OpenAI 兼容端点）
promptfoo python provider 约定：每个导出函数签名 call_api(prompt, options, context)
→ 每臂一个具名函数（config 用 python:file.py:funcname 引用）
"""
import json, os, urllib.request

KEY = json.load(open(os.path.expanduser("~/.local/share/opencode/auth.json")))["zhipuai-coding-plan"]["key"]
API = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
RCF = "你是严谨的算法工程师，精准第一。 先一步步推理，再给出最终答案。 严格遵循输出要求：不多不少，只输出要求的内容。"

def _glm(model, sys_p):
    async def call_api(prompt, options, context):
        user_q = context["vars"]["question"]
        msgs = ([{"role": "system", "content": sys_p}] if sys_p else []) + [{"role": "user", "content": user_q}]
        body = json.dumps({"model": model, "messages": msgs, "max_tokens": 1024, "temperature": 0.3}).encode()
        req = urllib.request.Request(API, data=body, headers={
            "Content-Type": "application/json", "Authorization": f"Bearer {KEY}"})
        for attempt in range(2):
            try:
                with urllib.request.urlopen(req, timeout=120) as r:
                    out = json.load(r)
                usage = out.get("usage", {})
                return {"output": out["choices"][0]["message"]["content"],
                        "tokenUsage": {"total": usage.get("total_tokens", 0),
                                       "completion": usage.get("completion_tokens", 0)}}
            except Exception as e:
                if attempt: return {"error": f"{type(e).__name__}: {e}"}
    return call_api

rcf_glm5  = _glm("glm-5", RCF)
base_glm5 = _glm("glm-5", None)
rcf_glm47 = _glm("glm-4.7", RCF)
