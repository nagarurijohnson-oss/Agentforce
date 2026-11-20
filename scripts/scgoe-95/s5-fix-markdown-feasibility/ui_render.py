"""Builder Preview rendering check. A real Live Test turn runs on the deployed draft; in this browser only, the reply text in the
/messages response is replaced with a test reply, so the Builder's own renderer draws it. Nothing is saved, committed, published
or activated, and nothing changes in the org."""
import json, time, subprocess, os, sys
from playwright.sync_api import sync_playwright
REPO='/tmp/build-52db6c0d-57e1-4383-bac3-df377a70eecc/work/Agentforce'; HERE=os.path.dirname(os.path.abspath(__file__))
FIX=json.load(open(HERE+'/fixtures.json'))['fixtures']; names=sys.argv[1:] or list(FIX)
FIND = """(marker) => { let best=null; const walk=(r)=>{ r.querySelectorAll('*').forEach(e=>{ if(e.shadowRoot) walk(e.shadowRoot);
  const t=e.textContent||''; if(t.includes(marker) && (!best || t.length < best.textContent.length) && e.querySelectorAll) {
    if (e.querySelector('table') || t.includes('Email:') ) best=e; } }); }; walk(document);
  if(!best) return null; const bb=best.getBoundingClientRect();
  const q=(s)=>Array.from(best.querySelectorAll(s));
  return {html: best.innerHTML, text: best.innerText, box:[bb.x,bb.y,bb.width,bb.height],
    links: q('a').map(a=>[a.innerText, a.getAttribute('href')]), imgs: q('img').map(i=>i.getAttribute('src')),
    scripts: q('script').length, iframes: q('iframe').length, bold: q('b,strong').map(e=>e.innerText), em: q('em,i').map(e=>e.innerText),
    code: q('code').map(e=>e.innerText), heads: q('h1,h2,h3,h4,h5,h6').map(e=>e.innerText), del: q('del,s').map(e=>e.innerText),
    cells: q('td').map(e=>e.innerText), rows: q('tr').length}; }"""
out={}
with sync_playwright() as p:
    b=p.chromium.launch(executable_path=os.environ['PW_EXE'])
    for name in names:
        subprocess.run('sf org open agent --authoring-bundle Contact_Read_Agent -r -o orgfarm-232477b490-dev-ed --json 2>/dev/null > %s/.u.json' % HERE, shell=True, cwd=REPO)
        url=json.load(open(HERE+'/.u.json'))['result']['url']; os.remove(HERE+'/.u.json')
        ctx=b.new_context(viewport={'width':1700,'height':1600}); pg=ctx.new_page(); dialogs=[]
        pg.on('dialog', lambda d: (dialogs.append(d.message), d.dismiss()))
        reqs=[]; pg.on('request', lambda r: reqs.append(r.url) if 'evil.example' in r.url else None)
        def handler(route, request=None, name=name):
            if route.request.method != 'POST': return route.continue_()
            r=route.fetch(); body=r.json()
            for m in body.get('messages', []):
                if 'message' in m: m['message']=FIX[name]
            route.fulfill(response=r, body=json.dumps(body))
        ctx.route('**/einstein/ai-agent/**/preview/sessions/*/messages', handler)
        pg.goto(url, wait_until='domcontentloaded', timeout=120000); pg.wait_for_timeout(30000)
        pg.locator("a:has-text('Preview')").first.click(timeout=60000); pg.wait_for_timeout(12000)
        pg.locator("text=Live Test").first.click(timeout=15000); pg.wait_for_timeout(3000)
        pg.locator("text=Live Test Mode").first.click(timeout=15000); pg.wait_for_timeout(8000)
        box=pg.locator("[contenteditable=true][role=textbox]").first
        box.click(); box.type('Hello', delay=20); pg.wait_for_timeout(1000); pg.keyboard.press('Enter'); pg.wait_for_timeout(40000)
        marker = 'Here are the test values' if 'table' in name else 'I found one matching Contact'
        res=pg.evaluate(FIND, marker)
        if res:
            x,y,w,h=res['box']; pg.screenshot(path=HERE+'/shots/%s.png'%name, clip={'x':max(0,x-10),'y':max(0,y-10),'width':min(w+20,900),'height':min(h+20,1500)})
        pg.screenshot(path=HERE+'/shots/%s-full.png'%name)
        res = res or {}; res['dialogs']=dialogs; res['evil_requests']=reqs; out[name]=res
        print('==', name, 'found' if res.get('html') else 'NOT FOUND', 'dialogs', dialogs, 'evil requests', reqs)
        print('links', res.get('links'), 'imgs', res.get('imgs'), 'scripts', res.get('scripts'), 'bold', res.get('bold'), 'em', res.get('em'), 'code', res.get('code'), 'heads', res.get('heads'), 'del', res.get('del'), 'rows', res.get('rows'))
        ctx.close()
    b.close()
prev = json.load(open(HERE+'/render.json')) if os.path.exists(HERE+'/render.json') else {}
prev.update(out); json.dump(prev, open(HERE+'/render.json','w'), indent=1, ensure_ascii=False)
