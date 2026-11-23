/*****************************************************************
Name:          CRA_ContactSearchSecurityTest
============================================================
Purpose:       Security tests for CRA_ContactSearchService, in two
               clearly separated groups:

               ENFORCED_* — real platform enforcement. Each test runs
               as a restricted user (Minimum Access - Salesforce
               profile plus a test-only permission set) inside
               System.runAs. Record sharing, object permissions and
               field-level security are applied by Salesforce itself
               to the service's USER_MODE queries and describes.
               Record level uses the org's real sharing: Contact is
               Controlled by Parent and Account is Public Read/Write,
               so a Contact with an Account is visible and a Contact
               without one is private to its owner (the admin).

               SIMULATED_* — the service is given a substitute
               CRA_FieldAccess that reports chosen fields or objects
               as unreadable while the admin runs the test. These
               prove the service's handling of an access answer
               (FILTER_UNAVAILABLE, "Not available"), not that
               Salesforce enforces it.

               Test users, test-only permission sets and every
               permission set assignment (including the one to
               DATA_Contact_Read_Only) are rolled back with the test;
               nothing is created or assigned in the org.
============================================================
History
-------
VERSION  AUTHOR                  DATE         DETAIL    DESCRIPTION
1.0      Revecast Orchestrate    19/11/2026   Created   SCGOE-95 Session 2
1.1      Revecast Orchestrate    20/11/2026   Updated   SCGOE-95 S2 review:
                                                      per-field phone FLS,
                                                      DATA / APP
                                                      permission sets
1.2      Revecast Orchestrate    23/11/2026   Updated   SCGOE-95 Session 6:
                                                      configuration checks,
                                                      limited UAT set,
                                                      additive-set proof
*****************************************************************/
@isTest
private class CRA_ContactSearchSecurityTest {

    private static final String SHARED_EMAIL = 'zara.visible@visible.example.com';
    private static final String HIDDEN_EMAIL = 'zed.hidden@hidden.example.com';
    private static final String ZANE_EMAIL = 'zane.visible@visible.example.com';
    private static final String SEC_TITLE = 'CRA-SEC Officer';
    private static final String ZANE_PHONE = '(303) 555-0188';
    private static final String ZANE_MOBILE = '(303) 555-0166';
    private static final String DATA_PERMISSION_SET = 'DATA_Contact_Read_Only';
    private static final String APP_PERMISSION_SET = 'APP_Contact_Read_Agent';
    private static final String LIMITED_PERMISSION_SET = 'DATA_Contact_Read_Limited_UAT';

    private static final List<String> BOTH_OBJECTS = new List<String>{ 'Account', 'Contact' };
    private static final List<String> ALL_FIELDS = new List<String>{
        'AccountId', 'Title', 'Email', 'Phone', 'MobilePhone', 'MailingAddress' };
    private static final List<String> PHONE_NOT_MOBILE = new List<String>{
        'AccountId', 'Title', 'Email', 'Phone', 'MailingAddress' };
    private static final List<String> MOBILE_NOT_PHONE = new List<String>{
        'AccountId', 'Title', 'Email', 'MobilePhone', 'MailingAddress' };
    private static final List<String> NO_EMAIL_OR_PHONE = new List<String>{
        'AccountId', 'Title', 'MailingAddress' };

