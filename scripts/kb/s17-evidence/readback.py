import json,subprocess,os
O='orgfarm-232477b490-dev-ed'
def q(s,tool=False):
    a=['sf','data','query','-o',O,'-q',s,'--json']+(['--use-tooling-api'] if tool else [])
    r=subprocess.run(a,capture_output=True,text=True,timeout=110); return [{k:v for k,v in x.items() if k!='attributes'} for x in json.loads(r.stdout)['result']['records']]
fields=json.load(open("pfields.json"))
out={}
for n in ['DATA_Knowledge_Read_Only','SYS_Knowledge_Default_DataSpace']:
    ps=q("SELECT Id,Label,LicenseId,HasActivationRequired FROM PermissionSet WHERE Name='"+n+"'")[0]
    for i in range(0,len(fields),80):
        ps.update(q("SELECT "+','.join(fields[i:i+80])+" FROM PermissionSet WHERE Name='"+n+"'")[0])
    pid=ps['Id']
    o={'id':pid,'label':ps['Label'],'license':ps['LicenseId'],'userPerms':[f for f in fields if ps.get(f) is True],
       'objectPerms':q(f"SELECT SobjectType,PermissionsRead,PermissionsCreate,PermissionsEdit,PermissionsDelete,PermissionsViewAllRecords,PermissionsModifyAllRecords FROM ObjectPermissions WHERE ParentId='{pid}'"),
       'fieldPerms':len(q(f"SELECT Id FROM FieldPermissions WHERE ParentId='{pid}'")),
       'setupEntityAccess':q(f"SELECT SetupEntityType,SetupEntityId FROM SetupEntityAccess WHERE ParentId='{pid}'"),
       'assignments':len(q(f"SELECT Id FROM PermissionSetAssignment WHERE PermissionSetId='{pid}'"))}
    out[n]=o; print(n,json.dumps(o)[:900])
json.dump(out,open('readback.json','w'),indent=1)
