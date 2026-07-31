#!/usr/bin/env python3
"""probe4: dump 两站消息列表的所有项，区分用户/AI，定位 AI 回复的 markdown 容器。不发消息。"""
import json
from playwright.sync_api import sync_playwright

DS_LIST_JS = r"""
()=>{
 const list=document.querySelector('[class*="ds-virtual-list-visible-items"]')||document.querySelector('[class*="ds-virtual-list-items"]');
 if(!list) return {err:'no list'};
 const items=[...list.children];
 return {n:items.length, items:items.map((c,i)=>{
   const md=c.querySelector('[class*="markdown"]');
   return {idx:i, cls:(c.className&&c.className.toString)?c.className.toString().slice(0,42):'',
     head:(c.innerText||'').trim().replace(/\n/g,' ').slice(0,32),
     mdCls: md?md.className.toString().slice(0,50):null};
 })};
}
"""

DB_LIST_JS = r"""
()=>{
 const list=document.querySelector('.list_items')||document.querySelector('[class*="list_items"]');
 if(!list) return {err:'no list'};
 const items=[...list.children];
 return {n:items.length, items:items.map((c,i)=>{
   const md=c.querySelector('[class*="markdown"],[class*="flow-markdown"],[class*="rich-text"],[class*="render"]');
   return {idx:i, cls:(c.className&&c.className.toString)?c.className.toString().slice(0,42):'',
     head:(c.innerText||'').trim().replace(/\n/g,' ').slice(0,32),
     mdCls: md?md.className.toString().slice(0,50):null,
     role: c.getAttribute('data-type')||c.getAttribute('role')};
 })};
}
"""

with sync_playwright() as p:
    br = p.chromium.connect_over_cdp("http://localhost:9222")
    for pg in br.contexts[0].pages:
        if "deepseek" in pg.url:
            print("=" * 64); print("DEEPSEEK:", pg.url)
            print(json.dumps(pg.evaluate(DS_LIST_JS), ensure_ascii=False, indent=1))
        elif "doubao" in pg.url:
            print("=" * 64); print("DOUBAO:", pg.url)
            print(json.dumps(pg.evaluate(DB_LIST_JS), ensure_ascii=False, indent=1))
