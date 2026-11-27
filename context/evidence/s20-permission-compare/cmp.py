"""Compare baseline (B, no Prompt Template User) vs grant (G) runs: per session id, invoked actions (output present?), errors, reply."""
import json,re,sys
def rows(f):
    d=json.load(open(f)); out={}
    for r in d['results']:
        sid=None; turns=[]
        for x in r.get('outputs',[]):
            if x.get('type')=='agent.create_session': sid=x.get('session_id')
            if x.get('type')=='agent.send_message': turns.append({'reply':x.get('response')})
            if x.get('type')=='agent.get_state':
                le=((x.get('response') or {}).get('planner_response') or {}).get('lastExecution') or {}
                acts=[]
                for grp in le.get('invokedActions') or []:
                    for a in grp:
                        fn=a.get('function',{}); o=fn.get('output')
                        acts.append(f"{fn.get('name')}[{'out' if o not in (None,'',{}) else 'NULL'}]")
                if turns: turns[-1]['acts']=acts; turns[-1]['errors']=le.get('errors')
        out[r['id']]={'sid':sid,'turns':turns,'err':r.get('errors')}
    return out
def links(t): return sorted(set(re.findall(r'/(003\w{12,15}|ka0\w{12,15})',t or '')))
if __name__=='__main__':
    B=rows(sys.argv[1]); G=rows(sys.argv[2])
    for k in B:
        b,g=B[k],G.get(k,{'turns':[],'sid':None})
        print(f"== {k}\n  B sid {b['sid']}  G sid {g['sid']}")
        for i,(tb,tg) in enumerate(zip(b['turns'],g['turns'])):
            print(f"  t{i} B acts {tb.get('acts')} links {links(tb['reply'])}\n     G acts {tg.get('acts')} links {links(tg['reply'])} errs {tg.get('errors')}")
            print(f"     B reply: {(tb['reply'] or '')[:160]!r}\n     G reply: {(tg['reply'] or '')[:160]!r}")
