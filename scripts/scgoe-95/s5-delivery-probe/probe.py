import json, subprocess, sys, os, glob
P='/tmp/build-52db6c0d-57e1-4383-bac3-df377a70eecc/work/s5-delivery'
ORG='orgfarm-232477b490-dev-ed'
def sf(a):
    p=subprocess.run(['sf']+a+['-o',ORG,'--json'],cwd=P+'/proj',capture_output=True,text=True,timeout=500)
    raw=p.stdout.strip()
    try: return json.loads(raw[raw.index('{'):])
    except Exception: return {'status':99,'raw':(raw or p.stderr)[-800:]}
b=sys.argv[1]; utts=sys.argv[2:] or ['Find the Contact with the email zed.obrien@synthetic.example']
st=sf(['agent','preview','start','--authoring-bundle',b,'--use-live-actions']); sid=(st.get('result') or {}).get('sessionId')
out={'bundle':b,'start':st,'turns':[]}
for u in utts:
    r=sf(['agent','preview','send','--authoring-bundle',b,'--session-id',sid,'-u',u]); out['turns'].append({'user':u,'raw':r})
e=sf(['agent','preview','end','--authoring-bundle',b,'--session-id',sid]); out['end']=e.get('result')
tp=(e.get('result') or {}).get('tracesPath'); out['traces']=[]
if tp:
    for f in sorted(glob.glob(tp+'/traces/*.json'),key=os.path.getmtime): out['traces'].append(json.load(open(f)))
json.dump(out,open(f'{P}/probe-{b}.json','w'),indent=1,ensure_ascii=False)
for t in out['turns']:
    print('USER:',t['user'])
    for m in ((t['raw'].get('result') or {}).get('messages') or []):
        print(' MSG keys',sorted(m.keys()),'type',m.get('type')); print(' TEXT:',repr((m.get('message') or '')[:600]))
        for k in m:
            if k not in ('message','type','id','feedbackId','planId','isContentSafe','message_type'): print('  ',k,'=',json.dumps(m[k],ensure_ascii=False)[:600])
for tr in out['traces']:
    print('STEPS:',[ (s['type'], (s.get('function') or {}).get('name')) for s in tr.get('plan',[])])
