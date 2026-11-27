import sys
from ui_common2 import *
from playwright.sync_api import sync_playwright
LAST = """() => { const blocks=[]; const f=(r)=>{ r.querySelectorAll('*').forEach(e=>{ if(e.tagName.toLowerCase()==='runtime_copilot_base-message-block') blocks.push(e); if(e.shadowRoot) f(e.shadowRoot); }); }; f(document);
  const res=blocks.map(bk=>{ const els=[]; const g=(r)=>{ r.querySelectorAll('*').forEach(e=>{ els.push(e); if(e.shadowRoot) g(e.shadowRoot); }); }; if(bk.shadowRoot) g(bk.shadowRoot); g(bk);
    const text=[...new Set(els.filter(e=>e.tagName==='P'||e.tagName==='LI'||e.tagName==='SPAN'&&e.children.length===0||e.tagName==='TD'||e.tagName==='TH').map(e=>e.textContent))].join('\\n');
    const links=els.filter(e=>e.tagName==='A').map(a=>({t:a.textContent.trim(), h:a.getAttribute('href')})).filter(x=>x.h);
    const fmt=els.filter(e=>['B','STRONG','EM','I','IMG','CODE','TABLE','U','S'].includes(e.tagName)).map(e=>e.tagName+':'+(e.tagName==='IMG'?e.getAttribute('src'):e.textContent.trim().slice(0,60)));
    const all=(bk.shadowRoot? bk.shadowRoot.textContent:'')+' '+bk.textContent;
    const it=bk.innerText||''; return {all:(it.trim()?it:text||all).trim(), links, fmt:fmt.filter(x=>!x.includes('helpful'))}; });
  return res; }"""
def wait_reply(pg, n_before, timeout=150):
    t0=time.time(); last=None; stable=0
    while time.time()-t0<timeout:
        time.sleep(5); r=pg.evaluate(LAST)
        if len(r)>n_before:
            cur=r[-1]['all']
            if cur==last and len(cur)>20: stable+=1
            else: stable=0
            last=cur
            if stable>=3: return r[-1]
    return pg.evaluate(LAST)[-1] if pg.evaluate(LAST) else None
def run(name, turns, nav=None, out=None):
    res={'conversation':name,'turns':[]}
    with sync_playwright() as p:
        b=p.chromium.launch(executable_path=EXE); ctx=b.new_context(viewport={'width':1600,'height':1000}); pg=ctx.new_page()
        open_panel(pg); gotit(pg)
        res['agent_selected']=pg.evaluate(TAGTXT,'runtime_copilot_base-base-button').get('runtime_copilot_base-base-button')
        for i,u in enumerate(turns):
            n=len(pg.evaluate(LAST)); send(pg,u); r=wait_reply(pg,n)
            res['turns'].append({'utterance':u,'reply':r}); print(name,i,json.dumps(r)[:1500]); sys.stdout.flush()
            pg.screenshot(path=f'shots/s6/{name}-{i+1}.jpg', type='jpeg', quality=45)
        if nav:
            before=pg.url
            lk=pg.locator('runtime_copilot_base-message-block a:has-text("Open record")').last
            href=lk.get_attribute('href'); lk.click(timeout=15000); time.sleep(15)
            pages=[x.url for x in ctx.pages]
            title=pg.evaluate("() => document.title")
            res['navigation']={'href':href,'before':before,'after':pg.url,'pages':pages,'title':title}
            print('NAV', json.dumps(res['navigation'])); pg.screenshot(path=f'shots/s6/{name}-nav.jpg', type='jpeg', quality=45)
        b.close()
    json.dump(res, open(out,'w'), indent=2)
if __name__=='__main__':
    cfg=json.loads(sys.argv[1]); run(cfg['name'], cfg['turns'], cfg.get('nav'), cfg['out'])
