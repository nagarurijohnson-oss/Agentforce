import json,re,sys
d=json.load(open(sys.argv[1]))
for t in sorted(d['results'],key=lambda x:x['id']):
  o={x['id']:x for x in t['outputs']}
  if t.get('errors'): print(t['id'],'ERR',t['errors']); continue
  def tools(g):
    le=o[g]['response']['planner_response']['lastExecution']; evs=[e for grp in le['llmEvents'] for e in grp]
    offered=set(); called=[]
    for e in evs:
      pc=e['prompt_content']; offered|=set(re.findall(r'"name":\s*"([a-z_]+)"',pc))
      pr=json.loads(e['prompt_response']) if isinstance(e['prompt_response'],str) else e['prompt_response']
      for ti in (pr.get('tool_invocations') or []): called.append(ti['function']['name'])
    return le['invokedActions'],called,offered
  r2=o['t2']['response']; links=re.findall(r'\[(Eng Mockup0\d)\]\(/lightning/r/Contact/(\w+)/view\)',r2)
  ia,called,off=tools('g2')
  print(t['id'],'| t1 links',len(re.findall(r'\]\(/lightning/r/Contact/',o['t1']['response'])),'| t2 linked rows',[n for n,_ in links],
        '| t2 planner calls',called,'| show_remaining offered' ,'show_remaining' in off,'| invokedActions',len(ia))
  if not links: print('    t2 reply:',r2[:160].replace('\n',' '))
