/*****************************************************************
Name:          CRA_CaseCreateFlowSecurityTest
============================================================
Purpose:       SCGOE-95 CASE-1 (S33). Proves that the two Case flows
               used by Contact_Read_Agent (SUB_Case_Draft_Validate and
               SUB_Case_Create_Confirmed) only work for a user who holds
               the CRA_Case_Create custom permission AND Case Create,
               Contact Read and Edit on every Case field the flow sets.
               The flows run in system mode with sharing, so these
               checks come from SUB_Case_Create_Access_Check.
               Every user, permission set and record is synthetic and
               is rolled back when the test ends.
============================================================
History
-------
VERSION  AUTHOR                  DATE         DETAIL    DESCRIPTION
1.0      Revecast Orchestrate    27/11/2026   Created   SCGOE-95 S33
*****************************************************************/
@isTest
private class CRA_CaseCreateFlowSecurityTest {

    private static final String CREATE_FLOW = 'SUB_Case_Create_Confirmed';
    private static final String DRAFT_FLOW = 'SUB_Case_Draft_Validate';
    private static final String CUSTOM_PERMISSION = 'CRA_Case_Create';
    private static final String CASE_PERMSET = 'DATA_Case_Create';
    private static final String CONTACT_PERMSET = 'DATA_Contact_Read_Only';
    private static final String SUBJECT = 'CRA-TEST S33 flow security';

    /*************************************************************
    Purpose: Creates one synthetic Minimum Access user with the given
             existing permission sets and optional test-only sets.
    *************************************************************/
    private static User createUser(List<String> permSetNames, List<PermissionSet> extraSets) {
        User runningAdmin = new User(Id = UserInfo.getUserId());
        User testUser;
        System.runAs(runningAdmin) {
            Profile minimumAccess = [SELECT Id FROM Profile WHERE Name = 'Minimum Access - Salesforce' LIMIT 1];
            String uniqueKey = String.valueOf(Crypto.getRandomInteger()).replace('-', '');
            testUser = new User(
                Alias = 'crasec', Email = 'cra.s33.' + uniqueKey + '@example.invalid',
                EmailEncodingKey = 'UTF-8', LastName = 'CRA S33 Test', LanguageLocaleKey = 'en_US',
                LocaleSidKey = 'en_US', ProfileId = minimumAccess.Id, TimeZoneSidKey = 'Asia/Kolkata',
                Username = 'cra.s33.' + uniqueKey + '@example.invalid'
            );
            insert testUser;
            List<PermissionSetAssignment> assignments = new List<PermissionSetAssignment>();
            for (PermissionSet existingSet : [SELECT Id FROM PermissionSet WHERE Name IN :permSetNames]) {
                assignments.add(new PermissionSetAssignment(AssigneeId = testUser.Id, PermissionSetId = existingSet.Id));
            }
            for (PermissionSet extraSet : extraSets) {
                assignments.add(new PermissionSetAssignment(AssigneeId = testUser.Id, PermissionSetId = extraSet.Id));
            }
            insert assignments;
        }
        return testUser;
    }

    /*************************************************************
    Purpose: A test-only permission set that grants the custom
             permission and, optionally, Case Create plus the listed
             Case fields. Simulates the custom permission being added
             outside DATA_Case_Create.
    *************************************************************/
    private static PermissionSet createCustomPermissionSet(Boolean grantCaseCreate, List<String> editableFields) {
        PermissionSet testSet;
        System.runAs(new User(Id = UserInfo.getUserId())) {
            testSet = new PermissionSet(Name = 'CRA_S33_Test_' + String.valueOf(Crypto.getRandomInteger()).replace('-', ''),
                                        Label = 'CRA S33 Test');
            insert testSet;
            CustomPermission gate = [SELECT Id FROM CustomPermission WHERE DeveloperName = :CUSTOM_PERMISSION LIMIT 1];
            insert new SetupEntityAccess(ParentId = testSet.Id, SetupEntityId = gate.Id);
            if (grantCaseCreate) {
                insert new ObjectPermissions(ParentId = testSet.Id, SobjectType = 'Case',
                                             PermissionsRead = true, PermissionsCreate = true);
            }
            List<FieldPermissions> fieldGrants = new List<FieldPermissions>();
            for (String fieldName : editableFields) {
                fieldGrants.add(new FieldPermissions(ParentId = testSet.Id, SobjectType = 'Case', Field = fieldName,
                                                     PermissionsRead = true, PermissionsEdit = true));
            }
            insert fieldGrants;
        }
        return testSet;
    }

    /*************************************************************
    Purpose: A synthetic Contact. A Contact without an Account is private
             to its owner, so ownerId lets the restricted user own it.
    *************************************************************/
    private static Contact createContact(Boolean withAccount, Id ownerId) {
        Account testAccount;
        if (withAccount) {
            testAccount = new Account(Name = 'CRA-TEST S33 Account');
            insert testAccount;
        }
        Contact testContact = new Contact(FirstName = 'Casey', LastName = 'CRA-TEST S33',
                                          AccountId = withAccount ? testAccount.Id : null,
                                          OwnerId = ownerId == null ? UserInfo.getUserId() : ownerId);
        insert testContact;
        return testContact;
    }

    private static Map<String, Object> inputs(Id contactId) {
        return new Map<String, Object>{
            'varT_ContactId' => String.valueOf(contactId), 'varT_Subject' => SUBJECT,
            'varT_Description' => 'Synthetic description for S33.', 'varT_Origin' => 'Web', 'varT_Priority' => 'Low'
        };
    }

    /*************************************************************
    Purpose: Runs a flow and returns its outcome code.
    *************************************************************/
    private static String runFlow(String flowName, Map<String, Object> params) {
        Flow.Interview interview = Flow.Interview.createInterview(flowName, params);
        interview.start();
        return (String) interview.getVariableValue('varT_OutcomeCode');
    }

