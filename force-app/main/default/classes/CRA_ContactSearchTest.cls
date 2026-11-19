/*****************************************************************
Name:          CRA_ContactSearchTest
============================================================
Purpose:       Functional tests for CRA_ContactSearchService and
               CRA_ContactSearchCriteria: every outcome code, the
               count boundaries 0, 1, 2, 5, 6, 10, 11, 100 and 101,
               duplicates, phone formats, refinement, follow-ups,
               input validation and injection payloads.
               Runs as the deploying administrator with synthetic
               CRA-TEST data only. Security tests that run as a
               restricted user are in CRA_ContactSearchSecurityTest.
============================================================
History
-------
VERSION  AUTHOR                  DATE         DETAIL    DESCRIPTION
1.0      Revecast Orchestrate    19/11/2026   Created   SCGOE-95 Session 2
*****************************************************************/
@isTest
private class CRA_ContactSearchTest {

    private static final String AVA_EMAIL = 'ava.lindqvist@acme.example.com';

    /*****************************************************************
    Purpose:   Named Contacts for outcome tests, plus numbered sets
               for the count boundaries (title tag CRAB-nnn-).
               245 Contacts in total, all synthetic.
    *****************************************************************/
    @testSetup
    static void createData() {
        Map<String, Account> accounts = CRA_TestDataFactory.createAccounts(
            new List<String>{ 'Acme', 'Globex', 'Initech', 'Hooli', 'Bulk' });
        Id acme = accounts.get('Acme').Id;
        Id globex = accounts.get('Globex').Id;
        Id initech = accounts.get('Initech').Id;

        List<Contact> records = new List<Contact>();
        records.add(CRA_TestDataFactory.withAddress(CRA_TestDataFactory.withDetails(
            CRA_TestDataFactory.buildContact('Ava', 'Lindqvist', acme),
            'Head of Procurement', AVA_EMAIL, '(212) 842-5500'),
            '1 Main Street', 'New York', 'NY', '10001', 'US'));
        records.add(CRA_TestDataFactory.withDetails(CRA_TestDataFactory.buildContact('John', 'Smith', acme),
            'Engineer', 'john.smith1@acme.example.com', '(415) 555-0101'));
        records.add(CRA_TestDataFactory.withDetails(CRA_TestDataFactory.buildContact('John', 'Smith', globex),
            'Analyst', 'john.smith2@globex.example.com', '(415) 555-0102'));
        records.add(CRA_TestDataFactory.withDetails(CRA_TestDataFactory.buildContact('Maria', 'Garcia', globex),
            'Buyer', 'm.garcia@globex.example.com', '(415) 555-0103'));
        records.add(CRA_TestDataFactory.withDetails(CRA_TestDataFactory.buildContact('Mario', 'Garcia', globex),
            'Buyer', 'm.garcia@globex.example.com', '(415) 555-0104'));
        records.add(CRA_TestDataFactory.withDetails(CRA_TestDataFactory.buildContact('Liam', 'Chen', initech),
            'Support', 'liam.chen@initech.example.com', '212-842-5599'));
        records.add(CRA_TestDataFactory.withDetails(CRA_TestDataFactory.buildContact('Noah', 'Chen', initech),
            'Support', 'noah.chen@initech.example.com', '(212) 842-5599'));
        records.add(CRA_TestDataFactory.withAddress(CRA_TestDataFactory.withDetails(
            CRA_TestDataFactory.buildContact('Olivia', 'Brown', initech),
            'Director', 'olivia.brown@initech.example.com', '+44 191 4956203'),
            '10 Quayside', 'Newcastle upon Tyne', null, 'NE1 3DX', 'GB'));
        records.add(CRA_TestDataFactory.buildContact('Ethan', 'Missing', accounts.get('Hooli').Id));

        Id bulkAccount = accounts.get('Bulk').Id;
        for (Integer size : new List<Integer>{ 1, 2, 5, 6, 10, 11, 100, 101 }) {
            records.addAll(CRA_TestDataFactory.buildTitleSet(tag(size), size, bulkAccount));
        }
        CRA_TestDataFactory.insertAllowingDuplicates(records);
    }

    // ---------------------------------------------------------------
    // Helpers
    // ---------------------------------------------------------------

