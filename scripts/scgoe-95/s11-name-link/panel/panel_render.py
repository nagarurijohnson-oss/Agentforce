"""Lightning Experience Agentforce panel rendering check. A real turn runs on the active agent (read-only search, synthetic
Contact). In THIS browser only, the reply in the /messages/stream response is replaced with a test reply, so the panel's own
renderer draws it. Nothing is saved and nothing changes in the org."""
import sys, json, time, re
sys.path.insert(0,'/tmp/agentforce_build-50144f18-a53e-4e8e-9955-a43b7975a4d2/work')
from ui_harness import *
D=json.load(open(sys.argv[1])); FIX=D['fixtures']; order=sys.argv[3:] or list(FIX); OUT=sys.argv[2]
DOM = """() => { const blocks=[]; const f=(r)=>{ r.querySelectorAll('*').forEach(e=>{ if(e.tagName.toLowerCase()==='runtime_copilot_base-message-block') blocks.push(e); if(e.shadowRoot) f(e.shadowRoot); }); }; f(document);
 const bk=blocks[blocks.length-1]; const els=[]; const g=(r)=>{ r.querySelectorAll('*').forEach(e=>{ els.push(e); if(e.shadowRoot) g(e.shadowRoot); }); }; if(bk.shadowRoot) g(bk.shadowRoot); g(bk);
 const q=(t)=>els.filter(e=>t.includes(e.tagName));
 return {n:blocks.length, text: bk.innerText, links:q(['A']).map(a=>({t:a.textContent, h:a.getAttribute('href'), target:a.getAttribute('target')})),
  imgs:q(['IMG']).map(i=>i.getAttribute('src')), fmt:q(['B','STRONG','EM','I','CODE','DEL','S','H1','H2','H3','U','SCRIPT','IFRAME']).map(e=>e.tagName+':'+e.textContent.slice(0,60)),
  rows:q(['TR']).map(tr=>Array.from(tr.children).map(td=>td.innerText)),
  paras:q(['P','LI']).map(p=>p.innerText) }; }"""
res={}
with sync_playwright() as p:
    b=p.chromium.launch(executable_path=EXE); ctx=b.new_context(viewport={'width':1600,'height':1000}); pg=ctx.new_page()
    dialogs=[]; evil=[]
    pg.on('dialog', lambda d:(dialogs.append(d.message), d.dismiss()))
    pg.on('request', lambda r: evil.append(r.url) if 'evil.example' in r.url else None)
    cur={'name':None}
    def handler(route):
        if route.request.method!='POST' or not cur['name']: return route.continue_()
        r=route.fetch(); body=r.text(); txt=FIX[cur['name']]; evs=[]; first=True
        for e in body.split('\n\n'):
            if not e.strip(): continue
            lines=e.split('\n'); dl=[l for l in lines if l.startswith('data: ')]
            if not dl: evs.append(e); continue
            d=json.loads(dl[0][6:]); m=d.get('message',{})
            if m.get('type')=='TextChunk':
                if not first: continue
                first=False; m['message']=txt
            elif m.get('type')=='Inform': m['message']=txt
            evs.append('\n'.join([l for l in lines if not l.startswith('data: ')]+['data: '+json.dumps(d, ensure_ascii=False)]))
        cur['name']=None
        route.fulfill(response=r, body='\n\n'.join(evs)+'\n\n')
    ctx.route('**/einstein/ai-agent/**/messages/stream', handler)
    open_panel(pg); gotit(pg)
    for name in order:
        n=len(pg.evaluate(LAST)); cur['name']=name
        send(pg,'Find the contact with email priya.synthwell@synthetic.example'); wait_reply(pg,n,180); time.sleep(4)
        r=pg.evaluate(DOM); r['dialogs']=list(dialogs); r['evil_requests']=list(evil); res[name]=r
        pg.screenshot(path='shots/s11/%s.jpg'%name, type='jpeg', quality=50, full_page=True)
        print(name, 'links', len(r['links']), 'imgs', r['imgs'], 'fmt', r['fmt'][:8], 'rows', len(r['rows'])); sys.stdout.flush()
    b.close()
json.dump(res, open(OUT,'w'), indent=1, ensure_ascii=False)
