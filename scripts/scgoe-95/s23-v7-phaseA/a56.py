"""S23 A-5/A-6 (read-only) as CRA UAT Restricted via Log in as. usage: a56.py <targets.json> <out.json>
targets: [{"kind":"contact|article","id":"...","expect":"open|refused","why":"..."}]. Session id is never printed or saved."""
import sys,json,time,re
W='/tmp/agentforce_build-50144f18-a53e-4e8e-9955-a43b7975a4d2/work'; sys.path.insert(0,W)
from ui_harness import *
ORG='00DjV000003BVbRUAW'; U='005jV000003sYUPQA2'
T=json.load(open(sys.argv[1])); out={'a5':{},'a6':[]}
DENY=re.compile(r"Insufficient Privileges|Data Not Available|do not have the level of access|don't have access|isn't available|has been deleted|Unable to Access Page|URL No Longer Exists",re.I)
with sync_playwright() as p:
    b=p.chromium.launch(executable_path=EXE); ctx=b.new_context(viewport={'width':1600,'height':1000}); pg=ctx.new_page()
    pg.goto(front('/lightning/page/home'),wait_until='domcontentloaded',timeout=120000); time.sleep(8)
    base=re.match(r'https://[^/]+',pg.url).group(0)
    pg.goto(f"{base}/servlet/servlet.su?oid={ORG}&suorgadminid={U}&retURL=%2Fhome%2Fhome.jsp&targetURL=%2Fhome%2Fhome.jsp",wait_until='domcontentloaded',timeout=120000); time.sleep(15)
    txt=pg.evaluate('() => document.body.innerText'); m=re.search(r'Logged in as ([^\n]{0,40})',txt); out['banner']=m.group(0) if m else None
    inst=re.match(r'https://[^/]+',pg.url).group(0); out['instance']=inst
    has=pg.evaluate("() => typeof window.__sfdcSessionId==='string' && window.__sfdcSessionId.length>20"); out['a5']['api_session_available']=has
    if has:
        JS="""async ([path,method,body]) => { const r=await fetch(path,{method,headers:{'Authorization':'Bearer '+window.__sfdcSessionId,'Content-Type':'application/json'},body:body?JSON.stringify(body):undefined});
          const t=await r.text(); return {status:r.status, body:t.slice(0,600)}; }"""
        out['a5']['whoami']=pg.evaluate(JS,['/services/oauth2/userinfo','GET',None])
        try: out['a5']['whoami_user']=json.loads(out['a5']['whoami']['body']+'"}' if False else out['a5']['whoami']['body']).get('user_id')
        except Exception: out['a5']['whoami_user']=re.search(r'"user_id":"(\w+)"',out['a5']['whoami']['body']).group(1) if '"user_id"' in out['a5']['whoami']['body'] else None
        out['a5']['control_soql']=pg.evaluate(JS,["/services/data/v66.0/query?q=SELECT+Id+FROM+Contact+LIMIT+1",'GET',None])
        for k,sql in [('dmo_kav',"SELECT ssot__ArticleNumber__c FROM ssot__KnowledgeArticleVersion__dlm LIMIT 3"),('dmo_chunk',"SELECT SourceRecordId__c FROM KA_CRA_Scholarship_Knowledge_chunk__dlm LIMIT 3")]:
            out['a5'][k]=pg.evaluate(JS,['/services/data/v66.0/ssot/query-sql','POST',{'sql':sql}])
            out['a5'][k+'_v68']=pg.evaluate(JS,['/services/data/v68.0/ssot/query-sql','POST',{'sql':sql}])
    for t in T:
        pg.goto(f"{inst}/{t['id']}",wait_until='domcontentloaded',timeout=120000); time.sleep(6)
        body=pg.evaluate('() => document.body.innerText'); title=pg.title()
        dm=DENY.search(body) or DENY.search(title)
        res={**t,'url':pg.url.split('?')[0],'title':title[:120],'denied':bool(dm),'deny_text':dm.group(0) if dm else None,
             'shows_name':bool(t.get('name')) and t['name'].split(' ')[0].lower() in body.lower()}
        res['outcome']='refused' if dm else ('open' if res['shows_name'] else 'unclear')
        res['pass']=res['outcome']==t['expect']; out['a6'].append(res); print('A6',t['kind'],t['id'],res['outcome'],'expect',t['expect'],res['deny_text'] or res['title'][:50]); sys.stdout.flush()
        pg.screenshot(path=f"{W}/s23/shots/a6-{t['id']}.jpg",type='jpeg',quality=40)
    b.close()
for k,v in out['a5'].items():
    if isinstance(v,dict): print('A5',k,v['status'],v['body'][:160].replace('\n',' '))
json.dump(out,open(sys.argv[2],'w'),indent=1)
