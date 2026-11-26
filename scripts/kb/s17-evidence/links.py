import sys,time,json
sys.path.insert(0,'/tmp/agentforce_build-50144f18-a53e-4e8e-9955-a43b7975a4d2/work')
from ui_harness import *
arts=json.load(open('s17/articles_live.json'))
ids=[(a['Id'],a['ArticleNumber'],a['Title'],a['PublishStatus'],a['VersionNumber']) for a in arts if a['PublishStatus']=='Online']+[('ka0jV000000nIF7QAM','000001011','Athletic Scholarship – Required Documents','Archived',1)]
out=[]
with sync_playwright() as p:
    b=p.chromium.launch(executable_path=EXE); ctx=b.new_context(viewport={'width':1500,'height':1000}); pg=ctx.new_page()
    ext=[]; pg.on('request', lambda r: ext.append(r.url) if not any(h in r.url for h in ['salesforce.com','force.com','sfdcstatic.com','salesforce-setup.com','visualforce.com','data:','blob:']) else None)
    pg.goto(front('/lightning/page/home'), wait_until='domcontentloaded', timeout=120000); time.sleep(15)
    for i,n,t,st,v in ids:
        pg.goto(pg.url.split('/lightning/')[0]+f'/lightning/r/Knowledge__kav/{i}/view', wait_until='domcontentloaded', timeout=120000); time.sleep(14)
        body=pg.evaluate('() => document.body.innerText')
        r={'id':i,'number':n,'expected_title':t,'status':st,'version':v,'title_shown':t in body,'number_shown':n in body,'url':pg.url,'doc_title':pg.title(),
           'status_text':[s for s in ['Published','Archived','Draft'] if s in body]}
        out.append(r); print(json.dumps(r,ensure_ascii=False)); sys.stdout.flush()
        if n=='000001011': pg.screenshot(path=f's17/shots/link-{n}-v{v}.jpg',type='jpeg',quality=45)
    b.close()
json.dump({'links':out,'external_requests':ext},open('s17/r/links.json','w'),indent=1,ensure_ascii=False); print('EXT',ext[:5])
