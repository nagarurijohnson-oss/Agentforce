"""Local agent preview (repository script, live deployed action): does a literal backslash in the action OUTPUT survive the runtime?
The name searched matches no Contact; criteriaSummary echoes it unchanged. No records are read or changed."""
import json, subprocess, os, glob, re, sys
REPO='/tmp/build-52db6c0d-57e1-4383-bac3-df377a70eecc/work/Agentforce'; ORG='orgfarm-232477b490-dev-ed'; B='Contact_Read_Agent'
OUT=os.path.dirname(os.path.abspath(__file__)); tag=sys.argv[1]; msg=sys.argv[2]
def sf(a):
    p=subprocess.run(['sf']+a+['-o',ORG,'--json'],cwd=REPO,capture_output=True,text=True,timeout=400); r=p.stdout
    return json.loads(r[r.index('{'):])
sid=sf(['agent','preview','start','--authoring-bundle',B,'--use-live-actions'])['result']['sessionId']
send=sf(['agent','preview','send','--authoring-bundle',B,'--session-id',sid,'-u',msg])
e=sf(['agent','preview','end','--authoring-bundle',B,'--session-id',sid])['result']
tr=[f for f in glob.glob(e['tracesPath']+'/**/*.json',recursive=True) if os.path.basename(f).startswith(('0','1','2','3','4','5','6','7','8','9','a','b','c','d','e','f')) and 'metadata' not in f and 'index' not in f]
t=json.load(open(tr[0])); json.dump(t,open(OUT+'/trace_%s.json'%tag,'w'),indent=1,ensure_ascii=False)
for i,st in enumerate(t['plan']):
    if st.get('type')!='FunctionStep': continue
    s=json.dumps(st,ensure_ascii=False)
    for key in ('"name\\":', 'criteriaSummary'):
        for m in re.finditer(re.escape(key)+r'.{0,140}', s): print(tag,i,'|',m.group(0)[:170])
print(tag,'REPLY |',json.dumps([m.get('message') for m in send['result'].get('messages',[])],ensure_ascii=False)[:600])
