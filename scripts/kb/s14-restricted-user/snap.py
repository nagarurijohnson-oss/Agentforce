import json,subprocess,sys
O='orgfarm-232477b490-dev-ed'
def q(s,tool=False):
    a=['sf','data','query','--target-org',O,'--query',s,'--json']+(['--use-tooling-api'] if tool else [])
    r=subprocess.run(a,capture_output=True,text=True,timeout=110,env={**__import__('os').environ,'SF_DISABLE_LOG_FILE':'true','SF_SKIP_NEW_VERSION_CHECK':'true'})
    d=json.loads(r.stdout); rec=d['result']['records']
    def clean(x):
        if isinstance(x,dict): return {k:clean(v) for k,v in x.items() if k!='attributes'}
        return x
    return [clean(x) for x in rec]
S={}
S['uat_psa']=q("SELECT PermissionSet.Name,PermissionSet.IsOwnedByProfile,SystemModstamp FROM PermissionSetAssignment WHERE AssigneeId='005jV000003sYUPQA2' ORDER BY PermissionSet.Name")
S['uat_psl']=q("SELECT PermissionSetLicense.DeveloperName FROM PermissionSetLicenseAssign WHERE AssigneeId='005jV000003sYUPQA2'")
S['uat_user']=q("SELECT Username,IsActive,ProfileId,UserRoleId,UserPermissionsKnowledgeUser,LastModifiedDate FROM User WHERE Id='005jV000003sYUPQA2'")
S['all_psa_count']=len(q("SELECT Id FROM PermissionSetAssignment"))
S['botversions']=q("SELECT VersionNumber,Status,LastModifiedDate,BotDefinition.DeveloperName FROM BotVersion ORDER BY BotDefinition.DeveloperName,VersionNumber")
S['contacts']=q("SELECT Id,LastModifiedDate FROM Contact ORDER BY Id")
S['articles']=q("SELECT Id,ArticleNumber,PublishStatus,LastModifiedDate FROM Knowledge__kav ORDER BY ArticleNumber")
S['templates']=q("SELECT DeveloperName,LastModifiedDate FROM GenAiPromptTemplateVersion WHERE Id!=null LIMIT 1",tool=False) if False else None
json.dump(S,open(sys.argv[1],'w'),indent=1)
print({k:(len(v) if isinstance(v,list) else v) for k,v in S.items()})
print([ (b['BotDefinition']['DeveloperName'],b['VersionNumber'],b['Status']) for b in S['botversions']])
print([p['PermissionSet']['Name'] for p in S['uat_psa']], S['uat_psl'], S['uat_user'])
