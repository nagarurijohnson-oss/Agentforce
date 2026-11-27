import sys,time
sys.path.insert(0,'/tmp/agentforce_build-50144f18-a53e-4e8e-9955-a43b7975a4d2/work')
from ui_harness import *
PS='0PSjV000004iF7V'
with sync_playwright() as p:
    b=p.chromium.launch(executable_path=EXE); pg=b.new_page(viewport={'width':1400,'height':1000})
    pg.goto(front('/'+PS+'/e?s=DataspaceScopes&isdtp=p1'), wait_until='domcontentloaded', timeout=120000); time.sleep(10)
    boxes=pg.locator('input[type=checkbox][id*="dataspace_scope_access"][id*="selected_viewport"]')
    rows=pg.evaluate("() => [...document.querySelectorAll('input[type=checkbox][id*=dataspace_scope_access]')].map(c=>c.closest('tr').innerText.trim())")
    print('ROWS',rows)
    if boxes.count()!=1 or 'default' not in rows[0]: print('ABORT unexpected rows'); b.close(); sys.exit(1)
    boxes.first.check(); time.sleep(2)
    pg.locator('input[id$=":saveButton"]').first.click(); time.sleep(12)
    pg.goto(front('/'+PS+'?s=DataspaceScopes&isdtp=p1'), wait_until='domcontentloaded', timeout=120000); time.sleep(10)
    t=' '.join(pg.evaluate('() => document.body.innerText').split()); i=t.find('Data Spaces'); print('VIEW',t[i:i+300])
    pg.screenshot(path='s17/shots/ds-after.jpg',type='jpeg',quality=45,full_page=True); b.close()
