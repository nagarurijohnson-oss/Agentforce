# S18: open every Knowledge link the published v4 cited (s18/cited.json) in Lightning as the admin; read-only.
import sys,time,json
sys.path.insert(0,'/tmp/agentforce_build-50144f18-a53e-4e8e-9955-a43b7975a4d2/work')
from ui_harness import *
cited=json.load(open('s18/cited.json')); out=[]
with sync_playwright() as p:
    b=p.chromium.launch(executable_path=EXE); ctx=b.new_context(viewport={'width':1500,'height':1000}); pg=ctx.new_page()
    ext=[]; pg.on('request', lambda r: ext.append(r.url) if not any(h in r.url for h in ['salesforce.com','force.com','sfdcstatic.com','salesforce-setup.com','visualforce.com','data:','blob:']) else None)
    pg.goto(front('/lightning/page/home'), wait_until='domcontentloaded', timeout=120000); time.sleep(15)
    items=list(cited.items())
    for i,(aid,v) in enumerate([items[0]]+items):
        title,num=v[0]
        pg.goto(pg.url.split('/lightning/')[0]+f'/lightning/r/Knowledge__kav/{aid}/view', wait_until='domcontentloaded', timeout=120000); time.sleep(12)
        body=pg.evaluate('() => document.body.innerText')
        r={'id':aid,'number':num,'title':title,'title_shown':title in body,'number_shown':num in body,'published':'Published' in body,'url_ok':aid in pg.url,'warmup':i==0}
        out.append(r); print(json.dumps(r,ensure_ascii=False)); sys.stdout.flush()
        if num=='000001011' and i>0: pg.screenshot(path='s18/shots/link-000001011-v2.jpg',type='jpeg',quality=45)
    b.close()
json.dump({'links':out,'external_requests':ext},open('s18/links.json','w'),indent=1,ensure_ascii=False); print('EXT',len(ext),ext[:3])