    private static String tag(Integer size) {
        return 'CRAB-' + String.valueOf(size).leftPad(3, '0') + '-';
    }

    private static CRA_ContactSearchResult run(CRA_ContactSearchCriteria criteria) {
        return new CRA_ContactSearchService().search(criteria);
    }

    private static CRA_ContactSearchResult searchTitleSet(Integer size, Boolean showRemaining) {
        CRA_ContactSearchCriteria criteria = new CRA_ContactSearchCriteria();
        criteria.jobTitle = tag(size);
        criteria.showRemaining = showRemaining;
        return run(criteria);
    }

    private static CRA_ContactSearchResult searchPhone(String phone) {
        CRA_ContactSearchCriteria criteria = new CRA_ContactSearchCriteria();
        criteria.phone = phone;
        return run(criteria);
    }

    private static void assertOutcome(String expected, CRA_ContactSearchResult result, String scenario) {
        System.assertEquals(expected, result.outcomeCode, scenario + ': ' + result.userMessage);
    }

    // ---------------------------------------------------------------
    // NEEDS_CLARIFICATION
    // ---------------------------------------------------------------

    /*****************************************************************
    Tests:     No filter in any shape returns NEEDS_CLARIFICATION.
    *****************************************************************/
    @isTest
    static void noFilterNeedsClarification() {
        CRA_ContactSearchCriteria onlyField = new CRA_ContactSearchCriteria();
        onlyField.requestedField = 'Email';
        CRA_ContactSearchCriteria onlyRemaining = new CRA_ContactSearchCriteria();
        onlyRemaining.showRemaining = true;

        Test.startTest();
        List<CRA_ContactSearchResult> results = new List<CRA_ContactSearchResult>{
            run(null), run(new CRA_ContactSearchCriteria()), run(onlyField), run(onlyRemaining),
            run(CRA_TestDataFactory.byName('    '))
        };
        Test.stopTest();

        for (CRA_ContactSearchResult result : results) {
            assertOutcome(CRA_ContactSearchResult.NEEDS_CLARIFICATION, result, 'no filter');
            System.assert(result.contacts.isEmpty(), 'No rows without a filter');
            System.assert(String.isNotBlank(result.userMessage), 'A clarification message is given');
        }
    }

    /*****************************************************************
    Tests:     Invalid inputs ask for clarification and never search.
    *****************************************************************/
    @isTest
    static void invalidInputsNeedClarification() {
        CRA_ContactSearchCriteria badField = CRA_TestDataFactory.byName('Ava');
        badField.requestedField = 'Salary';
        CRA_ContactSearchCriteria malformedId = new CRA_ContactSearchCriteria();
        malformedId.contactId = 'not-an-id';
        CRA_ContactSearchCriteria accountAsContact = new CRA_ContactSearchCriteria();
        accountAsContact.contactId = [SELECT Id FROM Account LIMIT 1].Id;

        Test.startTest();
        List<CRA_ContactSearchResult> results = new List<CRA_ContactSearchResult>{
            run(badField), run(malformedId), run(accountAsContact),
            run(CRA_TestDataFactory.byName('one two three four five six')),
            searchPhone('842'), searchPhone('call me maybe 12345678'), searchPhone('0000000123')
        };
        Test.stopTest();

        for (CRA_ContactSearchResult result : results) {
            assertOutcome(CRA_ContactSearchResult.NEEDS_CLARIFICATION, result, 'invalid input');
            System.assert(result.contacts.isEmpty(), 'Invalid input returns no rows');
        }
    }

    // ---------------------------------------------------------------
    // SINGLE_MATCH and FIELD_ANSWER
    // ---------------------------------------------------------------

