"""Drives the Agentforce Builder Preview (deployed draft, Live Test Mode) headlessly and screenshots each reply.
Never clicks Save, Commit Version, New Version or any publish/activate control."""
import json, time, sys, subprocess
from playwright.sync_api import sync_playwright
convo = json.loads(sys.argv[1]); tag = sys.argv[2]
subprocess.run('cd ../Agentforce && sf org open agent --authoring-bundle Contact_Read_Agent -r -o orgfarm-232477b490-dev-ed --json 2>/dev/null > ../s5/.builder-url.json', shell=True)
url = json.load(open('.builder-url.json'))['result']['url']
log = []
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_context(viewport={'width': 1700, 'height': 1250}).new_page()
    pg.goto(url, wait_until='domcontentloaded', timeout=120000); time.sleep(30)
    pg.locator("a:has-text('Preview')").first.click(timeout=60000); time.sleep(12)
    pg.locator("text=Live Test").first.click(timeout=15000); time.sleep(3)
    pg.locator("text=Live Test Mode").first.click(timeout=15000); time.sleep(8)
    for n, msg in enumerate(convo, 1):
        box = pg.locator("[contenteditable=true][role=textbox]").first
        box.click(); box.type(msg, delay=20); time.sleep(1); pg.keyboard.press('Enter')
        before = pg.evaluate("() => document.body.innerText")
        for w in range(30):
            time.sleep(4)
            t = pg.evaluate("() => document.body.innerText")
            if 'Thinking' not in t and 'Working' not in t and w > 4: break
        time.sleep(4)
        pg.screenshot(path='shots/%s-%02d-full.png' % (tag, n))
        pg.screenshot(path='shots/%s-%02d-chat.png' % (tag, n), clip={'x': 320, 'y': 120, 'width': 420, 'height': 1110})
        t = pg.evaluate("() => document.body.innerText"); i = t.find('Reset Simulator'); j = t.find('Agent Preview Details')
        fmt = pg.evaluate("""() => { const out={a:[],strong:0,table:0,th:0,b:0}; const walk=(r)=>{ r.querySelectorAll('a,strong,b,table,th').forEach(e=>{ const bb=e.getBoundingClientRect(); if(bb.x>300 && bb.x<760 && bb.width>0){ const tg=e.tagName.toLowerCase(); if(tg==='a') out.a.push([e.innerText.slice(0,40), (e.getAttribute('href')||'').slice(0,120)]); else out[tg]++; } }); r.querySelectorAll('*').forEach(e=>{if(e.shadowRoot) walk(e.shadowRoot)}); }; walk(document); return out; }""")
        log.append({'user': msg, 'panel_text': t[i:j], 'rendered': fmt}); print('RENDERED:', json.dumps(fmt, ensure_ascii=False)[:900])
        print('--- %s %d' % (tag, n)); print(t[i:j][-1800:])
    b.close()
json.dump(log, open('shots/%s-ui.json' % tag, 'w'), indent=1, ensure_ascii=False)
