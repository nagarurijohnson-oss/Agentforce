import json,glob,os,collections
rows=[]
for f in glob.glob('**/.sfdx/agents/*/sessions/*/traces/*.json',recursive=True):
    try: d=json.load(open(f))
    except Exception: continue
    sess=f.split('/sessions/')[1].split('/')[0]
    agentdir=f.split('/.sfdx/agents/')[1].split('/')[0]
    plan=d.get('plan',[]); msg=next((s.get('message') for s in plan if s['type']=='UserInputStep'),'')
    for i,st in enumerate(plan):
        if st['type']!='LLMStep': continue
        try: r=json.loads(st['data']['prompt_response'])
        except Exception: continue
        names=[t['function']['name'] for t in (r.get('tool_invocations') or [])]
        if 'set_criteria' in names:
            args=[t['function']['arguments'] for t in r['tool_invocations'] if t['function']['name']=='set_criteria'][0]
            # was criteria variable updated after this step, before next FunctionStep?
            applied=False; fn_in=None
            for s2 in plan[i+1:]:
                if s2['type']=='VariableUpdateStep' and any(u['variable_name'].startswith('criteria_') for u in s2['data']['variable_updates']): applied=True
                if s2['type']=='FunctionStep' and s2['function']['name']=='search_contacts': fn_in=s2['function'].get('input'); break
                if s2['type']=='LLMStep' and fn_in is None and not applied: pass
            crit={k:v for k,v in (fn_in or {}).items() if k in('name','email','phone','accountName','jobTitle','city','stateOrRegion','country') and v}
            rows.append((agentdir,sess[:13],os.path.getmtime(f),msg[:60],'+'.join(names),applied,json.dumps(crit,ensure_ascii=False)[:80]))
rows.sort(key=lambda r:r[2])
c=collections.Counter()
for r in rows:
    par='PARALLEL' if 'run_search' in r[4] else 'separate'
    lost = (r[6]=='{}')
    c[(par,r[5],lost)]+=1
    print(r[0][-6:],r[1],par,'applied='+str(r[5]),'search_criteria='+r[6],'|',r[3])
print(c)
