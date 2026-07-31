#!/usr/bin/env python3
"""probe6: 对比豆包用户消息项 vs AI消息项的全部 class 集合，找 AI 独有特征 + markdown 渲染容器。"""
import json
from playwright.sync_api import sync_playwright

CMP_JS = r"""
()=>{
 const list=document.querySelector('.list_items')||document.querySelector('[class*=list_items]');
 const rows=[...list.children].filter(r=>(r.innerText||'').trim().length>0);
 const classes=el=>{const s=new Set();el.querySelectorAll('*').forEach(e=>{if(e.className&&e.className.toString)e.className.toString().split(/\s+/).forEach(c=>{if(c)s.add(c)})});return [...s];};
 // rows[0]=user rows[1]=ai
 const user=new Set(classes(rows[0])), ai=classes(rows[1]);
 const aiOnly=ai.filter(c=>!user.has(c));
 // 在 AI 项里找 markdown-ish 容器
 const aiEl=rows[1];
 const mdLike=[...aiEl.querySelectorAll('*')].map(e=>({cls:(e.className&&e.className.toString)?e.className.toString().slice(0,60):'',txt:(e.innerText||'').trim().slice(0,15)})).filter(x=>/markdown|prose|rich|render|content|flow|md-|text-body|bubble/i.test(x.cls)).slice(0,8);
 return {user_classes:[...user], ai_classes:ai, ai_only:aiOnly, md_like:mdLike, ai_full_text:(aiEl.innerText||'').trim()};
}
"""

with sync_playwright() as p:
    br = p.chromium.connect_over_cdp("http://localhost:9222")
    for pg in br.contexts[0].pages:
        if "doubao" in pg.url:
            print("DOUBAO:", pg.url)
            print(json.dumps(pg.evaluate(CMP_JS), ensure_ascii=False, indent=1))
