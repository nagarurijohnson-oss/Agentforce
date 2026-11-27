"""Undo every temporary Session-14 change. Idempotent; safe to run repeatedly."""
import json,subprocess,os,time
E={**os.environ,'SF_DISABLE_LOG_FILE':'true','SF_SKIP_NEW_VERSION_CHECK':'true'}; O='orgfarm-232477b490-dev-ed'; U='005jV000003sYUPQA2'
W='/tmp/agentforce_build-50144f18-a53e-4e8e-9955-a43b7975a4d2/work/s14'
def sf(a,t=300): r=subprocess.run(['sf']+a+['--target-org',O,'--json'],capture_output=True,text=True,timeout=t,env=E); 
def sfj(a,t=300):
    r=subprocess.run(['sf']+a+['--target-org',O,'--json'],capture_output=True,text=True,timeout=t,env=E)
    try: return json.loads(r.stdout)
    except Exception: return {'raw':r.stdout[-500:]+r.stderr[-500:]}
def q(s,tool=False): return sfj(['data','query','--query',s]+(['--use-tooling-api'] if tool else [])).get('result',{}).get('records',[])
log=[]
# 1. Login As off
r=subprocess.run(['bash',W+'/sec_set.sh','false'],capture_output=True,text=True,env=E); log.append(r.stdout.strip())
# 2. temporary assignments
for ps in ['DATA_Knowledge_Read_Only','DATA_Knowledge_UAT_No_Campus','SYS_UAT_KB_Harness','DATA_Contact_Read_Limited_UAT']:
    for a in q(f"SELECT Id FROM PermissionSetAssignment WHERE AssigneeId='{U}' AND PermissionSet.Name='{ps}'"):
        d=sfj(['data','delete','record','--sobject','PermissionSetAssignment','--record-id',a['Id']]); log.append(f'unassign {ps} {a["Id"]} {d.get("status")}')
# re-add DATA_Contact_Read_Only if a phase removed it
if not q(f"SELECT Id FROM PermissionSetAssignment WHERE AssigneeId='{U}' AND PermissionSet.Name='DATA_Contact_Read_Only'"):
    ps=q("SELECT Id FROM PermissionSet WHERE Name='DATA_Contact_Read_Only'")[0]['Id']
    d=sfj(['data','create','record','--sobject','PermissionSetAssignment','--values',f'AssigneeId={U} PermissionSetId={ps}']); log.append(f'reassign DATA_Contact_Read_Only {d.get("status")}')
for a in q(f"SELECT Id FROM PermissionSetLicenseAssign WHERE AssigneeId='{U}' AND PermissionSetLicense.DeveloperName='EinsteinGPTPromptTemplatesPsl'"):
    d=sfj(['data','delete','record','--sobject','PermissionSetLicenseAssign','--record-id',a['Id']]); log.append(f'psl removed {d.get("status")}')
# 3. trace flags on the UAT user
for t in q(f"SELECT Id FROM TraceFlag WHERE TracedEntityId='{U}'",tool=True):
    d=sfj(['data','delete','record','--use-tooling-api','--sobject','TraceFlag','--record-id',t['Id']]); log.append(f'traceflag {d.get("status")}')
for dl in q("SELECT Id FROM DebugLevel WHERE Id='7dljV000001G4WvQAK'",tool=True):
    d=sfj(['data','delete','record','--use-tooling-api','--sobject','DebugLevel','--record-id',dl['Id']]); log.append(f'debuglevel {d.get("status")}')
# 4. deactivate + delete flow and the two UAT-only sets
fd=q("SELECT Id FROM FlowDefinition WHERE DeveloperName='SF_UAT_Knowledge_Answer_Harness'",tool=True)
if fd:
    d=sfj(['data','update','record','--use-tooling-api','--sobject','FlowDefinition','--record-id',fd[0]['Id'],'--values','Metadata=\'{"activeVersionNumber":0}\'']); log.append(f'flow deactivate {d.get("status")} {str(d)[:200] if d.get("status") else ""}')
    for v in q("SELECT Id FROM Flow WHERE Definition.DeveloperName='SF_UAT_Knowledge_Answer_Harness'",tool=True):
        d=sfj(['data','delete','record','--use-tooling-api','--sobject','Flow','--record-id',v['Id']]); log.append(f'flow version delete {d.get("status")} {d.get("message","")[:150]}')
for ps in ['DATA_Knowledge_UAT_No_Campus','SYS_UAT_KB_Harness']:
    for p in q(f"SELECT Id FROM PermissionSet WHERE Name='{ps}'"):
        d=sfj(['data','delete','record','--sobject','PermissionSet','--record-id',p['Id']]); log.append(f'delete {ps} {d.get("status")} {d.get("message","")[:150]}')
# 5. read back
r=subprocess.run(["python3",W+"/sec_read.py"],capture_output=True,text=True,env=E); log.append('SECREADBACK '+r.stdout.strip())
log.append('UAT_PSA '+str(sorted(x['PermissionSet']['Name'] for x in q(f"SELECT PermissionSet.Name FROM PermissionSetAssignment WHERE AssigneeId='{U}'"))))
log.append('UAT_PSL '+str(q(f"SELECT Id FROM PermissionSetLicenseAssign WHERE AssigneeId='{U}'")))
log.append('LEFT_SETS '+str(q("SELECT Name FROM PermissionSet WHERE Name IN ('DATA_Knowledge_UAT_No_Campus','SYS_UAT_KB_Harness')")))
log.append('LEFT_FLOW '+str(q("SELECT Id FROM FlowDefinition WHERE DeveloperName='SF_UAT_Knowledge_Answer_Harness'",tool=True)))
log.append('LEFT_TRACE '+str(q(f"SELECT Id FROM TraceFlag WHERE TracedEntityId='{U}'",tool=True)))
print('\n'.join(log)); open(W+'/ev/restore-log.txt','a').write(time.strftime('%FT%TZ',time.gmtime())+'\n'+'\n'.join(log)+'\n\n')
