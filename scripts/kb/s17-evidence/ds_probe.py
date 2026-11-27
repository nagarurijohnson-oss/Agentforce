import sys,time,json
sys.path.insert(0,'/tmp/agentforce_build-50144f18-a53e-4e8e-9955-a43b7975a4d2/work')
from ui_harness import *
PS='0PSjV000004iF7V'
with sync_playwright() as p:
    b=p.chromium.launch(executable_path=EXE); pg=b.new_page(viewport={'width':1400,'height':1000})
    pg.goto(front('/'+PS+'?s=DataspaceScopes&isdtp=p1'), wait_until='domcontentloaded', timeout=120000); time.sleep(10)
    print(' '.join(pg.evaluate('() => document.body.innerText').split())[:1500])
    print(pg.evaluate("() => [...document.querySelectorAll('input[type=button],input[type=submit],button,a')].map(e=>(e.value||e.textContent||'').trim()+'|'+(e.getAttribute('href')||e.getAttribute('onclick')||'').slice(0,160)).filter(x=>x.length>2).slice(0,80)"))
    pg.screenshot(path='s17/shots/ds-before.jpg',type='jpeg',quality=45,full_page=True); b.close()
