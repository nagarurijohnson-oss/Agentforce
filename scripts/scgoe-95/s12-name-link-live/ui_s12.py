"""SCGOE-95 Session 12: live Lightning panel tests on the deployed name-link presentation.
Signs in as the admin (frontdoor), types questions into the Agentforce panel, records every link with its row/line,
watches for images, dialogs and requests to non-Salesforce hosts, and clicks name links to confirm navigation.
Read-only: no record is changed."""
import sys, json, time, os
sys.path.insert(0, '/tmp/agentforce_build-50144f18-a53e-4e8e-9955-a43b7975a4d2/work')
from ui_harness import *
DOM = """() => { const blocks=[]; const f=(r)=>{ r.querySelectorAll('*').forEach(e=>{ if(e.tagName.toLowerCase()==='runtime_copilot_base-message-block') blocks.push(e); if(e.shadowRoot) f(e.shadowRoot); }); }; f(document);
 const bk=blocks[blocks.length-1]; const els=[]; const g=(r)=>{ r.querySelectorAll('*').forEach(e=>{ els.push(e); if(e.shadowRoot) g(e.shadowRoot); }); }; if(bk.shadowRoot) g(bk.shadowRoot); g(bk);
 const q=(t)=>els.filter(e=>t.includes(e.tagName));
 const ctxOf=(a)=>{ let p=a; while(p && !['TR','P','LI'].includes(p.tagName)) p=p.parentElement; return p? (p.tagName==='TR'? Array.from(p.children).map(td=>td.innerText).join(' | '): p.innerText): null; };
 return {n:blocks.length, text: bk.innerText, links:q(['A']).map(a=>({t:a.textContent, h:a.getAttribute('href'), target:a.getAttribute('target'), ctx:ctxOf(a)})),
  imgs:q(['IMG']).map(i=>i.getAttribute('src')), fmt:q(['B','STRONG','EM','I','CODE','DEL','S','H1','H2','H3','U','SCRIPT','IFRAME']).map(e=>e.tagName+':'+e.textContent.slice(0,60)),
  headers:q(['TH']).map(e=>e.innerText), rows:q(['TR']).map(tr=>Array.from(tr.children).map(td=>td.innerText)) }; }"""
SF = ('force.com', 'salesforce.com', 'sfdc', 'salesforce-scrt', 'visualforce.com', 'data:', 'blob:', 'about:', 'chrome', 'sfdcstatic.com', 'salesforceliveagent', 'documentforce.com', 'lightning.com')
def main(cfg):
    os.makedirs('shots/s12', exist_ok=True); name = cfg['name']; res = {'conversation': name, 'turns': []}
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=EXE); ctx = b.new_context(viewport={'width': 1600, 'height': 1000}); pg = ctx.new_page()
        dialogs = []; ext = []
        pg.on('dialog', lambda d: (dialogs.append(d.message), d.dismiss()))
        ctx.on('request', lambda r: ext.append(r.url) if r.url.startswith('http') and not any(s in r.url.split('/')[2] for s in SF) else None)
        open_panel(pg); gotit(pg)
        res['agent_selected'] = pg.evaluate(TAGTXT, 'runtime_copilot_base-base-button').get('runtime_copilot_base-base-button')
        for i, u in enumerate(cfg['turns']):
            n = len(pg.evaluate(LAST)); send(pg, u); wait_reply(pg, n, 200); time.sleep(4)
            r = pg.evaluate(DOM); r['utterance'] = u; res['turns'].append(r)
            print(name, i, json.dumps({'text': r['text'][:900], 'links': r['links'], 'imgs': r['imgs'], 'fmt': r['fmt']}, ensure_ascii=False)[:2500]); sys.stdout.flush()
            pg.screenshot(path=f'shots/s12/{name}-{i + 1}.jpg', type='jpeg', quality=45, full_page=True)
        if cfg.get('nav'):
            res['navigation'] = []
            for txt in cfg['nav']:
                try:
                    lk = pg.locator('runtime_copilot_base-message-block a').filter(has_text=txt).last
                    href = lk.get_attribute('href'); before = pg.url; npages = len(ctx.pages)
                    lk.click(timeout=15000); time.sleep(15)
                    tgt = ctx.pages[-1] if len(ctx.pages) > npages else pg
                    res['navigation'].append({'linkText': txt, 'href': href, 'before': before, 'after': tgt.url, 'newTab': len(ctx.pages) > npages,
                                              'title': tgt.evaluate('() => document.title')})
                    if tgt is not pg: tgt.close()
                    else: pg.go_back(); time.sleep(10)
                except Exception as e:
                    res['navigation'].append({'linkText': txt, 'error': str(e)[:200]})
                print('NAV', json.dumps(res['navigation'][-1], ensure_ascii=False)); sys.stdout.flush()
        res['dialogs'] = dialogs; res['external_requests'] = sorted(set(ext))
        b.close()
    json.dump(res, open(cfg['out'], 'w'), indent=1, ensure_ascii=False)
if __name__ == '__main__':
    main(json.load(open(sys.argv[1])))
