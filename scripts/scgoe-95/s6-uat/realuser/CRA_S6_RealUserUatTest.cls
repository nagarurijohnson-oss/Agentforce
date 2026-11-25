/*****************************************************************
Name:          CRA_S6_RealUserUatTest
============================================================
Purpose:       SCGOE-95 Session 6 UAT evidence. Runs the real
               CRA_ContactSearchAction as the REAL restricted user
               "CRA UAT Restricted" (Minimum Access - Salesforce plus
               the permission sets actually assigned in the org)
               against the real synthetic CRA-TEST data.
               - Sharing tests use the real assignments unchanged.
               - FLS and CRUD tests swap permission sets INSIDE the
                 test transaction only (rolled back).
               - Admin baseline runs as the deploying admin.
               This class is run ONLY through a check-only
               validation: it is never saved in the org, and every
               change it makes is rolled back. SeeAllData is needed
               to see the real user and data.
============================================================
History
-------
VERSION  AUTHOR                  DATE         DETAIL    DESCRIPTION
1.0      Revecast Orchestrate    23/11/2026   Created   SCGOE-95 Session 6
*****************************************************************/
@isTest(SeeAllData=true)
private class CRA_S6_RealUserUatTest {

    private static final String UAT_USERNAME = 'cra.uat.restricted@00djv000003bvbruaw.example';
    private static final String PRIYA_EMAIL = 'priya.synthwell@synthetic.example';
    private static final String PRIYA_MOBILE = '+1 555 0201';
    private static final String FULL_SET = 'DATA_Contact_Read_Only';
    private static final String LIMITED_SET = 'DATA_Contact_Read_Limited_UAT';

    private static User uat() {
        return [SELECT Id FROM User WHERE Username = :UAT_USERNAME AND IsActive = true LIMIT 1];
    }

    private static CRA_ContactSearchAction.Response search(CRA_ContactSearchAction.Request request) {
        return CRA_ContactSearchAction.searchContacts(new List<CRA_ContactSearchAction.Request>{ request })[0];
    }

    private static CRA_ContactSearchAction.Request req() {
        return new CRA_ContactSearchAction.Request();
    }

    private static CRA_ContactSearchAction.Request byName(String name) {
        CRA_ContactSearchAction.Request r = req(); r.name = name; return r;
    }

    private static CRA_ContactSearchAction.Request byEmail(String email) {
        CRA_ContactSearchAction.Request r = req(); r.email = email; return r;
    }

    private static CRA_ContactSearchAction.Request byTitle(String title) {
        CRA_ContactSearchAction.Request r = req(); r.jobTitle = title; return r;
    }

    private static CRA_ContactSearchAction.Request byAccount(String account) {
        CRA_ContactSearchAction.Request r = req(); r.accountName = account; return r;
    }

    private static String describe(CRA_ContactSearchAction.Response r) {
        return r.outcomeCode + ' total=' + r.totalMatchesLabel + ' shown=' + r.shownCount
            + ' remaining=' + r.remainingCount;
    }

    /*****************************************************************
    Purpose:   Swap the UAT user's DATA permission sets inside this
               test only: remove the full set, optionally add another.
    *****************************************************************/
    private static void swapDataSet(Id userId, String addSet) {
        System.runAs(new User(Id = UserInfo.getUserId())) {
            delete [SELECT Id FROM PermissionSetAssignment
                WHERE AssigneeId = :userId AND PermissionSet.Name = :FULL_SET];
            if (addSet != null) {
                insert new PermissionSetAssignment(AssigneeId = userId,
                    PermissionSetId = [SELECT Id FROM PermissionSet WHERE Name = :addSet LIMIT 1].Id);
            }
        }
    }

    // =================================================================
    // Record-level sharing (real assignments, unchanged)
    // =================================================================