    /*****************************************************************
    Purpose:   Three visible Contacts (on a public Account) and three
               private ones (no Account, owned by the admin). One
               private Contact shares the name, email and phone of a
               visible one, so duplicate checks can be tested.
    *****************************************************************/
    @testSetup
    static void createData() {
        Id visibleAccount = CRA_TestDataFactory.createAccounts(new List<String>{ 'Visible Co' })
            .get('Visible Co').Id;
        List<Contact> records = new List<Contact>{
            CRA_TestDataFactory.withMobile(CRA_TestDataFactory.withDetails(
                CRA_TestDataFactory.buildContact('Zara', 'Visible', visibleAccount),
                SEC_TITLE, SHARED_EMAIL, '(303) 555-0199'), '(303) 555-0155'),
            CRA_TestDataFactory.withMobile(CRA_TestDataFactory.withDetails(
                CRA_TestDataFactory.buildContact('Zane', 'Visible', visibleAccount),
                SEC_TITLE, ZANE_EMAIL, ZANE_PHONE), ZANE_MOBILE),
            CRA_TestDataFactory.withDetails(CRA_TestDataFactory.buildContact('Zoe', 'Visible', visibleAccount),
                SEC_TITLE, null, null),
            // Private: no Account, so only the owner (admin) can see these.
            CRA_TestDataFactory.withMobile(CRA_TestDataFactory.withDetails(
                CRA_TestDataFactory.buildContact('Zara', 'Visible', null),
                SEC_TITLE, SHARED_EMAIL, '303-555-0199'), '303.555.0155'),
            CRA_TestDataFactory.withDetails(CRA_TestDataFactory.buildContact('Zed', 'Hidden', null),
                SEC_TITLE, HIDDEN_EMAIL, '(303) 555-0177'),
            CRA_TestDataFactory.withDetails(CRA_TestDataFactory.buildContact('Zia', 'Hidden', null),
                SEC_TITLE, null, null)
        };
        CRA_TestDataFactory.insertAllowingDuplicates(records);
    }

    // ---------------------------------------------------------------
    // Helpers
    // ---------------------------------------------------------------

    private static CRA_ContactSearchResult run(CRA_ContactSearchCriteria criteria) {
        return new CRA_ContactSearchService().search(criteria);
    }

    private static CRA_ContactSearchCriteria byEmail(String email) {
        CRA_ContactSearchCriteria criteria = new CRA_ContactSearchCriteria();
        criteria.email = email;
        return criteria;
    }

    private static CRA_ContactSearchCriteria byPhone(String phone) {
        CRA_ContactSearchCriteria criteria = new CRA_ContactSearchCriteria();
        criteria.phone = phone;
        return criteria;
    }

    private static CRA_ContactSearchCriteria byTitle(String title) {
        CRA_ContactSearchCriteria criteria = new CRA_ContactSearchCriteria();
        criteria.jobTitle = title;
        return criteria;
    }

    private static Id hiddenContactId() {
        return [SELECT Id FROM Contact WHERE Email = :HIDDEN_EMAIL LIMIT 1].Id;
    }

    // =================================================================
    // ENFORCED — real record sharing
    // =================================================================

    /*****************************************************************
    Tests:     Baseline as admin: the private Contacts are counted, so
               the restricted-user tests below are meaningful.
    *****************************************************************/
    @isTest
    static void enforcedBaselineAdminSeesPrivateContacts() {
        Test.startTest();
        CRA_ContactSearchResult name = run(CRA_TestDataFactory.byName('Zara Visible'));
        CRA_ContactSearchResult title = run(byTitle('CRA-SEC'));
        Test.stopTest();
        System.assertEquals(CRA_ContactSearchResult.DUPLICATE_IDENTIFIER, name.outcomeCode);
        System.assertEquals('2', name.totalMatchesLabel);
        System.assertEquals(CRA_ContactSearchResult.LIST_6_TO_10, title.outcomeCode);
        System.assertEquals('6', title.totalMatchesLabel);
    }