    private static Integer caseCount(Id contactId) {
        return [SELECT COUNT() FROM Case WHERE ContactId = :contactId];
    }

    // Custom permission only (no Case access): both flows refuse and no Case exists.
    @isTest
    static void customPermissionWithoutCaseAccessIsDenied() {
        Contact testContact = createContact(true, null);
        User testUser = createUser(new List<String>{ CONTACT_PERMSET },
                                   new List<PermissionSet>{ createCustomPermissionSet(false, new List<String>()) });
        String draftOutcome;
        String createOutcome;
        Test.startTest();
        System.runAs(testUser) {
            draftOutcome = runFlow(DRAFT_FLOW, inputs(testContact.Id));
            createOutcome = runFlow(CREATE_FLOW, inputs(testContact.Id));
        }
        Test.stopTest();
        System.assertEquals('NO_PERMISSION', draftOutcome, 'Draft must be refused without Case Create');
        System.assertEquals('NO_PERMISSION', createOutcome, 'Create must be refused without Case Create');
        System.assertEquals(0, caseCount(testContact.Id), 'No Case may be created');
    }

    // Custom permission + Case Create, but no Edit on Priority: refused.
    @isTest
    static void missingFieldEditIsDenied() {
        Contact testContact = createContact(true, null);
        PermissionSet partial = createCustomPermissionSet(true,
            new List<String>{ 'Case.Subject', 'Case.Description', 'Case.Origin', 'Case.ContactId', 'Case.AccountId' });
        User testUser = createUser(new List<String>{ CONTACT_PERMSET }, new List<PermissionSet>{ partial });
        String createOutcome;
        Test.startTest();
        System.runAs(testUser) {
            createOutcome = runFlow(CREATE_FLOW, inputs(testContact.Id));
        }
        Test.stopTest();
        System.assertEquals('NO_PERMISSION', createOutcome, 'Create must be refused without Edit on Case.Priority');
        System.assertEquals(0, caseCount(testContact.Id), 'No Case may be created');
    }

    // Contact has an Account, user cannot edit Case.AccountId: refused; same user,
    // Contact without Account: allowed.
    @isTest
    static void accountLinkNeedsAccountIdEdit() {
        Contact withAccount = createContact(true, null);
        PermissionSet noAccountField = createCustomPermissionSet(true,
            new List<String>{ 'Case.Subject', 'Case.Description', 'Case.Origin', 'Case.Priority', 'Case.ContactId' });
        User testUser = createUser(new List<String>{ CONTACT_PERMSET }, new List<PermissionSet>{ noAccountField });
        Contact withoutAccount = createContact(false, testUser.Id);
        String draftWithAccount;
        String createWithAccount;
        String createWithoutAccount;
        Test.startTest();
        System.runAs(testUser) {
            draftWithAccount = runFlow(DRAFT_FLOW, inputs(withAccount.Id));
            createWithAccount = runFlow(CREATE_FLOW, inputs(withAccount.Id));
            createWithoutAccount = runFlow(CREATE_FLOW, inputs(withoutAccount.Id));
        }
        Test.stopTest();
        System.assertEquals('NO_PERMISSION', draftWithAccount, 'Draft must be refused without Case.AccountId Edit');
        System.assertEquals('NO_PERMISSION', createWithAccount, 'Create must be refused without Case.AccountId Edit');
        System.assertEquals(0, caseCount(withAccount.Id), 'No Case for the Contact with an Account');
        System.assertEquals('CREATED', createWithoutAccount, 'Contact without an Account needs no AccountId Edit');
        System.assertEquals(1, caseCount(withoutAccount.Id), 'Exactly one Case');
    }

    // Authorized restricted user: draft creates nothing, confirm creates exactly one
    // Case with the real Case Number, a repeat is refused as a duplicate.
    @isTest
    static void authorizedUserCreatesExactlyOneCase() {
        Contact testContact = createContact(true, null);
        User testUser = createUser(new List<String>{ CONTACT_PERMSET, CASE_PERMSET }, new List<PermissionSet>());
        String draftOutcome;
        Integer afterDraft;
        Flow.Interview created;
        String repeatOutcome;
        Test.startTest();
        System.runAs(testUser) {
            draftOutcome = runFlow(DRAFT_FLOW, inputs(testContact.Id));
            afterDraft = caseCount(testContact.Id);
            created = Flow.Interview.createInterview(CREATE_FLOW, inputs(testContact.Id));
            created.start();
            repeatOutcome = runFlow(CREATE_FLOW, inputs(testContact.Id));
        }
        Test.stopTest();
        System.assertEquals('DRAFT_READY', draftOutcome, 'Authorized user gets the draft');
        System.assertEquals(0, afterDraft, 'The draft (and a cancel) creates no Case');
        System.assertEquals('CREATED', (String) created.getVariableValue('varT_OutcomeCode'), 'Confirm creates the Case');
        Case createdCase = [SELECT Id, CaseNumber, AccountId, Status, Priority FROM Case WHERE ContactId = :testContact.Id];
        System.assertEquals(createdCase.CaseNumber, (String) created.getVariableValue('varT_CaseNumber'), 'Real Case Number returned');
        System.assertEquals(String.valueOf(createdCase.Id), (String) created.getVariableValue('varT_CaseId'), 'Real Case Id returned');
        System.assertEquals(testContact.AccountId, createdCase.AccountId, 'Account comes from the Contact');
        System.assertEquals('DUPLICATE', repeatOutcome, 'A repeated confirm is refused');
        System.assertEquals(1, caseCount(testContact.Id), 'Exactly one Case after two confirms');
    }
}
