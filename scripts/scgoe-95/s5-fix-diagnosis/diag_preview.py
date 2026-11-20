"""One preview turn on the synthetic Contact; save the raw trace and locate every form of the LLC value."""
import json, subprocess, os, glob, shutil, re
REPO='/tmp/build-52db6c0d-57e1-4383-bac3-df377a70eecc/work/Agentforce'; ORG='orgfarm-232477b490-dev-ed'; B='Contact_Read_Agent'
OUT=os.path.dirname(os.path.abspath(__file__))
def sf(a):
    p=subprocess.run(['sf']+a+['-o',ORG,'--json'],cwd=REPO,capture_output=True,text=True,timeout=400); r=p.stdout
    return json.loads(r[r.index('{'):])
sid=sf(['agent','preview','start','--authoring-bundle',B,'--use-live-actions'])['result']['sessionId']
msg=sf(['agent','preview','send','--authoring-bundle',B,'--session-id',sid,'-u','Find the Contact with email zed.obrien@synthetic.example'])
json.dump(msg,open(OUT+'/send.json','w'),indent=1,ensure_ascii=False)
e=sf(['agent','preview','end','--authoring-bundle',B,'--session-id',sid])['result']
tp=e.get('tracesPath'); print('traces',tp)
for f in glob.glob(tp+'/**/*',recursive=True):
    if os.path.isfile(f): shutil.copy(f,OUT+'/trace_'+os.path.basename(f))
