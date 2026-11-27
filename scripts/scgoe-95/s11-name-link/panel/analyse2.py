import json, sys, re
D=json.load(open('s11/fixtures2.json')); NAMES=D['names']; LK=D['linkable']; R=json.load(open(sys.argv[1]))
P=lambda k:'/lightning/r/Contact/003SYN0000000%02dAAA/view'%k
norm=lambda s:re.sub(r'\s+',' ',s or '').strip()
summary={}
for name,r in R.items():
    links=[l for l in r['links'] if l['h'] and 'helpful' not in (l['t'] or '')]
    guarded = name.startswith('G')
    ok=0; fails=[]
    for k,n in enumerate(NAMES,1):
        mine=[norm(l['t']) for l in links if l['h']==P(k)]
        want = norm(n) if (guarded and LK[k-1]) else 'Open record'
        g = mine==[want]; ok+=g
        if not g: fails.append((k,n,mine))
    foreign=[(norm(l['t']),l['h']) for l in links if not re.match(r'^/lightning/r/Contact/003SYN',l['h'] or '')]
    # visible name text exact? (escaped only) -> name text should appear in rendered text
    txt=norm(r['text']); vis=sum(1 for n in NAMES if norm(n) in txt)
    print('=====',name,'record links correct %d/%d'%(ok,len(NAMES)),'| names shown exactly %d/%d'%(vis,len(NAMES)),'| evil requests',len(r['evil_requests']),'| imgs',r['imgs'])
    for f in fails: print('   FAIL',f)
    for f in foreign: print('   OTHER LINK',f)
    if r['rows']: print('   rows',len(r['rows']),'cells',sorted(set(len(x) for x in r['rows'])))
    summary[name]={'record_links_correct':ok,'names_exact':vis,'of':len(NAMES),'other_links':foreign,'imgs':r['imgs'],'fails':fails}
json.dump(summary,open(sys.argv[1].replace('.json','-summary.json'),'w'),indent=1,ensure_ascii=False)
