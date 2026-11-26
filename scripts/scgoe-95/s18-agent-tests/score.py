# S18 scorer for CRA_S18_Agent_Tests run through the evaluation API (real multi-turn sessions).
# Pass = topic contains expectedTopic AND the actions run in the tested turn match expectedActions
# (none when [] is expected) AND the service's reply rating passed. A platform fallback reply
# ("Live Chat support is currently unavailable") is counted as INFRA, not as a test result.
import json,sys,yaml
spec=yaml.safe_load(open(sys.argv[1])); d=json.load(open(sys.argv[2]))
FALLBACK='Live Chat support is currently unavailable'
def names(ia):
    out=[]
    for g in ia:
        for a in (g if isinstance(g,list) else [g]):
            n=(a.get('function') or {}).get('name') if isinstance(a,dict) else None
            if n: out.append(n)
    return out
rows=[];tally={'PASS':0,'FAIL':0,'INFRA':0}
for t in d['results']:
    i=int(t['id'].rsplit('_',1)[1]); c=spec['testCases'][i]
    o={x['id']:x for x in t['outputs']}
    replies=' '.join(x.get('response','') for x in t['outputs'] if x['type']=='agent.send_message')
    if FALLBACK in replies or t.get('errors'):
        st='INFRA'; why='platform fallback reply or error'
    else:
        le=o['gs']['response']['planner_response']['lastExecution']
        topic=le.get('topic'); acts=names(le.get('invokedActions',[]))
        ev={e['id']:e for e in t.get('evaluation_results',[])}
        exp=c.get('expectedActions') or []; asserted='expectedActions' in c
        okt=c['expectedTopic'] in (topic or '')
        oka=True if not asserted else ((not acts) if not exp else all(a in acts for a in exp))
        oko=ev.get('check_outcome',{}).get('is_pass')
        st='PASS' if (okt and oka and oko) else 'FAIL'
        why=f"topic={topic}{'' if okt else ' (exp '+c['expectedTopic']+')'} actions={acts}{'' if oka else ' (exp '+str(exp)+')'} outcome={'pass' if oko else 'FAIL'}"
    tally[st]+=1; rows.append((i+1,st,why,o.get('sm',{}).get('response','')[:160].replace('\n',' ')))
for r in sorted(rows): print(f"{r[0]:>2} {r[1]:5} {r[2]}" + ('' if r[1]=='PASS' else f"\n      reply: {r[3]}"))
print(tally)
json.dump({'tally':tally,'rows':sorted(rows)},open(sys.argv[2].replace('.json','-score.json'),'w'),indent=1,ensure_ascii=False)