    /*****************************************************************
    Tests:     A restricted user never sees private Contacts in rows,
               counts, duplicate checks or follow-ups, and the
               NO_MATCH wording does not reveal that they exist.
    *****************************************************************/
    @isTest
    static void enforcedRecordSharingLimitsResultsCountsAndDuplicates() {
        User reader = CRA_TestDataFactory.createRestrictedUser('craread', BOTH_OBJECTS, ALL_FIELDS);
        Id hiddenId = hiddenContactId();
        Map<String, CRA_ContactSearchResult> results = new Map<String, CRA_ContactSearchResult>();

        Test.startTest();
        System.runAs(reader) {
            CRA_ContactSearchCriteria followUp = new CRA_ContactSearchCriteria();
            followUp.contactId = hiddenId;
            results.put('name', run(CRA_TestDataFactory.byName('Zara Visible')));
            results.put('email', run(byEmail(SHARED_EMAIL)));
            results.put('phone', run(byPhone('303 555 0199')));
            results.put('mobile', run(byPhone('303 555 0155')));
            results.put('title', run(byTitle('CRA-SEC')));
            results.put('hidden', run(CRA_TestDataFactory.byName('Zed Hidden')));
            results.put('hiddenEmail', run(byEmail(HIDDEN_EMAIL)));
            results.put('followUp', run(followUp));
            results.put('nobody', run(CRA_TestDataFactory.byName('Nobody Exists')));
        }
        Test.stopTest();

        // Shared identifiers: the private twin is not counted, so no duplicate.
        for (String key : new List<String>{ 'name', 'email', 'phone', 'mobile' }) {
            System.assertEquals(CRA_ContactSearchResult.SINGLE_MATCH, results.get(key).outcomeCode, key);
            System.assertEquals('1', results.get(key).totalMatchesLabel, key);
            System.assertEquals(null, results.get(key).duplicateOn, key);
        }
        // Counts reflect accessible records only (admin sees 6).
        System.assertEquals(CRA_ContactSearchResult.LIST_2_TO_5, results.get('title').outcomeCode);
        System.assertEquals('3', results.get('title').totalMatchesLabel);
        System.assert(!results.get('title').getContactsJson().contains('Hidden'), 'Private rows leaked');
        System.assert(!results.get('title').getResultContactIds().contains(hiddenId), 'Private Id leaked');
        // Private Contacts and a nonexistent one get the identical neutral answer.
        for (String key : new List<String>{ 'hidden', 'hiddenEmail', 'followUp', 'nobody' }) {
            System.assertEquals(CRA_ContactSearchResult.NO_MATCH, results.get(key).outcomeCode, key);
            System.assertEquals(CRA_ContactSearchService.NO_MATCH_MESSAGE, results.get(key).userMessage, key);
            System.assert(results.get(key).contacts.isEmpty(), key);
        }
    }

    // =================================================================
    // ENFORCED — real field-level security
    // =================================================================

    /*****************************************************************
    Tests:     A user without Read on Email and Phone gets "Not
               available" for them, cannot filter by them, and the
               values appear nowhere in the output.
    *****************************************************************/
    @isTest
    static void enforcedFieldSecurityHidesUnreadableFields() {
        User limited = CRA_TestDataFactory.createRestrictedUser('craflsu', BOTH_OBJECTS, NO_EMAIL_OR_PHONE);
        Boolean emailReadable;
        Boolean titleReadable;
        CRA_ContactSearchResult byName;
        CRA_ContactSearchResult emailFilter;
        CRA_ContactSearchResult phoneFilter;
        CRA_ContactSearchResult emailAsk;
        CRA_ContactSearchResult noneResult;

        Test.startTest();
        System.runAs(limited) {
            // Prove the platform itself reports the restriction for this user.
            emailReadable = Schema.SObjectType.Contact.fields.Email.isAccessible();
            titleReadable = Schema.SObjectType.Contact.fields.Title.isAccessible();
            byName = run(CRA_TestDataFactory.byName('Zane Visible'));
            emailFilter = run(byEmail(ZANE_EMAIL));
            phoneFilter = run(byPhone(ZANE_PHONE));
            CRA_ContactSearchCriteria ask = CRA_TestDataFactory.byName('Zane Visible');
            ask.requestedField = 'Email';
            emailAsk = run(ask);
            noneResult = run(CRA_TestDataFactory.byName('Nobody Exists'));
        }
        Test.stopTest();

        System.assertEquals(false, emailReadable, 'Email must be unreadable for this user');
        System.assertEquals(true, titleReadable, 'Title must be readable for this user');

        System.assertEquals(CRA_ContactSearchResult.SINGLE_MATCH, byName.outcomeCode);
        CRA_ContactSearchResult.ContactRow row = byName.contacts[0];
        System.assertEquals(CRA_ContactSearchResult.NOT_AVAILABLE, row.email);
        System.assertEquals(CRA_ContactSearchResult.NOT_AVAILABLE, row.phone);
        System.assertEquals(CRA_ContactSearchResult.NOT_AVAILABLE, row.mobilePhone);
        System.assertEquals(SEC_TITLE, row.title);
        System.assertEquals('CRA-TEST Visible Co', row.accountName);
        String json = byName.getContactsJson();
        System.assert(!json.contains(ZANE_EMAIL) && !json.contains('555-0188') && !json.contains('555-0166'),
            'Unreadable value leaked');
        System.assert(!noneResult.suggestedFiltersText.contains('email')
            && !noneResult.suggestedFiltersText.contains('phone'), 'Unreadable field suggested');

        System.assertEquals(CRA_ContactSearchResult.FILTER_UNAVAILABLE, emailFilter.outcomeCode);
        System.assertEquals(CRA_ContactSearchResult.FILTER_UNAVAILABLE, phoneFilter.outcomeCode);
        System.assert(emailFilter.contacts.isEmpty() && phoneFilter.contacts.isEmpty());
        System.assertEquals(CRA_ContactSearchResult.FIELD_ANSWER, emailAsk.outcomeCode);
        System.assertEquals(CRA_ContactSearchResult.NOT_AVAILABLE, emailAsk.contacts[0].email);
    }