    /*****************************************************************
    Tests:     Duplicate handling respects sharing. The UAT user sees
               2 Jordan Samename Contacts (the private 3rd is hidden),
               the admin sees 3; neither result picks one.
    *****************************************************************/
    @isTest
    static void sharingDuplicateNames() {
        CRA_ContactSearchAction.Response admin = search(byName('Jordan Samename'));
        CRA_ContactSearchAction.Response restricted;
        System.runAs(uat()) { restricted = search(byName('Jordan Samename')); }
        System.assertEquals('DUPLICATE_IDENTIFIER 3', admin.outcomeCode + ' ' + admin.totalMatchesLabel, describe(admin));
        System.assertEquals('DUPLICATE_IDENTIFIER 2', restricted.outcomeCode + ' ' + restricted.totalMatchesLabel,
            describe(restricted));
        System.assert(String.isBlank(restricted.singleContactId), 'No automatic selection');
        System.assert(!restricted.contactsJson.contains('Hiddenburg'), 'Private duplicate leaked');
    }

    /*****************************************************************
    Tests:     A shared email: the admin gets a duplicate, the UAT user
               gets Priya only, with no hint of the private record.
    *****************************************************************/
    @isTest
    static void sharingSharedEmail() {
        CRA_ContactSearchAction.Response admin = search(byEmail(PRIYA_EMAIL));
        CRA_ContactSearchAction.Response restricted;
        System.runAs(uat()) { restricted = search(byEmail(PRIYA_EMAIL)); }
        System.assertEquals('DUPLICATE_IDENTIFIER 2', admin.outcomeCode + ' ' + admin.totalMatchesLabel, describe(admin));
        System.assertEquals('SINGLE_MATCH 1', restricted.outcomeCode + ' ' + restricted.totalMatchesLabel,
            describe(restricted));
        System.assert(!restricted.searchResultJson.contains('Shadowell'), 'Private Contact leaked');
        System.assert(!restricted.searchResultJson.toLowerCase().contains('duplicate'), 'Duplicate hinted');
    }

    /*****************************************************************
    Tests:     Thresholds follow sharing: 11 for the admin (refine),
               8 for the UAT user (first 5, offer the other 3), and the
               remaining page holds no private Contact.
    *****************************************************************/
    @isTest
    static void sharingThresholdsAndRemaining() {
        CRA_ContactSearchAction.Response admin = search(byTitle('Synthetic Coordinator'));
        CRA_ContactSearchAction.Response restricted;
        CRA_ContactSearchAction.Response rest;
        System.runAs(uat()) {
            restricted = search(byTitle('Synthetic Coordinator'));
            CRA_ContactSearchAction.Request more = byTitle('Synthetic Coordinator');
            more.showRemaining = true;
            rest = search(more);
        }
        System.assertEquals('LIST_11_TO_100 11', admin.outcomeCode + ' ' + admin.totalMatchesLabel, describe(admin));
        System.assert(admin.refinementRequired, 'Admin must refine');
        System.assertEquals('LIST_6_TO_10 8 5 3', restricted.outcomeCode + ' ' + restricted.totalMatchesLabel + ' '
            + restricted.shownCount + ' ' + restricted.remainingCount, describe(restricted));
        System.assert(restricted.canShowRemaining, 'Offer the remaining 3');
        System.assertEquals('REMAINING_PAGE 3', rest.outcomeCode + ' ' + rest.shownCount, describe(rest));
        System.assert(!(restricted.contactsJson + rest.contactsJson).contains('Hidden'), 'Private coordinator leaked');
    }

