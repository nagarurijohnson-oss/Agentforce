"""S24 Phase B restore. Idempotent; runs every step even if one fails: reactivate v3 (if not Active), stop the watchdog,
Log in as off, remove the four temporary sets and the licence from CRA UAT Restricted, delete the saved sign-in,
after-snapshot and diff against the pre-snapshot."""
import json,subprocess,os,time,glob,signal
E={**os.environ,'SF_DISABLE_LOG_FILE':'true','SF_SKIP_NEW_VERSION_CHECK':'true'}; O='orgfarm-232477b490-dev-ed'; U='005jV000003sYUPQA2'
W='/tmp/agentforce_build-50144f18-a53e-4e8e-9955-a43b7975a4d2/work'
def sfj(a,t=300):
    try: r=subprocess.run(['sf']+a+['--target-org',O,'--json'],capture_output=True,text=True,timeout=t,env=E,cwd=W+'/Agentforce-kb'); return json.loads(r.stdout)
    except Exception as e: return {'error':str(e)[:300]}
def q(s): return sfj(['data','query','--query',s]).get('result',{}).get('records',[])
log=[]
def step(name,fn):
    try: log.append(f'{name}: {fn()}')
    except Exception as e: log.append(f'{name}: FAILED {e}')
def v3():
    st={r['VersionNumber']:r['Status'] for r in q("SELECT VersionNumber,Status FROM BotVersion WHERE BotDefinition.DeveloperName='Contact_Read_Agent'")}
    if st.get(3)=='Active': return 'v3 already Active'
    d=sfj(['agent','activate','--api-name','Contact_Read_Agent','--version','3']); return f"activate v3 {d.get('status')} {str(d.get('message',''))[:200]}"
step('reactivate_v3',v3)
def wd():
    f=W+'/s24/watchdog.pid'
    if not os.path.exists(f): return 'no watchdog'
    pid=int(open(f).read().strip())
    try: os.killpg(pid,signal.SIGTERM); r='stopped'
    except Exception as e: r=f'not running ({e})'
    os.remove(f); return r
step('watchdog',wd)
step('loginas_off',lambda: subprocess.run(['bash',W+'/s14/sec_set.sh','false'],capture_output=True,text=True,env=E).stdout.strip()[-200:])
def unassign():
    out=[]
    for ps in ['DATA_Knowledge_Read_Only','SYS_Knowledge_Default_DataSpace','EinsteinGPTPromptTemplateUser','SYS_Lightning_Experience_User']:
        for a in q(f"SELECT Id FROM PermissionSetAssignment WHERE AssigneeId='{U}' AND PermissionSet.Name='{ps}'"):
            out.append(f"{ps} {a['Id']} {sfj(['data','delete','record','--sobject','PermissionSetAssignment','--record-id',a['Id']]).get('status')}")
    for a in q(f"SELECT Id FROM PermissionSetLicenseAssign WHERE AssigneeId='{U}' AND PermissionSetLicenseId='0PLjV0000010UJLWA2'"):
        out.append(f"PSL {a['Id']} {sfj(['data','delete','record','--sobject','PermissionSetLicenseAssign','--record-id',a['Id']]).get('status')}")
    return out or 'nothing to remove'
step('unassign',unassign)
def signin():
    n=0
    for f in glob.glob(W+'/s20/secret/*'): os.remove(f); n+=1
    return f'removed {n} saved sign-in file(s)'
step('saved_signin',signin)
r=subprocess.run(['python3',W+'/s23/snap.py',W+'/s24/ev/after.json'],capture_output=True,text=True,env=E); 
try:
    a=json.load(open(W+'/s24/ev/after.json')); b=json.load(open(W+'/s24/ev/pre.json'))
    log.append('DIFF vs pre: '+json.dumps({k:[b.get(k),a[k]] for k in a if a[k]!=b.get(k)}))
except Exception as e: log.append(f'snapshot FAILED {e} {r.stderr[-300:]}')
log.append('LEX set assignees: '+str([x['AssigneeId'] for x in q("SELECT AssigneeId FROM PermissionSetAssignment WHERE PermissionSet.Name='SYS_Lightning_Experience_User'")]))
print('\n'.join(log)); open(W+'/s24/ev/restore-log.txt','a').write(time.strftime('%FT%TZ',time.gmtime())+'\n'+'\n'.join(log)+'\n\n')
