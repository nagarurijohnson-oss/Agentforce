"""Effective access of the UAT user: every permission set it holds (including the
profile's own), combined, because permission sets add up. Read-only queries."""
import json, subprocess, sys
O = 'orgfarm-232477b490-dev-ed'
U = '005jV000003sYUPQA2'
ADMIN = '005jV000001p8m9QAA'

def q(soql, tooling=False):
    cmd = ['sf', 'data', 'query', '-o', O, '--query', soql, '--json']
    if tooling:
        cmd.append('--use-tooling-api')
    out = subprocess.run(cmd, capture_output=True, text=True).stdout
    d = json.loads(out)
    if d.get('status') != 0:
        raise SystemExit(d.get('message'))
    return d['result']['records']

label = sys.argv[1] if len(sys.argv) > 1 else 'phase'
report = {'label': label}
psa = q(f"SELECT PermissionSetId, PermissionSet.Name, PermissionSet.IsOwnedByProfile, PermissionSetGroupId FROM PermissionSetAssignment WHERE AssigneeId = '{U}'")
ids = [r['PermissionSetId'] for r in psa]
report['permissionSets'] = [r['PermissionSet']['Name'] for r in psa]
inlist = ','.join(f"'{i}'" for i in ids)
fps = q(f"SELECT Field, PermissionsRead, PermissionsEdit, Parent.Name FROM FieldPermissions WHERE ParentId IN ({inlist}) AND SobjectType IN ('Contact','Account')")
eff = {}
for f in fps:
    e = eff.setdefault(f['Field'], {'read': False, 'edit': False, 'from': []})
    e['read'] |= f['PermissionsRead']; e['edit'] |= f['PermissionsEdit']
    e['from'].append(f['Parent']['Name'])
report['effectiveFields'] = eff
ops = q(f"SELECT SobjectType, PermissionsRead, PermissionsCreate, PermissionsEdit, PermissionsDelete, PermissionsViewAllRecords, PermissionsModifyAllRecords, Parent.Name FROM ObjectPermissions WHERE ParentId IN ({inlist})")
obj = {}
for o in ops:
    e = obj.setdefault(o['SobjectType'], {k: False for k in ['Read', 'Create', 'Edit', 'Delete', 'ViewAllRecords', 'ModifyAllRecords']})
    for k in e:
        e[k] |= o['Permissions' + k]
report['effectiveObjects'] = obj
sysp = q(f"SELECT Name, PermissionsViewAllData, PermissionsModifyAllData, PermissionsViewSetup, PermissionsApiEnabled, PermissionsAuthorApex FROM PermissionSet WHERE Id IN ({inlist})")
report['adminPermissions'] = {s['Name']: [k for k, v in s.items() if k.startswith('Permissions') and v] for s in sysp}
sea = q(f"SELECT SetupEntityType, SetupEntityId, Parent.Name FROM SetupEntityAccess WHERE ParentId IN ({inlist}) AND SetupEntityType IN ('ApexClass','BotDefinition')")
report['setupAccess'] = [(s['Parent']['Name'], s['SetupEntityType'], s['SetupEntityId']) for s in sea]

# Effective record visibility: UserRecordAccess for every CRA-TEST Contact without an Account,
# plus 3 on public Accounts as a control. Not assumed from the sharing model.
priv = q("SELECT Id, Name FROM Contact WHERE AccountId = null AND Email LIKE '%@synthetic.example'")
ctrl = q("SELECT Id, Name FROM Contact WHERE Email IN ('priya.synthwell@synthetic.example','jordan.samename.a@synthetic.example','bulk001@synthetic.example') AND AccountId != null")
ids2 = [r['Id'] for r in priv + ctrl]
names = {r['Id']: r['Name'] for r in priv + ctrl}
vis = {}
for who, uid in (('uat', U), ('admin', ADMIN)):
    rows = q(f"SELECT RecordId, HasReadAccess, HasEditAccess, HasDeleteAccess, MaxAccessLevel FROM UserRecordAccess WHERE UserId = '{uid}' AND RecordId IN ({','.join(repr(i) for i in ids2)})".replace('"', "'"))
    for r in rows:
        vis.setdefault(names[r['RecordId']] + ' ' + r['RecordId'], {})[who] = r['MaxAccessLevel']
report['recordAccess'] = vis
print(json.dumps(report, indent=1))
json.dump(report, open(f'/tmp/agentforce_build-50144f18-a53e-4e8e-9955-a43b7975a4d2/work/s6/effective-{label}.json', 'w'), indent=1)