    /*****************************************************************
    Tests:     Phone and MobilePhone are secured separately. A user who
               can read Phone but not MobilePhone cannot find a Contact
               by its mobile and never sees it; the reverse user cannot
               find by, or see, the Phone. Both answers stay neutral.
    *****************************************************************/
    @isTest
    static void enforcedPhoneFieldSecurityIsPerField() {
        User phoneOnly = CRA_TestDataFactory.createRestrictedUser('craphon', BOTH_OBJECTS, PHONE_NOT_MOBILE);
        User mobileOnly = CRA_TestDataFactory.createRestrictedUser('cramobl', BOTH_OBJECTS, MOBILE_NOT_PHONE);
        Map<String, CRA_ContactSearchResult> results = new Map<String, CRA_ContactSearchResult>();
        Boolean phoneUserReadsMobile;
        Boolean mobileUserReadsPhone;

        Test.startTest();
        System.runAs(phoneOnly) {
            phoneUserReadsMobile = Schema.SObjectType.Contact.fields.MobilePhone.isAccessible();
            results.put('phoneUser.byMobile', run(byPhone(ZANE_MOBILE)));
            results.put('phoneUser.byPhone', run(byPhone(ZANE_PHONE)));
            CRA_ContactSearchCriteria ask = CRA_TestDataFactory.byName('Zane Visible');
            ask.requestedField = 'mobile';
            results.put('phoneUser.askMobile', run(ask));
        }
        System.runAs(mobileOnly) {
            mobileUserReadsPhone = Schema.SObjectType.Contact.fields.Phone.isAccessible();
            results.put('mobileUser.byMobile', run(byPhone(ZANE_MOBILE)));
            results.put('mobileUser.byPhone', run(byPhone(ZANE_PHONE)));
        }
        Test.stopTest();

        System.assertEquals(false, phoneUserReadsMobile, 'Platform: MobilePhone unreadable');
        System.assertEquals(false, mobileUserReadsPhone, 'Platform: Phone unreadable');

        for (String key : new List<String>{ 'phoneUser.byMobile', 'mobileUser.byPhone' }) {
            System.assertEquals(CRA_ContactSearchResult.NO_MATCH, results.get(key).outcomeCode, key);
            System.assertEquals(CRA_ContactSearchService.NO_MATCH_MESSAGE, results.get(key).userMessage, key);
            System.assert(results.get(key).contacts.isEmpty(), key);
        }
        CRA_ContactSearchResult viaPhone = results.get('phoneUser.byPhone');
        System.assertEquals(CRA_ContactSearchResult.SINGLE_MATCH, viaPhone.outcomeCode);
        System.assertEquals(ZANE_PHONE, viaPhone.contacts[0].phone);
        System.assertEquals(CRA_ContactSearchResult.NOT_AVAILABLE, viaPhone.contacts[0].mobilePhone);
        System.assert(!viaPhone.getContactsJson().contains('555-0166'), 'Mobile leaked');
        System.assertEquals(CRA_ContactSearchResult.NOT_AVAILABLE,
            results.get('phoneUser.askMobile').contacts[0].mobilePhone);

        CRA_ContactSearchResult viaMobile = results.get('mobileUser.byMobile');
        System.assertEquals(CRA_ContactSearchResult.SINGLE_MATCH, viaMobile.outcomeCode);
        System.assertEquals(ZANE_MOBILE, viaMobile.contacts[0].mobilePhone);
        System.assertEquals(CRA_ContactSearchResult.NOT_AVAILABLE, viaMobile.contacts[0].phone);
        System.assert(!viaMobile.getContactsJson().contains('555-0188'), 'Phone leaked');
    }

