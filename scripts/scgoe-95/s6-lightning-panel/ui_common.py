import json, subprocess, os, time
os.environ.setdefault('PLAYWRIGHT_BROWSERS_PATH', '/tmp/agentforce_build-50144f18-a53e-4e8e-9955-a43b7975a4d2/work/pwbrowsers')
EXE = '/tmp/agentforce_build-50144f18-a53e-4e8e-9955-a43b7975a4d2/work/pwbrowsers/chromium_headless_shell-1255/chrome-headless-shell-linux64/chrome-headless-shell'
def front(path):
    r = subprocess.run(['sf','org','open','--url-only','--path',path,'-o','orgfarm-232477b490-dev-ed','--json'], capture_output=True, text=True)
    return json.loads(r.stdout)['result']['url']
def deep_text(pg):
    return pg.evaluate("""() => { let out=[]; const walk=(r)=>{ r.querySelectorAll('*').forEach(e=>{ if(e.shadowRoot) walk(e.shadowRoot); }); }; return document.body.innerText; }""")
