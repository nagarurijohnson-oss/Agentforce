"""SCGOE-95: one Builder Live Test turn on the deployed draft Contact_Read_Agent; record which display flags the
Builder channel reports. Saves request paths (no query strings, no headers, no cookies) and text snippets around
the flags. Never clicks Save, Commit Version, New Version, publish or activate."""
import json, time, re, os, subprocess, sys
from playwright.sync_api import sync_playwright
W='/tmp/build-52db6c0d-57e1-4383-bac3-df377a70eecc/work'; OUT=W+'/s5-delivery'
REPO=W+'/Agentforce'
u=subprocess.run(['sf','org','open','agent','--authoring-bundle','Contact_Read_Agent','-r','-o','orgfarm-232477b490-dev-ed','--json'],cwd=REPO,capture_output=True,text=True).stdout
url=json.loads(u[u.index('{'):])['result']['url']   # one-time sign-in link, kept in memory only
FLAGS=['__supports_result_display__','__render_rules_enabled__','__render_rule_end_turn_fired__','__show_tool_results_invoked__','__render_rule_end_turn__']
paths=[]; hits=[]; bodies_with_reply=[]
def on_resp(r):
    try:
        if r.request.resource_type not in ('xhr','fetch','eventsource','other'): return
        path=re.sub(r'\?.*$','',re.sub(r'^https://[^/]+','',r.url)); paths.append(path)
        t=r.text()
    except Exception: return
    for f in FLAGS:
        for m in re.finditer(re.escape(f)+r'.{0,40}', t):
            hits.append({'path':path,'flag':m.group(0)[:80]})
    if 'zed.obrien' in t or 'Open record' in t or 'O\'Brien' in t or 'Brien' in t:
        bodies_with_reply.append({'path':path,'len':len(t),'snippet':[t[max(0,m.start()-200):m.start()+700] for m in re.finditer(r'Brien',t)][:3]})
with sync_playwright() as p:
    b=p.chromium.launch(executable_path=W+'/pwbrowsers/chromium_headless_shell-1255/chrome-headless-shell-linux64/chrome-headless-shell')
    ctx=b.new_context(viewport={'width':1700,'height':1250}); ctx.on('response',on_resp); pg=ctx.new_page()
    pg.goto(url,wait_until='domcontentloaded',timeout=120000); time.sleep(35)
    pg.locator("a:has-text('Preview')").first.click(timeout=60000); time.sleep(12)
    pg.locator("text=Live Test").first.click(timeout=15000); time.sleep(3)
    pg.locator("text=Live Test Mode").first.click(timeout=15000); time.sleep(8)
    box=pg.locator("[contenteditable=true][role=textbox], textarea").first
    box.click(); box.type(sys.argv[1] if len(sys.argv)>1 else 'Find the Contact with the email zed.obrien@synthetic.example',delay=20); time.sleep(1); pg.keyboard.press('Enter')
    for w in range(30):
        time.sleep(4); t=pg.evaluate("() => document.body.innerText")
        if 'Thinking' not in t and 'Working' not in t and w>5: break
    time.sleep(6)
    pg.screenshot(path=OUT+'/builder-net-chat.png',clip={'x':320,'y':120,'width':430,'height':1110})
    t=pg.evaluate("() => document.body.innerText"); i=t.find('Reset Simulator'); j=t.find('Agent Preview Details')
    panel=t[i:j] if i>=0 else t[:3000]
    b.close()
json.dump({'paths':sorted(set(paths)),'flag_hits':hits,'reply_bodies':bodies_with_reply,'panel_text':panel},open(OUT+'/builder-net.json','w'),indent=1,ensure_ascii=False)
print('paths',len(set(paths)),'flag hits',len(hits),'reply bodies',len(bodies_with_reply))
for h in {(h['path'],h['flag']) for h in hits}: print(' ',h)
for x in bodies_with_reply: print(' BODY',x['path'],x['len'])
print('PANEL:',panel[:900])