    // =================================================================
    // ENFORCED — the shipped permission sets (review M4)
    // =================================================================

    /*****************************************************************
    Tests:     DATA_Contact_Read_Only on its own (Minimum Access user,
               assignment inside the test only) grants exactly what
               the search needs: read on Contact and Account and on
               every contract field, and no create, edit or delete.
    *****************************************************************/
    @isTest
    static void enforcedDataPermissionSetGrantsReadOnly() {
        User reader = CRA_TestDataFactory.createUserWithPermissionSet('cradata', DATA_PERMISSION_SET);
        Map<String, Boolean> checks = new Map<String, Boolean>();
        CRA_ContactSearchResult result;

        Test.startTest();
        System.runAs(reader) {
            Schema.DescribeSObjectResult contactDescribe = Schema.SObjectType.Contact;
            checks.put('Contact read', contactDescribe.isAccessible());
            checks.put('Account read', Schema.SObjectType.Account.isAccessible());
            checks.put('Contact create', contactDescribe.isCreateable());
            checks.put('Contact edit', contactDescribe.isUpdateable());
            checks.put('Contact delete', contactDescribe.isDeletable());
            checks.put('Account edit', Schema.SObjectType.Account.isUpdateable());
            Map<String, Schema.SObjectField> fields = contactDescribe.fields.getMap();
            for (String fieldName : new List<String>{ 'AccountId', 'Title', 'Email', 'Phone', 'MobilePhone',
                    'MailingCity' }) {
                Schema.DescribeFieldResult field = fields.get(fieldName).getDescribe();
                checks.put(fieldName + ' read', field.isAccessible());
                checks.put(fieldName + ' edit', field.isUpdateable());
            }
            result = run(CRA_TestDataFactory.byName('Zane Visible'));
        }
        Test.stopTest();

        for (String key : checks.keySet()) {
            Boolean expected = key.endsWith(' read');
            System.assertEquals(expected, checks.get(key), key);
        }
        System.assertEquals(CRA_ContactSearchResult.SINGLE_MATCH, result.outcomeCode);
        System.assertEquals(ZANE_EMAIL, result.contacts[0].email);
        System.assertEquals(ZANE_MOBILE, result.contacts[0].mobilePhone);
        System.assertEquals('CRA-TEST Visible Co', result.contacts[0].accountName);
    }

