import json,sys,html
def load(f):
    t=open(f).read(); return json.loads(t[t.index('{'):])['result']
def cases(r):
    out=[]
    for c in r['testCases']:
        res={x['name']:x['result'] for x in c.get('testResults',[])}
        g=c.get('generatedData',{})
        out.append((c['inputs']['utterance'],res,html.unescape(g.get('topic','')),html.unescape(g.get('actionsSequence','')),(g.get('generatedResponse') or '')[:110].replace('\n',' ')))
    return out
a=cases(load(sys.argv[1])); b=cases(load(sys.argv[2]))
pa=pb=0
for i,(x,y) in enumerate(zip(a,b),1):
    ok=lambda r: all(v=='PASS' for v in r.values())
    pa+=ok(x[1]); pb+=ok(y[1])
    fl=lambda r: ','.join(k.replace('_assertion','').replace('output_validation','outcome').replace('topic_sequence_match','topic').replace('action_sequence_match','action') for k,v in r.items() if v!='PASS') or 'PASS'
    print(f"{i:2} v1:{fl(x[1]):14} v2:{fl(y[1]):14} | {y[0][:60]} | {y[3]} | {y[4]}")
print('v1 pass',pa,'of',len(a),' v2 pass',pb,'of',len(b))
