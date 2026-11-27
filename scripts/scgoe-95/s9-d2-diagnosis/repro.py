"""SCGOE-95 Session 9 (D-2): repeat one utterance N times on a target and classify how the planner
called set_criteria/run_search and what search_contacts received. Read-only.
usage: repro.py <label> <cwd> <bundle-sim|bundle-live|published> <n> <utterance>"""
import json, subprocess, sys, os, glob
from concurrent.futures import ThreadPoolExecutor
OUT = os.path.dirname(os.path.abspath(__file__)) + '/'
ORG = 'orgfarm-232477b490-dev-ed'; B = 'Contact_Read_Agent'
label, cwd, mode, n, utt = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]), sys.argv[5]
tgt = ['--authoring-bundle', B] if mode.startswith('bundle') else ['--api-name', B]
def sf(args):
    p = subprocess.run(['sf'] + args + ['-o', ORG, '--json'], cwd=cwd, capture_output=True, text=True, timeout=400)
    raw = p.stdout.strip()
    try: return json.loads(raw[raw.index('{'):])
    except Exception: return {'status': 99, 'raw': (raw or p.stderr)[-500:]}
CRIT = ('name','email','phone','accountName','jobTitle','city','stateOrRegion','country')
def one(k):
    st = sf(['agent','preview','start'] + tgt + (['--simulate-actions'] if mode == 'bundle-sim' else ['--use-live-actions'] if mode == 'bundle-live' else []))
    sid = (st.get('result') or {}).get('sessionId')
    if not sid: return {'run': k, 'error': st}
    sf(['agent','preview','send'] + tgt + ['--session-id', sid, '-u', utt])
    e = sf(['agent','preview','end'] + tgt + ['--session-id', sid])
    tp = (e.get('result') or {}).get('tracesPath'); rec = {'run': k, 'session': sid, 'llm_calls': [], 'search_input': None, 'criteria_update_step': None, 'search_step': None}
    for f in glob.glob((tp or '') + '/traces/*.json'):
        plan = json.load(open(f))['plan']
        for i, s in enumerate(plan):
            if s['type'] == 'LLMStep':
                try: r = json.loads(s['data']['prompt_response'])
                except Exception: continue
                rec['llm_calls'].append([(t['function']['name'], t['function']['arguments']) for t in (r.get('tool_invocations') or [])])
            if s['type'] == 'VariableUpdateStep' and rec['criteria_update_step'] is None and any(u['variable_name'].startswith('criteria_') for u in s['data']['variable_updates']):
                rec['criteria_update_step'] = i
            if s['type'] == 'FunctionStep' and s['function']['name'] == 'search_contacts' and rec['search_input'] is None:
                rec['search_input'] = s['function'].get('input'); rec['search_step'] = i
    calls = [c for c in rec['llm_calls'] if any(x[0] == 'set_criteria' for x in c)]
    rec['parallel'] = any(any(x[0] == 'run_search' for x in c) for c in calls)
    rec['criteria_sent'] = {k2: v for k2, v in (rec['search_input'] or {}).items() if k2 in CRIT and v}
    rec['lost'] = rec['search_input'] is not None and not rec['criteria_sent']
    return rec
with ThreadPoolExecutor(3) as ex: res = list(ex.map(one, range(n)))
json.dump({'label': label, 'mode': mode, 'utterance': utt, 'runs': res}, open(OUT + f'{label}.json', 'w'), indent=1, ensure_ascii=False)
par = sum(r.get('parallel', False) for r in res); lost = sum(r.get('lost', False) for r in res)
lostpar = sum(r.get('lost', False) and r.get('parallel', False) for r in res); err = sum('error' in r for r in res)
print(f"{label}: runs={n} errors={err} parallel={par} lost={lost} lost&parallel={lostpar} separate&ok={sum((not r.get('parallel',True)) and not r.get('lost',True) for r in res)}")