    /*****************************************************************
    Tests:     Full-name match returns every contract field and a link.
    *****************************************************************/
    @isTest
    static void singleMatchReturnsAllFieldsAndLink() {
        Test.startTest();
        CRA_ContactSearchResult result = run(CRA_TestDataFactory.byName('Ava Lindqvist'));
        Test.stopTest();

        assertOutcome(CRA_ContactSearchResult.SINGLE_MATCH, result, 'full name');
        System.assertEquals('1', result.totalMatchesLabel);
        System.assertEquals(1, result.shownCount);
        System.assertEquals(0, result.remainingCount);
        CRA_ContactSearchResult.ContactRow row = result.contacts[0];
        System.assertEquals(result.singleContactId, row.id);
        System.assertEquals('Ava Lindqvist', row.name);
        System.assertEquals('CRA-TEST Acme', row.accountName);
        System.assertEquals('Head of Procurement', row.title);
        System.assertEquals(AVA_EMAIL, row.email);
        System.assertEquals('(212) 842-5500', row.phone);
        System.assert(row.mailingAddress.startsWith('1 Main Street, New York'), row.mailingAddress);
        System.assert(row.contactUrl.endsWith('/lightning/r/Contact/' + row.id + '/view'), row.contactUrl);
        System.assert(row.contactUrl.startsWith('https://'), 'Absolute My Domain link');
        System.assertEquals(1, row.n);
        System.assertEquals(row.id, result.getResultContactIds());
    }

    /*****************************************************************
    Tests:     Partial name (start of last name) and control characters
               inside a name still find the one Contact.
    *****************************************************************/
    @isTest
    static void partialNameAndControlCharactersMatch() {
        String control = String.fromCharArray(new List<Integer>{ 0, 7, 27 });
        Test.startTest();
        CRA_ContactSearchResult partial = run(CRA_TestDataFactory.byName('Lindq'));
        CRA_ContactSearchResult withControl = run(CRA_TestDataFactory.byName('Ava' + control + 'Lindqvist'));
        CRA_ContactSearchResult onlyControl = run(CRA_TestDataFactory.byName(control));
        Test.stopTest();

        assertOutcome(CRA_ContactSearchResult.SINGLE_MATCH, partial, 'partial name');
        assertOutcome(CRA_ContactSearchResult.SINGLE_MATCH, withControl, 'control characters');
        System.assertEquals('Name: Ava Lindqvist', withControl.criteriaSummary);
        assertOutcome(CRA_ContactSearchResult.NEEDS_CLARIFICATION, onlyControl, 'only control characters');
    }

    /*****************************************************************
    Tests:     Missing values read "Not available".
    *****************************************************************/
    @isTest
    static void missingValuesReadNotAvailable() {
        Test.startTest();
        CRA_ContactSearchResult result = run(CRA_TestDataFactory.byName('Ethan Missing'));
        Test.stopTest();

        assertOutcome(CRA_ContactSearchResult.SINGLE_MATCH, result, 'missing values');
        CRA_ContactSearchResult.ContactRow row = result.contacts[0];
        System.assertEquals(CRA_ContactSearchResult.NOT_AVAILABLE, row.title);
        System.assertEquals(CRA_ContactSearchResult.NOT_AVAILABLE, row.email);
        System.assertEquals(CRA_ContactSearchResult.NOT_AVAILABLE, row.phone);
        System.assertEquals(CRA_ContactSearchResult.NOT_AVAILABLE, row.mailingAddress);
        System.assertEquals('CRA-TEST Hooli', row.accountName);
    }

    /*****************************************************************
    Tests:     A requested field returns only that field, the name and
               the link (O7), including "Not available" when empty.
    *****************************************************************/
    @isTest
    static void fieldAnswerReturnsOnlyRequestedField() {
        CRA_ContactSearchCriteria emailAsk = CRA_TestDataFactory.byName('Ava Lindqvist');
        emailAsk.requestedField = 'email address';
        CRA_ContactSearchCriteria phoneAsk = CRA_TestDataFactory.byName('Ethan Missing');
        phoneAsk.requestedField = 'Phone Number';

        Test.startTest();
        CRA_ContactSearchResult email = run(emailAsk);
        CRA_ContactSearchResult phone = run(phoneAsk);
        Test.stopTest();

        assertOutcome(CRA_ContactSearchResult.FIELD_ANSWER, email, 'email asked');
        System.assertEquals('Email', email.requestedFieldLabel);
        System.assertEquals(AVA_EMAIL, email.contacts[0].email);
        System.assertEquals(null, email.contacts[0].title, 'Other fields are not returned');
        System.assertEquals(null, email.contacts[0].phone, 'Other fields are not returned');
        String json = email.getContactsJson();
        System.assert(json.contains(AVA_EMAIL) && !json.contains('Procurement'), json);
        System.assert(!json.contains('"title"') && json.contains('"contactUrl"'), json);

        assertOutcome(CRA_ContactSearchResult.FIELD_ANSWER, phone, 'empty field asked');
        System.assertEquals(CRA_ContactSearchResult.NOT_AVAILABLE, phone.contacts[0].phone);
    }

