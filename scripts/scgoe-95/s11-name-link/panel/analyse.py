import json, sys, re
D=json.load(open('s11/fixtures.json')); NAMES=D['names']; R=json.load(open(sys.argv[1]))
P=lambda k:'/lightning/r/Contact/003SYN0000000%02dAAA/view'%k
norm=lambda s:re.sub(r'\s+',' ',s or '').strip()
summary={}
for name,r in R.items():
    links=[l for l in r['links'] if l['h'] and 'helpful' not in (l['t'] or '')]
    print('=====',name,'evil requests',len(r['evil_requests']),'dialogs',r['dialogs'])
    ok=0; per=[]
    for k,n in enumerate(NAMES,1):
        mine=[l for l in links if l['h']==P(k)]
        good=len(mine)==1 and norm(mine[0]['t'])==norm(n)
        ok+=good
        per.append((k,good,[norm(l['t']) for l in mine]))
    foreign=[l for l in links if not re.match(r'^/lightning/r/Contact/003SYN',l['h'] or '')]
    for k,g,t in per:
        if not g: print('  FAIL %2d %-60r -> record link text %r'%(k,NAMES[k-1],t))
    print('  correct name links %d/%d'%(ok,len(NAMES)))
    for l in foreign: print('  OTHER LINK text=%r href=%r'%(norm(l['t']),l['h']))
    print('  imgs',r['imgs'],' fmt',[f for f in r['fmt'] if 'helpful' not in f and not f.startswith('STRONG:Name') and not f.startswith('STRONG:Account')])
    if r['rows']: print('  table rows',len(r['rows']),'cells per row',sorted(set(len(x) for x in r['rows'])))
    summary[name]={'correct':ok,'of':len(NAMES),'other_links':foreign,'imgs':r['imgs'],'failures':[(k,NAMES[k-1],t) for k,g,t in per if not g]}
json.dump(summary,open(sys.argv[1].replace('.json','-summary.json'),'w'),indent=1,ensure_ascii=False)
