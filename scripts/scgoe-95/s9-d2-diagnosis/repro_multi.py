"""SCGOE-95 Session 9 (D-2): multi-turn variant. For every turn, records the planner call pattern
around set_criteria and the criteria search_contacts actually received. Read-only.
usage: repro_multi.py <label> <cwd> <bundle-sim|bundle-live|published> <n> <turn1> [<turn2> ...]"""
import json, subprocess, sys, os, glob
from concurrent.futures import ThreadPoolExecutor
OUT = os.path.dirname(os.path.abspath(__file__)) + '/'
ORG = 'orgfarm-232477b490-dev-ed'; B = 'Contact_Read_Agent'
label, cwd, mode, n, turns = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]), sys.argv[5:]
tgt = ['--authoring-bundle', B] if mode.startswith('bundle') else ['--api-name', B]
extra = ['--simulate-actions'] if mode == 'bundle-sim' else ['--use-live-actions'] if mode == 'bundle-live' else []
CRIT = ('name','email','phone','accountName','jobTitle','city','stateOrRegion','country')
def sf(args):
    p = subprocess.run(['sf'] + args + ['-o', ORG, '--json'], cwd=cwd, capture_output=True, text=True, timeout=400)
    raw = p.stdout.strip()
    try: return json.loads(raw[raw.index('{'):])
    except Exception: return {'status': 99, 'raw': (raw or p.stderr)[-500:]}
def one(k):
    st = sf(['agent','preview','start'] + tgt + extra); sid = (st.get('result') or {}).get('sessionId')
    if not sid: return {'run': k, 'error': st}
    for u in turns: sf(['agent','preview','send'] + tgt + ['--session-id', sid, '-u', u])
    e = sf(['agent','preview','end'] + tgt + ['--session-id', sid]); tp = (e.get('result') or {}).get('tracesPath')
    out = {'run': k, 'session': sid, 'turns': []}
    for f in sorted(glob.glob((tp or '') + '/traces/*.json'), key=os.path.getmtime):
        plan = json.load(open(f))['plan']; t = {'user': next((s.get('message') for s in plan if s['type']=='UserInputStep'), ''), 'calls': [], 'search_inputs': [], 'outcomes': []}
        for s in plan:
            if s['type'] == 'LLMStep':
                try: r = json.loads(s['data']['prompt_response'])
                except Exception: continue
                c = [(x['function']['name'], x['function']['arguments']) for x in (r.get('tool_invocations') or [])]
                if c: t['calls'].append(c)
            if s['type'] == 'FunctionStep' and s['function']['name'] == 'search_contacts':
                t['search_inputs'].append({a: v for a, v in (s['function'].get('input') or {}).items() if a in CRIT and v})
                t['outcomes'].append(((s['function'].get('output') or {}).get('outcomeCode'), (s['function'].get('output') or {}).get('totalMatchesLabel')))
        t['parallel'] = any(any(x[0]=='set_criteria' for x in c) and any(x[0]=='run_search' for x in c) for c in t['calls'])
        out['turns'].append(t)
    return out
with ThreadPoolExecutor(3) as ex: res = list(ex.map(one, range(n)))
json.dump({'label': label, 'mode': mode, 'turns': turns, 'runs': res}, open(OUT + f'{label}.json', 'w'), indent=1, ensure_ascii=False)
for r in res:
    if 'error' in r: print(label, r['run'], 'ERROR'); continue
    print(label, r['run'], ' || '.join(f"{'PAR' if t['parallel'] else 'sep'} sent={t['search_inputs']} out={t['outcomes']}" for t in r['turns']))