    /*****************************************************************
    Tests:     Every requestable field resolves, including address.
    *****************************************************************/
    @isTest
    static void everyRequestedFieldResolves() {
        Map<String, String> askToLabel = new Map<String, String>{
            'Name' => 'Name', 'company' => 'Account', 'job title' => 'Title',
            'Mailing Address' => 'Mailing address', 'phone' => 'Phone'
        };
        Test.startTest();
        for (String ask : askToLabel.keySet()) {
            CRA_ContactSearchCriteria criteria = CRA_TestDataFactory.byName('Olivia Brown');
            criteria.requestedField = ask;
            CRA_ContactSearchResult result = run(criteria);
            assertOutcome(CRA_ContactSearchResult.FIELD_ANSWER, result, ask);
            System.assertEquals(askToLabel.get(ask), result.requestedFieldLabel);
        }
        Test.stopTest();

        CRA_ContactSearchCriteria addressAsk = CRA_TestDataFactory.byName('Olivia Brown');
        addressAsk.requestedField = 'address';
        CRA_ContactSearchResult.ContactRow row = run(addressAsk).contacts[0];
        System.assert(row.mailingAddress.contains('Newcastle upon Tyne'), row.mailingAddress);
        System.assertEquals(null, row.email);
    }

    /*****************************************************************
    Tests:     Follow-up on a previously identified Contact (R3).
    *****************************************************************/
    @isTest
    static void followUpByContactId() {
        Contact ava = [SELECT Id FROM Contact WHERE Email = :AVA_EMAIL LIMIT 1];
        Contact gone = CRA_TestDataFactory.buildContact('Temp', 'Deleted', null);
        CRA_TestDataFactory.insertAllowingDuplicates(new List<Contact>{ gone });
        delete gone;

        CRA_ContactSearchCriteria titleAsk = new CRA_ContactSearchCriteria();
        titleAsk.contactId = ava.Id;
        titleAsk.requestedField = 'title';
        CRA_ContactSearchCriteria deletedAsk = new CRA_ContactSearchCriteria();
        deletedAsk.contactId = gone.Id;

        Test.startTest();
        CRA_ContactSearchResult title = run(titleAsk);
        CRA_ContactSearchResult deleted = run(deletedAsk);
        Test.stopTest();

        assertOutcome(CRA_ContactSearchResult.FIELD_ANSWER, title, 'follow-up by id');
        System.assertEquals('Head of Procurement', title.contacts[0].title);
        System.assertEquals('Selected Contact: yes', title.criteriaSummary);
        assertOutcome(CRA_ContactSearchResult.NO_MATCH, deleted, 'deleted id');
        System.assertEquals(CRA_ContactSearchService.NO_MATCH_MESSAGE, deleted.userMessage);
    }

    // ---------------------------------------------------------------
    // Multiple filters and refinement
    // ---------------------------------------------------------------

    /*****************************************************************
    Tests:     Adding a filter refines a duplicate down to one (R3).
    *****************************************************************/
    @isTest
    static void refinementNarrowsToOne() {
        CRA_ContactSearchCriteria refined = CRA_TestDataFactory.byName('John Smith');
        refined.accountName = 'Globex';
        CRA_ContactSearchCriteria byTitle = CRA_TestDataFactory.byName('John');
        byTitle.jobTitle = 'analy';

        Test.startTest();
        CRA_ContactSearchResult first = run(CRA_TestDataFactory.byName('John Smith'));
        CRA_ContactSearchResult second = run(refined);
        CRA_ContactSearchResult third = run(byTitle);
        Test.stopTest();

        assertOutcome(CRA_ContactSearchResult.DUPLICATE_IDENTIFIER, first, 'before refinement');
        assertOutcome(CRA_ContactSearchResult.SINGLE_MATCH, second, 'name + account');
        System.assertEquals('CRA-TEST Globex', second.contacts[0].accountName);
        System.assertEquals('Name: John Smith; Account name: Globex', second.criteriaSummary);
        assertOutcome(CRA_ContactSearchResult.SINGLE_MATCH, third, 'name + title');
    }

