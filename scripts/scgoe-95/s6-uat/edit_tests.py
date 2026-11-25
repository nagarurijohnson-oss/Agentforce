import os
os.chdir('/tmp/agentforce_build-50144f18-a53e-4e8e-9955-a43b7975a4d2/work/Agentforce/force-app/main/default/classes')

def sub(s, old, new):
    assert old in s, old[:80]
    return s.replace(old, new, 1)

# ---------------- CRA_ContactSearchActionTest ----------------
p = 'CRA_ContactSearchActionTest.cls'
s = open(p).read()
s = sub(s, """               - permission set metadata (Apex class access on APP,
                 none on DATA, no assignments);""", """               - permission set metadata (Apex class access on APP,
                 none on DATA, no admin or write permissions);""")
s = sub(s, """1.0      Revecast Orchestrate    20/11/2026   Created   SCGOE-95 Session 3
*****************************************************************/
@isTest
private class CRA_ContactSearchActionTest""", """1.0      Revecast Orchestrate    20/11/2026   Created   SCGOE-95 Session 3
1.1      Revecast Orchestrate    23/11/2026   Updated   SCGOE-95 Session 6:
                                                      configuration checks
                                                      replace the zero-
                                                      assignment assertion
*****************************************************************/
@isTest
private class CRA_ContactSearchActionTest""")
s = sub(s, """               other class). DATA_Contact_Read_Only grants no class
               access. Neither is assigned to anyone.
    *****************************************************************/""", """               other class). DATA_Contact_Read_Only grants no class
               access. Neither carries an admin or write permission,
               so whoever holds them (for example the Session 6 UAT
               user) gets read access and the action only.
               Assignments are deliberately NOT counted: they change
               with UAT and do not describe the configuration.
    *****************************************************************/""")
s = sub(s, """        Integer assignments = [SELECT COUNT() FROM PermissionSetAssignment
            WHERE PermissionSet.Name IN (:APP_PERMISSION_SET, :DATA_PERMISSION_SET)];
        Test.stopTest();

        System.assertEquals(new Set<Id>{ actionClassId }, appClassGrants, 'APP grants the action class only');
        System.assertEquals(0, dataClassGrants, 'DATA grants no Apex class access');
        System.assertEquals(0, appObjectGrants, 'APP grants no object access');
        System.assertEquals(0, appFieldGrants, 'APP grants no field access');
        System.assertEquals(0, assignments, 'No automatic assignment');
    }""", """        Integer dataWriteGrants = [SELECT COUNT() FROM ObjectPermissions
            WHERE Parent.Name = :DATA_PERMISSION_SET
            AND (PermissionsCreate = true OR PermissionsEdit = true OR PermissionsDelete = true
                 OR PermissionsViewAllRecords = true OR PermissionsModifyAllRecords = true)];
        Integer dataFieldEdits = [SELECT COUNT() FROM FieldPermissions
            WHERE Parent.Name = :DATA_PERMISSION_SET AND PermissionsEdit = true];
        List<PermissionSet> craSets = [SELECT Name, IsOwnedByProfile, PermissionsViewAllData,
                PermissionsModifyAllData, PermissionsViewSetup, PermissionsApiEnabled
            FROM PermissionSet WHERE Name IN (:APP_PERMISSION_SET, :DATA_PERMISSION_SET)];
        Test.stopTest();

        System.assertEquals(new Set<Id>{ actionClassId }, appClassGrants, 'APP grants the action class only');
        System.assertEquals(0, dataClassGrants, 'DATA grants no Apex class access');
        System.assertEquals(0, appObjectGrants, 'APP grants no object access');
        System.assertEquals(0, appFieldGrants, 'APP grants no field access');
        System.assertEquals(0, dataWriteGrants, 'DATA grants no create, edit, delete, View All or Modify All');
        System.assertEquals(0, dataFieldEdits, 'DATA grants no field edit');
        System.assertEquals(2, craSets.size(), 'Both permission sets are in the deployment');
        for (PermissionSet craSet : craSets) {
            System.assert(!craSet.IsOwnedByProfile, craSet.Name + ' is a standalone permission set');
            System.assert(!craSet.PermissionsViewAllData, craSet.Name + ': no View All Data');
            System.assert(!craSet.PermissionsModifyAllData, craSet.Name + ': no Modify All Data');
            System.assert(!craSet.PermissionsViewSetup, craSet.Name + ': no View Setup');
            System.assert(!craSet.PermissionsApiEnabled, craSet.Name + ': no API Enabled');
        }
    }""")
open(p, 'w').write(s)

# ---------------- CRA_ContactSearchSecurityTest ----------------
p = 'CRA_ContactSearchSecurityTest.cls'
s = open(p).read()
s = sub(s, """    private static final String APP_PERMISSION_SET = 'APP_Contact_Read_Agent';
""", """    private static final String APP_PERMISSION_SET = 'APP_Contact_Read_Agent';
    private static final String LIMITED_PERMISSION_SET = 'DATA_Contact_Read_Limited_UAT';
""")
s = sub(s, """                                                      DATA / APP
                                                      permission sets
*****************************************************************/""", """                                                      DATA / APP
                                                      permission sets
1.2      Revecast Orchestrate    23/11/2026   Updated   SCGOE-95 Session 6:
                                                      configuration checks,
                                                      limited UAT set,
                                                      additive-set proof
*****************************************************************/""")
s = sub(s, """    Tests:     APP_Contact_Read_Agent carries application access only:
               no object or field permissions. Neither permission set
               is assigned to anyone in the org.
    *****************************************************************/""", """    Tests:     APP_Contact_Read_Agent carries application access only:
               no object or field permissions, and no CRA permission
               set carries an admin permission. Assignments are not
               counted (Session 6 assigns the sets to the UAT user);
               the configuration is what is checked.
    *****************************************************************/""")