    /*****************************************************************
    Tests:     APP_Contact_Read_Agent carries application access only:
               no object or field permissions, and no CRA permission
               set carries an admin permission. Assignments are not
               counted (Session 6 assigns the sets to the UAT user);
               the configuration is what is checked.
    *****************************************************************/
    @isTest
    static void enforcedAppPermissionSetGrantsNoData() {
        Test.startTest();
        Integer appSets = [SELECT COUNT() FROM PermissionSet WHERE Name = :APP_PERMISSION_SET];
        Integer appObjectGrants = [SELECT COUNT() FROM ObjectPermissions
            WHERE Parent.Name = :APP_PERMISSION_SET];
        Integer appFieldGrants = [SELECT COUNT() FROM FieldPermissions WHERE Parent.Name = :APP_PERMISSION_SET];
        Integer adminSets = [SELECT COUNT() FROM PermissionSet
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
    }

    // =================================================================
    // ENFORCED — real object permission (CRUD)
    // =================================================================

    /*****************************************************************
    Tests:     A user with no Contact Read gets the neutral NO_MATCH,
               not an error; and a raw USER_MODE query by that user is
               refused by the platform.
    *****************************************************************/
    @isTest
    static void enforcedNoContactAccessReturnsNeutralNoMatch() {
        User noAccess = CRA_TestDataFactory.createRestrictedUser('cranone', new List<String>(), new List<String>());
        Id hiddenId = hiddenContactId();
        CRA_ContactSearchResult byName;
        CRA_ContactSearchResult followUp;
        Boolean platformRefused = false;

        Test.startTest();
        System.runAs(noAccess) {
            byName = run(CRA_TestDataFactory.byName('Zane Visible'));
            CRA_ContactSearchCriteria criteria = new CRA_ContactSearchCriteria();
            criteria.contactId = hiddenId;
            followUp = run(criteria);
            try {
                Database.query('SELECT Id FROM Contact LIMIT 1', AccessLevel.USER_MODE);
            } catch (QueryException refused) {
                platformRefused = true;
            }
        }
        Test.stopTest();

        System.assert(platformRefused, 'USER_MODE must refuse Contact for this user');
        for (CRA_ContactSearchResult result : new List<CRA_ContactSearchResult>{ byName, followUp }) {
            System.assertEquals(CRA_ContactSearchResult.NO_MATCH, result.outcomeCode);
            System.assertEquals(CRA_ContactSearchService.NO_MATCH_MESSAGE, result.userMessage);
            System.assert(result.contacts.isEmpty());
        }
    }

    /*****************************************************************
    Tests:     USER_MODE is a real, independent layer. The service's own
               access check is replaced by one that says every field is
               readable, then the search runs as a user who cannot read
               Email or Phone. The USER_MODE query itself must refuse,
               so the result is the sanitised ERROR and no Email or
               Phone value reaches the output. (With SYSTEM_MODE the
               values would leak and this test fails.)
    *****************************************************************/
    @isTest
    static void enforcedUserModeBlocksFieldsEvenIfAccessCheckIsWrong() {
        User limited = CRA_TestDataFactory.createRestrictedUser('craumode', BOTH_OBJECTS, NO_EMAIL_OR_PHONE);
        CRA_ContactSearchResult result;

        Test.startTest();
        System.runAs(limited) {
            result = new CRA_ContactSearchService(new TrustingAccess())
                .search(CRA_TestDataFactory.byName('Zane Visible'));
        }
        Test.stopTest();

        System.assertEquals(CRA_ContactSearchResult.ERROR, result.outcomeCode,
            'USER_MODE must refuse the unreadable fields: ' + result.getContactsJson());
        System.assertEquals(CRA_ContactSearchService.ERROR_MESSAGE, result.userMessage);
        System.assert(!result.getContactsJson().contains(ZANE_EMAIL), 'Email leaked');
    }

    /*****************************************************************
    Purpose:   Deliberately wrong access check: reports everything as
               readable. Used only to isolate the USER_MODE layer.
    *****************************************************************/
    private class TrustingAccess extends CRA_FieldAccess {
        public override Boolean isContactReadable() {
            return true;
        }

        public override Boolean isAccountNameReadable() {
            return true;
        }

        public override Boolean isContactFieldReadable(String fieldName) {
            return contactFieldExists(fieldName);
        }
    }

    // =================================================================
    // SIMULATED — substitute access answers (admin context)
    // =================================================================

    /*****************************************************************
    Purpose:   Substitute access profile for simulated tests.
    *****************************************************************/
    private class SimulatedAccess extends CRA_FieldAccess {
        private final Boolean contactReadable;
        private final Boolean accountReadable;
        private final Set<String> unreadableFields;

        SimulatedAccess(Boolean contactReadable, Boolean accountReadable, Set<String> unreadableFields) {
            this.contactReadable = contactReadable;
            this.accountReadable = accountReadable;
            this.unreadableFields = unreadableFields;
        }

        public override Boolean isContactReadable() {
            return contactReadable;
        }

        public override Boolean isAccountNameReadable() {
            return accountReadable;
        }

        public override Boolean isContactFieldReadable(String fieldName) {
            return !unreadableFields.contains(fieldName) && super.isContactFieldReadable(fieldName);
        }
    }

    /*****************************************************************
    Tests:     SIMULATED: Account name unreadable — the Account filter
               is unavailable, the value reads "Not available" and is
               not suggested.
    *****************************************************************/
    @isTest
    static void simulatedAccountNameUnreadable() {
        CRA_ContactSearchService service = new CRA_ContactSearchService(
            new SimulatedAccess(true, false, new Set<String>()));
        CRA_ContactSearchCriteria accountFilter = new CRA_ContactSearchCriteria();
        accountFilter.accountName = 'Visible';

        Test.startTest();
        CRA_ContactSearchResult filtered = service.search(accountFilter);
        CRA_ContactSearchResult named = service.search(CRA_TestDataFactory.byName('Zane'));
        CRA_ContactSearchResult none = service.search(CRA_TestDataFactory.byName('Nobody'));
        Test.stopTest();

        System.assertEquals(CRA_ContactSearchResult.FILTER_UNAVAILABLE, filtered.outcomeCode);
        System.assert(filtered.userMessage.contains('Account name'), filtered.userMessage);
        System.assertEquals(CRA_ContactSearchResult.NOT_AVAILABLE, named.contacts[0].accountName);
        System.assert(!none.suggestedFiltersText.contains('Account name'), none.suggestedFiltersText);
    }

    /*****************************************************************
    Tests:     SIMULATED: Title and mailing address unreadable.
    *****************************************************************/
    @isTest
    static void simulatedTitleAndAddressUnreadable() {
        Set<String> hidden = new Set<String>{ 'Title', 'MailingStreet', 'MailingCity', 'MailingState',
            'MailingPostalCode', 'MailingCountry' };
        CRA_ContactSearchService service = new CRA_ContactSearchService(new SimulatedAccess(true, true, hidden));
        CRA_ContactSearchCriteria locationFilter = new CRA_ContactSearchCriteria();
        locationFilter.city = 'Denver';

        Test.startTest();
        CRA_ContactSearchResult titleResult = service.search(byTitle('CRA-SEC'));
        CRA_ContactSearchResult locationResult = service.search(locationFilter);
        CRA_ContactSearchResult named = service.search(CRA_TestDataFactory.byName('Zane'));
        Test.stopTest();

        System.assertEquals(CRA_ContactSearchResult.FILTER_UNAVAILABLE, titleResult.outcomeCode);
        System.assertEquals(CRA_ContactSearchResult.FILTER_UNAVAILABLE, locationResult.outcomeCode);
        System.assertEquals(CRA_ContactSearchResult.NOT_AVAILABLE, named.contacts[0].title);
        System.assertEquals(CRA_ContactSearchResult.NOT_AVAILABLE, named.contacts[0].mailingAddress);
        System.assertEquals(ZANE_EMAIL, named.contacts[0].email);
    }

    /*****************************************************************
    Tests:     SIMULATED: Contact unreadable gives the neutral NO_MATCH.
    *****************************************************************/
    @isTest
    static void simulatedContactUnreadable() {
        CRA_ContactSearchService service = new CRA_ContactSearchService(
            new SimulatedAccess(false, true, new Set<String>()));
        Test.startTest();
        CRA_ContactSearchResult result = service.search(CRA_TestDataFactory.byName('Zane'));
        Test.stopTest();
        System.assertEquals(CRA_ContactSearchResult.NO_MATCH, result.outcomeCode);
        System.assertEquals(CRA_ContactSearchService.NO_MATCH_MESSAGE, result.userMessage);
    }
}