    /*****************************************************************
    Tests:     Location filters on city, state, country and the
               combined location input.
    *****************************************************************/
    @isTest
    static void locationFilters() {
        CRA_ContactSearchCriteria cityAndState = new CRA_ContactSearchCriteria();
        cityAndState.city = 'New York';
        cityAndState.stateOrRegion = 'NY';
        CRA_ContactSearchCriteria countryCode = new CRA_ContactSearchCriteria();
        countryCode.country = 'GB';
        CRA_ContactSearchCriteria countryName = new CRA_ContactSearchCriteria();
        countryName.country = 'United Kingdom';
        CRA_ContactSearchCriteria stateName = new CRA_ContactSearchCriteria();
        stateName.stateOrRegion = 'New York';
        CRA_ContactSearchCriteria broad = new CRA_ContactSearchCriteria();
        broad.location = 'New';
        CRA_ContactSearchCriteria city = new CRA_ContactSearchCriteria();
        city.location = 'Newcastle';

        Test.startTest();
        assertOutcome(CRA_ContactSearchResult.SINGLE_MATCH, run(cityAndState), 'city + state code');
        assertOutcome(CRA_ContactSearchResult.SINGLE_MATCH, run(stateName), 'state name');
        System.assertEquals('Olivia Brown', run(countryCode).contacts[0].name, 'country code');
        System.assertEquals('Olivia Brown', run(countryName).contacts[0].name, 'country name');
        assertOutcome(CRA_ContactSearchResult.SINGLE_MATCH, run(city), 'location city');
        CRA_ContactSearchResult both = run(broad);
        Test.stopTest();

        assertOutcome(CRA_ContactSearchResult.LIST_2_TO_5, both, 'New York and Newcastle');
        System.assertEquals(2, both.shownCount);
    }

    /*****************************************************************
    Tests:     Partial email (no "@") is a contains match and is not
               treated as a duplicate identifier.
    *****************************************************************/
    @isTest
    static void partialEmailIsListNotDuplicate() {
        CRA_ContactSearchCriteria criteria = new CRA_ContactSearchCriteria();
        criteria.email = 'acme.example';
        Test.startTest();
        CRA_ContactSearchResult result = run(criteria);
        Test.stopTest();
        assertOutcome(CRA_ContactSearchResult.LIST_2_TO_5, result, 'partial email');
        System.assertEquals(2, result.shownCount);
    }

    // ---------------------------------------------------------------
    // DUPLICATE_IDENTIFIER (decision D-B)
    // ---------------------------------------------------------------

    /*****************************************************************
    Tests:     Shared full name, exact email and phone are duplicates;
               a single-word name and an Account-only search are not.
    *****************************************************************/
    @isTest
    static void duplicateIdentifiers() {
        CRA_ContactSearchCriteria sharedEmail = new CRA_ContactSearchCriteria();
        sharedEmail.email = 'M.Garcia@globex.example.com';
        CRA_ContactSearchCriteria accountOnly = new CRA_ContactSearchCriteria();
        accountOnly.accountName = 'Initech';

        Test.startTest();
        CRA_ContactSearchResult name = run(CRA_TestDataFactory.byName('john  smith'));
        CRA_ContactSearchResult email = run(sharedEmail);
        CRA_ContactSearchResult phone = searchPhone('212.842.5599');
        CRA_ContactSearchResult lastNameOnly = run(CRA_TestDataFactory.byName('Smith'));
        CRA_ContactSearchResult account = run(accountOnly);
        CRA_ContactSearchResult similarNames = run(CRA_TestDataFactory.byName('Mari Garcia'));
        Test.stopTest();

        assertOutcome(CRA_ContactSearchResult.DUPLICATE_IDENTIFIER, name, 'shared name');
        System.assertEquals('Name', name.duplicateOn);
        System.assertEquals(2, name.shownCount);
        assertOutcome(CRA_ContactSearchResult.DUPLICATE_IDENTIFIER, email, 'shared email');
        System.assertEquals('Email', email.duplicateOn);
        assertOutcome(CRA_ContactSearchResult.DUPLICATE_IDENTIFIER, phone, 'shared phone');
        System.assertEquals('Phone', phone.duplicateOn);
        System.assertEquals(2, phone.shownCount, 'Both phone formats match');
        assertOutcome(CRA_ContactSearchResult.LIST_2_TO_5, lastNameOnly, 'single word is not exact');
        assertOutcome(CRA_ContactSearchResult.LIST_2_TO_5, account, 'Account-only over shared phone');
        System.assertEquals(null, account.duplicateOn);
        assertOutcome(CRA_ContactSearchResult.LIST_2_TO_5, similarNames, 'different full names');
    }