s = sub(s, """        Integer assignments = [SELECT COUNT() FROM PermissionSetAssignment
            WHERE PermissionSet.Name IN (:APP_PERMISSION_SET, :DATA_PERMISSION_SET)];
        Test.stopTest();

        System.assertEquals(1, appSets, 'APP permission set is in the deployment');
        System.assertEquals(0, appObjectGrants, 'APP grants no object access');
        System.assertEquals(0, appFieldGrants, 'APP grants no field access');
        System.assertEquals(0, assignments, 'No automatic assignment');
    }""", """        Integer adminSets = [SELECT COUNT() FROM PermissionSet
            WHERE Name IN (:APP_PERMISSION_SET, :DATA_PERMISSION_SET, :LIMITED_PERMISSION_SET)
            AND (PermissionsViewAllData = true OR PermissionsModifyAllData = true
                 OR PermissionsViewSetup = true OR PermissionsApiEnabled = true)];
        Test.stopTest();

        System.assertEquals(1, appSets, 'APP permission set is in the deployment');
        System.assertEquals(0, appObjectGrants, 'APP grants no object access');
        System.assertEquals(0, appFieldGrants, 'APP grants no field access');
        System.assertEquals(0, adminSets, 'No CRA permission set grants an admin permission');
    }

    /*****************************************************************
    Tests:     DATA_Contact_Read_Limited_UAT on its own (Minimum Access
               user, assignment inside the test only) grants read on
               Contact, Account, AccountId, Title and Phone and does
               NOT grant Email, MobilePhone or Mailing Address. The
               search shows "Not available" for the withheld fields
               and answers an email filter with FILTER_UNAVAILABLE.
    *****************************************************************/
    @isTest
    static void enforcedLimitedUatSetWithholdsContactPoints() {
        User limited = CRA_TestDataFactory.createUserWithPermissionSet('cralim', LIMITED_PERMISSION_SET);
        Map<String, Boolean> readable = new Map<String, Boolean>();
        CRA_ContactSearchResult viaName;
        CRA_ContactSearchResult viaEmail;

        Test.startTest();
        System.runAs(limited) {
            Map<String, Schema.SObjectField> fields = Schema.SObjectType.Contact.fields.getMap();
            for (String fieldName : new List<String>{ 'AccountId', 'Title', 'Phone', 'Email', 'MobilePhone',
                    'MailingCity', 'MailingStreet' }) {
                readable.put(fieldName, fields.get(fieldName).getDescribe().isAccessible());
            }
            readable.put('Contact edit', Schema.SObjectType.Contact.isUpdateable());
            viaName = run(CRA_TestDataFactory.byName('Zane Visible'));
            viaEmail = run(byEmail(ZANE_EMAIL));
        }
        Test.stopTest();

        for (String fieldName : new List<String>{ 'AccountId', 'Title', 'Phone' }) {
            System.assert(readable.get(fieldName), fieldName + ' is readable');
        }
        for (String fieldName : new List<String>{ 'Email', 'MobilePhone', 'MailingCity', 'MailingStreet',
                'Contact edit' }) {
            System.assert(!readable.get(fieldName), fieldName + ' is withheld');
        }
        System.assertEquals(CRA_ContactSearchResult.SINGLE_MATCH, viaName.outcomeCode);
        System.assertEquals(CRA_ContactSearchResult.NOT_AVAILABLE, viaName.contacts[0].email);
        System.assertEquals(CRA_ContactSearchResult.NOT_AVAILABLE, viaName.contacts[0].mobilePhone);
        System.assertEquals(ZANE_PHONE, viaName.contacts[0].phone);
        System.assert(!viaName.getContactsJson().contains(ZANE_EMAIL), 'Email leaked');
        System.assert(!viaName.getContactsJson().contains(ZANE_MOBILE), 'Mobile leaked');
        System.assertEquals(CRA_ContactSearchResult.FILTER_UNAVAILABLE, viaEmail.outcomeCode);
        System.assert(viaEmail.contacts.isEmpty(), 'No rows through a withheld filter');
    }

    /*****************************************************************
    Tests:     Permission sets add up. A user holding BOTH the limited
               UAT set and DATA_Contact_Read_Only can read Email again,
               so during the field-level security phase the limited
               set must replace the full one, never join it.
    *****************************************************************/
    @isTest
    static void enforcedPermissionSetsAreAdditive() {
        User both = CRA_TestDataFactory.createUserWithPermissionSet('craboth', LIMITED_PERMISSION_SET);
        System.runAs(new User(Id = UserInfo.getUserId())) {
            Id fullSetId = [SELECT Id FROM PermissionSet WHERE Name = :DATA_PERMISSION_SET LIMIT 1].Id;
            insert new PermissionSetAssignment(AssigneeId = both.Id, PermissionSetId = fullSetId);
        }
        Boolean emailReadable;

        Test.startTest();
        System.runAs(both) {
            emailReadable = Schema.SObjectType.Contact.fields.Email.isAccessible();
        }
        Test.stopTest();

        System.assert(emailReadable, 'DATA_Contact_Read_Only restores Email: never combine the two sets');
    }""")
open(p, 'w').write(s)
print('ok')
