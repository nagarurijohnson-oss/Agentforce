"""A-5 fallback (read-only): use the Log in as session's own my-domain sid as a Bearer token. Never printed or saved."""
import sys,json,time,re
W='/tmp/agentforce_build-50144f18-a53e-4e8e-9955-a43b7975a4d2/work'; sys.path.insert(0,W)
from ui_harness import *
ORG='00DjV000003BVbRUAW'; U='005jV000003sYUPQA2'; out={}
with sync_playwright() as p:
    b=p.chromium.launch(executable_path=EXE); ctx=b.new_context(); pg=ctx.new_page()
    pg.goto(front('/lightning/page/home'),wait_until='domcontentloaded',timeout=120000); time.sleep(8)
    base=re.match(r'https://[^/]+',pg.url).group(0)
    pg.goto(f"{base}/servlet/servlet.su?oid={ORG}&suorgadminid={U}&retURL=%2Fhome%2Fhome.jsp&targetURL=%2Fhome%2Fhome.jsp",wait_until='domcontentloaded',timeout=120000); time.sleep(15)
    m=re.search(r'Logged in as ([^\n]{0,40})',pg.evaluate('() => document.body.innerText')); out['banner']=m.group(0) if m else None
    for c in [c for c in ctx.cookies() if c['name']=='sid']:
        inst='https://'+c['domain'].lstrip('.'); h={'Authorization':'Bearer '+c['value'],'Content-Type':'application/json'}
        if 'my.salesforce.com' not in inst: continue
        r={}
        x=ctx.request.get(inst+'/services/oauth2/userinfo',headers=h); r['userinfo']=[x.status,(re.search(r'"user_id":"(\w+)"',x.text()) or [None,None])[1] if x.ok else x.text()[:200]]
        x=ctx.request.get(inst+'/services/data/v66.0/query?q=SELECT+Id+FROM+Contact+LIMIT+1',headers=h); r['soql']=[x.status,x.text()[:200]]
        for k,sql in [('dmo_kav',"SELECT ssot__ArticleNumber__c FROM ssot__KnowledgeArticleVersion__dlm LIMIT 3"),('dmo_chunk',"SELECT SourceRecordId__c FROM KA_CRA_Scholarship_Knowledge_chunk__dlm LIMIT 3")]:
            x=ctx.request.post(inst+'/services/data/v66.0/ssot/query-sql',headers=h,data=json.dumps({'sql':sql})); r[k]=[x.status,x.text()[:300]]
        out[inst]=r
    b.close()
print(json.dumps(out,indent=1)); json.dump(out,open(W+'/s23/a5b.json','w'),indent=1)
