"""Session 14 restricted-user UAT driver. Signs in as the admin (frontdoor), uses Log in as for CRA UAT Restricted,
and in that session: runs the test-only harness flow, opens Knowledge article pages, and uses the Agentforce panel.
Read-only: no record is created or changed. Usage: uat.py <phase> <out.json> [steps...]  steps: who harness articles panel links"""
import sys, json, time, re, urllib.parse
W='/tmp/agentforce_build-50144f18-a53e-4e8e-9955-a43b7975a4d2/work'; sys.path.insert(0,W)
from ui_harness import *          # LAST, wait_reply, send, CLICK, VIS, gotit, EXE, front
ORG='00DjV000003BVbRUAW'; U='005jV000003sYUPQA2'
PH=sys.argv[1]; OUT=sys.argv[2]; STEPS=sys.argv[3:] or ['who','harness','articles']
ART=json.load(open(W+'/Agentforce-kb/scripts/kb/articles_live.json'))
HQ=[('KT-01','What GPA do I need to keep the Merit Excellence Scholarship?'),
    ('KT-13','How do I renew my parking permit?'),
    ('KT-12L','How do I appeal a library fine?'),
    ('KT-12','How do I appeal?')]
RUNS=int(__import__('os').environ.get('RUNS','2'))
res={'phase':PH,'started':time.strftime('%FT%TZ',time.gmtime())}
def alltext(pg):
    t=''
    for fr in pg.frames:
        try: t+='\n'+(fr.evaluate('() => document.body ? document.body.innerText : ""') or '')
        except Exception: pass
    return t
def alllinks(pg):
    out=[]
    for fr in pg.frames:
        try: out+=fr.evaluate("() => [...document.querySelectorAll('a')].map(a=>({t:a.textContent.trim(),h:a.getAttribute('href')})).filter(x=>x.h)")
        except Exception: pass
    return out
