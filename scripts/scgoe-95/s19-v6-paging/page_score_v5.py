# S19: score v5 two-turn paging runs. Pass = turn 1 shows rows 01-05 and turn 2 shows rows 06-08,
# every row a link to the right Contact Id, and turn 2 ran search_contacts with showRemaining itself.
import json,re,sys
ids=json.load(open('eng_ids.json'))
tot=dict(runs=0,passed=0,invented=0,no_answer=0,errors=0)
for f in sys.argv[1:]:
  d=json.load(open(f))
  for t in sorted(d['results'],key=lambda x:x['id']):
    tot['runs']+=1
    if t.get('errors'): tot['errors']+=1; print(t['id'],'ERR',str(t['errors'])[:200]); continue
    o={x['id']:x for x in t['outputs']}
    def rows(txt): return re.findall(r'\[(Eng Mockup\d\d)\]\(/lightning/r/Contact/(\w+)/view\)',txt)
    r1=o['t1']['response']; r2=o['t2']['response']
    ok1=[n for n,i in rows(r1)]==['Eng Mockup0%d'%k for k in range(1,6)] and all(ids[n]==i[:15] for n,i in rows(r1))
    rr=rows(r2); names=[n for n,_ in rr]
    ok2=names==['Eng Mockup06','Eng Mockup07','Eng Mockup08'] and all(ids[n]==i[:15] for n,i in rr)
    le=o['g2']['response']['planner_response']['lastExecution']
    acts=json.dumps(le.get('invokedActions',[]))
    ran=('search_contacts' in acts or 'CRA_ContactSearchAction' in acts) and re.search(r'showRemaining\\?"?\s*:\s*true',acts,re.I) is not None
    called=[]
    for grp in le.get('llmEvents',[]):
      for e in grp:
        pr=e['prompt_response']; pr=json.loads(pr) if isinstance(pr,str) else pr
        called+= [ti['function']['name'] for ti in (pr.get('tool_invocations') or [])]
    mentions=set(re.findall(r'Eng Mockup0[678]',r2)); unlinked=mentions-set(names)
    invented=bool(mentions) and (not ran or bool(unlinked))
    tot['invented']+=invented; tot['no_answer']+= (not mentions and not ok2)
    p=ok1 and ok2 and ran and not invented; tot['passed']+=p
    print(t['id'],'PASS' if p else 'FAIL','| t1',ok1,'| t2 rows',names,'| ran showRemaining',ran,'| planner tools',called,'| invented',invented)
    if not p: print('    t2:',r2[:220].replace('\n',' '))
print('TOTAL',tot)