    /*****************************************************************
    Tests:     A private Contact is invisible by name and by Id (a
               neutral no-match that does not confirm it exists); the
               admin finds it.
    *****************************************************************/
    @isTest
    static void sharingPrivateContactByNameAndId() {
        Id privateId = [SELECT Id FROM Contact WHERE Email = 'zed.hiddenmore@synthetic.example' LIMIT 1].Id;
        CRA_ContactSearchAction.Response admin = search(byName('Zed Hiddenmore'));
        CRA_ContactSearchAction.Response viaName;
        CRA_ContactSearchAction.Response viaId;
        CRA_ContactSearchAction.Response viaField;
        CRA_ContactSearchAction.Response fake;
        System.runAs(uat()) {
            viaName = search(byName('Zed Hiddenmore'));
            CRA_ContactSearchAction.Request fakeRequest = req(); fakeRequest.contactId = '003000000000000AAA';
            fake = search(fakeRequest);
            CRA_ContactSearchAction.Request idRequest = req(); idRequest.contactId = privateId;
            viaId = search(idRequest);
            CRA_ContactSearchAction.Request fieldRequest = req(); fieldRequest.contactId = privateId;
            fieldRequest.requestedField = 'Email';
            viaField = search(fieldRequest);
        }
        System.assertEquals('SINGLE_MATCH', admin.outcomeCode, describe(admin));
        System.assertEquals('NO_MATCH', viaName.outcomeCode, describe(viaName));
        System.assertEquals('NO_MATCH', viaId.outcomeCode, describe(viaId));
        System.assertEquals('NO_MATCH', viaField.outcomeCode, describe(viaField));
        // The criteria summary repeats the user's own words, so only the returned Contact data is checked.
        String rows = viaName.contactsJson + viaId.contactsJson + viaField.contactsJson;
        System.assert(!rows.contains('Hiddenmore') && !rows.contains('zed.hiddenmore'), 'Private Contact leaked: ' + rows);
        System.assertEquals(0, viaName.shownCount + viaId.shownCount + viaField.shownCount, 'Nothing shown');
        System.assertEquals(fake.outcomeCode + '|' + fake.userMessage + '|' + fake.totalMatchesLabel,
            viaId.outcomeCode + '|' + viaId.userMessage + '|' + viaId.totalMatchesLabel,
            'A private Id must look exactly like an Id that does not exist');
    }

    /*****************************************************************
    Tests:     Account-size outcomes for the UAT user: 22 (refine) and
               more than 100 (ask for filters, show nothing).
    *****************************************************************/
    @isTest
    static void sharingLargeAccounts() {
        CRA_ContactSearchAction.Response northwind;
        CRA_ContactSearchAction.Response bulkAccount;
        System.runAs(uat()) {
            northwind = search(byAccount('CRA-TEST Northwind Synthetic'));
            bulkAccount = search(byAccount('CRA-TEST Bulk Synthetic'));
        }
        System.assertEquals('LIST_11_TO_100 22 5', northwind.outcomeCode + ' ' + northwind.totalMatchesLabel + ' '
            + northwind.shownCount, describe(northwind));
        System.assertEquals('TOO_MANY more than 100 0', bulkAccount.outcomeCode + ' ' + bulkAccount.totalMatchesLabel + ' '
            + bulkAccount.shownCount, describe(bulkAccount));
    }

    /*****************************************************************
    Tests:     Read-only at platform level: sharing gives the UAT user
               Read on a public-Account Contact (UserRecordAccess), the
               object permission blocks edit, and a direct update by
               the user is refused. The CRA action contains no DML.
    *****************************************************************/
    @isTest
    static void restrictedUserCannotEdit() {
        User restrictedUser = uat();
        Contact priya = [SELECT Id, Title FROM Contact WHERE Email = :PRIYA_EMAIL AND AccountId != null LIMIT 1];
        UserRecordAccess access = [SELECT RecordId, HasReadAccess, HasEditAccess FROM UserRecordAccess
            WHERE UserId = :restrictedUser.Id AND RecordId = :priya.Id];
        Boolean updateable;
        Database.SaveResult attempt;
        System.runAs(restrictedUser) {
            updateable = Schema.SObjectType.Contact.isUpdateable();
            attempt = Database.update(new Contact(Id = priya.Id, Title = 'CFO'), false, AccessLevel.USER_MODE);
        }
        System.assert(access.HasReadAccess, 'Sharing grants read');
        System.assert(!access.HasEditAccess, 'No effective edit');
        System.assert(!updateable, 'No Edit object permission');
        System.assert(!attempt.isSuccess(), 'Platform refused the update');
    }

    // =================================================================
    // Field-level security (limited set replaces the full set; in-test)
    // =================================================================

