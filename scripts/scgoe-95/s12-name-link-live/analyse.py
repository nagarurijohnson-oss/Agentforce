import json, re, sys
F=json.load(open('s12/fixtures-deployed.json')); P=json.load(open('Agentforce/scripts/scgoe-95/s11-name-link/payloads.json')); R=json.load(open('s12/render-deployed.json'))
norm=lambda s:re.sub(r'\s+',' ',s or '').strip()
LABELS={'Name:','Account:','Title:','Email:','Phone:','Mobile:','Mailing address:'}
out={}; prev_evil=0
for k,r in R.items():
    case=k.split('-',1)[1].replace('_fail','')
    rows=P[case]['payload']['contacts']; paths={x['contactPath']:x for x in rows}
    links=[l for l in r['links'] if l['h'] and 'helpful' not in (l['t'] or '')]
    rec=[l for l in links if l['h'] in paths]; other=[l for l in links if l['h'] not in paths]
    issues=[]
    for x in rows:
        mine=[norm(l['t']) for l in rec if l['h']==x['contactPath']]
        want = norm(x['name']) if x['nameLinkable'] else 'Open record'
        if mine!=[want]: issues.append('row %d record link %r, expected [%r]'%(x['n'],mine,want))
        if not x['nameLinkable'] and norm(x['name']) not in norm(r['text']): issues.append('row %d name not shown exactly'%x['n'])
    disguised=[(norm(l['t']),l['h']) for l in other if not (norm(l['t']).rstrip('\\>') in l['h'] or l['h']=='mailto:'+norm(l['t']) or 'http://'+norm(l['t'])==l['h'])]
    auto=[(norm(l['t']),l['h']) for l in other if (norm(l['t']),l['h']) not in disguised]
    fmt=[f for f in r['fmt'] if 'helpful' not in f and not (f.startswith('STRONG:') and f[7:] in LABELS)]
    evil=len(r['evil_requests'])-prev_evil; prev_evil=len(r['evil_requests'])
    hdr=[c for c in (r['rows'][0] if r['rows'] else [])]
    out[k]={'record_link_issues':issues,'disguised_links':disguised,'autolinks':auto,'images':r['imgs'],'formatting':fmt,'new_evil_requests':evil,'header':hdr,'dialogs':r['dialogs']}
    flag='OK ' if not (issues or disguised or r['imgs'] or fmt or evil) else 'BAD'
    print(flag,'%-42s rows %d rec-links %d autolinks %d disguised %s imgs %s fmt %s evil %d hdr %s'%(k,len(rows),len(rec),len(auto),disguised,r['imgs'],fmt,evil,hdr))
    for i in issues: print('      ',i)
json.dump(out,open('s12/render-deployed-summary.json','w'),indent=1,ensure_ascii=False)