    // ---------------------------------------------------------------
    // Phone formats (decision D-F)
    // ---------------------------------------------------------------

    /*****************************************************************
    Tests:     US and UK formats match on digits; partial or short
               numbers do not widen the search.
    *****************************************************************/
    @isTest
    static void phoneFormatsMatchOnDigits() {
        Test.startTest();
        Map<String, String> expectedByInput = new Map<String, String>{
            '(212) 842-5500' => 'Ava Lindqvist',
            '212-842-5500' => 'Ava Lindqvist',
            '2128425500' => 'Ava Lindqvist',
            '+1 212 842 5500' => 'Ava Lindqvist',
            '+44 191 4956203' => 'Olivia Brown',
            '0191 4956203' => 'Olivia Brown',
            '191-495-6203' => 'Olivia Brown'
        };
        for (String input : expectedByInput.keySet()) {
            CRA_ContactSearchResult result = searchPhone(input);
            assertOutcome(CRA_ContactSearchResult.SINGLE_MATCH, result, input);
            System.assertEquals(expectedByInput.get(input), result.contacts[0].name, input);
        }
        CRA_ContactSearchResult local = searchPhone('842-5500');
        CRA_ContactSearchResult wrong = searchPhone('(212) 842-5501');
        Test.stopTest();

        assertOutcome(CRA_ContactSearchResult.NO_MATCH, local, 'seven digits must match exactly');
        assertOutcome(CRA_ContactSearchResult.NO_MATCH, wrong, 'one digit different');
    }

    /*****************************************************************
    Tests:     A full phone scan makes the count uncertain: TOO_MANY.
    *****************************************************************/
    @isTest
    static void fullPhoneScanIsTooMany() {
        CRA_ContactSearchService.phoneScanLimit = 1;
        Test.startTest();
        CRA_ContactSearchResult result = searchPhone('(212) 842-5599');
        Test.stopTest();
        assertOutcome(CRA_ContactSearchResult.TOO_MANY, result, 'scan limit reached');
        System.assert(result.contacts.isEmpty());
    }

    // ---------------------------------------------------------------
    // Count boundaries 0, 1, 2, 5, 6, 10, 11, 100, 101
    // ---------------------------------------------------------------

    @isTest
    static void boundaryZeroIsNoMatch() {
        CRA_ContactSearchCriteria criteria = new CRA_ContactSearchCriteria();
        criteria.jobTitle = 'CRAB-000-';
        Test.startTest();
        CRA_ContactSearchResult result = run(criteria);
        Test.stopTest();
        assertOutcome(CRA_ContactSearchResult.NO_MATCH, result, '0');
        System.assertEquals('0', result.totalMatchesLabel);
        System.assertEquals(CRA_ContactSearchService.NO_MATCH_MESSAGE, result.userMessage);
        System.assert(result.suggestedFiltersText.contains('Account name'), result.suggestedFiltersText);
        System.assert(!result.suggestedFiltersText.contains('job title'), 'Used filter not suggested');
    }

    @isTest
    static void boundaryOneIsSingleMatch() {
        Test.startTest();
        CRA_ContactSearchResult result = searchTitleSet(1, false);
        Test.stopTest();
        assertOutcome(CRA_ContactSearchResult.SINGLE_MATCH, result, '1');
    }

    @isTest
    static void boundaryTwoAndFiveAreSmallList() {
        Test.startTest();
        CRA_ContactSearchResult two = searchTitleSet(2, false);
        CRA_ContactSearchResult five = searchTitleSet(5, true);
        Test.stopTest();
        assertOutcome(CRA_ContactSearchResult.LIST_2_TO_5, two, '2');
        System.assertEquals(2, two.shownCount);
        assertOutcome(CRA_ContactSearchResult.LIST_2_TO_5, five, '5 (show remaining ignored)');
        System.assertEquals(5, five.shownCount);
        System.assertEquals(0, five.remainingCount);
        System.assertEquals(5, five.getResultContactIds().split(',').size());
    }

