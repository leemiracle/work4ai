#!/usr/bin/env python3
"""probe5: dump 豆包每个非空消息项的内部 class 树（深度3），区分用户/AI 消息。"""
import json
from playwright.sync_api import sync_playwright

TREE_JS = r"""
()=>{
 const list=document.querySelector('.list_items')||document.querySelector('[class*=list_items]');
 if(!list) return {err:'no list'};
 const rows=[...list.children].filter(r=>(r.innerText||'').trim().length>0);
 const walk=(el,depth)=>{
   if(depth>3||!el)return null;
   const cls=(el.className&&el.className.toString)?el.className.toString().split(/\s+/).slice(0,2).join('.'):'';
   const attrs=[...el.attributes].filter(a=>/data-|role|aria/i.test(a.name)).map(a=>a.name+'='+a.value).slice(0,2);
   const kids=[...el.children].slice(0,3).map(c=>walk(c,depth+1)).filter(x=>x);
   return {t:el.tagName.toLowerCase(),c:cls,a:attrs.length?attrs:undefined,k:kids.length?kids:undefined};
 };
 return rows.map((r,i)=>({i,head:(r.innerText||'').trim().slice(0,18),tree:walk(r,0)}));
}
"""

with sync_playwright() as p:
    br = p.chromium.connect_over_cdp("http://localhost:9222")
    for pg in br.contexts[0].pages:
        if "doubao" in pg.url:
            print("DOUBAO:", pg.url)
            print(json.dumps(pg.evaluate(TREE_JS), ensure_ascii=False, indent=1))
