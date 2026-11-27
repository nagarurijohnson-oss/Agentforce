"""S23 Phase A scorer (read-only). usage: score.py <uat_results.json> [<admin_v7_results.json>] -> <uat>-score.json
Per turn: session id, topic, invoked actions (output present?), contact_failed/kb_failed, fixed failure messages,
platform generic error (D-8b marker), Contact links, cited articles, emails/phones; compared with the admin v7 run."""
import json,re,sys,os,subprocess
sys.path.insert(0,os.path.dirname(__file__)+'/../s22'); from d8score import var,CF1,CF2,KF
E={**os.environ,'SF_DISABLE_LOG_FILE':'true','SF_SKIP_NEW_VERSION_CHECK':'true'}; O='orgfarm-232477b490-dev-ed'; U='005jV000003sYUPQA2'
GEN=re.compile(r'unexpected error',re.I); LINK=re.compile(r'/(003\w{15})'); KA=re.compile(r'(ka0\w{15})'); AN=re.compile(r'\b(0000010\d\d)\b')
EMAIL=re.compile(r'[\w.+-]+@[\w-]+\.[\w.]+'); HIDDEN={'003jV00000HCVpSQAX':'Zed Hiddenmore','003jV00000HCVpTQAX':'Jordan Samename (c)'}
HIDDEN_TXT=re.compile(r'hiddenmore|samename\.c@',re.I); CAMPUS_KA={'ka0jV000000nIFCQA2','ka0jV000000nIFBQA2'}; CAMPUS_AN={'000001007','000001013'}
ONLINE_KA={'ka0jV000000nIDWQA2','ka0jV000000nIDbQAM','ka0jV000000nIDaQAM','ka0jV000000nIDVQA2','ka0jV000000nIDXQA2','ka0jV000000nIDZQA2','ka0jV000000nIDYQA2','ka0jV000000nIFCQA2','ka0jV000000nIFAQA2','ka0jV000000nIF9QAM','ka0jV000000nIqDQAU','ka0jV000000nIF8QAM','ka0jV000000nIFBQA2'}
def turns(r):
    sid=None; T=[]
    for x in r.get('outputs',[]):
        if x.get('type')=='agent.create_session': sid=x.get('session_id')
        if x.get('type')=='agent.send_message': T.append({'reply':x.get('response') or ''})
        if x.get('type')=='agent.get_state' and T:
            pr=(x.get('response') or {}).get('planner_response') or {}; le=pr.get('lastExecution') or {}
            T[-1]['topic']=le.get('topic')
            T[-1]['acts']=[f"{a.get('function',{}).get('name')}[{'out' if a.get('function',{}).get('output') not in (None,'',{}) else 'NULL'}]" for g in le.get('invokedActions') or [] for a in (g if isinstance(g,list) else [g]) if isinstance(a,dict)]
            T[-1]['cf']=var(pr,'contact_failed'); T[-1]['kf']=var(pr,'kb_failed'); T[-1]['err']=le.get('errors')
    return sid,T,r.get('errors')
def feats(t):
    rep=t['reply']; return {'links':sorted(set(LINK.findall(rep))),'ka':sorted(set(KA.findall(rep))),'an':sorted(set(AN.findall(rep))),'emails':sorted(set(EMAIL.findall(rep))),
      'fixed':[n for n,s in (('CF1',CF1),('CF2',CF2),('KF',KF)) if s in rep],'generic_error':bool(GEN.search(rep)),'hidden_text':bool(HIDDEN_TXT.search(rep))}
def load(f):
    if not f or not os.path.exists(f): return {}
    return {r['id']:turns(r) for r in json.load(open(f))['results']}
def access(ids):
    if not ids: return {}
    s="','".join(ids); r=subprocess.run(['sf','data','query','-o',O,'--json','-q',f"SELECT RecordId,HasReadAccess FROM UserRecordAccess WHERE UserId='{U}' AND RecordId IN ('{s}')"],capture_output=True,text=True,env=E)
    return {x['RecordId']:x['HasReadAccess'] for x in json.loads(r.stdout)['result']['records']}
if __name__=='__main__':
    uat=load(sys.argv[1]); adm=load(sys.argv[2] if len(sys.argv)>2 else None); rows=[]
    for tid,(sid,T,errs) in uat.items():
        A=adm.get(tid,(None,[],None))[1]
        for i,t in enumerate(T):
            f=feats(t); a=A[i] if i<len(A) else None; fa=feats(a) if a else None
            rows.append({'id':tid,'turn':i,'sid':sid,'topic':t.get('topic'),'admin_topic':a.get('topic') if a else None,'acts':t.get('acts'),'admin_acts':a.get('acts') if a else None,
              'contact_failed':t.get('cf'),'kb_failed':t.get('kf'),'errors':t.get('err') or errs,**f,
              'admin_links':fa['links'] if fa else None,'admin_ka':fa['ka'] if fa else None,'admin_an':fa['an'] if fa else None,'reply':t['reply'],'admin_reply':(a['reply'][:600] if a else None)})
    acc=access(sorted({l for r in rows for l in r['links']}))
    for r in rows:
        fl=[]
        if r['fixed']: fl.append('FIXED_FAILURE_MSG '+','.join(r['fixed']))
        if r['generic_error']: fl.append('GENERIC_ERROR(D-8b)')
        if r['kb_failed'] or r['contact_failed']: fl.append(f"FLAG cf={r['contact_failed']} kf={r['kb_failed']}")
        if any('NULL' in a for a in r['acts'] or []): fl.append('NULL_ACTION_OUTPUT')
        bad=[l for l in r['links'] if not acc.get(l)]; 
        if bad: fl.append('LINK_NOT_READABLE '+','.join(bad))
        if set(r['links'])&set(HIDDEN) or r['hidden_text']: fl.append('HIDDEN_CONTACT')
        if set(r['ka'])&CAMPUS_KA or set(r['an'])&CAMPUS_AN: fl.append('CAMPUS_ARTICLE_CITED')
        if set(r['ka'])-ONLINE_KA: fl.append('UNKNOWN_ARTICLE '+','.join(set(r['ka'])-ONLINE_KA))
        if r['errors']: fl.append('ERRORS')
        diff=[]
        if r['admin_topic'] is not None and r['topic']!=r['admin_topic']: diff.append(f"topic {r['topic']} vs admin {r['admin_topic']}")
        if r['admin_ka'] is not None and r['ka']!=r['admin_ka']: diff.append(f"articles {r['ka']} vs admin {r['admin_ka']}")
        if r['admin_links'] is not None and r['links']!=r['admin_links']: diff.append(f"links {len(r['links'])} vs admin {len(r['admin_links'])}")
        r['flags']=fl; r['diff']=diff; r['link_access']={l:acc.get(l) for l in r['links']}
        print(f"{r['id']} t{r['turn']} sid={r['sid']} topic={r['topic']} acts={r['acts']} links={len(r['links'])} ka={r['ka']} an={r['an']} FLAGS={fl} DIFF={diff}\n    {r['reply'][:230]!r}")
    json.dump(rows,open(sys.argv[1].replace('.json','-score.json'),'w'),indent=1)
    print('TURNS',len(rows),'flagged',sum(1 for r in rows if r['flags']),'diff',sum(1 for r in rows if r['diff']))
