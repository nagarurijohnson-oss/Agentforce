"""S23 Phase A snapshot (read-only). usage: snap.py <out.json>"""
import json,subprocess,os,sys
E={**os.environ,'SF_DISABLE_LOG_FILE':'true','SF_SKIP_NEW_VERSION_CHECK':'true'}; O='orgfarm-232477b490-dev-ed'; U='005jV000003sYUPQA2'
W='/tmp/agentforce_build-50144f18-a53e-4e8e-9955-a43b7975a4d2/work'
def q(s,tool=False):
    r=subprocess.run(['sf','data','query','--query',s,'--target-org',O,'--json']+(['--use-tooling-api'] if tool else []),capture_output=True,text=True,env=E,timeout=300)
    return json.loads(r.stdout)['result']['records']
s={}
s['org']={k:v for k,v in q("SELECT Id,Name,OrganizationType,IsSandbox FROM Organization")[0].items() if k!='attributes'}
s['uat_sets']=sorted(r['PermissionSet']['Name'] for r in q(f"SELECT PermissionSet.Name FROM PermissionSetAssignment WHERE AssigneeId='{U}'"))
s['uat_psl']=sorted(r['PermissionSetLicense']['DeveloperName'] for r in q(f"SELECT PermissionSetLicense.DeveloperName FROM PermissionSetLicenseAssign WHERE AssigneeId='{U}'"))
p=q("SELECT UsedLicenses,TotalLicenses FROM PermissionSetLicense WHERE DeveloperName='EinsteinGPTPromptTemplatesPsl'")[0]; s['psl_used']={'UsedLicenses':p['UsedLicenses'],'TotalLicenses':p['TotalLicenses']}
s['grant_set_assignees']={n:sorted(r['AssigneeId'] for r in q(f"SELECT AssigneeId FROM PermissionSetAssignment WHERE PermissionSet.Name='{n}'")) for n in ['EinsteinGPTPromptTemplateUser','DATA_Knowledge_Read_Only','SYS_Knowledge_Default_DataSpace']}
s['org_assignments']=len(q("SELECT Id FROM PermissionSetAssignment WHERE Assignee.IsActive=true AND PermissionSet.IsOwnedByProfile=false"))
s['versions']=[[r['BotDefinition']['DeveloperName'],r['VersionNumber'],r['Status']] for r in q("SELECT BotDefinition.DeveloperName,VersionNumber,Status FROM BotVersion WHERE BotDefinition.DeveloperName IN ('Contact_Read_Agent','Employee_Leave_Assistant') ORDER BY BotDefinition.DeveloperName,VersionNumber")]
s['contacts']=len(q("SELECT Id FROM Contact"))
s['articles_online']=len(q("SELECT Id FROM Knowledge__kav WHERE PublishStatus='Online' AND Language='en_US'"))
s['trace']=len(q(f"SELECT Id FROM TraceFlag WHERE TracedEntityId='{U}'",tool=True))
s['debuglevel_cra']=len(q("SELECT Id FROM DebugLevel WHERE DeveloperName LIKE 'CRA_%'",tool=True))
r=subprocess.run(['python3',W+'/s14/sec_read.py'],capture_output=True,text=True,env=E); s['loginas']=r.stdout.strip()[-200:]
s['saved_signin']=sorted(os.listdir(W+'/s20/secret'))
json.dump(s,open(sys.argv[1],'w'),indent=1); print(json.dumps(s))
