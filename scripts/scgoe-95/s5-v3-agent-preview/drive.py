"""SCGOE-95 Session 5: live conversation preview of the draft Contact_Read_Agent (local bundle, live actions).
Each scenario is its own preview session. Transcripts are saved to transcripts.json."""
import json, subprocess, sys, os, time
REPO = '/tmp/build-52db6c0d-57e1-4383-bac3-df377a70eecc/work/Agentforce'
OUT = os.path.dirname(os.path.abspath(__file__)) + '/'
ORG = 'orgfarm-232477b490-dev-ed'
B = 'Contact_Read_Agent'
def sf(args):
    p = subprocess.run(['sf'] + args + ['-o', ORG, '--json'], cwd=REPO, capture_output=True, text=True, timeout=400)
    raw = p.stdout.strip()
    try: return json.loads(raw[raw.index('{'):])
    except Exception: return {'status': 99, 'raw': (raw or p.stderr)[-800:]}
SCEN = json.load(open(OUT + 'scenarios.json'))
only = sys.argv[1:]
res = json.load(open(OUT + 'transcripts.json')) if os.path.exists(OUT + 'transcripts.json') else {}
for name, turns in SCEN.items():
    if only and name not in only: continue
    st = sf(['agent', 'preview', 'start', '--authoring-bundle', B, '--use-live-actions'])
    sid = (st.get('result') or {}).get('sessionId')
    conv = {'start': st.get('result') if sid else st, 'turns': []}
    if sid:
        for u in turns:
            r = sf(['agent', 'preview', 'send', '--authoring-bundle', B, '--session-id', sid, '-u', u])
            msgs = (r.get('result') or {}).get('messages') or []
            conv['turns'].append({'user': u, 'agent': [m.get('message') for m in msgs], 'raw': r if not msgs else None})
        e = sf(['agent', 'preview', 'end', '--authoring-bundle', B, '--session-id', sid])
        conv['end'] = e.get('result')
        tp = (e.get('result') or {}).get('tracesPath')
        if tp and os.path.isdir(tp + '/traces'):
            import glob
            tr = sorted(glob.glob(tp + '/traces/*.json'), key=os.path.getmtime)
            for t, f in zip(conv['turns'], tr):
                d = json.load(open(f)); t['actions'] = []; t['template_raw'] = None; t['agent_raw'] = None
                for st in d['plan']:
                    if st['type'] == 'FunctionStep':
                        fn = st['function']; out = fn.get('output') or {}
                        t['actions'].append({'name': fn['name'], 'input': {k: v for k, v in (fn.get('input') or {}).items() if v not in ('', None, False)} if fn['name'] == 'search_contacts' else None,
                                             'outcome': out.get('outcomeCode'), 'shown': out.get('shownCount'), 'total': out.get('totalMatchesLabel')})
                        if fn['name'] == 'present_results': t['template_raw'] = out.get('promptResponse')
                    if st['type'] == 'LLMStep':
                        try:
                            c = json.loads(st['data']['prompt_response']).get('content')
                            if c: t['agent_raw'] = c
                        except Exception: pass
    res[name] = conv
    json.dump(res, open(OUT + 'transcripts.json', 'w'), indent=1, ensure_ascii=False)
    print('==', name, 'session', sid, flush=True)
    for t in conv['turns']:
        print('USER:', t['user']); print('ACTIONS:', [(a['name'], a.get('outcome'), a.get('total'), a.get('input')) for a in t.get('actions', [])])
        print('AGENT RAW:', t.get('agent_raw')); print('VERBATIM:', (t.get('agent_raw') or '').strip() == (t.get('template_raw') or '').strip() if t.get('template_raw') else 'no template'); print('--')
