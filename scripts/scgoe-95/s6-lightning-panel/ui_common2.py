import time, json
from ui_common import *
VIS = """() => { let ok=false; const f=(r)=>{ r.querySelectorAll('*').forEach(e=>{ if(e.tagName==='TEXTAREA' && e.classList.contains('chat-box')){ const b=e.getBoundingClientRect(); if(b.width>0) ok=true;} if(e.shadowRoot) f(e.shadowRoot); }); }; f(document); return ok; }"""
CLICK = """(lbl) => { const walk=(r)=>{ for(const e of r.querySelectorAll('button,a,[role=button],[role=option],[role=menuitem],li')){ const l=(e.getAttribute('aria-label')||e.getAttribute('title')||e.innerText||'').trim(); if(l===lbl){ e.click(); return true;} } for(const e of r.querySelectorAll('*')){ if(e.shadowRoot && walk(e.shadowRoot)) return true;} return false; }; return walk(document); }"""
PANEL = """() => { const out=[]; const walk=(r)=>{ r.querySelectorAll('*').forEach(e=>{ if(e.shadowRoot) walk(e.shadowRoot); }); }; const find=(r,acc)=>{ r.querySelectorAll('*').forEach(e=>{ const t=e.tagName.toLowerCase(); if(/copilot|einstein|agentforce|panel/.test(t)) acc.push(e); if(e.shadowRoot) find(e.shadowRoot,acc); }); return acc; }; const els=find(document,[]); const tags=[...new Set(els.map(e=>e.tagName.toLowerCase()))]; let txt=''; for(const e of els){ const s=(e.shadowRoot? e.shadowRoot.textContent: e.innerText)||''; if(s.length>txt.length) txt=s; } return {tags:tags.slice(0,40), txt:txt.replace(/\\s+/g,' ').slice(0,3000)}; }"""
def open_panel(pg):
    pg.goto(front('/lightning/page/home'), wait_until='domcontentloaded', timeout=120000)
    for k in range(12):
        time.sleep(5)
        if pg.evaluate(VIS): print('visible'); return
    for attempt in range(3):
        try:
            pg.locator('button[title="Agentforce"]:visible, button[aria-label="Agentforce"]:visible').first.click(timeout=20000)
        except Exception as e: print('click err', str(e)[:80])
        for k in range(6):
            time.sleep(5); pg.evaluate(CLICK, 'Got It')
            if pg.evaluate(VIS): print('visible'); return
    raise RuntimeError('panel not visible')
BTNS = """() => { const res=[]; const find=(r,inP)=>{ r.querySelectorAll('*').forEach(e=>{ const t=e.tagName.toLowerCase(); const p=inP||/copilot/.test(t); if(p && /^(button|a|li)$/.test(t) || p && ['button','option','menuitem','combobox'].includes(e.getAttribute('role'))){ const l=(e.getAttribute('aria-label')||e.getAttribute('title')||e.innerText||'').trim().replace(/\\s+/g,' '); if(l) res.push(l.slice(0,80)); } if(e.shadowRoot) find(e.shadowRoot,p); }); }; find(document,false); return [...new Set(res)]; }"""
TAGTXT = """(re) => { const out={}; const rx=new RegExp(re); const find=(r)=>{ r.querySelectorAll('*').forEach(e=>{ const t=e.tagName.toLowerCase(); if(rx.test(t)){ const s=((e.shadowRoot? e.shadowRoot.textContent: '')+' '+(e.textContent||'')).replace(/\\s+/g,' ').trim(); if(s && !(t in out)) out[t]=s.slice(0,400);} if(e.shadowRoot) find(e.shadowRoot); }); }; find(document); return out; }"""
def gotit(pg):
    pg.evaluate(CLICK, 'Got It'); time.sleep(12)
MSGTAGS = """() => { const c={}; const find=(r)=>{ r.querySelectorAll('*').forEach(e=>{ const t=e.tagName.toLowerCase(); if(/message|response|bubble|turn|conversation/.test(t)) c[t]=(c[t]||0)+1; if(e.shadowRoot) find(e.shadowRoot); }); }; find(document); return c; }"""
def send(pg, text):
    ta = pg.locator('textarea:visible').last
    ta.click(timeout=15000); ta.fill(text); time.sleep(1)
    try: pg.locator('button[title="Send"]:visible, button[aria-label="Send"]:visible').last.click(timeout=5000)
    except Exception: ta.press('Enter')