    @isTest
    static void boundarySixAndTenShowFirstFive() {
        Test.startTest();
        CRA_ContactSearchResult six = searchTitleSet(6, false);
        CRA_ContactSearchResult ten = searchTitleSet(10, false);
        Test.stopTest();
        assertOutcome(CRA_ContactSearchResult.LIST_6_TO_10, six, '6');
        System.assertEquals(5, six.shownCount);
        System.assertEquals(1, six.remainingCount);
        assertOutcome(CRA_ContactSearchResult.LIST_6_TO_10, ten, '10');
        System.assertEquals(5, ten.shownCount);
        System.assertEquals(5, ten.remainingCount);
        System.assertEquals('Set010 Member001', ten.contacts[0].name, 'Ordered by name');
    }

    @isTest
    static void boundaryTenRemainingPage() {
        Test.startTest();
        CRA_ContactSearchResult rest = searchTitleSet(10, true);
        CRA_ContactSearchResult sixRest = searchTitleSet(6, true);
        Test.stopTest();
        assertOutcome(CRA_ContactSearchResult.REMAINING_PAGE, rest, '10 remaining');
        System.assertEquals(5, rest.shownCount);
        System.assertEquals(0, rest.remainingCount);
        System.assertEquals(6, rest.contacts[0].n, 'Continues numbering');
        System.assertEquals('Set010 Member006', rest.contacts[0].name);
        assertOutcome(CRA_ContactSearchResult.REMAINING_PAGE, sixRest, '6 remaining');
        System.assertEquals(1, sixRest.shownCount);
    }

    @isTest
    static void boundaryElevenAndHundredSuggestFilters() {
        Test.startTest();
        CRA_ContactSearchResult eleven = searchTitleSet(11, true);
        CRA_ContactSearchResult hundred = searchTitleSet(100, false);
        Test.stopTest();
        assertOutcome(CRA_ContactSearchResult.LIST_11_TO_100, eleven, '11 (no show more, D-C)');
        System.assertEquals(5, eleven.shownCount);
        System.assertEquals(6, eleven.remainingCount);
        System.assert(String.isNotBlank(eleven.suggestedFiltersText));
        assertOutcome(CRA_ContactSearchResult.LIST_11_TO_100, hundred, '100');
        System.assertEquals('100', hundred.totalMatchesLabel);
        System.assertEquals(5, hundred.shownCount);
    }

    @isTest
    static void boundaryHundredOneIsTooMany() {
        Test.startTest();
        CRA_ContactSearchResult result = searchTitleSet(101, false);
        Test.stopTest();
        assertOutcome(CRA_ContactSearchResult.TOO_MANY, result, '101');
        System.assertEquals('more than 100', result.totalMatchesLabel);
        System.assertEquals(0, result.shownCount);
        System.assert(result.contacts.isEmpty(), 'No rows when too many');
        System.assertEquals('[]', result.getContactsJson());
    }

    // ---------------------------------------------------------------
    // Injection and hostile input
    // ---------------------------------------------------------------

    /*****************************************************************
    Tests:     Injection payloads in every text filter never throw and
               never widen results.
    *****************************************************************/
    @isTest
    static void injectionPayloadsNeverWiden() {
        List<String> payloads = new List<String>{
            '\' OR Name != \'', '%', '_', '\\', '%%', '\\%', '_%_', '\' OR \'1\'=\'1'
        };
        Test.startTest();
        for (String payload : payloads) {
            for (Integer filterIndex = 0; filterIndex < 5; filterIndex++) {
                CRA_ContactSearchCriteria criteria = new CRA_ContactSearchCriteria();
                if (filterIndex == 0) { criteria.name = payload; }
                if (filterIndex == 1) { criteria.email = payload; }
                if (filterIndex == 2) { criteria.accountName = payload; }
                if (filterIndex == 3) { criteria.jobTitle = payload; }
                if (filterIndex == 4) { criteria.location = payload; }
                CRA_ContactSearchResult result = run(criteria);
                assertOutcome(CRA_ContactSearchResult.NO_MATCH, result, payload + ' in filter ' + filterIndex);
                System.assert(result.contacts.isEmpty(), 'Payload widened results');
            }
        }
        Test.stopTest();
    }

