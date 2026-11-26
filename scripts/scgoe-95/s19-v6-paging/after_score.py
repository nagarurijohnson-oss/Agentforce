import json,sys
d=json.load(open(sys.argv[1]))
for t in sorted(d['results'],key=lambda x:x['id']):
  o={x['id']:x for x in t['outputs']}
  le=o['g1']['response']['planner_response']['lastExecution']
  for g in le['invokedActions']:
    for a in (g if isinstance(g,list) else [g]):
      if a['function']['name']=='search_contacts': print(t['id'],le.get('topic'),{k:v for k,v in a['function']['input'].items() if v})
  print('    ',o['t1']['response'][:120].replace('\n',' '))
