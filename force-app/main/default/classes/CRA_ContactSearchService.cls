/*****************************************************************
Name:          CRA_ContactSearchService
============================================================
Purpose:       Secure Contact search for the SCGOE-95 Contact Read
               Agent. Validates the criteria, builds a whitelisted
               query with bind variables only, runs every query in
               USER_MODE (sharing, object permissions and field-level
               security of the running user), counts matches with a
               cap of 101, pages results five at a time, detects
               duplicate identifiers and classifies the outcome.
               Counts, rows and duplicate checks only ever see records
               the running user can read.
               Read-only: this class performs no DML.
               Presentation belongs to the Prompt Template; the result
               carries data and outcome codes, plus a neutral fallback
               message.
============================================================
History
-------
VERSION  AUTHOR                  DATE         DETAIL    DESCRIPTION
1.0      Revecast Orchestrate    19/11/2026   Created   SCGOE-95 Session 2
1.1      Revecast Orchestrate    20/11/2026   Updated   SCGOE-95 S2 review:
                                                      Phone + MobilePhone,
                                                      exact full-name
                                                      priority, email
                                                      domain search,
                                                      refinement flags
1.2      Revecast Orchestrate    27/11/2026   Updated   SCGOE-95 AID-1:
                                                      Account Id filter;
                                                      hidden or missing
                                                      Account = NO_MATCH
*****************************************************************/
public with sharing class CRA_ContactSearchService {

    // Result shaping (requirements O2-O5).
    public static final Integer PAGE_SIZE = 5;
    public static final Integer LIST_SMALL_MAX = 5;
    public static final Integer LIST_MEDIUM_MAX = 10;
    public static final Integer TOO_MANY_THRESHOLD = 100;
    public static final Integer COUNT_CAP = TOO_MANY_THRESHOLD + 1;

    // Bounds on one call. Each request runs at most four queries
    // (an Account Id search adds one Account visibility check).
    public static final Integer MAX_REQUESTS_PER_CALL = 10;
    public static final Integer QUERIES_PER_REQUEST = 4;

    // Phone fields searched and returned (review H1: Phone and
    // MobilePhone only). Each is used only when the user can read it.
    public static final List<String> PHONE_FIELDS = new List<String>{ 'Phone', 'MobilePhone' };

    // Query budget reserved per request; a test raises it to prove
    // the budget branch in searchAll.
    @TestVisible
    private static Integer queriesPerRequest = QUERIES_PER_REQUEST;

    // Neutral messages. NO_MATCH wording is identical whether nothing
    // exists or nothing is accessible (SEC: never imply hidden records).
    public static final String NO_MATCH_MESSAGE = 'I could not find any Contacts that match '
        + 'your search. Try checking the spelling, using fewer details, or searching by a '
        + 'different detail.';
    public static final String ERROR_MESSAGE = 'Something went wrong while searching Contacts. '
        + 'Please try again. If it keeps happening, contact your Salesforce administrator.';

    // Digits compared when one number carries a country code and the
    // other does not (a full national number is at least 10 digits).
    public static final Integer PHONE_SUFFIX_DIGITS = 10;

    // Phone pre-filter scan size; a full scan means the count is uncertain.
    @TestVisible
    private static Integer phoneScanLimit = 2000;

    // Lets a test force the error path without touching data.
    @TestVisible
    private static Boolean forceFailureForTest = false;

    private final CRA_FieldAccess access;

    /*****************************************************************
    Purpose:   Default constructor: checks the running user's access.
    *****************************************************************/
    public CRA_ContactSearchService() {
        this(new CRA_FieldAccess());
    }

    /*****************************************************************
    Purpose:   Constructor with an injectable access profile (seam for
               simulated security tests).
    *****************************************************************/
    @TestVisible
    private CRA_ContactSearchService(CRA_FieldAccess accessChecker) {
        this.access = accessChecker;
    }

    /*****************************************************************
    Purpose:   Search for several requests, one result per request in
               the same order. Each request carries its own filters, so
               each needs its own queries; the number of requests per
               call and the remaining query budget are therefore capped
               and any request beyond them returns ERROR.
    *****************************************************************/
    public List<CRA_ContactSearchResult> searchAll(List<CRA_ContactSearchCriteria> requests) {
        List<CRA_ContactSearchResult> results = new List<CRA_ContactSearchResult>();
        if (requests == null) {
            return results;
        }
        for (Integer index = 0; index < requests.size(); index++) {
            Boolean withinBudget = index < MAX_REQUESTS_PER_CALL
                && (Limits.getLimitQueries() - Limits.getQueries()) >= queriesPerRequest;
            results.add(withinBudget ? search(requests[index]) : buildError());
        }
        return results;
    }

    /*****************************************************************
    Purpose:   Search for one request. Never throws: any unexpected
               failure becomes ERROR with a message that carries no
               internal detail.
    *****************************************************************/
    public CRA_ContactSearchResult search(CRA_ContactSearchCriteria criteria) {
        System.debug(LoggingLevel.FINE, 'Entering CRA_ContactSearchService.search');
        CRA_ContactSearchResult result;
        try {
            result = runSearch(criteria);
        } catch (Exception unexpected) {
            // Log the type only; never return it to the user.
            System.debug(LoggingLevel.ERROR, 'CRA search failed: ' + unexpected.getTypeName());
            result = buildError();
        }
        System.debug(LoggingLevel.FINE, 'Exiting CRA_ContactSearchService.search: ' + result.outcomeCode);
        return result;
    }

    /*****************************************************************
    Purpose:   The search itself, in outcome precedence order.
    *****************************************************************/
    private CRA_ContactSearchResult runSearch(CRA_ContactSearchCriteria criteria) {
        if (forceFailureForTest) {
            throw new SearchException('Forced failure for test');
        }
        CRA_ContactSearchResult result = new CRA_ContactSearchResult();
        if (criteria == null || !criteria.validate()) {
            result.outcomeCode = CRA_ContactSearchResult.NEEDS_CLARIFICATION;
            result.userMessage = criteria == null
                ? 'Please tell me who you are looking for.' : criteria.validationMessage;
            return result;
        }
        result.criteriaSummary = summarise(criteria);
        result.requestedFieldLabel = fieldLabel(criteria.requestedFieldKey);

        // No Contact access at all: the neutral NO_MATCH, never an error.
        if (!access.isContactReadable()) {
            return finishNoMatch(result, criteria);
        }
        List<String> unavailable = unavailableFilters(criteria);
        if (!unavailable.isEmpty()) {
            result.outcomeCode = CRA_ContactSearchResult.FILTER_UNAVAILABLE;
            result.userMessage = 'You cannot search by ' + String.join(unavailable, ', ')
                + '. Please try different details.';
            return result;
        }
        // AID-1: an Account the user cannot see, and one that does not
        // exist, both give the neutral NO_MATCH (never imply it exists).
        if (criteria.accountRecordId != null && !access.isAccountRecordVisible(criteria.accountRecordId)) {
            return finishNoMatch(result, criteria);
        }
        QueryPlan plan = buildPlan(criteria);
        MatchSet matches = String.isNotBlank(criteria.phone)
            ? countByPhone(plan, criteria) : countByQuery(plan, criteria);
        classify(result, criteria, plan, matches);
        return result;
    }

    /*****************************************************************
    Purpose:   Classify the match count into an outcome and load the
               page of rows that outcome shows. A single match is the
               only case where a Contact is identified; two or more
               matches are always listed, never picked for the user.
    *****************************************************************/
    private void classify(CRA_ContactSearchResult result, CRA_ContactSearchCriteria criteria,
            QueryPlan plan, MatchSet matches) {
        Integer total = matches.count;
        if (total == 0) {
            finishNoMatch(result, criteria);
            return;
        }
        if (total > TOO_MANY_THRESHOLD || matches.scanIncomplete) {
            result.outcomeCode = CRA_ContactSearchResult.TOO_MANY;
            result.totalMatchesLabel = 'more than ' + TOO_MANY_THRESHOLD;
            result.refinementRequired = true;
            result.suggestedFiltersText = suggestFilters(criteria);
            result.userMessage = 'More than ' + TOO_MANY_THRESHOLD
                + ' Contacts match. Please add more details to narrow the search.';
            return;
        }
        result.totalMatchesLabel = String.valueOf(total);
        result.similarNameCount = matches.similarNameCount;
        Integer offset = 0;
        if (total == 1) {
            classifySingle(result, criteria);
        } else {
            offset = classifyMultiple(result, criteria, matches);
        }
        loadPage(result, criteria, plan, matches, offset);
    }

    /*****************************************************************
    Purpose:   One match: the full record, or just the requested field.
    *****************************************************************/
    private void classifySingle(CRA_ContactSearchResult result, CRA_ContactSearchCriteria criteria) {
        if (criteria.requestedFieldKey != null) {
            result.outcomeCode = CRA_ContactSearchResult.FIELD_ANSWER;
            result.userMessage = 'Here is the ' + result.requestedFieldLabel.toLowerCase()
                + ' for this Contact.';
        } else {
            result.outcomeCode = CRA_ContactSearchResult.SINGLE_MATCH;
            result.userMessage = 'I found one matching Contact.';
        }
    }

    /*****************************************************************
    Purpose:   Two or more matches. The size bands apply to duplicates
               too (review L1):
               - 2-5   all rows
               - 6-10  first five, the rest on request (REMAINING_PAGE)
               - 11-100 first five, refinement required, no more pages
               A shared identifier keeps DUPLICATE_IDENTIFIER (and
               duplicateOn) so the user is asked which one they mean.
    Returns:   the row offset of the page to show.
    *****************************************************************/
    private Integer classifyMultiple(CRA_ContactSearchResult result, CRA_ContactSearchCriteria criteria,
            MatchSet matches) {
        Integer total = matches.count;
        String duplicateOn = findDuplicateIdentifier(criteria, matches);
        Boolean isDuplicate = duplicateOn != null;
        result.duplicateOn = duplicateOn;
        if (isDuplicate || total > LIST_MEDIUM_MAX) {
            result.suggestedFiltersText = suggestFilters(criteria);
        }
        String opening = isDuplicate
            ? total + ' Contacts have this ' + duplicateOn.toLowerCase() + '. Which one do you mean?'
            : 'I found ' + total + ' matching Contacts.';
        if (total <= LIST_SMALL_MAX) {
            result.outcomeCode = isDuplicate
                ? CRA_ContactSearchResult.DUPLICATE_IDENTIFIER : CRA_ContactSearchResult.LIST_2_TO_5;
            result.userMessage = opening;
            return 0;
        }
        if (total <= LIST_MEDIUM_MAX) {
            if (criteria.wantsRemaining()) {
                result.outcomeCode = CRA_ContactSearchResult.REMAINING_PAGE;
                result.userMessage = 'Here are the other ' + (total - PAGE_SIZE) + ' matching Contacts.';
                return PAGE_SIZE;
            }
            result.outcomeCode = isDuplicate
                ? CRA_ContactSearchResult.DUPLICATE_IDENTIFIER : CRA_ContactSearchResult.LIST_6_TO_10;
            result.canShowRemaining = true;
            result.userMessage = opening + ' Here are the first ' + PAGE_SIZE
                + '. Would you like to see the other ' + (total - PAGE_SIZE) + '?';
            return 0;
        }
        // 11-100 (decision D-C): first five, ask for filters, no paging.
        result.outcomeCode = isDuplicate
            ? CRA_ContactSearchResult.DUPLICATE_IDENTIFIER : CRA_ContactSearchResult.LIST_11_TO_100;
        result.refinementRequired = true;
        result.userMessage = opening + ' Here are the first ' + PAGE_SIZE
            + '. Please add more details to narrow the search.';
        return 0;
    }

    /*****************************************************************
    Purpose:   Finish a NO_MATCH result with the neutral wording.
    *****************************************************************/
    private CRA_ContactSearchResult finishNoMatch(CRA_ContactSearchResult result,
            CRA_ContactSearchCriteria criteria) {
        result.outcomeCode = CRA_ContactSearchResult.NO_MATCH;
        result.totalMatchesLabel = '0';
        result.suggestedFiltersText = suggestFilters(criteria);
        result.userMessage = NO_MATCH_MESSAGE;
        return result;
    }

    /*****************************************************************
    Purpose:   Build an ERROR result with no internal detail.
    *****************************************************************/
    private CRA_ContactSearchResult buildError() {
        CRA_ContactSearchResult result = new CRA_ContactSearchResult();
        result.outcomeCode = CRA_ContactSearchResult.ERROR;
        result.userMessage = ERROR_MESSAGE;
        return result;
    }

    // =================================================================
    // Query building
    // =================================================================

    /*****************************************************************
    Purpose:   Translate the validated criteria into WHERE conditions
               on whitelisted fields, with every value in a bind
               variable. LIKE wildcards in user input are escaped.
    *****************************************************************/
    @TestVisible
    private QueryPlan buildPlan(CRA_ContactSearchCriteria criteria) {
        QueryPlan plan = new QueryPlan();
        if (criteria.contactRecordId != null) {
            plan.add('Id = :contactIdValue', 'contactIdValue', criteria.contactRecordId);
        }
        if (criteria.accountRecordId != null) {
            plan.add('AccountId = :accountIdValue', 'accountIdValue', criteria.accountRecordId);
        }
        for (Integer index = 0; index < criteria.nameWords.size(); index++) {
            String bindName = 'nameWord' + index;
            plan.add('(FirstName LIKE :' + bindName + ' OR LastName LIKE :' + bindName + ')',
                bindName, escapeLike(criteria.nameWords[index]) + '%');
        }
        addEmail(plan, criteria);
        if (String.isNotBlank(criteria.phone)) {
            // Digit-subsequence pre-filter on each readable phone field;
            // the exact digit check runs in Apex (decision D-F).
            List<String> phoneConditions = new List<String>();
            for (String fieldName : readablePhoneFields()) {
                phoneConditions.add(fieldName + ' LIKE :phonePattern');
            }
            plan.add('(' + String.join(phoneConditions, ' OR ') + ')', 'phonePattern',
                digitPattern(criteria.phoneCoreDigits.right(PHONE_SUFFIX_DIGITS)));
        }
        addContains(plan, criteria.accountName, 'Account.Name', 'accountNameValue');
        addContains(plan, criteria.jobTitle, 'Title', 'jobTitleValue');
        addLocation(plan, criteria);
        return plan;
    }

    /*****************************************************************
    Purpose:   Email condition by match type (review M2):
               EXACT   Email = value (case-insensitive in SOQL)
               DOMAIN  Email LIKE '%@domain' (that domain exactly)
               PARTIAL Email LIKE '%value%'
    *****************************************************************/
    private void addEmail(QueryPlan plan, CRA_ContactSearchCriteria criteria) {
        if (criteria.emailMatchType == CRA_ContactSearchCriteria.EMAIL_EXACT) {
            plan.add('Email = :emailValue', 'emailValue', criteria.emailSearchValue);
        } else if (criteria.emailMatchType == CRA_ContactSearchCriteria.EMAIL_DOMAIN) {
            plan.add('Email LIKE :emailValue', 'emailValue', '%@' + escapeLike(criteria.emailSearchValue));
        } else if (criteria.emailMatchType == CRA_ContactSearchCriteria.EMAIL_PARTIAL) {
            plan.add('Email LIKE :emailValue', 'emailValue', '%' + escapeLike(criteria.emailSearchValue) + '%');
        }
    }

    /*****************************************************************
    Purpose:   Add a "contains" condition for a non-blank value.
    *****************************************************************/
    private void addContains(QueryPlan plan, String value, String fieldPath, String bindName) {
        if (String.isNotBlank(value)) {
            plan.add(fieldPath + ' LIKE :' + bindName, bindName, '%' + escapeLike(value) + '%');
        }
    }

    /*****************************************************************
    Purpose:   Location conditions. Text values match the start of the
               mailing city, state or country; state and country also
               match the ISO code when state and country picklists are
               enabled (they are in this org).
    *****************************************************************/
    private void addLocation(QueryPlan plan, CRA_ContactSearchCriteria criteria) {
        if (String.isNotBlank(criteria.city)) {
            plan.add('MailingCity LIKE :cityValue', 'cityValue', escapeLike(criteria.city) + '%');
        }
        if (String.isNotBlank(criteria.stateOrRegion)) {
            plan.add(locationCondition(new List<String>{ 'MailingState' }, 'stateValue',
                new List<String>{ 'MailingStateCode' }), 'stateValue',
                escapeLike(criteria.stateOrRegion) + '%');
            plan.binds.put('stateValueCode', criteria.stateOrRegion);
        }
        if (String.isNotBlank(criteria.country)) {
            plan.add(locationCondition(new List<String>{ 'MailingCountry' }, 'countryValue',
                new List<String>{ 'MailingCountryCode' }), 'countryValue',
                escapeLike(criteria.country) + '%');
            plan.binds.put('countryValueCode', criteria.country);
        }
        if (String.isNotBlank(criteria.location)) {
            plan.add(locationCondition(
                new List<String>{ 'MailingCity', 'MailingState', 'MailingCountry' }, 'locationValue',
                new List<String>{ 'MailingStateCode', 'MailingCountryCode' }), 'locationValue',
                escapeLike(criteria.location) + '%');
            plan.binds.put('locationValueCode', criteria.location);
        }
    }

    /*****************************************************************
    Purpose:   Build "(A LIKE :x OR B LIKE :x OR Code = :xCode)" using
               only code fields that exist in this org.
    *****************************************************************/
    private String locationCondition(List<String> textFields, String bindName, List<String> codeFields) {
        List<String> parts = new List<String>();
        for (String fieldName : textFields) {
            parts.add(fieldName + ' LIKE :' + bindName);
        }
        for (String codeField : codeFields) {
            if (access.contactFieldExists(codeField)) {
                parts.add(codeField + ' = :' + bindName + 'Code');
            }
        }
        return '(' + String.join(parts, ' OR ') + ')';
    }

    /*****************************************************************
    Purpose:   "%2%1%2%...%" — matches any stored format of the digits
               (spaces, brackets, dashes, dots). Input is digits only.
    *****************************************************************/
    @TestVisible
    private static String digitPattern(String digits) {
        List<String> pieces = new List<String>{ '%' };
        for (Integer index = 0; index < digits.length(); index++) {
            pieces.add(digits.substring(index, index + 1));
            pieces.add('%');
        }
        return String.join(pieces, '');
    }

    /*****************************************************************
    Purpose:   Escape the LIKE wildcards %, _ and the escape character
               itself, so user input is always matched literally.
    *****************************************************************/
    @TestVisible
    private static String escapeLike(String value) {
        return value.replace('\\', '\\\\').replace('%', '\\%').replace('_', '\\_');
    }

    // =================================================================
    // Counting
    // =================================================================

    /*****************************************************************
    Purpose:   Count matches in USER_MODE, capped at 101. For a full
               name, exact full-name matches take priority (review M1):
               when at least one accessible Contact has exactly that
               name, the search is narrowed to those Contacts and the
               near matches are only counted (similarNameCount).
               At most two counts; with the page, three queries.
    *****************************************************************/
    private MatchSet countByQuery(QueryPlan plan, CRA_ContactSearchCriteria criteria) {
        MatchSet matches = new MatchSet();
        if (criteria.hasFullName()) {
            Map<String, Object> exactBinds = plan.binds.clone();
            exactBinds.put('exactNameValue', criteria.normalisedName);
            Integer exact = countWhere(plan.whereClause() + ' AND Name = :exactNameValue', exactBinds);
            if (exact > 0) {
                Integer allNameMatches = countWhere(plan.whereClause(), plan.binds);
                plan.add('Name = :exactNameValue', 'exactNameValue', criteria.normalisedName);
                matches.count = exact;
                matches.exactNameMatch = true;
                matches.similarNameCount = Math.max(0, allNameMatches - exact);
                return matches;
            }
        }
        matches.count = countWhere(plan.whereClause(), plan.binds);
        return matches;
    }

    /*****************************************************************
    Purpose:   One USER_MODE COUNT() with the 101 cap.
    *****************************************************************/
    private Integer countWhere(String whereClause, Map<String, Object> binds) {
        return Database.countQueryWithBinds(
            'SELECT COUNT() FROM Contact WHERE ' + whereClause + ' LIMIT ' + COUNT_CAP,
            binds, AccessLevel.USER_MODE);
    }

    /*****************************************************************
    Purpose:   Phone search: scan the pre-filtered candidates in
               USER_MODE and keep those whose Phone or MobilePhone
               digits really match (only the fields the user can read).
               A full name is then narrowed to exact matches in Apex,
               as in countByQuery, with no extra query.
               If the scan is full the count is uncertain, so the
               result is treated as too many (ask for more filters).
    *****************************************************************/
    private MatchSet countByPhone(QueryPlan plan, CRA_ContactSearchCriteria criteria) {
        List<String> phoneFields = readablePhoneFields();
        List<Contact> candidates = Database.queryWithBinds(
            'SELECT Id, Name, ' + String.join(phoneFields, ', ') + ' FROM Contact WHERE '
                + plan.whereClause() + ' ORDER BY Name, Id LIMIT ' + phoneScanLimit,
            plan.binds, AccessLevel.USER_MODE);
        MatchSet matches = new MatchSet();
        matches.scanIncomplete = candidates.size() >= phoneScanLimit;
        List<Contact> phoneMatchesFound = new List<Contact>();
        for (Contact candidate : candidates) {
            if (anyPhoneMatches(candidate, phoneFields, criteria)) {
                phoneMatchesFound.add(candidate);
            }
        }
        List<Id> exactNameIds = new List<Id>();
        List<Id> allIds = new List<Id>();
        for (Contact found : phoneMatchesFound) {
            allIds.add(found.Id);
            if (criteria.hasFullName() && criteria.normalisedName.equalsIgnoreCase(found.Name)) {
                exactNameIds.add(found.Id);
            }
        }
        matches.exactNameMatch = !exactNameIds.isEmpty();
        matches.orderedIds = matches.exactNameMatch ? exactNameIds : allIds;
        matches.similarNameCount = matches.exactNameMatch ? allIds.size() - exactNameIds.size() : 0;
        matches.count = Math.min(matches.orderedIds.size(), COUNT_CAP);
        return matches;
    }

    /*****************************************************************
    Purpose:   True when any of the given phone fields matches.
    *****************************************************************/
    private static Boolean anyPhoneMatches(Contact candidate, List<String> phoneFields,
            CRA_ContactSearchCriteria criteria) {
        for (String fieldName : phoneFields) {
            if (phoneMatches((String) candidate.get(fieldName), criteria)) {
                return true;
            }
        }
        return false;
    }

    /*****************************************************************
    Purpose:   Exact digit check (decision D-F). The stored number
               matches when its digits equal the searched digits, or
               when one number (leading zeros removed) ends with the
               other and both have at least 10 digits. So 0191 4956203
               and 191 495 6203 match +44 191 4956203, and
               +1 212 842 5500 matches (212) 842-5500, but numbers with
               different country codes never match.
    *****************************************************************/
    @TestVisible
    private static Boolean phoneMatches(String storedPhone, CRA_ContactSearchCriteria criteria) {
        if (String.isBlank(storedPhone)) {
            return false;
        }
        String storedDigits = storedPhone.replaceAll('[^0-9]', '');
        if (storedDigits == criteria.phoneDigits) {
            return true;
        }
        String storedCore = storedDigits.replaceFirst('^0+', '');
        String searchedCore = criteria.phoneCoreDigits;
        Boolean bothFull = storedCore.length() >= PHONE_SUFFIX_DIGITS
            && searchedCore.length() >= PHONE_SUFFIX_DIGITS;
        return bothFull && (storedCore.endsWith(searchedCore) || searchedCore.endsWith(storedCore));
    }

    // =================================================================
    // Duplicates (decision D-B, revised after the S2 review)
    // =================================================================

    /*****************************************************************
    Purpose:   Name the identifier that two or more matches share,
               when the search used an exact one:
               - Name   two or more exact full-name matches (priority
                        narrowing in countByQuery / countByPhone)
               - Email  an exact address (a domain search is a list)
               - Phone  a phone number, on Phone or MobilePhone
    Returns:   e.g. "Name", "Email", "Name, Phone", or null.
    *****************************************************************/
    private String findDuplicateIdentifier(CRA_ContactSearchCriteria criteria, MatchSet matches) {
        List<String> shared = new List<String>();
        if (matches.exactNameMatch) {
            shared.add('Name');
        }
        if (criteria.isExactEmail()) {
            shared.add('Email');
        }
        if (String.isNotBlank(criteria.phone)) {
            shared.add('Phone');
        }
        return shared.isEmpty() ? null : String.join(shared, ', ');
    }

    // =================================================================
    // Rows
    // =================================================================

    /*****************************************************************
    Purpose:   Load one page of rows in USER_MODE and set the counts.
    *****************************************************************/
    private void loadPage(CRA_ContactSearchResult result, CRA_ContactSearchCriteria criteria,
            QueryPlan plan, MatchSet matches, Integer offset) {
        List<Contact> records = queryPage(plan, matches, offset);
        Boolean fieldAnswer = result.outcomeCode == CRA_ContactSearchResult.FIELD_ANSWER;
        for (Integer index = 0; index < records.size(); index++) {
            CRA_ContactSearchResult.ContactRow row = fieldAnswer
                ? toFieldAnswerRow(records[index], criteria.requestedFieldKey)
                : toRow(records[index]);
            row.n = offset + index + 1;
            result.contacts.add(row);
        }
        result.shownCount = result.contacts.size();
        // Only a 6-10 first page may offer the rest (review L2).
        result.remainingCount = result.canShowRemaining
            ? Math.max(0, matches.count - offset - result.shownCount) : 0;
        if (matches.count == 1 && !records.isEmpty()) {
            result.singleContactId = records[0].Id;
        }
    }

    /*****************************************************************
    Purpose:   Select only the fields the user can read, so the
               USER_MODE query never fails on field-level security.
    *****************************************************************/
    private List<Contact> queryPage(QueryPlan plan, MatchSet matches, Integer offset) {
        String selectClause = 'SELECT ' + String.join(readableSelectFields(), ', ') + ' FROM Contact';
        if (matches.orderedIds == null) {
            return Database.queryWithBinds(
                selectClause + ' WHERE ' + plan.whereClause() + ' ORDER BY Name, Id'
                    + ' LIMIT ' + PAGE_SIZE + ' OFFSET ' + offset,
                plan.binds, AccessLevel.USER_MODE);
        }
        List<Id> pageIds = new List<Id>();
        Integer pageEnd = Math.min(matches.orderedIds.size(), offset + PAGE_SIZE);
        for (Integer index = offset; index < pageEnd; index++) {
            pageIds.add(matches.orderedIds[index]);
        }
        return Database.queryWithBinds(
            selectClause + ' WHERE Id IN :pageIds ORDER BY Name, Id',
            new Map<String, Object>{ 'pageIds' => pageIds }, AccessLevel.USER_MODE);
    }

    /*****************************************************************
    Purpose:   Fields to select: Id and Name always, the rest only when
               readable by the running user.
    *****************************************************************/
    private List<String> readableSelectFields() {
        List<String> fields = new List<String>{ 'Id', 'Name' };
        if (access.isAccountNameReadable()) {
            fields.add('Account.Name');
        }
        for (String fieldName : new List<String>{ 'Title', 'Email', 'Phone', 'MobilePhone',
                'MailingStreet', 'MailingCity', 'MailingState', 'MailingPostalCode', 'MailingCountry' }) {
            if (access.isContactFieldReadable(fieldName)) {
                fields.add(fieldName);
            }
        }
        return fields;
    }

    /*****************************************************************
    Purpose:   Full row; unreadable or blank values are "Not available".
    *****************************************************************/
    private CRA_ContactSearchResult.ContactRow toRow(Contact record) {
        CRA_ContactSearchResult.ContactRow row = baseRow(record);
        row.accountName = readAccountName(record);
        row.title = readField(record, 'Title');
        row.email = readField(record, 'Email');
        row.phone = readField(record, 'Phone');
        row.mobilePhone = readField(record, 'MobilePhone');
        row.mailingAddress = readMailingAddress(record);
        return row;
    }

    /*****************************************************************
    Purpose:   Field-answer row (O7): name, link and the one field only.
    *****************************************************************/
    private CRA_ContactSearchResult.ContactRow toFieldAnswerRow(Contact record, String fieldKey) {
        CRA_ContactSearchResult.ContactRow row = baseRow(record);
        if (fieldKey == 'Account') {
            row.accountName = readAccountName(record);
        } else if (fieldKey == 'Title') {
            row.title = readField(record, 'Title');
        } else if (fieldKey == 'Email') {
            row.email = readField(record, 'Email');
        } else if (fieldKey == 'Phone') {
            // "Phone" answers with both numbers, so a Contact with only
            // a mobile is not reported as having no phone.
            row.phone = readField(record, 'Phone');
            row.mobilePhone = readField(record, 'MobilePhone');
        } else if (fieldKey == 'MobilePhone') {
            row.mobilePhone = readField(record, 'MobilePhone');
        } else if (fieldKey == 'MailingAddress') {
            row.mailingAddress = readMailingAddress(record);
        }
        return row;
    }

    /*****************************************************************
    Purpose:   Id, name and record link (My Domain URL).
    *****************************************************************/
    private CRA_ContactSearchResult.ContactRow baseRow(Contact record) {
        CRA_ContactSearchResult.ContactRow row = new CRA_ContactSearchResult.ContactRow();
        row.id = record.Id;
        row.name = CRA_ContactSearchResult.orNotAvailable(record.Name);
        row.contactUrl = URL.getOrgDomainUrl().toExternalForm()
            + '/lightning/r/Contact/' + record.Id + '/view';
        return row;
    }

    /*****************************************************************
    Purpose:   Read a Contact field only when it is readable.
    *****************************************************************/
    private String readField(Contact record, String fieldName) {
        String value = access.isContactFieldReadable(fieldName) ? (String) record.get(fieldName) : null;
        return CRA_ContactSearchResult.orNotAvailable(value);
    }

    /*****************************************************************
    Purpose:   Account name only when Account name is readable.
    *****************************************************************/
    private String readAccountName(Contact record) {
        String value = access.isAccountNameReadable() && record.Account != null
            ? record.Account.Name : null;
        return CRA_ContactSearchResult.orNotAvailable(value);
    }

    /*****************************************************************
    Purpose:   One-line mailing address from its readable parts.
    *****************************************************************/
    private String readMailingAddress(Contact record) {
        List<String> parts = new List<String>();
        for (String fieldName : new List<String>{ 'MailingStreet', 'MailingCity', 'MailingState',
                'MailingPostalCode', 'MailingCountry' }) {
            String value = access.isContactFieldReadable(fieldName) ? (String) record.get(fieldName) : null;
            if (String.isNotBlank(value)) {
                parts.add(value.replaceAll('\\s*[\\r\\n]+\\s*', ', ').trim());
            }
        }
        return CRA_ContactSearchResult.orNotAvailable(String.join(parts, ', '));
    }

    // =================================================================
    // Filter availability, suggestions and summary
    // =================================================================

    /*****************************************************************
    Purpose:   Labels of supplied filters on fields the user cannot
               read. Name and Id are readable with Contact access.
    *****************************************************************/
    private List<String> unavailableFilters(CRA_ContactSearchCriteria criteria) {
        List<String> unavailable = new List<String>();
        if (String.isNotBlank(criteria.email) && !access.isContactFieldReadable('Email')) {
            unavailable.add('email');
        }
        if (String.isNotBlank(criteria.phone) && readablePhoneFields().isEmpty()) {
            unavailable.add('phone');
        }
        if (String.isNotBlank(criteria.accountName) && !access.isAccountNameReadable()) {
            unavailable.add('Account name');
        }
        if (criteria.accountRecordId != null && !access.isAccountIdFilterable()) {
            unavailable.add('Account');
        }
        if (String.isNotBlank(criteria.jobTitle) && !access.isContactFieldReadable('Title')) {
            unavailable.add('job title');
        }
        Boolean usesLocation = String.isNotBlank(criteria.city) || String.isNotBlank(criteria.stateOrRegion)
            || String.isNotBlank(criteria.country) || String.isNotBlank(criteria.location);
        if (usesLocation && !access.isContactFieldReadable('MailingCity')) {
            unavailable.add('location');
        }
        return unavailable;
    }

    /*****************************************************************
    Purpose:   Readable filters the user has not used yet, as text.
    *****************************************************************/
    private String suggestFilters(CRA_ContactSearchCriteria criteria) {
        List<String> suggestions = new List<String>();
        // AID-1: a search already limited to one Account never suggests Account name.
        String accountUsed = criteria.accountRecordId != null ? String.valueOf(criteria.accountRecordId)
            : criteria.accountName;
        addSuggestion(suggestions, accountUsed, access.isAccountNameReadable(), 'Account name');
        addSuggestion(suggestions, criteria.jobTitle, access.isContactFieldReadable('Title'), 'job title');
        addSuggestion(suggestions, criteria.email, access.isContactFieldReadable('Email'), 'email');
        addSuggestion(suggestions, criteria.phone, !readablePhoneFields().isEmpty(), 'phone');
        Boolean locationReadable = access.isContactFieldReadable('MailingCity');
        addSuggestion(suggestions, criteria.city, locationReadable, 'city');
        addSuggestion(suggestions, criteria.stateOrRegion, locationReadable, 'state or region');
        addSuggestion(suggestions, criteria.country, locationReadable, 'country');
        return String.join(suggestions, ', ');
    }

    /*****************************************************************
    Purpose:   Phone fields the running user can read, in PHONE_FIELDS
               order. Unreadable ones are never filtered or selected.
    *****************************************************************/
    private List<String> readablePhoneFields() {
        List<String> readable = new List<String>();
        for (String fieldName : PHONE_FIELDS) {
            if (access.isContactFieldReadable(fieldName)) {
                readable.add(fieldName);
            }
        }
        return readable;
    }

    /*****************************************************************
    Purpose:   Add a suggestion when unused and readable.
    *****************************************************************/
    private void addSuggestion(List<String> suggestions, String usedValue, Boolean readable, String label) {
        if (String.isBlank(usedValue) && readable) {
            suggestions.add(label);
        }
    }

    /*****************************************************************
    Purpose:   Plain summary of the cleaned criteria, for the agent.
    *****************************************************************/
    private String summarise(CRA_ContactSearchCriteria criteria) {
        List<String> parts = new List<String>();
        addSummary(parts, 'Selected Contact', criteria.contactRecordId == null ? null : 'yes');
        addSummary(parts, 'Account record', criteria.accountRecordId == null ? null : 'yes');
        addSummary(parts, 'Name', criteria.name);
        addSummary(parts, emailSummaryLabel(criteria), criteria.emailSearchValue);
        addSummary(parts, 'Phone', criteria.phone);
        addSummary(parts, 'Account name', criteria.accountName);
        addSummary(parts, 'Job title', criteria.jobTitle);
        addSummary(parts, 'City', criteria.city);
        addSummary(parts, 'State or region', criteria.stateOrRegion);
        addSummary(parts, 'Country', criteria.country);
        addSummary(parts, 'Location', criteria.location);
        return String.join(parts, '; ');
    }

    /*****************************************************************
    Purpose:   Summary label for the email search type.
    *****************************************************************/
    private static String emailSummaryLabel(CRA_ContactSearchCriteria criteria) {
        if (criteria.emailMatchType == CRA_ContactSearchCriteria.EMAIL_DOMAIN) {
            return 'Email domain';
        }
        return criteria.emailMatchType == CRA_ContactSearchCriteria.EMAIL_PARTIAL ? 'Email contains' : 'Email';
    }

    /*****************************************************************
    Purpose:   Add "Label: value" when the value is supplied.
    *****************************************************************/
    private void addSummary(List<String> parts, String label, String value) {
        if (String.isNotBlank(value)) {
            parts.add(label + ': ' + value);
        }
    }

    /*****************************************************************
    Purpose:   User-facing label of a requested field key.
    *****************************************************************/
    private static String fieldLabel(String fieldKey) {
        if (fieldKey == null) {
            return null;
        }
        if (fieldKey == 'MailingAddress') {
            return 'Mailing address';
        }
        return fieldKey == 'MobilePhone' ? 'Mobile phone' : fieldKey;
    }

    // =================================================================
    // Inner types
    // =================================================================

    /*****************************************************************
    Purpose:   WHERE conditions and their bind values.
    *****************************************************************/
    @TestVisible
    private class QueryPlan {
        public List<String> conditions = new List<String>();
        public Map<String, Object> binds = new Map<String, Object>();

        public void add(String condition, String bindName, Object bindValue) {
            conditions.add(condition);
            binds.put(bindName, bindValue);
        }

        public String whereClause() {
            return String.join(conditions, ' AND ');
        }
    }

    /*****************************************************************
    Purpose:   Match count, plus ordered Ids for the phone path.
    *****************************************************************/
    private class MatchSet {
        public Integer count = 0;
        public List<Id> orderedIds;
        public Boolean scanIncomplete = false;
        public Boolean exactNameMatch = false;
        public Integer similarNameCount = 0;
    }

    /*****************************************************************
    Purpose:   Internal failure type; never shown to the user.
    *****************************************************************/
    public class SearchException extends Exception {
    }
}