    /*****************************************************************
    Tests:     With DATA_Contact_Read_Limited_UAT INSTEAD of the full
               set, Email, MobilePhone and Mailing Address are "Not
               available", an email filter is refused neutrally, a
               number held only in MobilePhone does not match, and a
               follow-up for Email returns no value.
    *****************************************************************/
    @isTest
    static void fieldLevelSecurityLimitedSet() {
        User restrictedUser = uat();
        swapDataSet(restrictedUser.Id, LIMITED_SET);
        Id priyaId = [SELECT Id FROM Contact WHERE Email = :PRIYA_EMAIL AND AccountId != null LIMIT 1].Id;
        CRA_ContactSearchAction.Response viaName;
        CRA_ContactSearchAction.Response viaEmail;
        CRA_ContactSearchAction.Response viaMobile;
        CRA_ContactSearchAction.Response viaField;
        CRA_ContactSearchAction.Response table;
        Boolean emailReadable;
        System.runAs(restrictedUser) {
            emailReadable = Schema.SObjectType.Contact.fields.Email.isAccessible();
            viaName = search(byName('Priya Synthwell'));
            viaEmail = search(byEmail(PRIYA_EMAIL));
            CRA_ContactSearchAction.Request phoneRequest = req(); phoneRequest.phone = PRIYA_MOBILE;
            viaMobile = search(phoneRequest);
            CRA_ContactSearchAction.Request fieldRequest = req(); fieldRequest.contactId = priyaId;
            fieldRequest.requestedField = 'Email';
            viaField = search(fieldRequest);
            table = search(byName('Jordan Samename'));
        }
        System.assert(!emailReadable, 'Email must be unreadable with the limited set alone');
        System.assertEquals('SINGLE_MATCH', viaName.outcomeCode, describe(viaName));
        String rows = viaName.searchResultJson + viaField.searchResultJson + table.searchResultJson;
        System.assert(!rows.contains('synthetic.example'), 'An email address leaked');
        System.assert(!rows.contains('555 0201'), 'Mobile leaked');
        System.assert(!rows.contains('Testville') && !rows.contains('Mockton'), 'Address leaked');
        System.assert(viaName.contactsJson.contains('555 0101'), 'Readable Phone is shown');
        System.assertEquals('FILTER_UNAVAILABLE', viaEmail.outcomeCode, describe(viaEmail));
        System.assertEquals(0, viaEmail.shownCount, 'No rows through a hidden filter');
        System.assertEquals('NO_MATCH', viaMobile.outcomeCode, describe(viaMobile));
        System.assert(!viaField.searchResultJson.contains(PRIYA_EMAIL), 'Follow-up leaked the email');
        System.assertEquals('DUPLICATE_IDENTIFIER', table.outcomeCode, describe(table));
    }

    // =================================================================
    // Object permission (CRUD): no Contact Read at all (in-test)
    // =================================================================

    /*****************************************************************
    Tests:     With no DATA set, every search returns the neutral
               NO_MATCH: no counts, names or hints.
    *****************************************************************/
    @isTest
    static void noContactReadIsNeutral() {
        User restrictedUser = uat();
        swapDataSet(restrictedUser.Id, null);
        List<CRA_ContactSearchAction.Response> results = new List<CRA_ContactSearchAction.Response>();
        Boolean contactReadable;
        System.runAs(restrictedUser) {
            contactReadable = Schema.SObjectType.Contact.isAccessible();
            results.add(search(byName('Priya Synthwell')));
            results.add(search(byName('Jordan Samename')));
            results.add(search(byAccount('CRA-TEST Northwind Synthetic')));
            results.add(search(byEmail(PRIYA_EMAIL)));
        }
        System.assert(!contactReadable, 'No Contact Read');
        for (CRA_ContactSearchAction.Response r : results) {
            System.assertEquals('NO_MATCH', r.outcomeCode, describe(r));
            System.assertEquals(0, r.shownCount, 'Nothing shown');
            System.assertEquals('0', r.totalMatchesLabel, 'No count revealed');
            System.assert(!r.contactsJson.contains('Synthwell') && !r.contactsJson.contains('Samename'),
                'A name leaked: ' + r.contactsJson);
        }
    }
}
