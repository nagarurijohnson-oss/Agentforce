# S18: capture how the Lightning Agentforce panel opens its Agent API session (request bodies only). Read-only;
# opens the panel as the admin and sends nothing to the agent.
import sys, json, time
sys.path.insert(0,'/tmp/agentforce_build-50144f18-a53e-4e8e-9955-a43b7975a4d2/work')
from ui_harness import *
reqs=[]
with sync_playwright() as p:
    b=p.chromium.launch(executable_path=EXE); ctx=b.new_context(viewport={'width':1600,'height':1000}); pg=ctx.new_page()
    def onreq(r):
        u=r.url
        if 'api.salesforce.com' in u or 'ai-agent' in u or '/sessions' in u or 'agentforce' in u.lower() or 'einstein' in u.lower():
            body=r.post_data
            reqs.append({'method':r.method,'url':u.split('?')[0][:200],'body':body[:4000] if body else None})
    pg.on('request', onreq)
    open_panel(pg); gotit(pg); time.sleep(8)
    pg.screenshot(path='s18/panel-open.png')
    b.close()
for r in reqs:
    if r['body'] and 'access_token' in r['body']: r['body']='<omitted: contains a token>'
json.dump(reqs,open('s18/panel-session.json','w'),indent=1)
for r in reqs: print(r['method'],r['url']); print('   ',(r['body'] or '')[:1500])