with sync_playwright() as p:
    b=p.chromium.launch(executable_path=EXE); ctx=b.new_context(viewport={'width':1600,'height':1000}); pg=ctx.new_page()
    ext=[]; pg.on('request', lambda r: ext.append(r.url) if not re.search(r'salesforce|force\.com|sfdc|lightning|visualforce|data:|blob:|about:',r.url) else None)
    pg.goto(front('/lightning/page/home'), wait_until='domcontentloaded', timeout=120000); time.sleep(8)
    base=re.match(r'https://[^/]+', pg.url).group(0)
    su=f"{base}/servlet/servlet.su?oid={ORG}&suorgadminid={U}&retURL=%2F005{U[3:]}&targetURL=%2Flightning%2Fpage%2Fhome"
    if PH.startswith('ADMIN'):
        m=re.match(r'(.*)','Logged in as ADMIN CONTROL (no Log in as)'); res['login_as']={'banner':'admin control','url':pg.url.split('?')[0]}
    else:
        pg.goto(su, wait_until='domcontentloaded', timeout=120000); time.sleep(20)
        txt=alltext(pg); m=re.search(r'Logged in as ([^\n]{0,60})',txt)
    if not PH.startswith('ADMIN'): res['login_as']={'banner':m.group(0) if m else None,'url':pg.url.split('?')[0]}
    print('LOGIN', res['login_as']); sys.stdout.flush()
    if not PH.startswith('ADMIN') and (not m or 'CRA UAT Restricted' not in m.group(0)):
        pg.screenshot(path=f'shots/{PH}-loginas-fail.jpg', type='jpeg', quality=45); res['error']='login as not confirmed'
        json.dump(res,open(OUT,'w'),indent=1); b.close(); sys.exit(2)
    if 'harness' in STEPS:
        res['harness']=[]
        for key,qq in HQ:
            for r in range(RUNS):
                pg.goto(f"{base}/flow/SF_UAT_Knowledge_Answer_Harness?varT_Question={urllib.parse.quote(qq)}", wait_until='domcontentloaded', timeout=120000)
                t0=time.time(); t=''
                while time.time()-t0<150:
                    time.sleep(4); t=alltext(pg)
                    if 'HARNESS_ANSWER_END' in t or 'HARNESS_FAULT' in t: break
                user=re.search(r'HARNESS_USER=([^\n]*)',t); ans=re.search(r'HARNESS_ANSWER_START(.*?)HARNESS_ANSWER_END',t,re.S); flt=re.search(r'HARNESS_FAULT=([^\n]*)',t)
                links=[l for l in alllinks(pg) if 'Knowledge__kav' in (l['h'] or '') or 'ka0' in (l['h'] or '')]
                row={'key':key,'q':qq,'run':r+1,'user':user.group(1).strip() if user else None,'answer':ans.group(1).strip() if ans else None,'fault':flt.group(1).strip() if flt else None,'kb_links':links,'secs':round(time.time()-t0)}
                if not user: row['page']=t[-800:]
                res['harness'].append(row); print('H',json.dumps(row,ensure_ascii=False)[:700]); sys.stdout.flush()
                pg.screenshot(path=f'shots/{PH}-h-{key}-{r+1}.jpg', type='jpeg', quality=40)
    if 'articles' in STEPS:
        res['articles']=[]
        for a in ART:
            pg.goto(f"{base}/lightning/r/Knowledge__kav/{a['Id']}/view", wait_until='domcontentloaded', timeout=120000); time.sleep(14)
            t=alltext(pg)
            shown = a['Title'] in t and ('Article Number' in t or a['ArticleNumber'] in t)
            err=re.search(r"(insufficient privileges|don.t have access|Looks like there.s a problem|isn.t available|no longer available|Record not found|hasn.t been shared|You can.t view)[^\n]{0,120}",t,re.I)
            row={"shown_ok":None,"n":a["ArticleNumber"],'status':a['PublishStatus'],'title':a['Title'],'shown':shown,'error':err.group(0) if err else None}
            res['articles'].append(row); print('A',row); sys.stdout.flush()
            pg.screenshot(path=f"shots/{PH}-a-{a['ArticleNumber']}.jpg", type='jpeg', quality=35)

    def open_panel_uat():
        pg.goto(base+'/lightning/page/home', wait_until='domcontentloaded', timeout=120000)
        for k in range(10):
            time.sleep(5)
            if pg.evaluate(VIS): return True
        for attempt in range(3):
            try: pg.locator('button[title="Agentforce"]:visible, button[aria-label="Agentforce"]:visible').first.click(timeout=20000)
            except Exception as e: print('click err', str(e)[:80])
            for k in range(6):
                time.sleep(5); pg.evaluate(CLICK, 'Got It')
                if pg.evaluate(VIS): return True
        return False
    CT=[('C1','Find the contact with email priya.synthwell@synthetic.example'),('C2','Find Zed Hiddenmore'),('C3','Find Jordan Samename'),
        ('C4',"Change Priya Synthwell's title to CFO"),('C5','What GPA do I need to keep the Merit Excellence Scholarship?')]
    if 'panel' in STEPS:
        res['panel']={'opened':open_panel_uat()}
        if res['panel']['opened']:
            gotit(pg); res['panel']['agent']=pg.evaluate(TAGTXT,'runtime_copilot_base-base-button').get('runtime_copilot_base-base-button'); res['panel']['turns']=[]
            for key,u in CT:
                n=len(pg.evaluate(LAST)); send(pg,u); r=wait_reply(pg,n,180)
                res['panel']['turns'].append({'key':key,'u':u,'reply':r}); print('P',key,json.dumps(r,ensure_ascii=False)[:600]); sys.stdout.flush()
                pg.screenshot(path=f'shots/{PH}-p-{key}.jpg', type='jpeg', quality=40)
        else: pg.screenshot(path=f'shots/{PH}-panel-fail.jpg', type='jpeg', quality=40)
    if 'links' in STEPS:
        # In THIS browser only, the agent's reply in /messages/stream is replaced by a Knowledge reply in the exact v6 template
        # format (Source link built from the article Id), so the panel draws it; then the link is clicked as the UAT user.
        FIXT=[('L-A04','Merit Excellence Scholarship – Renewal Requirements','ka0jV000000nIDXQA2','000001004'),
              ('L-A13','Campus Parking Permit – Renewal','ka0jV000000nIFBQA2','000001013')]
        cur={'t':None}
        def handler(route):
            if route.request.method!='POST' or not cur['t']: return route.continue_()
            r=route.fetch(); body=r.text(); evs=[]; first=True
            for e in body.split('\n\n'):
                if not e.strip(): continue
                lines=e.split('\n'); dl=[l for l in lines if l.startswith('data: ')]
                if not dl: evs.append(e); continue
                d=json.loads(dl[0][6:]); m=d.get('message',{})
                if m.get('type')=='TextChunk':
                    if not first: continue
                    first=False; m['message']=cur['t']
                elif m.get('type')=='Inform': m['message']=cur['t']
                evs.append('\n'.join([l for l in lines if not l.startswith('data: ')]+['data: '+json.dumps(d, ensure_ascii=False)]))
            cur['t']=None; route.fulfill(response=r, body='\n\n'.join(evs)+'\n\n')
        ctx.route('**/einstein/ai-agent/**/messages/stream', handler)
        res['links']=[]
        for key,title,aid,num in FIXT:
            if not pg.evaluate(VIS): open_panel_uat(); gotit(pg)
            txt=f"Test reply.\n\nSource: [{title}](/lightning/r/Knowledge__kav/{aid}/view) (Article {num})"
            n=len(pg.evaluate(LAST)); cur['t']=txt; send(pg,'Find the contact with email priya.synthwell@synthetic.example'); r=wait_reply(pg,n,180); time.sleep(3)
            row={'key':key,'expected_id':aid,'rendered_links':r.get('links') if r else None}
            try:
                lk=pg.locator(f'runtime_copilot_base-message-block a:has-text("{title}")').last; row['href']=lk.get_attribute('href'); before=len(ctx.pages)
                lk.click(timeout=15000); time.sleep(16)
                tgt=ctx.pages[-1]; row['new_tab']=len(ctx.pages)>before; row['url_after']=tgt.url.split('?')[0]
                t=alltext(tgt); row['article_shown']= title in t and (num in t or 'Article Number' in t)
                e=re.search(r"(insufficient privileges|don.t have access|Looks like there.s a problem|isn.t available|no longer available|Record not found|hasn.t been shared|You can.t view)[^\n]{0,120}",t,re.I); row['error']=e.group(0) if e else None
                tgt.screenshot(path=f'shots/{PH}-{key}.jpg', type='jpeg', quality=40)
                if tgt is not pg: tgt.close()
            except Exception as ex: row['exception']=str(ex)[:200]
            res['links'].append(row); print('L',json.dumps(row,ensure_ascii=False)[:500]); sys.stdout.flush()
        ctx.unroute('**/einstein/ai-agent/**/messages/stream')
    res['external_requests']=sorted(set(ext))
    if PH.startswith('ADMIN'): pass
    else:
     try: pg.goto(base+'/secur/logout.jsp', wait_until='domcontentloaded', timeout=60000); time.sleep(6); res['logout_url']=pg.url.split('?')[0]
     except Exception as e: res['logout_url']=str(e)[:100]
    b.close()
res['ended']=time.strftime('%FT%TZ',time.gmtime()); json.dump(res,open(OUT,'w'),indent=1,ensure_ascii=False); print('DONE')
