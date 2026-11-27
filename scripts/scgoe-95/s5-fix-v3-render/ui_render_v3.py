"""Builder Preview rendering check for payload v3 + Option A. A real Live Test turn runs on the deployed draft agent; in this
browser only, the reply text in the /messages response is replaced with a REAL v3 template reply (from the template tests,
generated with the template's own model). The Builder's own renderer draws it. Nothing is saved, committed, published or
activated, and nothing changes in the org. Synthetic values only."""
import json, os, re, subprocess, sys
from playwright.sync_api import sync_playwright
EXE = '/tmp/build-52db6c0d-57e1-4383-bac3-df377a70eecc/work/pwbrowsers/chromium_headless_shell-1255/chrome-headless-shell-linux64/chrome-headless-shell'
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = HERE + '/../../..'
T = HERE + '/../s5-fix-v3-template-tests/'
cases = json.load(open(T + 'payloads.json')); results = json.load(open(T + 'results.json'))
FIX = {}
for key, case in (('R1_single_hostile', '03_single_hostile_special'), ('R2_field_account', '22_field_account_special'),
                  ('R3_list_link_html_md', '27_list_link_html_markdown'), ('R4_single_entities', '28_single_entities_image'),
                  ('R5_list_override', '20_list_hostile_rows')):
    FIX[key] = {'payload': cases[case]['payload'], 'reply': results[case][0]['text']}
r18 = json.load(open(HERE + '/render-case-18.json')); FIX['R6_table_18_values'] = {'payload': r18['payload'], 'reply': r18['reply']}
names = sys.argv[1:] or list(FIX)
FIND = """(marker) => { let best=null; const walk=(r)=>{ r.querySelectorAll('*').forEach(e=>{ if(e.shadowRoot) walk(e.shadowRoot);
  const t=e.textContent||''; if(t.includes(marker) && (!best || t.length < best.textContent.length)) {
    if (e.querySelector('table') || t.includes('Record:')) best=e; } }); }; walk(document);
  if(!best) return null; const bb=best.getBoundingClientRect(); const q=(s)=>Array.from(best.querySelectorAll(s));
  return {text: best.innerText, box:[bb.x,bb.y,bb.width,bb.height], links: q('a').map(a=>[a.innerText, a.getAttribute('href')]),
    imgs: q('img').map(i=>i.getAttribute('src')), scripts: q('script').length, iframes: q('iframe').length,
    bold: q('b,strong').map(e=>e.innerText), em: q('em,i').map(e=>e.innerText), code: q('code').map(e=>e.innerText),
    heads: q('h1,h2,h3,h4,h5,h6').map(e=>e.innerText), del: q('del,s').map(e=>e.innerText), rows: q('tr').length,
    cells: q('td').map(e=>e.innerText)}; }"""
KEYS = ('name', 'accountName', 'title', 'email', 'phone', 'mobilePhone', 'mailingAddress')
def check(fix, res):
    """Compares what the Builder drew with the ORIGINAL values (line breaks as spaces)."""
    norm = lambda s: re.sub(r'\s+', ' ', s).strip()
    shown = norm(res.get('text', '')); rows = fix['payload']['contacts']; out = {}
    exact, missing = 0, []
    for r in rows:
        for k in KEYS:
            if k in r and r[k] and (k != 'mailingAddress' or 'Mailing address' in fix['reply']):
                if norm(r[k]) in shown: exact += 1
                else: missing.append('row %s %s: %r' % (r['n'], k, r[k]))
    paths = {r['contactPath'] for r in rows}
    links = res.get('links', [])
    record = [l for l in links if l[0].strip() == 'Open record']
    other = [l for l in links if l[0].strip() != 'Open record']
    out.update(values_exact=exact, values_not_exact=missing, open_record_links=len(record), contacts=len(rows),
               open_record_targets_ok=all(l[1] in paths for l in record) and {l[1] for l in record} == paths,
               other_links=other, misleading_links=[l for l in other if l[0].strip() != (l[1] or '').replace('mailto:', '').strip()
                                                    and not (l[1] or '').endswith(l[0].strip())],
               html_applied=bool(res.get('bold') and any('LLC' in b or 'Bold' in b for b in res['bold'])) or bool(res.get('imgs')) or
                            bool(res.get('scripts')) or bool(res.get('em')) or bool(res.get('code')) or bool(res.get('heads')) or bool(res.get('del')),
               imgs=res.get('imgs'), scripts=res.get('scripts'), iframes=res.get('iframes'))
    return out
out = {}
with sync_playwright() as p:
    b = p.chromium.launch(executable_path=EXE)
    for name in names:
        fix = FIX[name]
        subprocess.run('sf org open agent --authoring-bundle Contact_Read_Agent -r -o orgfarm-232477b490-dev-ed --json 2>/dev/null > %s/.u.json' % HERE, shell=True, cwd=REPO)
        url = json.load(open(HERE + '/.u.json'))['result']['url']; os.remove(HERE + '/.u.json')
        ctx = b.new_context(viewport={'width': 1900, 'height': 1800}); pg = ctx.new_page(); dialogs = []; reqs = []
        pg.on('dialog', lambda d: (dialogs.append(d.message), d.dismiss()))
        pg.on('request', lambda r: reqs.append(r.url) if 'evil.example' in r.url else None)
        def handler(route, request=None, reply=fix['reply']):
            if route.request.method != 'POST': return route.continue_()
            r = route.fetch(); body = r.json()
            for m in body.get('messages', []):
                if 'message' in m: m['message'] = reply
            route.fulfill(response=r, body=json.dumps(body))
        ctx.route('**/einstein/ai-agent/**/preview/sessions/*/messages', handler)
        pg.goto(url, wait_until='domcontentloaded', timeout=120000); pg.wait_for_timeout(30000)
        pg.locator("a:has-text('Preview')").first.click(timeout=60000); pg.wait_for_timeout(12000)
        pg.locator("text=Live Test").first.click(timeout=15000); pg.wait_for_timeout(3000)
        pg.locator("text=Live Test Mode").first.click(timeout=15000); pg.wait_for_timeout(8000)
        box = pg.locator("[contenteditable=true][role=textbox]").first
        box.click(); box.type('Hello', delay=20); pg.wait_for_timeout(1000); pg.keyboard.press('Enter'); pg.wait_for_timeout(40000)
        res = pg.evaluate(FIND, fix['reply'].splitlines()[0][:30])
        if res:
            x, y, w, h = res['box']
            pg.screenshot(path=HERE + '/shots/%s.png' % name, clip={'x': max(0, x - 10), 'y': max(0, y - 10), 'width': min(w + 20, 1400), 'height': min(h + 20, 1700)})
        res = res or {}; res['dialogs'] = dialogs; res['evil_requests'] = sorted(set(reqs)); res['check'] = check(fix, res) if res.get('text') else None
        out[name] = res
        c = res['check'] or {}
        print('==', name, 'found' if res.get('text') else 'NOT FOUND', '| dialogs', dialogs, '| evil requests', res['evil_requests'])
        print('   values exact %s, not exact %s | Open record %s/%s targets ok %s | other links %s | misleading %s | html applied %s'
              % (c.get('values_exact'), c.get('values_not_exact'), c.get('open_record_links'), c.get('contacts'), c.get('open_record_targets_ok'),
                 c.get('other_links'), c.get('misleading_links'), c.get('html_applied')), flush=True)
        ctx.close()
    b.close()
prev = json.load(open(HERE + '/render.json')) if os.path.exists(HERE + '/render.json') else {}
prev.update(out); json.dump(prev, open(HERE + '/render.json', 'w'), indent=1, ensure_ascii=False)
