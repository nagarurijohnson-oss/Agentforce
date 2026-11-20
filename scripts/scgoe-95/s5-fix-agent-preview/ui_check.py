"""SCGOE-95 Session 5 fixes: drive the Agentforce Builder Preview (deployed draft, Live Test Mode) headlessly.
For each reply: screenshot the chat panel, read every rendered link (text + href), count rendered bold/HTML
elements and save the chat text. With --click, click the first Contact-name link of the last reply and record
where the browser lands (URL + record name). Never clicks Save, Commit Version, New Version, publish or activate.
Usage: python3 ui_check.py '<json list of messages>' TAG [--click]"""
import json, time, sys, subprocess, os, re
from playwright.sync_api import sync_playwright
convo = json.loads(sys.argv[1]); tag = sys.argv[2]; click = '--click' in sys.argv
HERE = os.path.dirname(os.path.abspath(__file__)); SHOTS = os.environ.get('SHOTS', HERE + '/shots'); os.makedirs(SHOTS, exist_ok=True)
REPO = os.path.abspath(HERE + '/../../..')
u = subprocess.run(['sf', 'org', 'open', 'agent', '--authoring-bundle', 'Contact_Read_Agent', '-r', '-o', 'orgfarm-232477b490-dev-ed', '--json'],
                   cwd=REPO, capture_output=True, text=True).stdout
url = json.loads(u[u.index('{'):])['result']['url']   # one-time sign-in link: kept in memory, never printed or saved
RENDER = """() => { const out={links:[],bold:[],html:0}; const walk=(r)=>{ r.querySelectorAll('a,strong,b,script,img').forEach(e=>{ const bb=e.getBoundingClientRect();
  if(bb.x>300 && bb.x<760 && bb.width>0){ const t=e.tagName.toLowerCase(); if(t==='a') out.links.push([e.innerText.slice(0,60),e.getAttribute('href')||'']);
  else if(t==='strong'||t==='b') out.bold.push(e.innerText.slice(0,60)); else out.html++; } }); r.querySelectorAll('*').forEach(e=>{if(e.shadowRoot) walk(e.shadowRoot)}); };
  walk(document); return out; }"""
log = []
with sync_playwright() as p:
    b = p.chromium.launch(executable_path=os.environ['PW_EXE']); ctx = b.new_context(viewport={'width': 1700, 'height': 1250}); pg = ctx.new_page()
    pg.goto(url, wait_until='domcontentloaded', timeout=120000); time.sleep(35)
    pg.locator("a:has-text('Preview')").first.click(timeout=60000); time.sleep(12)
    pg.locator("text=Live Test").first.click(timeout=15000); time.sleep(3)
    pg.locator("text=Live Test Mode").first.click(timeout=15000); time.sleep(8)
    for n, msg in enumerate(convo, 1):
        box = pg.locator("[contenteditable=true][role=textbox], textarea").first
        box.click(); box.type(msg, delay=20); time.sleep(1); pg.keyboard.press('Enter')
        for w in range(30):
            time.sleep(4); t = pg.evaluate("() => document.body.innerText")
            if 'Thinking' not in t and 'Working' not in t and w > 5: break
        time.sleep(4)
        pg.screenshot(path='%s/%s-%02d-chat.png' % (SHOTS, tag, n), clip={'x': 320, 'y': 120, 'width': 430, 'height': 1110})
        t = pg.evaluate("() => document.body.innerText"); i = t.find('Reset Simulator'); j = t.find('Agent Preview Details')
        r = pg.evaluate(RENDER)
        log.append({'user': msg, 'panel_text': t[i:j] if i >= 0 else t[:4000], 'rendered': r})
        print('--- %s %d' % (tag, n), json.dumps(r, ensure_ascii=False)[:700], flush=True)
    if click:
        links = [l for l in log[-1]['rendered']['links'] if '/lightning/r/Contact/' in l[1]]
        rec = {'clicked': links[0] if links else None}
        if links:
            target = pg.locator('a[href="%s"]' % links[0][1]).last
            try:
                with ctx.expect_page(timeout=15000) as np:
                    target.click()
                page2 = np.value
            except Exception:
                page2 = pg   # same-tab navigation
            page2.wait_for_load_state('domcontentloaded', timeout=60000); time.sleep(20)
            rec['landed_url_path'] = re.sub(r'^https://[^/]+', '', page2.url)
            rec['title'] = page2.title()
            rec['record_name_visible'] = page2.evaluate("""() => { const hs=[]; const walk=(r)=>{ r.querySelectorAll('lightning-formatted-name,h1,records-entity-label,.slds-page-header__title').forEach(e=>{ if((e.innerText||'').trim()) hs.push(e.innerText.trim().slice(0,80)); }); r.querySelectorAll('*').forEach(e=>{if(e.shadowRoot) walk(e.shadowRoot)}); }; walk(document); return hs.slice(0,8); }""")
            page2.screenshot(path='%s/%s-record.png' % (SHOTS, tag), clip={'x': 0, 'y': 0, 'width': 1700, 'height': 420})
        log.append({'link_click': rec}); print('CLICK', json.dumps(rec, ensure_ascii=False), flush=True)
    b.close()
json.dump(log, open('%s/%s-ui.json' % (SHOTS, tag), 'w'), indent=1, ensure_ascii=False)
