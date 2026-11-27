"""S24 Phase B: Lightning Agentforce panel tests AS CRA UAT Restricted (Log in as). Read-only: types questions,
records each reply's text, links, images and formatting elements, screenshots, network session ids, and clicks links.
usage: panel.py <convs.json> <out.json> [only_ids]. No session token is printed or saved."""
import sys, json, time, re, os
W='/tmp/agentforce_build-50144f18-a53e-4e8e-9955-a43b7975a4d2/work'; sys.path.insert(0,W)
from ui_harness import *
ORG='00DjV000003BVbRUAW'; U='005jV000003sYUPQA2'
sys.path.insert(0,W+'/s24'); 
DOM=open(W+'/ui_s12.py').read().split('DOM = """')[1].split('"""')[0]
SF=('force.com','salesforce.com','sfdc','salesforce-scrt','visualforce.com','sfdcstatic.com','documentforce.com','lightning.com','salesforce-setup.com')
UUID=re.compile(r'"(?:sessionId|session_id|conversationId)"\s*:\s*"([0-9a-fA-F-]{20,40})"')
ACT=re.compile(r'(present_results|answer_from_knowledge|search_contacts\w*|CRA_\w+|set_question\w*)')
def login_as(pg):
    pg.goto(front('/lightning/page/home'),wait_until='domcontentloaded',timeout=120000); time.sleep(8)
    base=re.match(r'https://[^/]+',pg.url).group(0)
    pg.goto(f"{base}/servlet/servlet.su?oid={ORG}&suorgadminid={U}&retURL=%2Flightning%2Fpage%2Fhome&targetURL=%2Flightning%2Fpage%2Fhome",wait_until='domcontentloaded',timeout=120000); time.sleep(15)
    inst=re.match(r'https://[^/]+',pg.url).group(0)
    if '/lightning/' not in pg.url: pg.goto(inst+'/lightning/page/home',wait_until='domcontentloaded',timeout=120000); time.sleep(12)
    txt=pg.evaluate('() => document.body.innerText'); m=re.search(r'Logged in as ([^\n]{0,40})',txt)
    return inst, (m.group(0) if m else None), pg.url
def open_uat_panel(pg):
    for k in range(6):
        time.sleep(5)
        if pg.evaluate(VIS): return True
    for a in range(4):
        try: pg.locator('button[title="Agentforce"]:visible, button[aria-label="Agentforce"]:visible').first.click(timeout=20000)
        except Exception as e: print('click err',str(e)[:80])
        for k in range(6):
            time.sleep(5); pg.evaluate(CLICK,'Got It')
            if pg.evaluate(VIS): return True
    return False
def run_conv(p, c, outdir):
    res={'id':c['id'],'turns':[],'net_sessions':[],'net_actions':[]}
    b=p.chromium.launch(executable_path=EXE); ctx=b.new_context(viewport={'width':1600,'height':1000}); pg=ctx.new_page()
    dialogs=[]; ext=[]; sess=set(); acts=set()
    pg.on('dialog',lambda d:(dialogs.append(d.message),d.dismiss()))
    ctx.on('request',lambda r: ext.append(r.url.split('?')[0]) if r.url.startswith('http') and not any(s in r.url.split('/')[2] for s in SF) else None)
    def onresp(r):
        u=r.url
        if not any(k in u for k in ('einstein','copilot','agent','aura')): return
        try: t=r.text()
        except Exception: return
        if 'copilot' not in t.lower() and 'agent' not in u: return
        for m in UUID.findall(t): sess.add(m)
        for m in ACT.findall(t): acts.add(m)
    ctx.on('response',onresp)
    try:
        inst,banner,url=login_as(pg); res.update(banner=banner,landing=url.split('?')[0])
        res['panel_visible']=open_uat_panel(pg); gotit(pg)
        res['agent_selected']=pg.evaluate(TAGTXT,'runtime_copilot_base-base-button').get('runtime_copilot_base-base-button')
        pg.screenshot(path=f"{outdir}/{c['id']}-0.jpg",type='jpeg',quality=45)
        for i,u in enumerate(c['turns']):
            n=len(pg.evaluate(LAST)); send(pg,u); wait_reply(pg,n,240); time.sleep(4)
            r=pg.evaluate(DOM); r['utterance']=u; res['turns'].append(r)
            print(c['id'],i,json.dumps({'text':r['text'][:700],'links':r['links'],'imgs':r['imgs'],'fmt':r['fmt']},ensure_ascii=False)[:2200]); sys.stdout.flush()
            pg.screenshot(path=f"{outdir}/{c['id']}-{i+1}.jpg",type='jpeg',quality=45,full_page=True)
        res['navigation']=[]
        for txt in c.get('nav',[]):
            try:
                lk=pg.locator('runtime_copilot_base-message-block a').filter(has_text=txt).last
                href=lk.get_attribute('href'); np_=len(ctx.pages); lk.click(timeout=15000); time.sleep(15)
                tgt=ctx.pages[-1] if len(ctx.pages)>np_ else pg
                body=tgt.evaluate('() => document.body.innerText')
                nav={'linkText':txt,'href':href,'after':tgt.url.split('?')[0],'newTab':len(ctx.pages)>np_,'title':tgt.title()[:120],
                     'denied':bool(re.search(r'Insufficient Privileges|do not have the level of access',body))}
                tgt.screenshot(path=f"{outdir}/{c['id']}-nav-{len(res['navigation'])+1}.jpg",type='jpeg',quality=40)
                if tgt is not pg: tgt.close()
                else: pg.go_back(); time.sleep(10)
            except Exception as e: nav={'linkText':txt,'error':str(e)[:200]}
            res['navigation'].append(nav); print('NAV',json.dumps(nav,ensure_ascii=False)); sys.stdout.flush()
    except Exception as e:
        res['error']=str(e)[:300]; print('ERR',c['id'],res['error'])
        try: pg.screenshot(path=f"{outdir}/{c['id']}-err.jpg",type='jpeg',quality=40)
        except Exception: pass
    res.update(dialogs=dialogs,external_requests=sorted(set(ext)),net_sessions=sorted(sess),net_actions=sorted(acts))
    b.close(); return res
if __name__=='__main__':
    C=json.load(open(sys.argv[1])); out=sys.argv[2]; only=set(sys.argv[3].split(',')) if len(sys.argv)>3 else None
    outdir=W+'/s24/shots'; os.makedirs(outdir,exist_ok=True); R=[]
    with sync_playwright() as p:
        for c in C:
            if only and c['id'] not in only: continue
            R.append(run_conv(p,c,outdir)); json.dump(R,open(out,'w'),indent=1,ensure_ascii=False); time.sleep(int(os.environ.get('PAUSE','20')))
