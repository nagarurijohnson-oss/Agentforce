/*****************************************************************
Name:          CRA_TestDataFactory
============================================================
Purpose:       Synthetic test data for the SCGOE-95 Contact Read
               Agent tests. Every Account is named "CRA-TEST ..." and
               every Contact carries "CRA-TEST synthetic record" in its
               Description. Never touches real org data.
               Users and permission sets created here exist only
               inside the test transaction and are rolled back.
============================================================
History
-------
VERSION  AUTHOR                  DATE         DETAIL    DESCRIPTION
1.0      Revecast Orchestrate    19/11/2026   Created   SCGOE-95 Session 2
*****************************************************************/
@isTest
public class CRA_TestDataFactory {

    public static final String TEST_MARKER = 'CRA-TEST synthetic record';
    public static final String RESTRICTED_PROFILE = 'Minimum Access - Salesforce';

    /*****************************************************************
    Purpose:   Insert Accounts named "CRA-TEST <name>".
    Returns:   Accounts keyed by the short name passed in.
    *****************************************************************/
    public static Map<String, Account> createAccounts(List<String> shortNames) {
        Map<String, Account> accountsByName = new Map<String, Account>();
        for (String shortName : shortNames) {
            accountsByName.put(shortName, new Account(Name = 'CRA-TEST ' + shortName));
        }
        insertAllowingDuplicates(accountsByName.values());
        return accountsByName;
    }

    /*****************************************************************
    Purpose:   Build (not insert) a synthetic Contact. State and
               country are ISO codes because state and country
               picklists are enabled in the org.
    *****************************************************************/
    public static Contact buildContact(String firstName, String lastName, Id accountId) {
        return new Contact(
            FirstName = firstName,
            LastName = lastName,
            AccountId = accountId,
            Description = TEST_MARKER
        );
    }

    /*****************************************************************
    Purpose:   Set the identifying details on a built Contact.
    *****************************************************************/
    public static Contact withDetails(Contact record, String title, String email, String phone) {
        record.Title = title;
        record.Email = email;
        record.Phone = phone;
        return record;
    }

    /*****************************************************************
    Purpose:   Set the mailing address on a built Contact.
    *****************************************************************/
    public static Contact withAddress(Contact record, String street, String city, String stateCode,
            String postalCode, String countryCode) {
        record.MailingStreet = street;
        record.MailingCity = city;
        record.MailingStateCode = stateCode;
        record.MailingPostalCode = postalCode;
        record.MailingCountryCode = countryCode;
        return record;
    }

    /*****************************************************************
    Purpose:   Build a numbered set of Contacts sharing a title tag,
               e.g. tag "CRAB-006-" with size 6. Titles are unique
               per set so a "contains" title search hits one set only.
    *****************************************************************/
    public static List<Contact> buildTitleSet(String tag, Integer size, Id accountId) {
        List<Contact> records = new List<Contact>();
        for (Integer index = 1; index <= size; index++) {
            String suffix = String.valueOf(index).leftPad(3, '0');
            Contact record = buildContact('Set' + tag.replaceAll('[^0-9]', ''), 'Member' + suffix, accountId);
            record.Title = tag + 'X';
            records.add(record);
        }
        return records;
    }

    /*****************************************************************
    Purpose:   Insert records, allowing the org's standard duplicate
               rules to pass (several tests need duplicates on purpose).
    *****************************************************************/
    public static void insertAllowingDuplicates(List<SObject> records) {
        Database.DMLOptions options = new Database.DMLOptions();
        options.DuplicateRuleHeader.allowSave = true;
        options.DuplicateRuleHeader.runAsCurrentUser = true;
        List<Database.SaveResult> results = Database.insert(records, options);
        for (Database.SaveResult saveResult : results) {
            System.assert(saveResult.isSuccess(), 'Test data insert failed: ' + saveResult.getErrors());
        }
    }

    /*****************************************************************
    Purpose:   Create a user on the Minimum Access - Salesforce profile
               with a test-only permission set granting the given
               object reads and Contact field reads. Runs the setup
               DML as the current user to avoid mixed-DML errors.
    Parameters: alias         — up to 8 characters, unique per test
                objectReads   — e.g. {'Account','Contact'}; empty for none
                contactFields — e.g. {'Title','MailingAddress'}
    *****************************************************************/
    public static User createRestrictedUser(String alias, List<String> objectReads, List<String> contactFields) {
        User restricted;
        System.runAs(new User(Id = UserInfo.getUserId())) {
            Profile minimumAccess = [SELECT Id FROM Profile WHERE Name = :RESTRICTED_PROFILE LIMIT 1];
            restricted = new User(
                ProfileId = minimumAccess.Id,
                LastName = 'CRA-TEST ' + alias,
                Alias = alias,
                Email = alias + '@cra-test.example.com',
                Username = alias + '.' + UserInfo.getOrganizationId() + '@cra-test.example.com',
                TimeZoneSidKey = 'Asia/Kolkata',
                LocaleSidKey = 'en_US',
                EmailEncodingKey = 'UTF-8',
                LanguageLocaleKey = 'en_US'
            );
            insert restricted;
            if (!objectReads.isEmpty()) {
                grantReads(restricted.Id, alias, objectReads, contactFields);
            }
        }
        return restricted;
    }

    /*****************************************************************
    Purpose:   Test-only permission set with object and field reads.
               Account read is inserted before Contact read because
               Contact read depends on it.
    *****************************************************************/
    private static void grantReads(Id userId, String alias, List<String> objectReads, List<String> contactFields) {
        PermissionSet grant = new PermissionSet(Name = 'CRA_TEST_' + alias, Label = 'CRA TEST ' + alias);
        insert grant;

        List<ObjectPermissions> objectPermissions = new List<ObjectPermissions>();
        for (String objectName : objectReads) {
            objectPermissions.add(new ObjectPermissions(
                ParentId = grant.Id, SobjectType = objectName, PermissionsRead = true));
        }
        insert objectPermissions;

        List<FieldPermissions> fieldPermissions = new List<FieldPermissions>();
        for (String fieldName : contactFields) {
            fieldPermissions.add(new FieldPermissions(
                ParentId = grant.Id, SobjectType = 'Contact', Field = 'Contact.' + fieldName,
                PermissionsRead = true, PermissionsEdit = false));
        }
        if (!fieldPermissions.isEmpty()) {
            insert fieldPermissions;
        }
        insert new PermissionSetAssignment(AssigneeId = userId, PermissionSetId = grant.Id);
    }

    /*****************************************************************
    Purpose:   Criteria with only a name, the most common shape.
    *****************************************************************/
    public static CRA_ContactSearchCriteria byName(String name) {
        CRA_ContactSearchCriteria criteria = new CRA_ContactSearchCriteria();
        criteria.name = name;
        return criteria;
    }
}