    /*****************************************************************
    Tests:     Over-long values are rejected, not truncated.
    *****************************************************************/
    @isTest
    static void overLongValuesRejected() {
        String longValue = 'A'.repeat(5000);
        Test.startTest();
        for (Integer filterIndex = 0; filterIndex < 4; filterIndex++) {
            CRA_ContactSearchCriteria criteria = new CRA_ContactSearchCriteria();
            if (filterIndex == 0) { criteria.name = longValue; }
            if (filterIndex == 1) { criteria.email = longValue; }
            if (filterIndex == 2) { criteria.accountName = longValue; }
            if (filterIndex == 3) { criteria.phone = '1'.repeat(5000); }
            assertOutcome(CRA_ContactSearchResult.NEEDS_CLARIFICATION, run(criteria), 'long ' + filterIndex);
        }
        Test.stopTest();
    }

    // ---------------------------------------------------------------
    // ERROR, bulk entry point and helpers
    // ---------------------------------------------------------------

    /*****************************************************************
    Tests:     A failure becomes ERROR with no internal detail.
    *****************************************************************/
    @isTest
    static void failureReturnsSanitisedError() {
        CRA_ContactSearchService.forceFailureForTest = true;
        Test.startTest();
        CRA_ContactSearchResult result = run(CRA_TestDataFactory.byName('Ava'));
        Test.stopTest();
        assertOutcome(CRA_ContactSearchResult.ERROR, result, 'forced failure');
        System.assertEquals(CRA_ContactSearchService.ERROR_MESSAGE, result.userMessage);
        System.assert(!result.userMessage.contains('Exception') && !result.userMessage.contains('CRA_'));
        System.assert(result.contacts.isEmpty());
    }

    /*****************************************************************
    Tests:     searchAll keeps order, handles null and caps requests.
    *****************************************************************/
    @isTest
    static void searchAllKeepsOrderAndCapsRequests() {
        List<CRA_ContactSearchCriteria> requests = new List<CRA_ContactSearchCriteria>();
        for (Integer index = 0; index < CRA_ContactSearchService.MAX_REQUESTS_PER_CALL; index++) {
            requests.add(CRA_TestDataFactory.byName(Math.mod(index, 2) == 0 ? 'Ava' : 'Nobody'));
        }
        requests.add(CRA_TestDataFactory.byName('Ava'));

        Test.startTest();
        List<CRA_ContactSearchResult> results = new CRA_ContactSearchService().searchAll(requests);
        List<CRA_ContactSearchResult> none = new CRA_ContactSearchService().searchAll(null);
        Test.stopTest();

        System.assertEquals(requests.size(), results.size());
        assertOutcome(CRA_ContactSearchResult.SINGLE_MATCH, results[0], 'first');
        assertOutcome(CRA_ContactSearchResult.NO_MATCH, results[1], 'second');
        assertOutcome(CRA_ContactSearchResult.ERROR, results[requests.size() - 1], 'over the cap');
        System.assert(none.isEmpty());
    }

    /*****************************************************************
    Tests:     Escaping, digit pattern and phone matching helpers.
    *****************************************************************/
    @isTest
    static void helperFunctions() {
        System.assertEquals('a\\%b\\_c\\\\', CRA_ContactSearchService.escapeLike('a%b_c\\'));
        System.assertEquals('%1%2%3%', CRA_ContactSearchService.digitPattern('123'));
        System.assertEquals(null, CRA_ContactSearchCriteria.clean('  \n\t '));

        CRA_ContactSearchCriteria criteria = new CRA_ContactSearchCriteria();
        criteria.phone = '0191 4956203';
        System.assert(criteria.validate());
        System.assert(CRA_ContactSearchService.phoneMatches('+44 (191) 495-6203', criteria));
        System.assert(!CRA_ContactSearchService.phoneMatches(null, criteria));
        System.assert(!CRA_ContactSearchService.phoneMatches('+44 191 4956204', criteria));
    }
}
