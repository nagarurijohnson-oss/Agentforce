import sys,re,time
sys.path.insert(0,'/tmp/agentforce_build-50144f18-a53e-4e8e-9955-a43b7975a4d2/work')
from ui_harness import *
PS='0PSjV000004iB5V'
CATS=['Merit Excellence','Need-Based Opportunity','STEM Futures','Arts and Humanities','Graduate Research','International Student','Athletic','General Financial Aid']
with sync_playwright() as p:
    b=p.chromium.launch(executable_path=EXE); ctx=b.new_context(viewport={'width':1400,'height':1100}); pg=ctx.new_page()
    pg.goto(front('/'+PS+'/e?s=DataCategoryVisibility&cid=0D1jV000000OX2r&unid='+PS+'&sid=PermSets&isdtp=p1'), wait_until='domcontentloaded', timeout=120000); time.sleep(12)
    pg.locator('input[type=radio][value=custom]').check(); time.sleep(4)
    for c in CATS:
        pg.locator('a', has_text=re.compile('^'+re.escape(c)+'$')).first.click(); time.sleep(1)
        pg.get_by_text('Add >', exact=False).first.click(); time.sleep(2)
    t=pg.evaluate('() => document.body.innerText'); i=t.find('Selected Categories'); print('SELECTED', ' '.join(t[i:i+500].split()))
    pg.screenshot(path='shots/dcv-selected.jpg',type='jpeg',quality=45, full_page=True)
    if 'Campus Services' in t[i:]: print('ABORT campus selected'); b.close(); sys.exit(1)
    pg.locator('input[type=submit][value=Save]').first.click(); time.sleep(12)
    pg.goto(front('/'+PS+'?s=DataCategoryVisibility&isdtp=p1'), wait_until='domcontentloaded', timeout=120000); time.sleep(10)
    t=pg.evaluate('() => document.body.innerText'); i=t.find('Category Group Visibility Settings'); print('VIEW', ' '.join(t[i:i+700].split()))
    pg.screenshot(path='shots/dcv-after.jpg',type='jpeg',quality=45, full_page=True)
    b.close()
